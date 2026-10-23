#!/usr/bin/env python3
"""Verify the new lifetime guard with an inert child; never load model weights."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import signal
import subprocess
import sys
import time


def main():
    prep = Path(__file__).resolve().parent
    runtime = Path('/workspace/scratch/72d789d25fef/runtime_d8/launcher_controlled_probe_01')
    runtime.mkdir(parents=True, exist_ok=False)
    fixture = runtime / 'llama_cpp/llama-b11799/llama-server'
    fixture.parent.mkdir(parents=True)
    fixture.write_text('#!/usr/bin/env python3\nimport signal,time\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\nprint("INERT_FIXTURE_READY_NO_MODEL_OR_NETWORK", flush=True)\nwhile True: time.sleep(0.05)\n')
    fixture.chmod(0o755)
    dummy = runtime / 'downloads/Qwen3-4B-Q4_K_M.gguf'
    dummy.parent.mkdir()
    dummy.write_bytes(b'INERT PLACEHOLDER; NOT GGUF OR MODEL WEIGHTS\n')
    evidence = prep / 'controlled_probe_evidence'
    argv = [sys.executable, str(prep / 'run_local_model_d8.py'), '--runtime-root', str(runtime),
            '--evidence', str(evidence), '--max-runtime-seconds', '0.8',
            '--shutdown-grace-seconds', '0.4']
    began = dt.datetime.now(dt.timezone.utc).isoformat()
    start = time.monotonic()
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    timed_out = False
    try:
        out, err = process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGKILL)
        out, err = process.communicate(timeout=5)
    elapsed = time.monotonic() - start
    (prep / 'CONTROLLED_PROBE.stdout.txt').write_bytes(out)
    (prep / 'CONTROLLED_PROBE.stderr.txt').write_bytes(err)
    (prep / 'INERT_FIXTURE.py').write_bytes(fixture.read_bytes())
    finish = json.loads((evidence / 'FINISH.json').read_text()) if (evidence / 'FINISH.json').is_file() else {}
    child_stdout = (evidence / 'stdout.txt').read_text() if (evidence / 'stdout.txt').is_file() else ''
    kill_events = [e for e in finish.get('shutdown_events', []) if e['action'] == 'SIGKILL_SENT']
    checks = {
        'controller_did_not_timeout': not timed_out,
        'inert_fixture_ready': 'INERT_FIXTURE_READY_NO_MODEL_OR_NETWORK' in child_stdout,
        'automatic_lifetime_stop': finish.get('automatic_stop_reason') == 'MAXIMUM_RUNTIME_REACHED',
        'exact_child_forced_exit': finish.get('exit_code') == -9 and process.returncode == 137,
        'single_kill_event': len(kill_events) == 1,
        'monotonic_grace_not_early': bool(kill_events) and kill_events[0]['seconds_after_first_stop_request'] >= 0.4,
        'bounded_elapsed': 1.2 <= elapsed < 5.0,
        'shutdown_record_retained': (evidence / 'SHUTDOWN.json').is_file(),
    }
    record = {'schema': 'esa-d8-inert-lifetime-probe/v1', 'status': 'PASS' if all(checks.values()) else 'FAIL',
              'started_at_utc': began, 'finished_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'argv': argv, 'elapsed_seconds': elapsed, 'launcher_exit_code': process.returncode,
              'checks': checks, 'fixture': {'path': str(fixture), 'sha256': hashlib.sha256(fixture.read_bytes()).hexdigest()},
              'dummy_model_sha256': hashlib.sha256(dummy.read_bytes()).hexdigest(),
              'launcher_sha256': hashlib.sha256((prep / 'run_local_model_d8.py').read_bytes()).hexdigest(),
              'scope': 'Controlled inert Python child only. No real llama executable, model weights, network, native client or inference.'}
    (prep / 'CONTROLLED_PROBE.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
