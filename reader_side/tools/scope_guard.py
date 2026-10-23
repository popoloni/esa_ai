"""Owner-run chapter edit policy and protected integrity; not an OS sandbox.

The union supports cumulative regression tests. A chapter profile restricts a
particular exercise. Capture an owner-controlled baseline before editing and
compare it afterwards to detect actual out-of-scope changes. This neither
creates business authority nor protects against an actor who controls the
checker, its baseline, or its host process.
"""
from pathlib import Path, PurePosixPath
from hashlib import sha256
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT / "repo"
CHAPTER_EDIT_PATHS = {
    "CP01": {"src/treasury/routing.py"},
    "CP02": {"src/treasury/routing.py"},
    "CP03": {"engineering/discovery/assessment.json"},
    "CP04": {"engineering/specifications/explanation_alpha/specification.json"},
    "CP05": {"src/treasury/architecture/direct.py", "src/treasury/architecture/ports.py",
             "engineering/architecture/architecture_decision.json", "engineering/architecture/ADR-005.md"},
    "CP06": {"engineering/knowledge/context_packet.json", ".agents/skills/context-audit/SKILL.md"},
    "CP07": {"engineering/planning/delegation_plan.json", "engineering/planning/delegation_handoff.json"},
    "CP08": {"src/treasury/explanation_alpha.py", "engineering/implementation/implementation_report.json"},
    "CP09": {"engineering/verification/candidate.py", "engineering/verification/review.json"},
    "CP10": {"engineering/release/release_dossier.json"},
    "CP11": {"src/treasury/policy_history.py", "engineering/evolution/policy_delta.json"},
    "CP12": {"engineering/operations/deployment.json", "engineering/operations/incident_review.json"},
    "CP13": {"engineering/learning/transfer_review.json", "engineering/learning/team_knowledge.json"},
    "CP14": {"engineering/measurement/outcome_review.json", "engineering/measurement/tool_decision.json"},
}
# Optional extensions are materialized only in their isolated exercise copy.
# They are not missing baseline candidates in the CP01--14 chapter inventory.
OPTIONAL_EDIT_PATHS = {
    "TEACHING_LIFECYCLE": {"src/treasury/explanation_alpha.py", "src/treasury/operator_view.py"},
}
ALLOW_EDIT = set().union(*CHAPTER_EDIT_PATHS.values(), *OPTIONAL_EDIT_PATHS.values())
BASELINE = ROOT / "reader_side" / "protected_sha256.json"


def allowed_paths(chapter=None):
    if chapter is None:
        return ALLOW_EDIT
    if chapter in OPTIONAL_EDIT_PATHS:
        return OPTIONAL_EDIT_PATHS[chapter]
    if chapter not in CHAPTER_EDIT_PATHS:
        raise ValueError("unknown chapter profile: " + str(chapter))
    return CHAPTER_EDIT_PATHS[chapter]


def check_candidate_path(user_path: str, repo=REPO, chapter=None):
    if not isinstance(user_path, str) or not user_path or "\\" in user_path or "\0" in user_path:
        raise ValueError("invalid candidate path")
    parsed = PurePosixPath(user_path)
    if parsed.is_absolute() or any(p in (".", "..") for p in user_path.split("/")) or str(parsed) != user_path:
        raise ValueError("noncanonical or traversing path")
    if user_path not in allowed_paths(chapter):
        raise PermissionError(f"not allowed by {chapter or 'cumulative'} reader-side path policy: {user_path}")
    repo = Path(repo)
    target = repo / user_path
    if (any(p.is_symlink() for p in [repo, *[repo.joinpath(*parsed.parts[:i]) for i in range(1, len(parsed.parts) + 1)]])
            or not target.is_file() or repo.resolve() not in target.resolve().parents):
        raise PermissionError("symlink, missing or escaped target")
    return target


def _repo_inventory(root):
    inventory = {}
    for p in (Path(root) / 'repo').rglob('*'):
        if '__pycache__' in p.parts or p.suffix == '.pyc':
            continue
        if p.is_symlink():
            inventory[p.relative_to(Path(root) / 'repo').as_posix()] = 'SYMLINK'
        elif p.is_file():
            inventory[p.relative_to(Path(root) / 'repo').as_posix()] = sha256(p.read_bytes()).hexdigest()
    return inventory


def check_integrity(root=ROOT):
    root = Path(root)
    try:
        manifest = json.loads((root / 'reader_side/protected_sha256.json').read_text(encoding='utf-8'))
        if not isinstance(manifest, dict):
            return ['MANIFEST_NOT_OBJECT']
    except (OSError, ValueError) as exc:
        return ['MANIFEST_UNREADABLE:' + type(exc).__name__]
    mismatches = []
    for rel, expected in manifest.items():
        path = PurePosixPath(rel)
        if path.is_absolute() or '..' in path.parts or str(path) != rel:
            mismatches.append('MANIFEST_PATH:' + rel)
            continue
        p = root / rel
        if not p.is_file() or p.is_symlink() or sha256(p.read_bytes()).hexdigest() != expected:
            mismatches.append(rel)
    expected_repo = {rel for rel in manifest if rel.startswith('repo/')}
    expected_repo.update('repo/' + rel for rel in ALLOW_EDIT)
    for rel, digest in _repo_inventory(root).items():
        full = 'repo/' + rel
        if full not in expected_repo:
            mismatches.append('UNTRACKED:' + full)
        elif digest == 'SYMLINK':
            mismatches.append('SYMLINK:' + full)
    return sorted(set(mismatches))


def capture_edit_scope(chapter, root=ROOT):
    """Called by the reader before an exercise, after prior work is accepted locally."""
    root = Path(root)
    paths = allowed_paths(chapter)
    problems = check_integrity(root)
    if problems:
        raise ValueError('cannot capture with protected-integrity findings: ' + ','.join(problems))
    for path in paths:
        check_candidate_path(path, repo=root / 'repo', chapter=chapter)
    return {
        'schema': 'chapter-edit-baseline/v1',
        'chapter': chapter,
        'allowed_paths': sorted(paths),
        'protected_manifest_sha256': sha256((root / 'reader_side/protected_sha256.json').read_bytes()).hexdigest(),
        'repo_files': _repo_inventory(root),
        'meaning': 'Reader-owned before-edit snapshot of this working copy; does not grant business, merge or release authority.'
    }


def check_edit_scope(baseline_path, root=ROOT, chapter=None):
    root = Path(root)
    try:
        record = json.loads(Path(baseline_path).read_text(encoding='utf-8'))
        recorded_chapter = record.get('chapter')
        profile = chapter or recorded_chapter
        paths = allowed_paths(profile)
        if record.get('schema') != 'chapter-edit-baseline/v1' or recorded_chapter != profile:
            return ['EDIT_BASELINE_PROFILE_MISMATCH']
        if record.get('allowed_paths') != sorted(paths):
            return ['EDIT_BASELINE_POLICY_MISMATCH']
        expected = record.get('repo_files')
        if not isinstance(expected, dict) or not expected:
            return ['EDIT_BASELINE_FILES_MISSING']
        digest = sha256((root / 'reader_side/protected_sha256.json').read_bytes()).hexdigest()
        if record.get('protected_manifest_sha256') != digest:
            return ['EDIT_BASELINE_RELEASE_MISMATCH']
        current = _repo_inventory(root)
        findings = []
        for rel in sorted(set(expected) | set(current)):
            if expected.get(rel) != current.get(rel) and rel not in paths:
                findings.append('OUT_OF_SCOPE:' + rel)
        for rel in paths:
            try:
                check_candidate_path(rel, repo=root / 'repo', chapter=profile)
            except (ValueError, PermissionError) as exc:
                findings.append('INVALID_CANDIDATE:' + rel + ':' + str(exc))
        return findings
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        return ['EDIT_BASELINE_UNREADABLE:' + type(exc).__name__]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='*')
    parser.add_argument('--chapter', choices=sorted(set(CHAPTER_EDIT_PATHS) | set(OPTIONAL_EDIT_PATHS)))
    parser.add_argument('--capture', type=Path, help='Write an owner-controlled baseline before candidate edits')
    parser.add_argument('--baseline', type=Path, help='Check the actual changes since this baseline')
    args = parser.parse_args(argv)
    try:
        for path in args.paths:
            check_candidate_path(path, chapter=args.chapter)
        modified = check_integrity()
        if args.capture:
            if not args.chapter or args.baseline:
                raise ValueError('--capture requires --chapter and cannot be combined with --baseline')
            if args.capture.exists():
                raise ValueError('baseline already exists; keep it for the current edit session or choose a new file')
            record = capture_edit_scope(args.chapter)
            args.capture.parent.mkdir(parents=True, exist_ok=True)
            args.capture.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
            print('Captured before-edit baseline for ' + args.chapter + ': ' + str(args.capture))
        if args.baseline:
            modified.extend(check_edit_scope(args.baseline, chapter=args.chapter))
    except (PermissionError, ValueError, OSError) as exc:
        print('FAIL: ' + str(exc), file=sys.stderr)
        return 2
    if modified:
        print('FAIL: protected files or edit scope differ: ' + str(modified), file=sys.stderr)
        return 3
    print('PASS: requested path policy, protected hashes and supplied edit baseline')
    return 0


if __name__ == '__main__':
    sys.exit(main())
