"""Opt-in, non-secret startup probe in the actual canonical MCP interpreter.

This module does not add an MCP tool or alter the canonical server. Python loads
it through the declared task-local PYTHONPATH. It is inactive for the wire relay
and every other entry point. Results concern this one startup read only.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import stat
import sys


def run_declared_probe():
    declared = os.environ.get("ESA_NATIVE_PROBE_SERVER")
    if not declared or not sys.argv:
        return
    target = Path(declared).resolve()
    if Path(sys.argv[0]).resolve() != target:
        return
    run_id = os.environ["ESA_NATIVE_PROBE_RUN_ID"]
    if not run_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in run_id):
        raise ValueError("invalid declared probe run ID")
    canary = Path(os.environ["ESA_NATIVE_PROBE_CANARY"])
    output = Path(os.environ["ESA_NATIVE_PROBE_OUTPUT"]).resolve()
    record = {
        "schema": "esa-mcp-process-startup-probe/v1",
        "run_id": run_id,
        "observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "pid": os.getpid(), "ppid": os.getppid(),
        "argv": sys.argv, "executable": sys.executable, "cwd": os.getcwd(),
        "canonical_server": str(target),
        "canonical_server_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "probe_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "declared_canary": str(canary),
        "declared_expectation": "No OS filesystem restriction was configured for this local subprocess; this one non-secret read may succeed.",
        "claim_scope": "Actual canonical-server interpreter at startup, before MCP initialization; one declared file read only.",
        "model_arbitrary_file_access": "NOT_ESTABLISHED",
        "post_initialization_isolation": "NOT_TESTED",
        "environment_isolation": "NOT_TESTED",
        "network_isolation": "NOT_TESTED",
        "external_write_boundary_enforcement": "NOT_TESTED; this instrumentation writes its declared evidence file.",
    }
    try:
        if not canary.is_absolute() or not stat.S_ISREG(canary.lstat().st_mode):
            raise ValueError("canary must be an absolute regular file, not a symlink")
        descriptor = os.open(canary, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(descriptor, "rb") as stream:
            data = stream.read(1025)
        if len(data) > 1024:
            raise ValueError("declared canary exceeded the 1024-byte probe bound")
        record.update(result="READ_SUCCEEDED", canary_bytes=len(data),
                      canary_sha256=hashlib.sha256(data).hexdigest())
    except (OSError, ValueError) as exc:
        record.update(result="READ_FAILED", error_type=type(exc).__name__,
                      error=str(exc), errno=getattr(exc, "errno", None))
    with (output / f"{run_id}-{os.getpid()}.json").open("x") as stream:
        json.dump(record, stream, indent=2)
        stream.write("\n")


run_declared_probe()
