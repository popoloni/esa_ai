"""Run the CP11 owner checks into a NEW evidence directory."""
import argparse
import json
from pathlib import Path
import sys
from evolution_core import ROOT, SUCCESS, evaluate_evolution


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New directory; earlier evidence is never replaced")
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--reference", action="store_true")
    selector.add_argument("--unsafe-control", action="store_true")
    parser.add_argument("--receipt", type=Path, help="Earlier EVOLUTION_RESULT.json whose source and evidence must still match")
    parser.add_argument("--scope-baseline", type=Path)
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        parser.error("--output already exists; choose a fresh evidence directory")
    try:
        result = evaluate_evolution(ROOT, args.reference, args.unsafe_control, args.output,
                                    args.receipt, args.scope_baseline)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == SUCCESS else 1


if __name__ == "__main__":
    sys.exit(main())
