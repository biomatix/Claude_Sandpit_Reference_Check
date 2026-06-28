# CLAUDE.md — Project Rules for Claude_SandPit_Reference_Check

This sandpit does one thing: **check the referencing of an existing draft manuscript.** It
does not write manuscripts, run analyses, or produce reports. Every element here serves the
reference-checking task below.

---

## 1. Purpose and scope

The user is a **professional scientist** (population genetics / genomics background) who
supplies a draft manuscript and asks for its referencing to be audited before submission to a
target journal. The audit comprises exactly these tasks, and **nothing more**:

1. **In-text → list.** Every citation in the body *and in the figure and table captions*
   appears in the reference list.
2. **List → in-text.** Every entry in the reference list is cited somewhere in the manuscript.
3. **Missing key works.** Flag any key published reference that ought to be cited but is absent.
4. **Existence.** Every cited reference is real — confirmed via CrossRef (and PubMed / Google
   Scholar where there is no DOI), or by the PDF itself.
5. **Correctness and format.** Each entry's author list, year, title, journal, volume, and
   pages match the published record, and the entry is formatted to the **target journal's**
   style. If the journal does not require issue numbers, **remove the `(N)` after the volume**.
   Make title capitalisation **consistent** across the whole list.
6. **PDFs.** Obtain the full-text PDF of each cited reference and file a copy in `Literature/`;
   if it cannot be located, **ask the user** to download it into `Literature/`.
7. **Claim support.** The cited source actually contains text supporting the assertion it is
   attached to. **Flag every departure** to the user.
8. **Quotations.** Every direct quotation is reproduced **verbatim** (words and punctuation) from
   the cited source, with any omission marked by an ellipsis and any editorial change in
   `[brackets]`; its citation names a **single** source with the **page after a colon**
   (`Brown, 1996:72`); and a quotation over 30 words is set as indented italics without quote
   marks. **Flag every departure** — non-verbatim text, a wrong/missing/mis-punctuated page, a
   multi-source citation, or a long quote still in quote marks. The full rules are in §8.

Do not extend beyond these tasks. Do not rewrite the science, restructure the manuscript, edit
prose for style, or perform any computation. When something cannot be verified (an
unobtainable PDF, a paywalled claim), **flag it for the user** rather than guessing or papering
over it. **Never fabricate** a reference, a DOI, or a supporting passage.

---

## 2. The workflow and its skills

The whole job runs through the **`reference-check`** skill (the orchestrator). It sequences
five worker skills, each of which the user may also invoke directly:

- **`/reference-check`** — runs all seven checks in order over a manuscript and writes a single
  `reference_audit.md`. Start here.
- **`/citation-check`** — tasks 4 & 5: every reference exists and its metadata matches the
  published record (existence + metadata only; does **not** reformat, and does **not**
  cross-check in-text vs list).
- **`/reference-style`** — task 5: format a reference list to the **target journal's** style
  (author–date / Harvard, numbered / Vancouver, APA, Chicago, CSE). The journal's author
  instructions are authoritative; a fully worked CSIRO Harvard author–date variant is the
  built-in default when the style is author–date or none is named.
- **`/claim-check`** — task 7: the cited source supports the in-text assertion. Returns
  *supported / partially supported / contradicted / not found / paywalled — manual check
  needed*.
- **`/quote-check`** — task 8: every direct quotation is reproduced verbatim from the cited
  source and on the cited page. Checks quotes character-for-character (honouring ellipsis
  elisions and `[bracketed]`/`[sic]` marks), confirms the cited page, and flags
  quotation-format departures. Does **not** judge paraphrased claims (that is `claim-check`).
- **`/lit-search-a`** — tasks 3 & 6: surface key published works the manuscript is missing, and
  locate / resolve a specific paper and its full-text PDF.

Tasks 1 & 2 (the in-text/caption ↔ reference-list cross-check, both directions) are performed
by `reference-check` itself — no separate skill owns them.

---

## 3. Written output standards

When reporting an audit or proposing a corrected reference, write **clearly, concisely, and
directly** — active voice, short words, every word earning its place. Report findings; propose
corrections; apply an edit to the manuscript or reference list **only when the user asks**. Log
any applied changes alongside the audit.

---

## 4. File and directory conventions

### 4.1 Per-job working directories

Each manuscript is checked in its own subdirectory under `jobs/`:

```
jobs/<slug>/
├── draft/        the manuscript (.md/.docx/.tex/.txt) and any separate .bib / reference file
├── references/   optional: job-local PDFs the user supplies for paywalled sources
├── outputs/      reference_audit.md and any change logs — the only path the workflow writes to
└── memory/       per-job session notes (cross-job memory lives in <root>/memory/)
```

A new job is scaffolded with `/new-job <slug>`. `outputs/` is the only path the reference-check
workflow may write job output to.

### 4.2 The shared `Literature/` PDF store and the retrieval cascade

Two PDF stores back the full-text retrieval needed by tasks 6 and 7:

- **`Literature/`** (in the sandpit root) — **read and write.** The repository's store of
  full-text PDFs for cited references, named **`<FirstAuthorSurname>_<Year>_<sanitised-DOI>.pdf`**
  (DOI with `/` → `_`; e.g. a 2018 Zhang paper at `10.1371/journal.pone.0205209` →
  `Literature/Zhang_2018_10.1371_journal.pone.0205209.pdf`). Whenever a full-text PDF for a
  **cited** reference is obtained — fetched from the open web or copied from the personal
  library — a copy is filed here. PDFs are git-ignored; only the folder is tracked.
- **`D:/workspace/AA_Literature/`** (outside the sandpit) — **read-only.** The user's
  subscription/Mendeley library, granted via `permissions.additionalDirectories`. Searched but
  never written to.

When a literature-reading step (`claim-check`, `lit-search-a`, or the PDF-filing step of
`reference-check`) needs a paper's **full text**, it works this cascade and stops at the first
hit: (1) `Literature/` (`Glob *<sanitised-DOI>.pdf`, or by first-author surname + year); (2) the
job's `jobs/<slug>/references/`; (3) the personal library `D:/workspace/AA_Literature/`
(matched by surname + year or DOI, falling back to reading first pages when filenames are
uninformative); (4) the Georges lab page `georges.biomatix.org/publications/all` for
A. Georges–authored works (it links full-text PDFs and is not bot-blocked); (5) open-access web
(Unpaywall → PMC → preprint → publisher OA); (6) otherwise the source is recorded under a
`## PDFs needed` block (plus a machine-readable `pdfs_needed.ris`/DOI list for the user's
reference manager) and the user is asked to download the PDF into `Literature/` (any filename —
it is renamed) or `jobs/<slug>/references/`, after which the step re-runs. Headless fetching is
often bot-blocked even for open-access and cannot perform institutional SSO; the sanctioned route
for the paywalled set is the user's own authenticated tools (EndNote/Zotero "Find Full Text"
over institutional access), fed by the emitted `.ris`/DOI list.

The harness **only reads** `references/` and the personal library — the user owns both. It
**may write** only to `Literature/`, and only to file a cited full-text PDF (one fetched from
the open web, or copied *from* the personal library — never written *to* it).

---

## 5. Session continuity and memory

Reference checks can span sessions (usage limits). To resume cleanly:

- **Project memory** lives in `<root>/memory/`, indexed by `<root>/MEMORY.md`. Use it for
  cross-job lessons: literature-access arrangements, recurring journal-style preferences,
  pointers to external systems. Don't duplicate this file.
- **Job memory** lives in `jobs/<slug>/memory/`, indexed by `jobs/<slug>/memory/MEMORY.md`
  (seeded by `/new-job`). Use it for one manuscript's state: target journal, which checks are
  done, PDFs still awaited, claim departures still open.

At session start, read `<root>/MEMORY.md`; when resuming a job, also read its job memory. Use
TodoWrite to track multi-step checks. Save the audit and change logs to `jobs/<slug>/outputs/`
as each stage completes, not only in the chat. Before stopping or nearing limits, write a short
state note to job memory (active slug, what's done, what's outstanding). Keep each `MEMORY.md`
under 200 lines; update or remove stale entries rather than appending.

---

## 6. General conduct

- Stay within the seven tasks. Do not add features, prose edits, or analysis beyond what is
  asked.
- Do not edit the manuscript or reference list without explicit instruction; propose first.
- When in doubt about the target journal's style or whether a flagged item is an error, ask.
- Never fabricate, invent, or alter a reference, a DOI, a quotation, or a result.

---

## 7. Safety: sandpit containment and per-job isolation

A `PreToolUse` hook at [.claude/hooks/guard.ps1](.claude/hooks/guard.ps1) enforces two
invariants on every Edit, Write, NotebookEdit, MultiEdit, and Bash tool call:

1. **Sandpit containment.** No write may resolve outside the sandpit root (the directory
   containing this `CLAUDE.md`). Paths are canonicalised — `..` traversal and absolute paths are
   checked equivalently. The hook also scans Bash commands for the common write idioms (`>`,
   `>>`, `tee`, `Out-File`, `Set-Content`, `Add-Content`, `New-Item`, `rm`, `Remove-Item`) and
   rejects any whose target resolves outside. `Literature/` is inside the root, so PDF filing is
   allowed; `D:/workspace/AA_Literature/` is outside, so it stays read-only.

2. **Per-job isolation.** A pin file at `.claude/active_job` holds the slug of the active job.
   Any write to `jobs/<slug>/...` for any other slug is blocked. **Reads are not blocked** — a
   new job may consult a prior job's notes. The pin is set by `/new-job` and changed by
   `/switch-job` (with confirmation). If the pin is missing or empty, *all* writes to `jobs/*/`
   are blocked.

**One system carve-out:** Edit/Write calls targeting `~/.claude/plans/*.md` are allowed (plan
mode writes there); everything else under `~/.claude/` is blocked.

When the hook blocks a call it exits 2 with `BLOCKED by guard.ps1: <reason>` on stderr. For an
out-of-sandpit write, stop — the action is forbidden by policy. For a wrong-job write, stop and
ask whether to `/switch-job`. Never edit `guard.ps1` to weaken a check without explicit user
instruction; it is the project's hard safety boundary.

---

## 8. Quotation rules

These are the house rules `quote-check` (task 8) enforces. A quotation that follows them is
checked against its source; a quotation that breaks them is **flagged** (never silently fixed).

1. **Verbatim.** A direct quotation reproduces the source exactly — words **and punctuation** —
   not a paraphrase.
2. **Double quotes for quotations.** Use double quotation marks (`"`). Single quotes (`'`) are
   reserved for emphasis (`he 'dropped the bundle'`) or a quote within a quote (`the term
   'enropion' means …`). Because a draft under audit may not yet follow this rule, `quote-check`
   distinguishes a single-quoted *quotation* from single-quoted *emphasis* — a span immediately
   followed by a citation, or longer than a few words, is taken as a quotation — and flags it for
   conversion to double quotes. Output advice and corrected text always use double quotes.
3. **Ellipsis marks an omission.** Truncate the start with a leading `…` inside the quote
   marks, the end with a trailing `…`, and an internal aside removed with `…`. Material may be
   missing only where an ellipsis appears.
4. **Square brackets mark an editorial change.** An addition, clarification, or correction goes
   in `[brackets]` — e.g. `parliamentary [sic] sessions`. Bracketed text is the author's, not
   the source's, and cannot be auto-verified; it is flagged for a human eye.
5. **Long quotations.** A quotation longer than **30 words** is set as **indented italics with
   no quotation marks**; a shorter one is inline in double quotes.
6. **Citation of a quotation.** A quotation is followed by the citation of the **single** source
   that contains it, with the **page number separated from the citation by a colon** —
   `(Brown, 1996:72)`.

Worked example. The source (Brown, 1996:72) reads, verbatim: *It was always thought that the
quick brown fox, a cunning beast, jumped over the lozy dog.* All of the following are
rule-correct quotations of it:

- `"It was always thought that the quick brown fox, a cunning beast, jumped over the lozy dog" (Brown, 1996:72).`
- `"It was always thought that the quick brown fox, a cunning beast, jumped over the lazy [sic] dog" (Brown, 1996:72).`
- `"… the quick brown fox, a cunning beast, jumped over the lazy [sic] dog" (Brown, 1996:72).`
- `"… the quick brown fox … jumped over the lazy [sic] dog" (Brown, 1996:72).`
- and, being over 30 words, set as indented italics without quote marks:
  *It was always thought that the quick brown fox, a cunning beast, jumped over the lazy [sic]
  dog but this is now known to be simply a fable that has perpetuated over time within the
  English-speaking countries* (Brown, 1996:72).
