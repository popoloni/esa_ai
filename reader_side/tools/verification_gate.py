"""Owner-side gate for the known author-created Chapter 9 synthetic candidates."""
from pathlib import Path
import argparse,sys,json
from verification_core import owner_gate,PROPOSAL,REVIEW

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidate',type=Path,default=PROPOSAL)
    ap.add_argument('--review',type=Path,default=REVIEW)
    ap.add_argument('--scope-baseline',type=Path,
                    help='Owner-created repository snapshot for the actual CP09 edit-scope diff')
    a=ap.parse_args(argv)
    print(json.dumps(result:=owner_gate(a.candidate,a.review,scope_baseline=a.scope_baseline),indent=2))
    return 0 if result['status']=='PASS_REVIEW_GATE_ONLY' else 1
if __name__=='__main__':sys.exit(main())
