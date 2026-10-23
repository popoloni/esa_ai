"""Versioned CP08 attempt provenance; retained evidence is not proof of a model's identity.

This verifies the internal consistency and byte binding of a reader's observation.
An independent observer must still assess whether that record describes a real run.
No live client, human approval or release is inferred from deterministic case results.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json
import re

ROOT = Path(__file__).resolve().parents[2]
REPORT_SCHEMA = 'implementation-report/v2'
OBSERVATION_SCHEMA = 'agent-client-observation/v1'
FIXTURE_ORIGIN = 'SYNTHETIC_TEACHING_CASE'
OFFLINE = 'OFFLINE_DETERMINISTIC'
ACTUAL = 'ACTUAL_AGENT_CLIENT'


def evidence_path(ref, root=ROOT):
    """Return a canonical, contained non-symlink path or reject it before reading."""
    if not isinstance(ref, dict) or set(ref) != {'path', 'sha256'}:
        raise ValueError('reference must contain exactly path and sha256')
    rel, digest = ref['path'], ref['sha256']
    if not isinstance(rel, str) or not rel or '\\' in rel or '\0' in rel:
        raise ValueError('invalid path')
    parsed = PurePosixPath(rel)
    if parsed.is_absolute() or str(parsed) != rel or any(x in ('.', '..') for x in rel.split('/')):
        raise ValueError('path must be canonical and relative to the companion root')
    if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
        raise ValueError('sha256 must be 64 lowercase hexadecimal characters')
    root = Path(root).resolve()
    path = root / rel
    if any((root.joinpath(*parsed.parts[:i])).is_symlink() for i in range(1, len(parsed.parts) + 1)):
        raise ValueError('symlinked evidence path')
    if not path.resolve().is_relative_to(root):
        raise ValueError('evidence escaped the companion root')
    return path


def _bound_bytes(ref, label, issues, root):
    try:
        path = evidence_path(ref, root)
        data = path.read_bytes()
        if not data:
            issues.append(label + '_EMPTY')
        if sha256(data).hexdigest() != ref['sha256']:
            issues.append(label + '_SHA_MISMATCH')
        return path, data
    except (OSError, ValueError, TypeError) as exc:
        issues.append(label + '_INVALID:' + str(exc))
        return None, None


def observed_evidence_paths(report, root=ROOT):
    """Discover evidence inputs for a receipt, even if their digest later fails.

    Missing files are handled by receipt generation and by provenance_findings;
    malformed references are handled by provenance_findings, never trusted here.
    """
    if not isinstance(report, dict) or report.get('schema') != REPORT_SCHEMA:
        return []
    ref = report.get('observed_run_ref')
    if ref is None:
        return []
    try:
        path = evidence_path(ref, root)
    except (ValueError, TypeError):
        return []
    paths = [path]
    try:
        observation = json.loads(path.read_text(encoding='utf-8'))
        paths.append(evidence_path(observation.get('transcript_ref'), root))
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return paths


def provenance_findings(report, *, root=ROOT, candidate_path=None):
    """Accept historical offline receipts or explicit v2 attempt provenance."""
    schema = report.get('schema')
    if schema is None or schema == 'implementation-report/v1':
        issues = []
        if report.get('live_agent_run') is not False:
            issues.append('LEGACY_OFFLINE_ONLY: use implementation-report/v2 with bound observation for an actual-client attempt')
        if any(key in report for key in ('fixture_origin', 'execution_mode', 'observed_run_ref')):
            issues.append('REPORT_SCHEMA_REQUIRED: provenance fields require implementation-report/v2')
        return issues
    if schema != REPORT_SCHEMA:
        return ['REPORT_SCHEMA_UNSUPPORTED:' + str(schema)]
    issues = []
    if report.get('record_revision') != 2:
        issues.append('REPORT_RECORD_REVISION')
    if 'live_agent_run' in report:
        issues.append('V2_LEGACY_FLAG_NOT_ALLOWED: use execution_mode and observed_run_ref')
    if report.get('fixture_origin') != FIXTURE_ORIGIN:
        issues.append('FIXTURE_ORIGIN_INVALID')
    mode = report.get('execution_mode')
    if mode not in (OFFLINE, ACTUAL):
        issues.append('EXECUTION_MODE_INVALID')
    if 'observed_run_ref' not in report:
        issues.append('OBSERVED_RUN_REF_FIELD_REQUIRED')
    ref = report.get('observed_run_ref')
    if mode == OFFLINE:
        if ref is not None:
            issues.append('OFFLINE_OBSERVATION_CONTRADICTION')
        return issues
    if mode != ACTUAL:
        return issues
    if ref is None:
        return issues + ['OBSERVED_RUN_REF_REQUIRED: actual-client claims need retained, SHA-bound evidence']
    _, data = _bound_bytes(ref, 'OBSERVED_RUN', issues, root)
    if data is None:
        return issues
    try:
        observation = json.loads(data)
        if not isinstance(observation, dict):
            raise ValueError('observation is not an object')
    except (ValueError, UnicodeError):
        return issues + ['OBSERVED_RUN_JSON_INVALID']
    expected = {
        'schema': OBSERVATION_SCHEMA,
        'record_kind': 'ACTUAL_EXECUTION_RECORD',
        'execution_mode': ACTUAL,
        'change_id': report.get('change_id'),
        'claim_scope': 'CLIENT_ATTEMPT_ONLY_NOT_ACCEPTANCE',
    }
    for key, value in expected.items():
        if observation.get(key) != value:
            issues.append('OBSERVED_RUN_FIELD:' + key)
    for key in ('run_id', 'environment'):
        if not isinstance(observation.get(key), str) or not observation[key].strip():
            issues.append('OBSERVED_RUN_FIELD:' + key)
    client = observation.get('client')
    if not isinstance(client, dict) or any(not isinstance(client.get(key), str) or not client[key].strip()
                                           for key in ('name', 'version', 'model')):
        issues.append('OBSERVED_RUN_CLIENT_IDENTITY_REQUIRED')
    if observation.get('outcome') not in ('COMPLETED', 'FAILED', 'INTERRUPTED'):
        issues.append('OBSERVED_RUN_OUTCOME_INVALID')
    try:
        start = datetime.fromisoformat(observation['started_at'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(observation['ended_at'].replace('Z', '+00:00'))
        if start.tzinfo is None or end.tzinfo is None or end < start:
            raise ValueError('invalid observation interval')
    except (KeyError, ValueError, TypeError, AttributeError):
        issues.append('OBSERVED_RUN_TIMES_INVALID')
    try:
        if candidate_path is None or sha256(Path(candidate_path).read_bytes()).hexdigest() != observation.get('candidate_sha256'):
            issues.append('OBSERVED_RUN_CANDIDATE_SHA_MISMATCH')
    except OSError:
        issues.append('OBSERVED_RUN_CANDIDATE_UNREADABLE')
    _bound_bytes(observation.get('transcript_ref'), 'OBSERVED_TRANSCRIPT', issues, root)
    return issues


def provenance_summary(report):
    if report.get('schema') != REPORT_SCHEMA:
        return {'schema_mode': 'LEGACY_V1_OFFLINE_COMPATIBILITY',
                'fixture_origin': FIXTURE_ORIGIN, 'execution_mode': OFFLINE,
                'observed_run_ref': None,
                'meaning': 'Historical live_agent_run=false remains an offline claim; it is not relabeled as an actual client run.'}
    return {'schema_mode': 'V2_SEPARATE_PROVENANCE',
            **{key: report.get(key) for key in ('fixture_origin', 'execution_mode', 'observed_run_ref')},
            'meaning': 'Observation metadata and byte binding are checked separately from selected offline domain cases; external authenticity still needs review.'}
