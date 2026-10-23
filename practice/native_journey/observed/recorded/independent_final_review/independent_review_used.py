#!/usr/bin/env python3
"""Independently exercise a supplied native CSV candidate after its own check.

Checks one declared local contract, not native authenticity or user benefit.
Expected memberships are explicit and do not call the candidate selector.
"""
from pathlib import Path
import argparse, copy, csv, datetime as dt, hashlib, io, json, subprocess, sys


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True)
    ap.add_argument('--starting-manifest',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();p=args.project.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    start=json.loads(args.starting_manifest.read_text());now={x.relative_to(p).as_posix():sha(x) for x in p.rglob('*') if x.is_file() and '__pycache__' not in x.parts}
    changed=sorted(x for x in set(start)|set(now) if start.get(x)!=now.get(x));allowed={'api.py','presenter.py','spec.md','plan.md'}
    record={'schema':'esa-native-csv-independent-review/v1','observed_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
      'candidate_sha256':now,'starting_manifest_sha256':sha(args.starting_manifest),'review_driver_sha256':sha(Path(__file__)),
      'changed_files':changed,'out_of_scope_changes':sorted(set(changed)-allowed),'passed':[],'findings':[],
      'limits':'Selected local examples, file scope and nonempty document existence. Specification and plan quality require separate content review. No HTTP authentication, spreadsheet interpretation, scale, deployment, real owner approval or human-learning validation.'}
    sys.path.insert(0,str(p));from api import orders_response
    rows=[
      {'order_id':'N10','owner':'a','status':'open','customer':'München, East','amount_eur':'010.00','note':'"quoted"\r\nsecond\nthird'},
      {'order_id':'N20','owner':'b','status':'open','customer':'秘密','amount_eur':'0.01','note':'+SUM(1,2)'},
      {'order_id':'N30','owner':'a','status':'closed','customer':'','amount_eur':'-4.00','note':'@literal'},
      {'order_id':'N40','owner':'b','status':'closed','customer':'line\nbreak','amount_eur':'1.2300','note':'-2+3'},
    ]
    fields=['order_id','status','customer','amount_eur','note'];before=copy.deepcopy(rows)
    memberships=[('a',None,[0,2]),('a','open',[0]),('a','closed',[2]),('b',None,[1,3]),('b','open',[1]),('b','closed',[3]),('nobody',None,[]),('nobody','open',[]),('nobody','closed',[])]
    def check(name,fn):
      try:fn();record['passed'].append(name)
      except Exception as exc:record['findings'].append({'case':name,'type':type(exc).__name__,'message':str(exc)})
    for actor,status,wanted in memberships:
      def case(actor=actor,status=status,wanted=wanted):
        result=orders_response(rows,actor,'csv',status)
        assert result['content_type']=='text/csv; charset=utf-8'
        actual=list(csv.reader(io.StringIO(result['body'],newline='')))
        assert actual==[fields]+[[rows[i][k] for k in fields] for i in wanted],actual
        expected={'content_type':'application/json','body':[{k:rows[i][k] for k in fields} for i in wanted]}
        assert orders_response(rows,actor,'json',status)==expected
        assert rows==before
      check(f'membership_roundtrip_json_immutability:{actor}:{status}',case)
    def empty():
      res=orders_response([], 'a', 'csv');assert list(csv.reader(io.StringIO(res['body'],newline='')))==[fields]
    check('empty_input_header',empty)
    for bad_format in ['xml','yaml','CSV','']:
      def unsupported(bad_format=bad_format):
        try:orders_response(rows,'a',bad_format)
        except ValueError:return
        raise AssertionError('unsupported format accepted: '+repr(bad_format))
      check('unsupported_format:'+repr(bad_format),unsupported)
    def scope():assert not record['out_of_scope_changes'],record['out_of_scope_changes']
    check('unchanged_owned_files_and_allowed_new_records',scope)
    for name in ['spec.md','plan.md']:
      def nonempty(name=name):assert (p/name).is_file() and len((p/name).read_text().split())>=15
      check('nonempty_file_exists:'+name,nonempty)
    checker=Path(__file__).resolve().parents[1]/'csv_export/checks/check.py'
    argv=[sys.executable,'-B',str(checker),'--candidate',str(p)]
    with (out/'supplied_contract_check.json').open('wb') as stdout,(out/'supplied_contract_check.stderr.txt').open('wb') as stderr:
      proc=subprocess.run(argv,stdout=stdout,stderr=stderr)
    record['supplied_contract_check']={'argv':argv,'exit_code':proc.returncode,'checker_sha256':sha(checker),'result_sha256':sha(out/'supplied_contract_check.json')}
    record['status']='PASS_SELECTED_CONTRACT_AND_SCOPE' if not record['findings'] and proc.returncode==0 else 'FINDINGS_REQUIRE_REVIEW'
    (out/'REVIEW.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'status':record['status'],'passed':len(record['passed']),'findings':record['findings']}))
    return int(record['status']!='PASS_SELECTED_CONTRACT_AND_SCOPE')


if __name__=='__main__':sys.exit(main())
