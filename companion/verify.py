#!/usr/bin/env python3
"""Reproduce complete-edition practice controls with commands, outputs, receipts and candidate bytes.

Use a fresh directory: python3 companion/verify.py --output validation/full_practice/CP12
Controlled fixtures are not learner observations; historical replay is labeled.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or output.is_relative_to(ROOT):
        parser.error("Choose a fresh output directory outside companion/.")
    output.mkdir(parents=True)
    work, receipts = output / "candidates", output / "receipts"
    receipts.mkdir()
    scenarios, commands, matrix = [], [], []
    started = time.monotonic()

    def execute(label, command, expected=0, **options):
        result = subprocess.run(command, text=True, capture_output=True, timeout=70, **options)
        record = {"label": label, "command": command, "expected_returncode": expected, "returncode": result.returncode}
        commands.append(record)
        directory = output / "commands" / f"{len(commands):02d}_{label}"
        directory.mkdir(parents=True)
        (directory / "command.json").write_text(json.dumps(record, indent=2) + "\n")
        (directory / "stdout.txt").write_text(result.stdout)
        (directory / "stderr.txt").write_text(result.stderr)
        assert result.returncode == expected, (label, result.returncode, result.stdout, result.stderr)
        return result

    def cli(label, words, expected=0):
        result = execute(label, [sys.executable, str(ROOT / "start.py"), *[str(word) for word in words]], expected)
        if words[:2] == ["new", "G1"] and expected == 0:
            destination = Path(words[words.index("--dest") + 1])
            assert not (destination / "tests").exists()
            assert not (destination / "docs/G1-OD-01.md").exists()
            assert "return None" not in (destination / "booking.py").read_text()
            import ast
            initial = ast.parse((destination / "booking.py").read_text())
            lookup = next(node for node in initial.body if isinstance(node, ast.FunctionDef) and node.name == "get_reservation")
            assert lookup.returns is None
            assert "dict | None" not in (destination / "docs/G1-I01.md").read_text()
            assert "unknown" not in (ast.get_docstring(lookup) or "").lower()
            initial_text = "\n".join(x.read_text() for x in destination.rglob("*") if x.is_file())
            assert "unknown identifier returns" not in initial_text.lower()
            execute(label + "_predecision_refused", [sys.executable, str(ROOT / "start.py"), "check", "G1", "--candidate", str(destination), "--output", str(receipts / (label + "_blocked.json"))], 2)
            question = destination / "QUESTIONS.md"
            question.write_text("Author verification fixture: what should a lookup return when no reservation has that identifier? What should happen if storage is missing?\n")
            execute(label + "_clarify", [sys.executable, str(ROOT / "start.py"), "clarify", "G1", "--candidate", str(destination), "--question-file", str(question)])
            assert (destination / "docs/G1-OD-01.md").is_file()
            assert (destination / "tests/test_g1_slice.py").is_file()
        return result

    def note(name, **evidence):
        scenarios.append({"name": name, "status": "PASS", **evidence})

    def read(label):
        return json.loads((receipts / f"{label}.json").read_text())

    def check(label, mission, candidate, expected=0, extra=()):
        cli(label, ["check", mission, "--candidate", candidate, "--output", receipts / f"{label}.json", *extra], expected)
        return read(label)

    def handoff(label, mission, candidate, expected=0):
        cli(label, ["continue", mission, "--candidate", candidate, "--output", receipts / f"{label}.json"], expected)
        return read(label)

    def summary(group):
        return {"tests_run": group["tests_run"], "passed": group["methods_passed"],
                "failed": group["methods_failed"], "errored": group["methods_errored"]}

    try:
        cli("doctor", ["doctor"])
        note("Runtime available and all pinned upstream bytes unchanged")
        g1 = work / "g1"
        cli("new_g1", ["new", "G1", "--dest", g1])
        initial_g1 = check("g1_initial", "G1", g1, 1)
        assert initial_g1["tests_run"] == 4 and "NotImplementedError" in initial_g1["stderr"]
        note("G1 starter exposes the unimplemented public interface", receipt="g1_initial.json")
        shutil.copy2(ROOT / "solutions/G1/booking.py", g1 / "booking.py")
        first = check("g1_slice", "G1", g1)
        alias = check("g1_first_alias", "G1", g1, extra=["--select", "first"])
        assert first["tests_run"] == alias["tests_run"] == 4
        full = check("g1_slice_all", "G1", g1, 1, ["--select", "all"])
        assert full["tests_run"] == 14 and full["groups"]["g1_slice"]["status"] == "PASSED"
        assert full["groups"]["g1_final_api"]["methods_passed"] == 3
        assert len(full["groups"]["g1_final_api"]["methods_failed"]) == 7
        assert not full["groups"]["g1_final_api"]["methods_errored"]
        note("G1 slice four pass; ten separate final-contract diagnostics remain 3 pass / 7 failures",
             receipts=["g1_slice.json", "g1_first_alias.json", "g1_slice_all.json"], first_is_compatibility_alias=True)
        canonical_g1_hash = sha(g1 / "booking.py")
        g1_handoff = handoff("g1_handoff", "G1", g1)
        assert g1_handoff["status"] == "SCOPED_HANDOFF_READY" and g1_handoff["candidate_retained"]
        assert len(g1_handoff["persistence_probe"]["processes"]) == 2
        record = g1_handoff["persistence_probe"]["reader"]["reservation"]
        assert record == {"reservation_id": 1, **g1_handoff["persistence_probe"]["writer"]["request"]}
        assert sha(g1 / "booking.py") == canonical_g1_hash
        note("G1 second process reads the retained candidate through get_reservation", receipt="g1_handoff.json")

        alternative_g1 = work / "g1_alternative"
        cli("new_g1_alternative", ["new", "G1", "--dest", alternative_g1])
        shutil.copy2(ROOT / "solutions/G1/booking_alternative.py", alternative_g1 / "booking.py")
        alternative = check("g1_alternative_slice", "G1", alternative_g1)
        alternative_handoff = handoff("g1_alternative_handoff", "G1", alternative_g1)
        assert alternative["tests_run"] == 4 and alternative_handoff["status"] == "SCOPED_HANDOFF_READY"
        assert alternative_handoff["persistence_probe"]["reader"]["reservation"] == record
        assert sha(alternative_g1 / "booking.py") != canonical_g1_hash
        schemas = {}
        for name, evidence in (("canonical", g1_handoff), ("alternative", alternative_handoff)):
            with sqlite3.connect(evidence["persistence_probe"]["database"]) as connection:
                schemas[name] = connection.execute("SELECT name, sql FROM sqlite_master WHERE type='table'").fetchall()
        assert schemas["canonical"][0][0] == "reservations"
        assert schemas["alternative"][0][0] == "bookings_v2"
        assert all("request_hash" not in table_sql for tables in schemas.values() for _, table_sql in tables)
        note("Different G1 schemas pass the same public checks and handoff without request_hash",
             receipts=["g1_alternative_slice.json", "g1_alternative_handoff.json"], author_inspection_of_schemas=schemas,
             inspection_note="This inspection records how the controlled fixtures differ; it is not a learner gate.")

        wrong = work / "g1_wrong_asset"
        cli("new_g1_wrong_asset", ["new", "G1", "--dest", wrong])
        text = (ROOT / "solutions/G1/booking.py").read_text()
        changed = text.replace('        trusted_member_id, asset_id,',
                               '        trusted_member_id, "WRONG-ASSET",')
        assert changed != text
        (wrong / "booking.py").write_text(changed)
        wrong_result = handoff("g1_wrong_asset_handoff", "G1", wrong, 1)
        assert wrong_result["status"] == "HANDOFF_BLOCKED" and "persistence_probe" not in wrong_result
        assert "test_first_reservation_confirms_and_public_read_matches" in wrong_result["groups"]["g1_slice"]["methods_failed"]
        note("Wrong stored asset is rejected by its intended public assertion before handoff", receipt="g1_wrong_asset_handoff.json")

        memory = work / "g1_memory_only"
        cli("new_g1_memory_only", ["new", "G1", "--dest", memory])
        memory_source = (ROOT / "solutions/G1/starter.py").read_text().split("def init_db", 1)[0]
        memory_source += """import sqlite3
_records = {}
def init_db(path):
    sqlite3.connect(path).close()
    _records.setdefault(str(path), {})
def reserve(path, **request):
    record = {"reservation_id": 1, **request}
    _records.setdefault(str(path), {})[1] = record
    return Outcome(201, "confirmed", 1)
def get_reservation(path, reservation_id):
    if not Path(path).exists():
        raise sqlite3.OperationalError("storage absent")
    record = _records.get(str(path), {}).get(reservation_id)
    return dict(record) if record is not None else None
"""
        (memory / "booking.py").write_text(memory_source)
        memory_result = handoff("g1_memory_only_handoff", "G1", memory, 1)
        assert memory_result["groups"]["g1_slice"]["status"] == "PASSED"
        assert memory_result["status"] == "HANDOFF_BLOCKED"
        assert memory_result["persistence_probe"]["reader"]["status"] == "PUBLIC_RECORD_MISSING"
        note("In-memory fake passes four local cases but fails actual second-process public read", receipt="g1_memory_only_handoff.json")

        probe_dir = g1 / "author_probe"
        probe_dir.mkdir()
        shutil.copy2(ROOT / "checks/test_g1_integrity_fault.py", probe_dir / "test_integrity.py")
        probe_env = os.environ.copy()
        probe_env.update(PYTHONPATH=str(g1), PYTHONDONTWRITEBYTECODE="1")
        fault_control = execute("g1_integrity_probe_positive", [sys.executable, "-m", "unittest", "discover", "-s", str(probe_dir), "-v"], cwd=g1, env=probe_env)
        assert "Ran 1 test" in fault_control.stderr and "OK" in fault_control.stderr
        note("G1 supplemental fault probe passes on correct code before rejecting the constructed swallowing variant")

        full_reference = work / "g1_full_reference"
        cli("g1_full_reference", ["solution", "G1", "--variant", "full", "--dest", full_reference])
        full_result = check("g1_full_reference_all", "G1", full_reference, extra=["--select", "all", "--reference"])
        assert full_result["tests_run"] == 14 and full_result["methods_passed"] == 14
        note("Full reference with public reader passes slice four plus adapted final ten", receipt="g1_full_reference_all.json")
        shutil.copy2(ROOT / "upstream/base_13a1182/greenfield_studio/reference/booking.py", full_reference / "booking.py")
        historical = check("g1_original_ten", "G1", full_reference, extra=["--select", "historical", "--reference"])
        assert historical["tests_run"] == historical["methods_passed"] == 10
        assert sha(full_reference / "historical_tests/test_booking.py") == sha(ROOT / "upstream/base_13a1182/greenfield_studio/tests/test_booking.py")
        note("Original reference and original ten tests pass unchanged in separately labeled historical compatibility scope", receipt="g1_original_ten.json")
        cli("reference_not_learner", ["check", "G1", "--candidate", full_reference,
                                    "--output", receipts / "refused_reference.json"], 2)
        assert not (receipts / "refused_reference.json").exists()
        note("Reference exports require explicit reference verification")

        target = g1 / "tests/test_g1_slice.py"
        original = target.read_bytes()
        target.write_bytes(original + b"\n# changed protected oracle\n")
        tamper = check("g1_protected_change", "G1", g1, 1)
        assert tamper["status"] == "INPUT_INTEGRITY_FAILED" and tamper["tests_run"] == 0
        target.write_bytes(original)
        note("Changed G1 public oracle is refused before execution", receipt="g1_protected_change.json")

        b1 = work / "b1"
        cli("new_b1", ["new", "B1", "--dest", b1])
        initial_b1 = check("b1_initial", "B1", b1, 1)
        historical = initial_b1["groups"]["b1_core"]
        assert historical["tests_run"] == 7 and historical["methods_passed"] == 3
        assert len(historical["methods_failed"]) == len(historical["methods_errored"]) == 2
        note("Unchanged B1 starter reproduces 3 passes / 2 failures / 2 errors on seven core methods",
             receipt="b1_initial.json", current_groups={k:summary(v) for k,v in initial_b1["groups"].items()})
        router = b1 / "src/treasury/routing.py"
        shutil.copy2(ROOT / "solutions/B1/routing.py", router)
        good_b1 = check("b1_canonical", "B1", b1)
        b1_hash = sha(router)
        b1_handoff = handoff("b1_canonical_handoff", "B1", b1)
        assert good_b1["tests_run"] == good_b1["methods_passed"] == 12
        assert b1_handoff["status"] == "CONTEXT_HANDOFF_READY" and b1_handoff["candidate_retained"]
        assert sha(router) == b1_hash and len(b1_handoff["context_step"]["preview"]["rows"]) == 3
        note("Canonical repair passes seven core plus five public extended checks and continues with unchanged bytes",
             receipts=["b1_canonical.json", "b1_canonical_handoff.json"])
        b2 = work / "b1_alternative"
        cli("new_b1_alternative", ["new", "B1", "--dest", b2])
        alt_router = b2 / "src/treasury/routing.py"
        shutil.copy2(ROOT / "solutions/B1/routing_alternative.py", alt_router)
        alternate_b1 = check("b1_alternative", "B1", b2)
        alternate_handoff = handoff("b1_alternative_handoff", "B1", b2)
        assert alternate_b1["methods_passed"] == 12
        assert alternate_handoff["status"] == "CONTEXT_HANDOFF_READY"
        assert alternate_handoff["candidate_retained"] and sha(alt_router) != b1_hash
        assert alternate_handoff["context_step"]["preview"] == b1_handoff["context_step"]["preview"]
        note("Different correct B1 repair passes and continues into the same read-only preview", receipts=["b1_alternative.json", "b1_alternative_handoff.json"])

        index = json.loads((ROOT / "candidates/INDEX.json").read_text())
        for mission in ("G1", "B1"):
            identifiers = index["candidate_ids"][mission]
            for identifier in identifiers:
                label = "review_" + identifier.replace("-", "_")
                cli(label, ["review", mission, "--candidate-id", identifier,
                            "--output", receipts / f"{label}.json"])
                review = read(label)
                truth = review["ground_truth"]
                assert truth["origin"] == "CONSTRUCTED_TEACHING_VARIANT"
                assert not review["learner_source_modified"]
                groups = review["groups"]
                if mission == "B1":
                    assert (groups["b1_core"]["status"] == "PASSED") == truth["expected_core_pass"]
                    assert (groups["b1_extended"]["status"] == "PASSED") == truth["expected_extended_pass"]
                    assert (review["supplemental_probe"]["status"] == "PASSED") == truth["expected_supplemental_pass"]
                else:
                    assert (groups["g1_slice"]["status"] == "PASSED") == truth["expected_slice_pass"]
                    assert (review["supplemental_probe"]["status"] == "PASSED") == truth["expected_supplemental_pass"]
                observed = set()
                for group in [*groups.values(), review.get("supplemental_probe")]:
                    if group:
                        observed.update(group["methods_failed"] + group["methods_errored"])
                assert set(truth["targeted_assertions"]) <= observed, (identifier, observed)
                if truth["expected_decision"] == "REJECT":
                    assert review["status"] == "CHECKS_FAILED"
                else:
                    assert review["status"] == "SELECTED_CHECKS_PASSED"
                    if truth["expected_decision"] == "ASK":
                        assert truth["required_human_decision"]
                matrix.append({"candidate_id": identifier, "mission": mission, "origin": truth["origin"],
                               "groups": {k:summary(v) for k,v in groups.items()},
                               "supplemental_probe": summary(review["supplemental_probe"]) if review.get("supplemental_probe") else None,
                               "expected_decision": truth["expected_decision"], "decisive_assertions": truth["targeted_assertions"],
                               "receipt": f"receipts/{label}.json"})
                note(f"Constructed proposal {identifier} has the predicted bounded result", receipt=f"{label}.json",
                     decisive_assertions=truth["targeted_assertions"])
        assert sha(router) == b1_hash and sha(g1 / "booking.py") == canonical_g1_hash
        note("Review commands leave both learner implementations unchanged")

        cli("review_b1_core_native", ["review", "B1", "--candidate-id", "B1-H01",
                                           "--output", receipts / "review_b1_core_native.json"])
        actual = read("review_b1_core_native")
        assert actual["candidate_sha256"] == "dac968f4738761cc85a6b71f0d7265a2d8d1860f122cd22576a9645bc9139fe7"
        assert actual["groups"]["b1_core"]["methods_passed"] == 7
        assert actual["status"] == "HISTORICAL_SCOPE_PASSED_CURRENT_API_DIFFERENCE"
        assert actual["groups"]["b1_extended"]["methods_failed"] == ["test_non_string_argument_is_programming_error"]
        assert not actual["ground_truth"]["actual_model_rationale_available"]
        note("Exact historical native edit replays seven original passes; new API type requirement is a separate migration difference",
             receipt="review_b1_core_native.json", sha256=actual["candidate_sha256"])

        shutil.copy2(ROOT / "candidates/archived/B1/b1-nan-only/variant.py", router)
        nan_old = check("b1_nan_historical", "B1", b1, extra=["--select", "historical"])
        assert nan_old["tests_run"] == 7 and nan_old["status"] == "SELECTED_CHECKS_PASSED"
        nan_next = handoff("b1_nan_handoff", "B1", b1, 1)
        assert nan_next["status"] == "HANDOFF_BLOCKED" and "context_step" not in nan_next
        assert set(nan_next["groups"]["b1_extended"]["methods_failed"]) == {"test_positive_infinity_rejected", "test_short_infinity_rejected"}
        cli("historical_only_cannot_continue", ["continue", "B1", "--candidate", b1, "--select", "historical",
                                               "--output", receipts / "refused_historical_handoff.json"], 2)
        note("Seven-pass is_nan candidate is blocked by current extended assertions and cannot bypass continuation with historical selection",
             receipts=["b1_nan_historical.json", "b1_nan_handoff.json"])
        shutil.copy2(ROOT / "candidates/archived/B1/b1-boundary-inclusive/variant.py", router)
        boundary = handoff("b1_changed_after_pass", "B1", b1, 1)
        assert boundary["status"] == "HANDOFF_BLOCKED"
        assert boundary["groups"]["b1_core"]["methods_failed"] == ["test_exact_boundary_requires_review"]
        assert not boundary["groups"]["b1_core"]["methods_errored"]
        note("Stale passing receipt cannot authorize changed bytes; boundary mutant fails its exact assertion", receipt="b1_changed_after_pass.json")
        shutil.copy2(ROOT / "solutions/B1/routing.py", router)
        target = b1 / "tests/test_routing_extended.py"
        original = target.read_bytes()
        target.write_bytes(original + b"\n# changed extended oracle\n")
        tamper = check("b1_extended_protected_change", "B1", b1, 1)
        assert tamper["status"] == "INPUT_INTEGRITY_FAILED" and tamper["tests_run"] == 0
        target.write_bytes(original)
        note("Changed B1 extended oracle is refused before execution", receipt="b1_extended_protected_change.json")
        router.write_text("import time\ntime.sleep(5)\n")
        timeout = check("b1_timeout", "B1", b1, 1, ["--timeout-seconds", "0.2"])
        assert timeout["timed_out"] and timeout["returncode"] is None
        shutil.copy2(ROOT / "solutions/B1/routing.py", router)
        note("Stalled import is bounded and preserves a timeout receipt", receipt="b1_timeout.json")
        kept = sha(receipts / "b1_canonical.json")
        cli("receipt_overwrite_refused", ["check", "B1", "--candidate", b1, "--output", receipts / "b1_canonical.json"], 2)
        assert sha(receipts / "b1_canonical.json") == kept
        cli("workspace_overwrite_refused", ["new", "B1", "--dest", b1], 2)
        assert sha(router) == b1_hash
        note("Existing evidence and learner working directories remain intact")

        g1_ro = check("g1_readonly", "G1", g1, extra=["--select", "readonly"])
        alt_ro = check("g1_alternative_readonly", "G1", alternative_g1, extra=["--select", "readonly"])
        assert g1_ro["tests_run"] == alt_ro["tests_run"] == 2
        note("Both storage schemas read missing paths without creating files and handle URI-special filenames", receipts=["g1_readonly.json", "g1_alternative_readonly.json"])

        before_v2 = sha(router)
        v2 = work / "b1_v2"
        cli("extend_b1_v2", ["extend", "B1", "--candidate", b1, "--dest", v2])
        assert sha(router) == before_v2
        old_under_new = check("b1_v1_under_v2", "B1", v2, 1)
        assert old_under_new["groups"]["b1_core"]["status"] == "PASSED"
        assert old_under_new["groups"]["b1_extended"]["status"] == "PASSED"
        assert old_under_new["groups"]["b1_v2"]["status"] == "FAILED"
        assert "test_unapproved_lexical_forms_are_rejected" in old_under_new["groups"]["b1_v2"]["methods_failed"]
        shutil.copy2(ROOT / "solutions/B1/routing_v2.py", v2 / "src/treasury/routing.py")
        new_under_new = check("b1_v2_implemented", "B1", v2)
        v2_handoff = handoff("b1_v2_handoff", "B1", v2)
        assert new_under_new["tests_run"] == 18 and new_under_new["methods_passed"] == 18
        assert v2_handoff["status"] == "CONTEXT_HANDOFF_READY" and v2_handoff["candidate_retained"]
        assert sha(router) == before_v2
        note("Explicit owner decision v2 invalidates v1 applicability, new implementation passes 18 methods and leaves v1 intact", receipts=["b1_v1_under_v2.json", "b1_v2_implemented.json", "b1_v2_handoff.json"])

        for mission in ("G1", "B1"):
            outcomes = {x["expected_decision"] for x in matrix if x["mission"] == mission}
            expected = {json.loads((ROOT / "candidates" / mission / identifier / "TRUTH.json").read_text())["expected_decision"]
                        for identifier in index["candidate_ids"][mission]}
            assert outcomes == expected
        note("Each neutral-ID pack matches its declared outcomes without assuming one of each", matrix="exports/candidate_matrix.json")

        exports = output / "exports"
        exports.mkdir()
        def compact_output(group):
            lines = []
            for line in group["stderr"].splitlines():
                if line.startswith("test_"):
                    lines.append(re.sub(r" \([^)]*\)", "", line))
                elif line.startswith(("Ran ", "FAILED", "OK")):
                    lines.append(line)
            return "\n".join(lines) + "\n"
        (exports / "b1_before_core.txt").write_text(compact_output(initial_b1["groups"]["b1_core"]))
        (exports / "b1_after_core.txt").write_text(compact_output(good_b1["groups"]["b1_core"]))
        before = (ROOT / "upstream/base_13a1182/reader_side/routing/unsafe_routing_fixture.py").read_text()
        after = (ROOT / "solutions/B1/routing.py").read_text()
        a, b = "def assess" + before.split("def assess", 1)[1], "def assess" + after.split("def assess", 1)[1]
        raw_a, raw_b = a, b
        def reflow_calls(source):
            lines = []
            for line in source.splitlines():
                match = re.fullmatch(r'(\s*)return RoutingDecision\((.*)\)', line)
                if match and len(line) > 66:
                    indent, arguments = match.groups()
                    lines.extend([indent + "return RoutingDecision(", indent + "    " + arguments + ")"])
                else:
                    lines.append(line)
            return "\n".join(lines) + "\n"
        a, b = reflow_calls(a), reflow_calls(b)
        (exports / "b1_faulty_assess.py").write_text(a)
        (exports / "b1_repair.diff").write_text("".join(difflib.unified_diff(a.splitlines(keepends=True), b.splitlines(keepends=True), fromfile="starter/assess", tofile="repaired/assess")))
        compact = {"mission": "B1", "status": b1_handoff["status"],
                   "candidate_sha256": b1_handoff["candidate_sha256_before"],
                   "core": "7/7", "extended": "5/5", "preview_cases": 3,
                   "api_contract": b1_handoff["api_contract"], "recorded_at_utc": b1_handoff["recorded_at_utc"],
                   "command": b1_handoff["command"],
                   "candidate_retained": b1_handoff["candidate_retained"], "human_acceptance": "PENDING"}
        full_hash = compact.pop("candidate_sha256")
        compact_text = json.dumps(compact, indent=2).rstrip()
        compact_text = compact_text[:-1].rstrip() + ',\n  "candidate_sha256":\n"' + full_hash + '"\n}\n'
        assert json.loads(compact_text)["candidate_sha256"] == b1_handoff["candidate_sha256_before"]
        (exports / "b1_handoff_compact.json").write_text(compact_text)
        provenance = {"schema": "esa-printed-excerpt/v1", "method": "Only long RoutingDecision call expressions are line-wrapped as equivalent Python; full source files and original historical bytes are unchanged.",
                      "starter_source": "companion/upstream/base_13a1182/reader_side/routing/unsafe_routing_fixture.py", "starter_source_sha256": sha(ROOT / "upstream/base_13a1182/reader_side/routing/unsafe_routing_fixture.py"),
                      "repair_source": "companion/solutions/B1/routing.py", "repair_source_sha256": sha(ROOT / "solutions/B1/routing.py"),
                      "before_receipt": "receipts/b1_initial.json", "after_receipt": "receipts/b1_canonical.json", "handoff_receipt": "receipts/b1_canonical_handoff.json",
                      "function_layout_changed": a != raw_a or b != raw_b, "historical_tests_changed": False,
                      "output_excerpt_method": "Keep actual test method names, status and summary; omit repetitive unittest class/module qualifier and traceback details."}
        (exports / "PROVENANCE.json").write_text(json.dumps(provenance, indent=2) + "\n")
        compact_g1 = {"mission": "G1", "status": g1_handoff["status"], "slice_checks": "4/4",
                      "public_api": "get_reservation(path, reservation_id)", "separate_processes": 2,
                      "candidate_retained": True, "record": record, "human_acceptance": "PENDING"}
        (exports / "g1_handoff_compact.json").write_text(json.dumps(compact_g1, indent=2) + "\n")
        (exports / "candidate_matrix.json").write_text(json.dumps(matrix, indent=2) + "\n")
        (exports / "README.md").write_text("# Executed book excerpts\n\nThe output excerpts retain actual method names, statuses and summary lines from the named receipts; repetitive unittest class/module qualifiers and traceback detail are omitted for the page. Full stdout/stderr remains in receipts. The starter function and diff reflow long return-call expressions for print while preserving behavior; PROVENANCE.json identifies both complete source files and their hashes. Historical source bytes remain unchanged. Compact JSON selects actual receipt values; it is an excerpt, not a second acceptance record. Historical, extended, slice and final-contract scopes remain distinct.\n")
        status, error = "PASS", None
    except Exception as exc:
        status, error = "FAIL", repr(exc)
    report = {"schema": "esa-full-practice-validation/v1", "status": status,
              "origin": "EXECUTED_DETERMINISTIC_CONTROLS_AND_EXPLICIT_HISTORICAL_REPLAY",
              "candidate_origin": "Current solution and defect fixtures were deliberately copied; no real learner or fresh model session is represented. B1-H01 is exact historical native code.",
              "harness_sha256": {str(path.relative_to(ROOT)):sha(path) for path in
                                  [ROOT / "start.py", ROOT / "verify.py", ROOT / "workorders/progress.py", ROOT / "tools/reservation_persistence.py", ROOT / "checks/test_b1_extended.py", ROOT / "checks/test_b1_conversion_fault.py", ROOT / "checks/test_g1_slice.py", ROOT / "checks/test_g1_full_api.py"]},
              "source_dependencies_sha256": {str(path.relative_to(ROOT)):sha(path) for folder in ("contracts", "checks", "solutions/G1", "solutions/B1", "workorders/orders") for path in sorted((ROOT / folder).glob("*")) if path.is_file()},
              "python": sys.version, "elapsed_process_seconds": time.monotonic() - started,
              "scenarios_passed": len(scenarios), "commands_executed": len(commands),
              "scenarios": scenarios, "error": error,
              "limitations": ["Linux and Python version shown only; no Windows execution", "No fresh model call or human reader pilot",
                              "Full-contract API adaptation cannot prove absence of invisible extra rows",
                              "B1 review fault injection targets the known Decimal seam of supplied packs, not arbitrary learner implementations",
                              "G1 process-boundary review probes are separate from the four local slice methods",
                              "Current pack classification is a teaching design check, not human comprehension",
                              "Integrity and timeouts do not sandbox arbitrary candidate code"]}
    (output / "RESULTS.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": status, "scenarios_passed": len(scenarios), "commands_executed": len(commands),
                      "report": str(output / "RESULTS.json"), "error": error}, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
