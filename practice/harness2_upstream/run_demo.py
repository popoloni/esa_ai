#!/usr/bin/env python3
"""Run the pinned, unmodified Harness2 deterministic demo and inspect its outputs."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
VENDOR = HERE / 'vendor'
COMPANION = HERE.parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_source() -> dict:
    record = json.loads((HERE / 'UPSTREAM_SOURCE.json').read_text())
    expected = record['files']
    actual = {}
    for path in VENDOR.rglob('*'):
        if path.is_symlink():
            raise ValueError('Symlink in pinned upstream source: ' + str(path))
        if path.is_file():
            actual[path.relative_to(VENDOR).as_posix()] = sha(path)
    if actual != expected:
        raise ValueError('Pinned upstream source differs from UPSTREAM_SOURCE.json')
    return record


def new_output(path: Path) -> Path:
    target = Path(os.path.abspath(path.expanduser()))
    for part in (target, *target.parents):
        if part.is_symlink():
            raise ValueError('Choose an output path without symlink components')
    if target.exists():
        raise ValueError('Choose a NEW output directory; existing evidence is retained')
    for protected in (VENDOR, COMPANION / 'repo', COMPANION / 'reader_side'):
        if target.is_relative_to(protected):
            raise ValueError('Output cannot be placed inside protected source')
    target.mkdir(parents=True, exist_ok=False)
    return target


def inspect_outputs(root: Path, k: int, modes: list[str]) -> list[dict]:
    rows = []
    for mode in modes:
        for task in ['ledger-1', 'ledger-2']:
            source = root / 'sources' / task / 'ledger.csv'
            with source.open() as stream:
                amounts = [Decimal(row['amount']) for row in csv.DictReader(stream)]
            expected = 'Total: ' + format(sum(amounts, Decimal(0)), '.2f')
            selection_path = root / 'runs' / f'demo-oc-{mode}{k}' / task / 'selection' / f'{mode}{k}' / 'selection.json'
            selection = json.loads(selection_path.read_text())
            selected = Path(selection['chosen_run_dir']).resolve()
            if not selected.is_relative_to(root.resolve()):
                raise ValueError('Selected run points outside this observation')
            base = root / 'executions' / f'demo-oc-agg{k}' / task / 'base1' / 'answer.txt'
            # The schedule shares base executions across modes. In a sequential-only
            # invocation their actual path is recorded in that task's summary.
            summary = root / 'runs' / f'demo-oc-{modes[0]}{k}' / task / 'summary.json'
            if not base.is_file():
                summary_data = json.loads(summary.read_text())
                base_dir = Path(summary_data['base'][0]['run_dir']).resolve()
                if not base_dir.is_relative_to(root.resolve()):
                    raise ValueError('Base run points outside this observation')
                base = base_dir / 'answer.txt'
            observed = (selected / 'answer.txt').read_text().strip()
            baseline = base.read_text().strip()
            rows.append({'task': task, 'mode': mode, 'expected': expected,
                         'baseline': baseline, 'selected': observed,
                         'baseline_correct': baseline == expected,
                         'selected_correct': observed == expected,
                         'selection_ok': selection.get('ok') is True,
                         'selection': selection_path.relative_to(root).as_posix(),
                         'selected_answer': (selected / 'answer.txt').relative_to(root).as_posix()})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--k', type=int, choices=range(1, 5), default=2)
    parser.add_argument('--mode', choices=['parallel', 'sequential', 'both'], default='both')
    args = parser.parse_args()
    if not (3, 12) <= sys.version_info[:2] < (3, 14):
        parser.error('Pinned upstream package declares Python 3.12 or 3.13; use that interpreter')
    try:
        upstream = verify_source()
        output = new_output(args.output)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    modes = ['agg', 'seq'] if args.mode == 'both' else ['agg' if args.mode == 'parallel' else 'seq']
    run = output / 'run'
    bootstrap = 'import sys; sys.path.insert(0, sys.argv.pop(1)); from harness2.cli.demo import main; raise SystemExit(main())'
    argv = [sys.executable, '-I', '-B', '-c', bootstrap, str(VENDOR), '--output', str(run), '--k', str(args.k), '--mode', args.mode]
    # The deterministic adapter needs neither model configuration nor credentials.
    environment = {key: value for key, value in os.environ.items()
                   if key in {'PATH', 'LANG', 'LC_ALL', 'TMPDIR', 'SYSTEMROOT'}}
    report = {'schema': 'esa-harness2-upstream-demo/v1',
              'started_at_utc': datetime.now(timezone.utc).isoformat(),
              'upstream_commit': upstream['commit'], 'upstream_version': upstream['version'],
              'python': platform.python_version(), 'platform': platform.platform(),
              'argv': argv, 'mode': args.mode, 'k': args.k, 'model_calls': 0,
              'editor_kind': 'UPSTREAM_SCRIPTED_DETERMINISTIC',
              'source_files_verified': len(upstream['files']),
              'wrapper_sha256': sha(Path(__file__).resolve()),
              'source_record_sha256': sha(HERE / 'UPSTREAM_SOURCE.json'),
              'meaning': 'Execution of pinned upstream adaptation machinery with scripted edits, source-arithmetic selection and real Python subprocesses. Not a model-backed benchmark or an independent replication of paper effect sizes.'}
    started = time.perf_counter()
    try:
        with (output / 'stdout.txt').open('w') as stdout, (output / 'stderr.txt').open('w') as stderr:
            process = subprocess.run(argv, cwd=VENDOR, env=environment, stdout=stdout,
                                     stderr=stderr, timeout=60, check=False)
        report['exit_code'] = process.returncode
        if process.returncode != 0:
            raise RuntimeError('Upstream demo returned a failure; inspect stdout.txt and stderr.txt')
        report['upstream_report'] = json.loads((run / 'demo.json').read_text())
        report['independent_output_checks'] = inspect_outputs(run, args.k, modes)
        report['source_unchanged'] = verify_source() == upstream
        report['status'] = 'PASS' if (report['upstream_report']['failed'] == 0
            and len(report['independent_output_checks']) == 2 * len(modes)
            and all(row['selected_correct'] and row['selection_ok'] for row in report['independent_output_checks'])
            and report['source_unchanged']) else 'FAIL'
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired) as exc:
        report.update(status='FAIL', error=f'{type(exc).__name__}: {exc}')
    report['elapsed_seconds'] = time.perf_counter() - started
    report['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    (output / 'REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'] + ': ' + str(output / 'REPORT.json'))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
