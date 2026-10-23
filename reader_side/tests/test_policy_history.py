"""Independent CP11 history invariants; no recursive shared-runner execution."""
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "reader_side/tools"))
import evolution_core as owner
from scope_guard import check_candidate_path


class PersistentHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="cp11-unit-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.module = owner.load_candidate(ROOT / owner.REFERENCE)
        self.catalog = owner.catalog()
        self.db = self.directory / "history.sqlite"
        self.store = self.module.PolicyStore(self.db, self.catalog)
        self.addCleanup(self.store.close)
        self.payload = {"amount_eur": "4000.00", "beneficiary_id": "vendor_17"}

    def reopen(self):
        self.store.close()
        self.store = self.module.PolicyStore(self.db, self.catalog)
        self.addCleanup(self.store.close)

    def error(self, code, function, *args):
        with self.assertRaises(self.module.HistoryError) as caught:
            function(*args)
        self.assertEqual(code, caught.exception.code)

    def seed(self, fixture="complete"):
        seeded = owner.seed_legacy(self.directory / fixture, fixture)
        return Path(seeded["database"]), owner.read_json(seeded["provenance"])

    def test_owner_boundaries_preserve_both_versions(self):
        for case in owner.read_json(ROOT / "reader_side/evolution/case_oracle.json")["cases"]:
            with self.subTest(case=case["id"]):
                result = self.store.decide(case["id"], {"amount_eur": case["amount"], "beneficiary_id": "boundary"}, case["policy"])
                out = result["record"]["decision"]
                self.assertEqual((case["route"], case["reason"], case["policy"]), (out["route"], out["reason_code"], out["policy_version"]))
                self.assertIs(False, out["payment_authorized"])

    def test_activation_survives_restart_without_changing_v1_api(self):
        self.store.activate("BR-001/v2")
        self.reopen()
        self.assertEqual("BR-001/v2", self.store.active_policy())
        self.assertEqual("STANDARD_QUEUE", self.module.assess("4000").route)
        self.assertEqual("HUMAN_REVIEW", self.store.decide("new", self.payload)["record"]["decision"]["route"])

    def test_stored_replay_survives_rollout_and_restart(self):
        original = self.store.decide("original", self.payload)["record"]
        self.store.activate("BR-001/v2")
        self.reopen()
        self.assertEqual(original, self.store.replay("original"))
        self.assertEqual("BR-001/v1", original["policy_version"])

    def test_historical_recomputation_uses_recorded_policy_without_new_rows(self):
        original = self.store.decide("original", self.payload)["record"]
        self.store.activate("BR-001/v2")
        self.reopen()
        before = owner.database_rows(self.db), owner.database_rows(self.db, "audit_events")
        result = self.store.recompute("original")
        self.assertEqual("MATCH", result["status"])
        self.assertEqual(original["decision"], result["recomputed"])
        self.assertEqual("BR-001/v1", result["recorded_policy"])
        self.assertEqual(before, (owner.database_rows(self.db), owner.database_rows(self.db, "audit_events")))

    def test_canonical_retry_retains_raw_original_payload(self):
        original = self.store.decide("original", {**self.payload, "amount_eur": "4000.0"})["record"]
        self.store.activate("BR-001/v2")
        self.reopen()
        retry = self.store.decide("original", self.payload)
        self.assertEqual("REPLAYED", retry["status"])
        self.assertEqual(original, retry["record"])
        self.assertEqual("4000.0", retry["record"]["payload"]["amount_eur"])
        self.assertEqual(1, len(owner.database_rows(self.db)))
        self.assertEqual(2, len(owner.database_rows(self.db, "audit_events")))

    def test_changed_payload_is_conflict_after_restart(self):
        self.store.decide("original", self.payload)
        self.reopen()
        for change in ({"amount_eur": "4001"}, {"beneficiary_id": "different"}):
            self.error("IDEMPOTENCY_CONFLICT", self.store.decide, "original", {**self.payload, **change})
        self.assertEqual(1, len(owner.database_rows(self.db)))

    def test_explicit_policy_change_on_retry_is_conflict(self):
        self.store.decide("original", self.payload)
        self.store.activate("BR-001/v2")
        self.error("IDEMPOTENCY_CONFLICT", self.store.decide, "original", self.payload, "BR-001/v2")
        self.assertEqual("REPLAYED", self.store.decide("original", self.payload, "BR-001/v1")["status"])

    def test_unknown_explicit_retry_policy_is_not_ignored(self):
        self.store.decide("original", self.payload)
        self.error("UNKNOWN_POLICY", self.store.decide, "original", self.payload, "BR-001/v999")

    def test_reevaluation_creates_a_distinct_linked_record(self):
        old = self.store.decide("old", self.payload)["record"]
        result = self.store.reevaluate("old", "new", "BR-001/v2")
        self.assertEqual("old", result["record"]["parent_key"])
        self.assertNotEqual(old["decision_id"], result["record"]["decision_id"])
        self.assertEqual("HUMAN_REVIEW", result["record"]["decision"]["route"])
        self.assertEqual(old, self.store.replay("old"))
        self.assertEqual(result["record"], self.store.reevaluate("old", "new", "BR-001/v2")["record"])

    def test_reevaluation_cannot_change_explicit_target_on_retry(self):
        self.store.decide("old", self.payload)
        self.store.reevaluate("old", "new", "BR-001/v1")
        self.error("IDEMPOTENCY_CONFLICT", self.store.reevaluate, "old", "new", "BR-001/v2")
        self.error("UNKNOWN_POLICY", self.store.reevaluate, "old", "new", "BR-001/v999")

    def test_parent_operation_is_part_of_identity(self):
        self.store.decide("old", self.payload)
        self.store.decide("other", self.payload)
        self.store.reevaluate("old", "new", "BR-001/v2")
        self.error("IDEMPOTENCY_CONFLICT", self.store.reevaluate, "other", "new", "BR-001/v2")
        self.error("IDEMPOTENCY_CONFLICT", self.store.decide, "new", self.payload)
        self.error("NEW_KEY_REQUIRED", self.store.reevaluate, "old", "old", "BR-001/v2")

    def test_invalid_new_input_creates_no_history(self):
        for amount in ["1.001", "1e3", "NaN", "Infinity", "", " 1.00", 3.0]:
            self.error("INVALID_AMOUNT_FORMAT", self.store.decide, "invalid", {**self.payload, "amount_eur": amount})
        self.error("INVALID_PAYLOAD", self.store.decide, "invalid", {**self.payload, "ignored": True})
        self.assertEqual([], owner.database_rows(self.db))
        self.assertEqual([], owner.database_rows(self.db, "audit_events"))

    def test_version_cannot_be_redefined_after_reopening(self):
        self.store.decide("old", self.payload)
        self.store.close()
        changed = json.loads(json.dumps(self.catalog))
        changed["BR-001/v2"]["threshold_eur"] = "2000.00"
        self.error("POLICY_CATALOG_CHANGED", self.module.PolicyStore, self.db, changed)
        changed["BR-001/v1"]["threshold_eur"] = "3000.00"
        self.error("V1_POLICY_CHANGED", self.module.PolicyStore, self.db, changed)

    def test_unknown_activation_is_atomic(self):
        before = owner.database_rows(self.db, "audit_events")
        self.error("UNKNOWN_POLICY", self.store.activate, "BR-001/v999")
        self.assertEqual("BR-001/v1", self.store.active_policy())
        self.assertEqual(before, owner.database_rows(self.db, "audit_events"))

    def test_decision_and_audit_failure_roll_back_together(self):
        self.store.conn.execute("""CREATE TRIGGER owner_failure BEFORE INSERT ON audit_events
          BEGIN SELECT RAISE(ABORT,'audit failure'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.decide("atomic", self.payload)
        self.assertEqual([], owner.database_rows(self.db))
        self.assertEqual([], owner.database_rows(self.db, "audit_events"))
        self.store.conn.execute("DROP TRIGGER owner_failure")
        self.assertEqual("CREATED", self.store.decide("atomic", self.payload)["status"])

    def test_two_connections_serialize_and_retry_after_real_lock_contention(self):
        second = self.module.PolicyStore(self.db, self.catalog)
        self.addCleanup(second.close)
        second.conn.execute("PRAGMA busy_timeout=0")
        self.store.conn.execute("BEGIN IMMEDIATE")
        try:
            with self.assertRaises(sqlite3.OperationalError):
                second.decide("contended", self.payload)
        finally:
            self.store.conn.rollback()
        self.assertEqual("CREATED", second.decide("contended", self.payload)["status"])
        self.assertEqual("REPLAYED", self.store.decide("contended", self.payload)["status"])
        self.error("IDEMPOTENCY_CONFLICT", self.store.decide, "contended", {**self.payload, "amount_eur": "4001"})
        self.assertEqual(1, len(owner.database_rows(self.db)))
        self.assertEqual(1, len(owner.database_rows(self.db, "audit_events")))

    def test_second_initializer_between_schema_reads_does_not_break_open(self):
        # Deterministically reproduce the independently reviewed read interleaving.
        module, policies, payload = self.module, self.catalog, self.payload
        database = self.directory / "interleaved_initialization.sqlite"
        original_connect = module._connect

        class DelayedCursor:
            def __init__(self, cursor):
                self.cursor = cursor

            def fetchone(self):
                result = self.cursor.fetchone()  # First opener observes version 0.
                module._connect = original_connect
                other = module.PolicyStore(database, policies)
                try:
                    other.decide("from_second_initializer", payload)
                finally:
                    other.close()  # A valid v2 database now exists before A's table read.
                return result

        class InterleavedConnection:
            def __init__(self, connection):
                self.connection, self.fired = connection, False

            def execute(self, sql, *args):
                result = self.connection.execute(sql, *args)
                if sql == "PRAGMA user_version" and not self.fired:
                    self.fired = True
                    return DelayedCursor(result)
                return result

            def __getattr__(self, name):
                return getattr(self.connection, name)

        module._connect = lambda path: InterleavedConnection(original_connect(path))
        try:
            first = module.PolicyStore(database, policies)
            self.addCleanup(first.close)
            self.assertEqual("BR-001/v1", first.active_policy())
            self.assertEqual("STANDARD_QUEUE", first.replay("from_second_initializer")["decision"]["route"])
            self.assertEqual(1, len(owner.database_rows(database)))
        finally:
            module._connect = original_connect

    def test_historical_tables_reject_update_and_delete(self):
        self.store.decide("old", self.payload)
        for statement in ("UPDATE decisions SET payload_json='{}'", "DELETE FROM decisions",
                          "UPDATE policy_versions SET policy_json='{}'", "DELETE FROM audit_events"):
            with self.assertRaises(sqlite3.IntegrityError):
                self.store.conn.execute(statement)
        self.assertEqual("STANDARD_QUEUE", self.store.replay("old")["decision"]["route"])

    def test_corrupted_payload_is_not_returned_as_verified_history(self):
        self.store.decide("old", self.payload)
        self.store.conn.execute("DROP TRIGGER immutable_decisions_update")
        self.store.conn.execute("UPDATE decisions SET payload_json=? WHERE request_key='old'",
                                (owner.canonical({**self.payload, "amount_eur": "4001"}),))
        self.error("HISTORY_INTEGRITY", self.store.replay, "old")

    def test_legacy_open_requires_explicit_migration(self):
        db, provenance = self.seed()
        before = owner.digest(db)
        self.error("EXPLICIT_MIGRATION_REQUIRED", self.module.PolicyStore, db, self.catalog)
        self.assertEqual(before, owner.digest(db))

    def test_complete_migration_preserves_old_bytes_and_recomputes_v1(self):
        db, provenance = self.seed()
        old = owner.database_rows(db, "legacy_decisions")
        result = self.module.migrate_legacy(db, self.catalog, provenance)
        self.assertEqual("MIGRATED", result["status"])
        self.assertEqual(old, owner.database_rows(db, "legacy_decisions"))
        store = self.module.PolicyStore(db, self.catalog)
        self.addCleanup(store.close)
        store.activate("BR-001/v2")
        record = store.replay("legacy_4000")
        for field in ("payload_json", "policy_json", "decision_json"):
            self.assertEqual(old[0][field], record[field])
        self.assertEqual("STANDARD_QUEUE", store.recompute("legacy_4000")["recomputed"]["route"])
        self.assertEqual("REPLAYED", store.decide("legacy_4000", self.payload)["status"])

    def test_ambiguous_migration_aborts_every_row_and_schema_change(self):
        db, provenance = self.seed("ambiguous")
        before = db.read_bytes()
        self.error("HISTORY_AMBIGUOUS", self.module.migrate_legacy, db, self.catalog, provenance)
        self.assertEqual(before, db.read_bytes())
        with sqlite3.connect(db) as conn:
            self.assertEqual(1, conn.execute("PRAGMA user_version").fetchone()[0])
            self.assertEqual([("legacy_decisions",)], conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())

    def test_inconsistent_legacy_outcome_is_not_rewritten(self):
        db, provenance = self.seed("wrong_outcome")
        before = db.read_bytes()
        self.error("LEGACY_OUTCOME_MISMATCH", self.module.migrate_legacy, db, self.catalog, provenance)
        self.assertEqual(before, db.read_bytes())

    def test_missing_and_changed_provenance_fail_without_writes(self):
        db, provenance = self.seed()
        before = db.read_bytes()
        for changes in ({"source_id": ""}, {"rows_sha256": "invented"}):
            self.error("LEGACY_PROVENANCE_MISMATCH", self.module.migrate_legacy, db, self.catalog, {**provenance, **changes})
        self.assertEqual(before, db.read_bytes())

    def test_owner_boundary_rejects_invented_but_self_consistent_source(self):
        seeded = owner.seed_legacy(self.directory / "forged")
        provenance = owner.read_json(seeded["provenance"])
        provenance["source_id"] = "INVENTED"
        owner.write_json(seeded["provenance"], provenance)
        before = owner.digest(seeded["database"])
        with self.assertRaisesRegex(ValueError, "LEGACY_PROVENANCE_NOT_OWNER_BOUND"):
            owner.checked_provenance(seeded["database"], seeded["provenance"])
        self.assertEqual(before, owner.digest(seeded["database"]))

    def test_failed_migration_does_not_silently_become_reinitialization(self):
        db, provenance = self.seed("ambiguous")
        self.error("HISTORY_AMBIGUOUS", self.module.migrate_legacy, db, self.catalog, provenance)
        self.error("EXPLICIT_MIGRATION_REQUIRED", self.module.PolicyStore, db, self.catalog)

    def test_schema_migration_is_not_repeated(self):
        db, provenance = self.seed()
        self.module.migrate_legacy(db, self.catalog, provenance)
        before = db.read_bytes()
        self.error("LEGACY_SCHEMA_REQUIRED", self.module.migrate_legacy, db, self.catalog, provenance)
        self.assertEqual(before, db.read_bytes())

    def test_cp11_scope_does_not_authorize_changing_v1_router(self):
        self.assertEqual(ROOT / owner.CANDIDATE, check_candidate_path("src/treasury/policy_history.py", chapter="CP11"))
        with self.assertRaises(PermissionError):
            check_candidate_path("src/treasury/routing.py", chapter="CP11")

    def test_delta_requires_explicit_boolean_false_authority(self):
        correct = owner.read_json(ROOT / owner.REFERENCE_DELTA)
        self.assertEqual([], owner.delta_findings(correct))
        correct["claims"]["real_release_authorized"] = 0
        self.assertIn("POLICY_DELTA:authority_claims", owner.delta_findings(correct))


if __name__ == "__main__":
    unittest.main()
