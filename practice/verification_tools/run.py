#!/usr/bin/env python3
"""Run pinned optional tools against the actual Treasury router and named controls."""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.absolute()
    if out.exists() or any(p.is_symlink() for p in [out, *out.parents]):
        parser.error('choose a new output path without symlink ancestors')
    # Imports occur after arguments so --help works without optional packages.
    from hypothesis import given, example, settings, strategies as st
    from decimal import Decimal
    out.mkdir(parents=True)
    started = time.time()
    source = ROOT / 'repo/src/treasury/routing.py'
    router = load_module(source, 'esa_property_router')
    cases = {'positive_cent_strings': 0, 'nonpositive_cent_strings': 0}

    @settings(max_examples=250, derandomize=True, database=None, deadline=None)
    @example(cents=499999)
    @example(cents=500000)
    @example(cents=500001)
    @given(cents=st.integers(min_value=1, max_value=100000000))
    def valid_amounts(cents):
        amount = format(Decimal(cents) / 100, '.2f')
        actual = router.assess(amount)
        expected = 'STANDARD_QUEUE' if cents < 500000 else 'HUMAN_REVIEW'
        assert actual.route == expected, (amount, actual.route, expected)
        assert actual.policy_version == 'BR-001/v1'
        cases['positive_cent_strings'] += 1

    @settings(max_examples=100, derandomize=True, database=None, deadline=None)
    @example(cents=0)
    @given(cents=st.integers(min_value=-100000000, max_value=0))
    def nonpositive_amounts(cents):
        actual = router.assess(format(Decimal(cents) / 100, '.2f'))
        assert (actual.route, actual.reason) == ('REJECTED', 'INVALID_AMOUNT')
        cases['nonpositive_cent_strings'] += 1

    valid_amounts()
    nonpositive_amounts()
    invalid = ['NaN', 'Infinity', '-Infinity', '', 'not-an-amount']
    for value in invalid:
        assert router.assess(value).route == 'REJECTED', value
    property_seconds = time.time() - started

    text = source.read_text()
    assert text.count('amount < THRESHOLD_EUR') == 1
    mutant = out / 'boundary_mutant.py'
    mutant.write_text(text.replace('amount < THRESHOLD_EUR', 'amount <= THRESHOLD_EUR'))
    bad = load_module(mutant, 'esa_boundary_mutant')
    # An explicit equality example is part of the owner expectation, not inferred
    # from the implementation. Hypothesis runs the same generated-property shape.
    @settings(max_examples=100, derandomize=True, database=None, deadline=None)
    @example(cents=500000)
    @given(cents=st.integers(min_value=500000, max_value=100000000))
    def reject_boundary_mutation(cents):
        value = format(Decimal(cents) / 100, '.2f')
        assert bad.assess(value).route == 'HUMAN_REVIEW', value

    mutant_failure = None
    try:
        reject_boundary_mutation()
    except AssertionError as exc:
        mutant_failure = {'type': type(exc).__name__, 'counterexample': str(exc),
                          'notes': getattr(exc, '__notes__', [])}
    assert mutant_failure and mutant_failure['counterexample'] == '5000.00'

    insecure = out / 'unsafe_parse_control.py'
    assert text.count('Decimal(amount_eur)') == 1
    insecure.write_text(text.replace('Decimal(amount_eur)', 'Decimal(eval(amount_eur))'))
    # This deliberately unsafe candidate is scanned, never imported or executed.
    scans = []
    for name, paths, expected in [
        ('actual_router_and_adapter', [source, ROOT/'repo/src/treasury/architecture/direct.py'], 0),
        ('unsafe_parse_control', [insecure], 1),
    ]:
        cmd = [sys.executable, '-m', 'bandit', '-f', 'json', *map(str, paths)]
        before = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        (out/f'{name}.json').write_text(result.stdout)
        (out/f'{name}.stderr.txt').write_text(result.stderr)
        report = json.loads(result.stdout)
        assert result.returncode == expected, (name, result.returncode, result.stderr)
        assert not report['errors'], report['errors']
        if name == 'unsafe_parse_control':
            assert any(x['test_id'] == 'B307' for x in report['results'])
        else:
            assert report['results'] == []
        scans.append({'name':name,'argv':cmd,'exit_code':result.returncode,
                      'elapsed_seconds':time.time()-before,
                      'findings':[{'id':x['test_id'],'severity':x['issue_severity'],
                                   'confidence':x['issue_confidence'],'line':x['line_number']}
                                  for x in report['results']]})
    summary = {
        'schema':'esa-verification-tool-observation/v1',
        'status':'PASS_SELECTED_PROPERTIES_AND_NEGATIVE_CONTROLS',
        'python':platform.python_version(),'platform':platform.platform(),
        'dependencies':{x:importlib.metadata.version(x) for x in ['hypothesis','bandit']},
        'source':str(source.relative_to(ROOT)),'source_sha256':digest(source),
        'property_observations':cases,'explicit_invalid_inputs':invalid,
        'property_elapsed_seconds':property_seconds,
        'boundary_control':mutant_failure,'static_scans':scans,
        'elapsed_seconds':time.time()-started,
        'limits':['Generated inputs are finite decimal strings at cent precision within the stated range.',
                  'The equality control is explicitly seeded; its rejection is not an estimated detection rate.',
                  'Bandit examines selected Python syntax. A clean report is not proof of security.',
                  'B307 finds a risky eval call; it does not assess the business threshold.',
                  'No model, hosted CI, production deployment or human approval is exercised.']}
    (out/'OBSERVATIONS.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
