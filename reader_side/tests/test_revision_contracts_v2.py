"""Regressions for the four reproduced d3 defects and their v2/legacy boundaries.

Observation records created here are synthetic unit-test doubles. No AI client is
invoked or claimed to have been observed by running this suite. The tests assess
evidence binding and schema behavior, not the external authenticity of a record.
"""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import copy
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'reader_side/tools'))
import architecture_core
import discovery_core
import implementation_core
import integration_core
import knowledge_core
import planning_core
import specification_core
from provenance_core import ACTUAL, OFFLINE, provenance_summary
from review_register_core import current_pending_reviews

REF = ROOT / 'reader_side/reference_solution'


def load(name, current=False):
    return json.loads((REF / ('v2' if current else '') / (name + '.json')).read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')
    return path


class CanonicalDirectRegression(unittest.TestCase):
    def test_current_direct_route_passes_and_keeps_pending_authority(self):
        result = integration_core.review_workflow(reference=True)
        self.assertEqual('PASS_REVIEW_GATE_ONLY', result['status'], result['findings'])
        self.assertEqual('DIRECT', result['canonical_route'])
        self.assertEqual('PASS', result['layers']['CP05_CP07_canonical_route']['status'])
        self.assertEqual('BLOCKED', result['authority']['CP07_T07_04'])
        self.assertFalse(result['authority']['release_authorized'])

    def test_valid_ports_exploration_cannot_pass_direct_continuation(self):
        original = (REF / 'architecture_decision.json').read_bytes()
        decision = load('architecture_decision')
        decision['selected_design'] = 'ports'
        self.assertEqual([], architecture_core.check_design(decision))
        with TemporaryDirectory() as directory:
            paths = integration_core.input_paths(reference=True)
            paths['architecture'] = write(Path(directory) / 'ports.json', decision)
            paths['adr'] = Path(directory) / 'ports.md'
            paths['adr'].write_text((REF / 'ADR-005.md').read_text().replace(
                'Propose direct for the limited alpha', 'Propose ports for the limited alpha'))
            self.assertEqual([], architecture_core.check_adr(paths['adr'].read_text(), decision))
            with patch.object(integration_core, 'input_paths', return_value=paths):
                result = integration_core.review_workflow(reference=True)
            self.assertEqual('PASS', result['layers']['CP05_architecture']['status'])
            self.assertEqual('FAIL', result['status'])
            findings = result['layers']['CP05_CP07_canonical_route']['findings']
            self.assertTrue(any(x.startswith('UNSUPPORTED_CUMULATIVE_ROUTE:ports:') for x in findings), findings)
            self.assertIn('CURRENT_ARCHITECTURE_DIFFERS_FROM_PLANNED_SOURCE:selected_design', findings)
            self.assertEqual('ports', json.loads(paths['architecture'].read_text())['selected_design'])
        self.assertEqual(original, (REF / 'architecture_decision.json').read_bytes())

    def test_additional_legacy_pending_review_must_reach_planning(self):
        context = load('context_packet')
        context['human_review_required'].append('SPEC-004')
        with TemporaryDirectory() as directory:
            paths = integration_core.input_paths(reference=True)
            paths['knowledge'] = write(Path(directory) / 'context.json', context)
            paths['plan'] = REF / 'delegation_plan.json'
            self.assertIn('PENDING_REVIEW_NOT_PROPAGATED:SPEC-004', integration_core.canonical_route_findings(paths))


class AttemptProvenanceRegression(unittest.TestCase):
    def observed_fixture(self, root):
        """Synthetic record double, deliberately not exported as live evidence."""
        candidate = root / 'candidate.py'
        candidate.write_bytes((REF / 'explanation_alpha.py').read_bytes())
        transcript = root / 'evidence/transcript.txt'
        transcript.parent.mkdir(parents=True)
        transcript.write_text('SYNTHETIC UNIT TEST: no real agent or model was executed.\n')
        observation = {
            'schema': 'agent-client-observation/v1',
            'record_kind': 'ACTUAL_EXECUTION_RECORD',
            'execution_mode': ACTUAL,
            'change_id': 'IMPL-008/v1',
            'claim_scope': 'CLIENT_ATTEMPT_ONLY_NOT_ACCEPTANCE',
            'run_id': 'UNIT-TEST-RECORD-DOUBLE',
            'environment': 'Temporary unit-test fixture; not an observed client run',
            'client': {'name': 'TEST_DOUBLE', 'version': 'test', 'model': 'NO_MODEL_INVOKED'},
            'started_at': '2026-10-21T10:00:00Z',
            'ended_at': '2026-10-21T10:01:00Z',
            'outcome': 'COMPLETED',
            'candidate_sha256': sha256(candidate.read_bytes()).hexdigest(),
            'transcript_ref': {'path': 'evidence/transcript.txt', 'sha256': sha256(transcript.read_bytes()).hexdigest()},
        }
        record = write(root / 'evidence/observation.json', observation)
        report = load('implementation_report', True)
        report.update(execution_mode=ACTUAL, observed_run_ref={'path': 'evidence/observation.json', 'sha256': sha256(record.read_bytes()).hexdigest()})
        return report, observation, candidate, record, transcript

    def check(self, report, root, candidate):
        return implementation_core.report_findings(report, root=root, candidate_path=candidate)

    def test_legacy_offline_report_remains_offline_and_valid(self):
        report = load('implementation_report')
        self.assertEqual([], implementation_core.report_findings(report))
        self.assertEqual('LEGACY_V1_OFFLINE_COMPATIBILITY', provenance_summary(report)['schema_mode'])
        self.assertEqual(OFFLINE, provenance_summary(report)['execution_mode'])

    def test_legacy_report_cannot_be_relabeled_as_an_actual_attempt(self):
        report = load('implementation_report')
        report['live_agent_run'] = True
        self.assertTrue(any(x.startswith('LEGACY_OFFLINE_ONLY:') for x in implementation_core.report_findings(report)))

    def test_v2_offline_report_has_separate_origin_and_mode(self):
        report = load('implementation_report', True)
        self.assertEqual([], implementation_core.report_findings(report))
        self.assertEqual('SYNTHETIC_TEACHING_CASE', report['fixture_origin'])
        self.assertEqual(OFFLINE, report['execution_mode'])
        self.assertIsNone(report['observed_run_ref'])

    def test_bound_observation_contract_accepts_actual_client_mode(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            report, _, candidate, _, _ = self.observed_fixture(root)
            self.assertEqual([], self.check(report, root, candidate))
            self.assertEqual(ACTUAL, provenance_summary(report)['execution_mode'])

    def test_actual_claim_without_observation_fails_precisely(self):
        report = load('implementation_report', True)
        report['execution_mode'] = ACTUAL
        self.assertTrue(any(x.startswith('OBSERVED_RUN_REF_REQUIRED:') for x in implementation_core.report_findings(report)))

    def test_observation_digest_cannot_be_invented(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            report, _, candidate, _, _ = self.observed_fixture(root)
            report['observed_run_ref']['sha256'] = '0' * 64
            self.assertIn('OBSERVED_RUN_SHA_MISMATCH', self.check(report, root, candidate))

    def test_retained_transcript_changes_invalidate_binding(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            report, _, candidate, _, transcript = self.observed_fixture(root)
            transcript.write_text(transcript.read_text() + 'Changed after observation.\n')
            self.assertIn('OBSERVED_TRANSCRIPT_SHA_MISMATCH', self.check(report, root, candidate))

    def test_observed_run_is_bound_to_the_exact_candidate(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            report, _, candidate, _, _ = self.observed_fixture(root)
            candidate.write_text(candidate.read_text() + '\n# Different candidate bytes\n')
            self.assertIn('OBSERVED_RUN_CANDIDATE_SHA_MISMATCH', self.check(report, root, candidate))

    def test_actual_mode_does_not_grant_architecture_acceptance(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            report, _, candidate, _, _ = self.observed_fixture(root)
            report['architecture_status'] = 'APPROVED'
            self.assertIn('architecture_status: wrong claim or provenance', self.check(report, root, candidate))

    def test_v2_cannot_keep_the_ambiguous_legacy_flag(self):
        report = load('implementation_report', True)
        report['live_agent_run'] = False
        self.assertTrue(any(x.startswith('V2_LEGACY_FLAG_NOT_ALLOWED:') for x in implementation_core.report_findings(report)))

    def test_observation_path_cannot_escape_root_or_use_a_symlink(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            report, _, candidate, record, _ = self.observed_fixture(root)
            original = report['observed_run_ref']['path']
            for path in ('../observation.json', '/tmp/observation.json'):
                report['observed_run_ref']['path'] = path
                self.assertTrue(any(x.startswith('OBSERVED_RUN_INVALID:') for x in self.check(report, root, candidate)))
            link = root / 'evidence/link.json'
            link.symlink_to(record)
            report['observed_run_ref']['path'] = 'evidence/link.json'
            self.assertTrue(any('symlinked evidence' in x for x in self.check(report, root, candidate)))
            report['observed_run_ref']['path'] = original

    def test_cumulative_receipt_includes_observation_and_transcript_bytes(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            report, _, candidate, _, transcript = self.observed_fixture(root)
            report_path = write(root / 'report.json', report)
            paths = {'implementation': candidate, 'implementation_report': report_path}
            with patch.object(integration_core, 'ROOT', root), patch.object(integration_core, 'SHARED_INPUTS', []):
                before = integration_core.receipt_inputs(paths)
                self.assertIn('evidence/observation.json', before)
                self.assertIn('evidence/transcript.txt', before)
                transcript.write_text('Changed transcript after previous review.\n')
                after = integration_core.receipt_inputs(paths)
            receipt = {'schema': 'integrated-lab-review/v2', 'status': 'PASS_REVIEW_GATE_ONLY',
                       'mode': 'WORKING_CANDIDATES', 'input_receipts': before}
            self.assertIn('STALE_RECEIPT:evidence/transcript.txt', integration_core.check_receipt(receipt, after, 'WORKING_CANDIDATES'))

    def test_cumulative_receipt_uses_relative_names_through_root_alias(self):
        with TemporaryDirectory() as directory:
            real = Path(directory).resolve() / 'companion'
            real.mkdir()
            root = real.parent / 'alias'
            root.symlink_to(real, target_is_directory=True)
            report, _, candidate, _, _ = self.observed_fixture(root)
            paths = {'implementation': candidate,
                     'implementation_report': write(root / 'report.json', report)}
            with patch.object(integration_core, 'ROOT', root), patch.object(integration_core, 'SHARED_INPUTS', []):
                receipts = integration_core.receipt_inputs(paths)
            self.assertEqual({'candidate.py', 'report.json', 'evidence/observation.json',
                              'evidence/transcript.txt'}, set(receipts))


class PendingReviewRegression(unittest.TestCase):
    def setUp(self):
        self.skill = (REF / 'context-audit.SKILL.md').read_text()

    def test_legacy_plus_truthful_spec_review_is_allowed(self):
        packet = load('context_packet')
        packet['human_review_required'].append('SPEC-004')
        self.assertEqual([], knowledge_core.assess(packet, self.skill))

    def test_v2_complete_pending_list_is_valid(self):
        self.assertEqual([], knowledge_core.assess(load('context_packet', True), self.skill))

    def test_v2_missing_spec_is_reported_as_the_missing_review(self):
        packet = load('context_packet', True)
        packet['pending_reviews'] = [x for x in packet['pending_reviews'] if x['review_id'] != 'SPEC-004']
        self.assertIn('PENDING_REVIEW_MISSING:SPEC-004', knowledge_core.assess(packet, self.skill))

    def test_mandatory_missing_architecture_is_precise(self):
        packet = load('context_packet')
        packet['human_review_required'] = ['SPEC-004', 'OPERATOR_COPY']
        self.assertIn('HUMAN_REVIEW_MISSING:ADR-005', knowledge_core.assess(packet, self.skill))

    def test_invented_approval_is_rejected(self):
        packet = load('context_packet', True)
        packet['pending_reviews'][-1].update(status='APPROVED', decision_ref='invented')
        self.assertIn('PENDING_REVIEW_UNSUPPORTED_APPROVAL:SPEC-004', knowledge_core.assess(packet, self.skill))

    def test_unknown_review_is_not_mislabeled_as_missing(self):
        packet = load('context_packet')
        packet['human_review_required'].append('INVENTED-99')
        findings = knowledge_core.assess(packet, self.skill)
        self.assertIn('HUMAN_REVIEW_UNKNOWN:INVENTED-99', findings)
        self.assertFalse(any(x.startswith('HUMAN_REVIEW_MISSING') for x in findings))

    def test_current_and_legacy_plans_both_validate_in_their_own_schema(self):
        for current in (False, True):
            with self.subTest(current=current):
                self.assertEqual([], planning_core.validate(load('delegation_plan', current), load('delegation_handoff', current)))

    def test_spec_review_must_reach_plan_and_handoff(self):
        plan, handoff = load('delegation_plan', True), load('delegation_handoff', True)
        self.assertEqual(current_pending_reviews(), plan['pending_reviews'])
        for label, field in [('PLAN', plan), ('HANDOFF', handoff)]:
            with self.subTest(label=label):
                original = copy.deepcopy(field['pending_reviews'])
                field['pending_reviews'] = [x for x in original if x['review_id'] != 'SPEC-004']
                self.assertIn(label + ':PENDING_REVIEW_MISSING:SPEC-004', planning_core.validate(plan, handoff))
                field['pending_reviews'] = original

    def test_spec_decision_must_be_bound_to_human_task(self):
        plan, handoff = load('delegation_plan', True), load('delegation_handoff', True)
        next(t for t in plan['tasks'] if t['id'] == 'T07-03')['decision_subjects'] = ['ADR-005']
        self.assertIn('PENDING_REVIEW_TASK_BINDING:T07-03', planning_core.validate(plan, handoff))

    def test_new_schema_does_not_relax_source_digest_pins(self):
        plan, handoff = load('delegation_plan', True), load('delegation_handoff', True)
        plan['source_receipts'][-1]['sha256'] = '0' * 64
        self.assertIn('SOURCE_SHA_MISMATCH:CTX-006', planning_core.validate(plan, handoff))


class SemanticReviewRegression(unittest.TestCase):
    def test_equivalent_handoff_gets_human_review_not_missing_reasoning(self):
        spec = load('specification')
        spec['handoff'] = ('The explanation-only alpha is ready solely for review by the requirements owner. '
                           'Implementation and production deployment remain unauthorized.')
        findings = specification_core.validate(spec)
        self.assertEqual(1, len(findings), findings)
        self.assertTrue(findings[0].startswith('HUMAN_SEMANTIC_REVIEW:specification.handoff'))
        self.assertNotIn('missing', findings[0].lower())

    def test_missing_handoff_remains_a_hard_failure(self):
        spec = load('specification')
        spec['handoff'] = ''
        self.assertIn('TEXT_MISSING:specification.handoff human requirements review', specification_core.validate(spec))

    def test_unauthorized_handoff_cannot_pass(self):
        spec = load('specification')
        spec['handoff'] = 'Approved production deployment'
        self.assertTrue(specification_core.validate(spec))
        spec['status'] = 'IMPLEMENTATION_APPROVED'
        self.assertIn('premature acceptance or wrong review status', specification_core.validate(spec))

    def test_cumulative_semantic_only_findings_are_classified_distinctly(self):
        spec = load('specification')
        spec['handoff'] = 'Only a requirements-owner appraisal is requested; implementation remains unauthorized.'
        with TemporaryDirectory() as directory:
            paths = integration_core.input_paths(reference=True)
            paths['specification'] = write(Path(directory) / 'spec.json', spec)
            with patch.object(integration_core, 'input_paths', return_value=paths):
                result = integration_core.review_workflow(reference=True)
            self.assertEqual('HUMAN_SEMANTIC_REVIEW', result['status'], result['findings'])
            self.assertEqual('HUMAN_SEMANTIC_REVIEW', result['layers']['CP04_specification']['status'])

    def test_requirement_paraphrase_is_not_called_missing_semantics(self):
        spec = load('specification')
        spec['requirements'][1]['statement'] = 'The system MUST reserve transfer authorization to an accountable person and show that routing grants no such authority.'
        findings = specification_core.validate(spec)
        self.assertTrue(any(x.startswith('HUMAN_SEMANTIC_REVIEW:requirement REQ-EXPL-002') for x in findings))
        self.assertFalse(any('missing requirement semantic' in x for x in findings))

    def test_skill_paraphrase_is_not_called_missing_procedure(self):
        text = (REF / 'context-audit.SKILL.md').read_text().replace('human review', 'review by the accountable owner')
        findings = knowledge_core.lint_skill(text)
        self.assertTrue(any(x.startswith('HUMAN_SEMANTIC_REVIEW:skill.procedure') for x in findings), findings)
        self.assertFalse(any('PROCEDURE_MISSING' in x for x in findings))

    def test_exact_identifier_checks_still_fail(self):
        spec = load('specification')
        spec['spec_id'] = 'SPEC-004/v999'
        self.assertIn('wrong specification identity', specification_core.validate(spec))
        architecture = load('architecture_decision')
        architecture['specification_sha256'] = '0' * 64
        self.assertIn('stale or unsupported specification digest', architecture_core.check_design(architecture))


if __name__ == '__main__':
    unittest.main()
