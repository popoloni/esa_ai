"""Cumulative teaching handoff and independent review of the actual CP08 code.

Known author-created Python is executed locally. This gate is not a sandbox,
human sign-off or a release decision. Receipts identify exact input bytes.
"""
from pathlib import Path
from hashlib import sha256
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'repo/src'))
from scope_guard import check_integrity, check_edit_scope
import discovery_core
import specification_core
import architecture_core
import knowledge_core
import planning_core
import implementation_core
import verification_core
from provenance_core import observed_evidence_paths, provenance_summary
from review_register_core import pending_review_ids
from prose_review_core import finding_state

INPUT_PAIRS = {
 'discovery': ('repo/engineering/discovery/assessment.json', 'reader_side/reference_solution/assessment.json'),
 'specification': ('repo/engineering/specifications/explanation_alpha/specification.json', 'reader_side/reference_solution/specification.json'),
 'architecture': ('repo/engineering/architecture/architecture_decision.json', 'reader_side/reference_solution/architecture_decision.json'),
 'adr': ('repo/engineering/architecture/ADR-005.md', 'reader_side/reference_solution/ADR-005.md'),
 'knowledge': ('repo/engineering/knowledge/context_packet.json', 'reader_side/reference_solution/v2/context_packet.json'),
 'skill': ('repo/.agents/skills/context-audit/SKILL.md', 'reader_side/reference_solution/context-audit.SKILL.md'),
 'plan': ('repo/engineering/planning/delegation_plan.json', 'reader_side/reference_solution/v2/delegation_plan.json'),
 'planning_handoff': ('repo/engineering/planning/delegation_handoff.json', 'reader_side/reference_solution/v2/delegation_handoff.json'),
 'implementation': ('repo/src/treasury/explanation_alpha.py', 'reader_side/reference_solution/explanation_alpha.py'),
 'implementation_report': ('repo/engineering/implementation/implementation_report.json', 'reader_side/reference_solution/v2/implementation_report.json'),
 'verification_candidate': ('repo/engineering/verification/candidate.py', 'reader_side/reference_solution/ch09/safe_candidate.py'),
 'verification_review': ('repo/engineering/verification/review.json', 'reader_side/reference_solution/ch09/reference_review.json'),
}
SHARED_INPUTS = [
 'repo/src/treasury/__init__.py', 'repo/src/treasury/routing.py',
 'repo/src/treasury/architecture/__init__.py', 'repo/src/treasury/architecture/direct.py',
 'repo/src/treasury/architecture/ports.py',
 'reader_side/intent/INT-001.md', 'reader_side/specs/case_oracle.json',
 'reader_side/reference_solution/specification.json',
 'reader_side/discovery/sources/SRC-POL-001.json',
 'reader_side/knowledge/source_catalogue.json', 'reader_side/knowledge/claim_dependencies.json',
 'reader_side/implementation/WORK_ORDER_CP08.md', 'reader_side/protected_sha256.json',
]
PRESENTATION_LABELS = {'STANDARD_QUEUE': 'RECOMMENDED_STANDARD_QUEUE',
                       'HUMAN_REVIEW': 'RECOMMENDED_HUMAN_REVIEW', 'REJECTED': 'REJECTED'}


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def input_paths(reference=False, candidate=None, report=None):
    paths = {name: ROOT / pair[int(reference)] for name, pair in INPUT_PAIRS.items()}
    if candidate is not None:
        paths['implementation'] = Path(candidate).resolve()
    if report is not None:
        paths['implementation_report'] = Path(report).resolve()
    return paths


def receipt_inputs(paths):
    root = ROOT.resolve()
    evidence = set(observed_evidence_paths(read_json(paths['implementation_report']), root=root))
    all_paths = set(paths.values()) | {root / rel for rel in SHARED_INPUTS} | evidence
    receipts = {}
    for path in sorted(all_paths, key=str):
        path = path.resolve()
        name = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
        receipts[name] = 'MISSING' if path in evidence and not path.is_file() else sha256(path.read_bytes()).hexdigest()
    return receipts


def presentation_findings(fn):
    """Reviewer expectations come from the owner oracle, not the producer's labels."""
    findings = []
    for case in verification_core.selected_cases():
        try:
            out = fn(case['input_amount_eur'])
            if not isinstance(out, dict) or out.get('status_label') != PRESENTATION_LABELS[case['expected_route']]:
                findings.append('presentation_label:' + case['id'])
        except Exception as exc:
            findings.append('presentation_exception:' + case['id'] + ':' + type(exc).__name__)
    return findings


def check_receipt(receipt, current, mode):
    if not isinstance(receipt, dict) or receipt.get('schema') not in ('integrated-lab-review/v1', 'integrated-lab-review/v2'):
        return ['RECEIPT_SCHEMA']
    issues = []
    if receipt.get('status') != 'PASS_REVIEW_GATE_ONLY':
        issues.append('RECEIPT_NOT_PREVIOUSLY_PASSED')
    if receipt.get('mode') != mode:
        issues.append('RECEIPT_MODE_MISMATCH')
    old = receipt.get('input_receipts')
    if not isinstance(old, dict):
        return issues + ['RECEIPT_INPUTS_MISSING']
    for name in sorted(set(old) | set(current)):
        if old.get(name) != current.get(name):
            issues.append('STALE_RECEIPT:' + name)
    return issues


def canonical_route_findings(paths):
    """CP05 permits exploration; the shipped CP06--CP09 continuation is DIRECT.

    Validate the selected current architecture against downstream assumptions.
    Never rewrite the learner decision or promote a proposed design to acceptance.
    """
    architecture = read_json(paths['architecture'])
    context = read_json(paths['knowledge'])
    plan = read_json(paths['plan'])
    issues = []
    selected = architecture.get('selected_design')
    if selected != 'direct':
        issues.append('UNSUPPORTED_CUMULATIVE_ROUTE:' + str(selected) +
                      ': CP05 accepts ports as a design exploration; the supplied CP06--CP09 continuation is DIRECT. '
                      'Keep the ports decision as a separate exploration. To continue this route, deliberately select and review DIRECT '
                      'and refresh downstream context and receipts, or author a separately versioned ports continuation.')
    if context.get('architecture_choice') != 'DIRECT_ADAPTER_PROPOSED':
        issues.append('CANONICAL_ROUTE_CONTEXT_MISMATCH: cumulative context must describe the current DIRECT proposal')
    writers = [task for task in plan.get('tasks', []) if isinstance(task, dict) and task.get('kind') == 'CODING_AGENT']
    if any(task.get('write_paths') != [planning_core.SAFE_WRITE] for task in writers):
        issues.append('CANONICAL_ROUTE_WRITER_MISMATCH: downstream plan must target the DIRECT adapter')
    # Compare decision-bearing fields, not the wording of alternative rationales.
    sources = planning_core.CURRENT_SOURCES if plan.get('schema') == planning_core.PLAN_SCHEMA else planning_core.SOURCES
    pinned_architecture = read_json(ROOT / sources['ADR-005'])
    for field in ('decision_id', 'version', 'specification_id', 'status', 'selected_design'):
        if architecture.get(field) != pinned_architecture.get(field):
            issues.append('CURRENT_ARCHITECTURE_DIFFERS_FROM_PLANNED_SOURCE:' + field)
    pending = pending_review_ids(context)
    if plan.get('schema') == planning_core.PLAN_SCHEMA:
        planned = {x.get('review_id') for x in plan.get('pending_reviews', []) if isinstance(x, dict)}
    else:
        planned = {'ADR-005', 'OPERATOR_COPY'}
    issues += ['PENDING_REVIEW_NOT_PROPAGATED:' + key for key in sorted(pending - planned)]
    return issues


def review_workflow(reference=False, candidate=None, report=None, receipt=None, scope_baseline=None):
    paths = input_paths(reference, candidate, report)
    mode = 'REFERENCE_FIXTURES' if reference else 'WORKING_CANDIDATES'
    issues = ['protected_integrity:' + p for p in check_integrity()]
    layers = {}
    receipts = {}
    independent = None
    try:
        receipts = receipt_inputs(paths)
    except (OSError, ValueError) as exc:
        issues.append('INPUT_UNREADABLE:' + type(exc).__name__)
    if scope_baseline:
        issues.extend(check_edit_scope(scope_baseline, chapter='CP08'))
    # Never execute fixtures after a known checker/oracle integrity failure.
    if not issues:
        checks = {
            'CP03_discovery': lambda: discovery_core.validate_decision(read_json(paths['discovery'])),
            'CP04_specification': lambda: specification_core.validate(read_json(paths['specification'])),
            'CP05_architecture': lambda: architecture_core.check_behavior() + architecture_core.check_design(read_json(paths['architecture'])) + architecture_core.check_adr(paths['adr'].read_text(), read_json(paths['architecture'])),
            'CP05_CP07_canonical_route': lambda: canonical_route_findings(paths),
            'CP06_knowledge': lambda: knowledge_core.evaluate(paths['knowledge'], paths['skill']),
            'CP07_planning': lambda: planning_core.validate(read_json(paths['plan']), read_json(paths['planning_handoff'])),
            'CP08_implementation': lambda: implementation_core.check_implementation(implementation_core.load_candidate(paths['implementation'])) + implementation_core.report_findings(read_json(paths['implementation_report']), candidate_path=paths['implementation']),
        }
        for name, fn in checks.items():
            try:
                findings = fn()
            except Exception as exc:
                findings = ['input_or_execution_error:' + type(exc).__name__]
            layers[name] = {'status': finding_state(findings), 'findings': findings}
            issues.extend(name + ':' + x for x in findings)
        try:
            independent = verification_core.check_known_candidate(paths['implementation'], entry_point='build_explanation').as_dict()
            findings = independent['failures'] + presentation_findings(implementation_core.load_candidate(paths['implementation']))
        except Exception as exc:
            findings = ['input_or_execution_error:' + type(exc).__name__]
        layers['CP09_reviews_CP08'] = {'status': 'PASS' if not findings else 'FAIL', 'findings': findings, 'independent_cases': independent}
        issues.extend('CP09_reviews_CP08:' + x for x in findings)
        try:
            legacy = verification_core.owner_gate(paths['verification_candidate'], paths['verification_review'])
            findings = legacy['review_findings']
        except Exception as exc:
            findings = ['input_or_execution_error:' + type(exc).__name__]
        layers['CP09_verification_exercise'] = {'status': 'PASS' if not findings else 'FAIL', 'findings': findings}
        issues.extend('CP09_verification_exercise:' + x for x in findings)
    if receipt is not None:
        try:
            prior = read_json(receipt) if isinstance(receipt, (str, Path)) else receipt
            issues.extend(check_receipt(prior, receipts, mode))
        except (OSError, ValueError, TypeError) as exc:
            issues.append('RECEIPT_UNREADABLE:' + type(exc).__name__)
    try:
        provenance = provenance_summary(read_json(paths['implementation_report']))
    except (OSError, ValueError, AttributeError):
        provenance = {'schema_mode': 'REPORT_UNREADABLE'}
    status = 'PASS_REVIEW_GATE_ONLY' if not issues else ('HUMAN_SEMANTIC_REVIEW' if all(':HUMAN_SEMANTIC_REVIEW:' in x for x in issues) else 'FAIL')
    return {
        'schema': 'integrated-lab-review/v2',
        'status': status,
        'canonical_route': 'DIRECT',
        'attempt_provenance': provenance,
        'mode': mode, 'findings': issues, 'layers': layers, 'input_receipts': receipts,
        'edit_scope_checked': scope_baseline is not None,
        'authority': {'architecture_status': 'PROPOSED_FOR_HUMAN_ARCHITECTURE_REVIEW',
                      'CP07_T07_03': 'PENDING_HUMAN', 'CP07_T07_04': 'BLOCKED',
                      'payment_authorized': False, 'release_authorized': False,
                      'meaning': 'Required review boundary; valid only when the corresponding input checks pass.'},
        'scope': 'Cumulative synthetic artefact checks plus independent selected cases on the actual CP08 implementation. This gate executes no AI client. A separately retained attempt observation, if declared, is byte-bound and checked for consistency; it does not grant human acceptance, sandbox isolation or release authority.'
    }
