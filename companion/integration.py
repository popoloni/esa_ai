#!/usr/bin/env python3
"""Prepare paired G3 worktrees and independently check their real composition.

Git is a local teaching dependency. This helper never calls a model or pushes a
repository. Process receipts retain failures; checks do not grant human or
production authority. Run the contributions before invoking combine.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'integration_assets'
SKIP={'.git','__pycache__','.pytest_cache'}
SOURCES=('booking.py','reservation_report.py','reservation_cli.py')
ROLES={'report':{'module':'reservation_report.py','note':'CONTRIBUTION_A.md','test':'test_integration_a.py'},
       'cli':{'module':'reservation_cli.py','note':'CONTRIBUTION_B.md','test':'test_integration_b.py'}}
AUTHORITY={'principal':'ESA AI integration reviewer / recording operator',
           'kind':'AI reviewer and local recording operator',
           'authorized_by':'Author instruction to implement ESA agent-process remediation',
           'scope':'Scoped teaching integration, independent checks and provenance recording',
           'human_operator':False,'human_acceptance':'PENDING','production_authorization':False}


def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def json_write(path,value,*,exclusive=True):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x' if exclusive else 'w',encoding='utf-8') as stream:
        stream.write(json.dumps(value,indent=2)+'\n')
def inventory(path):
    result={}
    for item in sorted(Path(path).rglob('*')):
        relative=item.relative_to(path)
        if any(part in SKIP for part in relative.parts):continue
        if item.is_symlink():raise ValueError('Symlink is outside the candidate snapshot contract: '+str(item))
        if item.is_file():result[str(relative)]=sha(item)
    return result

def snapshot(source,target):
    target.mkdir(parents=True)
    for name in inventory(source):
        dest=target/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/name,dest)

def changed(before,after):
    return sorted(name for name in set(before)|set(after) if before.get(name)!=after.get(name))

def aggregate(hashes):
    return hashlib.sha256(json.dumps(hashes,sort_keys=True,separators=(',',':')).encode()).hexdigest()


class Recorder:
    def __init__(self,group):
        self.group=group;self.folder=group/'operator';self.folder.mkdir(exist_ok=True)
    def event(self,label,data):
        used=[int(p.name.split('_',1)[0]) for p in self.folder.glob('[0-9][0-9][0-9]_*.json')]
        path=self.folder/f'{max(used,default=0)+1:03d}_{label}.json'
        json_write(path,{'recorded_at_utc':now(),'operation':label,'authority':AUTHORITY,**data})
        return path
    def run(self,label,argv,cwd,*,expected=0,timeout=45):
        argv=[str(v) for v in argv]
        env=os.environ.copy();env.pop('PYTHONSTARTUP',None);env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONPATH']=str(cwd)
        started=time.monotonic()
        try:
            done=subprocess.run(argv,cwd=cwd,env=env,capture_output=True,text=True,timeout=timeout)
            result={'returncode':done.returncode,'stdout':done.stdout,'stderr':done.stderr,'timed_out':False}
        except subprocess.TimeoutExpired as exc:
            def decode(v):return v.decode(errors='replace') if isinstance(v,bytes) else v or ''
            result={'returncode':None,'stdout':decode(exc.stdout),'stderr':decode(exc.stderr),'timed_out':True}
        result.update(argv=argv,cwd=str(cwd),timeout_seconds=timeout,elapsed_process_seconds=time.monotonic()-started)
        path=self.event(label,result);result['operation_receipt']=str(path.relative_to(self.group))
        if expected is not None and result['returncode']!=expected:
            raise ValueError(f'{label} returned {result["returncode"]}; retained {path}. '+result['stderr'][-1200:])
        return result
    def git(self,label,args,cwd):return self.run(label,['git',*args],cwd)


def git_value(rec,label,args,path):return rec.git(label,args,path)['stdout'].strip()

def suite(rec,label,workspace,pattern,count):
    result=rec.run(label,[sys.executable,'-B','-m','unittest','discover','-s','tests','-p',pattern,'-v'],workspace)
    found=re.search(r'Ran (\d+) tests?',result['stdout']+result['stderr'])
    observed=int(found[1]) if found else 0
    if observed!=count:raise ValueError(f'{label} ran {observed}, expected {count}; command retained.')
    return {'status':'PASSED','tests_run':observed,'operation_receipt':result['operation_receipt']}


def mission_gate(rec,label,workspace,command='check'):
    output=rec.folder/(label+'_receipt.json')
    # Repeated attempts retain distinct receipt paths.
    if output.exists():
        output=rec.folder/(label+'_'+str(len(list(rec.folder.glob('*.json'))))+'_receipt.json')
    run=rec.run(label,[sys.executable,str(ROOT/'start.py'),command,'G3','--candidate',str(workspace),'--output',str(output)],ROOT,timeout=60)
    data=json.loads(output.read_text())
    expected='SCOPED_HANDOFF_READY' if command=='continue' else 'SELECTED_CHECKS_PASSED'
    if data['status']!=expected:raise ValueError(label+' did not establish '+expected)
    return {'status':data['status'],'tests_run':data['tests_run'],
            'receipt':str(output.relative_to(rec.group)),'sha256':sha(output),
            'operation_receipt':run['operation_receipt']}


def prepare(args):
    import start as common
    candidate=common.external(args.candidate)
    dest=common.external(args.dest,output=True)
    if dest==candidate or dest.is_relative_to(candidate):raise ValueError('Keep integration work outside the original candidate.')
    entry=common.load_entry('G3',candidate)
    if entry.get('mode')!='LEARNER':
        raise ValueError('Prepare an actual G3 learner candidate, not a reference or another mission.')
    if entry.get('integration'):raise ValueError('This G3 already has an integration record; retain it rather than replacing it.')
    if not shutil.which('git'):raise ValueError('Install Git as the local worktree dependency.')
    dest.mkdir(parents=True);rec=Recorder(dest)
    parent_check=mission_gate(rec,'parent_g3_handoff',candidate,'continue')
    main=dest/'workspace';snapshot(candidate,main)
    for name in ['reservation_report.py','reservation_cli.py','docs/INTEGRATION-G3.md','tests/test_integration_a.py','tests/test_integration_b.py']:
        target=main/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ASSETS/name,target)
    (main/'AGENTS.md').write_text('# G3 integration scope\n\nBooking and all docs/tests/dependencies/prior state are protected.\nThe report role owns reservation_report.py and CONTRIBUTION_A.md.\nThe CLI role owns reservation_cli.py and CONTRIBUTION_B.md.\nRead INTEGRATION_ROLE.json and docs/INTEGRATION-G3.md before editing.\nDo not commit or integrate; the recording operator retains those steps.\nNo network, dependency installation or production action is authorized.\nThis file is an instruction, not an operating-system boundary.\n')
    rec.git('initialize_repository',['init','-b','integration'],main)
    rec.git('stage_shared_baseline',['add','--',*inventory(main)],main)
    rec.git('commit_shared_baseline',['-c','user.name=ESA AI recording operator','-c','user.email=esa-ai-recording@example.invalid','commit','-m','Freeze retained G3 and shared integration contract'],main)
    base=git_value(rec,'record_baseline_commit',['rev-parse','HEAD'],main)
    specification={'schema':'esa-g3-integration/v1','created_at_utc':now(),'contract':'INTEGRATION-G3/v1',
        'main_workspace':'workspace','baseline_commit':base,'main_baseline_sha256':inventory(main),
        'parent_candidate':str(candidate),'parent_booking_sha256':sha(candidate/'booking.py'),
        'parent_handoff':parent_check,'shared_contract':'docs/INTEGRATION-G3.md',
        'asset_sha256':{name:sha(ASSETS/name) for name in ['docs/INTEGRATION-G3.md','tests/test_integration_a.py','tests/test_integration_b.py']},
        'roles':{},'authority':AUTHORITY}
    for role,row in ROLES.items():
        workspace=dest/'worktrees'/role
        workspace.parent.mkdir(exist_ok=True)
        rec.git('create_'+role+'_worktree',['worktree','add','-b','contribution-'+role,str(workspace),base],main)
        metadata={'schema':'esa-integration-role/v1','role':role,'contract':'INTEGRATION-G3/v1',
                  'editable_paths':[row['module'],row['note']],
                  'shared_contract':'docs/INTEGRATION-G3.md','shared_contract_sha256':sha(main/'docs/INTEGRATION-G3.md'),
                  'integration_manifest':os.path.relpath(dest/'INTEGRATION.json',workspace),
                  'baseline_commit':base,'component_test':row['test'],
                  'scope':'One contribution only; operator combines and independently checks the real transport bundle.'}
        json_write(workspace/'INTEGRATION_ROLE.json',metadata)
        baseline=dest/'baselines'/role;snapshot(workspace,baseline)
        specification['roles'][role]={**row,'workspace':str(workspace.relative_to(dest)),
            'baseline':str(baseline.relative_to(dest)),'baseline_sha256':inventory(baseline),
            'baseline_commit':base,'editable_paths':metadata['editable_paths']}
    json_write(dest/'INTEGRATION.json',specification)
    rec.event('preparation_complete',{'manifest':'INTEGRATION.json','sha256':sha(dest/'INTEGRATION.json'),
                                    'parent_unchanged':sha(candidate/'booking.py')==specification['parent_booking_sha256']})
    print(json.dumps({'status':'PAIRED_WORKTREES_PREPARED','group':str(dest),
                      'manifest':str(dest/'INTEGRATION.json'),
                      'worktrees':{role:str((dest/row['workspace']).resolve()) for role,row in specification['roles'].items()}},indent=2))
    return 0


def locate(args):
    workspace=Path(args.workspace).resolve()
    candidates=[Path(args.manifest).resolve()] if args.manifest else [workspace/'INTEGRATION.json',workspace.parent/'INTEGRATION.json']
    manifest=next((p for p in candidates if p.is_file()),None)
    if manifest is None:raise ValueError('Supply an explicit INTEGRATION.json manifest for this workspace layout.')
    spec=json.loads(manifest.read_text());group=manifest.parent
    main=(group/spec['main_workspace']).resolve()
    if workspace not in (main,group):raise ValueError('Workspace differs from the manifest main workspace.')
    if spec.get('schema')!='esa-g3-integration/v1' or set(spec['roles'])!=set(ROLES):raise ValueError('Unsupported integration manifest.')
    if spec.get('contract')!='INTEGRATION-G3/v1':
        raise ValueError('Unsupported integration contract.')
    expected_assets={'docs/INTEGRATION-G3.md','tests/test_integration_a.py','tests/test_integration_b.py'}
    if set(spec.get('asset_sha256',{}))!=expected_assets:
        raise ValueError('Integration manifest must bind the shared contract and both protected component tests.')
    for role,canonical in ROLES.items():
        row=spec['roles'][role]
        if (any(row.get(key)!=value for key,value in canonical.items())
                or set(row.get('editable_paths',[]))!={canonical['module'],canonical['note']}
                or row.get('baseline_commit')!=spec['baseline_commit']):
            raise ValueError('Integration manifest changes the authorized role scope or shared baseline: '+role)
    return group,main,manifest,spec


def make_bundle(main,target):
    hashes=inventory(main);target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for name in hashes:
            item=zipfile.ZipInfo(name,(1980,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o100644<<16
            archive.writestr(item,(main/name).read_bytes())
    return hashes


def combine(args):
    group,main,manifest,spec=locate(args)
    output=Path(args.output).resolve()
    if output.exists():raise ValueError('Receipt already exists; retain it and use a new output name.')
    if output.is_relative_to(main):raise ValueError('Keep integration receipts outside candidate inputs.')
    rec=Recorder(group)
    report={'schema':'esa-g3-integration-report/v1','started_at_utc':now(),'manifest':str(manifest),
            'manifest_sha256':sha(manifest),'workspace':str(main),'authority':AUTHORITY,
            'model_run_by_helper':False,'claim_scope':'Actual contributed sources, local Git composition and specified independent checks; no measured speedup or production authorization.'}
    state_path=group/'STATE.json'
    state=json.loads(state_path.read_text()) if state_path.exists() else {'role_commits':{},'cherry_picked':[]}
    def save_state(label):
        rec.event(label,{'state':state})
        json_write(state_path,state,exclusive=False)
    try:
        from start import load_entry
        entry=load_entry('G3',main)
        if entry.get('mode')!='LEARNER':raise ValueError('Combined workspace is not the retained learner G3.')
        if entry.get('integration'):raise ValueError('Integration already recorded in this candidate; do not replace its receipt.')
        if sha(main/'booking.py')!=spec['parent_booking_sha256']:raise ValueError('Retained booking source differs from the accepted G3 parent.')
        for name,digest in spec['asset_sha256'].items():
            if sha(ASSETS/name)!=digest or sha(main/name)!=digest:
                raise ValueError('Shared contract/protected component tests differ from the prepared assets: '+name)
        allowed=set().union(*(set(r['editable_paths']) for r in spec['roles'].values()))
        main_changes=changed(spec['main_baseline_sha256'],inventory(main))
        if set(main_changes)-allowed:raise ValueError('Protected main-workspace changes: '+str(set(main_changes)-allowed))
        scope={};components={}
        common_git=Path(git_value(rec,'main_git_directory',['rev-parse','--git-common-dir'],main))
        common_git=(main/common_git).resolve() if not common_git.is_absolute() else common_git.resolve()
        for role,row in spec['roles'].items():
            workspace=(group/row['workspace']).resolve();baseline=(group/row['baseline']).resolve()
            before=inventory(baseline);after=inventory(workspace)
            if before!=row['baseline_sha256']:raise ValueError('Retained contributor baseline changed: '+role)
            delta=changed(before,after)
            if set(delta)-set(row['editable_paths']):raise ValueError('Contributor exceeded scope: '+role+' '+str(delta))
            if not all((workspace/name).is_file() for name in row['editable_paths']):raise ValueError('Contributor source/note missing: '+role)
            git_dir=Path(git_value(rec,role+'_git_directory',['rev-parse','--git-common-dir'],workspace))
            git_dir=(workspace/git_dir).resolve() if not git_dir.is_absolute() else git_dir.resolve()
            if git_dir!=common_git:raise ValueError('Contributions are not worktrees of the same repository.')
            head=git_value(rec,role+'_head_before',['rev-parse','HEAD'],workspace)
            expected=state['role_commits'].get(role,row['baseline_commit'])
            if head!=expected:raise ValueError('Unrecorded contributor commit: '+role)
            scope[role]={'changed_files':delta,'allowed_files':row['editable_paths'],
                         'baseline_sha256':before,'actual_sha256':after,'head_before':head}
            rec.event(role+'_scope_review',scope[role])
            components[role]=suite(rec,role+'_component_check',workspace,row['test'],3)
        report['contributor_scope']=scope;report['component_checks']=components
        for role,row in spec['roles'].items():
            workspace=(group/row['workspace']).resolve()
            if role not in state['role_commits']:
                rec.git('stage_'+role+'_contribution',['add','--',*row['editable_paths']],workspace)
                staged=git_value(rec,role+'_staged_paths',['diff','--cached','--name-only'],workspace).splitlines()
                if set(staged)!=set(row['editable_paths']):raise ValueError('Unexpected staged contribution paths: '+role+' '+str(staged))
                rec.git('record_'+role+'_contribution',['-c','user.name=ESA AI recording operator','-c','user.email=esa-ai-recording@example.invalid','commit','-m','Record actual '+role+' contribution under INTEGRATION-G3/v1'],workspace)
                commit=git_value(rec,role+'_commit_identity',['rev-parse','HEAD'],workspace)
                state['role_commits'][role]=commit;save_state(role+'_commit_bound')
            if role not in state['cherry_picked']:
                rec.git('combine_'+role+'_contribution',['-c','user.name=ESA AI recording operator','-c','user.email=esa-ai-recording@example.invalid','cherry-pick',state['role_commits'][role]],main)
                state['cherry_picked'].append(role);save_state(role+'_combined')
        combined_commit=git_value(rec,'combined_commit_identity',['rev-parse','HEAD'],main)
        source_hashes={name:sha(main/name) for name in SOURCES}
        if source_hashes['booking.py']!=spec['parent_booking_sha256']:
            raise ValueError('Composition changed the protected retained G3 implementation.')
        for role,row in spec['roles'].items():
            if sha(main/row['module'])!=scope[role]['actual_sha256'][row['module']]:
                raise ValueError('Combined module differs from the actual contribution: '+role)
        report['combined_commit']=combined_commit;report['source_sha256']=source_hashes
        report['combined_component_checks']={role:suite(rec,'combined_'+role+'_check',main,row['test'],3) for role,row in ROLES.items()}
        report['combined_g3_handoff']=mission_gate(rec,'combined_g3_handoff',main,'continue')
        attempt=len(list((group/'packages').glob('*.zip')))+1
        bundle=group/'packages'/f'integration-{attempt:03d}.zip'
        payload=make_bundle(main,bundle)
        extracted=group/'extracted'/f'integration-{attempt:03d}';extracted.mkdir(parents=True)
        with zipfile.ZipFile(bundle) as archive:
            for item in archive.infolist():
                name=Path(item.filename)
                if name.is_absolute() or '..' in name.parts:raise ValueError('Unsafe transport member name.')
                target=extracted/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.read(item))
        extracted_hashes=inventory(extracted)
        if payload!=extracted_hashes:raise ValueError('Extracted transport bytes differ from the combined snapshot.')
        transport={'archive':str(bundle.relative_to(group)),'archive_sha256':sha(bundle),
                   'extracted':str(extracted.relative_to(group)),
                   'payload_file_sha256':payload,'extracted_file_sha256':extracted_hashes,
                   'payload_identity_sha256':aggregate(payload),'extracted_identity_sha256':aggregate(extracted_hashes),
                   'snapshot_scope':'Combined candidate before adding acceptance metadata; all runnable source bytes are bound.',
                   'source_sha256':{name:sha(extracted/name) for name in SOURCES}}
        rec.event('transport_snapshot_bound',transport)
        report['extracted_component_checks']={role:suite(rec,'extracted_'+role+'_check',extracted,row['test'],3) for role,row in ROLES.items()}
        report['extracted_g3_check']=mission_gate(rec,'extracted_g3_check',extracted)
        transport_receipt=rec.folder/f'transport-{attempt:03d}.json'
        process=rec.run('real_extracted_cli_contract',[sys.executable,'-B',str(ASSETS/'verify_transport.py'),
            '--package',str(extracted),'--output',str(transport_receipt),
            '--state-dir',str(group/'transport-state'/f'attempt-{attempt:03d}')],group,timeout=60)
        cli=json.loads(transport_receipt.read_text())
        if cli['status']!='TRANSPORT_CHECKS_PASSED':raise ValueError('Independent real CLI contract failed; receipt retained.')
        if inventory(extracted)!=payload or inventory(main)!=payload:raise ValueError('Source inputs changed during independent acceptance.')
        transport.update(checked_cli_cases=len(cli['cases']),cli_receipt=str(transport_receipt.relative_to(group)),
                         cli_receipt_sha256=sha(transport_receipt),operation_receipt=process['operation_receipt'])
        report['transport']=transport
        acceptance={'schema':'esa-integration-acceptance/v1','status':'INTEGRATION_CHECKS_PASSED',
                    'contract':spec['contract'],'source_sha256':source_hashes,'combined_commit':combined_commit,
                    'contribution_commits':state['role_commits'],'transport':transport,'authority':AUTHORITY,
                    'component_checks':report['combined_component_checks'],
                    'g3_handoff':report['combined_g3_handoff'],'extracted_g3_check':report['extracted_g3_check']}
        acceptance_path=rec.event('integration_acceptance',acceptance)
        record={'schema':'esa-accepted-integration/v1','contract':spec['contract'],
                'status':'INTEGRATION_CHECKS_PASSED','source_sha256':source_hashes,
                'receipt':os.path.relpath(acceptance_path,main),'receipt_sha256':sha(acceptance_path),
                'bundle_sha256':transport['archive_sha256'],'combined_commit':combined_commit,'authority':AUTHORITY}
        before_entry=sha(main/'READER_ENTRY.json');entry['integration']=record
        entry['dependency_sha256'].update({name:source_hashes[name] for name in SOURCES if name!='booking.py'})
        json_write(main/'READER_ENTRY.json',entry,exclusive=False)
        rec.event('bind_integration_lineage',{'entry_sha256_before':before_entry,'entry_sha256_after':sha(main/'READER_ENTRY.json'),'integration':record})
        rec.git('stage_integration_lineage',['add','--','READER_ENTRY.json'],main)
        rec.git('commit_integration_lineage',['-c','user.name=ESA AI recording operator','-c','user.email=esa-ai-recording@example.invalid','commit','-m','Bind independently checked integration to retained G3 lineage'],main)
        report['accepted_commit']=git_value(rec,'accepted_commit_identity',['rev-parse','HEAD'],main)
        report['accepted_entry_sha256']=sha(main/'READER_ENTRY.json')
        report['acceptance_receipt']=str(acceptance_path.relative_to(group));report['acceptance_receipt_sha256']=sha(acceptance_path)
        report['status']='INTEGRATION_CHECKS_PASSED'
    except Exception as exc:
        report['status']='INTEGRATION_BLOCKED';report['failure']={'type':type(exc).__name__,'message':str(exc)}
        rec.event('integration_blocked',report['failure'])
    report['finished_at_utc']=now()
    report['operator_receipts_sha256']={str(p.relative_to(group)):sha(p) for p in sorted(rec.folder.glob('*.json'))}
    json_write(output,report)
    print(json.dumps({'status':report['status'],'receipt':str(output),'failure':report.get('failure')},indent=2))
    return 0 if report['status']=='INTEGRATION_CHECKS_PASSED' else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('--candidate',required=True,type=Path);p.add_argument('--dest',required=True,type=Path)
    c=sub.add_parser('combine');c.add_argument('--workspace',required=True,type=Path);c.add_argument('--output',required=True,type=Path);c.add_argument('--manifest',type=Path)
    args=parser.parse_args()
    try:
        return prepare(args) if args.command=='prepare' else combine(args)
    except (ValueError,OSError,KeyError) as exc:
        print('REFUSED: '+str(exc),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
