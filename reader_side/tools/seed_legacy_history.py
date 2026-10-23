"""Create an explicitly synthetic, NEW brownfield database and its provenance."""
import argparse
import json
from pathlib import Path
import sys
from evolution_core import ROOT, seed_legacy
from scope_guard import check_integrity


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixture", choices=["complete", "ambiguous", "wrong_outcome"], default="complete")
    args = parser.parse_args(argv)
    try:
        problems = check_integrity(ROOT)
        if problems:
            raise ValueError("PROTECTED_INTEGRITY:" + ",".join(problems))
        result = seed_legacy(args.output, args.fixture, ROOT)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
