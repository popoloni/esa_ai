"""One cumulative owner-run CP01–CP14 regression and worked-example runner."""
from pathlib import Path
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from scope_guard import check_integrity, check_candidate_path, CHAPTER_EDIT_PATHS

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'repo/src'))


def run(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-candidates',action='store_true',help='Also require the current CP01–CP09 learner artefacts to pass their cumulative review gate')
    parser.add_argument('--release-rehearsal',type=Path,help='Evaluate the current CP10 release dossier against this recorded local rehearsal')
    parser.add_argument('--require-release',action='store_true',help='Require current CP01–CP09 candidates and the CP10 gate for a WORKING_CANDIDATES rehearsal; requires --release-rehearsal')
    parser.add_argument('--require-evolution',action='store_true',help='Require current CP01–CP09 and CP11 policy/history candidates; does not imply a CP10 release decision')
    parser.add_argument('--incident-rehearsal',type=Path,help='Evaluate current CP12 candidates using this WORKING_CANDIDATES incident rehearsal')
    parser.add_argument('--require-operations',action='store_true',help='Require current CP01–CP09, CP11 and CP12 local incident recovery; requires --incident-rehearsal and grants no release authority')
    parser.add_argument('--transfer-session',type=Path,help='Evaluate current CP13 review/knowledge candidates against recorded transfer evidence')
    parser.add_argument('--require-learning',action='store_true',help='Require current prior workflow, CP11, CP12 and CP13 protocol review; requires both incident and transfer sessions; does not certify human learning')
    parser.add_argument('--measurement-session',type=Path,help='Evaluate CP14 outcome accounting and proposed tool decision against recorded local telemetry')
    parser.add_argument('--require-measurement',action='store_true',help='Require current prior workflow, CP11, CP12, CP13 and CP14 with the same nominated incident and seed transfer; does not establish field economics')
    parser.add_argument('--output',type=Path,default=ROOT/'reader_side/evidence/INTEGRATED_CP01_CP14_RESULTS.json')
    args=parser.parse_args(argv)
    if args.require_release and args.release_rehearsal is None:
        parser.error('--require-release requires --release-rehearsal; a regression pass alone does not approve a release dossier')
    if args.require_operations and args.incident_rehearsal is None:
        parser.error('--require-operations requires --incident-rehearsal; regression green does not establish operational recovery')
    if (args.require_learning or args.require_measurement) and (args.incident_rehearsal is None or args.transfer_session is None):
        parser.error('--require-learning/--require-measurement require --incident-rehearsal and --transfer-session; they cannot certify human competence')
    if args.require_measurement and args.measurement_session is None:
        parser.error('--require-measurement requires --measurement-session; unknown field costs are not zero')
    protected=json.loads((ROOT/'reader_side/protected_sha256.json').read_text())
    output=args.output.resolve()
    if output.is_relative_to(ROOT/'repo') or output == ROOT/'reader_side/protected_sha256.json' or any(output == (ROOT/rel).resolve() for rel in protected):
        parser.error('--output must not overwrite candidates or protected sources')
    before=check_integrity()
    for chapter,paths in sorted(CHAPTER_EDIT_PATHS.items()):
        for path in sorted(paths):
            try:check_candidate_path(path,chapter=chapter)
            except (ValueError,PermissionError) as exc:before.append('EDIT_BOUNDARY:'+chapter+':'+path+':'+str(exc))
    runs=[]
    controls={}
    candidate={'status':'NOT_RUN'}
    release_candidate={'status':'NOT_RUN','reason':'No --release-rehearsal supplied; CP10 learner readiness has not been evaluated.'}
    evolution_candidate={'status':'NOT_RUN'}
    operations_candidate={'status':'NOT_RUN','reason':'No --incident-rehearsal supplied; CP12 local recovery has not been evaluated.'}
    learning_candidate={'status':'NOT_RUN','reason':'No --transfer-session supplied; CP13 protocol/knowledge readiness has not been evaluated.'}
    measurement_candidate={'status':'NOT_RUN','reason':'No --measurement-session supplied; CP14 measurement review has not been evaluated.'}
    if not before:
        env=dict(os.environ)
        env['PYTHONPATH']=str(ROOT/'repo/src')
        env['PYTHONDONTWRITEBYTECODE']='1'
        for label,directory in [('acceptance','acceptance'),('regression','tests')]:
            command=[sys.executable,'-B','-m','unittest','discover','-s',str(ROOT/'reader_side'/directory),'-v']
            try:
                result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=180)
                counts=re.findall(r'Ran (\d+) tests? in',result.stderr)
                count=int(counts[-1]) if counts else 0
                record={'suite':label,'returncode':result.returncode,'tests':count,'stdout':result.stdout,'stderr':result.stderr}
            except subprocess.TimeoutExpired:
                record={'suite':label,'returncode':124,'tests':0,'stdout':'','stderr':'Test subprocess timed out after 180 seconds'}
            runs.append(record)
            print(record['stderr'],end='')
            if record['stdout']:print(record['stdout'])
        try:
            from implementation_core import load_candidate, check_implementation, report_findings
            from verification_core import owner_gate, REF, REFERENCE_REVIEW
            from integration_core import review_workflow
            from evolution_core import evaluate_evolution, SUCCESS as EVOLUTION_SUCCESS
            impl=ROOT/'reader_side/implementation'
            reference=ROOT/'reader_side/reference_solution'
            def impl_findings(code,report):
                return check_implementation(load_candidate(code))+report_findings(json.loads(report.read_text()))
            unsafe=impl_findings(impl/'unsafe_explanation_fixture.py',impl/'unsafe_report_fixture.json')
            safe=impl_findings(reference/'explanation_alpha.py',reference/'implementation_report.json')
            controls['CP08_unsafe_rejected']={'passed':bool(unsafe),'findings':unsafe}
            controls['CP08_reference_passed']={'passed':not safe,'findings':safe}
            bad9=owner_gate(ROOT/'reader_side/verification/unsafe_candidate_fixture.py',ROOT/'reader_side/verification/unsafe_review_fixture.json')
            good9=owner_gate(REF,REFERENCE_REVIEW)
            controls['CP09_unsafe_rejected']={'passed':bad9['status']=='FAIL','result':bad9}
            controls['CP09_reference_passed']={'passed':good9['status']=='PASS_REVIEW_GATE_ONLY','result':good9}
            full=review_workflow(reference=True)
            controls['complete_reference_workflow_passed']={'passed':full['status']=='PASS_REVIEW_GATE_ONLY','result':full}
            candidate=review_workflow()
            unsafe11=evaluate_evolution(root=ROOT,unsafe=True)
            safe11=evaluate_evolution(root=ROOT,reference=True)
            controls['CP11_unsafe_rejected']={'passed':unsafe11['status']=='FAIL'
                and 'BEHAVIOR:decision_and_audit_atomic' in unsafe11['findings'], 'result':unsafe11}
            controls['CP11_reference_passed']={'passed':safe11['status']==EVOLUTION_SUCCESS,'result':safe11}
            evolution_candidate=evaluate_evolution(root=ROOT)
            if args.release_rehearsal is not None:
                from release_core import evaluate_release
                release_candidate=evaluate_release(
                    ROOT/'repo/engineering/release/release_dossier.json',
                    args.release_rehearsal.resolve(),root=ROOT)
            if args.incident_rehearsal is not None:
                from incident_core import evaluate_incident
                operations_candidate=evaluate_incident(args.incident_rehearsal.resolve(),root=ROOT)
            if args.transfer_session is not None:
                from learning_core import evaluate_learning
                learning_candidate=evaluate_learning(args.transfer_session.resolve(),root=ROOT)
            if args.measurement_session is not None:
                from measurement_core import evaluate_measurement
                measurement_candidate=evaluate_measurement(args.measurement_session.resolve(),root=ROOT)
        except Exception as exc:
            controls['execution_error']={'passed':False,'error':type(exc).__name__+':'+str(exc)}
    after=check_integrity()
    suite_pass=(not before and not after and len(runs)==2
                and all(r['returncode']==0 and r['tests']>0 for r in runs)
                and bool(controls) and all(c['passed'] for c in controls.values()))
    candidates_pass=candidate['status']=='PASS_REVIEW_GATE_ONLY'
    release_pass=release_candidate.get('status')=='PASS_LOCAL_RELEASE_REHEARSAL_ONLY'
    evolution_pass=evolution_candidate.get('status')=='PASS_POLICY_EVOLUTION_REVIEW_ONLY'
    operations_pass=(operations_candidate.get('status')=='PASS_INCIDENT_RECOVERY_REVIEW_ONLY'
                     and operations_candidate.get('mode')=='WORKING_CANDIDATES'
                     and operations_candidate.get('rehearsal_mode')=='WORKING_CANDIDATES')
    learning_pass=(learning_candidate.get('status')=='PASS_LEARNING_PROTOCOL_REVIEW_ONLY'
                   and learning_candidate.get('mode')=='WORKING_CANDIDATES'
                   and learning_candidate.get('transfer_mode')=='WORKING_CANDIDATES')
    learning_requirement_findings=[]
    if (args.require_learning or args.require_measurement) and learning_candidate.get('learning_session_sha256') != operations_candidate.get('session_sha256'):
        learning_requirement_findings.append('LEARNING_SOURCE_SESSION_MISMATCH')
    measurement_pass=(measurement_candidate.get('status')=='PASS_MEASUREMENT_REVIEW_ONLY'
                      and measurement_candidate.get('mode')=='WORKING_CANDIDATES'
                      and measurement_candidate.get('measurement_mode')=='WORKING_CANDIDATES')
    measurement_requirement_findings=[]
    if args.require_measurement:
        if measurement_candidate.get('incident_session_sha256') != operations_candidate.get('session_sha256'):
            measurement_requirement_findings.append('MEASUREMENT_INCIDENT_SESSION_MISMATCH')
        if measurement_candidate.get('seed_transfer_session_sha256') != learning_candidate.get('transfer_session_sha256'):
            measurement_requirement_findings.append('MEASUREMENT_SEED_TRANSFER_SESSION_MISMATCH')
    release_requirement_findings=[]
    if args.require_release and release_candidate.get('rehearsal_mode')!='WORKING_CANDIDATES':
        release_requirement_findings.append('CURRENT_SOURCE_REHEARSAL_REQUIRED: a protected reference session cannot certify the current working source')
    overall=(suite_pass and (candidates_pass or not (args.require_candidates or args.require_release or args.require_evolution or args.require_operations or args.require_learning or args.require_measurement))
             and ((release_pass and not release_requirement_findings) or not args.require_release)
             and (evolution_pass or not (args.require_evolution or args.require_operations or args.require_learning or args.require_measurement))
             and (operations_pass or not (args.require_operations or args.require_learning or args.require_measurement))
             and ((learning_pass and not learning_requirement_findings) or not (args.require_learning or args.require_measurement))
             and ((measurement_pass and not measurement_requirement_findings) or not args.require_measurement))
    report={
        'schema':'integrated-lab-run/v1',
        'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status':'PASS' if overall else 'FAIL',
        'suite_status':'PASS' if suite_pass else 'FAIL',
        'candidate_status':candidate['status'],
        'candidate_scope':'CP01–CP09 cumulative learner artifacts',
        'release_candidate_status':release_candidate['status'],
        'release_candidate_scope':'CP10 dossier and exact local rehearsal; no production authorization',
        'release_rehearsal_mode':release_candidate.get('rehearsal_mode','NOT_RUN'),
        'release_requirement_findings':release_requirement_findings,
        'evolution_candidate_status':evolution_candidate['status'],
        'evolution_candidate_scope':'CP11 versioned policy, persistent replay, retry identity and synthetic migration; no release authorization',
        'operations_candidate_status':operations_candidate['status'],
        'operations_candidate_scope':'CP12 local diagnosis, preserved state selection and recovery guards; reconciliation and production operation remain unapproved',
        'operations_rehearsal_mode':operations_candidate.get('rehearsal_mode','NOT_RUN'),
        'learning_candidate_status':learning_candidate['status'],
        'learning_candidate_scope':'CP13 transfer evidence, knowledge dependencies and synthetic protocol calibration; no human learning certification',
        'learning_transfer_mode':learning_candidate.get('transfer_mode','NOT_RUN'),
        'learning_requirement_findings':learning_requirement_findings,
        'measurement_candidate_status':measurement_candidate['status'],
        'measurement_candidate_scope':'CP14 observed local telemetry and protected synthetic scenario accounting; no human field-economic result',
        'measurement_mode':measurement_candidate.get('measurement_mode','NOT_RUN'),
        'measurement_requirement_findings':measurement_requirement_findings,
        'actual_economic_field_result':'UNKNOWN_INCOMPLETE_MEASUREMENTS',
        'human_learning_trial_status':'PENDING_INDEPENDENT_HUMAN_TRIAL',
        'rubric_validity':'PENDING_HUMAN_VALIDATION',
        'require_candidates':args.require_candidates,
        'require_release':args.require_release,
        'require_evolution':args.require_evolution,
        'require_operations':args.require_operations,
        'require_learning':args.require_learning,
        'require_measurement':args.require_measurement,
        'chapters':list(range(1,15)),
        'tests_total':sum(r['tests'] for r in runs),
        'tests_by_suite':{r['suite']:r['tests'] for r in runs},
        'integrity_before':before,'integrity_after':after,
        'runs':runs,'controls':controls,'current_workflow':candidate,'current_release_review':release_candidate,
        'current_evolution_review':evolution_candidate,
        'current_operations_review':operations_candidate,
        'current_learning_review':learning_candidate,
        'current_measurement_review':measurement_candidate,
        'meaning':'One canonical shared-code lab, with cumulative tests and protected positive/negative controls. Candidate readiness is reported separately. No live agents, human acceptance or release authorization.'
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Integrated CP01–CP14 suite:',report['suite_status'],'| tests:',report['tests_total'])
    print('Current CP01–CP09 learner workflow:',report['candidate_status'])
    print('Nominated CP10 release dossier:',report['release_candidate_status'],'| mode:',report['release_rehearsal_mode'])
    print('Current CP11 policy/history candidate:',report['evolution_candidate_status'])
    print('Current CP12 incident recovery:',report['operations_candidate_status'])
    print('Current CP13 protocol/knowledge review:',report['learning_candidate_status'],'| human trial:',report['human_learning_trial_status'])
    print('Current CP14 measurement review:',report['measurement_candidate_status'],'| field economics:',report['actual_economic_field_result'])
    for finding in release_requirement_findings:print(finding)
    print('Overall:',report['status'],'| report:',str(output))
    return 0 if overall else 1


if __name__=='__main__':sys.exit(run())
