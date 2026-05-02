# biomatix_template.docx

Pandoc reference-doc for the Biomatix-house-style **body** of Word (`.docx`) deliverables. Used by Step 6 of `popgen-report/SKILL.md` as the `--reference-doc` argument when pandoc converts `report_draft.md` to `report_final.docx`.

This file is **NOT a cover-page template**. The cover lives in `biomatix_cover_template.docx` (a separate file, see its README) and is prepended at render time. Pandoc discards the body of any reference-doc — only its styles, page setup, and headers/footers survive.

## What's set

| Property | Value |
|---|---|
| Page size | A4 (210 × 297 mm) |
| Margins | 2.5 cm all sides |
| Header/footer | none (the cover doc supplies the footer; body has none) |
| Style set | pandoc default — Title, Heading 1–6, Author, Date, Subtitle, Abstract, Block Text, Table Caption, Image Caption, Source Code, Verbatim Char, Footnote Text, Definition, plus Word's built-in Normal, Hyperlink, etc. |

## What to customise (later, in Word, not by editing XML)

The current file is pandoc's default styling on an A4 page. To bring it into line with the LaTeX render's appearance, open in Word and modify these styles via Home → Styles → Modify. Suggested values (matching the LaTeX render's 11 pt body, 1.15 line spacing, 2.5 cm margins):

| Style | Suggested setting | Used for |
|---|---|---|
| Normal / Body Text | 11 pt, 1.15 line spacing, 6 pt space after | All prose paragraphs |
| First Paragraph | as Normal, no first-line indent | First paragraph after each heading |
| Title | 18 pt bold centred, 24 pt space after | The H1 at the top of the body (`# Species identity…`) |
| Heading 1 | 16 pt bold, 18 pt above, 6 pt below | (rarely used — most reports start at H2) |
| Heading 2 | 14 pt bold, 18 pt above, 6 pt below | Section headings (`## EXECUTIVE SUMMARY`, etc.) |
| Heading 3 | 12 pt bold italic, 12 pt above, 4 pt below | Sub-headings (`### *Data generation*`, `### 5a.`) |
| Image Caption | 10 pt italic, centred, 4 pt above, 12 pt below | Figure captions (pandoc-crossref emits this) |
| Table Caption | 10 pt italic, centred, 4 pt above, 6 pt below | Table captions |
| Hyperlink | (Word default: blue underlined) | DOIs and URLs |

After modifying, save in place — pandoc will pick up your style values on the next render.

## What pandoc does with this file

When invoked as:

```
pandoc report_draft.md \
  --filter pandoc-crossref \
  --reference-doc biomatix_template.docx \
  --from markdown --to docx \
  -o body.docx
```

pandoc:
- Throws away the body of `biomatix_template.docx` (the placeholder paragraphs you see if you open it).
- Reads the styles from `word/styles.xml` and copies them into the output.
- Reads the page size + margins from the sectPr in `word/document.xml` and copies them to the output's sectPr.
- Reads any header/footer XML and copies it (currently none).
- Generates the body content from the markdown, applying the style names emitted by its writer (Title, Heading 1, Heading 2, Image Caption, etc.) — these names match the styles defined here.

## What this file is NOT

- Not the cover page. See `biomatix_cover_template.docx` and its README.
- Not the deliverable. The deliverable is `<job>/outputs/report_final.docx` — a concatenation of the per-job-substituted cover plus the pandoc body output.
- Not a `.dotx` Word template. It's a regular `.docx`, used by pandoc as a style-source-only file.
