#!/usr/bin/env python3
"""Keep bounded, scoped memory claims in an append-only local teaching ledger.

This ledger checks declared roles and file identities. It does not authenticate
an owner, establish an OS security boundary, train a model or run an agent.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys

SCHEMA = 'agent-memory-ledger/v1'
RECORD_SCHEMA = 'agent-memory-record/v1'
SCOPE_KEYS = {'task', 'component', 'contract', 'schema'}
ACTOR_KINDS = {'human', 'model_agent', 'automated_control'}
RECORD_KEYS = {'schema', 'record_id', 'version', 'memory_type', 'claim', 'scope',
               'producer', 'last_checked_at', 'valid_from', 'expires_at',
               'source_refs', 'evidence_refs', 'revisit_if', 'sensitivity', 'supersedes'}


class Refused(ValueError):
    pass


def stamp():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_time(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        raise Refused('INVALID_DATED_VALIDITY')
    if result.tzinfo is None or result.utcoffset().total_seconds() != 0:
        raise Refused('UTC_TIMESTAMP_REQUIRED')
    return result


def workspace_path(workspace, name):
    path = Path(name)
    if path.is_absolute() or '..' in path.parts:
        raise Refused('REFERENCE_OUTSIDE_WORKSPACE')
    path = workspace / path
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise Refused('SYMLINK_REFERENCE_REFUSED')
    if not path.resolve().is_relative_to(workspace):
        raise Refused('REFERENCE_OUTSIDE_WORKSPACE')
    return path


def relative_file(workspace, path):
    path = path.resolve()
    if not path.is_relative_to(workspace):
        raise Refused('INPUT_OUTSIDE_WORKSPACE')
    return path.relative_to(workspace).as_posix()


def load_json(path, max_bytes=65536):
    if not path.is_file() or path.is_symlink():
        raise Refused('REGULAR_INPUT_FILE_REQUIRED')
    data = path.read_bytes()
    if len(data) > max_bytes:
        raise Refused('INPUT_TOO_LARGE')
    try:
        return json.loads(data)
    except (UnicodeError, json.JSONDecodeError):
        raise Refused('INVALID_JSON_INPUT')


def checked_ref(workspace, ref):
    if not isinstance(ref, dict) or set(ref) != {'path', 'sha256', 'locator'}:
        raise Refused('REFERENCE_REQUIRES_PATH_HASH_LOCATOR')
    if not isinstance(ref['path'], str) or not 1 <= len(ref['path']) <= 512:
        raise Refused('BOUNDED_REFERENCE_PATH_REQUIRED')
    if not isinstance(ref['locator'], str) or not 1 <= len(ref['locator']) <= 240:
        raise Refused('REFERENCE_LOCATOR_REQUIRED')
    if not re.fullmatch(r'[0-9a-f]{64}', str(ref['sha256'])):
        raise Refused('INVALID_REFERENCE_HASH')
    path = workspace_path(workspace, ref['path'])
    if not path.is_file():
        raise Refused('REFERENCE_MISSING')
    if digest(path.read_bytes()) != ref['sha256']:
        raise Refused('REFERENCE_HASH_MISMATCH')
    return ref


def checked_scope(scope):
    if not isinstance(scope, dict) or set(scope) != SCOPE_KEYS:
        raise Refused('EXACT_TASK_COMPONENT_CONTRACT_SCHEMA_REQUIRED')
    if any(not isinstance(v, str) or not 1 <= len(v) <= 160 or v == '*' for v in scope.values()):
        raise Refused('CONCRETE_SCOPE_REQUIRED')
    return scope


def checked_actor(actor):
    if not isinstance(actor, dict) or set(actor) != {'id', 'kind'}:
        raise Refused('DECLARED_ACTOR_REQUIRED')
    if actor['kind'] not in ACTOR_KINDS or not isinstance(actor['id'], str) or not actor['id'].strip():
        raise Refused('INVALID_DECLARED_ACTOR')
    return actor


def check_record(workspace, record):
    if not isinstance(record, dict) or set(record) != RECORD_KEYS or record['schema'] != RECORD_SCHEMA:
        raise Refused('CLOSED_RECORD_SCHEMA_REQUIRED')
    if record['sensitivity'] != 'public':
        raise Refused('SENSITIVE_CONTENT_NOT_ALLOWED')
    if record['memory_type'] not in {'fact', 'procedure', 'decision'}:
        raise Refused('UNSUPPORTED_MEMORY_TYPE')
    if not re.fullmatch(r'[A-Za-z0-9_-]{3,80}', str(record['record_id'])):
        raise Refused('INVALID_RECORD_ID')
    if type(record['version']) is not int or record['version'] < 1:
        raise Refused('POSITIVE_RECORD_VERSION_REQUIRED')
    if not isinstance(record['claim'], str) or not 1 <= len(record['claim']) <= 1600:
        raise Refused('BOUNDED_CLAIM_REQUIRED')
    checked_scope(record['scope'])
    checked_actor(record['producer'])
    times = [parse_time(record[k]) for k in ('valid_from', 'last_checked_at', 'expires_at')]
    if not times[0] <= times[1] < times[2]:
        raise Refused('INVALID_VALIDITY_INTERVAL')
    for field in ('source_refs', 'evidence_refs'):
        refs = record[field]
        if not isinstance(refs, list) or not 1 <= len(refs) <= 6:
            raise Refused('SOURCE_AND_OBSERVED_EVIDENCE_REQUIRED')
        for ref in refs:
            checked_ref(workspace, ref)
    if not isinstance(record['revisit_if'], list) or not record['revisit_if'] or any(not isinstance(v, str) or len(v) > 240 for v in record['revisit_if']):
        raise Refused('INVALIDATION_OR_REVISIT_TRIGGERS_REQUIRED')
    if record['supersedes'] is not None and not isinstance(record['supersedes'], str):
        raise Refused('INVALID_SUPERSESSION_REFERENCE')
    return record


@contextmanager
def writer_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + '.lock')
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise Refused('LEDGER_WRITER_BUSY_RETAIN_LOCK_FOR_INSPECTION')
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def load_events(path):
    if not path.is_file() or path.is_symlink():
        raise Refused('INITIALIZED_REGULAR_LEDGER_REQUIRED')
    data = path.read_bytes()
    if data and not data.endswith(b'\n'):
        raise Refused('UNTERMINATED_EVENT_TAIL')
    events = []
    previous = None
    for number, raw in enumerate(data.splitlines(), 1):
        try:
            event = json.loads(raw)
        except (UnicodeError, json.JSONDecodeError):
            raise Refused('BROKEN_EVENT_JSON')
        if not isinstance(event, dict) or event.get('sequence') != number or event.get('schema') != SCHEMA:
            raise Refused('BROKEN_EVENT_SEQUENCE')
        if event.get('previous_event_sha256') != previous:
            raise Refused('BROKEN_EVENT_CHAIN')
        stated = event.get('event_sha256')
        body = {k: v for k, v in event.items() if k != 'event_sha256'}
        if stated != digest(canonical(body)):
            raise Refused('EVENT_HASH_MISMATCH')
        previous = stated
        events.append(event)
    if not events or events[0]['kind'] != 'initialized':
        raise Refused('INITIALIZATION_EVENT_REQUIRED')
    return events


def append(path, events, kind, data):
    event = {'schema': SCHEMA, 'sequence': len(events) + 1, 'recorded_at_utc': stamp(),
             'kind': kind, 'previous_event_sha256': events[-1]['event_sha256'] if events else None,
             'data': data}
    event['event_sha256'] = digest(canonical(event))
    with path.open('ab') as stream:
        stream.write(canonical(event) + b'\n')
        stream.flush()
        os.fsync(stream.fileno())
    events.append(event)
    return event


def state_from(events):
    records = {}
    for event in events:
        data = event['data']
        if event['kind'] == 'proposed':
            record = data['record']
            records[record['record_id']] = {'record': record, 'record_sha256': data['record_sha256'],
                'content_sha256': digest(record['claim'].encode('utf-8')),
                'status': 'proposed', 'created_at': event['recorded_at_utc'],
                'proposal_event_sha256': event['event_sha256'], 'approval': None, 'invalidation': None}
        elif event['kind'] == 'promoted':
            records[data['record_id']]['status'] = 'approved'
            records[data['record_id']]['approval'] = data | {'event_sha256': event['event_sha256']}
        elif event['kind'] == 'invalidated':
            records[data['record_id']]['status'] = 'revoked'
            records[data['record_id']]['invalidation'] = data | {'event_sha256': event['event_sha256']}
    return records


def current_policy(workspace, events):
    ref = events[0]['data']['policy_ref']
    checked_ref(workspace, ref)
    policy = load_json(workspace_path(workspace, ref['path']))
    if policy.get('schema') != 'agent-memory-authority/v1' or not isinstance(policy.get('grants'), list):
        raise Refused('INVALID_LOCAL_AUTHORITY_POLICY')
    return policy


def authorized(workspace, events, actor, scope, action):
    checked_actor(actor)
    for grant in current_policy(workspace, events)['grants']:
        if grant.get('actor') == actor and grant.get('scope') == scope and action in grant.get('actions', []):
            checked_ref(workspace, grant['basis'])
            return grant
    raise Refused('NO_MATCHING_LOCAL_OWNER_GRANT')


def event_ref(workspace, path):
    name = relative_file(workspace, path)
    return {'path': name, 'sha256': digest(path.read_bytes()), 'locator': 'whole file'}


def initialize(workspace, ledger, policy_file):
    with writer_lock(ledger):
        if ledger.exists():
            raise Refused('LEDGER_ALREADY_EXISTS')
        policy = load_json(policy_file)
        if policy.get('schema') != 'agent-memory-authority/v1' or not policy.get('grants'):
            raise Refused('INVALID_LOCAL_AUTHORITY_POLICY')
        for grant in policy['grants']:
            checked_scope(grant['scope'])
            checked_actor(grant['actor'])
            checked_ref(workspace, grant['basis'])
            if not set(grant['actions']) <= {'promote', 'invalidate'}:
                raise Refused('UNKNOWN_OWNER_ACTION')
        event = append(ledger, [], 'initialized', {'policy_ref': event_ref(workspace, policy_file),
            'authority_limit': 'Actor IDs and grants are local declarations, not authenticated owner authority.',
            'append_limit': 'The application appends events and detects a broken chain; the file owner can still rewrite the file.'})
    return {'status': 'INITIALIZED', 'event_sha256': event['event_sha256']}


def mutate(workspace, ledger, action, args):
    with writer_lock(ledger):
        events = load_events(ledger)
        records = state_from(events)
        try:
            current_policy(workspace, events)
            if action == 'propose':
                record = check_record(workspace, load_json(args.record))
                identifier = record['record_id']
                if identifier in records:
                    raise Refused('RECORD_ID_ALREADY_EXISTS_CREATE_A_NEW_VERSION')
                if record['supersedes'] is not None:
                    prior = records.get(record['supersedes'])
                    if not prior or prior['status'] != 'revoked' or prior['record']['scope'] != record['scope'] or record['version'] != prior['record']['version'] + 1:
                        raise Refused('CORRECTION_REQUIRES_REVOKED_PREDECESSOR_AND_NEXT_VERSION')
                elif record['version'] != 1:
                    raise Refused('FIRST_VERSION_MUST_BE_ONE')
                event = append(ledger, events, 'proposed', {'record': record, 'record_sha256': digest(canonical(record))})
                return {'status': 'PROPOSED_NOT_RETRIEVABLE', 'record_id': identifier,
                        'record_sha256': event['data']['record_sha256'], 'event_sha256': event['event_sha256']}

            if args.record_id not in records:
                raise Refused('UNKNOWN_RECORD')
            view = records[args.record_id]
            record = view['record']
            actor = {'id': args.actor, 'kind': args.actor_kind}
            grant = authorized(workspace, events, actor, record['scope'], action)
            if action == 'promote':
                if actor == record['producer']:
                    raise Refused('PRODUCER_CANNOT_PROMOTE_OWN_RECORD')
                if view['status'] != 'proposed':
                    raise Refused('ONLY_A_NEW_PROPOSAL_CAN_BE_PROMOTED')
                check_record(workspace, record)
                decision = load_json(args.decision)
                if decision.get('decision') != 'PROMOTE' or decision.get('record_sha256') != view['record_sha256']:
                    raise Refused('APPROVAL_MUST_BIND_EXACT_RECORD_SHA256')
                expected = record['source_refs'] + record['evidence_refs']
                if decision.get('reviewed_refs') != expected or not str(decision.get('reason', '')).strip():
                    raise Refused('APPROVAL_MUST_IDENTIFY_REVIEWED_SOURCES_AND_EVIDENCE')
                event = append(ledger, events, 'promoted', {'record_id': args.record_id,
                    'record_sha256': view['record_sha256'], 'actor': actor,
                    'authority_basis': grant['basis'], 'decision_ref': event_ref(workspace, args.decision),
                    'reason': decision['reason'], 'identity_authenticated': False})
                return {'status': 'APPROVED_LOCAL_DECLARATION', 'record_id': args.record_id,
                        'event_sha256': event['event_sha256'], 'identity_authenticated': False}
            if view['status'] != 'approved':
                raise Refused('ONLY_APPROVED_MEMORY_CAN_BE_REVOKED')
            counterevidence = checked_ref(workspace, load_json(args.counterevidence))
            note = load_json(args.decision)
            if note.get('decision') != 'REVOKE' or note.get('record_sha256') != view['record_sha256'] or not str(note.get('reason', '')).strip():
                raise Refused('REVOCATION_MUST_BIND_RECORD_AND_REASON')
            event = append(ledger, events, 'invalidated', {'record_id': args.record_id,
                'record_sha256': view['record_sha256'], 'actor': actor,
                'counterevidence_ref': counterevidence, 'decision_ref': event_ref(workspace, args.decision),
                'reason': note['reason'], 'identity_authenticated': False})
            return {'status': 'REVOKED_RETAINED_IN_HISTORY', 'record_id': args.record_id,
                    'event_sha256': event['event_sha256']}
        except Refused as error:
            # Keep the refusal without ingesting an unapproved or sensitive claim.
            data = {'action': action, 'reason': str(error), 'submitted_content_retained': False}
            if getattr(args, 'record', None) and args.record.is_file():
                data['submitted_file_sha256'] = digest(args.record.read_bytes())
            if getattr(args, 'record_id', None):
                data['record_id'] = args.record_id
            append(ledger, events, 'refused', data)
            raise


def retrieval(workspace, ledger, scope, at, limit, max_bytes):
    checked_scope(scope)
    date = parse_time(at)
    if not 1 <= limit <= 10 or not 2048 <= max_bytes <= 65536:
        raise Refused('RETRIEVAL_BUDGET_OUT_OF_RANGE')
    events = load_events(ledger)
    current_policy(workspace, events)
    records = state_from(events)
    excluded = {}
    candidates = []
    for identifier, view in records.items():
        record = view['record']
        reason = None
        if view['status'] != 'approved':
            reason = view['status']
        elif record['scope'] != scope:
            reason = 'scope_mismatch'
        elif date < parse_time(record['valid_from']):
            reason = 'not_yet_valid'
        elif date >= parse_time(record['expires_at']):
            reason = 'expired'
        else:
            try:
                for ref in record['source_refs'] + record['evidence_refs']:
                    checked_ref(workspace, ref)
                checked_ref(workspace, view['approval']['decision_ref'])
                authorized(workspace, events, view['approval']['actor'], scope, 'promote')
            except Refused:
                reason = 'source_evidence_or_approval_identity_changed'
        if reason:
            excluded[reason] = excluded.get(reason, 0) + 1
        else:
            candidates.append(view)
    # Ranking is only applied after authority, identity, date and scope gates.
    candidates.sort(key=lambda v: (v['record']['last_checked_at'], v['record']['version'], v['record']['record_id']), reverse=True)
    selected = candidates[:limit]
    result = {'status': 'RETRIEVED' if selected else 'NO_APPLICABLE_MEMORY',
              'as_of': at, 'scope': scope, 'records': selected, 'excluded_counts': excluded,
              'omitted_by_count_or_byte_budget': len(candidates) - len(selected),
              'budget': {'max_records': limit, 'max_bytes': max_bytes},
              'authority_limit': 'Approved is a checked local declaration, not authenticated owner approval.',
              'model_calls': 0}
    while len(canonical(result)) + 1 > max_bytes and result['records']:
        result['records'].pop()
        result['omitted_by_count_or_byte_budget'] += 1
    result['status'] = 'RETRIEVED' if result['records'] else 'NO_APPLICABLE_MEMORY'
    if len(canonical(result)) + 1 > max_bytes:
        raise Refused('BUDGET_TOO_SMALL_FOR_RECEIPT_METADATA')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path.cwd())
    parser.add_argument('--ledger', type=Path, required=True)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init'); init.add_argument('--policy', type=Path, required=True)
    propose = commands.add_parser('propose'); propose.add_argument('--record', type=Path, required=True)
    for name in ('promote', 'invalidate'):
        sub = commands.add_parser(name)
        sub.add_argument('--record-id', required=True)
        sub.add_argument('--actor', required=True)
        sub.add_argument('--actor-kind', choices=sorted(ACTOR_KINDS), required=True)
        sub.add_argument('--decision', type=Path, required=True)
        if name == 'invalidate':
            sub.add_argument('--counterevidence', type=Path, required=True)
    retrieve = commands.add_parser('retrieve')
    for name in sorted(SCOPE_KEYS):
        retrieve.add_argument('--' + name, required=True)
    retrieve.add_argument('--at', required=True)
    retrieve.add_argument('--limit', type=int, default=3)
    retrieve.add_argument('--max-bytes', type=int, default=12000)
    inspect = commands.add_parser('inspect'); inspect.add_argument('--record-id')
    args = parser.parse_args(argv)
    workspace = args.workspace.resolve()
    try:
        relative_file(workspace, args.ledger)
        if any(p.is_symlink() for p in [args.ledger, *args.ledger.parents]):
            raise Refused('REGULAR_LEDGER_PATH_REQUIRED')
        for field in ('policy', 'record', 'decision', 'counterevidence'):
            path = getattr(args, field, None)
            if path is not None:
                relative_file(workspace, path)
                if any(p.is_symlink() for p in [path, *path.parents]):
                    raise Refused('REGULAR_INPUT_PATH_REQUIRED')
        if args.command == 'init':
            result = initialize(workspace, args.ledger, args.policy)
        elif args.command in {'propose', 'promote', 'invalidate'}:
            result = mutate(workspace, args.ledger, args.command, args)
        elif args.command == 'retrieve':
            result = retrieval(workspace, args.ledger, {k: getattr(args, k) for k in SCOPE_KEYS}, args.at, args.limit, args.max_bytes)
        else:
            events = load_events(args.ledger)
            current_policy(workspace, events)
            state = state_from(events)
            if args.record_id and args.record_id not in state:
                raise Refused('UNKNOWN_RECORD')
            result = {'status': 'INSPECTED', 'events': len(events), 'head_sha256': events[-1]['event_sha256'],
                      'records': {args.record_id: state[args.record_id]} if args.record_id else state,
                      'model_calls': 0}
        sys.stdout.buffer.write(canonical(result) + b'\n')
        return 0
    except (Refused, OSError) as error:
        sys.stdout.buffer.write(canonical({'status': 'REFUSED', 'reason': str(error), 'model_calls': 0}) + b'\n')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
