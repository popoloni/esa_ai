"""Owner-run synthetic source-and-skill audit. No external access or AI model invocation."""
from pathlib import Path
import argparse, json, sys,datetime
from knowledge_core import ROOT,PACKET,SKILL,REF,evaluate,affected_claims,read_json

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidate',type=Path,default=PACKET)
    ap.add_argument('--skill',type=Path,default=SKILL)
    args=ap.parse_args(argv)
    issues=evaluate(args.candidate,args.skill)
    deps=read_json(ROOT/'reader_side/knowledge/claim_dependencies.json')
    examples={x:affected_claims([x],deps) for x in ('K-ADR-005','K-POL-001','K-WIKI-OLD')}
    report={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'gate':'CP06_CONTEXT_AND_SKILL','candidate':str(args.candidate.relative_to(ROOT)) if args.candidate.is_relative_to(ROOT) else str(args.candidate),
        'status':'PASS' if not issues else 'FAIL', 'issues':issues,'hypothetical_invalidation':examples,
        'meaning':'Selected synthetic source, typed-context and skill-file checks only. Not a live agent test, factual validation, sandbox, security certification or human approval.'}
    print(json.dumps(report,indent=2))
    target=ROOT/'reader_side/evidence/CP06_KNOWLEDGE_GATE.json'
    target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return 0 if not issues else 1
if __name__=='__main__':sys.exit(main())
