"""The outer presentation layer owns the complete user-facing sentence."""
from label import make_label

def render(route):
    return make_label(route)

