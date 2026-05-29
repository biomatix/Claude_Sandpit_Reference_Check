# Biomatix report template — section-by-section conventions

Read this file at the assembly step of `SKILL.md`, before drafting any section. The template
is derived from precedent Biomatix consulting reports and is the prose contract this skill
enforces. The report follows a scientific-paper structure (Materials and Methods → Results →
Discussion), with the client-facing recommendations carried in the Executive Summary.

---

## Section order (mandatory)

1. **Title page** — rendered at the render step from intake metadata; not drafted here.
2. **Citation** — page 2; rendered at the render step.
3. **Title block** (markdown H1, repeats the report title — top of page 3).
4. **Executive Summary** (`## EXECUTIVE SUMMARY`) — summary of results and conclusions,
   **followed by a Recommendations block**.
5. **Brief** (the statement of the brief).
6. **Variation to the Brief**.
7. **Preamble**.
8. **Materials and Methods**
   - 8.1 Data generation (H3, italic: `### *Data generation*`)
   - 8.2 SNP genotyping (H3, italic: `### *SNP genotyping*`)
   - 8.3 Analysis (H3, italic: `### *Analysis*`)
9. **Results**.
10. **Discussion**.
11. **Acknowledgements** (`### Acknowledgements`, flush left) — house-style, brief; retain
    unless the brief says otherwise.
12. **References**.

Sections 4–10 use H2 in ALL CAPS (e.g. `## EXECUTIVE SUMMARY`, `## MATERIALS AND METHODS`,
`## RESULTS`, `## DISCUSSION`). Subsections inside Materials and Methods use italic H3.

Figures and tables are interleaved within Results (and Materials and Methods where a method
needs one) at first reference, not collected at the end.

---

## Section conventions

### Executive Summary

The Executive Summary carries the report's value to a reader who reads nothing else. It has
two parts: a **summary** of results and conclusions, then a **Recommendations** block.

- **Length:** concise — a precis, not a re-run of the report. No hard cap, but discipline is
  house style.
- **Tense:** past for what was done and found ("Samples were taken from …", "Two individuals
  were full sibs …"); present for live recommendations ("Snake BHS06_F should not be included
  in the selection of mating pairs").
- **Voice:** mostly passive for findings; active imperative for recommendations.
- **Summary part:** state the deliverable (what was done), the headline results (what was
  found), and the conclusions drawn. Do not include analysis detail or literature comparison.
- **Recommendations part:** a clearly delimited block (a short paragraph or a bulleted list
  introduced by **Recommendations**) stating the management recommendations arising from the
  analysis. Name specific individuals, populations, or sites where a question implies a
  per-individual decision (e.g. "**Snakes BHS08_F, BHS07_M and BHS19_M should not form
  mating pairs**"). The default is to name; escape to a generic statement only where the
  analysis genuinely cannot identify candidates.
- **Binding facts:** no recommendation may contradict a fact stated in the brief. This is the
  highest-risk regression site in the whole report — cross-check it on the closing pass.
- **Closing sentence:** a one-sentence reminder that the genetic information should be weighed
  alongside the client's other decision factors (animal health, age, body size, prior breeding
  success). House style — Biomatix advises, the client decides.
- **What it is not:** a journal abstract. No background, no aim, no methods sentence. Open with
  the deliverable, not the species.

### Brief

- **Length:** 1–2 sentences. The statement of the questions the client asked of the data.
- **Tense:** infinitive ("To undertake an interim evaluation of …") or past ("Biomatix was
  engaged to …"). Match the contract.
- **Verbatim from intake.** Do not paraphrase or expand.

### Variation to the Brief

- **Length:** the single word `None`, or a short bulleted list.
- One short bullet per agreed deviation (additional analyses requested mid-project; sample-size
  reduction from failed extractions; scope additions). Both parties should have agreed any
  variation in writing before it appears here.

### Preamble

A concise scientific introduction — the kind that opens a journal paper, not an IMRAD
literature review.

- **Length:** 3–4 paragraphs.
- **Tense:** present for species facts ("The broad-headed snake inhabits the Sydney Basin …");
  past for historical events ("A nidovirus epizootic in 2014–2015 killed …").
- **Voice:** declarative; no hedging on well-established facts.
- **Content:** condense the ecologist, conservationist, and geneticist briefings into ~3–4
  paragraphs covering: (i) where the focal taxon lives and how it lives there; (ii) major
  threats and the conservation context; (iii) genetic/genomic background and any management
  actions in train; and (iv) one closing paragraph that links this context to the specific
  question the client asked. The closing paragraph **always** ends with a sentence of the form
  "Here we [verb] [deliverable]". That sentence is the bridge into Materials and Methods.
- **Citations:** every factual claim is cited; provenance is tracked per the citation-provenance
  rule in `SKILL.md`. Draws on `lit-search-a` (ecology, genetics) and `lit-search-b`
  (conservation) sources supplied by the briefing agents.
- **What it is not:** it does not state hypotheses, does not review the literature
  systematically, and does not describe the report's structure. It establishes context and
  ends by pointing at the question.

### Materials and Methods

How the data were generated **and** how they were analysed. Three subsections.

#### Data generation (italic H3)

- **Length:** 1–3 paragraphs. **Tense:** past throughout. **Voice:** passive scientific.
- **Content:** sample provenance (where stored, in what format, by whom), tissue handling
  (extraction kit, robot, proteinase K conditions), the lab vendor, and any technical-replicate
  scheme. Cite the lab pipeline (Kilian et al. 2012; Sansaloni et al. 2011 for DArTseq).
- **House detail:** kit name, manufacturer, and city for reagents and instrumentation. The
  detail is forensic — an auditor must be able to reproduce the lab side.

#### SNP genotyping (italic H3)

- **Length:** 2–4 paragraphs. **Tense:** past throughout.
- **Content:** the DArTseq pipeline (restriction-enzyme combination and why, adaptor design,
  PCR cycling, sequencing platform, read length, sequence count); the proprietary DArT Pty Ltd
  analytical pipeline note; the technical-replicate / repeatability filter; the data file
  received and how it was reconciled with the tissue-collection database.
- **Filtering paragraph:** state which dartRverse filtering steps were applied (secondaries,
  reproducibility, callrate, monomorphs, MAF, …) and the loci/individuals retained. End with
  the loci × individuals count actually used. Cite `dartR` (Gruber et al. 2018) and `dartR v2`
  (Mijangos et al. 2022).

#### Analysis (italic H3)

- **Length:** 1–3 paragraphs. **Tense:** past throughout.
- **Content:** the analyses the planner specified and the analyst executed, in the order the
  Results report them. Name each dartRverse function used and its key non-default parameters.
  Mandatory baseline analyses always appear here: basic summary statistics; a sampling-location
  map (`gl.map.interactive`); and a population-coloured PCA (`gl.pcoa` then `gl.plot.pcoa`).
  Name any external software (e.g. NeEstimator via `gl.LDNe`) and its version. Cite the method
  source for any non-trivial estimator.
- **What it is not:** results. State what was done and how, not what came out.

### Results

What was found. Enough interpretation of each table and statistic that the reader grasps the
finding quickly — but **no discussion** of what it means in the wider context. Discussion is
the next section.

- **Length:** brief. 2–6 paragraphs depending on analysis count. Reports are not journal
  Results — restraint is house style.
- **Tense:** past throughout for findings.
- **Voice:** declarative; cite figures and tables at first reference using `@fig:…` / `@tbl:…`.
- **Content:** for each analysis the planner specified, one paragraph stating what was examined,
  the result (point estimate and any uncertainty in the same sentence), and a pointer to the
  supporting figure/table, with just enough reading of the table/statistic that the result is
  intelligible without the reader reconstructing it. The mandatory map and PCA appear here.
- **What it is not:** a literature comparison, a methods recap, a discussion of alternatives,
  or a recommendation. Findings and their plain reading only.

### Discussion

Interprets the results in the context of what is known and published.

- **Length:** 2–5 paragraphs.
- **Tense:** present for established knowledge and interpretation ("Low heterozygosity is
  consistent with …"); past when restating a specific finding being discussed.
- **Voice:** declarative, measured. Calibrate confidence to the reliability of the result.
- **Content:** place each material finding against the primary literature (from `lit-search-a`)
  and the conservation context (from `lit-search-b`). Explain what the results imply for the
  focal taxon and for the client's questions, note concordance or conflict with published work,
  and state the limitations of the analysis. The recommendations themselves live in the
  Executive Summary; the Discussion supplies the reasoning that justifies them.
- **What it is not:** a restatement of the Results, and not the place to introduce new results.

### Acknowledgements

- **Length:** 2–4 sentences. **Tense:** past.
- **Content:** the client team who collected samples, anyone who advised on analysis or
  interpretation, and any institutional support not already cited. No funding statement; no
  conflict-of-interest statement (the contract is the disclosure).

### References

- **Style:** CSIRO Harvard via the `reference-style-1` skill.
- **Order:** alphabetical by first author surname.
- **DOIs:** include where present, as a bare `doi:` prefix (e.g. `doi:10.1111/1755-0998.12745`),
  not wrapped in `https://doi.org/`.
- **Grey literature:** government, IUCN, and recovery-plan sources (from `lit-search-b`) use
  the issuing authority as author, the document year, the title, the agency/publisher, and a
  stable URL with access date.
- **Consolidation:** the reference list merges the references returned by the ecologist,
  conservationist, and geneticist briefings plus any source added during assembly or review,
  de-duplicated, into one alphabetical list.
- **Reference form.** The authoritative house form is the `reference-style-1` skill:
  `Author IN, Author IN (Year). Title in sentence case. *Journal Name In Full* Volume:pages.
  doi:10.xxxx/xxxxx` — surname+initials with no periods, "and" not "&", no `vol./no./pp.`, a
  bare `doi:` prefix (no `https://doi.org/` wrapper), and the issue number only where pagination
  restarts each issue. The briefing agents already emit this form via `lit-search-a`/`-b`, so the
  consolidated list needs reconciliation (one canonical entry per DOI), not reformatting.

---

## House-style notes

- **Tone:** professional, direct, declarative. Avoid first-person plural ("we") in
  Recommendations — use the imperative or third-person passive. First-person plural is
  acceptable in the Preamble's closing "Here we …" sentence and in Acknowledgements.
- **Animal IDs:** plain text, not backticks. Use the IDs exactly as supplied by the client
  (e.g. `BHS08_F`, not `bhs8f` or `BHS-8F`).
- **Species names:** italicised at every mention (`*Hoplocephalus bungaroides*`).
- **Numbers:** percentages with no space before `%`; units with a non-breaking space
  (`12 m`, not `12m`).
- **Hedging:** acceptable in the Discussion and in a recommendation where the analysis
  genuinely admits multiple interpretations (e.g. "either full sibs or in a parent–offspring
  relationship") — but the recommendation's action must remain unambiguous (e.g. "**only one
  of BHS15_F and BHS17_F should be included**").
- **No emoji, no exclamation marks, no rhetorical questions.**

---

## Worked example anchors

The Aussie Ark *Hoplocephalus bungaroides* relatedness report (Georges 2024, updated
17-Nov-2025) is the canonical exemplar of the prose tone and length. Note that the exemplar
predates the move to the Materials and Methods → Results → Discussion structure: use it for
tone and concision, not for section order.
