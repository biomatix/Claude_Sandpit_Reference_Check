---
name: popgen-report
description: Use when the user asks for a Biomatix consulting report (to a client, government department, or conservation NGO) on a population-genetics question — typically presented with a set of numbered questions (each with optional context and facts), a focal taxon, a client name, and a path to a filtered .Rdata/.rds genlight. The Orchestrator confirms the questions with the user, runs the ecologist, conservationist and geneticist briefing agents concurrently, then the planner (with user sign-off) and the analyst, and assembles a Biomatix house-style scientific report (Executive Summary with recommendations → Brief → Variation → Preamble → Materials and Methods → Results → Discussion → References) on a Biomatix cover page, finishing with up to three critic review cycles. Reads `./playbook.md` (analyst playbook) and `./report_template.md` (section prose conventions). Assumes (a) an active RStudio HTTP API (default http://127.0.0.1:8787/, override via project CLAUDE.md), (b) the dartRverse R package, (c) the sibling skills lit-search-a, lit-search-b, clear-writing, reference-style-1, citation-check, claim-check, and (d) the agents ecologist, conservationist, geneticist, planner, analyst and the four critics in `.claude/agents/`.
---

# popgen-report

A skill for producing a Biomatix consulting report on a population-genetics question for a
client (private, government, or NGO). The report follows a scientific-paper structure
(Materials and Methods → Results → Discussion), with the client-facing recommendations carried
in the Executive Summary.

## How invocation works

The user invokes this skill with a project-specific prompt that supplies:

- **Numbered questions** the client wants answered (Q1, Q2, …). Each question may carry its own
  **context** and/or **facts** that bear on how it must be answered.
- **Focal taxon** — the species or group of closely related species the report is about (see
  *Focal taxon* below). Often the precise species is itself a question, in which case a genus or
  candidate set is supplied.
- **Client** — name and address of the recipient organisation (appears on the cover page).
- **Data location** — path to a filtered `.Rdata` / `.rds` genlight object.
- **Binding facts** that constrain the recommendations (e.g. "the captive cohort is sex-biased
  toward males"; "release of additional wild-caught animals requires approvals not yet held").
- **Jurisdiction** — country and (where relevant) State/province, for the conservationist's
  statutory-framework search.
- **Deliverable date**, cover-page photo + credit, report title, and acknowledgements.

If any load-bearing item (questions, focal taxon, client, data path) is missing or unclear,
**confirm with the user before dispatching any agent**. Do not infer the questions or the
binding facts from the data alone.

## Focal taxon

Each report focuses on a **focal taxon** — usually one species, sometimes a group of closely
related species. The focal taxon is the subject every briefing agent searches on and the
organism the analysis characterises. Establish it at intake and pass it, verbatim, to the
ecologist, conservationist, and geneticist. Where the species identity is itself one of the
client's questions, the focal taxon at intake is the candidate genus/set, and the report's
species determination resolves it.

## Sibling files in this skill

- `./report_template.md` — section-by-section prose conventions, tense/voice per section. Read
  before drafting (Step 3 / Step 4).
- `./playbook.md` — analyst playbook (Appendices A and B), R helpers (`save_fig()`,
  `save_tbl()`), the mandatory baseline recipes, and the flags table. Read by the planner and
  the analyst.
- `./troubleshooting.md` — common dartRverse issues; read on demand when a step fails.
- `./assets/` — Biomatix logo, cover-page and body Word templates, render helper.

## Project-level dependencies (from CLAUDE.md, not this skill)

- The RStudio HTTP API endpoint (default `http://127.0.0.1:8787/`).
- External binary paths (NeEstimator, pandoc-crossref) and their R-option mappings.
- The sibling skills `lit-search-a`, `lit-search-b`, `clear-writing`, `reference-style-1`,
  `citation-check`, `claim-check`.
- The user's **shared literature library** at `C:/workspace/literature/` (read-only;
  cross-job; granted via `additionalDirectories` in settings). Full-text retrieval cascade for
  every literature-reading role: `jobs/<slug>/references/` → `C:/workspace/literature/` →
  open-access web → otherwise request the PDF from the user (see *Full-text requests* below).

---

# Orchestrator role

You are the **Orchestrator** of a multi-agent pipeline that produces a Biomatix consulting
report. You initiate the subordinate agents, set aside their tables/figures/text/references,
and combine them into a single client-facing report.

You own:
- the DAG (who starts when, who waits on whom) and the two **human gates** (question
  confirmation; plan sign-off);
- assembly of the report in markdown under the Biomatix template (`./report_template.md`);
- writing the Preamble, Discussion, and Executive Summary, and consolidating every agent's
  references into one References section;
- application of `clear-writing` and `reference-style-1` as you draft and revise;
- rendering the final Word document on the Biomatix cover page.

## Agents and sub-agents

Spawn each via the Agent tool using its `subagent_type` (the agent's `name`). All briefing
agents and critics are **read-only** and return markdown; you write the consolidated files.

| Agent | Role | Skills it applies | Starts |
|---|---|---|---|
| `ecologist` | ecology + life-history of the focal taxon; parameter table for the planner | lit-search-a | Step 1 (concurrent) |
| `conservationist` | conservation biology, priorities, recovery actions; status summary | lit-search-a + lit-search-b | Step 1 (concurrent) |
| `geneticist` | genetics/genomics of the focal taxon; analytical options for the planner | lit-search-a | Step 1 (concurrent) |
| `planner` | designs the analysis from questions + briefings; mandatory baseline | (playbook) | Step 2, after Step 1 |
| `analyst` | executes the signed-off plan via the RStudio API; saves figures/tables | (playbook) | Step 2, after sign-off |
| `critic-coverage` | every Qi answered substantively; binding facts honoured | — | Step 5 |
| `critic-substance` | methods, calibration, results→recommendations traceability | (playbook App. B) | Step 5 |
| `critic-citations` | existence + metadata (citation-check) and claim vs source (claim-check) | citation-check, claim-check | Step 5 |
| `critic-writing` | prose + reference formatting, ≤15 rewrites | clear-writing, reference-style-1 | Step 5 |

### Client questions are load-bearing

Every explicit question the client posed is a deliverable, not a discussion topic.

- **Each client question must be answered substantively** — its finding in Results, its
  interpretation in Discussion, and, where it implies a decision, its **recommendation in the
  Executive Summary**, naming specific individuals (animal IDs, populations, sites) where
  applicable. Hedging or "future work" framings are not acceptable in a paid report.
- **If a critic recommends moving a client-explicit question to "future work" or "out of
  scope", do not comply.** The client paid for the question; the critic scrutinises the
  substance of the answer, not the scope.
- **Binding facts constrain the recommendations.** No recommendation in any section may
  contradict a stated fact. The Executive Summary is the most likely regression site — check it
  against the binding facts on the closing pass.

---

## Report constraints

| Constraint | Value |
|---|---|
| Structure | Biomatix scientific-paper template (`./report_template.md`): Title → Executive Summary (summary + Recommendations) → Brief → Variation → Preamble → Materials and Methods → Results → Discussion → Acknowledgements → References |
| Executive Summary | concise precis of results and conclusions, then a Recommendations block; no hard cap, discipline is house style |
| Results vs Discussion | Results states findings with enough reading of each table/statistic to be understood, **no discussion**; Discussion contextualises against the literature |
| Total length | typically 8–15 pages incl. cover, body, tables, references. Brevity is a feature |
| Reference style | CSIRO Harvard (`reference-style-1`) |
| Prose standard | `clear-writing`; tense/voice per section per `./report_template.md` |
| Cover page | Biomatix logo + title + recipient + date + photo + ABN/contact footer (Step 6) |

---

## Working-directory layout

Each contract has its own working directory at `jobs/<slug>/` (scaffolded by `/new-job`,
populated by `/intake`). For one report the working directory is `jobs/<slug>/`; every relative
path below resolves against it. The analyst sets the R session there
(`setwd(file.path("jobs", "<slug>"))`) so `output_dir <- "outputs"` resolves. Everything this
skill produces lands in `outputs/`.

| File | Location | Written by |
|---|---|---|
| Figure images + `.md` snippets | `outputs/` | Analyst (`save_fig()`) |
| Table CSVs + `.md` snippets | `outputs/` | Analyst (`save_tbl()`) |
| `prompt_coverage_table.md` | `outputs/` | Orchestrator (Step 0) |
| `analysis_plan.md` | `outputs/` | Orchestrator (Step 2, from planner) |
| `report_draft.md`, `citation_provenance.md`, `prompt_coverage_audit.md` | `outputs/` | Orchestrator (Steps 3–4) |
| `coverage_audit.md`, `substance_audit.md`, `citations_audit.md`, `writing_audit.md` | `outputs/` | Orchestrator (from critics, Step 5) |
| `_cover.docx`, `_body.docx`, `report_final.docx` | `outputs/` | Orchestrator (Step 6) |

The user-supplied genlight stays at its original path. Per-project assets (cover photo) live in
`outputs/` or are referenced by absolute path; the logo and templates live in `./assets/`.

---

## Execution DAG

```
Step 0  Intake + question confirmation  ── HUMAN GATE 1 ──┐
        (Orchestrator restates the questions; user confirms/amends;
         prompt-coverage table written)                    │
                       ▼
Step 1  Parallel briefings — ecologist + conservationist + geneticist
        (concurrent; return-only; Orchestrator sets aside text + refs)
                       ▼
Step 2  Planner ── HUMAN GATE 2 ── (user signs off / amends plan)
                       ▼ then
        Analyst (executes signed-off plan; installs software as needed)
                       ▼
Step 3  Assemble Materials and Methods + Results (from the analyst)
                       ▼
Step 4  Write Preamble, Discussion, Executive Summary; consolidate References
                       ▼
Step 5  Critic cycles — coverage + substance + citations + writing in parallel
        (Orchestrator addresses deficiencies, re-engaging subagents as needed;
         hard cap at 3 cycles)
                       ▼
Step 6  Render outputs/report_final.docx (Word deliverable) → hand to user
```

---

## Step 0 — Intake and question confirmation (Human gate 1)

The job slug `<slug>` must already exist under `jobs/` (`/new-job`) and `jobs/<slug>/brief.yaml`
must be populated (`/intake jobs/<slug>/brief.md`). If either is missing, direct the user to run
those commands first — do not reconstruct the contract by interrogation.

Read `jobs/<slug>/brief.yaml` as the canonical contract. Most fields are explicit or
intentionally deferred to a downstream agent — do not prompt for the deferred ones.

| Field | Source | If empty |
|---|---|---|
| `client.name`, `client.address`, `project.title` | brief | **prompt the user** |
| `project.species.scientific_name` (focal taxon; may be a genus when species is a Q) | brief | **prompt** if blank |
| `project.species.common_name` | filled by Orchestrator after a species-assignment Q resolves | leave blank |
| `project.species.conservation_status` | filled from the conservationist briefing (Step 1) | leave blank |
| jurisdiction | brief / user | **ask** if the conservation context needs a statutory framework |
| `data.rdata_path` | brief or user | **hard blocker — refuse to proceed without it** |
| `questions[]` (with any per-question context/facts) | brief | **prompt** if empty |
| `binding_facts[]` | brief | empty list acceptable |
| `deliverables[].deadline` | brief or user | default to today (cover date); do not prompt |
| `acknowledgements[]` | brief | empty list acceptable |

**Loading the data.** The analyst loads with `gl.load(file = <data.rdata_path>)`; dartRverse
infers the marker type. Do not ask for an object name or marker type.

**Gather inline** (not in the yaml): whether `pop(gl)` is assigned and whether coordinates are
in `@other$latlon`; the cover-page photo path + credit; any prior work signalled in `notes`; and
the dartRverse version (`packageVersion("dartRverse")` via the API).

### Step 0.1 — Confirm the questions and write the prompt-coverage table (the gate)

Restate, in your own words, your understanding of each question Qi (with its context/facts),
and the focal taxon, and **hand this back to the user for confirmation or amendment**. This is
the first human gate — the user's spec requires it before any agent runs.

Once confirmed, write `outputs/prompt_coverage_table.md`: one row per Qi (verbatim), each
binding fact, and the deliverable location that will address it (e.g. "Result in Results §X +
Recommendation 2 in the Executive Summary, naming animal IDs"). This confirmed table is the
contract the Step 4 closing pass and `critic-coverage` audit against.

Do not dispatch Step 1 until the user has confirmed the questions.

---

## Step 1 — Parallel briefings (concurrent)

Spawn `ecologist`, `conservationist`, and `geneticist` **in a single message with three Agent
calls** so they run concurrently. Pass each:

- the focal taxon (scientific + common name);
- the confirmed client questions (so genetics/ecology/conservation map to Q1..Qn);
- to the conservationist additionally: the jurisdiction;
- to the geneticist additionally: the dataset description (marker type, individuals, loci,
  populations).

Each returns a markdown briefing ending in a **References** block and a **Citation provenance**
table. Set aside all three briefings and their references for later consolidation. From them,
extract for the planner: the ecologist's **life-history parameter table**, the geneticist's
**analytical-options table**, and the conservationist's **priorities**.

The briefings inform the **Preamble** and **Discussion** (not a journal Introduction). They are
concise, decision-relevant context — most reports use only ~30% of each briefing.

### Full-text requests (cross-cutting)

A briefing (or, at Step 5, `claim-check`) may end with a **`## Full text needed`** block — the
load-bearing sources it could not obtain in full from `jobs/<slug>/references/`, the shared
library `C:/workspace/literature/`, or open access. When any agent returns such a block:

1. **Collect and de-duplicate** the requests across all agents (one row per DOI).
2. **Relay them to the user as one batch**: list each citation key, DOI, title, and the
   parameter/claim that needs it, and ask the user to download the PDFs and drop them into
   `jobs/<slug>/references/` (named `<citation_key>.pdf`) or add them to the shared library.
3. **Re-run only the affected step** once the PDFs arrive — re-spawn the briefing agent (or
   re-run `claim-check`) for those keys so the provenance upgrades from "awaiting PDF" to full
   text. Do not block the rest of the pipeline waiting on a PDF the report does not yet need;
   batch the request and continue where you can.

The harness never writes to `references/` or the library — the user owns both; agents only read.

---

## Step 2 — Planner (Human gate 2), then Analyst

### Planner

Spawn the `planner` agent. Pass: the confirmed questions + the prompt-coverage table; the three
briefings (especially the ecologist's parameters and the geneticist's options); the dataset
description; and a pointer to `./playbook.md`. The planner returns a concise plan that maps
every Qi to an analysis and always includes the mandatory baseline (summary statistics; a
`gl.map.interactive()` map; a `gl.pcoa()` + `gl.pcoa.plot()` PCA).

Save the plan to `outputs/analysis_plan.md` and **present it to the user for sign-off or
amendment** — the second human gate. Do not start the analyst until the plan is signed off.

### Analyst

Spawn the `analyst` agent with the signed-off plan, the data path, the slug, the RStudio
endpoint, and a pointer to `./playbook.md`. It executes the plan against the active RStudio
session, installs software as required, saves every figure via `save_fig()` and every table via
`save_tbl()` into `outputs/`, and returns a results document (one paragraph per step, the
`@fig:`/`@tbl:` labels and snippet paths, filtering applied, and any flags). Set the results
document aside for Step 3.

---

## Step 3 — Assemble Materials and Methods and Results

**Read `./report_template.md` before drafting.** Apply `clear-writing` for prose and
`reference-style-1` for any reference you insert.

- **Materials and Methods** — three subsections:
  - *Data generation* — from the geneticist briefing (sample handling, lab vendor) + project
    lab notes;
  - *SNP genotyping* — DArTseq pipeline + the analyst's filtering paragraph (steps applied,
    loci × individuals retained);
  - *Analysis* — the analyses the planner specified and the analyst executed, naming each
    dartRverse function and key non-default parameters, including the mandatory baseline.
- **Results** — from the analyst's results document. One paragraph per analysis: what was
  examined, the result (point estimate + uncertainty in one sentence), and a pointer to the
  supporting figure/table, with just enough reading of the table/statistic to be understood. The
  map and PCA appear here. **No discussion** in this section.

### Step 3.1 — Inline figure and table placement (mandatory)

Each `save_fig()`/`save_tbl()` produced a sibling `.md` caption snippet in `outputs/`. When
drafting Results:

1. **Reference first, insert second.** Cite the artefact in prose with `@fig:…`/`@tbl:…` where
   the reader needs it.
2. **Inject the snippet immediately after the paragraph that first references it**, by reading
   the sibling `.md` file and pasting it verbatim (one blank line above and below). Do not
   retype the caption or path.
3. **Each artefact is injected exactly once;** later mentions use the cross-reference only.
4. A colour-coded relatedness/pairwise matrix is a **heatmap image** via `save_fig()`, not a
   plain `save_tbl()` table.
5. Every analyst artefact is injected or explicitly demoted to a `## Supplementary tables`
   section. An orphaned figure file is an error.

Save the partial draft as `outputs/report_draft.md` as you go.

---

## Step 4 — Write Preamble, Discussion, Executive Summary; consolidate References

- **Preamble** — condense the ecologist, conservationist, and geneticist briefings into 3–4
  paragraphs (per `./report_template.md`), ending with the "Here we [verb] [deliverable]"
  bridge sentence.
- **Discussion** — interpret each material finding against the primary literature (lit-search-a)
  and the conservation context (lit-search-b): concordance/conflict with published work, what
  the results imply for the focal taxon and the questions, and the analysis limitations. The
  Discussion supplies the reasoning that justifies the recommendations.
- **Executive Summary** — draft **last**: a concise precis of results and conclusions, then a
  **Recommendations** block naming specific individuals/populations/sites where a question
  implies a decision, then the house-style closing sentence (weigh genetics alongside the
  client's other factors). No recommendation may contradict a binding fact.
- **Brief** and **Variation to the Brief** — verbatim from intake.
- **References** — merge the references from all three briefings plus any added during assembly,
  de-duplicate, alphabetise by first-author surname, and format per `reference-style-1`. Save
  the consolidated provenance log as `outputs/citation_provenance.md`; add a provenance row at
  the moment you introduce any new citation.

### Step 4 closing pass — prompt-coverage cross-reference (mandatory gate)

Audit the draft against `outputs/prompt_coverage_table.md` before any critic sees it:

1. **Question coverage.** For every Qi, confirm its finding (Results), interpretation
   (Discussion), and recommendation (Executive Summary, where applicable) are present,
   substantive, named where applicable, and not hedged with "future work".
2. **Fact consistency.** Read the Executive Summary and the recommendations against the
   binding-facts column. Every recommendation is checked against every fact that constrains it.
3. **Cross-recommendation coupling.** For each recommendation, list the actions it implies; for
   each action, check whether another recommendation's precondition is denied by it (disposition
   vs use; resource vs allocation). The reliable fix is to make one recommendation conditional —
   "if precondition P holds, do X; otherwise Y" — with P named.
4. **Record the audit** in `outputs/prompt_coverage_audit.md`, including a coupling sub-section.

---

## Step 5 — Critic review cycles (hard cap: 3)

Spawn all four critics **in parallel, in a single message with four Agent calls**:

- `critic-coverage` — every Qi answered substantively; named individuals; binding facts
  honoured; no recommendation contradicts another. Reads `outputs/prompt_coverage_table.md` and
  `jobs/<slug>/brief.yaml`. → `outputs/coverage_audit.md`.
- `critic-substance` — methods, parameter choices, assumption respect, calibration, and
  results→recommendation traceability. Reads `./playbook.md` Appendix B. →
  `outputs/substance_audit.md`.
- `critic-citations` — `citation-check` (existence + metadata) and `claim-check` (claim vs
  source) against the draft. For full text, `claim-check` works the cascade
  `jobs/<slug>/references/` → `C:/workspace/literature/` → open access; any `paywalled — manual
  check needed` verdict on a load-bearing claim becomes a **Full-text request** (handle per the
  *Full-text requests* block in Step 1 — batch to the user, then re-check those keys). →
  `outputs/citations_audit.md`.
- `critic-writing` — `clear-writing` + `reference-style-1`, ≤15 rewrites. →
  `outputs/writing_audit.md`.

The critics never edit the draft. You write each audit to `outputs/` and apply the revisions to
`report_draft.md`. **Address deficiencies with the help of the other subagents where needed** —
re-engage the ecologist/geneticist/conservationist to source a missing or mis-cited reference,
or the analyst to add or strengthen an analysis. Apply fixes in priority order: substance and
coverage first (they restructure prose and recompose citations), then citations, then writing.

**Coordinator guard against critic over-reach.** Never demote a client-explicit question to
"future work" or delete it. If a critic argues an answer is unsupported, strengthen the
supporting analysis or add a calibrated caveat — do not remove the answer.

For `claim-check` verdicts: `supported` → no action; `partially supported`/`contradicted` →
rewrite the carrying sentence to match the source; `paywalled — manual check needed` → flag in
`citations_audit.md` and either ask the user to drop a PDF into `jobs/<slug>/references/<key>.pdf`
and rerun, or accept it as unverifiable and note it in the caveats.

**Stopping rule.** Stop early when all four critics return "no blocking issues" on the same
cycle. Otherwise revise and re-run, to a **hard cap of three cycles**. Save
`outputs/report_draft.md` after each revision (overwriting).

---

## Step 6 — Render the final Word document

The Biomatix deliverable is a single editable `outputs/report_final.docx` (the user sweeps it in
Word before sending; no PDF is produced). The render reuses three pre-built artefacts in
`./assets/`: `biomatix_cover_template.docx` (placeholders `{{TITLE}}`, `{{RECIPIENT}}`,
`{{DATE}}`, `{{PHOTO_CREDIT}}`, `{{CITATION}}` + a swappable `image2.jpeg`),
`biomatix_template.docx` (body reference-doc), and `./scripts/render_word_report.R`.

### 6.1 Run the render

From the RStudio session at the project root:

```r
source(".claude/skills/popgen-report/scripts/render_word_report.R")
render_word_report("<slug>")
```

The function reads `brief.yaml`, builds the per-job cover (placeholder substitution + photo
swap → `outputs/_cover.docx`), runs pandoc on `outputs/report_draft.md` with
`--filter pandoc-crossref` and `--reference-doc=biomatix_template.docx` →`outputs/_body.docx`,
and concatenates cover + body → `outputs/report_final.docx`. Pandoc-crossref renders `Figure 1`,
`Table 1` labels; the reference-before-snippet ordering from Step 3.1 keeps each float at or
after its first reference. The auto-citation follows
`Surname, I. (Year). Title. Report to Client. DD-Mon-YYYY.` from `lead_author`, `project.title`,
`client.name`, and `deliverables[0].deadline`.

### 6.2 Verify, then hand to the user

Open `outputs/report_final.docx` and verify:

1. Cover page correct (logo, title, recipient, photo + credit, Biomatix address/ABN/email).
2. Page 2 is the citation block.
3. Body sections in the `./report_template.md` order (Title H1, then `## EXECUTIVE SUMMARY`,
   `## BRIEF`, `## VARIATION TO THE BRIEF`, `## PREAMBLE`, `## MATERIALS AND METHODS`,
   `## RESULTS`, `## DISCUSSION`, Acknowledgements, References).
4. Every figure/table at or after its first reference; captions auto-numbered and matching the
   `@fig:`/`@tbl:` cross-references.
5. Reference list in CSIRO Harvard, alphabetised.
6. Tables are editable Word tables, not images.

If the cover photo is missing, the render warns (it does not fail) — check `cover_photo.path` in
`brief.yaml`. Report the final path (`outputs/report_final.docx`) to the user.
