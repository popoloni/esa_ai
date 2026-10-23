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
    parser.add_argument("--ctx-size", type=int, default=16384,
                        help="Per-slot context size; the observed Chapter 1 default is 16384.")
    parser.add_argument("--cache-type-k", choices=("q8_0", "q4_0"), default="q8_0",
                        help="Key-cache representation; retain the exact observed choice.")
    parser.add_argument("--cache-type-v", choices=("q8_0", "q4_0"), default="q8_0",
                        help="Value-cache representation; retain the exact observed choice.")
    args = parser.parse_args()
    if args.ctx_size <= 0:
        parser.error("--ctx-size must be positive")
    runtime = args.runtime_root.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    binary = runtime / "llama_cpp/llama-b11799/llama-server"
    model = runtime / "downloads/Qwen3-4B-Q4_K_M.gguf"
    argv = [str(binary), "--model", str(model), "--alias", "esa-qwen3-4b",
            "--host", "127.0.0.1", "--port", "18080", "--ctx-size", str(args.ctx_size),
            "--parallel", "1", "--threads", "8", "--threads-batch", "8",
            "--n-gpu-layers", "0", "--ubatch-size", "128", "--jinja",
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
               "scope": "Loopback inference only; no built-in server agent tools or MCP hosts enabled."}
    start = time.monotonic()
    with (evidence / "stdout.txt").open("xb") as out, (evidence / "stderr.txt").open("xb") as err:
        process = subprocess.Popen(argv, cwd=runtime, env=env, stdout=out, stderr=err)
        receipt["server_pid"] = process.pid
        (evidence / "START.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps({"server_pid": process.pid, "evidence": str(evidence)}), flush=True)

        def stop(signum, frame):
            receipt.setdefault("termination_signals", []).append({"signal": signum, "at_utc": now()})
            if process.poll() is None:
                process.terminate()

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        code = process.wait()
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt.update({"finished_at_utc": now(), "exit_code": code,
                    "wall_seconds": time.monotonic() - start,
                    "child_user_cpu_seconds": usage.ru_utime,
                    "child_system_cpu_seconds": usage.ru_stime,
                    "child_max_rss_kib": usage.ru_maxrss})
    (evidence / "FINISH.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"exit_code": code, "finished_at_utc": receipt["finished_at_utc"]}), flush=True)
    return code if code >= 0 else 128 - code


if __name__ == "__main__":
    raise SystemExit(main())
