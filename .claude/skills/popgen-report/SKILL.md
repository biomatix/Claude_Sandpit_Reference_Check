---
name: popgen-report
description: Use when the user asks for a Biomatix consulting report (to a client, government department, or conservation NGO) on a population-genetics question — typically presented with a brief, a client name, a numbered question list, a path to a .Rdata file, and species/conservation context. Orchestrates a six-role pipeline (ecologist, conservationist, geneticist, planner, analyst, critic) and assembles a Biomatix house-style report (Executive Summary → Brief → Variation → Preamble → Preliminary Analysis → Results → Strategy → Acknowledgements → References) on a Biomatix cover page. Reads `./playbook.md` for the analyst playbook and `./report_template.md` for section-level prose conventions. Assumes (a) an active RStudio HTTP API (default http://127.0.0.1:8787/, override via project CLAUDE.md), (b) the dartRverse R package, (c) the sibling skills clear-writing, reference-style-1, citation-check, claim-check.
---

# popgen-report

A skill for producing a Biomatix consulting report on a population-genetics question for a client (private, government, or NGO).

## How invocation works

The user invokes this skill with a project-specific prompt that supplies:

- **Client** — name and address of the recipient organisation (appears on the cover page).
- **Brief** — one or two sentences, verbatim from the contract, naming the deliverable.
- **Variation to the brief** — `None` or a short bulleted list of agreed deviations.
- **Species and conservation context** — scientific name, common name, listing status.
- **Data location** — path to a filtered `.Rdata` / `.rds` genlight object, with the object name.
- **Numbered questions** the client wants answered (Q1, Q2, …).
- **Binding facts** that constrain the recommendations (e.g., "the captive cohort is sex-biased toward males", "release of additional wild-caught animals requires NSW DPE approval not yet held").
- **Deliverable date** — the date that appears on the cover page.
- **Cover-page assets** — photo file (`assets/cover_<project>.jpg`), photographer credit, report title.
- **Acknowledgements** — client team members and any advisors.

If any of these is missing or unclear, **ask before dispatching any agent**. Do not infer the brief, the questions, or the binding facts from the data alone.

## Sibling files in this skill

- `./report_template.md` — section-by-section prose conventions and tense/voice expectations for Biomatix reports. Read at Step 3 (Assembly).
- `./playbook.md` — analyst playbook (Appendices A and B), with R code helpers (`save_fig()`, `save_tbl()`, etc.) and the flags table. Read at Step 2.
- `./troubleshooting.md` — troubleshooting common dartRverse issues. Read on demand when an analyst step fails.
- `./assets/` — Biomatix logo, cover-page LaTeX template, standard footer. Per-project photos live in the job's `outputs/` directory, not in `assets/`.

## Project-level dependencies

These come from the project's CLAUDE.md, not from this skill:

- The RStudio HTTP API endpoint (default `http://127.0.0.1:8787/`).
- External binary paths (NeEstimator, pandoc-crossref) and their R-option mappings.
- The sibling skills `clear-writing`, `reference-style-1`, `citation-check`, `claim-check`.

---

# Coordinator role

You are the **coordinator** of a multi-agent pipeline that produces a Biomatix consulting report on a population-genetics question. You orchestrate six subordinate roles — ecologist, conservationist, geneticist, planner, analyst, critic — and assemble their outputs into a single client-facing report.

You own:
- the DAG (who starts when, who waits on whom),
- the report assembly (markdown under the Biomatix template — see `./report_template.md`),
- application of the `clear-writing` and `reference-style-1` skills during drafting and revision,
- rendering the final PDF with the Biomatix cover page.

The **critic** scrutinises **scientific substance and client-defensibility** — analysis, interpretation, and whether the Strategy section's recommendations are concrete, named, and actionable. Prose quality is your responsibility, not the critic's: apply `clear-writing` and `./report_template.md` yourself as you draft and revise. The critic is also the only role that invokes `citation-check`, and only on its final cycle.

### Client questions are load-bearing

Every explicit question the client posed in the prompt is a deliverable, not a discussion topic.

- **Each client question must be answered substantively in the Strategy section**, with concrete recommendations naming specific individuals (animal IDs, populations, sites) where applicable. Hedging or "future work" framings are not acceptable in a paid report.
- **If a critic recommends moving the answer to a client-explicit question into "future work" or "out of scope", do not comply.** The client paid for the question to be answered; the critic's role is to scrutinise the substance of the answer, not relitigate scope.
- **Stated facts in the brief constrain the recommendations.** If the client states a constraint ("release of additional wild-caught animals requires approvals not yet held"), no recommendation in any section may contradict it. The Executive Summary is the most likely place to regress to template language; cross-check against binding facts before declaring done (Step 3 closing pass).

Do not begin execution until Step 0 (intake) is complete and the Step 0.1 prompt-coverage table is confirmed by the user.

---

## Report constraints

| Constraint | Value |
|---|---|
| Executive Summary length | 250–350 words |
| Total length | Typically 8–15 pages including cover, citation page, body, tables, references. No hard cap; brevity is a feature in client reports |
| Structure | Biomatix house template (see `./report_template.md`) — **not** IMRAD |
| Reference style | CSIRO Harvard (`reference-style-1` skill) |
| Prose standard | Applied via `clear-writing` skill during drafting and revision; tense and voice per section as defined in `./report_template.md` |
| Cover page | Biomatix logo + title + recipient + date + project photo + ABN/contact footer (Step 6 generates this) |

---

## Working-directory layout

Each contract has its own working directory at `jobs/<slug>/` (scaffolded by `/new-job`, populated by `/intake`). For the duration of one report, the **working directory is `jobs/<slug>/`** and every relative path below — `outputs/`, `data/`, `references/`, `brief.yaml` — resolves against it.

The R session is set to that working directory at Step 2 (`setwd(file.path("jobs", "<slug>"))`), and all paths in `./playbook.md` §A.1.1 (`output_dir <- "outputs"`) resolve correctly from there. Every artefact this skill produces is written into `outputs/` of the active job's working directory. The Analyst at Step 2 creates the directory via the helpers in `./playbook.md` §A.1.1. The Coordinator's Step 6 also writes into `outputs/`.

| File | Location | Written by |
|---|---|---|
| Figure PDFs and `.md` snippets | `outputs/` | Analyst (`save_fig()`) |
| Table CSVs and `.md` snippets | `outputs/` | Analyst (`save_tbl()`) |
| `prompt_coverage_table.md` | `outputs/` | Coordinator (Step 0.1) |
| `report_draft.md`, `citation_provenance.md`, `prompt_coverage_audit.md` | `outputs/` | Coordinator (Step 3) |
| `_cover.docx`, `_body.docx`, `report_final.docx` | `outputs/` | Coordinator (Step 6, via `render_word_report.R`) |
| `citation_check_changes.md` | `outputs/` | Critic via `citation-check` (Step 5) |

The user-supplied input (the filtered `.Rdata` / `.rds` genlight) stays at its original path; nothing this skill writes lands at the workspace root. Per-project assets the user provides (cover photo) should be placed in `outputs/` or referenced by absolute path from the intake; the Biomatix logo and cover-page LaTeX template live in `./assets/`.

---

## Execution DAG

```
Step 0: Intake (including the prompt-coverage table — user must confirm
         before Step 1 dispatches)
       │
       ▼
Step 1: Parallel briefings — Ecologist (blocking), Conservationist
        (parallel), Geneticist (parallel)
       │
       ▼
Step 2: Planner ──▶ Analyst (sequential; both follow Ecologist;
        Analyst reads ./playbook.md)
       │
       ▼
Step 3: Assembly (Coordinator drafts the Biomatix-template report;
        sees ./report_template.md for section conventions)
       │
       ▼
Step 4: Critique cycles (critic-coverage + critic-substance +
        critic-writing in parallel; hard cap at 3 cycles)
       │
       ▼
Step 5: Final cycle — critic-citations runs citation-check + claim-check
       │
       ▼
Step 6: Coordinator runs render_word_report.R to produce
        outputs/report_final.docx (Word-only deliverable)
```

---

## Step 0 — Intake

The job slug `<slug>` must already exist under `jobs/` (created by `/new-job`) and `jobs/<slug>/brief.yaml` must already be populated (created by `/intake jobs/<slug>/brief.md`). If either is missing, stop and direct the user to run those commands first — do not attempt to recreate the contract by asking the user thirteen questions inline.

Read `jobs/<slug>/brief.yaml` as the canonical contract. Most fields are either explicitly filled or intentionally deferred to a downstream agent (see below) — **do not prompt the user for the deferred fields**.

| Field | Source | If empty in yaml |
|---|---|---|
| `client.name`, `client.address` | brief | **prompt the user** |
| `project.title` | brief | **prompt the user** |
| `project.species.scientific_name` | brief (often a genus when species is a Q) | **prompt the user** if blank |
| `project.species.common_name` | filled by Coordinator after the species-assignment Q is resolved | leave blank; do not prompt |
| `project.species.conservation_status` | filled by Conservationist briefing agent at Step 1 (EPBC / BCAct / IUCN) | leave blank; do not prompt |
| `data.rdata_path` | brief or user | **hard blocker — refuse to proceed without this** |
| `questions[]` | brief | **prompt the user** if empty (intake should have filled) |
| `binding_facts[]` | brief | empty list is acceptable |
| `deliverables[].deadline` | brief or user | default to today's date (cover-page date); do not prompt |
| `acknowledgements[]` | brief | empty list is acceptable; do not prompt |
| `notes` | brief / intake | use as supplied |

**Loading the data.** The Analyst at Step 2 loads with `gl <- gl.load(file = <data.rdata_path>)`. dartRverse infers marker type (SNP / silicoDArT) from the file — you do **not** need an `object_name` or a `marker_type` field. Do not ask for them.

**Other items to gather inline** (not in the yaml):

- **Populations** — `pop(gl)` already assigned? Coordinates in `@other$latlon`? Ask the user.
- **Cover-page photo** — photo file path (typically `jobs/<slug>/outputs/cover_<slug>.jpg`) and photographer credit. Ask if not supplied.
- **Prior work** — anything in `notes` that signals analyses already completed; ask only if the brief implies prior work without naming it.
- **Software versions** — run `packageVersion("dartRverse")` via the RStudio API; note the version.

Record this briefing block (yaml + user clarifications). Pass species/conservation details to Ecologist, Conservationist, Geneticist; the full block to Planner and Analyst; the cover-page block to Step 6.

### Step 0.1 — Prompt-coverage table (mandatory; gate to Step 1)

Parse the brief.yaml and the user's invocation, then produce a table listing every question Qi (verbatim), every binding fact, and the deliverable section that addresses each. Save the confirmed table to `outputs/prompt_coverage_table.md`. The deliverable section column should name the report sub-section (e.g. "Strategy principle 2 + Executive Summary point 3 with named animal IDs"). The confirmed table becomes the contract that the Step 3 closing pass and `critic-coverage` audit against.

Hand the table back to the user and wait for explicit confirmation before dispatching Step 1.

---

## Step 1 — Parallel briefings

Three briefing agents (Ecologist blocking, Conservationist and Geneticist parallel) returning markdown briefings, each ending with a `## Citation provenance` table linking each in-text citation to the specific passage in the cited publication that supports the claim.

**One adjustment for reports.** The briefings inform the **Preamble** section (single section, ~3–4 paragraphs) rather than separate Introduction + Methods context paragraphs. Tell each agent that their briefing will be consolidated into a Preamble for a client-facing report, not a journal Introduction — the prose target is concise, decision-relevant context, not a literature review. Word cap remains 1500 per briefing (excluding provenance table); most reports use only ~30% of each briefing.

---

## Step 2 — Planner then Analyst

### Planner

Spawn as `Plan` agent (or play the role inline). Prompt:

> You are the **planner**. Given the ecologist's life-history briefing (attached), the user's dataset description (attached), and the client's numbered questions (attached), design a population-genetics analysis using the dartRverse playbook in `./playbook.md` of the popgen-report skill. The deliverable is a Biomatix consulting report — choose the smallest set of analyses that answers the client's questions decisively. Avoid analyses whose results would be too uncertain or too caveat-laden to be actionable for the client. The plan must address every question Qi from the prompt-coverage table — for any Qi whose answer requires an analysis not in the standard playbook, design the bespoke analysis explicitly. Specify which figures and tables the report will contain. Under 800 words.

### Analyst

Do not delegate. The analyst role is played inline by the Coordinator and uses the active RStudio session. **Read `./playbook.md` (Appendices A and B) at the start of this step.** Execute the plan step by step. Save every figure via `save_fig()` and every table via `save_tbl()` (defined in playbook §A.1.1) — these write into `outputs/` with sibling caption snippets that the Coordinator will inject at Step 3.

Return a markdown results document with: one paragraph per analysis step, the `{#fig:label}` / `{#tbl:label}` for each saved artefact and the path to its `.md` snippet, and any flagged issues from the playbook's flags table.

---

## Step 3 — Assembly

Draft the report in markdown following the Biomatix template. **Read `./report_template.md` before drafting** — it specifies section order, length expectations, tense, voice, and prose conventions for each section. Apply `clear-writing` for prose quality and `reference-style-1` when inserting each reference into the list.

Section sources:

| Section | Primary input |
|---|---|
| Cover page (rendered at Step 6) | Step 0 cover-page metadata |
| Citation block (rendered at Step 6) | Coordinator (auto-generated from cover-page metadata) |
| Executive Summary | Coordinator (250–350 words; draft last) |
| Brief | User (verbatim from intake) |
| Variation to the Brief | User (verbatim from intake) |
| Preamble | Ecologist + Conservationist briefings, condensed to 3–4 paragraphs |
| Preliminary Analysis: Data generation | Geneticist briefing (sample handling) + project-specific lab notes |
| Preliminary Analysis: SNP genotyping | Geneticist briefing (DArTseq pipeline) + Analyst (filtering applied) |
| Results | Analyst |
| Strategy | Analyst's findings + the client's questions (every Qi must be answered here) |
| Acknowledgements | Coordinator (from Step 0 intake) |
| References | Consolidated from briefings; formatted per `reference-style-1` |
| Supplementary: `citation_provenance.md` | Concatenation of briefing agents' provenance tables, with a fourth table added for citations introduced during assembly or critique cycles |

Save the draft as `outputs/report_draft.md`. Save the consolidated provenance log as `outputs/citation_provenance.md` alongside it. If you introduce a new citation during assembly or in response to the critic, add the matching provenance row at the same time.

### Step 3.1 — Inline figure and table placement (mandatory)

Each `save_fig()` / `save_tbl()` produces a sibling `.md` caption snippet in `outputs/`. When drafting Results:

1. **Reference first, insert second.** Cite the artefact in prose using `@fig:…` / `@tbl:…` at the point in the argument where the reader needs it.
2. **Inject the snippet immediately after the paragraph that first references it**, by reading the sibling `.md` file and pasting its contents verbatim. Do not retype the caption or restate the path. One blank line above and below the snippet.
3. **Each artefact is injected exactly once.** Subsequent mentions in Strategy or Executive Summary use the cross-reference only.
4. Floats may move to the next page break, but never appear before their first reference (enforced by `\usepackage{flafter}` at render time).
5. Every Analyst artefact must be either injected or explicitly demoted to a `## Supplementary tables` section. An orphaned figure file is an error.

**One report-specific note.** Reports often need a **colour-coded relatedness or pairwise matrix** rendered as a heatmap (cells filled by value), not a plain pandoc table. Save these via `save_fig()` (heatmap image), not `save_tbl()` (plain table). Reserve `save_tbl()` for tables whose value is in the literal numbers, not in the colour pattern.

### Step 3 closing pass — prompt-coverage cross-reference (mandatory)

A hard gate. Audit the draft against `outputs/prompt_coverage_table.md`:

1. **Question coverage.** For every Qi, confirm the named deliverable section (typically a Strategy principle) addresses it substantively, names specific individuals where applicable, and is not hedged with "future work".
2. **Fact consistency.** Read the Executive Summary and the Strategy side-by-side with the binding-facts column. Every recommendation must be checked against every fact that constrains it. The Executive Summary is the highest-risk regression site.
3. **Cross-principle coupling.** For each Strategy principle, list the actions/decisions it recommends. Then, for each action, ask: does any *other* principle prescribe an action whose precondition is denied by this one? Two patterns to look for:
   - **Disposition vs use.** Principle A says "release/discard X" (or "no genetic case to retain X"); Principle B prescribes a use of X that requires X to be retained or curated. Either A is contingent on B not happening, or B is contingent on A not happening — write the conditionality into both principles, do not assert them flatly.
   - **Resource vs allocation.** Principle A says "the only deposit is Y"; Principle B prescribes a method that consumes more of Y than Y exists. Reconcile the budget.
   The Executive Summary inherits both errors and is the most common regression site for them. The most reliable fix is to invert one principle from "do X" to "if precondition P holds, do X; otherwise do Y", with P named explicitly.
4. **Record the audit.** Append a `## Prompt-coverage audit` section to `outputs/citation_provenance.md` (or write a sibling `outputs/prompt_coverage_audit.md`). Include a coupling sub-section listing every (Principle A, Principle B) pair that touches the same individual, dataset, or resource.

The critic should not see a draft until question coverage, fact consistency, and cross-principle coupling are all clean.

---

## Step 4 — Substance + coverage critique cycles (substance first)

Critics run in two stages. Stage one is **substance + coverage**, with up
to three feedback cycles. Stage two (Step 5) is writing + citations,
which run only after stage one is settled. Reason: substance fixes
restructure prose and recompose citations, so polishing prose or
verifying claims against a draft that is about to be rewritten wastes
work and risks reverting fixes the substance critic asked for.

Spawn both stage-one critics in parallel via a single message with two
Agent calls:

- **`critic-substance`** — methods, parameter choices, calibration of interpretation, traceability from results to recommendations (the report-specific lens emphasises **client-defensibility**: are recommendations concrete? Do they name specific individuals? Is Strategy consistent with Executive Summary and Brief?). Reads `./playbook.md` Appendix B for the flags table. Output: `outputs/substance_audit.md`.
- **`critic-coverage`** — confirms every Qi is addressed substantively, named individuals named, binding facts honoured, and that no Strategy principle contradicts another (especially: a recommendation in one principle whose precondition is denied in another — see Step 3 closing pass). Reads `outputs/prompt_coverage_table.md` and `jobs/<slug>/brief.yaml`. Output: `outputs/coverage_audit.md`.

Hold `critic-writing` and `critic-citations` for Step 5.

The critics never edit the draft. Each returns its audit as markdown; you (the coordinator) write each file to `outputs/` and apply revisions to `report_draft.md`.

**Coordinator guard against critic over-reach.** When applying critic revisions, never demote a client-explicit question to "future work" or remove it. If a critic argues an answer is unsupported by the analysis, the correct action is to strengthen the supporting analysis or add a calibrated caveat — not to delete the answer.

**Stopping rule: hard cap at three cycles.** Stop earlier when both stage-one critics return "no blocking issues" on the same cycle. Save `outputs/report_draft.md` after each revision (overwriting). Regardless of cap or early sign-off, proceed to Step 5 for prose-and-citation finishing before rendering.

---

## Step 5 — Writing + citations finishing pass

Stage two: spawn both finishing critics in parallel via a single message
with two Agent calls. One pass each, not iterated — by this point the
substance is locked. If either pass surfaces a substance-grade issue
(e.g. a citation that contradicts the carrying claim and forces a
prose change beyond a one-sentence rewrite), kick back to Step 4 with
that issue named, do not paper over it.

- **`critic-writing`** — `clear-writing` plus `reference-style-1`, capped at 15 prose rewrites. Output: `outputs/writing_audit.md`.
- **`critic-citations`** — runs both passes (`citation-check` for existence + metadata, `claim-check` for assertion vs source) against the now-stable prose. Reads `jobs/<slug>/references/` for local PDF overrides; falls back through Unpaywall → preprint → abstract → "paywalled — manual check needed". Output: `outputs/citations_audit.md`.

Then run a final coordinator pass yourself (do not delegate):

- **Provenance cross-check.** Confirm every in-text citation in `outputs/report_draft.md` has a matching row in `outputs/citation_provenance.md`. Resolve ungrounded citations either by tracing to a source (and adding the row) or by deleting the citation. Drop orphan provenance rows.
- **Final prompt-coverage check.** Re-verify, for every Qi, that the report still addresses it substantively. For every binding fact, re-verify no recommendation in the Executive Summary or Strategy contradicts it. The earlier critic-coverage audit is the baseline — list any regression introduced since.
- **Substance regressions.** Confirm no substantive concern raised by `critic-substance` in earlier cycles remains unaddressed.

Apply citation-check corrections to the reference list, to in-text citations affected by the corrections, and to the matching rows in `outputs/citation_provenance.md`. For `claim-check` verdicts:

- `supported` → no action.
- `partially supported` or `contradicted` → rewrite the carrying sentence to match the source's actual claim, using the suggested rewrite from the audit table as a starting point.
- `paywalled — manual check needed` → flag in `outputs/citations_audit.md` and either (a) ask the user to drop a PDF into `jobs/<slug>/references/<key>.pdf` and rerun `claim-check` for that key, or (b) accept the assertion as unverifiable and note it in the report's caveats.

The citation-check skill writes its own `outputs/citation_check_changes.md` log when run in batch-apply mode (see `citation-check` SKILL.md auto-apply guard).

---

## Step 6 — Render the final Word document

The Biomatix deliverable is a single editable `.docx` (`outputs/report_final.docx`). The user always sweeps the output in Word before sending to the client, so a PDF is not produced — the PDF render path was removed from this skill on 2026-05-03. If a client specifically asks for a PDF, the user produces it themselves from the final reviewed Word file.

The render pipeline reuses three pre-built artefacts in `./assets/`:

- `biomatix_cover_template.docx` — the literal cover page (logo + title + recipient + date + photo + ABN footer + citation block on page 2). Carries five placeholder tokens (`{{TITLE}}`, `{{RECIPIENT}}`, `{{DATE}}`, `{{PHOTO_CREDIT}}`, `{{CITATION}}`) and a swappable `image2.jpeg`. See `./assets/biomatix_cover_template.README.md` for the placeholder map.
- `biomatix_template.docx` — the body reference-doc (A4, 2.5 cm margins, pandoc-default style names that pandoc populates with the converted markdown). See `./assets/biomatix_template.README.md`.
- `./scripts/render_word_report.R` — the orchestration script, exporting `render_word_report(slug)`.

### 6.1 Run the render

From the RStudio session at the project root:

```r
source(".claude/skills/popgen-report/scripts/render_word_report.R")
render_word_report("<slug>")
```

The function:

1. Reads `jobs/<slug>/brief.yaml` for client, project title, deadline, lead author, cover photo path and photographer.
2. Builds the per-job cover by unzipping `biomatix_cover_template.docx`, substituting the five placeholders in `word/document.xml`, swapping `word/media/image2.jpeg` with the photo at `cover_photo.path`, and re-zipping into `outputs/_cover.docx`.
3. Runs pandoc on `outputs/report_draft.md` with `--filter pandoc-crossref` and `--reference-doc=biomatix_template.docx`, producing `outputs/_body.docx`.
4. Concatenates cover + body via `officer::body_add_docx` into `outputs/report_final.docx`.

Cross-references via pandoc-crossref produce `Figure 1`, `Table 1`-style labels in the Word output. Pandoc emits inline images at the markdown position, so the figure-after-first-reference convention from Step 3.1 is preserved without further work — there is no Word-side equivalent of LaTeX's `flafter`, but the reference-followed-by-snippet ordering in the markdown delivers the same outcome.

The auto-generated citation follows the pattern `Surname, I. (Year). Title. Report to Client. DD-Mon-YYYY.` from `lead_author`, `project.title`, `client.name`, and `deliverables[0].deadline` in `brief.yaml`. If `lead_author` is omitted the citation falls back to a year-only attribution.

### 6.2 Verify

After rendering, open `outputs/report_final.docx` in Word and verify:

1. Cover page renders correctly (logo present, title legible, recipient line correct, photo and credit in place, Biomatix address + ABN + email at bottom).
2. Page 2 is the citation block (`Citation: <auto-generated entry>`).
3. Body sections appear in the order specified in `./report_template.md` (Title H1, then `## EXECUTIVE SUMMARY` etc.).
4. Every figure and table appears in the body at or after its first reference (carried from the markdown ordering set in Step 3.1).
5. Captions are auto-numbered (`Figure 1.`, `Table 1.`, …) and match the `[@fig:…]` / `[@tbl:…]` cross-references in the prose.
6. Reference list is in CSIRO Harvard format and alphabetised.
7. Tables are **editable Word tables** (click a cell, see the table-tools ribbon), not pasted images.

If the cover photo is missing, check that `cover_photo.path` in `brief.yaml` resolves from the project root and that the file exists. The render warns but does not fail when the photo is missing — the cover renders with the previous occupant of `image2.jpeg`.

Report the final path (`outputs/report_final.docx`) to the user.
