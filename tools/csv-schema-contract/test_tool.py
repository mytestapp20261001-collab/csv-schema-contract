import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(HERE.name.replace("-", "_"), HERE / "tool.py")
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)

class CommonTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, str(HERE / "tool.py"), *args], cwd=HERE,
                              capture_output=True, text=True, timeout=10)
    def test_cli_pass(self):
        result = self.cli("examples/" + PASS, *ARGS)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")
        self.assertEqual(result.stderr, "")
    def test_cli_fail(self):
        result = self.cli("examples/" + FAIL, *ARGS)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")
    def test_cli_malformed(self):
        result = self.cli("examples/" + MALFORMED, *ARGS)
        self.assertEqual(result.returncode, MALFORMED_CODE, result.stdout + result.stderr)
        self.assertIn(json.loads(result.stdout)["status"], ("fail", "error"))
    def test_cli_missing_file(self):
        result = self.cli("nonexistent-input", *ARGS)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["error"], "unreadable_utf8_input")
    def test_cli_invalid_arguments_are_redacted(self):
        result = self.cli("--unrecognized-secret-value")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["error"], "invalid_arguments")
        self.assertNotIn("unrecognized-secret-value", result.stdout + result.stderr)
    def test_cli_help(self):
        result = self.cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)
    def test_cli_stability(self):
        a = self.cli("examples/" + FAIL, *ARGS)
        b = self.cli("examples/" + FAIL, *ARGS)
        self.assertEqual(a.stdout, b.stdout)
    def test_file_limit_and_utf8(self):
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            path = Path(directory) / "input"
            path.write_bytes(b"x" * (tool.MAX_BYTES + 1))
            with self.assertRaises(tool.InputError):
                tool.read_text(path)
            path.write_bytes(b"\xff")
            with self.assertRaises(UnicodeDecodeError):
                tool.read_text(path)
    def test_json_parser_safety(self):
        for text in ('{"x":1,"x":2}', '[NaN]', '[' * 130 + '0' + ']' * 130):
            with self.subTest(text=text[:20]), self.assertRaises(tool.InputError):
                tool.parse_json(text)
    def test_report_cap_preserves_count(self):
        report = tool.Report("test")
        for i in range(101):
            report.add("sample", record=i)
        result = report.finish()
        self.assertEqual(len(result["findings"]), 100)
        self.assertEqual(result["summary"]["finding_count"], 101)
        self.assertTrue(result["findings_truncated"])

    def test_adversarial_cli_and_read_only_corpus(self):
        samples = ['', 'null', 'true', '0', '[]', '{}', '[null]', '[true]', '[1]',
                   '["NaN"]', '[{}]', '[[]]', '{"x":1,"x":2}',
                   '[1e99999999999999999999999999]', '[NaN]', '[Infinity]',
                   '"\\ud800"', '["\\ud800"]', '{', '[', '["a","b"]',
                   '[1e-99999999999999999999999999]']
        before = {path: path.read_bytes() for path in (HERE / 'examples').iterdir()}
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            path = Path(directory) / 'input.txt'
            for sample in samples:
                with self.subTest(sample=sample):
                    path.write_text(sample, encoding='utf-8')
                    result = self.cli(str(path), *ARGS)
                    self.assertIn(result.returncode, (0, 1, 2), result.stderr)
                    self.assertEqual(result.stderr, '')
                    self.assertIn(json.loads(result.stdout)['status'], ('pass','fail','error'))
                    self.assertEqual(path.read_text(encoding='utf-8'), sample)
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)

PASS = 'pass.csv'
FAIL = 'fail.csv'
MALFORMED = 'malformed.csv'
MALFORMED_CODE = 2
ARGS = ['--contract', 'examples/contract.json']

class AuditTests(unittest.TestCase):
    def contract(self, **extra):
        return dict(columns=[{"name":"id","type":"integer"},{"name":"value","type":"string","required":False}], **extra)
    def test_quoted_newline_and_empty_optional(self):
        self.assertEqual(tool.audit('id,value\n1,"line\nnext"\n2,\n', self.contract())["status"], "pass")
    def test_duplicate_missing_and_extra_headers(self):
        result = tool.audit('id,id,extra\n1,2,z\n', self.contract())
        self.assertEqual({f['code'] for f in result['findings']}, {'duplicate_header','missing_column','unexpected_column'})
    def test_width_and_type(self):
        result = tool.audit('id,value\nx\n1,x,extra\n', self.contract())
        self.assertEqual(result['summary']['finding_count'], 3)
    def test_empty_required(self):
        self.assertEqual(tool.audit('id,value\n,x\n', self.contract())['findings'][0]['code'], 'missing_value')
    def test_order(self):
        self.assertEqual(tool.audit('value,id\nx,1\n', self.contract(header_order=True))['status'], 'fail')
    def test_allow_extra(self):
        self.assertEqual(tool.audit('id,value,x\n1,v,q\n', self.contract(allow_extra=True))['status'], 'pass')
    def test_all_types(self):
        self.assertTrue(tool.valid_type('-10','integer'))
        self.assertFalse(tool.valid_type('１２','integer'))
        self.assertTrue(tool.valid_type('.5e-2','decimal'))
        for value in ('NaN','Infinity',' 1 '):
            self.assertFalse(tool.valid_type(value,'decimal'))
        self.assertFalse(tool.valid_type('2026-02-29','date'))
        self.assertTrue(tool.valid_type('2024-02-29','date'))
    def test_contract_error(self):
        for contract in ({}, {'columns':[]}, {'columns':[{'name':'x','type':'unknown'}]}, {'columns':[{'name':'x','type':[]}]} , self.contract(allow_extra='true')):
            with self.subTest(contract=contract), self.assertRaises(tool.InputError): tool.audit('id\n1',contract)
    def test_malformed_and_empty(self):
        for text in ('','id,value\n1,"bad'):
            with self.assertRaises(tool.InputError): tool.audit(text,self.contract())
    def test_record_limit(self):
        previous = tool.MAX_RECORDS
        try:
            tool.MAX_RECORDS = 1
            with self.assertRaises(tool.InputError): tool.audit('id,value\n1,x\n2,y',self.contract())
        finally: tool.MAX_RECORDS = previous
    def test_parser_global_limit_restored(self):
        previous=tool.csv.field_size_limit()
        tool.audit('id,value\n1,x',self.contract())
        self.assertEqual(tool.csv.field_size_limit(),previous)
        with self.assertRaises(tool.InputError): tool.audit('',self.contract())
        self.assertEqual(tool.csv.field_size_limit(),previous)
    def test_values_redacted(self):
        result = tool.audit('id,value\nSUPERSECRET,x\n',self.contract())
        self.assertNotIn('SUPERSECRET',json.dumps(result))

if __name__ == '__main__': unittest.main()
