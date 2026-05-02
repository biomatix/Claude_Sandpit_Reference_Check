# biomatix_cover_template.docx

Single-page Biomatix-house-style cover page for Word (`.docx`) deliverables. Used by the popgen-report Step 6 Word-render path (the parallel to `coverpage.tex` for the PDF render).

This is a **literal cover document** that gets prepended to the pandoc-generated body. It is *not* a pandoc reference-doc — pandoc discards reference-doc body content. See `popgen-report/SKILL.md` Step 6 for the prepend mechanics.

## Placeholder tokens

The cover carries five placeholder strings that the render pipeline must substitute per job. Each token sits in its own paragraph so a literal-string replace on `word/document.xml` is sufficient — no XML surgery required at substitution time.

| Token              | Replace with (per-job source in `brief.yaml`)                          | Example                                                                 |
|--------------------|------------------------------------------------------------------------|-------------------------------------------------------------------------|
| `{{TITLE}}`        | `project.title`                                                        | Species identity, maternity and paternity of a Myuchelys clutch from captive holding |
| `{{RECIPIENT}}`    | `Report to <client.name>, <client.address>.`                           | Report to NSW Local Land Services, 126-130 Taylor Street, Armidale NSW 2350. |
| `{{DATE}}`         | `deliverables[0].deadline` formatted as DD-MMM-YYYY                    | 02-May-2026                                                             |
| `{{PHOTO_CREDIT}}` | `Photo: <cover_photo.photographer>` (or empty if no credit)            | Photo: A. Georges                                                       |
| `{{CITATION}}`     | Auto-generated CSIRO Harvard citation: `<lead_author surname>, <initial>. (<year>). <title>. Report to <client.name>, <client.locality>. <date>.` | Georges, A. (2026). Species identity, ... Report to NSW Local Land Services, Armidale. 02-May-2026. |

Substitution is a flat string-replace on the unzipped `word/document.xml`, not a Word merge field — Word's mailmerge is overkill and not scriptable from R without COM. The render step in popgen-report unzips the template, runs five replacements, re-zips into `<job>/outputs/_cover.docx`, then concatenates that with the pandoc body output.

## Embedded images

Two images live in `word/media/` of the .docx:

- `image1.jpeg` — Biomatix logo, ~65 KB. **Do not swap.** Same on every job.
- `image2.jpeg` — cover photo, ~290 KB. **Swap per job** with the file at `cover_photo.path` from `brief.yaml`.

The render pipeline replaces `image2.jpeg` inside the unzipped template with the per-job cover photo before re-zipping. Constraints:
- The file must remain named `image2.jpeg` inside the .docx so the existing relationship in `word/_rels/document.xml.rels` and the `<a:blip r:embed="rId9"/>` reference still resolve. The render step renames the per-job photo on insertion, regardless of its on-disk extension or name.
- JPEG is fine; PNG also works (Word infers from content). If the source is PNG and you want to keep the name as `image2.jpeg`, that's harmless — Word handles the mismatch.
- The frame is sized for a roughly 4:3 landscape photo. Other aspect ratios will distort unless you also edit the `<wp:extent/>` element in `document.xml`. Recommended: keep cover photos in roughly the same aspect ratio across jobs.

## Invariants kept on every cover

These bits are baked into the template and do not change between jobs:
- Biomatix logo (image1.jpeg)
- "Biomatix Pty Ltd, PO Box 7417, Sutton NSW 2620, Australia" address line
- "ABN 90-642-823-023" line
- "info@biomatix.com.au" hyperlink
- "Citation:" label preceding `{{CITATION}}`
- Footer (page number)

If any of these change company-wide (new ABN, new address), edit the template directly in Word, save, and commit — no script needed.

## Backup

The original Mastacomys-populated cover (the file you placed before tokenisation) is preserved at `biomatix_cover_template.docx.bak`. Keep it as a worked example of what a fully-populated cover should look like; if the substitution pipeline produces a broken cover, comparing structures against the .bak helps diagnose.

## What this file is NOT

- Not a pandoc `--reference-doc`. That's a separate file (still to be built) carrying the *body* style definitions for Heading 1/2/3, Body Text, Caption, etc. Pandoc discards reference-doc body content; it would discard this cover.
- Not a Word `.dotx` template. It is a regular `.docx` — the placeholder substitution is text-level, not Word's template-instantiation mechanism.
- Not the deliverable. The render pipeline *uses* this to construct the per-job cover; the deliverable is `<job>/outputs/report_final.docx` with the cover prepended and the placeholders filled.
