# Medical PPTX

A Claude Code skill for generating professional medical and scientific PowerPoint presentations from source PDFs, notes, or described content.

## Features

- **Full workflow automation** -- from intake questions to delivered .pptx with visual QA
- **Two talk structures** -- Research Talk (story arc: hook, context, gap, approach, results, implications) and Topic Review (medical teaching: epidemiology, etiology, clinical presentation, diagnosis, treatment, etc.)
- **Visual-first design** -- 60-70% visual content per slide, modern color palettes, varied layouts (two-column, full-figure, icon rows, stat callouts)
- **Smart intake** -- collects talk type, duration, audience, content, markdown preview preference, content scope, and color palette via numbered prose questions
- **Content scoping** -- when given a source PDF, scans section headings and lets you include/exclude sections to focus slide budget
- **Figure extraction & insertion** -- extracts figures from source PDFs (PyMuPDF), then inserts them into placeholder slots with correct aspect ratios and labels
- **Necessity-based figure selection** -- filters figures by relevance to talk duration, audience, and type instead of dumping everything in
- **Visual QA pipeline** -- converts slides to images via LibreOffice + PyMuPDF for automated review of text overflow, overlap, and contrast issues
- **10 built-in color palettes** -- or specify a custom palette
- **Supports all talk types** -- conference talks, seminars, thesis defenses, grant pitches, journal clubs, grand rounds/didactic lectures (5-60 min)

## How to Use

### 1. Install dependencies

**Python:**
```bash
pip install pymupdf python-pptx "markitdown[pptx]"
```

**Node.js:**
```bash
npm install -g pptxgenjs react-icons react react-dom sharp
```

**LibreOffice** (for visual QA):
```bash
# macOS
brew install --cask libreoffice
# Ubuntu/Debian
sudo apt install libreoffice
```

### 2. Install the skill

```bash
claude mcp add-skill /path/to/medical-pptx
```

Or upload `SKILL.md` and the `references/` folder to a Claude Project's knowledge base.

### 3. Generate a presentation

Ask Claude to create a presentation. The skill will:

1. **Gather input** -- ask about your talk type, duration, audience, source material, content scope, and color palette
2. **Plan the deck** -- create a slide-by-slide outline with a markdown preview for your approval
3. **Build the .pptx** -- generate slides programmatically with PptxGenJS
4. **Run QA** -- validate via text extraction and visual inspection
5. **Insert figures** (optional) -- if a source PDF was provided, extract and insert figures into placeholders. 

Note: figure insertion works well in most cases, but can occasionally produce imperfect results (e.g. misaligned crops or sizing issues) when processing a large number of figures from complex PDFs. You may need to manually adjust a few images afterward.

## File Structure

```
medical-pptx/
├── SKILL.md                          # Core skill instructions
├── README.md                         # This file
├── references/
│   ├── pptxgenjs_reference.md        # PptxGenJS API reference
│   ├── presentation_structure.md     # Structure templates for all talk lengths
│   ├── slide_design_principles.md    # Typography, color theory, layout, accessibility
│   ├── data_visualization_slides.md  # Chart types, color guidelines
│   ├── talk_types_guide.md           # Conference, seminar, defense, grant, journal club guidance
│   ├── visual_review_workflow.md     # QA process for visual inspection
│   └── beamer_guide.md              # LaTeX Beamer documentation (alternative output)
├── assets/
│   ├── powerpoint_design_guide.md    # PowerPoint design workflow and best practices
│   ├── timing_guidelines.md          # Timing, pacing, and practice strategies
│   ├── beamer_template_conference.tex
│   ├── beamer_template_seminar.tex
│   └── beamer_template_defense.tex
└── scripts/
    ├── extract_figures.py            # Extract figures from source PDFs
    ├── insert_figures.py             # Insert extracted figures into PPTX placeholders
    ├── pdf_to_images.py              # Convert PDF pages to images for QA
    └── validate_presentation.py      # Validate slide count, dimensions, fonts vs. duration
```

## Supported Talk Types

| Type | Duration | Slides | Use Case |
|------|----------|--------|----------|
| Conference talk | 10-20 min | 10-20 | Presenting 1-2 key findings |
| Academic seminar | 45-60 min | 40-60 | Deep dive, multiple studies |
| Thesis defense | 45-60 min | 50-65 | Comprehensive dissertation overview |
| Grant pitch | 10-20 min | 10-20 | Significance, feasibility, impact |
| Journal club | 20-45 min | 20-40 | Critiquing published work |
| Grand rounds / didactic | 30-60 min | 30-60 | Teaching a clinical topic |

## Credits

- Skill author: AK
- Based on:
  - [pptx](https://github.com/anthropics/skills/tree/main/skills/pptx) by Anthropic -- PptxGenJS reference, QA pipeline, design guidance
  - [scientific-slides](https://github.com/K-Dense-AI/claude-scientific-skills/tree/main/scientific-skills/scientific-slides) by K-Dense Inc. -- presentation structure, reference material, Beamer templates
- License: MIT
