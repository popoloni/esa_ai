"""Owner-run human-pilot records or explicitly synthetic clock calibration."""
import argparse
import json
from pathlib import Path
import sys
from learning_pilot_core import (start_trial, submit_answer, release_retention,
    release_transfer, record_score, adjudicate, pilot_status, calibrate)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    start = sub.add_parser("start")
    start.add_argument("--transfer-session", required=True, type=Path)
    start.add_argument("--owner-state", required=True, type=Path)
    start.add_argument("--trial-output", required=True, type=Path)
    start.add_argument("--participant", required=True)
    start.add_argument("--reviewer", required=True, action="append")
    start.add_argument("--coordinator", required=True)
    start.add_argument("--attest-no-prior-transfer-exposure", action="store_true")
    for name in ("submit-baseline", "submit-retention", "submit-transfer", "score", "adjudicate"):
        command = sub.add_parser(name)
        command.add_argument("--owner-state", required=True, type=Path)
        command.add_argument("--file", required=True, type=Path)
        if name == "score":
            command.add_argument("--reviewer", required=True)
    for name in ("release-retention", "release-transfer", "status"):
        command = sub.add_parser(name)
        command.add_argument("--owner-state", required=True, type=Path)
    calibration = sub.add_parser("calibrate")
    calibration.add_argument("--transfer-session", required=True, type=Path)
    calibration.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == "start":
            result = start_trial(args.transfer_session, args.owner_state, args.trial_output, args.participant,
                                 args.reviewer, args.coordinator, args.attest_no_prior_transfer_exposure)
        elif args.action.startswith("submit-"):
            result = submit_answer(args.owner_state, args.action.removeprefix("submit-"), args.file)
        elif args.action == "release-retention":
            result = release_retention(args.owner_state)
        elif args.action == "release-transfer":
            result = release_transfer(args.owner_state)
        elif args.action == "score":
            result = record_score(args.owner_state, args.reviewer, args.file)
        elif args.action == "adjudicate":
            result = adjudicate(args.owner_state, args.file)
        elif args.action == "status":
            result = pilot_status(args.owner_state)
        else:
            result = calibrate(args.transfer_session, args.output)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        result = {"status": "FAIL", "error": str(exc), "error_type": type(exc).__name__,
                  "human_competence": "NOT_ESTABLISHED_BY_AUTOMATION"}
    print(json.dumps(result, indent=2))
    return 1 if result.get("status") == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
