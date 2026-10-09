"""Synthetic examples; all fixtures live in an automatically removed temporary directory."""
from pathlib import Path
import json, subprocess, sys, tempfile
TOOL=Path(__file__).resolve().parents[1]/"tool.py"
def run(expected,*args):
    r=subprocess.run([sys.executable,str(TOOL),*map(str,args)],capture_output=True,text=True)
    assert r.returncode==expected,(r.returncode,r.stdout,r.stderr)
    print(r.stdout.strip())
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)
    a=p/"a";b=p/"b";a.mkdir();b.mkdir()
    (a/"file.txt").write_text("synthetic\n");(b/"file.txt").write_text("synthetic\n")
    run(0,a,"--compare",b);(b/"file.txt").write_text("changed synthetic\n");run(1,a,"--compare",b)
