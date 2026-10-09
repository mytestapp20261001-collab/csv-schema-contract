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

class CorsTests(unittest.TestCase):
    def codes(self,d): return {x['code'] for x in tool.audit(d)['findings']}
    def test_good(self): self.assertTrue(tool.audit(fixture())['modeled_check_passed'])
    def test_duplicate_origin_not_collapsed(self):
        d=fixture(); d['response_headers'].append(['access-control-allow-origin','https://app.example'])
        self.assertIn('missing_or_duplicate_allow_origin',self.codes(d))
    def test_origin_byte_match(self):
        d=fixture(); d['response_headers'][0][1]='https://app.example/'
        self.assertIn('origin_not_allowed',self.codes(d))
    def test_noncredentialed_wildcard(self):
        d=fixture(); d['credentials']='omit'; d['response_headers']=[['Access-Control-Allow-Origin','*'],['Access-Control-Allow-Methods','*'],['Access-Control-Allow-Headers','*']]; d['unsafe_request_headers']=['X-Trace']
        self.assertTrue(tool.audit(d)['ok'])
    def test_authorization_never_covered_by_wildcard(self):
        d=fixture(); d['credentials']='omit'; d['response_headers'][-2][1]='*'
        self.assertIn('request_header_not_allowed',self.codes(d))
    def test_case_sensitive_method(self):
        d=fixture(); d['response_headers'][2][1]='put'
        self.assertIn('method_not_allowed',self.codes(d))
    def test_true_is_case_sensitive(self):
        d=fixture(); d['response_headers'][1][1]='True'
        self.assertIn('credentialed_response_requires_literal_true',self.codes(d))
    def test_list_fields_combine(self):
        d=fixture(); d['response_headers'][3][1]='Authorization'; d['response_headers'].append(['Access-Control-Allow-Headers','X-Trace'])
        self.assertTrue(tool.audit(d)['ok'])
    def test_invalid_list_syntax(self):
        d=fixture(); d['response_headers'][2][1]='"PUT"'
        self.assertIn('invalid_token_list',self.codes(d))
    def test_actual_response_does_not_require_preflight_lists(self):
        d=fixture(); d['preflight']=False; d['status']=500; d['response_headers']=d['response_headers'][:2]
        self.assertTrue(tool.audit(d)['ok'])
    def test_safelisted_method(self):
        d=fixture(); d['method']='POST'; d['response_headers'][2][1]='GET'
        self.assertTrue(tool.audit(d)['ok'])
    def test_null_is_literal_origin(self):
        d=fixture(); d['origin']='null'; d['response_headers'][0][1]='null'
        self.assertTrue(tool.audit(d)['ok'])
    def test_bad_origin(self):
        for v in ['https://app.example/','https://u:p@app.example','https://app.example:443','https://EXAMPLE.COM','file://local','https://a..b','https://a%2Eb','http://127.1','http://0x7f000001','http://0177.0.0.1']:
            d=fixture(); d['origin']=v
            with self.assertRaises(tool.InputError): tool.audit(d)
    def test_header_controls_and_secret_non_echo(self):
        d=fixture(); d['response_headers'].append(['Set-Cookie','s=PRIVATE_TOKEN'])
        self.assertNotIn('PRIVATE_TOKEN',json.dumps(tool.audit(d)))
        d['response_headers'][-1][1]+='\r\nextra'
        with self.assertRaises(tool.InputError): tool.audit(d)
if __name__=='__main__': unittest.main()
