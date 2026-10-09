import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("release_asset_tool", HERE / "tool.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "assets"
        self.root.mkdir()
        self.manifest = self.base / "manifest.json"
        self.content = b"synthetic asset\n"
        (self.root / "demo.txt").write_bytes(self.content)
        self.document = {"version": 1, "files": [{"path": "demo.txt", "size": len(self.content),
                                                  "sha256": hashlib.sha256(self.content).hexdigest()}]}
        self.write_manifest()

    def write_manifest(self):
        self.manifest.write_text(json.dumps(self.document))

    def run_audit(self, **kwargs):
        return tool.audit(self.manifest, self.root, **kwargs)

    def test_pass_example(self):
        self.assertEqual(tool.audit(HERE / "examples/pass.json", HERE / "examples/assets")["status"], "pass")

    def test_findings_example(self):
        answer = tool.audit(HERE / "examples/fail.json", HERE / "examples/assets")
        self.assertEqual(answer["status"], "findings")
        self.assertEqual(answer["findings"][0]["code"], "sha256_mismatch")

    def test_missing_asset(self):
        (self.root / "demo.txt").unlink()
        self.assertEqual(self.run_audit()["findings"][0]["code"], "missing_asset")

    def test_size_and_sha_findings(self):
        (self.root / "demo.txt").write_bytes(b"different")
        self.assertEqual([f["code"] for f in self.run_audit()["findings"]], ["size_mismatch", "sha256_mismatch"])

    def test_extra_files_not_checked(self):
        (self.root / "extra").write_bytes(b"unlisted")
        answer = self.run_audit()
        self.assertEqual(answer["status"], "pass")
        self.assertFalse(answer["summary"]["extra_files_checked"])

    def test_duplicate_targets(self):
        self.document["files"].append(dict(self.document["files"][0]))
        self.write_manifest()
        self.assertEqual(self.run_audit()["status"], "error")

    def test_malformed_duplicate_key_and_nonfinite_json(self):
        for raw in ('{', '{"version":1,"version":1,"files":[]}',
                    '{"version":NaN,"files":[]}', '{"version":Infinity,"files":[]}',
                    '{"version":1e999,"files":[]}', '{"version":true,"files":[]}'):
            with self.subTest(raw=raw):
                self.manifest.write_text(raw)
                self.assertEqual(self.run_audit()["status"], "error")

    def test_overflow_float_rejected_during_decode(self):
        self.manifest.write_text('{"version":1,"files":[],"extra":1e999}')
        with self.assertRaises(tool.InputError):
            tool.read_manifest(self.manifest)

    def test_duplicate_nested_key(self):
        self.manifest.write_text('{"version":1,"files":[{"path":"a","path":"b","size":0,"sha256":"'+'0'*64+'"}]}')
        self.assertEqual(self.run_audit()["status"], "error")

    def test_unsafe_paths(self):
        for path in ("../outside", "/outside", "a/../b", "./demo.txt", "a//b", "C:/a", "a\\b", "a\x00b", "a\ud800b", ""):
            with self.subTest(path=path):
                self.document["files"][0]["path"] = path
                self.write_manifest()
                self.assertEqual(self.run_audit()["status"], "error")

    def test_leaf_symlink(self):
        (self.root / "demo.txt").unlink()
        (self.root / "demo.txt").symlink_to(self.manifest)
        self.assertEqual(self.run_audit()["findings"][0]["code"], "unsafe_asset_path")

    def test_directory_symlink_and_root_symlink(self):
        (self.root / "link").symlink_to(self.base, target_is_directory=True)
        self.document["files"][0]["path"] = "link/manifest.json"
        self.write_manifest()
        self.assertEqual(self.run_audit()["findings"][0]["code"], "unsafe_asset_path")
        link = self.base / "rootlink"
        link.symlink_to(self.root, target_is_directory=True)
        self.assertEqual(tool.audit(self.manifest, link)["status"], "error")

    def test_fifo_does_not_block(self):
        (self.root / "demo.txt").unlink()
        os.mkfifo(self.root / "demo.txt")
        self.assertEqual(self.run_audit()["findings"][0]["code"], "unsafe_asset_type")

    def test_read_boundaries(self):
        size = len(self.content)
        self.assertEqual(self.run_audit(max_asset_bytes=size, max_total_bytes=size)["status"], "pass")
        self.assertEqual(self.run_audit(max_asset_bytes=size-1)["status"], "error")
        self.assertEqual(self.run_audit(max_total_bytes=size-1)["status"], "error")
        self.document["files"][0]["size"] = 1
        self.write_manifest()
        self.assertEqual(self.run_audit(max_asset_bytes=1)["status"], "error")

    def test_zero_length_file(self):
        (self.root / "demo.txt").write_bytes(b"")
        self.document["files"][0].update(size=0, sha256=hashlib.sha256(b"").hexdigest())
        self.write_manifest()
        self.assertEqual(self.run_audit()["status"], "pass")

    def test_manifest_size_boundary(self):
        raw = self.manifest.read_bytes()
        self.manifest.write_bytes(raw + b" " * (tool.MANIFEST_LIMIT - len(raw)))
        self.assertEqual(self.run_audit()["status"], "pass")
        with self.manifest.open("ab") as stream:
            stream.write(b" ")
        self.assertEqual(self.run_audit()["status"], "error")

    def test_bad_fields_and_limits(self):
        for key, value in (("size", True), ("size", -1), ("sha256", "invalid"), ("sha256", None)):
            original = self.document["files"][0][key]
            self.document["files"][0][key] = value
            self.write_manifest()
            self.assertEqual(self.run_audit()["status"], "error")
            self.document["files"][0][key] = original
        self.write_manifest()
        for kwargs in ({"max_files": 0}, {"max_total_bytes": True}, {"max_asset_bytes": -1}):
            self.assertEqual(self.run_audit(**kwargs)["status"], "error")

    def test_cli_statuses(self):
        for args, expected in (([str(HERE / "examples/pass.json"), str(HERE / "examples/assets")], 0),
                               ([str(HERE / "examples/fail.json"), str(HERE / "examples/assets")], 1),
                               ([str(HERE / "examples/malformed.json"), str(HERE / "examples/assets")], 2),
                               ([str(self.manifest), str(self.root), "--max-files", "bad"], 2), ([], 2)):
            with self.subTest(args=args):
                p = subprocess.run([sys.executable, "-I", str(HERE / "tool.py"), *args], capture_output=True, text=True)
                self.assertEqual(p.returncode, expected, p.stderr)
                self.assertEqual(json.loads(p.stdout)["schema_version"], 1)
                self.assertEqual(p.stderr, "")

    def test_cli_argument_errors_do_not_echo_input(self):
        secret = "PRIVATE_ARGUMENT_VALUE"
        process = subprocess.run([sys.executable, "-I", str(HERE / "tool.py"),
                                  "--unknown=" + secret], capture_output=True, text=True)
        self.assertEqual(process.returncode, 2)
        self.assertNotIn(secret, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout)["errors"][0]["message"], "invalid command arguments")


if __name__ == "__main__":
    unittest.main()
