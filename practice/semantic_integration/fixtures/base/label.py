"""Authored teaching baseline: labels omit the required notice."""
LABELS = {
    "STANDARD_QUEUE": "Recommended standard queue",
    "HUMAN_REVIEW": "Recommended human review",
    "REJECTED": "Rejected",
}

def make_label(route):
    return LABELS[route]

