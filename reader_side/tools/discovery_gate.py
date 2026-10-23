"""Run the reader-side CP03 review gate without altering the candidate."""
import argparse,sys,json
from pathlib import Path
from discovery_core import validate_decision,collect_baseline,json_read

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--candidate',default='repo/engineering/discovery/assessment.json')
    args=p.parse_args()
    root=Path(__file__).resolve().parents[2]
    candidate=(root/args.candidate).resolve()
    if not candidate.is_file() or root not in candidate.parents:
        print('FAIL: candidate must be inside companion',file=sys.stderr);return 2
    try:
        data=json_read(candidate)
        problems=validate_decision(data)
    except Exception as e:
        print('FAIL: discovery input error:',e,file=sys.stderr);return 2
    print('Synthetic baseline:',json.dumps(collect_baseline(),sort_keys=True))
    if problems:
        print('FAIL:',len(problems),'issues')
        for x in problems:print('-',x)
        return 1
    print('PASS: conditional alpha assessment passes deterministic offline checks')
    print('CAVEAT: no real user validation, no live agent run, no permission to deploy')
    return 0
if __name__=='__main__':sys.exit(main())
