#!/usr/bin/env python3
"""Inspect TAR member metadata and budgets without extraction."""
import gzip
import io
import ntpath
import posixpath
import tarfile
import zlib
from _support import InputError, Parser, Report, cli, guarded, limits, positive, read_file
TOOL = "tar-member-preflight"

class BoundedStream:
    def __init__(self, source, limit):
        self.source, self.limit, self.count = source, limit, 0
    def read(self, size=-1):
        remaining = self.limit - self.count
        request = remaining + 1 if size < 0 else min(size, remaining + 1)
        data = self.source.read(request)
        self.count += len(data)
        if self.count > self.limit:
            raise InputError("expanded TAR stream byte limit exceeded")
        return data

def unsafe_path(name):
    return (not name or "\\" in name or name.startswith("/") or bool(ntpath.splitdrive(name)[0])
            or ".." in name.split("/") or "\x00" in name)

@guarded(TOOL)
def audit(path, *, max_members=10000, max_member_bytes=67108864, max_total_bytes=268435456,
          max_input_bytes=67108864, max_stream_bytes=134217728, max_findings=1000):
    limits(max_members=max_members, max_member_bytes=max_member_bytes, max_total_bytes=max_total_bytes,
           max_input_bytes=max_input_bytes, max_stream_bytes=max_stream_bytes, max_findings=max_findings)
    data = read_file(path, max_input_bytes)
    if data.startswith((b"BZh", b"\xfd7zXZ")):
        raise InputError("only plain TAR and gzip-compressed TAR are supported")
    raw = io.BytesIO(data)
    source = gzip.GzipFile(fileobj=raw) if data.startswith(b"\x1f\x8b") else raw
    bounded = BoundedStream(source, max_stream_bytes)
    report = Report(TOOL, max_findings)
    seen, links, members = set(), set(), []
    total = 0
    complete = True
    try:
        with tarfile.open(fileobj=bounded, mode="r|") as archive:
            for index, member in enumerate(archive, 1):
                if index > max_members:
                    report.add("member_budget_exceeded")
                    complete = False
                    break
                name = member.name
                normalized = posixpath.normpath(name)
                members.append((index, normalized))
                if len(name) > 4096 or len(member.linkname) > 4096:
                    report.add("metadata_path_too_long", member=index)
                if unsafe_path(name) or normalized == ".":
                    report.add("unsafe_member_path", member=index)
                if normalized in seen:
                    report.add("duplicate_destination", member=index)
                seen.add(normalized)
                if member.size < 0:
                    raise InputError("negative member size")
                total += member.size
                if member.size > max_member_bytes:
                    report.add("member_size_budget_exceeded", member=index, declared_bytes=member.size)
                if total > max_total_bytes:
                    report.add("total_size_budget_exceeded", declared_bytes=total)
                    complete = False
                    break
                if member.issym() or member.islnk():
                    links.add(normalized)
                    report.add("link_member", member=index, kind="symlink" if member.issym() else "hardlink")
                    target = member.linkname
                    target_path = posixpath.normpath(posixpath.join(posixpath.dirname(normalized), target) if member.issym() else target)
                    if (not target or "\\" in target or target.startswith("/") or ntpath.splitdrive(target)[0]
                        or target_path == ".." or target_path.startswith("../")):
                        report.add("link_target_outside_archive", member=index)
                elif not (member.isfile() or member.isdir()):
                    report.add("special_member", member=index)
                if member.sparse is not None:
                    report.add("sparse_member", member=index)
                if member.mode & 0o6000:
                    report.add("privileged_mode_bits", member=index)
                # Python 3.12 retains member metadata; keep it bounded by max_members.
        for index, name in members:
            parts = name.split("/")
            if any("/".join(parts[:i]) in links for i in range(1, len(parts))):
                report.add("member_beneath_link", member=index)
    except (tarfile.TarError, EOFError, gzip.BadGzipFile, zlib.error):
        raise InputError("malformed or unsupported TAR stream") from None
    finally:
        source.close()
    return report.finish({"members_scanned":len(members), "declared_bytes":total,
                          "expanded_bytes_read":bounded.count,"complete":complete})

def parse_and_audit():
    p = Parser(description=__doc__)
    p.add_argument("archive")
    for name, default in [("max-members",10000),("max-member-bytes",67108864),("max-total-bytes",268435456),
                          ("max-input-bytes",67108864),("max-stream-bytes",134217728),("max-findings",1000)]:
        p.add_argument("--"+name, type=positive, default=default)
    args = vars(p.parse_args()); path = args.pop("archive")
    return audit(path, **args)
if __name__ == "__main__":
    raise SystemExit(cli(TOOL, parse_and_audit))
