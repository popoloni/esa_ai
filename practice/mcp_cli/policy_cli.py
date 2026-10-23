#!/usr/bin/env python3
"""Read a named synthetic policy. Standard library only; no arbitrary path input."""
import argparse
import json
import sys
from policy_lookup import lookup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["lookup"])
    parser.add_argument("policy_id", help="BR-001/v1 or BR-001/v2")
    args = parser.parse_args()
    result = lookup(args.policy_id)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
