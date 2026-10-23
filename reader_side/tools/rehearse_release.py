"""Materialize a local Git merge candidate and rehearse exact artifact rollback.

This creates new reader-owned evidence only. --reference installs the earlier
worked examples inside the new disposable copy, never the caller's candidates.
"""
import argparse
import json
from pathlib import Path
import sys
from release_core import rehearse


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="New rehearsal directory")
    parser.add_argument("--reference", action="store_true", help="Use protected prior-chapter worked examples inside the disposable copy")
    parser.add_argument("--teaching-operator", action="store_true", help="Add the explicitly supplied operator_view.py in the candidate commit; prior artifact lacks it")
    args = parser.parse_args(argv)
    try:
        result = rehearse(args.output, reference=args.reference, teaching_operator=args.teaching_operator)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "READY_FOR_DOSSIER_REVIEW" else 1


if __name__ == "__main__":
    sys.exit(main())
