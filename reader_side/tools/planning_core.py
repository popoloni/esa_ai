"""CP07 owner-run plan validation; synthetic offline teaching gate, NOT runtime enforcement."""
from __future__ import annotations
from pathlib import Path, PurePosixPath
import json, hashlib
from review_register_core import pending_review_findings
from prose_review_core import rubric_text
ROOT=Path(__file__).resolve().parents[2]
IDS=('T07-01','T07-02','T07-03','T07-04','T07-05','T07-06')
SOURCES={'INT-001':'reader_side/intent/INT-001.md','SPEC-004/v1':'reader_side/reference_solution/specification.json','ADR-005':'reader_side/reference_solution/architecture_decision.json','CTX-006':'reader_side/reference_solution/context_packet.json'}
CURRENT_SOURCES = dict(SOURCES, **{'CTX-006':'reader_side/reference_solution/v2/context_packet.json'})
PLAN_SCHEMA='delegation-plan/v2'
HANDOFF_SCHEMA='delegation-handoff/v2'
SAFE_WRITE='src/treasury/architecture/direct.py'
PENDING='PROPOSED_FOR_HUMAN_ARCHITECTURE_REVIEW'
READ_ONLY=('READ_ONLY_AGENT','READ_ONLY_REVIEWER','HUMAN_DECISION')

def read_json(path):
    try:return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError,ValueError):return None

def safe_relpath(s):
    if not isinstance(s,str) or not s or '\\' in s or '\x00' in s:return False
    p=PurePosixPath(s)
    return not p.is_absolute() and str(p)==s and all(x not in ('..','.') for x in s.split('/'))

def _check_receipts(plan, errors, root):
    sources = CURRENT_SOURCES if plan.get('schema') == PLAN_SCHEMA else SOURCES
    r=plan.get('source_receipts',[])
    if not isinstance(r,list):errors.append('SOURCES_NOT_LIST');return
    actual={x.get('source_id'):x for x in r if isinstance(x,dict)}
    for sid,rel in sources.items():
        record=actual.get(sid)
        if not record or record.get('path')!=rel:errors.append('SOURCE_MISSING_OR_PATH:'+sid);continue
        p=root/rel
        if not p.is_file() or p.is_symlink():errors.append('SOURCE_MISSING:'+sid);continue
        if hashlib.sha256(p.read_bytes()).hexdigest()!=record.get('sha256'):errors.append('SOURCE_SHA_MISMATCH:'+sid)
    if set(actual)!=set(sources) or len(r)!=len(actual):errors.append('SOURCE_COUNT_OR_EXTRA')

def validate(plan,handoff,root=ROOT):
    issues=[]
    if not isinstance(plan,dict) or not isinstance(handoff,dict):return ['MALFORMED_PLAN_OR_HANDOFF']
    for key,value in [('plan_id','PLAN-007/v1'),('from_checkpoint','CP06'),('spec_id','SPEC-004/v1'),('intent_id','INT-001')]:
        if plan.get(key)!=value:issues.append('IDENTITY:'+key)
    if plan.get('schema') not in (None, 'delegation-plan/v1', PLAN_SCHEMA):
        issues.append('PLAN_SCHEMA_UNSUPPORTED')
    if plan.get('schema') == PLAN_SCHEMA:
        if plan.get('record_revision') != 2 or handoff.get('record_revision') != 2 or handoff.get('schema') != HANDOFF_SCHEMA:
            issues.append('PLAN_HANDOFF_SCHEMA_REVISION_MISMATCH')
        for label, record in [('PLAN',plan),('HANDOFF',handoff)]:
            issues.extend(label+':'+x for x in pending_review_findings(record.get('pending_reviews')))
    elif handoff.get('schema') not in (None, 'delegation-handoff/v1'):
        issues.append('PLAN_HANDOFF_SCHEMA_MISMATCH')
    _check_receipts(plan,issues,root)
    auth=plan.get('authority',{})
    if not isinstance(auth,dict):auth={}
    for field,expected in [('routing_threshold_eur',5000),('payment_approval_allowed',False),('architecture_status',PENDING),('release_authorized',False),('architecture_decision','ADR-005')]:
        if auth.get(field)!=expected:issues.append('AUTHORITY:'+field)
    for field,value in [('payment_approval_allowed',False),('release_authorized',False)]:
        if auth.get(field) is not value:issues.append('BOOLEAN_TYPE:'+field)
    b=plan.get('budgets',{})
    if not isinstance(b,dict):b={}
    for key,maximum in [('max_concurrent_agents',2),('max_model_invocations',6),('max_retries_per_task',1),('max_elapsed_minutes',45)]:
        v=b.get(key)
        if type(v) is not int or not 0<v<=maximum:issues.append('BUDGET:'+key)
    selection=plan.get('selection',{})
    if not isinstance(selection,dict) or selection.get('execution_mode')!='BOUNDED_SINGLE_WRITER':issues.append('MODE_NOT_JUSTIFIED')
    if not isinstance(selection.get('reason'),str) or len(selection['reason'].strip())<20:issues.append('SELECTION_RATIONALE_MISSING')
    tasks=plan.get('tasks')
    if not isinstance(tasks,list):return issues+['TASKS_NOT_LIST']
    by={t.get('id'):t for t in tasks if isinstance(t,dict) and isinstance(t.get('id'),str)}
    if len(tasks)!=len(by) or set(by)!=set(IDS):issues.append('TASK_IDS_OR_DUPLICATES')
    # Required task dependencies and statuses model a state *before* any owner approval.
    expected={
        'T07-01':([], 'READY','READ_ONLY_AGENT'),
        'T07-02':([], 'READY','READ_ONLY_AGENT'),
        'T07-03':(['T07-01','T07-02'],'PENDING_HUMAN','HUMAN_DECISION'),
        'T07-04':(['T07-03'],'BLOCKED','CODING_AGENT'),
        'T07-05':(['T07-04'],'BLOCKED','READ_ONLY_REVIEWER'),
        'T07-06':(['T07-05'],'PENDING_HUMAN','HUMAN_DECISION')}
    for tid,(deps,status,kind) in expected.items():
        t=by.get(tid)
        if not t:continue
        if t.get('depends_on')!=deps:issues.append('DEPENDENCIES:'+tid)
        if t.get('state')!=status:issues.append('STATE:'+tid)
        if t.get('kind')!=kind:issues.append('ROLE_KIND:'+tid)
        for k in ('title','assigned_to','expected_output'):
            if not isinstance(t.get(k),str) or len(t[k].strip())<3:issues.append('UNDEFINED_OUTPUT_OR_OWNER:'+tid+':'+k)
        if t.get('max_attempts')!=1:issues.append('TASK_RETRY_POLICY:'+tid)
        refs=t.get('read_refs',[])
        if not isinstance(refs,list) or not refs or not set(refs).issubset(SOURCES):issues.append('UNBOUNDED_READ_SOURCES:'+tid)
        writes=t.get('write_paths',[])
        if not isinstance(writes,list):issues.append('WRITES_NOT_LIST:'+tid);continue
        if kind in READ_ONLY and writes:issues.append('READ_ONLY_WRITES:'+tid)
        if kind=='CODING_AGENT' and writes!=[SAFE_WRITE]:issues.append('WRITER_SCOPE:'+tid)
        for p in writes:
            if not safe_relpath(p):issues.append('ESCAPED_WRITE_PATH:'+tid)
            if p.startswith('reader_side/') or p.startswith('.github/') or p.startswith('engineering/specifications/') or p.startswith('engineering/architecture/'):issues.append('PROTECTED_PATH:'+tid)
    if plan.get('schema') == PLAN_SCHEMA:
        for tid, subjects in [('T07-03',['SPEC-004','ADR-005']),('T07-06',['OPERATOR_COPY'])]:
            if by.get(tid,{}).get('decision_subjects') != subjects:
                issues.append('PENDING_REVIEW_TASK_BINDING:'+tid)
    # DAG check independent of mandated example shape.
    def visit(x,seen,stack):
        if x in stack:return True
        if x in seen:return False
        seen.add(x);stack.add(x)
        for y in by.get(x,{}).get('depends_on',[]):
            if y not in by:issues.append('DANGLING_DEP:'+x);continue
            if visit(y,seen,stack):return True
        stack.remove(x);return False
    seen=set()
    for x in by:
        if x not in seen and visit(x,seen,set()):issues.append('TASK_GRAPH_CYCLE');break
    parallel=plan.get('parallel_read_only_task_ids')
    if parallel!=['T07-01','T07-02']:issues.append('PARALLEL_SET_NOT_READ_ONLY')
    else:
        if any(by[x].get('write_paths') for x in parallel if x in by):issues.append('PARALLEL_WRITES')
    policy=plan.get('worktree_policy',{})
    if not isinstance(policy,dict) or policy.get('shared_state_review_required') is not True or policy.get('mandatory') is not False:issues.append('WORKTREE_POLICY')
    acceptance=plan.get('acceptance',{})
    for k,e in [('maker_may_edit_reader_oracle',False),('makers_may_approve_own_work',False),('human_decision_required_before_write',True)]:
        if not isinstance(acceptance,dict) or acceptance.get(k) is not e:issues.append('ACCEPTANCE:'+k)
    hs=[('handoff_id','HOF-007/v1'),('plan_id','PLAN-007/v1'),('architecture_decision','ADR-005'),('architecture_status',PENDING),('policy_threshold_eur',5000),('payment_approval_allowed',False),('release_authorized',False),('claim','PLANNING_ONLY_NOT_EXECUTED')]
    for k,v in hs:
        if handoff.get(k)!=v:issues.append('HANDOFF:'+k)
    if handoff.get('source_ids')!=list(SOURCES):issues.append('HANDOFF_SOURCES')
    for key,values in [('tasks_ready',['T07-01','T07-02']),('tasks_blocked',['T07-04','T07-05']),('human_decisions_pending',['T07-03','T07-06']),('agent_execution_evidence',[])]:
        if handoff.get(key)!=values:issues.append('HANDOFF_STATE:'+key)
    next_step = handoff.get('recommended_next_step')
    if not isinstance(next_step,str) or not next_step.strip():
        issues.append('TEXT_MISSING:planning.handoff next action')
    elif 'review' not in next_step.lower() and 'architecture' not in next_step.lower():
        issues.append('HUMAN_SEMANTIC_REVIEW:planning.handoff next action: review whether the next action preserves pending decisions')
    return sorted(set(issues))

def ready_levels(plan, worker_slots=1):
    """Illustrative dependency *rounds*, not wall-clock, tokens or real agent execution."""
    tasks=plan.get('tasks',[])
    available={t['id']:t for t in tasks if t.get('kind')=='READ_ONLY_AGENT'}
    if type(worker_slots) is not int or worker_slots<1:raise ValueError('slots must be >=1')
    ready=[x for x in ('T07-01','T07-02') if x in available and not available[x].get('depends_on')]
    return [ready[i:i+worker_slots] for i in range(0,len(ready),worker_slots)]
