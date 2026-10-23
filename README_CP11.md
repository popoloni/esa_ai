# Chapter 11 — Change an existing system without erasing its history

This chapter extends the same Treasury laboratory with a persistent SQLite
teaching exercise. It retains BR-001/v1 at EUR 5,000 and adds BR-001/v2 at EUR
3,000. Strictly below the selected threshold routes to STANDARD_QUEUE; equality
and above route to HUMAN_REVIEW. Both are queue recommendations, never payment
approvals. The inherited routing.py, assess() API, original oracle and earlier
test expectations remain unchanged.

Use Python's standard library. No database server, account, credentials or
network is needed. Run the commands below from the companion directory.
SQLite files and their evidence belong under reader_side/evidence or in a new
reader-owned directory outside the source tree.

## The change and its authority

The protected WORK_ORDER_CP11.md in reader_side/evolution authorizes only
CP11-POLICY-001, a local synthetic policy-evolution experiment. The protected
change_context.json retains CP11-RETAINED-V1 and its original SRC-POL-001
source, the underspecified REQ-11-INITIAL, and the later
INT-11-RETRY-CLARIFICATION. These are explicitly author-created teaching
records, not evidence of a real stakeholder conversation.

Only these two paths are editable in the CP11 exercise:

| Path relative to companion | Purpose |
| --- | --- |
| repo/src/treasury/policy_history.py | Version selection, durable history, retries and migration |
| repo/engineering/evolution/policy_delta.json | Explicit semantics and limits of the policy change |

The catalog, oracles, tools, protected good/faulty examples, earlier source,
scope baseline and observed database files stay under reader control. CP07's
T07-03 remains PENDING_HUMAN and T07-04 remains BLOCKED. A passing CP11 gate
does not execute that task, approve a payment or authorize a production release.

## Start the repair exercise

First complete the earlier candidate workflow in this same working copy.
The older require-candidates option still concerns Chapters 1–9:

~~~bash
python3 reader_side/tools/run_checks.py --require-candidates \
  --output reader_side/evidence/CP11_PRIOR_WORKFLOW.json
python3 reader_side/tools/scope_guard.py --chapter CP11 \
  --capture reader_side/evidence/CP11_EDIT_BASELINE.json
python3 reader_side/tools/evolution_gate.py \
  --output reader_side/evidence/CP11_BASELINE \
  --scope-baseline reader_side/evidence/CP11_EDIT_BASELINE.json
~~~

The supplied CP11 starter must fail. Its three implementation defects confuse
stored history with today's policy, accept changed retry intent, and commit a
decision before its audit event. Its policy delta also overclaims authority.
The protected faulty copies remain faulty after the editable copies are fixed.

Repair only the two allowed files. Do not change the owner oracle or recapture
the baseline after an out-of-scope edit. Check the repaired current files:

~~~bash
python3 reader_side/tools/evolution_gate.py \
  --output reader_side/evidence/CP11_REPAIRED \
  --scope-baseline reader_side/evidence/CP11_EDIT_BASELINE.json
python3 reader_side/tools/run_checks.py --require-evolution \
  --output reader_side/evidence/CP11_COMBINED.json
~~~

The dedicated success status is PASS_POLICY_EVOLUTION_REVIEW_ONLY. The combined
require-evolution option requires the regression suite, the current Chapters
1–9 workflow and the current CP11 candidates. It does not imply a CP10 release
decision. Without release-rehearsal, that separate status remains NOT_RUN.

For a protected worked example, leave your candidates unchanged:

~~~bash
python3 reader_side/tools/evolution_gate.py --reference \
  --output reader_side/evidence/CP11_REFERENCE
python3 reader_side/tools/evolution_gate.py --unsafe-control \
  --output reader_side/evidence/CP11_FAULTY_CONTROL
~~~

These modes are explicitly reported as PROTECTED_REFERENCE and
PROTECTED_UNSAFE_CONTROL. The ordinary gate reports WORKING_CANDIDATES.
Without scope-baseline the gate cannot prove the actual before/after edit
boundary. Its local integrity checks are not an arbitrary-code sandbox.

## A persistent request across rollout and restart

After repair, create a new database and record a v1 request:

~~~bash
python3 reader_side/tools/policy_history_cli.py \
  --db reader_side/evidence/CP11_DEMO/history.sqlite init
python3 reader_side/tools/policy_history_cli.py \
  --db reader_side/evidence/CP11_DEMO/history.sqlite \
  decide --key request_4000 --amount 4000.00 --beneficiary vendor_17
python3 reader_side/tools/policy_history_cli.py \
  --db reader_side/evidence/CP11_DEMO/history.sqlite \
  activate --policy BR-001/v2
python3 reader_side/tools/policy_history_cli.py \
  --db reader_side/evidence/CP11_DEMO/history.sqlite \
  decide --key request_4000 --amount 4000.0 --beneficiary vendor_17
~~~

Each command runs a fresh process against the same database. The first decision
is CREATED, STANDARD_QUEUE, BR-001/v1. After activation, the canonically equal
retry is REPLAYED with the original record. It does not become a v2 decision.
An in-memory dictionary could not preserve this property across these processes.

The persistence API has a deliberately explicit new input contract: an amount
is a string with 1–12 digits before the decimal point, optional minus sign and
at most two fractional digits; a beneficiary contains 1–80 ASCII letters,
digits, underscores or hyphens. More precision, exponent notation, floats,
non-finite values and extra payload fields fail before recording. Zero and
negative values with valid syntax produce recorded INVALID_AMOUNT rejections.
The older assess() API keeps its original behavior.

The original raw amount string is retained. Canonical identity normalizes cents,
so 4000, 4000.0 and 4000.00 represent the same amount. The saved payload
fingerprint covers amount and beneficiary; parent operation and explicit policy
intent are checked separately. Ambient active policy is excluded from retry
identity. If policy is supplied explicitly, it must exist and match the
recorded policy on a retry. An explicit v2 retry of an existing v1 request is
IDEMPOTENCY_CONFLICT; an unknown version is UNKNOWN_POLICY.

## Stored response, historical recomputation and new reevaluation

~~~bash
python3 reader_side/tools/policy_history_cli.py \
  --db reader_side/evidence/CP11_DEMO/history.sqlite \
  replay --key request_4000
python3 reader_side/tools/policy_history_cli.py \
  --db reader_side/evidence/CP11_DEMO/history.sqlite \
  recompute --key request_4000
python3 reader_side/tools/policy_history_cli.py \
  --db reader_side/evidence/CP11_DEMO/history.sqlite \
  reevaluate --from-key request_4000 --key reevaluation_4000 --policy BR-001/v2
~~~

| Operation | Reads | Produces |
| --- | --- | --- |
| replay | Stored payload, policy, outcome and identity | The same recorded response, without calculation |
| recompute | Stored payload and selected historical policy snapshot | A MATCH comparison with the stored outcome, without a new decision or event |
| reevaluate | The old payload plus an explicitly requested new policy | A new decision identity linked by parent_key to the original |

The historical recomputation remains STANDARD_QUEUE under v1. The new v2
reevaluation is HUMAN_REVIEW. The original decision is unchanged. Reusing the
old key for reevaluation fails NEW_KEY_REQUIRED. Retrying the new key with a
different parent or explicit target policy conflicts; matching retries return
the same new record. Changing amount or beneficiary under any existing key
also conflicts.

## Persistent identity and transaction boundary

The schema stores immutable policy snapshots and digests, raw payload/outcome
JSON and their digests, a canonical request fingerprint, selected policy
version, decision identity and optional parent. Activation is persisted in
settings and appended to the audit trail. A named version cannot silently
acquire a different threshold when the store is reopened.

BEGIN IMMEDIATE and a unique request key serialize competing writers. Decision
insertion and its audit insertion share one explicit transaction. The owner
test injects a real SQLite abort on the second insert and verifies that neither
row survives. The protected exercise also starts two worker processes for one
key with different payloads: exactly one may create a decision, and the other
must conflict. A deterministic two-connection lock test verifies failure while
another writer holds the lock and successful retry after release.

Immutable-table triggers reject ordinary updates/deletes. Hash checks detect
altered stored content. These are integrity checks within this teaching
environment; a person controlling the checker, database and host can defeat
local controls. They are not signatures or proof of real payment processing.

## Migrate a synthetic brownfield fixture without inventing history

Earlier chapters used a pure Python router; they did not operate a SQLite
database. The following seed is a newly introduced synthetic legacy fixture:

~~~bash
python3 reader_side/tools/seed_legacy_history.py \
  --output reader_side/evidence/CP11_LEGACY_COMPLETE
python3 reader_side/tools/policy_history_cli.py \
  --db reader_side/evidence/CP11_LEGACY_COMPLETE/history.sqlite \
  migrate --provenance reader_side/evidence/CP11_LEGACY_COMPLETE/provenance.json
~~~

The seed creates a schema-1 legacy_decisions table and provenance.json.
Migration is explicit: opening this file through the normal store first fails
EXPLICIT_MIGRATION_REQUIRED. The reusable migration API expects trusted
owner-supplied provenance. At the owner CLI boundary, the source ID and complete
row digest must match a protected known synthetic fixture, and the actual
database rows must match it too. A self-consistent invented source ID fails
LEGACY_PROVENANCE_NOT_OWNER_BOUND. This establishes fixture consistency, not
authenticated real-world history.

Migration validates the original payload, complete policy snapshot and recorded
outcome before conversion, performs schema/data changes in one transaction, and
retains the original legacy table and raw bytes. The owner then activates v2 and
recomputes the migrated request under its retained v1 snapshot.

Two deliberately incomplete/inconsistent fixtures are also available:

~~~bash
python3 reader_side/tools/seed_legacy_history.py --fixture ambiguous \
  --output reader_side/evidence/CP11_LEGACY_AMBIGUOUS
python3 reader_side/tools/policy_history_cli.py \
  --db reader_side/evidence/CP11_LEGACY_AMBIGUOUS/history.sqlite \
  migrate --provenance reader_side/evidence/CP11_LEGACY_AMBIGUOUS/provenance.json
~~~

Missing policy history fails HISTORY_AMBIGUOUS. The wrong_outcome fixture fails
LEGACY_OUTCOME_MISMATCH. In each case every legacy row, schema version and file
byte remains unchanged; migration does not convert only the easy rows or guess
a policy from the amount or route. Repeating a completed migration fails
LEGACY_SCHEMA_REQUIRED. Do not relabel a failed migration as a fresh empty
database to hide the original records.

## Preserve evidence and invalidate stale claims

Every evolution gate requires a NEW output directory. It preserves actual
SQLite files, fresh-process step JSON/logs and EVOLUTION_RESULT.json. That
receipt binds the candidate, policy delta, protected catalog/context/oracles,
v1 router and checker manifest, plus every retained database and step file.
To require an earlier passing receipt to remain valid:

~~~bash
python3 reader_side/tools/evolution_gate.py \
  --output reader_side/evidence/CP11_RECHECK \
  --receipt reader_side/evidence/CP11_REPAIRED/EVOLUTION_RESULT.json \
  --scope-baseline reader_side/evidence/CP11_EDIT_BASELINE.json
~~~

A comment-only source edit invalidates the source receipt. An altered database
or step log invalidates its evidence hash. Malformed receipts, protected-oracle
changes and out-of-scope edits fail closed. A new run never overwrites the
earlier output directory. Observed nested gate checks are not added to the
shared runner's discovered unit-test total.

CP10 freshness now also binds the CP11 candidate, delta and policy/context
inputs. Repairing CP11 invalidates an earlier CP10 session. CP10's artifact
continues to contain only its presentation experiment; it excludes the new
policy_history.py. Even a fresh passing CP10 presentation dossier reports
policy_evolution_release_authorized=false and cannot authorize policy v2.

## Reproduce the packaged validation

From the book-package root:

~~~bash
python3 scripts/validate_chapter11_lab.py
# For another run, choose a fresh directory.
python3 scripts/validate_chapter11_lab.py --output build/chapter11_validation_02
~~~

The first default directory is build/chapter11_validation. The validator repairs
earlier candidates and CP11 only in disposable copies, captures the real edit
boundary, preserves starter failures and completed SQLite evidence, challenges
stale and malformed records, proves CP10 staleness, runs the shared
require-evolution check, and verifies that delivered source hashes did not
change. It derives counts from the actual runner JSON. No production migration,
real human acceptance, payment authorization or deployment is claimed.
