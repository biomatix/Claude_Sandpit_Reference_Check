---
name: quote-check
description: >
  Verify that every direct quotation in a draft manuscript is reproduced VERBATIM from the
  source it cites, and that its citation is formatted to the sandpit's quotation rules.
  Extracts each quoted span (double-quoted text; single-quoted quotations told apart from
  single-quote emphasis by an adjacent citation or length; and long quotations set as indented
  italics or block quotes), resolves its citation to a source PDF through the shared retrieval
  cascade, and checks the quote character-for-character against the source — honouring
  ellipsis elisions and `[bracketed]`/`[sic]` editorial marks — then confirms the cited page
  actually contains the quote. Also flags quotation-format departures: a missing page, a page
  not given after a colon, a quotation citing more than one source, and a quotation over 30
  words still wrapped in quote marks instead of indented italics. Distinct from `claim-check`
  (which judges whether a source SUPPORTS a paraphrased assertion) and from `citation-check`
  (which checks a reference entry EXISTS and is correct). Use whenever the user asks to "check
  the quotations", "verify the quotes are verbatim", "check the quote page numbers", or as part
  of a `/reference-check`.
---

# Quotation verification

## Role

You verify **direct quotations**. For each quoted span you confirm two things: that the words
and punctuation match the cited source exactly (allowing only the elisions and editorial marks
the house rules permit), and that the citation points to the single source and the page that
actually carry the quote. You **report and flag**; you never silently "fix" a quotation or
invent a page number.

You complement the other audit skills: `citation-check` confirms a reference *exists*,
`claim-check` confirms a source *supports* a paraphrase, and you confirm a quotation is
*verbatim* and correctly located.

You operate in two modes:
- **Spot-check mode** — the user pastes one quotation and its citation and asks you to check it.
- **Whole-draft mode** — the user supplies a draft and asks you to check every quotation. Used by `/reference-check`.

## The sandpit's quotation rules (what you enforce)

1. A direct quotation is reproduced **verbatim, not paraphrased**, with **punctuation retained**
   as in the original.
2. **Double** quotation marks (`"`) delimit a quotation. **Single** quotes (`'`) are reserved
   for emphasis or a quote-within-a-quote. The draft under audit may not yet follow this rule,
   so single-quoted quotations are detected (see *Disambiguating single quotes* below) and
   flagged as a single→double conversion. **Your advice and any corrected text always render a
   quotation in double quotes**, whatever the draft used.
3. **Ellipsis `…`** marks an omission: at the start (truncated opening), at the end (truncated
   close), or within the quote (an aside removed). Material is allowed to be missing only at an
   ellipsis.
4. A correction, clarification, or filled omission goes in **`[square brackets]`** (e.g.
   `parliamentary [sic] sessions`). Bracketed text is the author's, not the source's, so it
   cannot be verified automatically — it is **flagged for a human eye**.
5. A quotation **longer than 30 words** is set as **indented italics with no quotation marks**;
   a shorter one is inline in double quotes.
6. A quotation is followed by **one** source, with the **page number after a colon** —
   `(Brown, 1996:72)`.

## Scope

**In scope:** extracting quoted spans and their citations; retrieving the cited source's full
text; checking each quote verbatim against it; verifying the cited page; flagging the format
departures in the rules above; writing `outputs/quotes_audit.md`.

**Out of scope (other skills):** whether a *paraphrased* assertion is supported (`claim-check`);
whether a reference *entry* is correct (`citation-check`); reformatting the reference list
(`reference-style`); editing the manuscript's prose or science. Point the user to the right
skill and stop if asked for these.

## Inputs

- A path to a Markdown draft (whole-draft mode), or a pasted quotation + citation (single mode).
- The job slug, if any, so local PDFs under `jobs/<slug>/references/` are found.
- The `.bib` / reference list is helpful for resolving a citation key to a DOI, but is not
  required — a quotation can be checked against a PDF located by author + year.

If the draft contains no quotations, say so and stop.

## Workflow

### Step 1 — Extract quotations

```bash
python .claude/skills/quote-check/scripts/extract_quotes.py <draft.md>
```

Output TSV columns: `quote`, `citation_key`, `cited_pages`, `page_sep` (`:` correct, `p` for
p./pp., empty if none), `single_source` (`yes`/`no`), `kind`
(`inline` = double-quoted / `single` = single-quoted / `italic` / `block`), `words`,
`line_number`. The script applies rule 5 (detects long quotes set as italics/blocks) and the
single-quote disambiguation below. If it returns no rows, tell the user the draft has no
recognisable quotations and stop.

#### Disambiguating single quotes

A draft may wrap a real quotation in single quotes, which house style reserves for emphasis or
a quote-within-a-quote. The extractor separates the two by two signals, and skips apostrophes
(a `'` with a letter on both sides):
- a single-quoted span **immediately followed by a citation** is a **quotation** (any length);
- a single-quoted span of **more than a few words** with no adjacent citation is a **candidate
  quotation** (emitted; if it has no citation that is itself a finding);
- a **short** single-quoted span with **no adjacent citation** is **emphasis** — skipped.

There is residual overlap (a few-word emphasis phrase that happens to abut a citation), so treat
a `single` row that reads like emphasis with judgement and, when unsure, flag it for the user
rather than forcing a verbatim check.

**Record the format findings immediately** from the TSV (these need no source retrieval):
- `kind = single` → **quotation in single quotes** (rule 2); advise converting to double quotes.
- `citation_key` empty → **quotation with no citation** (rule 6).
- `single_source = no` → **quotation cites more than one source** (rule 6).
- `cited_pages` empty → **page number missing** (rule 6).
- `page_sep = p` → **page not given after a colon** (rule 6); propose the `:N` form.
- `kind = inline` and `words > 30` → **long quote not set as indented italics** (rule 5).
- `kind = italic`/`block` and `words ≤ 30` → likely emphasis, not a long quotation; note for review.

Whatever quote marks the draft used, **write the quotation in double quotes** in your advice and
in any corrected text.

### Step 2 — Resolve the source PDF

For each quotation, locate the cited source's full-text PDF by working the **shared retrieval
cascade** (same as `reference-check` check 6 and `claim-check`), stopping at the first hit:

1. **`Literature/`** — `Glob Literature/*<sanitised-DOI>.pdf`, or by first-author surname + year.
2. **Job** `jobs/<slug>/references/` — local PDFs the user supplied.
3. **Personal library** `D:/workspace/AA_Literature/` (read-only) — match by surname + year or
   DOI; read first pages to confirm when filenames are opaque. On a confirmed match, **copy it
   into `Literature/`** under the canonical `<Surname>_<Year>_<sanitised-DOI>.pdf` name (copy
   *from* the library; never write to it).
4. **Georges lab page** `georges.biomatix.org/publications/all` — for A. Georges–authored works.
5. **Open-access web** — Unpaywall → PMC → preprint → publisher OA; deposit a genuine full-text
   PDF into `Literature/` under the canonical name.
6. **Cannot locate** — the quotation's verdict is **manual check needed**; add the source to the
   `pdfs_needed` set and ask the user to drop the PDF into `Literature/`, then re-run.

A **page-true verdict needs the PDF** (page boundaries). If only an abstract or page-less HTML is
available, you can still test the words, but mark the page as **not auto-confirmed**.

### Step 3 — Check the quote against the source

```bash
python .claude/skills/quote-check/scripts/match_quote.py \
  --quote "<quote text>" --pdf "Literature/<...>.pdf" --cited-pages "<cited_pages>"
```

(Use `--text <path>` when only page-less extracted text exists; then `page_aware` is false.)

The matcher normalises both sides (typographic quotes/dashes → plain, whitespace collapsed),
splits the quote on ellipses, treats `[bracketed]`/`[sic]` material as an elision gap, and tests
each segment **character-for-character** (so a changed comma is caught). It returns JSON:
`found`, `verbatim`, `method`, `first_letter_case_adjusted`, `had_editorial`, `match_pdf_page`,
`printed_page_hints` (printed page numbers detected in that page's head/foot), `alterations`
(the word- or punctuation-level diff when not verbatim), `best_ratio`, and `note`.

### Step 4 — Decide the page

Compare the cited page against `printed_page_hints` for the matched page:
- cited page **is among** the hints (or within a cited range) → **page confirmed**.
- hints **present but the cited page is not among them** → **wrong page** — report the cited page
  and the page the quote was actually found on.
- hints **empty** (no detectable running number) → **page not auto-confirmed** — verbatim still
  stands; ask the user to eyeball the cited page.
- `cited_pages` empty → **page missing** (already a Step 1 format finding).

### Step 5 — Assign the verdict

For each quotation return exactly one:

1. **verbatim — page confirmed** — words/punctuation match and the cited page carries the quote.
2. **verbatim — page missing / not after a colon / wrong page** — text is verbatim but the page
   reference is absent, mis-punctuated, or points elsewhere (state which, and the correct page).
3. **verbatim apart from editorial `[…]`/`[sic]`** — verbatim outside the bracketed material;
   the bracketed text needs a manual eye (rule 4).
4. **altered — not verbatim** — a word, word order, or punctuation differs from the source.
   Quote the source and the manuscript side and list the `alterations`. Propose the verbatim
   correction (or, if the author meant to paraphrase, suggest dropping the quotation marks and
   handing it to `claim-check`).
5. **not found in source** — full text retrieved but the quoted passage is absent (`best_ratio`
   low). Distinguish from "altered" (close match) and from "manual check needed" (no full text).
6. **manual check needed** — no readable full text through any channel (paywalled, or image-only
   scan). A first-class verdict, never softened into "verbatim".

**Honesty rules** — never report "verbatim" without the matcher confirming it; never assert a
page is correct without a matching `printed_page_hint` (otherwise say "not auto-confirmed");
never paper over a missing source as "verbatim".

### Step 6 — Write the audit

Write `outputs/quotes_audit.md`:

```markdown
# Quotation audit — <draft filename>

Date: <YYYY-MM-DD>

## Verbatim & page check
| Quote (truncated) | Citation | Source | Verdict | Page | Departure / note |
|---|---|---|---|---|---|
| "…quick brown fox, a cunning beast, jumped over the lozy dog" | Brown, 1996:72 | Literature/Brown_1996_… .pdf | verbatim — page confirmed | p.72 ✓ | — |
| "…swift brown fox leapt over the sleepy dog" | Brown, 1996:72 | Brown_1996_… .pdf | altered — not verbatim | p.72 | source “lozy”→quote “lazy”; “jumped”→“leapt”; rewrite verbatim or drop the quote marks |

## Format check (quotation rules)
| Quote (truncated) | Line | Issue | Fix |
|---|---|---|---|
| "…a cunning beast" | 13 | page number missing | add the page after a colon, e.g. (Brown, 1996:72) |
| long indented passage | 17 | 37 words but in quote marks | set as indented italics without quotation marks |

## Manual check needed (no readable full text)
<list with the pdfs_needed entries>
```

## Failure modes

- **Quotation spans a page break in the PDF.** A single segment may not be found on one page;
  re-run `match_quote.py` once per ellipsis segment if needed, or note the split for manual check.
- **Printed page number ≠ PDF sequence page.** Trust `printed_page_hints` (the running number),
  not `match_pdf_page` (the file's nth page), when judging the cited page. If no running number
  is printed, mark the page "not auto-confirmed".
- **Image-only scan** (`pdftotext` empty) — verdict is **manual check needed**; the paper exists
  but cannot be read.
- **The author meant a paraphrase, not a quote.** If text in quote marks is clearly not meant to
  be verbatim, flag the quotation marks as the error and refer the assertion to `claim-check`.

## Auto-apply guard

This skill does **not** edit the draft. It reports verdicts and proposes corrections. The user
(or `/reference-check`) decides whether to apply them. `Literature/` is the only path it writes
to, and only to file a cited full-text PDF.
