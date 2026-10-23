"""Local function demonstration, not an authenticated HTTP deployment."""
import argparse
import json
from pathlib import Path
from api import orders_response

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("--actor", default="alice")
    parser.add_argument("--status", default=None)
    args = parser.parse_args()
    rows = json.loads((Path(__file__).parent / "orders.json").read_text())
    result = orders_response(rows, args.actor, args.format, args.status)
    if args.format == "json":
        print(json.dumps(result["body"], indent=2))
    else:
        print(result["body"], end="")

if __name__ == "__main__":
    main()
