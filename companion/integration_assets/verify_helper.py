#!/usr/bin/env python3
"""Exercise the reusable integration lifecycle using one retained actual bundle.

This is a replay of recorded source bytes, not a new agent/model observation.
Its new Git commits and check processes are actual local helper operations.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile

COMPANION=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(COMPANION))
import integration
import curriculum


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',required=True,type=Path)
    parser.add_argument('--recorded-report',required=True,type=Path)
    parser.add_argument('--workdir',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    work=args.workdir.resolve();output=args.output.resolve()
    if work.exists() or output.exists():raise ValueError('Use fresh work and output paths; prior runs remain retained.')
    work.mkdir(parents=True)
    report={'schema':'esa-integration-helper-test/v1','recorded_at_utc':datetime.now(timezone.utc).isoformat(),
            'origin':'REPLAY_OF_RETAINED_ACTUAL_SOURCE_BUNDLE','model_run':False,
            'human_acceptance':'PENDING','checks':[],'commands':[]}
    def check(name,ok,details):
        report['checks'].append({'check':name,'passed':bool(ok),'details':details})
        if not ok:raise ValueError(name)
    def command(label,argv,expected=0):
        env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env.pop('PYTHONPATH',None)
        done=subprocess.run([str(v) for v in argv],cwd=work,env=env,capture_output=True,text=True,timeout=60)
        row={'label':label,'argv':[str(v) for v in argv],'cwd':str(work),'returncode':done.returncode,
             'stdout':done.stdout,'stderr':done.stderr}
        report['commands'].append(row)
        integration.json_write(work/(label+'.json'),row)
        check(label+'_exit',done.returncode==expected,{'expected':expected,'observed':done.returncode})
        return row
    try:
        actual=json.loads(args.recorded_report.read_text());group=args.recorded_report.resolve().parent
        bundle=group/actual['transport']['archive']
        check('recorded_bundle_identity',integration.sha(bundle)==actual['transport']['archive_sha256'],str(bundle))
        retained=work/'recorded_bundle';retained.mkdir()
        with zipfile.ZipFile(bundle) as archive:
            for item in archive.infolist():
                name=Path(item.filename)
                if name.is_absolute() or '..' in name.parts:raise ValueError('Unsafe recorded archive member.')
                dest=retained/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(archive.read(item))
        check('recorded_extraction_identity',integration.inventory(retained)==actual['transport']['payload_file_sha256'],
              {'source_sha256':{name:integration.sha(retained/name) for name in integration.SOURCES}})
        candidate=args.candidate.resolve()
        check('same_retained_g3_source',integration.sha(candidate/'booking.py')==integration.sha(retained/'booking.py'),str(candidate))
        prepared=work/'prepared'
        command('prepare',[sys.executable,str(COMPANION/'integration.py'),'prepare','--candidate',candidate,'--dest',prepared])
        manifest=json.loads((prepared/'INTEGRATION.json').read_text())
        role_copy=[]
        for role,row in manifest['roles'].items():
            workspace=prepared/row['workspace']
            metadata=json.loads((workspace/'INTEGRATION_ROLE.json').read_text())
            check(role+'_role_metadata',metadata['role']==role and metadata['editable_paths']==row['editable_paths'],metadata)
            before=integration.inventory(workspace)
            for name in row['editable_paths']:shutil.copy2(retained/name,workspace/name)
            after=integration.inventory(workspace)
            role_copy.append({'role':role,'origin':'Retained actual source replay; no model invoked.',
                              'changed_files':integration.changed(before,after),
                              'copied_sha256':{name:integration.sha(workspace/name) for name in row['editable_paths']}})
        integration.json_write(work/'source_replay.json',role_copy)
        result=prepared/'REPORT.json'
        command('combine',[sys.executable,str(COMPANION/'integration.py'),'combine','--workspace',prepared/'workspace','--output',result])
        combined=json.loads(result.read_text())
        check('reusable_combination_passed',combined['status']=='INTEGRATION_CHECKS_PASSED',
              {'receipt':str(result),'sha256':integration.sha(result)})
        check('replayed_source_bytes_match_actual',combined['source_sha256']==actual['source_sha256'],combined['source_sha256'])
        check('reusable_transport_cases',combined['transport']['checked_cli_cases']==9,combined['transport']['cli_receipt'])
        next_candidate=work/'g4'
        command('advance_g4',[sys.executable,str(COMPANION/'start.py'),'advance','G4','--from-candidate',prepared/'workspace','--dest',next_candidate])
        entry=json.loads((next_candidate/'READER_ENTRY.json').read_text())
        binding=curriculum.integration_binding(next_candidate,entry,required=True)
        check('g4_retains_integrated_sources',binding['record']['source_sha256']==actual['source_sha256'] and
              all(entry['dependency_sha256'][name]==actual['source_sha256'][name] for name in integration.SOURCES),
              {'source_sha256':binding['record']['source_sha256'],'local_receipt':entry['integration']['receipt']})
        check('g4_retains_source_snapshots',all(integration.sha(next_candidate/'prior/integration'/name)==digest for name,digest in actual['source_sha256'].items()),
              'All three integrated modules have local lineage snapshots.')
        damaged=work/'g4_controlled_source_change';integration.snapshot(next_candidate,damaged)
        with (damaged/'reservation_report.py').open('a') as stream:stream.write('\n# Deliberate isolated integrity-test change.\n')
        refusal=work/'g4_changed_source_refusal.json'
        command('reject_changed_integrated_source',[sys.executable,str(COMPANION/'start.py'),'check','G4','--candidate',damaged,'--output',refusal],expected=1)
        refused=json.loads(refusal.read_text())
        check('changed_source_blocks_before_tests',refused['status']=='INPUT_INTEGRITY_FAILED' and refused['tests_run']==0,
              {'status':refused['status'],'protected_changes':refused['protected_changes']})
        command('reject_unintegrated_g4_advance',[sys.executable,str(COMPANION/'start.py'),'advance','G4','--from-candidate',candidate,'--dest',work/'unintegrated_g4'],expected=2)
        check('unintegrated_g4_not_created',not (work/'unintegrated_g4').exists(),'The original G3 candidate has no accepted integration receipt.')
        report['status']='PASSED'
        report['limits']=['Source replay does not create a new agent observation.','The G4 starter still requires implementation; no G4 acceptance is claimed.','The controlled changed-source case is a deliberate test, not an observed model failure.']
    except Exception as exc:
        report['status']='FAILED';report['failure']={'type':type(exc).__name__,'message':str(exc)}
    integration.json_write(output,report)
    print(json.dumps({'status':report['status'],'checks':len(report['checks']),'receipt':str(output),'failure':report.get('failure')},indent=2))
    return 0 if report['status']=='PASSED' else 1


if __name__=='__main__':raise SystemExit(main())
