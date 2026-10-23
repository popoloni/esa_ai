"""One local synthetic process using CP12 deployment config and CP11 PolicyStore."""
import argparse
import json
from pathlib import Path
import sys
from incident_core import ROOT, CONFIG, HISTORY, service_event


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True, help="Existing owner-created CP12 workspace")
    parser.add_argument("--config", type=Path, default=ROOT / CONFIG)
    parser.add_argument("--history", type=Path, default=ROOT / HISTORY, help="Known current or protected CP11 source")
    parser.add_argument("--event-id", default="MANUAL_OBSERVATION")
    operations = parser.add_subparsers(dest="operation", required=True)
    operations.add_parser("inspect")
    command = operations.add_parser("activate")
    command.add_argument("--policy", required=True)
    command = operations.add_parser("decide")
    command.add_argument("--key", required=True)
    command.add_argument("--amount", required=True)
    command.add_argument("--beneficiary", required=True)
    command.add_argument("--policy")
    for name in ("replay", "recompute"):
        command = operations.add_parser(name)
        command.add_argument("--key", required=True)
    args = parser.parse_args(argv)
    arguments = {key: value for key, value in vars(args).items()
                 if key not in {"workspace", "config", "history", "event_id", "operation"} and value is not None}
    result = service_event(args.workspace, args.config, args.history, args.operation, arguments, args.event_id)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
