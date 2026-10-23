"""Two response readers and a bounded compatibility drill; not an HTTP/release gate."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = ("legacy_only", "expanded", "contracted", "string_boolean", "wrong_policy", "payment_authority")

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def probe(response, reader, expectation):
    problems = []
    if not isinstance(response, dict):
        return {"consumer": reader, "accepted": False, "findings": ["RESPONSE_NOT_OBJECT"]}
    if response.get("route") != expectation["expected_route"]:
        problems.append("ROUTE_MISMATCH")
    if response.get("payment_authorized") is not False:
        problems.append("PAYMENT_AUTHORITY_NOT_BOOLEAN_FALSE")
    if reader == "legacy":
        version = response.get("policy_version")
    else:
        policy = response.get("policy")
        version = policy.get("version") if isinstance(policy, dict) else None
    if version != expectation["expected_policy"]:
        problems.append("POLICY_VERSION_MISSING_OR_MISMATCH")
    return {"consumer": reader, "accepted": not problems, "findings": problems}

def inspect_fixture(name, readers, expectation):
    path = HERE / "fixtures" / (name + ".json")
    response = read_json(path)
    return {"fixture": name, "fixture_sha256": digest(path),
            "probes": [probe(response, reader, expectation) for reader in readers]}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", choices=FIXTURES, default="expanded")
    parser.add_argument("--consumer", choices=("legacy", "current", "both"), default="both")
    parser.add_argument("--self-check", action="store_true", help="Check the declared positive/negative fixture matrix")
    args = parser.parse_args(argv)
    try:
        expectation = read_json(HERE / "contract_expectations.json")
        report = {"schema": "consumer-probe-result/v1", "script_sha256": digest(Path(__file__)),
                  "expectations_sha256": digest(HERE / "contract_expectations.json"),
                  "meaning": "Selected local response readers only; no HTTP, full consumer inventory, production rollout or acceptance authority."}
        if args.self_check:
            expected = read_json(HERE / "expected_matrix.json")["expected_acceptance"]
            report["matrix_sha256"] = digest(HERE / "expected_matrix.json")
            report["fixtures"] = [inspect_fixture(name, ("legacy", "current"), expectation) for name in FIXTURES]
            comparisons = []
            for fixture in report["fixtures"]:
                for observed in fixture["probes"]:
                    wanted = expected[fixture["fixture"]][observed["consumer"]]
                    comparisons.append({"fixture": fixture["fixture"], "consumer": observed["consumer"],
                                        "expected_acceptance": wanted, "observed_acceptance": observed["accepted"],
                                        "matches": observed["accepted"] is wanted})
            report["comparisons"] = comparisons
            report["checks_total"] = len(comparisons)
            report["checks_passed"] = sum(row["matches"] for row in comparisons)
            ok = report["checks_total"] == report["checks_passed"]
            report["status"] = "PASS_TEACHING_MATRIX_ONLY" if ok else "FAIL_TEACHING_MATRIX"
        else:
            readers = ("legacy", "current") if args.consumer == "both" else (args.consumer,)
            report.update(inspect_fixture(args.fixture, readers, expectation))
            ok = all(row["accepted"] for row in report["probes"])
            report["status"] = "PASS_SELECTED_CONSUMERS_ONLY" if ok else "FAIL_SELECTED_CONSUMERS"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if ok else 1
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "FAIL_INPUT", "error": type(exc).__name__, "detail": str(exc)}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
