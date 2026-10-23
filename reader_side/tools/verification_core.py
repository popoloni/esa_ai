"""CP09 educational reviewer-side checks, NOT an OS sandbox or a proof system.
Owner-created, intentionally vulnerable and safe Python modules are executed as
local code. Never point this loader at arbitrary code from an untrusted agent.
"""
from __future__ import annotations
import ast
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
SIDE=ROOT/'reader_side'
REPO=ROOT/'repo'
ORACLE=SIDE/'specs/case_oracle.json'
PROPOSAL=REPO/'engineering/verification/candidate.py'
REVIEW=REPO/'engineering/verification/review.json'
REF=SIDE/'reference_solution/ch09/safe_candidate.py'
REFERENCE_REVIEW=SIDE/'reference_solution/ch09/reference_review.json'

KEYS=('route','reason_code','policy_version','payment_authorized','notice','benefit_status')
BANNED_IMPORTS={'os','subprocess','socket','ctypes','requests','urllib','pathlib','shutil'}
BANNED_CALLS={'eval','exec','compile','__import__','open'}

@dataclass
class CheckReport:
    checked:int
    passed:int
    failures:list[str]
    digest:str
    def as_dict(self): return {'checked':self.checked,'passed':self.passed,
        'failures':self.failures,'candidate_sha256':self.digest}


def source_findings(source:str)->list[str]:
    issues=[]
    try: tree=ast.parse(source)
    except SyntaxError: return ['python_syntax_error']
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            for a in node.names:
                if a.name.split('.')[0] in BANNED_IMPORTS:issues.append('suspicious_import:'+a.name)
        if isinstance(node,ast.ImportFrom) and node.module:
            if node.module.split('.')[0] in BANNED_IMPORTS:issues.append('suspicious_import:'+node.module)
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in BANNED_CALLS:
            issues.append('suspicious_builtin:'+node.func.id)
    return issues


def load_known_author_fixture(path:Path, entry_point:str='propose_explanation'):
    """Local teaching-only loader. This is not execution isolation."""
    path=Path(path)
    if not isinstance(entry_point,str) or not entry_point.isidentifier():
        raise ValueError('entry_point must be one explicit Python function name')
    findings=source_findings(path.read_text(encoding='utf-8'))
    if findings:raise ValueError('narrow source precheck findings: '+','.join(findings))
    sys.path.insert(0,str(REPO/'src'))
    spec=spec_from_file_location('cp09_candidate_'+sha256(str(path).encode()).hexdigest()[:12],path)
    if spec is None or spec.loader is None:raise ValueError('cannot load module')
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module,entry_point,None)):
        raise ValueError(entry_point+' is not callable')
    return getattr(module,entry_point)


def selected_cases():
    data=json.loads(ORACLE.read_text())
    return data['cases']


def expected_findings(answer:dict,case:dict)->list[str]:
    issues=[]
    for key in KEYS:
        if key not in answer:issues.append('missing_field:'+key)
    if answer.get('route')!=case['expected_route']:issues.append('route:'+case['id'])
    if answer.get('reason_code')!=case['expected_reason']:issues.append('reason:'+case['id'])
    if answer.get('policy_version')!=case['expected_policy_version']:issues.append('provenance:'+case['id'])
    if answer.get('payment_authorized') is not False:issues.append('payment_authority:'+case['id'])
    if answer.get('notice')!='ROUTING_ONLY_NOT_PAYMENT_APPROVAL':issues.append('notice:'+case['id'])
    if answer.get('benefit_status')!='HYPOTHESIS_NOT_VALIDATED':issues.append('benefit_claim:'+case['id'])
    return issues


def check_known_candidate(path:Path, entry_point:str='propose_explanation')->CheckReport:
    """Check a known teaching candidate against the separate owner-side oracle.

    ``build_explanation`` is an explicit option for the integrated CP08 producer;
    the CP09 wrapper exercise retains the original default entry point.
    Invalid source, imports or entry points are evidence of failure, not an
    uncaught success-path interruption. This loader still provides no sandbox.
    """
    path=Path(path)
    try: digest=sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        return CheckReport(0,0,['candidate_read_error:'+type(exc).__name__],'')
    try:
        cases=selected_cases()
        if not isinstance(cases,list) or not cases:
            raise ValueError('selected oracle cases must be a nonempty list')
    except Exception as exc:
        return CheckReport(0,0,['oracle_input_error:'+type(exc).__name__],digest)
    try: f=load_known_author_fixture(path,entry_point=entry_point)
    except (Exception,SystemExit) as exc:
        return CheckReport(len(cases),0,['candidate_load_error:'+type(exc).__name__],digest)
    issues=[];pass_count=0
    for case in cases:
        try:
            result=f(case['input_amount_eur'])
            if not isinstance(result,dict):raise TypeError('expected dict')
            errors=expected_findings(result,case)
            if errors:issues.extend(errors)
            else:pass_count+=1
        except (Exception,SystemExit) as exc:
            case_id=case.get('id','unknown') if isinstance(case,dict) else 'invalid_case'
            issues.append('exception:'+str(case_id)+':'+type(exc).__name__)
    try:
        if sha256(path.read_bytes()).hexdigest()!=digest:
            issues.append('candidate_changed_during_check')
    except OSError:
        issues.append('candidate_unreadable_after_check')
    return CheckReport(len(cases),pass_count,issues,digest)


def seeded_mutation_probe(cases:list[dict]|None=None)->dict:
    """Three hand-written faults in an output transformation, NOT a mutmut run."""
    cases=selected_cases() if cases is None else cases
    mutant_names=('boundary_off_by_one','grant_payment','erase_policy_version')
    killed=[];survived=[]
    for name in mutant_names:
        faults=[]
        for c in cases:
            out={'route':c['expected_route'],'reason_code':c['expected_reason'],
                 'policy_version':c['expected_policy_version'],
                 'payment_authorized':False,'notice':'ROUTING_ONLY_NOT_PAYMENT_APPROVAL',
                 'benefit_status':'HYPOTHESIS_NOT_VALIDATED'}
            if name=='boundary_off_by_one' and c['input_amount_eur'] in ('5000','5000.00'):
                out['route']='STANDARD_QUEUE';out['reason_code']='BELOW_LIMIT'
            if name=='grant_payment' and out['route']=='STANDARD_QUEUE':out['payment_authorized']=True
            if name=='erase_policy_version':out['policy_version']='BR-001/unknown'
            faults+=expected_findings(out,c)
        (killed if faults else survived).append(name)
    return {'manually_seeded_faults':len(mutant_names),'killed':killed,'survived':survived,
            'scope':'handwritten output-level faults against selected synthetic cases; not mutation score for repository code'}


def check_review(review:dict,report:CheckReport,probe:dict)->list[str]:
    issues=[]
    if not isinstance(review,dict):
        return ['review_must_be_object']
    fixed={'review_id':'VER-009/v1','contract_id':'SPEC-004/v1','policy_version':'BR-001/v1',
           'oracle_source':'reader_side/specs/case_oracle.json',
           'status':'READY_FOR_HUMAN_REVIEW_NOT_ACCEPTED',
           'decision_owner':'human_technical_owner_pending',
           'claim':'SELECTED_CHECKS_ONLY_NO_RELEASE_AUTHORITY'}
    for key,val in fixed.items():
        if review.get(key)!=val:issues.append('incorrect_'+key)
    if review.get('candidate_sha256')!=report.digest:issues.append('candidate_digest_mismatch')
    expected={'case_count':report.checked,'case_passed':report.passed,
              'injected_faults_killed':len(probe['killed']),
              'injected_faults_total':probe['manually_seeded_faults']}
    evidence=review.get('test_evidence',{})
    if not isinstance(evidence,dict):
        issues.append('test_evidence_must_be_object')
        evidence={}
    for k,v in expected.items():
        if evidence.get(k)!=v:issues.append('evidence_mismatch:'+k)
    if report.failures:issues.append('unresolved_behavior_findings')
    if len(probe['killed'])!=probe['manually_seeded_faults']:issues.append('surviving_seeded_fault')
    if review.get('release_authorized') is not False:issues.append('release_permission_claim')
    if review.get('human_review_required') is not True:issues.append('human_review_not_required')
    remaining=review.get('remaining_uncertainty',[])
    if (not isinstance(remaining,list)
        or not all(isinstance(item,str) for item in remaining)
        or not {'owner_policy_confirmation','operator_comprehension','security_scope_review'}<=set(remaining)):
        issues.append('missing_remaining_uncertainty')
    return issues


def owner_gate(candidate:Path=PROPOSAL,review_path:Path=REVIEW,verify_integrity:bool=True,
               scope_baseline:Path|None=None)->dict:
    """Return a structured verdict for the CP09 wrapper teaching exercise.

    The optional owner-created scope baseline checks the actual repository diff
    for this exercise. Protected-reference checks remain available separately.
    The CP08-to-CP09 bridge calls ``check_known_candidate`` with the producer's
    explicit entry point and additionally binds its own upstream receipts.
    """
    from scope_guard import check_integrity,check_candidate_path
    candidate=Path(candidate);review_path=Path(review_path)
    problems=[];issues=[];path_findings=[];scope_findings=[]
    if verify_integrity:
        try: problems=[str(x) for x in check_integrity()]
        except Exception as exc:
            problems=['integrity_check_error:'+type(exc).__name__]
    for role,path in [('candidate',candidate),('review',review_path)]:
        try: relative=path.absolute().relative_to(REPO.absolute()).as_posix()
        except ValueError:
            # The supplied owner-controlled reference/negative fixtures live
            # outside repo/. This is a teaching loader, not an untrusted runner.
            continue
        try: check_candidate_path(relative,chapter='CP09')
        except Exception as exc:
            path_findings.append(role+':'+type(exc).__name__)
    if scope_baseline is not None:
        try:
            from scope_guard import check_edit_scope
            scope_findings=[str(x) for x in check_edit_scope(Path(scope_baseline),root=ROOT,chapter='CP09')]
        except Exception as exc:
            scope_findings=['scope_check_error:'+type(exc).__name__]
    if path_findings:
        try: digest=sha256(candidate.read_bytes()).hexdigest()
        except OSError: digest=''
        candidate_report=CheckReport(0,0,['candidate_path_rejected'],digest)
    else:
        candidate_report=check_known_candidate(candidate)
    try: probe=seeded_mutation_probe()
    except Exception as exc:
        issues.append('fault_probe_error:'+type(exc).__name__)
        probe={'manually_seeded_faults':0,'killed':[],'survived':[],
               'scope':'fault probe could not run; no positive evidence'}
    try:
        review=json.loads(review_path.read_text(encoding='utf-8'))
        issues.extend(check_review(review,candidate_report,probe))
    except Exception as exc:
        issues.append('review_input_error:'+type(exc).__name__)
    if candidate_report.failures and 'unresolved_behavior_findings' not in issues:
        issues.append('unresolved_behavior_findings')
    issues.extend('candidate_path_policy:'+x for x in path_findings)
    issues.extend('edit_scope:'+x for x in scope_findings)
    if problems:issues.extend('protected_integrity:'+p for p in problems)
    return {'status':'PASS_REVIEW_GATE_ONLY' if not issues else 'FAIL','review_findings':issues,
            'behavior':candidate_report.as_dict(),'fault_probe':probe,
            'protected_changes':problems,
            'edit_scope':{'baseline_requested':scope_baseline is not None,'findings':scope_findings},
            'scope':'selected synthetic examples; no independent stakeholder oracle validation, human sign-off, live AI, sandbox, production SAST or security audit'}
