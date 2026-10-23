# CP11-POLICY-001 — local policy-evolution experiment

The reader authorizes a bounded synthetic exercise with BR-001/v1 at EUR 5,000
and BR-001/v2 at EUR 3,000. Strictly below the selected threshold means
STANDARD_QUEUE; equality and above mean HUMAN_REVIEW. Neither route approves a
payment. BR-001/v1, its pure routing API, old fixtures and tests remain intact.

Only repo/src/treasury/policy_history.py and
repo/engineering/evolution/policy_delta.json are learner-editable. Capture the
CP11 edit baseline before repair. The owner catalog, oracles, worked example,
faulty control, CLI, receipts and database evidence remain reader-controlled.

This is a new SQLite teaching experiment. Its synthetic legacy database models
a brownfield migration; the earlier chapters did not operate a database.
The protected change_context.json retains CP11-RETAINED-V1 and the initial
REQ-11-INITIAL alongside the later INT-11-RETRY-CLARIFICATION. These are
author-created teaching records; the clarification is not invented evidence
of a real stakeholder conversation.
Preserve exact historical payload and outcome bytes, selected policy snapshot,
their digests, request identity, and any explicit reevaluation parent.

The new persistence API accepts amount strings with 1–12 digits before the
decimal point, an optional minus sign and at most two fractional digits.
Beneficiary identifiers contain 1–80 ASCII letters, digits, underscores or
hyphens. Negative/zero monetary values produce recorded INVALID_AMOUNT routing
rejections. Exponents, non-finite values, floats, extra payload fields and more
than two decimal places fail before recording. These restrictions do not
change the older routing.assess() input semantics.

Canonical request identity includes normalized amount and beneficiary, plus
the parent operation and any explicitly requested policy. It excludes the
ambient active policy. An explicit unknown version fails, and an explicitly
changed policy conflicts with the recorded decision. A repeated key with the
same identity returns the original decision after rollout and restart; changed
payload or changed parent is a conflict. A new reevaluation has a new key and
an explicit parent. replay returns the saved response; recompute recalculates
under the recorded snapshot and creates no new decision or audit event.

Policy versions are immutable. Activation is an explicit persistent event.
Decision and audit insertion form one transaction. A failed second write must
roll back the first. SQLite serializes the two competing writers in the race
exercise; an in-memory cache is insufficient.

Legacy migration requires matching owner provenance and complete, consistent
payload, policy and outcome. Ambiguity or an inconsistent outcome aborts the
whole migration; do not infer a policy from an amount, date or queue. Successful
migration retains the original legacy table. It does not reconstruct unknown
history or simulate a production migration.

CP07 T07-03 remains PENDING_HUMAN and T07-04 remains BLOCKED. This work order
does not authorize the blocked architecture task. CP10's presentation review
does not authorize policy v2. Source changes invalidate earlier CP10 evidence;
fresh policy-evolution release review would be a separate future decision.
No live payment, production rollout, human acceptance or release is claimed.
