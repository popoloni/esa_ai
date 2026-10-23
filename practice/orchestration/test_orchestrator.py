#!/usr/bin/env python3
"""Integration checks for execution, stale evidence and bounded failure behavior."""
import copy
import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

from run_demo import HERE, command, invoke, plan, setup_case, state, worker, write


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="treasury-orchestrator-test-")
        self.root = Path(self.tmp.name)

    def tearDown(self):
        # Snapshot files are read-only but their containing directories are owned.
        self.tmp.cleanup()

    def case(self, spec=None):
        return setup_case(self.root, "case", spec or plan([worker("echo", mode="echo")]))

    def custom(self, body):
        path = self.root / "adapter.py"
        path.write_text("import argparse,json\nfrom pathlib import Path\np=argparse.ArgumentParser()\np.add_argument('--request')\np.add_argument('--response')\na=p.parse_args()\nr=json.loads(Path(a.request).read_text())\n" + body)
        return path

    def wait_running(self, case, proc):
        until = time.monotonic() + 5
        while time.monotonic() < until:
            if (case / "run/state.json").exists():
                data = state(case)
                if any(r["status"] == "RUNNING" for r in data["tasks"].values()):
                    return
            if proc.poll() is not None:
                self.fail("Coordinator exited before a worker started")
            time.sleep(0.02)
        self.fail("No running worker observed")

    def test_actual_parallel_dispatch_then_dependency(self):
        case = self.case(plan())
        self.assertEqual(invoke(case, "run").returncode, 0)
        data = state(case)
        self.assertEqual(data["peak_parallel"], 2)
        events = data["events"]
        start = next(e["seq"] for e in events if e["event"] == "TASK_STARTED" and e["task_id"] == "synthesis")
        for tid in ("policy", "routing"):
            done = next(e["seq"] for e in events if e["event"] == "TASK_COMPLETED" and e["task_id"] == tid)
            self.assertLess(done, start)
        self.assertEqual([e["seq"] for e in events], list(range(1, len(events) + 1)))

    def test_human_task_stops_dependents(self):
        spec = plan([{"id": "owner", "kind": "human", "depends_on": []}, worker("writer", mode="echo", deps=("owner",))])
        case = self.case(spec)
        self.assertEqual(invoke(case, "run").returncode, 3)
        self.assertEqual(state(case)["tasks"]["owner"]["status"], "WAITING_HUMAN")
        self.assertEqual(state(case)["tasks"]["writer"]["attempts"], [])

    def test_failed_dependency_never_dispatches(self):
        case = self.case(plan([worker("broken", mode="fail"), worker("dependent", mode="echo", deps=("broken",))]))
        self.assertEqual(invoke(case, "run").returncode, 1)
        self.assertEqual(state(case)["tasks"]["dependent"]["status"], "BLOCKED_DEPENDENCY")
        self.assertEqual(state(case)["tasks"]["dependent"]["attempts"], [])

    def test_retry_retains_both_attempts(self):
        case = self.case(plan([worker("retry", mode="retry_once", attempts=2)]))
        self.assertEqual(invoke(case, "run").returncode, 0)
        record = state(case)["tasks"]["retry"]
        self.assertEqual([a["outcome"] for a in record["attempts"]], ["NONZERO_EXIT", "COMPLETED"])
        self.assertEqual(record["attempts"][0]["returncode"], 7)

    def test_timeout_stops_after_attempt_budget(self):
        case = self.case(plan([worker("slow", mode="sleep", attempts=2, timeout=0.1, seconds=5)]))
        self.assertEqual(invoke(case, "run").returncode, 1)
        self.assertEqual([a["outcome"] for a in state(case)["tasks"]["slow"]["attempts"]], ["TIMEOUT", "TIMEOUT"])

    def test_deadline_exhausts_work(self):
        spec = plan([worker("slow", mode="sleep", timeout=3, seconds=5)])
        spec["max_wall_seconds"] = 0.15
        case = self.case(spec)
        self.assertEqual(invoke(case, "run").returncode, 1)
        self.assertEqual(state(case)["run_status"], "BUDGET_EXHAUSTED")

    def test_completed_resume_does_not_rerun_even_after_deadline(self):
        spec = plan()
        # Completion is the precondition under test. Give normal subprocess
        # startup room, then wait for the actual retained deadline to expire.
        # A half-second graph budget can fail before resume is exercised.
        spec["max_wall_seconds"] = 5
        case = self.case(spec)
        initial = invoke(case, "run")
        self.assertEqual(initial.returncode, 0, initial.stdout + initial.stderr)
        completed = state(case)
        before = {i: r["attempts"] for i, r in completed["tasks"].items()}
        deadline = completed["deadline_epoch"]
        time.sleep(max(0, deadline - time.time()) + 0.05)
        self.assertGreaterEqual(time.time(), deadline)
        resumed = invoke(case, "resume", "--resume")
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        self.assertEqual(before, {i: r["attempts"] for i, r in state(case)["tasks"].items()})

    def test_input_change_refuses_resume(self):
        case = self.case()
        self.assertEqual(invoke(case, "run").returncode, 0)
        path = case / "inputs/intent.md"
        path.chmod(0o644)
        path.write_text(path.read_text() + "changed\n")
        self.assertEqual(invoke(case, "resume", "--resume").returncode, 2)

    def test_plan_change_refuses_resume(self):
        case = self.case()
        self.assertEqual(invoke(case, "run").returncode, 0)
        spec = json.loads((case / "plan.json").read_text())
        spec["max_parallel"] = 1
        write(case / "plan.json", spec)
        self.assertEqual(invoke(case, "resume", "--resume").returncode, 2)

    def test_worker_code_change_refuses_resume(self):
        case = self.case()
        wrapper = self.custom("Path(a.response).write_text(json.dumps({'task_id':r['task']['id'],'status':'COMPLETED'}))\n")
        self.assertEqual(invoke(case, "run", "--worker-script", str(wrapper)).returncode, 0)
        wrapper.write_text(wrapper.read_text() + "# changed code\n")
        self.assertEqual(invoke(case, "resume", "--worker-script", str(wrapper), "--resume").returncode, 2)

    def test_changed_completed_result_refuses_resume(self):
        case = self.case()
        self.assertEqual(invoke(case, "run").returncode, 0)
        result = case / "run" / state(case)["tasks"]["echo"]["result_path"]
        result.write_text(result.read_text() + "\n")
        self.assertEqual(invoke(case, "resume", "--resume").returncode, 2)

    def test_escape_and_cycle_refused_before_dispatch(self):
        spec = plan([worker("escape", mode="echo")])
        spec["tasks"][0]["response"] = "../escape.json"
        case = self.case(spec)
        self.assertEqual(invoke(case, "escape").returncode, 2)
        self.assertFalse((case / "run").exists())
        spec = plan([worker("one", mode="echo", deps=("two",)), worker("two", mode="echo", deps=("one",))])
        write(case / "plan.json", spec)
        self.assertEqual(invoke(case, "cycle").returncode, 2)
        self.assertFalse((case / "run").exists())

    def test_nonfinite_budget_and_unsafe_retry_refused(self):
        spec = plan()
        spec["max_wall_seconds"] = float("nan")
        case = self.case(spec)
        self.assertEqual(invoke(case, "nan").returncode, 2)
        spec = plan([worker("writer", mode="echo", attempts=2)])
        spec["tasks"][0]["idempotent"] = False
        write(case / "plan.json", spec)
        self.assertEqual(invoke(case, "unsafe_retry").returncode, 2)

    def test_response_cannot_replace_retained_request_or_logs(self):
        case = self.case()
        for index, response in enumerate(["request.json", "stdout.txt", "stderr.txt", "request.json/nested.json", "stdout.txt/nested.json", "stderr.txt/nested.json"]):
            with self.subTest(response=response):
                spec = plan([worker("echo", mode="echo")])
                spec["tasks"][0]["response"] = response
                write(case / "plan.json", spec)
                result = invoke(case, f"reserved_{index}")
                self.assertEqual(result.returncode, 2)
                self.assertIn("collides", result.stdout)
                self.assertFalse((case / "run").exists())

    def test_response_requires_a_nonempty_file_path_string(self):
        case = self.case()
        for index, response in enumerate(["", ".", None, 4, [], {}]):
            with self.subTest(response=response):
                spec = plan([worker("echo", mode="echo")])
                spec["tasks"][0]["response"] = response
                write(case / "plan.json", spec)
                result = invoke(case, f"invalid_{index}")
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse((case / "run").exists())

    def test_output_symlink_ancestor_refused_without_mutation(self):
        case = self.case()
        target = self.root / "real"
        target.mkdir()
        (target / "keep.txt").write_text("keep")
        alias = self.root / "alias"
        alias.symlink_to(target, target_is_directory=True)
        argv = command(case)
        argv[argv.index("--output") + 1] = str(alias / "run")
        result = subprocess.run(argv, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 2)
        self.assertIn("symlink", result.stdout)
        result = subprocess.run([sys.executable, str(HERE / "run_demo.py"), "--output", str(alias / "demo")], capture_output=True, text=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(sorted(p.name for p in target.iterdir()), ["keep.txt"])
        self.assertEqual((target / "keep.txt").read_text(), "keep")

    def test_controller_and_demo_refuse_core_destinations(self):
        case = self.case()
        companion = HERE.parents[1]
        for index, name in enumerate(["repo", "reader_side"]):
            destination = companion / name / "oh01_forbidden_destination"
            self.assertFalse(destination.exists())
            argv = command(case)
            argv[argv.index("--output") + 1] = str(destination)
            result = subprocess.run(argv, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 2)
            result = subprocess.run([sys.executable, str(HERE / "run_demo.py"), "--output", str(destination)], capture_output=True, text=True, timeout=5)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(destination.exists())

    def test_invalid_response_is_not_completed(self):
        case = self.case()
        wrapper = self.custom("Path(a.response).write_text(json.dumps({'task_id':'wrong','status':'COMPLETED'}))\n")
        self.assertEqual(invoke(case, "run", "--worker-script", str(wrapper)).returncode, 1)
        self.assertEqual(state(case)["tasks"]["echo"]["attempts"][0]["outcome"], "INVALID_RESPONSE")

    def test_symlink_response_is_rejected(self):
        case = self.case()
        wrapper = self.custom("Path(a.response).symlink_to(Path(a.request))\n")
        self.assertEqual(invoke(case, "run", "--worker-script", str(wrapper)).returncode, 1)
        self.assertEqual(state(case)["tasks"]["echo"]["attempts"][0]["outcome"], "INVALID_RESPONSE")

    def test_output_limit_stops_worker(self):
        spec = plan()
        spec["max_output_bytes"] = 1000
        case = self.case(spec)
        wrapper = self.custom("import time\nprint('x'*10000,flush=True)\ntime.sleep(4)\n")
        self.assertEqual(invoke(case, "run", "--worker-script", str(wrapper)).returncode, 1)
        self.assertEqual(state(case)["tasks"]["policy"]["attempts"][0]["outcome"], "OUTPUT_LIMIT")

    def test_live_lock_prevents_second_coordinator(self):
        case = self.case(plan([worker("slow", mode="sleep", seconds=0.5)]))
        proc = subprocess.Popen(command(case), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            self.wait_running(case, proc)
            result = invoke(case, "second", "--resume")
            self.assertEqual(result.returncode, 2)
            self.assertIn("Another coordinator", result.stdout)
            self.assertEqual(proc.wait(timeout=5), 0)
        finally:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)

    def test_mutated_input_invalidates_running_work(self):
        case = self.case(plan([worker("slow", mode="sleep", seconds=3)]))
        proc = subprocess.Popen(command(case), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            self.wait_running(case, proc)
            path = case / "inputs/intent.md"
            path.chmod(0o644)
            path.write_text(path.read_text() + "changed during execution\n")
            self.assertEqual(proc.wait(timeout=5), 2)
            self.assertEqual(state(case)["run_status"], "INVALIDATED")
        finally:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)

    def test_interrupted_nonidempotent_work_needs_reconciliation(self):
        spec = plan([worker("writer", mode="sleep", seconds=4)])
        spec["tasks"][0]["idempotent"] = False
        case = self.case(spec)
        proc = subprocess.Popen(command(case), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            self.wait_running(case, proc)
            proc.send_signal(signal.SIGINT)
            self.assertEqual(proc.wait(timeout=5), 130)
            self.assertEqual(invoke(case, "resume", "--resume", "--retry-interrupted").returncode, 3)
            self.assertEqual(state(case)["run_status"], "NEEDS_RECONCILIATION")
            self.assertEqual(len(state(case)["tasks"]["writer"]["attempts"]), 1)
        finally:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
