# EDOD work orders and reached verification stages

`schema.json` defines EDOD work-order version 1. `registry.json` holds 12
chapter cases and eight missions; `generate.py` emits complete, independently
validatable JSON files in `orders/` and the concise mission text in `printed/`.
The authored contracts are teaching specifications, not execution receipts or
observed owner approvals. A work order names the authority, its version, the
candidate scope, an operational budget and the decision that remains with its
owner.

From the extracted package root:

```bash
python3 companion/workorders/validate.py --all --output work/evidence/workorders-validation.json
```

The standard-library validator checks the keywords used by the shipped JSON
Schema, plus consistency between editable/protected paths and command/review
checks. It is not a general validator for arbitrary JSON Schema documents.
A valid shape does not establish that a contract is approved or its scope is
adequate. Review those claims against the named source. Chapter orders use
explicit manual checks where the chapter asks for a specification, analysis or
plan; an empty command array then means no shell execution is asserted.

## Profiles follow the consequence

| Value | Reader name | Minimum decision evidence |
|---|---|---|
| `investigation` | Investigation | Question or decision to resolve, bounded inquiry or plan, observations and limits; the investigation or plan owner decides the next action. |
| `bounded_repair` | Bounded repair | Reproducer, scoped diff, valid control and regression; the implementation reviewer decides. |
| `new_capability` | New capability | Approved behavior, independent acceptance examples and a consumer check; the capability owner decides. |
| `persistent_effect` | Persistent effect | Applicable evidence above plus retained-state/history, artifact or recovery controls; the relevant data/release owner decides. |

Chapters 2, 6 and 12 use Investigation: they decide an inquiry, a plan or a reader trial, without claiming a delivered capability.

These are evidence profiles, distinct from an autonomy classification. G1
creates a new capability in a disposable fixture. G2 preserves existing G1
history and therefore uses Persistent effect. The presence of SQLite does not
choose a profile. B1's initial repair uses Bounded repair; the explicit B1 v2
grammar extension is New capability and keeps its separate owner decision.

Attempt and implementation-minute values are **declared teaching budgets**.
They are not measured completion times or automatically enforced by schema
validation. The local runner enforces a timeout per check process; an entire
session can contain several such processes. `max_external_calls=0` applies to
the candidate integration, whose providers are local fixtures. It does not
prohibit the live coding-agent operation used by the primary practice route. B2's separate
per-item/global provider invocation limits remain part of INTAKE/v1.

## Progress is derived from observations

Current `check`, `continue` and individual proposal results add
`verification_progress`. Batch receipts retain that field in each nested
result. `progress.py` interprets existing fields; it executes no extra test.
The source-field digest excludes only the added progress object and allows the
interpretation to be reproduced. Existing raw receipts are not rewritten.

| Stage | Evidence used | Meaning and stopping boundary |
|---|---|---|
| `startup` | Receipt schema, mission and accepted entry identity | The intended runner reached its check path. Candidate import is separate. A pre-entry refusal can produce no receipt. |
| `integrity` | Protected-input comparisons and candidate-retention fields | A changed/missing protected input blocks tests. A later change remains a failure even when some checks already ran. |
| `contract` | Named groups and contract-specific supplemental probes | The selected observation passed or failed. `behavior_reached` is separate: an import placeholder is not a candidate assertion; incomplete output may be unknown. |
| `integration` | Present continuation, consumer or process-boundary observations | The retained candidate was exercised in that local composition. Contract/integrity failure does not start the normal continuation. |
| `artifact` | Separate artifact/extraction gate, when supplied | Mission-local receipt and demonstration hashes alone do not prove release fitness; these receipts leave the stage NOT_RUN. |
| `authorization` | A decision by the responsible owner on the identified object | Tests and the teaching answer key do not supply it. Current mission receipts leave it NOT_RUN. |

PASS and FAIL require actual recorded evidence. NOT_RUN means no observation
for that stage is present. NOT_APPLICABLE requires an explicit scope exclusion
by the work order; missing evidence alone never supplies one. Multiple groups
within the contract stage may collect diagnostic failures before the stage
stops later continuation. The progress record is an interpretation of the
receipt, not an independent attestation of its truth.

## Diagnostic controls

The workbook's two tables are backed by constructed cases in `verify.py`:
G1 missing-owner entry refusal; starter `NotImplementedError`; slice-versus-
final scope; protected-input stop without module import; B1 boundary failure
versus `_FailedTest`; B2 wrong API predecessor and budgeted DEFERRED outcome;
B3 missing-provenance refusal with a valid-provenance control; B4 known
WRONG_LEDGER diagnosis; and refusal to overwrite an earlier receipt.

The same verifier challenges the work-order schema with missing authority,
wrong profiles, empty acceptance, impossible/boolean budgets, unexpected
approval fields and conflicting path scopes. Its observations are local
fixture executions: no human participant, human agreement score, model
frequency or measured completion time is inferred.
