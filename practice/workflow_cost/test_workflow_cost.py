"""Accounting safety tests: counterexamples that would otherwise overstate evidence."""
import copy
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import tempfile
import shutil
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("workflow_cost", HERE / "workflow_cost.py")
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
T = datetime(2026, 10, 21, 12, tzinfo=timezone.utc)
REF = {"path": "test_only.txt", "sha256": "1" * 64}


def stamp(seconds):
    return (T + timedelta(seconds=seconds)).isoformat()


def account():
    a = w.new_account("test", "accounting controls", "unittest", "synthetic test", "SYNTHETIC_TEACHING_CASE")
    a["boundary"].update(start_utc=stamp(0), finish_utc=stamp(100))
    return a


def span(id="a", start=10, finish=30, phase="implementation", actor="writer", kind="AGENT", measure="WALL_INTERVAL", outcome="PASSED"):
    return {"id": id, "phase": phase, "actor": actor, "actor_kind": kind,
            "measure": measure, "start_utc": stamp(start), "finish_utc": stamp(finish),
            "outcome": outcome, "evidence": [REF]}


def decision(id="d1", kind="AUTOMATED", item="change-1", at=50, choice="ACCEPTED"):
    return {"id": id, "kind": kind, "item": item, "at_utc": stamp(at),
            "decision": choice, "reviewer": "reviewer", "candidate": REF,
            "evidence": REF, "human_attestation": "Synthetic declared human" if kind == "HUMAN" else None}


def money(id="m1", key="invoice/1", value="2.5", unit="USD", component="model"):
    return {"id": id, "kind": "MONEY", "component": component, "value": value,
            "unit": unit, "charge_key": key, "at_utc": stamp(80), "evidence": REF}


def complete(a):
    for category in w.PHASES:
        a["coverage"][category] = {"state": "NOT_PERFORMED", "reason": "Synthetic explicit absence", "evidence": [REF]}
    for component in w.MONEY_COMPONENTS:
        a["money_coverage"][component] = {"state": "NOT_APPLICABLE", "reason": "Synthetic explicit non-applicability", "evidence": [REF]}
    a["money_coverage"]["model"] = {"state": "COMPLETE", "reason": "Synthetic invoice complete", "evidence": [REF]}
    a["usage"] = [money()]
    return a


class AccountingControls(unittest.TestCase):
    def test_negative_duration_refused(self):
        a = account(); a["spans"] = [span(start=30, finish=10)]
        with self.assertRaisesRegex(w.AccountError, "Reversed"):
            w.summarize(a)

    def test_timezone_required(self):
        a = account(); a["boundary"]["start_utc"] = "2026-10-21T12:00:00"
        with self.assertRaisesRegex(w.AccountError, "timezone"):
            w.summarize(a)

    def test_overlap_is_not_added_to_elapsed(self):
        a = account(); a["spans"] = [span("a", 10, 40), span("b", 20, 50, actor="checker", kind="AUTOMATION")]
        r = w.summarize(a)
        self.assertEqual(60, r["sum_of_interval_seconds_not_elapsed"])
        self.assertEqual(40, r["observed_interval_union_seconds"])
        self.assertEqual(20, r["overlap_seconds_removed_from_elapsed_coverage"])
        self.assertEqual(100, r["workflow_elapsed_seconds"])

    def test_same_human_concurrent_entries_union_before_person_effort(self):
        a = account(); a["spans"] = [span("a", 10, 40, "human_review", "person1", "HUMAN", "DECLARED_ACTIVE_HUMAN_INTERVAL"), span("b", 20, 50, "human_review", "person1", "HUMAN", "DECLARED_ACTIVE_HUMAN_INTERVAL")]
        self.assertEqual(40, w.summarize(a)["declared_active_human_seconds_total"])

    def test_distinct_people_effort_is_summed_but_elapsed_is_unioned(self):
        a = account(); a["spans"] = [span("a", 10, 40, "human_review", "person1", "HUMAN", "DECLARED_ACTIVE_HUMAN_INTERVAL"), span("b", 10, 40, "human_review", "person2", "HUMAN", "DECLARED_ACTIVE_HUMAN_INTERVAL")]
        r = w.summarize(a)
        self.assertEqual(60, r["declared_active_human_seconds_total"])
        self.assertEqual(30, r["observed_interval_union_seconds"])

    def test_automated_pass_does_not_supply_human_denominator(self):
        a = complete(account()); a["acceptance"] = [decision()]
        r = w.summarize(a)
        self.assertEqual(1, r["acceptance"]["AUTOMATED"]["accepted_distinct_items"])
        self.assertIsNone(r["acceptance"]["HUMAN"]["accepted_distinct_items"])
        self.assertIsNone(r["cost_per_human_accepted_item"])

    def test_two_passes_of_same_item_count_once(self):
        a = account(); a["acceptance"] = [decision("d1", at=40), decision("d2", at=60)]
        self.assertEqual(1, w.summarize(a)["acceptance"]["AUTOMATED"]["accepted_distinct_items"])

    def test_later_rejection_revokes_earlier_count(self):
        a = account(); a["acceptance"] = [decision("d1", at=40), decision("d2", at=60, choice="REJECTED")]
        self.assertEqual(0, w.summarize(a)["acceptance"]["AUTOMATED"]["accepted_distinct_items"])

    def test_duplicate_charge_is_rejected(self):
        a = account(); a["usage"] = [money("m1"), money("m2")]
        with self.assertRaisesRegex(w.AccountError, "twice"):
            w.summarize(a)

    def test_unknown_money_not_replaced_with_zero(self):
        a = account(); a["usage"] = [money()]
        r = w.summarize(a)
        self.assertEqual({"USD": "2.5"}, r["observed_money_subtotals_by_currency"])
        self.assertIsNone(r["complete_workflow_money"])

    def test_assumed_rate_not_inserted_into_observed_money(self):
        a = account(); a["assumptions"] = [{"name": "hourly rate", "value": "100", "unit": "USD/hour", "basis": "Illustrative scenario only"}]
        self.assertEqual({}, w.summarize(a)["observed_money_subtotals_by_currency"])

    def test_zero_denominator_is_undefined(self):
        a = complete(account()); a["acceptance"] = [decision(kind="HUMAN", choice="REJECTED")]
        r = w.summarize(a)
        self.assertEqual("2.5", r["complete_workflow_money"])
        self.assertIsNone(r["cost_per_human_accepted_item"])

    def test_incomplete_phase_prevents_whole_workflow_total(self):
        a = complete(account()); a["coverage"]["preparation"] = {"state": "UNKNOWN", "reason": "No record", "evidence": []}
        self.assertIsNone(w.summarize(a)["complete_workflow_money"])

    def test_multiple_currencies_not_added(self):
        a = complete(account()); a["usage"].append(money("m2", "invoice/2", "3", "EUR"))
        r = w.summarize(a)
        self.assertEqual({"USD": "2.5", "EUR": "3"}, r["observed_money_subtotals_by_currency"])
        self.assertIsNone(r["complete_workflow_money"])

    def test_failed_attempt_retained_in_time_and_report(self):
        a = account(); a["spans"] = [span("failure", 10, 30, outcome="FAILED"), span("repair", 30, 50, "rework")]
        r = w.summarize(a)
        self.assertEqual(["failure"], r["failed_span_ids"])
        self.assertEqual(40, r["observed_interval_union_seconds"])

    def test_agent_cannot_be_human_review(self):
        a = account(); a["spans"] = [span(phase="human_review")]
        with self.assertRaisesRegex(w.AccountError, "cannot be human review"):
            w.summarize(a)

    def test_human_acceptance_needs_explicit_attribution(self):
        a = account(); d = decision(kind="HUMAN"); d["human_attestation"] = None; a["acceptance"] = [d]
        with self.assertRaisesRegex(w.AccountError, "explicit attribution"):
            w.summarize(a)

    def test_roi_claim_refused(self):
        a = account(); a["empirical_roi"] = 4
        with self.assertRaisesRegex(w.AccountError, "does not establish ROI"):
            w.summarize(a)

    def test_no_roi_even_when_cost_and_acceptance_complete(self):
        a = complete(account()); a["acceptance"] = [decision(kind="HUMAN")]
        a["spans"] = [span("review", 30, 40, "human_review", "reviewer", "HUMAN", "DECLARED_ACTIVE_HUMAN_INTERVAL")]
        a["coverage"]["human_review"] = {"state": "OBSERVED", "reason": "Synthetic interval", "evidence": [REF]}
        r = w.summarize(a)
        self.assertEqual("2.5", r["cost_per_human_accepted_item"])
        self.assertIsNone(r["roi"])

    def test_acceptance_and_declared_absence_of_human_review_conflict(self):
        a = complete(account()); a["acceptance"] = [decision(kind="HUMAN")]
        with self.assertRaisesRegex(w.AccountError, "absence of human review"):
            w.summarize(a)

    def test_acceptance_without_measured_human_effort_remains_partial(self):
        a = complete(account()); a["acceptance"] = [decision(kind="HUMAN")]
        a["coverage"]["human_review"] = {"state": "UNKNOWN", "reason": "Decision exists but review effort missing", "evidence": []}
        r = w.summarize(a)
        self.assertEqual(1, r["acceptance"]["HUMAN"]["accepted_distinct_items"])
        self.assertIsNone(r["cost_per_human_accepted_item"])

    def test_negative_nan_and_infinite_money_refused(self):
        for value in ("-1", "NaN", "Infinity"):
            with self.subTest(value=value):
                a = account(); a["usage"] = [money(value=value)]
                with self.assertRaises(w.AccountError):
                    w.summarize(a)

    def test_changed_source_is_not_silently_rebound(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "task.txt"; p.write_text("first")
            a = account(); s = span(); s["evidence"] = [w.fingerprint(p, Path(d) / "account.json")]; a["spans"] = [s]
            w.summarize(a, d)
            p.write_text("modified")
            with self.assertRaisesRegex(w.AccountError, "changed evidence"):
                w.summarize(a, d)

    def test_closed_account_open_span_refused(self):
        a = account(); s = span(); s["finish_utc"] = None; s["outcome"] = None; a["spans"] = [s]
        with self.assertRaisesRegex(w.AccountError, "open interval"):
            w.summarize(a)

    def test_cli_preserves_existing_account(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "account.json"; p.write_text("precious")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                result = w.main(["init", str(p), "--run-id", "t", "--purpose", "t", "--interface", "test", "--boundary", "test"])
            self.assertEqual(2, result)
            self.assertEqual("precious", p.read_text())

    def test_relative_evidence_survives_moving_complete_tree(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "first"; source.mkdir()
            evidence = source / "evidence.txt"; evidence.write_text("immutable")
            nested = source / "run"; nested.mkdir()
            a = account(); s = span(); s["evidence"] = [w.fingerprint(evidence, nested / "account.json")]; a["spans"] = [s]
            moved = Path(d) / "moved"; shutil.copytree(source, moved)
            shutil.rmtree(source)
            self.assertEqual(20, w.summarize(a, moved / "run")["observed_interval_union_seconds"])

    def test_missing_evidence_is_not_reported_as_verified(self):
        with tempfile.TemporaryDirectory() as d:
            a = account(); a["spans"] = [span()]
            with self.assertRaisesRegex(w.AccountError, "Missing or changed"):
                w.summarize(a, d)

    def test_report_cannot_overwrite_its_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "evidence.txt"; source.write_text("immutable")
            path = Path(d) / "account.json"
            a = account(); s = span(); s["evidence"] = [w.fingerprint(source, path)]; a["spans"] = [s]
            path.write_text(json.dumps(a))
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                result = w.main(["report", str(path), "--output", str(source)])
            self.assertEqual(2, result)
            self.assertEqual("immutable", source.read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
