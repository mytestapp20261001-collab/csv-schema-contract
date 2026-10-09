import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).parent))
spec=importlib.util.spec_from_file_location("audit_tool",Path(__file__).with_name("tool.py"))
tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)
class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def codes(self,result):return {x["code"] for x in result.get("findings",[])}
    def call(self,*args):
        result=subprocess.run([sys.executable,str(Path(__file__).with_name("tool.py")),*map(str,args)],capture_output=True,text=True)
        return result.returncode,json.loads(result.stdout)
    def test_bad_cli(self):
        code,result=self.call("--unknown");self.assertEqual(code,2);self.assertEqual(result["status"],"error")
    def test_examples(self):
        result=subprocess.run([sys.executable,str(Path(__file__).parent/"examples"/"run_examples.py")],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        reports=[json.loads(x) for x in result.stdout.splitlines()]
        self.assertEqual([r["status"] for r in reports],["pass","findings"])

    def test_deterministic_and_cli(self):
        (self.root/'a').write_bytes(b'x');r=tool.audit(self.root);self.assertEqual(r,tool.audit(self.root));self.assertEqual(self.call(self.root)[0],0)
        self.assertEqual(r['manifest'][0]['bytes'],1);self.assertNotIn('mtime',str(r))
    def test_diff_changes(self):
        a=self.root/'a';b=self.root/'b';a.mkdir();b.mkdir()
        (a/'same').write_text('one');(b/'same').write_text('two');(a/'gone').touch();(b/'new').touch()
        r=tool.audit(a,compare=b);self.assertEqual(self.codes(r),{'changed','added','removed'});self.assertEqual(self.call(a,'--compare',b)[0],1)
    def test_symlink_target_not_read(self):
        scan=self.root/'scan';scan.mkdir();outside=self.root/'outside';outside.write_text('secret value')
        (scan/'link').symlink_to(outside);r=tool.audit(scan);self.assertEqual(r['manifest'][0]['type'],'symlink');self.assertNotIn('secret',json.dumps(r));self.assertNotIn(str(outside),json.dumps(r))
        outside.write_text('changed');self.assertEqual(r,tool.audit(scan))
    def test_empty_dirs_and_type_change(self):
        a=self.root/'a';b=self.root/'b';a.mkdir();b.mkdir();(a/'entry').mkdir();(b/'entry').touch()
        self.assertIn('type_changed',self.codes(tool.audit(a,compare=b)))
    def test_limits_and_permissions(self):
        (self.root/'a').write_text('xxx');self.assertEqual(tool.audit(self.root,max_file_bytes=1)['status'],'error');self.assertEqual(tool.audit(self.root,max_total_bytes=1)['status'],'error')
        with mock.patch.object(tool,'read_at',side_effect=PermissionError):self.assertEqual(tool.audit(self.root)['status'],'error')
    def test_special_and_ancestor_link(self):
        os.mkfifo(self.root/'fifo');self.assertEqual(tool.audit(self.root)['status'],'error')
        (self.root/'fifo').unlink();(self.root/'d').mkdir();(self.root/'alias').symlink_to(self.root/'d');self.assertEqual(tool.audit(self.root/'alias')['status'],'error')

    def test_support_rejects_symlink_before_dotdot(self):
        import _support
        (self.root/'actual').mkdir();(self.root/'alias').symlink_to('actual');(self.root/'safe').write_bytes(b'x')
        with self.assertRaises((OSError,_support.InputError)):
            with _support.anchored(str(self.root)+'/alias/../safe'):
                self.fail('must not normalize away a symlink component')
    def test_support_detects_pre_read_mutation(self):
        import _support
        p=self.root/'changed';p.write_bytes(b'a');before=p.stat();p.write_bytes(b'longer')
        with _support.anchored(self.root,True) as fd:
            with self.assertRaises(_support.InputError):_support.read_at(fd,'changed',before,100)
    def test_support_entry_budget_and_host_guard(self):
        import _support
        (self.root/'a').mkdir();(self.root/'a'/'x').touch();(self.root/'b').touch()
        with _support.anchored(self.root,True) as fd:
            with self.assertRaises(_support.InputError):list(_support.walk(fd,max_entries=2))
        with mock.patch.object(_support.os,'name','unsupported'):
            with self.assertRaises(_support.InputError):_support._flags()

if __name__=="__main__":unittest.main()
