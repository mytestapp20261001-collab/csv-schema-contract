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
    import io, tarfile
    for name,member,expected in [("good.tar","hello.txt",0),("bad.tar","../escape.txt",1)]:
        with tarfile.open(p/name,"w") as f:
            info=tarfile.TarInfo(member);data=b"synthetic\n";info.size=len(data);f.addfile(info,io.BytesIO(data))
        run(expected,p/name)
