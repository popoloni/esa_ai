# A context, rule and skill lifecycle in the existing lab

This card turns the Chapter 6 source audit into a sequence you can perform. The
target is CTX-006 and its `context-audit` skill, not approval of ADR-005. The learner
may edit only the existing CP06 candidate paths:

- `repo/engineering/knowledge/context_packet.json`
- `repo/.agents/skills/context-audit/SKILL.md`

Do not update reader-owned source hashes to make an inconvenient mismatch pass.

## 1. Select the next decision, then locate its sources

The task is to prepare a context handoff for planning the explanation-only alpha.
Read `reader_side/knowledge/source_catalogue.json`, then follow its relative paths.
Predict these treatments before looking at the reference candidate:

| Record | Required treatment | Why it belongs |
|---|---|---|
| K-POL-001 | INCLUDE_NORMATIVE | The synthetic current routing intent constrains the task |
| K-SPEC-004 | INCLUDE_CONTRACT | Reference examples specify the explanation, not a production approval |
| K-ADR-005 | INCLUDE_PROPOSED | The recommendation is useful and human architecture review remains pending |
| K-WIKI-OLD | EXCLUDE_SUPERSEDED | Retain the disagreement in the source trail, not as operative policy |
| K-ARCHIVED-NOTE | EXCLUDE_UNTRUSTED | Retrieved instructions do not acquire authority by being returned |

Search for a known identifier or symbol before reading a whole directory. Retrieve
the containing source to understand the match; a matching line is not the full
contract. If a name is unknown, ask for the missing source or inspect the relevant
module first. Neither a larger context window nor a retrieval tool resolves an
authority conflict for you.

## 2. Choose where each item should live

| Item | Home | Example |
|---|---|---|
| This task's failing input, scope and stop condition | Task/session record | Repair only CTX-006 and the named skill |
| Repeated repository convention | Short rule pointing to its source | Consult current intent before a routing change |
| Repeated multi-step method | Skill body and narrowly relevant references | Audit source status; run selected checks; report limits |
| Policy, ADR, test output or incident finding | Versioned engineering record | INT-001, proposed ADR-005, saved gate result |
| Temporary search result or speculative hypothesis | Working notes, with source/status | The learner packet claims EUR 9,999; the current policy source says EUR 5,000 |

Do not convert every useful sentence into a permanent rule. Remove a repeated
policy value from an adapter when a source pointer is sufficient. Preserve
historical records when retiring instructions; deleting context from the next
prompt is different from deleting the audit trail.

## 3. Observe the unsafe starting pair

From the lab root, choose a new evidence directory. These commands preserve stdout
as a separate record; `knowledge_gate.py` also updates its normal reader-side
evidence file. A nonzero status for the unsafe starter is expected.

```bash
mkdir -p build
mkdir build/context_lifecycle_01
python3 reader_side/tools/knowledge_gate.py \
  > build/context_lifecycle_01/before.json
```

If `context_lifecycle_01` already exists, choose a new name instead of replacing
previous evidence. If you already
repaired the candidates, the current result may be green; record that starting
state rather than reinstalling faults in the continuing lab.

Read the result. Connect each wrong threshold, promoted proposal or unsafe skill
instruction to the governing source. The gate is lab lint; it is not a model
comprehension test or native-host activation test.

## 4. Revise and check the pair

Correct the two allowed candidate files. Keep the skill's name and descriptive
trigger; replace the unsafe shortcut with a source-audit procedure. Include the
non-trigger: it cannot authorize a payment, accept ADR-005 or release software.
The protected reference remains available after your own attempt.

```bash
python3 reader_side/tools/knowledge_gate.py \
  > build/context_lifecycle_01/after.json
python3 reader_side/tools/run_checks.py
```

Retain the before/after pair and the exact two-file diff. The source catalogue,
approved fixture and oracle must remain unchanged. Report the checks that really
ran and the human decisions that did not.

Keep the CP06 `human_review_required` list at its fixed teaching subset,
`["ADR-005", "OPERATOR_COPY"]`. The checker compares that list exactly with the
reference; adding `SPEC-004` produces `HUMAN_REVIEW_MISSING` even though the
requirements review is still pending. Save a reader-held review note as
`build/context_lifecycle_01/handoff.md`, beside the run evidence and outside the
two candidate files. Record that `SPEC-004/v1` remains
`READY_FOR_HUMAN_REQUIREMENTS_REVIEW`, and link to
`reader_side/reference_solution/specification.json` for the next planner.
A packet `PASS` covers selected field and skill checks; it does not check this
note or establish that every pending review has been enumerated or completed.

## 5. Make a maintenance decision

Use `reader_side/knowledge/claim_dependencies.json` to answer three distinct events:

- **ADR status changes:** recheck `architecture_choice`, the affected plan and
  source status. A rejected ADR requires replanning, not a false-ready writer.
- **Intent changes:** recheck routing threshold and payment-authority claims.
  Do not apply the new threshold here; CP11 owns the history-preserving exercise.
- **Client convention changes:** revise the disposable client projection and
  verify actual discovery/activation in that client. The business intent does not
  change because a folder convention changed.

Record: asset owner; revision identity; sources consulted; trigger/non-trigger;
one relevant task; one task that should not activate it; actual loaded files if a
host was used; observed output; and the next review trigger. Use `not observed`
where appropriate. A projected file is not an observed skill invocation.

Retire a rule or skill when it is superseded, redundant or inappropriate for the
current workflow. Keep its prior revision and reason for retirement. This is a
proposed maintenance protocol; no automatic native-host loading, version-upgrade
trial or human-learning gain is claimed by these Python checks.
