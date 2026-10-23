#!/usr/bin/env python3
"""Chapter entry cards and non-destructive study copies. Never grants acceptance."""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "reader_side/tools"))
from scope_guard import CHAPTER_EDIT_PATHS, check_integrity

DATA = ROOT / "navigation"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_findings(root=ROOT):
    findings = check_integrity(root)
    recorded = read_json(root / "navigation/starter_state.json")
    for rel, digest in recorded["candidate_sha256"].items():
        path = root / rel
        if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            findings.append("NOT_RELEASE_STARTER:" + rel)
    return findings


def cards():
    rows = read_json(DATA / "chapter_cards.json")["chapters"]
    if [r["chapter"] for r in rows] != list(range(1, 15)):
        raise ValueError("chapter cards must cover 1 through 14 exactly once")
    for row in rows:
        profile = f"CP{row['chapter']:02}"
        expected = sorted("repo/" + rel for rel in CHAPTER_EDIT_PATHS[profile])
        if row["editable_paths"] != expected:
            raise ValueError("card scope differs from protected profile: " + profile)
    return rows


def show(chapter, as_json=False):
    card = cards()[chapter - 1]
    if as_json:
        print(json.dumps(card, indent=2))
        return
    print(f"CHAPTER {chapter}: {card['title']}\n")
    for label, field in [("Input state", "input_state"), ("Cumulative prerequisite", "prerequisite"),
                         ("Supplied starter outcome", "starter_outcome"),
                         ("Local acceptance boundary", "acceptance_boundary"),
                         ("Decisions still pending", "pending_decisions"),
                         ("Continue", "continuation"), ("Recover", "recovery")]:
        print(label + ": " + card[field] + "\n")
    for label, field in [("Editable paths", "editable_paths"), ("Before editing", "before_edit"),
                         ("Candidate checks", "candidate_checks"), ("Worked-example route", "reference_checks")]:
        print(label + ":")
        for line in card[field]:
            print("  " + line)
        print()
    for exercise in card.get("optional_practice", []):
        print("Additional practice: " + exercise["title"])
        print("  " + exercise["command"])
        print("  " + exercise["boundary"] + "\n")
    print("Commands are run from the companion copy. Replace NEW names with unused session names.")
    print("A worked example does not repair or accept your current candidates.")


def prepare(chapter, requested):
    requested = requested.expanduser().absolute()
    # A symlinked ancestor can redirect a future copy. Reject before resolving.
    if any(path.is_symlink() for path in [requested, *requested.parents]):
        raise ValueError("destination and its ancestors must not be symlinks")
    destination = requested.resolve()
    if destination.exists() or destination.is_relative_to(ROOT):
        raise ValueError("choose a NEW directory outside this companion")
    findings = source_findings()
    if findings:
        raise ValueError("new study copies require the unchanged release starter; continue current work with 'show', or extract a fresh release: " + ", ".join(findings))
    if chapter == 1:
        completed = subprocess.run([sys.executable, str(ROOT / "reader_side/tools/prepare_chapter01.py"),
                                    "--destination", str(destination)], cwd=ROOT, check=False)
        if completed.returncode:
            raise ValueError("Chapter 1 preparation failed; inspect its report and retain any partial output")
    else:
        # Keep all original exercise candidates, including their deliberate faults.
        shutil.copytree(ROOT, destination, symlinks=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".venv"))
    if check_integrity(destination):
        raise ValueError("copied protected integrity differs; retain the copy for diagnosis")
    entry = {"schema": "reader-entry/v1", "chapter": chapter,
             "release": read_json(DATA / "starter_state.json")["release"],
             "mode": "CP01_FAULTY_STARTER" if chapter == 1 else "FRESH_STUDY_STARTER",
             "source_companion": str(ROOT),
             "earlier_candidate_readiness": "NOT_ESTABLISHED",
             "human_acceptance": "PENDING", "reference_solutions_installed": False,
             "meaning": "A new study copy. For cumulative work, preserve and continue your existing copy; no prior decision is accepted by this entry command."}
    (destination / "READER_ENTRY.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    print("Prepared " + str(destination))
    print(f"From that directory run: python3 reader_start.py show {chapter}")


def doctor():
    cards()
    findings = check_integrity()
    git = shutil.which("git")
    git_version = None
    merge_tree_supported = False
    if git:
        git_version = subprocess.run([git, "--version"], capture_output=True, text=True, check=False).stdout.strip()
        help_run = subprocess.run([git, "merge-tree", "-h"], capture_output=True, text=True, check=False)
        merge_tree_supported = "--write-tree" in help_run.stdout + help_run.stderr
    ready = not findings and sys.version_info >= (3, 10) and merge_tree_supported
    report = {"schema": "reader-doctor/v1", "status": "PASS_PREREQUISITES_ONLY" if ready else "ACTION_REQUIRED",
              "python": platform.python_version(), "platform": platform.platform(),
              "git": git_version, "git_merge_tree_write_tree": merge_tree_supported,
              "protected_findings": findings, "chapter_cards": 14,
              "release_starter_findings": source_findings(),
              "meaning": "Prerequisite and source checks, not candidate readiness, interpreter certification or human acceptance. Chapter 13 real pilot has additional host, delay and reviewer requirements."}
    print(json.dumps(report, indent=2))
    return 0 if ready else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    view = subs.add_parser("show", help="Display scope, state, commands and recovery for a chapter")
    view.add_argument("chapter", type=int, choices=range(1, 15)); view.add_argument("--json", action="store_true")
    new = subs.add_parser("new", help="Make a NEW study copy from an unchanged release starter")
    new.add_argument("chapter", type=int, choices=range(1, 15)); new.add_argument("--destination", type=Path, required=True)
    subs.add_parser("doctor", help="Check prerequisites and integrity without installing anything")
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            return doctor()
        if args.command == "show":
            show(args.chapter, args.json)
        else:
            prepare(args.chapter, args.destination)
        return 0
    except (ValueError, OSError) as exc:
        print("Reader entry failed: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
