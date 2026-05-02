---
description: Switch the active-job pin (.claude/active_job) to a different job slug. The PreToolUse safety hook reads this pin and rejects writes to any other job, so this command is the only legitimate way to change which job is being worked on.
argument-hint: <slug>
---

You are switching the active-job pin from whatever it is now to `$1`.

The pin is the file `.claude/active_job`. The PreToolUse hook at `.claude/hooks/guard.ps1` reads it before every Edit / Write / NotebookEdit / Bash call and blocks anything that would write into a different `jobs/<other-slug>/...` directory. Switching the pin is therefore a privileged action — it changes which job Claude can mutate.

## Steps

1. **Read the current pin.** If `.claude/active_job` exists, show its current value to the user. If it does not exist, say so.

2. **Verify the target job exists.** `jobs/$1/` must already exist (created by `/new-job`). If it does not, stop and tell the user; do not create it.

3. **Confirm with the user.** Even though the user just typed the command, this is a state-changing operation that affects the safety hook. State both the previous slug and the new slug, and ask the user to confirm before writing the pin. If the user declines, do not write the pin.

4. **Write the pin atomically.** Use the Bash tool with PowerShell:

   ```powershell
   Set-Content -LiteralPath .claude/active_job -Value '$1' -NoNewline
   ```

   `-NoNewline` keeps the pin file as a single bare slug (the hook's `Trim()` makes this robust either way, but a single line is cleaner).

5. **Confirm.** Show the user the new pin's contents and remind them that writes to other jobs are now blocked. If they need to look at another job's files, Read / Grep / Glob still work — only writes are restricted.

## Rules

- Never write the pin without user confirmation in step 3.
- Never delete `.claude/active_job` to "unpin" — write an empty value if absolutely needed, but the hook treats no-pin and empty-pin identically (both block all writes to `jobs/*/`).
- Do not create `jobs/$1/`. That belongs to `/new-job`.
- If the user typed the wrong slug (e.g. `/switch-job awc-mala-202604201` with a typo), point it out before writing the pin.
