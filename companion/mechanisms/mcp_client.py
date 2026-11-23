#!/usr/bin/env python3
"""Execute a real, sequential MCP stdio exchange; retain both message streams."""
import hashlib
from datetime import datetime, timezone
import json
from pathlib import Path
import queue
import subprocess
import sys
import threading

from protocol import PREFIX, PROTOCOL, request_meta


def run_exchange(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-B", str(Path(__file__).with_name("mcp_server.py"))]
    transcript = []
    sent_lines = []
    received_lines = []
    lines = queue.Queue()
    with (output / "mcp.stderr.txt").open("w", encoding="utf-8") as diagnostics:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=diagnostics, text=True, encoding="utf-8", bufsize=1)

        def read_stdout():
            for line in process.stdout:
                lines.put(line)
            lines.put(None)

        reader = threading.Thread(target=read_stdout, daemon=True)
        reader.start()

        def send(message, expect_response=True):
            wire = json.dumps(message, ensure_ascii=False, separators=(",", ":"))
            transcript.append({"direction": "client_to_server", "message": message})
            sent_lines.append(wire + "\n")
            process.stdin.write(wire + "\n")
            process.stdin.flush()
            if not expect_response:
                return None
            try:
                line = lines.get(timeout=5)
            except queue.Empty as error:
                raise TimeoutError("MCP response not received within five seconds") from error
            if line is None:
                raise RuntimeError("MCP server closed stdout before replying")
            received_lines.append(line)
            response = json.loads(line)
            if response.get("jsonrpc") != "2.0" or response.get("id") != message["id"]:
                raise ValueError("MCP response envelope does not match request")
            transcript.append({"direction": "server_to_client", "message": response})
            return response

        try:
            def request(number, method, **parameters):
                return {"jsonrpc": "2.0", "id": number, "method": method,
                        "params": {"_meta": request_meta(), **parameters}}

            discovery = send(request(1, "server/discover"))
            if PROTOCOL not in discovery.get("result", {}).get("supportedVersions", []):
                raise ValueError("Server does not support the selected protocol")
            catalogue = send(request(2, "tools/list"))
            approved = send(request(3, "tools/call", name="read_policy",
                                    arguments={"source_id": "BR-001/v1"}))
            proposal = send(request(4, "tools/call", name="read_policy",
                                    arguments={"source_id": "legacy-note-001"}))
            unknown = send(request(5, "tools/call", name="read_policy",
                                   arguments={"source_id": "../../secret"}))
            unknown_tool = send(request(6, "tools/call", name="unlisted_tool", arguments={}))
            missing_meta = send({"jsonrpc": "2.0", "id": 7, "method": "tools/list", "params": {}})
            unsupported_request = request(8, "tools/list")
            unsupported_request["params"]["_meta"][PREFIX + "protocolVersion"] = "1900-01-01"
            unsupported_version = send(unsupported_request)
            after_errors = send(request(9, "tools/call", name="read_policy",
                                        arguments={"source_id": "BR-001/v1"}))
            process.stdin.close()
            exit_code = process.wait(timeout=5)
            reader.join(timeout=1)
            if exit_code != 0:
                raise RuntimeError("MCP server exited unsuccessfully")
            unexpected = []
            while not lines.empty():
                extra = lines.get_nowait()
                if extra is not None:
                    unexpected.append(extra)
            if unexpected:
                raise ValueError("Unsolicited stdout after the final response")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            (output / "mcp.transcript.json").write_text(json.dumps(transcript, indent=2) + "\n", "utf-8")
            (output / "mcp.stdin.jsonl").write_text("".join(sent_lines), "utf-8")
            (output / "mcp.stdout.jsonl").write_text("".join(received_lines), "utf-8")
    context = Path(__file__).resolve().parents[1] / "context"
    source_bytes_match = all(
        response["result"]["content"][0]["text"].encode("utf-8") == (context / filename).read_bytes()
        and response["result"]["structuredContent"]["sha256"] == hashlib.sha256((context / filename).read_bytes()).hexdigest()
        for response, filename in ((approved, "BR-001.md"), (proposal, "legacy_note.json")))
    responses = [x["message"] for x in transcript if x["direction"] == "server_to_client"]
    checks = {
        "pinned_protocol_discovered": discovery["result"]["supportedVersions"] == [PROTOCOL],
        "one_named_tool_listed": [tool["name"] for tool in catalogue["result"]["tools"]] == ["read_policy"],
        "canonical_source_id_schema": catalogue["result"]["tools"][0]["inputSchema"]["required"] == ["source_id"],
        "approved_source_label": approved["result"]["structuredContent"]["status"] == "approved",
        "proposal_label": proposal["result"]["structuredContent"]["status"] == "proposal",
        "source_id_roundtrip": approved["result"]["structuredContent"]["source_id"] == "BR-001/v1"
            and proposal["result"]["structuredContent"]["source_id"] == "legacy-note-001",
        "unknown_source_is_tool_error": unknown.get("result", {}).get("isError") is True
            and "error" not in unknown,
        "unknown_tool_is_protocol_error": unknown_tool.get("error", {}).get("code") == -32602,
        "required_metadata_enforced": missing_meta.get("error", {}).get("code") == -32602,
        "unsupported_protocol_error": unsupported_version.get("error", {}).get("code") == -32022
            and unsupported_version["error"]["data"]["supported"] == [PROTOCOL],
        "errors_do_not_change_request_state": after_errors.get("result") == approved["result"],
        "all_success_results_complete": all(x["result"].get("resultType") == "complete"
            for x in responses if "result" in x),
        "cache_metadata_present": all(x["result"].get("ttlMs") == 300000
            and x["result"].get("cacheScope") == "public" for x in (discovery, catalogue)),
        "returned_source_bytes_and_digests_match": source_bytes_match,
        "no_initialization_handshake": not any(x["message"].get("method") in
            ("initialize", "notifications/initialized") for x in transcript),
        "clean_exit": exit_code == 0,
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL", "command": command,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "protocol": PROTOCOL, "server_exit_code": exit_code, "checks": checks,
            "request_messages": len(sent_lines), "response_messages": len(received_lines),
            "model_invocation": False, "transport": "stdio",
            "scope": "Executed bounded profile, not a certification of every MCP feature."}



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output directory already exists; choose a fresh path")
    result = run_exchange(args.output)
    (args.output / "mcp.receipt.json").write_text(json.dumps(result, indent=2) + "\n", "utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
