# A proportionate first week

[Home](../README.md) · [Navigation](README.md) · [Lab guide](LAB_GUIDE.md)

First install the required tools and complete the source checks in [Getting started](GETTING_STARTED.md). That guide also gives the exact first-exercise commands. The sessions below are a learning outline, not a replacement for prerequisites or the chapter-by-chapter route.

The minimum workflow for a small bug has four steps: state the intended behavior,
make one bounded edit, check it against an expectation outside that edit, and
review the result and remaining uncertainty. Choose the cumulative Treasury route below, or the [independent CSV preview](EXPERIENCED_PREVIEW.md) if you want to apply the method first to a small orders API. The preview requires no completed Treasury work. Both routes distinguish a proposed candidate, observed evidence and the applicable acceptance decision.

1. **First session: one repair.** `python3 -B reader_start.py doctor`, then
   `python3 -B reader_start.py new 1 --destination ../esa_first_week_01` from the
   unmodified release. Continue in that copy. Use `show 1` for the reproducer,
   permitted edit and check command. Explain equality at EUR 5,000 before editing.
2. **Next session: make the work repeatable.** Begin with Chapter 2's workspace
   preparation, then its actual-event bridge and task/context/tool distinctions.
   Keep only the relevant repository rule and command. A tool
   integration is optional until the task needs external information.
3. **Then state and challenge one feature.** Use the Chapter 4 explanation
   contract and the Chapter 5 tradeoff question. An unresolved owner decision is
   recorded as pending. The cumulative worked route uses the direct adapter;
   ports is a valid separate design exploration, not a silently interchangeable
   input to the fixed downstream teaching plan.
4. **Transfer once.** Follow [the CSV preview](EXPERIENCED_PREVIEW.md). Implement CSV over
   the existing authorized row selection, retain the failure and inspect the
   independent checks. Compare valid alternatives using its rubric.
5. **Review and choose depth.** Explain what passed, what was actually executed,
   what remains a proposal and whether the next change needs additional control.

These are suggested sessions, not measured completion-time promises. Use the
chapter entry cards to resume at a later stage without replacing earlier work.

| Add this control | When the work makes it useful | Where |
|---|---|---|
| Discovery and explicit owner decision | The request is ambiguous, changes purpose or conflicts with policy. | Chapters 3–4 |
| Design comparison | Competing seams or tradeoffs affect a meaningful future change. | Chapter 5 |
| Versioned context | Several sources, pending decisions or sessions can disagree. | Chapter 6 |
| Orchestration | Independent work, dependencies, budgets or recovery exceed a single task. | Chapter 7 |
| Release and rollback | A reviewed artifact must become a reproducible operational candidate. | Chapter 10 |
| History and operations controls | Data persists, policy changes, retries or incidents affect earlier outcomes. | Chapters 11–12 |
| Team and outcome evaluation | Others depend on the practice or someone wants an adoption claim. | Chapters 13–14 |

After Part I, explain which source can authorize the change. After Part II,
defend a design and name what would reopen it. After Part III, identify the exact
candidate and one plausible missed fault. After Part IV, distinguish an observed
outcome from a proposed benefit. These reuse the chapters' existing questions;
the CSV capstone is the one added executable transfer.

### Optional: use the observed installed client

After understanding the Chapter 1 contract, follow [../practice/native_client/README.md](../practice/native_client/README.md)
for the installed OpenCode and local-model route. The guide records the actual
failures and recovery decisions. Use a fresh study copy and compare the returned
patch with the owner-side cases; a client finishing successfully is not proof
that the repair passed. This optional setup is separate from the core Python lab.

For the cross-chapter requirement trace and proportionality choices, use [the lifecycle map](LIFECYCLE_MAP.md). For your own authorized task, use the preview's five-line handoff and the [existing transfer exercises](../practice/production_controls/TRANSFER_EXERCISES.md). Written guidance and reference checks do not establish human learning or transfer.
