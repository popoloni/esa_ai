#!/usr/bin/env python3
"""Record PATH/version observations without probing accounts or credentials."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

CLIENTS = ("codex", "claude", "copilot", "opencode", "gemini", "code")
TOOLS = (*CLIENTS, "specify", "openspec", "uv", "python3", "git")


def observe():
    rows = []
    for name in TOOLS:
        path = shutil.which(name)
        row = {"name": name, "path": path, "path_status": "FOUND" if path else "ABSENT"}
        if path:
            row["version_argv"] = [path, "--version"]
            try:
                result = subprocess.run(row["version_argv"], capture_output=True,
                                        text=True, timeout=10, stdin=subprocess.DEVNULL)
                row.update(version_exit_code=result.returncode,
                           version_stdout=result.stdout[:4096], version_stderr=result.stderr[:4096],
                           output_truncated=len(result.stdout) > 4096 or len(result.stderr) > 4096,
                           version_command_status="SUCCEEDED" if result.returncode == 0 else "FAILED")
            except (OSError, subprocess.TimeoutExpired) as exc:
                row["version_error"] = type(exc).__name__
                row["version_command_status"] = "FAILED"
        rows.append(row)
    return {
        "schema": "coding-client-path-observation/v2",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version, "platform": platform.platform(), "executables": rows,
        "named_client_found_on_path": any(r["path"] for r in rows if r["name"] in CLIENTS),
        "named_client_version_command_succeeded": any(
            r.get("version_command_status") == "SUCCEEDED" for r in rows if r["name"] in CLIENTS),
        "authentication": "NOT_CHECKED", "account_or_plan": None,
        "model_generation": "NOT_ATTEMPTED", "native_skill_loading": "NOT_TESTED",
        "credential_files_read": False,
        "scope": "PATH and bounded --version observations only. Absence is local; presence does not prove authentication, supported flags, or a successful agent run.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New JSON file; existing files are refused")
    args = parser.parse_args()
    record = observe()
    text = json.dumps(record, indent=2) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
