#!/usr/bin/env python3
"""Record a real legacy SDK list-argument rejection, separately from any host/model."""
import argparse
import asyncio
from datetime import datetime, timezone
from hashlib import sha256
import importlib.metadata
import json
from pathlib import Path
import sys
import traceback

from mcp import Client, StdioServerParameters, stdio_client


def now():
    return datetime.now(timezone.utc).isoformat()


def encoded(value):
    return value.model_dump(mode="json", by_alias=True, exclude_none=True)


async def observe(server, output, record):
    (output / "trace").mkdir(exist_ok=False)
    params = StdioServerParameters(command=sys.executable,
        args=["-B", str(server / "wire_proxy.py"), str(output / "trace")],
        cwd=str(server), env={"PYTHONDONTWRITEBYTECODE": "1"})
    record["server_argv"] = [params.command, *params.args]
    record["server_cwd"] = str(server)
    with (output / "server.stderr.txt").open("x") as err:
        async with Client(stdio_client(params, errlog=err), mode="legacy",
                          read_timeout_seconds=20) as client:
            record["protocol_version"] = client.protocol_version
            record["server_info"] = encoded(client.server_info)
            record["tools"] = encoded(await client.list_tools())
            record["request"] = {"name": "lookup_policy", "arguments": {"policy_id": []}}
            record["response"] = encoded(await client.call_tool("lookup_policy", {"policy_id": []}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    server = args.server_dir.resolve(strict=True)
    output = args.output.absolute()
    output.mkdir(parents=True, exist_ok=False)
    source_paths = [server / name for name in ("policy_server.py", "policy_lookup.py", "wire_proxy.py")]
    def sources():
        return {str(p): sha256(p.read_bytes()).hexdigest() for p in source_paths}
    record = {"schema": "esa-legacy-sdk-argument-control/v1", "started_at_utc": now(),
        "argv": sys.argv, "cwd": str(Path.cwd()), "python_executable": sys.executable,
        "executed_script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "mcp_distribution_version": importlib.metadata.version("mcp"),
        "client": "Official Python SDK Client(mode=legacy)",
        "model_selected": False, "coding_host_trial": False, "human_review": "NOT_PERFORMED",
        "source_sha256_before": sources(),
        "purpose": "Actual server-side type rejection control; does not replace or repair the native host first output.",
        "scope": "One empty-array argument over legacy stdio. No OS/network isolation conclusion."}
    try:
        if record["mcp_distribution_version"] != "2.3.0":
            raise ValueError("This observation requires the retained mcp==2.3.0 pin")
        asyncio.run(asyncio.wait_for(observe(server, output, record), timeout=60))
        record["status"] = "OBSERVED_SERVER_ARGUMENT_REJECTION" if record["response"].get("isError") else "EXPECTED_REJECTION_NOT_OBSERVED"
    except Exception as exc:
        record["status"] = "CONTROL_FAILED"
        record["error"] = str(exc)
        (output / "failure.txt").write_text(traceback.format_exc())
    record["source_sha256_after"] = sources()
    record["sources_unchanged"] = record["source_sha256_before"] == record["source_sha256_after"]
    record["finished_at_utc"] = now()
    record["evidence_sha256"] = {p.relative_to(output).as_posix(): sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.rglob("*")) if p.is_file()}
    (output / "CONTROL.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"status": record["status"], "protocol_version": record.get("protocol_version"),
                      "sources_unchanged": record["sources_unchanged"]}, indent=2))
    return 0 if record["status"] == "OBSERVED_SERVER_ARGUMENT_REJECTION" and record["sources_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
