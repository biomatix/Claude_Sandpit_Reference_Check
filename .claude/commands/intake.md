---
description: Parse a verbatim contract brief into the structured brief.yaml that the popgen-report skill consumes. Extracts client, species, data path, numbered questions, binding facts, deliverables, deadlines.
argument-hint: <path-to-brief.md>
---

You are parsing a Biomatix consulting brief at `$1` and writing the structured contract to `jobs/<slug>/brief.yaml` so that `/popgen-report` and `critic-coverage` have a canonical machine-readable contract to work against.

## Step 0 — Locate the job

Derive the slug from the brief path: if the path is `jobs/<slug>/brief.md`, then `<slug>` is the directory between `jobs/` and `brief.md`. If the brief is at any other path, ask the user which job slug it belongs to and refuse to proceed without one.

If `jobs/<slug>/brief.yaml` already exists and has any non-empty fields, stop and ask whether to (a) merge new findings into the existing yaml, (b) overwrite it (with a backup at `brief.yaml.bak`), or (c) abort.

## Step 1 — Read the brief

Read `$1` in full. Treat its contents as the verbatim contract — do **not** paraphrase, summarise, or "improve" the wording when extracting verbatim fields like the brief sentence or the client name and address.

If the brief is a PDF or DOCX rather than markdown, ask the user to convert it first; do not guess at content. (PDF conversion via pandoc is fine if the user authorises it.)

## Step 2 — Extract fields

Pull these into structured form. Where a field is not stated in the brief, leave it as an empty string and note it in your confirmation message — do **not** infer.

- **Client name and postal address.** Verbatim from the cover sheet or salutation.
- **Project title.** Either explicit ("Project: ...") or the title line of the brief. Strip leading structural prefixes like "Brief — " or "Project: " — the title is the content after the prefix, not the prefix itself.
- **Species.** Scientific name only — usually a genus when species ID is itself a question. Do **not** record common name or conservation status at intake; those are filled later (common name by the Coordinator from the species-assignment Q result, conservation status by the Conservationist briefing agent at /popgen-report Step 1).
- **Data location.** Path to the `.Rdata` / `.rds` file, relative to the job directory (e.g. `data/raw.RData`). The Analyst loads it with `gl <- gl.load(file=<path>)` and dartRverse infers marker type (SNP / silicoDArT) from the file. Do **not** ask for an object name or marker type — neither is needed.
- **Numbered questions Q1..Qn.** Extract verbatim. If the brief poses questions in prose without numbering, number them in order of appearance and include the original phrasing. Each question becomes a record:

  ```yaml
  - id: Q1
    text: "<verbatim question text>"
    deliverable_section: ""    # filled by the coordinator at popgen-report Step 0.1
    success_criterion: ""      # filled by the coordinator at popgen-report Step 0.1
  ```

- **Binding facts.** Statements of fact in the brief that constrain what can be recommended. Examples: "The hatchlings are no longer available for release", "Captive cohort is sex-biased toward males", "NSW DPE approval is not yet held". For each, record:

  ```yaml
  - fact: "<verbatim>"
    sections_constrained: []   # filled by the coordinator at popgen-report Step 0.1
  ```

  Bias toward over-extraction here — a fact that turns out to be irrelevant is harmless, but a missed fact is the most common failure mode the prompt-coverage gate is designed to catch.

- **Deliverables.** What the contract says will be delivered. Each deliverable becomes:

  ```yaml
  - kind: "report"            # this harness only delivers reports; flag anything else
    deadline: "YYYY-MM-DD"    # absolute date; convert relative dates ("end of Q2") to ISO.
                              # If the brief does not state a deadline, default to TODAY's date
                              # (the cover-page date). Do not prompt the user for it.
  ```

  If multiple deliverables are mentioned, list each.

- **Acknowledgements.** Names of client team members and advisors the brief explicitly asks to be acknowledged. **Leave the list empty if the brief does not name anyone — do not prompt the user for it.**

- **Notes.** Free-text field for anything that does not fit cleanly above (variation to brief, prior work, restricted-information caveats).

## Step 3 — Resolve ambiguities

If any of the following hold, **ask the user before writing the yaml**:

- Two or more candidate questions with overlapping wording — the user must confirm whether they are one question or two.
- Numbered questions that mix research questions with management requests in the same numbering — confirm which the user wants treated as Q1..Qn deliverables.
- A binding fact that could be read as either a constraint or a preference (e.g., "we prefer not to use sourced individuals from outside the catchment") — confirm whether it is binding.
- A deliverable kind that is not `report` (e.g. a presentation deck, an Excel matrix). Ask the user how to handle it; this harness only delivers Biomatix consulting reports.

Do **not** proceed past Step 3 with unresolved ambiguities.

## Step 4 — Write brief.yaml

Write the merged contract to `jobs/<slug>/brief.yaml` using the schema seeded by `/new-job`. Preserve key order; preserve verbatim text in `client.name`, `client.address`, `project.title`, `questions[].text`, and `binding_facts[].fact`.

## Step 5 — Confirmation

Show the user a concise summary:
- N questions extracted (list IDs and one-line excerpts).
- N binding facts extracted.
- The path of the written `brief.yaml`.
- **Only one field is a hard blocker for `/popgen-report`**: `data.rdata_path`. If it's blank, ask the user to fill it (or to drop the data file at `jobs/<slug>/data/<name>.RData` and tell you the filename). Do not list the other intentionally-deferred fields — `project.species.common_name`, `project.species.conservation_status`, `acknowledgements` — as "missing"; they're not, they're agent-filled.

End the message with: "Run `/popgen-report` when the data file is in place."

## Rules

- Do not paraphrase verbatim contract language.
- Do not invent missing fields. Empty is empty.
- Do not begin any genetic analysis. Intake is parse-and-confirm only; analysis is a separate command.
- Do not edit `$1` (the brief). The brief is the contract; treat it as immutable.
