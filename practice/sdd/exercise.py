"""Create a fresh editable copy of the two intentionally incomplete SDD artifacts."""
from pathlib import Path
import argparse
import shutil

PRACTICE = Path(__file__).resolve().parent
COMPANION = PRACTICE.parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=PRACTICE / "work")
    args = parser.parse_args()
    dest = args.out.absolute()
    resolved = dest.resolve()
    if dest.exists() or dest.is_symlink():
        parser.error("output already exists; choose a fresh directory to preserve your prior attempt")
    if resolved.is_relative_to(COMPANION) and not resolved.is_relative_to(PRACTICE / "work"):
        parser.error("inside the companion, output must be practice/sdd/work or a child of that directory")
    if any(p.is_symlink() for p in [dest, *dest.parents]):
        parser.error("output path may not contain a symlink")
    shutil.copytree(PRACTICE / "fixtures/before", dest)
    print(f"Created two authored, deliberately incomplete artifact sets in {dest}")
    print("Run check.py --artifacts <that directory>. Expected: one missing equality case per flow.")
    print("Edit only the two behavioral spec files. Shared inputs, core lab, and retained specimens stay unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
