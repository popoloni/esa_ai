#!/usr/bin/env python3
"""Prepare a fresh, narrowly scoped OpenCode 1.19.3 Chapter 1 observation.

This helper creates configuration, prompts and literal command specifications.
Its only subprocess is a read-only Git worktree probe. It does not invoke a
model, edit the router, change permissions in the OS, or accept a candidate.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess


CLIENT_VERSION = "1.19.3"
MODEL = "esa-local/esa-qwen3-4b"
ROUTER = "repo/src/treasury/routing.py"
INTENT = "reader_side/intent/INT-001.md"
CASES = "reader_side/acceptance/test_routing.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def relative_json(value: str) -> str:
    path = PurePosixPath(value)
    if (path.is_absolute() or ".." in path.parts or path.as_posix() != value
            or path.parent.as_posix() != "reader_side/evidence"
            or not re.fullmatch(r"[A-Za-z0-9_.-]+\.json", path.name)):
        raise argparse.ArgumentTypeError(
            "use a canonical reader_side/evidence/NAME.json path")
    return value


def inspect_worktree(work: Path) -> tuple[Path, dict]:
    executable = shutil.which("git")
    if not executable:
        raise ValueError("Git is needed to inspect the actual worktree; this helper will not guess it")
    argv = [executable, "-C", str(work), "rev-parse", "--show-toplevel"]
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    record = {"argv": argv, "exit_code": completed.returncode,
              "stdout": completed.stdout, "stderr": completed.stderr,
              "observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
    if completed.returncode == 0 and completed.stdout.strip():
        worktree = Path(completed.stdout.strip()).resolve(strict=True)
        if not work.is_relative_to(worktree):
            raise ValueError("Git reported a worktree that does not contain the study copy")
        record["mode"] = "GIT_WORKTREE"
    elif "not a git repository" in completed.stderr.lower():
        # This is the observed/pinned OpenCode 1.19.3 non-Git convention.
        worktree = Path("/")
        record["mode"] = "OPENCODE_1_19_3_NON_GIT_ROOT"
    else:
        raise ValueError("Cannot determine worktree: " + completed.stderr.strip())
    record["permission_worktree"] = str(worktree)
    return worktree, record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True,
                        help="fresh prepared Chapter 1 companion copy")
    parser.add_argument("--runtime-root", type=Path, required=True,
                        help="directory containing the pinned opencode installation")
    parser.add_argument("--output", type=Path, required=True,
                        help="new configuration/evidence directory outside the study copy")
    parser.add_argument("--initial-report", type=relative_json,
                        default="reader_side/evidence/CH01_NATIVE_INITIAL_01.json")
    parser.add_argument("--baseline", type=relative_json,
                        default="reader_side/evidence/CP01_NATIVE_BASELINE_01.json")
    parser.add_argument("--candidate-output", type=relative_json,
                        default="reader_side/evidence/CH01_NATIVE_AGENT_01.json")
    args = parser.parse_args()
    if args.work.is_symlink() or args.output.is_symlink():
        parser.error("use ordinary directories, not symlink roots")
    work = args.work.resolve(strict=True)
    runtime = args.runtime_root.resolve(strict=True)
    output = args.output.resolve()
    if not work.is_dir() or output.exists() or output.is_relative_to(work):
        parser.error("choose a new output directory outside the existing study copy")
    # Keep the named launcher path: resolving its symlink can change its name.
    client = runtime / "opencode/node_modules/.bin/opencode"
    if not client.is_file() or not os.access(client, os.X_OK):
        parser.error("the expected local OpenCode launcher is not executable")
    required = [ROUTER, INTENT, CASES, "repo/AGENTS.md", args.initial_report,
                args.baseline, "reader_side/protected_sha256.json"]
    if any(not (work / name).is_file() or (work / name).is_symlink() for name in required):
        parser.error("required study inputs must be existing ordinary files")
    if (work / args.candidate_output).exists():
        parser.error("candidate report already exists; preserve it and choose an unused name")
    initial = json.loads((work / args.initial_report).read_text())
    baseline = json.loads((work / args.baseline).read_text())
    if (initial.get("status") != "FAIL"
            or (initial.get("passed"), initial.get("failures"), initial.get("errors")) != (3, 2, 2)
            or initial.get("candidate_sha256") != digest(work / ROUTER)
            or initial.get("intent_sha256") != digest(work / INTENT)
            or initial.get("acceptance_sha256") != digest(work / CASES)
            or initial.get("integrity_before") != [] or initial.get("integrity_after") != []):
        parser.error("initial report does not describe the unchanged, protected 3/2/2 starter")
    if (baseline.get("schema") != "chapter-edit-baseline/v1"
            or baseline.get("chapter") != "CP01"
            or baseline.get("allowed_paths") != ["src/treasury/routing.py"]
            or baseline.get("repo_files", {}).get("src/treasury/routing.py") != digest(work / ROUTER)
            or baseline.get("protected_manifest_sha256") != digest(work / "reader_side/protected_sha256.json")):
        parser.error("scope baseline does not describe the current CP01 starter and protected manifest")
    try:
        worktree, probe = inspect_worktree(work)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        parser.error(str(exc))
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "WORKTREE_PROBE.json", probe)

    def key(relative: str) -> str:
        return (work / relative).relative_to(worktree).as_posix()

    check = ("python3 -B reader_side/tools/run_acceptance.py --output "
             + args.candidate_output)
    reads = ["repo/AGENTS.md", ROUTER, INTENT, CASES,
             args.initial_report, args.candidate_output]
    config = {
        "$schema": "https://opencode.ai/config.json",
        "model": MODEL, "small_model": MODEL, "enabled_providers": ["esa-local"],
        "autoupdate": False, "share": "disabled", "compaction": {"auto": False},
        "provider": {"esa-local": {
            "npm": "@ai-sdk/openai-compatible", "name": "ESA local llama.cpp",
            "options": {"baseURL": "http://127.0.0.1:18080/v1", "timeout": 600000,
                        "headerTimeout": 600000},
            "models": {"esa-qwen3-4b": {"name": "Qwen3-4B Q4_K_M local",
                "tool_call": True, "limit": {"context": 16384, "output": 2048}}}}},
        "default_agent": "esa-bounded",
        "agent": {"esa-bounded": {
            "description": "Bounded ESA local-model routing exercise", "mode": "primary",
            "model": MODEL, "steps": 8, "temperature": 0.2,
            "prompt": "Inspect the supplied task and permitted files. Make only the authorized change. Report actual tool results, preserve failures and stop for human review."}},
        "permission": {
            "*": "deny", "read": {"*": "deny", **{key(p): "allow" for p in reads}},
            "edit": {"*": "deny", key(ROUTER): "allow"},
            "bash": {"*": "deny", check: "allow"},
            "external_directory": "deny", "glob": "deny", "grep": "deny",
            "task": "deny", "skill": "deny", "webfetch": "deny", "websearch": "deny"},
        "mcp": {},
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
        "Perform the bounded Chapter 1 routing repair in this disposable companion copy.\n\n"
        "The actual working directory is " + str(work) + ".\n"
        "Read these exact absolute paths; do not omit the study-copy directory:\n"
        + "\n".join(str(work / p) for p in [INTENT, CASES, ROUTER, args.initial_report, "repo/AGENTS.md"])
        + "\n\nThe retained initial result is 3 passes, 2 failures and 2 errors. "
        "Follow INT-001. Repair only " + str(work / ROUTER) + ". "
        "Preserve the public API, BR-001/v1 and the EUR5,000 boundary. "
        "Do not read worked answers or edit the intent, tests, checkers, baselines or other source.\n\n"
        "After your edit run this exact command once, from the existing working directory:\n"
        + check + "\n\nIf a tool or check fails, report its actual error and stop. "
        "The checker's named JSON is the sole authorized generated report. "
        "Do not claim a pass you have not observed. Report the change and actual result. "
        "Only if all seven acceptance cases pass and the check reports no integrity findings "
        "may you state READY_FOR_HUMAN_REVIEW_NOT_ACCEPTED. Otherwise state the actual "
        "failure or TASK_NOT_COMPLETED and stop without a readiness claim. "
        "No payment, merge, deployment or human acceptance is authorized.\n"
    )
    (output / "TASK_PROMPT.txt").write_text(prompt, encoding="utf-8")
    prefix = ["/usr/bin/env", "-i", *[k + "=" + v for k, v in env.items()], str(client), "--pure"]

    def task(argv: list[str], origin: str, allowed: list[str], timeout: int) -> dict:
        return {"origin": origin, "tool": "OpenCode", "tool_version": None,
                "required_tool_version": CLIENT_VERSION, "model": None,
                "configured_model": MODEL, "argv": prefix + argv,
                "cwd": str(work), "inventory_root": str(work),
                "allowed_changed_files": allowed, "timeout_seconds": timeout}

    for name, argv in [("VERSION_TASK", ["--version"]),
                       ("CONFIG_TASK", ["debug", "config"]),
                       ("AGENT_TASK", ["debug", "agent", "esa-bounded"])]:
        write_json(output / (name + ".json"), task(argv, "native_configuration_probe", [], 60))
    write_json(output / "CLIENT_TASK.json", task(
        ["--print-logs", "--log-level", "DEBUG", "run", "--format", "json",
         "--agent", "esa-bounded", "--model", MODEL,
         "--title", "ESA reader Chapter1 native attempt01", prompt],
        "actual_named_client_chapter01_attempt", [ROUTER, args.candidate_output], 1800))
    manifest = {
        "schema": "esa-native-client-preparation/v1", "status": "PREPARED_NOT_RUN",
        "prepared_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "required_client_version": CLIENT_VERSION, "work": str(work),
        "runtime_root": str(runtime), "permission_worktree": str(worktree),
        "automatic_compaction": False,
        "initial_report": args.initial_report, "scope_baseline": args.baseline,
        "candidate_report": args.candidate_output,
        "input_sha256": {p: digest(work / p) for p in required},
        "files_sha256": {p.name: digest(p) for p in sorted(output.iterdir()) if p.is_file()},
        "limits": ["No inference or candidate change performed by this helper.",
                   "Configured model and required client identities are declarations pending actual diagnostics.",
                   "Application allowlists are not OS process containment.",
                   "The 600-second per-request and 1800-second outer deadlines are bounded CPU-study settings, not expected durations.",
                   "Automatic compaction is explicitly disabled after the retained continued session began compaction after its final-looking text; inspect actual process completion separately.",
                   "Disabling optional plugins did not prevent every background package attempt in the retained author run.",
                   "Worked solutions ship in the companion; the author had prior exposure, so this is not a blind benchmark."]}
    write_json(output / "CONFIGURATION_MANIFEST.json", manifest)
    print(json.dumps({"status": "PREPARED_NOT_RUN", "output": str(output),
                      "next": "Capture VERSION_TASK, CONFIG_TASK and AGENT_TASK; inspect identity/effective rules before CLIENT_TASK."}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
