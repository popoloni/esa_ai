"""Review the integrated working candidates or protected reference workflow."""
import argparse
import json
from pathlib import Path
import sys
from integration_core import review_workflow


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', action='store_true', help='Use protected reference artefacts; never repairs working candidates')
    parser.add_argument('--candidate', type=Path, help='Override the CP08 implementation under review')
    parser.add_argument('--report', type=Path, help='Override the CP08 implementation report')
    parser.add_argument('--receipt', type=Path, help='Require a previous passing receipt to match all current input bytes')
    parser.add_argument('--scope-baseline', type=Path, help='Check actual CP08 edits since an owner-captured baseline')
    parser.add_argument('--output', type=Path, help='Write this observed result as a receipt; never edits candidates')
    args = parser.parse_args(argv)
    result = review_workflow(reference=args.reference, candidate=args.candidate, report=args.report,
                             receipt=args.receipt, scope_baseline=args.scope_baseline)
    body = json.dumps(result, indent=2) + '\n'
    print(body, end='')
    if args.output:
        target=args.output.resolve()
        root=Path(__file__).resolve().parents[2]
        # Evidence belongs outside the editable and protected source trees.
        protected=json.loads((root/'reader_side/protected_sha256.json').read_text())
        if target.is_relative_to(root/'repo') or target == root/'reader_side/protected_sha256.json' or any(target == (root/rel).resolve() for rel in protected):
            parser.error('--output must not overwrite a candidate or protected source')
        if args.receipt and target == args.receipt.resolve():
            parser.error('keep the earlier receipt; choose a different output path')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding='utf-8')
    return 0 if result['status'] == 'PASS_REVIEW_GATE_ONLY' else 1


if __name__ == '__main__':
    sys.exit(main())
