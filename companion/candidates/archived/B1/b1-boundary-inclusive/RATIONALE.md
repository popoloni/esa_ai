# Candidate b1-boundary-inclusive

**Origin: CONSTRUCTED_TEACHING_VARIANT.** Prepared on 2026-11-02 for offline review. The code and the rationale below were deliberately constructed; neither is an actual model transcript, a measured model capability, or a learner result.

## Proposal to review

> I preserved the amount validation and used an inclusive comparison so that an amount equal to the configured limit follows the ordinary queue. This makes the threshold read as the maximum amount in that queue.

This quoted paragraph is the candidate's constructed rationale. Assess its claims against the contract and observations.

## Bounded scope

The candidate changes only `src/treasury/routing.py`. It preserves `RoutingDecision`, `assess(amount_eur: str)`, the EUR 5,000 threshold and the `BR-001/v1` policy identifier. The test suites and source authority remain outside the proposed change.

## Review task

Resolve the boundary from the policy rather than from the variable name or this explanation. Record the exact input, expected result and observed result.

Record an initial decision and its reason before reading `TRUTH.json`. Then compare the actual test output with that decision. The ground truth describes expected behavior; an executed receipt is the observation.
