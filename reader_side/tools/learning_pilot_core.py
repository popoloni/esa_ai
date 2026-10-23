"""Owner-run delayed protocol; human judgments remain raw, attributed records."""
from contextlib import contextmanager
from hashlib import sha256
import hmac
import os
from pathlib import Path
import platform
import re
import secrets
import shutil
import tempfile
import time
import uuid

from learning_core import (ROOT, PROTOCOL, RUBRIC, REVIEW, KNOWLEDGE, REFERENCE_REVIEW,
    REFERENCE_KNOWLEDGE, TRANSFER_EVENTS, source_inputs, validate_transfer,
    safe_owned_path, tree_hashes, read_json, write_json, canonical, digest)
from scope_guard import check_integrity

SYNTHETIC = "SYNTHETIC_CALIBRATION"
HUMAN = "OPERATOR_ATTESTED_HUMAN_TRIAL"
TASKS = ("baseline", "retention", "transfer")


def owner_clock():
    boot = Path("/proc/sys/kernel/random/boot_id")
    if platform.system() != "Linux" or not boot.is_file():
        raise ValueError("REAL_CLOCK_REQUIRES_SUPPORTED_LINUX_HOST_BOOT")
    context = sha256((platform.node() + ":" + boot.read_text().strip()).encode()).hexdigest()
    return {"kind": "OWNER_HOST_CLOCK", "wall_ns": time.time_ns(), "monotonic_ns": time.monotonic_ns(),
            "host_boot": context}


def checked_clock(origin, supplied=None, previous=None, root=ROOT):
    if supplied is not None and origin != SYNTHETIC:
        raise ValueError("CLOCK_INJECTION_FORBIDDEN_IN_HUMAN_MODE")
    now = dict(supplied) if supplied is not None else owner_clock()
    expected = "PROTECTED_SYNTHETIC_CLOCK" if origin == SYNTHETIC else "OWNER_HOST_CLOCK"
    if (now.get("kind") != expected or set(now) != {"kind", "wall_ns", "monotonic_ns", "host_boot"}
            or type(now.get("wall_ns")) is not int or type(now.get("monotonic_ns")) is not int
            or now["wall_ns"] <= 0 or now["monotonic_ns"] <= 0
            or not isinstance(now.get("host_boot"), str) or not now["host_boot"]):
        raise ValueError("CLOCK_SCHEMA")
    if previous:
        if now["host_boot"] != previous["host_boot"]:
            raise ValueError("OWNER_CLOCK_CONTEXT_CHANGED_RESTART_TRIAL")
        wall, monotonic = now["wall_ns"] - previous["wall_ns"], now["monotonic_ns"] - previous["monotonic_ns"]
        limit = read_json(Path(root) / PROTOCOL)["max_wall_monotonic_drift_seconds"] * 1_000_000_000
        if wall < 0 or monotonic < 0 or abs(wall - monotonic) > limit:
            raise ValueError("OWNER_CLOCK_DISCONTINUITY_RESTART_TRIAL")
    return now


def pilot_inputs(root, reference):
    inputs = source_inputs(root, reference)
    for name in ((REFERENCE_REVIEW, REFERENCE_KNOWLEDGE) if reference else (REVIEW, KNOWLEDGE)):
        inputs[name] = digest(Path(root) / name)
    return inputs


def _private_hashes(owner):
    private = Path(owner) / "private"
    return tree_hashes(private) if private.exists() else {}


def _append(owner, state, action, clock):
    owner = Path(owner)
    existing = sorted((owner / "events").glob("*.json"))
    previous = read_json(existing[-1])["signature"] if existing else None
    state["trial_files"] = tree_hashes(Path(state["trial_path"]))
    state["private_files"] = _private_hashes(owner)
    event = {"schema": "cp13-owner-event/v1", "sequence": len(existing) + 1,
             "action": action, "clock": clock, "previous": previous, "state": state}
    event["signature"] = hmac.new((owner / "owner.key").read_bytes(), canonical(event).encode(), "sha256").hexdigest()
    path = owner / "events" / (f"{len(existing) + 1:06d}.json")
    with path.open("x") as stream:
        stream.write(canonical(event) + "\n")
    return event


def _load(owner, root=ROOT):
    owner = safe_owned_path(owner, root)
    key = owner / "owner.key"
    if key.is_symlink() or not key.is_file() or len(key.read_bytes()) != 32:
        raise ValueError("OWNER_KEY_UNAVAILABLE")
    files = sorted((owner / "events").glob("*.json"))
    if not files:
        raise ValueError("OWNER_EVENTS_MISSING")
    previous = None
    event = None
    for number, path in enumerate(files, 1):
        if path.name != f"{number:06d}.json" or path.is_symlink():
            raise ValueError("OWNER_EVENT_SEQUENCE")
        event = read_json(path)
        if not isinstance(event, dict) or event.get("schema") != "cp13-owner-event/v1":
            raise ValueError("OWNER_EVENT_SCHEMA")
        signature = event.get("signature")
        expected = hmac.new(key.read_bytes(), canonical({k: v for k, v in event.items() if k != "signature"}).encode(), "sha256").hexdigest()
        if (not isinstance(signature, str) or not hmac.compare_digest(signature, expected)
                or event.get("sequence") != number or event.get("previous") != previous):
            raise ValueError("OWNER_EVENT_INTEGRITY")
        previous = signature
    state = event["state"]
    trial = safe_owned_path(state["trial_path"], root)
    if owner.is_relative_to(trial) or trial.is_relative_to(owner):
        raise ValueError("OWNER_STATE_MUST_BE_SEPARATE_FROM_PUBLIC_TRIAL")
    if tree_hashes(trial) != state.get("trial_files") or _private_hashes(owner) != state.get("private_files"):
        raise ValueError("TRIAL_RECORDS_CHANGED")
    if check_integrity(root) or pilot_inputs(root, state["mode"] == "PROTECTED_REFERENCE") != state.get("source_inputs"):
        raise ValueError("PILOT_SOURCE_OR_RUBRIC_CHANGED")
    _, findings, _ = validate_transfer(state["transfer_path"], root, state["mode"] == "PROTECTED_REFERENCE")
    if findings or digest(Path(state["transfer_path"]) / "TRANSFER_SESSION.json") != state["transfer_session_sha256"]:
        raise ValueError("PILOT_TRANSFER_EVIDENCE_CHANGED")
    return owner, state, event["clock"]


@contextmanager
def owner_action(owner, root=ROOT):
    owner = safe_owned_path(owner, root)
    lock = owner / "ACTION_LOCK"
    try:
        handle = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise ValueError("OWNER_ACTION_IN_PROGRESS") from None
    os.close(handle)
    try:
        yield _load(owner, root)
    finally:
        lock.unlink()


def _summary(owner, state):
    result = {"schema": "cp13-pilot-status/v1", "trial_id": state["trial_id"], "origin": state["origin"],
              "mode": state["mode"], "phase": state["phase"], "answer_sha256": state["answer_sha256"],
              "review_sha256": state["review_sha256"], "adjudication_sha256": state.get("adjudication_sha256"),
              "rubric_id": state["rubric_id"], "rubric_sha256": state["rubric_sha256"],
              "transfer_session_sha256": state["transfer_session_sha256"],
              "real_clock_delay_elapsed": state["origin"] == HUMAN and state.get("delay_released", False),
              "human_trial_status": "PENDING_REAL_HUMAN_TRIAL" if state["origin"] == SYNTHETIC else "OPERATOR_ATTESTED_RECORDS_REQUIRE_OWNER_CONFIRMATION",
              "rubric_validity": "PENDING_HUMAN_VALIDATION", "human_competence": "NOT_ESTABLISHED_BY_AUTOMATION",
              "reviewer_identity_and_independence": "DECLARED_NOT_AUTHENTICATED",
              "release_authorized": False, "incident_reconciliation": "PENDING_OWNER", "CP07_T07_04": "BLOCKED"}
    if len(state["review_sha256"]) == 2:
        profiles = {name: read_json(Path(owner) / "private" / (name + ".json")) for name in state["reviewers"]}
        result["raw_ratings"] = {name: data["ratings"] for name, data in profiles.items()}
        dimensions = list(next(iter(profiles.values()))["ratings"]["baseline"])
        a, b = state["reviewers"]
        result["disagreements"] = [{"task": task, "dimension": dim,
                                    "reviewer_a": profiles[a]["ratings"][task][dim],
                                    "reviewer_b": profiles[b]["ratings"][task][dim]}
                                   for task in TASKS for dim in dimensions
                                   if profiles[a]["ratings"][task][dim] != profiles[b]["ratings"][task][dim]]
        result["descriptive_totals"] = {name: {task: sum(data["ratings"][task].values()) for task in TASKS}
                                         for name, data in profiles.items()}
        if state.get("adjudication_sha256"):
            result["separate_adjudication"] = read_json(Path(state["trial_path"]) / "adjudication/raw.json")
    return result


def start_trial(transfer, owner, trial, participant, reviewers, coordinator, attest_no_exposure,
                root=ROOT, synthetic=False, clock=None):
    root, transfer = Path(root).resolve(), safe_owned_path(transfer, root)
    origin = SYNTHETIC if synthetic else HUMAN
    now = checked_clock(origin, clock, root=root)
    owner, trial = safe_owned_path(owner, root), safe_owned_path(trial, root)
    if (owner.is_relative_to(trial) or trial.is_relative_to(owner) or owner.is_relative_to(transfer)
            or trial.is_relative_to(transfer) or transfer.is_relative_to(owner) or transfer.is_relative_to(trial)):
        raise ValueError("OWNER_PUBLIC_AND_TRANSFER_DIRECTORIES_MUST_BE_SEPARATE")
    roles = [participant, *reviewers, coordinator]
    if (len(reviewers) != 2 or len(set(roles)) != 4 or not attest_no_exposure
            or any(not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", name) for name in roles)):
        raise ValueError("DISTINCT_ROLE_IDS_AND_EXPOSURE_ATTESTATION_REQUIRED")
    if owner.exists() or trial.exists():
        raise ValueError("NEW_OWNER_AND_PUBLIC_DIRECTORIES_REQUIRED")
    integrity = check_integrity(root)
    if integrity:
        raise ValueError("PROTECTED_INTEGRITY:" + ",".join(integrity))
    transfer_record = read_json(transfer / "TRANSFER_SESSION.json")
    reference = transfer_record.get("mode") == "PROTECTED_REFERENCE"
    _, findings, _ = validate_transfer(transfer, root, reference)
    if findings:
        raise ValueError("TRANSFER_NOT_READY:" + ",".join(findings))
    owner.mkdir(parents=True)
    (owner / "events").mkdir()
    (owner / "private").mkdir()
    descriptor = os.open(owner / "owner.key", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(secrets.token_bytes(32))
    trial.mkdir(parents=True)
    shutil.copytree(transfer / "learning_material", trial / "learning_material")
    for relative, name in ((PROTOCOL, "protocol.json"), (RUBRIC, "rubric.json")):
        shutil.copyfile(root / relative, trial / name)
    shutil.copyfile(root / "reader_side/learning/baseline_prompt.md", trial / "baseline_prompt.md")
    rubric = read_json(root / RUBRIC)
    state = {"schema": "cp13-owner-trial/v1", "trial_id": "TRIAL-013-" + uuid.uuid4().hex,
             "phase": "LEARNING_OPEN", "origin": origin, "mode": transfer_record["mode"],
             "trial_path": str(trial), "transfer_path": str(transfer), "participant": participant,
             "reviewers": list(reviewers), "coordinator": coordinator,
             "prior_transfer_exposure": "OPERATOR_ATTESTS_NONE" if not synthetic else "SYNTHETIC_PROTOCOL_FIXTURE",
             "source_inputs": pilot_inputs(root, reference),
             "transfer_session_sha256": digest(transfer / "TRANSFER_SESSION.json"),
             "rubric_id": rubric["rubric_id"], "rubric_sha256": digest(root / RUBRIC),
             "answer_sha256": {}, "review_sha256": {}, "adjudication_sha256": None}
    write_json(trial / "trial_info.json", {key: state[key] for key in
        ("trial_id", "origin", "mode", "participant", "reviewers", "coordinator", "prior_transfer_exposure", "rubric_id", "rubric_sha256", "transfer_session_sha256")})
    _append(owner, state, "START", now)
    return _summary(owner, state)


def _input_bytes(path, owner):
    path = Path(path).absolute()
    if path.is_symlink() or not path.is_file() or path.is_relative_to(Path(owner)):
        raise ValueError("INPUT_FILE_NOT_ALLOWED")
    raw = path.read_bytes()
    if not raw or len(raw) > 250_000 or not raw.decode("utf-8").strip():
        raise ValueError("EMPTY_OR_OVERSIZED_RECORD")
    return raw


def _write_raw(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)


def submit_answer(owner, task, file, root=ROOT, clock=None):
    required = {"baseline": "LEARNING_OPEN", "retention": "RETENTION_OPEN", "transfer": "TRANSFER_OPEN"}
    next_phase = {"baseline": "DELAY_RUNNING", "retention": "RETENTION_SEALED", "transfer": "AWAITING_REVIEWS"}
    if task not in required:
        raise ValueError("ANSWER_TASK")
    with owner_action(owner, root) as (owner, state, previous):
        now = checked_clock(state["origin"], clock, previous, root)
        if state["phase"] != required[task]:
            raise ValueError("PHASE_REQUIRES_" + required[task])
        raw = _input_bytes(file, owner)
        _write_raw(Path(state["trial_path"]) / "answers" / (task + ".raw.md"), raw)
        state["answer_sha256"][task] = sha256(raw).hexdigest()
        state["phase"] = next_phase[task]
        if task == "baseline":
            state["delay_anchor"] = now
        if task == "transfer":
            knowledge = Path(root) / (REFERENCE_KNOWLEDGE if state["mode"] == "PROTECTED_REFERENCE" else KNOWLEDGE)
            shutil.copyfile(knowledge, Path(state["trial_path"]) / "team_knowledge.json")
            for reviewer in state["reviewers"]:
                write_json(Path(state["trial_path"]) / "review_forms" / (reviewer + ".json"), score_template(state, reviewer, root))
        _append(owner, state, "SUBMIT_" + task.upper(), now)
        return _summary(owner, state)


def release_retention(owner, root=ROOT, clock=None):
    with owner_action(owner, root) as (owner, state, previous):
        now = checked_clock(state["origin"], clock, previous, root)
        if state["phase"] != "DELAY_RUNNING":
            raise ValueError("PHASE_REQUIRES_DELAY_RUNNING")
        anchor = state["delay_anchor"]
        checked_clock(state["origin"], now if state["origin"] == SYNTHETIC else None, anchor, root)
        delay = read_json(Path(root) / PROTOCOL)["delay_seconds"] * 1_000_000_000
        if min(now["wall_ns"] - anchor["wall_ns"], now["monotonic_ns"] - anchor["monotonic_ns"]) < delay:
            raise ValueError("DELAY_NOT_ELAPSED")
        shutil.copyfile(Path(root) / "reader_side/learning/retention_prompt.md", Path(state["trial_path"]) / "retention_prompt.md")
        state["phase"], state["delay_released"] = "RETENTION_OPEN", True
        _append(owner, state, "RELEASE_RETENTION", now)
        return _summary(owner, state)


def release_transfer(owner, root=ROOT, clock=None):
    with owner_action(owner, root) as (owner, state, previous):
        now = checked_clock(state["origin"], clock, previous, root)
        if state["phase"] != "RETENTION_SEALED":
            raise ValueError("RETENTION_MUST_BE_SEALED_BEFORE_TRANSFER")
        material = Path(state["trial_path"]) / "transfer_material"
        material.mkdir()
        for name in TRANSFER_EVENTS:
            for suffix in (".json", ".log"):
                shutil.copyfile(Path(state["transfer_path"]) / "steps" / (name + suffix), material / (name + suffix))
        shutil.copyfile(Path(root) / "reader_side/learning/transfer_prompt.md", material / "PROMPT.md")
        state["phase"] = "TRANSFER_OPEN"
        _append(owner, state, "RELEASE_TRANSFER", now)
        return _summary(owner, state)


def score_template(state, reviewer, root=ROOT):
    dimensions = read_json(Path(root) / RUBRIC)["dimensions"]
    return {"schema": "cp13-independent-score/v1", "origin": SYNTHETIC if state["origin"] == SYNTHETIC else "OPERATOR_ATTESTED_HUMAN_RECORD",
            "trial_id": state["trial_id"], "reviewer_id": reviewer, "rubric_id": state["rubric_id"],
            "rubric_sha256": state["rubric_sha256"], "transfer_session_sha256": state["transfer_session_sha256"],
            "answer_sha256": state["answer_sha256"],
            "ratings": {task: {dim: None for dim in dimensions} for task in TASKS},
            "rationales": {task: "" for task in TASKS},
            "attestations": {"human_record": False, "independent_scoring": False, "no_other_scores_seen": False}}


def validate_ratings(ratings, rationales, root=ROOT):
    dimensions = read_json(Path(root) / RUBRIC)["dimensions"]
    if not isinstance(ratings, dict) or set(ratings) != set(TASKS) or not isinstance(rationales, dict) or set(rationales) != set(TASKS):
        raise ValueError("SCORE_TASKS")
    for task in TASKS:
        if (not isinstance(ratings[task], dict) or set(ratings[task]) != set(dimensions)
                or any(type(value) is not int or value not in (0, 1, 2, 3) for value in ratings[task].values())
                or not isinstance(rationales[task], str) or not rationales[task].strip()):
            raise ValueError("SCORE_DIMENSIONS_OR_RATIONALE")


def record_score(owner, reviewer, file, root=ROOT, clock=None):
    with owner_action(owner, root) as (owner, state, previous):
        now = checked_clock(state["origin"], clock, previous, root)
        if state["phase"] != "AWAITING_REVIEWS" or reviewer not in state["reviewers"] or reviewer in state["review_sha256"]:
            raise ValueError("INDEPENDENT_REVIEWER_OR_PHASE_REQUIRED")
        raw = _input_bytes(file, owner)
        import json
        value = json.loads(raw)
        template = score_template(state, reviewer, root)
        if not isinstance(value, dict) or set(value) != set(template):
            raise ValueError("SCORE_SCHEMA")
        for key in template:
            if key not in {"ratings", "rationales", "attestations"} and value[key] != template[key]:
                raise ValueError("SCORE_IDENTITY:" + key)
        validate_ratings(value["ratings"], value["rationales"], root)
        expected_attestation = {key: state["origin"] != SYNTHETIC for key in template["attestations"]}
        if (not isinstance(value["attestations"], dict)
                or set(value["attestations"]) != set(expected_attestation)
                or any(type(item) is not bool for item in value["attestations"].values())
                or value["attestations"] != expected_attestation):
            raise ValueError("HUMAN_OR_SYNTHETIC_ATTESTATION_MISMATCH")
        _write_raw(owner / "private" / (reviewer + ".json"), raw)
        state["review_sha256"][reviewer] = sha256(raw).hexdigest()
        if len(state["review_sha256"]) == 2:
            public = Path(state["trial_path"]) / "reviews"
            public.mkdir()
            for name in state["reviewers"]:
                shutil.copyfile(owner / "private" / (name + ".json"), public / (name + ".raw.json"))
            state["phase"] = "REVIEWS_RECORDED"
            write_json(Path(state["trial_path"]) / "adjudication_form.json", adjudication_template(state, root))
        _append(owner, state, "RECORD_SCORE:" + reviewer, now)
        return _summary(owner, state)


def adjudication_template(state, root=ROOT):
    dimensions = read_json(Path(root) / RUBRIC)["dimensions"]
    return {"schema": "cp13-adjudication/v1", "origin": SYNTHETIC if state["origin"] == SYNTHETIC else "OPERATOR_ATTESTED_HUMAN_RECORD",
            "trial_id": state["trial_id"], "coordinator_id": state["coordinator"],
            "rubric_sha256": state["rubric_sha256"], "answer_sha256": state["answer_sha256"],
            "review_sha256": state["review_sha256"],
            "ratings": {task: {dim: None for dim in dimensions} for task in TASKS},
            "rationales": {task: "" for task in TASKS}}


def adjudicate(owner, file, root=ROOT, clock=None):
    with owner_action(owner, root) as (owner, state, previous):
        now = checked_clock(state["origin"], clock, previous, root)
        if state["phase"] != "REVIEWS_RECORDED":
            raise ValueError("TWO_RAW_REVIEWS_REQUIRED_BEFORE_ADJUDICATION")
        raw = _input_bytes(file, owner)
        import json
        value = json.loads(raw)
        template = adjudication_template(state, root)
        if not isinstance(value, dict) or set(value) != set(template):
            raise ValueError("ADJUDICATION_SCHEMA")
        for key in template:
            if key not in {"ratings", "rationales"} and value[key] != template[key]:
                raise ValueError("ADJUDICATION_IDENTITY:" + key)
        validate_ratings(value["ratings"], value["rationales"], root)
        _write_raw(Path(state["trial_path"]) / "adjudication/raw.json", raw)
        state["adjudication_sha256"], state["phase"] = sha256(raw).hexdigest(), "ADJUDICATED"
        _append(owner, state, "ADJUDICATE_SEPARATELY", now)
        return _summary(owner, state)


def pilot_status(owner, root=ROOT):
    owner, state, _ = _load(owner, root)
    return _summary(owner, state)


def calibrate(transfer, output, root=ROOT):
    """Only this labelled path injects owner fixture clocks; no human completion."""
    output, transfer = safe_owned_path(output, root), safe_owned_path(transfer, root)
    if output.is_relative_to(transfer):
        raise ValueError("OUTPUT_MUST_NOT_NEST_IN_TRANSFER")
    output.mkdir(parents=True, exist_ok=False)
    fixture = read_json(Path(root) / "reader_side/learning/calibration.json")
    checks = []
    def check(name, passed):
        checks.append({"name": name, "passed": bool(passed)})
    tick = 0
    def clock(advance=1):
        nonlocal tick
        tick += advance * 1_000_000_000
        return {"kind": "PROTECTED_SYNTHETIC_CLOCK", "wall_ns": fixture["clock_start_wall_ns"] + tick,
                "monotonic_ns": fixture["clock_start_monotonic_ns"] + tick, "host_boot": fixture["clock_host_boot"]}
    result = {"schema": "cp13-calibration-result/v1", "status": "FAIL", "origin": SYNTHETIC,
              "human_trial_status": "PENDING_REAL_HUMAN_TRIAL", "rubric_validity": "PENDING_HUMAN_VALIDATION",
              "checks": checks, "owner_key_retained_in_output": False}
    try:
        with tempfile.TemporaryDirectory(prefix="cp13-owner-calibration-") as temporary:
            owner, inputs = Path(temporary) / "owner", Path(temporary) / "inputs"
            inputs.mkdir()
            trial = output / "trial"
            start_trial(transfer, owner, trial, fixture["participant"], fixture["reviewers"], fixture["coordinator"], True,
                        root, synthetic=True, clock=clock())
            check("baseline_has_exact_task_without_transfer_knowledge", (trial / "baseline_prompt.md").is_file()
                  and not (trial / "team_knowledge.json").exists() and not (trial / "transfer_material").exists())
            for task, text in fixture["answers"].items():
                (inputs / (task + ".md")).write_text(text + "\n")
            submit_answer(owner, "baseline", inputs / "baseline.md", root, clock())
            try:
                release_retention(owner, root, clock())
                check("early_delay_refused", False)
            except ValueError as exc:
                check("early_delay_refused", str(exc) == "DELAY_NOT_ELAPSED")
            try:
                release_transfer(owner, root, clock())
                check("transfer_before_retention_refused", False)
            except ValueError as exc:
                check("transfer_before_retention_refused", str(exc) == "RETENTION_MUST_BE_SEALED_BEFORE_TRANSFER")
            release_retention(owner, root, clock(read_json(Path(root) / PROTOCOL)["delay_seconds"]))
            check("no_transfer_material_before_retention", not (trial / "transfer_material").exists())
            submit_answer(owner, "retention", inputs / "retention.md", root, clock())
            release_transfer(owner, root, clock())
            check("only_fault_observations_released", not list((trial / "transfer_material").glob("U*"))
                  and (trial / "transfer_material/T03_new_request.json").is_file())
            check("knowledge_card_withheld_until_transfer_answer", not (trial / "team_knowledge.json").exists())
            submit_answer(owner, "transfer", inputs / "transfer.md", root, clock())
            check("knowledge_card_released_after_transfer_answer", (trial / "team_knowledge.json").is_file())
            dimensions = list(read_json(Path(root) / RUBRIC)["dimensions"])
            for index, reviewer in enumerate(fixture["reviewers"]):
                form = read_json(trial / "review_forms" / (reviewer + ".json"))
                profile = fixture["ratings_a" if index == 0 else "ratings_b"]
                form["ratings"] = {task: dict(zip(dimensions, profile[task])) for task in TASKS}
                form["rationales"] = {task: "Synthetic fixture rationale; no human judgment was obtained." for task in TASKS}
                path = inputs / (reviewer + ".json")
                write_json(path, form)
                record_score(owner, reviewer, path, root, clock())
                if index == 0:
                    check("first_raw_review_not_published_early", not (trial / "reviews").exists())
            before = pilot_status(owner, root)
            check("raw_disagreement_preserved", bool(before["disagreements"]))
            raw_hashes = dict(before["review_sha256"])
            form = read_json(trial / "adjudication_form.json")
            form["ratings"] = {task: dict(zip(dimensions, fixture["adjudicated_ratings"][task])) for task in TASKS}
            form["rationales"] = {task: "Separate synthetic adjudication; original ratings retained." for task in TASKS}
            write_json(inputs / "adjudication.json", form)
            final = adjudicate(owner, inputs / "adjudication.json", root, clock())
            check("adjudication_does_not_replace_raw_scores", final["review_sha256"] == raw_hashes
                  and final["disagreements"] == before["disagreements"] and final["phase"] == "ADJUDICATED")
            check("synthetic_clock_does_not_claim_real_elapsed_delay", final["real_clock_delay_elapsed"] is False)
            check("competence_and_validity_remain_unestablished", final["human_competence"] == "NOT_ESTABLISHED_BY_AUTOMATION"
                  and final["rubric_validity"] == "PENDING_HUMAN_VALIDATION")
            result["pilot_status"] = final
            result["owner_event_signatures_verified_during_run"] = True
            check("key_not_in_public_artifacts", not any(path.name == "owner.key" for path in output.rglob("*")))
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        result["error"] = type(exc).__name__ + ":" + str(exc)
        check("calibration_completed", False)
    result["status"] = "PASS_SYNTHETIC_CALIBRATION_ONLY" if checks and all(item["passed"] for item in checks) else "FAIL"
    result["evidence_sha256"] = tree_hashes(output)
    write_json(output / "CALIBRATION_RESULT.json", result)
    return result
