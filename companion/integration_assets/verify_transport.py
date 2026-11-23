#!/usr/bin/env python3
"""Observe the real integrated CLI in a separately extracted teaching package.

Oracles below are authored from INTEGRATION-G3/v1, not copied from CLI output.
The fixture uses only the retained public booking API. No fake provider is used.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import dataclasses
import hashlib
import importlib
import json
import os
import subprocess
import sys
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inventory(path):
    return {str(p.relative_to(path)):sha(p) for p in sorted(path.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and '.git' not in p.parts}


def verify(package, output, state_dir):
    sys.dont_write_bytecode=True
    package=package.resolve();output=output.resolve();state_dir=state_dir.resolve()
    if output.exists() or state_dir.exists():
        raise ValueError('Use new receipt and state paths to retain every prior observation.')
    if state_dir.is_relative_to(package) or output.is_relative_to(package):
        raise ValueError('Keep test state and receipts outside the extracted package.')
    state_dir.mkdir(parents=True)
    before=inventory(package)
    env=os.environ.copy();env.pop('PYTHONSTARTUP',None)
    env['PYTHONPATH']=str(package);env['PYTHONDONTWRITEBYTECODE']='1'
    report={'schema':'esa-integration-transport-check/v1',
            'recorded_at_utc':datetime.now(timezone.utc).isoformat(),
            'package':str(package),'package_sha256_before':before,
            'oracle':'Explicit INTEGRATION-G3/v1 examples; real composed modules and public booking API.',
            'fake_provider_used':False,'cases':[],'fixture_operations':[],
            'human_acceptance':'PENDING','production_authorization':False}
    def process(label, argv, expected_code, expected_json=None, error=False):
        state_before=inventory(state_dir)
        started=time.monotonic()
        try:
            run=subprocess.run(argv,cwd=package,env=env,capture_output=True,text=True,timeout=30)
            rc,out,err,timed_out=run.returncode,run.stdout,run.stderr,False
        except subprocess.TimeoutExpired as exc:
            rc,out,err,timed_out=None,exc.stdout or '',exc.stderr or '',True
            if isinstance(out,bytes):out=out.decode(errors='replace')
            if isinstance(err,bytes):err=err.decode(errors='replace')
        state_after=inventory(state_dir)
        one_json=None
        if expected_json is not None:
            try:one_json=json.loads(out)
            except ValueError:one_json=None
        checks={'exit_status':rc==expected_code,'not_timed_out':not timed_out,
                'state_unchanged':state_before==state_after}
        if expected_json is not None:
            checks.update(exact_report=json.dumps(one_json,sort_keys=True)==json.dumps(expected_json,sort_keys=True),
                          stderr_empty=err=='')
        elif error:
            checks.update(stdout_empty=out=='',stderr_present=bool(err.strip()))
        else:
            checks.update(stdout_empty=out=='',stderr_empty=err=='')
        row={'case':label,'argv':[str(v) for v in argv],'cwd':str(package),
             'returncode':rc,'stdout':out,'stderr':err,'timed_out':timed_out,
             'elapsed_process_seconds':time.monotonic()-started,
             'expected_exit_status':expected_code,'expected_json':expected_json,
             'state_sha256_before':state_before,'state_sha256_after':state_after,
             'checks':checks,'passed':all(checks.values())}
        report['cases'].append(row)
        return row
    try:
        process('import_has_no_cli_side_effect',[sys.executable,'-B','-c','import reservation_cli'],0)
        sys.path.insert(0,str(package))
        booking=importlib.import_module('booking')
        if Path(booking.__file__).resolve()!=package/'booking.py':
            raise ValueError('Fixture imported booking from outside the extracted package.')
        database=state_dir/'reservations.sqlite'
        booking.init_db(database)
        report['fixture_operations'].append({'call':'booking.init_db','args':[str(database)],'result':None,'state_sha256':inventory(state_dir)})
        request={'trusted_member_id':'integration-member','asset_id':'ROOM-17',
                 'starts_at':'2026-11-16T09:00:00Z','ends_at':'2026-11-16T10:00:00Z',
                 'idempotency_key':'integration-reservation-1'}
        reserved=booking.reserve(database,**request)
        report['fixture_operations'].append({'call':'booking.reserve','args':[str(database)],
                                            'kwargs':request,'result':dataclasses.asdict(reserved),
                                            'state_sha256':inventory(state_dir)})
        if reserved.status!=201 or reserved.reservation_id is None:
            raise ValueError('Public booking API did not establish the authored fixture.')
        rid=reserved.reservation_id
        history={'reservation_id':rid,**request}
        base=[sys.executable,'-B','reservation_cli.py','inspect','--database',str(database),'--reservation-id']
        process('confirmed_record',base+[str(rid)],0,
                {'found':True,'reservation':history,'current':{'state':'active','version':1}})
        cancelled=booking.cancel(database,rid,trusted_member_id=request['trusted_member_id'],expected_version=1)
        report['fixture_operations'].append({'call':'booking.cancel','args':[str(database),rid],
             'kwargs':{'trusted_member_id':request['trusted_member_id'],'expected_version':1},
             'result':cancelled,'state_sha256':inventory(state_dir)})
        # RES-002/v1 fixes status, code and the incremented version; it does not fix the
        # result's complete key set. Edition 5.0 compared the reference dictionary exactly
        # and blocked a native candidate that also returned reservation_id (16 Nov 2026).
        contracted=(cancelled.get('status'),cancelled.get('code'),cancelled.get('version')) if isinstance(cancelled,dict) else None
        if contracted!=(200,'cancelled',2):
            raise ValueError('Public cancellation did not establish the authored fixture.')
        process('cancelled_record_preserves_history',base+[str(rid)],0,
                {'found':True,'reservation':history,'current':{'state':'cancelled','version':2}})
        process('absent_identifier',base+[str(rid+1000)],3,
                {'found':False,'reservation':None,'current':None})
        missing=state_dir/'missing.sqlite'
        process('missing_storage_is_not_created',
                [sys.executable,'-B','reservation_cli.py','inspect','--database',str(missing),'--reservation-id','1'],2,error=True)
        for raw in ['0','-1','abc']:
            process('invalid_identifier_'+raw,base+[raw],2,error=True)
        process('missing_required_argument',
                [sys.executable,'-B','reservation_cli.py','inspect','--database',str(database)],2,error=True)
    except Exception as exc:
        report['failure']={'type':type(exc).__name__,'message':str(exc)}
    report['package_sha256_after']=inventory(package)
    report['package_unchanged']=before==report['package_sha256_after']
    report['status']='TRANSPORT_CHECKS_PASSED' if (len(report['cases'])==9 and all(r['passed'] for r in report['cases']) and report['package_unchanged'] and 'failure' not in report) else 'TRANSPORT_CHECKS_FAILED'
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as stream:stream.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'cases':len(report['cases']),'receipt':str(output)}))
    return 0 if report['status']=='TRANSPORT_CHECKS_PASSED' else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--state-dir',required=True,type=Path)
    args=parser.parse_args()
    return verify(args.package,args.output,args.state_dir)


if __name__=='__main__':raise SystemExit(main())
