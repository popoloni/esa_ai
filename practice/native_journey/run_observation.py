#!/usr/bin/env python3
"""Capture an actual bounded native client invocation and export its session.

This recorder executes the declared argv with the retained explicit environment.
It does not generate model output, modify candidate files, or decide acceptance.
"""
from pathlib import Path
import argparse, datetime as dt, hashlib, json, os, signal, subprocess, time


def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def inv(p):return {f.relative_to(p).as_posix():sha(f) for f in sorted(p.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--preparation',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--task',type=Path);args=ap.parse_args()
    prep=args.preparation.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    task_path=args.task.resolve() if args.task else prep/'CLIENT_TASK.json'
    task=json.loads(task_path.read_text());env=json.loads((prep/'ENVIRONMENT.json').read_text());project=Path(task['inventory_root'])
    before=inv(project);dump(out/'BEFORE.json',before)
    (out/'TASK.json').write_bytes(task_path.read_bytes())
    record={'schema':'esa-native-csv-invocation/v1','started_at_utc':now(),'argv':task['argv'],'cwd':task['cwd'],
      'environment_reference':str(prep/'ENVIRONMENT.json'),'environment_sha256':sha(prep/'ENVIRONMENT.json'),
      'task_sha256':sha(task_path),'driver_sha256':sha(Path(__file__)),'timeout_seconds':task['timeout_seconds'],
      'allowed_changed_files':task['allowed_changed_files'],'human_acceptance':'PENDING','cost':'NOT_MEASURED',
      'claim':'Actual native client capture, not automatic completion or external approval.'}
    dump(out/'LAUNCH.json',record);start=time.monotonic()
    with (out/'stdout.txt').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
      proc=subprocess.Popen(task['argv'],cwd=task['cwd'],env=env,stdout=stdout,stderr=stderr,start_new_session=True)
      record['pid']=proc.pid;dump(out/'LAUNCH.json',record)
      try:record['exit_code']=proc.wait(timeout=task['timeout_seconds'])
      except subprocess.TimeoutExpired:
        record['stop_reason']='OUTER_TIMEOUT';os.killpg(proc.pid,signal.SIGTERM)
        try:record['exit_code']=proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
          os.killpg(proc.pid,signal.SIGKILL);record['exit_code']=proc.wait();record['forced_group_stop']=True
    record.update(ended_at_utc=now(),elapsed_seconds=time.monotonic()-start)
    after=inv(project);dump(out/'AFTER.json',after)
    changed=sorted(n for n in set(before)|set(after) if before.get(n)!=after.get(n))
    record['changed_files']=changed;record['out_of_scope_changes']=sorted(set(changed)-set(task['allowed_changed_files']))
    record['streams_sha256']={n:sha(out/n) for n in ['stdout.txt','stderr.txt']}
    dump(out/'RECEIPT.json',record)
    events=[]
    for line in (out/'stdout.txt').read_text(errors='replace').splitlines():
      try:events.append(json.loads(line))
      except ValueError:pass
    identities={x['sessionID'] for x in events if 'sessionID' in x}
    if len(identities)==1:
      session=next(iter(identities));cmd=[task['argv'][0],'--pure','export',session]
      rec={'started_at_utc':now(),'argv':cmd,'cwd':task['cwd'],'scope':'Native export; no inference.'}
      with (out/'native-session.json').open('wb') as stdout,(out/'export.stderr.txt').open('wb') as stderr:
        result=subprocess.run(cmd,cwd=task['cwd'],env=env,stdout=stdout,stderr=stderr,timeout=90)
      rec.update(ended_at_utc=now(),exit_code=result.returncode)
      try:json.loads((out/'native-session.json').read_text());rec['json_valid']=True
      except ValueError:rec['json_valid']=False
      dump(out/'EXPORT.json',rec)
    print(json.dumps({'exit_code':record['exit_code'],'elapsed_seconds':record['elapsed_seconds'],'changed_files':changed,'out_of_scope_changes':record['out_of_scope_changes'],'receipt':str(out/'RECEIPT.json')}))


if __name__=='__main__':main()
