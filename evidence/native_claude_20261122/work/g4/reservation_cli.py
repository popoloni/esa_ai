"""Read-only reservation CLI (INTEGRATION-G3/v1, contribution B)."""
import argparse
import json
import sqlite3
import sys

import reservation_report


def _positive_int(raw):
    try:
        value = int(raw)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid positive integer: {raw!r}")
    if value < 1:
        raise argparse.ArgumentTypeError(f"invalid positive integer: {raw!r}")
    return value


def _parser():
    parser = argparse.ArgumentParser(prog="reservation_cli")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", help="print a read-only reservation report")
    inspect.add_argument("--database", required=True, metavar="PATH")
    inspect.add_argument("--reservation-id", required=True, type=_positive_int,
                         metavar="POSITIVE_INTEGER")
    return parser


def main(argv=None):
    try:
        args = _parser().parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    try:
        report = reservation_report.build_report(args.database, args.reservation_id)
    except (sqlite3.Error, OSError) as exc:
        print(f"error: cannot read reservation storage: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(report) + "\n")
    return 0 if report["found"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
