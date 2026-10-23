"""Known outstanding decisions for CTX-006; no decision can be self-approved here."""
CONTEXT_SCHEMA = 'context-packet/v2'
MANDATORY_REVIEWS = ('ADR-005', 'OPERATOR_COPY')
REVIEW_SUBJECTS = {
    'ADR-005': ('ADR-005/v1', 'Technical Lead (synthetic scenario)'),
    'OPERATOR_COPY': ('SPEC-004/v1#operator-copy', 'Product Owner (synthetic scenario)'),
    'SPEC-004': ('SPEC-004/v1', 'Product Owner (synthetic scenario)'),
}


def current_pending_reviews():
    return [{'review_id': key, 'subject_ref': subject, 'owner_role': owner,
             'status': 'PENDING_HUMAN', 'decision_ref': None}
            for key, (subject, owner) in REVIEW_SUBJECTS.items()]


def pending_review_findings(records, *, require_complete=True):
    if not isinstance(records, list):
        return ['PENDING_REVIEWS_NOT_LIST']
    issues, seen = [], set()
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get('review_id'), str):
            issues.append('PENDING_REVIEW_RECORD_INVALID')
            continue
        key = record['review_id']
        if key in seen:
            issues.append('PENDING_REVIEW_DUPLICATE:' + key)
        seen.add(key)
        if key not in REVIEW_SUBJECTS:
            issues.append('PENDING_REVIEW_UNKNOWN:' + key)
            continue
        subject, owner = REVIEW_SUBJECTS[key]
        if record.get('subject_ref') != subject:
            issues.append('PENDING_REVIEW_SUBJECT:' + key)
        if record.get('owner_role') != owner:
            issues.append('PENDING_REVIEW_OWNER:' + key)
        if record.get('status') != 'PENDING_HUMAN' or record.get('decision_ref') is not None:
            issues.append('PENDING_REVIEW_UNSUPPORTED_APPROVAL:' + key)
    required = set(REVIEW_SUBJECTS) if require_complete else set(MANDATORY_REVIEWS)
    issues += ['PENDING_REVIEW_MISSING:' + key for key in sorted(required - seen)]
    return sorted(set(issues))


def context_review_findings(packet):
    schema = packet.get('schema')
    if schema is None or schema == 'context-packet/v1':
        # Legacy minimum remains valid. A truthful additional SPEC-004 is allowed.
        ids = packet.get('human_review_required')
        if not isinstance(ids, list) or any(not isinstance(x, str) for x in ids):
            return ['HUMAN_REVIEW_LIST_INVALID']
        issues = ['HUMAN_REVIEW_MISSING:' + key for key in sorted(set(MANDATORY_REVIEWS) - set(ids))]
        issues += ['HUMAN_REVIEW_UNKNOWN:' + key for key in sorted(set(ids) - set(REVIEW_SUBJECTS))]
        if len(ids) != len(set(ids)):
            issues.append('HUMAN_REVIEW_DUPLICATE')
        return issues
    if schema != CONTEXT_SCHEMA:
        return ['CONTEXT_SCHEMA_UNSUPPORTED:' + str(schema)]
    issues = []
    if packet.get('record_revision') != 2:
        issues.append('CONTEXT_RECORD_REVISION')
    required = packet.get('mandatory_human_reviews')
    if not isinstance(required, list) or set(required) != set(MANDATORY_REVIEWS) or len(required) != len(MANDATORY_REVIEWS):
        issues.append('MANDATORY_HUMAN_REVIEWS_MISMATCH')
    if 'human_review_required' in packet:
        issues.append('V2_AMBIGUOUS_REVIEW_LIST: use mandatory_human_reviews and pending_reviews')
    return issues + pending_review_findings(packet.get('pending_reviews'))


def pending_review_ids(packet):
    if packet.get('schema') == CONTEXT_SCHEMA:
        return {x['review_id'] for x in packet.get('pending_reviews', [])
                if isinstance(x, dict) and isinstance(x.get('review_id'), str)}
    return set(packet.get('human_review_required', []))
