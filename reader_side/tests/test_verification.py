"""CP09 owner-authored checks: deliberate false-green and selected independent controls."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

SIDE=Path(__file__).resolve().parents[1]
ROOT=SIDE.parent
sys.path.insert(0,str(SIDE/'tools'))
sys.path.insert(0,str(SIDE/'verification'))
from verification_core import (
    REPO,REF,PROPOSAL,REVIEW,REFERENCE_REVIEW,ORACLE,expected_findings,
    selected_cases,check_known_candidate,seeded_mutation_probe,source_findings,
    owner_gate,check_review,load_known_author_fixture
)
from scope_guard import check_integrity,check_candidate_path
from circular_smoke import run as circular_smoke
UNSAFE=SIDE/'verification/unsafe_candidate_fixture.py'
UNSAFE_REVIEW=SIDE/'verification/unsafe_review_fixture.json'
from treasury.architecture import direct

class IndependentVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good=check_known_candidate(REF)
        cls.bad=check_known_candidate(UNSAFE)
        cls.mutations=seeded_mutation_probe()
        cls.ref_review=json.loads(REFERENCE_REVIEW.read_text())
        cls.cases=selected_cases()

    def changed_review(self):return copy.deepcopy(self.ref_review)
    def assert_review_flags(self,review,phrase):
        self.assertTrue(any(phrase in x for x in check_review(review,self.good,self.mutations)))

    def test_01_reference_matches_selected_cases(self):self.assertEqual(self.good.passed,8)
    def test_02_reference_has_no_findings(self):self.assertEqual(self.good.failures,[])
    def test_03_bad_candidate_is_not_accepted(self):self.assertLess(self.bad.passed,8)
    def test_04_bad_candidate_has_payment_violation(self):self.assertTrue(any('payment_authority' in x for x in self.bad.failures))
    def test_05_bad_candidate_has_threshold_violation(self):self.assertTrue(any('route:SC-EXPL-002' in x for x in self.bad.failures))
    def test_06_circular_self_check_passes_bad_candidate(self):
        f=load_known_author_fixture(UNSAFE)
        self.assertTrue(circular_smoke(f))
        self.assertGreater(len(self.bad.failures),0)
    def test_07_circular_self_check_passes_good_candidate(self):self.assertTrue(circular_smoke(load_known_author_fixture(REF)))
    def test_08_selected_cases_8(self):self.assertEqual(len(self.cases),8)
    def test_09_selected_cases_include_boundary(self):self.assertTrue(any(c['input_amount_eur']=='5000' for c in self.cases))
    def test_10_selected_cases_include_invalid(self):self.assertTrue(any(c['expected_route']=='REJECTED' for c in self.cases))
    def test_11_selected_cases_reject_money_movement(self):self.assertTrue(all(c['payment_authorized'] is False for c in self.cases))
    def test_12_mutation_probe_kills_3_of_3(self):
        self.assertEqual(self.mutations['manually_seeded_faults'],3)
        self.assertEqual(len(self.mutations['killed']),3)
    def test_13_no_surviving_selected_mutant(self):self.assertEqual(self.mutations['survived'],[])
    def test_14_without_boundary_case_mutant_survives(self):
        result=seeded_mutation_probe([c for c in self.cases if c['input_amount_eur']!='5000'])
        self.assertIn('boundary_off_by_one',result['survived'])
    def test_15_without_standard_cases_payment_mutant_survives(self):
        result=seeded_mutation_probe([c for c in self.cases if c['expected_route']!='STANDARD_QUEUE'])
        self.assertIn('grant_payment',result['survived'])
    def test_16_policy_version_fault_detected(self):
        a=direct.explain('1');a['policy_version']='BR-001/unknown'
        self.assertTrue(any('provenance' in z for z in expected_findings(a,self.cases[-1])))
    def test_17_payment_flag_fault_detected(self):
        a=direct.explain('1');a['payment_authorized']=True
        self.assertTrue(any('payment_authority' in z for z in expected_findings(a,self.cases[-1])))
    def test_18_missing_reason_field_detected(self):
        a=direct.explain('1');a.pop('reason_code')
        self.assertTrue(any('missing_field:reason_code' in z for z in expected_findings(a,self.cases[-1])))
    def test_19_false_roi_field_detected(self):
        a=direct.explain('1');a['benefit_status']='PROVEN_SAVED_90_PERCENT'
        self.assertTrue(any('benefit_claim' in z for z in expected_findings(a,self.cases[-1])))
    def test_20_correct_review_passes_structural_review(self):self.assertEqual([],check_review(self.ref_review,self.good,self.mutations))
    def test_21_wrong_digest_detected(self):
        r=self.changed_review();r['candidate_sha256']='0'*64;self.assert_review_flags(r,'candidate_digest_mismatch')
    def test_22_wrong_status_detected(self):
        r=self.changed_review();r['status']='RELEASE_APPROVED';self.assert_review_flags(r,'incorrect_status')
    def test_23_agent_cannot_claim_owner(self):
        r=self.changed_review();r['decision_owner']='agent';self.assert_review_flags(r,'incorrect_decision_owner')
    def test_24_release_flag_detected(self):
        r=self.changed_review();r['release_authorized']=True;self.assert_review_flags(r,'release_permission_claim')
    def test_25_removal_of_human_review_detected(self):
        r=self.changed_review();r['human_review_required']=False;self.assert_review_flags(r,'human_review_not_required')
    def test_26_claim_improves_without_evidence_detected(self):
        r=self.changed_review();r['claim']='EVERYTHING_SAFE';self.assert_review_flags(r,'incorrect_claim')
    def test_27_wrong_case_denominator_detected(self):
        r=self.changed_review();r['test_evidence']['case_count']=500;self.assert_review_flags(r,'evidence_mismatch:case_count')
    def test_28_wrong_fault_total_detected(self):
        r=self.changed_review();r['test_evidence']['injected_faults_total']=100;self.assert_review_flags(r,'evidence_mismatch:injected_faults_total')
    def test_29_unresolved_uncertainty_required(self):
        r=self.changed_review();r['remaining_uncertainty']=[];self.assert_review_flags(r,'missing_remaining_uncertainty')
    def test_30_wrong_contract_detected(self):
        r=self.changed_review();r['contract_id']='SPEC-999';self.assert_review_flags(r,'incorrect_contract_id')
    def test_31_unsafe_starter_gate_fails(self):self.assertEqual(owner_gate(UNSAFE,UNSAFE_REVIEW)['status'],'FAIL')
    def test_32_reference_gate_passes_review_not_release(self):
        x=owner_gate(REF,REFERENCE_REVIEW)
        self.assertEqual(x['status'],'PASS_REVIEW_GATE_ONLY')
        self.assertTrue(x['scope'].startswith('selected synthetic'))
    def test_33_source_simple_safe_candidate(self):self.assertEqual(source_findings(REF.read_text()),[])
    def test_34_ast_flags_subprocess(self):self.assertIn('suspicious_import:subprocess',source_findings('import subprocess\n'))
    def test_35_ast_flags_network(self):self.assertIn('suspicious_import:socket',source_findings('import socket\n'))
    def test_36_ast_flags_eval(self):self.assertIn('suspicious_builtin:eval',source_findings('def f():\n return eval("2+2")\n'))
    def test_37_ast_flags_syntax(self):self.assertIn('python_syntax_error',source_findings('def = 1'))
    def test_38_narrow_source_check_not_overclaim(self):
        self.assertEqual(source_findings('def f():\n return 5\n'),[])
        self.assertNotEqual(source_findings('import os\n'),[])
    def test_39_verification_candidate_path_allowed(self):self.assertTrue(check_candidate_path('engineering/verification/candidate.py').exists())
    def test_40_verification_review_path_allowed(self):self.assertTrue(check_candidate_path('engineering/verification/review.json').exists())
    def test_41_owner_oracle_path_not_allowed(self):
        with self.assertRaises(ValueError):check_candidate_path('../reader_side/specs/case_oracle.json')
    def test_42_protected_files_intact(self):self.assertEqual(check_integrity(),[])
    def test_43_independent_oracle_tamper_detected(self):
        with tempfile.TemporaryDirectory() as td:
            c=Path(td)/'copy'
            # copy hardlinked prohibited; real copy
            shutil.copytree(ROOT,c,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            target=c/'reader_side/specs/case_oracle.json'
            target.write_text(target.read_text()+' ',encoding='utf-8')
            self.assertIn('reader_side/specs/case_oracle.json',check_integrity(c))
    def test_44_false_green_test_edit_detected(self):
        with tempfile.TemporaryDirectory() as td:
            c=Path(td)/'copy'
            shutil.copytree(ROOT,c,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            target=c/'reader_side/verification/circular_smoke.py'
            target.write_text('return True\n')
            self.assertIn('reader_side/verification/circular_smoke.py',check_integrity(c))
    def test_45_reviewer_reference_hash_detected(self):
        self.assertEqual(self.good.digest,hashlib.sha256(REF.read_bytes()).hexdigest())
    def test_46_reference_evidence_denominators_are_disclosed(self):
        self.assertEqual(self.ref_review['test_evidence']['case_count'],8)
        self.assertEqual(self.ref_review['test_evidence']['injected_faults_total'],3)
    def test_47_original_route_threshold_preserved(self):
        self.assertEqual(direct.explain('5000')['route'],'HUMAN_REVIEW')
    def test_48_reference_has_no_payment_authority(self):
        for amt in ('0','1','4999.99','5000','9000','NaN'):
            self.assertIs(load_known_author_fixture(REF)(amt)['payment_authorized'],False)
    def test_49_reference_preserves_unvalidated_benefit(self):
        self.assertEqual(load_known_author_fixture(REF)('4000')['benefit_status'],'HYPOTHESIS_NOT_VALIDATED')
    def test_50_reviewer_claim_is_narrow(self):self.assertFalse(self.ref_review['release_authorized'])

class VerificationIntegrationInterface(unittest.TestCase):
    """Entry-point and failure-path checks for the integrated teaching gate."""

    def candidate_report(self,source,entry_point='propose_explanation'):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'known_fixture.py'
            path.write_text(source,encoding='utf-8')
            return check_known_candidate(path,entry_point=entry_point)

    def gate_with_review_text(self,text):
        with tempfile.TemporaryDirectory() as td:
            review_path=Path(td)/'review.json'
            review_path.write_text(text,encoding='utf-8')
            return owner_gate(REF,review_path,verify_integrity=False)

    def test_explicit_build_explanation_entry_point_uses_independent_oracle(self):
        source='from treasury.architecture.direct import explain\ndef build_explanation(amount_eur):\n    return explain(amount_eur)\n'
        report=self.candidate_report(source,entry_point='build_explanation')
        self.assertEqual((report.checked,report.passed,report.failures),(8,8,[]))

    def test_default_entry_point_does_not_silently_guess_build_explanation(self):
        report=self.candidate_report('def build_explanation(amount_eur):\n    return {}\n')
        self.assertEqual(report.passed,0)
        self.assertTrue(any(x.startswith('candidate_load_error:') for x in report.failures))

    def test_invalid_python_is_structured_failure(self):
        report=self.candidate_report('def = invalid\n')
        self.assertEqual(report.passed,0)
        self.assertTrue(report.failures)

    def test_missing_import_is_structured_failure(self):
        report=self.candidate_report('import deliberately_missing_cp09_module\ndef propose_explanation(value):\n    return {}\n')
        self.assertIn('candidate_load_error:ModuleNotFoundError',report.failures)

    def test_missing_candidate_is_structured_failure(self):
        with tempfile.TemporaryDirectory() as td:
            report=check_known_candidate(Path(td)/'absent.py')
        self.assertEqual(report.passed,0)
        self.assertIn('candidate_read_error:FileNotFoundError',report.failures)

    def test_non_callable_entry_is_structured_failure(self):
        report=self.candidate_report('propose_explanation = 7\n')
        self.assertEqual(report.passed,0)
        self.assertTrue(report.failures)

    def test_module_system_exit_does_not_terminate_reviewer(self):
        report=self.candidate_report('raise SystemExit(9)\n')
        self.assertIn('candidate_load_error:SystemExit',report.failures)

    def test_malformed_review_json_is_structured_fail(self):
        verdict=self.gate_with_review_text('{not JSON')
        self.assertEqual(verdict['status'],'FAIL')
        self.assertIn('review_input_error:JSONDecodeError',verdict['review_findings'])

    def test_review_array_is_structured_fail(self):
        verdict=self.gate_with_review_text('[]')
        self.assertEqual(verdict['status'],'FAIL')
        self.assertIn('review_must_be_object',verdict['review_findings'])

    def test_review_evidence_array_is_structured_fail(self):
        review=json.loads(REFERENCE_REVIEW.read_text())
        review['test_evidence']=[]
        verdict=self.gate_with_review_text(json.dumps(review))
        self.assertEqual(verdict['status'],'FAIL')
        self.assertIn('test_evidence_must_be_object',verdict['review_findings'])

    def test_malformed_uncertainty_items_are_structured_fail(self):
        review=json.loads(REFERENCE_REVIEW.read_text())
        review['remaining_uncertainty']=[{'unexpected':'object'}]
        verdict=self.gate_with_review_text(json.dumps(review))
        self.assertEqual(verdict['status'],'FAIL')
        self.assertIn('missing_remaining_uncertainty',verdict['review_findings'])


if __name__=='__main__':unittest.main()
