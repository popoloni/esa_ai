"""CP07 offline regression checks for proposed task/authority/handoff records.

These tests exercise an *owner-run* synthetic validator, not a product security boundary,
real multi-agent execution or proof of business authorization.
"""
import sys, unittest,copy,json,tempfile
from pathlib import Path
TOOLS=Path(__file__).resolve().parents[1]/'tools'
sys.path.insert(0,str(TOOLS))
from planning_core import read_json,validate,ready_levels,ROOT
REF=ROOT/'reader_side/reference_solution'

class DelegationPlanChecks(unittest.TestCase):
    def setUp(self):
        self.plan=read_json(REF/'delegation_plan.json')
        self.handoff=read_json(REF/'delegation_handoff.json')
    def errors(self):return validate(self.plan,self.handoff)
    def expect(self,prefix):
        problems=self.errors()
        self.assertTrue(any(x.startswith(prefix) for x in problems),problems)
    def task(self,id):return next(t for t in self.plan['tasks'] if t['id']==id)
    def test_safe_reference_passes(self):self.assertEqual(self.errors(),[])
    def test_intent_identity(self):self.plan['intent_id']='INT-002';self.expect('IDENTITY:intent_id')
    def test_spec_identity(self):self.plan['spec_id']='SPEC-004/v2';self.expect('IDENTITY:spec_id')
    def test_plan_identity(self):self.plan['plan_id']='PLAN-999';self.expect('IDENTITY:plan_id')
    def test_from_checkpoint(self):self.plan['from_checkpoint']='CP05';self.expect('IDENTITY:from_checkpoint')
    def test_threshold_rewrite_is_not_allowed(self):self.plan['authority']['routing_threshold_eur']=3000;self.expect('AUTHORITY:routing_threshold_eur')
    def test_payment_authority_is_not_inferred(self):self.plan['authority']['payment_approval_allowed']=True;self.expect('AUTHORITY:payment_approval_allowed')
    def test_architecture_proposal_not_accepted(self):self.plan['authority']['architecture_status']='ACCEPTED';self.expect('AUTHORITY:architecture_status')
    def test_release_not_authorized(self):self.plan['authority']['release_authorized']=True;self.expect('AUTHORITY:release_authorized')
    def test_ref_wrong_version(self):self.plan['authority']['architecture_decision']='ADR-006';self.expect('AUTHORITY:architecture_decision')
    def test_source_digest_tamper(self):self.plan['source_receipts'][0]['sha256']='0'*64;self.expect('SOURCE_SHA_MISMATCH')
    def test_source_path_tamper(self):self.plan['source_receipts'][1]['path']='reader_side/discovery/sources/SRC-WIKI-OLD.json';self.expect('SOURCE_MISSING_OR_PATH')
    def test_missing_source(self):self.plan['source_receipts'].pop();self.expect('SOURCE_MISSING_OR_PATH')
    def test_extra_source(self):self.plan['source_receipts'].append({'source_id':'WIKI','path':'reader_side/discovery/sources/SRC-WIKI-OLD.json','sha256':'123'});self.expect('SOURCE_COUNT_OR_EXTRA')
    def test_source_not_list(self):self.plan['source_receipts']='INT-001';self.expect('SOURCES_NOT_LIST')
    def test_unbounded_concurrency(self):self.plan['budgets']['max_concurrent_agents']=8;self.expect('BUDGET:max_concurrent_agents')
    def test_unbounded_invocations(self):self.plan['budgets']['max_model_invocations']=200;self.expect('BUDGET:max_model_invocations')
    def test_zero_elapsed_budget(self):self.plan['budgets']['max_elapsed_minutes']=0;self.expect('BUDGET:max_elapsed_minutes')
    def test_unbounded_retries(self):self.plan['budgets']['max_retries_per_task']=3;self.expect('BUDGET:max_retries_per_task')
    def test_boolean_confusion(self):self.plan['authority']['payment_approval_allowed']=0;self.expect('BOOLEAN_TYPE:payment_approval_allowed')
    def test_duplicate_tasks(self):self.plan['tasks'].append(copy.deepcopy(self.plan['tasks'][0]));self.expect('TASK_IDS_OR_DUPLICATES')
    def test_unknown_dependency(self):self.task('T07-05')['depends_on']=['MISSING'];self.expect('DANGLING_DEP')
    def test_cyclic_dependency(self):self.task('T07-01')['depends_on']=['T07-02'];self.task('T07-02')['depends_on']=['T07-01'];self.expect('TASK_GRAPH_CYCLE')
    def test_human_gate_removed(self):self.task('T07-04')['depends_on']=[];self.expect('DEPENDENCIES:T07-04')
    def test_human_decision_falsely_done(self):self.task('T07-03')['state']='DONE';self.expect('STATE:T07-03')
    def test_coding_agent_falsely_ready(self):self.task('T07-04')['state']='READY';self.expect('STATE:T07-04')
    def test_reviewer_falsely_done(self):self.task('T07-05')['state']='DONE';self.expect('STATE:T07-05')
    def test_agent_acts_as_owner(self):self.task('T07-03')['kind']='CODING_AGENT';self.expect('ROLE_KIND:T07-03')
    def test_readonly_agent_cannot_write(self):self.task('T07-01')['write_paths']=['src/treasury/architecture/direct.py'];self.expect('READ_ONLY_WRITES:T07-01')
    def test_reviewer_cannot_write(self):self.task('T07-05')['write_paths']=['engineering/architecture/architecture_decision.json'];self.expect('READ_ONLY_WRITES:T07-05')
    def test_coding_agent_cannot_edit_router(self):self.task('T07-04')['write_paths']=['src/treasury/routing.py'];self.expect('WRITER_SCOPE:T07-04')
    def test_coding_agent_cannot_edit_tests(self):self.task('T07-04')['write_paths']=['reader_side/acceptance/test_routing.py'];self.expect('PROTECTED_PATH:T07-04')
    def test_coding_agent_cannot_edit_adr(self):self.task('T07-04')['write_paths']=['engineering/architecture/ADR-005.md'];self.expect('PROTECTED_PATH:T07-04')
    def test_path_traversal(self):self.task('T07-04')['write_paths']=['../reader_side/specs/case_oracle.json'];self.expect('ESCAPED_WRITE_PATH:T07-04')
    def test_parallel_set_cannot_contain_writer(self):self.plan['parallel_read_only_task_ids']=['T07-01','T07-04'];self.expect('PARALLEL_SET_NOT_READ_ONLY')
    def test_makers_may_not_approve_own_work(self):self.plan['acceptance']['makers_may_approve_own_work']=True;self.expect('ACCEPTANCE:makers_may_approve_own_work')
    def test_oracle_edit_not_allowed(self):self.plan['acceptance']['maker_may_edit_reader_oracle']=True;self.expect('ACCEPTANCE:maker_may_edit_reader_oracle')
    def test_handoff_false_release(self):self.handoff['release_authorized']=True;self.expect('HANDOFF:release_authorized')
    def test_handoff_false_architecture_acceptance(self):self.handoff['architecture_status']='ACCEPTED';self.expect('HANDOFF:architecture_status')
    def test_handoff_fake_execution_evidence(self):self.handoff['agent_execution_evidence']=['success'];self.expect('HANDOFF_STATE:agent_execution_evidence')
    def test_handoff_falsely_ready_implementation(self):self.handoff['tasks_ready']=['T07-04'];self.expect('HANDOFF_STATE:tasks_ready')
    def test_handoff_must_record_sources(self):self.handoff['source_ids']=['SRC-WIKI-OLD'];self.expect('HANDOFF_SOURCES')
    def test_handoff_identity(self):self.handoff['plan_id']='PLAN-008';self.expect('HANDOFF:plan_id')
    def test_worktree_does_not_grant_permissions(self):self.plan['worktree_policy']['shared_state_review_required']=False;self.expect('WORKTREE_POLICY')
    def test_execution_mode_unbounded(self):self.plan['selection']['execution_mode']='UNBOUNDED_PARALLEL_WRITERS';self.expect('MODE_NOT_JUSTIFIED')
    def test_task_retries_must_be_bounded(self):self.task('T07-04')['max_attempts']=10;self.expect('TASK_RETRY_POLICY:T07-04')
    def test_single_worker_logical_rounds(self):self.assertEqual(ready_levels(self.plan,1),[['T07-01'],['T07-02']])
    def test_two_worker_logical_rounds(self):self.assertEqual(ready_levels(self.plan,2),[['T07-01','T07-02']])
    def test_parallelism_not_wallclock(self):self.assertEqual(len(ready_levels(self.plan,2)),1);self.assertNotIn('elapsed_seconds',self.plan)
    def test_bad_concurrency_setting(self):
        with self.assertRaises(ValueError):ready_levels(self.plan,0)

if __name__=='__main__':unittest.main()
