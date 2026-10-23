#!/usr/bin/env python3
"""Observe an official MCP SDK stdio round trip and the same fixed-task CLI.

Writes a NEW evidence directory. Timings are local process measurements;
serialized byte counts are not tokens, billable units or a client benchmark.
"""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import asyncio
import importlib.metadata
import json
import platform
import subprocess
import sys
import time
import traceback
from policy_lookup import CATALOG

HERE = Path(__file__).resolve().parent


def dump(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def serialized(value):
    return value.model_dump(mode="json", by_alias=True, exclude_none=True)


async def observe(output):
    from mcp import Client, StdioServerParameters, stdio_client
    params = StdioServerParameters(command=sys.executable,
        args=["-B", str(HERE / "wire_proxy.py"), str(output)], cwd=str(HERE),
        env={"PYTHONDONTWRITEBYTECODE": "1"})
    record = {"server_argv": [params.command, *params.args], "server_cwd": str(HERE),
              "explicit_environment": params.env, "cases": []}
    with (output / "server.stderr.txt").open("x", encoding="utf-8") as log:
        async with Client(stdio_client(params, errlog=log), read_timeout_seconds=15) as client:
            record["protocol_version"] = client.protocol_version
            record["server_info"] = serialized(client.server_info) if client.server_info else None
            tools = serialized(await client.list_tools())
            (output / "tools.json").write_text(json.dumps(tools, indent=2) + "\n")
            record["listed_tools"] = [t["name"] for t in tools["tools"]]
            record["tools_result_json_utf8_bytes"] = len(dump(tools).encode())
            for number, policy in enumerate(["BR-001/v1", "BR-001/v2", "../../outside.json"], 1):
                request = {"name": "lookup_policy", "arguments": {"policy_id": policy}}
                start = time.perf_counter()
                response = serialized(await client.call_tool(request["name"], request["arguments"]))
                duration = time.perf_counter() - start
                argv = [sys.executable, "-B", str(HERE / "policy_cli.py"), "lookup", policy]
                cli_start = time.perf_counter()
                cli = subprocess.run(argv, cwd=HERE, capture_output=True, text=True, timeout=15, check=False)
                cli_duration = time.perf_counter() - cli_start
                (output / f"case_{number}_cli.stdout.json").write_text(cli.stdout)
                (output / f"case_{number}_cli.stderr.txt").write_text(cli.stderr)
                cli_data = json.loads(cli.stdout)
                structured = response.get("structuredContent")
                # SDK v2 exposes dictionary results directly. Fail visibly if that contract changes.
                matched = structured == cli_data
                row = {"case": number, "request": request, "mcp_response": response,
                       "cli_argv": argv, "cli_exit_code": cli.returncode, "cli_result": cli_data,
                       "same_domain_result": matched, "expected_domain_ok": number < 3,
                       "mcp_duration_seconds": duration, "cli_duration_seconds": cli_duration,
                       "mcp_result_json_utf8_bytes": len(dump(response).encode()),
                       "cli_stdout_utf8_bytes": len(cli.stdout.encode()),
                       "interpretation": "Domain rejection is returned as ok=false, not a protocol error." if number == 3 else "Known synthetic policy returned."}
                record["cases"].append(row)
            invalid = serialized(await client.call_tool("lookup_policy", {"policy_id": ["BR-001/v1"]}))
            record["invalid_schema_response"] = invalid
            record["invalid_schema_rejected"] = bool(invalid.get("isError"))
    record["all_expected"] = (record["listed_tools"] == ["lookup_policy"]
        and all(c["same_domain_result"] and c["cli_result"]["ok"] == c["expected_domain_ok"]
                and c["cli_exit_code"] == (0 if c["expected_domain_ok"] else 2) for c in record["cases"])
        and record["invalid_schema_rejected"])
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error("use a new output directory")
    output = args.output.resolve()
    if output.is_relative_to(HERE):
        parser.error("create the run outside practice/mcp_cli; retain selected receipts after review")
    output.mkdir(parents=True, exist_ok=False)
    catalog_before = sha256(CATALOG.read_bytes()).hexdigest()
    record = {"schema": "mcp-cli-observation/v1", "origin": "sdk_integration",
              "started_at_utc": datetime.now(timezone.utc).isoformat(),
              "python": platform.python_version(), "platform": platform.platform(),
              "mcp_version": importlib.metadata.version("mcp"),
              "model": None, "host_client": "official Python SDK Client over stdio",
              "human_review": "PENDING", "named_coding_client_trial": "NOT_RUN",
              "catalog_sha256_before": catalog_before,
              "source_sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))},
              "boundary": {"input": "two literal policy identifiers; no caller file path",
                           "api_writes": "none", "catalog_write_check": "before/after SHA-256",
                           "credentials": "no credentials supplied; SDK default environment allow-list plus explicit bytecode flag",
                           "transport": "local stdio subprocess; no HTTP listener configured",
                           "os_isolation": "NOT_ESTABLISHED_BY_THIS_EXAMPLE",
                           "network_egress_audit": "NOT_PERFORMED; stdio is not a network-denial policy"}}
    start = time.perf_counter()
    try:
        if record["mcp_version"] != "2.3.0":
            raise ValueError("This frozen exercise requires mcp==2.3.0; review upgrades separately")
        record.update(asyncio.run(observe(output)))
    except Exception as exc:
        record.update(all_expected=False, error=type(exc).__name__ + ": " + str(exc))
        (output / "failure.txt").write_text(traceback.format_exc())
    record["catalog_sha256_after"] = sha256(CATALOG.read_bytes()).hexdigest()
    record["catalog_unchanged"] = record["catalog_sha256_after"] == catalog_before
    record["duration_seconds"] = time.perf_counter() - start
    record["ended_at_utc"] = datetime.now(timezone.utc).isoformat()
    record["status"] = "PASS_LOCAL_SDK_CLI_COMPARISON" if record.get("all_expected") and record["catalog_unchanged"] else "FAIL"
    record["evidence_files"] = {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p.read_bytes()).hexdigest()}
                                for p in sorted(output.iterdir()) if p.is_file()}
    (output / "COMPARISON.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"status": record["status"], "output": str(output), "error": record.get("error")}, indent=2))
    return 0 if record["status"].startswith("PASS") else 1


if __name__ == "__main__":
    sys.exit(main())
