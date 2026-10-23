"""Contributor A repairs the missing notice in the label helper."""
LABELS = {
    "STANDARD_QUEUE": "Recommended standard queue",
    "HUMAN_REVIEW": "Recommended human review",
    "REJECTED": "Rejected",
}

def make_label(route):
    return LABELS[route] + " | Routing only; no payment approval."

