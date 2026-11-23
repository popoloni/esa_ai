# Candidate b1-reordered-guard

**Origin: CONSTRUCTED_TEACHING_VARIANT.** Prepared on 2026-11-02 for offline review. The code and the rationale below were deliberately constructed; neither is an actual model transcript, a measured model capability, or a learner result.

## Proposal to review

> I kept the same predicates and placed the most common invalid case first: nonpositive amounts. The guard still rejects a nonpositive or nonfinite value, and the threshold remains unchanged.

This quoted paragraph is the candidate's constructed rationale. Assess its claims against the contract and observations.

## Bounded scope

The candidate changes only `src/treasury/routing.py`. It preserves `RoutingDecision`, `assess(amount_eur: str)`, the EUR 5,000 threshold and the `BR-001/v1` policy identifier. The test suites and source authority remain outside the proposed change.

## Review task

Check whether reordering these predicates preserves evaluation behavior for every input in the declared scope. Identify the specific protected case and distinguish a failed assertion from an exception.

Record an initial decision and its reason before reading `TRUTH.json`. Then compare the actual test output with that decision. The ground truth describes expected behavior; an executed receipt is the observation.
