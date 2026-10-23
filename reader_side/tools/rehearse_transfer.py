"""Reproduce a distinct policy-selection transfer case using actual CP12 evidence."""
import argparse
import json
from pathlib import Path
import sys
from learning_core import rehearse_transfer, TRANSFER_SUCCESS


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--learning-session", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="NEW evidence directory")
    parser.add_argument("--reference", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = rehearse_transfer(args.learning_session, args.output, reference=args.reference)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == TRANSFER_SUCCESS else 1


if __name__ == "__main__":
    sys.exit(main())
