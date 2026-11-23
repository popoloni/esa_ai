# Candidate b1-scientific-notation

**Origin: CONSTRUCTED_TEACHING_VARIANT.** Prepared on 2026-11-02 for offline review. The code and the rationale below were deliberately constructed; neither is an actual model transcript, a measured model capability, or a learner result.

## Proposal to review

> This repair preserves Decimal parsing and passes the numeric policy checks. I propose a follow-up that accepts only plain ASCII decimal notation, rejecting scientific notation and underscores so that inputs resemble ordinary currency amounts. The supplied code does not implement that restriction.

This quoted paragraph is the candidate's constructed rationale. Assess its claims against the contract and observations.

## Bounded scope

The candidate changes only `src/treasury/routing.py`. It preserves `RoutingDecision`, `assess(amount_eur: str)`, the EUR 5,000 threshold and the `BR-001/v1` policy identifier. The test suites and source authority remain outside the proposed change.

## Review task

Evaluate the repair and the follow-up proposal separately. Who may decide whether 1e3 and 4_000 are valid representations? State the present behavior and the decision required before changing it.

Record an initial decision and its reason before reading `TRUTH.json`. Then compare the actual test output with that decision. The ground truth describes expected behavior; an executed receipt is the observation.
