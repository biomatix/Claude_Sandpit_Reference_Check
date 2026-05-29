# CLAUDE.md — Project Rules for Claude_SandPit_Biomatix_Reports

## 1. User Profile

The user is a **professional geneticist** using Claude Code as an analytical collaborator. Work is conducted in the context of population genetics, genomics, and related quantitative analyses. All assistance should be calibrated to this level of domain expertise.

---

## 2. Primary Programming Language: R

All code written on behalf of the user must be in **R** unless the user explicitly requests otherwise.

### 2.1 Package Priority: dartRverse

Wherever a relevant function exists in the **dartRverse** ecosystem (packages: `dartR.base`, `dartR.data`, `dartR.popgen`, `dartR.spatial`, `dartR.sim`, `dartRsexlinked`), use it in preference to equivalent functions from other packages. dartRverse functions operate on `genlight` objects (S4 class from the `adegenet` package) and are the standard analytical toolkit for this project.

When no dartRverse function covers the requirement, fall back to packages from the tidyverse, then base R, then other well-maintained CRAN packages then other packages or software written in other languages — in that order of preference.

### 2.2 Coding Style: Tidyverse

Follow the [tidyverse style guide](https://style.tidyverse.org/) for all R code:

- Use `<-` for assignment (not `=`).
- Use snake_case for variable and function names; use the `gl.` prefix for any new functions that operate on genlight objects.
- Two-space indentation.
- Spaces after commas and around infix operators.
- Keep lines to 80 characters where practical.
- Use double quotes for strings.
- Prefer `|>` (base pipe, R ≥ 4.1) for pipelines; use `%>%` only if required for compatibility.
- Use `ggplot2` for all visualisation; apply `theme_dartR()` as the default plot theme.

---

## 3. Script Format: Follow gl.report.bases.r

All R scripts and functions written for this project must follow the structure and conventions of `gl.report.bases.r` from the dartRverse codebase. This means:

### 3.1 Roxygen2 Documentation

Every function must include a complete roxygen2 header block:

```r
#' @name function.name
#' @title Brief title (sentence case, no trailing period)
#' @family <family group>
#'
#' @description
#' One or more paragraphs describing what the function does.
#'
#' @param x Name of the genlight object [required].
#' @param plot.display If TRUE, plots are displayed in the plot window [default TRUE].
#' @param plot.theme Theme for the plot [default theme_dartR()].
#' @param plot.colors List of two color names for borders and fill [default c("#2171B5","#6BAED6")].
#' @param plot.file Name for the RDS binary file to save (base name only) [default NULL].
#' @param plot.dir Directory to save plot RDS files [default tempdir()].
#' @param verbose Verbosity: 0, silent or fatal errors; 1, begin and end; 2,
#' progress log; 3, progress and results summary; 5, full report
#' [default NULL, unless specified using gl.set.verbosity].
#' @param ... Parameters passed to \link[ggplot2]{ggsave}.
#'
#' @details
#' Extended explanation of methods, caveats, and references.
#'
#' @author Author. Custodian: Name -- Post to \url{https://groups.google.com/d/forum/dartr}
#'
#' @examples
#' out <- function.name(testset.gl)
#'
#' @export
#' @return Description of the return value.
```

### 3.2 Function Body Structure

Use the following internal section layout, marked with comment banners:

```r
function.name <- function(x,
                          plot.display = TRUE,
                          plot.theme = theme_dartR(),
                          plot.colors = NULL,
                          plot.file = NULL,
                          plot.dir = NULL,
                          verbose = NULL,
                          ...) {

  # PRELIMINARIES -- checking ----------------
  funname <- match.call()[[1]]
  verbose <- gl.check.verbosity(verbose)
  plot.dir <- gl.check.wd(plot.dir, verbose = 0)
  utils.flag.start(func = funname, build = "v.2023.3", verbose = verbose)
  datatype <- utils.check.datatype(x, accept = c("genlight", "SNP", "SilicoDArT"),
                                   verbose = verbose)

  # DO THE JOB --------------------------------
  # ... analysis logic ...

  # PLOT THE RESULTS --------------------------
  # ... ggplot2 visualisation ...

  # SAVE PLOT (OPTIONAL) ----------------------
  # ... utils.plot.save() call if plot.file is not NULL ...

  # FLAG SCRIPT END ---------------------------
  if (verbose >= 1) {
    cat(report("Completed:", funname, "\n"))
  }

  # RETURN
  invisible(x)
}
```

### 3.3 Verbosity

Use the standard dartRverse verbosity levels for all console output:

| Level | Behaviour |
|-------|-----------|
| 0 | Silent — fatal errors only |
| 1 | Begin and end messages |
| 2 | Progress log |
| 3 | Progress and results summary |
| 5 | Full report |

Wrap all console messages in the appropriate helper: `error()`, `warn()`, `report()`, or `important()`.

### 3.4 Error Handling

Validate inputs at the start of every function using the dartRverse utility functions (`utils.check.datatype()`, etc.). Use `stop(error(...))` for fatal errors and `cat(warn(...))` for warnings within verbose output.

---

## 4. Written Output: Scientific Writing Standards

When producing any text output — reports, summaries, interpretations, manuscript sections, or other written documents — apply the principles defined in the project skills:

- **`/lit-search-a`** — search the primary published (peer-reviewed) literature for a focal taxon; returns cited facts with resolved metadata. Used by the ecologist and geneticist agents.
- **`/lit-search-b`** — search the grey/government conservation literature (IUCN Red List always; national/sub-national statutory listings, recovery plans, submissions per the job's jurisdiction). Used by the conservationist agent.
- **`/clear-writing`** — general prose quality, economy of expression, grammar, and style.
- **`/reference-style-1`** — CSIRO Harvard referencing format for in-text citations and the reference list.
- **`/citation-check`** — verify that every reference in the list points to a real publication and that the metadata matches the published record (existence and metadata only).
- **`/claim-check`** — verify that the cited paper actually supports the in-text assertion that cites it (assertion vs source; complements `/citation-check`, distinct scope).

The report is produced by the `popgen-report` skill, which acts as **Orchestrator** over persistent production agents in `.claude/agents/`: `ecologist`, `conservationist`, `geneticist` (concurrent briefings), then `planner` (with user sign-off) and `analyst`. The report follows a scientific-paper structure — Executive Summary (with recommendations) → Brief → Variation → Preamble → Materials and Methods → Results → Discussion → References.

For end-to-end review of a draft, four persistent critic subagents in `.claude/agents/` run as a quartet (typically via `/review`):

- **`critic-coverage`** — every client question Q1..Qn answered substantively in a named section; binding facts honoured.
- **`critic-substance`** — methods, parameter choices, calibration of interpretation, traceability from results to recommendations.
- **`critic-citations`** — orchestrates `/citation-check` (existence) and `/claim-check` (assertion vs source).
- **`critic-writing`** — `/clear-writing` plus `/reference-style-1`, capped at 15 concrete rewrites.

In brief: write clearly, concisely, and directly. Use active voice. Prefer short words. Every word must earn its place. The harness produces only Biomatix consulting reports under the house-style template at `.claude/skills/popgen-report/report_template.md`.

---

## 5. Executing R Code: RStudio Connection

All R code must be executed by sending it to the active RStudio session via the HTTP API at `http://127.0.0.1:8787/`. Never use `Rscript` or any other independent R process to run analyses.

The API accepts POST requests with a JSON body of the form `{"code": "<R code>"}` and returns `{"success": true, "output": "..."}` on success or `{"success": false, "error": "..."}` on failure. Use the `curl` Bash tool to make these calls.

Run gl.set.verbosity(3) early when running dartRverse workflows.

**Rules:**
- Send code in logical, self-contained chunks (library loading, data reading, analysis steps, summary output) rather than as one monolithic call, so that progress is visible and errors can be isolated.
- Always check the `success` field of each response before proceeding to the next step. If `success` is `false`, diagnose the error before sending further code.
- Objects created in one call persist in the RStudio session for subsequent calls — do not re-run earlier steps unnecessarily.
- Use `show()` rather than `print()` to display dartR genlight objects (the `print` method has a known display error in the current dartR.base version).

---

## 6. File and Directory Conventions

### 6.1 Per-job working directories

Every contract from Biomatix Pty Ltd lives in its own subdirectory under `jobs/`:

```
jobs/<client-short>-<species-short>-<YYYYMMDD>/
├── brief.md          verbatim contract text
├── brief.yaml        parsed contract (questions Q1..Qn, binding facts, deliverables)
├── data/             .Rdata, .rds, raw CSVs supplied with the brief
├── references/       optional: local PDFs of cited works (resolves paywalls for claim-check)
├── outputs/          drafts, audits, figures, tables, final Word document
└── memory/           job-local session notes (cross-job memory lives in <root>/memory/)
```

The slug `<client-short>-<species-short>-<YYYYMMDD>` is enforced by `/new-job`. The `outputs/` subdirectory is the only path the analyst, coordinator, and critics may write to during a job.

A new job is scaffolded with `/new-job <slug>`. The brief is then parsed with `/intake jobs/<slug>/brief.md`, which populates `brief.yaml`. From that point `/popgen-report` reads `brief.yaml` and writes into `jobs/<slug>/outputs/`.

### 6.2 R script and plot conventions

- Save all R scripts with `.R` extension (capital R).
- Name scripts after the primary function they define, following the `gl.verb.noun.R` pattern where applicable.
- Save plots as RDS files via `utils.plot.save()` unless the user requests a different format.
- Do not create documentation files (README, vignettes) unless explicitly requested.

---

## 7. Session Continuity and Memory

Multi-step workflows in this project often span multiple sessions because of usage limits. To ensure no work is lost and sessions can resume cleanly:

### 7.1 Two memory scopes

- **Project-level memory** lives in `<project root>/memory/` and is indexed by `<project root>/MEMORY.md`. Use it for cross-job lessons: feedback that applies to every contract, references to external systems, recurring patterns the user wants you to follow on every job. Do not duplicate CLAUDE.md content.
- **Job-level memory** lives in `jobs/<slug>/memory/` and is indexed by `jobs/<slug>/memory/MEMORY.md`, seeded by `/new-job`. Use it for state specific to one contract: pipeline phase in progress, decisions made during the job, blockers, intermediate outputs already on disk. Job memory is what a future session reads when the user says "continue the bellinger job".

### 7.2 At session start

- Read `<project root>/MEMORY.md` and any project-level memory files relevant to the user's request before beginning work.
- If the user is resuming a specific job, also read `jobs/<slug>/memory/MEMORY.md` and the job-local memory files.
- If the user says "continue", "pick up where we left off", or similar, consult memory to reconstruct context rather than asking the user to re-explain.

### 7.3 During work

- Use the TodoWrite tool to track multi-step tasks. Update task status in real time (mark completed immediately, not in batches).
- Save intermediate outputs to `jobs/<slug>/outputs/` as each analytical step completes — do not accumulate results only in the R session, where they are lost if the session dies.
- When spawning subagents (the four critics or any one-off Agent call), note their purpose and expected output files in the todo list so a future session can verify completion.

### 7.4 Before session end or when nearing limits

- **Proactively save session state to job memory** when: (a) the user says they are stopping, (b) a subagent reports a usage-limit error, or (c) you sense the conversation is approaching context limits (e.g., after many large tool results).
- The session-state memory save should include:
  - Which job slug is active.
  - What was completed this session (list of steps/deliverables with file paths under `jobs/<slug>/outputs/`).
  - What is still outstanding (next steps, blockers, open questions).
  - Any decisions or caveats the user should know about.
- Update `jobs/<slug>/memory/MEMORY.md` and the relevant job-local memory files (especially `pipeline_status.md` if a multi-phase workflow was interrupted) so the next session has a clean picture.
- Lessons that generalise across jobs (recurring user feedback, project-wide conventions) should be written to `<project root>/memory/`, not the job-local memory.

### 7.5 Memory hygiene

- Do not duplicate information already in CLAUDE.md or derivable from the codebase.
- Keep each `MEMORY.md` under 200 lines — it is an index, not a narrative.
- Update or remove stale memories rather than appending indefinitely.
- Job-local memory can be left in place when the job ships — it is part of the job's archived record. Project-level memory should be kept clean of job-specific entries that have outlived their relevance.

---

## 8. General Conduct

- Do not add features, comments, or documentation beyond what is asked.
- Do not refactor code that is not the subject of the current request.
- Do not speculate about future requirements or add handling for hypothetical edge cases.
- When in doubt about the intended analysis, ask before writing code.
- Never fabricate, invent, or alter data or results.

---

## 9. Safety: Sandpit Containment and Per-Job Isolation

A `PreToolUse` hook at [.claude/hooks/guard.ps1](d:/workspace/Claude_Code/Claude_SandPit_Biomatix_Reports/.claude/hooks/guard.ps1) enforces two invariants on every Edit, Write, NotebookEdit, MultiEdit, and Bash tool call:

1. **Sandpit containment.** No write may resolve outside the sandpit root (the directory containing this `CLAUDE.md`). Paths are canonicalised — `..` traversal and absolute paths are checked equivalently. The hook also scans Bash commands for the common write idioms (`>`, `>>`, `tee`, `Out-File`, `Set-Content`, `Add-Content`, `New-Item`, `rm`, `Remove-Item`) and rejects any whose target resolves outside.

2. **Per-job isolation.** A pin file at `.claude/active_job` holds the slug of the currently active job. Any write to `jobs/<slug>/...` for any slug other than the pinned one is blocked. **Reads are not blocked** — the cross-job-learning case (a new job consulting a prior job's notes) is exactly what the per-job folder structure exists to support.

**One system carve-out:** Edit/Write/NotebookEdit/MultiEdit calls targeting `~/.claude/plans/*.md` are allowed even though they fall outside the sandpit, because plan mode writes its plan files there. The carve-out is scoped exactly to `*.md` files in that one directory; everything else under `~/.claude/` is still blocked, and Bash writes to that path are also still blocked (Claude has no reason to write plan files via shell).

The pin is set by `/new-job <slug>` (automatically, when scaffolding a new job) and changed by `/switch-job <slug>` (explicitly, with user confirmation). If the pin is missing or empty, *all* writes to `jobs/*/` are blocked — there is no "default job".

### What the hook cannot enforce

The RStudio HTTP API at `http://127.0.0.1:8787/` runs R with full filesystem access. When Claude posts an R chunk to that endpoint, the hook sees only the curl command and cannot reliably parse R syntax to find `write*`, `save*`, `saveRDS`, etc. The popgen skills constrain R writes to `jobs/<slug>/outputs/` via `setwd()` plus prompt-level discipline, but this is *prompt enforcement*, not a hard hook. Users who want hard enforcement of the R session should add wrappers in `~/.Rprofile` that refuse to write paths that do not normalise under the sandpit root.

### When the hook blocks a tool call

The hook exits with status 2 and writes `BLOCKED by guard.ps1: <reason>` to stderr. Claude sees the rejection message and should:

- For an out-of-sandpit write: stop. The action is forbidden by project policy. If the user genuinely intends to write outside, they must do it themselves (the hook only governs Claude).
- For a wrong-job write: stop and ask whether to switch the active job via `/switch-job`. Do not silently retry.

Never edit `.claude/hooks/guard.ps1` to weaken or disable a check without explicit user instruction. The hook is the project's hard safety boundary; treating it as a soft suggestion defeats its purpose.

---

## 10. External Software Paths

External binaries invoked from R live at the paths below. The user's `~/.Rprofile` (at `C:/Users/arthu/Documents/.Rprofile`) sets the corresponding R options at session start, so scripts should not hard-code these paths — refer to the option instead.

| Software | Version | Install location | R option |
|---|---|---|---|
| NeEstimator | v2.1 | `C:/Users/arthu/AppData/Local/Programs/NeEstimator_v2.1/` | `options(neest.path = ...)` |
| pandoc-crossref | v0.3.23 (pandoc 3.9) | `C:/Users/arthu/AppData/Local/Pandoc/pandoc-crossref.exe` | — (on PATH) |

- **NeEstimator** — used by `dartR::gl.LDNe()` for linkage-disequilibrium Ne estimation. The Windows binary is `Ne2-1.exe` inside the install directory; `gl.LDNe()` expects the containing folder path, which is already set by `~/.Rprofile`. To verify: `getOption("neest.path")`.
- **pandoc-crossref** — a pandoc filter that resolves `{#fig:name}` / `{#tbl:name}` / `{#eq:name}` labels and `[@fig:name]` cross-references when rendering markdown to PDF. Invoke as `pandoc --filter pandoc-crossref input.md -o output.pdf`, or add `filters: [pandoc-crossref]` under `pandoc_args` in an rmarkdown YAML header. Installed alongside `pandoc.exe`, so it is found automatically. A version-string warning ("compiled with pandoc 3.9 but running through 3.9.0.2") is cosmetic and can be ignored — both use the same pandoc-types 1.23.1.1 library.
