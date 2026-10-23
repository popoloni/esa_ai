"""Distinguish absent text from wording this small teaching rubric cannot assess.

Token/prefix recognition does not prove semantics. Unknown equivalents need
human review, not an accusation that the author omitted the underlying idea.
"""


def rubric_text(value, field, *, prefix=None, terms=()):
    if not isinstance(value, str) or not value.strip():
        return ['TEXT_MISSING:' + field]
    if prefix is not None and not value.startswith(prefix):
        return ['HUMAN_SEMANTIC_REVIEW:' + field + ': wording differs from the example; review the authority boundary']
    missing = [term for term in terms if term.lower() not in value.lower()]
    if missing:
        return ['HUMAN_SEMANTIC_REVIEW:' + field + ': lexical rubric did not recognize ' + ', '.join(missing)]
    return []


def finding_state(findings):
    if not findings:
        return 'PASS'
    if all(x.startswith('HUMAN_SEMANTIC_REVIEW:') for x in findings):
        return 'HUMAN_SEMANTIC_REVIEW'
    return 'FAIL'
