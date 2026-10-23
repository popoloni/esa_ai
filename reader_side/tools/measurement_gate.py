"""Review exact local telemetry, scenario costs and bounded tool-pilot decisions."""
import argparse
import json
from pathlib import Path
import sys
from measurement_core import evaluate_measurement, SUCCESS


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measurement-session", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="NEW evidence directory")
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--reference", action="store_true")
    selector.add_argument("--unsafe-control", action="store_true")
    parser.add_argument("--scope-baseline", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args(argv)
    try:
        result = evaluate_measurement(args.measurement_session, reference=args.reference, unsafe=args.unsafe_control,
                                      output=args.output, receipt=args.receipt, scope_baseline=args.scope_baseline)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == SUCCESS else 1


if __name__ == "__main__":
    sys.exit(main())
