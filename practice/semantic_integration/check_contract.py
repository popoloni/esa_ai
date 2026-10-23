"""Independent selected output contract, kept outside the candidate Git tree."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

EXPECTED = {
    "STANDARD_QUEUE": "Recommended standard queue | Routing only; no payment approval.",
    "HUMAN_REVIEW": "Recommended human review | Routing only; no payment approval.",
    "REJECTED": "Rejected | Routing only; no payment approval.",
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.source.resolve()))
    spec = importlib.util.spec_from_file_location("semantic_view", args.source / "view.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    observations = []
    for route, expected in EXPECTED.items():
        try:
            actual = module.render(route)
            observations.append({"route": route, "expected": expected, "actual": actual,
                                 "passed": actual == expected})
        except Exception as exc:
            observations.append({"route": route, "expected": expected,
                                 "exception": type(exc).__name__, "passed": False})
    try:
        module.render("UNRECOGNIZED")
        invalid_rejected = False
    except KeyError:
        invalid_rejected = True
    observations.append({"route": "UNRECOGNIZED", "expected": "KeyError",
                         "passed": invalid_rejected})
    failures = sum(not item["passed"] for item in observations)
    print(json.dumps({"status": "PASS" if failures == 0 else "FAIL",
                      "cases": len(observations), "failures": failures,
                      "observations": observations}, indent=2))
    return int(failures != 0)

if __name__ == "__main__":
    raise SystemExit(main())

