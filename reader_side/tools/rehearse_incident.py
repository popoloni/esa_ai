"""Reproduce INC-012 in NEW local state and evidence; never a production deployment."""
import argparse
import json
from pathlib import Path
import sys
from incident_core import REPRODUCED, rehearse_incident


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New directory; prior incident evidence is retained")
    parser.add_argument("--reference", action="store_true", help="Use the protected CP11 worked example, not current candidate readiness")
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        parser.error("--output already exists; choose a fresh directory")
    try:
        result = rehearse_incident(args.output, reference=args.reference)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == REPRODUCED else 1


if __name__ == "__main__":
    sys.exit(main())
