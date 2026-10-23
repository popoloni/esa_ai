"""Record actual local CP13 attempts and explicitly synthetic scenario acceptance."""
import argparse
import json
from pathlib import Path
import sys
from measurement_core import rehearse_measurement, RECORDED


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--incident-rehearsal", type=Path, required=True)
    parser.add_argument("--transfer-session", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="NEW evidence directory")
    parser.add_argument("--reference", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = rehearse_measurement(args.incident_rehearsal, args.transfer_session, args.output, reference=args.reference)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == RECORDED else 1


if __name__ == "__main__":
    sys.exit(main())
