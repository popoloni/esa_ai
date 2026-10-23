"""Deterministic discovery review tests. All scenario sources and values are synthetic."""
import csv,copy,hashlib,json,shutil,tempfile,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from discovery_core import PACKET,ROUTING, collect_baseline, validate_decision, check_packet_integrity
ROOT=Path(__file__).resolve().parents[2]
REF=json.loads((ROOT/'reader_side/reference_solution/assessment.json').read_text(encoding='utf-8'))

class DiscoveryGateTests(unittest.TestCase):
    def candidate(self,**kwargs):
        base=copy.deepcopy(REF)
        base.update(kwargs)
        return base
    def assert_issue(self,decision,fragment):
        issues=validate_decision(decision)
        self.assertTrue(any(fragment in x for x in issues),issues)
    def test_reference_assessment_is_bounded_and_passes(self):
        self.assertEqual(validate_decision(REF),[])
    def test_known_unsafe_status_fails_without_freezing_editable_starter(self):
        # In contrast to the CLI demonstration, this unit test must keep passing
        # when a reader repairs the mutable repo/engineering/discovery/assessment.json.
        d=self.candidate(status='GO_DEPLOY')
        self.assertIn('not a bounded alpha decision',validate_decision(d))
    def test_baseline_counts_with_explicit_exclusions(self):
        self.assertEqual(collect_baseline(),{'total_cases':12,'measured_cases':10,'excluded_missing':2,
            'over_24h_cases':4,'over_24h_denominator':10,'median_hours':15.5})
    def test_proposed_auto_approval_rejected(self):
        self.assert_issue(self.candidate(selected_option='auto_approve'),'unrevised or incorrect engineering choice')
    def test_unapproved_request_is_not_policy_authority(self):
        self.assert_issue(self.candidate(policy_authority='SRC-TKT-017'),'non-authoritative policy')
    def test_correct_denominator_is_required(self):
        d=self.candidate();d['baseline']['over_24h_denominator']=12
        self.assert_issue(d,'incorrect baseline over_24h_denominator')
    def test_wrong_median_rejected(self):
        d=self.candidate();d['baseline']['median_hours']=16
        self.assert_issue(d,'incorrect baseline median_hours')
    def test_real_user_validation_cannot_be_claimed(self):
        self.assert_issue(self.candidate(research_status='REAL_USERS_VALIDATED'),'synthetic example misrepresented')
    def test_claimed_roi_without_field_evidence_rejected(self):
        self.assert_issue(self.candidate(value_claim='ROI_PROVEN_35_PERCENT'),'unsupported value claim')
    def test_stale_wiki_cannot_be_authoritative(self):
        self.assert_issue(self.candidate(policy_authority='SRC-WIKI-OLD'),'non-authoritative policy')
    def test_unknown_sources_rejected(self):
        d=self.candidate();d['source_ids'].append('SRC-FAKE-INVENTED')
        self.assert_issue(d,'unknown source identifiers')
    def test_missing_risk_source_rejected(self):
        d=self.candidate();d['source_ids'].remove('SRC-RISK-002')
        self.assert_issue(d,'incomplete source provenance')
    def test_unrecorded_conflict_rejected(self):
        self.assert_issue(self.candidate(contradictions=[]),'contradiction not recorded')
    def test_no_human_accountability_record_rejected(self):
        self.assert_issue(self.candidate(decision_owner='AI Agent'),'decision owner missing')
    def test_missing_open_questions_rejected(self):
        self.assert_issue(self.candidate(unknowns=['Only one question']),'open discovery questions omitted')
    def test_missing_experiment_stop_rule_rejected(self):
        d=self.candidate();d['experiment']['stop_rule']=''
        self.assert_issue(d,'incomplete pilot experiment: stop_rule')
    def test_missing_policy_guardrail_rejected(self):
        d=self.candidate();d['experiment']['guardrails']=['No payment approval']
        self.assert_issue(d,'HUMAN_SEMANTIC_REVIEW:discovery.guardrails')
    def test_raw_packet_currently_matches_hashes(self):
        self.assertEqual(check_packet_integrity(),[])
    def test_single_source_edit_detected_in_temporary_copy(self):
        with tempfile.TemporaryDirectory() as t:
            target=Path(t)/'packet';shutil.copytree(PACKET,target)
            f=target/'sources/SRC-POL-001.json'
            f.write_text(f.read_text()+'\nextra',encoding='utf-8')
            self.assertIn('sources/SRC-POL-001.json',check_packet_integrity(target))
    def test_duration_exactly_24_hours_is_not_over_24(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'cases.csv'
            with f.open('w',encoding='utf-8',newline='') as h:
                w=csv.DictWriter(h,fieldnames=['case_id','created_utc','routed_utc','service','notes']);w.writeheader()
                w.writerow({'case_id':'Z1','created_utc':'2026-09-01T00:00:00+00:00','routed_utc':'2026-09-02T00:00:00+00:00','service':'x','notes':'synth'})
            stats=collect_baseline(f)
            self.assertEqual(stats['over_24h_cases'],0)
            self.assertEqual(stats['median_hours'],24.0)
    def test_duplicate_cases_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'cases.csv'
            f.write_text('case_id,created_utc,routed_utc,service,notes\nA,2026-09-01T00:00:00+00:00,2026-09-02T02:00:00+00:00,x,a\nA,2026-09-01T00:00:00+00:00,2026-09-01T01:00:00+00:00,x,b\n')
            with self.assertRaisesRegex(ValueError,'duplicate'):collect_baseline(f)
    def test_negative_elapsed_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'cases.csv';f.write_text('case_id,created_utc,routed_utc,service,notes\nA,2026-09-02T00:00:00+00:00,2026-09-01T00:00:00+00:00,x,a\n')
            with self.assertRaisesRegex(ValueError,'invalid elapsed'):collect_baseline(f)
    def test_naive_timestamps_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'cases.csv';f.write_text('case_id,created_utc,routed_utc,service,notes\nA,2026-09-01T00:00:00,2026-09-02T00:00:00,x,a\n')
            with self.assertRaisesRegex(ValueError,'timezone'):collect_baseline(f)
    def test_existing_routing_policy_is_unchanged(self):
        expected=(PACKET/'routing.sha256').read_text().strip()
        self.assertEqual(hashlib.sha256(ROUTING.read_bytes()).hexdigest(),expected)
    def test_no_unapproved_source_autoapproval_exists(self):
        from treasury.routing import assess
        self.assertEqual(assess('4000').route,'STANDARD_QUEUE')
        self.assertNotIn('AUTO_APPROVED',assess('4000').route)

if __name__=='__main__':unittest.main()
