#!/usr/bin/env python3
"""Derive printable function excerpts from the executable reference modules.

Whitespace outside literals is narrowed without AST changes. Every function
is checked against its authentic source;
source/fragment hashes and selectors are emitted for independent reproduction.
"""
from pathlib import Path
import ast
import hashlib
import json
from reflow_python import narrow, dedent_code, check_literal_integrity

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "curriculum/excerpts"
SELECTIONS = {
    "g2_reserve.py": ("solutions/G2/booking.py", ["reserve"]),
    "g3_cancel.py": ("solutions/G3/booking.py", ["cancel"]),
    "g4_cost_summary.py": ("solutions/G4/operations.py", ["cost_summary"]),
    "b2_evaluate_batch.py": ("solutions/B2/intake.py", ["_receipt", "evaluate_batch"]),
    "b3_decide.py": ("solutions/B3/ledger.py", ["PolicyStore._decide"]),
    "b3_reevaluate.py": ("solutions/B3/ledger.py", ["PolicyStore.reevaluate"]),
    "b4_diagnose_plan.py": ("solutions/B4/incident.py", ["diagnose", "recovery_plan"]),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def derive():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = []
    for name, (source, selectors) in SELECTIONS.items():
        path = ROOT / source
        raw = path.read_bytes()
        tree = ast.parse(raw.decode())
        lines = raw.decode().splitlines(keepends=True)
        fragments, literal_checks = [], []
        for selector in selectors:
            node = tree
            for part in selector.split("."):
                node = next(n for n in node.body if getattr(n,"name",None) == part)
            fragment = dedent_code("".join(lines[node.lineno-1:node.end_lineno]))
            assert ast.dump(ast.parse(fragment).body[0],include_attributes=False) == ast.dump(node,include_attributes=False)
            formatted = narrow(fragment, 68)
            literal_checks.append(check_literal_integrity(fragment, formatted))
            fragments.append(formatted)
        data = "\n".join(fragments).encode()
        (OUTPUT/name).write_bytes(data)
        records.append({"output":"curriculum/excerpts/"+name,"source":source,"selectors":selectors,
                        "source_sha256":digest(raw),"output_sha256":digest(data),
                        "transformation":"AST-selected complete function; whitespace-only narrow layout at 68 columns; literal tokens retained exactly",
                        "literal_checks":literal_checks,
                        "max_line_length":max(map(len, data.decode().splitlines())),
                        "ast_equivalent":True})
    manifest = {"schema":"esa-curriculum-print-derivation/v1","command":"python3 companion/curriculum/derive_excerpts.py","records":records}
    (OUTPUT/"PROVENANCE.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"status":"PASS","functions":sum(len(v[1]) for v in SELECTIONS.values()),"files":len(records),"provenance":str(OUTPUT/"PROVENANCE.json")},indent=2))

if __name__ == "__main__":
    derive()
