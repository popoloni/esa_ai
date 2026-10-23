#!/usr/bin/env python3
"""Read-only exact-owned-server observation; authorized metrics GET only, no model task."""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import re
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    args = parser.parse_args()
    if not re.fullmatch(r'snapshot_[0-9]{3}', args.name):
        parser.error('Use a new snapshot_NNN name')
    base = Path(__file__).resolve().parent
    server_root = base.parent
    start_path = server_root / 'lifecycle_04/START.json'
    start = json.loads(start_path.read_text())
    pid = start['server_pid']
    proc = Path('/proc') / str(pid)
    argv = [x.decode() for x in (proc / 'cmdline').read_bytes().rstrip(b'\0').split(b'\0')]
    if argv != start['argv']:
        raise RuntimeError('Owned process argv mismatch; no further inspection')
    directory = base / args.name
    directory.mkdir(exist_ok=False)
    record = {
        'schema': 'esa-d8-native-inference-observation/v1',
        'observed_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'server_pid': pid,
        'owned_argv_match': True,
        'start_sha256': hashlib.sha256(start_path.read_bytes()).hexdigest(),
        'scope': 'Read-only exact-owned-process, cgroup, existing logs and authorized metrics GET; no model/backend task request or process control.',
        'controller_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    for name in ['status', 'stat', 'maps']:
        (directory / ('process_' + name + '.txt')).write_text((proc / name).read_text())
    resources = {}
    for name in ['cpu.max', 'cpu.stat', 'memory.current', 'memory.max', 'memory.stat', 'memory.events']:
        text = (Path('/sys/fs/cgroup') / name).read_text()
        resources[name] = text
        (directory / ('cgroup_' + name.replace('.', '_') + '.txt')).write_text(text)
    log_path = server_root / 'lifecycle_04/stderr.txt'
    log = log_path.read_bytes()
    (directory / 'server_log_observed.txt').write_bytes(log)
    lines = log.decode(errors='replace').splitlines()
    progress = [line for line in lines if any(t in line for t in [
        'prompt processing', 'prompt eval time', 'eval time', 'total time',
        'new prompt', 'n_prompt_tokens', 'n_predict', 'max_tokens', 'processing task',
        'launch_slot', 'stop processing', 'release_slot', 'prompt cache', 'n_gen =', 'cancel task',
    ])]
    record['observed_log_bytes'] = len(log)
    record['observed_log_sha256'] = hashlib.sha256(log).hexdigest()
    record['request_progress_lines'] = progress[-35:]
    record['actual_output_cap_log_lines'] = [line for line in lines if 'max_tokens' in line or 'n_predict' in line][-10:]
    record['actual_sampler_observations'] = []
    for i, line in enumerate(lines):
        if 'sampler params' in line:
            block = lines[i:i + 10]
            task_line = next((x for x in block if 'processing task' in x), '')
            task_match = re.search(r'task (\d+) \|', task_line)
            temp_line = next((x for x in block if re.search(r'\btemp\s*=', x)), '')
            temp_match = re.search(r'\btemp\s*=\s*([0-9.]+)', temp_line)
            record['actual_sampler_observations'].append({'task_id': int(task_match.group(1)) if task_match else None,
                'temperature': float(temp_match.group(1)) if temp_match else None,
                'source_lines': block[:6]})
    record['actual_request_contexts'] = []
    for line in lines:
        if 'new prompt' in line:
            task_match = re.search(r'task (\d+) \|', line)
            ctx_match = re.search(r'n_ctx_slot = (\d+)', line)
            prompt_match = re.search(r'task.n_tokens = (\d+)', line)
            if ctx_match and prompt_match:
                ctx, prompt = int(ctx_match.group(1)), int(prompt_match.group(1))
                record['actual_request_contexts'].append({'task_id': int(task_match.group(1)) if task_match else None,
                    'prompt_tokens': prompt, 'context_tokens': ctx, 'remaining_after_prompt': ctx - prompt,
                    'remaining_after_declared_1536_response_reserve': ctx - prompt - 1536,
                    'source_line': line})
    record['output_cap_limit'] = 'Do not infer a native request cap from launcher argv or /props. These lines support an actual cap only if they explicitly bind that request.'
    prior_summary_path = server_root / 'inference_observation_03/OBSERVATION_SUMMARY.json'
    prior_summary = json.loads(prior_summary_path.read_text())
    older_summary_path = server_root / 'inference_observation_02/OBSERVATION_SUMMARY.json'
    older_summary = json.loads(older_summary_path.read_text())
    prior_ids = {entry['task_id'] for entry in older_summary['requests']} | {entry['task_id'] for entry in prior_summary['actual_requests']}
    record['prior_observation_sha256'] = hashlib.sha256(prior_summary_path.read_bytes()).hexdigest()
    record['older_observation_sha256'] = hashlib.sha256(older_summary_path.read_bytes()).hexdigest()
    record['prior_request_ids_excluded_from_current_summary'] = sorted(prior_ids)
    record['actual_sampler_observations'] = [x for x in record['actual_sampler_observations'] if x['task_id'] not in prior_ids]
    record['actual_request_contexts'] = [x for x in record['actual_request_contexts'] if x['task_id'] not in prior_ids]
    current_task_ids = {x['task_id'] for x in record['actual_request_contexts']}
    record['actual_generation_progress_lines'] = [line for line in lines if 'n_gen' in line and any(re.search(r'task\s+' + str(task) + r'\s*\|', line) for task in current_task_ids)]
    record['actual_cancel_lines'] = [line for line in lines if 'cancel task' in line and any(re.search(r'id_task = ' + str(task) + r'\b', line) for task in current_task_ids)]
    current_contexts = record['actual_request_contexts']
    first_prompt = current_contexts[0]['prompt_tokens'] if current_contexts else None
    record['continuation_remaining_after_1664_history_and_1536_response'] = []
    for item in current_contexts:
        growth = max(0, item['prompt_tokens'] - first_prompt)
        history_left = max(0, 1664 - growth)
        record['continuation_remaining_after_1664_history_and_1536_response'].append({
            'task_id': item['task_id'], 'additional_prompt_occupancy_since_first': growth,
            'remaining_of_original_1664_history_reserve': history_left,
            'original_history_reserve_exceeded': growth > 1664,
            'tokens_after_remaining_history_and_1536_output': item['context_tokens'] - item['prompt_tokens'] - history_left - 1536})
    try:
        with urllib.request.urlopen('http://127.0.0.1:18080/metrics', timeout=10) as response:
            metrics_data = response.read()
            metrics_status = response.status
        (directory / 'server_metrics.prom').write_bytes(metrics_data)
        values = {line.split()[0]: float(line.split()[1]) for line in metrics_data.decode().splitlines()
                  if line and not line.startswith('#')}
        baseline_path = server_root / 'inference_observation_03/snapshot_010/server_metrics.prom'
        baseline_values = {line.split()[0]: float(line.split()[1]) for line in baseline_path.read_text().splitlines()
                           if line and not line.startswith('#')}
        names = ['prompt_tokens_total', 'prompt_tokens_cached_total', 'prompt_seconds_total',
                 'tokens_predicted_total', 'tokens_predicted_seconds_total', 'n_decode_total']
        delta = {name: values['llamacpp:' + name] - baseline_values['llamacpp:' + name] for name in names}
        record['metrics'] = {'http_status': metrics_status, 'raw_sha256': hashlib.sha256(metrics_data).hexdigest(),
            'baseline_sha256': hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
            'values': values, 'continuation_delta': delta,
            'limit': 'Counters can update at different phases; no completed output count or tool write is inferred from decode-call growth.'}
    except Exception as exc:
        record['metrics'] = {'error_type': type(exc).__name__, 'message': str(exc)}
    memory = {k: int(v) for k, v in (line.split() for line in resources['memory.stat'].splitlines())}
    fields = {}
    for line in (directory / 'process_status.txt').read_text().splitlines():
        key, _, value = line.partition(':')
        fields[key] = value.strip()
    paths = sorted({line.split()[-1] for line in (directory / 'process_maps.txt').read_text().splitlines()
                    if len(line.split()) >= 6 and line.split()[-1].startswith('/')})
    mapped_bytes = sum(Path(f).stat().st_size for f in paths if Path(f).is_file())
    limit = int(resources['memory.max'])
    protected = memory.get('anon', 0) + memory.get('kernel', 0) + mapped_bytes + memory.get('shmem', 0)
    events = {k: int(v) for k, v in (line.split() for line in resources['memory.events'].splitlines())}
    baseline = json.loads((server_root / 'startup_preflight_04/REVIEW.json').read_text())['oom_events_after']
    record['memory'] = {
        'server_rss_kib': int(fields['VmRSS'].split()[0]),
        'cgroup_current_bytes': int(resources['memory.current']),
        'anon_bytes': memory.get('anon', 0), 'kernel_bytes': memory.get('kernel', 0),
        'mapped_full_file_bytes': mapped_bytes, 'protected_estimate_bytes': protected,
        'limit_bytes': limit, 'headroom_bytes': limit - protected,
        'headroom_gib': (limit - protected) / 1024**3,
        'estimate_limit': 'Conservative mapped-full-file + cgroup anon/kernel/shmem estimate; no guarantee of future peak.',
    }
    record['oom_events'] = events
    record['new_oom'] = events['oom'] - baseline['oom']
    record['new_oom_kill'] = events['oom_kill'] - baseline['oom_kill']
    record['attention_required'] = record['new_oom'] > 0 or record['new_oom_kill'] > 0 or limit - protected < 384 * 1024**2
    attempt = server_root.parent / 'native_sdd_01/attempt_04'
    record['attempt_receipt_candidates'] = [str(f) for f in attempt.glob('*') if f.is_file() and any(word in f.name.upper() for word in ['RECEIPT', 'FINISH'])] if attempt.exists() else []
    (directory / 'OBSERVATION.json').write_text(json.dumps(record, indent=2) + '\n')
    manifest = []
    for f in sorted(directory.iterdir()):
        if f.is_file():
            data = f.read_bytes()
            manifest.append({'path': f.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    (directory / 'MANIFEST.json').write_text(json.dumps({'schema': 'esa-immutable-observation-manifest/v1', 'files': manifest}, indent=2) + '\n')
    print(json.dumps({'snapshot': args.name, 'observed_at_utc': record['observed_at_utc'],
                      'memory': record['memory'], 'new_oom': record['new_oom'], 'new_oom_kill': record['new_oom_kill'],
                      'attention_required': record['attention_required'], 'progress': progress[-12:],
                      'actual_output_cap_log_lines': record['actual_output_cap_log_lines'],
                      'actual_samplers': [{'task_id': x['task_id'], 'temperature': x['temperature']} for x in record['actual_sampler_observations']],
                      'metrics': record['metrics'],
                      'actual_request_contexts': record['actual_request_contexts'][-3:],
                      'continuation_first_request_reserve': record['continuation_remaining_after_1664_history_and_1536_response'],
                      'attempt_receipt_candidates': record['attempt_receipt_candidates']}, indent=2))


if __name__ == '__main__':
    main()
