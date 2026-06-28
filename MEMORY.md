# MEMORY.md — Project memory index

This file is the project's memory index, read at session start per `.claude/CLAUDE.md` §5. It
holds cross-job lessons for the reference-check harness (literature-access arrangements,
recurring journal-style preferences, pointers to external systems). Per-manuscript state lives
in `jobs/<slug>/memory/`.

Add one line per memory file under the matching heading: `- [Title](path/to/file.md) — one-line
hook`. Keep this index under 200 lines.

## User

_(none yet)_

## Feedback

- [Literature access: Sci-Hub refused, ANU pending](memory/literature-access-scihub-anu.md) — Sci-Hub/Sci-Net is a firm no (don't rebuild); ANU institutional access agreed, auth-model decision pending.

## Project

- **Active job (pin):** `jobs/waters-methylome-20260611/` — Waters/Hanrahan *Pogona* methylome ms (target **GBE**). All 7 reference checks COMPLETE + audit rendered to PDF; **parked clean 2026-06-11**. 25 PDFs filed, 20 still needed (pdfs_needed.ris). Outstanding = author fixes + claim-check ~14 refs once PDFs supplied. Full state in that job's `memory/MEMORY.md`. (Pin left here for clean resume.)
- **Parked:** `jobs/pearson-ms-20260608/` — *Pogona vitticeps* sex-reversal fecundity ms (target PNAS). All 7 reference checks + extended soundness review COMPLETE (2026-06-09); parked clean 2026-06-11. Two items offered but not delivered (author action list; audit PDFs). Resume notes in that job's `memory/MEMORY.md`.
- **Other jobs on disk:** `jobs/brain-ms-20260606/`. Empty leftover `jobs/pearson-ms/` (locked .docx) still pending deletion. (`field-guide-20260609` was an unused empty-seed job — deleted 2026-06-11.)

## Reference

- [GitHub remote](memory/github_remote.md) — repo at biomatix/Claude_Sandpit_Reference_Check (PUBLIC since 2026-06-28); push via `git push origin main`, GitHub Desktop, or gh; gh CLI v2.95.0 installed 2026-06-28 (not yet authenticated).
- [EndNote Find Full Text — ANU settings](memory/endnote-anu-fulltext.md) — OpenURL Path `https://anu.primo.exlibrisgroup.com/view/uresolver/61ANU_INST/openurl?`; Authenticate URL `https://virtual.anu.edu.au/login`.
- [.docx comments & PDF rendering](memory/docx-comments-and-pdf.md) — pandoc drops Word comments (extract from word/comments.xml); render audits to PDF via pandoc + TinyTeX lualatex/Calibri.
