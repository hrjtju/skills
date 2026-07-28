---
name: ralph-wiggum-loop
description: "Ralph Wiggum technique: run an agent in a while-loop that feeds the same prompt back until the task is genuinely done. Use when asked to set up an autonomous/unattended iteration loop, 'keep going until tests pass', overnight or long-running self-correcting agent work, or when asked about ralph loop / ralph wiggum / --completion-promise / --max-iterations. Also covers when NOT to loop."
---

# Ralph Wiggum Loop

> "Ralph is a technique. In its purest form, Ralph is a Bash loop." — Geoffrey Huntley (2025)

An iterative development method: repeatedly feed an agent the same prompt until the task completes.
Anthropic packaged it as the `ralph-loop` Claude Code plugin (stop-hook based); the idea itself is
harness-agnostic. Sources: `plugins/ralph-loop` in `anthropics/claude-plugins-official`, and
https://awesomeclaude.ai/ralph-wiggum.

## Principles

| Principle | Meaning |
|---|---|
| Iteration > perfection | Don't aim for perfect on the first pass; let the loop refine it. |
| Failures are data | Deterministically bad output is predictable and informative. |
| Operator skill matters | Success depends on prompt quality, not just model quality. |
| Persistence wins | The loop handles retry; you handle the stopping condition. |

Between iterations the agent's memory is the **filesystem and git history**, not the context window.
The prompt must therefore tell it to inspect existing work first.

## Purest form (works in any harness)

```bash
while :; do cat PROMPT.md | claude ; done
```

With pi's print mode and a hard iteration cap plus a completion sentinel:

```bash
MAX=20
for i in $(seq 1 $MAX); do
  echo "=== iteration $i ==="
  out=$(cat PROMPT.md | pi -p "Continue the task. Inspect existing files and git log first." | tee /dev/tty)
  case "$out" in *"<promise>COMPLETE</promise>"*) echo "done at $i"; break;; esac
done
```

Run it inside a git worktree or a scratch branch, commit each iteration, and keep `PROMPT.md` under
version control so you can see what you actually asked for.

If using Claude Code with the plugin instead:

```
/plugin install ralph-loop@claude-plugins-official
/ralph-loop:ralph-loop "<prompt>" --max-iterations 20 --completion-promise "COMPLETE"
/ralph-loop:cancel-ralph
```

Claude Code 2.1 also ships supported primitives that cover most cases and survive version updates —
prefer these when available: `/goal` (work until a condition verifies), `/loop` (re-run on an
interval), `/batch` (one mechanical change across many parallel worktree agents).

## Prompt writing (the actual skill)

**1. Clear completion criteria.**

- Bad: `Build a todo API and make it good.`
- Good:
  ```
  Build a REST API for todos. When complete:
  - All CRUD endpoints working
  - Input validation in place
  - Tests passing (coverage > 80%)
  - README with API docs
  - Output: <promise>COMPLETE</promise>
  ```

**2. Incremental goals.** Phase 1 / Phase 2 / Phase 3, promise only when all phases done.

**3. Self-correction pattern.** Spell out the loop body: write failing test → implement → run tests →
debug on failure → refactor → repeat until green → emit the promise.

**4. Escape hatches.**
- Always set a max-iteration cap; it is the primary safety net.
- Completion promises are exact string matches — brittle by design, so never the only stop condition.
- Document what to do after N failed iterations (write a blocker report and stop).

**Critical rule for the agent inside the loop:** emit the completion promise only when the statement
is completely and unequivocally TRUE. Do not fake it to escape the loop, even when stuck. If stuck,
write the blockers to a file and let the iteration cap end the run.

## When to use

Good for: well-defined tasks with clear success criteria; work that needs iteration (getting tests
green); greenfield projects you can walk away from; tasks with automatic verification (tests, linters);
overnight/weekend automated work.

Not good for: tasks needing human judgment or design decisions; one-shot operations; unclear or
subjective success criteria; production debugging; anything requiring approvals or human-in-the-loop.

## Templates

Feature: requirements list + success criteria + `<promise>COMPLETE</promise>`, `--max-iterations 30`.
TDD: test-first loop, `<promise>DONE</promise>`, `--max-iterations 50`.
Bug fix: reproduce → root cause → fix → regression test → verify; after 15 iterations document
blockers and alternatives; `<promise>FIXED</promise>`, `--max-iterations 20`.
Refactor: constraints (tests pass, no behavior change, incremental commits);
`<promise>REFACTORED</promise>`, `--max-iterations 25`.

Parallelize by giving each loop its own git worktree and branch.

## Cost and honesty warning

Reported results (6 repos overnight at a YC hackathon, a $50k contract delivered for $297 of API
cost, the CURSED language) are anecdotes from the technique's creator, not benchmarks. Unattended
loops burn tokens continuously — always cap iterations, and check cost after the first run before
scaling up.
