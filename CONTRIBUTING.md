# Contributing to Claude_Sandpit_Reference_Check

Thanks for helping improve this reference-checking sandpit. Changes are reviewed and
incorporated through **GitHub Pull Requests (PRs)**, so every proposed change can be
discussed and approved before it lands on `main`.

This repository is **public**. Anything you commit (including history) is visible to
everyone, so do not add manuscripts, paywalled PDFs, credentials, or private library
paths to a PR.

---

## The workflow at a glance

1. You make changes on a **branch**.
2. You open a **pull request** against `biomatix/Claude_Sandpit_Reference_Check:main`.
3. The maintainer (Arthur) is **notified**, reviews the diff, comments, and either merges
   or requests changes.
4. Once merged, everyone pulls the updated `main`.

There are two ways to get your changes onto a branch, depending on your access.

---

## Option A — Fork + pull request (no special access needed)

Use this if you are **not** a collaborator on the repo.

**One-time setup**

1. On GitHub, open
   <https://github.com/biomatix/Claude_Sandpit_Reference_Check> and click **Fork**.
   This creates `your-username/Claude_Sandpit_Reference_Check`.
2. Clone your fork:

   ```bash
   git clone https://github.com/your-username/Claude_Sandpit_Reference_Check.git
   cd Claude_Sandpit_Reference_Check
   ```

3. Point at the original repo so you can stay up to date:

   ```bash
   git remote add upstream https://github.com/biomatix/Claude_Sandpit_Reference_Check.git
   ```

**Each set of changes**

```bash
git checkout main
git pull upstream main            # sync with the latest
git checkout -b short-descriptive-name
# ...make your edits...
git add <files>
git commit -m "Concise summary of the change"
git push origin short-descriptive-name
```

Then on GitHub, your fork shows a **"Compare & pull request"** button — click it, target
`biomatix/...:main`, and fill in the description (see *Writing a good PR* below).

---

## Option B — Collaborator + pull request

Use this if Arthur has added you as a **Write collaborator**. You skip the fork and work
in the repo directly.

```bash
git clone https://github.com/biomatix/Claude_Sandpit_Reference_Check.git
cd Claude_Sandpit_Reference_Check
git checkout -b short-descriptive-name
# ...make your edits...
git add <files>
git commit -m "Concise summary of the change"
git push origin short-descriptive-name
```

Then open a pull request from your branch into `main` on GitHub. **Do not push directly
to `main`** — always go through a PR so the change can be reviewed.

---

## Writing a good pull request

- **One topic per PR.** Smaller PRs are reviewed faster.
- **Title:** a short imperative summary, e.g. *"Add issue-number stripping to reference-style"*.
- **Description:** what changed, why, and anything the reviewer should check. Link any
  related discussion.
- Keep commits focused; a clear message beats many tiny "wip" commits.

## Notifications & review

- The maintainer is notified automatically when a PR is opened (and via the repo's
  **Pull requests** tab). Watching the repo with **Watch → All Activity** ensures nothing
  is missed.
- Review happens in the PR's **Files changed** tab. Expect inline comments; respond by
  pushing more commits to the same branch — the PR updates automatically.
- The maintainer merges accepted PRs (**Squash and merge** is preferred to keep history
  tidy) or closes them with an explanation.

## Keeping your branch current

If `main` moves while your PR is open:

```bash
git checkout main
git pull upstream main      # or `origin main` if you are a collaborator
git checkout short-descriptive-name
git merge main              # resolve any conflicts, then push again
```

---

## Scope and house rules

This sandpit does exactly one thing: **check the referencing of an existing draft
manuscript** (see `.claude/CLAUDE.md` for the full task list and conventions). Please keep
contributions within that scope — the skills, hooks, and conventions that support
reference checking — rather than adding unrelated features.

A couple of repository-specific points:

- **Safety hook.** `.claude/hooks/guard.ps1` is the project's hard safety boundary
  (sandpit containment + per-job isolation). Do not weaken its checks without a clear,
  agreed reason described in the PR.
- **Job data stays out.** The `jobs/<slug>/` directories hold per-manuscript work and the
  `Literature/` PDFs are git-ignored. Don't commit manuscript content, PDFs, or anything
  tied to a specific author's unpublished work.

Thanks again — clear, well-scoped PRs make this easy to review and incorporate.
