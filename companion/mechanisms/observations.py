#!/usr/bin/env python3
"""Observe instruction bytes, an OS write denial and a real stdio exchange."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import textwrap

from protocol import PROTOCOL

from mcp_client import run_exchange

ROOT = Path(__file__).resolve().parents[2]
CONTEXT = ROOT / "companion" / "context"
HISTORY = ROOT / "evidence" / "historical_episode" / "native_20261022"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", "utf-8")


def historical_load(output):
    source = HISTORY / "attempt_01" / "native-session.json"
    instructions = HISTORY / "starting_files" / "repo" / "AGENTS.md"
    session = json.loads(source.read_text("utf-8"))
    body = instructions.read_text("utf-8").strip()
    matches = []
    for mi, message in enumerate(session["messages"]):
        for pi, part in enumerate(message.get("parts", [])):
            state = part.get("state", {})
            if part.get("type") == "tool" and body in state.get("output", ""):
                matches.append((mi, pi, part))
    if len(matches) != 1:
        raise ValueError("Expected one historical tool result containing the full AGENTS file")
    mi, pi, part = matches[0]
    state = part["state"]
    write_json(output / "agents.historical_event.json", part)
    (output / "agents.historical_output.txt").write_text(state["output"], "utf-8")
    return {
        "status": "PASS",
        "evidence_kind": "Recorded model run",
        "observed_at": datetime.fromtimestamp(state["time"]["end"] / 1000, timezone.utc).isoformat(),
        "source": str(source.relative_to(ROOT)),
        "source_sha256": digest(source),
        "json_pointer": f"/messages/{mi}/parts/{pi}",
        "session_id": session["info"]["id"],
        "client": "OpenCode " + session["info"]["version"],
        "model_id": session["info"]["model"]["id"],
        "tool": part["tool"],
        "tool_status": state["status"],
        "instructions_source": str(instructions.relative_to(ROOT)),
        "instructions_sha256": digest(instructions),
        "exact_instruction_body_in_tool_output": True,
        "mechanism": "Client attached AGENTS.md to the routing.py read result as a system-reminder",
        "explicit_model_read_of_AGENTS_observed": False,
        "instruction_compliance_observed": False,
        "startup_injection_observed": False,
        "scope": "The saved client tool result contains the file body; this is a recheck of a historical capture, not a new model run.",
    }


def observe_access_denial(output):
    status_file = Path("/proc/self/status")
    cap_eff = 0
    if status_file.exists():
        cap_eff = next(int(line.split(":", 1)[1].strip(), 16)
                       for line in status_file.read_text().splitlines()
                       if line.startswith("CapEff:"))
    required_caps = (1 << 0) | (1 << 6) | (1 << 7) | (1 << 8)
    preflight = {"platform": sys.platform, "parent_euid": os.geteuid() if os.name == "posix" else None,
                 "parent_cap_eff": hex(cap_eff), "required_cap_eff_mask": hex(required_caps),
                 "worker_uid": 65534, "worker_gid": 65534}
    if (not sys.platform.startswith("linux") or os.geteuid() != 0
            or cap_eff & required_caps != required_caps):
        result = {"status": "UNSUPPORTED", "preflight": preflight,
                  "reason": "Linux trusted setup needs CHOWN, SETUID, SETGID and SETPCAP to establish a distinct worker. No same-owner fallback was attempted."}
        write_json(output / "access.command.json", result)
        return result
    sandbox = Path(tempfile.mkdtemp(prefix="esa-permission-observation-"))
    try:
        sandbox.chmod(0o755)
        tests = sandbox / "tests"
        scratch = sandbox / "scratch"
        tests.mkdir()
        scratch.mkdir()
        os.chown(scratch, 65534, 65534)
        scratch.chmod(0o700)
        protected = tests / "test_policy.py"
        protected.write_text("THRESHOLD = 5000\n", "utf-8")
        protected.chmod(0o444)
        tests.chmod(0o555)
        worker_source = Path(__file__).with_name("access_worker.py")
        worker = sandbox / "access_worker.py"
        shutil.copyfile(worker_source, worker)
        worker.chmod(0o444)
        command = [sys.executable, "-I", "-B", str(Path(__file__).with_name("access_launcher.py")),
                   str(worker), str(sandbox), "65534", "65534"]
        before = digest(protected)
        completed = subprocess.run(command, capture_output=True, text=True,
                                   encoding="utf-8", timeout=10)
        (output / "access.stdout.txt").write_text(completed.stdout, "utf-8")
        (output / "access.stderr.txt").write_text(completed.stderr, "utf-8")
        write_json(output / "access.command.json", {
            "argv": command, "preflight": preflight, "setup_identity": "trusted fixture owner",
            "worker_source": str(worker_source.relative_to(ROOT)), "worker_sha256": digest(worker_source),
            "protected_file_mode": "0444", "protected_directory_mode": "0555",
            "protected_parent_mode": "0755", "worker_scratch_mode": "0700",
            "timeout_seconds": 10, "returncode": completed.returncode,
            "sandbox_cleanup": "Temporary fixture removed after observations; logs retained."})
        if completed.returncode != 0:
            return {"status": "FAIL", "reason": "Distinct-identity probe did not complete",
                    "returncode": completed.returncode, "preflight": preflight}
        result = json.loads(completed.stdout)
        write_json(output / "access.operations.json", result)
        capability_keys = ("CapEff", "CapPrm", "CapInh", "CapAmb", "CapBnd")
        credentials_safe = (result["uid"] == result["euid"] == 65534
            and result["gid"] == result["egid"] == 65534 and result["groups"] == []
            and all(int(result["capabilities"].get(k, "1"), 16) == 0 for k in capability_keys)
            and result["capabilities"].get("NoNewPrivs") == "1")
        protected_owners = all(row["uid"] != result["euid"] for row in result["metadata_before"])
        checks = {"distinct_owner_and_worker": protected_owners,
                  "worker_cannot_regain_privileges": credentials_safe,
                  "positive_control_same_process": result["positive_control_writable"],
                  "protected_file_reached": result["protected_read_succeeded"],
                  "six_relevant_mutations_denied": len(result["events"]) == 6 and
                      all(e["denied"] and e["target_reached"] for e in result["events"]),
                  "protected_bytes_unchanged": result["unchanged"] and before == digest(protected),
                  "ownership_and_modes_unchanged": result["metadata_before"] == result["metadata_after"]}
        return {"status": "PASS" if all(checks.values()) else "FAIL", "evidence_kind": "Executed control",
                "mechanism": "Linux POSIX discretionary access control with separate identities",
                "checks": checks, "observations": result,
                "scope": "Disposable fixture only. The worker has no capabilities, no supplementary groups and no_new_privs. It can read but cannot write, replace, chmod or rename the protected objects. This is not a general network or process sandbox."}
    finally:
        if (sandbox / "tests").exists():
            (sandbox / "tests").chmod(0o755)
        shutil.rmtree(sandbox)


def export_excerpts(output, observations):
    excerpts = output / "excerpts"
    excerpts.mkdir()
    historical = observations["historical_instructions"]
    event = json.loads((output / "agents.historical_event.json").read_text("utf-8"))
    text = event["state"]["output"]
    marker = text.index("Instructions from:")
    segment = text[marker:].splitlines()[:10]
    (excerpts / "agents_load.txt").write_text("\n".join(segment) + "\n", "utf-8")
    # A display projection is labelled as such; the raw event is retained separately.
    write_json(excerpts / "agents_load_projection.json", {
        "kind": "Projection of recorded model run",
        "observed_at": historical["observed_at"], "client": historical["client"],
        "model_id": historical["model_id"], "tool": historical["tool"],
        "tool_status": historical["tool_status"],
        "loaded_file": "repo/AGENTS.md", "whole_file_present": True,
        "source_pointer": historical["json_pointer"]})
    access = observations["access_denial"]
    write_json(excerpts / "access_denial.json", {
        "kind": "Projection of executed control",
        "mechanism": access.get("mechanism"),
        "effective_uid": access.get("observations", {}).get("euid"),
        "effective_capabilities": access.get("observations", {}).get("capabilities", {}).get("CapEff"),
        "positive_control_writable": access.get("observations", {}).get("positive_control_writable"),
        "events": access.get("observations", {}).get("events", []),
        "protected_file_unchanged": access.get("observations", {}).get("unchanged"),
    })
    exchange = json.loads((output / "mcp" / "mcp.transcript.json").read_text("utf-8"))
    for number, stem in ((1, "mcp_discover"), (2, "mcp_list"), (3, "mcp_call_approved"), (4, "mcp_call_proposal"), (5, "mcp_call_unknown_source"), (6, "mcp_call_unknown_tool")):
        pair = [item["message"] for item in exchange if item["message"].get("id") == number]
        write_json(excerpts / (stem + ".json"), {"request": pair[0], "response": pair[1]})
        write_json(excerpts / (stem + "_request.json"), pair[0])
        write_json(excerpts / (stem + "_response.json"), pair[1])
    approved = next(item["message"]["result"] for item in exchange
                    if item["direction"] == "server_to_client" and item["message"].get("id") == 3)
    proposal = next(item["message"]["result"] for item in exchange
                    if item["direction"] == "server_to_client" and item["message"].get("id") == 4)
    write_json(excerpts / "mcp_call_projection.json", {
        "kind": "Projection of executed MCP exchange",
        "request": {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                    "params": {"name": "read_policy", "arguments": {"source_id": "legacy-note-001"}}},
        "response_metadata": proposal["structuredContent"], "isError": proposal["isError"],
    })
    write_json(excerpts / "sources_returned.json", {
        "approved": approved["structuredContent"], "proposal": proposal["structuredContent"]})
    # Short print projections preserve the selected observed values. They are
    # not wire messages; complete messages and all hashes remain above.
    write_json(excerpts / "agents_load_projection_short.json", {
        "kind": "Recorded model run / selected fields",
        "observed_at": historical["observed_at"],
        "client": historical["client"], "model_id": historical["model_id"],
        "tool": historical["tool"], "status": historical["tool_status"],
        "loaded_file": "repo/AGENTS.md", "whole_file_present": True,
        "source_pointer": historical["json_pointer"]})
    probe = access.get("observations", {})
    compact_access = {
        "kind": "Executed control / selected fields",
        "protected_owner_uid": probe.get("metadata_before", [{}])[0].get("uid"),
        "effective_uid": probe.get("euid"),
        "effective_gid": probe.get("egid"),
        "supplementary_groups": probe.get("groups"),
        "no_new_privs": probe.get("capabilities", {}).get("NoNewPrivs"),
        "effective_capabilities": probe.get("capabilities", {}).get("CapEff"),
        "positive_control_writable": probe.get("positive_control_writable"),
    }
    for item in probe.get("events", []):
        compact_access[item["operation"]] = item.get("exception", "NONE") + " / errno " + str(item.get("errno"))
    compact_access["protected_file_unchanged"] = probe.get("unchanged")
    write_json(excerpts / "access_denial_compact.json", compact_access)
    catalogue = next(item["message"]["result"] for item in exchange
                     if item["direction"] == "server_to_client" and item["message"].get("id") == 2)
    tool = catalogue["tools"][0]
    schema = tool["inputSchema"]
    write_json(excerpts / "mcp_tools_projection.json", {
        "kind": "Executed tools/list / selected fields",
        "name": tool["name"], "input_type": schema["type"],
        "required": schema["required"], "source_id_values": schema["properties"]["source_id"]["enum"],
        "additionalProperties": schema["additionalProperties"],
        "readOnlyHint": tool["annotations"]["readOnlyHint"],
    })
    write_json(excerpts / "mcp_call_projection_compact.json", {
        "kind": "Executed exchange / selected fields",
        "request": {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                    "name": "read_policy", "source_id_argument": "legacy-note-001"},
        "response": {key: proposal["structuredContent"][key] for key in ("source_id", "status", "owner", "date")},
        "isError": proposal["isError"],
    })
    clauses = (CONTEXT / "BR-001.md").read_text("utf-8").splitlines()[2:9]
    lines = ["Selected clauses: companion/context/BR-001.md", ""]
    for clause in clauses:
        lines.extend(textwrap.wrap(clause, width=66, break_long_words=False, break_on_hyphens=False) or [""])
    (excerpts / "policy_excerpt.txt").write_text("\n".join(lines) + "\n", "utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output directory already exists; use a fresh path")
    output = args.output.resolve()
    output.mkdir(parents=True)
    sources = [*sorted(CONTEXT.iterdir()), *sorted(Path(__file__).parent.glob("*.py"))]
    before = {str(path.relative_to(ROOT)): digest(path) for path in sources if path.is_file()}
    observations = {
        "historical_instructions": historical_load(output),
                "access_denial": observe_access_denial(output),
        "mcp_exchange": run_exchange(output / "mcp"),
    }
    after = {str(path.relative_to(ROOT)): digest(path) for path in sources if path.is_file()}
    checks = {name: value["status"] == "PASS" for name, value in observations.items()}
    checks["source_files_unchanged"] = before == after
    receipt = {
        "schema": "esa-mechanism-observations/v2", "release": "ESA-full-review-v1",
        "protocol": PROTOCOL,
        "recorded_at": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
        "platform": platform.platform(), "status": ("PASS" if all(checks.values()) else
                   "UNSUPPORTED" if observations["access_denial"]["status"] == "UNSUPPORTED" else "FAIL"),
        "checks": checks, "observations": observations,
        "source_sha256_before": before, "source_sha256_after": after,
        "live_model_run": False,
    }
    write_json(output / "RECEIPT.json", receipt)
    export_excerpts(output, observations)
    print(json.dumps({"status": receipt["status"], "checks": checks, "output": str(output)}, indent=2))
    return 0 if receipt["status"] == "PASS" else 2 if receipt["status"] == "UNSUPPORTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
