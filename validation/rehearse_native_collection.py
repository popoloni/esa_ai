#!/usr/bin/env python3
"""Run non-model collection and diagnosis checks with disposable synthetic files.

This is a recorder/CLI rehearsal. It never runs a named coding client, imports
the optional MCP SDK, reads credentials, opens a network connection or accepts
a learner candidate. Every command and failed result is retained.
"""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
import platform
import shutil
import sys
from record_observed_command import run
from observe_native import prepare, bind, inspect

HERE = Path(__file__).resolve().parent
COMPANION = HERE.parent


def rehearse(output):
    if output.exists() or output.is_symlink():
        raise ValueError("choose a new output directory")
    output = output.resolve()
    if output.is_relative_to(COMPANION):
        raise ValueError("keep the rehearsal outside the delivered companion")
    output.mkdir(parents=True)
    work = output / "work"
    for relative in ["practice/mcp_cli/policy_cli.py", "practice/mcp_cli/policy_lookup.py",
                     "reader_side/evolution/policy_catalog.json"]:
        target = work / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(COMPANION / relative, target)
    record_path = prepare(work, output / "packet", ["R06", "R07"])
    canary = output / "NONSECRET_CANARY.txt"
    canary.write_text("ESA disposable recorder canary; no user data.\n")
    cli = work / "practice/mcp_cli/policy_cli.py"
    cases = [
        ("01_client_absent", [str(work / "intentionally_absent_client")], 127,
         "CLIENT_EXECUTABLE_ABSENT"),
        ("02_server_path_missing", [sys.executable, "-B", str(work / "intentionally_absent_server.py")], 2,
         "SERVER_PROCESS_SETUP_FAILURE"),
        ("03_cli_argument_missing", [sys.executable, "-B", str(cli), "lookup"], 2,
         "CLI_USAGE_ARGUMENT_FAILURE_NOT_MCP_SCHEMA_RESULT"),
        ("04_domain_refusal", [sys.executable, "-B", str(cli), "lookup", "../../outside.json"], 2,
         "CLI_DOMAIN_REFUSAL"),
        ("05_valid_policy", [sys.executable, "-B", str(cli), "lookup", "BR-001/v1"], 0,
         "CLI_DOMAIN_SUCCESS"),
        ("06_sibling_canary", [sys.executable, "-B", "-c",
          "from pathlib import Path; import json,sys; p=Path(sys.argv[1]); print(json.dumps({'canary_readable':p.read_text().startswith('ESA disposable'), 'scope':'THIS_SIBLING_PYTHON_PROCESS_ONLY_NOT_NATIVE_HOST'}))",
          str(canary)], 0, "SIBLING_PROCESS_CANARY_OBSERVATION_NOT_NATIVE_BOUNDARY"),
        ("07_client_version", [sys.executable, "--version"], 0,
         "PYTHON_IDENTITY_FOR_REHEARSAL_ONLY"),
    ]
    results = []
    for name, argv, expected, classification in cases:
        spec = {"origin": "LOCAL_PROCESS_AND_CLI_REHEARSAL", "tool": "Python/local process",
                "tool_version": platform.python_version(), "model": None,
                "argv": argv, "cwd": str(work), "inventory_root": str(work),
                "allowed_changed_files": [], "timeout_seconds": 15}
        spec_path = output / (name + "_TASK.json")
        spec_path.write_text(json.dumps(spec, indent=2) + "\n")
        destination = output / "packet" / name
        recorder_status = run(spec_path, destination)
        receipt = json.loads((destination / "RECEIPT.json").read_text())
        check = receipt["exit_code"] == expected and not receipt["changed_files"]
        if name == "04_domain_refusal":
            data = json.loads((destination / "stdout.txt").read_text())
            check = check and data.get("ok") is False and data.get("error", {}).get("code") == "UNKNOWN_POLICY"
        if name == "05_valid_policy":
            data = json.loads((destination / "stdout.txt").read_text())
            check = check and data.get("ok") is True
        if name == "06_sibling_canary":
            check = check and json.loads((destination / "stdout.txt").read_text()).get("canary_readable") is True
        results.append({"case": name, "classification": classification,
                        "expected_exit": expected, "actual_exit": receipt["exit_code"],
                        "recorder_status": recorder_status, "passed": bool(check),
                        "receipt": (destination / "RECEIPT.json").relative_to(output).as_posix(),
                        "receipt_sha256": sha256((destination / "RECEIPT.json").read_bytes()).hexdigest()})
    record = json.loads(record_path.read_text())
    record.update(execution_kind="OFFLINE_COLLECTOR_REHEARSAL",
                  prior_solution_exposure="Author-controlled local process rehearsal; no generating model or learner.")
    record["client"] = {"name": "Python/local subprocess rehearsal", "version": platform.python_version(),
                        "model_identity": None, "model_identity_availability": "NOT_APPLICABLE_REHEARSAL"}
    record_path.write_text(json.dumps(record, indent=2) + "\n")
    bind(record_path, "client_identity", "07_client_version/stdout.txt")
    bind(record_path, "effective_configuration", "07_client_version/TASK.json")
    consistency = inspect(record_path)
    (output / "INCOMPLETE_PACKET_CHECK.json").write_text(json.dumps(consistency, indent=2) + "\n")
    expected_refusal = (consistency["status"] == "FAIL_EVIDENCE_CONSISTENCY"
                        and "MISSING_EVIDENCE:tool_actions" in consistency["issues"]
                        and "MISSING_EVIDENCE:mcp_valid_call" in consistency["issues"])
    result = {
        "schema": "native-collector-local-rehearsal/v1",
        "status": "PASS_LOCAL_REHEARSAL_ONLY" if all(item["passed"] for item in results) and expected_refusal else "FAIL",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution_kind": "LOCAL_PROCESS_AND_CLI_REHEARSAL",
        "cases": results,
        "incomplete_native_packet_correctly_refused": expected_refusal,
        "named_coding_client": "NOT_RUN", "model_calls": 0,
        "mcp_sdk_connection": "NOT_RUN", "human_acceptance": "PENDING",
        "boundary_scope": "Only the launched sibling Python process read the explicitly created non-secret canary. No named-host, server, environment or network boundary was tested.",
        "source_sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in
                          [HERE / "record_observed_command.py", HERE / "observe_native.py", Path(__file__).resolve()]},
    }
    (output / "REHEARSAL.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = rehearse(args.output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps({"status": result["status"], "output": str(args.output)}, indent=2))
    return 0 if result["status"] == "PASS_LOCAL_REHEARSAL_ONLY" else 1


if __name__ == "__main__":
    sys.exit(main())
