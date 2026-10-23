#!/usr/bin/env python3
"""Observe this exact startup; no model, completion, embedding or tokenizer call."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import time
import urllib.request


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(__file__).resolve().parent
    root = out.parent
    sample = out / 'sample_01'
    sample.mkdir(exist_ok=False)
    start_path = root / 'lifecycle_04/START.json'
    start = json.loads(start_path.read_text())
    pid = start['server_pid']
    proc = Path('/proc') / str(pid)
    actual = [v.decode() for v in (proc / 'cmdline').read_bytes().rstrip(b'\0').split(b'\0')]
    if actual != start['argv']:
        raise RuntimeError('Owned argv does not match START')
    record = {'schema': 'esa-d8-native-startup-preflight/v1',
              'observed_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'server_pid': pid, 'launcher_pid': start['launcher_pid'],
              'start_sha256': sha(start_path), 'identity_argv_match': True,
              'argv': actual, 'controller_sha256': sha(Path(__file__)),
              'scope': 'Health/props GET and read-only owned-process/resource observation only; no inference or tokenizer call.'}
    for name in ['status', 'stat', 'cgroup', 'maps', 'smaps_rollup']:
        (sample / ('process_' + name + '.txt')).write_text((proc / name).read_text())
    cgroup = {}
    for name in ['cpu.max', 'cpuset.cpus.effective', 'cpu.stat', 'memory.max', 'memory.current',
                 'memory.stat', 'memory.events', 'memory.swap.max', 'memory.pressure']:
        try:
            value = (Path('/sys/fs/cgroup') / name).read_text()
            cgroup[name] = value
            (sample / ('cgroup_' + name.replace('.', '_') + '.txt')).write_text(value)
        except FileNotFoundError:
            record.setdefault('unavailable_optional_files', []).append(name)
    record['cgroup_files'] = cgroup
    for endpoint in ['health', 'props']:
        began = time.monotonic()
        with urllib.request.urlopen('http://127.0.0.1:18080/' + endpoint, timeout=10) as response:
            data = response.read()
            code = response.status
        (sample / (endpoint + '.json')).write_bytes(data)
        record[endpoint] = {'http_status': code, 'bytes': len(data),
                            'sha256': hashlib.sha256(data).hexdigest(), 'seconds': time.monotonic() - began}
    memory = {k: int(v) for k, v in (l.split() for l in cgroup['memory.stat'].splitlines())}
    fields = {}
    for line in (sample / 'process_status.txt').read_text().splitlines():
        key, _, value = line.partition(':')
        fields[key] = value.strip()
    paths = sorted({l.split()[-1] for l in (sample / 'process_maps.txt').read_text().splitlines()
                    if len(l.split()) >= 6 and l.split()[-1].startswith('/')})
    mapped_files = [{'path': f, 'full_size_bytes': Path(f).stat().st_size} for f in paths if Path(f).is_file()]
    full = sum(f['full_size_bytes'] for f in mapped_files)
    protected = memory.get('anon', 0) + memory.get('kernel', 0) + memory.get('shmem', 0) + full
    limit = int(cgroup['memory.max'])
    record['memory_estimate'] = {
        'formula': 'cgroup anon + all cgroup kernel + cgroup shmem + full size of every unique mapped regular file',
        'anon_bytes': memory.get('anon', 0), 'kernel_bytes': memory.get('kernel', 0),
        'shmem_bytes': memory.get('shmem', 0), 'mapped_full_file_bytes': full, 'mapped_files': mapped_files,
        'protected_estimate_bytes': protected, 'limit_bytes': limit, 'headroom_bytes': limit - protected,
        'headroom_gib': (limit - protected) / 1024**3, 'minimum_startup_headroom_bytes': 768 * 1024**2,
        'server_rss_kib': int(fields['VmRSS'].split()[0]),
        'limit': 'Conservative startup estimate; unrelated file cache is reclaimable. Does not guarantee future peak or set a runtime abort threshold.'}
    props = json.loads((sample / 'props.json').read_text())
    baseline = json.loads((root / 'startup_preflight_03/REVIEW.json').read_text())['oom_events_after']
    current = {k: int(v) for k, v in (l.split() for l in cgroup['memory.events'].splitlines())}
    log = (root / 'lifecycle_04/stderr.txt').read_text()
    (sample / 'startup_log_observed.txt').write_text(log)
    checks = {
        'owned_argv_identity': True, 'health_http_200': record['health']['http_status'] == 200,
        'props_http_200': record['props']['http_status'] == 200,
        'context_24576': props['default_generation_settings']['n_ctx'] == 24576,
        'single_slot': props['total_slots'] == 1, 'expected_build': props['build_info'] == 'b11799-0756e83fc',
        'actual_zen4_backend': any(f.endswith('libggml-cpu-zen4.so') for f in paths),
        'f16_k_and_v_logged': 'K (f16)' in log and 'V (f16)' in log,
        'no_cpu_repack_allocation_logged': 'CPU_REPACK' not in log,
        'headroom_at_least_768_mib': limit - protected >= 768 * 1024**2,
        'no_new_oom': current['oom'] == baseline['oom'],
        'no_new_oom_kill': current['oom_kill'] == baseline['oom_kill'],
    }
    (sample / 'OBSERVATION.json').write_text(json.dumps(record, indent=2) + '\n')
    review = {'schema': 'esa-d8-native-startup-review/v1',
              'reviewed_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'status': 'PASS_STARTUP_ONLY' if all(checks.values()) else 'FAIL_OR_REVIEW_REQUIRED',
              'checks': checks, 'observation_sha256': sha(sample / 'OBSERVATION.json'),
              'memory_estimate': record['memory_estimate'], 'oom_events_before': baseline, 'oom_events_after': current,
              'server_pid': pid, 'launcher_pid': start['launcher_pid'],
              'lifetime': {'started_at_utc': start['started_at_utc'], 'fixed_maximum_seconds': start['maximum_runtime_seconds'],
                           'native_prospective_outer_seconds': 5400, 'shutdown_grace_seconds': 30},
              'source_budget': {'candidate': '03', 'complete_prospective_tokens_including_reserves': 23265,
                               'context_tokens': 24576, 'remaining_margin_tokens': 1311,
                               'limit': 'Sibling/root owns exact new native input binding and generation release.'},
              'output_cap_disclosure': {'argv_requested_n_predict': 3072,
                                       'props_max_tokens': props['default_generation_settings']['params']['max_tokens'],
                                       'props_n_predict': props['default_generation_settings']['params']['n_predict'],
                                       'independent_server_cap_claim': False},
              'temperature_limit': 'No task sampler exists yet in this new startup. Candidate native model capability may enable agent intent0.2; actual sampler must be observed on the real request.',
              'scope': record['scope'], 'generation_authorization': 'Root release required; no native client launched by this preflight.'}
    (out / 'REVIEW.json').write_text(json.dumps(review, indent=2) + '\n')
    entries = []
    for f in sorted(out.rglob('*')):
        if f.is_file() and f != out / 'MANIFEST.json':
            entries.append({'path': f.relative_to(out).as_posix(), 'bytes': f.stat().st_size, 'sha256': sha(f)})
    (out / 'MANIFEST.json').write_text(json.dumps({'schema': 'esa-d8-native-startup-preflight-manifest/v1',
                                                  'file_count': len(entries), 'files': entries}, indent=2) + '\n')
    print(json.dumps({'status': review['status'], 'checks': checks, 'server_pid': pid, 'launcher_pid': start['launcher_pid'],
                      'headroom_bytes': limit - protected, 'headroom_gib': (limit - protected) / 1024**3,
                      'rss_kib': record['memory_estimate']['server_rss_kib'],
                      'review_sha256': sha(out / 'REVIEW.json'), 'manifest_sha256': sha(out / 'MANIFEST.json'),
                      'manifest_file_count': len(entries)}, indent=2))


if __name__ == '__main__':
    main()
