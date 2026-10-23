#!/usr/bin/env python3
"""Create a fresh installed Spec Kit scaffold and retain its exact fixed inputs.

This preparation invokes the pinned framework only. It never invokes a model,
creates a feature output, or changes the retained d7 project/evidence.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

AUTHOR_ROOT = Path('/workspace/scratch/72d789d25fef/work/Engineering_Software_with_Agentic_AI_20261021_d5')
RUNTIME = Path('/workspace/scratch/72d789d25fef/runtime_d8')
PINNED_RUNTIME = Path('/workspace/scratch/72d789d25fef/runtime_d7')
EVIDENCE = AUTHOR_ROOT / 'revision_d8/evidence/native_sdd_01/preparation'
PROJECT = RUNTIME / 'native_sdd_01'


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    with path.open('x', encoding='utf-8') as out:
        json.dump(value, out, indent=2)
        out.write('\n')


def inventory(root):
    return {p.relative_to(root).as_posix(): {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
            for p in sorted(root.rglob('*')) if p.is_file()}


def main():
    if PROJECT.exists():
        raise SystemExit('Fresh scaffold path must not exist; preserve any prior attempt.')
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    env_keys = ('PATH', 'LANG', 'TZ', 'HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY',
                'SSL_CERT_FILE', 'REQUESTS_CA_BUNDLE')
    env = {key: os.environ[key] for key in env_keys if key in os.environ}
    env.update({'PATH': str(PINNED_RUNTIME / 'opencode/node_modules/.bin') + ':'
                       + str(PINNED_RUNTIME / 'sdd_venv/bin') + ':' + env.get('PATH', ''),
                'LANG': 'C.UTF-8', 'TZ': 'UTC', 'CI': '1', 'DO_NOT_TRACK': '1',
                'PYTHONDONTWRITEBYTECODE': '1', 'GIT_CONFIG_NOSYSTEM': '1',
                'GIT_CONFIG_GLOBAL': '/dev/null'})
    argv = [str(PINNED_RUNTIME / 'sdd_venv/bin/specify'), 'init', PROJECT.name,
            '--integration', 'opencode', '--script', 'py', '--non-interactive']
    receipt = {'status': 'STARTED_INSTALLED_FRAMEWORK_SCAFFOLD_ONLY', 'started_at_utc': now(),
               'argv': argv, 'cwd': str(RUNTIME), 'env_keys': sorted(env),
               'pinned_runtime_reused_read_only': str(PINNED_RUNTIME),
               'project': str(PROJECT), 'model_call': False, 'generated_feature_outputs': False}
    write_json(EVIDENCE / 'SCAFFOLD_START.json', receipt)
    with (EVIDENCE / 'scaffold.stdout.txt').open('xb') as out, (EVIDENCE / 'scaffold.stderr.txt').open('xb') as err:
        try:
            result = subprocess.run(argv, cwd=RUNTIME, env=env, stdout=out, stderr=err, timeout=90)
            receipt['exit_code'] = result.returncode
        except subprocess.TimeoutExpired:
            receipt.update(exit_code=None, failure='TIMEOUT_90_SECONDS')
    receipt['finished_at_utc'] = now()
    receipt['status'] = 'INSTALLED_FRAMEWORK_SCAFFOLD_CREATED' if receipt.get('exit_code') == 0 else 'SCAFFOLD_FAILED'
    for name in ('scaffold.stdout.txt', 'scaffold.stderr.txt'):
        data = (EVIDENCE / name).read_bytes()
        receipt[name] = {'sha256': sha(data), 'bytes': len(data)}
    write_json(EVIDENCE / 'SCAFFOLD_FINISH.json', receipt)
    if receipt.get('exit_code') != 0:
        raise SystemExit(1)

    scaffold = inventory(PROJECT)
    reference = PINNED_RUNTIME / 'native_sdd_03'
    unchanged_commands = {}
    for name in ('speckit.specify.md', 'speckit.clarify.md'):
        new = (PROJECT / '.opencode/commands' / name).read_bytes()
        old = (reference / '.opencode/commands' / name).read_bytes()
        unchanged_commands[name] = {'d8_sha256': sha(new), 'd7_sha256': sha(old),
                                    'bytes': len(new), 'byte_identical': new == old}
        assert new == old, 'Installed command identity changed: ' + name
    assert not any((PROJECT / p).exists() for p in ('.specify/feature.json', 'specs/001-explain-treasury/spec.md',
                                                  'specs/001-explain-treasury/checklists/requirements.md'))
    shutil.copytree(AUTHOR_ROOT / 'companion/practice/sdd/shared', PROJECT / 'inputs')
    (PROJECT / 'source/treasury').mkdir(parents=True, exist_ok=False)
    source_router = AUTHOR_ROOT / 'companion/repo/src/treasury/routing.py'
    shutil.copy2(source_router, PROJECT / 'source/treasury/routing.py')
    manifest = json.loads((PROJECT / 'inputs/INPUT_MANIFEST.json').read_text())
    fixed_checks = {}
    for relative, declared in manifest['files'].items():
        path = PROJECT / 'inputs' / relative
        original = AUTHOR_ROOT / 'companion/practice/sdd/shared' / relative
        raw = path.read_bytes()
        fixed_checks[relative] = {'sha256': sha(raw), 'expected': declared['sha256'],
                                  'bytes': len(raw), 'same_as_author_source': raw == original.read_bytes(),
                                  'matches_fixed_manifest': sha(raw) == declared['sha256']}
        assert fixed_checks[relative]['same_as_author_source'] and fixed_checks[relative]['matches_fixed_manifest']
    assert len(fixed_checks) == 9
    shutil.copytree(PROJECT, EVIDENCE / 'initial_tree')
    write_json(EVIDENCE / 'INITIAL_MANIFEST.json', inventory(PROJECT))
    write_json(EVIDENCE / 'SCAFFOLD_AND_FIXED_INPUT_CHECKS.json', {
        'status': 'PASS_NO_INFERENCE_NO_FEATURE_OUTPUT', 'checked_at_utc': now(),
        'scaffold_files': scaffold, 'full_installed_commands': unchanged_commands,
        'fixed_input_checks': fixed_checks,
        'router': {'source': str(source_router), 'sha256': sha(source_router.read_bytes())},
        'exposure': 'Supplied authored inputs/specification.json is the reference contract. Nine fixed JSON inputs and original router are preserved; this is not blind elicitation. No earlier generated Markdown artifacts, reviews, exercise answers or owner answers are supplied.',
        'scope': 'Installed scaffold and fixed-input copying only. Native generation remains NOT_RUN.'})
    print(json.dumps({'status': 'PASS_NO_INFERENCE_NO_FEATURE_OUTPUT', 'project': str(PROJECT),
                      'fixed_inputs': len(fixed_checks), 'full_commands_identical': True}, indent=2))


if __name__ == '__main__':
    main()
