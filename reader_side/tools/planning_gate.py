"""CP07 command-line review: starter expected fail, reference expected pass."""
from pathlib import Path
import sys,json,argparse
from planning_core import read_json,validate,ROOT,ready_levels

def main(args=None):
    p=argparse.ArgumentParser()
    p.add_argument('--plan',default=str(ROOT/'repo/engineering/planning/delegation_plan.json'))
    p.add_argument('--handoff',default=str(ROOT/'repo/engineering/planning/delegation_handoff.json'))
    ns=p.parse_args(args)
    data=read_json(ns.plan);handoff=read_json(ns.handoff)
    issues=validate(data,handoff)
    result={'status':'PASS' if not issues else 'FAIL','findings':issues,'findings_count':len(issues),'meaning':'Owner-run CP07 synthetic planning gate: does not run coding agents or grant permissions'}
    print(json.dumps(result,indent=2))
    if not issues:
        print('Read-only logical rounds: one slot =',ready_levels(data,1),'; two slots =',ready_levels(data,2))
    return 0 if not issues else 1
if __name__=='__main__':sys.exit(main())
