# Personal Claude Code Preferences

## Collaboration

- **Discuss before editing.** When reviewing PR comments or issues, first understand the essential semantics — what can vs cannot change, what the design actually requires — before proposing any fix. Do not edit until alignment is reached.
- **First principles only.** No legacy considerations, code fallbacks, or patch-style fixes. Understand the essential nature of the problem, then apply the most clean, simple, and logistically canonical fix. This applies to automated reviewer suggestions too — evaluate whether the current behavior is correct by design before treating a suggestion as a bug.

## Design Philosophy

- **Efficiency is top priority.** Never sacrifice efficiency or write a temporary version. At equivalent efficiency, target the most slim, clean, and decoupled implementation.
- **Let it crash.** No defensive parameter checks at internal boundaries. Validate only at system boundaries (user input, external APIs).
- **No helpers.** Minimize helper functions. Inline short logic; only extract when reused 3+ times.
- **Julia-style defaults.** `def foo(x, y=10):` not `def foo(x, y=None): y = y or 10`.
