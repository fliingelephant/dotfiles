---
name: prompt-gpt-astra
description: Write or review prompts, instruction files and notes for GPT-6 Astra, so that they convey the user's goal and do not cause excessive self-criticism or over-reactions. Use when you write PROMPT.md or AGENTS.md for an Astra run, when you send a note to an Astra agent, or when an Astra run becomes defensive.
---

# Prompting GPT-6 Astra

## Basic principles

- Astra is too cautious and self-critical. Its answers are defensive: a simple
  conclusion comes with several "this does not mean …" lines.
- It is very sensitive to prompts. It over-reacts to them, and a small hint can
  steer its whole direction.
- It follows written instructions well. It is weak at understanding fuzzy
  intentions.
- So it reads a warning or an example as a rule. It then collapses early onto one
  direction.
- You act for the user. Convey the user's motivations to Astra in a form that fits
  these constraints, so that Astra uses its creativity.

Another major risk is the writer. You will underestimate how cautious Astra is,
and you will want to add checks, rules and ideas of your own. The user did not
ask for them, and each one makes Astra more cautious. Remove them before you
send any prompt or note.

Apply these principles when you write any prompt or note, before you send it.
The evidence for them is below: OpenAI's guidance, user reports, and our own
runs.

## How to write for it

Content:

- State the goal clearly, and encourage. Do not add constraints: Astra already
  constrains and criticizes itself.
- Write facts and permissions. Remove or reword any line that can cause
  self-defense.
- Do not prescribe an approach unless the user asks for one.
- Say when to run work in parallel. Authorize safe workflows, so that Astra does
  not stop to ask.
- Say that refining what works and trying new families at the same time are both
  valued. Otherwise Astra puts all its effort on the best direction.
- Define a broad term, such as "tensor network", by its principle: what the term
  means, and which properties of the problem fit it. Named examples of options to
  try tend to become the only options. Naming known methods as facts, such as
  baselines, is fine.
- With a proxy metric, the prompt must state the parts of the goal that the score
  cannot measure. Write this text from the user's own words, and agree on it with
  the user when they are present.

Wording:

- Do not write warnings.
- Do not add pass/fail bars for ideas, checks or required stops.
- For replacements of wording that caused problems, see the table below.

Instruction files:

- Audit every instruction file that Astra can read, including
  `~/.codex/AGENTS.md`. Conflicting instructions make it pause.

## Evidence

OpenAI guidance, checked 2026-11-02 ([guide](https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra.md), [blog](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)):

- It is more sensitive to instructions in context. Unclear or conflicting
  instructions can make it pause and block work.
- It already tests and checks itself. If you encourage this, it tests more than
  needed.
- Defensive wording and step-by-step plans overconstrain it.
- If a prompt requires a stop for review, it tends to stop early.
- It asks non-blocking questions, and it can delegate less than you want.

User reports, not verified ([#49705](https://github.com/openai/codex/issues/49705), [#42937](https://github.com/openai/codex/issues/42937), [#46700](https://github.com/openai/codex/issues/46700)):

- Goal substitution: it builds supporting work, rewrites the criteria around it,
  and then marks the goal complete. One report quotes it: "I substituted storage,
  replay, packaging, and tests for the hard part."
- Self-made rules: it keeps enforcing constraints that it invented.
- Loops: it reverts and rewrites its own work.

Our runs:

- A selector of known methods reached score 1.0, and then took the run's
  attention.
- Self-set thresholds, for example "6.8% improvement, below its declared gate."
- Skeptic checks on its own idea when no rule asked for them.
- 83 of 120 trial reports started with disclaimers such as "no novelty claim".
- A novelty check before building; it skipped known tools such as TDVP.
- Implement, fail a small test, discard.
- Hours of self-made checks before any full run.
- Files stayed uncommitted, and the GPU stayed idle while subagents waited for the
  lead.
- It obeyed personal rules in `~/.codex/AGENTS.md` that were written for
  interactive work.
- After one family worked, most trials that the agent chose refined that family.
  Example: the comb in FMO.

## Wording that caused problems

| Wording | Effect | Use instead |
|---|---|---|
| "genuinely new algorithms" | It treated novelty as a test to pass | "New ideas, including exotic ones, are welcome. Results decide novelty at the end." |
| "the bar to beat"; "not limited to TDVP" as a rule | It anchored on TEBD and avoided TDVP | A plain fact: "Known methods include, but are not limited to, TEBD, TDVP and Pauli propagation." |
| "a mere combination is not the goal" | Self-defense; the user rejected this line | Plain facts, no warning |
| "state exact scope" | Disclaimers in most reports | "The lead says what was found, in one to three plain sentences." |
| "claims are checked", "honestly", "do not trust" | Self-criticism | Remove |
| "twice as far as the best baseline", "not a published method" | Self-set thresholds | Remove |
| "speed matters at full size" | The user saw a risk of over-reaction | "The aim is an algorithm with better scaling." |
| "new way to build Lambda" | 37 of 69 trials took this approach | Name no approach |
| "studies the failure it targets" | Too many diagnostics | "Build early; diagnose when it helps the next step." |
| Any wording that sounds like a failed test | Self-criticism | "A failed first test is a normal step, not a verdict." |

## Notes

A note is a prompt too, so the same principles apply before you send it. There
are two kinds:

- A tip is a small suggestion that does not ask the agent to change its research,
  for example about commits or idle compute. Write it so that Astra reads it as a
  suggestion and not as a judgment of its work: praise real progress, give one
  measured fact, say what is already allowed, and leave the decision to the agent.
  Leave out any fact that reads as criticism of the trial.
- A correction tells the agent what the user cares about when the run goes
  against it, for example when the run games the score. State it as a fact about
  the user. Do not criticize the trial.

Tips that worked:

- "Great T067 holdout gain. Tip from me: your six hours of careful small checks
  have prepared T060, T063 and T065 well; a brave full three-case score, even a
  weak one, shows where they stand on L3." Full scores followed.
- "Tip from me: in my last 14-min sample the H100 had no job about 70% of the
  time. PROMPT.md lets each subagent test with the harness itself, and the bench
  lock keeps scores clean, so GPU runs need not wait for the lead." GPU jobs then
  ran about 75% of the time.
- "Small tip from me: about 100 files ... have sat uncommitted for over an hour;
  checkpoint commits per trial keep the history safe and readable." Clean commits
  followed.

A correction that was not tested, because the agent hit its usage limit minutes
later. It followed a selector of known methods: "I added one line to PROMPT.md on
what I care about: one general algorithm run the same way on every case."

## After a note

Read the agent's next steps. They show whether the wording worked. If a tip made
the agent criticize itself or give up good work, tell it at once that the tip was
only a suggestion and that the direction is its own, and improve the wording of
later notes. Example: "From the user: that was only context. Your direction is
yours. Keep going."
