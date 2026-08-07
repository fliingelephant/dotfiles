---
name: align-intents
description: Use when the user invokes /align-intents or opens a session with a noisy braindump — mixed background, pasted context, links, and half-formed asks — before any work starts.
---

# Align Intents

## Overview

Human attention is valuable. The user opened with noisy context — background, links, random thoughts around a real goal. Mirror back the essential intent so they can correct it cheaply, before any work spends their attention or tokens. Everything this skill writes follows ASD-STE100 Simplified Technical English: short sentences, active voice, one meaning per word. Use the user's own vocabulary, or standard terms defined at first use — never process jargon or invented labels. Skip only when the message is already one clear action.

## The Reply Contract

Your first message is the alignment statement. Before writing it, really navigate what the user handed you — open the links, read the files, walk the repo; an intent mirrored without that is faked from their words. Two resources are valuable: the user's attention and their time. Simple navigation costs neither — read freely, as any agent would. The gate sits before heavy work: long runs, heavy code, anything that costs money — servers, cluster time, paid APIs — any modification, anything that would land a wall of output on the user. Those wait until intents are aligned. It has exactly these parts, in order, and fits on one screen — shorter is better:

**Intent** — up to 3 sentences stating the goal behind the words: the outcome the user actually wants, not a paraphrase of what they typed.

**Plan** — 2–5 numbered lines of concrete actions, in execution order.

**Output** — one line naming the deliverable's shape (table, doc, patch, report). Only when the shape isn't already obvious from the plan.

**Noticed** — only when navigation contradicted the braindump: one short, anchored warning that states the consequence — what it changes for the plan. Skip it otherwise.

**Closing question** — one line carrying your most genuine uncertainty: the point where a wrong guess would most change the plan. If nothing is uncertain, ask for confirmation to proceed.

Then stop and end the turn. Work begins after the user confirms or corrects; after a correction, restate the corrected intent in one line and proceed.

## Example

User braindump (compressed): *repo-design notes pasted; "read PR #152 — a challenge PR that also contributes project-wise knowledge. I wanna scan all PRs with dynamic workflow and summarize: some are challenge runs, some fix primitives, some contribute design. Raise simple points, then discuss with me."*

> **Intent** — You want to see what community PRs teach the harness, sorted three ways: challenge runs, primitive fixes, and design contributions like PR #152's project-wise knowledge — so the lessons feed back into the design. I read #152: +40k lines, 100 files, zero harness files touched — its design ideas live only in its in-track prose docs; open PRs number 92 today. Points first; the scan waits for our discussion.
>
> **Plan**
> 1. Draft 3–5 simple points from #152 — e.g., file paths alone miss prose-only design contributions.
> 2. Settle the points and the scan fan-out with you.
> 3. After sign-off: run the workflow scan and summarize.
>
> **Output** — one line per PR (kind + takeaway) plus a to-adopt shortlist.
>
> **Noticed** — the decoupling block you pasted shows two `.knowledge/` dirs: `models/` and `methods/`. The repo has four more: `physics/`, `literature/`, `software/`, `solvable/`. A scan built only on that block will mislabel the PRs that touch these four.
>
> Sharpest unknown: "all PRs" — the 92 open only, or merged and closed too? That sets the scan's size.
