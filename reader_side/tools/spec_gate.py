"""Use: python reader_side/tools/spec_gate.py --candidate repo/engineering/specifications/explanation_alpha/specification.json"""
import argparse,json,sys
from pathlib import Path
from specification_core import ROOT,load_json,validate,export_projections
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--export-reviewed',default='')
a=p.parse_args()
f=Path(a.candidate)
if not f.is_absolute():f=ROOT/f
if f.is_symlink() or not f.is_file():sys.exit('ERROR: candidate missing or symlinked')
try:spec=load_json(f)
except (OSError,ValueError) as e:sys.exit(f'ERROR: invalid JSON: {e}')
issues=validate(spec)
if issues:
    print(f'REVIEW REQUIRED: {len(issues)} issue(s)')
    for s in issues:print(' - '+s)
    sys.exit(1)
print('OFFLINE STRUCTURAL+CASE CHECK PASS — human requirements approval still required')
if a.export_reviewed:
    out=Path(a.export_reviewed)
    if not out.is_absolute():out=ROOT/out
    # Command-line writer accepts only a dedicated export subtree and resolves symlinks/traversal.
    # This is narrow teaching-side hygiene, NOT a sandbox around the invoking process.
    out=out.resolve(strict=False)
    export_root=(ROOT/'exports').resolve(strict=False)
    if out==export_root or export_root not in out.parents:
        sys.exit('ERROR: export must be inside companion/exports/<subdirectory>')
    for kind,path in export_projections(spec,out).items():print(kind,path)
