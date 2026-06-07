---
description: Scaffold a new job directory under jobs/<slug>/ for a manuscript reference check. Creates draft/, references/, outputs/, memory/ and pins the active job.
argument-hint: <slug>
---

You are scaffolding a new reference-check job at `jobs/$1/` in the current project.

The slug `$1` should identify the manuscript — a short, lowercase, hyphenated handle, e.g.
`<firstauthor>-<topic>-<YYYYMMDD>` (`georges-turtle-genomics-20260606`). If the slug the user
supplied does not look like that, point it out before creating anything and let the user adjust.

## Steps

1. **Verify the slug.** Reject if it contains spaces, uppercase letters, or path separators.
   Lowercase letters, digits, and hyphens only.

2. **Check for collisions.** If `jobs/$1/` already exists, do not overwrite — list its current
   contents and ask the user whether to (a) pick a different slug, (b) reuse the existing job,
   or (c) abort.

3. **Create the skeleton.** Use the Bash tool with PowerShell:

   ```powershell
   New-Item -ItemType Directory -Path jobs/$1/draft -Force | Out-Null
   New-Item -ItemType Directory -Path jobs/$1/references -Force | Out-Null
   New-Item -ItemType Directory -Path jobs/$1/outputs -Force | Out-Null
   New-Item -ItemType Directory -Path jobs/$1/memory -Force | Out-Null
   ```

   - `draft/` — the manuscript to check (Markdown, `.docx`, LaTeX, or plain text) and, if the
     references are separate, the `.bib` / reference file.
   - `references/` — optional job-local PDFs the user supplies for paywalled sources (read by
     `claim-check`). The shared PDF store is the repository-level `Literature/` folder.
   - `outputs/` — the reference audit and any change logs. The only path the reference-check
     workflow writes job output to.
   - `memory/` — per-job session notes so a later session can resume.

4. **Seed `jobs/$1/memory/MEMORY.md`** with the same skeleton as the project root MEMORY.md so
   future sessions can resume cleanly:

   ```markdown
   # MEMORY.md — Job memory index ($1)

   This is the per-job memory index for `jobs/$1/`. It is read at session start when work
   resumes on this job. Cross-job memory lives at `<project root>/memory/`.

   ## Manuscript
   - Target journal: _(not set)_
   - Draft file: _(paste into jobs/$1/draft/)_

   ## Progress
   _(none yet)_

   ## Outstanding
   _(none yet)_
   ```

5. **Set the active-job pin.** Write the slug to `.claude/active_job` so the PreToolUse safety
   hook recognises this job as the one Claude may write into. This is the *only* automatic pin
   write — switching to an existing job requires the explicit `/switch-job` command.

   ```powershell
   Set-Content -LiteralPath .claude/active_job -Value '$1' -NoNewline
   ```

   Tell the user that the active-job pin is now `$1` and that writes to any other `jobs/<slug>/`
   are blocked until they run `/switch-job`.

6. **Confirm.** Report the four directories created, the seeded memory index, the active-job
   pin, and the next step: drop the manuscript (and any reference file) into `jobs/$1/draft/`,
   then run `/reference-check jobs/$1/draft/<file>` (state the target journal).

## Rules

- Do not invent manuscript or reference content — those come from the file the user supplies.
- Do not run any analysis or fetch any references at scaffold time. That is `/reference-check`.
- Do not edit any file outside `jobs/$1/`.
- If the user supplies no slug, ask for one and stop. Do not pick a default.
