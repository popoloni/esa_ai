"""Read-only reservation report command line interface."""

import argparse
import json
import sqlite3
import sys

import reservation_report


def _positive_integer(value):
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(prog="reservation_cli", allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", allow_abbrev=False)
    inspect.add_argument("--database", required=True)
    inspect.add_argument("--reservation-id", required=True, type=_positive_integer)
    args = parser.parse_args(argv)

    try:
        report = reservation_report.build_report(args.database, args.reservation_id)
    except (sqlite3.Error, OSError) as error:
        print(f"reservation_cli: storage error: {error}", file=sys.stderr)
        return 2

    print(json.dumps(report))
    return 0 if report["found"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
