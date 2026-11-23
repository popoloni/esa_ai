import unittest, io, json, sqlite3
from contextlib import redirect_stdout,redirect_stderr
from unittest.mock import patch
import reservation_report
import reservation_cli
class CLIContract(unittest.TestCase):
    def call(self, args):
        out,err=io.StringIO(),io.StringIO()
        with redirect_stdout(out),redirect_stderr(err):
            try:code=reservation_cli.main(args)
            except SystemExit as ex:code=ex.code
        return code,out.getvalue(),err.getvalue()
    def test_found_uses_report_and_prints_exact_json(self):
        data={"found":True,"reservation":{"sentinel":"public report"},"current":{"state":"cancelled","version":2}}
        with patch.object(reservation_report,"build_report",return_value=data) as fake:
            # Also support a direct imported binding, which is a valid composition.
            target='reservation_cli.build_report' if hasattr(reservation_cli,'build_report') else 'reservation_report.build_report'
            with patch(target,return_value=data) as selected:
                code,out,err=self.call(['inspect','--database','chosen.sqlite','--reservation-id','41'])
                self.assertEqual(code,0);self.assertEqual(json.loads(out),data);self.assertEqual(err,'')
                selected.assert_called_once();self.assertEqual(selected.call_args.args[1],41)
    def test_absent_exit_is_distinct(self):
        target='reservation_cli.build_report' if hasattr(reservation_cli,'build_report') else 'reservation_report.build_report'
        data={"found":False,"reservation":None,"current":None}
        with patch(target,return_value=data):
            code,out,err=self.call(['inspect','--database','chosen.sqlite','--reservation-id','99'])
        self.assertEqual(code,3);self.assertEqual(json.loads(out),data);self.assertEqual(err,'')
    def test_storage_error_and_bad_identifier(self):
        target='reservation_cli.build_report' if hasattr(reservation_cli,'build_report') else 'reservation_report.build_report'
        with patch(target,side_effect=sqlite3.OperationalError('no database')):
            code,out,err=self.call(['inspect','--database','missing.sqlite','--reservation-id','1'])
        self.assertEqual(code,2);self.assertEqual(out,'');self.assertTrue(err.strip())
        for raw in ('0','-1','abc'):
            code,out,err=self.call(['inspect','--database','chosen.sqlite','--reservation-id',raw])
            self.assertEqual(code,2);self.assertEqual(out,'')
