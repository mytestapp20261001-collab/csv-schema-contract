#!/usr/bin/env python3
"""Make deterministic SHA-256 tree manifests or compare two live trees."""
import hashlib
import json
import os
import stat
from _support import InputError, Parser, Report, anchored, cli, guarded, limits, positive, read_at, walk
TOOL="directory-manifest-diff"

def manifest(root, max_entries, max_depth, max_file_bytes, max_total_bytes):
    records=[];total=0
    with anchored(root,True) as fd:
        for rel,st,parent,name in walk(fd,max_entries,max_depth):
            record={"path":rel}
            if stat.S_ISREG(st.st_mode):
                if total+st.st_size>max_total_bytes:raise InputError("total content byte limit exceeded")
                data=read_at(parent,name,st,min(max_file_bytes,max_total_bytes-total));total+=len(data)
                record.update(type="file",bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
            elif stat.S_ISLNK(st.st_mode):
                target=os.readlink(name,dir_fd=parent)
                record.update(type="symlink",target_sha256=hashlib.sha256(os.fsencode(target)).hexdigest())
            elif stat.S_ISDIR(st.st_mode):record.update(type="directory")
            else:raise InputError("special filesystem entries are unsupported")
            records.append(record)
    records.sort(key=lambda r:r["path"])
    digest=hashlib.sha256(json.dumps(records,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
    return records,digest,total

@guarded(TOOL)
def audit(root, *, compare=None, max_entries=100000, max_depth=64,max_file_bytes=16777216,
          max_total_bytes=268435456,max_findings=1000):
    limits(max_entries=max_entries,max_depth=max_depth,max_file_bytes=max_file_bytes,max_total_bytes=max_total_bytes,max_findings=max_findings)
    report=Report(TOOL,max_findings)
    args=(max_entries,max_depth,max_file_bytes,max_total_bytes)
    first,digest,total=manifest(root,*args)
    summary={"entries":len(first),"content_bytes":total,"manifest_sha256":digest}
    if compare is None:return report.finish(summary,manifest=first)
    second,other_digest,other_total=manifest(compare,*args)
    left={r["path"]:r for r in first};right={r["path"]:r for r in second}
    for path in sorted(left.keys()|right.keys()):
        if path not in left:report.add("added",path=path)
        elif path not in right:report.add("removed",path=path)
        elif left[path]!=right[path]:report.add("type_changed" if left[path]["type"]!=right[path]["type"] else "changed",path=path)
    summary.update(compared_entries=len(second),compared_content_bytes=other_total,compared_manifest_sha256=other_digest)
    return report.finish(summary)

def parse_and_audit():
    p=Parser(description=__doc__);p.add_argument("root");p.add_argument("--compare")
    for name,default in [("max-entries",100000),("max-depth",64),("max-file-bytes",16777216),("max-total-bytes",268435456),("max-findings",1000)]:
        p.add_argument("--"+name,type=positive,default=default)
    a=vars(p.parse_args());root=a.pop("root");return audit(root,**a)
if __name__=="__main__":raise SystemExit(cli(TOOL,parse_and_audit))
