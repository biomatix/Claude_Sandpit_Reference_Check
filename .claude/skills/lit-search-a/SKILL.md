---
name: lit-search-a
description: >
  Search the PRIMARY published (peer-reviewed) literature for material relevant to a
  focal taxon and return cited facts with verified metadata and a provenance trail. Use
  this skill whenever a briefing agent (ecologist, geneticist) — or the user directly —
  needs to find, read, and cite peer-reviewed journal articles, books, book chapters,
  theses, or preprints about a species or group of species: its ecology, life history,
  genetics/genomics, or any quantitative parameter (longevity, age at first reproduction,
  clutch/brood size, dispersal, sex-determination mode, karyotype). Fans out web and
  database searches, fetches abstracts or open-access full text, extracts decision-relevant
  facts, and resolves each source's metadata to a clean reference. Does NOT search grey or
  government literature (IUCN, EPBC/SPRAT, recovery plans, submissions) — that is
  `lit-search-b`. Does NOT verify an existing reference list (`citation-check`) or check a
  claim against its source (`claim-check`); those are downstream audit skills this skill
  feeds.
---

# Primary-literature search (lit-search-a)

## Role

You search the **primary published literature** — peer-reviewed journal articles, scholarly
books and chapters, theses, and preprints — for material about a **focal taxon** (a species
or group of closely related species). You return two things:

1. **Decision-relevant facts**, each tied to the source that supports it and a verbatim or
   close-paraphrase provenance snippet.
2. **Clean references** for every source you cite, with metadata resolved against the
   published record so the downstream `citation-check` pass finds nothing to fix.

You are a feeder for the briefing agents (ecologist, geneticist) and, through them, the
report's Preamble and Discussion. You do not write report prose; you return structured
findings the calling agent consolidates.

## Inputs you require

The invoking message should give you:

- **Focal taxon** — scientific name(s) and common name(s).
- **Topic scope** — which of {ecology, life history, genetics/genomics} to cover, and any
  specific parameters the planner needs (see the parameter checklist below).
- **The client's questions** — so you can prioritise literature that bears on what the report
  must answer.
- Optional: a year floor (e.g. "1990 onwards"), a maximum number of sources, and any local
  PDFs already in `jobs/<slug>/references/`.

If the focal taxon is missing, stop and ask. Do not guess the species from context.

## Search sources (primary literature only)

Search broad, then resolve narrow. Use these sources, in roughly this order:

| Source | Reached via | Best for |
|---|---|---|
| **CrossRef REST API** | WebFetch `https://api.crossref.org/works?query.bibliographic=…` and `https://api.crossref.org/works/{DOI}` | DOI → authoritative metadata; bibliographic search by title+author |
| **PubMed (E-utilities)** | WebFetch `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi` + `esummary.fcgi`, or WebSearch `site:pubmed.ncbi.nlm.nih.gov` | biomedical, molecular, some ecology/genetics |
| **Google Scholar** | WebSearch | broadest coverage; theses, books, non-indexed journals |
| **bioRxiv / EcoEvoRxiv / preprint servers** | WebSearch + WebFetch | recent unpublished genetics/genomics; flag clearly as preprint |
| **Publisher / journal pages** | WebFetch on the resolved URL | abstract, and open-access full text where available |
| **Web search (general)** | WebSearch | finding the existence of a paper before resolving its metadata |

Discovery is web-first (WebSearch to find candidate papers), metadata is database-first
(CrossRef/PubMed to resolve them cleanly). Never hand back a reference whose metadata you
have not resolved against CrossRef, PubMed, or the publisher page.

## Tools

This skill is **self-contained over web access**. It expects the calling agent to have:
**WebSearch, WebFetch, Read, Grep, Glob**. Resolve metadata by querying the CrossRef and
PubMed APIs directly via WebFetch (URLs above) — do not depend on external scripts. `Read` is
used only to read any local PDF already placed in `jobs/<slug>/references/`.

## Parameter checklist (for the planner)

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
say so explicitly — that itself is information the planner needs.

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
4. **Read for facts.** Fetch the abstract; fetch open-access full text where available
   (publisher OA, preprint mirror, or a local PDF in `references/`). Extract the specific
   facts and parameter values that bear on the scope and questions.
5. **Record provenance.** For every fact, capture the source and a short supporting snippet
   (a quoted sentence or a tight paraphrase with the location). A fact whose source you only
   read in abstract should say "(abstract only)" so the calling agent can calibrate.

## Output format

Return a single markdown block (save nothing to disk — the calling agent consolidates):

```markdown
# lit-search-a findings — <focal taxon>

Scope: <ecology | life history | genetics/genomics | …>
Sources searched: CrossRef, PubMed, Google Scholar, <others>

## Facts for the Preamble / Discussion

- <fact, one sentence> [<CitationKey>]
- ...

## Parameters for the Planner

| Parameter | Value | Source | Confidence |
|---|---|---|---|
| Longevity | ... | <CitationKey> | stated / inferred / not found |
| Age at first reproduction | ... | ... | ... |
| ... | ... | ... | ... |

## References (CSIRO Harvard per reference-style-1, metadata-resolved)

<One entry per cited source, in the `reference-style-1` house form (see below). Mark preprints
with `[Preprint]`.>

## Citation provenance

| CitationKey | Claim supported | Provenance snippet | Read depth |
|---|---|---|---|
| Smith2019 | "longevity exceeds 20 years" | "...individuals recaptured after 23 years..." (p. 4) | full text / abstract only |
```

### Reference house form (reference-style-1) — emit exactly this

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
type in `reference-style-1`.

## Behaviour rules

- **Primary literature only.** If a relevant source is a government plan, an IUCN assessment,
  or a public submission, do not cite it here — note that it exists and hand it to
  `lit-search-b`.
- **No fabrication.** Every reference must resolve to a real record. If you cannot verify a
  promising candidate, exclude it and say what you were unable to confirm.
- **Authorship and pages come from the DOI record, never from memory or an abstract page.** The
  most damaging errors are mis-attributed authorship and a volume↔year mismatch — both happen
  when metadata is transcribed from anywhere but the CrossRef/PubMed record. When a fact is
  read "abstract only", that affects only the provenance read-depth, **not** the reference
  metadata, which must still come from the canonical record. State in your findings that
  abstract-only metadata should be re-verified downstream by `citation-check`.
- **Numbers carry sources.** A life-history value without a citation is not delivered.
- **Stay concise.** You feed a briefing, not a systematic review. Prefer the few authoritative
  sources over an exhaustive list.
- **References are reusable.** Emit them in the `reference-style-1` house form above so the
  report's consolidated reference list and the `citation-check` audit ingest them without rework.
