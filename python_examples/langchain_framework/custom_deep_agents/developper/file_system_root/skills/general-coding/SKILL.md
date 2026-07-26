---
name: general-coding
description: |
  Trigger when: (1) User asks to implement, fix, refactor, or review code, (2) User requests tests, debugging, or performance improvements, (3) User wants a new feature in an existing codebase.

  General coding execution skill focused on safe, minimal, verifiable changes. Prioritizes correctness, clear assumptions, and validation through tests or static checks.
---

## Goal

Deliver production-ready code changes that satisfy the user request with the smallest correct diff.

## Standard Workflow

1. Understand the request
- Identify required behavior, constraints, and any non-goals.
- Confirm target files and entry points before editing.

2. Gather context
- Read nearby code, interfaces, and existing tests.
- Reuse established patterns in the repository.

3. Plan before editing
- Break work into small steps.
- Prefer backward-compatible changes unless the request requires a breaking change.

4. Implement minimal diffs
- Change only what is necessary.
- Keep naming and structure consistent with local style.
- Add short comments only where logic is non-obvious.

5. Validate
- Run the smallest relevant checks first (unit tests, linters, type checks, compile checks).
- If full test suites are expensive, run targeted tests and report limits.

6. Report clearly
- Summarize what changed and why.
- List validations executed and outcomes.
- Call out assumptions, risks, and follow-up options.

## Coding Rules

- Prefer readability over cleverness.
- Do not silently change unrelated behavior.
- Avoid broad refactors unless explicitly requested.
- Preserve public APIs unless the request requires API changes.
- Handle edge cases and error paths intentionally.

## Debugging Heuristics

- Reproduce the issue first when possible.
- Narrow root cause before patching symptoms.
- Add or update tests that would fail before the fix and pass after the fix.
- Verify no regressions in adjacent behavior.

## Review Checklist

- Correctness: Does the code satisfy the request and edge cases?
- Safety: Are failures handled and assumptions explicit?
- Compatibility: Are existing callers and contracts preserved?
- Maintainability: Is the solution understandable for future edits?
- Verification: Were relevant checks run and results reported?

## When Information Is Missing

- State assumptions explicitly and proceed with the safest reasonable default.
- If blocked by ambiguity that changes implementation direction, ask a focused clarifying question.
