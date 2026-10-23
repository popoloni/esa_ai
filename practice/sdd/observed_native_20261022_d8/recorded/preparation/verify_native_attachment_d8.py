#!/usr/bin/env python3
"""Bounded native noReply file-attachment preflight; never invoke a model.

Uses a new, explicitly titled preparation session. The session is never reused
for generation. The same native resolveUserPart/read path handles a file part
created by a discovered command's @absolute-file reference.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    with path.open('x', encoding='utf-8') as out:
        json.dump(value, out, indent=2)
        out.write('\n')


def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes())
            for p in sorted(root.rglob('*')) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preparation', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--port', type=int, default=18081)
    args = parser.parse_args()
    prep = args.preparation.resolve(strict=True)
    output = args.output.absolute()
    output.mkdir(parents=True, exist_ok=False)
    task = json.loads((prep / 'CLIENT_TASK_01.json').read_text())
    notes = json.loads((prep / 'CONFIGURATION_NOTES.json').read_text())
    env = json.loads((prep / 'ENVIRONMENT_01.json').read_text())
    project = Path(task['cwd'])
    bundle = Path(notes['input_bundle']['path'])
    opencode = notes['native_invocation_prepared_not_executed']['argv_without_env_wrapper'][0]
    source = (prep / 'pinned_client_sources/session_prompt.ts').read_text()
    assert 'if (input.noReply === true) return message' in source
    assert source.index('if (input.noReply === true) return message') < source.index('return yield* loop({ sessionID: input.sessionID })', source.index('if (input.noReply === true) return message'))
    assert 'ask: () => Effect.void' in source and 'bypassCwdCheck: true' in source
    config = json.loads((prep / 'OPENCODE_CONFIG_01.json').read_text())
    assert config['enabled_providers'] == ['esa-local']
    assert config['provider']['esa-local']['options']['baseURL'] == 'http://127.0.0.1:18080/v1'
    for port, description in ((args.port, 'preflight port must be unused'), (18080, 'no model backend may be running during this noReply preflight')):
        with socket.socket() as check:
            check.settimeout(1)
            if check.connect_ex(('127.0.0.1', port)) == 0:
                raise SystemExit(description)
    before = inventory(project)
    argv = [opencode, '--pure', '--print-logs', '--log-level', 'DEBUG', 'serve',
            '--hostname', '127.0.0.1', '--port', str(args.port)]
    record = {'status': 'STARTING_NATIVE_NOREPLY_PREFLIGHT', 'started_at_utc': now(),
              'argv': argv, 'cwd': str(project), 'environment_reference': str(prep / 'ENVIRONMENT_01.json'),
              'configuration_sha256': sha((prep / 'OPENCODE_CONFIG_01.json').read_bytes()),
              'source_proof': {'file': 'pinned_client_sources/session_prompt.ts', 'sha256': sha(source.encode()),
                               'noReply_guard': 'prompt() returns the fully created user message before loop(); title/agent inference is inside loop().',
                               'scope': 'Native attachment-resolution preflight, not named-command execution or model generation.'},
              'model_backend_port_18080_unoccupied': True, 'generation_session_reuse': 'FORBIDDEN',
              'calls': [], 'errors': []}
    write_json(output / 'START.json', {k: v for k, v in record.items() if k not in ('calls', 'errors')})
    base = f'http://127.0.0.1:{args.port}'
    proc = None

    def request(name, method, route, payload=None, timeout=40):
        call = {'name': name, 'method': method, 'route': route, 'started_at_utc': now(), 'model_call': False}
        raw = json.dumps(payload).encode() if payload is not None else None
        if raw is not None:
            with (output / (name + '.request.json')).open('xb') as out:
                out.write(raw)
            call['request_sha256'] = sha(raw)
        req = Request(base + route, data=raw, method=method,
                      headers={'Content-Type': 'application/json', 'x-opencode-directory': str(project)})
        try:
            with urlopen(req, timeout=timeout) as response:
                content = response.read()
                call['status_code'] = response.status
        except HTTPError as exc:
            content = exc.read()
            call['status_code'] = exc.code
        call.update(finished_at_utc=now(), response_sha256=sha(content), response_bytes=len(content))
        with (output / (name + '.response.json')).open('xb') as out:
            out.write(content)
        record['calls'].append(call)
        if call['status_code'] != 200:
            raise RuntimeError(f'{name}: HTTP {call["status_code"]}: {content[:300]!r}')
        return json.loads(content)

    try:
        with (output / 'server.stdout.txt').open('xb') as out, (output / 'server.stderr.txt').open('xb') as err:
            proc = subprocess.Popen(argv, cwd=project, env=env, stdout=out, stderr=err, start_new_session=True)
        record['server_pid'] = proc.pid
        record['server_pgid'] = os.getpgid(proc.pid)
        deadline = time.monotonic() + 75
        ready = False
        while time.monotonic() < deadline and proc.poll() is None:
            try:
                with urlopen(base + '/global/health', timeout=1) as response:
                    health_raw = response.read()
                    if response.status == 200:
                        with (output / 'HEALTH.json').open('xb') as out:
                            out.write(health_raw)
                        ready = True
                        break
            except (URLError, TimeoutError):
                time.sleep(0.25)
        if not ready:
            raise RuntimeError('Native preflight server did not become healthy within 75 seconds')
        api = request('OPENAPI', 'GET', '/doc')
        record['message_route_present'] = '/session/{sessionID}/message' in api.get('paths', {})
        if not record['message_route_present']:
            raise RuntimeError('Expected native message API not present in actual OpenAPI')
        session = request('CREATE_SESSION', 'POST', '/session', {
            'title': 'PREPARATION ONLY d8 native attachment noReply verification; never use for generation'})
        session_id = session['id']
        record['session_id'] = session_id
        record['session_title'] = session.get('title')
        payload = {'noReply': True, 'agent': 'esa-sdd',
                   'model': {'providerID': 'esa-local', 'modelID': 'esa-qwen3-4b'},
                   'parts': [{'type': 'text', 'text': 'Preparation-only native input attachment verification. No generation task is requested. This session is not reused.'},
                             {'type': 'file', 'mime': 'text/plain', 'filename': bundle.name, 'url': bundle.as_uri()}]}
        native = request('NOREPLY_ATTACHMENT', 'POST', f'/session/{session_id}/message', payload)
        messages = request('SESSION_MESSAGES', 'GET', f'/session/{session_id}/message')
        info = request('SESSION_INFO', 'GET', f'/session/{session_id}')
        write_json(output / 'API_SESSION_EXPORT.json', {'format': 'API responses assembled without modifying native message bodies',
                                                       'info': info, 'messages': messages})
        parts = native.get('parts', [])
        text_parts = [p['text'] for p in parts if p.get('type') == 'text']
        reads = [text for text in text_parts if '<content>\n' in text and f'<path>{bundle}</path>' in text]
        assert len(reads) == 1, 'Expected exactly one native full-file read output'
        actual = reads[0]
        with (output / 'ACTUAL_NATIVE_ATTACHMENT_TEXT.txt').open('x', encoding='utf-8') as out:
            out.write(actual)
        assert '... (line truncated to 2000 chars)' not in actual
        assert 'Output capped at ' not in actual and '(Showing lines ' not in actual
        assert '<system-reminder>' not in actual, 'Unexpected extra instruction file was appended'
        inner = actual.split('<content>\n', 1)[1].split('\n</content>', 1)[0]
        numbered = re.findall(r'^(\d+): (.*)$', inner, flags=re.MULTILINE)
        lines = bundle.read_text().splitlines()
        assert [int(n) for n, _ in numbered] == list(range(1, len(lines) + 1)), 'Native read line sequence differs'
        assert [text for _, text in numbered] == lines, 'Native read altered or clipped a source line'
        reconstructed = '\n'.join(text for _, text in numbered) + '\n'
        assert reconstructed.encode() == bundle.read_bytes(), 'Complete native attachment bytes differ after removing presentation line labels'
        source_checks = {}
        for relative, source_record in notes['input_bundle']['source_files'].items():
            raw = (project / relative).read_bytes()
            assert sha(raw) == source_record['sha256']
            language, fence = ('json', '```') if relative.endswith('.json') else (('python', '```') if relative.endswith('.py') else ('markdown', '````'))
            prefix = f'## {relative}\nSHA-256: {sha(raw)}\n{fence}{language}\n'
            assert reconstructed.count(prefix) == 1
            body = reconstructed.split(prefix, 1)[1].split('\n' + fence, 1)[0]
            if relative.endswith('.json'):
                same = json.loads(body) == json.loads(raw)
                basis = 'Parsed JSON values equal every original source value'
            else:
                same = body.encode() == raw
                basis = 'Exact complete original source bytes'
            assert same, 'Incomplete source body: ' + relative
            source_checks[relative] = {'pass': same, 'basis': basis, 'original_sha256': sha(raw), 'original_bytes': len(raw)}
        assert len(source_checks) == 13
        assert len(messages) == 1 and messages[0]['info']['role'] == 'user'
        assert not any(p.get('type') in ('tool', 'step-start', 'step-finish', 'reasoning') for p in messages[0].get('parts', []))
        after = inventory(project)
        assert before == after, 'Native input preflight changed project files'
        record.update(status='PASS_NATIVE_FULL_ATTACHMENT_NOREPLY_NO_INFERENCE',
                      checks={'one_explicitly_titled_preparation_session': True,
                              'one_user_message_no_assistant_or_model_step': True,
                              'all_13_source_bodies_verified': True,
                              'all_nine_json_values_preserved': True,
                              'no_native_read_line_clipping_or_file_cap': True,
                              'no_extra_instruction_file_appended': True,
                              'native_read_output_reconstructs_exact_bundle': True,
                              'project_inventory_unchanged': True},
                      source_checks=source_checks, native_attachment_sha256=sha(actual.encode()),
                      native_attachment_bytes=len(actual.encode()), native_line_count=len(lines),
                      reconstructed_bundle_sha256=sha(reconstructed.encode()),
                      permission_scope='The named file is explicitly permitted by the scoped configuration. The pinned user-attachment implementation internally supplies ask=>void and bypassCwdCheck; this is not a model-selected permission-boundary probe.',
                      inference_scope='No model backend was running; noReply returned a user message before the model/title loop. Named-command generation remains NOT_RUN.')
    except Exception as exc:
        record['status'] = 'NATIVE_ATTACHMENT_PREFLIGHT_FAILED'
        record['errors'].append({'type': type(exc).__name__, 'message': str(exc), 'at_utc': now()})
    finally:
        if proc is not None:
            cleanup = {'pid': proc.pid, 'pgid': record['server_pgid'], 'started_at_utc': now()}
            if proc.poll() is None:
                os.killpg(record['server_pgid'], signal.SIGTERM)
                cleanup['sigterm_sent'] = True
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    os.killpg(record['server_pgid'], signal.SIGKILL)
                    cleanup['sigkill_after_15_seconds'] = True
                    proc.wait(timeout=10)
            cleanup.update(returncode=proc.returncode, finished_at_utc=now(), owned_process_stopped=proc.poll() is not None)
            record['cleanup'] = cleanup
        record['finished_at_utc'] = now()
        record['files'] = inventory(output)
        write_json(output / 'RESULT.json', record)
    print(json.dumps({'status': record['status'], 'session_id': record.get('session_id'),
                      'source_checks': len(record.get('source_checks', {})), 'errors': record['errors'],
                      'result': str(output / 'RESULT.json')}, indent=2))
    return 0 if record['status'].startswith('PASS_') else 1


if __name__ == '__main__':
    raise SystemExit(main())
