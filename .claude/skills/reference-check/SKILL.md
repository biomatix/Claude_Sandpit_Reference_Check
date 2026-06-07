---
name: reference-check
description: >
  Audit the referencing of an existing draft manuscript end to end, and do nothing else
  (no rewriting of the science, no new analysis). Runs seven checks in order: (1) every
  in-text and figure/table-caption citation appears in the reference list; (2) every
  reference-list entry is cited somewhere in the manuscript; (3) flags any key published
  work that appears to be missing; (4) confirms each cited reference EXISTS (CrossRef / the
  PDF itself); (5) checks each entry's metadata (authors, year, title, journal, volume,
  pages) and formats it to the target journal's style — dropping bracketed issue numbers
  the journal does not require and making title capitalisation consistent; (6) locates the
  full-text PDF and files a copy in Literature/, or asks the user to supply it; (7) checks
  the cited source actually supports the assertion next to the citation, flagging departures.
  Orchestrates the citation-check, claim-check, reference-style and lit-search-a skills.
  Use when the user asks to "check the references", "audit the citations", "check the
  referencing in this manuscript", or supplies a draft and a reference list.
---

# Reference check for a draft manuscript

## Role

You audit the **referencing** of an existing draft manuscript. You change nothing about the
science, the argument, or the prose. Your entire job is the seven checks below: every
in-text and caption citation is in the reference list and vice versa, no key reference is
missing, every cited reference exists and is described correctly and in the target journal's
style, every cited PDF is filed in `Literature/`, and every assertion is actually supported
by the source it cites.

You **report** findings and **propose** corrections. You apply an edit to the manuscript or
reference list only when the user asks you to (see *Applying fixes*). When you cannot resolve
something — a PDF you cannot find, a claim you cannot verify behind a paywall — you flag it
for the user rather than guessing.

This skill is an **orchestrator**. It sequences four worker skills:

| Check | Worker skill |
|---|---|
| 4 — references exist; 5 — metadata correct | `citation-check` |
| 5 — formatting to the journal style | `reference-style` |
| 7 — claim supported by source | `claim-check` |
| 3 — key references missing; 6 — locate/file PDFs | `lit-search-a` |
| 1 & 2 — in-text ↔ reference-list cross-check | this skill (below) |

## Inputs

Before starting, you need:

1. **The draft manuscript** — a path to a Markdown, Word (`.docx`), LaTeX, or plain-text
   file. If it is `.docx`, convert to text/Markdown first (`pandoc <file>.docx -t markdown -o <file>.md`)
   so the body, captions, and reference list are readable; keep the original.
2. **The reference list** — usually the end of the manuscript, or a separate `.bib` /
   reference file. If the manuscript embeds its references, extract them.
3. **The target journal** — needed for check 5 (formatting). Ask if not stated. The journal's
   author instructions are authoritative; `reference-style` establishes the journal's style and
   applies its built-in CSIRO Harvard author–date variant as the default when the style is
   author–date or none is named.

If you are working inside a job folder, the draft lives in `jobs/<slug>/` and outputs go to
`jobs/<slug>/outputs/`. If the user just points you at a loose file, write the audit beside
it (or wherever they ask) and skip the job machinery.

If the draft has no reference list at all, say so and stop.

## The seven checks, in order

Run them in this order — later checks depend on the citation inventory the early ones build.

### Checks 1 & 2 — in-text/caption citations ↔ reference list (this skill does these directly)

Neither `citation-check` nor `claim-check` cross-checks the body against the list; you do it
here.

1. **Build the in-text citation inventory.** Scan the manuscript body **and the figure and
   table captions** for citations: `(Smith 2020)`, `(Smith and Jones 2020)`,
   `(Smith et al. 2020)`, `Smith (2020)`, `[@smith2020]`, numeric `[12]` styles, and
   compound forms `(Smith 2020; Jones 2021)`. Captions are frequently the place a citation is
   missed, so read every `Figure N.` / `Table N.` legend. Record each distinct
   (first-author, year) — or numeric key — with the locations it appears.
2. **Build the reference-list inventory.** Parse each entry to (first-author surname, year,
   title).
3. **Cross-check both directions:**
   - **Check 1 — citations with no entry:** every in-text/caption citation must match a
     reference-list entry. List any that do not (these are the serious ones — a reader cannot
     follow them up).
   - **Check 2 — entries never cited:** every reference-list entry must be cited at least
     once in the body or a caption. List any orphan entries (candidates for deletion, unless
     the journal permits a "further reading" list).
   - Watch for near-misses that are really the same work: year typos (`2019` in text vs
     `2018` in list), `et al.` hiding a different author set, `a`/`b` suffix mismatches, and
     spelling variants of the first author. Report these as *probable matches needing
     reconciliation*, not as both a missing-citation and an orphan-entry.

Report checks 1 & 2 as two short lists plus the reconciliation notes.

### Check 3 — key references missing from the literature

Invoke **`lit-search-a`** to scan the primary published literature for the manuscript's
topic and focal taxon. The goal is **not** an exhaustive bibliography — it is to surface
**well-known, load-bearing works a referee would expect** and that the draft omits: the
foundational method paper for a technique the manuscript uses, the standard reference for the
study species, a directly contradicting or superseding recent paper. List each candidate with
a one-line reason it belongs and its resolved citation. Be conservative: flag a handful of
high-confidence omissions, not every tangentially related paper. The user decides whether to
add them.

### Checks 4 & 5 — references exist; metadata correct; journal formatting

Invoke **`citation-check`** against the reference list (or the `.bib`) in **read-only mode**:
for every entry it resolves the DOI via CrossRef (or searches PubMed / Google Scholar by
title + first author + year when there is no DOI) and compares the canonical record field by
field — **authors, year, title, journal, volume, pages/article ID** — flagging fabricated
entries, wrong years, mistyped authors, mistyped title words, swapped page ranges,
abbreviated journal names, and duplicates, each with a suggested correction. Where the DOI
will not resolve and search finds nothing, fall back to **the PDF itself** in `Literature/`
or the personal library (see check 6) to confirm the work exists. Do **not** auto-apply.

Then apply **check 5 formatting** with **`reference-style`**, targeting the **manuscript's
journal**:
- Reformat each entry to the journal's required style (author list form, year placement,
  title case, journal-name form, volume/page punctuation, DOI form).
- **Issue numbers:** if the target journal does not require the issue number, **remove the
  `(N)` that follows the volume** — e.g. `18(3):691–699` → `18:691–699`. Keep it only where
  the journal requires it or each issue restarts pagination.
- **Capitalisation:** make title capitalisation **consistent across the whole list** —
  sentence case or title case as the journal dictates, applied uniformly. Flag entries that
  currently mix the two.

Present checks 4 & 5 together per entry: existence/metadata problems first, then the
journal-formatted version.

### Check 6 — locate the full-text PDF and file it in `Literature/`

For every **cited** reference, ensure a full-text PDF is filed in the repository's
`Literature/` folder, named `<FirstAuthorSurname>_<Year>_<sanitised-DOI>.pdf` (DOI with `/` →
`_`; e.g. `10.1111/mec.14497` → `Smith_2020_10.1111_mec.14497.pdf`). Work the cascade and
stop at the first hit:

1. **Already in `Literature/`** — `Glob Literature/*<sanitised-DOI>.pdf`, or match by
   first-author surname + year. If present, nothing to do.
2. **Personal library** `D:/workspace/AA_Literature/` (read-only) — `Glob` recursively for a
   PDF matching by surname + year or DOI; if filenames are opaque, read the first page of a
   few candidates to confirm title/authors/year. On a confirmed match, **copy it into
   `Literature/`** under the canonical name (`cp` from the library — never write *to* the
   library).
3. **Georges lab page** `http://georges.biomatix.org/publications/all` — for works authored
   by A. Georges or close collaborators, this page links full-text PDFs and is a permitted,
   non-bot-blocked domain. Fetch the linked PDF directly into `Literature/` under the canonical
   name. (It is also a discovery source in `lit-search-a`; here it is used to *acquire* the PDF.)
4. **Open-access web** — Unpaywall (uses `CLAIM_CHECK_EMAIL`) → PMC → preprint mirror →
   publisher OA. Download a genuine full-text PDF (not an HTML page or abstract) with
   `curl -o Literature/<Surname>_<Year>_<sanitised-DOI>.pdf <url>`.
5. **Cannot locate it** — record the reference under a **`## PDFs needed`** block (citation,
   DOI, title) and **ask the user to download the PDF and drop it into `Literature/`** (any
   filename; you will rename it). Re-run the relevant checks once it arrives. Do not fabricate
   a source or silently skip it.

#### Normalising filenames (run this whenever PDFs are added to `Literature/`)

The user (and the open-access fetch) drop PDFs in with arbitrary publisher/browser names
(`nbt.3820.pdf`, `animals-11-03013-v2.pdf`, `document-2.pdf`,
`Global Change Biology - 2023 - Fuentes - ….pdf`, URL/SICI-encoded DOIs, etc.). **Convert them
all to the canonical `<Surname>_<Year>_<sanitised-lowercased-DOI>.pdf`** with the bundled helper —
**dry-run first, review the plan, then `--apply`:**

```bash
python .claude/skills/reference-check/scripts/normalize_literature.py \
  --lit Literature --refs <manuscript .md/.bib/reflist>          # dry run
python .claude/skills/reference-check/scripts/normalize_literature.py \
  --lit Literature --refs <manuscript> --apply                    # execute
```

The script encodes the lessons that make this safe — **do not hand-roll renames around it:**
- It decides each file's DOI from the **PDF text only if that DOI is one of the manuscript's
  cited DOIs** (a paper's own DOI is on p.1; its reference list is full of *other* DOIs —
  trusting any text DOI once mis-renamed a paper with a DOI scraped from its bibliography),
  then from the filename (incl. encoded/SICI DOIs), then from a unique surname+year filename
  match; otherwise it leaves the file and lists it as MANUAL for you to identify by first page.
- **Case-insensitive-filesystem safety:** a case-only rename (`…GCEN…`→`…gcen…`) must never
  trigger a "remove existing target" — on Windows/macOS the target path is the *same file*, so
  removing it deletes the source. (An earlier hand-written version did exactly this and deleted
  7 PDFs.) The helper compares paths with `normcase` and only removes a genuinely different file.
- It **dedupes keeping the text-richest copy** and flags image-only scans (`pdftotext` empty) —
  a scan confirms existence but cannot be claim-checked.

Run the cascade for **every cited reference**, not just the few you happen to need for the
claims you check first — otherwise the upload request is incomplete.

**At the end of check 6, the missing-PDF upload request is an RIS file, `pdfs_needed.ris`**
(not a markdown list) — built with the bundled helper:

```bash
python .claude/skills/reference-check/scripts/build_ris.py \
  --refs <manuscript reference list> --lit Literature --out pdfs_needed.ris --missing
```

RIS is the deliverable because it is the *actionable* artifact: the user imports it into their
reference manager (EndNote / Zotero / Mendeley) and runs **"Find Full Text"**, which uses their
**institutional (ANU) entitlements through an authenticated browser/link-resolver** to
batch-download the whole defined set in one operation, then drops the folder into `Literature/`
for normalising. The harness cannot authenticate to the institution itself (headless requests
are bot-blocked and cannot do SSO), so handing the user a ready-to-import list for their own
authenticated tools is the fastest sanctioned path for the paywalled set. Then **explicitly
pause and ask the user to import `pdfs_needed.ris` and supply the PDFs before check 7 can be
declared complete.** Do not produce a markdown "issues" list for missing PDFs — RIS only. (If a
needed reference has no DOI, the helper lists it on stderr; flag those for the user to supply
manually.)

Honesty rules for this step:
- **Do not auto-file a PDF on a weak filename match.** A surname+year match with several
  candidates, or a short/common surname, must be confirmed by reading the first page; filing the
  wrong paper under a canonical DOI name corrupts the cache and every downstream claim-check.
- **"Filed" ≠ "readable".** Test each filed PDF with `pdftotext`; an image-only scan confirms the
  paper exists but cannot be claim-checked — list it under (C), not as done.
- **Automated OA download is often blocked** (publisher anti-bot / Cloudflare 403) even for genuinely
  open-access papers. When the fetch fails, still classify the source as open-access in group (A)
  so the user knows it is free to obtain — do not misreport it as paywalled.

`Literature/` is the only PDF store you write to. You only ever **read** the personal library.

### Check 7 — does the source support the assertion?

Invoke **`claim-check`** against the manuscript. For each in-text citation it extracts the
carrying sentence, retrieves the cited content (preferring the PDF now filed in `Literature/`
from check 6, then OA full text, then abstract), and returns one verdict per citation:
**supported** (with the quoted supporting passage), **partially supported**, **contradicted**,
**not found in retrieved text**, or **paywalled — manual check needed**. **Flag every
departure** — every `partially supported`, `contradicted`, `not found`, and `paywalled`
verdict — to the user, with the carrying sentence, the source, and (where text was retrieved)
the quoted passage. A `supported` verdict must carry its quote. Never soften `paywalled` into
`supported`.

## Outputs

The job produces three deliverables, split by kind:

| File | Format | What |
|---|---|---|
| `outputs/reference_audit.md` | **Markdown** | the audit — *issues and analysis* (cross-check, missing key refs, metadata problems, claim departures). Prose findings; RIS cannot carry them. |
| `outputs/references.ris` | **RIS** | the corrected reference list (cited entries), importable into EndNote/Zotero/Mendeley. Built with `build_ris.py --refs <list> --out references.ris --all`. |
| `outputs/pdfs_needed.ris` | **RIS** | references still lacking a readable PDF — the Find-Full-Text upload request. Built with `build_ris.py … --lit Literature --out pdfs_needed.ris --missing`. |

**Bibliographic deliverables are RIS, not markdown** — the reference list and the missing-PDF
request are things the user *imports into a reference manager*, so emit them as RIS. Only the
audit (the issues report) is markdown. Do **not** produce a markdown reference list or a markdown
"PDFs needed" list as the deliverable.

### The audit document (`reference_audit.md`)
Use this shape:

```markdown
# Reference audit — <manuscript filename>

Date: <YYYY-MM-DD>
Target journal: <journal>  ·  Reference style: <journal style / Harvard fallback>

## Summary
<One paragraph: counts — citations with no entry, orphan entries, missing key refs,
existence/metadata errors, formatting fixes, PDFs filed, PDFs needed, claim departures.>

## 1. In-text/caption citations with no reference-list entry
## 2. Reference-list entries never cited
## (reconciliation) Probable same-work mismatches to resolve
## 3. Key references that appear to be missing
## 4 & 5. Existence, metadata, and journal formatting (per entry)
## 6. Full-text PDFs — filed in Literature/ vs. needed from the user
## 7. Claim-vs-source — departures flagged

## Action items for the user
<Numbered, shortest path to a clean reference section: PDFs to supply, claims to re-word,
entries to add/remove, high-confidence metadata fixes ready to apply on request.>
```

## Applying fixes

You are read-only on the manuscript by default. Apply edits only when the user explicitly asks
("apply the metadata fixes", "reformat the list", "delete the orphan entries"). When applying:
- **Metadata/formatting** (check 4 & 5) — `citation-check`'s auto-apply guard governs: title
  casing, journal-name expansion, volume/issue/page fixes, and canonical-DOI substitutions may
  be applied in batch; anything that would change a **first-author surname**, shift the **year
  by more than ±1**, or rewrite the **title's substantive words** is held for manual review.
- **Orphan entries / missing citations** (checks 1 & 2) — propose, but let the user confirm
  each deletion or addition; a "missing" citation may be an in-text typo to fix rather than an
  entry to add.
- **Claim departures** (check 7) — never silently re-word the science. Propose a calibrated
  rewrite and leave the decision to the user.

Log every applied change to `outputs/reference_audit_changes.md` (or beside the draft).

## What this skill does NOT do

- It does not rewrite the manuscript's argument, structure, or prose, and does not run any
  data analysis.
- It does not build a bibliography from scratch or search grey/government literature.
- It does not invent a source, a DOI, or a supporting passage. A reference that cannot be
  verified and a claim that cannot be checked are **flagged**, not papered over.
