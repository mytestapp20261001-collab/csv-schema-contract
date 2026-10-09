import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
import tool

ROOT = Path(__file__).parent

def fixture(name="good"):
    return json.loads((ROOT / "examples" / (name + ".json")).read_text())

class CLITests(unittest.TestCase):
    def run_tool(self, raw):
        return subprocess.run([sys.executable, str(ROOT / "tool.py")], input=raw, capture_output=True, text=True)

    def test_cli_fixture_exit_codes(self):
        for name, code in [("good", 0), ("bad", 1)]:
            run = subprocess.run([sys.executable, str(ROOT / "tool.py"), "--input", str(ROOT / "examples" / (name + ".json"))], capture_output=True, text=True)
            self.assertEqual(run.returncode, code, run.stdout + run.stderr)
            self.assertEqual(json.loads(run.stdout)["ok"], code == 0)
            self.assertEqual(run.stderr, "")

    def test_cli_argument_errors_are_json_and_redacted(self):
        secret = "PRIVATE_ARGUMENT_MARKER"
        for arguments in [("--unknown", secret), ("--input",),
                          ("--pretty=" + secret,), (secret,)]:
            run = subprocess.run([sys.executable, str(ROOT / "tool.py"), *arguments],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(run.stderr, "")
            self.assertNotIn(secret, run.stdout + run.stderr)
            self.assertEqual(json.loads(run.stdout)["error"]["code"], "invalid_input")

    def test_cli_help_remains_text_and_success(self):
        run = subprocess.run([sys.executable, str(ROOT / "tool.py"), "--help"],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0)
        self.assertEqual(run.stderr, "")
        self.assertIn("--input", run.stdout)

    def test_large_json_integer_is_safe_error(self):
        run=self.run_tool('{"number":'+'9'*5000+'}')
        self.assertEqual(run.returncode,2)
        self.assertEqual(run.stderr,'')
        self.assertEqual(json.loads(run.stdout)['error']['code'],'invalid_input')

    def test_nonregular_input_file(self):
        run=subprocess.run([sys.executable,str(ROOT/'tool.py'),'--input',str(ROOT)],capture_output=True,text=True)
        self.assertEqual(run.returncode,2)
        self.assertEqual(run.stderr,'')

    def test_bad_json(self):
        for raw in ['{', '{"x":1,"x":2}', '[]', '{"x":NaN}', '"' + 'x' * (tool.MAX_BYTES + 1) + '"']:
            run = self.run_tool(raw)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(json.loads(run.stdout)["error"]["code"], "invalid_input")

    def test_unknown_field_and_boolean_number(self):
        obj = fixture(); obj["unrecognized"] = 1
        with self.assertRaises(tool.InputError): tool.audit(obj)

    def test_output_is_deterministic(self):
        raw=json.dumps(fixture())
        self.assertEqual(self.run_tool(raw).stdout, self.run_tool(raw).stdout)

import hashlib
class FilenameTests(unittest.TestCase):
    def audit_header(self,value): return tool.audit({'content_disposition':value})
    def test_extended_precedence(self):
        out=tool.audit(fixture()); self.assertTrue(out['ok']); self.assertEqual(out['selected_parameter'],'filename*')
        self.assertEqual(out['candidates'][1]['filename_sha256'],hashlib.sha256('report-€.txt'.encode()).hexdigest())
    def test_latin1_compatibility(self):
        self.assertEqual(tool.decode_extended("ISO-8859-1'en'%A3.txt"),'£.txt')
    def test_plus_is_literal_not_form_space(self):
        self.assertEqual(tool.decode_extended("UTF-8''a+b.txt"),'a+b.txt')
    def test_quoted_semicolon(self):
        self.assertTrue(self.audit_header('attachment; filename="report;v2.txt"')['ok'])
    def test_duplicate_parameters_not_resolved(self):
        out=self.audit_header('attachment; filename=a.txt; FILENAME=b.txt')
        self.assertFalse(out['ok']); self.assertIsNone(out['selected_parameter'])
    def test_missing_filename(self): self.assertFalse(self.audit_header('inline')['ok'])
    def test_no_echo(self):
        self.assertNotIn('PRIVATE_NAME',json.dumps(self.audit_header('attachment; filename=PRIVATE_NAME.txt')))
    def test_path_hazards(self):
        for name in ['../../x','..\\x','/etc/file','C:\\x','\\\\host\\share','.','..']:
            self.assertTrue(tool.inspect_filename(name),name)
    def test_reserved_devices_and_characters(self):
        for name in ['CON.txt','LPT1','COM¹.txt','x:stream','a?b','a|b']:
            self.assertTrue(tool.inspect_filename(name),name)
    def test_control_unicode_and_trailing_spaces(self):
        for name in ['a\x00b','a\u202eb','x.',' x','e\u0301.txt','x '*256]:
            self.assertTrue(tool.inspect_filename(name),name)
    def test_percent_is_not_decoded_twice(self):
        out=self.audit_header("attachment; filename*=UTF-8''%252e%252e%252fx")
        self.assertIn('literal_percent_escape_can_be_misinterpreted',{v['code'] for v in out['findings']})
    def test_both_fallback_and_extended_are_audited(self):
        out=self.audit_header("attachment; filename=CON; filename*=UTF-8''safe.txt")
        self.assertEqual(out['selected_parameter'],'filename*'); self.assertFalse(out['ok'])
    def test_invalid_extended_encoding(self):
        for value in ["UTF-8''%ZZ","UTF-8''%2","UTF-8''%FF","UTF-8''%C0%AF","UTF-8''%ED%A0%80","UTF-16''abc","UTF-8'abc","UTF-8''a*b",'"UTF-8\'\'a.txt"']:
            with self.assertRaises(tool.InputError): self.audit_header('attachment; filename*='+value)
    def test_invalid_header_syntax(self):
        for value in ['attachment; filename="unterminated','attachment; filename=x\r\nY: z','attachment; filename=two words','attachment; filename=é.txt','attachment; bad']:
            with self.assertRaises(tool.InputError): self.audit_header(value)
    def test_extension_risk_is_policy_finding(self):
        self.assertIn('potentially_executable_extension',tool.inspect_filename('setup.exe'))
    def test_escape_backslash(self):
        out=self.audit_header('attachment; filename="a\\\\b.txt"')
        self.assertIn('contains_path_separator',{v['code'] for v in out['findings']})
if __name__=='__main__': unittest.main()
