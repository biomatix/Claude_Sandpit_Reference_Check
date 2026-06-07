# Reference-check sandpit — user manual

This sandpit is a **harness** that audits the referencing of a draft manuscript before you
submit it to a journal. It checks the citations and the reference list, and **does nothing
else** — it does not write, restructure, or analyse. Claude Code is the runtime; this manual
tells you how to operate it.

---

## 1. What it checks

Seven tasks, in order (see `.claude/CLAUDE.md §1`):

1. **In-text → list** — every citation in the body *and in figure/table captions* is in the
   reference list.
2. **List → in-text** — every reference-list entry is cited somewhere.
3. **Missing key works** — flags well-known published works the manuscript ought to cite.
4. **Existence** — every cited reference is real (CrossRef / PubMed / the PDF).
5. **Correctness & format** — author list, year, title, journal, volume, pages match the
   published record, formatted to your target journal; bracketed issue numbers dropped where
   the journal does not require them; title capitalisation made consistent.
6. **PDFs** — the full text of each cited reference is filed in `Literature/`; if it can't be
   found, you are asked to supply it.
7. **Claim support** — the cited source actually supports the assertion next to it; departures
   are flagged.

The harness **reports and proposes**. It edits your manuscript or reference list only when you
explicitly ask, and it logs what it changed. It never fabricates a reference, a DOI, or a
supporting quotation — anything it cannot verify is flagged for you.

---

## 2. Running a check

```
/new-job <slug>
```

Scaffolds `jobs/<slug>/` (`draft/ references/ outputs/ memory/`) and pins the job so writes are
isolated to it. Use a short lowercase hyphenated slug, e.g. `georges-turtle-genomics-20260606`.

Put the manuscript into `jobs/<slug>/draft/` — Markdown, `.docx`, LaTeX, or plain text. If the
references live in a separate `.bib` or reference file, put it there too. A `.docx` is converted
to Markdown (`pandoc`) so the body, captions, and list are readable; the original is kept.

```
/reference-check jobs/<slug>/draft/<file>
```

Runs all seven checks and writes `jobs/<slug>/outputs/reference_audit.md`. **Tell it the target
journal** — it governs the reference formatting in task 5. To apply high-confidence fixes
afterwards, ask explicitly (e.g. "apply the metadata fixes", "reformat the list"); changes are
logged to `outputs/reference_audit_changes.md`.

You can also run the worker skills individually:

| Skill | Does |
|---|---|
| `/citation-check` | tasks 4 & 5 — references exist; metadata correct (no reformat, no cross-check) |
| `/reference-style` | task 5 — format a list to the target journal's style |
| `/claim-check` | task 7 — cited source supports the assertion |
| `/lit-search-a` | tasks 3 & 6 — missing key works; locate a paper / its PDF |

---

## 3. The PDF stores and the retrieval cascade

Tasks 6 and 7 need full-text PDFs. Two stores back them:

- **`Literature/`** (in the repo root, read **and** write) — the shared store of PDFs for cited
  references, named `<Surname>_<Year>_<sanitised-DOI>.pdf` (DOI's `/` → `_`). Copies are filed
  here automatically when a PDF is obtained; later checks reuse them.
- **`D:/workspace/AA_Literature/`** (read-only) — your subscription/Mendeley library. Searched,
  never written to.

When full text is needed the cascade is: `Literature/` → the job's `references/` → your personal
library → open-access web (Unpaywall → PMC → preprint → publisher OA). If none yields the PDF,
the source is listed under **`## PDFs needed`** and you are asked to download it into
`Literature/` (any filename — it gets renamed) or `jobs/<slug>/references/`; the step then
re-runs.

---

## 4. Multiple manuscripts, isolation, and memory

Each manuscript is a separate `jobs/<slug>/`. A `PreToolUse` safety hook
([.claude/hooks/guard.ps1](.claude/hooks/guard.ps1)) keeps every write inside the sandpit root
and inside the **pinned** job only (`.claude/active_job`). To work on a different existing job:

```
/switch-job <slug>
```

which changes the pin after confirming with you. Reads are never blocked, so a new check can
consult an earlier one's notes.

Long checks can span sessions. Project-wide lessons go in `<root>/memory/` (indexed by
`MEMORY.md`); one manuscript's state (target journal, checks done, PDFs awaited, open claim
departures) goes in `jobs/<slug>/memory/`. Say "continue the <slug> check" to resume.

---

## 5. What it will not do

It will not draft or rewrite the manuscript, edit prose for style, restructure sections, run any
analysis, or build a bibliography from scratch. If you ask for those, it will say so and stop.
Its entire remit is the seven reference-checking tasks above.
