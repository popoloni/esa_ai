# An observed AI critic on five teaching cases

This exercise retains one actual ChatGPT collaboration-agent review of five independent Python snippets. Three snippets contain a declared contract defect; two are clean controls within the supplied contract. The exercise makes a useful review concrete: identify the obligation, locate the defect, and show an input whose actual result differs from the required result.

## Try the review before reading the answers

1. Read `input/CONTRACT.md`, then review `input/C01.py` through `input/C05.py` independently. They are separate examples, not components of one application.
2. For each finding, record the source location, a discriminating input, the observed or predicted result, and the required result. A clean case should remain unflagged unless you can justify a contract defect.
3. Save your first review before opening `REFERENCE_SEALED_BEFORE_CRITIC.json` or `observed/critic_01/RESULTS.json`. Compare both detected defects and false alarms. Do not change your original output to match the reference.
4. Inspect the retained critic's raw response and execution observations. Decide which evidence supports each finding and which inputs remain unexplored. A confident assertion alone is not an execution observation.

## What the retained attempt found

| Case | Predeclared expectation | First-output result |
| --- | --- | --- |
| C01 | Equality at EUR 5,000 requires human review | Identified the incorrect standard-queue branch at equality |
| C02 | Clean control | No contract defect reported |
| C03 | Queue placement must not authorize payment | Identified the incorrect `payment_authorized=true` result |
| C04 | Clean control | No contract defect reported |
| C05 | Preserve the supplied policy version | Identified a v2 decision relabeled as v1 |

The case-level account records **3 true hits, 0 missed seeded issues, 0 false alarms, and 2 correctly unflagged clean controls**. All six input hashes, including the contract, still match the separately prepared reference. The critic executed 34 selected snippet observations. Zero misses is the observed result for these cases; the account does not manufacture an unsuccessful case.

## Follow the evidence

| Record | Purpose |
| --- | --- |
| `REFERENCE_SEALED_BEFORE_CRITIC.json` | Expectations and input hashes prepared before the critic output |
| `observed/critic_01/TASK.txt` and `PROMPT.txt` | Task and retained instructions |
| `observed/critic_01/REVIEW.json` and `RAW_RESPONSE.md` | First review, preserved without hindsight correction |
| `observed/critic_01/EXECUTION_OBSERVATIONS.json` | Selected inputs and actual local results |
| `observed/critic_01/SETTINGS.json` and `ACTION_JOURNAL.md` | Interface, available settings, timing and recorded actions |
| `observed/critic_01/RESULTS.json` | Editorial comparison with the reference, case-level scoring and source hashes |

The critic received the task, contract and snippets in a separate context. Its recorded actions do not read the reference. This was instruction-based separation in a shared filesystem, not enforced access isolation or independent human adjudication. The reference and later scoring were prepared by editorial AI agents. Their agreement does not replace an accountable human review.

The retained interval between explicit local clock readings is 102.522337 seconds. It starts after the initial task read and ends before the settings and journal were written, so it is not the complete session duration or active model time. “GPT-6 Astra Pro” is the instruction-supplied label; the exact runtime model ID, sampling settings, provider usage and monetary cost were unavailable. The reviewer's “high” confidence is self-report, not a calibrated probability.

Use this five-case attempt to learn how to inspect findings and clean controls. It supplies no model ranking, population precision or recall estimate, exhaustive correctness claim, or human acceptance of the snippets.
