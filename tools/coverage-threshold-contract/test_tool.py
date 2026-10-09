import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("local_tool", HERE / "tool.py")
tool = importlib.util.module_from_spec(spec); spec.loader.exec_module(tool)

class Tests(unittest.TestCase):
    def good(self):
        return json.loads((HERE / "examples/pass.json").read_text())
    def codes(self, data):
        return [item['code'] for item in tool.audit(data)['findings']]
    def test_pass(self):
        self.assertEqual(tool.audit(self.good())['status'], 'pass')
    def test_findings(self):
        self.assertEqual(tool.audit(json.loads((HERE / "examples/fail.json").read_text()))['status'], 'findings')
    def test_malformed_shape(self):
        with self.assertRaises(tool.BadInput): tool.audit([])
    def test_cli_examples(self):
        for name, expected in [('pass',0),('fail',1)]:
            result = subprocess.run([sys.executable, str(HERE/'tool.py'), str(HERE/f'examples/{name}.json')], capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stdout+result.stderr)
            self.assertEqual(json.loads(result.stdout)['schema_version'], 1)
    def test_cli_malformed(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'bad.json'
            for text in ['{', '{"x":1,"x":2}', '{"x":NaN}']:
                path.write_text(text)
                result = subprocess.run([sys.executable, str(HERE/'tool.py'), str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)['status'], 'error')
    def test_cli_bad_args(self):
        result = subprocess.run([sys.executable, str(HERE/'tool.py'), '--unknown'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2); self.assertEqual(json.loads(result.stdout)['status'], 'error')
    def test_size_limit(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'big.json'; path.write_text(' '* (tool.MAX_BYTES+1))
            with self.assertRaises(tool.BadInput): tool.load_json(path)

    def test_zero_is_not_pass(self):
        data = self.good(); data['files'][0]['line'] = {'covered':0,'total':0}
        self.assertIn('zero_denominator', self.codes(data))
    def test_missing_is_not_pass(self):
        data = self.good(); del data['files'][0]['branch']
        self.assertIn('missing_metric', self.codes(data))
    def test_below_threshold(self):
        data = self.good(); data['files'][0]['line']['covered'] = 7
        self.assertIn('below_threshold', self.codes(data))
    def test_threshold_boundary(self):
        data = self.good(); data['files'][0]['line']['covered'] = 8
        self.assertEqual(tool.audit(data)['status'], 'pass')
    def test_empty(self):
        data = self.good(); data['files'] = []
        self.assertIn('no_coverage_files', self.codes(data))
    def test_bad_counter(self):
        data = self.good(); data['files'][0]['line']['covered'] = True
        with self.assertRaises(tool.BadInput): tool.audit(data)
    def test_nan_threshold(self):
        data = self.good(); data['thresholds']['line'] = float('nan')
        with self.assertRaises(tool.BadInput): tool.audit(data)
    def test_duplicate_file(self):
        data = self.good(); data['files'] *= 2
        self.assertIn('duplicate_file', self.codes(data))

class ExactThresholdTests(unittest.TestCase):
    def check(self, token, covered, total, expected):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'input.json'
            path.write_text('{"thresholds":{"line":'+token+'},"files":[{"path":"x","line":{"covered":'+str(covered)+',"total":'+str(total)+'}}]}')
            p=subprocess.run([sys.executable,str(HERE/'tool.py'),str(path)],capture_output=True,text=True)
            self.assertEqual(p.returncode,expected,p.stdout+p.stderr)
            self.assertIsInstance(json.loads(p.stdout),dict)
    def test_exact_decimal_boundary(self): self.check('0.07',7,10000,0)
    def test_decimal_below(self): self.check('0.07',6,10000,1)
    def test_decimal_above(self): self.check('0.07',8,10000,0)
    def test_sub_float_precision(self): self.check('50.000000000000000000001',1,2,1)
    def test_tiny_positive_threshold(self): self.check('1e-400',0,1,1)
    def test_extreme_exponent_sanitized(self): self.check('1e999999999999999999999999999999',0,1,2)
    def test_exponent_budget(self): self.check('1e-1001',0,1,2)
    def test_decimal_token_budget(self): self.check('0.'+'1'*129,0,1,2)
    def test_float_api_shortest_decimal(self):
        self.assertEqual(tool.audit({'thresholds':{'line':0.07},'files':[{'path':'x','line':{'covered':7,'total':10000}}]})['status'],'pass')

if __name__ == "__main__": unittest.main()
