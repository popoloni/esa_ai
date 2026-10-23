# Follow one requirement through the software lifecycle

[Home](../README.md) · [Navigation](README.md) · [Lab guide](LAB_GUIDE.md)

Use this as a source map, not a mandatory document checklist. Start with the
phase your change needs. Commands run from the companion root; `python3 -B
reader_start.py show N` supplies the current chapter's candidate, reference,
scope and recovery commands. A reference check does not repair or accept your
candidate. All named business owners and decisions below are fictional fixtures.

| Phase and chapter | Input | Reviewable output and exact current source | Owner and stopping condition |
|---|---|---|---|
| Need, Ch3 | Operations testimony and existing policy | [Operations note](../reader_side/discovery/sources/SRC-OPS-004.json), [policy source](../reader_side/discovery/sources/SRC-POL-001.json), and [discovery handoff](../reader_side/specs/discovery_handoff.json) define an explanation experiment; benefit remains a hypothesis. | Product owner settles purpose; stop if the request and policy conflict. |
| Behavior, Ch4 | Discovery decision and unchanged router meaning | Repair [the candidate spec](../repo/engineering/specifications/explanation_alpha/specification.json); check against [the case oracle](../reader_side/specs/case_oracle.json) with [spec_gate.py](../reader_side/tools/spec_gate.py). [The worked spec](../reader_side/reference_solution/specification.json) keeps review pending. | Product and policy owners settle meaning; selected checks prepare requirements review. |
| Design, Ch5 | One behavior contract, two implementation options | Inspect [direct.py](../repo/src/treasury/architecture/direct.py), [ports.py](../repo/src/treasury/architecture/ports.py) and [ADR-005](../repo/engineering/architecture/ADR-005.md). | Technical owner chooses a design; stop before adopting an unaccepted proposal. |
| Task and handoff, Ch7 | Relevant sources, proposed design, separate pending reviews | Repair [delegation_plan.json](../repo/engineering/planning/delegation_plan.json) and [delegation_handoff.json](../repo/engineering/planning/delegation_handoff.json); use [planning_gate.py](../reader_side/tools/planning_gate.py). | Coordinator checks dependencies; product/technical/release owners retain their decisions. A correct plan can have blocked work. |
| Implementation, Ch8 | [Local work order](../reader_side/implementation/WORK_ORDER_CP08.md) | Repair [explanation_alpha.py](../repo/src/treasury/explanation_alpha.py) and [its report](../repo/engineering/implementation/implementation_report.json); use [implementation_gate.py](../reader_side/tools/implementation_gate.py) and the original scope baseline. | Maker produces a reviewable candidate; stop on scope drift, missing behavior or unresolved meaning. |
| Independent review, Ch9 | Actual patch and selected test observations | [Verification exercise](../reader_side/verification/readme.md), [verification_gate.py](../reader_side/tools/verification_gate.py) and [observed verification tools](../practice/verification_tools/README.md) distinguish a result from its explanation. | Reviewer evaluates the named candidate; unresolved findings stay visible. |
| Release, Ch10 | Reviewed source, artifact and applicable fictional decision | [Release guide](../guides/README_CP10.md), [rehearse_release.py](../reader_side/tools/rehearse_release.py) and [release_gate.py](../reader_side/tools/release_gate.py) bind a local rehearsal to an actual candidate. | Release owner decides for that source. Technical learning completion for another correct patch is separate from the fixed decision. |
| Later change, Ch11 | [Versioned work order](../reader_side/evolution/WORK_ORDER_CP11.md) and retained decisions | [Policy catalogue](../reader_side/evolution/policy_catalog.json), [policy delta](../repo/engineering/evolution/policy_delta.json), [policy_history.py](../repo/src/treasury/policy_history.py) and [evolution_gate.py](../reader_side/tools/evolution_gate.py) connect new behavior to persistent history. | Policy and operations owners settle the change; stop on ambiguous historical provenance or failed migration/retry checks. |

## Trace REQ-EXPL-004 without changing its meaning

1. The policy source and `BR-001/v1` define the version returned by the original
   router. `REQ-EXPL-004` in the worked specification says to display the version
   from the routing decision and not invent a newer one.
2. The [worked plan](../reader_side/reference_solution/v2/delegation_plan.json)
   carries `SPEC-004/v1` through investigation T07-01 and the blocked implementation
   dependency. Its [handoff](../reader_side/reference_solution/v2/delegation_handoff.json)
   preserves the missing requirements and architecture decisions. It does not
   report those tasks as executed.
3. The Chapter 8 work order separately permits the presentation repair. Its
   independent check rejects an invented version. The candidate report identifies
   what was actually checked; it is a handoff for review.
4. The [accepted teaching continuation](../practice/lifecycle/README.md) supplies
   separately authored fictional decisions and [a revised plan](../practice/lifecycle/teaching_plan.json).
   It connects that actual repair to the operator view, a local artifact rehearsal
   and later operations. It preserves the earlier blocked plan instead of rewriting
   it as approved. A recorded local release concerns its identified source only.
5. Chapter 11 retains a `legacy_4000` decision under v1 while making v2 available
   for new work. EUR 4,000 routes to the standard queue under the EUR 5,000 v1
   threshold, but to human review under the EUR 3,000 v2 threshold. Reusing the
   same request key preserves the stored v1 result. A separately identified new
   evaluation can use v2. The [complete legacy fixture](../reader_side/evolution/legacy_complete.json)
   and [case oracle](../reader_side/evolution/case_oracle.json) make the difference
   inspectable. An old receipt remains evidence about its old input.

## Choose the minimum useful process

| Change | Keep | Omit until a concrete need appears |
|---|---|---|
| Small repair | Short intent, reproducer, bounded patch, selected checks and review | Full PRD, architecture comparison and parallel-agent graph |
| Small feature | Concise behavior contract, consumer/compatibility decision, selected cases and handoff | A new service or approval framework merely to organize one formatter |
| Stateful or externally acting change | Stable identity, versioned policy, retry/migration/recovery observations and accountable operational decision | Claims that local tests prove every remote side effect or production condition |

Maintain one entry point to the currently applicable contract. Keep old contract
versions, raw attempts and receipts immutable. After a contract, source or runtime
changes, identify the dependent checks and create fresh evidence for that new
state. A live pointer and an old receipt have different jobs. The [recovery guide](RECOVERY.md)
explains how to retain the earlier result when it becomes stale for a new task.
