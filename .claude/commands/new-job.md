---
description: Scaffold a new job directory under jobs/<slug>/ for a Biomatix popgen contract. Creates brief.md, brief.yaml, data/, references/, outputs/, memory/.
argument-hint: <slug>
---

You are scaffolding a new Biomatix consulting job at `jobs/$1/` in the current project.

The slug `$1` should follow the convention `<client-short>-<species-short>-<YYYYMMDD>` (e.g. `nsw-dpe-bellinger-20260315`). If the slug the user supplied does not look like that, point it out before creating anything and let the user adjust.

## Steps

1. **Verify the slug.** Reject if it contains spaces, uppercase letters, or path separators. Lowercase letters, digits, and hyphens only.

2. **Check for collisions.** If `jobs/$1/` already exists, do not overwrite — list its current contents and ask the user whether to (a) pick a different slug, (b) reuse the existing job, or (c) abort.

3. **Create the skeleton.** Use the Bash tool with PowerShell:

   ```powershell
   New-Item -ItemType Directory -Path jobs/$1/data -Force | Out-Null
   New-Item -ItemType Directory -Path jobs/$1/references -Force | Out-Null
   New-Item -ItemType Directory -Path jobs/$1/outputs -Force | Out-Null
   New-Item -ItemType Directory -Path jobs/$1/memory -Force | Out-Null
   ```

4. **Seed `jobs/$1/brief.md`** with a one-line placeholder so the file exists for `/intake` to populate. Do not invent client details — the file is a stub the user will paste the contract into.

   ```markdown
   <!-- Paste the verbatim contract brief below. Then run /intake jobs/$1/brief.md to parse it into brief.yaml. -->
   ```

5. **Seed `jobs/$1/brief.yaml`** with empty fields so the user (or `/intake`) can fill them. Use this exact shape — the harness expects these keys:

   ```yaml
   slug: $1
   client:
     name: ""
     address: ""
   project:
     title: ""
     species:
       scientific_name: ""
       common_name: ""
       conservation_status: ""
   data:
     rdata_path: ""     # path to .Rdata, relative to jobs/<slug>/; loaded with gl <- gl.load(file=...)
                        # dartRverse infers marker type (SNP / silicoDArT) from the file — no need to set it.
   questions: []        # filled by /intake — list of {id, text, deliverable_section, success_criterion}
   binding_facts: []    # filled by /intake — list of {fact, sections_constrained}
   deliverables:
     - kind: "report"   # this harness only delivers Biomatix consulting reports
       deadline: ""     # cover-page date; defaults to today's date if /intake leaves it blank
   acknowledgements: [] # leave empty unless the brief names people; not prompted by intake
   notes: ""
   ```

6. **Create `jobs/$1/memory/MEMORY.md`** with the same skeleton as the project root MEMORY.md so future sessions can resume cleanly:

   ```markdown
   # MEMORY.md — Job memory index ($1)

   This is the per-job memory index for `jobs/$1/`. It is read at session start when work resumes on this job. Cross-job memory lives at `<project root>/memory/`.

   ## User
   _(none yet)_

   ## Feedback
   _(none yet)_

   ## Project
   _(none yet)_

   ## Reference
   _(none yet)_
   ```

7. **Set the active-job pin.** Write the slug to `.claude/active_job` so the PreToolUse safety hook recognises this job as the one Claude may write into. This is the *only* automatic pin write — switching to an existing job requires the explicit `/switch-job` command.

   ```powershell
   Set-Content -LiteralPath .claude/active_job -Value '$1' -NoNewline
   ```

   Tell the user that the active-job pin is now `$1` and that writes to any other `jobs/<slug>/` are blocked until they run `/switch-job`.

8. **Confirm.** Report the four directories created, the three seeded files, the active-job pin, and the next step: paste the contract into `jobs/$1/brief.md`, then run `/intake jobs/$1/brief.md`.

## Rules

- Do not invent client, species, or question content — those come from the contract via `/intake`.
- Do not stage R code or attempt to load the .Rdata file. That belongs to `/popgen-report`.
- Do not edit any file outside `jobs/$1/`.
- If the user supplies no slug, ask for one and stop. Do not pick a default.
