"""Offline Chapter 10 review and artifact-selection rehearsal.

The protected records describe synthetic roles and decisions. They are not an
identity service, a signature system, a sandbox or actual human acceptance.
Only known teaching code runs, in fresh local processes, without network use.
"""
from pathlib import Path, PurePosixPath
from hashlib import sha256
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import zipfile

from scope_guard import check_integrity, check_candidate_path, check_edit_scope
from integration_core import INPUT_PAIRS, SHARED_INPUTS

ROOT = Path(__file__).resolve().parents[2]
DOSSIER = "repo/engineering/release/release_dossier.json"
REFERENCE = "reader_side/reference_solution/ch10/release_dossier.json"
UNSAFE = "reader_side/release/unsafe_dossier.json"
PRODUCER = "repo/src/treasury/explanation_alpha.py"
OPERATOR_ADDITION = "repo/src/treasury/operator_view.py"
SUCCESS = "PASS_LOCAL_RELEASE_REHEARSAL_ONLY"
SCOPE = "LOCAL_SYNTHETIC_PRESENTATION_EXPERIMENT"
OWNER_FILES = ("scenario.json", "mock_pr.json", "owner_decisions.json")
CHECK_FILES = {
    "CI-MERGE-001": "evidence/merge.json",
    "CI-ROUTING-001": "evidence/acceptance.json",
    "CI-INTEGRATION-001": "evidence/integration.json",
    "CI-ARTIFACT-001": "evidence/artifact.json",
}
ARTIFACT_FILES = {"current": "artifacts/current.zip", "previous": "artifacts/previous.zip"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(value))


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _environment():
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env.update(PYTHONDONTWRITEBYTECODE="1", GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0", LC_ALL="C",
               GIT_AUTHOR_NAME="Synthetic teaching owner", GIT_AUTHOR_EMAIL="teaching@example.invalid",
               GIT_COMMITTER_NAME="Synthetic teaching owner", GIT_COMMITTER_EMAIL="teaching@example.invalid",
               GIT_AUTHOR_DATE="2026-10-20T00:00:00+0000", GIT_COMMITTER_DATE="2026-10-20T00:00:00+0000")
    return env


def _git(repo, *args, binary=False):
    command = ["git", "-c", "core.hooksPath=" + os.devnull,
               "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false", "-C", str(repo), *args]
    result = subprocess.run(command, env=_environment(), capture_output=True,
                            text=not binary, timeout=60)
    if result.returncode:
        error = result.stderr.decode(errors="replace") if binary else result.stderr
        raise ValueError("GIT:" + " ".join(args[:2]) + ":" + error.strip())
    return result.stdout if binary else result.stdout.strip()


def source_manifest(root, exclude_dossier=False):
    result = {}
    for path in sorted(Path(root).rglob("*")):
        relative = path.relative_to(root)
        if any(part in {".git", "__pycache__"} for part in relative.parts) or path.suffix == ".pyc":
            continue
        if relative.parts[:2] == ("reader_side", "evidence") or (exclude_dossier and relative.as_posix() == DOSSIER):
            continue
        if path.is_symlink():
            raise ValueError("SOURCE_SYMLINK:" + relative.as_posix())
        if path.is_file():
            result[relative.as_posix()] = digest(path)
    return result


def _selection_inputs(root, reference):
    paths = set(SHARED_INPUTS)
    paths.update(pair[int(reference)] for pair in INPUT_PAIRS.values())
    # The later experiment changes this source context, but CP10 still reviews
    # only its separately scoped presentation artifact, never policy-v2 release.
    paths.update(("repo/src/treasury/policy_history.py",
                  "repo/engineering/evolution/policy_delta.json",
                  "reader_side/evolution/policy_catalog.json",
                  "reader_side/evolution/change_context.json",
                  "repo/engineering/operations/deployment.json",
                  "repo/engineering/operations/incident_review.json",
                  "repo/engineering/learning/transfer_review.json",
                  "repo/engineering/learning/team_knowledge.json",
                  "repo/engineering/measurement/outcome_review.json",
                  "repo/engineering/measurement/tool_decision.json"))
    if (root / OPERATOR_ADDITION).is_file():
        paths.add(OPERATOR_ADDITION)
    return {name: digest(root / name) for name in sorted(paths)}


def _owner_inputs(root):
    return [read_json(root / "reader_side/release" / name) for name in OWNER_FILES]


def _owner_hashes(root):
    return {name: digest(root / "reader_side/release" / name) for name in OWNER_FILES}


def _copy_source(root, target, reference):
    for name in source_manifest(root, exclude_dossier=True):
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((root / name).read_bytes())
    if reference:
        for candidate, solution in INPUT_PAIRS.values():
            (target / candidate).write_bytes((root / solution).read_bytes())


def _tree_files(repo, commit):
    data = _git(repo, "archive", "--format=tar", commit, binary=True)
    files = {}
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive.getmembers():
            relative = PurePosixPath(member.name)
            if relative.is_absolute() or ".." in relative.parts or not (member.isfile() or member.isdir()):
                raise ValueError("UNSAFE_GIT_ARCHIVE_MEMBER")
            if member.isfile():
                files[member.name] = archive.extractfile(member).read()
    return files


def _materialize(repo, commit, destination):
    destination.mkdir(parents=True, exist_ok=False)
    data = _git(repo, "archive", "--format=tar", commit, binary=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive.getmembers():
            relative = PurePosixPath(member.name)
            if relative.is_absolute() or ".." in relative.parts or not (member.isfile() or member.isdir()):
                raise ValueError("UNSAFE_GIT_ARCHIVE_MEMBER")
            path = destination / member.name
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.extractfile(member).read())


def _artifact_bytes(repo, commit, kind):
    """Package committed Treasury bytes deterministically, never the worktree."""
    files = {name.removeprefix("repo/"): data for name, data in _tree_files(repo, commit).items()
             if name.startswith("repo/src/treasury/") and name.endswith(".py")
             and name != "repo/src/treasury/policy_history.py"}
    if "src/treasury/explanation_alpha.py" not in files:
        raise ValueError("ARTIFACT_PRODUCER_MISSING")
    manifest = {"schema": "cp10-artifact/v1", "kind": kind, "git_commit": commit,
                "git_tree": _git(repo, "rev-parse", commit + "^{tree}"),
                "files_sha256": {name: sha256(data).hexdigest() for name, data in files.items()},
                "meaning": "Synthetic local presentation artifact; not a production deployment."}
    files["MANIFEST.json"] = json_bytes(manifest)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(files.items()):
            item = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            item.create_system = 3
            item.external_attr = 0o100644 << 16
            item.compress_type = zipfile.ZIP_STORED
            archive.writestr(item, data)
    return buffer.getvalue()


SMOKE_PROGRAM = r'''
from pathlib import Path
import json,sys
sys.path.insert(0,sys.argv[1])
from treasury.explanation_alpha import build_explanation
cases=json.loads(Path(sys.argv[2]).read_text())
if isinstance(cases,dict): cases=cases.get('cases',[])
labels={'STANDARD_QUEUE':'RECOMMENDED_STANDARD_QUEUE','HUMAN_REVIEW':'RECOMMENDED_HUMAN_REVIEW','REJECTED':'REJECTED'}
findings=[]
for case in cases:
    try:
        out=build_explanation(case['input_amount_eur'])
        expected={'route':case['expected_route'],'reason_code':case['expected_reason'],
                  'policy_version':'BR-001/v1','payment_authorized':False,
                  'notice':'ROUTING_ONLY_NOT_PAYMENT_APPROVAL','benefit_status':'HYPOTHESIS_NOT_VALIDATED'}
        for key,value in expected.items():
            if out.get(key)!=value or (key=='payment_authorized' and out.get(key) is not False):
                findings.append(case['id']+':'+key)
        if sys.argv[3]=='current' and out.get('status_label')!=labels[case['expected_route']]:
            findings.append(case['id']+':status_label')
        if sys.argv[3]=='previous' and 'status_label' in out:
            findings.append(case['id']+':unexpected_new_presentation_label')
    except Exception as exc: findings.append(case['id']+':'+type(exc).__name__)
print(json.dumps({'status':'PASS' if cases and not findings else 'FAIL','cases':len(cases),'findings':findings}))
raise SystemExit(1 if findings or not cases else 0)
'''


def artifact_smoke(path, expected_hash, root=ROOT, kind="current"):
    path, root = Path(path), Path(root)
    if digest(path) != expected_hash:
        return {"status": "FAIL", "cases": 0, "findings": ["ARTIFACT_DIGEST_MISMATCH"]}
    with tempfile.TemporaryDirectory(prefix="cp10-artifact-") as directory:
        directory = Path(directory)
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            manifest = json.loads(archive.read("MANIFEST.json"))
            files = manifest.get("files_sha256", {})
            if manifest.get("kind") != kind or set(names) != set(files) | {"MANIFEST.json"} or len(names) != len(set(names)):
                raise ValueError("ARTIFACT_MANIFEST_MISMATCH")
            for name, expected in files.items():
                relative = PurePosixPath(name)
                if relative.is_absolute() or ".." in relative.parts or not name.startswith("src/treasury/"):
                    raise ValueError("ARTIFACT_PATH")
                data = archive.read(name)
                if sha256(data).hexdigest() != expected:
                    raise ValueError("ARTIFACT_MEMBER_DIGEST")
                target = directory / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        process = subprocess.run([sys.executable, "-I", "-B", "-c", SMOKE_PROGRAM,
                                  str(directory / "src"), str(root / "reader_side/specs/case_oracle.json"), kind],
                                 env=_environment(), capture_output=True, text=True, timeout=60)
        try:
            result = json.loads(process.stdout)
        except ValueError:
            result = {"status": "FAIL", "cases": 0, "findings": ["SMOKE_EXECUTION:" + process.stderr[-2000:]]}
        result["exit_code"] = process.returncode
        result["artifact_sha256"] = expected_hash
        return result


def _fresh_gate(tree, script, output):
    process = subprocess.run([sys.executable, "-B", str(tree / "reader_side/tools" / script),
                              "--output", str(output)], cwd=tree, env=_environment(),
                             capture_output=True, text=True, timeout=180)
    output.with_suffix(".log").write_text(process.stdout + "\nSTDERR\n" + process.stderr, encoding="utf-8")
    try:
        result = read_json(output)
    except (OSError, ValueError):
        result = {"status": "FAIL", "findings": ["CHECK_DID_NOT_PRODUCE_JSON"],
                  "exit_code": process.returncode}
        write_json(output, result)
    return result, process.returncode


def _instantiate_owner(catalogue, binding):
    return {section: [{**record, "binding": binding} for record in catalogue[section]]
            for section in ("resolutions", "review_decisions", "release_decisions")}


def _select(output, descriptor, event):
    path = output / descriptor["file"]
    if digest(path) != descriptor["sha256"]:
        raise ValueError("SELECTION_ARTIFACT_SUBSTITUTED")
    selected = {"artifact_id": descriptor["id"], "sha256": descriptor["sha256"], "file": descriptor["file"]}
    write_json(output / "selected_artifact.json", selected)
    with (output / "selection_log.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps({"event": event, **selected}, sort_keys=True) + "\n")


def rehearse(output_dir, reference=False, root=ROOT, teaching_operator=False):
    """Create a NEW reader-owned rehearsal; never repair the caller's candidates."""
    root, output = Path(root).resolve(), Path(output_dir).resolve()
    if output.exists() or output.is_relative_to(root / "repo"):
        raise ValueError("Rehearsal destination must be new and outside the editable repository")
    if output.is_relative_to(root) and not output.is_relative_to(root / "reader_side/evidence"):
        raise ValueError("Within the companion, rehearsal output belongs under reader_side/evidence")
    integrity = check_integrity(root)
    if integrity:
        return {"schema": "cp10-rehearsal/v1", "status": "FAIL",
                "findings": ["PROTECTED_INTEGRITY:" + name for name in integrity]}
    original = source_manifest(root)
    scenario, discussion, catalogue = _owner_inputs(root)
    output.mkdir(parents=True, exist_ok=False)
    (output / "evidence").mkdir()
    repo = output / "repository"
    repo.mkdir()
    record = {"schema": "cp10-rehearsal/v1", "status": "FAIL", "reference": bool(reference),
              "source_root": str(root), "python_version": sys.version.split()[0],
              "source_inputs": _selection_inputs(root, reference), "owner_inputs_sha256": _owner_hashes(root),
              "change_id": scenario["change_id"], "findings": [],
              "meaning": "Instantiated protected synthetic owner fixtures and local Git/artifact checks; no actual human approval or deployment."}
    try:
        _copy_source(root, repo, reference)
        proposed = (repo / PRODUCER).read_bytes()
        additions = {}
        if teaching_operator:
            addition = repo / OPERATOR_ADDITION
            additions[OPERATOR_ADDITION] = addition.read_bytes()
            record["candidate_additions"] = {OPERATOR_ADDITION: sha256(additions[OPERATOR_ADDITION]).hexdigest()}
            addition.unlink()
        (repo / PRODUCER).write_bytes((root / "reader_side/release/previous_presentation.py").read_bytes())
        _git(repo, "init", "--quiet", "--object-format=sha1", "--initial-branch=target")
        _git(repo, "add", ".")
        _git(repo, "commit", "--quiet", "-m", "Previous synthetic core presentation")
        previous = _git(repo, "rev-parse", "HEAD")
        _git(repo, "branch", "prior", previous)
        _git(repo, "checkout", "--quiet", "-b", "candidate")
        (repo / PRODUCER).write_bytes(proposed)
        for name, data in additions.items():
            (repo / name).write_bytes(data)
        _git(repo, "add", PRODUCER, *additions)
        _git(repo, "commit", "--quiet", "--allow-empty", "-m", "Candidate CP08 presentation source")
        head = _git(repo, "rev-parse", "HEAD")
        _git(repo, "checkout", "--quiet", "target")
        (repo / "CP10_TARGET_NOTE.txt").write_text("Target branch advanced with a synthetic review note; routing policy is unchanged.\n")
        _git(repo, "add", "CP10_TARGET_NOTE.txt")
        _git(repo, "commit", "--quiet", "-m", "Current target review note")
        base = _git(repo, "rev-parse", "HEAD")
        _git(repo, "checkout", "--quiet", "-b", "merge_candidate")
        _git(repo, "merge", "--quiet", "--no-ff", "candidate", "-m", "Exact local merge candidate")
        merged = _git(repo, "rev-parse", "HEAD")
        tree_id = _git(repo, "rev-parse", merged + "^{tree}")
        recomputed = _git(repo, "merge-tree", "--write-tree", base, head).splitlines()[0]
        if recomputed != tree_id:
            raise ValueError("MERGE_TREE_MISMATCH")
        git_state = {"base_commit": base, "head_commit": head, "merge_commit": merged,
                     "merge_tree": tree_id, "previous_commit": previous}
        record["git"] = git_state
        checked = output / "checked_tree"
        _materialize(repo, merged, checked)
        expected_files = {name: sha256(data).hexdigest() for name, data in _tree_files(repo, merged).items()}
        materialized_ok = source_manifest(checked, exclude_dossier=True) == expected_files
        merge_report = {"status": "PASS" if materialized_ok else "FAIL", **git_state,
                        "materialized_source_sha256": expected_files}
        write_json(output / CHECK_FILES["CI-MERGE-001"], merge_report)
        acceptance, acceptance_exit = _fresh_gate(checked, "run_acceptance.py", output / CHECK_FILES["CI-ROUTING-001"])
        integration, integration_exit = _fresh_gate(checked, "integration_gate.py", output / CHECK_FILES["CI-INTEGRATION-001"])
        artifacts = {}
        for kind, commit in (("current", merged), ("previous", previous)):
            data = _artifact_bytes(repo, commit, kind)
            path = output / ARTIFACT_FILES[kind]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            artifacts[kind] = {"id": scenario[kind + "_artifact_id"], "file": ARTIFACT_FILES[kind],
                               "sha256": sha256(data).hexdigest(), "commit": commit, "kind": kind}
        record["artifacts"] = artifacts
        smoke = artifact_smoke(output / artifacts["current"]["file"], artifacts["current"]["sha256"], root, "current")
        write_json(output / CHECK_FILES["CI-ARTIFACT-001"], smoke)
        binding = {**git_state, "candidate_source_sha256": sha256(proposed).hexdigest(),
                   "integration_receipt_sha256": digest(output / CHECK_FILES["CI-INTEGRATION-001"]),
                   "artifact_sha256": artifacts["current"]["sha256"]}
        record["binding"] = binding
        statuses = {"CI-MERGE-001": materialized_ok,
                    "CI-ROUTING-001": acceptance_exit == 0 and acceptance.get("status") == "PASS" and acceptance.get("tests_total") == acceptance.get("passed") == 7,
                    "CI-INTEGRATION-001": integration_exit == 0 and integration.get("status") == "PASS_REVIEW_GATE_ONLY",
                    "CI-ARTIFACT-001": smoke.get("status") == "PASS" and smoke.get("exit_code") == 0}
        record["checks"] = {name: {"status": "PASS" if statuses[name] else "FAIL", "file": path,
                                   "sha256": digest(output / path), "binding": binding}
                            for name, path in CHECK_FILES.items()}
        record["owner_records"] = _instantiate_owner(catalogue, binding)
        record["discussion_sha256"] = digest(root / "reader_side/release/mock_pr.json")
        rollback = {"status": "FAIL", "meaning": "Actual local artifact selection and smoke checks; no production or data rollback."}
        if all(statuses.values()):
            _select(output, artifacts["current"], "SELECT_CURRENT")
            _select(output, artifacts["previous"], "ROLLBACK_TO_PREVIOUS")
            prior_smoke = artifact_smoke(output / artifacts["previous"]["file"], artifacts["previous"]["sha256"], root, "previous")
            _select(output, artifacts["current"], "RESTORE_CURRENT")
            restored_smoke = artifact_smoke(output / artifacts["current"]["file"], artifacts["current"]["sha256"], root, "current")
            rollback.update(status="PASS" if prior_smoke.get("status") == restored_smoke.get("status") == "PASS" else "FAIL",
                            previous_smoke=prior_smoke, restored_smoke=restored_smoke,
                            log_sha256=digest(output / "selection_log.jsonl"),
                            restored_selection=read_json(output / "selected_artifact.json"))
        record["rollback"] = rollback
        record["upstream_authority"] = integration.get("authority", {})
        record["ci_status"] = "PASS" if all(statuses.values()) else "FAIL"
        if source_manifest(checked, exclude_dossier=True) != expected_files:
            record["findings"].append("CHECKED_TREE_CHANGED_DURING_CHECKS")
        if source_manifest(root) != original:
            record["findings"].append("SOURCE_COMPANION_CHANGED")
        record["source_companion_unchanged"] = source_manifest(root) == original
        if record["ci_status"] == "PASS" and rollback["status"] == "PASS" and not record["findings"]:
            record["status"] = "READY_FOR_DOSSIER_REVIEW"
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        record["findings"].append("REHEARSAL_ERROR:" + type(exc).__name__ + ":" + str(exc))
    write_json(output / "rehearsal.json", record)
    return record


def _identity_and_checks(root, directory, record, scenario, catalogue):
    """Return verified evidence facts and failures; never trust the dossier's CI claims."""
    issues = []
    if record.get("schema") != "cp10-rehearsal/v1" or not isinstance(record.get("reference"), bool):
        return ["REHEARSAL_SCHEMA"], {}
    if record.get("owner_inputs_sha256") != _owner_hashes(root):
        issues.append("OWNER_INPUTS_CHANGED")
    current_inputs = _selection_inputs(root, record["reference"])
    for name in sorted(set(current_inputs) | set(record.get("source_inputs", {}))):
        if current_inputs.get(name) != record.get("source_inputs", {}).get(name):
            issues.append("STALE_INPUT:" + name)
    repo = directory / "repository"
    if _git(repo, "remote"):
        issues.append("REHEARSAL_REMOTE_NOT_ALLOWED")
    git_state = record.get("git", {})
    for ref, field, failure in (("target", "base_commit", "STALE_BASE"),
                                 ("candidate", "head_commit", "STALE_HEAD"),
                                 ("merge_candidate", "merge_commit", "STALE_MERGE_CANDIDATE"),
                                 ("prior", "previous_commit", "STALE_PREVIOUS_ARTIFACT_SOURCE")):
        if _git(repo, "rev-parse", "refs/heads/" + ref) != git_state.get(field):
            issues.append(failure)
    if _git(repo, "status", "--porcelain", "--untracked-files=all"):
        issues.append("DIRTY_REHEARSAL_WORKTREE")
    merged, base, head = (git_state.get(name) for name in ("merge_commit", "base_commit", "head_commit"))
    parents = _git(repo, "rev-list", "--parents", "-n", "1", merged).split()
    if parents != [merged, base, head]:
        issues.append("MERGE_PARENT_IDENTITY")
    tree_id = _git(repo, "rev-parse", merged + "^{tree}")
    if tree_id != git_state.get("merge_tree") or _git(repo, "merge-tree", "--write-tree", base, head).splitlines()[0] != tree_id:
        issues.append("MERGE_TREE_IDENTITY")
    committed = _tree_files(repo, merged)
    additions = record.get("candidate_additions", {})
    if additions:
        prior_files = _tree_files(repo, git_state["previous_commit"])
        if (set(additions) != {OPERATOR_ADDITION}
                or any(name in prior_files or name not in committed
                       or sha256(committed[name]).hexdigest() != value
                       or not (root / name).is_file() or digest(root / name) != value
                       for name, value in additions.items())):
            issues.append("CANDIDATE_ADDITION_IDENTITY")
    expected = {name: sha256(data).hexdigest() for name, data in committed.items()}
    if source_manifest(directory / "checked_tree", exclude_dossier=True) != expected:
        issues.append("CHECKED_TREE_CHANGED")
    producer_hash = sha256(committed[PRODUCER]).hexdigest()
    artifacts = record.get("artifacts", {})
    for kind, commit in (("current", merged), ("previous", git_state["previous_commit"])):
        item = artifacts.get(kind, {})
        wanted = sha256(_artifact_bytes(repo, commit, kind)).hexdigest()
        if item.get("file") != ARTIFACT_FILES[kind] or item.get("id") != scenario[kind + "_artifact_id"] or item.get("commit") != commit:
            issues.append("ARTIFACT_IDENTITY:" + kind)
        path = directory / ARTIFACT_FILES[kind]
        if item.get("sha256") != wanted or digest(path) != wanted:
            issues.append("ARTIFACT_SUBSTITUTION:" + kind)
    expected_binding = {**git_state, "candidate_source_sha256": producer_hash,
                        "integration_receipt_sha256": digest(directory / CHECK_FILES["CI-INTEGRATION-001"]),
                        "artifact_sha256": artifacts.get("current", {}).get("sha256")}
    if record.get("binding") != expected_binding:
        issues.append("EVIDENCE_BINDING_MISMATCH")
    if record.get("owner_records") != _instantiate_owner(catalogue, expected_binding):
        issues.append("OWNER_RECORD_BINDING_MISMATCH")
    if record.get("discussion_sha256") != digest(root / "reader_side/release/mock_pr.json"):
        issues.append("DISCUSSION_CHANGED")
    checks = record.get("checks", {})
    if set(checks) != set(scenario["required_checks"]):
        issues.append("MISSING_REQUIRED_CHECKS")
    reports = {}
    for name, relative in CHECK_FILES.items():
        item = checks.get(name, {})
        path = directory / relative
        if item.get("file") != relative or not path.is_file():
            issues.append("CHECK_MISSING:" + name)
            continue
        if item.get("sha256") != digest(path) or item.get("binding") != expected_binding:
            issues.append("STALE_CHECK:" + name)
        data = read_json(path)
        reports[name] = data
        expected_status = "PASS_REVIEW_GATE_ONLY" if name == "CI-INTEGRATION-001" else "PASS"
        if item.get("status") != "PASS" or data.get("status") != expected_status:
            issues.append("CHECK_FAILED:" + name)
    acceptance = reports.get("CI-ROUTING-001", {})
    if acceptance.get("tests_total") != 7 or acceptance.get("passed") != 7 or any(acceptance.get(key) != 0 for key in ("failures", "errors", "skipped")):
        issues.append("ROUTING_CHECK_INCOMPLETE")
    integration = reports.get("CI-INTEGRATION-001", {})
    receipt_paths = set(SHARED_INPUTS) | {pair[0] for pair in INPUT_PAIRS.values()}
    input_receipts = {name: sha256(committed[name]).hexdigest() for name in sorted(receipt_paths)}
    if integration.get("mode") != "WORKING_CANDIDATES" or integration.get("input_receipts") != input_receipts:
        issues.append("INTEGRATION_RECEIPT_IDENTITY")
    authority = integration.get("authority", {})
    if authority.get("CP07_T07_03") != "PENDING_HUMAN" or authority.get("CP07_T07_04") != "BLOCKED" or authority.get("release_authorized") is not False or authority.get("payment_authorized") is not False:
        issues.append("UPSTREAM_AUTHORITY_ESCALATION")
    merge_report = reports.get("CI-MERGE-001", {})
    if merge_report.get("materialized_source_sha256") != expected or any(merge_report.get(key) != value for key, value in git_state.items()):
        issues.append("CHECKED_MERGE_IDENTITY")
    smoke = reports.get("CI-ARTIFACT-001", {})
    if smoke.get("artifact_sha256") != artifacts.get("current", {}).get("sha256") or smoke.get("cases") != 8 or smoke.get("findings") != []:
        issues.append("ARTIFACT_CHECK_IDENTITY")
    return issues, {"binding": expected_binding, "artifacts": artifacts, "authority": authority,
                    "producer_sha256": producer_hash, "checks": reports}


def _rollback_findings(directory, record, facts, root):
    rollback = record.get("rollback", {})
    issues = []
    artifacts = facts["artifacts"]
    wanted = {"artifact_id": artifacts["current"]["id"], "sha256": artifacts["current"]["sha256"],
              "file": ARTIFACT_FILES["current"]}
    if rollback.get("status") != "PASS" or read_json(directory / "selected_artifact.json") != wanted:
        issues.append("ROLLBACK_NOT_RESTORED")
    log = directory / "selection_log.jsonl"
    events = [json.loads(line) for line in log.read_text().splitlines()]
    expected_events = []
    for event, kind in (("SELECT_CURRENT", "current"), ("ROLLBACK_TO_PREVIOUS", "previous"), ("RESTORE_CURRENT", "current")):
        item = artifacts[kind]
        expected_events.append({"event": event, "artifact_id": item["id"], "sha256": item["sha256"], "file": item["file"]})
    if events != expected_events or digest(log) != rollback.get("log_sha256"):
        issues.append("ROLLBACK_SELECTION_EVIDENCE")
    for kind, key in (("previous", "previous_smoke"), ("current", "restored_smoke")):
        item = artifacts[kind]
        actual = artifact_smoke(directory / item["file"], item["sha256"], root, kind)
        saved = rollback.get(key, {})
        if actual.get("status") != "PASS" or saved != actual:
            issues.append("ROLLBACK_SMOKE:" + kind)
    return issues


def evaluate_release(dossier_path, rehearsal_dir, root=ROOT, scope_baseline=None):
    """Check exact evidence and protected synthetic decisions; fail closed."""
    root, directory = Path(root).resolve(), Path(rehearsal_dir).resolve()
    candidate = Path(dossier_path).resolve()
    result = {"schema": "cp10-release-verdict/v1", "status": "FAIL", "ci_status": "FAIL",
              "readiness": "BLOCKED", "review_decision": "NOT_ACCEPTED",
              "local_release_decision": "NOT_AUTHORIZED", "rollback_status": "FAIL",
              "edit_scope_checked": scope_baseline is not None, "findings": [],
              "real_human_acceptance": False, "real_release_authorized": False,
              "policy_evolution_release_authorized": False,
              "payment_authorized": False, "CP07_T07_03": "PENDING_HUMAN", "CP07_T07_04": "BLOCKED",
              "meaning": "Known protected synthetic roles authorize only a local presentation artifact-selection rehearsal. No real human approval, merge of the caller's repository or production deployment is performed."}
    issues = result["findings"]
    try:
        integrity = check_integrity(root)
        if integrity:
            issues.extend("PROTECTED_INTEGRITY:" + name for name in integrity)
            return result
        allowed = {root / name for name in (DOSSIER, REFERENCE, UNSAFE)}
        if candidate not in allowed:
            issues.append("DOSSIER_PATH_NOT_ALLOWED")
            return result
        if candidate == root / DOSSIER:
            check_candidate_path("engineering/release/release_dossier.json", repo=root / "repo", chapter="CP10")
        if scope_baseline:
            issues.extend(check_edit_scope(scope_baseline, root=root, chapter="CP10"))
        dossier = read_json(candidate)
        result["dossier_sha256"] = digest(candidate)
        if not isinstance(dossier, dict) or dossier.get("schema") != "cp10-release-dossier/v1":
            issues.append("DOSSIER_SCHEMA")
            return result
        scenario, discussion, catalogue = _owner_inputs(root)
        record = read_json(directory / "rehearsal.json")
        result["rehearsal_mode"] = "PROTECTED_REFERENCE" if record.get("reference") else "WORKING_CANDIDATES"
        result["rehearsal_sha256"] = digest(directory / "rehearsal.json")
        evidence_issues, facts = _identity_and_checks(root, directory, record, scenario, catalogue)
        issues.extend(evidence_issues)
        result["ci_status"] = "FAIL" if evidence_issues else "PASS"
        if facts:
            result["binding"] = facts["binding"]
        if evidence_issues:
            return result
        rollback_issues = _rollback_findings(directory, record, facts, root)
        issues.extend(rollback_issues)
        result["rollback_status"] = "FAIL" if rollback_issues else "PASS"
        if dossier.get("change_id") != scenario["change_id"] or dossier.get("author_id") != scenario["author_id"]:
            issues.append("CHANGE_OR_AUTHOR_IDENTITY")
        if dossier.get("candidate_source_sha256") != facts["producer_sha256"]:
            issues.append("DOSSIER_SOURCE_IDENTITY")
        if facts["producer_sha256"] != scenario["authorized_source_sha256"]:
            issues.append("SOURCE_NOT_COVERED_BY_SYNTHETIC_OWNER_DECISION")
        if dossier.get("ci_evidence_ids") != scenario["required_checks"]:
            issues.append("DOSSIER_MISSING_REQUIRED_CHECKS")
        if dossier.get("artifact_id") != scenario["current_artifact_id"]:
            issues.append("DOSSIER_ARTIFACT_SUBSTITUTION")
        if dossier.get("rollback_artifact_id") != scenario["previous_artifact_id"]:
            issues.append("DOSSIER_ROLLBACK_ARTIFACT")
        claims = dossier.get("claims", {})
        if not isinstance(claims, dict) or any(claims.get(key) is not False for key in
                ("real_human_acceptance", "production_deployed", "payment_authorized", "cp07_t07_04_executed")):
            issues.append("AUTHORITY_OVERCLAIM")
        resolution_ids = dossier.get("discussion_resolution_ids", [])
        if not isinstance(resolution_ids, list):
            issues.append("DISCUSSION_RESOLUTION_SCHEMA")
            resolution_ids = []
        resolutions = {item["id"]: item for item in catalogue["resolutions"]}
        roles = scenario["roles"]
        for thread in discussion["threads"]:
            if not thread.get("mandatory"):
                continue
            resolution = resolutions.get(thread["resolution_id"], {})
            if thread["resolution_id"] not in resolution_ids:
                issues.append("UNRESOLVED_MANDATORY_THREAD:" + thread["id"])
                continue
            if resolution.get("thread_id") != thread["id"] or resolution.get("actor_id") == scenario["author_id"] or roles.get(resolution.get("actor_id")) not in {"independent_reviewer", "release_owner"}:
                issues.append("INVALID_THREAD_RESOLUTION:" + thread["id"])
            if any(record["checks"].get(check, {}).get("status") != "PASS" for check in thread.get("required_checks", [])):
                issues.append("THREAD_REQUIRED_CHECKS:" + thread["id"])
            if thread.get("requires_rollback") and rollback_issues:
                issues.append("THREAD_REQUIRES_ROLLBACK:" + thread["id"])
        reviews = {item["id"]: item for item in catalogue["review_decisions"]}
        review = reviews.get(dossier.get("review_decision_id"), {})
        review_applicable = bool(review) and (review.get("scope") == SCOPE
            and review.get("source_sha256") == facts["producer_sha256"]
            and review.get("change_id") == scenario["change_id"]
            and review.get("synthetic") is True)
        if review and not review_applicable:
            issues.append("REVIEW_DECISION_IDENTITY_OR_SCOPE")
        if not review:
            issues.append("REVIEW_DECISION_MISSING")
        elif review.get("actor_id") == scenario["author_id"]:
            issues.append("SELF_APPROVAL")
        elif roles.get(review.get("actor_id")) != "independent_reviewer":
            issues.append("REVIEWER_ROLE")
        elif not review_applicable:
            pass  # An inapplicable fixture is neither acceptance nor rejection.
        elif review.get("decision") == "REJECT":
            result["review_decision"] = "REJECT"
            issues.append("OWNER_REVIEW_REJECTED")
        elif review.get("decision") == "ACCEPT":
            result["review_decision"] = "ACCEPT"
        else:
            issues.append("REVIEW_DECISION_VALUE")
        releases = {item["id"]: item for item in catalogue["release_decisions"]}
        release = releases.get(dossier.get("release_decision_id"), {})
        if not release or release.get("decision") != "AUTHORIZE_LOCAL_PRESENTATION_EXPERIMENT":
            issues.append("EXPLICIT_LOCAL_RELEASE_AUTHORIZATION_MISSING")
        elif roles.get(release.get("actor_id")) != "release_owner" or release.get("actor_id") == scenario["author_id"]:
            issues.append("RELEASE_OWNER_ROLE")
        if release and (release.get("scope") != SCOPE or release.get("source_sha256") != facts["producer_sha256"] or release.get("change_id") != scenario["change_id"] or release.get("synthetic") is not True):
            issues.append("RELEASE_DECISION_IDENTITY_OR_SCOPE")
        result["readiness"] = "READY_FOR_OWNER_REVIEW" if result["ci_status"] == result["rollback_status"] == "PASS" else "BLOCKED"
        if not issues:
            result["status"] = SUCCESS
            result["local_release_decision"] = "AUTHORIZE_LOCAL_PRESENTATION_EXPERIMENT"
    except (OSError, ValueError, TypeError, KeyError, AttributeError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        issues.append("GATE_ERROR:" + type(exc).__name__ + ":" + str(exc))
    return result
