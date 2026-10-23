"""Contributor B repairs the missing notice in the outer presentation."""
from label import make_label

def render(route):
    return make_label(route) + " | Routing only; no payment approval."

