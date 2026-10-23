# Treasury teaching repository — integrated Chapters 1–14

This synthetic exercise routes requests to queues. It never approves payments
or moves funds. The inherited routing API remains BR-001/v1 with the EUR 5,000 boundary. Chapter 11 adds a separately versioned policy-history teaching experiment.
The reader-controlled intent, source catalogue, specification, reference
solutions, test oracles, scope baselines and checks are outside this repo.

## Select the exercise before editing

The combined laboratory supports several exercises. Its cumulative inventory
is not permission to edit every candidate at once. Select the chapter's scope
profile and capture a reader-owned baseline before making its changes.

| Chapter | Candidate paths relative to this repo |
| --- | --- |
| 1–2 | `src/treasury/routing.py` in the original routing/workspace exercise |
| 3 | `engineering/discovery/assessment.json` |
| 4 | `engineering/specifications/explanation_alpha/specification.json` |
| 5 | `src/treasury/architecture/direct.py`, `src/treasury/architecture/ports.py`, `engineering/architecture/architecture_decision.json`, `engineering/architecture/ADR-005.md` |
| 6 | `engineering/knowledge/context_packet.json`, `.agents/skills/context-audit/SKILL.md` |
| 7 | `engineering/planning/delegation_plan.json`, `engineering/planning/delegation_handoff.json` |
| 8 | `src/treasury/explanation_alpha.py`, `engineering/implementation/implementation_report.json` |
| 9 | `engineering/verification/candidate.py`, `engineering/verification/review.json` |
| 10 | `engineering/release/release_dossier.json` |
| 11 | `src/treasury/policy_history.py`, `engineering/evolution/policy_delta.json` |
| 12 | `engineering/operations/deployment.json`, `engineering/operations/incident_review.json` |
| 13 | `engineering/learning/transfer_review.json`, `engineering/learning/team_knowledge.json` |
| 14 | `engineering/measurement/outcome_review.json`, `engineering/measurement/tool_decision.json` |

Keep source catalogues, claim dependencies, reader-side specifications, tests,
reference solutions, manifests and baselines under reader/CI control. Do not
rewrite an oracle or rebaseline after an unauthorized change to make it pass.
Check actual before/after edits with the selected chapter baseline. Task advice
is not process isolation: enforce real restrictions outside candidate control.

## Planning and teaching experiments

PLAN-007/v1 keeps the architectural decision T07-03 pending and the proposed
implementation T07-04 blocked. Its protected reference does not claim any live
agent execution or human acceptance. Do not mark these tasks complete because
later classroom checks pass.

Chapter 8 has a separate local experiment work order at
`../reader_side/implementation/WORK_ORDER_CP08.md`. It concerns a different
presentation wrapper and only the two CP08 paths. It does not authorize the
blocked CP07 edit of `architecture/direct.py`, accept ADR-005, approve a payment,
or permit merge or release. Chapter 9 supplies independent verification of
known teaching examples and the actual Chapter 8 output.

Chapter 10 reviews this presentation experiment using a disposable local Git
rehearsal, exact artifact identities and explicitly synthetic owner records.
Only the release dossier is editable in CP10. Do not change reviewer identities,
decisions, mandatory discussion threads, checks, earlier source or artifact
bytes to turn a rejection into a pass. A recorded local authorization is limited
to this classroom experiment; CP07 remains blocked and real release authority
remains false. Source changes require the relevant earlier exercise and fresh
evidence and owner decisions for that exact candidate.

## Checks and handoff

From the companion root, use `python3 reader_side/tools/run_checks.py` for the
shared regression suite. `python3 reader_side/tools/integration_gate.py`
checks the current cumulative candidate workflow; `--reference` checks the
protected worked example. Preserve unresolved questions and stop at
`PASS_REVIEW_GATE_ONLY` / `READY_FOR_HUMAN_REVIEW_NOT_ACCEPTED`.

For Chapter 10, use `rehearse_release.py` and `release_gate.py` as described in
`../guides/README_CP10.md`. The shared runner's `--release-rehearsal DIR` option evaluates
the current release dossier; `--require-release` also requires the current
CP01–CP09 candidates to pass. Without rehearsal evidence CP10 readiness is
reported as `NOT_RUN`; a passing regression suite supplies no release decision.

No production credentials, network writes, deployment or additional package
installation is needed for this standard-library offline laboratory. Chapter 10
also uses the local Git executable; no remote repository or deployment service
is contacted.

## Chapter 11 persistence boundary

The protected ../reader_side/evolution/WORK_ORDER_CP11.md authorizes only the two
CP11 paths. Retain the original router and all v1 history; add versioned policy
selection, persistent request identity and explicit historical recomputation.
Do not infer missing legacy policy evidence or erase records on retry. Keep
SQLite data and receipts outside source, under reader control. See
../guides/README_CP11.md for the narrower new payload contract, owner-bound synthetic
legacy fixtures and fresh-output gate commands. --require-evolution checks
current CP11 readiness separately from any CP10 presentation-release decision.
No earlier blocked task or real payment/release authority is granted.

## Chapter 12 incident boundary

The protected ../reader_side/operations/WORK_ORDER_CP12.md authorizes only the
two CP12 paths. Keep the router and CP11 history implementation unchanged.
Investigate the selected SQLite state using actual local process evidence;
preserve the control and incident ledgers and do not silently initialize a
replacement during recovery. Gate probes use new copies. Incident-only rows
remain quarantined pending owner reconciliation; local restoration is not
incident closure or production rollout. See ../guides/README_CP12.md for the current
and protected-reference modes. --require-operations requires current CP01–09,
CP11 and CP12 readiness and a current incident session; it does not imply any
CP10 release acceptance or real operational authority.

## Chapter 13 learning and governance boundary

The protected ../reader_side/learning/WORK_ORDER_CP13.md authorizes only the two
CP13 JSON candidates. Reuse actual CP12 evidence and the unchanged PolicyStore
for the different active-policy transfer case. Keep rubrics, protocol, raw
human explanations, independent reviewer records, owner clocks and keys outside
candidate control. Synthetic clock/rater fixtures test the harness only. They
do not establish human retention, transfer, rubric validity or competence.
Seal delayed retention before releasing transfer material; keep both raw scores
and any later adjudication distinct. Knowledge claims are owned, versioned and
invalidated with their dependencies. --require-learning requires the current
prior candidate workflow and CP13 protocol review, never human competence,
incident reconciliation, production recovery or delegated release authority.

## Chapter 14 measurement and tool-decision boundary

The protected ../reader_side/measurement/WORK_ORDER_CP14.md authorizes only the
two CP14 JSON candidates. Observe actual local CP13 commands on disposable
copies and retain every attempt, including rejection, repair, repeated green,
stale evidence and refresh. Distinct accepted work items require applicable
owner records; repeated passes are not new outcomes. Local elapsed time is not
human effort, and missing hours/billing/real acceptance remain UNKNOWN.
Protected synthetic costs and owner acceptance illustrate a proposed pilot,
not measured ROI or an empirical tool winner. --require-measurement requires
the current prior workflow and the same nominated CP12/CP13 evidence, while
CP10 release stays separate. CP07, reconciliation, human-learning validation,
pilot approval, procurement and real release authority remain unresolved.
