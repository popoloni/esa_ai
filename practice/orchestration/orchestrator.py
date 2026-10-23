#!/usr/bin/env python3
"""A small, observable process orchestrator. This is not a process sandbox.

The single atomic state.json is the authority for both task state and its event
journal. Workers exchange JSON files; a command adapter can wrap an installed
agent client. Completed processes are not equivalent to accepted engineering work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone


class Refused(ValueError):
    """The run cannot proceed while retaining its recorded meaning."""


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def regular(path: Path) -> Path:
    if path.is_symlink() or not path.is_file():
        raise Refused(f"Expected a regular, non-symlink file: {path}")
    return path


def confined(root: Path, relative: str) -> Path:
    """Check paths we consume; this does not confine a worker's OS access."""
    if not isinstance(relative, str) or relative in ("", "."):
        raise Refused("Relative output path must be a nonempty string naming a file")
    rel = Path(relative)
    if not relative or rel.is_absolute() or any(p in ("..", ".") for p in rel.parts):
        raise Refused(f"Unsafe relative output path: {relative}")
    cursor = root
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise Refused(f"Symlink in managed output: {cursor}")
    if not cursor.resolve().is_relative_to(root.resolve()):
        raise Refused(f"Output escapes run directory: {relative}")
    return cursor


def response_path(relative):
    confined(Path.cwd(), relative)
    if Path(relative).parts[0] in {"request.json", "stdout.txt", "stderr.txt"}:
        raise Refused("Response path collides with retained request or process logs")


def output_location(path: Path) -> Path:
    """Refuse accidental redirection and writes into the cumulative exercise."""
    raw = path.expanduser().absolute()
    cursor = Path(raw.anchor)
    for part in raw.parts[1:]:
        cursor = cursor / part
        if cursor.is_symlink():
            raise Refused("Output directory contains a symlink ancestor or destination")
    result = Path(os.path.abspath(raw))
    companion = Path(__file__).resolve().parents[2]
    if any(result.is_relative_to(companion / name) for name in ("repo", "reader_side")):
        raise Refused("Output must be outside the protected repo/ and reader_side/ trees")
    return result


def atomic_json(path: Path, value: dict) -> None:
    if path.is_symlink():
        raise Refused(f"Refusing symlink state destination: {path}")
    temporary = path.with_name(path.name + ".new")
    if temporary.exists() or temporary.is_symlink():
        raise Refused(f"Unexpected pending state file: {temporary}")
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    if os.name == "posix":
        fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def positive(value, label: str, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise Refused(f"{label} must be a positive number")
    if integer and not isinstance(value, int):
        raise Refused(f"{label} must be an integer")
    return value


def validate(plan: dict) -> dict:
    if plan.get("schema") != "treasury-orchestrator/v1":
        raise Refused("Unsupported plan schema")
    positive(plan.get("max_parallel"), "max_parallel", True)
    positive(plan.get("max_wall_seconds"), "max_wall_seconds")
    positive(plan.get("max_output_bytes", 1048576), "max_output_bytes", True)
    tasks = plan.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise Refused("A non-empty tasks list is required")
    if any(not isinstance(t, dict) for t in tasks):
        raise Refused("Every task must be an object")
    ids = [t.get("id") for t in tasks]
    if any(not isinstance(i, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,47}", i) for i in ids):
        raise Refused("Task IDs must be short filesystem-safe identifiers")
    if len(set(ids)) != len(ids):
        raise Refused("Duplicate task ID")
    by_id = {t["id"]: t for t in tasks}
    for task in tasks:
        if task.get("kind") not in ("worker", "human"):
            raise Refused(f"Unknown task kind: {task['id']}")
        deps = task.get("depends_on")
        if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps) or len(set(deps)) != len(deps) or any(d not in by_id for d in deps):
            raise Refused(f"Invalid dependencies: {task['id']}")
        if task["kind"] == "worker":
            positive(task.get("timeout_seconds"), "timeout_seconds")
            positive(task.get("max_attempts"), "max_attempts", True)
            if not isinstance(task.get("idempotent"), bool):
                raise Refused("A worker must explicitly declare idempotent true or false")
            if task["max_attempts"] > 1 and not task["idempotent"]:
                raise Refused("Automatic retry requires an explicitly idempotent task")
            response_path(task.get("response", "result.json"))
    pending, visited = set(ids), set()
    while pending:
        ready = {i for i in pending if set(by_id[i]["depends_on"]) <= visited}
        if not ready:
            raise Refused("Dependency graph contains a cycle")
        visited |= ready
        pending -= ready
    argv = plan.get("adapter_argv", ["{python}", "{worker}", "--request", "{request}", "--response", "{response}"])
    if not isinstance(argv, list) or not argv or any(not isinstance(a, str) or not a for a in argv):
        raise Refused("adapter_argv must be a non-empty string array")
    allowed = {"{python}", "{worker}", "{request}", "{response}"}
    if any(("{" in a or "}" in a) and a not in allowed for a in argv):
        raise Refused("Adapter placeholders must occupy a whole argument and be known")
    if "{request}" not in argv or "{response}" not in argv:
        raise Refused("Adapter must receive both request and response paths")
    return by_id


def identities(plan_path: Path, inputs: Path, worker: Path, plan: dict) -> dict:
    if inputs.is_symlink() or not inputs.is_dir():
        raise Refused("Inputs must be a regular directory")
    files = {}
    for path in sorted(inputs.rglob("*")):
        if path.is_symlink():
            raise Refused(f"Symlink input is not supported: {path}")
        if path.is_file():
            files[str(path.relative_to(inputs))] = digest(path)
    executable = plan.get("adapter_argv", ["{python}"])[0]
    executable = sys.executable if executable == "{python}" else (str(worker) if executable == "{worker}" else executable)
    binary = shutil.which(executable)
    if binary is None:
        raise Refused(f"Adapter executable is not installed: {executable}")
    return {"plan_sha256": digest(regular(plan_path)), "inputs": files,
            "code": {"orchestrator.py": digest(Path(__file__).resolve()), "worker_script": digest(regular(worker))},
            "python": sys.version, "adapter_executable_sha256": digest(Path(binary).resolve())}


def process_alive(pid) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def terminate(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGTERM)
        else:
            proc.terminate()
        proc.wait(timeout=0.4)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
        proc.wait(timeout=2)
    except ProcessLookupError:
        pass


class Runner:
    def __init__(self, plan_path: Path, inputs: Path, output: Path, worker: Path,
                 resume=False, retry_interrupted=False):
        self.plan_path, self.inputs, self.output, self.worker = [p.absolute() for p in (plan_path, inputs, output, worker)]
        self.plan = json.loads(regular(self.plan_path).read_text())
        self.by_id = validate(self.plan)
        self.identity = identities(self.plan_path, self.inputs, self.worker, self.plan)
        self.resume, self.retry_interrupted = resume, retry_interrupted
        self.running, self.stop_requested = {}, False
        self.state = None
        self.owned_lock = False

    def save(self, event: str, task=None, **detail):
        self.state["events"].append({"seq": len(self.state["events"]) + 1, "at_utc": utc(),
                                     "event": event, "task_id": task, **detail})
        self.state["updated_at_utc"] = utc()
        atomic_json(confined(self.output, "state.json"), self.state)

    def prepare(self):
        self.output = output_location(self.output)
        if self.output.resolve().is_relative_to(self.inputs.resolve()) or self.inputs.resolve().is_relative_to(self.output.resolve()):
            raise Refused("Input and output directories must be disjoint")
        if not self.resume:
            self.output.mkdir(parents=True, exist_ok=False)
        elif not self.output.is_dir():
            raise Refused("Resume requires an existing run directory")
        lock = confined(self.output, "run.lock")
        if lock.exists():
            data = json.loads(regular(lock).read_text())
            if process_alive(data.get("pid")):
                raise Refused("Another coordinator may still own this run")
            lock.unlink()  # A dead coordinator cannot own the local advisory lock.
        with lock.open("x") as stream:
            json.dump({"pid": os.getpid(), "started_at_utc": utc()}, stream)
        self.owned_lock = True
        if not self.resume:
            self.state = {"schema": "treasury-run/v1", "run_status": "RUNNING", "created_at_utc": utc(),
                          "deadline_epoch": time.time() + self.plan["max_wall_seconds"],
                          "identity": self.identity, "worker_kind": self.plan.get("worker_kind", "UNSPECIFIED"),
                          "peak_parallel": 0, "tasks": {i: {"status": "PENDING", "attempts": []} for i in self.by_id},
                          "events": []}
            self.save("RUN_CREATED")
        else:
            self.state = json.loads(regular(confined(self.output, "state.json")).read_text())
            if self.state.get("identity") != self.identity:
                raise Refused("Plan, input, code, interpreter or adapter identity changed; start a new run")
            for task_id, record in self.state["tasks"].items():
                if record["status"] == "COMPLETED":
                    path = regular(confined(self.output, record["result_path"]))
                    if digest(path) != record["result_sha256"]:
                        raise Refused(f"Completed result changed: {task_id}")
                if record["status"] == "RUNNING":
                    record["status"] = "UNCERTAIN"
                    record["attempts"][-1]["outcome"] = "INTERRUPTED_UNKNOWN"
            self.save("RESUME_REQUESTED", retry_interrupted=self.retry_interrupted)
            uncertain = []
            for task_id, record in self.state["tasks"].items():
                if record["status"] != "UNCERTAIN":
                    continue
                task = self.by_id[task_id]
                attempt = record["attempts"][-1]
                if process_alive(attempt.get("pid")) and attempt.get("outcome") == "INTERRUPTED_UNKNOWN":
                    uncertain.append(task_id)
                    continue
                if self.retry_interrupted and task["idempotent"] and len(record["attempts"]) < task["max_attempts"]:
                    record["status"] = "PENDING"
                    self.save("INTERRUPTED_RETRY_AUTHORIZED", task_id)
                else:
                    uncertain.append(task_id)
            if uncertain:
                self.state["run_status"] = "NEEDS_RECONCILIATION"
                self.save("RESUME_BLOCKED", tasks=uncertain)
                return False
            self.state["run_status"] = "RUNNING"
            self.save("RESUMED")
        return True

    def start(self, task_id: str):
        task, record = self.by_id[task_id], self.state["tasks"][task_id]
        if len(record["attempts"]) >= task["max_attempts"]:
            record["status"] = "FAILED"
            self.save("ATTEMPT_BUDGET_EXHAUSTED", task_id)
            return
        number = len(record["attempts"]) + 1
        directory = confined(self.output, f"attempts/{task_id}/{number:03d}")
        directory.mkdir(parents=True, exist_ok=False)
        request, response = directory / "request.json", confined(directory, task.get("response", "result.json"))
        response.parent.mkdir(parents=True, exist_ok=True)
        deps = {d: {"response_path": str(confined(self.output, self.state["tasks"][d]["result_path"])),
                    "sha256": self.state["tasks"][d]["result_sha256"]} for d in task["depends_on"]}
        atomic_json(request, {"schema": "treasury-worker-request/v1", "task": task, "attempt": number,
                              "input_root": str(self.inputs), "dependencies": deps,
                              "authority": "Read supplied inputs; write only this attempt's outputs. No acceptance or release authority."})
        values = {"{python}": sys.executable, "{worker}": str(self.worker), "{request}": str(request), "{response}": str(response)}
        argv = [values.get(a, a) for a in self.plan.get("adapter_argv", ["{python}", "{worker}", "--request", "{request}", "--response", "{response}"])]
        attempt = {"number": number, "started_at_utc": utc(), "outcome": "RUNNING", "pid": None,
                   "request_path": str(request.relative_to(self.output)), "argv": argv}
        record["status"] = "RUNNING"
        record["attempts"].append(attempt)
        self.save("TASK_DISPATCHING", task_id, attempt=number)
        stdout, stderr = (directory / "stdout.txt").open("xb"), (directory / "stderr.txt").open("xb")
        try:
            proc = subprocess.Popen(argv, cwd=directory, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                    start_new_session=(os.name == "posix"), shell=False)
        except (OSError, ValueError) as exc:
            stdout.close()
            stderr.close()
            attempt.update(outcome="START_FAILED", error=str(exc), finished_at_utc=utc())
            record["status"] = "FAILED"
            self.save("TASK_FAILED", task_id, reason="START_FAILED")
            return
        attempt["pid"] = proc.pid
        self.running[task_id] = {"proc": proc, "started": time.monotonic(), "stdout": stdout, "stderr": stderr,
                                 "response": response, "directory": directory}
        self.state["peak_parallel"] = max(self.state["peak_parallel"], len(self.running))
        self.save("TASK_STARTED", task_id, attempt=number, pid=proc.pid, active=len(self.running))

    def finish(self, task_id: str, reason=None):
        active = self.running.pop(task_id)
        proc, record, task = active["proc"], self.state["tasks"][task_id], self.by_id[task_id]
        if reason:
            terminate(proc)
        active["stdout"].close()
        active["stderr"].close()
        attempt = record["attempts"][-1]
        attempt.update(returncode=proc.poll(), finished_at_utc=utc(), elapsed_seconds=round(time.monotonic() - active["started"], 6))
        if reason == "INTERRUPTED":
            attempt["outcome"], record["status"] = "INTERRUPTED", "UNCERTAIN"
            self.save("TASK_INTERRUPTED", task_id)
            return
        if reason is None and proc.returncode != 0:
            reason = "NONZERO_EXIT"
        if reason is None:
            try:
                path = regular(confined(active["directory"], task.get("response", "result.json")))
                if path.stat().st_size > self.plan.get("max_output_bytes", 1048576):
                    raise Refused("Response exceeds configured output limit")
                result = json.loads(path.read_text())
                if not isinstance(result, dict) or result.get("task_id") != task_id or result.get("status") != "COMPLETED":
                    raise Refused("Response requires the matching task_id and status COMPLETED")
                record.update(result_path=str(path.relative_to(self.output)), result_sha256=digest(path))
            except (ValueError, OSError) as exc:
                reason = "INVALID_RESPONSE"
                attempt["error"] = str(exc)
        attempt["outcome"] = reason or "COMPLETED"
        if reason:
            retry = task["idempotent"] and len(record["attempts"]) < task["max_attempts"]
            record["status"] = "PENDING" if retry else "FAILED"
            self.save("TASK_RETRY_PENDING" if retry else "TASK_FAILED", task_id, reason=reason)
        else:
            record["status"] = "COMPLETED"
            self.save("TASK_COMPLETED", task_id, result_sha256=record["result_sha256"])

    def loop(self):
        while True:
            if self.stop_requested:
                for task_id in list(self.running):
                    self.finish(task_id, "INTERRUPTED")
                self.state["run_status"] = "INTERRUPTED"
                self.save("RUN_INTERRUPTED")
                return 130
            if time.monotonic() >= self.deadline_monotonic:
                for task_id in list(self.running):
                    self.finish(task_id, "RUN_DEADLINE")
                for record in self.state["tasks"].values():
                    if record["status"] == "PENDING":
                        record["status"] = "BUDGET_EXHAUSTED"
                self.state["run_status"] = "BUDGET_EXHAUSTED"
                self.save("RUN_DEADLINE")
                return 1
            for task_id, active in list(self.running.items()):
                task = self.by_id[task_id]
                size = sum(regular(active["directory"] / n).stat().st_size for n in ("stdout.txt", "stderr.txt"))
                if size > self.plan.get("max_output_bytes", 1048576):
                    self.finish(task_id, "OUTPUT_LIMIT")
                elif active["proc"].poll() is not None:
                    self.finish(task_id)
                elif time.monotonic() - active["started"] >= task["timeout_seconds"]:
                    self.finish(task_id, "TIMEOUT")
            try:
                unchanged = identities(self.plan_path, self.inputs, self.worker, self.plan) == self.identity
                for record in self.state["tasks"].values():
                    if record["status"] == "COMPLETED":
                        unchanged = unchanged and digest(regular(confined(self.output, record["result_path"]))) == record["result_sha256"]
            except (OSError, ValueError):
                unchanged = False
            if not unchanged:
                for task_id in list(self.running):
                    self.finish(task_id, "INPUT_OR_CODE_CHANGED")
                self.state["run_status"] = "INVALIDATED"
                self.save("IDENTITY_CHANGED")
                return 2
            for task_id, task in self.by_id.items():
                record = self.state["tasks"][task_id]
                if record["status"] != "PENDING":
                    continue
                deps = [self.state["tasks"][d]["status"] for d in task["depends_on"]]
                if any(s in ("FAILED", "BLOCKED_DEPENDENCY", "BUDGET_EXHAUSTED", "UNCERTAIN") for s in deps):
                    record["status"] = "BLOCKED_DEPENDENCY"
                    self.save("TASK_BLOCKED_DEPENDENCY", task_id)
                elif any(s in ("WAITING_HUMAN", "BLOCKED_HUMAN") for s in deps):
                    record["status"] = "BLOCKED_HUMAN"
                    self.save("TASK_BLOCKED_HUMAN", task_id)
                elif all(s == "COMPLETED" for s in deps):
                    if task["kind"] == "human":
                        record["status"] = "WAITING_HUMAN"
                        self.save("HUMAN_DECISION_REQUIRED", task_id)
                    elif len(self.running) < self.plan["max_parallel"]:
                        self.start(task_id)
            if not self.running and all(r["status"] != "PENDING" for r in self.state["tasks"].values()):
                statuses = {r["status"] for r in self.state["tasks"].values()}
                result = "COMPLETED" if statuses == {"COMPLETED"} else ("WAITING_HUMAN" if statuses <= {"COMPLETED", "WAITING_HUMAN", "BLOCKED_HUMAN"} else "FAILED")
                self.state["run_status"] = result
                self.save("RUN_STOPPED", reason=result)
                return 0 if result == "COMPLETED" else (3 if result == "WAITING_HUMAN" else 1)
            time.sleep(0.02)

    def run(self):
        old_handlers = {}
        try:
            if not self.prepare():
                return 3
            if all(r["status"] == "COMPLETED" for r in self.state["tasks"].values()):
                self.state["run_status"] = "COMPLETED"
                self.save("RESUME_NO_WORK")
                return 0
            # Preserve the original deadline across sessions; a local clock
            # adjustment must not extend the remaining time during this run.
            self.deadline_monotonic = time.monotonic() + max(0, self.state["deadline_epoch"] - time.time())
            def stop(signum, frame):
                self.stop_requested = True
            for sig in (signal.SIGINT, signal.SIGTERM):
                old_handlers[sig] = signal.signal(sig, stop)
            return self.loop()
        finally:
            for task_id in list(self.running):
                self.finish(task_id, "INTERRUPTED")
            for sig, handler in old_handlers.items():
                signal.signal(sig, handler)
            if self.owned_lock:
                confined(self.output, "run.lock").unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--worker-script", type=Path, default=Path(__file__).with_name("treasury_worker.py"))
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--retry-interrupted", action="store_true")
    args = parser.parse_args()
    try:
        runner = Runner(args.plan, args.inputs, args.output, args.worker_script, args.resume, args.retry_interrupted)
        code = runner.run()
        print(json.dumps({"run_status": runner.state["run_status"], "output": str(args.output), "exit_code": code}))
        return code
    except (Refused, FileExistsError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(json.dumps({"run_status": "REFUSED", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
