---
name: citation-check
description: >
  Verify that every entry in a reference list points to a real publication and that the metadata
  in the entry matches the published record. Parses BibTeX files or prose-formatted reference
  lists (e.g. CSIRO Harvard), then for each entry resolves the DOI via CrossRef, or — if no DOI
  is present — searches PubMed (biomedical) or Google Scholar (other) by title + first author +
  year, and compares the returned metadata against what is written. Flags fabricated entries,
  invalid or mismatched DOIs, wrong years, mistyped or missing authors, mistyped title words,
  wrong or swapped page ranges, abbreviated journal names, missing required fields, and
  duplicates. Proposes a corrected entry alongside each error and, on request, applies the fix
  in place. Use whenever the user asks you to verify, validate, audit, fact-check, sanity-check,
  or "check the references exist" in a reference list or bibliography. Does NOT cross-check
  in-text citations against the reference list (a separate concern). Does NOT reformat
  references — use `reference-style` for that.
---

# Citation existence and accuracy check

## Role

You verify that every reference in a reference list points to a real publication, that the metadata in the entry matches the published record, and you propose corrections for any errors found.

## Scope

**In scope:**
- Parsing a reference list (BibTeX `.bib` file, prose pasted in chat, or the reference list of a manuscript document).
- For each entry, resolving the DOI (or searching CrossRef / PubMed / Google Scholar by title + first author + year) to retrieve the canonical metadata.
- Comparing canonical metadata against the entry as written, field by field.
- Reporting errors with a suggested correction and, on request, applying corrections in place.

**Out of scope (other skills handle these):**
- Cross-checking that each reference is cited somewhere in the manuscript text, or that every in-text citation has a matching reference. Do not read or parse the manuscript body for citations.
- **Verifying that the cited paper actually supports the in-text assertion that cites it.** That is the job of `claim-check`, which retrieves the cited content (open-access PDF/HTML, preprint mirror, or abstract as fallback) and compares it to the carrying sentence. `citation-check` and `claim-check` are complementary: existence + metadata vs. assertion vs. source. A draft going to a client or journal should pass both.
- Reformatting references in any particular style (e.g. CSIRO Harvard, APA, Vancouver). Use `reference-style` for that.
- Searching for new papers to add to the bibliography or building a bibliography from scratch.

If the user asks for any of the above, point them to the relevant skill and stop.

## Inputs

Accept any of:
- A path to a `.bib` file.
- A path to a Markdown, plain-text, or Word manuscript whose reference list is at the end. If so, extract only the reference list — ignore the body.
- A block of prose references pasted directly into the chat.

If the input is ambiguous, ask before proceeding.

## Workflow

### Step 1 — Parse the reference list

**BibTeX:** run `python scripts/validate_citations.py <file.bib>` first. This parses the file and reports structural problems (missing required fields, malformed years, duplicates) before any network call. Capture the output.

**Prose:** parse each entry yourself into a record with these fields where present:
- `authors` (list of surnames + initials)
- `year`
- `title`
- `journal` (or book title / venue)
- `volume`
- `pages` (or article ID)
- `doi`

If you cannot confidently parse an entry, flag it as `[UNPARSED]` and skip verification for that entry — do not guess fields.

### Step 2 — Verify each entry

For each parsed entry, in order:

1. **DOI present →** run `python scripts/extract_metadata.py --doi <DOI>` to fetch the canonical CrossRef record. Compare each field against what is written:
   - **Title** — allow minor punctuation, hyphenation, and case differences. Flag substantive word changes.
   - **First author surname** — must match. Compare additional authors on surname plus first initial only (full given names vary by source).
   - **Year** — must match.
   - **Journal name** — must match in full. Flag abbreviations.
   - **Volume, issue, pages / article ID** — must match.

2. **No DOI →** if the entry looks biomedical, run `python scripts/search_pubmed.py "<first author surname> <three or four key title words> <year>"`. Otherwise run `python scripts/search_google_scholar.py "<first author surname> <three or four key title words> <year>"`. If a single high-confidence match is returned, perform the comparison as above. If no confident match is found, flag as `[UNVERIFIED]` — do not assume fabrication on a search miss alone (search APIs are imperfect).

3. **DOI does not resolve (HTTP 404 from CrossRef) →** flag as `[ERROR] invalid or fabricated DOI`. Then attempt step 2 by title + author + year to see whether the cited paper exists under a different DOI.

For batch verification of a `.bib` file, `python scripts/validate_citations.py --check-dois <file.bib>` performs steps 1 and 3 in one pass.

### Step 3 — Report and correct

Produce one block per problem entry:

```
[STATUS] <CitationKey or "FirstAuthor Year">
  Problem: <short description>
  Written:   <the field as currently written>
  Canonical: <the value from the resolved record>
  Suggested correction: <full corrected entry, in the same format as the input>
```

Where `[STATUS]` is one of:
- `[ERROR]` — definite mismatch with the canonical record, or DOI fails to resolve.
- `[WARNING]` — probable issue (e.g. abbreviated journal name, missing recommended field).
- `[UNVERIFIED]` — could not locate the record via DOI or search. Human review needed.
- `[UNPARSED]` — entry could not be parsed into structured fields.

Omit `[OK]` entries from the report unless the user asks for a full pass.

If the user asks you to **apply** corrections:
- For BibTeX files: use `Edit` to replace each problem entry with the corrected version. Summarise what changed.
- For prose references in the chat: return the full corrected reference list as a clean block, with the same ordering as the input.
- For a manuscript document: confirm with the user before editing it in place.

### Auto-apply guard (mandatory when applying without per-entry confirmation)

When the user has authorised batch application of corrections (a single up-front "apply all" rather than per-entry approval), the following classes are **eligible** for unattended fixing — apply them silently and list them in the closing summary:

- `[ERROR]` or `[WARNING]` where the only changes are: title casing or punctuation, abbreviated → full journal name, missing volume/issue/pages/article ID, page-range typo, missing or malformed DOI replaced with the canonical DOI returned by CrossRef, additional-author surname or initial.

The following classes are **never** auto-applied even in batch mode — flag them in a separate `## Manual review required` block and leave the entry unchanged:

- `[UNVERIFIED]` — no canonical record could be located. Auto-applying nothing prevents silent rewrites driven by a false-positive search match.
- `[UNPARSED]` — entry could not be parsed into structured fields.
- Any correction that would change the **first author surname**, the **publication year by more than ±1**, or the **title's substantive words** (i.e. word-token Jaccard similarity below 0.6 between written and canonical title). These are signals that the wrong paper was retrieved, not a typo in a real entry.
- Any entry where CrossRef / PubMed returned a network error or rate-limit response. Retry on the next run; do not assume fabrication.

After a batch run, write a `citation_check_changes.md` log **alongside the input file** (i.e. in the same directory as the `.bib` or manuscript that was checked) with one section per applied change (entry key, what changed, source of the canonical value) and one section listing the deferred manual-review items. The user reviews this log instead of approving each correction live.

## Bundled scripts

The following ship with this skill in `scripts/`:

- `validate_citations.py` — BibTeX hygiene; required-field validation; optional `--check-dois` flag for CrossRef resolution; duplicate detection. **Primary tool for BibTeX inputs.**
- `extract_metadata.py` — fetches canonical metadata from CrossRef (`--doi`), PubMed (`--pmid`), or arXiv (`--arxiv`). **Primary tool for per-entry verification.**
- `search_pubmed.py` — PubMed E-utilities search; used as a fallback when no DOI is present (biomedical references).
- `search_google_scholar.py` — Google Scholar search; used as a fallback when no DOI is present (non-biomedical references). Rate-limited; use sparingly.
- `doi_to_bibtex.py` — DOI → BibTeX. Useful for generating a clean replacement entry once a verified DOI is in hand.
- `format_bibtex.py` — BibTeX cleaner. **Not used by this skill** (formatting is out of scope); kept for completeness.

Reference documentation in `references/` covers field requirements (`metadata_extraction.md`), validation criteria (`citation_validation.md`), and search syntax (`pubmed_search.md`, `google_scholar_search.md`). Consult only when needed.

## Dependencies

Python 3 with `requests`. Install with `pip install requests` if missing.

## Common pitfalls

- **Capitalisation differences are not errors.** CrossRef returns titles in their original case; ignore pure case differences.
- **Author initials vs. full given names.** Sources differ. Compare on surnames plus at least one initial.
- **Article IDs vs. page ranges.** Modern e-journals (e.g. *International Journal of Wildland Fire*) use article IDs like `WF24031`; absence of a page range is not an error.
- **Preprints.** A bioRxiv or arXiv DOI is a valid record even without a journal name.
- **Same author, same year — letter suffix.** Two distinct papers by the same first author in the same year (e.g. `Smith JA 2023a` and `Smith JA 2023b`) are not duplicates. Distinguish by title.
- **Network failures.** If CrossRef or PubMed is unreachable, report the network error and continue with the remaining entries — do not flag entries as fabricated when verification could not run.
- **Rate limits.** CrossRef tolerates polite use; PubMed E-utilities is capped at 3 requests/second without an API key. For lists over ~100 entries, insert a short delay between calls.
