"""Independent selected-case review of the versioned operator projection.

Expected wording and meanings are in an author-owned contract, outside the
candidate module. Run this process against source or the extracted CP10 archive.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--cases", required=True, type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.source.resolve()))
    from treasury import operator_view
    cases = json.loads(args.cases.read_text())
    observations, findings = [], []
    for case in cases["cases"]:
        try:
            actual = operator_view.explain_for_operator(case["amount"])
            passed = actual == case["expected"]
            if not passed:
                findings.append(case["id"] + ":OUTPUT_MISMATCH")
            observations.append({"id": case["id"], "passed": passed, "actual": actual})
        except Exception as exc:
            findings.append(case["id"] + ":" + str(exc))
    # These cases check meaningful violations, including a different policy
    # snapshot and a supplied route that contradicts the explanation.
    base = {"route": "STANDARD_QUEUE", "reason_code": "BELOW_LIMIT", "policy_version": "BR-001/v1",
            "payment_authorized": False, "notice": "ROUTING_ONLY_NOT_PAYMENT_APPROVAL"}
    policy = {"version": "BR-001/v1", "threshold_eur": "5000.00", "algorithm": "TREASURY_THRESHOLD_V1"}
    negative = [
        ("payment_authorized", {**base, "payment_authorized": True}, policy, "PAYMENT_AUTHORITY_MISMATCH"),
        ("wrong_policy", base, {**policy, "threshold_eur": "3000.00"}, "UNKNOWN_OR_MISMATCHED_POLICY"),
        ("wrong_route", {**base, "route": "HUMAN_REVIEW", "reason_code": "AT_OR_ABOVE_LIMIT"}, policy, "DECISION_EXPLANATION_MISMATCH"),
        ("unknown_route", {**base, "route": "PAID"}, policy, "DECISION_EXPLANATION_MISMATCH"),
        ("unknown_policy", {**base, "policy_version": "BR-001/v99"}, policy, "UNKNOWN_OR_MISMATCHED_POLICY"),
    ]
    for name, decision, snapshot, expected in negative:
        observed = "NO_ERROR"
        try:
            operator_view.present("4000.00", decision, snapshot)
        except ValueError as exc:
            observed = str(exc)
        passed = observed == expected
        observations.append({"id": name, "passed": passed, "observed": observed})
        if not passed:
            findings.append(name)
    # Experiment metadata must not change product wording.
    metadata = deepcopy(base)
    metadata["benefit_status"] = "AN_UNVERIFIED_CLAIM"
    passed = operator_view.present("4000.00", metadata, policy) == operator_view.present("4000.00", base, policy)
    observations.append({"id": "benefit_metadata_is_not_product_output", "passed": passed})
    if not passed:
        findings.append("BENEFIT_METADATA_LEAK")
    result = {"schema": "operator-review/v1", "status": "PASS_SELECTED_OPERATOR_CASES" if not findings else "FAIL",
              "observations": observations, "findings": findings,
              "human_comprehension": "NOT_MEASURED", "real_operator_benefit": "NOT_MEASURED"}
    print(json.dumps(result, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
