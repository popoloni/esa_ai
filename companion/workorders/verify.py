#!/usr/bin/env python3
"""Exercise EDOD schema rejection, real runner stages and route diagnostics."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from progress import derive
from validate import validate_order

ROOT = Path(__file__).resolve().parent
COMPANION = ROOT.parent
PACKAGE = COMPANION.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.absolute()
    if output.exists() or output.with_suffix("").exists():
        raise ValueError("Use a new output path; preserve prior evidence.")
    work = output.with_suffix("")
    work.mkdir(parents=True)
    commands, findings = [], []

    def command(arguments, expected=0, *, script="start.py"):
        argv = [sys.executable, str(COMPANION / script), *map(str, arguments)]
        result = subprocess.run(argv, cwd=PACKAGE, text=True,
                                capture_output=True, timeout=60)
        commands.append({"argv": argv, "returncode": result.returncode,
                         "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode != expected:
            raise AssertionError(commands[-1])
        return result

    def record(name, **data):
        findings.append({"name": name, "status": "PASS", **data})

    def receipt(name):
        return work / (name + ".json")

    def read(name):
        return json.loads(receipt(name).read_text())

    def states(report):
        progress = report["verification_progress"]
        assert progress == derive(report)
        assert list(progress["stages"]) == ["startup", "integrity", "contract",
                                          "integration", "artifact", "authorization"]
        return progress["stages"]

    error = None
    try:
        command(["--all", "--output", receipt("schema")],
                script="workorders/validate.py")
        assert read("schema")["orders_checked"] == 20
        assert read("schema")["status"] == "PASS"
        base = json.loads((ROOT / "orders/mission_G1.json").read_text())
        mutants = []
        def mutation(name, edit):
            altered = copy.deepcopy(base)
            edit(altered)
            errors = validate_order(altered)
            assert errors, name
            mutants.append({"name": name, "errors": errors})
        mutation("missing_authority_version", lambda x:
                 x["expect"]["authority"].pop("version"))
        mutation("autonomy_is_not_evidence", lambda x:
                 x.update(evidence_profile="autonomous_B"))
        mutation("empty_acceptance", lambda x:
                 x["expect"].update(acceptance=[]))
        mutation("boolean_budget", lambda x:
                 x["delegate"]["budget"].update(max_attempts=True))
        mutation("zero_attempt_budget", lambda x:
                 x["delegate"]["budget"].update(max_attempts=0))
        mutation("timeout_outside_runner_limit", lambda x:
                 x["delegate"]["budget"].update(check_timeout_seconds=61))
        mutation("unknown_approval_field", lambda x:
                 x.update(approved_by_tests=True))
        mutation("editable_protected_overlap", lambda x:
                 x["delegate"]["editable_paths"].append("docs/contract.md"))
        mutation("writable_parent_contains_protected_file", lambda x:
                 x["delegate"].update(editable_paths=["tests/"],
                     protected_paths=["tests/test_g1_slice.py"]))
        mutation("command_without_argv", lambda x:
                 x["observe"]["checks"][0].update(argv=[]))
        mutation("manual_review_as_command", lambda x:
                 x["observe"]["checks"][0].update(method="review"))
        positive = copy.deepcopy(base)
        positive["delegate"]["editable_paths"].append("analysis.md")
        assert not validate_order(positive)
        investigation_ids = []
        for order_path in sorted((ROOT / "orders").glob("*.json")):
            order = json.loads(order_path.read_text())
            if order["evidence_profile"] == "investigation":
                investigation_ids.append(order["id"])
                assert not validate_order(order)
                assert all(check["method"] == "review"
                           for check in order["observe"]["checks"])
        assert investigation_ids == ["chapter_02", "chapter_06", "chapter_12"]
        positive["evidence_profile"] = "investigation"
        assert not validate_order(positive)
        (work / "SCHEMA_MUTANTS.json").write_text(json.dumps(mutants, indent=2)+"\n")
        record("twenty_orders_and_discriminating_schema_controls",
               valid_orders=20, rejected_mutants=len(mutants), positive_controls=2,
               investigation_cases=investigation_ids)

        g1 = work / "g1"
        command(["new", "G1", "--dest", g1])
        refused = command(["check", "G1", "--candidate", g1,
                           "--output", receipt("g1-before-decision")], expected=2)
        assert "OWNER_DECISION_REQUIRED" in refused.stderr
        assert not receipt("g1-before-decision").exists()
        record("g1_entry_refusal_is_not_a_run", receipt_emitted=False,
               observed_error="OWNER_DECISION_REQUIRED")
        question = work / "question.md"
        question.write_text("What should lookup return for a missing ID or missing database?\n")
        command(["clarify", "G1", "--candidate", g1, "--question-file", question])
        command(["check", "G1", "--candidate", g1,
                 "--output", receipt("g1-starter")], expected=1)
        first = read("g1-starter")
        st = states(first)
        assert "NotImplementedError" in first["stderr"]
        assert st["contract"]["status"] == "FAIL"
        assert st["contract"]["behavior_reached"] is True
        assert st["integration"]["status"] == "NOT_RUN"
        record("g1_expected_starter_failure_reached_code", tests=first["tests_run"])
        shutil.copy2(COMPANION / "solutions/G1/booking.py", g1 / "booking.py")
        command(["check", "G1", "--candidate", g1,
                 "--output", receipt("g1-positive")])
        st = states(read("g1-positive"))
        assert st["contract"]["status"] == "PASS"
        assert st["integration"]["status"] == "NOT_RUN"
        command(["check", "G1", "--candidate", g1, "--select", "all",
                 "--output", receipt("g1-final-scope")], expected=1)
        all_scope = read("g1-final-scope")
        assert all_scope["groups"]["g1_slice"]["status"] == "PASSED"
        assert all_scope["groups"]["g1_final_api"]["status"] == "FAILED"
        record("g1_slice_vs_future_scope_is_distinct")
        command(["continue", "G1", "--candidate", g1,
                 "--output", receipt("g1-continuation")])
        st = states(read("g1-continuation"))
        assert st["integration"]["status"] == "PASS"
        assert st["artifact"]["status"] == "NOT_RUN"
        assert st["authorization"]["status"] == "NOT_RUN"
        record("g1_real_integration_does_not_authorize_release")
        before = receipt("g1-positive").read_bytes()
        refused = command(["check", "G1", "--candidate", g1,
                           "--output", receipt("g1-positive")], expected=2)
        assert "Output already exists" in refused.stderr
        assert receipt("g1-positive").read_bytes() == before
        record("existing_receipt_refusal_preserves_original")
        marker = work / "would-have-imported.txt"
        with (g1 / "booking.py").open("a") as stream:
            stream.write("\nfrom pathlib import Path\nPath("+repr(str(marker))+").write_text('ran')\n")
        with (g1 / "tests/test_g1_slice.py").open("a") as stream:
            stream.write("\n# deliberately changed protected input\n")
        command(["continue", "G1", "--candidate", g1,
                 "--output", receipt("integrity-stop")], expected=1)
        stopped = read("integrity-stop")
        st = states(stopped)
        assert stopped["tests_run"] == 0 and not marker.exists()
        assert st["integrity"]["status"] == "FAIL"
        assert st["contract"]["status"] == "NOT_RUN"
        assert st["integration"]["status"] == "NOT_RUN"
        record("integrity_stop_executes_no_candidate", tests_run=0,
               import_marker_created=False)

        b1 = work / "b1"
        command(["new", "B1", "--dest", b1])
        command(["check", "B1", "--candidate", b1,
                 "--output", receipt("b1-starter")], expected=1)
        broken = read("b1-starter")
        assert states(broken)["contract"]["behavior_reached"] is True
        record("b1_fault_is_a_candidate_result", failed_methods=[
            name for group in broken["groups"].values()
            for name in group["methods_failed"] + group["methods_errored"]])
        refused = command(["advance", "B2", "--from-candidate", b1,
                           "--dest", work / "wrong-predecessor"], expected=2)
        assert "B1 v2 extension" in refused.stderr
        assert not (work / "wrong-predecessor").exists()
        record("b2_wrong_api_predecessor_stops_before_creation")
        (b1 / "src/treasury/routing.py").write_text("def broken(:\n")
        command(["check", "B1", "--candidate", b1,
                 "--output", receipt("import-failure")], expected=1)
        bad_import = read("import-failure")
        st = states(bad_import)
        assert "_FailedTest" in bad_import["stderr"]
        assert st["contract"]["status"] == "FAIL"
        assert st["contract"]["behavior_reached"] is False
        assert st["integration"]["status"] == "NOT_RUN"
        record("import_placeholder_does_not_claim_behavior")

        for mission in ("B2", "B3", "B4"):
            dest = work / mission.lower()
            command(["new", mission, "--dest", dest])
            spec = json.loads((COMPANION / "curriculum/MANIFEST.json").read_text())["missions"][mission]
            shutil.copy2(COMPANION / spec["reference"], dest / spec["module"])
            command(["continue", mission, "--candidate", dest,
                     "--output", receipt(mission.lower()+"-continuation")])
            report = read(mission.lower()+"-continuation")
            st = states(report)
            assert st["contract"]["status"] == "PASS"
            assert st["integration"]["status"] == "PASS"
            assert st["authorization"]["status"] == "NOT_RUN"
        classification = json.loads((work / "b2-continuation/classification.json").read_text())
        assert classification["result"]["records"][-1]["status"] == "DEFERRED"
        diagnosis = json.loads((work / "b4-continuation/diagnosis.json").read_text())
        assert diagnosis["observation"]["status"] == "WRONG_LEDGER"
        record("brownfield_expected_outcomes_and_positive_continuations",
               missions=["B2", "B3", "B4"], last_budget_outcome="DEFERRED",
               incident_diagnosis="WRONG_LEDGER")
        (work / "b2/intake.py").unlink()
        command(["continue", "B2", "--candidate", work / "b2",
                 "--output", receipt("b2-missing-module")], expected=1)
        missing = read("b2-missing-module")
        st = states(missing)
        assert missing["tests_run"] == 0
        assert st["integrity"]["status"] == "FAIL"
        assert st["contract"]["status"] == "NOT_RUN"
        record("missing_module_remains_integrity_failure_after_handoff_status",
               tests_run=0)
        # Execute the existing missing-provenance fixture and retain its actual
        # exception code, then execute the valid-evidence control separately.
        probe = work / "provenance_probe.py"
        probe.write_text("import json,sys\nfrom pathlib import Path\n"
            + "sys.path[:0]=" + repr([str(work / "b3"), str(work / "b3/tests")]) + "\n"
            + "import test_b3 as t\nx=t.PersistentDecisions()\nx.setUp()\n"
            + "try:\n p,row,proof=x.seed_legacy();before=p.read_bytes()\n"
            + " try:t.ledger.migrate_legacy(p,t.CATALOG,{})\n"
            + " except t.ledger.HistoryError as e:code=e.code\n"
            + " else:raise AssertionError('missing provenance accepted')\n"
            + " assert p.read_bytes()==before\n"
            + " positive=t.ledger.migrate_legacy(p,t.CATALOG,proof)\n"
            + " print(json.dumps({'negative_code':code,'bytes_preserved':True,'positive':positive}))\n"
            + "finally:x.doCleanups()\n")
        result = subprocess.run([sys.executable, str(probe)], text=True,
                                capture_output=True, timeout=30)
        commands.append({"argv": [sys.executable, str(probe)],
                         "returncode": result.returncode, "stdout": result.stdout,
                         "stderr": result.stderr})
        assert result.returncode == 0, result.stderr
        observed = json.loads(result.stdout)
        assert observed["negative_code"] == "LEGACY_PROVENANCE_MISMATCH"
        record("b3_provenance_refusal_has_positive_control", **observed)
        assert "NOT_APPLICABLE" not in {
            s["status"] for s in states(read("g1-positive")).values()}
        record("absence_never_becomes_not_applicable_or_authorization")
    except Exception as exc:
        error = repr(exc)
    finally:
        (work / "COMMANDS.json").write_text(json.dumps(commands, indent=2)+"\n")
        sources = [COMPANION / "start.py", COMPANION / "curriculum.py"]
        sources += sorted(p for p in ROOT.rglob("*") if p.is_file()
                          and "__pycache__" not in p.parts)
        sources += [PACKAGE / "manuscript/19_workbook_note.md"]
        sources += [p for p in (PACKAGE / "manuscript").glob("*_mission_*.md")]
        report = {"schema": "esa-loop-practice-qa/v1",
                  "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                  "status": "FAIL" if error else "PASS", "error": error,
                  "checks": findings, "checks_passed": len(findings),
                  "commands_executed": len(commands),
                  "inputs_sha256": {str(p.relative_to(PACKAGE)): digest(p)
                                    for p in sorted(set(sources))},
                  "artifacts": str(work), "observed_model_runs": 0,
                  "observed_human_participants": 0,
                  "limits": "Constructed controls executed locally. Planning budgets "
                      "are not measured durations; schema validity is not authority; "
                      "the stage derivation does not itself execute checks."}
        output.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"status": report["status"], "checks": len(findings),
                      "commands": len(commands), "error": error}, indent=2))
    return int(error is not None)


if __name__ == "__main__":
    sys.exit(main())
