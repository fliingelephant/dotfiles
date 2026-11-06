---
name: propose-benchmark
description: Propose benchmarks for a research goal, with a short reason for each choice, so that the user can decide. Load it when a research workflow needs benchmarks chosen, usually after the knowledge base exists and before the harness is built; when a benchmark stops working during a run; or when the user asks to choose or check a benchmark.
---

# Propose Benchmark

## Why this skill exists

A benchmark decides what a research run optimizes. If it measures the goal
poorly, a run can improve its score and still miss the goal. Most problems come
from details, not from the choice of topic.

Another major risk is the proposer. You will want to add benchmarks and checks
against hacks that the user did not ask for. Each one slows feedback and makes a
cautious agent more defensive.

## Who decides

You propose. The user decides, unless the user has explicitly delegated the
decision. Give each choice a short, self-contained reason with sources, so that
the user can decide without reading anything else.

Example: "FMO has been the standard test for open quantum systems since Engel et
al. 2007 and Ishizaki and Fleming 2009."

## 1. Align with the user

Find out whether the goal is exact or fuzzy. This decides whether a metric can be
direct or must be a proxy.

**Exact goal.** A benchmark can be the goal itself, so its metric can be direct.
A few benchmarks, or one, can be enough. Step 3 can still call for more than one
benchmark, and for care with the reference and the setup. Example: "simulate
7-site FMO for longer times at the same accuracy".

**Fuzzy goal.** No single benchmark can measure it, so the metrics are proxies.
Example: "generic algorithms for the Lindblad or Redfield equation", where an
exactly solvable case can be one of the benchmarks.

- Choose the smallest set of trusted and valuable benchmarks that conveys the
  goal best, each with its own reason. A small set keeps each round of tests
  fast. Each extra benchmark slows every round and makes a cautious agent more
  defensive. A holdout is a benchmark too: keep it when it is valuable and
  trusted.
- Think of the set as a small sample of the problems the goal is about. Add a
  benchmark only when, without it, the sample would be strongly biased, for
  example toward special cases that a method could fit. Example: one
  free-fermion solvable case alone is strongly biased. Adding a case solvable by
  the Bethe ansatz makes the sample much less biased, while it stays quick to
  test. The actual cases come from the goal and the knowledge base.
- A loose first set is fine; tune it later, when the run shows a bias.
- State in words the parts of the goal that no metric measures.

## 2. Choose benchmarks

Start from the knowledge base, for example `.knowledge/`, then search for recent
work. Prefer benchmarks that are:

- **Recognized:** the field uses it as a standard, or recent great methodology
  work uses it. Then results can be compared and matter to the field.
- **Not a toy:** current methods find it hard, so there is room to improve.
- **Backed by a trusted reference:** a strong source gives a reference result
  that fits the goal. For a goal about solving a model, use exact or converged
  results of the same model. For a goal about predicting nature, use experiment.
  A physical system in a benchmark is usually a model, which matches nature only
  roughly.
- **Feasible:** one test fits the available compute and time, often enough to
  give feedback. Shorter is better. State the estimated time of one test on a
  certain device, for example "about 40 minutes on one H100".
- **Reproducible:** the model parameters and reference data are public, so the
  case can be rebuilt exactly.

Examples: FMO in open quantum systems; Fe-S clusters in quantum chemistry.

## 3. Set the details

The details decide whether the benchmark works. Derive them from these
principles:

- **Faithful:** the score measures what the goal says. All methods solve the
  same model under the same conditions. A smaller or shorter version keeps the
  property that matters at the size of the goal.
- **Trusted reference:** the reference error is much smaller than the
  differences that the score must detect, over the whole scored range. Check it
  with the reference's own convergence data or with an independent method.
  Approximations that all reference runs share do not show in their
  differences.
- **Discriminating:** the score keeps separating the best methods. It leaves room
  above the best method. The baselines include the strongest known methods and
  their recent advanced variants, found by a search and tuned. Example: for
  Lindblad simulation, TEBD, TDVP and Pauli propagation are baselines, and GSE-
  and CBE-TDVP are advanced variants of TDVP; TEBD alone would be too weak.
- **Feasible:** as in step 2.

Each constraint added for scoring, such as an error limit, a cost budget, an end
time or a cost measure, needs a stated reason.

If one benchmark cannot meet all principles, use more than one, and state the
role of each and the reason for it.

Examples from FMO:

- A 2-site case gave fast feedback, and a 7-site case ranked methods at the size
  of the goal.
- The reference DAMPF runs used an approximate bath. Whether every method should
  use that bath or the exact one is a choice to consider: the same bath keeps
  errors comparable with the reference, and the exact bath is closer to the real
  system but needs its own reference.
- The 2-site score reached its cap, so it stopped separating methods.
- Two 7-site reference runs differed by half the error limit near 180 fs, so the
  test could not judge later times.
- Both reference runs used the same number of levels per mode, so an error from
  that cut could not show in their difference.
- The error limit had no recorded reason.

## Output

Give the user each choice and its reason, enough to decide, in a form that fits
the case.

## With other skills

- `monitor-autoresearch`: put the reasons, and what the score cannot show, into
  the run's charter. When the monitor sees a benchmark stop working, it loads
  this skill again.
- If the research agents are Astra, read `prompt-gpt-astra` before you make these
  choices.
- `prompt-gpt-astra`: when a prompt for Astra describes the benchmark, use that
  skill for the wording: plain facts and reasons, no warnings.
