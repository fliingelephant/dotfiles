# Personal Claude Code Preferences

## Collaboration

- **Discuss before editing.** When reviewing PR comments or issues, first understand the essential semantics — what can vs cannot change, what the design actually requires — before proposing any fix. Do not edit until alignment is reached.
- **First principles only.** No legacy considerations, code fallbacks, or patch-style fixes. Understand the essential nature of the problem, then apply the most clean, simple, and logistically canonical fix. This applies to automated reviewer suggestions too — evaluate whether the current behavior is correct by design before treating a suggestion as a bug.
- **Human in the loop.** Implementation might be incorrect. For uncertain behavior, refer to notes or ask the user rather than guessing. When in doubt, ask.

## Design Philosophy

- **Efficiency is top priority.** Never sacrifice efficiency or write a temporary version. At equivalent efficiency, target the most slim, clean, and decoupled implementation.
- **Let it crash.** No defensive parameter checks at internal boundaries. Validate only at system boundaries (user input, external APIs).
- **No helpers.** Minimize helper functions. Inline short logic; only extract when reused 3+ times.
- **Julia-style defaults.** `def foo(x, y=10):` not `def foo(x, y=None): y = y or 10`.
- **No trivial TDD.** Do not use TDD for example scripts, demos, or one-off experiments. TDD is for library/framework code where correctness matters and regressions are costly. Writing tests for example scripts is useless overhead.

## Workflow

- **Run `/simplify` before feature-dev or refactor commits.** Skip for bug-fix commits. Code slimness is a top priority.
- **Subagents match the main agent.** When launching subagents or review agents, use the same model id, reasoning/effort level, service tier, sandbox, approval policy, and tool-access settings as the main agent. Rely on default inheritance only when it preserves an exact match; otherwise pass the matching values explicitly. Do not downgrade to smaller, cheaper, lower-effort, or differently configured agents unless the user explicitly asks.

<!-- context7 -->
Use the `ctx7` CLI to fetch current documentation whenever the user asks about a library, framework, SDK, API, CLI tool, or cloud service -- even well-known ones like React, Next.js, Prisma, Express, Tailwind, Django, or Spring Boot. This includes API syntax, configuration, version migration, library-specific debugging, setup instructions, and CLI tool usage. Use even when you think you know the answer -- your training data may not reflect recent changes. Prefer this over web search for library docs.

Do not use for: refactoring, writing scripts from scratch, debugging business logic, code review, or general programming concepts.

## Steps

1. Resolve library: `npx ctx7@latest library <name> "<user's question>"` — use the official library name with proper punctuation (e.g., "Next.js" not "nextjs", "Customer.io" not "customerio", "Three.js" not "threejs")
2. Pick the best match (ID format: `/org/project`) by: exact name match, description relevance, code snippet count, source reputation (High/Medium preferred), and benchmark score (higher is better). If results don't look right, try alternate names or queries (e.g., "next.js" not "nextjs", or rephrase the question)
3. Fetch docs: `npx ctx7@latest docs <libraryId> "<user's question>"`
4. Answer using the fetched documentation

You MUST call `library` first to get a valid ID unless the user provides one directly in `/org/project` format. Use the user's full question as the query -- specific and detailed queries return better results than vague single words. Do not run more than 3 commands per question. Do not include sensitive information (API keys, passwords, credentials) in queries.

For version-specific docs, use `/org/project/version` from the `library` output (e.g., `/vercel/next.js/v14.3.0`).

If a command fails with a quota error, inform the user and suggest `npx ctx7@latest login` or setting `CONTEXT7_API_KEY` env var for higher limits. Do not silently fall back to training data.
Run Context7 CLI requests outside Codex's default sandbox. If a Context7 CLI command fails with DNS or network errors such as ENOTFOUND, host resolution failures, or fetch failed, rerun it outside the sandbox instead of retrying inside the sandbox.
<!-- context7 -->
