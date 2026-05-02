# Biomatix report template — section-by-section conventions

Read this file at Step 3 of `SKILL.md` (Assembly), before drafting any section. The template is derived from precedent Biomatix consulting reports and is the prose contract this skill enforces.

---

## Section order (mandatory)

1. **Cover page** — rendered at Step 6 from intake metadata; not drafted here.
2. **Citation** — page 2; rendered at Step 6.
3. **Title block** (markdown H1, repeats the report title — appears at the top of page 3).
4. **Executive Summary** (H2 in ALL CAPS: `## EXECUTIVE SUMMARY`)
5. **Brief**
6. **Variation to the Brief**
7. **Preamble**
8. **Preliminary Analysis**
   - 8.1 Data generation (H3, italic: `### *Data generation*`)
   - 8.2 SNP genotyping (H3, italic: `### *SNP genotyping*`)
9. **Results**
10. **Strategy**
11. **Acknowledgements** (H3 or H2 depending on weight given — typically `### Acknowledgements` flush left, no all-caps)
12. **Tables** (interleaved within Results / Strategy at first reference, not at end — but a final summary table per Q is conventional)
13. **References**

Sections 4–10 use H2 in ALL CAPS (e.g. `## EXECUTIVE SUMMARY`, `## STRATEGY`). Subsections inside Preliminary Analysis use italic H3.

---

## Section conventions

### Executive Summary

- **Length:** No limit on the length, but should remain concise precis of the report including specifically at the end, the management recommendations.
- **Tense:** past tense for what was done and found ("Samples were taken from …", "Two female individuals were either full sibs …"); present tense for live recommendations ("Snake BHS06_F should not be included in the selection of mating pairs").
- **Voice:** mostly passive for findings; active imperative for recommendations directed at the client.
- **Content:** state the deliverable (what was done), the headline result (what was found), the named individuals or populations the recommendations apply to, and any binding-fact-driven caveats. Do not include analysis details.
- **What it is not:** a journal abstract. No background, no aim, no methods sentence. Open with the deliverable, not the species.
- **Closing paragraph:** a one-sentence reminder that the genetic information should be considered alongside other client decision factors (animal health, age, body size, prior breeding success). This is house style and grounds the report's authority — Biomatix advises but does not decide.

### Brief

- **Length:** 1–2 sentences.
- **Tense:** infinitive ("To undertake an interim evaluation of …") or past ("Biomatix was engaged to …"). Match what the contract said.
- **Verbatim from intake.** The Coordinator does not paraphrase or expand the brief.

### Variation to the Brief

- **Length:** the single word `None`, or a short bulleted list.
- If variations occurred (additional analyses requested mid-project; sample-size reduction owing to failed extractions; scope additions), each is one short bullet.
- Both client and Biomatix should already have agreed any variation in writing before it appears here.

### Preamble

- **Length:** 3–4 paragraphs.
- **Tense:** present tense for species facts ("The broad-headed snake inhabits the Sydney Basin …"); past tense for any historical events referenced (e.g. "A nidovirus epizootic in 2014–2015 killed …").
- **Voice:** declarative; no hedging on well-established facts.
- **Content:** condense the Ecologist and Conservationist briefings into ~3–4 paragraphs covering: (i) where the species lives and how it lives there, (ii) major threats and the conservation context, (iii) research priorities and management actions in train, and (iv) one closing paragraph that links the species/conservation context to the specific question the client asked. The closing paragraph **always** ends with a sentence of the form "Here we [verb] [deliverable]". This is the bridge into Preliminary Analysis.
- **Citations:** every factual claim must be cited per the citation-provenance rule (see SKILL.md §1). It is acceptable for a Preamble to be light on citations if it points to a single authoritative source (e.g. the SPRAT database) at the end.
- **What it is not:** an introduction in the IMRAD sense. It does not state hypotheses, does not review the literature systematically, and does not describe what will follow. It establishes context and ends by pointing at the question.

### Preliminary Analysis

Always two subsections.

#### Data generation (italic H3)

- **Length:** 1–3 paragraphs.
- **Tense:** past throughout ("The samples were curated …", "DNA was extracted by Diversity Arrays Technologies …").
- **Voice:** passive scientific.
- **Content:** sample provenance (where stored, in what format, by whom), tissue handling (extraction kit, robot, proteinase K conditions), and the lab vendor and any technical-replicate scheme. Cite the lab pipeline (Kilian et al. 2012; Sansaloni et al. 2011 for DArTseq).
- **House detail:** include kit name, manufacturer, and city for the extraction reagents and instrumentation. The level of detail is forensic — the report must let an auditor reproduce the lab side.

#### SNP genotyping (italic H3)

- **Length:** 2–4 paragraphs.
- **Tense:** past throughout.
- **Content:** the DArTseq pipeline (restriction-enzyme combination chosen and why, adaptor design, PCR cycling, sequencing platform, read length, sequence count); the proprietary DArT Pty Ltd analytical pipeline note; the technical-replicate / repeatability filter; the data file received and how it was reconciled with the Wildlife Tissue Collection (or equivalent) database.
- **Then a filtering paragraph:** state explicitly which dartRverse filtering steps were applied (secondaries, reproducibility, callrate, monomorphs, MAF, …) and the loci/individuals retained. End with the loci × individuals count actually used in the analysis. Cite `dartR` (Gruber et al. 2018) and `dartR v2` (Mijangos et al. 2022).

### Results

- **Length:** brief. 2–6 paragraphs depending on the analysis count. Reports are not journal Results — restraint is house style.
- **Tense:** past throughout for findings ("Most of the individuals in the colony did not show any close familial relationships …").
- **Voice:** declarative; cite figures and tables at first reference using `@fig:…` / `@tbl:…`.
- **Content:** for each analysis specified by the Planner, one paragraph stating the question, the result (with point estimate and any uncertainty in the same sentence), and a pointer to the supporting figure/table. Do not interpret or recommend in this section — interpretation belongs in Strategy.
- **What it is not:** a literature comparison, a methods recap, or a discussion of alternatives. Findings only.

### Strategy

This is the deliverable. Every client question must be answered here.

- **Structure:** numbered principles (1, 2, 3, …), each with two parts:
  - a short prose paragraph (2–4 sentences) explaining the principle in plain language a non-specialist client can follow;
  - a bulleted list of action items in **bold**, naming specific individuals (animal IDs, populations, sites) where applicable.
- **Tense:** present tense for principles ("Avoiding individuals with a high inbreeding coefficient when selecting mating pairs is essential …"); imperative or "should" for action items ("**Snake BHS06_F should not be included in the selection of mating pairs.**").
- **Voice:** instructive, not exhortatory. The client paid for advice, not motivation.
- **Naming:** action items must name specific individuals where the question implies a per-individual decision. "Avoid full sibs" is not an action item; "**Snakes BHS08_F, BHS07_M and BHS19_M should not form mating pairs**" is. The default is to name; only escape to a generic statement if the analysis genuinely cannot identify candidates.
- **Closing paragraph:** a single paragraph offering a higher-order recommendation, typically about colony management, replacement of animals from the wild, or future review cadence. This paragraph may invoke conditional or future-tense language ("Aussie Ark may consider …", "subject to the necessary approvals").

### Acknowledgements

- **Length:** 2–4 sentences.
- **Tense:** past.
- **Content:** the client team who collected samples, anyone who advised on analysis or interpretation, and any institutional support not already cited. No funding statement (Biomatix is not a grant-funded body); no conflict-of-interest statement (the contract is the disclosure).

### References

- **Style:** CSIRO Harvard via the `reference-style-1` skill.
- **Order:** alphabetical by first author surname.
- **DOIs:** include where present, as full URL (`https://doi.org/…`).
- **Format quirk in Biomatix house style:** journal volume is followed by `(issue) :pages` with a space before the colon (e.g. `Molecular Ecology Resources 18(3) :691–699.`). This is a Biomatix-specific deviation from canonical CSIRO Harvard. The `reference-style-1` skill emits `(issue):pages` without the space; either accept that minor deviation or post-edit the rendered list.

---

## House-style notes

- **Tone:** professional, direct, declarative. Avoid first-person plural ("we") in Strategy — use the imperative or third-person passive. First-person plural is acceptable in Acknowledgements ("We would like to thank …").
- **Animal IDs:** rendered in non-italic monospace-equivalent typography by default in markdown (just plain text); do not wrap in backticks. Use the IDs exactly as supplied by the client (e.g. `BHS08_F`, not `bhs8f` or `BHS-8F`).
- **Species names:** italicised at every mention (`*Hoplocephalus bungaroides*`).
- **Numbers:** percentages with no space before `%`; units with a non-breaking space (`12 m`, not `12m`).
- **Hedging:** acceptable in Strategy where the analysis genuinely admits multiple interpretations (e.g. "either full sibs or in a parent–offspring relationship") — but the action item must still be unambiguous (e.g. "**only one of BHS15_F and BHS17_F should be included**").
- **No emoji, no exclamation marks, no rhetorical questions.**

---

## Worked example anchors

The Aussie Ark *Hoplocephalus bungaroides* relatedness report (Georges 2024, updated 17-Nov-2025) is the canonical exemplar of this template. When in doubt about a section's tone or length, compare the draft to the corresponding section of that report.
