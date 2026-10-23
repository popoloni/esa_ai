"""Educational anti-pattern. This test intentionally knows no expected policy."""

def run(candidate):
    for amount in ("1", "4999.99", "5000", "7000"):
        a = candidate(amount)
        b = candidate(amount)
        if a != b:
            return False
    return True
