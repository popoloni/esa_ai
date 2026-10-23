#!/usr/bin/env python3
"""Prepare/run the pinned d8 f16 local server with a bounded lifecycle.

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
    parser.add_argument("--ctx-size", type=int, default=22528,
                        help="Per-slot context size; d8 startup candidate is 22528, pending memory/token gates.")
    parser.add_argument("--cache-type-k", choices=("f16", "q8_0", "q4_0"), default="f16",
                        help="Key-cache representation; retain the exact observed choice.")
    parser.add_argument("--cache-type-v", choices=("f16", "q8_0", "q4_0"), default="f16",
                        help="Value-cache representation; retain the exact observed choice.")
    parser.add_argument("--shutdown-grace-seconds", type=float, default=30.0,
                        help="Grace after the first stop request before SIGKILL to this launcher's still-running child.")
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--ubatch-size", type=int, default=128)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--max-runtime-seconds", type=float, default=7200.0,
                        help="Finite wall limit from launch; initiates the same bounded direct-child shutdown.")
    parser.add_argument("--print-plan", action="store_true",
                        help="Print argv/identity plan without creating evidence or starting any child.")
    args = parser.parse_args()
    if args.ctx_size <= 0:
        parser.error("--ctx-size must be positive")
    if not math.isfinite(args.shutdown_grace_seconds) or args.shutdown_grace_seconds <= 0:
        parser.error("--shutdown-grace-seconds must be finite and positive")
    if args.batch_size <= 0 or args.ubatch_size <= 0 or args.ubatch_size > args.batch_size or args.threads <= 0:
        parser.error("batch, microbatch and thread values must be positive; microbatch must not exceed batch")
    if not math.isfinite(args.max_runtime_seconds) or args.max_runtime_seconds <= 0:
        parser.error("--max-runtime-seconds must be finite and positive")
    runtime = args.runtime_root.resolve()
    evidence = args.evidence.resolve()
    binary = runtime / "llama_cpp/llama-b11799/llama-server"
    model = runtime / "downloads/Qwen3-4B-Q4_K_M.gguf"
    argv = [str(binary), "--model", str(model), "--alias", "esa-qwen3-4b",
            "--host", "127.0.0.1", "--port", "18080", "--ctx-size", str(args.ctx_size),
            "--parallel", "1", "--threads", str(args.threads), "--threads-batch", str(args.threads),
            "--n-gpu-layers", "0", "--batch-size", str(args.batch_size),
            "--ubatch-size", str(args.ubatch_size), "--jinja", "--reasoning", "off",
            "--no-repack", "--no-warmup", "--no-context-shift", "--verbosity", "4",
            "--n-predict", "3072",
            "--no-agent", "--no-ui-mcp-proxy", "--no-webui", "--metrics",
            "--timeout", "1500", "--cache-ram", "0", "--ctx-checkpoints", "0",
            "--cache-type-k", args.cache_type_k, "--cache-type-v", args.cache_type_v,
            "--flash-attn", "on"]
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
           "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC"}
    receipt = {"schema": "esa-local-server-lifecycle/v2", "argv": argv,
               "cwd": str(runtime), "environment": env,
               "started_at_utc": now(), "launcher_pid": os.getpid(),
               "launcher_identity": {"path": str(Path(__file__).resolve()),
                                     "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
               "python": {"executable": sys.executable, "version": sys.version},
               "startup_status": "No inference authorized by launcher; health, memory and token budget require separate review",
               "maximum_runtime_seconds": args.max_runtime_seconds,
               "shutdown_policy": {"grace_seconds": args.shutdown_grace_seconds,
                                   "clock": "monotonic", "poll_seconds": 0.2,
                                   "repeated_signals_reset_deadline": False,
                                   "escalation_target": "Only the exact still-running direct child created by this launcher",
                                   "timing_limit": "Escalation is checked after the grace interval; scheduling and I/O can add delay."},
               "scope": "Loopback inference only; no built-in server agent tools or MCP hosts enabled."}
    if args.print_plan:
        receipt["plan_only"] = True
        receipt["prepared_at_utc"] = receipt.pop("started_at_utc")
        receipt.pop("launcher_pid", None)
        print(json.dumps(receipt, indent=2))
        return 0
    if not binary.is_file() or not model.is_file():
        parser.error("Pinned server executable and model file must already exist")
    evidence.mkdir(parents=True, exist_ok=False)
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
                if stop_requested is None and time.monotonic() - start >= args.max_runtime_seconds:
                    receipt["automatic_stop_reason"] = "MAXIMUM_RUNTIME_REACHED"
                    stop(signal.SIGTERM, None)
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
                    "child_max_rss_kib": usage.ru_maxrss,
                    "shutdown_result": ("FORCED_EXIT_AFTER_GRACE" if kill_sent else
                                        "EXIT_AFTER_STOP_REQUEST" if stop_requested is not None else
                                        "EXIT_WITHOUT_STOP_REQUEST")})
    (evidence / "FINISH.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"exit_code": code, "finished_at_utc": receipt["finished_at_utc"]}), flush=True)
    return code if code >= 0 else 128 - code


if __name__ == "__main__":
    raise SystemExit(main())
