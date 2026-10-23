"""CP06 synthetic source selection and skill audit; standard library only.
Deterministic selected checks do NOT validate human authority, semantic truth,
model compliance, security isolation or actual skills activation.
"""
from pathlib import Path
import hashlib,json,re
from review_register_core import context_review_findings
from prose_review_core import rubric_text
ROOT=Path(__file__).resolve().parents[2]
REPO=ROOT/'repo'
DATA=ROOT/'reader_side/knowledge'
REF=ROOT/'reader_side/reference_solution/context_packet.json'
PACKET=REPO/'engineering/knowledge/context_packet.json'
SKILL=REPO/'.agents/skills/context-audit/SKILL.md'
EXPECTED_STATUS='PROPOSED_FOR_HUMAN_ARCHITECTURE_REVIEW'

def read_json(path):
    try: return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError,ValueError,UnicodeError): return None

def source_integrity(root=ROOT):
    cat=read_json(root/'reader_side/knowledge/source_catalogue.json')
    if not isinstance(cat,list): return ['SOURCE_CATALOGUE_INVALID']
    failures=[]
    for record in cat:
        try:
            rel=record['relative_path']; p=root/rel
            if p.is_symlink() or not p.is_file() or root.resolve() not in p.resolve().parents:
                failures.append('SOURCE_MISSING_OR_ESCAPED:'+record['id']);continue
            sha=hashlib.sha256(p.read_bytes()).hexdigest()
            if sha != record['sha256']: failures.append('SOURCE_CONTENT_CHANGED:'+record['id'])
        except (TypeError,KeyError,OSError,ValueError): failures.append('SOURCE_RECORD_INVALID')
    return failures

def affected_claims(changed_ids, dependency_map):
    if not isinstance(changed_ids,(list,tuple,set)) or not isinstance(dependency_map,dict):
        raise TypeError('invalid invalidation input')
    changed=set(changed_ids)
    return sorted(k for k,deps in dependency_map.items() if isinstance(deps,list) and changed.intersection(deps))

def lint_skill(raw):
    issues=[]
    if not isinstance(raw,str) or not raw.startswith('---\n'):
        return ['SKILL_FRONTMATTER_MISSING']
    parts=raw.split('---\n',2)
    if len(parts)<3: return ['SKILL_FRONTMATTER_INVALID']
    metadata=parts[1]; body=parts[2]
    fields={}
    for line in metadata.splitlines():
        if ':' in line:
            k,v=line.split(':',1); fields[k.strip()]=v.strip()
    name=fields.get('name',''); desc=fields.get('description','')
    if name!='context-audit': issues.append('SKILL_NAME_INVALID')
    if not (1<=len(desc)<=1024):
        issues.append('SKILL_DESCRIPTION_LENGTH_INVALID')
    else:
        issues.extend(rubric_text(desc, 'skill.description', terms=('context', 'provenance')))
    issues.extend(rubric_text(body, 'skill.procedure', terms=('source catalogue','human review','limitations','source IDs')))
    if 'knowledge_gate.py' not in body:
        issues.append('SKILL_GATE_COMMAND_MISSING:knowledge_gate.py')
    for token in ('automatic approval','promote the old wiki','ignore independent checks','certify payments'):
        if token.lower() in raw.lower(): issues.append('SKILL_UNSAFE_INSTRUCTION:'+token)
    if 'references/CASE_SOURCE_MAP.md' not in raw: issues.append('SKILL_REFERENCE_MISSING')
    return sorted(set(issues))

def assess(packet,skill_text):
    issues=[]
    ref=read_json(REF)
    if not isinstance(packet,dict): return ['CONTEXT_PACKET_INVALID']
    if not isinstance(ref,dict): return ['REFERENCE_UNAVAILABLE']
    for key in ('packet_id','source_catalogue','intent_ref','threshold_eur','payment_authorized',
                'policy_status','architecture_status','architecture_choice','evidence_status','context_confidence'):
        if packet.get(key)!=ref.get(key): issues.append('FIELD_MISMATCH:'+key)
    if packet.get('purpose') != ref.get('purpose'):
        issues.extend(rubric_text(packet.get('purpose'), 'context.purpose', prefix=ref['purpose']))
    ref_sel={x['id']:x['treatment'] for x in ref['source_selections']}
    candidate=packet.get('source_selections',[])
    if not isinstance(candidate,list): issues.append('SELECTIONS_INVALID')
    else:
        ids=[x.get('id') for x in candidate if isinstance(x,dict)]
        if sorted(ids)!=sorted(ref_sel): issues.append('SOURCE_IDS_MISMATCH')
        for x in candidate:
            if isinstance(x,dict) and x.get('id') in ref_sel and x.get('treatment')!=ref_sel[x['id']]:
                issues.append('SOURCE_CLASSIFICATION_WRONG:'+x['id'])
    if packet.get('claim_dependencies')!=ref['claim_dependencies']: issues.append('CLAIM_DEPENDENCIES_MISMATCH')
    issues.extend(context_review_findings(packet))
    if sorted(packet.get('revision_triggers',[]))!=sorted(ref['revision_triggers']):
        issues.append('REFRESH_TRIGGERS_WRONG')
    issues+=lint_skill(skill_text)
    return sorted(set(issues))

def evaluate(packet_path=PACKET, skill_path=SKILL, root=ROOT):
    issues=source_integrity(root)
    try: raw=Path(skill_path).read_text(encoding='utf-8')
    except OSError: raw=''
    issues.extend(assess(read_json(packet_path),raw))
    return sorted(set(issues))
