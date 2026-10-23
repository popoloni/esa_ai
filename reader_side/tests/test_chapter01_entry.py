"""Regression checks for the Chapter 1 entry into the integrated companion.

Preparation and acceptance commands run in fresh processes. All candidate
mutations and preparation destinations are disposable temporary copies.
"""
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
ROUTER='repo/src/treasury/routing.py'
REFERENCE='reader_side/reference_solution/routing.py'
UNSAFE='reader_side/routing/unsafe_routing_fixture.py'


class ChapterOneEntryTests(unittest.TestCase):
    def inventory(self,root):
        return {
            path.relative_to(root).as_posix():sha256(path.read_bytes()).hexdigest()
            for path in root.rglob('*')
            if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc'
        }

    def copy_source(self,directory):
        source=Path(directory)/'source'
        shutil.copytree(ROOT,source,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        # Keep the assertion meaningful even after a learner edits the current router.
        shutil.copyfile(source/REFERENCE,source/ROUTER)
        return source

    def command(self,root,tool,*arguments):
        environment=dict(os.environ)
        environment.pop('PYTHONPATH',None)
        environment['PYTHONDONTWRITEBYTECODE']='1'
        return subprocess.run(
            [sys.executable,str(root/'reader_side/tools'/tool),*map(str,arguments)],
            cwd=root,env=environment,capture_output=True,text=True,timeout=60,
        )

    def json_result(self,observed,expected_exit):
        self.assertEqual(expected_exit,observed.returncode,observed.stderr+observed.stdout)
        try:
            return json.loads(observed.stdout)
        except ValueError:
            self.fail('Command did not return JSON: '+observed.stderr+observed.stdout)

    def test_preparation_changes_only_router_and_preserves_source_and_owner_inputs(self):
        original_before=self.inventory(ROOT)
        with tempfile.TemporaryDirectory(prefix='chapter01-prepare-') as directory:
            source=self.copy_source(directory)
            before=self.inventory(source)
            target=Path(directory)/'exercise'
            result=self.json_result(
                self.command(source,'prepare_chapter01.py','--destination',target),0)
            self.assertEqual('PASS',result['status'])
            prepared=self.inventory(target)
            self.assertEqual(set(before),set(prepared))
            changed={name for name in before if before[name]!=prepared[name]}
            self.assertEqual({ROUTER},changed)
            self.assertEqual(before[UNSAFE],prepared[ROUTER])
            protected=json.loads((source/'reader_side/protected_sha256.json').read_text())
            for name in protected:
                self.assertEqual(before[name],prepared[name],name)
            self.assertEqual(before,self.inventory(source),'Preparation modified its source companion')
        self.assertEqual(original_before,self.inventory(ROOT),'Preparation touched the original release')

    def test_preparation_refuses_existing_destination_without_overwriting_it(self):
        with tempfile.TemporaryDirectory(prefix='chapter01-existing-') as directory:
            target=Path(directory)/'existing'
            target.mkdir()
            marker=target/'keep.txt'
            marker.write_text('Existing reader work must remain intact.\n')
            before=self.inventory(target)
            result=self.command(ROOT,'prepare_chapter01.py','--destination',target)
            self.assertEqual(2,result.returncode,result.stderr+result.stdout)
            self.assertEqual(before,self.inventory(target))

    def test_preparation_refuses_destinations_nested_inside_its_source(self):
        with tempfile.TemporaryDirectory(prefix='chapter01-nested-') as directory:
            source=self.copy_source(directory)
            before=self.inventory(source)
            for target in (source/'nested_copy',source/'repo/nested_copy'):
                with self.subTest(target=target.relative_to(source).as_posix()):
                    result=self.command(source,'prepare_chapter01.py','--destination',target)
                    self.assertEqual(2,result.returncode,result.stderr+result.stdout)
                    self.assertFalse(target.exists())
                    self.assertEqual(before,self.inventory(source))

    def test_real_red_baseline_then_canonical_repair_passes_seven_owner_cases(self):
        original_before=self.inventory(ROOT)
        with tempfile.TemporaryDirectory(prefix='chapter01-red-green-') as directory:
            target=Path(directory)/'exercise'
            self.json_result(self.command(ROOT,'prepare_chapter01.py','--destination',target),0)
            red_file=target/'reader_side/evidence/CP01_TEST_RED.json'
            red=self.json_result(self.command(target,'run_acceptance.py','--output',red_file),1)
            self.assertEqual('FAIL',red['status'])
            self.assertEqual('chapter01-routing-result/v1',red['schema'])
            self.assertEqual((7,3,2,2,0),tuple(red[k] for k in
                             ('tests_total','passed','failures','errors','skipped')))
            self.assertEqual(sha256((target/UNSAFE).read_bytes()).hexdigest(),red['candidate_sha256'])
            self.assertEqual(red,json.loads(red_file.read_text()))

            shutil.copyfile(target/REFERENCE,target/ROUTER)
            green_file=target/'reader_side/evidence/CP01_TEST_GREEN.json'
            green=self.json_result(self.command(target,'run_acceptance.py','--output',green_file),0)
            self.assertEqual('PASS',green['status'])
            self.assertEqual((7,7,0,0,0),tuple(green[k] for k in
                             ('tests_total','passed','failures','errors','skipped')))
            self.assertEqual(sha256((target/REFERENCE).read_bytes()).hexdigest(),green['candidate_sha256'])
            self.assertNotEqual(red['candidate_sha256'],green['candidate_sha256'])
            self.assertEqual(red['intent_sha256'],green['intent_sha256'])
            self.assertEqual(red['acceptance_sha256'],green['acceptance_sha256'])
            self.assertEqual(green,json.loads(green_file.read_text()))
        self.assertEqual(original_before,self.inventory(ROOT))


if __name__=='__main__':
    unittest.main()
