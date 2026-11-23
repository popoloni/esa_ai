#!/usr/bin/env python3
"""Derive 24 concise, decision-free proposal cards from authentic variants.

Each selection is one or more complete source AST statements. Noncontiguous
regions are identified in the caption. Layout alone may change; the combined
selected AST must equal the printed artifact AST. No answer key is read.
"""
from pathlib import Path
import ast
import hashlib
import json
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'curriculum'))
from reflow_python import narrow, dedent_code, check_literal_integrity
OUT = ROOT / 'candidates/cards'
# Keep the full ownership/version/state decision readable on this card.
# All other cards retain the original 15-line ceiling.
LINE_BUDGETS = {'G3-P02': 16}

# scope is a function or Class.method, or empty for module-level selection.
SPECS = {
 'G1-P01': ('reserve: the write transaction after constructing payload and opening the connection.', [('reserve','try:'),('reserve','return Outcome')]),
 'G1-P02': ('The module registry and reserve; get_reservation reads this same registry.', [('', '_records ='),('', 'def reserve')]),
 'G1-P03': ('get_reservation: the unknown-record branch; the helper supplies its read-only URI.', [('get_reservation','if row is None:'),('', 'def _readonly_uri')]),
 'G2-P01': ('reserve: the selected identity and its replay branch.', [('reserve','prior = con.execute'),('reserve','if prior is not None:')]),
 'G2-P02': ('The proposed new series API; existing single-reservation behavior is unchanged.', [('', 'def plan_recurring')]),
 'G2-P03': ('init_db: selected row-conversion statements inside the migration loop, then exception cleanup; identifier, member, asset, start, end and key come from the legacy row.', [('init_db','request_hash ='),('init_db','con.execute("INSERT INTO reservations VALUES'),('init_db','if con.in_transaction:'),('init_db','raise')]),
 'G3-P01': ('The proposed refund API; cancellation ownership and state handling are unchanged.', [('', 'def quote_refund')]),
 'G3-P02': ('cancel: the decision after reading owner, state and version in one write transaction.', [('cancel','if row is None:')]),
 'G3-P03': ('cancel: selected statements in the update branch after the version/state checks, before commit.', [('cancel','con.execute("""'),('cancel','if row[0] != trusted_member_id:')]),
 'G4-P01': ('cost_summary: result after validating and summing every supplied attempt.', [('cost_summary','return {')]),
 'G4-P02': ('cost_summary: result after the attempt totals have been accumulated.', [('cost_summary','return {')]),
 'G4-P03': ('The new helper and its call at the start of cost_summary; subsequent accounting is unchanged.', [('', 'def _billable_attempts'),('cost_summary','attempts =')]),
 'B1-P01': ('assess: exact parsing, validity guard, routing and returned fields; the string-type guard precedes this region.', [('assess','try:'),('assess','if amount is None'),('assess','return RoutingDecision(route')]),
 'B1-P02': ('assess: numeric parsing and routing after the string-type guard.', [('assess','try:'),('assess','if not math.isfinite'),('assess','if amount <'),('assess','return RoutingDecision("HUMAN')]),
 'B1-P03': ('The separate input-policy artifact submitted with the unchanged exact assess implementation.', [('', 'PROPOSED_INPUT_POLICY =')]),
 'B2-P01': ('evaluate_batch: the budget guard before the next provider invocation.', [('evaluate_batch','if len(attempts)'),('evaluate_batch','event ='),('evaluate_batch','attempts.append')]),
 'B2-P02': ('evaluate_batch: response validation after recording the current attempt; exceptions retain the receipt.', [('evaluate_batch','if ('),('evaluate_batch','event["outcome"] = response')]),
 'B2-P03': ('Preflight helper called before the provider loop; error snapshots are attached by evaluate_batch.', [('', 'def _unique_requests'),('evaluate_batch','requests = _unique')]),
 'B3-P01': ('migrate_legacy: required historical fields and policy validation; these checks precede insertion.', [('migrate_legacy','if any(not isinstance(row.get'),('migrate_legacy','if not isinstance(policy')]),
 'B3-P02': ('Existing-identity branch after matching the request fingerprint: selected statements before return.', [('PolicyStore._decide','current ='),('PolicyStore._decide','record = {'),('PolicyStore._decide','return {"status": "REPLAYED"')]),
 'B3-P03': ('`_decide`: existing-identity handling occurs before active-policy selection for new work.', [('PolicyStore._decide','if existing is not None:')]),
 'B4-P01': ('diagnose: the two state observations used by all subsequent comparisons.', [('diagnose','selected, expected =')]),
 'B4-P02': ('recovery_plan: the currently supplied plan; the proposed merge is a separate requested change.', [('recovery_plan','return {')]),
 'B4-P03': ('diagnose: state selection and returned status, around the path, policy and anchor comparisons.', [('diagnose','selected, expected ='),('diagnose','return {')]),
}


def accounting_result(denominator):
    return f'''return {{
    "attempts": len(attempts),
    "accepted_outcomes": accepted,
    "total_cost_eur": str(money),
    "total_minutes": str(minutes),
    "cost_per_accepted_eur": (
        None if accepted == 0 else str(money / {denominator})),
    "minutes_per_accepted": (
        None if accepted == 0 else str(minutes / accepted)),
    "status": (
        "NO_ACCEPTED_OUTCOME" if accepted == 0 else "ACCOUNTED")}}
'''


LAYOUTS = {
 'G4-P01': accounting_result('accepted'),
 'G4-P02': accounting_result('len(attempts)'),
 'B4-P02': '''return {
    "restore_configuration_to": diagnosis["expected"]["path"],
    "preserve_ledgers": [
        diagnosis["selected"]["path"],
        diagnosis["expected"]["path"]],
    "verification": [
        "historical replay",
        "current-policy decision on disposable copy",
        "restart and state binding"],
    "automatic_merge": False,
    "reconciliation": "PENDING_OWNER_DECISION",
    "production_authorized": False}
''',
}


def sha(data): return hashlib.sha256(data).hexdigest()


def selection(tree, lines, scope, prefix):
    node = tree
    if scope:
        for part in scope.split('.'):
            node = next(n for n in node.body if getattr(n,'name',None) == part)
    found = [n for n in ast.walk(node) if isinstance(n, ast.stmt)
             and lines[n.lineno-1].lstrip().startswith(prefix)]
    if prefix == 'raise':
        found = [n for n in found if isinstance(n,ast.Raise) and n.exc is None]
    if found:
        first = min(n.lineno for n in found)
        column = min(n.col_offset for n in found if n.lineno == first)
        found = [n for n in found if n.lineno == first and n.col_offset == column]
    if len(found) != 1:
        raise ValueError((scope,prefix,len(found)))
    n = found[0]
    # Retain the actual string tokens. ast.unparse would turn triple-quoted
    # SQL/docstrings into escaped strings before the layout check could see it.
    fragment = dedent_code(''.join(lines[n.lineno-1:n.end_lineno]))
    assert ast.dump(ast.parse(fragment).body[0],include_attributes=False) == ast.dump(n,include_attributes=False), (scope,prefix,fragment,ast.dump(n,include_attributes=False))
    return fragment, {'scope':scope,'prefix':prefix,'first_line':n.lineno,'last_line':n.end_lineno,
                      'node_sha256':sha(ast.dump(n,include_attributes=False).encode())}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    records, missions = [], {}
    for identifier,(caption,selectors) in SPECS.items():
        mission = identifier.split('-')[0]
        source = ROOT/'candidates'/mission/identifier/'variant.py'
        data = source.read_bytes();lines=data.decode().splitlines(keepends=True)
        tree = ast.parse(data.decode()); fragments, origins = [], []
        for scope,prefix in selectors:
            fragment,origin=selection(tree,lines,scope,prefix)
            fragments.append(fragment.rstrip());origins.append(origin)
        joined='\n'.join(fragments)+'\n'
        artifact=LAYOUTS.get(identifier) or narrow(joined,68)
        assert ast.dump(ast.parse(artifact),include_attributes=False) == ast.dump(ast.parse(joined),include_attributes=False),identifier
        literal_checks = check_literal_integrity(joined, artifact)
        count=len(artifact.splitlines());width=max(map(len,artifact.splitlines()))
        if count > LINE_BUDGETS.get(identifier, 15) or width > 68:
            raise ValueError((identifier,count,width,artifact))
        path=OUT/(identifier+'.py');path.write_text(artifact)
        rationale_path=source.parent/'RATIONALE.md'
        rationale=rationale_path.read_text().split('\n\n',1)[1].strip()
        card=f'### {identifier}\n\n{rationale}\n\n*Artifact: {caption}*\n\n```python\n{artifact.rstrip()}\n```\n'
        missions.setdefault(mission,[]).append(card)
        records.append({'candidate_id':identifier,'source':str(source.relative_to(ROOT)),
                        'source_sha256':sha(data),'rationale_sha256':sha(rationale_path.read_bytes()),
                        'output':str(path.relative_to(ROOT)),'output_sha256':sha(path.read_bytes()),
                        'selections':origins,'ast_equivalent':True,'lines':count,'max_line_length':width,
                        'literal_checks':literal_checks,
                        'line_budget':LINE_BUDGETS.get(identifier,15),
                        'line_budget_reason':('Full owner/version/state branches use conventional multiline layout.' if identifier=='G3-P02' else 'Standard concise card ceiling.'),
                        'transformation':'Selected complete original source statements; deterministic whitespace reflow outside literal tokens; caption identifies omitted context.'})
    for mission,cards in missions.items(): (OUT/(mission+'.md')).write_text('\n'.join(cards))
    (OUT/'PROVENANCE.json').write_text(json.dumps({'schema':'esa-proposal-cards/v1',
        'answer_key_read':False,'cards':records},indent=2)+'\n')
    print(json.dumps({'status':'PASS','cards':len(records),'max_lines':max(x['lines'] for x in records),
                      'max_columns':max(x['max_line_length'] for x in records)},indent=2))

if __name__=='__main__':main()
