---
name: medical-pptx
description: Build slide decks and presentations for medical and scientific talks. Use this for making PowerPoint slides, conference presentations, seminar talks, research presentations, thesis defense slides, case presentations, grand rounds, journal clubs, didactic lectures, or any medical/scientific talk. Use this skill whenever the user mentions slides, presentations, PowerPoint, PPTX, talks, lectures, or wants to present research findings, clinical topics, or scientific content — even if they don't say "medical" or "scientific" explicitly. Also use when converting a PDF paper or textbook chapter into presentation slides. Provides slide structure, design templates, timing guidance, and visual validation. Output is always .pptx generated via PptxGenJS.
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: AK
    based-on: pptx skill by Anthropic, scientific-slides by K-Dense Inc.
---

# Medical PPTX

## Overview

Scientific presentations are a critical medium for communicating research, sharing findings, and engaging with academic and professional audiences. This skill provides comprehensive guidance for creating effective scientific presentations, from structure and content development to visual design and delivery preparation.

**Key Focus**: Oral presentations for conferences, seminars, defenses, and professional talks.

**Output Format**: All presentations are generated as editable `.pptx` files using **PptxGenJS**. This gives you editable slides you can refine in PowerPoint, Keynote, or Google Slides.

**Design philosophy**: Scientific presentations should be visually engaging and research-backed. Dry, text-heavy slides get forgotten — visually driven slides get remembered. Great scientific presentations combine:
- **Compelling visuals**: High-quality figures, charts, diagrams, icons (not just bullet points)
- **Research context**: Proper citations establishing credibility
- **Concise but informative text**: Most bullet lines should be 6-8 words (staying on one line), but some lines can go longer when clinical detail requires it. Lists of etiology, risk factors, investigations, medications, etc. should be presented as bullet points.
- **Professional design**: Modern color schemes, strong visual hierarchy, generous white space
- **Story-driven**: Clear narrative arc, not just data dumps

**Remember**: Boring presentations = forgotten science. Make your slides visually memorable while maintaining scientific rigor through proper citations.

## When to Use This Skill

This skill should be used when:
- Preparing conference presentations (5-20 minutes)
- Developing academic seminars (45-60 minutes)
- Creating thesis or dissertation defense presentations
- Designing grant pitch presentations
- Preparing journal club presentations
- Giving research talks at institutions or companies
- Teaching or tutorial presentations on scientific topics

## How It Works

This skill combines scientific presentation expertise with **PptxGenJS** for programmatic slide generation:

1. **Reference files** provide: presentation structure, talk-type guidance, content planning, design philosophy, timing, and validation checklists
2. **PptxGenJS** provides: the actual .pptx file creation (text, shapes, charts, images, icons, tables)

**IMPORTANT**: Before creating any slides, read the PptxGenJS API reference:
- `references/pptxgenjs_reference.md` — full PptxGenJS API (text, shapes, charts, images, icons, tables, slide masters, common pitfalls)

---

## Slide Generation Workflow

### Step 1: Gather Input from User

**Gate** — Collect all intake items before proceeding. Missing even one item (especially audience or duration) leads to mismatched slides that need full regeneration, wasting significant time and context window.

**Avoid `ask_user_input` for intake** — it caps at 3 questions and locks the input field, preventing the user from typing free-text answers. Instead, **ask all unanswered items as numbered prose questions in a single message**. The user types all their answers in one reply — no question limit and full flexibility in responses.

There are 9 intake items (item 8 only applies when a source PDF is provided). Some can be inferred from context; the rest MUST be explicitly asked. Check each one:

| # | Item | Can it be inferred? | If not inferable, MUST ask |
|---|------|--------------------|-----------------------------|
| 1 | **Outline type** | YES — if user uploads a textbook chapter or says "teaching session", infer Topic Review (Outline B). If user says "presenting my research" or uploads their own paper, infer Research Talk (Outline A). Otherwise ASK. | Research Talk (Outline A) vs. Topic Review (Outline B) |
| 2 | **Talk type** | SOMETIMES — if user says "conference talk" or "grand rounds", it's stated. Otherwise ASK. | Conference, seminar, defense, grant pitch, journal club, grand rounds, didactic lecture |
| 3 | **Topic and content** | YES — if user uploaded a PDF or described what to present, this is already known. Otherwise ASK. | What research/findings/topic to present |
| 4 | **Audience** | NEVER inferable — ALWAYS ASK | Specialists, general/non-expert, mixed |
| 5 | **Duration** | NEVER inferable — ALWAYS ASK | Exact minutes allocated |
| 6 | **Existing materials** | YES — check if files were uploaded. If none, ask if user has figures/logos/templates to provide. | Uploaded figures, charts, data tables, logos, or a template .pptx |
| 7 | **Markdown preview** | NEVER inferable — ALWAYS ASK. | Whether the user wants to review the full slide content in Markdown format before the PPTX is generated. Yes (review first) vs. No (generate directly) |
| 8 | **Content scope** | SOMETIMES — if the user says "focus on treatment and diagnosis" or "skip epidemiology", it's stated. Otherwise, when a source PDF is provided, scan for major section headings and ASK. Skip this item if no source PDF. | Which sections/topics from the source to include in the presentation, and which to skip |
| 9 | **Color palette** | NEVER inferable — ALWAYS ASK | Which color scheme to use for the slides |

**Procedure:**
1. Scan the user's message and uploaded files. Check off any items that are already answered or clearly inferable.
2. Collect all remaining unanswered items into a **single message with numbered prose questions**. State what you've inferred first, then list the questions. Include the available options in parentheses so the user knows what to pick from. Example:
   ```
   Based on the uploaded chapter, I can infer:
   - **Outline type**: Topic Review (Outline B)
   - **Topic**: [inferred topic]
   - **Existing materials**: PDF with figures

   Before I build the deck, please answer the following:
   1. **Talk type** — what setting is this for? (conference talk / seminar / grand rounds / didactic lecture / journal club / defense / grant pitch)
   2. **Audience** — who will you be presenting to? (specialists / general physicians & residents / mixed & non-expert)
   3. **Duration** — how long is your talk? (10 / 15 / 20 / 30 / 45 / 60 minutes)
   4. **Markdown preview** — would you like to review the full slide content in Markdown before I generate the PPTX, or should I generate it directly? (review first / generate directly)
   5. **Content scope** — I found these major sections in the chapter:
      - Introduction & Anatomy
      - Etiology (causes & mechanisms)
      - Clinical Presentation
      - Diagnosis & Investigations
      - Treatment & Management
      - Prognosis
      Should I cover all of them, or exclude any? Excluding sections gives more slides for deeper coverage of the rest.
   6. **Color palette** — which color scheme would you like?
      1. Forest & Moss — forest green, moss, cream (natural, growth)
      2. Coral Energy — coral, gold, navy (vibrant, energetic)
      3. Warm Terracotta — terracotta, sand, sage (warm, inviting)
      4. Berry & Cream — berry, dusty rose, cream (elegant, distinctive)
      5. Midnight Executive — navy, ice blue, white (formal, classic)
      6. Custom — describe your preferred colors
   ```
   **Never silently drop a question. Every mandatory item must be either asked or confirmed as inferable.**
3. Wait for the user's typed response.
4. Confirm the full set of parameters before proceeding. Example: "Great — here's the plan: **Topic Review**, **didactic lecture**, **45 min**, **specialist audience**, **Markdown preview: yes**. **Covering:** Etiology, Clinical Presentation, Diagnosis, Treatment. **Skipping:** Epidemiology, Prognosis. Building the deck now." (Omit the Covering/Skipping line if no source PDF or if covering everything.)
5. Only THEN proceed to Step 2.

**Items 4 (Audience), 5 (Duration), 7 (Markdown preview), and 9 (Color palette) are NEVER optional and must be resolved before proceeding.** Audience determines vocabulary, depth, and assumed background knowledge. Duration determines slide count. Markdown preview determines whether the user gets to review content before PPTX generation. Color palette prevents defaulting to generic blue — letting the user choose ensures a distinctive, intentional design.

**Item 8 (Content scope) is mandatory when a source PDF is provided.** Scan the PDF for major section headings and present them to the user. If the PDF lacks clear section headings, ask in open-ended form: "Is there anything in this material you'd like me to skip or de-emphasize?" If the user says "cover everything", proceed with no filtering.

### Step 2: Plan the Deck

Create a detailed slide-by-slide plan before writing any code. Choose the outline that matches the talk type. **If a source PDF was provided, complete Step 2a (Figure Selection) before writing the slide-by-slide plan.** Only plan slides for sections the user included in their content scope (Step 1, item 8). Reallocate the freed slide budget to deeper coverage of included sections.

**Target slide counts** (~1 slide per minute):
- 15-min conference talk: 15-18 slides
- 45-min seminar: 40-50 slides
- 60-min defense: 50-65 slides

#### Outline A: Research Talk (Story Arc)

Use for conference presentations, thesis defenses, and grant pitches — any talk where you are presenting **your own research findings**.

1. **Hook**: Grab attention (30-60 seconds)
2. **Context**: Establish importance (5-10% of talk)
3. **Problem/Gap**: Identify what's unknown (5-10% of talk)
4. **Approach**: Explain your solution (15-25% of talk)
5. **Results**: Present key findings (40-50% of talk)
6. **Implications**: Discuss meaning (15-20% of talk)
7. **Closure**: Memorable conclusion (1-2 minutes)

**Example plan (15-minute research talk):**
```
Slide 1:  Title slide (presentation title + [Author] at the bottom)
Slide 2:  Hook — compelling problem statement
Slide 3:  Background — key context [cite 2-3 papers]
Slide 4:  Knowledge gap — what's unknown [cite gap papers]
Slide 5:  Research question / hypothesis
Slide 6:  Methods overview (diagram or flowchart)
Slide 7:  Result 1 — key figure + interpretation
Slide 8:  Result 1 — supporting data
Slide 9:  Result 2 — key figure + interpretation
Slide 10: Result 2 — supporting data
Slide 11: Result 3 — key figure
Slide 12: Discussion — comparison with prior work [cite 2-3 papers]
Slide 13: Implications and future directions
Slide 14: Conclusions — 3 key takeaways
Slide 15: Thank You / Questions & Discussion
```

#### Outline B: Medical/Scientific Topic Review

Use for teaching sessions, journal clubs, grand rounds, didactic lectures, or any talk that **reviews a clinical or scientific topic** rather than presenting original research.

**Standard section order** (include only the sections relevant to the topic — not every review needs all of them):

1. **Outline** — brief roadmap of the talk
2. **Introduction** — definition, scope, why this topic matters
3. **Epidemiology** — incidence, prevalence, demographics, risk factors
4. **Etiology** — causes, pathophysiology, mechanisms
5. **Clinical Presentation** — signs, symptoms, history, exam findings
6. **Diagnosis** — approach to diagnosis, differential diagnosis
7. **Diagnostic Criteria** — formal criteria if they exist (e.g., McDonald, ICHD, DSM)
8. **Investigations** — labs, imaging, electrophysiology, pathology
9. **Complications** — disease complications, sequelae
10. **Treatment / Management** — acute, chronic, pharmacologic, non-pharmacologic, algorithms
11. **Prognosis** — natural history, outcomes, prognostic factors
12. **Conclusion / Take-Home Message** — key points to remember

**IMPORTANT**: Not all topics require every section. Omit sections that don't apply. For example, a review of a lab technique might skip Epidemiology and Complications. A review of a rare syndrome might not have formal Diagnostic Criteria. Adapt the outline to the content.

**Example plan (20-minute topic review — Myasthenia Gravis):**
```
Slide 1:  Title slide (presentation title + [Author] at the bottom)
Slide 2:  Outline — roadmap of sections
Slide 3:  Introduction — definition, NMJ pathophysiology
Slide 4:  Epidemiology — incidence, bimodal age distribution
Slide 5:  Clinical Presentation — ocular vs generalized, fatigability
Slide 6:  Clinical Presentation — exam findings, ice pack test
Slide 7:  Diagnosis — approach, antibody testing
Slide 8:  Diagnostic Criteria — MGFA classification
Slide 9:  Investigations — AChR/MuSK antibodies, RNS, SFEMG
Slide 10: Investigations — CT chest (thymoma screening)
Slide 11: Complications — myasthenic crisis, respiratory failure
Slide 12: Treatment — pyridostigmine, immunosuppression
Slide 13: Treatment — thymectomy, IVIG/PLEX for crisis
Slide 14: Prognosis — remission rates, long-term outcomes
Slide 15: Conclusion — 4-5 take-home points
```

### Step 2a: Figure Selection (if source PDF provided)

**Skip this step if no source PDF was provided.**

Before writing the slide-by-slide plan, decide which figures from the source PDF to include. **Every figure must earn its place** — the default is to exclude. Do not include a figure just because it exists in the source. **Automatically exclude figures from sections the user excluded in content scope (Step 1, item 8).**

**Necessity test — include a figure ONLY if it meets at least one of these criteria:**
- **Irreplaceable visual**: Shows something that cannot be adequately conveyed in words (anatomy, imaging, histology, clinical photos, complex flowcharts)
- **Key result**: The figure IS the finding — a graph, survival curve, or outcome chart that is the point of a slide
- **Widely recognized reference**: A standard figure the audience expects to see (e.g., a canonical classification diagram or treatment algorithm)

**Exclude a figure if:**
- It is a **table** that can be recreated as a cleaner, simplified slide table
- It is **decorative or contextual** (equipment photos, lab setups, generic illustrations)
- It **duplicates** another selected figure (same data, different format)
- It shows **supplementary data** not discussed in the talk
- It is **too complex** for the audience level

**Duration raises or lowers the bar** (these are filters, not targets):
- **Short talks (5-15 min)**: Only figures that ARE the point of a slide. Ask: "Would I spend 30+ seconds discussing this figure?" If no, cut it.
- **Medium talks (20-30 min)**: Figures that support key points are included. Supporting/contextual figures still cut.
- **Long talks (45-60 min)**: More room for supporting figures, but still no decorative or redundant ones.

**Audience adjusts the complexity threshold:**
- **Specialists**: Can include more technical figures (detailed mechanisms, raw data)
- **Mixed / residents**: Prefer visually self-explanatory figures; skip figures requiring deep domain knowledge
- **General / non-expert**: Only figures with immediate visual impact; fewer is better

**Talk type shifts what counts as "irreplaceable":**
- **Topic review / didactic**: Anatomy and mechanism diagrams are high priority
- **Research talk (Outline A)**: Own result figures are high priority; background figures from other sources rarely necessary
- **Journal club**: Key result figures necessary; supplementary figures usually not
- **Clinical management**: Algorithms and flowcharts necessary; epidemiology figures usually not

**Procedure:**
1. List all figures in the source PDF (label + one-line description)
2. Apply the necessity test to each, considering duration, audience, and talk type
3. Output a brief selection summary before the slide plan:
   ```
   **Figure selection** (15-min conference, specialist audience):
   - INCLUDE: Fig. 3 (primary outcome KM curve), Fig. 5 (treatment algorithm), Fig. 7 (MRI) — 3 figures
   - EXCLUDE: Fig. 1 (table — recreate as slide table), Fig. 2 (not discussed), Fig. 4 (supplementary), Fig. 6 (decorative)
   ```
4. Only place `[Figure: ...]` markers for included figures in the slide plan

**Edge cases:**
- Very few figures (1-3): Still apply the necessity test — don't force-include just because few are available
- User explicitly requests specific figures: User requests override the necessity test
- Multiple source PDFs: Apply the necessity test independently per PDF

### Step 3: Markdown Preview & User Approval (if requested)

**Skip this step if the user chose "No" for Markdown preview in Step 1.**

If the user chose "Yes", generate a complete Markdown document that contains the full text content of every slide, organized slide-by-slide. This lets the user review, request changes, and approve the content BEFORE the PPTX is built — avoiding costly regeneration.


```markdown
# [Presentation Title]

## Figure Selection
*(Include this section only if a source PDF was provided and Step 2a was completed)*

**Figure selection** ([duration] [talk type], [audience] audience):
- INCLUDE: [list of included figures with brief rationale]
- EXCLUDE: [list of excluded figures with brief reason]

---

## Slide 1: Title Slide
- **Title**: [Presentation title — large, prominent, centered]
- **Author**: [Author] — smaller text, bottom of slide
- **No subtitle, institution, affiliation, or date** — title slide contains only the title and author name

---

## Slide 2: [Slide Title]
- Bullet point one (6-8 words typical)
- Bullet point two
- Bullet point three with more detail if clinically needed
- [Figure: Fig. 1 — Description] ← placeholder for extracted/referenced figures

---

## Slide 3: [Slide Title]
- ...

(continue for all slides)
```

**Requirements for the Markdown preview:**
1. Every slide from the Step 2 plan must appear, numbered and titled.
2. All bullet point text must be written in final form — this is what will go on the slides, not a summary or outline.
3. Figure placements must be indicated with `[Figure: label — description]` markers showing where images will be embedded.
4. Citations must appear exactly as they will on the slides.
5. The Markdown file should be saved as `slide_content_preview.md` and presented to the user using `present_files`.

**After presenting the Markdown preview:**
1. **WAIT** for the user to review and respond. Do NOT proceed until the user explicitly approves or requests changes.
2. If the user requests changes, update the Markdown, re-present it, and wait again.
3. Only after the user approves (e.g., "looks good", "approved", "go ahead", "yes", etc.) proceed to Step 4.

**This gate is required when the user opted for Markdown preview.** Generating a full PPTX costs significant time and context window. Reviewing content in Markdown first lets the user catch structural issues, missing sections, or wrong emphasis before the expensive generation step — saving both time and tokens.

### Step 4: Build the .pptx with PptxGenJS

Use PptxGenJS to create the presentation programmatically. **All figure references use placeholder boxes** — actual images are inserted in Step 7 after the PPTX is complete.

**Before writing code, read:**
- `references/pptxgenjs_reference.md` — full PptxGenJS API reference
- `assets/powerpoint_design_guide.md` — design ideas, color palettes, typography

**Key design decisions to make up front:**
- **Color palette**: Use the palette the user selected in intake item 9. Full hex values for all palettes are in `references/slide_design_principles.md`.
- **Font pairing**: Choose a header + body font pair (e.g., Georgia + Calibri, Arial Black + Arial)
- **Visual motif**: Pick ONE distinctive element and repeat it across slides (colored circles for icons, thick side borders, etc.)

**Building the deck:**

```javascript
const pptxgen = require("pptxgenjs");
let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "Speaker Name";
pres.title = "Presentation Title";

// Title slide — dark background, title + author (Forest & Moss palette)
let slide1 = pres.addSlide();
slide1.background = { color: "2C5F2D" };
slide1.addText("Research Title Here", {
  x: 0.8, y: 1.8, w: 8.4, h: 2.0,
  fontSize: 36, fontFace: "Georgia", color: "FFFFFF", bold: true,
  align: "center", valign: "middle"
});
slide1.addText("[Author]", {
  x: 0.8, y: 4.5, w: 8.4, h: 0.6,
  fontSize: 18, fontFace: "Calibri", color: "CCCCCC",
  align: "center", valign: "middle"
});

// Content slide — use charts, images, shapes, icons
// ... (see references/pptxgenjs_reference.md for full API)

pres.writeFile({ fileName: "presentation.pptx" });
```

**What PptxGenJS gives you for scientific slides:**
- **Charts** (bar, line, pie, scatter, radar) — for presenting data/results directly
- **Images** — embed user-provided figures, plots, diagrams (from uploaded files or generated)
- **Icons** — via react-icons (Font Awesome, Material Design, etc.) for visual interest
- **Shapes** — rectangles, ovals, lines for layout structure and visual motifs
- **Tables** — for comparison data, study parameters, etc.
- **Slide masters** — for consistent styling across all slides

**Figure placeholders (default for all figure references):**

All slides that reference figures use placeholder boxes. Actual images are inserted in Step 7 after the PPTX is delivered.

```javascript
// Placeholder for a figure — dashed border + label text
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1.2, w: 7, h: 3.2,
  fill: { color: "F1F5F9" },
  line: { color: "94A3B8", width: 1, dashType: "dash" }
});
slide.addText("[Insert Fig. 35.1 — Lumbosacral plexus anatomy]", {
  x: 1, y: 1.2, w: 7, h: 3.2,
  fontSize: 14, fontFace: "Calibri", color: "64748B",
  align: "center", valign: "middle", italic: true
});
```

This creates a dashed-border placeholder box with the figure label, so the user knows exactly which figure goes where. **IMPORTANT: The text box MUST have the same x/y/w/h as the rectangle.** The `insert_figures.py` script uses the text box dimensions to size the inserted image — if the text box is smaller than the rectangle, images will be undersized.

**Supported label types in placeholders:** Fig., Figure, Table, Box, CASE, Image, Plate, Panel — matching all types that `extract_figures.py` can detect. Use the same label in the placeholder as appears in the source PDF (e.g., `[Insert CASE 1 — Clinical scenario]`, `[Insert Panel A — Subpanel description]`).

**Embedding user-provided images directly:**

If the user provides specific image files (not from PDF extraction), embed them directly using the `fitImage` helper below. **CRITICAL — NEVER stretch or compress images.** Always read the image's native dimensions first, compute a display size that preserves the aspect ratio, then center it within the available space.

```javascript
const sizeOf = require("image-size");  // npm install image-size

function fitImage(imgPath, maxW, maxH, areaX, areaY, align = "center") {
  const dims = sizeOf(imgPath);
  const aspect = dims.width / dims.height;

  let dispW = maxW;
  let dispH = dispW / aspect;
  if (dispH > maxH) {
    dispH = maxH;
    dispW = dispH * aspect;
  }

  let x = areaX;
  if (align === "center") {
    x = areaX + (maxW - dispW) / 2;
  } else if (align === "right") {
    x = areaX + maxW - dispW;
  }
  const y = areaY + (maxH - dispH) / 2;

  return { x, y, w: dispW, h: dispH };
}

// Usage — full-width figure slide:
const pos = fitImage("figures/p1_Fig__35_1.png", 9.0, 4.0, 0.5, 1.2);
slide.addImage({ path: "figures/p1_Fig__35_1.png", ...pos });
```

**Rules for image sizing on slides:**

1. **Always call `fitImage()`** (or equivalent logic) for every image. Never hardcode `w` and `h` without reading the native dimensions first.
2. **Tall images get smaller bounding boxes.** If the native aspect ratio is < 0.8 (portrait/tall), reduce `maxW` so the image doesn't dominate the slide.
3. **Wide images get full width.** If the native aspect ratio is > 1.5 (landscape/wide), use the full available width (`maxW: 9.0`).
4. **When in doubt, make the image smaller with correct proportions** rather than larger with distorted proportions.
5. **Never use `sizing: { type: "contain" }` or `sizing: { type: "cover" }`** — always compute explicit `w` and `h` values using `fitImage`.
6. **Install `image-size`** (`npm install image-size`) at the start of the build script alongside `pptxgenjs`.

### Step 5: Content QA (Required)

Verify the generated deck by extracting its text content with markitdown:

```bash
python -m markitdown presentation.pptx
```

**Check for:**
- All planned slides are present and in the correct order
- No missing content (every section from the outline appears)
- No leftover placeholder text — run: `python -m markitdown presentation.pptx | grep -iE "\bx{3,}\b|lorem|ipsum|\bTODO|\[insert"`
- Slide titles match the plan
- Citations appear where intended
- No typos or garbled text

**Visual and structural checks:**
- [ ] Slide count appropriate for duration (~1 slide/min)
- [ ] Title slide contains only the title and [Author] (no subtitle, institution, affiliation, or date)
- [ ] Font sizes ≥18pt (preferably 24pt+), high contrast colors
- [ ] No text overflow or element overlap
- [ ] Consistent design throughout, slide numbers present
- [ ] Final slide is "Thank You / Questions & Discussion" (no references or contact info)

**If issues are found**, fix them in the generation code and re-run. Repeat until the extracted text matches the plan.

### Step 6: Deliver the File

Save the final .pptx in the current working directory and present it to the user.

### Step 7: Offer Figure Insertion (if source PDF provided)

After delivering the PPTX with placeholders, ask the user:

> "Would you like me to extract figures from the source PDF and insert them into the slides?"

If the user says **yes**, run the following pipeline:

**1. Extract figures from the source PDF:**

```bash
python scripts/extract_figures.py <source.pdf> --output-dir figures/
```

This runs the full extraction pipeline (caption detection, column-aware clipping, 3x zoom rasterization, whitespace trimming, edge text cleanup) and produces:
- Individual PNG files in `figures/`
- A JSON manifest at `figures/manifest.json` with per-figure metadata

**2. Review the extraction results:**

Read `figures/manifest.json` and check the `flags` field for each figure. Visually inspect any flagged figures (VERY WIDE, VERY TALL, VERY SMALL). Re-extract manually with adjusted parameters if needed.

**3. Insert figures into the PPTX:**

```bash
python scripts/insert_figures.py <presentation.pptx> figures/manifest.json
```

This replaces placeholder shapes (e.g., `[Insert Fig. 35.1 — description]`) with the corresponding extracted images, preserving aspect ratios and centering within the placeholder's bounding box.

The script reports which placeholders were matched/replaced and which were skipped. Review the output for unmatched placeholders or unused figures. **Note:** The extraction script extracts ALL figures from the PDF, but the PPTX only contains placeholders for figures selected in Step 2a. Unused extracted figures in the report are expected — they were intentionally excluded during figure selection.

**4. Re-run Content QA** on the updated PPTX to verify images are correctly placed and no layout issues were introduced.

**4b. Verify figure labels**: After insertion, spot-check that each figure has a visible reference label below it (e.g., "Fig. 35.1 — Lumbosacral plexus anatomy"). The script handles this automatically, but verify on the first few slides by running `python -m markitdown <output.pptx> | grep -i "fig\."` to confirm labels appear in the text extraction.

If the user says **no**, the PPTX is delivered as-is with placeholder boxes that the user can replace manually in PowerPoint/Keynote/Google Slides.

---

## Design Philosophy

Audiences remember slides that are visually driven — not text-heavy bullet dumps. Every slide should have a strong visual element (figure, chart, icon, shape) with text as the complement, not the centerpiece. Target 60-70% visual content, 30-40% text. Vary layouts across the deck (two-column, full-figure, visual overlays) so slides don't blur together. Use modern color palettes matched to the topic, generous white space (40-50%), and large fonts (24pt+ body, 36pt+ titles). Cite relevant papers in intro and discussion slides — research context builds credibility.

For detailed design guidance: `references/slide_design_principles.md` (typography, color, layout, accessibility).

## Additional References

### Data Visualization

Slide figures differ from journal figures: simplify, use larger fonts (18pt+), split multi-panel figures across slides, and use direct labeling instead of legends. PptxGenJS supports bar, line, pie, scatter, and radar charts natively. For complex figures (heatmaps, network diagrams), generate as images with Python (matplotlib/seaborn) and embed.

For figures from a source PDF, use `scripts/extract_figures.py` (Step 7) — do NOT use `extract_image()`, as it fails for vector drawings and composite figures.

For detailed guidance: `references/data_visualization_slides.md`.

### Talk Types, Timing, and Structure

- **Presentation structure**: `references/presentation_structure.md`
- **Talk-type guidance** (conferences, seminars, defenses, grants, journal clubs): `references/talk_types_guide.md`
- **Timing and pacing**: `assets/timing_guidelines.md`

---

## LaTeX Beamer (Alternative)

For math-heavy presentations, LaTeX Beamer remains an option.

**Templates Available**:
- `assets/beamer_template_conference.tex`: 15-minute conference talk
- `assets/beamer_template_seminar.tex`: 45-minute academic seminar
- `assets/beamer_template_defense.tex`: Dissertation defense

For complete Beamer documentation, see `references/beamer_guide.md`.

---

## Reference Files

- **`references/pptxgenjs_reference.md`**: PptxGenJS API reference (text, shapes, images, icons, charts, tables, slide masters)
- **`references/presentation_structure.md`**: Detailed structure for all talk types, timing, transitions
- **`references/slide_design_principles.md`**: Typography, color theory, layout, accessibility
- **`references/data_visualization_slides.md`**: Simplifying figures, chart types, progressive disclosure
- **`references/talk_types_guide.md`**: Specific guidance for conferences, seminars, defenses, grants, journal clubs
- **`references/beamer_guide.md`**: Complete LaTeX Beamer documentation
- **`references/visual_review_workflow.md`**: Visual inspection and iterative improvement

## Assets

- **`assets/beamer_template_conference.tex`**: 15-minute conference talk template
- **`assets/beamer_template_seminar.tex`**: 45-minute academic seminar template
- **`assets/beamer_template_defense.tex`**: Dissertation defense template
- **`assets/powerpoint_design_guide.md`**: Complete PowerPoint design guide
- **`assets/timing_guidelines.md`**: Comprehensive timing, pacing, and practice strategies

