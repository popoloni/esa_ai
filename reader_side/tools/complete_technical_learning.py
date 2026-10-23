"""Report CP10 technical exercise completion separately from release authority.

This reader-run check reuses the existing release verifier. It does not create,
edit, replace or grant an owner decision. A source without an applicable decision
must leave both decision references null. The nested release verdict remains a
failure, while fresh technical evidence can complete the technical exercise.
"""
import argparse
import json
from pathlib import Path
import sys

from release_core import ROOT, DOSSIER, evaluate_release, digest, read_json

SUCCESS = "TECHNICAL_LEARNING_COMPLETE"
# These three findings concern a decision that was never issued for this source.
# Every other finding, including self-approval, stale evidence and bad behavior,
# remains a technical-learning failure. The original release verdict is retained.
PENDING_DECISION_FINDINGS = frozenset({
    "SOURCE_NOT_COVERED_BY_SYNTHETIC_OWNER_DECISION",
    "REVIEW_DECISION_MISSING",
    "EXPLICIT_LOCAL_RELEASE_AUTHORIZATION_MISSING",
})


def evaluate_completion(rehearsal, scope_baseline, root=ROOT):
    root = Path(root).resolve()
    dossier = root / DOSSIER
    release = evaluate_release(dossier, rehearsal, root=root,
                               scope_baseline=scope_baseline)
    result = {
        "schema": "cp10-technical-completion/v1",
        "status": "TECHNICAL_LEARNING_INCOMPLETE",
        "completed_component": "CP10_TECHNICAL_EXERCISE",
        "findings": [],
        "release_assessment": release,
        "real_human_acceptance": False,
        "real_release_authorized": False,
        "payment_authorized": False,
        "meaning": (
            "This receipt assesses selected current-source checks, exact "
            "integration/artifact identity, dossier technical links, CP10 edit "
            "scope and local rollback. No owner decision is issued. "
            "This is not a measured human-learning or competence result."
        ),
    }
    findings = result["findings"]
    if scope_baseline is None:
        findings.append("BEFORE_EDIT_SCOPE_BASELINE_REQUIRED")
    if release.get("rehearsal_mode") != "WORKING_CANDIDATES":
        findings.append("CURRENT_WORKING_CANDIDATES_REQUIRED")
    if release.get("ci_status") != "PASS":
        findings.append("CURRENT_TECHNICAL_CHECKS_NOT_PASSING")
    if release.get("rollback_status") != "PASS":
        findings.append("LOCAL_ROLLBACK_NOT_PASSING")
    try:
        value = read_json(dossier)
        pending = ("review_decision_id" in value and "release_decision_id" in value
                   and value.get("review_decision_id") is None
                   and value.get("release_decision_id") is None)
        result["decision_references"] = (
            "UNISSUED" if pending else "ASSESSED_BY_ORIGINAL_RELEASE_GATE"
        )
        result["dossier_sha256"] = digest(dossier)
        result["scope_baseline_sha256"] = digest(scope_baseline) if scope_baseline else None
        for finding in release.get("findings", []):
            if not (pending and finding in PENDING_DECISION_FINDINGS):
                findings.append(finding)
        # Do not treat a missing or truncated release assessment as success.
        if not release.get("binding") or release.get("edit_scope_checked") is not True:
            findings.append("COMPLETE_CURRENT_EVIDENCE_REQUIRED")
        result["binding"] = release.get("binding")
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        findings.append("COMPLETION_ERROR:" + type(exc).__name__ + ":" + str(exc))
    if not findings:
        result["status"] = SUCCESS
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rehearsal", required=True, type=Path)
    parser.add_argument("--scope-baseline", required=True, type=Path,
                        help="Reader-owned CP10 baseline captured before dossier edits")
    parser.add_argument("--output", type=Path, help="New receipt; never overwrite prior evidence")
    args = parser.parse_args(argv)
    output = args.output.resolve() if args.output else None
    if args.output:
        if args.output.exists() or args.output.is_symlink():
            parser.error("--output already exists; preserve it and choose a new file")
        if output.is_relative_to(ROOT) and not output.is_relative_to(ROOT / "reader_side/evidence"):
            parser.error("--output must not replace candidate or protected source files")
        if output.is_relative_to(args.rehearsal.resolve()):
            parser.error("keep rehearsal evidence unchanged; write the receipt outside its directory")
    result = evaluate_completion(args.rehearsal, args.scope_baseline)
    body = json.dumps(result, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            with output.open("x", encoding="utf-8") as stream:
                stream.write(body)
        except FileExistsError:
            parser.error("--output already exists; preserve it and choose a new file")
    print(body, end="")
    return 0 if result["status"] == SUCCESS else 1


if __name__ == "__main__":
    sys.exit(main())
