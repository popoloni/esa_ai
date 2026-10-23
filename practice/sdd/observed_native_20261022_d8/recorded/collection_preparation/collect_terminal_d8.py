#!/usr/bin/env python3
"""Collect a completed native attempt without generating or editing project data.

Run only after root authorizes terminal collection. A terminal RECEIPT and its
recorded stdout/stderr/task hashes are mandatory. Export uses regular files,
following the proven d7 route. Reconstruction is explicitly separate from an
intermediate filesystem observation and from independent semantic acceptance.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

AUTHOR_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(AUTHOR_ROOT / 'companion/validation'))
from record_observed_command import inventory


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8') as out:
        json.dump(value, out, indent=2)
        out.write('\n')


def complete_inventory(root):
    result = {}
    for path in sorted(root.rglob('*')):
        name = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[name] = {'symlink_target': os.readlink(path)}
        elif path.is_file():
            raw = path.read_bytes()
            result[name] = {'sha256': sha(raw), 'bytes': len(raw)}
    return result


def relative_in_project(value, project):
    path = Path(value)
    if not path.is_absolute():
        path = project / path
    path = path.resolve(strict=False)
    return path.relative_to(project).as_posix() if path.is_relative_to(project) else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', type=Path, required=True)
    parser.add_argument('--starting-tree', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected-session')
    parser.add_argument('--terminal-collection-authorized', action='store_true', required=True)
    args = parser.parse_args()
    attempt = args.attempt.resolve(strict=True)
    baseline = args.starting_tree.resolve(strict=True)
    receipt = json.loads((attempt / 'RECEIPT.json').read_text())
    task_raw = (attempt / 'TASK.json').read_bytes()
    task = json.loads(task_raw)
    if not receipt.get('ended_at_utc') or 'exit_code' not in receipt:
        parser.error('A completed actual command receipt is required; do not collect an active run.')
    assert sha(task_raw) == receipt['task_sha256']
    assert receipt['argv'] == task['argv']
    for name in ('TASK.json', 'stdout.txt', 'stderr.txt'):
        assert sha((attempt / name).read_bytes()) == receipt['evidence_sha256'][name], name
    project = Path(task['inventory_root']).resolve(strict=True)
    assert Path(task['cwd']).resolve(strict=True) == project
    assert inventory(baseline) == receipt['before'], 'Starting snapshot differs from actual command inventory'
    assert inventory(project) == receipt['after'], 'Project differs from the terminal command inventory'
    output = args.output.absolute()
    assert not output.exists() and not output.resolve().is_relative_to(project)
    output.mkdir(parents=True, exist_ok=False)
    record = {'status': 'STARTING_TERMINAL_COLLECTION', 'started_at_utc': now(),
              'attempt': str(attempt), 'project': str(project), 'baseline': str(baseline),
              'collector_sha256': sha(Path(__file__).read_bytes()),
              'command_receipt_sha256': sha((attempt / 'RECEIPT.json').read_bytes()),
              'task_sha256': sha(task_raw), 'model_call': False, 'project_written': False,
              'human_review': 'ABSENT', 'acceptance': 'Not determined by this collector.',
              'terminal_authorization': 'Root explicitly authorized collection after the actual terminal receipt.',
              'origin_qualification': 'The command receipt may retain its preparation-origin label. Its actual timestamps, exit code and native events establish execution; that historical label is not rewritten.'}
    save(output / 'COLLECTION_START.json', record)
    try:
        events, parse_failures = [], []
        for line_number, line in enumerate((attempt / 'stdout.txt').read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                parse_failures.append({'line': line_number, 'error': str(exc), 'raw': line})
        event_ids = {e.get('sessionID') or e.get('part', {}).get('sessionID') for e in events}
        event_ids.discard(None)
        stderr = (attempt / 'stderr.txt').read_text()
        created_ids = set(re.findall(r'message=created\s+id=(ses_[A-Za-z0-9]+)', stderr))
        fallback_ids = set(re.findall(r'(?:sessionID|session\.id|session_id)[=:\s]+["\']?(ses_[A-Za-z0-9]+)', stderr))
        candidates = event_ids or created_ids or fallback_ids
        assert len(candidates) == 1, f'A unique observed session is required: {sorted(candidates)}'
        session_id = next(iter(candidates))
        if args.expected_session:
            assert session_id == args.expected_session
        save(output / 'SESSION_ID_OBSERVATION.json', {'session_id': session_id,
             'event_session_ids': sorted(event_ids), 'stderr_created_session_ids': sorted(created_ids),
             'stderr_fallback_session_ids': sorted(fallback_ids), 'stdout_parse_failures': parse_failures})

        wrapped = task['argv']
        assert wrapped[:2] == ['/usr/bin/env', '-i']
        env, index = {}, 2
        while index < len(wrapped) and re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', wrapped[index]):
            key, value = wrapped[index].split('=', 1)
            env[key] = value
            index += 1
        opencode = wrapped[index]
        assert Path(opencode).name == 'opencode' and wrapped[index + 1] == '--pure'
        assert env == json.loads(Path(task['environment_reference']).read_text())

        before_export = complete_inventory(project)
        shutil.copytree(project, output / 'final_project_tree', symlinks=True)
        assert complete_inventory(output / 'final_project_tree') == before_export
        assert complete_inventory(project) == before_export, 'Project changed during final snapshot'
        export_argv = [opencode, '--pure', 'export', session_id]
        export_record = {'argv': export_argv, 'cwd': str(project),
                         'environment_reference': task['environment_reference'],
                         'started_at_utc': now(), 'session_id': session_id, 'model_call': False,
                         'capture': 'regular file, not a subprocess pipe'}
        with (output / 'native-session.json').open('xb') as stdout, (output / 'export.stderr.txt').open('xb') as error:
            try:
                result = subprocess.run(export_argv, cwd=project, env=env, stdout=stdout,
                                        stderr=error, timeout=90, check=False)
                export_record['exit_code'] = result.returncode
            except subprocess.TimeoutExpired:
                export_record.update(exit_code=124, failure='EXPORT_TIMEOUT_90_SECONDS')
        export_record['finished_at_utc'] = now()
        raw = (output / 'native-session.json').read_bytes()
        export_record.update(export_bytes=len(raw), export_sha256=sha(raw),
                             stderr_sha256=sha((output / 'export.stderr.txt').read_bytes()))
        save(output / 'EXPORT_COMMAND.json', export_record)
        assert export_record['exit_code'] == 0, 'Native export failed; preserve this collection attempt'
        native = json.loads(raw)
        assert native['info']['id'] == session_id, 'Exported session identity differs'
        after_export = complete_inventory(project)

        changed = sorted(name for name in set(receipt['before']) | set(receipt['after'])
                         if receipt['before'].get(name) != receipt['after'].get(name))
        diff = []
        for name in changed:
            old = baseline / name
            new = output / 'final_project_tree' / name
            old_raw = old.read_bytes() if old.is_file() and not old.is_symlink() else b''
            new_raw = new.read_bytes() if new.is_file() and not new.is_symlink() else b''
            diff.extend(difflib.unified_diff(old_raw.decode('utf-8', 'replace').splitlines(keepends=True),
                                            new_raw.decode('utf-8', 'replace').splitlines(keepends=True),
                                            fromfile='before/' + name, tofile='after/' + name))
        with (output / 'FINAL_DIFF.patch').open('x') as out:
            out.write(''.join(diff))
        save(output / 'FINAL_INVENTORY.json', {'full_project_snapshot': before_export,
             'capture_scope_inventory': receipt['after'], 'changed_files': changed,
             'out_of_scope_changes': sorted(set(changed) - set(task['allowed_changed_files'])),
             'snapshot_matches_terminal_receipt': True, 'project_unchanged_by_export': before_export == after_export,
             'post_export_inventory_if_changed': after_export if before_export != after_export else None,
             'scope': 'Complete declared project snapshot plus recorder-compatible inventory; not OS containment.'})

        tools, texts, assistant_info = [], [], []
        for message_index, message in enumerate(native.get('messages', [])):
            info = message['info']
            if info.get('role') != 'assistant':
                continue
            assistant_info.append(info)
            for part_index, part in enumerate(message.get('parts', [])):
                if part.get('type') == 'text':
                    texts.append({'message_id': info['id'], 'part_id': part.get('id'),
                                  'time': part.get('time'), 'text': part.get('text', '')})
                if part.get('type') == 'tool':
                    state = part.get('state', {})
                    tools.append({'message_id': info['id'], 'message_index': message_index,
                                  'part_index': part_index, 'part': part,
                                  'ordering_time': state.get('time', {}).get('start', info.get('time', {}).get('created', 0))})
        tools.sort(key=lambda x: (x['ordering_time'], x['message_index'], x['part_index']))
        save(output / 'NATIVE_TOOL_RECORDS.json', {'source': 'native-session.json', 'records': tools})
        save(output / 'ASSISTANT_PARTS.json', {'source': 'native-session.json',
             'assistant_message_info': assistant_info, 'text_parts': texts,
             'scope': 'Raw native message usage/timing and text; incomplete messages are not completed usage or acceptance.'})
        actions = [e for e in events if e.get('type') in ('text', 'tool_use', 'error', 'reasoning')]
        if actions:
            save(output / 'FIRST_EMITTED_MODEL_ACTION.json', actions[0])
        if texts:
            with (output / 'FIRST_ASSISTANT_TEXT.txt').open('x') as out:
                out.write(texts[0]['text'])

        known = {name: (baseline / name).read_bytes() for name in receipt['before']
                 if (baseline / name).is_file() and not (baseline / name).is_symlink()}
        template = (baseline / '.specify/templates/spec-template.md').read_bytes()
        writes, first_generated = [], set()
        for number, tool_record in enumerate(tools, 1):
            part = tool_record['part']; state = part.get('state', {}); values = state.get('input', {})
            tool = part.get('tool'); status = state.get('status')
            item = {'tool_sequence': number, 'call_id': part.get('callID'), 'tool': tool,
                    'status': status, 'message_id': tool_record['message_id'],
                    'native_input': values, 'content_basis': None}
            content, relative = None, None
            if tool == 'bash':
                command = values.get('command', '')
                try:
                    bits = shlex.split(command)
                except ValueError:
                    bits = []
                if bits == ['cp', '.specify/templates/spec-template.md', 'specs/001-explain-treasury/spec.md']:
                    relative = bits[2]
                    item['classification'] = 'FRAMEWORK_TEMPLATE_COPY_NOT_GENERATED_FEATURE_CONTENT'
                    if status == 'completed' and state.get('metadata', {}).get('exit') == 0:
                        content = template
                        item['content_basis'] = 'Exact initial framework template and completed native cp exit0'
                else:
                    continue
            elif tool in ('write', 'edit'):
                path_value = values.get('filePath')
                if isinstance(path_value, str):
                    relative = relative_in_project(path_value, project)
                item['classification'] = 'COMPLETED_NATIVE_CONTENT_WRITE' if status == 'completed' else 'ATTEMPTED_CONTENT_WRITE_NOT_CONFIRMED'
                if tool == 'write' and isinstance(values.get('content'), str):
                    proposed = values['content'].encode('utf-8')
                    proposal = output / f'write_input_{number:03d}.txt'
                    with proposal.open('xb') as out:
                        out.write(proposed)
                    item['retained_input_content'] = {'path': proposal.name, 'sha256': sha(proposed), 'bytes': len(proposed)}
                    if status == 'completed':
                        content = proposed
                        item['content_basis'] = 'Reconstructed from completed native write input; post-write formatter effects are not assumed'
                elif tool == 'edit' and status == 'completed' and relative in known:
                    old, new = values.get('oldString'), values.get('newString')
                    previous = known[relative].decode('utf-8')
                    if isinstance(old, str) and old and isinstance(new, str) and old in previous:
                        occurrences = previous.count(old)
                        if values.get('replaceAll') or occurrences == 1:
                            content = previous.replace(old, new) if values.get('replaceAll') else previous.replace(old, new, 1)
                            content = content.encode('utf-8')
                            item['content_basis'] = 'Literal edit reconstructed against retained prior bytes; fuzzy edits are not guessed'
                if status == 'completed' and content is None:
                    item['reconstruction_limit'] = 'Missing baseline or non-literal edit; preserve raw native diff/input and final snapshot without inventing intermediate bytes'
            else:
                continue
            item['relative_path'] = relative
            if content is not None and relative is not None:
                known[relative] = content
                item['reconstructed_sha256'] = sha(content)
                item['reconstructed_bytes'] = len(content)
                final = output / 'final_project_tree' / relative
                item['matches_final_file_bytes'] = bool(final.is_file() and not final.is_symlink() and final.read_bytes() == content)
                if tool in ('write', 'edit') and content == template:
                    item['classification'] = 'TEMPLATE_EQUIVALENT_CONTENT_NOT_SUBSTANTIVE_FEATURE_GENERATION'
                if tool in ('write', 'edit') and relative not in first_generated:
                    dest = output / 'first_reconstructed_native_content' / relative
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with dest.open('xb') as out:
                        out.write(content)
                    first_generated.add(relative)
                    item['first_reconstructed_content_path'] = dest.relative_to(output).as_posix()
            writes.append(item)
        save(output / 'NATIVE_CONTENT_PROVENANCE.json', {'writes_and_template_copies': writes,
             'scope': 'First completed tool-input content reconstruction is not an independent observation of every intermediate filesystem version. Exact final bytes are retained separately. Scaffold copies and template-equivalent content do not establish useful generation.',
             'semantic_acceptance': 'Independent review required; this collector supplies no owner answer or acceptance verdict.'})
        record.update(status='COLLECTED_TERMINAL_NATIVE_EVIDENCE_REVIEW_PENDING', session_id=session_id,
                      native_export_sha256=sha(raw), exported_info_id_matches=True,
                      changed_files=changed, native_tool_parts=len(tools), assistant_text_parts=len(texts),
                      reconstructed_native_content_paths=sorted(first_generated),
                      project_unchanged_by_export=before_export == after_export)
    except Exception as exc:
        record.update(status='COLLECTION_FAILED_PARTIAL_EVIDENCE_PRESERVED',
                      error={'type': type(exc).__name__, 'message': str(exc)})
    record['finished_at_utc'] = now()
    record['files'] = complete_inventory(output)
    save(output / 'COLLECTION_RECEIPT.json', record)
    print(json.dumps({key: record.get(key) for key in ('status', 'session_id', 'changed_files', 'native_tool_parts', 'error')}, indent=2))
    return 0 if record['status'] == 'COLLECTED_TERMINAL_NATIVE_EVIDENCE_REVIEW_PENDING' else 1


if __name__ == '__main__':
    raise SystemExit(main())
