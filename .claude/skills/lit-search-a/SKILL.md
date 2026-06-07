---
name: lit-search-a
description: >
  Search the PRIMARY published (peer-reviewed) literature on a topic or focal taxon and
  return candidate sources with verified metadata and a provenance trail. Use this skill
  whenever `/reference-check` — or the user directly — needs to (a) surface key published
  works a manuscript appears to be MISSING, or (b) locate and resolve the metadata / full-text
  PDF of a specific paper. Covers peer-reviewed journal articles, books, book chapters,
  theses, and preprints, including any quantitative parameter where the manuscript's field is
  ecology/genetics (longevity, age at first reproduction, clutch/brood size, dispersal,
  sex-determination mode, karyotype). Fans out web and database searches, fetches abstracts or
  open-access full text, and resolves each source's metadata to a clean reference. Does NOT
  verify an existing reference list (`citation-check`) or check a claim against its source
  (`claim-check`); those are the audit skills this one feeds.
---

# Primary-literature search (lit-search-a)

## Role

You search the **primary published literature** — peer-reviewed journal articles, scholarly
books and chapters, theses, and preprints — on a topic or about a **focal taxon** (a species
or group of closely related species). You serve two purposes for `/reference-check`:

1. **Missing-reference scan** — surface well-known, load-bearing works a manuscript on this
   topic omits (the foundational method paper, the standard reference for the study species, a
   directly contradicting or superseding recent paper), each with a one-line reason it belongs.
2. **Source location** — find a specific paper, resolve its metadata against the published
   record so `citation-check` finds nothing to fix, and surface its full-text PDF so it can be
   filed in `Literature/`.

You do not write manuscript prose; you return structured findings the caller consolidates.

## Inputs you require

The invoking message should give you:

- **Topic and/or focal taxon** — the manuscript's subject, and the scientific/common name(s)
  of any focal species.
- **Topic scope** — which of {ecology, life history, genetics/genomics, methodology} to cover,
  and any specific parameters to look for (see the parameter checklist below).
- **The manuscript's key claims** — so you can prioritise literature that bears on what the
  manuscript asserts (for the missing-reference scan).
- Optional: a year floor (e.g. "1990 onwards"), a maximum number of sources, and any PDFs
  already in `Literature/` or `jobs/<slug>/references/`.

If neither a topic nor a focal taxon is given, stop and ask. Do not guess the subject from
context.

## Search sources (primary literature only)

Search broad, then resolve narrow. Use these sources, in roughly this order:

| Source | Reached via | Best for |
|---|---|---|
| **CrossRef REST API** | WebFetch `https://api.crossref.org/works?query.bibliographic=…` and `https://api.crossref.org/works/{DOI}` | DOI → authoritative metadata; bibliographic search by title+author |
| **PubMed (E-utilities)** | WebFetch `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi` + `esummary.fcgi`, or WebSearch `site:pubmed.ncbi.nlm.nih.gov` | biomedical, molecular, some ecology/genetics |
| **Google Scholar** | WebSearch | broadest coverage; theses, books, non-indexed journals |
| **bioRxiv / EcoEvoRxiv / preprint servers** | WebSearch + WebFetch | recent unpublished genetics/genomics; flag clearly as preprint |
| **Publisher / journal pages** | WebFetch on the resolved URL | abstract, and open-access full text where available |
| **Georges lab publications** | WebFetch `http://georges.biomatix.org/publications/all` | the publication list of A. Georges and collaborators — Australian freshwater turtles (incl. *Myuchelys*, *Emydura*, *Elseya*), reptile sex determination, conservation genetics. Often the primary source for focal-taxon parameters; check it whenever the focal taxon is an Australian reptile or A. Georges is a plausible author, then resolve each hit's metadata via CrossRef as usual. |
| **Web search (general)** | WebSearch | finding the existence of a paper before resolving its metadata |

Discovery is web-first (WebSearch to find candidate papers), metadata is database-first
(CrossRef/PubMed to resolve them cleanly). Never hand back a reference whose metadata you
have not resolved against CrossRef, PubMed, or the publisher page.

## Tools

This skill is **self-contained over web access**. It expects the calling agent to have:
**WebSearch, WebFetch, Read, Grep, Glob**. Resolve metadata by querying the CrossRef and
PubMed APIs directly via WebFetch (URLs above) — do not depend on external scripts. `Read` is
used only to read any local PDF already placed in `jobs/<slug>/references/`.

## Parameter checklist (when the manuscript's field is ecology/genetics)

When the topic scope includes life history or genetics, actively hunt for these values, each
with a source and a number (or an explicit "not found in the primary literature"):

- longevity / maximum age
- age (or size) at first reproduction
- clutch or brood size
- duration of the breeding season
- clutch/brood frequency per breeding season
- generation time (derived or stated)
- dispersal distance and whether it is **sex-biased**
- mode of sex determination (GSD/TSD, heterogamety)
- karyotype / chromosome number
- effective population size or any prior genetic-diversity estimates for the taxon
- any analytical approach the primary literature has used successfully on this or a sister taxon

A value with no source is not a finding. If the primary literature is silent on a parameter,
say so explicitly — that itself is information the caller needs.

## Method

1. **Plan the queries.** Translate the topic scope and client questions into 4–8 concrete
   search queries. Vary the angle (by species name, by parameter, by sister taxon, by method).
2. **Fan out discovery.** Run the queries across WebSearch / Google Scholar / PubMed. Collect
   candidate titles + DOIs.
3. **Resolve metadata — from the canonical record, not the abstract page.** For each kept
   candidate, fetch the **CrossRef record for the DOI** (`https://api.crossref.org/works/{DOI}`)
   and take the **author list, year, journal, volume, and page range verbatim from that record**.
   Do not transcribe authors or pages from a publisher abstract page, a PDF header, a Google
   Scholar snippet, or memory — those are the source of the most common errors (mis-attributed
   authorship, wrong pages, volume↔year mismatch). Where no DOI exists, resolve against PubMed
   (E-utilities `esummary`) and treat its record as canonical. **One DOI = one canonical entry:**
   if you cite a paper more than once, or two findings point to the same DOI, the author/year/
   pages must be byte-identical every time. Discard any candidate you cannot resolve to a real
   record — never pass through an unverifiable reference.
4. **Read for facts — follow the full-text retrieval cascade below.** Extract the specific
   facts and parameter values that bear on the scope and questions.
5. **Record provenance.** For every fact, capture the source, a short supporting snippet
   (a quoted sentence or a tight paraphrase with the location), and the **read depth /
   retrieval tier** (full text — references/ | full text — local library | full text — OA |
   abstract only | awaiting PDF) so the calling agent can calibrate.

### Full-text retrieval cascade (when you need more than the abstract)

A claim is **load-bearing** when a quantitative parameter is drawn from it or a downstream
`claim-check` must verify it. For load-bearing claims, do not settle for the abstract — work
the cascade in order and stop at the first tier that yields the full text:

1. **Job references folder** — `jobs/<slug>/references/`. `Glob` it and read any PDF that
   matches the source (by `<CitationKey>.pdf`, or by first-author surname + year). This is
   where the user places PDFs you have requested.
2. **Claude cache** — `Literature/` (in the sandpit root). The harness's own
   store of previously fetched full-text PDFs, named `<Surname>_<Year>_<sanitised-DOI>.pdf`
   (a 2020 Smith paper at `10.1111/mec.14497` → `Smith_2020_10.1111_mec.14497.pdf`), so a `Glob`
   for `*<sanitised-DOI>.pdf` (the DOI sits in the name) — or by first-author surname + year — is a
   near-zero-read match. Grown automatically (see tier 4).
3. **Personal library** — `D:/workspace/AA_Literature/` (read-only; the user's
   subscription-sourced library, reused across jobs). Identify a matching PDF in two passes:
   - **Filename pass (cheap, first).** `Glob` the library recursively and select any PDF whose
     filename or path contains the first-author surname **and** year (or the DOI).
   - **First-page pass (fallback, filename-agnostic).** If the filename pass yields no confident
     match — filenames are opaque, hashed, or scanned-in — **read the first page of candidate
     PDFs** with the Read tool (`pages: "1"`). The first page almost always carries the title,
     author list, year, and often the DOI — enough to identify the paper. Narrow candidates
     first where you can (filenames sharing any token — surname, a title word, or the year); if
     filenames carry no usable token at all, scan first pages, but **cap the scan at ~40 PDFs
     per source** and, if the library is larger and unindexed, stop and fall through to tier 4/5
     rather than reading hundreds of files — and note in your output that the library would
     benefit from descriptive filenames (`<Surname>_<Year>_<DOI>`) or an index.
   Confirm the match (title + first author + year agree) before reading the body. If two
   candidates are plausible, prefer to request rather than cite the wrong paper. **A library
   paper that ends up cited is also copied into `Literature/`** as
   `Literature/<Surname>_<Year>_<sanitised-DOI>.pdf` (author, year and DOI are already known from discovery), so
   later runs resolve it at tier 2 and skip this scan — the copy is filed by `/reference-check`
   (its PDF-filing step), not by you; surface the matched file path and DOI in your provenance
   so the deposit can be made.
4. **Open-access web** — Unpaywall (uses `CLAIM_CHECK_EMAIL`) → PMC → preprint mirror →
   publisher open-access → as a last automated step, the CrossRef/PubMed abstract. A full-text
   PDF obtained here for a source that ends up **cited in the manuscript** is filed to
   `Literature/<Surname>_<Year>_<sanitised-DOI>.pdf` so the next run hits tier 2 — the deposit
   is filed by `/reference-check`, not by you: surface the DOI and the open-access PDF URL in
   your provenance so it can be filed.
5. **Request the PDF from the user.** If the source is paywalled, load-bearing, and absent from
   tiers 1–3, **do not cite the load-bearing claim from the abstract alone.** Add the source to
   a **`## Full text needed`** block in your output (citation key, DOI, title, and the exact
   parameter/claim that needs it) and mark its provenance read depth **"awaiting PDF"**.
   `/reference-check` relays the request; the user drops the PDF into `Literature/` (or
   `jobs/<slug>/references/`) and the step re-runs.

You only ever **read** `Literature/`, `references/`, and the personal library — you write to
none of them; the user owns `references/` and the personal library, and `/reference-check`
files PDFs into `Literature/`. Background/context citations that do not carry a parameter or a
verifiable assertion may remain "abstract only" without a request.

## Output format

Return a single markdown block (save nothing to disk — the calling agent consolidates):

```markdown
# lit-search-a findings — <focal taxon>

Scope: <ecology | life history | genetics/genomics | …>
Sources searched: CrossRef, PubMed, Google Scholar, <others>

## Candidate sources / facts

- <fact or candidate source, one sentence> [<CitationKey>]
- ...

## Parameters found (if a parameter scope was requested)

| Parameter | Value | Source | Confidence |
|---|---|---|---|
| Longevity | ... | <CitationKey> | stated / inferred / not found |
| Age at first reproduction | ... | ... | ... |
| ... | ... | ... | ... |

## References (CSIRO Harvard per reference-style, metadata-resolved)

<One entry per cited source, in the `reference-style` house form (see below). Mark preprints
with `[Preprint]`.>

## Citation provenance

| CitationKey | Claim supported | Provenance snippet | Read depth |
|---|---|---|---|
| Smith2019 | "longevity exceeds 20 years" | "...individuals recaptured after 23 years..." (p. 4) | full text (library) / OA / abstract only / awaiting PDF |

## Full text needed

<Only the load-bearing sources you could not obtain in full from references/, the local
library, or open access. Omit this section if there are none.>

| CitationKey | DOI | Title | Why full text is needed |
|---|---|---|---|
| Jones2018 | 10.xxxx/xxxx | ... | needed to verify the carrying claim; abstract gives no detail |
```

### Reference house form (reference-style) — emit exactly this

Format references in the CSIRO Harvard house form so the consolidated list needs no rework:

`Author1 IN, Author2 IN, Author3 IN (Year). Title in sentence case. *Journal Name In Full* Volume:firstpage–lastpage. doi:10.xxxx/xxxxx`

- **Authors:** surname then initials with **no periods and no spaces** (`Georges A`, not
  `Georges, A.`); join with **"and"**, never `&`; **never** truncate with an ellipsis.
- **Year** in parentheses, then `. ` before the title.
- **Title** sentence case, no terminal period before the journal; italicise any scientific name.
- **Journal** italicised and spelled out in full (never abbreviated).
- **Volume:pages** — volume then a colon then the page range with an **en-dash (–)**; **no
  `vol.`/`no.`/`pp.`**; include the issue number only when each issue restarts pagination.
- **DOI** as a bare `doi:` prefix — **no** `https://doi.org/` wrapper, no trailing period.
- Worked example: `Gruber B, Unmack PJ, Berry OF, Georges A (2018). dartR: an R package to
  facilitate analysis of SNP data generated from reduced representation genome sequencing.
  *Molecular Ecology Resources* 18:691–699. doi:10.1111/1755-0998.12745`

For books, chapters, theses, preprints, datasets, and reports, follow the corresponding entry
type in `reference-style`.

## Behaviour rules

- **Primary literature focus.** If a relevant source is a government plan, an IUCN assessment,
  or a public submission, note that it exists rather than treating it as a peer-reviewed
  reference.
- **No fabrication.** Every reference must resolve to a real record. If you cannot verify a
  promising candidate, exclude it and say what you were unable to confirm.
- **Authorship and pages come from the DOI record, never from memory or an abstract page.** The
  most damaging errors are mis-attributed authorship and a volume↔year mismatch — both happen
  when metadata is transcribed from anywhere but the CrossRef/PubMed record. When a fact is
  read "abstract only", that affects only the provenance read-depth, **not** the reference
  metadata, which must still come from the canonical record. State in your findings that
  abstract-only metadata should be re-verified downstream by `citation-check`.
- **Numbers carry sources.** A life-history value without a citation is not delivered.
- **Stay concise.** You feed a reference check, not a systematic review. Prefer the few
  authoritative sources over an exhaustive list.
- **References are reusable.** Emit them in the `reference-style` house form above so the
  manuscript's reference list and the `citation-check` audit ingest them without rework.
