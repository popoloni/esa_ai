#!/usr/bin/env python3
"""Execute later-mission controls and preserve every command/receipt.

These are author verification runs of constructed code fixtures. No model or
human learner is observed. Expected starter/proposal failures are positive
controls for the assessment, never concealed as successful implementations.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(destination):
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    candidates, receipts = destination/"candidates", destination/"receipts"
    receipts.mkdir()
    manifest = json.loads((ROOT/"curriculum/MANIFEST.json").read_text())["missions"]
    commands, scenarios, matrix = [], [], []
    started = time.monotonic()
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    environment.pop("PYTHONPATH", None)

    def execute(label, words, expected=0, program="start.py"):
        command = [sys.executable, str(ROOT/program), *map(str, words)]
        try:
            process = subprocess.run(command, text=True, capture_output=True, timeout=100, env=environment)
        except subprocess.TimeoutExpired as exc:
            def decoded(value):return value.decode(errors="replace") if isinstance(value,bytes) else value or ""
            process=subprocess.CompletedProcess(command,None,decoded(exc.stdout),decoded(exc.stderr))
        record = {"label":label, "command":command, "expected_returncode":expected,
                  "returncode":process.returncode, "recorded_at_utc":datetime.now(timezone.utc).isoformat()}
        commands.append(record)
        folder = destination/"commands"/f"{len(commands):03d}_{label}"
        folder.mkdir(parents=True)
        (folder/"command.json").write_text(json.dumps(record,indent=2)+"\n")
        (folder/"stdout.txt").write_text(process.stdout)
        (folder/"stderr.txt").write_text(process.stderr)
        assert process.returncode == expected, (label,process.returncode,process.stdout,process.stderr)
        return process

    def note(name, **evidence):
        scenarios.append({"name":name,"status":"PASS",**evidence})

    def check(label, mission, candidate, expected=0, reference=False, operation="check"):
        target = receipts/(label+".json")
        words = [operation,mission,"--candidate",candidate,"--output",target]
        if reference: words.append("--reference")
        execute(label, words, expected)
        return json.loads(target.read_text())

    def integrate(path, integration_root, label):
        execute(label+"_prepare",["prepare","--candidate",path,"--dest",integration_root],program="integration.py")
        specification=json.loads((integration_root/"INTEGRATION.json").read_text())
        copied=[]
        for role,row in specification["roles"].items():
            workspace=integration_root/row["workspace"]
            reference=ROOT/"solutions/G3"/row["module"]
            shutil.copy2(reference,workspace/row["module"])
            (workspace/row["note"]).write_text(
                "# Deterministic integration control\n\n"
                "Origin: AUTHOR_CONTROLLED_REFERENCE_COPY. No model or human learner run.\n"
                "The validator copied "+str(reference.relative_to(ROOT))+
                " at SHA256 "+sha(reference)+".\n"
                "The shared contract, retained booking source and tests remain protected.\n"
                "Component and combined observations are recorded by the integration helper.\n")
            copied.append({"role":role,"module":row["module"],"source":str(reference.relative_to(ROOT)),
                           "sha256":sha(reference),"note":row["note"]})
        (integration_root/"FIXTURE_ORIGIN.json").write_text(json.dumps({
            "origin":"AUTHOR_EXECUTION_OF_CONSTRUCTED_FIXTURES","observed_model_runs":0,
            "observed_human_pilots":0,"contributions":copied},indent=2)+"\n")
        combined_receipt=integration_root/"REPORT.json"
        execute(label+"_combine",["combine","--workspace",integration_root/"workspace",
                                  "--output",combined_receipt],program="integration.py")
        combined=json.loads(combined_receipt.read_text())
        assert combined["status"]=="INTEGRATION_CHECKS_PASSED"
        assert combined["source_sha256"]["booking.py"]==sha(path/"booking.py")
        assert combined["transport"]["checked_cli_cases"]==9
        note(label.replace("_integration","_deterministic_integration")+"_before_G4",origin="AUTHOR_CONTROLLED_REFERENCE_COPY",
             observed_model_runs=0,receipt=str(combined_receipt.relative_to(destination)),
             receipt_sha256=sha(combined_receipt),archive_sha256=combined["transport"]["archive_sha256"],
             source_sha256=combined["source_sha256"],transport_cases=9)
        return integration_root/"workspace"

    error = None
    try:
        execute("doctor", ["doctor"])
        version_evidence = destination / "issued_entry_compatibility"
        execute("issued_entry_compatibility", ["--output", version_evidence],
                program="curriculum/verify_release_compatibility.py")
        versions = json.loads((version_evidence / "RESULTS.json").read_text())
        assert versions["status"] == "PASS"
        note("issued_learner_entries_survive_upgrade", releases=versions["issued_releases_tested"],
             commands=versions["command_count"], report="issued_entry_compatibility/RESULTS.json")
        # Each entry is useful independently as well as from its predecessor.
        for mission,spec in manifest.items():
            path = candidates/(mission.lower()+"_standalone")
            execute(mission+"_new", ["new",mission,"--dest",path])
            initial = check(mission+"_starter", mission,path,expected=1)
            assert initial["status"] == "CHECKS_FAILED" and initial["tests_run"] == spec["tests"]
            note(mission+"_incomplete_starter_detected", methods=initial["tests_run"],
                 failed=initial["groups"]["contract"]["methods_failed"],errored=initial["groups"]["contract"]["methods_errored"])
            shutil.copy2(ROOT/spec["reference"],path/spec["module"])
            passed = check(mission+"_positive",mission,path)
            assert passed["status"] == "SELECTED_CHECKS_PASSED"
            handoff = check(mission+"_handoff",mission,path,operation="continue")
            assert handoff["status"] == "SCOPED_HANDOFF_READY" and handoff["candidate_retained"]
            assert handoff["demonstration"]["origin"] == "EXECUTED_OFFLINE_TEACHING_FIXTURE"
            note(mission+"_positive_and_executed_continuation",methods=passed["tests_run"],artifacts=list(handoff["demonstration_files_sha256"]))
            reference = candidates/(mission.lower()+"_reference")
            execute(mission+"_solution",["solution",mission,"--dest",reference])
            check(mission+"_reference",mission,reference,reference=True)
            note(mission+"_reference_export")
            for key in spec["candidate_ids"]:
                target = receipts/(key+".json")
                execute(key,["review",mission,"--candidate-id",key,"--output",target])
                result = json.loads(target.read_text());truth=result["ground_truth"]
                assert (result["status"]=="SELECTED_CHECKS_PASSED") == truth["expected_check_pass"]
                observed = result["groups"]["contract"]["methods_failed"] + result["groups"]["contract"]["methods_errored"]
                for assertion in truth["targeted_assertions"]: assert assertion in observed,(key,assertion,observed)
                entry={"mission":mission,"candidate_id":key,"expected_decision":truth["expected_decision"],
                       "check_status":result["status"],"methods":result["tests_run"],"targeted_failures":observed}
                matrix.append(entry);note(key+"_discrimination",**entry)

        # A concrete carried learner chain, prepared by author-controlled source
        # copies; never presented as a participant's completed work.
        g1 = candidates/"g1_chain"
        execute("chain_g1_new",["new","G1","--dest",g1])
        (g1/"QUESTIONS.md").write_text("Author chain fixture: what is the outcome for a reservation identifier absent from existing storage, and for missing storage?\n")
        execute("chain_g1_clarify",["clarify","G1","--candidate",g1,"--question-file",g1/"QUESTIONS.md"])
        shutil.copy2(ROOT/"solutions/G1/booking_alternative.py",g1/"booking.py")
        check("chain_g1_handoff","G1",g1,operation="continue")
        b1 = candidates/"b1_chain"
        execute("chain_b1_new",["new","B1","--dest",b1])
        shutil.copy2(ROOT/"solutions/B1/routing.py",b1/"src/treasury/routing.py")
        # Deliberate rejection verifies B2 cannot silently treat v1 as v2.
        execute("b2_requires_explicit_v2",["advance","B2","--from-candidate",b1,"--dest",candidates/"invalid_b2"],expected=2)
        b1v2 = candidates/"b1_v2_chain"
        execute("chain_b1_extend",["extend","B1","--candidate",b1,"--dest",b1v2])
        shutil.copy2(ROOT/"solutions/B1/routing_v2.py",b1v2/"src/treasury/routing.py")
        check("chain_b1_v2_handoff","B1",b1v2,operation="continue")
        current = {"G":g1,"B":b1v2}
        for mission,spec in manifest.items():
            parent = current[mission[0]]
            parent_module = "src/treasury/routing.py" if spec["predecessor"]=="B1" else "booking.py" if spec["predecessor"]=="G1" else manifest[spec["predecessor"]]["module"]
            before = sha(parent/parent_module)
            path = candidates/(mission.lower()+"_chain")
            execute(mission+"_advance",["advance",mission,"--from-candidate",parent,"--dest",path])
            entry = json.loads((path/"READER_ENTRY.json").read_text())
            assert entry["lineage"]["source_sha256"] == before and sha(parent/parent_module) == before
            assert sha(path/entry["lineage"]["stored_snapshot"]) == before
            if mission=="G2": assert sha(path/"booking.py") == before
            elif mission=="G4": assert sha(path/"booking.py") == before
            elif mission=="B2": assert sha(path/"routing.py") == before
            elif mission=="B4": assert sha(path/"ledger.py") == before
            shutil.copy2(ROOT/spec["reference"],path/spec["module"])
            result = check(mission+"_chain_handoff",mission,path,operation="continue")
            assert result["status"] == "SCOPED_HANDOFF_READY"
            assert sha(parent/parent_module) == before
            note(mission+"_predecessor_retained",prior_sha256=before,prior_files=len(entry["prior_sha256"]),
                 handoff=result["status"],source_of_implementation="AUTHOR_CONTROLLED_REFERENCE_COPY")
            current[mission[0]] = path
            if mission=="G3":
                # An explicit deterministic composition control satisfies the
                # same prerequisite as the reader route. No model is invoked.
                current["G"]=integrate(path,destination/"g3_integration_control","G3_integration")

        # A G3 lineage that keeps its current reservations under another table
        # name, built from the reference G3 by a checked text transform. It
        # reproduces the 22 November 2026 live finding without a model run:
        # advance G4 must record the owner mapping G4-OD-01, and an observer
        # that ignores it must fail the protected check.
        renamed = candidates/"g3_renamed_chain"
        execute("renamed_G3_advance",["advance","G3","--from-candidate",candidates/"g2_chain","--dest",renamed])
        source=(ROOT/"solutions/G3/booking.py").read_text()
        head,tail=source.split("def _parse_utc_seconds",1)
        probe='columns = {x[1] for x in con.execute("PRAGMA table_info(reservations)")}\n        if "state" not in columns:'
        commit='        con.execute("PRAGMA user_version=3")\n        con.execute("COMMIT")'
        assert head.count(probe)==1 and head.count(commit)==1
        head=head.replace(probe,probe.replace('")}','")} if version != 3 else {"state"}',1))
        head=head.replace(commit,'        if version != 3:\n            con.execute("ALTER TABLE reservations RENAME TO reservation_records")\n'+commit)
        import re
        tail,count=re.subn(r"\breservations\b","reservation_records",tail)
        assert count==7,count
        (renamed/"booking.py").write_text(head+"def _parse_utc_seconds"+tail)
        result=check("renamed_G3_handoff","G3",renamed,operation="continue")
        assert result["status"]=="SCOPED_HANDOFF_READY"
        renamed_workspace=integrate(renamed,destination/"g3_renamed_integration","renamed_G3_integration")
        g4_mapped=candidates/"g4_renamed_chain"
        execute("renamed_G4_advance_derives_owner_mapping",["advance","G4","--from-candidate",renamed_workspace,"--dest",g4_mapped])
        mapping=json.loads((g4_mapped/"docs/G4-SCHEMA-MAP.json").read_text())
        entry=json.loads((g4_mapped/"READER_ENTRY.json").read_text())
        assert mapping["origin"]=="DERIVED_FROM_NAMED_COLUMNS" and mapping["table"]=="reservation_records"
        assert entry["owner_mapping"]=="G4-OD-01" and "docs/G4-OD-01.md" in entry["dependency_sha256"]
        ignoring=(ROOT/"solutions/G4/operations.py").read_text().replace('/ "G4-SCHEMA-MAP.json"','/ "IGNORED.json"')
        assert "IGNORED.json" in ignoring
        (g4_mapped/"operations.py").write_text(ignoring)
        ignored=check("renamed_G4_mapping_ignored","G4",g4_mapped,expected=1)
        missed=set(ignored["groups"]["contract"]["methods_failed"]+ignored["groups"]["contract"]["methods_errored"])
        assert {"test_clean_storage_is_observed_without_mutation","test_active_overlap_is_detected_not_repaired",
                "test_reference_and_native_current_layouts_are_refused"} <= missed, missed
        shutil.copy2(ROOT/"solutions/G4/operations.py",g4_mapped/"operations.py")
        mapped=check("renamed_G4_mapped_handoff","G4",g4_mapped,operation="continue")
        assert mapped["status"]=="SCOPED_HANDOFF_READY" and mapped["tests_run"]==manifest["G4"]["tests"]
        note("G4_owner_mapping_for_renamed_G3_lineage",origin="AUTHOR_CONTROLLED_TRANSFORM_OF_REFERENCE_G3",
             table=mapping["table"],mapping_origin=mapping["origin"],ignoring_observer_failed=sorted(missed),
             mapped_handoff=mapped["status"],observed_model_runs=0)
        maps=destination/"schema_maps";maps.mkdir()
        wrong=maps/"wrong_table.json";wrong.write_text(json.dumps({"table":"reservations","roles":mapping["roles"]}))
        execute("operator_map_for_missing_table_refused",["advance","G4","--from-candidate",renamed_workspace,
                "--dest",candidates/"g4_wrong_map","--schema-map",wrong],expected=2)
        partial=maps/"partial_roles.json";partial.write_text(json.dumps({"table":"reservation_records",
                "roles":{k:v for k,v in mapping["roles"].items() if k!="request_hash"}}))
        execute("operator_map_with_missing_role_refused",["advance","G4","--from-candidate",renamed_workspace,
                "--dest",candidates/"g4_partial_map","--schema-map",partial],expected=2)
        supplied=maps/"operator.json";supplied.write_text(json.dumps({"table":"reservation_records","roles":mapping["roles"]}))
        execute("operator_map_checked_and_recorded",["advance","G4","--from-candidate",renamed_workspace,
                "--dest",candidates/"g4_operator_map","--schema-map",supplied])
        assert json.loads((candidates/"g4_operator_map/docs/G4-SCHEMA-MAP.json").read_text())["origin"]=="OPERATOR_SUPPLIED_AND_CHECKED"
        execute("named_layout_needs_no_owner_map",["advance","G4","--from-candidate",destination/"g3_integration_control"/"workspace",
                "--dest",candidates/"g4_named_with_map","--schema-map",supplied],expected=2)
        assert not (candidates/"g4_chain"/"docs/G4-OD-01.md").exists()
        note("G4_operator_schema_map_checked",refused=["missing table","missing role","named layout"],
             recorded="OPERATOR_SUPPLIED_AND_CHECKED",named_lineage_owner_mapping=False)

        # One focused shared-runner guard confirms input protection and mode distinction.
        protected = candidates/"g4_standalone"/"tests/test_g4.py"
        original = protected.read_bytes()
        protected.write_bytes(original+b"\n# constructed integrity-negative fixture\n")
        bad = check("protected_input_change_refused","G4",candidates/"g4_standalone",expected=1)
        assert bad["status"] == "INPUT_INTEGRITY_FAILED" and bad["tests_run"] == 0
        protected.write_bytes(original)
        execute("reference_cannot_be_learner_handoff",["continue","G4","--candidate",candidates/"g4_reference","--output",receipts/"reference_block.json"],expected=2)
        note("shared_runner_preserves_input_and_reference_boundaries")
        status = "PASS"
    except Exception as exc:
        status, error = "FAIL", repr(exc)
    dependencies = set(["start.py","curriculum.py","curriculum_demo.py","verify_curriculum.py","curriculum/MANIFEST.json","workorders/progress.py",
                        "integration.py","solutions/G3/reservation_report.py","solutions/G3/reservation_cli.py","contracts/G4_OWNER_MAPPING.md",
                        "solutions/G3/INTEGRATION_REFERENCE_PROVENANCE.json"])
    dependencies.update(str(p.relative_to(ROOT)) for p in (ROOT/"integration_assets").rglob("*")
                        if p.is_file() and "__pycache__" not in p.parts)
    dependencies.add("curriculum/verify_release_compatibility.py")
    dependencies.update(str(p.relative_to(ROOT)) for p in (ROOT / "curriculum/issued_entries").glob("*.json"))
    dependencies.update(str(p.relative_to(ROOT)) for p in (ROOT / "workorders/orders").glob("*.json"))
    for spec in manifest.values():
        dependencies.update([spec["reference"],spec["starter"],*spec["protected"].values(),*spec["dependencies"].values()])
        for key in spec["candidate_ids"]:
            mission=key.split("-")[0]
            dependencies.update(f"candidates/{mission}/{key}/{f}" for f in ("variant.py","RATIONALE.md","TRUTH.json"))
    report = {"schema":"esa-curriculum-verification/v1","status":status,"error":error,
              "recorded_at_utc":datetime.now(timezone.utc).isoformat(),"elapsed_seconds":time.monotonic()-started,
              "origin":"AUTHOR_EXECUTION_OF_CONSTRUCTED_FIXTURES","observed_model_runs":0,"observed_human_pilots":0,
              "scenarios":scenarios,"scenario_count":len(scenarios),"commands":commands,"command_count":len(commands),
              "candidate_matrix":matrix,"dependency_sha256":{p:sha(ROOT/p) for p in sorted(dependencies)},
              "scope":"Local Python/SQLite teaching contract checks and continuation fixtures; not a production, financial or human-learning acceptance."}
    (destination/"RESULTS.json").write_text(json.dumps(report,indent=2)+"\n")
    (destination/"candidate_matrix.json").write_text(json.dumps(matrix,indent=2)+"\n")
    print(json.dumps({"status":status,"scenarios":len(scenarios),"commands":len(commands),"error":error,"report":str(destination/"RESULTS.json")},indent=2))
    return status == "PASS"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    return 0 if verify(args.output) else 1

if __name__ == "__main__":
    raise SystemExit(main())
