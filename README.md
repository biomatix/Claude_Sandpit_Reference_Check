# Claude_SandPit_Reference_Check

A Claude Code harness for **checking the referencing of a draft manuscript** before submission.
It audits citations and the reference list — and does nothing else (no writing, no analysis).

The audit covers: in-text and caption citations all appear in the reference list and vice
versa; no key published work is missing; every cited reference exists and its metadata is
correct and formatted to the target journal; the full-text PDF of each cited reference is filed
in `Literature/`; and each cited source actually supports the assertion it is attached to.

## Usage

```
/new-job <slug>                       scaffold jobs/<slug>/ and pin it
# drop the manuscript into jobs/<slug>/draft/
/reference-check jobs/<slug>/draft/<file>   run all seven checks -> outputs/reference_audit.md
```

## Documentation

- [MANUAL.md](MANUAL.md) — full operating manual: the seven checks, a workflow diagram, running a job step by step, and the **EndNote** round-trip for pulling PDFs through institutional access.
- [.claude/CLAUDE.md](.claude/CLAUDE.md) — project rules read at session start: the seven
  tasks, the skills, file conventions, memory, and the safety hook.

## Skills

- `reference-check` — orchestrator; runs the seven checks in order.
- `citation-check` — references exist and metadata is correct.
- `reference-style` — format a reference list (target journal authoritative).
- `claim-check` — the cited source supports the in-text assertion.
- `lit-search-a` — find missing key works and locate full-text PDFs.

## Repository scope

The harness is tracked (skills, commands, hook, project rules, manual). Per-manuscript work
under `jobs/<slug>/` and the `Literature/` PDFs are git-ignored and kept on the local machine.
