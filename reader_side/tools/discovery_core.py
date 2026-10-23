"""Small offline teaching gate for CP03 discovery. Not a human authority substitute.

Every source and metric is synthetic. Strict schema checks are necessary but
cannot determine whether a real discovery decision is good or whether a model
has faithfully researched real users.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
from statistics import median
from hashlib import sha256
import csv,json,math
from prose_review_core import rubric_text

ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'reader_side/discovery'
MANIFEST=PACKET/'input_sha256.json'
ROUTING=ROOT/'repo/src/treasury/routing.py'
ROUTING_ORIGINAL=PACKET/'routing.sha256'

def json_read(p): return json.loads(Path(p).read_text(encoding='utf-8'))

def check_packet_integrity(packet=PACKET):
    manifest=json_read(packet/'input_sha256.json')
    issues=[]
    for rel, expected in manifest.items():
        file=packet/rel
        if file.is_symlink() or not file.is_file() or sha256(file.read_bytes()).hexdigest()!=expected:
            issues.append(rel)
    return issues

def collect_baseline(csv_path=None):
    """Exclude missing endpoint records from denominator; report that exclusion."""
    file=csv_path or PACKET/'triage_cases.csv'
    with Path(file).open(newline='',encoding='utf-8') as f:
        records=list(csv.DictReader(f))
    ids=[row['case_id'] for row in records]
    if len(ids)!=len(set(ids)): raise ValueError('duplicate case_id')
    vals=[];missing=0
    for row in records:
        start=row.get('created_utc','').strip()
        end=row.get('routed_utc','').strip()
        if not start or not end:
            missing+=1
            continue
        a,b=datetime.fromisoformat(start),datetime.fromisoformat(end)
        if a.tzinfo is None or b.tzinfo is None: raise ValueError('timezone required')
        hours=(b-a).total_seconds()/3600
        if not math.isfinite(hours) or hours<0: raise ValueError('invalid elapsed duration')
        vals.append(hours)
    if not vals: raise ValueError('no measurable cases')
    return {'total_cases':len(records),'measured_cases':len(vals),'excluded_missing':missing,
     'over_24h_cases':sum(x>24 for x in vals),'over_24h_denominator':len(vals),
     'median_hours':float(median(vals))}

def validate_decision(decision, *, packet=PACKET, routing=ROUTING):
    issues=[]
    if check_packet_integrity(packet): issues.append('source packet integrity differs')
    original=(packet/'routing.sha256').read_text(encoding='ascii').strip()
    if routing.is_symlink() or not routing.is_file() or sha256(routing.read_bytes()).hexdigest()!=original:
        issues.append('routing source changed during discovery')
    expected=collect_baseline(packet/'triage_cases.csv')
    if decision.get('assessment_id')!='DISC-003/v1': issues.append('wrong discovery record identity')
    if decision.get('status')!='CONDITIONAL_GO_TO_LIMITED_ALPHA': issues.append('not a bounded alpha decision')
    if decision.get('decision_owner')!='Product Owner (synthetic scenario)': issues.append('decision owner missing or misidentified')
    if decision.get('policy_authority')!='SRC-POL-001': issues.append('non-authoritative policy source')
    if decision.get('starting_request')!='SRC-TKT-017': issues.append('missing original request provenance')
    if decision.get('initial_solution')!='auto_approve_below_5000' or decision.get('selected_option')!='explain_routing':
        issues.append('unrevised or incorrect engineering choice')
    for prohibited in ('auto_approve','move_funds','change_threshold'):
        if prohibited not in decision.get('excluded_changes',[]): issues.append('missing explicit non-scope: '+prohibited)
    ids=set(decision.get('source_ids',[]))
    required={'SRC-TKT-017','SRC-POL-001','SRC-OPS-004','SRC-RISK-002','SRC-WIKI-OLD','SYN-TRIAGE-CSV'}
    if not required.issubset(ids): issues.append('incomplete source provenance')
    if ids-required:issues.append('unknown source identifiers')
    contradictions=decision.get('contradictions',[])
    if not any(isinstance(c,dict) and c.get('proposal_source')=='SRC-TKT-017' and c.get('policy_source')=='SRC-POL-001' for c in contradictions):
        issues.append('initial proposal/policy contradiction not recorded')
    baseline=decision.get('baseline',{})
    if not isinstance(baseline,dict): baseline={}
    for k,v in expected.items():
        if baseline.get(k)!=v: issues.append('incorrect baseline '+k)
    if decision.get('research_status')!='SYNTHETIC_ONLY_NO_USER_VALIDATION': issues.append('synthetic example misrepresented as user research')
    if decision.get('value_claim')!='HYPOTHESIS_NOT_PROVEN': issues.append('unsupported value claim')
    if len(decision.get('unknowns',[]))<3: issues.append('open discovery questions omitted')
    options={x.get('id') for x in decision.get('alternatives',[]) if isinstance(x,dict)}
    if not {'no_change_training','explain_routing','auto_approve'}.issubset(options):issues.append('alternative options incomplete')
    experiment=decision.get('experiment',{})
    if not isinstance(experiment,dict):experiment={}
    for k in ('hypothesis','measure','collection','stop_rule'):
        if len(str(experiment.get(k,'')))<20: issues.append('incomplete pilot experiment: '+k)
    guardrails=experiment.get('guardrails',[])
    if not isinstance(guardrails,list) or not guardrails:
        issues.append('GUARDRAILS_MISSING')
    else:
        issues.extend(rubric_text(' '.join(str(g) for g in guardrails), 'discovery.guardrails payment authority and policy-version', terms=('No payment approval','BR-001/v1 unchanged')))
    issues.extend(rubric_text(decision.get('handoff'), 'discovery.handoff boundary', prefix='Chapter 4 may specify an explanation-only alpha'))
    return issues
