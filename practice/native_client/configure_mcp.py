#!/usr/bin/env python3
"""Prepare a new OpenCode observation of the unchanged Treasury MCP server.

Creates a fresh study directory, a starting snapshot, literal configuration and
one declared non-secret canary. No model, server or canary read is executed.
The opt-in probe runs later in the actual serving Python process at startup.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True, help="new disposable study directory")
    parser.add_argument("--runtime-root", type=Path, required=True,
                        help="contains opencode/ and the pinned mcp_venv/")
    parser.add_argument("--output", type=Path, required=True,
                        help="new evidence directory outside the study and companion trees")
    args = parser.parse_args()
    companion = Path(__file__).resolve().parents[2]
    work, output = args.work.resolve(), args.output.resolve()
    runtime = args.runtime_root.resolve(strict=True)
    if (args.work.is_symlink() or args.output.is_symlink() or work.exists() or output.exists()
            or output.is_relative_to(work) or work.is_relative_to(output)
            or output.is_relative_to(companion) or work.is_relative_to(companion)):
        parser.error("choose two unused ordinary directories outside each other and the companion")
    client = runtime / "opencode/node_modules/.bin/opencode"
    interpreter = runtime / "mcp_venv/bin/python"
    server = companion / "practice/mcp_cli/policy_server.py"
    relay = server.with_name("wire_proxy.py")
    probe = Path(__file__).resolve().parent / "probe/sitecustomize.py"
    recorder = companion / "validation/observe_native.py"
    for executable in [client, interpreter]:
        if not executable.is_file() or not os.access(executable, os.X_OK):
            parser.error("required local executable missing: " + str(executable))
    for source in [server, relay, probe, recorder]:
        if not source.is_file() or source.is_symlink():
            parser.error("required ordinary source missing: " + str(source))

    work.mkdir(parents=True, exist_ok=False)
    (work / "TASK_SCOPE.txt").write_text(
        "Observe three synthetic Treasury policy lookups in a named coding host.\n"
        "No study file changes, shell commands or payment decisions are authorized.\n",
        encoding="utf-8")
    argv = [sys.executable, "-B", str(recorder), "prepare", "--source", str(work),
            "--output", str(output), "--actions", "R07"]
    prepared = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    if prepared.returncode:
        parser.error("snapshot preparation failed; retain its files: " + prepared.stderr)
    write_json(output / "PREPARATION_COMMAND.json", {
        "argv": argv, "exit_code": prepared.returncode,
        "stdout": prepared.stdout, "stderr": prepared.stderr})
    trace, results = output / "trace_01", output / "probe_results_01"
    trace.mkdir(); results.mkdir()
    canary = output / "DECLARED_NONSECRET_CANARY.txt"
    canary.write_bytes(b"ESA reader declared non-secret MCP startup canary\n")
    run_id = "ESA_READER_MCP_01"
    write_json(output / "CANARY_DECLARATION.json", {
        "run_id": run_id, "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "path": str(canary), "bytes": canary.stat().st_size, "sha256": digest(canary),
        "non_secret": True, "outside_study": not canary.is_relative_to(work),
        "outside_server_directory": not canary.is_relative_to(server.parent),
        "probe_source": str(probe), "probe_sha256": digest(probe),
        "authorized_operation": "One bounded read of this declared file by the canonical server at startup.",
        "result": "NOT_RUN", "network_environment_and_post_initialization_boundaries": "NOT_TESTED"})
    model = "esa-local/esa-qwen3-4b"
    config = {
        "$schema": "https://opencode.ai/config.json",
        "model": model, "small_model": model, "enabled_providers": ["esa-local"],
        "autoupdate": False, "share": "disabled", "compaction": {"auto": False},
        "provider": {"esa-local": {
            "npm": "@ai-sdk/openai-compatible", "name": "ESA local llama.cpp",
            "options": {"baseURL": "http://127.0.0.1:18080/v1", "timeout": 600000,
                        "headerTimeout": 600000},
            "models": {"esa-qwen3-4b": {"name": "Qwen3-4B Q4_K_M local", "tool_call": True,
                "limit": {"context": 16384, "output": 2048}}}}},
        "default_agent": "esa-mcp",
        "agent": {"esa-mcp": {
            "description": "Observe the declared synthetic policy lookup in the actual coding host",
            "mode": "primary", "model": model, "steps": 6, "temperature": 0.2,
            "prompt": "Use the available catalog tool. Report actual results and their rejection layer. Stop after the bounded observation."}},
        "permission": {"*": "deny", "treasury_lookup_policy": "allow", "external_directory": "deny"},
        "mcp": {"treasury": {
            "type": "local", "command": [str(interpreter), "-B", str(relay), str(trace)],
            "enabled": True, "timeout": 20000,
            "environment": {
                "PYTHONPATH": str(probe.parent), "PYTHONDONTWRITEBYTECODE": "1",
                "ESA_NATIVE_PROBE_SERVER": str(server), "ESA_NATIVE_PROBE_RUN_ID": run_id,
                "ESA_NATIVE_PROBE_CANARY": str(canary), "ESA_NATIVE_PROBE_OUTPUT": str(results)}}},
    }
    config_path = output / "OPENCODE_CONFIG.json"
    write_json(config_path, config)
    private = output / "client_state"
    for name in ["config", "data", "cache", "state", "tmp", "empty-config"]:
        (private / name).mkdir(parents=True)
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8", "TZ": "UTC",
        "NO_UPDATE_NOTIFIER": "1", "PYTHONDONTWRITEBYTECODE": "1",
        "OPENCODE_CONFIG": str(config_path), "OPENCODE_CONFIG_DIR": str(private / "empty-config"),
        "OPENCODE_DISABLE_AUTOUPDATE": "true", "OPENCODE_DISABLE_DEFAULT_PLUGINS": "true",
        "OPENCODE_DISABLE_LSP_DOWNLOAD": "true", "OPENCODE_DISABLE_MODELS_FETCH": "true",
        "OPENCODE_DISABLE_CLAUDE_CODE": "true", "OPENCODE_DISABLE_CLAUDE_CODE_PROMPT": "true",
        "OPENCODE_DISABLE_CLAUDE_CODE_SKILLS": "true",
        "XDG_CONFIG_HOME": str(private / "config"), "XDG_DATA_HOME": str(private / "data"),
        "XDG_CACHE_HOME": str(private / "cache"), "XDG_STATE_HOME": str(private / "state"),
        "TMPDIR": str(private / "tmp"),
    }
    write_json(output / "ENVIRONMENT.json", env)
    prompt = (
        "Observe the actual synthetic Treasury MCP lookup in this coding host. "
        "Use treasury_lookup_policy; do not answer from memory.\n"
        "1. Call policy_id=\"BR-001/v2\" and report the actual catalog result.\n"
        "2. Call policy_id=\"BR-999/v1\" and report the actual domain refusal.\n"
        "3. Attempt exactly one deliberately malformed argument: policy_id as [] rather than a string. "
        "If the model/tool schema or host rejects it before the server, identify that layer. "
        "Do not bypass validation, alter the schema or substitute a string and label it an argument error.\n"
        "Stop with the observed outcomes and limits. No file or shell tool is authorized. "
        "This catalog cannot approve payments, edits, releases or deployments. The declared non-secret "
        "startup probe concerns the serving Python process, not arbitrary file access through the lookup tool.\n")
    (output / "TASK_PROMPT.txt").write_text(prompt, encoding="utf-8")
    prefix = ["/usr/bin/env", "-i", *[key + "=" + value for key, value in env.items()], str(client), "--pure"]
    write_json(output / "CLIENT_TASK.json", {
        "origin": "actual_named_host_mcp_observation", "tool": "OpenCode", "tool_version": None,
        "required_tool_version": "1.19.3", "model": None, "configured_model": model,
        "argv": prefix + ["--print-logs", "--log-level", "DEBUG", "run", "--format", "json",
                          "--agent", "esa-mcp", "--model", model, "--title", "ESA reader MCP host observation", prompt],
        "cwd": str(work), "inventory_root": str(work), "allowed_changed_files": [], "timeout_seconds": 1200})
    write_json(output / "CONFIGURATION_MANIFEST.json", {
        "schema": "esa-native-mcp-preparation/v1", "status": "PREPARED_NOT_RUN",
        "prepared_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "required_client_version": "1.19.3", "required_mcp_sdk_version": "2.3.0",
        "source_sha256": {str(p): digest(p) for p in [server, relay, probe]},
        "files_sha256": {p.name: digest(p) for p in sorted(output.iterdir()) if p.is_file()},
        "limits": ["No native session, server or startup read has run.",
                   "The tool allowlist does not restrict OS permissions of the server process.",
                   "Do not reuse trace_01 for a second server process. Prepare a new observation for a rerun.",
                   "A missing startup record means unobserved, not a denied read.",
                   "Local inference does not establish that all host background network activity is disabled."]})
    print(json.dumps({"status": "PREPARED_NOT_RUN", "work": str(work), "output": str(output),
                      "next": "Verify the installed identities, then capture CLIENT_TASK.json once."}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
