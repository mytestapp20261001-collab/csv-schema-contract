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

class CookieTests(unittest.TestCase):
    def test_host_only_and_no_secret_echo(self):
        d=fixture(); d['set_cookie']=d['set_cookie'].replace('synthetic','PRIVATE_TOKEN')
        out=tool.audit(d); self.assertTrue(out['host_only']); self.assertTrue(out['ok'])
        self.assertNotIn('PRIVATE_TOKEN',json.dumps(out))
    def test_host_only_excludes_subdomain(self):
        d=fixture(); d['request_url']='https://child.app.example/account'
        self.assertFalse(tool.audit(d)['conditions']['request_domain'])
    def test_domain_match_requires_dot(self):
        d=fixture(); d['set_cookie']='s=x; Domain=example; Path=/'
        d['request_url']='https://notexample/account'
        self.assertFalse(tool.audit(d)['conditions']['request_domain'])
        self.assertIn('public_suffix_list',tool.audit(d)['unresolved_checks'])
    def test_leading_domain_dot(self):
        d=fixture(); d['set_cookie']='s=x; Domain=.app.example; Path=/'
        d['request_url']='https://child.app.example/account'
        self.assertTrue(tool.audit(d)['conditions']['request_domain'])
    def test_path_segment_boundary(self):
        self.assertFalse(tool.path_match('/administer','/admin'))
        self.assertTrue(tool.path_match('/admin/x','/admin'))
        self.assertTrue(tool.path_match('/admin','/admin'))
    def test_default_path(self):
        d=fixture(); d['set_cookie']='s=x'; d['response_url']='https://app.example/a/b'; d['request_url']='https://app.example/a/c'
        self.assertTrue(tool.audit(d)['conditions']['request_path'])
    def test_lax_navigation_and_strict(self):
        d=fixture(); d['same_site']=False
        self.assertFalse(tool.audit(d)['conditions']['samesite_context'])
        d['top_level_navigation']=True
        self.assertTrue(tool.audit(d)['conditions']['samesite_context'])
        d['set_cookie']=d['set_cookie'].replace('Lax','Strict')
        self.assertFalse(tool.audit(d)['conditions']['samesite_context'])
    def test_none_needs_secure(self):
        d=fixture(); d['set_cookie']='s=x; SameSite=None'
        self.assertFalse(tool.audit(d)['ok'])
    def test_secure_transport(self):
        d=fixture(); d['request_url']='http://app.example/account'
        self.assertFalse(tool.audit(d)['conditions']['secure_transport'])
    def test_prefix_case_insensitive_profile(self):
        d=fixture(); d['set_cookie']='__hOsT-a=x; Secure'
        self.assertFalse(tool.audit(d)['conditions']['prefix'])
    def test_duplicate_path_last_used(self):
        d=fixture(); d['set_cookie']='s=x; Path=/wrong; Path=/'
        out=tool.audit(d); self.assertFalse(out['ok']); self.assertTrue(out['conditions']['request_path'])
    def test_deletion(self):
        d=fixture(); d['set_cookie']='s=x; Max-Age=0'
        self.assertFalse(tool.audit(d)['modeled_conditions_match'])
    def test_ports_do_not_scope_cookies(self):
        d=fixture(); d['request_url']='https://app.example:444/account'
        self.assertTrue(tool.audit(d)['ok'])
    def test_ip_not_suffix_domain(self):
        self.assertFalse(tool.domain_match('127.0.0.1','0.0.1'))
    def test_invalid_inputs(self):
        for key,value in [('set_cookie','s=a, b=c'),('set_cookie','s=\r\nx'),('set_cookie','s="a;b"'),('same_site',1),('response_url','https://u:p@app.example'),('set_cookie','s=x; =bad')]:
            d=fixture(); d[key]=value
            with self.assertRaises(tool.InputError): tool.audit(d)

    def test_equivalent_ipv6_host_text_matches_and_cli_passes(self):
        d=fixture(); d['set_cookie']='sid=synthetic; Secure; Path=/; SameSite=Strict'
        d['response_url']='https://[2001:0db8::1]/'
        d['request_url']='https://[2001:db8::1]/'
        out=tool.audit(d)
        self.assertTrue(out['conditions']['request_domain']); self.assertTrue(out['ok'])
        run=subprocess.run([sys.executable,str(ROOT/'tool.py')],input=json.dumps(d),capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertTrue(json.loads(run.stdout)['conditions']['request_domain'])
        d['response_url']='https://[2001:0DB8:0000:0000:0000:0000:0000:0001]/'
        self.assertTrue(tool.audit(d)['ok'])
    def test_different_ipv6_addresses_do_not_match(self):
        d=fixture(); d['response_url']='https://[2001:db8::1]/'
        d['request_url']='https://[2001:db8::2]/'
        out=tool.audit(d)
        self.assertFalse(out['conditions']['request_domain']); self.assertFalse(out['ok'])
    def test_ipv4_host_identity_and_domain_suffix_boundary(self):
        d=fixture(); d['response_url']='https://192.0.2.1/'
        d['request_url']='https://192.0.2.1:444/'
        self.assertTrue(tool.audit(d)['ok'])
        d['request_url']='https://192.0.2.2/'
        self.assertFalse(tool.audit(d)['conditions']['request_domain'])
        self.assertFalse(tool.domain_match('192.0.2.1','0.2.1'))
    def test_mapped_ipv6_spellings_match_but_do_not_become_ipv4(self):
        d=fixture(); d['response_url']='https://[::ffff:192.0.2.1]/'
        d['request_url']='https://[0:0:0:0:0:ffff:c000:201]/'
        self.assertTrue(tool.audit(d)['ok'])
        d['request_url']='https://192.0.2.1/'
        self.assertFalse(tool.audit(d)['conditions']['request_domain'])
    def test_dns_case_and_host_only_boundary_unchanged(self):
        d=fixture(); d['response_url']='https://APP.EXAMPLE/'
        d['request_url']='https://app.example/'
        self.assertTrue(tool.audit(d)['ok'])
        for host in ['child.app.example','notapp.example','app.example.other']:
            d['request_url']='https://'+host+'/'
            self.assertFalse(tool.audit(d)['conditions']['request_domain'])
if __name__=='__main__': unittest.main()
