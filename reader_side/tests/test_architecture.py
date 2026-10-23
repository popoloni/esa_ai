"""CP05 tests: common behavior, isolation seam, proposal quality, attack cases."""
from pathlib import Path
import copy,hashlib,json,sys,tempfile,shutil,unittest
S=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(S/'tools'))
from architecture_core import REF,SPEC,REPO,SIDE,ORACLE,load,check_design,check_adr,check_behavior
sys.path.insert(0,str(REPO/'src'))
from treasury.architecture import direct,ports
from treasury.routing import RoutingDecision

REFERENCE=load(REF)
ADR=(SIDE/'reference_solution/ADR-005.md').read_text(encoding='utf-8')
CASES=load(ORACLE)['cases']

class ArchitectureTests(unittest.TestCase):
    def altered(self):return copy.deepcopy(REFERENCE)
    def report(self,obj,needle):
        issues=check_design(obj)
        self.assertTrue(any(needle in i for i in issues),issues)

    def test_01_reference_decision_passes(self):self.assertEqual([],check_design(REFERENCE))
    def test_02_reference_adr_passes(self):self.assertEqual([],check_adr(ADR,REFERENCE))
    def test_03_all_prototypes_pass_cases(self):self.assertEqual([],check_behavior())
    def test_04_same_output_schema(self):
        for case in CASES:
            self.assertEqual(set(direct.explain(case['input_amount_eur'])),set(ports.explain(case['input_amount_eur'])))
    def test_05_exact_outputs_equal(self):
        for case in CASES:
            self.assertEqual(direct.explain(case['input_amount_eur']),ports.explain(case['input_amount_eur']))
    def test_06_no_payment_authority_on_valid(self):
        for amount in ('1','4999.99','5000','5000.01'):
            for mod in (direct,ports): self.assertIs(mod.explain(amount)['payment_authorized'],False)
    def test_07_no_payment_authority_on_invalid(self):
        for amount in ('0','-1','NaN','Infinity','abc','-Infinity'):
            for mod in (direct,ports): self.assertIs(mod.explain(amount)['payment_authorized'],False)
    def test_08_no_false_roi_on_any_case(self):
        for c in CASES:
            for mod in (direct,ports): self.assertEqual(mod.explain(c['input_amount_eur'])['benefit_status'],'HYPOTHESIS_NOT_VALIDATED')
    def test_09_valid_injected_fake_port(self):
        fake=lambda amount:RoutingDecision('HUMAN_REVIEW','AT_OR_ABOVE_LIMIT','BR-001/test-simulation')
        out=ports.ExplanationPresenter(ports.RoutingPort(fake)).explain('4')
        self.assertEqual(out['policy_version'],'BR-001/test-simulation')
        self.assertFalse(out['payment_authorized'])
    def test_10_invalid_injected_fake_is_rejected(self):
        fake=lambda amount:RoutingDecision('TRANSFER_FUNDS','PAY_NOW','BR-001/test')
        with self.assertRaises(ValueError): ports.ExplanationPresenter(ports.RoutingPort(fake)).explain('4')
    def test_11_direct_uses_real_router(self):self.assertEqual('STANDARD_QUEUE',direct.explain('4999.99')['route'])
    def test_12_ports_uses_real_router(self):self.assertEqual('HUMAN_REVIEW',ports.explain('5000')['route'])
    def test_13_negative_zero_is_rejected(self):
        for mod in (direct,ports):self.assertEqual(mod.explain('-0')['route'],'REJECTED')
    def test_14_very_large_amount_goes_human(self):
        for mod in (direct,ports):self.assertEqual(mod.explain('1e40')['route'],'HUMAN_REVIEW')
    def test_15_scientific_tiny_amount_standard(self):
        for mod in (direct,ports):self.assertEqual(mod.explain('1e-7')['route'],'STANDARD_QUEUE')
    def test_16_wrong_policy_version(self):
        x=self.altered();x['policy_version']='BR-001/v2';self.report(x,'unauthorized policy version')
    def test_17_stale_spec_digest(self):
        x=self.altered();x['specification_sha256']='0'*64;self.report(x,'specification digest')
    def test_18_decision_owner_is_ai(self):
        x=self.altered();x['decision_owner']='AI Agent';self.report(x,'human decision owner')
    def test_19_unauthorised_approval(self):
        x=self.altered();x['status']='RELEASE_APPROVED';self.report(x,'premature approval')
    def test_20_incorrect_discovery(self):
        x=self.altered();x['discovery_id']='DISC-404';self.report(x,'wrong trace')
    def test_21_incorrect_spec_version(self):
        x=self.altered();x['specification_id']='SPEC-999';self.report(x,'wrong trace')
    def test_22_design_not_in_alternatives(self):
        x=self.altered();x['selected_design']='microservices';self.report(x,'unknown selected')
    def test_23_only_one_option(self):
        x=self.altered();x['alternatives']=['direct'];self.report(x,'incomplete alternatives')
    def test_24_fabricated_latency_claim(self):
        x=self.altered();x['evidence']['performance']='99_PCT_FASTER';self.report(x,'unsupported evidence claim: performance')
    def test_25_fabricated_security_audit(self):
        x=self.altered();x['evidence']['security_audit']='PASSED';self.report(x,'unsupported evidence claim: security_audit')
    def test_26_fabricated_comprehension_study(self):
        x=self.altered();x['evidence']['human_comprehension']='PROVEN';self.report(x,'unsupported evidence claim: human_comprehension')
    def test_27_fabricated_release(self):
        x=self.altered();x['evidence']['implementation_release']='APPROVED';self.report(x,'unsupported evidence claim: implementation_release')
    def test_28_fabricated_case_evidence(self):
        x=self.altered();x['evidence']['direct_case_results']='PASS_1000_OF_1000';self.report(x,'unsubstantiated case evidence')
    def test_29_case_count_changed(self):
        x=self.altered();x['evidence']['shared_cases']=20;self.report(x,'unsubstantiated case evidence')
    def test_30_missing_payment_authority_driver(self):
        x=self.altered();x['decision_drivers'].remove('separate_payment_authority');self.report(x,'decision drivers')
    def test_31_missing_design_risk(self):
        x=self.altered();x['risks']['direct']=[];self.report(x,'alternative risks')
    def test_32_missing_ports_benefit(self):
        x=self.altered();x['strengths']['ports']=[];self.report(x,'alternative strengths')
    def test_33_missing_reconsideration(self):
        x=self.altered();x['revisit_when']=[];self.report(x,'reconsideration')
    def test_34_missing_open_questions(self):
        x=self.altered();x['unresolved_questions']=[];self.report(x,'open technical')
    def test_35_missing_rollback_path(self):
        x=self.altered();x['reversibility']='TBD';self.report(x,'reversibility')
    def test_36_wrong_handoff_deployed(self):
        x=self.altered();x['handoff']='Production deployed and accepted';self.report(x,'release handoff')
    def test_37_starter_unsafe_after_reader_fixes(self):
        x=self.altered(); x['status']='RELEASE_APPROVED';x['evidence']['performance']='90_PERCENT_FASTER';x['decision_owner']='AI Agent'
        self.assertGreaterEqual(len(check_design(x)),3)
    def test_38_wrong_adr_status_detected(self):
        self.assertTrue(any('status mismatch' in z for z in check_adr(ADR.replace('PROPOSED_FOR_HUMAN_ARCHITECTURE_REVIEW','RELEASE_APPROVED'),REFERENCE)))
    def test_39_adr_missing_context(self):
        self.assertTrue(any('missing ADR section' in z for z in check_adr(ADR.replace('## Context','## Omitted'),REFERENCE)))
    def test_40_adr_wrong_spec(self):
        self.assertTrue(any('contract/policy' in z for z in check_adr(ADR.replace('SPEC-004/v1','SPEC-999'),REFERENCE)))
    def test_41_adr_fabricated_performance(self):
        self.assertTrue(any('unsupported' in z for z in check_adr(ADR+'\n90% faster\n',REFERENCE)))
    def test_42_adr_missing_evidence_note(self):
        self.assertTrue(any('evidence qualifier' in z for z in check_adr(ADR.replace('NOT_MEASURED','UNKNOWN'),REFERENCE)))
    def test_43_spec_and_decision_digest_agree(self):
        self.assertEqual(REFERENCE['specification_sha256'],__import__('hashlib').sha256(SPEC.read_bytes()).hexdigest())
    def test_44_prototype_does_not_import_protected_oracle(self):
        for module in ('direct.py','ports.py'):
            source=(REPO/'src/treasury/architecture'/module).read_text(encoding='utf-8')
            self.assertNotIn('reader_side', source)
            self.assertNotIn('case_oracle.json', source)
    def test_45_same_policy_from_original(self):
        for mod in (direct,ports):
            for amount in ('2','5000'):
                self.assertEqual(mod.explain(amount)['policy_version'],'BR-001/v1')
    def test_46_reference_remains_proposal(self):
        self.assertNotIn('APPROVED',REFERENCE['status'])
    def test_47_architecture_code_is_in_repo_candidate_tree(self):
        self.assertTrue((REPO/'src/treasury/architecture/direct.py').is_file())
        self.assertTrue((REPO/'src/treasury/architecture/ports.py').is_file())
    def test_48_independent_oracle_has_eight_cases(self):
        self.assertEqual(len(CASES),8)
