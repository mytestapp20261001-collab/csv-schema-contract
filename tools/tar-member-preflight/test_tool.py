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

    def create_tar(self, members):
        import io, tarfile
        p=self.root/'a.tar'
        with tarfile.open(p,'w') as f:
            for name,kind,target,data in members:
                i=tarfile.TarInfo(name);i.type=kind;i.linkname=target;i.size=len(data)
                f.addfile(i,io.BytesIO(data))
        return p
    def test_regular_and_cli(self):
        p=self.create_tar([('a.txt',b'0','',b'hello')]);r=tool.audit(p)
        self.assertEqual(r['status'],'pass');self.assertEqual(r['summary']['declared_bytes'],5)
        self.assertEqual(self.call(p)[0],0)
    def test_links_traversal_special_and_duplicates(self):
        p=self.create_tar([('../escape',b'0','',b''),('link',b'2','../../outside',b''),('link/x',b'0','',b''),('same',b'0','',b''),('same',b'0','',b''),('fifo',b'6','',b'')])
        codes=self.codes(tool.audit(p));self.assertTrue({'unsafe_member_path','link_member','link_target_outside_archive','member_beneath_link','duplicate_destination','special_member'}<=codes)
        self.assertEqual(self.call(p)[0],1)
    def test_budget_and_truncation(self):
        p=self.create_tar([('a',b'0','',b'xx'),('b',b'0','',b'yy')])
        self.assertIn('member_size_budget_exceeded',self.codes(tool.audit(p,max_member_bytes=1)))
        r=tool.audit(p,max_members=1);self.assertFalse(r['summary']['complete'])
        r=tool.audit(p,max_total_bytes=1);self.assertIn('total_size_budget_exceeded',self.codes(r))
        self.assertEqual(tool.audit(p,max_stream_bytes=100)['status'],'error')
        self.assertEqual(tool.audit(p,max_input_bytes=1)['status'],'error')
    def test_gzip_and_malformed(self):
        import gzip
        p=self.create_tar([('x',b'0','',b'a'*10000)]);q=self.root/'a.tar.gz';q.write_bytes(gzip.compress(p.read_bytes(),mtime=0))
        self.assertEqual(tool.audit(q)['status'],'pass')
        self.assertEqual(tool.audit(q,max_stream_bytes=4096)['status'],'error')
        q.write_bytes(b'not tar');self.assertEqual(tool.audit(q)['status'],'error')
    def test_input_symlink_and_permissions(self):
        p=self.create_tar([]);q=self.root/'link';q.symlink_to(p)
        self.assertEqual(tool.audit(q)['status'],'error')
        with mock.patch.object(tool,'read_file',side_effect=PermissionError):self.assertEqual(tool.audit(p)['status'],'error')
    def test_windows_paths_and_internal_link(self):
        p=self.create_tar([('C:/escape',b'0','',b''),('a\\b',b'0','',b''),('safe',b'2','inside',b'')])
        r=tool.audit(p);self.assertIn('unsafe_member_path',self.codes(r));self.assertNotIn('link_target_outside_archive',self.codes(r))

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

    def test_malformed_gzip_returns_json_error(self):
        p=self.root/'bad.gz';p.write_bytes(b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\xff'+b'\xff'*30)
        self.assertEqual(tool.audit(p)['status'],'error');self.assertEqual(self.call(p)[0],2)

if __name__=="__main__":unittest.main()
