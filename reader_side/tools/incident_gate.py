"""Validate CP12 diagnosis and recovery on NEW copies of retained incident state."""
import argparse
import json
from pathlib import Path
import sys
from incident_core import SUCCESS, evaluate_incident


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rehearsal", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New directory outside the rehearsal and prior receipt directories")
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--reference", action="store_true")
    selector.add_argument("--unsafe-control", action="store_true")
    parser.add_argument("--scope-baseline", type=Path)
    parser.add_argument("--receipt", type=Path, help="Prior INCIDENT_RESULT.json; require unchanged sources and evidence")
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        parser.error("--output already exists; choose a fresh directory")
    try:
        result = evaluate_incident(args.rehearsal, reference=args.reference, unsafe=args.unsafe_control,
                                   output=args.output, receipt=args.receipt, scope_baseline=args.scope_baseline)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == SUCCESS else 1


if __name__ == "__main__":
    sys.exit(main())
