---
name: review-draft
description: Use when the user asks for a thorough review of an existing draft Biomatix consulting report without running any new computational analyses. Treats all numbers, figures, tables, and analysis results in the draft as fixed inputs. Fans out to the four critic subagents (critic-coverage, critic-substance, critic-citations, critic-writing) in parallel — critic-citations invokes both citation-check (existence + metadata) and claim-check (assertion vs source). Produces a single review document; does NOT edit the draft and does NOT produce a revised version. Trigger phrases: "review my draft", "audit this report", "give it a thorough review", "go over this".
---

# review-draft

A skill for producing a thorough review of an existing draft Biomatix consulting report, **without running any computational analyses**. Fans out to the four critic subagents in `.claude/agents/` (`critic-coverage`, `critic-substance`, `critic-citations`, `critic-writing`), runs them in parallel, and assembles the four audit blocks into a single review document.

## What this skill does and does not do

**Does:**
- Read the draft as supplied.
- Spawn the four critic subagents in parallel against the draft.
- Within `critic-citations`, both `citation-check` (existence + metadata) and `claim-check` (assertion vs source) are run.
- Assemble the four audit blocks into a single review document at `jobs/<slug>/outputs/<basename>_review.md`.

**Does not:**
- Start the RStudio session or run any R code.
- Compute new statistics, generate new figures, or re-analyse the data.
- Edit the draft itself.
- Produce a revised version of the draft.
- Auto-apply citation-check or claim-check corrections (read-only is enforced; the user can run popgen-report Step 5 separately if they want corrections applied).

If the user asks for any of the above (e.g. "review and revise"), point them to popgen-report (which include the full assembly and citation-correction loop) and stop.

---

## Step 0 — Intake

Establish from the user, asking only for what is missing:

1. **Path to the draft.** Markdown, plain text, Word, or PDF. If markdown with figure/table snippets in `jobs/<slug>/outputs/`, the snippets are part of the draft.
2. **Job slug.** Required so the critics can locate `jobs/<slug>/brief.yaml` (for coverage), `jobs/<slug>/references/` (for claim-check local PDF overrides), and write the review next to the draft. If the draft path is `jobs/<slug>/outputs/...`, derive the slug from it; otherwise ask.
3. **Confirm it is a Biomatix report.** Section headings should include `BRIEF`, `VARIATION TO THE BRIEF`, `PREAMBLE`, `STRATEGY`, or `EXECUTIVE SUMMARY`. If the draft is some other document type, stop and ask the user — this skill is scoped to Biomatix consulting reports only.
4. **Scope toggles** — whether to skip any of the four critic passes (rare; the default is all four). For example, a draft that has not yet had references inserted should skip `critic-citations`.
5. **Output filename.** Default is `jobs/<slug>/outputs/<basename>_review.md`. The user may override.

If the draft references a separate `citation_provenance.md` (produced by popgen-report), critic-substance and critic-citations will cross-reference it; ask whether one exists and where.

---

## The four critic passes (parallel)

Spawn the four critic subagents in a single message via parallel Agent calls. Each runs against the draft, returns its audit as markdown, and you (the orchestrator) write each audit to `jobs/<slug>/outputs/`. The critics never edit the draft.

| Subagent | Audit file | Purpose |
|---|---|---|
| `critic-coverage` | `coverage_audit.md` | Every Q1..Qn answered substantively; binding facts honoured. Reads `jobs/<slug>/brief.yaml` or `outputs/prompt_coverage_table.md`. |
| `critic-substance` | `substance_audit.md` | Methods, parameters, calibration of interpretation, traceability from results to recommendations. Reads `.claude/skills/popgen-report/playbook.md` Appendix B. |
| `critic-citations` | `citations_audit.md` | Two passes: `citation-check` (existence + metadata, read-only) and `claim-check` (assertion vs source — fetches DOI → open-access PDF/HTML, preprint, or abstract; falls back to `paywalled — manual check needed`). |
| `critic-writing` | `writing_audit.md` | `clear-writing` plus `reference-style-1`. Capped at 15 concrete prose rewrites and 20 reference-list rewrites. |

Each subagent's prompt should include: the draft path, the job slug, the document type, the path to any `citation_provenance.md`, and (for critic-coverage) the path to `brief.yaml` or `prompt_coverage_table.md`.

A pass that fails (e.g. claim-check hits a network error or a subagent returns an error) should produce a partial audit in its file with the failure recorded; do not abort the whole run on a single failure.

---

## Step 6 — Assemble the review document

After all four critic subagents return, concatenate their audits into a single review at `jobs/<slug>/outputs/<basename>_review.md`:

```markdown
# Review: <draft filename>

Date: <YYYY-MM-DD>
Job: <slug>
Reviewer: review-draft skill (orchestrating four critic subagents)

## 1. Coverage

<contents of coverage_audit.md>

## 2. Substance

<contents of substance_audit.md>

## 3. Citations (existence, metadata, assertion vs source)

<contents of citations_audit.md>

## 4. Writing (prose + reference formatting)

<contents of writing_audit.md>

## Summary

<3–6 bullet points naming the most consequential issues across all four
passes, ordered by severity. This is what the user reads first. List
blocking issues separately from non-blocking observations.>
```

Save the document and report the path to the user. The four per-critic audit files remain alongside the consolidated review for traceability. Do not edit the draft itself.

---

## Working-directory layout

All audit files and the consolidated review go to `jobs/<slug>/outputs/`. The draft itself is read from wherever the user supplied it; if the draft is also in `jobs/<slug>/outputs/` (the typical case when reviewing a popgen-report output), the review lands beside it.

The skill writes only the four `*_audit.md` files plus the consolidated review. No other intermediates.

---

## Common pitfalls

- **Treating recommendations as actionable when they require re-analysis.** If `critic-substance` surfaces "the K range was too narrow", that is information for the user, not a fix this skill can apply. The substance audit must mark such items "requires re-analysis (out of scope for this review)" so the user can route them to popgen-report Step 2 if they decide to act.
- **Letting `critic-writing` swamp the review.** The 15-rewrite cap is enforced inside the subagent's system prompt; if it returns more, the orchestrator trims to 15 before consolidation.
- **Confusing read-only citation-check with the auto-apply variant.** This skill never authorises auto-apply for either citation-check or claim-check. If the user wants corrections applied, that is a separate invocation.
- **Missing slug.** Without a slug, `critic-coverage` cannot locate the contract and `critic-citations` cannot locate the local PDF directory. If the draft is not under `jobs/<slug>/`, ask the user before spawning subagents.
- **Not detecting document type correctly.** A short draft might be missing the headings used for detection. Ask the user when in doubt; do not guess.
