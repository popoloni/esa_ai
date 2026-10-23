# Ordinary mentoring path: explain a different boundary

This optional exercise is separate from PILOT-013/v1 and does not use its reserved transfer case. Reading this feedback does not itself establish an unseen-transfer result.

## Prompt

A teammate proposes an AI-generated runbook for an invoice-status API. Its smoke check receives HTTP 200 twice and concludes the change is correct. The API also contains a refund-permission field and serves two client versions. Write a short response naming the next useful independent checks, the evidence owner and the decision that remains human. Then ask a peer to challenge one assumption.

## Reasoning criteria

- Distinguish repeated success from the expected business fields.
- Preserve the separate authority for refunds; a status response is not permission to move money.
- Identify supported consumer versions and a concrete incompatible response.
- Name a bounded check, its source and what a pass would still leave unknown.
- Record an unresolved owner decision without inventing a signature.

## Worked feedback

A second HTTP 200 shows neither an authorized refund nor the compatibility of the two clients. Start from the owner-approved response contract and exercise one consequential boundary, the prohibition on unintended refund permission, and the actual fields each client consumes. Review the exact changed response and current evidence. A pass in these selected cases does not establish every user interpretation, authentication path or production effect. A useful answer can propose a smaller set than a full enterprise checklist if it explains why those checks address the present change.

## Mentor record

Initial prediction: ______
Assistance and resources allowed: ______
Observation and evidence reference: ______
Specific peer feedback: ______
Revised explanation and remaining uncertainty: ______
Next independent practice: ______

Keep the initial response. Do not turn a polished second answer into proof of retention or an employee ranking. Use the advanced chapter protocol only if a separately designed delayed learning claim is actually needed.
