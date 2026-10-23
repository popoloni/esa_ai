# Choose controls that match the consequence

Use this card before the agent edits anything. It is an original engineering
worksheet, not an empirically validated risk score. All three cases below use the
book's existing contracts. More rows do not create more authority.

## Three worked choices

| Change | Smallest useful record and check | Added control and its reason | Stop at |
|---|---|---|---|
| **CP01: reject invalid input in one pure routing function** | INT-001; known red baseline; one-file diff; seven selected acceptance cases; review verdict | Preserve the policy and oracle. A minimal parsing repair must not quietly lower the threshold. No database migration or deployment procedure belongs in this task. | Candidate ready for human review; real owner acceptance still needs its owner |
| **CP11: apply BR-001/v2 to future persistent decisions** | Bounded CP11 work order and policy delta; new behavior cases; retained v1 source/history | Use one persisted ledger across activation/restart. Test stored replay, historical recomputation, explicit reevaluation, retry conflict and migration ambiguity. These controls are necessary because new behavior can affect old records. | `PASS_POLICY_EVOLUTION_REVIEW_ONLY`; the old CP10 release receipt does not cover changed source |
| **CP10 / CP12: select an artifact or restore service state** | Exact artifact/configuration and input identities; target state; named decision authority; observed rehearsal | CP10 checks the real disposable merge candidate and reversible artifact selection. CP12 preserves the control and incident ledgers and checks state selection, restart and history. Recovery must be observable because a process action can outlive an editing session. | Local rehearsal/recovery review only; no production rollout, payment authority or real incident closure |

The third row is a pair of bounded local teaching cases, not a claim that a
production release and an incident are interchangeable. Their concrete
authorizations and gate names remain in Chapters 10 and 12. The CP10 mock owner
decision does not authorize CP12 or a real deployment.

Sensitive data is a separate trigger: identify what may be read, sent to a model,
stored in a log and retained. A read-only operation can still export information.
The synthetic lab contains no customer data or production credentials; it cannot
demonstrate the controls of an actual confidential-data environment.

## Fill one small card for your own change

1. **Outcome:** What observable behavior is different when the task is complete?
2. **Authority:** Who has authorized that behavior, and what remains undecided?
3. **Reversibility:** Is this a file edit, a persisted record change, or an external
   action? What would reversing it actually mean?
4. **Scope:** Which paths, data and tools may the delegate use? What enforces this?
5. **Evidence:** Which failing observation, independent expectation and candidate
   identity will support the decision?
6. **Review/stop:** Who examines the result? What stops a run before it does more?

For CP01, one intent file, one patch, two reports and a short review note answer
these questions. Do not reproduce every later chapter's dossier. If you add a
control, name the failure it addresses. If you remove one, say why the consequence
that required it is absent. A passing check never substitutes for the authority
to change a rule or affect another system.

## Review the amount of process

Ask a second reader to point to each control's reason. If they cannot identify
one, simplify it or state the unresolved risk. This is a proposed review activity;
no independent-reader result or measured reduction in effort is claimed here.
