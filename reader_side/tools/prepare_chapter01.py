"""Create a new cumulative teaching copy with the original Chapter 1 routing bug.

Only the new copy's editable router is replaced. Reader-owned sources and the
delivered companion remain unchanged. This is preparation, not a sandbox.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys

from scope_guard import check_candidate_path, check_integrity


ROOT = Path(__file__).resolve().parents[2]
ROUTER = "repo/src/treasury/routing.py"
UNSAFE = "reader_side/routing/unsafe_routing_fixture.py"


def inventory(root):
    """Inventory source bytes; Python cache files do not belong to the exercise."""
    result = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            result[relative.as_posix()] = "SYMLINK"
        elif path.is_file():
            result[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def run(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, type=Path,
                        help="New full working-copy directory outside this companion")
    args = parser.parse_args(argv)
    requested = args.destination.expanduser()
    if requested.exists() or requested.is_symlink():
        parser.error("--destination must not already exist")
    destination = requested.resolve()
    if destination.is_relative_to(ROOT):
        parser.error("--destination must be outside the source companion")
    if destination.exists() or destination.is_symlink():
        parser.error("--destination must not already exist")
    before = inventory(ROOT)
    findings = check_integrity()
    try:
        check_candidate_path("src/treasury/routing.py", chapter="CP01")
        if findings:
            raise ValueError("source protected integrity failed: " + ",".join(findings))
        faulty_bytes = (ROOT / UNSAFE).read_bytes()
        shutil.copytree(ROOT, destination, symlinks=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        router = check_candidate_path("src/treasury/routing.py",
                                      repo=destination / "repo", chapter="CP01")
        router.write_bytes(faulty_bytes)
        copied = inventory(destination)
        source_after = inventory(ROOT)
        changed = sorted(path for path in set(before) | set(copied)
                         if before.get(path) != copied.get(path))
        expected_changes = [] if before.get(ROUTER) == copied.get(ROUTER) else [ROUTER]
        findings.extend(check_integrity(destination))
        if changed != expected_changes:
            findings.append("UNEXPECTED_COPY_DIFFERENCE")
        if source_after != before:
            findings.append("SOURCE_COMPANION_CHANGED")
        report = {
            "schema": "chapter01-preparation/v1",
            "status": "FAIL" if findings else "PASS",
            "source_companion": str(ROOT), "destination": str(destination),
            "installed_candidate": ROUTER,
            "candidate_sha256": hashlib.sha256(faulty_bytes).hexdigest(),
            "copied_source_files": len(copied), "changed_source_paths": changed,
            "reader_side_unchanged": all(before.get(path) == copied.get(path)
                                         for path in set(before) | set(copied)
                                         if path.startswith("reader_side/")),
            "source_companion_unchanged": source_after == before,
            "findings": findings,
            "meaning": "A new full cumulative lab with only the CP01 editable router set to its known faulty starter; no payment or release authority.",
        }
    except (OSError, ValueError, PermissionError) as exc:
        report = {"schema": "chapter01-preparation/v1", "status": "FAIL",
                  "destination": str(destination),
                  "findings": findings + [type(exc).__name__ + ":" + str(exc)]}
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(run())
