#!/usr/bin/env python3
"""Six later missions behind start.py; standard library, offline fixtures only."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent
MANIFEST=ROOT/'curriculum/MANIFEST.json'


def manifest():return json.loads(MANIFEST.read_text())['missions']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def integration_binding(candidate,entry,*,required=False):
    """Verify the exact accepted G3 composition before forwarding or checking it."""
    record=entry.get('integration')
    if record is None:
        if required:
            raise ValueError('G4 advances the retained integrated G3. Run integration.py prepare/combine and retain its passing receipt first.')
        return None
    names={'booking.py','reservation_report.py','reservation_cli.py'}
    if (record.get('schema')!='esa-accepted-integration/v1'
            or record.get('contract')!='INTEGRATION-G3/v1'
            or record.get('status')!='INTEGRATION_CHECKS_PASSED'
            or set(record.get('source_sha256',{}))!=names):
        raise ValueError('Unrecognized or incomplete accepted integration record.')
    receipt=candidate/record['receipt']
    if (not receipt.is_file() or any(p.is_symlink() for p in [receipt,*receipt.parents])
            or sha(receipt)!=record['receipt_sha256']):
        raise ValueError('Accepted integration receipt bytes differ or are unavailable.')
    accepted=json.loads(receipt.read_text())
    transport=accepted.get('transport',{})
    if (accepted.get('schema')!='esa-integration-acceptance/v1'
            or accepted.get('contract')!=record['contract']
            or accepted.get('status')!='INTEGRATION_CHECKS_PASSED'
            or accepted.get('source_sha256')!=record['source_sha256']
            or transport.get('source_sha256')!=record['source_sha256']
            or transport.get('archive_sha256')!=record['bundle_sha256']
            or transport.get('payload_file_sha256')!=transport.get('extracted_file_sha256')
            or transport.get('payload_identity_sha256')!=transport.get('extracted_identity_sha256')):
        raise ValueError('Integration receipt does not bind the same checked composition and transport.')
    payload=transport['payload_file_sha256']
    identity=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if identity!=transport['payload_identity_sha256']:
        raise ValueError('Integration transport inventory does not match its identity.')
    for name,digest in record['source_sha256'].items():
        source=candidate/name
        if not source.is_file() or source.is_symlink() or sha(source)!=digest or payload.get(name)!=digest:
            raise ValueError('Accepted integration source differs: '+name)
    return {'record':record,'receipt':receipt,'accepted':accepted}


# OPS-G4/v3 names three current representations. A lineage whose G3 keeps its
# reservations elsewhere receives G4-OD-01, a recorded owner mapping, at advance.
G4_NAMED=(('reservations',('id','asset_id','member_id','starts_at','ends_at','request_key','request_hash','state','version')),
          ('reservations_v2',('reservation_id','trusted_member_id','asset_id','starts_at','ends_at','idempotency_key','payload_fingerprint','state','version')),
          ('reservations_v2',('id','trusted_member_id','asset_id','starts_at','ends_at','idempotency_key','fingerprint','state','version')))
# Each role accepts only the column names the three named layouts already use.
G4_ROLE_NAMES={'id':('id','reservation_id'),'asset_id':('asset_id',),'member_id':('member_id','trusted_member_id'),
               'starts_at':('starts_at',),'ends_at':('ends_at',),'request_key':('request_key','idempotency_key'),
               'request_hash':('request_hash','payload_fingerprint','fingerprint'),'state':('state',),'version':('version',)}
G4_LAYOUT_PROBE=r'''
import json,sqlite3,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import booking
db=Path(sys.argv[2]);booking.init_db(db)
con=sqlite3.connect(db);tables={}
for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
    tables[name]=[{'name':r[1],'type':r[2],'pk':r[5]} for r in con.execute('PRAGMA table_info("'+name.replace('"','""')+'")')]
print(json.dumps({'user_version':con.execute('PRAGMA user_version').fetchone()[0],'tables':tables}))
'''


def g4_layout_probe(workspace):
    """Initialize fresh storage with the retained booking.py and list its tables."""
    with tempfile.TemporaryDirectory(prefix='esa-g4-layout-') as temp:
        result=subprocess.run([sys.executable,'-I','-B','-c',G4_LAYOUT_PROBE,str(workspace),str(Path(temp)/'probe.sqlite')],
                              text=True,capture_output=True,timeout=60,cwd=temp)
    if result.returncode:
        raise ValueError('The retained booking.init_db could not create storage for the G4 layout probe: '+result.stderr[-800:])
    return json.loads(result.stdout)


def g4_owner_mapping(workspace,supplied=None):
    """Return None for a named OPS-G4/v3 layout, else the recorded G4-OD-01 mapping."""
    probe=g4_layout_probe(workspace)
    tables=probe['tables']
    if probe['user_version']!=3:
        raise ValueError('G4 requires retained G3 storage at schema version 3; init_db produced version '+str(probe['user_version'])+'.')
    named=[table for table,signature in G4_NAMED if tuple(c['name'] for c in tables.get(table,[]))==signature]
    if named:
        if supplied is not None:
            raise ValueError('This lineage already uses a representation named by OPS-G4/v3; no owner mapping is needed.')
        return None
    if supplied is not None:
        data=json.loads(Path(supplied).read_text(encoding='utf-8'))
        table,roles=data.get('table'),data.get('roles')
        if not isinstance(table,str) or not isinstance(roles,dict):
            raise ValueError('A schema map is a JSON object with "table" and "roles".')
        origin='OPERATOR_SUPPLIED_AND_CHECKED'
    else:
        qualifying=[]
        for table,columns in tables.items():
            names=[c['name'] for c in columns]
            roles={role:found[0] for role,allowed in G4_ROLE_NAMES.items()
                   for found in [[n for n in names if n in allowed]] if len(found)==1}
            if len(roles)==len(G4_ROLE_NAMES)==len(names):
                qualifying.append((table,roles))
        if len(qualifying)!=1:
            listing='; '.join(t+'('+', '.join(c['name'] for c in cols)+')' for t,cols in tables.items()) or 'none'
            raise ValueError(('No' if not qualifying else 'More than one')+' table created by the retained booking.init_db '
                             'maps onto the nine OPS-G4 roles by the column names the named layouts use. Tables: '+listing+'. '
                             'Acting for the owner, write a schema map {"table": ..., "roles": {"id", "asset_id", "member_id", '
                             '"starts_at", "ends_at", "request_key", "request_hash", "state", "version"}} and rerun advance '
                             'with --schema-map FILE, or start the standalone route with new G4.')
        table,roles=qualifying[0]
        origin='DERIVED_FROM_NAMED_COLUMNS'
    columns=tables.get(table)
    if columns is None:
        raise ValueError('Mapped table '+repr(table)+' is not created by the retained booking.init_db.')
    names=[c['name'] for c in columns]
    if set(roles)!=set(G4_ROLE_NAMES) or len(set(roles.values()))!=len(roles) or sorted(roles.values())!=sorted(names):
        raise ValueError('Map each of the nine roles to a distinct column, covering every column of '+table+'.')
    identifier=next(c for c in columns if c['name']==roles['id'])
    if identifier['pk']!=1 or 'INT' not in identifier['type'].upper() or sum(1 for c in columns if c['pk'])!=1:
        raise ValueError('The id role must be the INTEGER PRIMARY KEY of '+table+'.')
    return {'schema':'esa-g4-schema-map/v1','decision':'G4-OD-01','extends':'OPS-G4/v3','origin':origin,
            'table':table,'signature':names,'roles':{role:roles[role] for role in G4_ROLE_NAMES},
            'schema_version':3,'booking_sha256':sha(workspace/'booking.py'),'tables_created_by_init_db':sorted(tables)}


def g4_install_owner_mapping(dest,mapping):
    origin={'DERIVED_FROM_NAMED_COLUMNS':'Each of its columns uses a name that one of the three named '
            'representations already uses for the same role, so the mapping below follows from them.',
            'OPERATOR_SUPPLIED_AND_CHECKED':'The operator, acting for the owner, supplied the role mapping below; '
            'the companion checked it against the columns that the retained init_db creates.'}[mapping['origin']]
    rows='\n'.join('| '+role+' | `'+column+'` |' for role,column in mapping['roles'].items())
    text=(ROOT/'contracts/G4_OWNER_MAPPING.md').read_text(encoding='utf-8')
    for key,value in (('@BOOKING_SHA256@',mapping['booking_sha256']),('@TABLE@',mapping['table']),('@ORIGIN@',origin),
                      ('@SIGNATURE@',', '.join(mapping['signature'])),('@ROLE_ROWS@',rows)):
        text=text.replace(key,value)
    (dest/'docs').mkdir(exist_ok=True)
    (dest/'docs/G4-OD-01.md').write_text(text,encoding='utf-8')
    (dest/'docs/G4-SCHEMA-MAP.json').write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
    return ['docs/G4-OD-01.md','docs/G4-SCHEMA-MAP.json']


def create(args,reference=False):
    import start as common
    spec=manifest()[args.mission]
    dest=common.external(args.dest,output=True)
    source=ROOT/spec['reference' if reference else 'starter']
    parent=None
    parent_record=None
    parent_artifacts={}
    parent_integration=None
    forwarded_integration=None
    owner_mapping=None
    supplied_map=getattr(args,'schema_map',None)
    if supplied_map is not None and not (args.command=='advance' and args.mission=='G4'):
        raise ValueError('--schema-map applies only to advance G4.')
    if args.command=='advance':
        parent=common.external(args.from_candidate)
        parent_record=common.load_entry(spec['predecessor'],parent)
        if args.mission == 'B2' and parent_record.get('api_contract') != 'B1-API/v2':
            raise ValueError('B2 continues the explicit B1 v2 extension; complete extend/check/continue first.')
        if args.mission=='G4':
            parent_integration=integration_binding(parent,parent_record,required=True)
        with tempfile.TemporaryDirectory(prefix='esa-parent-check-') as temp:
            receipt=Path(temp)/'parent-handoff.json'
            cmd=[sys.executable,str(ROOT/'start.py'),'continue',spec['predecessor'],'--candidate',str(parent),'--output',str(receipt)]
            result=subprocess.run(cmd,text=True,capture_output=True,timeout=90)
            if result.returncode:
                raise ValueError('The retained predecessor did not complete its current handoff: '+result.stdout+result.stderr)
            parent_check=json.loads(receipt.read_text())
            parent_artifacts={str(p.relative_to(receipt.with_suffix(""))):p.read_bytes() for p in receipt.with_suffix("").rglob("*") if p.is_file()}
        if args.mission=='G4':
            owner_mapping=g4_owner_mapping(parent,supplied_map.expanduser() if supplied_map else None)
    dest.mkdir(parents=True)
    shutil.copy2(source,dest/spec['module'])
    for relative,original in spec['protected'].items():
        target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/original,target)
    for relative,original in spec['dependencies'].items():
        target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/original,target)
    lineage=None
    if parent:
        predecessor_module='booking.py' if spec['predecessor'].startswith('G') and spec['predecessor']!='G4' else 'src/treasury/routing.py' if spec['predecessor']=='B1' else manifest()[spec['predecessor']]['module']
        parent_file=parent/predecessor_module
        previous=dest/'prior';previous.mkdir()
        shutil.copy2(parent_file,previous/Path(predecessor_module).name)
        (previous/'parent-entry.json').write_text(json.dumps(parent_record,indent=2)+'\n')
        (previous/'parent-handoff.json').write_text(json.dumps(parent_check,indent=2)+'\n')
        for name,data in parent_artifacts.items():
            saved=previous/'parent-check-artifacts'/name
            saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(data)
        lineage={'mission':spec['predecessor'],'source_sha256':sha(parent_file),'source_path':str(parent_file),
                 'handoff_status':parent_check['status'],'stored_snapshot':'prior/'+Path(predecessor_module).name,
                 'copied_parent_demonstration':'prior/parent-check-artifacts' if parent_artifacts else None}
        if args.mission=='G2':shutil.copy2(parent_file,dest/'booking.py')
        elif args.mission=='G3':
            text=parent_file.read_text()
            text+='\n\ndef reservation_status(path,reservation_id):\n    raise NotImplementedError("Implement the approved status API")\n\ndef cancel(path,reservation_id,*,trusted_member_id,expected_version):\n    raise NotImplementedError("Implement the approved cancellation API")\n'
            (dest/'booking.py').write_text(text)
        elif args.mission=='G4':
            shutil.copy2(parent_file,dest/'booking.py')
            for name in parent_integration['record']['source_sha256']:
                if name!='booking.py':shutil.copy2(parent/name,dest/name)
                saved=previous/'integration'/name;saved.parent.mkdir(exist_ok=True)
                shutil.copy2(parent/name,saved)
            shutil.copy2(parent_integration['receipt'],previous/'integration-acceptance.json')
            forwarded_integration=json.loads(json.dumps(parent_integration['record']))
            forwarded_integration['receipt']='prior/integration-acceptance.json'
            lineage['integration_source_sha256']=forwarded_integration['source_sha256']
            lineage['integration_receipt_sha256']=forwarded_integration['receipt_sha256']
            lineage['integration_snapshots']='prior/integration'
        elif args.mission=='B2':shutil.copy2(parent_file,dest/'routing.py')
        elif args.mission=='B3' and (parent/'routing.py').is_file():shutil.copy2(parent/'routing.py',dest/'routing.py')
        elif args.mission=='B4':
            shutil.copy2(parent_file,dest/'ledger.py')
            shutil.copy2(parent/'routing.py',dest/'routing.py')
    mapping_files=g4_install_owner_mapping(dest,owner_mapping) if owner_mapping else []
    if owner_mapping:
        lineage['owner_mapping']={'decision':'docs/G4-OD-01.md','map':'docs/G4-SCHEMA-MAP.json',
                                  'origin':owner_mapping['origin'],'table':owner_mapping['table']}
    entry={'schema':'esa-full-mission/v1','release':common.RELEASE,'mission':args.mission,
           'mode':'REFERENCE' if reference else 'LEARNER','contract':spec['contract'],
           'module':spec['module'],'lineage':lineage,'human_acceptance':'PENDING',
           'dependency_sha256':{name:sha(dest/name) for name in spec['dependencies']},
           'prior_sha256':{str(p.relative_to(dest)):sha(p) for p in (dest/'prior').rglob('*') if p.is_file()} if parent else {}}
    if mapping_files:
        entry['owner_mapping']='G4-OD-01'
        entry['dependency_sha256'].update({name:sha(dest/name) for name in mapping_files})
    if forwarded_integration:
        entry['integration']=forwarded_integration
        entry['dependency_sha256'].update({name:sha(dest/name) for name in
                                          ['reservation_report.py','reservation_cli.py']})
    common.json_write(dest/'READER_ENTRY.json',entry)
    (dest/'DOSSIER.md').write_text(f'# {args.mission} decision record\n\n## Expect\n\nState the contract, acceptance example and open owner question.\n\n## Delegate\n\nBound the implementation change.\n\n## Observe\n\nRecord commands and identified receipts, including failures.\n\n## Decide\n\nExplain ACCEPT/REJECT/ASK for the three proposals and the handoff scope.\n')
    (dest/'AGENTS.md').write_text(f'# {args.mission} scope\n\nEdit {spec["module"]} and DOSSIER.md. Preserve docs, tests, dependencies, prior snapshots and READER_ENTRY.json. Run checks as feedback. Report actual behavior. This instruction is not an operating-system boundary.\n')
    print(json.dumps({'status':'REFERENCE_CREATED' if reference else 'STARTER_CREATED','mission':args.mission,'path':str(dest),'edit':spec['module'],'contract':spec['contract'],'lineage':lineage},indent=2))
    return 0


def checks(args,*,reference=False):
    import start as common
    spec=manifest()[args.mission]
    candidate=common.external(args.candidate)
    entry=common.load_entry(args.mission,candidate,reference)
    integration=None
    integration_error=None
    try:integration=integration_binding(candidate,entry)
    except (ValueError,OSError,KeyError) as exc:integration_error=str(exc)
    paths={**{name:sha(ROOT/source) for name,source in spec['protected'].items()},**entry['dependency_sha256'], **entry.get('prior_sha256', {})}
    bad=[name for name,h in paths.items() if not (candidate/name).is_file() or (candidate/name).is_symlink() or sha(candidate/name)!=h]
    module=candidate/spec['module']
    before=sha(module) if module.is_file() else None
    report={'schema':'esa-full-mission-check/v1','mission':args.mission,'release':common.RELEASE,
            'contract':spec['contract'],'candidate_sha256_before':before,'protected_input_sha256':paths,
            'candidate_path':str(candidate),'human_acceptance':'PENDING','model_run':False,
            'scope':'Executable local teaching controls; no human reader performance or production authority.'}
    if integration_error:
        return {**report,'status':'INPUT_INTEGRITY_FAILED','protected_changes':['integration: '+integration_error],
                'tests_run':0,'groups':{}}
    if integration:
        report['integration']={'source_sha256':integration['record']['source_sha256'],
                               'receipt_sha256':integration['record']['receipt_sha256'],
                               'bundle_sha256':integration['record']['bundle_sha256']}
    if bad or before is None or module.is_symlink():
        return {**report,'status':'INPUT_INTEGRITY_FAILED','protected_changes':bad,'tests_run':0,'groups':{}}
    group=common.suite_run(candidate,args.mission,'tests',spec['test_pattern'],spec['tests'],args.timeout_seconds)
    after=sha(module)
    unchanged=before==after and all((candidate/p).is_file() and sha(candidate/p)==h for p,h in paths.items())
    return {**report,'groups':{'contract':group},'tests_run':group['tests_run'],
            'candidate_sha256_after':after,'inputs_unchanged':unchanged,
            'status':'SELECTED_CHECKS_PASSED' if group['status']=='PASSED' and unchanged else 'CHECKS_FAILED'}


def check(args):
    import start as common
    output=common.external(args.output,output=True)
    candidate=common.external(args.candidate)
    if output.is_relative_to(candidate):raise ValueError('Keep receipts outside candidate inputs.')
    report=checks(args,reference=getattr(args,'reference',False))
    passed=report['status']=='SELECTED_CHECKS_PASSED'
    if args.command=='continue':
        if passed:
            demo=output.with_suffix('')
            if demo.exists():raise ValueError('Demonstration output already exists; use a new receipt name.')
            command=[sys.executable,str(ROOT/'curriculum_demo.py'),args.mission,'--candidate',str(candidate),'--output',str(demo)]
            run=common.run_process(command,ROOT,args.timeout_seconds,common.environment(args.mission,candidate))
            report['demonstration_process']=run
            passed=run['returncode']==0 and not run['timed_out']
            if passed:
                report['demonstration']=json.loads(run['stdout'])
                report['demonstration_files_sha256']={str(p.relative_to(demo)):sha(p) for p in sorted(demo.rglob('*')) if p.is_file()}
            report['candidate_retained']=sha(candidate/manifest()[args.mission]['module'])==report['candidate_sha256_before']
            passed=passed and report['candidate_retained']
            entry=json.loads((candidate/'READER_ENTRY.json').read_text())
            if entry.get('integration'):
                try:
                    integration_binding(candidate,entry)
                    report['integration_inputs_retained']=True
                except (ValueError,OSError,KeyError):
                    report['integration_inputs_retained']=False
                passed=passed and report['integration_inputs_retained']
        report['status']='SCOPED_HANDOFF_READY' if passed else 'HANDOFF_BLOCKED'
    common.json_write(output,report)
    print(json.dumps({'status':report['status'],'mission':args.mission,'tests_run':report['tests_run'],'receipt':str(output)},indent=2))
    return 0 if passed else 1


def _review_single(args):
    import start as common
    output=common.external(args.output,output=True)
    spec=manifest()[args.mission]
    if args.candidate_id not in spec['candidate_ids']:raise ValueError('Use a neutral candidate ID from the mission.')
    pack=ROOT/'candidates'/args.mission/args.candidate_id
    truth=json.loads((pack/'TRUTH.json').read_text())
    with tempfile.TemporaryDirectory(prefix='esa-full-review-') as temp:
        candidate=Path(temp)/'candidate'
        import contextlib,io
        with contextlib.redirect_stdout(io.StringIO()):
            create(argparse.Namespace(command='new',mission=args.mission,dest=candidate))
        shutil.copy2(pack/'variant.py',candidate/spec['module'])
        result=checks(argparse.Namespace(mission=args.mission,candidate=candidate,timeout_seconds=args.timeout_seconds))
        result.update(candidate_id=args.candidate_id,origin='EXECUTED_CONSTRUCTED_TEACHING_VARIANT',
                      ground_truth=truth,rationale=(pack/'RATIONALE.md').read_text(),learner_source_modified=False)
        common.json_write(output,result)
    print(json.dumps({'status':'REVIEW_RECORDED','candidate_id':args.candidate_id,'observed_check_status':result['status'],'expected_decision':truth['expected_decision'],'receipt':str(output)},indent=2))
    return 0


def review(args):
    import start as common
    return common.batch_review(args, _review_single)


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    choices=list(manifest())
    for operation in ('new','solution','advance'):
        c=sub.add_parser(operation);c.add_argument('mission',choices=choices);c.add_argument('--dest',required=True,type=Path)
        if operation=='advance':
            c.add_argument('--from-candidate',required=True,type=Path)
            c.add_argument('--schema-map',type=Path,help='G4 only: owner mapping for a G3 layout that OPS-G4/v3 does not name')
    for operation in ('check','continue'):
        c=sub.add_parser(operation);c.add_argument('mission',choices=choices);c.add_argument('--candidate',required=True,type=Path);c.add_argument('--output',required=True,type=Path)
        c.add_argument('--timeout-seconds',type=float,default=30)
        if operation=='check':c.add_argument('--reference',action='store_true')
    c=sub.add_parser('review');c.add_argument('mission',choices=choices);ids=c.add_mutually_exclusive_group(required=True);ids.add_argument('--candidate-id');ids.add_argument('--candidate-ids',nargs='+');c.add_argument('--output',required=True,type=Path);c.add_argument('--timeout-seconds',type=float,default=30)
    args=p.parse_args()
    try:
        import start as common
        if sys.version_info < (3, 10):raise ValueError('Python 3.10 or newer is required.')
        changed=common.upstream_integrity()
        if changed:raise ValueError('Packaged upstream inputs differ: '+', '.join(changed))
        if args.command in ('new','solution','advance'):return create(args,args.command=='solution')
        if not 0<args.timeout_seconds<=60:raise ValueError('Timeout must be 0 < seconds <= 60.')
        return review(args) if args.command=='review' else check(args)
    except (ValueError,OSError,KeyError) as exc:
        print('REFUSED: '+str(exc),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
