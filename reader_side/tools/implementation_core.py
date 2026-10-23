"""CP08 selected-case oracle plus separately bound attempt provenance."""
from pathlib import Path
import json,importlib.util,sys
from provenance_core import provenance_findings
ROOT=Path(__file__).resolve().parents[2]
REPO=ROOT/'repo'
CODE=REPO/'src/treasury/explanation_alpha.py'
REPORT=REPO/'engineering/implementation/implementation_report.json'
SCENARIOS=json.loads((ROOT/'reader_side/reference_solution/specification.json').read_text())['scenarios']
LABELS={'STANDARD_QUEUE':'RECOMMENDED_STANDARD_QUEUE','HUMAN_REVIEW':'RECOMMENDED_HUMAN_REVIEW','REJECTED':'REJECTED'}
NOTICE='ROUTING_ONLY_NOT_PAYMENT_APPROVAL'
REQUIRED_KEYS={'status_label','route','reason_code','policy_version','payment_authorized','notice','benefit_status'}

def load_candidate(path=CODE):
    # The reader-side CLI must also work without a caller-supplied PYTHONPATH.
    # Both reference and learner modules import the same local Treasury package.
    source_root=str((REPO/'src').resolve())
    if source_root not in sys.path:
        sys.path.insert(0,source_root)
    spec=importlib.util.spec_from_file_location('candidate_explanation_cp08',Path(path).resolve())
    if spec is None or spec.loader is None:
        raise ValueError('candidate must be a loadable Python source file')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.build_explanation

def check_implementation(fn):
    errors=[]
    for item in SCENARIOS:
        case=item['id']
        try: out=fn(item['input_amount_eur'])
        except Exception as ex:errors.append(case+': raised '+str(ex));continue
        if not isinstance(out,dict):errors.append(case+': output is not object');continue
        if set(out)!=REQUIRED_KEYS:errors.append(case+': field contract mismatch')
        expected={'route':item['expected_route'],'reason_code':item['expected_reason'],'policy_version':item['expected_policy_version'],'status_label':LABELS[item['expected_route']],'payment_authorized':False,'notice':NOTICE,'benefit_status':'HYPOTHESIS_NOT_VALIDATED'}
        for key,val in expected.items():
            if out.get(key)!=val:errors.append(case+': '+key+' mismatch')
    return errors

def report_findings(v, *, root=ROOT, candidate_path=CODE):
    if not isinstance(v,dict): return ['REPORT_NOT_OBJECT']
    expect={'change_id':'IMPL-008/v1','intent_ref':'INT-001','spec_ref':'SPEC-004/v1','architecture_ref':'ADR-005','architecture_status':'PROPOSED_FOR_HUMAN_ARCHITECTURE_REVIEW','scope':'explanation_only','changed_files':['src/treasury/explanation_alpha.py'],'checks':'CP08_SELECTED_OFFLINE_CASES_PASS','status':'READY_FOR_HUMAN_REVIEW_NOT_ACCEPTED','human_approver':None,'value_validated':False}
    errs=[]
    for k,correct in expect.items():
        if v.get(k)!=correct:errs.append(k+': wrong claim or provenance')
    if not isinstance(v.get('unresolved_questions'),list) or not v.get('unresolved_questions'):errs.append('unresolved questions missing')
    errs.extend(provenance_findings(v, root=root, candidate_path=candidate_path))
    return errs
