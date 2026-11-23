#!/usr/bin/env python3
"""Exercise native-recorder failures with local transport doubles only.

No client process or model is launched. Synthetic event streams below are
labelled controls; they cannot establish native-client, product or human gates.
"""
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from datetime import datetime, timezone
import argparse
import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import sys

COMPANION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COMPANION))
import agent_session as adapter
import start as workshop
import collect_native as collector


def verify(output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    checks = []

    def check(name, condition):
        checks.append({'check': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)

    complete = [
        {'type': 'thread.started', 'thread_id': 'CONTROL-THREAD-NOT-A-NATIVE-RUN'},
        {'type': 'turn.started'},
        {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Synthetic recorder control.'}},
        {'type': 'turn.completed', 'usage': {'input_tokens': 1, 'output_tokens': 1}},
    ]

    def fixture(name, events, *, code=0, mutation=None, start_error=None, model='CONTROL-NOT-A-MODEL', client='codex'):
        folder = output / name
        candidate = folder / 'candidate'
        # The recorder transport is synthetic. Use the normal issuer for the
        # learner entry so session resumption exercises the real identity gate.
        with contextlib.redirect_stdout(io.StringIO()):
            workshop.new_copy(SimpleNamespace(mission="B1", dest=candidate))
        entry = workshop.load_entry("B1", candidate)
        (candidate / 'product.py').write_text('# Synthetic recorder control; no product acceptance.\n')
        (candidate / 'protected.txt').write_text('Preserve this synthetic control input.\n')
        session = folder / 'session'
        session.mkdir()
        (session / 'task.txt').write_text('AUTOMATED TRANSPORT CONTROL. No real client or model may run.\n')
        (session / 'SESSION.json').write_text(json.dumps({
            'mission': 'B1', 'entry': entry, 'candidate': str(candidate), 'max_runs': 3, 'session_seconds_from_first_launch': 60,
            'wall_seconds_per_run': 5, 'editable_paths': ['product.py'],
            'protected_sha256': {'protected.txt': adapter.inventory(candidate)['protected.txt']},
            'test_origin': 'AUTOMATED_TRANSPORT_CONTROL_NO_MODEL_CALL',
        }))

        class LocalTransport:
            def __init__(self, command, **kwargs):
                self.returncode = code
                self.command = command
                self.kwargs = kwargs
            def communicate(self, prompt, timeout):
                self.kwargs['stdout'].write('\n'.join(json.dumps(e) if not isinstance(e, str) else e for e in events) + '\n')
                if mutation:
                    (candidate / mutation).write_text('Deliberate synthetic mutation.\n')

        args = SimpleNamespace(session=str(session), client=client, model=model, task_file=None, max_budget_usd=2.0 if client == 'claude' else None)
        start = mock.Mock(side_effect=start_error or LocalTransport)
        version = SimpleNamespace(stdout='synthetic-recorder-client 0; NOT A REAL CLIENT', returncode=0)
        with mock.patch.object(adapter.shutil, 'which', return_value='/SYNTHETIC_CONTROL_NOT_EXECUTABLE'), \
             mock.patch.object(adapter.subprocess, 'run', return_value=version), \
             mock.patch.object(adapter.subprocess, 'Popen', start), \
             contextlib.redirect_stdout(io.StringIO()):
            returned = adapter.run(args)
        receipt = json.loads((session / 'runs/01/RESULT.json').read_text())
        invocation = json.loads((session / 'runs/01/INVOCATION.json').read_text())
        check(name + '_process_intercepted', start.call_count == 1)
        check(name + '_acceptance_unestablished', receipt['acceptance'] == 'NOT_ESTABLISHED')
        check(name + '_snapshots_retained', (session/'runs/01/before/product.py').is_file() and (session/'runs/01/after/product.py').is_file())
        return returned, receipt, invocation

    status, failure = 'FAIL', None
    try:
        returned, receipt, invocation = fixture('empty_success_exit', [])
        check('zero_exit_empty_stream_rejected', returned == 1 and receipt['status'] == 'NATIVE_EVENT_STREAM_INCOMPLETE')
        returned, receipt, _ = fixture('thread_without_response', complete[:2])
        check('thread_creation_is_not_model_completion', returned == 1)
        returned, receipt, _ = fixture('completed_without_message', [complete[0], complete[-1]])
        check('completed_without_agent_message_rejected', returned == 1)
        check('terminal_event_alone_does_not_set_native_completion', not receipt['native_turn_completed'] and receipt['native_completion_event_observed'])
        returned, receipt, _ = fixture('protocol_complete', complete)
        check('complete_protocol_requires_review', returned == 0 and receipt['status'] == 'NATIVE_TURN_COMPLETED_REVIEW_REQUIRED')
        check('requested_model_not_inferred_as_observed', receipt['requested_model'] == 'CONTROL-NOT-A-MODEL' and receipt['observed_model_ids'] == [] and not receipt['model_identity_observed'])
        check('usage_kept_as_emitted', receipt['native_observations']['usage_observations'][0]['value']['input_tokens'] == 1)
        check('explicit_model_argument_bound', '--model' in invocation['argv'] and invocation['requested_model'] == 'CONTROL-NOT-A-MODEL')
        check('codex_launch_keeps_workspace_sandbox', invocation['argv'][invocation['argv'].index('--sandbox')+1] == 'workspace-write')
        check('codex_launch_does_not_override_auth_or_approvals', not any(flag in invocation['argv'] for flag in ['--ignore-user-config', '--ignore-rules', '--dangerously-bypass-approvals-and-sandbox', '--dangerously-bypass-hook-trust', '--approve-for-me', '--ask-for-approval', '--add-dir']))
        check('codex_permissions_not_inferred_from_request', invocation['launch_profile']['effective_host_permissions_verified'] is False)
        check('transport_capture_digests_retained', {'native_events.jsonl', 'stderr.txt'} <= set(receipt['capture_sha256']))
        returned, receipt, _ = fixture('non_object_json', [*complete, ['not', 'an', 'event']])
        check('non_object_json_rejected_without_crash', returned == 1 and receipt['malformed_native_event_lines'] == [5])
        returned, receipt, _ = fixture('malformed_json', [*complete, '{broken'])
        check('malformed_json_rejected', returned == 1 and receipt['status'] == 'NATIVE_EVENT_STREAM_INVALID')
        returned, receipt, _ = fixture('protocol_error_after_completion', [*complete, {'type': 'error', 'message': 'Synthetic error.'}])
        check('error_event_prevents_success', returned == 1 and receipt['status'] == 'NATIVE_TURN_FAILED')
        returned, receipt, _ = fixture('nonzero_after_completion', complete, code=1)
        check('nonzero_exit_prevents_success', returned == 1 and receipt['status'] == 'CLIENT_EXIT_NONZERO')
        returned, receipt, _ = fixture('permitted_edit', complete, mutation='product.py')
        check('permitted_edit_recorded', returned == 0 and receipt['changed_files'] == ['product.py'])
        returned, receipt, _ = fixture('protected_edit', complete, mutation='protected.txt')
        check('protected_edit_requires_review', returned == 1 and receipt['scope_changes_requiring_review'] == ['protected.txt'])
        check('protected_edit_does_not_set_accepted_native_completion', not receipt['native_turn_completed'])
        returned, receipt, _ = fixture('process_start_error', [], start_error=PermissionError('Synthetic denial; no client launched.'))
        check('start_exception_receipt_preserved', returned == 1 and receipt['exit_code'] == 126)
        identity = [dict(complete[0], model='CONTROL-OBSERVED-METADATA'), *complete[1:]]
        returned, receipt, _ = fixture('explicit_metadata', identity)
        check('metadata_identity_retains_source_line', receipt['observed_model_ids'] == ['CONTROL-OBSERVED-METADATA'] and receipt['native_observations']['model_observations'][0]['event_line'] == 1)
        text_claim = [*complete[:2], {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'I claim to be another model.'}}, complete[-1]]
        returned, receipt, _ = fixture('free_form_identity_claim', text_claim, model=None)
        check('free_form_model_claim_not_used', not receipt['model_identity_observed'] and receipt['requested_model'] is None)
        session_id = 'CONTROL-SESSION-NOT-A-NATIVE-RUN'
        claude_complete = [
            {'type': 'system', 'subtype': 'init', 'session_id': session_id, 'model': 'CONTROL-CLAUDE-METADATA', 'tools': ['Read']},
            {'type': 'assistant', 'session_id': session_id, 'message': {'model': 'CONTROL-CLAUDE-METADATA', 'content': [{'type': 'tool_use', 'id': 'control-1', 'name': 'Read', 'input': {}}], 'usage': {'input_tokens': 1, 'output_tokens': 1}}},
            {'type': 'user', 'session_id': session_id, 'message': {'content': [{'type': 'tool_result', 'tool_use_id': 'control-1', 'content': 'Synthetic.'}]}},
            {'type': 'assistant', 'session_id': session_id, 'message': {'model': 'CONTROL-CLAUDE-METADATA', 'content': [{'type': 'text', 'text': 'Synthetic recorder control.'}]}},
            {'type': 'result', 'subtype': 'success', 'is_error': False, 'result': 'Synthetic final message.', 'session_id': session_id,
             'total_cost_usd': 0.01, 'usage': {'input_tokens': 1, 'output_tokens': 1},
             'permission_denials': [{'tool_name': 'Bash', 'tool_input': {'command': 'synthetic denied command'}}]},
        ]
        returned, receipt, invocation = fixture('claude_protocol_complete', claude_complete, client='claude')
        check('claude_complete_stream_requires_review', returned == 0 and receipt['status'] == 'NATIVE_TURN_COMPLETED_REVIEW_REQUIRED')
        fields = sorted({row['field'] for row in receipt['native_observations']['model_observations']})
        check('claude_metadata_identity_fields_retained', receipt['observed_model_ids'] == ['CONTROL-CLAUDE-METADATA'] and fields == ['message.model', 'model'])
        check('claude_final_message_written', (output/'claude_protocol_complete/session/runs/01/agent_final.txt').read_text() == 'Synthetic final message.')
        check('claude_denials_and_reported_cost_retained', len(receipt['permission_denials']) == 1 and receipt['reported_cost_usd'] == [0.01])
        argv = invocation['argv']
        check('claude_isolation_flags_bound', invocation['client'] == 'claude' and argv[argv.index('--tools')+1] == adapter.CLAUDE_TOOLS
              and '--strict-mcp-config' in argv and '--no-session-persistence' in argv and argv[argv.index('--max-budget-usd')+1] == '2'
              and invocation['spend_limit_usd'] == 2.0 and '--model' in argv)
        returned, receipt, _ = fixture('claude_result_without_message', [claude_complete[0], claude_complete[-1]], client='claude')
        check('claude_result_without_agent_text_rejected', returned == 1 and receipt['status'] == 'NATIVE_EVENT_STREAM_INCOMPLETE')
        budget_stop = dict(claude_complete[-1], subtype='error_max_budget_usd', is_error=True)
        returned, receipt, _ = fixture('claude_budget_stop', [*claude_complete[:-1], budget_stop], client='claude')
        check('claude_error_result_prevents_success', returned == 1 and receipt['status'] == 'NATIVE_TURN_FAILED')
        flagged = dict(claude_complete[-1], is_error=True)
        returned, receipt, _ = fixture('claude_success_subtype_flagged_error', [*claude_complete[:-1], flagged], client='claude')
        check('claude_is_error_overrides_success_subtype', returned == 1 and receipt['status'] == 'NATIVE_TURN_FAILED')
        unflagged = {key: value for key, value in claude_complete[-1].items() if key != 'is_error'}
        returned, receipt, _ = fixture('claude_missing_is_error', [*claude_complete[:-1], unflagged], client='claude')
        check('claude_missing_is_error_not_success', returned == 1 and receipt['status'] == 'NATIVE_TURN_FAILED')
        text_claim = [claude_complete[0] | {'model': None}, {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'I am model X.'}]}}, claude_complete[-1]]
        returned, receipt, _ = fixture('claude_free_form_identity_claim', text_claim, client='claude', model=None)
        check('claude_free_form_model_claim_not_used', not receipt['model_identity_observed'])
        returned, receipt, _ = fixture('claude_stream_under_codex_invocation', claude_complete, client='codex')
        check('claude_events_cannot_complete_codex', returned == 1 and receipt['status'] == 'NATIVE_CLIENT_PROTOCOL_MISMATCH'
              and not receipt['native_turn_completed'] and receipt['observed_model_ids'] == [])
        returned, receipt, _ = fixture('codex_stream_under_claude_invocation', complete, client='claude')
        check('codex_events_cannot_complete_claude', returned == 1 and receipt['status'] == 'NATIVE_CLIENT_PROTOCOL_MISMATCH'
              and not receipt['native_turn_completed'])
        returned, receipt, _ = fixture('mixed_stream_under_codex_invocation', [*complete, *claude_complete], client='codex')
        check('mixed_protocol_stream_requires_review', returned == 1 and receipt['status'] == 'NATIVE_CLIENT_PROTOCOL_MISMATCH')
        source_session = output/'protocol_complete/session'
        decision_note = output/'decision_note.txt'
        decision_note.write_text('AUTOMATED CONTROL: record the current synthetic candidate; no human authority or product acceptance.\n')
        with contextlib.redirect_stdout(io.StringIO()):
            adapter.decide(SimpleNamespace(session=str(source_session), note_file=str(decision_note), operator='Synthetic recorder control', operator_kind='AI', decision='continue'))
        decision = json.loads((source_session/'decisions/01.json').read_text())
        binding = decision['decision_binding']
        check('decision_keeps_operator_kind', decision['operator_kind'] == 'AI')
        check('decision_binds_candidate_bytes', binding['candidate_hashes'] == adapter.inventory(output/'protocol_complete/candidate')
              and binding['inventory_sha256'] == hashlib.sha256(json.dumps(binding['candidate_hashes'], sort_keys=True, separators=(',', ':')).encode()).hexdigest())
        check('decision_binds_latest_run_and_spec', binding['latest_run'] == 'runs/01'
              and binding['latest_result_sha256'] == hashlib.sha256((source_session/'runs/01/RESULT.json').read_bytes()).hexdigest()
              and binding['session_spec_sha256'] == hashlib.sha256((source_session/'SESSION.json').read_bytes()).hexdigest())
        inspection = output/'inspection_start_denied'
        with mock.patch.object(adapter.shutil, 'which', return_value='/SYNTHETIC_CONTROL_NOT_EXECUTABLE'), \
             mock.patch.object(adapter.subprocess, 'run', side_effect=PermissionError('Synthetic local inspection denial.')), \
             contextlib.redirect_stdout(io.StringIO()):
            returned = adapter.inspect_client(SimpleNamespace(output=str(inspection), client='codex'))
        inspected = json.loads((inspection/'RESULT.json').read_text())
        check('inspection_start_failure_is_retained', returned == 1 and inspected['status'] == 'CLIENT_INSPECTION_FAILED'
              and inspected['native_model_calls_requested'] == 0 and all(row['exit_code'] == 126 for row in inspected['commands']))
        observed = adapter.native_observations([(i+1, e) for i, e in enumerate(complete)])
        check('timeout_prevents_success', adapter.native_status(-15, True, [], observed, []) == 'CLIENT_TIMEOUT')
        collection = output / 'collector_fixture'
        collection.mkdir()
        with contextlib.redirect_stdout(io.StringIO()):
            returned = collector.collect(collection, collection/'empty.json')
        empty = json.loads((collection/'empty.json').read_text())
        check('missing_native_sessions_remain_open', returned == 1 and empty['completed_missions'] == 0 and not empty['publication_ready'])
        target = collection/'work/g1-question'
        target.parent.mkdir(parents=True)
        shutil.copytree(output/'explicit_metadata/session', target)
        spec = json.loads((target/'SESSION.json').read_text())
        spec.update(schema='esa-agent-session/v1', mission='G1', stage='question',
                    runtime='Real installed Codex CLI; no model responses are simulated.')
        (target/'SESSION.json').write_text(json.dumps(spec))
        invocation_path = target/'runs/01/INVOCATION.json'
        invocation = json.loads(invocation_path.read_text())
        invocation['session_spec_sha256'] = hashlib.sha256((target/'SESSION.json').read_bytes()).hexdigest()
        invocation_path.write_text(json.dumps(invocation))
        with contextlib.redirect_stdout(io.StringIO()):
            returned = collector.collect(collection, collection/'synthetic_label.json')
        found = json.loads((collection/'synthetic_label.json').read_text())['sessions'][0]
        check('synthetic_transport_label_cannot_close_native_session', returned == 1 and not found['native_turn_completed'] and not found['session_contract_matches'])
        with contextlib.redirect_stdout(io.StringIO()):
            collector.collect(collection, collection/'codex_only.json', client='codex')
            collector.collect(collection, collection/'claude_only.json', client='claude')
        codex_only = json.loads((collection/'codex_only.json').read_text())
        claude_only = json.loads((collection/'claude_only.json').read_text())
        check('client_filter_keeps_selected_client_attempt', codex_only['client_filter'] == 'codex'
              and codex_only['sessions'][0]['selected_attempt_path'] == 'work/g1-question/runs/01')
        check('client_filter_cannot_borrow_other_client_run', claude_only['sessions'][0]['selected_attempt_path'] is None
              and claude_only['sessions'][0]['status'] == 'NOT_RUN_FOR_SELECTED_CLIENT'
              and claude_only['completed_native_sessions'] == 0)
        check('per_client_coverage_is_separate', set(codex_only['client_coverage']) == {'codex', 'claude'}
              and all(row['completed_native_sessions'] == 0 for row in codex_only['client_coverage'].values()))
        original_task = (target/'runs/01/task.txt').read_bytes()
        (target/'runs/01/task.txt').write_text('Deliberate capture-integrity mutation.\n')
        with contextlib.redirect_stdout(io.StringIO()):
            collector.collect(collection, collection/'changed_task.json')
        changed = json.loads((collection/'changed_task.json').read_text())['sessions'][0]
        check('changed_task_hash_detected', not changed['attempts'][0]['capture_hashes_match'])
        (target/'runs/01/task.txt').write_bytes(original_task)
        with (target/'runs/01/native_events.jsonl').open('a') as stream:
            stream.write(json.dumps({'type': 'thread.started', 'thread_id': 'CONTROL-TAMPERED-STREAM'})+'\n')
        with contextlib.redirect_stdout(io.StringIO()):
            collector.collect(collection, collection/'changed_stream.json')
        changed_stream = json.loads((collection/'changed_stream.json').read_text())['sessions'][0]['attempts'][0]
        check('changed_transport_hash_detected', changed_stream['transport_hashes_match'] is False
              and not changed_stream['capture_hashes_match'] and not changed_stream['native_turn_completed'])
        status = 'PASS'
    except Exception as error:
        failure = {'type': type(error).__name__, 'message': str(error)}
    result = {'schema': 'engineering-native-recorder-controls/v1', 'at_utc': datetime.now(timezone.utc).isoformat(),
              'status': status, 'checks': checks, 'checks_recorded': len(checks), 'failure': failure,
              'native_client_launches': 0, 'model_calls': 0, 'human_sessions': 0,
              'scope': 'Local synthetic transport controls. Popen and version lookup are intercepted. These fixtures are not native-model evidence.',
              'adapter_sha256': hashlib.sha256((COMPANION/'agent_session.py').read_bytes()).hexdigest(),
              'collector_sha256': hashlib.sha256(Path(collector.__file__).read_bytes()).hexdigest()}
    (output/'RESULTS.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ['status','checks_recorded','failure','native_client_launches','model_calls']},indent=2))
    return 0 if status == 'PASS' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    raise SystemExit(verify(parser.parse_args().output))
