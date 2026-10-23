#!/usr/bin/env python3
"""Owner-side behavioral checks; no canonical-source hash or prose matching."""
from pathlib import Path
import argparse, copy, csv, importlib, io, json, sys

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    args=parser.parse_args()
    sys.path.insert(0,str(args.candidate.resolve()))
    from api import orders_response
    rows=[
      {"order_id":"R1","owner":"a","status":"open","customer":"A, B","amount_eur":"10.01","note":"Say \"yes\"\nnext"},
      {"order_id":"R2","owner":"b","status":"open","customer":"Hidden","amount_eur":"9.00","note":"secret"},
      {"order_id":"R3","owner":"a","status":"closed","customer":"Caffè","amount_eur":"0.00","note":"=2+2"},
    ]
    fields=["order_id","status","customer","amount_eur","note"]
    before=copy.deepcopy(rows)
    failures=[];passed=[]
    def check(name, fn):
        try: fn();passed.append(name)
        except Exception as exc: failures.append({"case":name,"error":type(exc).__name__,"message":str(exc)})
    def expect(rows_wanted, actor, status=None):
        result=orders_response(rows,actor,"csv",status)
        assert result["content_type"] == "text/csv; charset=utf-8"
        records=list(csv.reader(io.StringIO(result["body"],newline="")))
        assert records[0] == fields, records
        assert records[1:] == [[row[k] for k in fields] for row in rows_wanted], records
    check("authorized_membership_and_csv_roundtrip",lambda:expect([rows[0],rows[2]],"a"))
    check("preserve_existing_status_filter",lambda:expect([rows[0]],"a","open"))
    check("empty_result_keeps_header",lambda:expect([],"nobody"))
    check("other_actor_gets_only_own_rows",lambda:expect([rows[1]],"b"))
    def json_unchanged():
        expected={"content_type":"application/json","body":[{k:rows[0][k] for k in fields}]}
        assert orders_response(rows,"a","json","open")==expected
    check("existing_json_unchanged",json_unchanged)
    def unsupported():
        try: orders_response(rows,"a","xml")
        except ValueError: return
        raise AssertionError("unsupported format was accepted")
    check("unsupported_format_refused",unsupported)
    def immutable():
        assert rows==before, "presentation changed source rows"
    check("source_rows_unchanged",immutable)
    result={"status":"PASS_SELECTED_CONTRACT" if not failures else "REFUSE_SELECTED_CONTRACT", "passed":passed,"findings":failures,
            "limits":"Local function and declared machine-CSV contract; no HTTP authentication, spreadsheet safety, scale or deployment validation."}
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return bool(failures)

if __name__=="__main__":sys.exit(main())
