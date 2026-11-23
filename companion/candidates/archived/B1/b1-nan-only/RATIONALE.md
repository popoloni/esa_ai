# Candidate b1-nan-only

**Origin: CONSTRUCTED_TEACHING_VARIANT.** Prepared on 2026-11-02 for offline review. The code and the rationale below were deliberately constructed; neither is an actual model transcript, a measured model capability, or a learner result.

## Proposal to review

> The observed nonfinite defect is NaN. I added an explicit NaN guard, retained the nonpositive check and kept the original boundary. All seven historical examples pass.

This quoted paragraph is the candidate's constructed rationale. Assess its claims against the contract and observations.

## Bounded scope

The candidate changes only `src/treasury/routing.py`. It preserves `RoutingDecision`, `assess(amount_eur: str)`, the EUR 5,000 threshold and the `BR-001/v1` policy identifier. The test suites and source authority remain outside the proposed change.

## Review task

Decide whether the observed seven passing cases establish the finite-positive requirement. Try the additional nonfinite inputs without changing the historical cases.

Record an initial decision and its reason before reading `TRUTH.json`. Then compare the actual test output with that decision. The ground truth describes expected behavior; an executed receipt is the observation.
