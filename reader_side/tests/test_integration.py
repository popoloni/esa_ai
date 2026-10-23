"""Regression checks for the real CP01--CP09 merge and its review evidence.

Runtime source changes happen only in disposable companion copies. The tests
use protected good/bad controls, so repairing learner starters does not invalidate
the regression suite. Passing these tests is not a human acceptance decision.
"""
from contextlib import contextmanager
from hashlib import sha256
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'reader_side/tools'))
import integration_core
from scope_guard import capture_edit_scope, check_edit_scope


class IntegratedWorkflowTests(unittest.TestCase):
    @contextmanager
    def working_copy(self):
        with tempfile.TemporaryDirectory(prefix='treasury-integration-') as directory:
            target=Path(directory)/'companion'
            shutil.copytree(ROOT,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            yield target

    def run_review(self,root,*,reference=False,candidate=None,report=None,receipt=None,output=None):
        command=[sys.executable,str(root/'reader_side/tools/integration_gate.py')]
        if reference:
            command.append('--reference')
        for option,value in [('--candidate',candidate),('--report',report),
                             ('--receipt',receipt),('--output',output)]:
            if value is not None:
                command.extend([option,str(value)])
        environment=dict(os.environ)
        environment.pop('PYTHONPATH',None)
        environment['PYTHONDONTWRITEBYTECODE']='1'
        observed=subprocess.run(command,cwd=root,env=environment,
                                capture_output=True,text=True,timeout=60)
        self.assertIn(observed.returncode,(0,1),observed.stderr+observed.stdout)
        try:
            result=json.loads(observed.stdout)
        except ValueError:
            self.fail('Review subprocess did not return JSON: '+observed.stderr+observed.stdout)
        self.assertEqual(0 if result['status']=='PASS_REVIEW_GATE_ONLY' else 1,
                         observed.returncode,observed.stderr)
        return result

    def prepare_cp08_reference_candidates(self,root):
        paths={}
        for key in ('implementation','implementation_report'):
            candidate,reference=integration_core.INPUT_PAIRS[key]
            target=root/candidate
            shutil.copyfile(root/reference,target)
            paths[key]=target
        return paths['implementation'],paths['implementation_report']

    def capture_scope(self,root,chapter):
        baseline=root/'reader_side/evidence'/f'{chapter}_TEST_EDIT_BASELINE.json'
        baseline.parent.mkdir(parents=True,exist_ok=True)
        baseline.write_text(json.dumps(capture_edit_scope(chapter,root=root)),encoding='utf-8')
        return baseline

    def passing_candidate_receipt(self,root):
        candidate,report=self.prepare_cp08_reference_candidates(root)
        receipt=root/'reader_side/evidence/INTEGRATION_TEST_RECEIPT.json'
        observed=self.run_review(root,reference=True,candidate=candidate,report=report,output=receipt)
        self.assertEqual('PASS_REVIEW_GATE_ONLY',observed['status'],observed['findings'])
        return candidate,report,receipt

    def assert_stale_path(self,result,path):
        self.assertEqual('FAIL',result['status'])
        self.assertIn('STALE_RECEIPT:'+path,result['findings'])

    def test_reference_workflow_passes_all_connected_layers(self):
        result=integration_core.review_workflow(reference=True)
        self.assertEqual('PASS_REVIEW_GATE_ONLY',result['status'],result['findings'])
        expected={'CP03_discovery','CP04_specification','CP05_architecture',
                  'CP05_CP07_canonical_route','CP06_knowledge','CP07_planning','CP08_implementation',
                  'CP09_reviews_CP08','CP09_verification_exercise'}
        self.assertEqual(expected,set(result['layers']))
        self.assertTrue(all(layer['status']=='PASS' for layer in result['layers'].values()))
        self.assertFalse(result['authority']['release_authorized'])
        self.assertEqual('BLOCKED',result['authority']['CP07_T07_04'])

    def test_unchanged_passing_receipt_is_reusable_in_its_mode(self):
        receipt=integration_core.review_workflow(reference=True)
        self.assertEqual('PASS_REVIEW_GATE_ONLY',receipt['status'],receipt['findings'])
        result=integration_core.review_workflow(reference=True,receipt=receipt)
        self.assertEqual('PASS_REVIEW_GATE_ONLY',result['status'],result['findings'])
        self.assertEqual(receipt['input_receipts'],result['input_receipts'])

    def test_all_twelve_repaired_working_artifacts_form_a_passing_workflow(self):
        with self.working_copy() as root:
            self.assertEqual(12,len(integration_core.INPUT_PAIRS))
            for candidate,reference in integration_core.INPUT_PAIRS.values():
                target=root/candidate
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(root/reference,target)
            result=self.run_review(root)
            self.assertEqual('PASS_REVIEW_GATE_ONLY',result['status'],result['findings'])
            self.assertEqual('WORKING_CANDIDATES',result['mode'])
            self.assertIn('repo/src/treasury/explanation_alpha.py',result['input_receipts'])
            self.assertEqual('PASS',result['layers']['CP09_reviews_CP08']['status'])

    def test_independent_cp09_review_rejects_cp08_label_only_mutation(self):
        with self.working_copy() as root:
            candidate,report=self.prepare_cp08_reference_candidates(root)
            code=candidate.read_text()
            original="'status_label': _LABELS[decision['route']]"
            self.assertEqual(1,code.count(original))
            candidate.write_text(code.replace(original,"'status_label': 'APPROVED'"))
            result=self.run_review(root,reference=True,candidate=candidate,report=report)
            self.assertEqual('FAIL',result['status'])
            review=result['layers']['CP09_reviews_CP08']
            self.assertEqual('FAIL',review['status'])
            self.assertTrue(any(x.startswith('presentation_label:') for x in review['findings']))
            # Underlying routing fields still pass; presentation has its own oracle.
            self.assertEqual([],review['independent_cases']['failures'])

    def test_receipt_invalidates_after_producer_byte_change(self):
        with self.working_copy() as root:
            candidate,report,receipt=self.passing_candidate_receipt(root)
            candidate.write_text(candidate.read_text()+'\n# Source revision after the previous review.\n')
            result=self.run_review(root,reference=True,candidate=candidate,report=report,receipt=receipt)
            self.assert_stale_path(result,'repo/src/treasury/explanation_alpha.py')

    def test_receipt_invalidates_after_report_byte_change(self):
        with self.working_copy() as root:
            candidate,report,receipt=self.passing_candidate_receipt(root)
            report.write_text(report.read_text()+'\n')
            result=self.run_review(root,reference=True,candidate=candidate,report=report,receipt=receipt)
            self.assert_stale_path(result,'repo/engineering/implementation/implementation_report.json')

    def test_receipt_invalidates_after_upstream_router_byte_change(self):
        with self.working_copy() as root:
            candidate,report,receipt=self.passing_candidate_receipt(root)
            router=root/'repo/src/treasury/routing.py'
            router.write_text(router.read_text()+'\n# Upstream source revision.\n')
            result=self.run_review(root,reference=True,candidate=candidate,report=report,receipt=receipt)
            self.assert_stale_path(result,'repo/src/treasury/routing.py')

    def test_receipt_rejects_wrong_or_missing_mode(self):
        original=integration_core.review_workflow(reference=True)
        self.assertEqual('PASS_REVIEW_GATE_ONLY',original['status'],original['findings'])
        for mode in ('WORKING_CANDIDATES',None):
            with self.subTest(mode=mode):
                receipt=copy.deepcopy(original)
                if mode is None:
                    receipt.pop('mode')
                else:
                    receipt['mode']=mode
                result=integration_core.review_workflow(reference=True,receipt=receipt)
                self.assertEqual('FAIL',result['status'])
                self.assertIn('RECEIPT_MODE_MISMATCH',result['findings'])

    def test_receipt_cannot_omit_a_previously_reviewed_input(self):
        receipt=integration_core.review_workflow(reference=True)
        self.assertEqual('PASS_REVIEW_GATE_ONLY',receipt['status'],receipt['findings'])
        path='reader_side/reference_solution/v2/implementation_report.json'
        receipt['input_receipts'].pop(path)
        result=integration_core.review_workflow(reference=True,receipt=receipt)
        self.assert_stale_path(result,path)

    def test_cp08_scope_accepts_both_candidate_files(self):
        with self.working_copy() as root:
            baseline=self.capture_scope(root,'CP08')
            for path in ['repo/src/treasury/explanation_alpha.py',
                         'repo/engineering/implementation/implementation_report.json']:
                target=root/path
                target.write_text(target.read_text()+'\n')
            self.assertEqual([],check_edit_scope(baseline,root=root,chapter='CP08'))

    def test_cp08_scope_rejects_router_edit(self):
        with self.working_copy() as root:
            baseline=self.capture_scope(root,'CP08')
            target=root/'repo/src/treasury/routing.py'
            target.write_text(target.read_text()+'\n')
            self.assertIn('OUT_OF_SCOPE:src/treasury/routing.py',
                          check_edit_scope(baseline,root=root,chapter='CP08'))

    def test_cp08_scope_rejects_cp07_planning_edit(self):
        with self.working_copy() as root:
            baseline=self.capture_scope(root,'CP08')
            target=root/'repo/engineering/planning/delegation_plan.json'
            target.write_text(target.read_text()+'\n')
            self.assertIn('OUT_OF_SCOPE:engineering/planning/delegation_plan.json',
                          check_edit_scope(baseline,root=root,chapter='CP08'))

    def test_cp09_scope_rejects_cp08_producer_edit(self):
        with self.working_copy() as root:
            baseline=self.capture_scope(root,'CP09')
            target=root/'repo/src/treasury/explanation_alpha.py'
            target.write_text(target.read_text()+'\n')
            self.assertIn('OUT_OF_SCOPE:src/treasury/explanation_alpha.py',
                          check_edit_scope(baseline,root=root,chapter='CP09'))

    def test_new_chapter_baseline_retains_legitimate_prior_work(self):
        with self.working_copy() as root:
            # Complete a prior chapter before capturing the next exercise's baseline.
            for key in ('plan','planning_handoff'):
                candidate,reference=integration_core.INPUT_PAIRS[key]
                target=root/candidate
                shutil.copyfile(root/reference,target)
                # Keep a real prior-step byte revision even after learner repairs.
                target.write_text(target.read_text()+'\n')
            baseline=self.capture_scope(root,'CP08')
            record=json.loads(baseline.read_text())
            plan='engineering/planning/delegation_plan.json'
            self.assertEqual(sha256((root/'repo'/plan).read_bytes()).hexdigest(),
                             record['repo_files'][plan])
            self.prepare_cp08_reference_candidates(root)
            self.assertEqual([],check_edit_scope(baseline,root=root,chapter='CP08'))

    def test_protected_oracle_tamper_stops_candidate_execution(self):
        with self.working_copy() as root:
            candidate,report=self.prepare_cp08_reference_candidates(root)
            marker=root/'candidate_was_executed.txt'
            candidate.write_text(
                'from pathlib import Path\n'
                f'Path({str(marker)!r}).write_text("executed")\n'
                'def build_explanation(amount):\n    return {}\n'
            )
            oracle=root/'reader_side/specs/case_oracle.json'
            oracle.write_text(oracle.read_text()+'\n')
            result=self.run_review(root,reference=True,candidate=candidate,report=report)
            self.assertEqual('FAIL',result['status'])
            self.assertIn('protected_integrity:reader_side/specs/case_oracle.json',result['findings'])
            self.assertFalse(marker.exists(),'Candidate executed despite a protected-oracle failure')
            self.assertEqual({},result['layers'])

    def test_malformed_scope_baselines_fail_closed(self):
        with self.working_copy() as root:
            baseline=root/'reader_side/evidence/MALFORMED_TEST_BASELINE.json'
            baseline.parent.mkdir(parents=True,exist_ok=True)
            for content in ('{invalid','[]','{}','null'):
                with self.subTest(content=content):
                    baseline.write_text(content)
                    self.assertTrue(check_edit_scope(baseline,root=root,chapter='CP08'))

    def test_scope_baseline_cannot_be_reused_for_another_chapter(self):
        with self.working_copy() as root:
            baseline=self.capture_scope(root,'CP09')
            self.assertIn('EDIT_BASELINE_PROFILE_MISMATCH',
                          check_edit_scope(baseline,root=root,chapter='CP08'))

    def test_scope_baseline_is_bound_to_its_protected_release(self):
        with self.working_copy() as root:
            baseline=self.capture_scope(root,'CP08')
            manifest=root/'reader_side/protected_sha256.json'
            manifest.write_text(manifest.read_text()+'\n')
            self.assertIn('EDIT_BASELINE_RELEASE_MISMATCH',
                          check_edit_scope(baseline,root=root,chapter='CP08'))


if __name__=='__main__':
    unittest.main()
