"""CP08 owner-side cases and reporting checks, with optional before-edit scope evidence.

Integrity checks always run. Actual edit scope is evaluated only when the reader
supplies a baseline captured before editing. These are local teaching checks,
not an operating-system sandbox or a human acceptance decision.
"""
import argparse
import json
import sys
from pathlib import Path

from implementation_core import (
    CODE, REPORT, load_candidate, check_implementation, report_findings,
)
from scope_guard import check_integrity, check_edit_scope
from provenance_core import provenance_summary


def run(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,default=CODE)
    parser.add_argument('--report',type=Path,default=REPORT)
    parser.add_argument(
        '--scope-baseline',type=Path,
        help='Reader-owned repository snapshot captured before CP08 candidate edits.',
    )
    args=parser.parse_args(argv)

    findings=list(check_integrity())
    if args.scope_baseline is not None:
        try:
            findings.extend(check_edit_scope(args.scope_baseline,chapter='CP08'))
        except (OSError,ValueError,TypeError) as exc:
            findings.append('scope baseline cannot be checked: '+str(exc))
    try:
        findings.extend(check_implementation(load_candidate(args.candidate)))
    except Exception as exc:
        findings.append('code cannot be loaded or checked: '+str(exc))
    try:
        report = json.loads(args.report.read_text(encoding='utf-8'))
        findings.extend(report_findings(report, candidate_path=args.candidate))
    except Exception as exc:
        findings.append('report cannot be loaded or checked: '+str(exc))

    for finding in findings:
        print('ISSUE:',finding)
    print(('PASS' if not findings else 'FAIL')+': CP08 implementation gate, '+str(len(findings))+' findings')
    if args.scope_baseline is None:
        print('Edit scope: NOT CHECKED; no before-edit baseline supplied.')
    else:
        print('Edit scope: evaluated against the supplied CP08 before-edit baseline.')
    if not findings:
        print('Selected offline checks passed; ready for HUMAN CODE REVIEW only.')
        print('Attempt provenance:', json.dumps(provenance_summary(report), sort_keys=True))
        print('No business-value, architecture-acceptance or release authority follows from these checks.')
    return 0 if not findings else 1


if __name__=='__main__':
    sys.exit(run())
