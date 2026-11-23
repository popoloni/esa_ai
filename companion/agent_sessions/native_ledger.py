#!/usr/bin/env python3
"""Join retained native sessions, operator decisions and protected receipts per mission.

This reads files only. It launches no client and no check. A mission counts as
natively verified here when every required session in NATIVE_SESSION_MATRIX.json
has a completed native turn with client and model identified (collect_native.py),
the operator's last recorded verdict for each implementation session is
'accept', and the mission's printed final check and continuation receipts both
report a passing status for the same candidate bytes. Operator kind is copied
as recorded; nothing here verifies a person's identity or authority.

These are retained gates, not a rerun of today's protected suite. Later
regressions or contract findings must be reported separately.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import contextlib
import hashlib
import io
import json
import sys

COMPANION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import collect_native as collector

# Final receipts printed in Part V for each mission, in the order they are run.
# A tuple of paths lists retained attempts in order. Every printed name also
# accepts numbered retries (g2-first-02.json, g2-first-03.json, ...), because the
# CLI never overwrites a receipt. The most recently recorded attempt is the gate;
# earlier ones are kept and reported as superseded, never deleted.
RECEIPTS = {
    # G1's --select all run deliberately fails on the G2 backlog; the slice is the gate.
    'G1': [('check', 'work/evidence/g1-first.json'), ('continue', 'work/evidence/g1-handoff.json')],
    'G2': [('check', 'work/evidence/g2-first.json'), ('continue', 'work/evidence/g2-handoff.json')],
    'G3': [('check', ('work/evidence/g3-first.json', 'work/evidence/g3-second.json')),
           ('continue', ('work/evidence/g3-handoff.json', 'work/evidence/g3-handoff-02.json')),
           ('integration', ('work/g3-integration/REPORT.json', 'work/g3-integration/REPORT-02.json'))],
    'G4': [('check', 'work/evidence/g4-first.json'), ('continue', 'work/evidence/g4-handoff.json')],
    'B1': [('check', 'work/evidence/b1-check.json'), ('continue', 'work/evidence/b1-context.json'),
           ('check', 'work/evidence/b1-v2-check.json'), ('continue', 'work/evidence/b1-v2-handoff.json')],
    'B2': [('check', 'work/evidence/b2-first.json'), ('continue', 'work/evidence/b2-handoff.json')],
    'B3': [('check', 'work/evidence/b3-first.json'), ('continue', 'work/evidence/b3-handoff.json')],
    'B4': [('check', 'work/evidence/b4-first.json'), ('continue', 'work/evidence/b4-handoff.json')],
}
PASSING = {'SELECTED_CHECKS_PASSED', 'CONTEXT_HANDOFF_READY', 'SCOPED_HANDOFF_READY',
           'INTEGRATION_ACCEPTED_FOR_SCOPED_CHECKS', 'COMBINED_CHECKS_PASSED', 'INTEGRATION_CHECKS_PASSED'}
MODULES = {'G1': 'booking.py', 'G2': 'booking.py', 'G3': 'booking.py',
           'G4': 'operations.py', 'B1': 'src/treasury/routing.py',
           'B2': 'intake.py', 'B3': 'ledger.py', 'B4': 'incident.py'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Evidence path escapes the selected workspace: ' + str(relative))
    return path


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('Missing recorded timestamp')
    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if value.tzinfo is None:
        raise ValueError('Recorded timestamps must include a timezone')
    return value


def selected_capture(root, row):
    path = row.get('selected_attempt_path')
    if path is None:
        raise ValueError('No native attempt selected for this stage/client')
    attempt = inside(root, path)
    return attempt, json.loads((attempt / 'RESULT.json').read_text())


def decision_assessment(root, row, made):
    """Bind new decisions; retain the narrower meaning of old statements."""
    result = {'passing': False, 'binding': 'NOT_ASSESSED', 'errors': []}
    try:
        if not made:
            raise ValueError('No operator disposition is retained')
        decision = made[-1]
        expected = 'stop' if row['stage'] == 'question' else 'accept'
        if decision['decision'] != expected:
            raise ValueError('The last disposition is not ' + expected)
        attempt, capture = selected_capture(root, row)
        if timestamp(decision['at_utc']) < timestamp(capture['at_utc']):
            raise ValueError('Disposition predates the selected native attempt')
        folder = inside(root, row['session_path'])
        recorded = json.loads((folder / 'decisions' / decision['file']).read_text())
        binding = recorded.get('decision_binding')
        if binding is None:
            result['binding'] = 'LEGACY_RECORDED_STATEMENT_AFTER_RUN'
        else:
            expected_hashes = capture['after']
            canonical = json.dumps(expected_hashes, sort_keys=True, separators=(',', ':')).encode('utf-8')
            if not isinstance(binding, dict) or not all((
                binding.get('latest_run') == str(attempt.relative_to(folder)),
                binding.get('latest_result_sha256') == sha(attempt / 'RESULT.json'),
                binding.get('session_spec_sha256') == sha(folder / 'SESSION.json'),
                binding.get('candidate_hashes') == expected_hashes,
                binding.get('inventory_sha256') == hashlib.sha256(canonical).hexdigest(),
            )):
                raise ValueError('Decision binding does not match the selected native snapshot/result/spec')
            result['binding'] = 'RECORDED_BYTES_AND_RUN_MATCH'
        result['passing'] = True
    except (OSError, ValueError, KeyError, TypeError) as error:
        result['errors'].append(str(error))
    return result


def candidate_binding(root, mission, item, session_rows):
    """Check each retained product receipt against its actual native stage."""
    result = {'passing': False, 'errors': [], 'scope': 'Retained receipt and snapshot identity; no new product execution'}
    try:
        data = json.loads(inside(root, item['path']).read_text())
        stage = 'implement'
        if mission == 'B1':
            stage = 'v2' if Path(item['path']).name.startswith('b1-v2-') else 'v1'
        matching = [row for row in session_rows if row['stage'] == stage]
        if len(matching) != 1:
            raise ValueError('Receipt has no unique required implementation stage')
        row = matching[0]
        attempt, capture = selected_capture(root, row)
        spec = json.loads(inside(root, row['session_path']).joinpath('SESSION.json').read_text())
        module = MODULES[mission]
        expected = capture['after'].get(module)
        result.update(stage=stage, selected_attempt=str(attempt.relative_to(root)),
                      module=module, expected_candidate_sha256=expected)
        if not expected or data.get('mission') != mission:
            raise ValueError('Receipt mission or selected source is missing/mismatched')
        if data.get('candidate_sha256_before') != expected or data.get('candidate_sha256_after') != expected:
            raise ValueError('Receipt candidate hashes do not match the selected native source')
        if 'candidate_sha256_after_handoff' in data and data['candidate_sha256_after_handoff'] != expected:
            raise ValueError('Continuation candidate hash does not match the native source')
        if data.get('inputs_unchanged') is not True or data.get('candidate_retained', True) is not True:
            raise ValueError('Receipt does not establish unchanged candidate inputs')
        expected_contract = spec.get('api') or spec.get('task_contract')
        actual_contract = data.get('api_contract') or data.get('contract')
        if expected_contract != actual_contract:
            raise ValueError('Receipt API/contract differs from the selected session')
        if timestamp(data.get('recorded_at_utc')) < timestamp(capture.get('at_utc')):
            raise ValueError('Receipt predates the selected native attempt')
        protected = data.get('protected_input_sha256')
        if protected is None:
            before, after = data.get('protected_before'), data.get('protected_after')
            if not before or before != after:
                raise ValueError('Protected receipt input maps are missing or changed')
            if any(p.get('symlink') or p.get('expected_sha256') != p.get('candidate_sha256') for p in after):
                raise ValueError('Protected receipt inputs failed integrity checks')
            protected = {p['path']: p['candidate_sha256'] for p in after}
        if not protected or any(capture['after'].get(name) != digest for name, digest in protected.items()):
            raise ValueError('Protected test/contract/dependency hashes differ from the native snapshot')
        groups = data.get('groups', {})
        if not groups or any(group.get('status') != 'PASSED' or group.get('returncode') != 0
                             or group.get('timed_out') or not group.get('tests_run') for group in groups.values()):
            raise ValueError('Receipt does not contain successful nonempty protected check groups')
        result['protected_inputs_compared'] = len(protected)
        result['passing'] = True
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        result['errors'].append(str(error))
    return result


def integration_binding(root, item, session_rows):
    """Bind all three native sources to the extracted integration and its gate."""
    result = {'passing': False, 'errors': []}
    try:
        report_path = inside(root, item['path'])
        folder = report_path.parent
        data = json.loads(report_path.read_text())
        expected = {}
        for stage, module in (('implement', 'booking.py'), ('report', 'reservation_report.py'), ('cli', 'reservation_cli.py')):
            rows = [row for row in session_rows if row['stage'] == stage]
            if len(rows) != 1:
                raise ValueError('Integration requires a unique native ' + stage + ' stage')
            _, capture = selected_capture(root, rows[0])
            expected[module] = capture['after'][module]
        result['expected_source_sha256'] = expected
        transport = data['transport']
        if data.get('source_sha256') != expected or transport.get('source_sha256') != expected:
            raise ValueError('Integrated sources differ from the three native stage snapshots')
        payload = transport['payload_file_sha256']
        extracted = transport['extracted_file_sha256']
        if payload != extracted or any(payload.get(name) != digest for name, digest in expected.items()):
            raise ValueError('Integration payload/extracted maps do not bind all native sources')
        actual = collector.adapter.inventory(inside(folder, transport['extracted']))
        if actual != extracted:
            raise ValueError('Retained extracted package does not match its recorded file map')
        if sha(inside(folder, transport['archive'])) != transport.get('archive_sha256'):
            raise ValueError('Retained transport archive hash mismatch')
        cli_path = inside(folder, transport['cli_receipt'])
        if sha(cli_path) != transport.get('cli_receipt_sha256'):
            raise ValueError('Extracted CLI receipt hash mismatch')
        cli = json.loads(cli_path.read_text())
        if (cli.get('status') != 'TRANSPORT_CHECKS_PASSED' or cli.get('package_unchanged') is not True
                or cli.get('package_sha256_before') != extracted or cli.get('package_sha256_after') != extracted
                or len(cli.get('cases', [])) != 9 or not all(case.get('passed') for case in cli['cases'])):
            raise ValueError('Extracted CLI gate does not bind nine passing cases to this package')
        for name in ('combined_g3_handoff', 'extracted_g3_check'):
            bound = data[name]
            path = inside(folder, bound['receipt'])
            if sha(path) != bound.get('sha256'):
                raise ValueError(name + ' receipt hash mismatch')
            check = json.loads(path.read_text())
            if (check.get('status') not in PASSING or check.get('candidate_sha256_after') != expected['booking.py']
                    or check.get('candidate_sha256_before') != expected['booking.py'] or check.get('inputs_unchanged') is not True):
                raise ValueError(name + ' does not pass on the native booking source')
        result['passing'] = True
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        result['errors'].append(str(error))
    return result


def attempts(root, relative):
    """Present attempts of one printed receipt, oldest first."""
    names = []
    for name in (relative if isinstance(relative, tuple) else (relative,)):
        base = Path(name)
        names.append(name)
        folder = root / base.parent
        if folder.is_dir():
            names.extend((base.parent / item.name).as_posix()
                         for item in sorted(folder.glob(base.stem + '-[0-9][0-9]' + base.suffix)))
    present = [name for name in dict.fromkeys(names) if (root / name).is_file()]
    try:
        times = [timestamp(json.loads((root / name).read_text()).get('recorded_at_utc')) for name in present]
    except (OSError, ValueError, AttributeError):
        return present  # Without a time on every attempt, keep the printed order.
    return [name for _, _, name in sorted(zip(times, range(len(present)), present))]


def receipt(root, kind, relative, single=False):
    superseded = []
    if not single:
        present = attempts(root, relative)
        printed = relative if isinstance(relative, str) else relative[-1]
        chosen = present[-1] if present else printed
        superseded = [receipt(root, kind, item, single=True) for item in present[:-1]]
        relative = chosen
    path = root / relative
    row = {'kind': kind, 'path': relative, 'present': path.is_file(), 'superseded_attempts': superseded}
    if not row['present']:
        return row
    data = json.loads(path.read_text())
    row.update(status=data.get('status'), tests_run=data.get('tests_run'),
               candidate_sha256_after=data.get('candidate_sha256_after'),
               sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
               passing=data.get('status') in PASSING)
    return row


def decisions(folder):
    rows = []
    for path in sorted((folder / 'decisions').glob('*.json')):
        data = json.loads(path.read_text())
        rows.append({'file': path.name, 'sha256': sha(path), 'decision': data.get('decision'), 'operator': data.get('operator'),
                     'operator_kind': data.get('operator_kind'), 'at_utc': data.get('at_utc')})
    return rows


def build(root, output, client=None):
    root, output = root.resolve(), output.resolve()
    if output.exists():
        raise ValueError('Use a fresh output file.')
    scratch = output.with_suffix('.coverage.json')
    with contextlib.redirect_stdout(io.StringIO()):
        collector.collect(root, scratch, client=client)
    coverage = json.loads(scratch.read_text())
    scratch.unlink()
    missions = []
    for summary in coverage['missions']:
        mission = summary['mission']
        sessions = []
        session_rows = [r for r in coverage['sessions'] if r['mission'] == mission]
        for row in session_rows:
            folder = root / row['session_path']
            made = decisions(folder) if folder.is_dir() else []
            assessment = decision_assessment(root, row, made)
            settled = assessment['passing']
            sessions.append({
                'id': row['id'], 'stage': row['stage'], 'status': row['status'],
                'native_turn_completed': row['native_turn_completed'],
                'client_and_model_identified': row['client_and_model_identified'],
                'selected_attempt_path': row.get('selected_attempt_path'),
                'attempts': [{k: a.get(k) for k in ('path', 'status', 'client', 'client_version', 'requested_model',
                                                    'observed_model_ids', 'reported_cost_usd',
                                                    'permission_denial_count', 'changed_files',
                                                    'scope_changes_requiring_review', 'capture_hashes_match')}
                             for a in row['attempts']],
                'operator_decisions': made, 'operator_disposition_settled': settled,
                'operator_disposition_binding': assessment})
        receipts = [receipt(root, kind, relative) for kind, relative in RECEIPTS[mission]]
        for item in receipts:
            binding = (integration_binding(root, item, session_rows) if item['kind'] == 'integration'
                       else candidate_binding(root, mission, item, session_rows))
            item['candidate_binding'] = binding
            item['bound_passing'] = bool(item.get('passing') and binding['passing'])
        native = summary['complete_native_capture'] and summary['client_and_model_identified']
        verified = native and all(s['operator_disposition_settled'] for s in sessions) and all(r.get('bound_passing') for r in receipts)
        missions.append({'mission': mission, 'native_capture_complete': native,
                         'operator_dispositions_settled': all(s['operator_disposition_settled'] for s in sessions),
                         'receipts_passing': all(r.get('passing') for r in receipts),
                         'receipt_candidate_bindings_match': all(r.get('bound_passing') for r in receipts),
                         'natively_verified': verified, 'sessions': sessions, 'receipts': receipts})
    matrix_paths = {(root / row['session_path']).resolve() for row in coverage['sessions']}
    extra = []
    for spec_path in sorted((root / 'work').glob('*/SESSION.json')):
        folder = spec_path.parent.resolve()
        if folder in matrix_paths:
            continue
        attempts = []
        for attempt in sorted((folder / 'runs').glob('[0-9][0-9]')):
            result_path = attempt / 'RESULT.json'
            data = json.loads(result_path.read_text()) if result_path.is_file() else {}
            attempts.append({'path': str(attempt.relative_to(root)), 'status': data.get('status'),
                             'exit_code': data.get('exit_code'), 'reported_cost_usd': data.get('reported_cost_usd'),
                             'changed_files': data.get('changed_files')})
        extra.append({'path': str(folder.relative_to(root)), 'mission': json.loads(spec_path.read_text()).get('mission'),
                      'attempts': attempts, 'operator_decisions': decisions(folder),
                      'meaning': 'Retained session outside the printed matrix; it neither opens nor closes a required stage.'})
    kinds = sorted({d['operator_kind'] for m in missions for s in m['sessions'] for d in s['operator_decisions']})
    costs = [c for m in missions for s in m['sessions'] for a in s['attempts']
             if client is None or a.get('client') == client for c in (a.get('reported_cost_usd') or [])]
    result = {
        'schema': 'engineering-native-run-ledger/v2', 'at_utc': datetime.now(timezone.utc).isoformat(),
        'workspace': str(root), 'coverage_status': coverage['status'],
        'client_filter': client, 'client_coverage': coverage.get('client_coverage'),
        'verified_native_missions': sum(m['natively_verified'] for m in missions),
        'required_native_missions': len(missions),
        'native_sessions_completed': sum(s['native_turn_completed'] for m in missions for s in m['sessions']),
        'required_capture_stages': sum(len(m['sessions']) for m in missions),
        'operator_kinds_recorded': kinds,
        'human_operator_sessions': sum(1 for m in missions for s in m['sessions']
                                       if any(d['operator_kind'] == 'human' for d in s['operator_decisions'])),
        'reported_cost_usd_total': round(sum(costs), 4) if costs else None,
        'reported_cost_scope': 'Client-reported matrix attempts, including unsuccessful earlier attempts; not an invoice.',
        'missions': missions, 'retained_sessions_outside_matrix': extra,
        'retained_gate_scope': 'The receipts bind to the captured historical source and historical test inputs. This ledger does not rerun the current suite or close later regression findings.',
        'scope': ('Native transport capture, recorded operator statements and protected receipts only. '
                  'Operator identity and authority are not verified; product acceptance is technical within '
                  'the fictional teaching case; no human learning outcome is measured.')}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('coverage_status', 'verified_native_missions', 'required_native_missions',
                                             'native_sessions_completed', 'required_capture_stages',
                                             'operator_kinds_recorded', 'human_operator_sessions',
                                             'reported_cost_usd_total')}, indent=2))
    return 0 if result['verified_native_missions'] == result['required_native_missions'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace-root', type=Path, default=COMPANION.parent)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--client', choices=collector.adapter.CLIENTS,
                        help='Bind gates to the selected client; retain the broader capture inventory.')
    args = parser.parse_args()
    try:
        raise SystemExit(build(args.workspace_root, args.output, client=args.client))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, 'REFUSED: ' + str(error) + '\n')
