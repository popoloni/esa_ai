"""CP05 CLI for reviewing two prototypes and a candidate ADR (offline only)."""
import argparse,sys
from pathlib import Path
from architecture_core import REPO,REF,load,check_design,check_adr,check_behavior

def run(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--candidate',default=str(REPO/'engineering/architecture/architecture_decision.json'))
    p.add_argument('--adr',default=str(REPO/'engineering/architecture/ADR-005.md'))
    a=p.parse_args(argv)
    errs=check_behavior()
    try: obj=load(a.candidate)
    except (OSError,ValueError) as ex:obj={};errs.append('candidate unreadable: '+str(ex))
    errs+=check_design(obj)
    try: text=Path(a.adr).read_text(encoding='utf-8')
    except OSError as ex: text='';errs.append('ADR unreadable: '+str(ex))
    errs+=check_adr(text,obj)
    for x in errs:print('ISSUE:',x)
    if errs:
        print('FAIL: CP05 architecture review',len(errs),'issues');return 1
    print('PASS: two synthetic prototypes match eight selected cases; decision is ready for HUMAN review only')
    return 0

if __name__=='__main__':sys.exit(run())
