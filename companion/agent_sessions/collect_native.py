#!/usr/bin/env python3
"""Inventory the printed native-session matrix without launching any client.

This is a local evidence consistency check, not a signature, human identity
verification, product acceptance or publication authorization.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import sys

COMPANION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COMPANION))
import agent_session as adapter


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect(root, output, client=None):
    if client is not None and client not in adapter.CLIENTS:
        raise ValueError('Unknown client filter: ' + str(client))
    root = root.resolve()
    output = output.resolve()
    if output.exists():
        raise ValueError('Use a fresh output file; earlier inventories remain retained.')
    matrix_path = Path(__file__).with_name('NATIVE_SESSION_MATRIX.json')
    matrix = json.loads(matrix_path.read_text())
    rows = []
    for required in matrix['sessions']:
        folder = (root / required['session_path']).resolve()
        if not folder.is_relative_to(root):
            raise ValueError('Session path escapes the selected workspace.')
        row = dict(required, status='NOT_RUN', attempts=[], client=None, client_version=None,
                   observed_model_ids=[], native_turn_completed=False,
                   client_and_model_identified=False, product_acceptance='NOT_ASSESSED',
                   human_operator_and_authorizer='NOT_VERIFIED',
                   selected_attempt_path=None, last_attempts_by_client={})
        if (folder / 'SESSION.json').is_file():
            spec = json.loads((folder / 'SESSION.json').read_text())
            correct = (spec.get('mission') == required['mission']
                       and spec.get('schema') == 'esa-agent-session/v1'
                       and not spec.get('test_origin')
                       and spec.get('runtime') in (adapter.RUNTIME, adapter.LEGACY_RUNTIME))
            if required['stage'] in ('v1', 'v2'):
                correct = correct and spec.get('api') == 'B1-API/' + required['stage']
            elif required['stage'] in ('report', 'cli'):
                correct = correct and spec.get('integration_role') == required['stage']
            else:
                correct = correct and spec.get('stage') == required['stage']
            row['session_contract_matches'] = correct
            for attempt in sorted((folder / 'runs').glob('[0-9][0-9]')):
                item = {'path': str(attempt.relative_to(root)), 'status': 'INCOMPLETE_CAPTURE'}
                try:
                    receipt = json.loads((attempt / 'RESULT.json').read_text())
                    invocation = json.loads((attempt / 'INVOCATION.json').read_text())
                    attempt_client = invocation.get('client', 'codex')
                    item['client'] = attempt_client
                    events, malformed = adapter.native_events(attempt / 'native_events.jsonl')
                    observations = adapter.native_observations(events, client=attempt_client)
                    before, after = adapter.inventory(attempt / 'before'), adapter.inventory(attempt / 'after')
                    changed = sorted(name for name in set(before) | set(after) if before.get(name) != after.get(name))
                    outside = [name for name in changed if name not in spec['editable_paths']]
                    status = adapter.native_status(receipt['exit_code'], receipt['timed_out'], malformed, observations, outside)
                    transport_hashes = receipt.get('capture_sha256')
                    transport_match = None
                    if transport_hashes is not None:
                        transport_match = (isinstance(transport_hashes, dict)
                                           and {'native_events.jsonl', 'stderr.txt'} <= set(transport_hashes)
                                           and set(transport_hashes) <= {'native_events.jsonl', 'stderr.txt', 'agent_final.txt'}
                                           and all((attempt / name).is_file() and sha(attempt / name) == digest
                                                   for name, digest in transport_hashes.items()))
                    identity_matches = (attempt_client in adapter.CLIENTS
                                        and receipt.get('client', attempt_client) == attempt_client)
                    integrity = (before == receipt['before'] and after == receipt['after']
                                 and invocation.get('task_sha256') == sha(attempt / 'task.txt')
                                 and invocation.get('session_spec_sha256') == sha(folder / 'SESSION.json')
                                 and identity_matches and transport_match is not False)
                    item.update(status=status, capture_hashes_match=integrity,
                                client_identity_matches=identity_matches,
                                transport_hashes_match=transport_match,
                                transport_digest_binding='LEGACY_NOT_RECORDED' if transport_match is None else ('MATCH' if transport_match else 'MISMATCH'),
                                result_sha256=sha(attempt / 'RESULT.json'),
                                invocation_sha256=sha(attempt / 'INVOCATION.json'),
                                client_version=invocation.get('client_version'),
                                reported_cost_usd=[row['value'] for row in observations.get('reported_cost_observations', [])],
                                permission_denial_count=len(observations.get('permission_denials', [])),
                                requested_model=invocation.get('requested_model'),
                                observed_model_ids=sorted({m['value'] for m in observations['model_observations']}),
                                event_count=len(events), failed_event_lines=observations['failed_turn_or_error_lines'],
                                unexpected_protocol_lines=observations['unexpected_protocol_lines'],
                                usage_observation_count=len(observations['usage_observations']),
                                native_turn_completed=(status == 'NATIVE_TURN_COMPLETED_REVIEW_REQUIRED' and integrity),
                                changed_files=changed, scope_changes_requiring_review=outside)
                except (OSError, ValueError, KeyError, TypeError) as error:
                    item['capture_error'] = {'type': type(error).__name__, 'message': str(error)}
                row['attempts'].append(item)
            for name in adapter.CLIENTS:
                matching = [item for item in row['attempts'] if item.get('client') == name]
                if matching:
                    last = matching[-1]
                    row['last_attempts_by_client'][name] = {
                        'path': last['path'], 'status': last['status'],
                        'native_turn_completed': bool(correct and last.get('native_turn_completed')),
                        'client_and_model_identified': bool(correct and last.get('native_turn_completed')
                                                           and last.get('client_version') and last.get('observed_model_ids')),
                    }
            selected_attempts = [item for item in row['attempts'] if client is None or item.get('client') == client]
            if selected_attempts:
                last = selected_attempts[-1]
                row.update(status=last['status'], client=last.get('client'),
                           selected_attempt_path=last['path'], client_version=last.get('client_version'),
                           observed_model_ids=last.get('observed_model_ids', []),
                           native_turn_completed=bool(correct and last.get('native_turn_completed')),
                           client_and_model_identified=bool(correct and last.get('native_turn_completed')
                                                            and last.get('client_version') and last.get('observed_model_ids')))
            else:
                row['status'] = 'NOT_RUN_FOR_SELECTED_CLIENT' if row['attempts'] else 'PREPARED_NOT_RUN'
        rows.append(row)
    missions = []
    for mission in matrix['required_missions']:
        selected = [row for row in rows if row['mission'] == mission and row['required']]
        missions.append({'mission': mission, 'required_sessions': len(selected),
                         'native_sessions_completed': sum(row['native_turn_completed'] for row in selected),
                         'complete_native_capture': all(row['native_turn_completed'] for row in selected),
                         'client_and_model_identified': all(row['client_and_model_identified'] for row in selected)})
    complete = all(row['complete_native_capture'] and row['client_and_model_identified'] for row in missions)
    client_coverage = {}
    for name in adapter.CLIENTS:
        client_missions = []
        for mission in matrix['required_missions']:
            selected = [row for row in rows if row['mission'] == mission and row['required']]
            client_missions.append({
                'mission': mission,
                'complete_native_capture': all(row['last_attempts_by_client'].get(name, {}).get('native_turn_completed', False) for row in selected),
                'client_and_model_identified': all(row['last_attempts_by_client'].get(name, {}).get('client_and_model_identified', False) for row in selected),
            })
        client_coverage[name] = {
            'completed_missions': sum(row['complete_native_capture'] for row in client_missions),
            'completed_native_sessions': sum(row['last_attempts_by_client'].get(name, {}).get('native_turn_completed', False) for row in rows if row['required']),
            'client_and_model_identified_missions': sum(row['client_and_model_identified'] for row in client_missions),
            'required_missions': len(matrix['required_missions']),
            'required_native_sessions': sum(row['required'] for row in rows),
        }
    result = {'schema': 'engineering-native-coverage-inventory/v1',
              'at_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'NATIVE_CAPTURES_READY_FOR_REVIEW' if complete else 'NATIVE_COVERAGE_INCOMPLETE',
              'matrix_sha256': sha(matrix_path), 'workspace': str(root),
              'client_filter': client, 'client_coverage': client_coverage,
              'sessions': rows, 'missions': missions,
              'completed_missions': sum(row['complete_native_capture'] for row in missions),
              'completed_native_sessions': sum(row['native_turn_completed'] for row in rows if row['required']),
              'client_and_model_identified_missions': sum(row['client_and_model_identified'] for row in missions),
              'native_client_launches_by_this_collector': 0,
              'product_acceptance': 'NOT_ASSESSED', 'human_operator_identity': 'NOT_VERIFIED',
              'publication_ready': False,
              'scope': 'Retained local transport and snapshot consistency only. Review operator authority, product acceptance, coverage and human evidence separately.'}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','client_filter','completed_missions','completed_native_sessions','client_and_model_identified_missions','publication_ready']},indent=2))
    return 0 if complete else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace-root', type=Path, default=COMPANION.parent)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--client', choices=adapter.CLIENTS,
                        help='Count only this client; retain all attempts and report separate per-client coverage.')
    args = parser.parse_args()
    try:
        raise SystemExit(collect(args.workspace_root, args.output, client=args.client))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, 'REFUSED: ' + str(error) + '\n')
