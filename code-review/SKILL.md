---
name: code-review
description: Multi-agent pull request code review with false-positive filtering. Use when asked to review a PR, review a pull request, do a code review on GitHub, check a PR for bugs or CLAUDE.md/AGENTS.md compliance, or post review comments back to GitHub. Focuses on high-confidence bugs and project-convention violations, not nitpicks.
---

# Pull Request Code Review

Adapted from the official Anthropic `code-review` plugin (`plugins/code-review/commands/code-review.md`).
Upstream ships this as a `/code-review` slash command; here it is a skill so any harness can invoke it.

Provide a code review for the given pull request. Use `gh` for all GitHub interaction (never web fetch).

## Procedure

Make a todo list first. Where the steps below say "agent", dispatch a subagent if the harness
supports it (cheap/fast model for mechanical steps, stronger model for review steps); otherwise do
the step yourself in sequence.

1. **Eligibility check.** Check whether the PR (a) is closed, (b) is a draft, (c) does not need review
   (automated PR, or trivially and obviously fine), or (d) already has a review from you. If any hold,
   stop — do not proceed.
2. **Collect convention files.** Get a list of file *paths* (not contents) to relevant `CLAUDE.md` /
   `AGENTS.md` files: the repo root one, plus any in directories the PR modified.
3. **Summarize the change.** View the PR and produce a summary of what it does.
4. **Five parallel reviewers.** Each returns a list of issues plus the reason each was flagged
   (convention adherence, bug, historical git context, ...):
   - Agent 1: audit changes against `CLAUDE.md`/`AGENTS.md`. These files are guidance for writing
     code, so not every instruction applies to review.
   - Agent 2: read only the diff and do a shallow scan for obvious bugs. Do not pull extra context.
     Focus on large bugs; skip nitpicks; ignore likely false positives.
   - Agent 3: read `git blame`/history of the modified code and find bugs visible only in that context.
   - Agent 4: read previous PRs touching these files; check whether comments there also apply here.
   - Agent 5: read code comments in the modified files; check the change complies with their guidance.
5. **Confidence scoring.** For each issue, one agent scores confidence 0–100 given the PR, the issue,
   and the convention-file list. For issues flagged from `CLAUDE.md`/`AGENTS.md`, verify the file
   actually calls out that specific issue. Rubric (give verbatim to the scorer):
   - 0: not confident at all — false positive that fails light scrutiny, or a pre-existing issue.
   - 25: somewhat confident — might be real, might not; unverified. Stylistic issues not explicitly
     called out in the relevant convention file land here.
   - 50: moderately confident — verified real, but possibly a nitpick or rare in practice.
   - 75: highly confident — double-checked, very likely hit in practice, current approach insufficient,
     or explicitly mentioned in the relevant convention file.
   - 100: certain — confirmed real, frequent in practice, evidence directly confirms it.
6. **Filter to score >= 80.** If nothing survives, do not proceed to commenting with issues.
7. **Re-check eligibility** (repeat step 1) before posting.
8. **Post the comment** with `gh`. Keep it brief, no emojis, link and cite relevant code/files/URLs.

## False positives (for steps 4 and 5)

- Pre-existing issues.
- Things that look like a bug but are not.
- Pedantic nitpicks a senior engineer would not raise.
- Anything a linter, typechecker, or compiler catches (missing imports, type errors, broken tests,
  formatting). Do not run builds yourself — assume CI covers them.
- General code-quality complaints (test coverage, vague security, docs) unless the convention file
  explicitly requires them.
- Issues called out in a convention file but explicitly silenced in code (e.g. a lint-ignore comment).
- Functional changes that are plainly intentional or part of the broader change.
- Real issues on lines the PR did not modify.

## Notes

- Do not check build signal or try to build/typecheck the app.
- Cite and link every bug. If you invoke a convention file, link it.
- Code links must use the **full commit SHA** — `$(git rev-parse HEAD)` inside the comment will not
  work, because the comment is rendered as Markdown:
  `https://github.com/owner/repo/blob/<full-sha>/path/file.py#L10-L15`
  - `#` after the filename, range as `L[start]-L[end]`, repo must match the reviewed repo.
  - Include at least one line of context before and after (commenting on 5–6 → link `L4-L7`).

## Comment format

Follow precisely. With issues found:

```markdown
### Code review

Found 3 issues:

1. <brief description of bug> (CLAUDE.md says "<...>")

<full-sha permalink with line range>

2. <brief description of bug> (some/other/CLAUDE.md says "<...>")

<full-sha permalink with line range>

3. <brief description of bug> (bug due to <file and code snippet>)

<full-sha permalink with line range>
```

With nothing found:

```markdown
### Code review

No issues found. Checked for bugs and CLAUDE.md compliance.
```

Upstream appends a "Generated with Claude Code" footer and a 👍/👎 feedback line; drop or replace it
to match the harness actually posting the review.
