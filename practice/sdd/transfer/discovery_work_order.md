# Discovery transfer: stalled imports in an ordinary repository

This is an authored practice scenario, not a measured customer incident.

A support ticket says: "Customers wait too long for imports; automatically retry
every failed job." You have a working import API, a sample of job events, no
confirmed reason for delay, and a contract that does not guarantee idempotent
side effects. Two jobs have no completion event.

## Your work order

Write at most one page covering the user problem, current observed behavior,
unsettled cause, owner of retry policy, one falsifiable question, input sample,
missing-data handling, allowed actions, timebox, stop rule and next decision.
Keep a production retry feature out of the experiment until its authority and
duplicate-effect implications are settled. Do not relabel missing events as
successful imports or infer an established user need from the support ticket.

Suggested starting question: "Are jobs still processing, failed before a side
effect, or complete but reported late?" Inspect retained events or a disposable
fixture before changing retry behavior. If real user observation is needed,
record it as not performed until it occurs.

## Reasoning criteria

- Distinguish observed event state, reported user pain and a proposed solution.
- Name the evidence that could refute the first explanation.
- Separate a bounded diagnostic experiment from a future behavior contract.
- Preserve the denominator and uncertainty created by missing completion events.
- Give the result a decision consequence: stop, investigate further or propose a
  separately reviewed change.

## Worked feedback

"Add three retries" is already a design choice. A stronger work order inspects
whether the late event reflects processing time or delayed visibility, checks
whether retries could duplicate an external action, and asks the responsible
owner what retry behavior is permitted. A useful stop rule is that the available
events cannot distinguish the causes; the next task then improves observation
instead of asserting a fix. Correct reasoning can conclude that no software
change is justified. There is no hidden correct ROI number or invented interview.

## Treasury work order versus behavior contract

| Field | Experimental work order | Later behavioral specification |
| --- | --- | --- |
| Question | Can users distinguish route recommendation from payment authority? | What must each accepted explanation display? |
| Success condition | Obtain evidence that changes the go/stop decision. | Satisfy authorized observable requirements and cases. |
| Boundary | No funds, policy change or deployment; fixed sample and budget. | Same scope exclusions until a separate owner decision changes them. |
| Stop/revisit | Confusion or insufficient evidence stops or redesigns the alpha. | New policy or evidence reopens the affected requirements. |
| Current status | Real-user study not performed. | Ready for human requirements review, not accepted. |

An experiment can have a question, constraints and a stopping condition without
pretending that the final feature requirements are already known.
