# Claude_SandPit_Biomatix_Reports

A Claude Code harness for producing population-genetics consulting reports for Biomatix Pty Ltd. The harness wraps the dartRverse R toolchain in a structured pipeline that turns a client brief into a Biomatix house-style report.

## Documentation

- [MANUAL.md](MANUAL.md) — operating manual: how the harness is structured, how to run a job end to end, how the skills and critic agents fit together.
- [.claude/CLAUDE.md](.claude/CLAUDE.md) — project rules read by Claude Code at session start: coding conventions, R/RStudio integration, per-job isolation, memory scopes, safety hooks.

## Repository scope

This repository tracks the harness only — skills, agents, hooks, slash commands, project rules, and the manual. Per-contract work under `jobs/<slug>/` (briefs, raw data, drafts, final outputs) is deliberately excluded by `.gitignore` and kept on the local working machine.
