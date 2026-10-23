"""CP04 offline specification review. Synthetic fixtures, NO semantic-proof or agent autonomy guarantees.

A separately managed runner + protected oracle are assumptions of this teaching example.
In this downloadable archive both are ordinary files and NOT an OS sandbox.
"""
from __future__ import annotations
from pathlib import Path
import csv,hashlib,json
from typing import Any
from prose_review_core import rubric_text

ROOT=Path(__file__).resolve().parents[2]
SIDE=ROOT/'reader_side'
REPO=ROOT/'repo'
SPECBASE=SIDE/'specs'
REFERENCE=SIDE/'reference_solution/specification.json'
PACKET=SIDE/'discovery'
ROUTING=REPO/'src/treasury/routing.py'
MANDATORY_REQ={'REQ-EXPL-001','REQ-EXPL-002','REQ-EXPL-003','REQ-EXPL-004','REQ-EXPL-005'}
MANDATORY_OUT={'auto_approve','move_funds','change_threshold','alter_history','deploy_to_production'}
MANDATORY_IN={'show_route','show_reason_code','show_policy_version','explicit_human_payment_boundary'}
MANDATORY_SOURCE={'SRC-TKT-017','SRC-POL-001','SRC-OPS-004','SRC-RISK-002','SYN-TRIAGE-CSV'}

def load_json(path:Path):
    return json.loads(path.read_text(encoding='utf-8'))

def input_integrity(side:Path=SIDE)->list[str]:
    """Detect changes to selected protected fixture bytes, not prevent an attacker editing them."""
    manifest_path=side/'specs/protected_sha256.json'
    if manifest_path.is_symlink() or not manifest_path.is_file(): return ['missing or symlinked manifest']
    try: manifest=load_json(manifest_path)
    except (ValueError,OSError): return ['unreadable manifest']
    issues=[]
    if not isinstance(manifest,dict): return ['malformed manifest']
    for rel,expected in manifest.items():
        path=side/rel
        if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            issues.append(rel)
    return issues

def _as_list(value): return value if isinstance(value,list) else []
def _as_obj(value): return value if isinstance(value,dict) else {}
def _str(value): return value if isinstance(value,str) else ''

def validate(spec:dict[str,Any],*,side:Path=SIDE,routing:Path=ROUTING)->list[str]:
    issues=[]
    if not isinstance(spec,dict): return ['spec is not a JSON object']
    if input_integrity(side):issues.append('protected source input changed')
    bridge=load_json(side/'specs/discovery_handoff.json')
    oracle=load_json(side/'specs/case_oracle.json')
    if bridge.get('status')!='CONDITIONAL_GO_TO_LIMITED_ALPHA' or bridge.get('selected_option')!='explain_routing':
        issues.append('discovery handoff is not approved for explanation alpha')
    # The Chapter 3 integrity gate checks the routing code independently of any specification draft.
    expected_route_sha=(side/'discovery/routing.sha256').read_text().strip()
    if routing.is_symlink() or not routing.is_file() or hashlib.sha256(routing.read_bytes()).hexdigest()!=expected_route_sha:
        issues.append('routing source changed before design authorization')
    if spec.get('spec_id')!='SPEC-004/v1':issues.append('wrong specification identity')
    if spec.get('status')!='READY_FOR_HUMAN_REQUIREMENTS_REVIEW':issues.append('premature acceptance or wrong review status')
    if spec.get('discovery_id')!=bridge['assessment_id'] or spec.get('discovery_verdict')!=bridge['status']:
        issues.append('invalid discovery decision trace')
    if spec.get('selected_option')!=bridge['selected_option'] or spec.get('capability')!='EXPLAIN_ROUTING_RECOMMENDATION_ONLY':
        issues.append('unauthorized capability expansion')
    if spec.get('policy_authority')!='SRC-POL-001' or spec.get('policy_version')!='BR-001/v1':
        issues.append('incorrect policy authority or version')
    if spec.get('decision_owner')!=bridge['decision_owner'] or spec.get('policy_owner')!='Treasury Policy Owner (synthetic scenario)':
        issues.append('missing human decision owner')
    have_sources=set(_str(x) for x in _as_list(spec.get('source_ids')))
    if have_sources!=MANDATORY_SOURCE:issues.append('missing or invented source provenance')
    if set(_str(x) for x in _as_list(spec.get('scope_out')))!=MANDATORY_OUT:
        issues.append('scope_out missing prohibited actions')
    if set(_str(x) for x in _as_list(spec.get('scope_in')))!=MANDATORY_IN:
        issues.append('scope_in missing limited explanation outputs')
    if spec.get('value_status')!='HYPOTHESIS_NOT_VALIDATED':
        issues.append('unsupported business value assertion')
    if len(_as_list(spec.get('unresolved_questions')))<3:issues.append('discovery unknowns prematurely closed')
    issues.extend(rubric_text(spec.get('handoff'), 'specification.handoff human requirements review', prefix='Ready for human requirements review only'))
    issues.extend(rubric_text(spec.get('authorized_delegation'), 'specification.delegation boundary', prefix='An agent may propose'))
    reqs=_as_list(spec.get('requirements'))
    reqids=[x.get('id') for x in reqs if isinstance(x,dict)]
    if len(reqids)!=len(set(reqids)) or set(reqids)!=MANDATORY_REQ:
        issues.append('missing or duplicate requirement IDs')
    reference=load_json(side/'reference_solution/specification.json')
    required_reference={x['id']:x for x in reference['requirements']}
    for obj in reqs:
        if not isinstance(obj,dict): issues.append('malformed requirement');continue
        rid=obj.get('id')
        if rid not in required_reference:continue
        if len(_str(obj.get('statement')))<45 or 'MUST' not in _str(obj.get('statement')):
            issues.append('missing normative requirement statement: '+rid)
        for forbidden in ('auto-approve all requests','automatically authorize payment','automatically approve payment'):
            if forbidden in _str(obj.get('statement')).lower():issues.append('unauthorized payment behavior: '+rid)
        if obj.get('owner')!=required_reference[rid]['owner']:
            issues.append('incorrect requirement owner: '+rid)
        if set(_as_list(obj.get('source_ids')))!=set(required_reference[rid]['source_ids']):
            issues.append('requirement source provenance inconsistent: '+rid)
        # Unknown wording is a human-review request, not a finding of missing meaning.
        terms={'REQ-EXPL-001':['route','reason','policy version'],
          'REQ-EXPL-002':['payment','human'],
          'REQ-EXPL-003':['invalid','rejection'],
          'REQ-EXPL-004':['policy version','threshold'],
          'REQ-EXPL-005':['hypothes','ROI']}
        text=_str(obj.get('statement')).lower()
        issues.extend(rubric_text(text, 'requirement '+rid, terms=terms.get(rid,[])))
    scenarios=_as_list(spec.get('scenarios'))
    sids=[x.get('id') for x in scenarios if isinstance(x,dict)]
    case_map={x['id']:x for x in oracle['cases']}
    if len(sids)!=len(set(sids)) or set(sids)!=set(case_map):
        issues.append('missing/duplicated scenario coverage')
    for case in scenarios:
        if not isinstance(case,dict):issues.append('malformed scenario');continue
        sid=case.get('id')
        if sid not in case_map:continue
        expected=case_map[sid]
        for key in ('input_amount_eur','expected_route','expected_reason','expected_policy_version','payment_authorized'):
            if case.get(key)!=expected.get(key):issues.append(f'incorrect oracle case {sid}: {key}')
        if case.get('requirement_id')!=expected.get('requirement_id'):
            issues.append('scenario requirement trace mismatch: '+sid)
        for keyword in ('given','when','then'):
            if len(_str(case.get(keyword)))<20:issues.append(f'incomplete Given/When/Then {sid}: {keyword}')
        issues.extend(rubric_text(case.get('given'), 'scenario '+sid+' given payment authority boundary', terms=('human',)))
        issues.extend(rubric_text(case.get('then'), 'scenario '+sid+' then payment authority boundary', terms=('no-payment-approval',)))
    return issues

def projection(spec:dict[str,Any],kind:str)->str:
    """Illustrative writer; NOT vendor CLI or semantic validator."""
    if kind=='portable':
        lines=['# EXPLANATION-ONLY ALPHA — SPEC-004/v1','','_Review candidate; not permission to implement or deploy._','',
               '## Authority',f"- Discovery: {spec['discovery_id']} ({spec['discovery_verdict']})",f"- Policy: {spec['policy_version']} — {spec['policy_authority']}",f"- Owner: {spec['decision_owner']}",'','## Scope','In: '+', '.join(spec['scope_in']),'Out: '+', '.join(spec['scope_out']),'','## Requirements']
        for r in spec['requirements']:
            lines.extend([f"### {r['id']}: {r['name']}",r['statement'],f"Sources: {', '.join(r['source_ids'])}",''])
        lines.append('## Scenarios')
        for s in spec['scenarios']:
            lines.extend([f"### {s['id']}: {s['requirement_id']}",f"**Given** {s['given']}",f"**When** {s['when']}",f"**Then** {s['then']}",''])
        lines.extend(['## Open Questions', *('- '+q for q in spec['unresolved_questions']),'','## Handoff',spec['handoff']])
    elif kind=='openspec':
        lines=['# EXPLANATION-ONLY CHANGE — ILLUSTRATIVE DRAFT','','## ADDED Requirements','']
        for r in spec['requirements']:
            lines += [f"### Requirement: {r['name']}",r['statement'],'']
            for s in spec['scenarios']:
                if s['requirement_id']==r['id']:
                    lines += [f"#### Scenario: {s['id']}",f"- **GIVEN** {s['given']}",f"- **WHEN** {s['when']}",f"- **THEN** {s['then']}",'']
    elif kind=='kiro':
        lines=['# Requirements — explanation-only alpha','','> Illustrative EARS-style mapping; review in Kiro before design.','']
        for r in spec['requirements']:
            lines += [f"## {r['id']} {r['name']}",r['statement']]
            for s in spec['scenarios']:
                if s['requirement_id']==r['id']:
                    lines += [f"WHEN {s['when']}",f"THE SYSTEM SHALL {s['then']}",'']
    elif kind=='gherkin':
        lines=['Feature: Explain the routing recommendation without authorizing payment','  # Illustrative Gherkin; no Cucumber/Behave runner executed.','']
        for s in spec['scenarios']:
            lines += [f"  Scenario: {s['id']}",f"    Given {s['given']}",f"    When {s['when']}",f"    Then {s['then']}",'']
    else:raise ValueError('Unknown projection '+kind)
    return '\n'.join(lines)+'\n'

def export_projections(spec:dict[str,Any],dest:Path)->dict[str,Path]:
    """Generate docs under explicitly passed destination. Call only on reviewed reference."""
    dest.mkdir(parents=True,exist_ok=True)
    files={'portable':'specification.md','openspec':'openspec_delta.spec.md','kiro':'kiro_requirements.md','gherkin':'explanation_alpha.feature'}
    out={}
    for kind,name in files.items():
        p=dest/name;p.write_text(projection(spec,kind),encoding='utf-8');out[kind]=p
    return out
