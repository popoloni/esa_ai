"""Independent controlled process probe. No model, real server, or network."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time


ROOT = Path('/workspace/scratch/72d789d25fef/work/Engineering_Software_with_Agentic_AI_20261021_d5')
HERE = Path(__file__).resolve().parent
LAUNCHER = ROOT / 'companion/practice/native_client/run_local_model.py'
RUNTIME = Path('/workspace/scratch/72d789d25fef/runtime_d7/shutdown_controlled_probe_02')


def now():
    return datetime.now(timezone.utc).isoformat()


def identity(path):
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


COOPERATIVE = '''#!/usr/bin/env python3
"""Explicitly inert fixture: print identity, wait, and exit on SIGTERM."""
import json, os, signal, sys, time
def stop(signum, frame):
    print(json.dumps({'fixture': 'cooperative', 'received_signal': signum}), flush=True)
    sys.exit(0)
signal.signal(signal.SIGTERM, stop)
print(json.dumps({'ready': True, 'fixture': 'cooperative', 'pid': os.getpid(), 'argv': sys.argv, 'model_loaded': False, 'network_opened': False}), flush=True)
while True:
    time.sleep(0.05)
'''

IGNORING = '''#!/usr/bin/env python3
"""Explicitly inert fixture: ignore SIGTERM and wait for exact-child cleanup."""
import json, os, signal, sys, time
signal.signal(signal.SIGTERM, signal.SIG_IGN)
print(json.dumps({'ready': True, 'fixture': 'ignoring', 'pid': os.getpid(), 'argv': sys.argv, 'model_loaded': False, 'network_opened': False}), flush=True)
while True:
    time.sleep(0.05)
'''


def one_case(name, fixture, repeat):
    case = HERE / name
    case.mkdir()
    fixture_path = case / 'INERT_FIXTURE.py'
    fixture_path.write_text(fixture)
    runtime = RUNTIME / name
    binary = runtime / 'llama_cpp/llama-b11799/llama-server'
    binary.parent.mkdir(parents=True)
    shutil.copyfile(fixture_path, binary)
    binary.chmod(0o755)
    evidence = case / 'lifecycle'
    grace = 1.2
    argv = [sys.executable, str(LAUNCHER), '--runtime-root', str(runtime),
            '--evidence', str(evidence), '--shutdown-grace-seconds', str(grace)]
    result = {'case': name, 'started_at_utc': now(), 'argv': argv,
              'cwd': str(ROOT), 'fixture': identity(fixture_path),
              'runtime_fixture': identity(binary), 'grace_seconds': grace,
              'no_real_server_model_or_network': True, 'controller_signals': []}
    (case / 'REQUEST.json').write_text(json.dumps(result, indent=2) + '\n')
    start = time.monotonic()
    with (case / 'launcher_stdout.txt').open('x') as out, (case / 'launcher_stderr.txt').open('x') as err:
        proc = subprocess.Popen(argv, cwd=ROOT, stdout=out, stderr=err)
        result['launcher_pid'] = proc.pid
        child = None
        try:
            ready_deadline = time.monotonic() + 5
            while time.monotonic() < ready_deadline:
                if proc.poll() is not None:
                    raise RuntimeError('Launcher exited before fixture readiness')
                output = evidence / 'stdout.txt'
                if (evidence / 'START.json').exists() and output.exists() and '"ready": true' in output.read_text():
                    break
                time.sleep(0.02)
            else:
                raise RuntimeError('Fixture did not become ready within five seconds')
            start_record = json.loads((evidence / 'START.json').read_text())
            child = start_record['server_pid']
            result['child_pid'] = child
            result['launcher_cmdline_before_signal'] = Path(f'/proc/{proc.pid}/cmdline').read_bytes().replace(b'\0', b' ').decode()
            result['child_cmdline_before_signal'] = Path(f'/proc/{child}/cmdline').read_bytes().replace(b'\0', b' ').decode()
            assert str(binary) in result['child_cmdline_before_signal']
            first = time.monotonic()
            schedule = [(0.0, signal.SIGTERM)]
            if repeat:
                schedule += [(0.45, signal.SIGINT), (0.90, signal.SIGTERM)]
            for offset, signum in schedule:
                remaining = first + offset - time.monotonic()
                if remaining > 0:
                    time.sleep(remaining)
                proc.send_signal(signum)
                result['controller_signals'].append({'signal': signum.value, 'at_utc': now(), 'seconds_after_first_send': time.monotonic() - first})
            code = proc.wait(timeout=6)
            result['launcher_exit_code'] = code
            result['seconds_from_first_signal_to_reap'] = time.monotonic() - first
            finish = json.loads((evidence / 'FINISH.json').read_text())
            result['finish'] = finish
            result['shutdown_event_file_exists'] = (evidence / 'SHUTDOWN.json').exists()
            result['child_still_exists_after_reap'] = Path(f'/proc/{child}').exists()
            kills = [e for e in finish.get('shutdown_events', []) if e['action'] == 'SIGKILL_SENT']
            if repeat:
                checks = {
                    'launcher_returned_137': code == 137,
                    'child_exit_minus_9': finish['exit_code'] == -9,
                    'forced_disposition': finish['shutdown_result'] == 'FORCED_EXIT_AFTER_GRACE',
                    'three_stop_signals_recorded': len(finish.get('termination_signals', [])) == 3,
                    'exactly_one_direct_child_kill': len(kills) == 1 and kills[0]['server_pid'] == child,
                    'first_deadline_not_reset': len(kills) == 1 and grace <= kills[0]['seconds_after_first_stop_request'] < 1.7,
                    'shutdown_event_file_retained': result['shutdown_event_file_exists'],
                }
            else:
                checks = {
                    'launcher_returned_zero': code == 0,
                    'child_exit_zero': finish['exit_code'] == 0,
                    'cooperative_disposition': finish['shutdown_result'] == 'EXIT_AFTER_STOP_REQUEST',
                    'no_force_signal': not kills,
                    'one_stop_signal_recorded': len(finish.get('termination_signals', [])) == 1,
                    'completed_before_grace': result['seconds_from_first_signal_to_reap'] < grace,
                }
            checks['no_child_left_running'] = not result['child_still_exists_after_reap']
            checks['launcher_identity_matches'] = finish['launcher_identity']['sha256'] == identity(LAUNCHER)['sha256']
            result['checks'] = checks
            result['status'] = 'PASS' if all(checks.values()) else 'FAIL'
        except Exception as exc:
            result.update(status='ERROR', error=type(exc).__name__, message=str(exc))
        finally:
            if proc.poll() is None:
                result['controller_cleanup_needed'] = True
                if child is not None:
                    path = Path(f'/proc/{child}/cmdline')
                    if path.exists() and str(binary).encode() in path.read_bytes():
                        os.kill(child, signal.SIGKILL)
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2)
            result['finished_at_utc'] = now()
            result['total_probe_wall_seconds'] = time.monotonic() - start
    (case / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    assert not (HERE / 'REPORT.json').exists()
    RUNTIME.mkdir(exist_ok=False)
    helper_before = identity(LAUNCHER)
    result = {
        'schema': 'esa-controlled-native-shutdown-probe/v1',
        'started_at_utc': now(),
        'scope': 'Independent process-control probe of the future launcher with explicitly inert subprocess fixtures. No actual llama.cpp executable, GGUF model, native coding client, network operation, or model request is used.',
        'original_observation_preserved': 'The earlier server03 forced cleanup and client TIMEOUT are not rewritten by this probe.',
        'launcher': helper_before, 'probe': identity(Path(__file__)),
        'cases': [one_case('cooperative', COOPERATIVE, False), one_case('ignoring_repeated_signals', IGNORING, True)],
    }
    result['helper_unchanged_during_probe'] = identity(LAUNCHER) == helper_before
    result['status'] = 'PASS' if result['helper_unchanged_during_probe'] and all(c['status'] == 'PASS' for c in result['cases']) else 'FAIL'
    result['finished_at_utc'] = now()
    result['timing_limit'] = 'Short local observations under this scheduler, not a hard real-time guarantee. The helper documents that scheduling and I/O can add delay beyond the monotonic grace.'
    (HERE / 'REPORT.json').write_text(json.dumps(result, indent=2) + '\n')
    inventory = {}
    for path in sorted(HERE.rglob('*')):
        if path.is_file() and path.name != 'PROBE_MANIFEST.json':
            inventory[str(path.relative_to(HERE))] = identity(path)
    (HERE / 'PROBE_MANIFEST.json').write_text(json.dumps({'schema': 'esa-controlled-probe-manifest/v1', 'created_at_utc': now(), 'files': inventory, 'manifest_excluded_from_own_inventory': True}, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'launcher_sha256': helper_before['sha256'], 'cases': [{'case': c['case'], 'status': c['status'], 'checks': c.get('checks'), 'seconds_to_reap': c.get('seconds_from_first_signal_to_reap'), 'kill_events': [e for e in c.get('finish', {}).get('shutdown_events', []) if e['action'] == 'SIGKILL_SENT']} for c in result['cases']]}, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
