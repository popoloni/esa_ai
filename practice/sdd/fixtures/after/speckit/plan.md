# Candidate design plan — explanation-only Treasury alpha

AUTHOR_EXERCISE — authored teaching artifacts, not output from a live named coding-agent client.

Status: PROPOSED; human requirements and design approval pending.
Contract: SPEC-004/v1; policy BR-001/v1; authority SRC-POL-001.

## Reuse before adding a component

Read the existing `treasury.routing.assess` result. A small presenter can carry its
route, reason and policy version without changing the router. Chapter 5 compares
a direct function with an injected routing port; this plan does not accept either
architecture on a human owner's behalf. No database, network service, new policy
engine or payment operation is needed for the current presentation experiment.

## Obligation-to-design trace

| Obligation | Candidate design response | Review question |
| --- | --- | --- |
| REQ-EXPL-001 | Copy the existing route and reason, with no second routing calculation. | Does the presenter preserve the result? |
| REQ-EXPL-002 | Carry an explicit no-payment-approval notice on valid and rejected paths. | Could an operator confuse the wording with permission? |
| REQ-EXPL-003 | Represent INVALID_AMOUNT as REJECTED without eligibility. | Are zero, negative, malformed and nonfinite cases retained? |
| REQ-EXPL-004 | Carry the version from the routing result unchanged. | Does the display invent a newer policy? |
| REQ-EXPL-005 | Keep benefit unvalidated. | Is any unsupported gain reported? |

## Cases, uncertainty and reversibility

Review SC-EXPL-001 through SC-EXPL-008, including equality SC-EXPL-002,
against the independent shared case oracle. Unknown vocabulary and operator
comprehension remain research questions. A missing routing result or unknown
reason requires a future owner decision; do not invent that rule here.
Revert only the proposed presenter if the alpha is stopped; the existing router
and historical records stay unchanged. Implementation and release remain pending.
