"""Offline launcher checks using inert children, never model weights or networking."""
from pathlib import Path
import json
import hashlib
import os
import platform
import signal
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
LAUNCHERS = ("run_local_model.py", "run_local_model_d8.py")


class NativeRuntimeTests(unittest.TestCase):
    def test_explicit_native_binary_and_gpu_layers_are_recorded(self):
        for name in LAUNCHERS:
            with self.subTest(launcher=name), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                original = self.fixture(root)
                binary = root / "native-server"
                original.rename(binary)
                binary.write_text(f"#!{sys.executable}\nprint('INERT_EXIT')\n")
                result = subprocess.run(self.command(name, root) + [
                    "--server-binary", str(binary), "--n-gpu-layers", "99"],
                    capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                receipt = json.loads((root / "evidence/FINISH.json").read_text())
                self.assertEqual(receipt["argv"][0], str(binary.resolve()))
                offset = receipt["argv"].index("--n-gpu-layers")
                self.assertEqual(receipt["argv"][offset + 1], "99")
                self.assertEqual(receipt["server_identity"]["sha256"],
                                 hashlib.sha256(binary.read_bytes()).hexdigest())
                self.assertTrue(receipt["host"]["system"])
                self.assertTrue(receipt["host"]["machine"])
                darwin = platform.system() == "Darwin"
                self.assertEqual(receipt["child_max_rss_raw_unit"], "bytes" if darwin else "KiB")
                self.assertEqual(receipt["child_max_rss_kib"],
                                 receipt["child_max_rss_raw"] / (1024 if darwin else 1))

    def test_negative_gpu_layers_refused_before_evidence(self):
        for name in LAUNCHERS:
            with self.subTest(launcher=name), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                self.fixture(root)
                result = subprocess.run(self.command(name, root) + ["--n-gpu-layers", "-1"],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 2)
                self.assertIn("--n-gpu-layers must be nonnegative", result.stderr)
                self.assertFalse((root / "evidence").exists())

    def command(self, name, root):
        return [sys.executable, "-B", str(ROOT / "practice/native_client" / name),
                "--runtime-root", str(root), "--evidence", str(root / "evidence"),
                "--shutdown-grace-seconds", "0.2"]

    def fixture(self, root, ignore=False):
        binary = root / "llama_cpp/llama-b11799/llama-server"
        binary.parent.mkdir(parents=True)
        binary.write_text(
            f"#!{sys.executable}\nimport signal, time, sys\n"
            + ("signal.signal(signal.SIGTERM, signal.SIG_IGN)\n" if ignore else
               "signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))\n")
            + "print('INERT_READY_NO_MODEL_OR_NETWORK', flush=True)\n"
            + "while True: time.sleep(0.02)\n")
        binary.chmod(0o755)
        model = root / "downloads/Qwen3-4B-Q4_K_M.gguf"
        model.parent.mkdir()
        model.write_bytes(b"INERT PLACEHOLDER; NOT MODEL WEIGHTS\n")
        return binary

    def test_missing_or_nonexecutable_runtime_refused_before_evidence(self):
        for name in LAUNCHERS:
            for state in ("absent", "not_executable", "model_absent"):
                with self.subTest(launcher=name, state=state), tempfile.TemporaryDirectory() as td:
                    root = Path(td)
                    if state != "absent":
                        binary = self.fixture(root)
                        if state == "not_executable":
                            binary.chmod(0o644)
                        else:
                            (root / "downloads/Qwen3-4B-Q4_K_M.gguf").unlink()
                    result = subprocess.run(self.command(name, root), capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertFalse((root / "evidence").exists())

    def test_inert_children_stop_and_retain_actual_exit(self):
        for name in LAUNCHERS:
            for ignore in (False, True):
                with self.subTest(launcher=name, ignores_term=ignore), tempfile.TemporaryDirectory() as td:
                    root = Path(td)
                    self.fixture(root, ignore)
                    proc = subprocess.Popen(self.command(name, root), stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, start_new_session=True)
                    try:
                        deadline = time.monotonic() + 5
                        log = root / "evidence/stdout.txt"
                        while time.monotonic() < deadline:
                            if log.exists() and "INERT_READY" in log.read_text():
                                break
                            if proc.poll() is not None:
                                self.fail("launcher exited before child readiness")
                            time.sleep(0.02)
                        else:
                            self.fail("inert child did not become ready")
                        proc.send_signal(signal.SIGTERM)
                        stdout, stderr = proc.communicate(timeout=5)
                        self.assertEqual(proc.returncode, 137 if ignore else 0, stderr)
                        finish = json.loads((root / "evidence/FINISH.json").read_text())
                        offset = finish["argv"].index("--n-gpu-layers")
                        self.assertEqual(finish["argv"][offset + 1], "0")
                        self.assertEqual(finish["exit_code"], -9 if ignore else 0)
                        kills = [event for event in finish["shutdown_events"] if event["action"] == "SIGKILL_SENT"]
                        self.assertEqual(len(kills), int(ignore))
                        if ignore:
                            self.assertGreaterEqual(kills[0]["seconds_after_first_stop_request"], 0.2)
                    finally:
                        if proc.poll() is None:
                            os.killpg(proc.pid, signal.SIGKILL)
                        proc.communicate(timeout=5)


if __name__ == "__main__":
    unittest.main()
