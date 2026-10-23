"""Versioned synthetic routing history; never a payment or release authority.

This NEW persistence API accepts finite decimal strings with at most two decimal
places. The inherited treasury.routing.assess API and its input semantics stay
unchanged. Retry identity excludes the currently active policy.
"""
from contextlib import contextmanager
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3

from treasury.routing import assess

APPLICATION_ID = 1129337137
SCHEMA_VERSION = 2


class HistoryError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(text):
    return sha256(text.encode("utf-8")).hexdigest()


def canonical_payload(payload):
    if not isinstance(payload, dict) or set(payload) != {"amount_eur", "beneficiary_id"}:
        raise HistoryError("INVALID_PAYLOAD")
    amount, beneficiary = payload["amount_eur"], payload["beneficiary_id"]
    if not isinstance(amount, str) or not re.fullmatch(r"-?\d{1,12}(?:\.\d{1,2})?", amount):
        raise HistoryError("INVALID_AMOUNT_FORMAT")
    if not isinstance(beneficiary, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", beneficiary):
        raise HistoryError("INVALID_BENEFICIARY")
    normalized = format(Decimal(amount).quantize(Decimal("0.01")), ".2f")
    if Decimal(normalized) == 0:
        normalized = "0.00"
    return canonical({"amount_eur": normalized, "beneficiary_id": beneficiary})


def valid_key(key):
    if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", key):
        raise HistoryError("INVALID_KEY")


def checked_catalog(catalog):
    if not isinstance(catalog, dict) or not catalog:
        raise HistoryError("INVALID_CATALOG")
    result = {}
    for version, policy in catalog.items():
        if (not isinstance(policy, dict) or set(policy) != {"version", "threshold_eur", "algorithm"}
                or version != policy.get("version")
                or policy.get("algorithm") != "TREASURY_THRESHOLD_V1"
                or not isinstance(policy.get("threshold_eur"), str)
                or not re.fullmatch(r"\d+\.\d{2}", policy["threshold_eur"])
                or Decimal(policy["threshold_eur"]) <= 0):
            raise HistoryError("INVALID_CATALOG")
        result[version] = dict(policy)
    if result.get("BR-001/v1", {}).get("threshold_eur") != "5000.00":
        raise HistoryError("V1_POLICY_CHANGED")
    return result


def outcome(payload, policy):
    amount = Decimal(json.loads(canonical_payload(payload))["amount_eur"])
    if policy["version"] == "BR-001/v1":
        legacy = assess(payload["amount_eur"])
        route, reason = legacy.route, legacy.reason
    elif amount <= 0:
        route, reason = "REJECTED", "INVALID_AMOUNT"
    elif amount < Decimal(policy["threshold_eur"]):
        route, reason = "STANDARD_QUEUE", "BELOW_LIMIT"
    else:
        route, reason = "HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT"
    return {"route": route, "reason_code": reason, "policy_version": policy["version"],
            "payment_authorized": False, "notice": "ROUTING_ONLY_NOT_PAYMENT_APPROVAL",
            "benefit_status": "HYPOTHESIS_NOT_VALIDATED"}


def _connect(path):
    conn = sqlite3.connect(str(path), isolation_level=None, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


@contextmanager
def transaction(conn):
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield
        conn.commit()
    except BaseException:
        conn.rollback()
        raise


def _schema(conn):
    # execute(), not executescript(): DDL stays in the caller's transaction.
    statements = [
        "CREATE TABLE policy_versions(version TEXT PRIMARY KEY, policy_json TEXT NOT NULL, policy_sha256 TEXT NOT NULL)",
        "CREATE TABLE settings(name TEXT PRIMARY KEY, value TEXT NOT NULL)",
        """CREATE TABLE decisions(
          request_key TEXT PRIMARY KEY, payload_json TEXT NOT NULL,
          payload_sha256 TEXT NOT NULL, request_fingerprint TEXT NOT NULL,
          policy_version TEXT NOT NULL REFERENCES policy_versions(version),
          policy_json TEXT NOT NULL, policy_sha256 TEXT NOT NULL,
          decision_json TEXT NOT NULL, decision_sha256 TEXT NOT NULL,
          decision_id TEXT NOT NULL UNIQUE, parent_key TEXT REFERENCES decisions(request_key))""",
        """CREATE TABLE audit_events(
          event_id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL,
          request_key TEXT, evidence_json TEXT NOT NULL)""",
    ]
    for statement in statements:
        conn.execute(statement)
    for table in ("policy_versions", "decisions", "audit_events"):
        for action in ("UPDATE", "DELETE"):
            conn.execute(f"""CREATE TRIGGER immutable_{table}_{action.lower()}
              BEFORE {action} ON {table} BEGIN
              SELECT RAISE(ABORT, 'immutable_history'); END""")


def _install_catalog(conn, catalog):
    for version, policy in sorted(catalog.items()):
        raw = canonical(policy)
        conn.execute("INSERT INTO policy_versions VALUES(?,?,?)", (version, raw, digest(raw)))
    conn.execute("INSERT INTO settings VALUES('active_policy','BR-001/v1')")
    conn.execute(f"PRAGMA application_id={APPLICATION_ID}")
    conn.execute(f"PRAGMA user_version={SCHEMA_VERSION}")


def _record_identity(key, payload_hash, policy_hash, decision_hash, parent):
    return digest(canonical({"request_key": key, "payload_sha256": payload_hash,
                             "policy_sha256": policy_hash, "decision_sha256": decision_hash,
                             "parent_key": parent}))


def _insert(conn, key, payload_raw, policy_raw, decision_raw, parent=None):
    payload = json.loads(payload_raw)
    policy = json.loads(policy_raw)
    ph, sh, dh = digest(payload_raw), digest(policy_raw), digest(decision_raw)
    identity = _record_identity(key, ph, sh, dh, parent)
    conn.execute("INSERT INTO decisions VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                 (key, payload_raw, ph, digest(canonical_payload(payload)), policy["version"],
                  policy_raw, sh, decision_raw, dh, identity, parent))
    return identity


class PolicyStore:
    def __init__(self, path, catalog):
        self.path = Path(path)
        self.catalog = checked_catalog(catalog)
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = _connect(self.path)
        try:
            version = self.conn.execute("PRAGMA user_version").fetchone()[0]
            tables = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if version == 0:
                with transaction(self.conn):
                    # A second initializer may have waited for this write lock.
                    version = self.conn.execute("PRAGMA user_version").fetchone()[0]
                    tables = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                    if version == 0 and not tables:
                        _schema(self.conn)
                        _install_catalog(self.conn, self.catalog)
                        version = SCHEMA_VERSION
            if version == 1:
                raise HistoryError("EXPLICIT_MIGRATION_REQUIRED")
            if version != SCHEMA_VERSION:
                raise HistoryError("UNSUPPORTED_SCHEMA")
            if self.conn.execute("PRAGMA application_id").fetchone()[0] != APPLICATION_ID:
                raise HistoryError("WRONG_DATABASE")
            saved = {row["version"]: (row["policy_json"], row["policy_sha256"])
                     for row in self.conn.execute("SELECT * FROM policy_versions")}
            wanted = {version: (canonical(policy), digest(canonical(policy)))
                      for version, policy in self.catalog.items()}
            if saved != wanted:
                raise HistoryError("POLICY_CATALOG_CHANGED")
            self._policy(self.active_policy())
        except BaseException:
            self.conn.close()
            raise

    def close(self):
        self.conn.close()

    def active_policy(self):
        row = self.conn.execute("SELECT value FROM settings WHERE name='active_policy'").fetchone()
        if row is None:
            raise HistoryError("ACTIVE_POLICY_MISSING")
        return row[0]

    def _policy(self, version):
        if version not in self.catalog:
            raise HistoryError("UNKNOWN_POLICY")
        row = self.conn.execute("SELECT * FROM policy_versions WHERE version=?", (version,)).fetchone()
        if row is None or row["policy_json"] != canonical(self.catalog[version]) or row["policy_sha256"] != digest(row["policy_json"]):
            raise HistoryError("POLICY_CATALOG_CHANGED")
        return json.loads(row["policy_json"])

    def activate(self, version):
        with transaction(self.conn):
            self._policy(version)
            old = self.active_policy()
            if old != version:
                self.conn.execute("UPDATE settings SET value=? WHERE name='active_policy'", (version,))
                self.conn.execute("INSERT INTO audit_events(event_type,evidence_json) VALUES('POLICY_ACTIVATED',?)",
                                  (canonical({"from": old, "to": version}),))
        return {"active_policy": version, "payment_authorized": False}

    def _record(self, row):
        if row is None:
            raise HistoryError("NOT_FOUND")
        row = dict(row)
        valid = (digest(row["payload_json"]) == row["payload_sha256"]
                 and digest(row["decision_json"]) == row["decision_sha256"]
                 and digest(row["policy_json"]) == row["policy_sha256"]
                 and digest(canonical_payload(json.loads(row["payload_json"]))) == row["request_fingerprint"]
                 and self._policy(row["policy_version"]) == json.loads(row["policy_json"])
                 and _record_identity(row["request_key"], row["payload_sha256"], row["policy_sha256"],
                                      row["decision_sha256"], row["parent_key"]) == row["decision_id"])
        if not valid:
            raise HistoryError("HISTORY_INTEGRITY")
        return {**row, "payload": json.loads(row["payload_json"]),
                "policy": json.loads(row["policy_json"]), "decision": json.loads(row["decision_json"])}

    def replay(self, key):
        """Return the exact stored response; no policy recomputation or writes."""
        valid_key(key)
        return self._record(self.conn.execute("SELECT * FROM decisions WHERE request_key=?", (key,)).fetchone())

    def recompute(self, key):
        """Recalculate using the recorded snapshot; do not create a new decision."""
        record = self.replay(key)
        calculated = outcome(record["payload"], record["policy"])
        if calculated != record["decision"]:
            raise HistoryError("HISTORICAL_REPLAY_MISMATCH")
        return {"status": "MATCH", "decision_id": record["decision_id"],
                "recorded_policy": record["policy_version"], "recomputed": calculated}

    def _decide(self, key, payload, version, parent):
        valid_key(key)
        fingerprint = digest(canonical_payload(payload))
        if version is not None:
            self._policy(version)  # Explicit caller intent is not an ambient default.
        existing = self.conn.execute("SELECT * FROM decisions WHERE request_key=?", (key,)).fetchone()
        if existing is not None:
            record = self._record(existing)
            if (record["request_fingerprint"] != fingerprint or record["parent_key"] != parent
                    or (version is not None and version != record["policy_version"])):
                raise HistoryError("IDEMPOTENCY_CONFLICT")
            return {"status": "REPLAYED", "record": record}
        policy = self._policy(version or self.active_policy())
        identity = _insert(self.conn, key, canonical(payload), canonical(policy),
                           canonical(outcome(payload, policy)), parent)
        self.conn.execute("INSERT INTO audit_events(event_type,request_key,evidence_json) VALUES('DECISION_RECORDED',?,?)",
                          (key, canonical({"decision_id": identity, "parent_key": parent})))
        return {"status": "CREATED", "record": self.replay(key)}

    def decide(self, key, payload, policy_version=None):
        with transaction(self.conn):
            return self._decide(key, payload, policy_version, None)

    def reevaluate(self, old_key, new_key, policy_version):
        if old_key == new_key:
            raise HistoryError("NEW_KEY_REQUIRED")
        with transaction(self.conn):
            old = self.replay(old_key)
            self._policy(policy_version)
            return self._decide(new_key, old["payload"], policy_version, old_key)


def migrate_legacy(path, catalog, provenance):
    """Atomic conversion of an explicitly evidenced synthetic v1 fixture.

    Provenance is a trusted owner-supplied input to this reusable API; the owner
    CLI independently binds it to a protected synthetic fixture. This is not
    authentication of real-world historical records.
    Missing provenance, policy or outcome is a stop condition, never a default
    to today's policy. The original legacy_decisions table remains untouched.
    """
    catalog = checked_catalog(catalog)
    conn = _connect(path)
    try:
        with transaction(conn):
            if conn.execute("PRAGMA user_version").fetchone()[0] != 1 or conn.execute("PRAGMA application_id").fetchone()[0] != APPLICATION_ID:
                raise HistoryError("LEGACY_SCHEMA_REQUIRED")
            rows = [dict(row) for row in conn.execute("SELECT * FROM legacy_decisions ORDER BY request_key")]
            if (not isinstance(provenance, dict) or provenance.get("schema") != "cp11-legacy-provenance/v1"
                    or provenance.get("origin") != "SYNTHETIC_BROWNFIELD_FIXTURE"
                    or not isinstance(provenance.get("source_id"), str) or not provenance["source_id"].strip()
                    or provenance.get("rows_sha256") != digest(canonical(rows))):
                raise HistoryError("LEGACY_PROVENANCE_MISMATCH")
            validated = []
            for row in rows:
                valid_key(row["request_key"])
                if any(not isinstance(row.get(field), str) for field in ("payload_json", "policy_json", "decision_json")):
                    raise HistoryError("HISTORY_AMBIGUOUS")
                payload, policy, decision = (json.loads(row[field]) for field in ("payload_json", "policy_json", "decision_json"))
                canonical_payload(payload)
                if not isinstance(policy, dict) or policy.get("version") not in catalog or policy != catalog[policy["version"]]:
                    raise HistoryError("HISTORY_AMBIGUOUS")
                if decision != outcome(payload, policy):
                    raise HistoryError("LEGACY_OUTCOME_MISMATCH")
                validated.append(row)
            _schema(conn)
            _install_catalog(conn, catalog)
            for row in validated:
                identity = _insert(conn, row["request_key"], row["payload_json"], row["policy_json"], row["decision_json"])
                conn.execute("INSERT INTO audit_events(event_type,request_key,evidence_json) VALUES('LEGACY_IMPORTED',?,?)",
                             (row["request_key"], canonical({"decision_id": identity, "source_id": provenance.get("source_id"),
                                                            "rows_sha256": provenance["rows_sha256"]})))
            for action in ("UPDATE", "DELETE"):
                conn.execute(f"""CREATE TRIGGER immutable_legacy_{action.lower()}
                  BEFORE {action} ON legacy_decisions BEGIN
                  SELECT RAISE(ABORT, 'immutable_history'); END""")
        return {"status": "MIGRATED", "records": len(rows), "source_id": provenance.get("source_id"),
                "original_table_preserved": True}
    finally:
        conn.close()
