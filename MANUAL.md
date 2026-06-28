# Reference-check harness — user manual

This sandpit is a **Claude Code harness** that audits the referencing of a draft manuscript
before you submit it to a journal. It checks the citations, the reference list, and the
quotations — and **does nothing else**: it does not write, rewrite, restructure, or analyse the
science. It reports and proposes; it changes your files only when you ask.

This manual covers what it does, the end-to-end workflow (including the **EndNote** component for
pulling PDFs through your institutional access), how to run a job, and what it produces.

---

## 1. What it checks — the eight tasks

For one manuscript, the harness runs eight checks (see `.claude/CLAUDE.md §1`):

1. **In-text → list.** Every citation in the body *and in figure/table captions* appears in the
   reference list.
2. **List → in-text.** Every reference-list entry is cited somewhere.
3. **Missing key works.** Flags well-known published works the manuscript ought to cite.
4. **Existence.** Every cited reference is real (verified via CrossRef/PubMed, or the PDF itself).
5. **Correctness & journal format.** Author list, year, title, journal, volume, pages match the
   published record; formatted to the **target journal** (issue numbers dropped where the journal
   omits them; consistent title case).
6. **PDFs.** The full text of every cited reference is filed in `Literature/` (or you are asked
   to supply it).
7. **Claim support.** The cited source actually contains text supporting the assertion next to
   it; departures are flagged.
8. **Quotations.** Every direct quotation is reproduced **verbatim** from the cited source and
   sits on the **cited page**; departures and quotation-format breaches are flagged.

It **reports and proposes**; it edits the manuscript or reference list only on explicit request,
and never fabricates a reference, DOI, supporting passage, or quotation.

### The quotation rules (task 8)

Check 8 enforces the house rules in `.claude/CLAUDE.md §8`. In short:

- A quotation is **verbatim** — words *and punctuation* — never a paraphrase.
- **Double** quotes delimit a quotation; **single** quotes are for emphasis or a quote within a
  quote. A draft may break this rule, so the harness tells a single-quoted *quotation* (one
  immediately followed by a citation, or longer than a few words) from single-quoted *emphasis*,
  and flags the quotation for conversion to double quotes. Its advice always uses double quotes.
- An omission is marked by an ellipsis `…`; an editorial change goes in `[brackets]` (e.g.
  `[sic]`), which the harness flags for your eye since it can't verify bracketed text.
- A quotation over **30 words** is set as indented italics with no quote marks.
- A quotation cites a **single** source with the **page after a colon** — `(Brown, 1996:72)`.

---

## 2. Workflow at a glance

The job is a two-stage literature process wrapped around the checks, with you + EndNote doing
the part robots can't (authenticated PDF download).

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │ SET UP                                                                   │
  │   /new-job <slug>   →  drop the manuscript into jobs/<slug>/draft/        │
  └───────────────┬────────────────────────────────────────────────────────┘
                  │
  ┌───────────────▼─────────────  /reference-check  ───────────────────────┐
  │ STAGE 1 — IDENTIFY & VERIFY THE LITERATURE  (harness, automatic)         │
  │   • cross-check in-text ↔ reference list      (checks 1, 2)              │
  │   • find missing key works                    (check 3, lit-search)      │
  │   • verify existence + metadata vs CrossRef   (check 4)                  │
  │   • format to the target journal              (check 5)                  │
  └───────────────┬────────────────────────────────────────────────────────┘
                  │
  ┌───────────────▼─────────────  STAGE 2 — SOURCE THE PDFs  (check 6) ──────┐
  │  harness works the retrieval cascade for every cited reference:          │
  │   Literature/ → job references/ → your AA_Literature library →           │
  │   Georges lab page → open-access web                                     │
  │  whatever it CAN'T get (paywalled / bot-blocked) →  pdfs_needed.ris  ────┼──┐
  └───────────────┬─────────────────────────────────────────────────────────┘  │
                  │                                                              │
  ┌───────────────▼─────────────  YOU + ENDNOTE  ◄──────────────────────────────┘
  │  import pdfs_needed.ris → Find Full Text (ANU)
  │  → copy the PDFs into Literature/  → tell harness
  └───────────────┬──────────────────────────────────
                  │ (harness normalises the filenames)
  ┌───────────────▼────────────────────────────────────────────────────────┐
  │ STAGE 3 — EXAMINE  (checks 7 & 8, once PDFs are in)                      │
  │   • claim-check every in-text assertion against its source PDF  (7)      │
  │       → supported / partial / contradicted / not-found                  │
  │   • quote-check every direct quotation against its source PDF   (8)      │
  │       → verbatim+page / altered / wrong-or-missing page / format        │
  └───────────────┬────────────────────────────────────────────────────────┘
                  │
  ┌───────────────▼────────────────────────────────────────────────────────┐
  │ DELIVERABLES                                                             │
  │   reference_audit.md + claims_audit.md + quotes_audit.md  (markdown)     │
  │   references.ris                          (clean corrected list — RIS)   │
  │   pdfs_needed.ris                         (anything still to fetch — RIS)│
  │   → you apply the fixes / run the journal style in EndNote               │
  └─────────────────────────────────────────────────────────────────────────┘
```

The checks **interleave** in practice (metadata verification feeds the cross-check; claim-check
and quote-check both wait on PDFs), but locate → source-PDFs → examine is the spine. Claim-check
and quote-check share the same filed PDFs: once a source is in `Literature/`, both read it.

---

## 3. Running a job, step by step

1. **Scaffold the job.**
   ```
   /new-job <slug>
   ```
   Use a short, lowercase, hyphenated slug, e.g. `georges-brain-20260607`. This creates
   `jobs/<slug>/` with `draft/ references/ outputs/ memory/` and pins the job (writes are
   isolated to it).

2. **Add the manuscript.** Put the draft into `jobs/<slug>/draft/` — Markdown, **`.docx`**,
   LaTeX or plain text. If the references are a separate `.bib`, put it there too. (`.docx` is
   converted to Markdown with `pandoc` so body, captions and list are all readable; the original
   is kept.)

3. **Run the check, naming the target journal.**
   ```
   /reference-check jobs/<slug>/draft/<file>
   ```
   Tell it the **target journal** — it governs check 5 (e.g. PLoS Genetics → numbered Vancouver,
   abbreviated journals, no issue numbers). The harness runs stages 1–2, files every PDF it can,
   and **pauses** with `pdfs_needed.ris` listing what it couldn't get.

4. **Do the EndNote PDF round-trip** (section 4) to obtain the remaining PDFs and drop them into
   `Literature/`. Tell the harness when done; it normalises the filenames and confirms coverage.

5. **Finish the examination (stage 3)** once all cited PDFs are present — claim-check (check 7)
   and quote-check (check 8) run against the filed sources.

6. **Review and apply.** Read `reference_audit.md`, `claims_audit.md`, and `quotes_audit.md`. Ask
   the harness to apply any high-confidence fixes (it logs them) and to produce the final
   `references.ris`. Run the journal style in EndNote for the submission-ready bibliography.

You can also run a single check directly — e.g. `/quote-check jobs/<slug>/draft/<file>` to verify
just the quotations, or `/citation-check` for existence and metadata only.

---

## 4. The EndNote component — pulling PDFs through institutional access

**Why EndNote is in the loop.** The harness fetches PDFs headlessly, but two walls stop it:
(1) **paywalls** — it has no institutional login; (2) **anti-bot blocking** (Cloudflare/403)
that rejects scripted downloads *even for open-access papers*. EndNote, running in your
authenticated session, gets past both. So the division of labour is: **the harness identifies
exactly which PDFs are needed and hands you an RIS; EndNote (with your ANU access) downloads
them.** The same filed PDFs serve both claim-check and quote-check, so the round-trip is done
once.

### 4.1 One-time setup
- Install **EndNote *Desktop*** (the ANU library licence). *Find Full Text is desktop-only* —
  EndNote Web/Online (myendnoteweb.com) won't batch-download.
- `Edit ▸ Preferences ▸ Find Full Text`: enable **DOI, PubMed (LinkOut), Web of Science, OpenURL**,
  and enter the **ANU** values:
  - **OpenURL Path:** `https://anu.primo.exlibrisgroup.com/view/uresolver/61ANU_INST/openurl?`
  - **Authenticate with: URL:** `https://virtual.anu.edu.au/login`  *(ANU reverse-proxy / EZproxy login — when Find Full Text runs, complete the ANU SSO popup that appears; that session is what unlocks subscribed publishers).*

  Or simply work **on the ANU VPN / on campus** so publisher access is granted by IP — the
  licence alone does *not* unlock paywalls; the proxy login (above) or network recognition does.
  Note: some publishers bot-block EndNote's downloader regardless of entitlement, so a few PDFs
  will always need a manual browser download.
- **Keep the EndNote library OUT of `Literature/`.** Put `My EndNote Library.enl` and `.Data` in
  Documents. (See the warning in 4.3.)

### 4.2 The round-trip
1. The harness gives you **`jobs/<slug>/outputs/pdfs_needed.ris`** (RIS = one record per needed
   reference, with the DOI — the field Find Full Text matches on).
2. In EndNote Desktop: `File ▸ Import ▸ File…` → choose `pdfs_needed.ris` → **Import Option:
   "Reference Manager (RIS)"**.
3. Connect the **ANU VPN**, select the imported references, **References ▸ Find Full Text**.
   Watch the left panel: "Found PDF" (📎 attached) vs "Not found".
4. **Get the PDFs into the harness.** EndNote stores attachments *inside itself*
   (`…\My EndNote Library.Data\PDF\…`), not in `Literature/`. So copy them out: select the
   references → drag the PDFs to a folder, or copy the `.pdf` files from the `.Data\PDF`
   subfolders, into **`Literature/`** (any filenames — the harness renames them).
5. Tell the harness "done." It runs `normalize_literature.py` to give every PDF the canonical
   `Surname_Year_DOI.pdf` name, confirms coverage, and proceeds to claim-check and quote-check.

### 4.3 ⚠ Gotchas (learned the hard way)
- **Never create or keep your EndNote library inside `Literature/`.** EndNote's *PDF
  auto-import* treats its own folder as a watched folder and will sweep every PDF out of the top
  level into an `Imported/` subfolder — making `Literature/` look empty. (Nothing is lost, but
  it's alarming.) Keep the library in Documents.
- **Fully quit EndNote before the harness reconciles `Literature/`.** If EndNote is live it
  keeps moving files; quit it (File ▸ Exit, check the system tray) so the folder holds still.
- **Turn off auto-import** (`Preferences ▸ PDF Handling ▸ Enable automatic importing` — unticked;
  and ensure the *PDF auto-import folder* is not `Literature/`).
- **Find Full Text won't get everything in one pass** — open-access ones come easily; paywalled
  ones need the VPN/proxy live. Re-run for misses. Your *own* papers are quickest dropped in
  directly.
- **Quotations need a readable, text-based PDF.** An image-only scan confirms a paper exists but
  cannot be checked for verbatim text or page; quote-check flags those as *manual check needed*.
- EndNote Web ≠ EndNote Desktop — only the desktop app has Find Full Text.

### 4.4 Mendeley / Zotero
Zotero ("Find Available PDF" on a multi-selection, + EZproxy) is a free alternative; Mendeley's
batch retrieval is weaker but its `Mendeley_pdfs` folder (inside `AA_Literature/`) is already
read by the harness's library tier. `pdfs_needed.ris` imports into all three.

---

## 5. The `Literature/` folder and the retrieval cascade

`Literature/` (repo root) is the harness's PDF store — read **and** write. PDFs are named
**`<FirstAuthorSurname>_<Year>_<sanitised-DOI>.pdf`** (DOI `/`→`_`). PDFs and the `_txt/`
extractions are git-ignored; only the folder is tracked.

When full text is needed — for filing (check 6), claim-check (check 7), or quote-check (check 8)
— the harness works this cascade, stopping at the first hit:
1. `Literature/` (already filed) → 2. the job's `references/` → 3. your personal library
**`D:/workspace/AA_Literature/`** (read-only) → 4. the **Georges lab page**
(`georges.biomatix.org/publications`) for A. Georges–authored works → 5. open-access web
(Unpaywall → PMC → preprint → publisher OA) → 6. otherwise it lists the source in
`pdfs_needed.ris` and asks you (section 4).

`normalize_literature.py` canonicalises any PDFs you drop in: it identifies each by the **DOI in
its text** (only trusting one of the manuscript's cited DOIs, so a reference's DOI can't hijack
the name), is safe on case-insensitive filesystems, dedupes keeping the text-richest copy, and
flags image-only scans.

---

## 6. Outputs

| File | Format | Contents |
|---|---|---|
| `outputs/reference_audit.md` | Markdown | the audit — all issues & analysis (the 8 checks) |
| `outputs/claims_audit.md` | Markdown | per-citation claim-vs-source verdicts + quoted passages |
| `outputs/quotes_audit.md` | Markdown | per-quotation verbatim & page verdicts + format breaches |
| `outputs/references.ris` | **RIS** | the clean corrected reference list — import into EndNote |
| `outputs/pdfs_needed.ris` | **RIS** | references still needing a PDF — the Find-Full-Text request |
| `outputs/reference_audit_changes.{rtf,md}` | RTF/MD | log of any fixes applied (RTF shows changes **in colour**) |

**Bibliographic deliverables are RIS** (they're for importing into a reference manager); the
audit/analysis is markdown. The harness does not produce a markdown reference list or a markdown
"PDFs needed" list as a deliverable.

For the journal-ready bibliography (e.g. PLoS Genetics numbered + abbreviated), import
`references.ris` into EndNote, set the output style to the journal, and "format bibliography" —
that renumbers by order of appearance and abbreviates journals.

---

## 7. Conventions & safety

- **One job per manuscript** under `jobs/<slug>/`. `/switch-job <slug>` changes the active job.
- A `PreToolUse` hook ([.claude/hooks/guard.ps1](.claude/hooks/guard.ps1)) blocks any write
  outside the sandpit root and any write into a non-active job. Reads are never blocked.
- The harness writes PDFs only to `Literature/`; it reads `AA_Literature/` (your library) and
  never writes to it.
- Long jobs can span sessions — state is kept in `jobs/<slug>/memory/`. Say "continue the <slug>
  check" to resume.

---

## 8. What it does NOT do

It will not draft or rewrite the manuscript, edit prose for style, restructure sections, run any
data analysis, build a bibliography from scratch, or invent a reference/DOI/quotation. It does
not silently "fix" a quotation or insert a page number — it proposes the verbatim correction and
leaves the decision to you. Anything it cannot verify is **flagged**, not papered over. Its remit
is the eight reference-checking tasks.

---

## 9. Quick reference

**Commands**
- `/new-job <slug>` — scaffold a job and pin it
- `/reference-check jobs/<slug>/draft/<file>` — run the checks (state the target journal)
- `/switch-job <slug>` — change the active job

**Skills** (also invocable directly): `reference-check` (orchestrator), `citation-check`
(existence + metadata), `reference-style` (journal formatting), `claim-check` (assertion vs
source), `quote-check` (quotation verbatim + page), `lit-search-a` (missing key works / locate a
paper).

**Scripts**
- `reference-check/scripts/normalize_literature.py --lit Literature --refs <manuscript> [--apply]`
  — canonical PDF names
- `reference-check/scripts/build_ris.py --refs <list> --out references.ris --all` — clean list as RIS
- `reference-check/scripts/build_ris.py --refs <list> --lit Literature --out pdfs_needed.ris --missing`
  — Find-Full-Text request
- `quote-check/scripts/extract_quotes.py <draft.md>` — pull quotations + citations + pages (run by the skill)
- `quote-check/scripts/match_quote.py --quote "<text>" --pdf <pdf> --cited-pages <n>` — verbatim & page test

**EndNote loop:** `pdfs_needed.ris` → Import (RIS) → ANU VPN → Find Full Text → copy PDFs into
`Literature/` → tell the harness. (Keep the EndNote library in Documents, not in `Literature/`.)
