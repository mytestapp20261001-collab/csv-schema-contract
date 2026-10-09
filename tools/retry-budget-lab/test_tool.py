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

class RetryTests(unittest.TestCase):
    def test_server_minimum_is_not_capped(self):
        d=fixture(); d["retry_after"]="100"; d["deadline"]=d["now"]+200
        out=tool.audit(d); self.assertEqual(out["selected_wait_seconds"],100)
        self.assertTrue(out["ok"])
    def test_date_and_past_date(self):
        d=fixture(); d["retry_after"]="Mon, 01 Jan 2024 00:00:10 GMT"
        self.assertEqual(tool.audit(d)["server_minimum_wait_seconds"],10)
        d["retry_after"]="Sun, 31 Dec 2023 00:00:00 GMT"
        self.assertEqual(tool.audit(d)["server_minimum_wait_seconds"],0)
    def test_deadline_includes_attempt_duration(self):
        d=fixture(); d["deadline"]=d["now"]+9
        self.assertFalse(tool.audit(d)["ok"])
        d["deadline"]=d["now"]+10
        self.assertTrue(tool.audit(d)["ok"])
    def test_max_attempts_and_retry_safety(self):
        d=fixture(); d["completed_attempts"]=3; d["retry_safe"]=False
        self.assertEqual({x["code"] for x in tool.audit(d)["findings"]}, {"attempt_limit_reached","caller_has_not_established_retry_safety"})
    def test_backoff_cap(self):
        d=fixture(); d.pop("retry_after"); d["completed_attempts"]=50; d["max_attempts"]=100
        self.assertEqual(tool.audit(d)["selected_wait_seconds"],20)
    def test_invalid_retry_after(self):
        for value in ["-1", "1.5", "١", "1, 2", "soon", "9"*13, "Monday, 01-Jan-24 00:00:00 GMT"]:
            d=fixture(); d["retry_after"]=value
            with self.assertRaises(tool.InputError): tool.audit(d)
    def test_bool_and_limit_inputs(self):
        for key,value in [("now",True),("max_attempts",101),("completed_attempts",0),("base_delay_seconds",21),("retry_safe",1),("attempt_budget_seconds",0)]:
            d=fixture(); d[key]=value
            with self.assertRaises(tool.InputError): tool.audit(d)

if __name__ == "__main__": unittest.main()
