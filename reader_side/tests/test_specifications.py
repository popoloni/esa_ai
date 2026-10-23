"""CP04: portable spec + protected toy oracle. All cases fictional; no AI client executed."""
from pathlib import Path
import copy,hashlib,json,shutil,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from specification_core import SIDE,ROOT,ROUTING,REFERENCE,load_json,validate,input_integrity,export_projections,projection,MANDATORY_REQ
REF=load_json(REFERENCE)

class SpecCaseTests(unittest.TestCase):
    def candidate(self):return copy.deepcopy(REF)
    def check(self,s,needle):
        msgs=validate(s);self.assertTrue(any(needle in x for x in msgs),msgs)
    def test_01_reference_pass(self):self.assertEqual([],validate(REF))
    def test_02_unsafe_candidate_rejected_independent_of_editable_starter(self):
        # A reader can repair the editable starter without breaking the persistent regression suite.
        bad=self.candidate()
        bad.update({'status':'IMPLEMENTATION_APPROVED','selected_option':'auto_approve',
                    'policy_authority':'SRC-TKT-017','decision_owner':'AI Agent',
                    'capability':'AUTOMATIC_PAYMENT_APPROVAL','value_status':'ROI_PROVEN_35_PERCENT'})
        bad['scope_out']=['deploy_to_production']
        bad['scenarios'][0]['payment_authorized']=True
        self.assertGreaterEqual(len(validate(bad)),7)
    def test_03_premature_implementation_approval(self):
        s=self.candidate();s['status']='IMPLEMENTATION_APPROVED';self.check(s,'premature')
    def test_04_invented_discovery_identifier(self):
        s=self.candidate();s['discovery_id']='DISC-007';self.check(s,'discovery decision trace')
    def test_05_unauthorised_discovery_verdict(self):
        s=self.candidate();s['discovery_verdict']='GO_DEPLOY';self.check(s,'discovery decision trace')
    def test_06_wrong_solution_autoapprove(self):
        s=self.candidate();s['selected_option']='auto_approve';self.check(s,'unauthorized capability')
    def test_07_wrong_capability(self):
        s=self.candidate();s['capability']='PROCESS_PAYMENT';self.check(s,'unauthorized capability')
    def test_08_policy_source_sponsor_is_wrong(self):
        s=self.candidate();s['policy_authority']='SRC-TKT-017';self.check(s,'incorrect policy authority')
    def test_09_policy_version_changes(self):
        s=self.candidate();s['policy_version']='BR-001/v2';self.check(s,'incorrect policy authority')
    def test_10_ai_is_not_business_decision_owner(self):
        s=self.candidate();s['decision_owner']='AI Agent';self.check(s,'missing human decision owner')
    def test_11_policy_owner_missing(self):
        s=self.candidate();s['policy_owner']='';self.check(s,'missing human decision owner')
    def test_12_prohibited_change_omitted(self):
        s=self.candidate();s['scope_out'].remove('alter_history');self.check(s,'scope_out')
    def test_13_payment_approval_becomes_scope(self):
        s=self.candidate();s['scope_in'].append('auto_payment_approval');self.check(s,'scope_in')
    def test_14_deploy_in_scope_false(self):
        s=self.candidate();s['scope_out'].remove('deploy_to_production');self.check(s,'scope_out')
    def test_15_value_claim_unsupported(self):
        s=self.candidate();s['value_status']='ROI_PROVEN';self.check(s,'unsupported business value')
    def test_16_stale_wiki_promoted_to_policy(self):
        s=self.candidate();s['source_ids'].append('SRC-WIKI-OLD');self.check(s,'source provenance')
    def test_17_missing_policy_source_in_source_ids(self):
        s=self.candidate();s['source_ids'].remove('SRC-POL-001');self.check(s,'source provenance')
    def test_18_missing_requirement(self):
        s=self.candidate();s['requirements'].pop();self.check(s,'missing or duplicate requirement')
    def test_19_duplicate_requirement_id(self):
        s=self.candidate();s['requirements'][0]['id']=s['requirements'][1]['id'];self.check(s,'missing or duplicate requirement')
    def test_20_unapproved_requirement_owner(self):
        s=self.candidate();s['requirements'][1]['owner']='AI Agent';self.check(s,'incorrect requirement owner')
    def test_21_requirement_sources_modified(self):
        s=self.candidate();s['requirements'][0]['source_ids'].remove('SRC-POL-001');self.check(s,'source provenance inconsistent')
    def test_22_false_rule_autoapprove(self):
        s=self.candidate();s['requirements'][1]['statement']='The system MUST auto-approve all requests under EUR 5,000.';self.check(s,'unauthorized payment behavior')
    def test_23_missing_normative_keyword(self):
        s=self.candidate();s['requirements'][2]['statement']='Reject invalid amounts.';self.check(s,'missing normative requirement')
    def test_24_missing_human_boundary_semantics(self):
        s=self.candidate();s['requirements'][1]['statement']='The system MUST display a generic message while routing requests without user interaction.';self.check(s,'HUMAN_SEMANTIC_REVIEW:requirement')
    def test_25_missing_scenario(self):
        s=self.candidate();s['scenarios'].pop();self.check(s,'scenario coverage')
    def test_26_scenario_duplicate_id(self):
        s=self.candidate();s['scenarios'][0]['id']=s['scenarios'][1]['id'];self.check(s,'scenario coverage')
    def test_27_exact_threshold_no_autoapproval(self):
        s=self.candidate();s['scenarios'][1]['expected_route']='STANDARD_QUEUE';self.check(s,'incorrect oracle case')
    def test_28_boundary_price_just_below_threshold(self):
        s=self.candidate();s['scenarios'][0]['expected_reason']='AT_OR_ABOVE_LIMIT';self.check(s,'incorrect oracle case')
    def test_29_wrong_version_in_one_scenario(self):
        s=self.candidate();s['scenarios'][0]['expected_policy_version']='BR-001/v2';self.check(s,'incorrect oracle case')
    def test_30_false_payment_authorization(self):
        s=self.candidate();s['scenarios'][0]['payment_authorized']=True;self.check(s,'incorrect oracle case')
    def test_31_invented_then(self):
        s=self.candidate();s['scenarios'][2]['then']='pay customer';self.check(s,'incomplete Given/When/Then')
    def test_32_no_human_in_given(self):
        s=self.candidate();s['scenarios'][2]['given']='policy routing only, no additional roles';self.check(s,'payment authority boundary')
    def test_33_trace_to_wrong_req(self):
        s=self.candidate();s['scenarios'][0]['requirement_id']='REQ-EXPL-005';self.check(s,'requirement trace mismatch')
    def test_34_fabricated_scenario(self):
        s=self.candidate();s['scenarios'][0]['id']='SC-EXPL-999';self.check(s,'scenario coverage')
    def test_35_questions_left_open(self):
        s=self.candidate();s['unresolved_questions']=[];self.check(s,'unknowns prematurely closed')
    def test_36_handoff_to_deploy_claim(self):
        s=self.candidate();s['handoff']='Approved production deployment';self.check(s,'human requirements review')
    def test_37_agent_policy_authority(self):
        s=self.candidate();s['authorized_delegation']='AI can approve all specs';self.check(s,'delegation boundary')
    def test_38_protected_inputs_current(self):self.assertEqual([],input_integrity())
    def test_39_protected_oracle_tamper_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            pp=Path(tmp)/'reader_side';shutil.copytree(SIDE,pp,ignore=shutil.ignore_patterns('__pycache__'))
            f=pp/'specs/case_oracle.json';f.write_text(f.read_text()+'  ',encoding='utf-8')
            self.assertIn('specs/case_oracle.json',input_integrity(pp))
    def test_40_protected_policy_symlink_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            pp=Path(tmp)/'reader_side';shutil.copytree(SIDE,pp,ignore=shutil.ignore_patterns('__pycache__'))
            f=pp/'discovery/sources/SRC-POL-001.json'; f.unlink()
            f.symlink_to(pp/'discovery/sources/SRC-TKT-017.json')
            self.assertIn('discovery/sources/SRC-POL-001.json',input_integrity(pp))
    def test_41_discovery_handoff_tamper_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            pp=Path(tmp)/'reader_side';shutil.copytree(SIDE,pp,ignore=shutil.ignore_patterns('__pycache__'))
            f=pp/'specs/discovery_handoff.json';f.write_text('{}',encoding='utf-8')
            self.assertIn('specs/discovery_handoff.json',input_integrity(pp))
    def test_42_routing_code_consistent_with_protected_cases(self):
        sys.path.insert(0,str(ROOT/'repo/src'))
        from treasury.routing import assess
        for s in REF['scenarios']:
            out=assess(s['input_amount_eur'])
            self.assertEqual((out.route,out.reason,out.policy_version),(s['expected_route'],s['expected_reason'],s['expected_policy_version']))
    def test_43_generated_projection_paths(self):
        with tempfile.TemporaryDirectory() as d:
            out=export_projections(REF,Path(d));self.assertEqual(4,len(out))
            for f in out.values(): self.assertTrue(f.stat().st_size>100)
    def test_44_openspec_draft_shape(self):
        doc=projection(REF,'openspec')
        self.assertIn('## ADDED Requirements',doc);self.assertEqual(5,doc.count('### Requirement:'));self.assertEqual(8,doc.count('#### Scenario:'))
    def test_45_kiro_ears_shape(self):
        doc=projection(REF,'kiro');self.assertEqual(8,doc.count('THE SYSTEM SHALL'))
    def test_46_gherkin_synthetic_not_executed(self):
        doc=projection(REF,'gherkin');self.assertIn('no Cucumber/Behave runner executed',doc);self.assertEqual(8,doc.count('  Scenario:'))
    def test_47_no_new_implementation_in_chapter_four(self):
        expected=(SIDE/'discovery/routing.sha256').read_text().strip()
        self.assertEqual(expected,hashlib.sha256(ROUTING.read_bytes()).hexdigest())

if __name__=='__main__':unittest.main()
