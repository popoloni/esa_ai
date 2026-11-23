#!/usr/bin/env python3
"""Check task preparation and staged trace disclosure without a native launch.

All candidates and decisions here are disposable automated control fixtures.
Passing this script does not establish native-client execution or reader skill.
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

COMPANION=Path(__file__).resolve().parents[1]
BOOK=COMPANION.parent
sys.path.insert(0,str(COMPANION))
import integration


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(output):
    output=output.resolve();output.mkdir(parents=True,exist_ok=False)
    command_dir=output/'commands';command_dir.mkdir()
    fixtures=output/'fixtures';fixtures.mkdir()
    sessions=output/'sessions';sessions.mkdir()
    records=[];checks=[]
    def assert_check(name,value,detail=None):
        checks.append({'check':name,'passed':bool(value),'detail':detail})
        if not value:raise ValueError(name+': '+str(detail))
    def command(label,program,args,expected=0):
        argv=[sys.executable,'-B',str(program),*map(str,args)]
        env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env.pop('PYTHONPATH',None)
        run=subprocess.run(argv,cwd=BOOK,env=env,capture_output=True,text=True,timeout=60)
        record={'label':label,'argv':argv,'cwd':str(BOOK),'returncode':run.returncode,
                'expected_returncode':expected,'stdout':run.stdout,'stderr':run.stderr,
                'origin':'AUTOMATED_DISPOSABLE_CONTROL_NO_MODEL_CALL'}
        records.append(record)
        integration.json_write(command_dir/f'{len(records):03d}_{label}.json',record)
        assert_check(label+'_exit',run.returncode==expected,{'expected':expected,'actual':run.returncode})
        return record
    def prepare(label,mission,candidate,*,extra=(),editable=None,expected=0):
        before=integration.inventory(candidate);target=sessions/label
        record=command(label,COMPANION/'agent_session.py',
                       ['prepare',mission,'--candidate',candidate,'--output',target,*extra],expected)
        after=integration.inventory(candidate)
        assert_check(label+'_candidate_preserved',before==after)
        if expected==0:
            specification=json.loads((target/'SESSION.json').read_text())
            assert_check(label+'_editable_scope',specification['editable_paths']==editable,specification['editable_paths'])
            assert_check(label+'_not_launched',specification['model_run'] is False and not (target/'runs').exists())
            assert_check(label+'_snapshot_bound',specification['before']==before and integration.inventory(target/'before')==before)
            protected={name:digest for name,digest in before.items() if name not in editable}
            assert_check(label+'_protected_context',specification['protected_sha256']==protected)
            return specification
        assert_check(label+'_no_task_created',not target.exists())
        return record
    status='FAILED';failure=None
    try:
        g1=fixtures/'g1'
        command('new_g1',COMPANION/'start.py',['new','G1','--dest',g1])
        (g1/'QUESTIONS.md').write_text('AUTOMATED CONTROL: What happens for an absent reservation identifier and missing storage?\n')
        question=prepare('g1_question','G1',g1,extra=['--stage','question'],editable=['AGENT_QUESTIONS.md','AGENT_PLAN.md'])
        assert_check('g1_question_budget',question['max_runs']==1 and question['session_seconds_from_first_launch']==600)
        prepare('g1_implement_before_decision','G1',g1,extra=['--stage','implement'],expected=2)
        command('g1_clarify',COMPANION/'start.py',['clarify','G1','--candidate',g1,'--question-file',g1/'QUESTIONS.md'])
        prepare('g1_implementation','G1',g1,extra=['--stage','implement'],editable=['booking.py','DOSSIER.md'])
        prepare('g1_question_after_decision','G1',g1,extra=['--stage','question'],expected=2)
        b1=fixtures/'b1'
        command('new_b1',COMPANION/'start.py',['new','B1','--dest',b1])
        prepare('b1_v1','B1',b1,extra=['--api','v1'],editable=['src/treasury/routing.py','DOSSIER.md'])
        shutil.copy2(COMPANION/'solutions/B1/routing.py',b1/'src/treasury/routing.py')
        b1v2=fixtures/'b1_v2'
        command('extend_b1',COMPANION/'start.py',['extend','B1','--candidate',b1,'--dest',b1v2])
        v2=prepare('b1_v2','B1',b1v2,extra=['--api','v2'],editable=['src/treasury/routing.py','DOSSIER.md'])
        assert_check('b1_v2_budget',v2['session_seconds_from_first_launch']==1200)
        prepare('b1_api_mismatch','B1',b1v2,extra=['--api','v1'],expected=2)
        manifest=json.loads((COMPANION/'curriculum/MANIFEST.json').read_text())['missions']
        for mission,spec in manifest.items():
            candidate=fixtures/mission.lower()
            command('new_'+mission.lower(),COMPANION/'start.py',['new',mission,'--dest',candidate])
            prepare('prepare_'+mission.lower(),mission,candidate,editable=[spec['module'],'DOSSIER.md'])
        carried=fixtures/'g4_carried'
        integration.snapshot(BOOK/'evidence/agent_process_v4/AP-G4/baseline',carried)
        linked=prepare('prepare_g4_carried','G4',carried,editable=['operations.py','DOSSIER.md'])
        assert_check('g4_integration_identity_carried',bool(linked['entry'].get('integration')))
        original=(carried/'reservation_report.py').read_bytes()
        try:
            (carried/'reservation_report.py').write_bytes(original+b'\n# Deliberate adapter integrity-control change.\n')
            prepare('reject_changed_g4_dependency','G4',carried,expected=2)
        finally:(carried/'reservation_report.py').write_bytes(original)
        actual_g3=fixtures/'g3_for_roles';integration.snapshot(BOOK/'evidence/agent_process_v4/AP-G3/workspace',actual_g3)
        role_group=output/'role_group'
        command('prepare_role_worktrees',COMPANION/'integration.py',['prepare','--candidate',actual_g3,'--dest',role_group])
        for role,row in integration.ROLES.items():
            candidate=role_group/'worktrees'/role
            spec=prepare('role_'+role,'G3',candidate,extra=['--role',role],editable=[row['module'],row['note']])
            assert_check(role+'_shared_contract_bound',spec['task_contract']=='INTEGRATION-G3/v1' and bool(spec['integration_manifest_sha256']))
        report_role=role_group/'worktrees/report'
        prepare('reject_omitted_role','G3',report_role,expected=2)
        prepare('reject_other_role','G3',report_role,extra=['--role','cli'],expected=2)
        metadata=report_role/'INTEGRATION_ROLE.json';original=metadata.read_bytes()
        try:
            value=json.loads(original);value['editable_paths'].append('booking.py');metadata.write_text(json.dumps(value,indent=2)+'\n')
            prepare('reject_widened_role','G3',report_role,extra=['--role','report'],expected=2)
        finally:metadata.write_bytes(original)
        contract=report_role/'docs/INTEGRATION-G3.md';original=contract.read_bytes()
        try:
            contract.write_bytes(original+b'\nDeliberate contract identity control.\n')
            prepare('reject_changed_shared_contract','G3',report_role,extra=['--role','report'],expected=2)
        finally:contract.write_bytes(original)
        prepare('reject_role_on_b2','B2',fixtures/'b2',extra=['--role','report'],expected=2)
        prepare('reject_wrong_mission','G3',fixtures/'b2',expected=2)
        reference=fixtures/'g4_reference'
        command('new_g4_reference',COMPANION/'start.py',['solution','G4','--dest',reference])
        prepare('reject_reference','G4',reference,expected=2)
        prepare('reject_zero_wall_limit','G2',fixtures/'g2',extra=['--wall-seconds','0'],expected=2)
        prepare('reject_excess_wall_limit','G2',fixtures/'g2',extra=['--wall-seconds','3601'],expected=2)

        tours=json.loads((COMPANION/'agent_sessions/tours.json').read_text())
        required={'AP-G1','AP-G2','AP-G3','AP-G4','AP-B1-V1','AP-B1-V2','AP-B2','AP-B3','AP-B4'}
        assert_check('all_primary_tours_present',required<=set(tours))
        short_note=output/'short_note.txt';short_note.write_text('ask\n')
        for task,tour in tours.items():
            trace=output/'traces'/task
            first=command(task+'_start',COMPANION/'agent_session.py',['trace','--task',task,'--output',trace])
            state=json.loads((trace/'TRACE.json').read_text())
            assert_check(task+'_initial_outcomes_withheld',all(s['outcome'] not in first['stdout'] and s['outcome'] not in (trace/'TRACE.json').read_text() for s in tour['stages']))
            assert_check(task+'_version_bound',bool(state.get('tour_sha256')) and state['stages']==len(tour['stages']))
            repeated=command(task+'_no_decision',COMPANION/'agent_session.py',['trace','--session',trace])
            assert_check(task+'_no_decision_no_progress',not list(trace.glob('decision_*.json')) and 'RECORDED OUTCOME' not in repeated['stdout'])
            command(task+'_short_decision',COMPANION/'agent_session.py',['trace','--session',trace,'--decision-file',short_note],expected=2)
            assert_check(task+'_short_decision_no_progress',not list(trace.glob('decision_*.json')))
            for index,stage in enumerate(tour['stages']):
                note=output/f'{task}_decision_{index+1:02}.txt'
                text=f'AUTOMATED ADAPTER CONTROL, stage {index+1}: retain the displayed evidence and request the scoped next observation. This is not a human learner decision.\n'
                note.write_text(text)
                result=command(task+'_reveal_'+str(index+1),COMPANION/'agent_session.py',['trace','--session',trace,'--decision-file',note])
                decision=json.loads((trace/f'decision_{index+1:02}.json').read_text())
                assert_check(task+'_decision_'+str(index+1)+'_retained',decision['reader_note']==text and decision['stage']==index+1)
                assert_check(task+'_reveal_'+str(index+1)+'_only',stage['outcome'] in result['stdout'] and all(s['outcome'] not in result['stdout'] for s in tour['stages'][index+1:]))
                if index+1<len(tour['stages']):assert_check(task+'_next_question_'+str(index+1),tour['stages'][index+1]['question'] in result['stdout'])
                for field in ['observation_sources','reveal_sources']:
                    for source in stage[field]:assert_check(task+'_source_'+source['path'],sha(BOOK/source['path'])==source['sha256'])
            complete=command(task+'_complete',COMPANION/'agent_session.py',['trace','--session',trace])
            assert_check(task+'_completion_limit','not live-agent proficiency' in complete['stdout'])
            command(task+'_past_end',COMPANION/'agent_session.py',['trace','--session',trace,'--decision-file',note],expected=2)
            assert_check(task+'_no_extra_decision',len(list(trace.glob('decision_*.json')))==len(tour['stages']))
        # A local copy tests a changed tour without touching the real catalogue.
        clone=output/'changed_tour_probe/companion';(clone/'agent_sessions').mkdir(parents=True)
        shutil.copy2(COMPANION/'agent_session.py',clone/'agent_session.py')
        shutil.copy2(COMPANION/'agent_sessions/tours.json',clone/'agent_sessions/tours.json')
        trace=output/'changed_tour_probe/trace'
        command('version_binding_start',clone/'agent_session.py',['trace','--task','AP-G1','--output',trace])
        catalogue=json.loads((clone/'agent_sessions/tours.json').read_text());catalogue['AP-G1']['stages'][0]['observation']+=' Deliberate local version change.'
        (clone/'agent_sessions/tours.json').write_text(json.dumps(catalogue,indent=2)+'\n')
        command('reject_changed_tour_version',clone/'agent_session.py',['trace','--session',trace,'--decision-file',note],expected=2)
        assert_check('changed_tour_decision_not_written',not list(trace.glob('decision_*.json')))
        joined=[]
        pattern=re.compile(r'\b(?:Record|record|records|all|protected|most|observed|across|precision|the|complete|returns|reports|passed|those|plus)\d')
        for task,tour in tours.items():
            for index,stage in enumerate(tour['stages']):
                for field in ['observation','question','outcome']:
                    if pattern.search(stage[field]):joined.append([task,index+1,field])
        assert_check('joined_word_regressions_absent',not joined,joined)
        status='PASS'
    except Exception as exc:failure={'type':type(exc).__name__,'message':str(exc)}
    report={'schema':'esa-reader-adapter-check/v1','status':status,'failure':failure,
            'recorded_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'commands':records,
            'commands_run':len(records),'checks_recorded':len(checks),'native_client_launches':0,
            'observed_model_runs':0,'human_reader_pilots':0,
            'scope':'Disposable preparation, scope guards and all staged-tour reveal sequences; no native launch, learning outcome or canonical AP mutation.',
            'input_sha256':{str(path.relative_to(BOOK)):sha(path) for path in [COMPANION/'agent_session.py',COMPANION/'agent_sessions/tours.json',COMPANION/'agent_sessions/TOUR_PROVENANCE.json',Path(__file__)]}}
    integration.json_write(output/'RESULTS.json',report)
    print(json.dumps({'status':status,'commands':len(records),'checks':len(checks),'failure':failure,'report':str(output/'RESULTS.json')},indent=2))
    return status=='PASS'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    return 0 if verify(args.output) else 1


if __name__=='__main__':raise SystemExit(main())
