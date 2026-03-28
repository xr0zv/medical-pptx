#!/usr/bin/env python3
"""Extract figures from medical/scientific PDFs.

Runs a full pipeline: caption detection, column-aware clipping, rasterization
at 3x zoom, whitespace trimming, and edge text cleanup. Outputs a JSON manifest
with per-figure metadata.

Usage:
    python extract_figures.py <pdf_path> [--output-dir figures/] [--include-caption] [--debug]
"""

import argparse
import json
import os
import re
import sys

import numpy as np
import pymupdf
from PIL import Image

# ---------------------------------------------------------------------------
# Caption patterns
# ---------------------------------------------------------------------------

caption_patterns = [
    r'^Fig\.?\s*\d[\d.\-]*',
    r'^Figure\s*\d[\d.\-]*',
    r'^Box\s*\d[\d.\-]*',
    r'^CASE\s*\d[\d.\-]*',
    r'^Table\s*\d[\d.\-]*',
    r'^Image\s*\d[\d.\-]*',
    r'^Plate\s*\d[\d.\-]*',
    r'^Panel\s*[A-Z]',
]

# ---------------------------------------------------------------------------
# Block classification
# ---------------------------------------------------------------------------

def classify_blocks(page):
    """Classify each text block as header, footer, body, caption, or image_block."""
    pw, ph = page.rect.width, page.rect.height
    blocks = page.get_text("dict")["blocks"]
    classified = []
    for b in blocks:
        if "lines" not in b:
            classified.append((b, "image_block"))
            continue
        first_text = ""
        for line in b["lines"]:
            for span in line["spans"]:
                first_text += span["text"] + " "
                if len(first_text) > 60:
                    break
            if len(first_text) > 60:
                break
        first_text = first_text.strip()
        bbox = b["bbox"]
        if bbox[3] < ph * 0.08:
            classified.append((b, "header", first_text))
        elif bbox[1] > ph * 0.95:
            classified.append((b, "footer", first_text))
        else:
            is_caption = False
            for pat in caption_patterns:
                if re.match(pat, first_text, re.IGNORECASE):
                    is_caption = True
                    break
            if is_caption:
                classified.append((b, "caption", first_text))
            else:
                classified.append((b, "body", first_text))
    return classified

# ---------------------------------------------------------------------------
# Column detection
# ---------------------------------------------------------------------------

def detect_column_bounds(page, caption_bbox, classified_blocks):
    """Determine if this caption is in a column layout and return (x0, x1) bounds."""
    pw, ph = page.rect.width, page.rect.height
    cx0, cy0, cx1, cy1 = caption_bbox
    caption_width = cx1 - cx0
    caption_center = (cx0 + cx1) / 2
    page_center = pw / 2
    page_margin = 10

    if caption_width > pw * 0.55:
        return (page_margin, pw - page_margin)

    if caption_center < page_center:
        col_x0 = page_margin
        col_x1 = page_center + 10
    else:
        col_x0 = page_center - 10
        col_x1 = pw - page_margin

    for (b, btype, *rest) in classified_blocks:
        if btype != "image_block":
            continue
        bb = b["bbox"]
        if bb[3] < cy0 - pw * 0.5 or bb[1] > cy0:
            continue
        if bb[2] > col_x0 and bb[0] < col_x1:
            col_x0 = min(col_x0, max(bb[0] - 5, page_margin))
            col_x1 = max(col_x1, min(bb[2] + 5, pw - page_margin))

    return (col_x0, col_x1)

# ---------------------------------------------------------------------------
# Figure boundary detection
# ---------------------------------------------------------------------------

def find_figure_top(page, caption_bbox, classified_blocks, col_x0, col_x1):
    """Find the y-coordinate where the figure starts (above the caption)."""
    pw, ph = page.rect.width, page.rect.height
    caption_top = caption_bbox[1]
    col_width = col_x1 - col_x0

    body_above = []
    for (b, btype, *rest) in classified_blocks:
        if btype != "body" or b["bbox"][3] >= caption_top - 5:
            continue
        block_text = rest[0] if rest else ""
        if len(block_text) < 50:
            continue
        bx0, bx1 = b["bbox"][0], b["bbox"][2]
        overlap = max(0, min(bx1, col_x1) - max(bx0, col_x0))
        if overlap > col_width * 0.25:
            body_above.append(b["bbox"])

    for (b, btype, *rest) in classified_blocks:
        if btype != "caption" or b["bbox"][3] >= caption_top - 5:
            continue
        bx0, bx1 = b["bbox"][0], b["bbox"][2]
        overlap = max(0, min(bx1, col_x1) - max(bx0, col_x0))
        if overlap > col_width * 0.25:
            body_above.append(b["bbox"])

    if body_above:
        nearest_body_bottom = max(bb[3] for bb in body_above)
        return nearest_body_bottom + 3
    else:
        header_bottoms = [b["bbox"][3] for (b, btype, *rest) in classified_blocks if btype == "header"]
        if header_bottoms:
            return max(header_bottoms) + 3
        return 20


def find_content_bottom(page, header_bbox, classified_blocks, col_x0, col_x1):
    """Find the y-coordinate where a box/table content ends (below the header)."""
    pw, ph = page.rect.width, page.rect.height
    header_bottom = header_bbox[3]
    col_width = col_x1 - col_x0

    body_below = []
    for (b, btype, *rest) in classified_blocks:
        if btype != "body" or b["bbox"][1] <= header_bottom + 5:
            continue
        bx0, bx1 = b["bbox"][0], b["bbox"][2]
        overlap = max(0, min(bx1, col_x1) - max(bx0, col_x0))
        if overlap > col_width * 0.25:
            body_below.append(b["bbox"])

    if body_below:
        nearest_body_top = min(bb[1] for bb in body_below)
        return nearest_body_top - 3

    footer_tops = [b["bbox"][1] for (b, btype, *rest) in classified_blocks if btype == "footer"]
    if footer_tops:
        return min(footer_tops) - 3
    return ph - 20

# ---------------------------------------------------------------------------
# Edge text cleanup
# ---------------------------------------------------------------------------

def clean_text_edges(img_path, strip_pct=0.06, text_density_threshold=0.008,
                     min_content_fraction=0.05, debug=False):
    """Remove partial text fragments bleeding in from adjacent columns/paragraphs."""
    img = Image.open(img_path)
    arr = np.array(img)
    h, w = arr.shape[:2]

    if arr.ndim == 3:
        dark = np.all(arr < 180, axis=2)
    else:
        dark = arr < 180

    crops = {"left": 0, "right": w, "top": 0, "bottom": h}
    diagnostics = []

    edges = {
        "left":   (dark[:, :max(int(w * strip_pct), 8)], "cols", w),
        "right":  (dark[:, min(w - int(w * strip_pct), w-8):], "cols", w),
        "top":    (dark[:max(int(h * strip_pct), 8), :], "rows", h),
        "bottom": (dark[min(h - int(h * strip_pct), h-8):, :], "rows", h),
    }

    for edge_name, (strip, axis_type, full_dim) in edges.items():
        strip_size = strip.shape[1] if axis_type == "cols" else strip.shape[0]
        total_pixels = strip.size
        dark_pixels = np.sum(strip)
        density = dark_pixels / total_pixels if total_pixels > 0 else 0

        is_text_like = (0.001 < density < text_density_threshold)

        if is_text_like and axis_type == "cols":
            rows_with_dark = np.sum(np.any(strip, axis=1))
            row_coverage = rows_with_dark / strip.shape[0]
            is_text_like = row_coverage < 0.35

        if is_text_like:
            trim_amount = strip_size
            if trim_amount / full_dim > min_content_fraction * 3:
                trim_amount = int(full_dim * min_content_fraction)

            if edge_name == "left":
                crops["left"] = trim_amount
            elif edge_name == "right":
                crops["right"] = w - trim_amount
            elif edge_name == "top":
                crops["top"] = trim_amount
            elif edge_name == "bottom":
                crops["bottom"] = h - trim_amount

            diagnostics.append(f"  \u2702 {edge_name}: trimmed {trim_amount}px (density={density:.4f})")
        elif debug:
            diagnostics.append(f"  \u2713 {edge_name}: clean (density={density:.4f})")

    left, top, right, bottom = crops["left"], crops["top"], crops["right"], crops["bottom"]
    was_modified = (left > 0 or top > 0 or right < w or bottom < h)

    if was_modified:
        if right - left < w * 0.5 or bottom - top < h * 0.5:
            diagnostics.append(f"  \u26a0 Skipped: trim too aggressive (would remove >50%)")
            return False, None, "\n".join(diagnostics)

        img_cropped = img.crop((left, top, right, bottom))
        img_cropped.save(img_path)
        diagnostics.append(f"  \u2192 Saved: {right-left}x{bottom-top} (was {w}x{h})")

    return was_modified, (left, top, right, bottom) if was_modified else None, "\n".join(diagnostics)

# ---------------------------------------------------------------------------
# Flag generation
# ---------------------------------------------------------------------------

def compute_flags(width, height):
    """Return a list of warning flags for a figure based on its dimensions."""
    flags = []
    ar = width / height if height > 0 else 0
    if ar > 3.0:
        flags.append("VERY WIDE")
    if ar < 0.33:
        flags.append("VERY TALL")
    if width < 200 and height < 200:
        flags.append("VERY SMALL")
    return flags

# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def extract_figures(pdf_path, output_dir="figures", include_caption=False, debug=False):
    """Run the full figure-extraction pipeline on a PDF.

    Returns a list of figure metadata dicts.
    """
    doc = pymupdf.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)

    extracted_figures = []

    for page_idx in range(doc.page_count):
        page = doc[page_idx]
        pw, ph = page.rect.width, page.rect.height
        classified = classify_blocks(page)

        for (b, btype, *rest) in classified:
            if btype != "caption":
                continue
            first_text = rest[0] if rest else ""
            caption_bbox = b["bbox"]
            label_match = None
            for pat in caption_patterns:
                m = re.match(pat, first_text, re.IGNORECASE)
                if m:
                    label_match = m.group()
                    break
            if not label_match:
                continue

            col_x0, col_x1 = detect_column_bounds(page, caption_bbox, classified)

            if re.match(r'^(Box|CASE|Table)', first_text, re.IGNORECASE):
                content_bottom = find_content_bottom(page, caption_bbox, classified, col_x0, col_x1)
                clip = pymupdf.Rect(
                    max(caption_bbox[0] - 5, col_x0),
                    caption_bbox[1] - 5,
                    min(caption_bbox[2] + 5, col_x1),
                    content_bottom
                )
            else:
                figure_top = find_figure_top(page, caption_bbox, classified, col_x0, col_x1)
                clip_figure_only = pymupdf.Rect(
                    col_x0, figure_top,
                    col_x1, caption_bbox[1] - 2
                )
                clip_with_caption = pymupdf.Rect(
                    col_x0, figure_top,
                    col_x1, caption_bbox[3] + 5
                )
                clip = clip_with_caption if include_caption else clip_figure_only

            if clip.width < 20 or clip.height < 20:
                print(f"\u26a0 Skipping {label_match} on page {page_idx+1}: "
                      f"clip too small ({clip.width:.0f}x{clip.height:.0f})",
                      file=sys.stderr)
                continue

            pix = page.get_pixmap(clip=clip, matrix=pymupdf.Matrix(3, 3))
            safe_label = re.sub(r'[^a-zA-Z0-9_.-]', '_', label_match.strip())
            fname = os.path.join(output_dir, f"p{page_idx+1}_{safe_label}.png")
            pix.save(fname)

            # Whitespace trimming
            img = Image.open(fname)
            arr = np.array(img)
            non_white_rows = np.where(arr.min(axis=(1, 2)) < 250)[0]
            non_white_cols = np.where(arr.min(axis=(0, 2)) < 250)[0]
            if len(non_white_rows) > 0 and len(non_white_cols) > 0:
                pad = 15
                top = max(non_white_rows[0] - pad, 0)
                bottom = min(non_white_rows[-1] + pad, arr.shape[0])
                left = max(non_white_cols[0] - pad, 0)
                right = min(non_white_cols[-1] + pad, arr.shape[1])
                img = img.crop((left, top, right, bottom))
                img.save(fname)

            final_img = Image.open(fname)
            extracted_figures.append({
                "file": fname,
                "label": label_match,
                "page": page_idx + 1,
                "width": final_img.width,
                "height": final_img.height,
                "aspect_ratio": round(final_img.width / final_img.height, 2),
                "clip_region": f"({clip.x0:.0f},{clip.y0:.0f})\u2192({clip.x1:.0f},{clip.y1:.0f})",
                "column_bounds": f"x:[{col_x0:.0f},{col_x1:.0f}]",
            })
            print(f"\u2713 {label_match} (page {page_idx+1}): "
                  f"{final_img.width}x{final_img.height}px, "
                  f"AR={final_img.width/final_img.height:.2f}, "
                  f"col={col_x0:.0f}-{col_x1:.0f}",
                  file=sys.stderr)

    doc.close()

    # --- Edge text cleanup pass ---
    print("=" * 60, file=sys.stderr)
    print("EDGE TEXT CLEANUP PASS", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    cleaned_count = 0
    for fig in extracted_figures:
        modified, crop_box, diag = clean_text_edges(fig["file"], debug=debug)
        if modified:
            cleaned_count += 1
            new_img = Image.open(fig["file"])
            fig["width"], fig["height"] = new_img.size
            fig["aspect_ratio"] = round(new_img.width / new_img.height, 2)
            print(f"\u2702 {fig['label']} (page {fig['page']}): CLEANED", file=sys.stderr)
            if diag:
                print(diag, file=sys.stderr)
        else:
            print(f"\u2713 {fig['label']} (page {fig['page']}): no text edges found", file=sys.stderr)
            if diag:
                print(diag, file=sys.stderr)
    print(f"\nCleaned {cleaned_count}/{len(extracted_figures)} figures", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # --- Add flags to each figure ---
    for fig in extracted_figures:
        fig["flags"] = compute_flags(fig["width"], fig["height"])

    return extracted_figures


def main():
    parser = argparse.ArgumentParser(
        description="Extract figures from a medical/scientific PDF."
    )
    parser.add_argument("pdf_path", help="Path to the source PDF file")
    parser.add_argument(
        "--output-dir",
        default="figures",
        help="Directory to write extracted figure PNGs (default: figures/)",
    )
    parser.add_argument(
        "--include-caption",
        action="store_true",
        default=False,
        help="Include the caption text below each figure in the clipped region",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable verbose diagnostic output",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.pdf_path):
        print(f"Error: file not found: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)

    try:
        figures = extract_figures(
            pdf_path=args.pdf_path,
            output_dir=args.output_dir,
            include_caption=args.include_caption,
            debug=args.debug,
        )
    except Exception as exc:
        print(f"Error during extraction: {exc}", file=sys.stderr)
        sys.exit(1)

    # --- Human-readable summary to stderr ---
    print(f"\n{'=' * 60}", file=sys.stderr)
    print(f"Extracted {len(figures)} figures", file=sys.stderr)
    for fig in figures:
        flag_str = f"  [{', '.join(fig['flags'])}]" if fig["flags"] else ""
        print(
            f"  {fig['label']:20s}  {fig['width']:5d}x{fig['height']:<5d}  "
            f"AR={fig['aspect_ratio']}  {fig['column_bounds']}{flag_str}",
            file=sys.stderr,
        )
    print(f"{'=' * 60}", file=sys.stderr)

    # --- Write JSON manifest ---
    manifest_path = os.path.join(args.output_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(figures, f, indent=2)
    print(f"Manifest written to {manifest_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
