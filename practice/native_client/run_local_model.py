#!/usr/bin/env python3
"""Run the pinned local inference server and retain its actual lifecycle.

The public runtime/model are obtained separately by download_local_stack.py.
This launcher performs no model request and enables no server-side agent tools.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import platform
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--server-binary", type=Path,
                        help="Explicit separately verified platform-native server; default retains the pinned runtime layout.")
    parser.add_argument("--n-gpu-layers", type=int, default=0,
                        help="Layers to offload to an available GPU backend; default 0 preserves the CPU recipe.")
    parser.add_argument("--ctx-size", type=int, default=16384,
                        help="Per-slot context size; the observed Chapter 1 default is 16384.")
    parser.add_argument("--cache-type-k", choices=("q8_0", "q4_0"), default="q8_0",
                        help="Key-cache representation; retain the exact observed choice.")
    parser.add_argument("--cache-type-v", choices=("q8_0", "q4_0"), default="q8_0",
                        help="Value-cache representation; retain the exact observed choice.")
    parser.add_argument("--shutdown-grace-seconds", type=float, default=30.0,
                        help="Grace after the first stop request before SIGKILL to this launcher's still-running child.")
    args = parser.parse_args()
    if args.n_gpu_layers < 0:
        parser.error("--n-gpu-layers must be nonnegative")
    if args.ctx_size <= 0:
        parser.error("--ctx-size must be positive")
    if not math.isfinite(args.shutdown_grace_seconds) or args.shutdown_grace_seconds <= 0:
        parser.error("--shutdown-grace-seconds must be finite and positive")
    runtime = args.runtime_root.resolve()
    evidence = args.evidence.resolve()
    binary = (args.server_binary.expanduser().resolve() if args.server_binary else
              runtime / "llama_cpp/llama-b11799/llama-server")
    model = runtime / "downloads/Qwen3-4B-Q4_K_M.gguf"
    if not binary.is_file() or not os.access(binary, os.X_OK) or not model.is_file():
        parser.error("Pinned executable server and model file must already exist")
    evidence.mkdir(parents=True, exist_ok=False)
    argv = [str(binary), "--model", str(model), "--alias", "esa-qwen3-4b",
            "--host", "127.0.0.1", "--port", "18080", "--ctx-size", str(args.ctx_size),
            "--parallel", "1", "--threads", "8", "--threads-batch", "8",
            "--n-gpu-layers", str(args.n_gpu_layers), "--ubatch-size", "128", "--jinja",
            "--chat-template-kwargs", '{"enable_thinking":false}',
            "--no-agent", "--no-ui-mcp-proxy", "--no-webui", "--metrics",
            "--timeout", "300", "--cache-ram", "0", "--ctx-checkpoints", "0",
            "--cache-type-k", args.cache_type_k, "--cache-type-v", args.cache_type_v,
            "--flash-attn", "on"]
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
           "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC"}
    receipt = {"schema": "esa-local-server-lifecycle/v1", "argv": argv,
               "cwd": str(runtime), "environment": env,
               "started_at_utc": now(), "launcher_pid": os.getpid(),
               "launcher_identity": {"path": str(Path(__file__).resolve()),
                                     "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
               "python": {"executable": sys.executable, "version": sys.version},
               "host": {"system": platform.system(), "machine": platform.machine()},
               "server_identity": {"path": str(binary), "sha256": hashlib.sha256(binary.read_bytes()).hexdigest()},
               "shutdown_policy": {"grace_seconds": args.shutdown_grace_seconds,
                                   "clock": "monotonic", "poll_seconds": 0.2,
                                   "repeated_signals_reset_deadline": False,
                                   "escalation_target": "Only the exact still-running direct child created by this launcher",
                                   "timing_limit": "Escalation is checked after the grace interval; scheduling and I/O can add delay."},
               "scope": "Loopback inference only; no built-in server agent tools or MCP hosts enabled."}
    start = time.monotonic()
    with (evidence / "stdout.txt").open("xb") as out, (evidence / "stderr.txt").open("xb") as err:
        process = subprocess.Popen(argv, cwd=runtime, env=env, stdout=out, stderr=err)
        receipt["server_pid"] = process.pid
        stop_requested = None
        kill_sent = False
        recorded_events = 0

        def stop(signum, frame):
            nonlocal stop_requested
            receipt.setdefault("termination_signals", []).append({"signal": signum, "at_utc": now()})
            if stop_requested is None:
                stop_requested = time.monotonic()
                receipt["first_stop_requested_at_utc"] = now()
            if process.poll() is None:
                try:
                    process.terminate()
                    receipt.setdefault("shutdown_events", []).append(
                        {"action": "SIGTERM_SENT", "server_pid": process.pid, "at_utc": now()})
                except ProcessLookupError:
                    receipt.setdefault("shutdown_events", []).append(
                        {"action": "CHILD_ALREADY_GONE_AT_SIGTERM", "server_pid": process.pid, "at_utc": now()})

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        (evidence / "START.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps({"server_pid": process.pid, "evidence": str(evidence)}), flush=True)
        while True:
            try:
                code = process.wait(timeout=0.2)
                break
            except subprocess.TimeoutExpired:
                elapsed = time.monotonic() - stop_requested if stop_requested is not None else None
                if elapsed is not None and elapsed >= args.shutdown_grace_seconds and not kill_sent:
                    if process.poll() is None:
                        try:
                            process.kill()
                            kill_sent = True
                            receipt.setdefault("shutdown_events", []).append(
                                {"action": "SIGKILL_SENT", "server_pid": process.pid, "at_utc": now(),
                                 "seconds_after_first_stop_request": elapsed})
                        except ProcessLookupError:
                            receipt.setdefault("shutdown_events", []).append(
                                {"action": "CHILD_ALREADY_GONE_AT_SIGKILL", "server_pid": process.pid, "at_utc": now()})
                event_count = len(receipt.get("shutdown_events", []))
                if event_count != recorded_events:
                    (evidence / "SHUTDOWN.json").write_text(json.dumps(receipt, indent=2) + "\n")
                    recorded_events = event_count
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt.update({"finished_at_utc": now(), "exit_code": code,
                    "wall_seconds": time.monotonic() - start,
                    "child_user_cpu_seconds": usage.ru_utime,
                    "child_system_cpu_seconds": usage.ru_stime,
                    "child_max_rss_raw": usage.ru_maxrss,
                    "child_max_rss_raw_unit": "bytes" if platform.system() == "Darwin" else "KiB",
                    "child_max_rss_kib": usage.ru_maxrss / 1024 if platform.system() == "Darwin" else usage.ru_maxrss,
                    "shutdown_result": ("FORCED_EXIT_AFTER_GRACE" if kill_sent else
                                        "EXIT_AFTER_STOP_REQUEST" if stop_requested is not None else
                                        "EXIT_WITHOUT_STOP_REQUEST")})
    (evidence / "FINISH.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"exit_code": code, "finished_at_utc": receipt["finished_at_utc"]}), flush=True)
    return code if code >= 0 else 128 - code


if __name__ == "__main__":
    raise SystemExit(main())
