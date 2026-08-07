---
name: rlhf
description: Use when composing a reusable artifact — a skill, template, prompt, recurring format — whose open questions are the user's taste, intent, or needs rather than anything machine-checkable; or when editing one and the signals say it matters: the user shows they care and you feel real uncertainty, or the user already rejected a version once — or whenever the user explicitly calls a round on an artifact they deem important.
---

# RLHF

## Two Kinds of Uncertainty

Verifiable — the math, the numerics, does-it-run — machines settle alone:
check it yourself or with agents, and save human attention for what only the
user can judge. The user's taste, intents, needs — no verifier exists for
these. Left to you and your subagents, a reusable artifact converges to
something self-consistent and weird, and its wrongness compounds with every
future use.

The only ground truth is the user's felt preference: humans feel *which is
better* far more reliably than they can specify *what I want*.

## The Round

A round starts two ways. You start one yourself — no request needed — whenever
you are about to finalize anything reusable that carries the user's taste,
intents, or needs — a skill, a template, a recurring report format, a prompt,
a style rule. The user calls one explicitly on anything they deem important —
a figure, a note, a one-off that matters.

When composing, run the two-question test before you finalize: Does the open
question sit in the user's taste, intents, or needs? Does the artifact affect
much — reused, compounding? Two yes answers mean bring a pair. When editing,
also read the signals: the user shows they care and you feel real
uncertainty, or the user already rejected a version once — any of these
means bring a pair, not a direct edit — even for one sentence, even to fold
the user's markup.

Bring a pair: two real versions, of the artifact itself or of outputs produced
under it, contrasting on an axis that matters. The deeper the axis, the more
the round is worth: the understanding of the user's intent (two readings of
what they actually want), then the logic (two ways it could work), ahead of
the surface — voice, structure, strictness. Never two paraphrases. Show both
exactly as the user will meet them — text verbatim, figures rendered. When the
artifact is long, show only the differing passages with a line of context,
visually anchored so the eye finds the diff — never point at content the user
cannot see. Name the differing axes in one line; advocate for neither. The
user picks one, rejects both, or marks up — fold it back. After a fold, show
the updated part at candidate size — never the whole file — for confirm. Then
loop: to the next part that needs a round, or the same part again if the user
is unsatisfied. One pair per round; a rejection's reason seeds the next pair.
Done when every part stands accepted without markup.

Everything shown to the user — candidates, diffs, axes, folds — follows
ASD-STE100 Simplified Technical English: short sentences, active voice, one
meaning per word. Use the user's own vocabulary, or standard terms defined at
first use — never invented labels.

## Out of Scope

One-off, low-stakes outputs: just make them. A user-called round outranks
this line.
