# Style Guide: Databricks Axos GenAI Session 5 Deck

Source: https://docs.google.com/presentation/d/1m2spc85Z36MvMNMcYVS1aVKvY6vfibPcnXEBxYTyUc4/edit

This is a customer-facing Databricks Field Engineering enablement deck (10 slides, 16:9 widescreen).
Use this as your layout and visual-style template when building a new deck in the same series.

---

## Overall Visual Theme

- **Style**: Clean, modern, minimalist. Dark teal and bright brand-red on white, with no gradients or drop shadows.
- **Two masters**: a light master (white backgrounds for content slides) and a dark master (deep teal #0b2026 for section dividers).
- **Logo placement**: Databricks logo appears as a tiny embedded image at the bottom-left of each master slide (~0.25", 7.01") -- so small it is effectively decorative; the brand signal comes from color and font, not a hero logo.
- **Footer**: "©2026 Databricks, Inc. - All rights reserved" at bottom-left (~0.83", 7.05") in the light master. No slide numbers visible in the content area.
- **Slide size**: 13.33" x 7.5" (standard widescreen 16:9, 12192000 x 6858000 EMU).

---

## Color Palette

All colors confirmed from Slides API shape fills and text style data.

| Role | Hex | Usage |
|------|-----|-------|
| Brand Red/Orange (primary accent) | `#ff5f46` | Section divider rectangle fills, arrow separators between columns, presenter name text, sequential step numbers |
| Deep Dark Teal (dark bg + column headers) | `#0b2026` | Dark-master slide background, CRAWL/WALK/RUN column header fills, body text on light slides |
| Medium Slate Gray (body secondary) | `#475568` | Sub-bullets and supporting body text on light slides |
| Off-White/Light Gray (dark-bg subtitle) | `#edeef1` | Subtitle/caption text on dark-background section dividers |
| White | `#ffffff` | All text on dark backgrounds, shape fills in light master |
| Pure Black | `#000000` | Theme color fallback; rarely used directly |

### Hex Quick-Reference

```
Brand Red:   #ff5f46
Dark Teal:   #0b2026
Slate Gray:  #475568
Off-White:   #edeef1
White:       #ffffff
```

---

## Typography

- **Font family**: DM Sans -- used exclusively throughout the entire presentation.
- No mixed font families; no serif, no monospace in body.

### Type Scale (confirmed from Slides API fontSize data)

| Use | Size | Weight | Color |
|-----|------|--------|-------|
| Section divider hero word (CRAWL / WALK / RUN / Demo) | 107 pt | Bold | `#ffffff` on `#0b2026` |
| Slide title (content slides) | 30--60 pt | Regular | default (dark) |
| Forward-looking / closing title | 60 pt | Regular | default |
| Section-divider step number (00, 01, 02, 03) | 35 pt | Bold | `#ff5f46` on `#0b2026` |
| Section-divider subtitle | 27 pt | Regular | `#edeef1` |
| Column header labels (CRAWL/WALK/RUN in diagram) | 18 pt | Bold | `#ffffff` on `#0b2026` fill |
| Column body bullets (in diagram) | 18 pt | Bold | `#0b2026` (heading) / `#475568` (detail) |
| Presenter names | 16 pt | Bold | `#ff5f46` |
| Body / bullet text | 16--20 pt | Regular | `#0b2026` |

---

## Slide Layouts (10 slides across 5 layout types)

### Layout 1 -- Title Slide (Slide 1)

**Type**: Title + presenter attribution
**Background**: White (light master, `g3f2c12d979e_0_1879`)
**Structure**:
- Large title text box, upper-left: ~(0.83", 1.77"), font ~40 pt
- Presenter name boxes, bottom strip: ~(0.83", 6.29") and ~(4.40", 6.29")
  - White fill behind names
  - Text: Name in red bold (#ff5f46, 16 pt), role in regular below
- No visible section divider bar at top

**Replication notes**: Place title in upper-left quadrant, not centered. Presenter names sit in the bottom gutter side-by-side, colored red for name and gray for role.

---

### Layout 2 -- Forward-looking / Legal Boilerplate (Slide 2)

**Type**: Dense text / disclaimer
**Background**: Explicit white (`#ffffff`), light master
**Structure**:
- Large heading at top-left (~0.82", 0.59"), 60 pt
- Dense body text block (~0.83", 2.18"), 16.5 pt, line-spaced
- No accent shapes

**Replication notes**: Standard safe-harbor slide. Keep heading large, body at small readable size. Include on every customer-facing deck.

---

### Layout 3 -- Two-Column Content (Slides 3, 9)

**Type**: Agenda / value-list content with two columns
**Background**: White, light master
**Structure**:
- Title: top-left (~0.82", 0.59"), large, no fill
- Optional subtitle/intro line: (~0.82", 1.28"), smaller, no fill
- Left column text box: ~(0.74", 2.40"), white fill, 18--20 pt, `#0b2026`
- Right column text box: ~(6.71", 2.40"), white fill, 18--20 pt, `#0b2026` bold
- Closing callout line (Slide 9): single line below columns in italic/bold

**Replication notes**: Left column = "what we built on" (context). Right column = "where we're going" (forward). Use `#0b2026` text with DM Sans 18--20 pt. White fills on the column boxes create a card-like separation.

---

### Layout 4 -- Three-Column Journey Diagram (Slide 4)

**Type**: Visual step/journey diagram with icon-free columns
**Background**: White, light master; rendered as PNG thumbnail (shapes-based, not an image)
**Structure**:
- Title: top-left, 30 pt DM Sans, dark text
- Subtitle: one-line below title -- **color `#ff5f46` (brand red)**, smaller than title (confirmed from rendered image)
- Three dark-fill rectangles side by side (each ~3.4" wide), starting at y=2.29"
  - Fill: `#0b2026`
  - Column header text (CRAWL / WALK / RUN): 18 pt bold white, inside rectangle
- Between each column: a ">" arrow text box, 22 pt bold, color `#ff5f46`
- Below each rectangle: bullet text block, 18 pt, `#0b2026` bold for heading + `#475568` for detail items
- Column positions (x): ~0.83", ~5.00", ~9.17"
- Arrow positions (x): ~4.46", ~8.62"

**Replication notes**: This is a hand-built diagram using rectangles and text boxes -- NOT a SmartArt or Slides chart. Replicate by placing three RECTANGLE shapes with `#0b2026` fill, add white bold header text inside, add `#ff5f46` ">" separators, and place bullet text below each rectangle.

---

### Layout 5 -- Section Divider / Dark Interstitial (Slides 5, 6, 7, 8)

**Type**: Section break / demo stage announcement
**Background**: `#0b2026` (dark teal), dark master (`g3fb50216ad7_3_1495`)
**Structure**:
- Full-width `#ff5f46` rectangle at top (pos 0,0), fills the entire upper portion of the slide
- Step number (00, 01, 02, 03): top-left ~(0.73", 0.73"), 35 pt bold, `#ff5f46` text on white fill
- Hero word (Demo / CRAWL / WALK / RUN): center-left ~(0.67", 1.60"), 107 pt bold white
- Subtitle/caption: bottom-left ~(0.73", 5.09"), 27 pt regular, `#edeef1`

**Replication notes**: The red rectangle fills the entire background at z-order bottom (pos 0,0, full slide width). The dark teal background comes from the master/layout pageBackgroundFill, not a shape. The step number sits inside a white-fill text box that visually punches the red number out of the red background. Hero word is enormous -- 107 pt -- for dramatic visual impact at a glance.

---

### Layout 6 -- Closing / Q&A (Slide 10)

**Type**: Minimal closing
**Background**: White, light master
**Structure**:
- Single centered or left-aligned text, ~(0.83", 2.70"), 60 pt
- No other content shapes

**Replication notes**: Keep it clean and minimal. No body text, no bullets. Just the closing call-to-action at ~60 pt.

---

## Header/Footer Treatment

- **No visible top header bar** on content slides (light master).
- **No running footer** with slide numbers in the visible content area.
- **Copyright footer text** lives in the master at bottom-left (~0.83", 7.05"): "©2026 Databricks, Inc. - All rights reserved" -- appears on all light-master slides automatically.
- **Databricks logo**: embedded as a tiny 0.02" image at the master bottom-left (~0.25", 7.01"). Not a prominent logo placement; brand identity carried by color and typography.
- On dark-master slides (section dividers), the copyright/logo footer is absent from those master elements.

---

## Deck Structure Pattern (10-slide arc)

This deck follows a repeatable structure for a single-session enablement:

1. **Title** -- session number, topic, SA + AE names
2. **Forward-looking statement** -- legal/safe-harbor boilerplate
3. **Agenda / session context** -- what we built on + where we are going (two-column)
4. **Journey overview diagram** -- crawl/walk/run or equivalent stage breakdown (three-column diagram)
5. **Section divider: "00 - Demo"** -- dark slide, names the demo scenario
6. **Section divider: "01 - Stage 1"** -- dark slide, names first stage
7. **Section divider: "02 - Stage 2"** -- dark slide, names second stage
8. **Section divider: "03 - Stage 3"** -- dark slide, names third stage
9. **Value summary** -- "Where [Customer] Gets Value" -- bullet list of business outcomes
10. **Q & A** -- minimal closing

**Total**: 10 slides. Dense content lives in the demo (live) not in slide text.

---

## Key Design Decisions to Preserve

1. **DM Sans everywhere** -- never mix in another font.
2. **Red `#ff5f46` is the ONLY accent** -- do not add blue, green, or purple highlights.
3. **Dark teal `#0b2026` doubles as both a dark slide background and a column-header fill** -- same color for visual cohesion.
4. **Section dividers are DARK, not just colored** -- the visual contrast between white content slides and dark #0b2026 section dividers is the primary pacing mechanism.
5. **Hero text on section dividers is enormous (107 pt)** -- do not reduce below ~80 pt or the dramatic effect is lost.
6. **Step numbers are sequential with zero-padding** (00, 01, 02, 03) -- start at 00 for the demo intro.
7. **Arrows as text characters** -- the ">" separator in the journey diagram is a literal text character in `#ff5f46`, not a shape connector or icon.
8. **No gradients, shadows, or rounded corners** on any shapes in this deck.
