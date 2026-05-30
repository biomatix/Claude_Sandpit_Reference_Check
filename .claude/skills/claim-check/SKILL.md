---
name: claim-check
description: >
  Verify that each in-text citation in a draft Biomatix consulting report points to a
  source that actually supports the carrying assertion. Extracts
  (citation_key, carrying_sentence) pairs from the draft, resolves each citation key to a
  DOI from the matching .bib file, retrieves cited content (local PDF override → DOI
  open-access PDF/HTML via Unpaywall → preprint mirror → CrossRef abstract → PubMed
  abstract), and judges each claim as supported, partially supported, contradicted, not
  found in retrieved text, or paywalled — manual check needed. Distinct from
  `citation-check`, which verifies references EXIST and that their metadata is correct
  but does NOT read the cited text. Use whenever the user asks "does the source
  actually support this claim", "verify the assertions", "audit the citations for
  accuracy of use", or as part of a /review.
---

# Claim-vs-source verification

## Role

You verify that each in-text citation's carrying assertion is actually supported by the cited paper. You complement `citation-check` (which confirms the reference *exists* and its metadata is correct) by reading the cited content and comparing it to what the prose claims.

You operate in two modes:
- **Single-citation mode** — the user pastes one or two assertions and citations and asks you to verify them.
- **Whole-draft mode** — the user supplies a draft and a `.bib` file and asks you to audit every citation. Used by `critic-citations` and `/review`.

The drafts you audit are Biomatix consulting reports produced by `/popgen-report`.

## Scope

**In scope:**
- Extracting (citation_key, carrying_sentence) pairs from a markdown draft.
- Resolving each citation key to a DOI via the `.bib` file.
- Retrieving cited content in this priority order:
  1. Local PDF at `jobs/<slug>/references/<citation_key>.pdf`, if present.
  2. Shared local library `C:/workspace/literature/` (read-only) — `Glob` it recursively for a
     PDF whose filename or path matches the source by first-author surname + year, or the DOI.
  3. DOI → open-access PDF or HTML via the Unpaywall API.
  4. Preprint mirror (bioRxiv, PMC, arXiv) where DOI maps to one.
  5. CrossRef abstract (always available for resolvable DOIs).
  6. PubMed abstract (biomedical only).
- Comparing the carrying assertion against the retrieved passage and assigning a verdict.
- Writing a per-claim audit table to `outputs/claims_audit.md`.

**Out of scope (other skills handle these):**
- Verifying that the reference *entry* in the bibliography is correct (that is `citation-check`).
- Reformatting references in any particular style (use `reference-style-1`).
- Critiquing prose, structure, or scientific substance.
- Re-running computational analyses.

If the user asks for any of those, point them to the relevant skill and stop.

## Inputs

Accept any of:
- A path to a markdown draft (`report_draft.md`) plus the matching `.bib` file. Both are required for whole-draft mode.
- A pasted block of (assertion, citation_key) pairs plus the `.bib`. Used for single-citation spot checks.
- Optional: the job slug (e.g. `awc-mala-20260420`) so the skill can locate `jobs/<slug>/references/` for any local PDF overrides. If absent, ask before retrieval starts.

If the draft has no citations, say so and stop.

## The five verdicts

For each (assertion, citation) pair, return exactly one of:

1. **supported** — retrieved text directly supports the assertion. Quote the supporting passage; the verdict cannot stand without a quote.
2. **partially supported** — retrieved text supports part of the assertion but the prose over-states or generalises it. Quote the supporting passage and explain the over-reach.
3. **contradicted** — retrieved text says the opposite of what the prose claims, or restricts the claim to a context the prose ignores. Quote the contradicting passage.
4. **not found in retrieved text** — full text was retrieved but the supporting passage was not present. Distinguishes from "paywalled" (text not available) and from "contradicted" (text says otherwise). State which sections of the source were searched.
5. **paywalled — manual check needed** — full text was not retrievable through any channel (job `references/`, the shared library `C:/workspace/literature/`, Unpaywall, preprint, open mirror) and the assertion cannot be verified from the abstract alone. This is a first-class verdict, not a hidden failure. The standing **suggested action** is for the user to download the PDF and drop it into `jobs/<slug>/references/<citation_key>.pdf` (or add it to the shared library), after which the claim is re-checked.

**Honesty rules** — never report "supported" without quoting the supporting passage. Never silently downgrade "paywalled" to "supported" or "unverified". An assertion verifiable only from the abstract that is in fact supported by the abstract should be reported as `supported (abstract only)` so the reader knows the depth of evidence.

## Workflow

### Step 1 — Extract claims

Run:

```bash
python .claude/skills/claim-check/scripts/extract_claims.py <draft.md>
```

The script outputs a TSV with one row per in-text citation: `citation_key\tcarrying_sentence\tline_number`.

A citation appears as `(Smith 2023)` or `(Smith and Jones 2023)` or `(Smith et al. 2023)` or `[@smith2023]` (pandoc citeproc style). The script handles both. Compound citations (`(Smith 2023; Jones 2024)`) split into two rows sharing the same carrying sentence.

If the script returns zero rows, stop and tell the user the draft has no recognisable in-text citations.

### Step 2 — Resolve DOIs

For each unique citation_key in the TSV, look up the matching entry in the `.bib` file. Most entries will have a DOI field. For those that do not, the skill cannot check the assertion against full text — record that citation as `verdict = paywalled — manual check needed (no DOI)` and move on.

### Step 3 — Retrieve cited content

For each (citation_key, doi) pair, run:

```bash
python .claude/skills/claim-check/scripts/resolve_full_text.py \
  --doi "<doi>" \
  --citation-key "<key>" \
  --local-dir "jobs/<slug>/references/"
```

The script returns JSON with `kind` (one of `local_pdf`, `open_access_pdf`, `open_access_html`, `preprint`, `abstract_only`, `not_found`), `text_path` (path to a `.txt` file with extracted text — written into `outputs/.claim_check_cache/`), and `source_url`. The cache lets repeat runs skip re-fetch.

**Shared-library fallback (before declaring paywalled).** The script's `--local-dir` only matches `<citation_key>.pdf`, so it will not find the user's library where filenames differ. When the script returns `abstract_only` or `not_found` and the assertion needs full text, search the shared library `C:/workspace/literature/` in two passes: (1) **filename pass** — `Glob` `**/*.pdf` and pick the PDF matching by first-author surname + year (or DOI); (2) **first-page pass** — if no confident filename match, read the first page of candidate PDFs (`Read` with `pages: "1"`) to identify by title/authors/year/DOI, narrowing by any shared filename token first and capping at ~40 PDFs (if the library is larger and unindexed, stop and keep the paywalled verdict rather than scanning hundreds). On a confirmed match, **read it with the Read tool** and assess the claim against that text, recording `kind = local_pdf (library)`. The library is read-only — never copy into or write it. Only if neither pass finds the source does the claim stay paywalled.

Mapping from `kind` to which verdicts are reachable:
- `local_pdf`, `open_access_pdf`, `open_access_html`, `preprint` → all five verdicts reachable.
- `abstract_only` → `supported (abstract only)`, `partially supported (abstract only)`, `contradicted (abstract only)`, or `paywalled — manual check needed` (if the abstract does not address the assertion).
- `not_found` → always `paywalled — manual check needed`.

### Step 4 — Compare claim to source

For each (claim, text_path) pair, run:

```bash
python .claude/skills/claim-check/scripts/find_passage.py \
  --claim "<carrying_sentence>" \
  --text "<text_path>"
```

The script returns the top three candidate supporting passages from the source text, ranked by keyword overlap with the claim. **You** (the LLM) then read the top candidate and assign the verdict semantically — keyword overlap alone is not sufficient because synonyms and paraphrasing matter.

If the top candidate's overlap score is below the script's threshold, the verdict starts at `not found in retrieved text`; you must still read the candidate to confirm the source does not support the claim through paraphrase before finalising.

### Step 5 — Write the audit

Append rows to `outputs/claims_audit.md`:

```markdown
# Claims audit — <draft filename>

Date: <YYYY-MM-DD>
Cache: outputs/.claim_check_cache/

| Citation | Carrying sentence | Source kind | Verdict | Supporting / contradicting passage | Suggested action |
|---|---|---|---|---|---|
| Smith 2023 | "Generation time is 11–13 years." | open_access_pdf | supported | "Mean generation time across populations was 11.8 years (SD 0.7), range 11–13." (p. 214) | none |
| Doe 2024 | "Inbreeding depression is severe in this lineage." | abstract_only | paywalled — manual check needed | abstract does not address inbreeding depression directly | drop PDF into `jobs/<slug>/references/doe2024.pdf` and rerun |
| Lee 2022 | "Genetic rescue requires unrelated source individuals." | open_access_pdf | partially supported | "Genetic rescue benefits from low-relatedness sources, but related sources can succeed when alternatives are unavailable (p. 312)." | rewrite assertion to match the cited nuance |
```

Where the verdict is `partially supported` or `contradicted`, the **suggested action** column should propose a calibrated rewrite — usually a softening or a restriction in scope — that aligns the prose with what the source actually says. Where the verdict is `supported (abstract only)`, suggest the user obtain the full text if the assertion is load-bearing.

## Failure modes and how to handle them

- **Bib file missing or unparseable.** Stop and ask the user. Do not attempt to verify any citations from prose alone.
- **DOI present in bib but does not resolve.** Record `verdict = paywalled — manual check needed (DOI not resolved)`. This is also a citation-check finding; flag it for that skill.
- **Unpaywall says open access but the URL 404s.** Fall back through the priority list (preprint, abstract). Record the source kind that succeeded, not the one that failed.
- **PDF text extraction returns mostly garbage** (scanned PDFs without OCR). Record `kind = local_pdf (extraction failed)` and treat as `paywalled — manual check needed`. Suggest the user OCR the PDF or accept the manual check.
- **The carrying sentence cites multiple sources** (`(Smith 2023; Jones 2024)`). Audit each independently; if Smith is supported and Jones is contradicted, the assertion is partially supported.
- **The carrying sentence is a long compound claim.** Decompose into atomic claims and audit each. Report the most pessimistic verdict for the sentence as a whole.

## Auto-apply guard

This skill does **not** edit the draft. The audit table is your output. The orchestrator (the user, `critic-citations`, or `/review`) decides whether and how to act on the suggestions.

## Honesty checklist before returning

Before you hand the audit back:

1. Is every "supported" verdict accompanied by a quoted passage from the retrieved source? If not, downgrade to "not found in retrieved text".
2. Is every "paywalled" verdict labelled exactly "paywalled — manual check needed"? Soft language (e.g. "could not verify", "may be supported") is forbidden.
3. Did you mark abstract-only verdicts with "(abstract only)" suffix? If not, add it.
4. Did you suggest a rewrite for every "partially supported" or "contradicted" entry? If not, add one.
