# Short transfer exercises with worked feedback

Use a separate practice copy or a repository you are authorized to inspect. Do not modify the protected oracle or infer a release decision. These formative exercises are not the unseen Chapter 13 retention/transfer pilot. Stop before the worked feedback when first forming your explanation.

## T09 — A green new API client

A provider changes `policy_version` to `policy.version`. The new client passes; an older reporting client still reads the original field. Run the local contract drill in expanded and contracted modes. Explain which caller breaks, the source of its expectation and why an additive transition does not prove all real clients are compatible. Specify one real client observation you would collect before removing the old field.

Reasoning criteria: identifies the exact missing field and affected version; preserves behavior/authority; distinguishes the selected readers from a complete client inventory; proposes a check that can reject the change.

Worked feedback: the contracted fixture breaks the legacy reader even though the current reader succeeds. The expanded fixture satisfies these two readers because they tolerate additional keys. A strict unknown-field decoder, cached schema or unrecorded client could behave differently. Test representative actual callers and establish a deprecation decision; do not erase the old expectation to obtain green.

## T11 — A consumer repeats a message

A queue consumer records a routing decision in its local database, then sends a notification, then acknowledges the message. The notification succeeds but the acknowledgement is lost. The queue redelivers. Define the business identity, retained payload and expected local retry behavior. Identify the side effect outside the local transaction and propose the evidence needed to assess duplicate handling.

Reasoning criteria: does not confuse message delivery ID with business identity without justification; preserves recorded policy on an equivalent retry; rejects conflicting reuse; recognizes the transaction boundary.

Worked feedback: the database can return its stored decision while notification delivery still repeats. A local uniqueness constraint does not make a remote effect exactly once. Propose how to retain the intended notification, carry a stable identity and handle duplicates at the receiver. Assess those persistence, retry and failure assumptions separately; naming a design is not a proof. Retain sender/receiver evidence and tests for interruptions around each boundary before an owner accepts the design.

## T12 — The right executable, the wrong tenant

Two workers have the same code revision. One receives a successful response using another tenant's state locator. A health endpoint and latency monitor stay green. Define a symptom without choosing a cause, nominate two competing explanations, and specify a controlled comparison that changes one relevant input. Name the evidence that must be preserved before repair.

Reasoning criteria: distinguishes source identity from effective state identity; uses a falsifiable prediction; preserves authorization and privacy boundaries; separates restoration from downstream reconciliation.

Worked feedback: investigate the effective locator and authorized tenant binding, not only a configured name or matching code hash. A path-only comparison can discriminate one cause in an isolated fixture. It does not authorize reading another tenant's production records. Restore within an approved scope and retain a separate owner decision for any data exposure or erroneous effects.

## Review note

Record your initial prediction, observation, revised explanation and unresolved decision. A peer should identify one assumption that would make the procedure unsafe to reuse. Keep that feedback with the original response; an improved second answer is useful mentoring evidence, not a validated learning-effect estimate.
