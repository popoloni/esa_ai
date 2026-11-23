#!/usr/bin/env python3
"""Behavioral checks of the published MCP subset; no third-party packages."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
VERSION = "2026-07-28"
P = "io.modelcontextprotocol/"


def request(number, method="tools/call", **params):
    return {"jsonrpc": "2.0", "id": number, "method": method,
            "params": {"_meta": {P + "protocolVersion": VERSION,
                         P + "clientCapabilities": {}}, **params}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists; choose a fresh path")
    args.output.mkdir(parents=True)
    good = request(1, name="read_policy", arguments={"source_id": "BR-001/v1"})
    inputs = [
        good,
        request(2, "server/discover"),
        request(3, "tools/list"),
        request(4, name="read_policy", arguments={"source_id": "legacy-note-001"}),
        request(5, name="read_policy", arguments={"source_id": "../../secret"}),
        request(6, name="unlisted", arguments={}),
        request(7, name="read_policy", arguments={"source_id": "BR-001/v1", "path": "/tmp/secret"}),
        request(8, name="read_policy", arguments={"source_id": 7}),
        {"jsonrpc": "2.0", "id": 9, "method": "tools/list", "params": {}},
        request(10, "removed_method"),
        request(11, name="read_policy", arguments=["BR-001/v1"]),
        request(12, "tools/list", cursor="not-issued"),
    ]
    version_error = request(13, "tools/list")
    version_error["params"]["_meta"][P + "protocolVersion"] = "2025-11-25"
    inputs.append(version_error)
    missing_capabilities = request(14, "tools/list")
    del missing_capabilities["params"]["_meta"][P + "clientCapabilities"]
    inputs.append(missing_capabilities)
    inputs.append(request(15, name="read_policy", arguments={"source_id": "BR-001/v1"}))
    wire = "\n".join(json.dumps(x, separators=(",", ":")) for x in inputs) + "\n"
    command = [sys.executable, "-B", str(HERE / "mcp_server.py")]
    run = subprocess.run(command, input=wire, text=True, capture_output=True, timeout=10)
    (args.output / "stdin.jsonl").write_text(wire)
    (args.output / "stdout.jsonl").write_text(run.stdout)
    (args.output / "stderr.txt").write_text(run.stderr)
    messages = [json.loads(x) for x in run.stdout.splitlines()]
    by_id = {m["id"]: m for m in messages}
    checks = []
    def check(name, passed):
        checks.append({"name": name, "status": "PASS" if passed else "FAIL"})
    check("one response per request; matching IDs; JSON-only stdout",
          len(messages) == len(inputs) and set(by_id) == set(range(1, 16))
          and all(m.get("jsonrpc") == "2.0" for m in messages))
    check("tools/call works as first request without discovery or initialization",
          by_id[1].get("result", {}).get("structuredContent", {}).get("source_id") == "BR-001/v1")
    check("discovery publishes the selected version and tools capability",
          by_id[2]["result"]["supportedVersions"] == [VERSION] and "tools" in by_id[2]["result"]["capabilities"])
    check("cache metadata present on both cacheable responses",
          all(by_id[i]["result"].get("ttlMs") == 300000 and
              by_id[i]["result"].get("cacheScope") == "public" for i in (2, 3)))
    tool = by_id[3]["result"]["tools"][0]
    check("schema and calls use canonical source_id",
          tool["inputSchema"]["required"] == ["source_id"] and
          tool["inputSchema"]["properties"]["source_id"]["enum"] == ["BR-001/v1", "legacy-note-001"])
    check("unapproved newer note retains proposal and unknown owner",
          by_id[4]["result"]["structuredContent"]["source_id"] == "legacy-note-001" and
          by_id[4]["result"]["structuredContent"]["status"] == "proposal" and
          by_id[4]["result"]["structuredContent"]["owner"] == "unknown")
    check("unknown source path is a tool error with no file content",
          by_id[5].get("result", {}).get("isError") is True and
          "structuredContent" not in by_id[5]["result"] and "error" not in by_id[5])
    check("unknown tool is a protocol error", by_id[6].get("error", {}).get("code") == -32602)
    check("extra tool arguments and wrong source_id type rejected at tool boundary",
          all(by_id[i].get("result", {}).get("isError") is True for i in (7, 8)))
    check("required per-request metadata enforced",
          all(by_id[i].get("error", {}).get("code") == -32602 for i in (9, 14)))
    check("unknown method reported", by_id[10].get("error", {}).get("code") == -32601)
    check("malformed arguments object and unknown cursor are protocol errors",
          all(by_id[i].get("error", {}).get("code") == -32602 for i in (11, 12)))
    check("unsupported version returns modern error and supported alternatives",
          by_id[13].get("error", {}).get("code") == -32022 and
          by_id[13]["error"]["data"] == {"supported": [VERSION], "requested": "2025-11-25"})
    check("later request unaffected by preceding failures", by_id[15]["result"] == by_id[1]["result"])
    check("all results contain resultType complete",
          all(m["result"].get("resultType") == "complete" for m in messages if "result" in m))
    context = HERE.parent / "context"
    check("approved source returned byte for byte with matching digest",
          by_id[1]["result"]["content"][0]["text"].encode() == (context / "BR-001.md").read_bytes() and
          by_id[1]["result"]["structuredContent"]["sha256"] == hashlib.sha256((context / "BR-001.md").read_bytes()).hexdigest())
    check("server exits cleanly on input EOF; diagnostics remain on stderr", run.returncode == 0 and bool(run.stderr.strip()))
    # Malformed JSON is a separate process, not confused with an application error.
    malformed = subprocess.run(command, input="{not-json}\n", text=True, capture_output=True, timeout=5)
    parsed = json.loads(malformed.stdout)
    check("malformed JSON produces parse error without invented correlation id",
          parsed.get("error", {}).get("code") == -32700 and "id" not in parsed)
    (args.output / "malformed.stdout.json").write_text(malformed.stdout)
    result = {"schema": "esa-mcp-profile-checks/v1", "protocol": VERSION,
              "recorded_at": datetime.now(timezone.utc).isoformat(),
              "status": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL",
              "command": command, "request_count": len(inputs), "checks": checks,
              "model_invocation": False,
              "scope": "Behavioral checks of the published synchronous stdio subset; not full protocol certification.",
              "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob("*.py")}}
    (args.output / "RESULTS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": len(checks), "output": str(args.output)}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
