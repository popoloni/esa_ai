"""Read-only CLI for the reservation report (INTEGRATION-G3/v1, contribution B).

All report semantics live in reservation_report.build_report; this module only
parses arguments, prints the returned object as JSON and maps it to an exit code.
"""
import argparse
import json
import sqlite3
import sys

import reservation_report


def _positive_int(raw):
    try:
        value = int(raw)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a positive integer: {raw!r}")
    if value <= 0:
        raise argparse.ArgumentTypeError(f"not a positive integer: {raw!r}")
    return value


def _parser():
    parser = argparse.ArgumentParser(prog="reservation_cli", allow_abbrev=False)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", allow_abbrev=False,
                             help="print the report for one reservation")
    inspect.add_argument("--database", required=True, metavar="PATH")
    inspect.add_argument("--reservation-id", required=True, type=_positive_int,
                         metavar="POSITIVE_INTEGER")
    return parser


def main(argv=None):
    try:
        args = _parser().parse_args(argv)
    except SystemExit as exc:  # argparse: usage errors exit 2, --help exits 0
        return exc.code if isinstance(exc.code, int) else 2
    try:
        report = reservation_report.build_report(args.database, args.reservation_id)
    except (sqlite3.Error, OSError) as exc:
        print(f"error: cannot read reservation storage: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0 if report.get("found") else 3


if __name__ == "__main__":
    raise SystemExit(main())
