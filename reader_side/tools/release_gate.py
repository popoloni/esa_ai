"""Review a Chapter 10 dossier against exact local CI and synthetic owner evidence."""
import argparse
import json
from pathlib import Path
import sys
from release_core import ROOT, DOSSIER, SUCCESS, evaluate_release


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rehearsal", required=True, type=Path)
    parser.add_argument("--candidate", type=Path, default=ROOT / DOSSIER)
    parser.add_argument("--scope-baseline", type=Path)
    parser.add_argument("--output", type=Path, help="Optional new verdict file; keep the earlier rehearsal evidence")
    args = parser.parse_args(argv)
    if args.output:
        if args.output.exists() or args.output.is_symlink():
            parser.error("--output already exists; choose a new verdict file to preserve earlier evidence")
        output = args.output.resolve()
        if output.is_relative_to(ROOT) and not output.is_relative_to(ROOT / "reader_side/evidence"):
            parser.error("--output must not replace candidate or protected source files")
        if output.is_relative_to(args.rehearsal.resolve()):
            parser.error("keep rehearsal evidence unchanged; write the verdict outside its directory")
    result = evaluate_release(args.candidate, args.rehearsal, scope_baseline=args.scope_baseline)
    body = json.dumps(result, indent=2) + "\n"
    if args.output:
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            with output.open("x", encoding="utf-8") as stream:
                stream.write(body)
        except FileExistsError:
            parser.error("--output already exists; choose a new verdict file to preserve earlier evidence")
    print(body, end="")
    return 0 if result["status"] == SUCCESS else 1


if __name__ == "__main__":
    sys.exit(main())
