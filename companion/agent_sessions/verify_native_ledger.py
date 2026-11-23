#!/usr/bin/env python3
"""Exercise evidence-binding failures on an isolated copy of retained sessions.

No model is launched, and the supplied evidence tree is never changed. This is
a consistency control, not proof of authorship or of a human operator's identity.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import shutil
import tempfile

import native_ledger as ledger


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(source, output, baseline_script=None):
    source, output = source.resolve(), output.resolve()
    if output.exists() or output.is_relative_to(source):
        raise ValueError('Use a fresh output directory outside retained evidence.')
    output.mkdir(parents=True)
    baseline = None
    if baseline_script:
        spec = importlib.util.spec_from_file_location('native_ledger_before_binding', baseline_script)
        baseline = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(baseline)
    observed = []
    with tempfile.TemporaryDirectory(prefix='native-ledger-controls-') as temp:
        root = Path(temp) / 'evidence'
        shutil.copytree(source, root)
        changed = set()

        def edit(relative, change):
            path = root / relative
            data = json.loads(path.read_text())
            change(data)
            path.write_text(json.dumps(data, indent=2) + '\n')
            changed.add(relative)

        def restore():
            for relative in changed:
                path, original = root / relative, source / relative
                if original.exists():
                    shutil.copy2(original, path)
                else:
                    path.unlink()
            changed.clear()

        def evaluate(label, expected, client='claude', compare_baseline=True):
            receipt = output / (label + '.json')
            with contextlib.redirect_stdout(io.StringIO()):
                ledger.build(root, receipt, client=client)
            data = json.loads(receipt.read_text())
            row = {'case': label, 'expected_verified_missions': expected,
                   'observed_verified_missions': data['verified_native_missions'],
                   'receipt': receipt.name, 'sha256': sha(receipt),
                   'control_passed': data['verified_native_missions'] == expected}
            if baseline and compare_baseline:
                old_receipt = output / (label + '_v5_1.json')
                with contextlib.redirect_stdout(io.StringIO()):
                    baseline.build(root, old_receipt)
                old = json.loads(old_receipt.read_text())
                row['v5_1_verified_missions'] = old['verified_native_missions']
                row['v5_1_receipt'] = old_receipt.name
                row['v5_1_sha256'] = sha(old_receipt)
            observed.append(row)
            restore()

        evaluate('retained_valid', 8)
        edit('work/evidence/g1-first.json', lambda d: d.update(
            candidate_sha256_before='0'*64, candidate_sha256_after='0'*64))
        evaluate('unrelated_candidate_receipt_refused', 7)
        edit('work/evidence/g1-first.json', lambda d: d.update(mission='B1'))
        evaluate('wrong_mission_receipt_refused', 7)
        edit('work/evidence/g1-first.json', lambda d: d.update(inputs_unchanged=False))
        evaluate('changed_check_inputs_refused', 7)
        edit('work/evidence/g2-first.json', lambda d: d['protected_input_sha256'].update({'tests/test_g2.py':'0'*64}))
        evaluate('unrelated_protected_test_receipt_refused', 7)
        edit('work/g3-integration/REPORT-02.json', lambda d: d['source_sha256'].update({'reservation_cli.py':'0'*64}))
        evaluate('integration_source_substitution_refused', 7)
        relative = 'work/g3-integration/extracted/integration-002/reservation_cli.py'
        with (root / relative).open('a') as stream:
            stream.write('\n# isolated ledger-negative-control mutation\n')
        changed.add(relative)
        evaluate('extracted_package_mutation_refused', 7)
        edit('work/g1-implementation/decisions/01.json', lambda d: d.update(at_utc='2020-01-01T00:00:00+00:00'))
        evaluate('stale_acceptance_refused', 7)
        relative = 'work/g1-implementation/decisions/02.json'
        d = json.loads((root / 'work/g1-implementation/decisions/01.json').read_text())
        d.update(decision='correct', at_utc=datetime.now(timezone.utc).isoformat())
        (root / relative).write_text(json.dumps(d, indent=2) + '\n')
        changed.add(relative)
        evaluate('later_correction_reopens_disposition', 7)

        def add_binding(data):
            folder = root / 'work/g1-implementation'
            result = folder / 'runs/01/RESULT.json'
            hashes = json.loads(result.read_text())['after']
            data['decision_binding'] = {
                'latest_run': 'runs/01', 'latest_result_sha256': sha(result),
                'session_spec_sha256': sha(folder / 'SESSION.json'),
                'candidate_hashes': hashes,
                'inventory_sha256': hashlib.sha256(json.dumps(hashes, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest(),
            }
        edit('work/g1-implementation/decisions/01.json', add_binding)
        evaluate('explicit_valid_decision_binding', 8)
        def stale_binding(data):
            add_binding(data)
            data['decision_binding']['latest_result_sha256'] = '0'*64
        edit('work/g1-implementation/decisions/01.json', stale_binding)
        evaluate('unrelated_decision_result_refused', 7)
        def changed_binding(data):
            add_binding(data)
            data['decision_binding']['candidate_hashes']['booking.py'] = '0'*64
            data['decision_binding']['inventory_sha256'] = hashlib.sha256(json.dumps(
                data['decision_binding']['candidate_hashes'], sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
        edit('work/g1-implementation/decisions/01.json', changed_binding)
        evaluate('decision_on_other_candidate_refused', 7)
        evaluate('claude_evidence_cannot_close_codex', 0, client='codex', compare_baseline=False)

    report = {'schema': 'native-ledger-controls/v1', 'new_model_calls': 0,
              'origin': 'NEW_DETERMINISTIC_CONTROLS_ON_ISOLATED_COPIES',
              'source': str(source), 'native_evidence_modified': False,
              'ledger_sha256': sha(Path(ledger.__file__)),
              'baseline_script_sha256': sha(baseline_script) if baseline_script else None,
              'controls': observed, 'passed': sum(row['control_passed'] for row in observed),
              'total': len(observed)}
    (output / 'RESULTS.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('passed', 'total', 'new_model_calls')}))
    return 0 if all(row['control_passed'] for row in observed) else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline-script', type=Path)
    args = parser.parse_args()
    raise SystemExit(verify(args.workspace_root, args.output, args.baseline_script))
