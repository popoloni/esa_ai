"""Operate one known CP11 candidate on a reader-owned synthetic SQLite file."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys
from evolution_core import ROOT, CANDIDATE, REFERENCE, operate
from scope_guard import check_integrity


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, type=Path)
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--reference", action="store_true")
    selector.add_argument("--candidate", type=Path)
    sub = parser.add_subparsers(dest="operation", required=True)
    sub.add_parser("init")
    decide = sub.add_parser("decide")
    decide.add_argument("--key", required=True)
    decide.add_argument("--amount", required=True)
    decide.add_argument("--beneficiary", required=True)
    decide.add_argument("--policy")
    activate = sub.add_parser("activate")
    activate.add_argument("--policy", required=True)
    for name in ("replay", "recompute"):
        command = sub.add_parser(name)
        command.add_argument("--key", required=True)
    reevaluate = sub.add_parser("reevaluate")
    reevaluate.add_argument("--from-key", required=True)
    reevaluate.add_argument("--key", required=True)
    reevaluate.add_argument("--policy", required=True)
    migrate = sub.add_parser("migrate")
    migrate.add_argument("--provenance", type=Path, required=True)
    args = parser.parse_args(argv)
    result = {"status": "FAIL", "operation": args.operation, "payment_authorized": False,
              "real_release_authorized": False}
    try:
        problems = check_integrity(ROOT)
        if problems:
            raise ValueError("PROTECTED_INTEGRITY:" + ",".join(problems))
        source = args.candidate or ROOT / (REFERENCE if args.reference else CANDIDATE)
        result["result"] = operate(source, args.db, args.operation, vars(args), ROOT)
        result["status"] = "OK"
    except sqlite3.IntegrityError:
        result["error"] = "SQLITE_INTEGRITY"
    except sqlite3.OperationalError as exc:
        result["error"] = "SQLITE_BUSY" if "locked" in str(exc).lower() else "SQLITE_OPERATIONAL"
    except Exception as exc:
        result["error"] = getattr(exc, "code", str(exc) if isinstance(exc, ValueError) else type(exc).__name__)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
