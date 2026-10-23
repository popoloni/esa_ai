"""Behavior and failure checks for the original deterministic teaching experiment."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import common
import run_experiment as experiment
import worker


class ExperimentIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="harness-engineering-test-")
        cls.output = common.create_output_directory(str(Path(cls.temporary.name) / "run"))
        cls.report = experiment.run(cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_composed_candidate_meets_independent_contract(self):
        self.assertEqual(self.report["scores"]["composed"]["development"]["full_contract_correct"], 4)
        self.assertEqual(self.report["scores"]["composed"]["held_out"]["full_contract_correct"], 8)
        self.assertEqual(self.report["process_executions"], 63)
        self.assertEqual(self.report["domain_tool_calls"], 27)
        self.assertEqual(self.report["model_calls"], 0)

    def test_overfitting_control_fails_transfer(self):
        score = self.report["scores"]["memorized_development"]
        self.assertEqual(score["development"]["full_contract_correct"], 4)
        self.assertEqual(score["held_out"]["full_contract_correct"], 4)
        precision = common.read_json(self.output / "probes/memorized_development/held_out/HOLD-02.json")
        self.assertEqual(precision["execution"]["response"]["route"], "HUMAN_REVIEW")

    def test_shape_and_semantic_correctness_remain_distinct(self):
        score = self.report["scores"]["tool_first"]["held_out"]
        self.assertEqual(score["route_correct"], 8)
        self.assertEqual(score["full_contract_correct"], 0)
        self.assertEqual(self.report["scores"]["schema_complete"]["held_out"]["full_contract_correct"], 4)

    def test_improver_receives_no_held_out_inputs_or_correctness_scores(self):
        inputs = common.read_json(self.output / "IMPROVER_INPUT.json")
        self.assertFalse(inputs["oracle_scores_available"])
        self.assertNotIn("held_out", inputs)
        text = json.dumps(inputs)
        self.assertNotIn("HOLD-", text)
        self.assertNotIn("full_contract_correct", text)
        self.assertNotIn("route_correct", text)
        adoption = common.read_json(self.output / "ADOPTION_RECEIPT.json")
        self.assertFalse(adoption["held_out_has_run"])
        self.assertEqual(adoption["improver_input_sha256"], common.digest(self.output / "IMPROVER_INPUT.json"))

    def test_context_and_runtime_identity_preserved(self):
        self.assertTrue(self.report["protection"]["all_selected_sources_runtime_and_oracle_unchanged"])
        self.assertEqual(self.report["protection"]["before"], self.report["protection"]["after"])
        manifest = common.read_json(self.output / "OUTPUT_SHA256.json")
        for rel, expected in manifest.items():
            self.assertEqual(common.digest(self.output / rel), expected, rel)

    def test_failed_proposals_and_stale_lessons_remain_visible(self):
        self.assertEqual(set(self.report["rejected_proposals"]), {"policy_rewrite", "budget_rewrite"})
        for name in self.report["rejected_proposals"]:
            item = common.read_json(self.output / "rejected_proposals" / (name + ".json"))
            self.assertEqual(item["status"], "REJECTED_BEFORE_EXECUTION")
        self.assertEqual(self.report["library_reuse"]["full_contract_correct"], 3)
        self.assertEqual(self.report["library_reuse"]["stale_source_control"], "REJECTED_STALE_REUSE")


class FailureContracts(unittest.TestCase):
    def test_unsafe_or_duplicate_case_ids_are_refused_before_artifact_writes(self):
        original = common.read_json(ROOT / "fixtures/tasks.json")
        for case_id in ["../escape", "/tmp/escape", "bad/id", original["held_out"][0]["case_id"]]:
            changed = copy.deepcopy(original)
            changed["development"][0]["case_id"] = case_id
            real_read_json = experiment.read_json
            def intercepted(path):
                return changed if path == ROOT / "fixtures/tasks.json" else real_read_json(path)
            with tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / "run"
                output.mkdir()
                with patch.object(experiment, "read_json", side_effect=intercepted):
                    with self.assertRaises(ValueError):
                        experiment.run(output)
                self.assertEqual(list(output.iterdir()), [])

    def test_raw_receipt_survives_malformed_and_mismatched_worker_results(self):
        for stdout in ["not JSON", json.dumps({"case_id": "WRONG", "config_sha256": "0" * 64})]:
            raw = {"returncode": 0, "stdout": stdout, "stderr": "kept diagnostic", "timed_out": False, "elapsed_seconds": 0.01}
            with tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / "run"
                output.mkdir()
                with patch.object(experiment, "execute_process", return_value=raw):
                    with self.assertRaises(ValueError):
                        experiment.run(output)
                receipt = common.read_json(output / "probes/base/development/DEV-01.json")
                self.assertEqual(receipt["raw_process"], raw)
                self.assertEqual(receipt["validation"], "REJECTED")
                self.assertIn("validation_error", receipt)

    def test_output_inside_protected_trees_is_refused_before_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            companion = Path(tmp) / "companion"
            practice = companion / "practice/harness_engineering"
            for name in ["repo", "reader_side", "practice/harness_engineering/fixtures", "practice/harness_engineering/tests"]:
                (companion / name).mkdir(parents=True, exist_ok=True)
            before = sorted(str(p.relative_to(companion)) for p in companion.rglob("*"))
            with patch.object(common, "COMPANION", companion), patch.object(common, "ROOT", practice):
                for forbidden in [companion / "repo/new/deep/run", companion / "reader_side/new/deep/run",
                                  practice / "fixtures/new/deep/run", practice / "tests/new/deep/run"]:
                    with self.assertRaisesRegex(ValueError, "protected"):
                        common.create_output_directory(str(forbidden))
            after = sorted(str(p.relative_to(companion)) for p in companion.rglob("*"))
            self.assertEqual(before, after)

    def test_output_reuse_and_symlink_escape_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            run = common.create_output_directory(str(base / "run"))
            sentinel = run / "keep.txt"
            sentinel.write_text("keep")
            with self.assertRaisesRegex(ValueError, "already exists"):
                common.create_output_directory(str(run))
            (base / "alias").symlink_to(run, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                common.create_output_directory(str(base / "alias/escape"))
            self.assertEqual(sentinel.read_text(), "keep")
            self.assertFalse((run / "escape").exists())

    def test_unknown_fields_and_payment_authority_are_refused(self):
        for name, value in [("command", ["sh", "-c", "anything"]), ("runtime_budget", 100), ("policy_threshold_eur", "3000")]:
            config = dict(experiment.base_harness(), **{name: value})
            with self.assertRaises(ValueError):
                common.validate_config(config)
        config = experiment.base_harness()
        config["routing_strategy"] = "memorized_development"
        config["development_memory"] = {"100": {"route": "STANDARD_QUEUE", "reason": "BELOW_LIMIT",
            "policy_version": "BR-001/v1", "payment_authorized": True}}
        with self.assertRaisesRegex(ValueError, "cannot authorize"):
            common.validate_config(config)

    def test_fixed_router_preserves_decimal_boundary_and_invalid_inputs(self):
        config = experiment.base_harness()
        config.update(routing_strategy="router_tool", response_fields=list(common.REQUIRED_FIELDS))
        router = common.COMPANION / "repo/src/treasury/routing.py"
        decimal = worker.execute(config, {"case_id": "precision", "amount_eur": "4999.9999999999999999999"}, router)
        invalid = worker.execute(config, {"case_id": "invalid", "amount_eur": "Infinity"}, router)
        self.assertEqual(decimal["response"]["route"], "STANDARD_QUEUE")
        self.assertEqual(invalid["response"]["route"], "REJECTED")
        self.assertEqual(worker.cached_estimate("4999.9999999999999999999")["route"], "HUMAN_REVIEW")

    def test_process_failure_and_timeout_are_observable(self):
        failed = experiment.execute_process([sys.executable, "-c", "import sys;sys.stderr.write('fixture failure');sys.exit(7)"], {}, 1)
        self.assertEqual(failed["returncode"], 7)
        self.assertIn("fixture failure", failed["stderr"])
        timed_out = experiment.execute_process([sys.executable, "-c", "import time;time.sleep(10)"], {}, 0.1)
        self.assertTrue(timed_out["timed_out"])
        self.assertIsNone(timed_out["returncode"])

    def test_changed_source_is_not_silently_rebaselined(self):
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp)
            pins = common.read_json(ROOT / "fixtures/SOURCE_PINS.json")
            for name in pins["companion_files"]:
                target = copied / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(common.COMPANION / name, target)
            (copied / "repo/src/treasury/routing.py").write_text("# changed source\n")
            with patch.object(common, "COMPANION", copied):
                with self.assertRaisesRegex(ValueError, "Source differs"):
                    common.require_source_pins()

    def test_composer_stops_when_evidence_does_not_support_components(self):
        config = experiment.base_harness()
        observed = {"base": [{"fresh_router_calls": 0, "required_fields_present": ["route"]}]}
        with self.assertRaisesRegex(ValueError, "No proposal demonstrated"):
            experiment.compose({"base": config}, observed)

    def test_library_reuse_requires_current_source_and_contract(self):
        entry = {"source_router_sha256": "a" * 64, "required_fields": list(common.REQUIRED_FIELDS),
                 "reusable_components": {"routing_strategy": "router_tool", "response_fields": list(common.REQUIRED_FIELDS), "development_memory": {}}}
        with self.assertRaisesRegex(ValueError, "STALE_LIBRARY_SOURCE"):
            experiment.suggest_from_library(experiment.base_harness(), entry, "b" * 64)
        changed = copy.deepcopy(entry)
        changed["required_fields"] = ["route"]
        with self.assertRaisesRegex(ValueError, "output contract"):
            experiment.suggest_from_library(experiment.base_harness(), changed, "a" * 64)


if __name__ == "__main__":
    unittest.main()

