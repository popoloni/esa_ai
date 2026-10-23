# Decide whether a small agent practice helps the team

This is an authored teaching scenario, not a report from a real organization.
It extends Chapter 13's ordinary operating agreement. No retention study or
measured adoption benefit is required to try the exercise.

Mira, a senior maintainer, objects because an earlier proposal changed an API
field without naming its consumers. Leo wants agent use to become the default
because he can produce patches quickly. Sara, their reviewer, struggles to find
the contract and checks attached to each patch. Identify the compatibility risk,
the review bottleneck and the proposed tool-policy change separately.

Use the existing [CSV feature](../csv_export/README.md) as the bounded task.
Keep its row selector and JSON contract. In this fictional scenario Sara owns
the experiment decision; Mira supplies a consumer example before editing; Leo
prepares the permitted candidate and a handoff. This role assignment grants no
authority in a real organization.

## Make an agreement before collecting results

| Decision | Proposed rule for this example |
| --- | --- |
| Admission | One bounded candidate in review at a time; retain every attempt |
| Evidence | Current contract, permitted diff, independent consumer check and location of the row-selection boundary |
| Stop | A missing expectation, unexplained scope change or failed compatibility check stops the candidate |
| Queue | Help resolve a waiting review before producing another unreviewed patch |
| Working conditions | Use agreed working hours, permitted data and an available client; no expectation of continuous availability |
| Next decision | The reviewer keeps, revises or drops this handoff practice after the nominated changes are assessed |

Choose the number of ordinary changes and the observation window before the
trial. Record preparation, implementation and review effort, missing evidence,
compatibility failures and assistance. A few changes can reveal a local problem;
they do not establish a general productivity effect or rank people.

## Distinguish two possible diagnoses

If a newcomer finds the selector but cannot explain actor filtering, arrange a
pairing session and retain the first and assisted explanations. If experienced
reviewers repeatedly cannot find the contract, fix its link in the handoff.
One observation suggests a learning need; the other suggests a workflow defect.
Do not infer either diagnosis from a person's attitude to the tool.

Write four lines for your own team: the concrete objection, the observation
that could change the decision, the condition that stops the experiment and
the person authorized to decide. Use the existing [pairing and review guide](PAIRING_AND_REVIEW.md)
and operating-agreement template to carry it forward. Leave results blank until
actual work has been observed.
