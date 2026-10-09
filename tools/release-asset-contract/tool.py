#!/usr/bin/env python3
"""Validate an explicit local release file set against a bounded JSON manifest."""
import argparse
import errno
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import unicodedata

TOOL = "release-asset-contract"
MANIFEST_LIMIT = 1048576


class InputError(ValueError):
    pass


class UnsafeAsset(ValueError):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise InputError("invalid command arguments")


def result(findings=None, summary=None, error=None):
    findings = findings or []
    return {"schema_version": 1, "tool": TOOL,
            "status": "error" if error else "findings" if findings else "pass",
            "summary": summary or {}, "findings": findings,
            "errors": [{"code": "bad_input", "message": error}] if error else []}


def selected_absolute(path):
    """Reject parent traversal before normalization can hide symlink components."""
    raw = Path(os.fspath(path))
    if ".." in raw.parts:
        raise InputError("Selected paths must not contain parent (..) components")
    return Path(os.path.abspath(raw))


def open_directory(path):
    if not hasattr(os, "O_NOFOLLOW") or os.open not in os.supports_dir_fd:
        raise InputError("This tool requires POSIX O_NOFOLLOW and dir_fd support")
    absolute = selected_absolute(path)
    fd = os.open(absolute.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in absolute.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def open_relative(root_fd, components):
    fd = os.dup(root_fd)
    try:
        for part in components[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        target = os.open(components[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        if not stat.S_ISREG(os.fstat(target).st_mode):
            os.close(target)
            raise UnsafeAsset("Target is not a regular file")
        return target
    finally:
        os.close(fd)


def reject_pairs(pairs):
    output = {}
    for key, value in pairs:
        if key in output:
            raise InputError("Manifest contains a duplicate JSON object key")
        output[key] = value
    return output


def reject_constant(value):
    raise InputError("Manifest contains a non-finite JSON number")


def parse_finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise InputError("Manifest contains a non-finite JSON number")
    return number


def read_manifest(path):
    absolute = selected_absolute(path)
    parent = open_directory(absolute.parent)
    fd = None
    try:
        fd = open_relative(parent, [absolute.name])
        before = os.fstat(fd)
        if before.st_size > MANIFEST_LIMIT:
            raise InputError("Manifest exceeds 1048576 bytes")
        chunks = []
        remaining = MANIFEST_LIMIT + 1
        while remaining:
            block = os.read(fd, min(65536, remaining))
            if not block:
                break
            chunks.append(block)
            remaining -= len(block)
        raw = b"".join(chunks)
        after = os.fstat(fd)
        if len(raw) > MANIFEST_LIMIT:
            raise InputError("Manifest exceeds 1048576 bytes")
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise InputError("Manifest changed during inspection")
        return json.loads(raw.decode("utf-8"), object_pairs_hook=reject_pairs,
                          parse_constant=reject_constant, parse_float=parse_finite_float)
    finally:
        if fd is not None:
            os.close(fd)
        os.close(parent)


def validate_manifest(document, max_files, max_asset_bytes, max_total_bytes):
    if not isinstance(document, dict) or set(document) != {"version", "files"}:
        raise InputError("Manifest must contain exactly version and files")
    if type(document["version"]) is not int or document["version"] != 1:
        raise InputError("Manifest version must be integer 1")
    files = document["files"]
    if not isinstance(files, list) or not 1 <= len(files) <= max_files:
        raise InputError("files must be a nonempty array within max_files")
    seen = set()
    total = 0
    for item in files:
        if not isinstance(item, dict) or set(item) != {"path", "size", "sha256"}:
            raise InputError("Each file must contain exactly path, size, and sha256")
        path = item["path"]
        if not isinstance(path, str) or not 1 <= len(path) <= 4096:
            raise InputError("Asset path must be a nonempty string of at most 4096 characters")
        if "\\" in path or ":" in path or any(unicodedata.category(c) == "Cc" or 0xD800 <= ord(c) <= 0xDFFF for c in path):
            raise InputError("Asset paths must be safe relative POSIX paths")
        if any(part in ("", ".", "..") for part in path.split("/")):
            raise InputError("Asset paths cannot be absolute, empty, or contain dot components")
        if path in seen:
            raise InputError("Manifest contains duplicate asset targets")
        seen.add(path)
        size = item["size"]
        if type(size) is not int or not 0 <= size <= max_asset_bytes:
            raise InputError("Asset size must be a nonnegative integer within max_asset_bytes")
        digest = item["sha256"]
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            raise InputError("sha256 must be exactly 64 hexadecimal characters")
        total += size
        if total > max_total_bytes:
            raise InputError("Declared asset bytes exceed max_total_bytes")
    # Ordering in output does not depend on JSON list order.
    return sorted(files, key=lambda item: item["path"])


def _audit(manifest, root, max_files, max_asset_bytes, max_total_bytes):
    for name, value, upper in (("max_files", max_files, 10000),
                               ("max_asset_bytes", max_asset_bytes, 1073741824),
                               ("max_total_bytes", max_total_bytes, 4294967296)):
        if type(value) is not int or not 1 <= value <= upper:
            raise InputError(f"{name} must be an integer from 1 to {upper}")
    files = validate_manifest(read_manifest(manifest), max_files, max_asset_bytes, max_total_bytes)
    root_fd = open_directory(root)
    findings = []
    hashed_bytes = 0
    checked = 0
    try:
        for item in files:
            path = item["path"]
            try:
                fd = open_relative(root_fd, path.split("/"))
            except FileNotFoundError:
                findings.append({"code": "missing_asset", "path": path})
                continue
            except UnsafeAsset:
                findings.append({"code": "unsafe_asset_type", "path": path})
                continue
            except OSError as exc:
                if exc.errno in (errno.ELOOP, errno.ENOTDIR):
                    findings.append({"code": "unsafe_asset_path", "path": path})
                    continue
                raise
            try:
                before = os.fstat(fd)
                if before.st_size > max_asset_bytes or hashed_bytes + before.st_size > max_total_bytes:
                    raise InputError("Actual asset bytes exceed configured read limits")
                if before.st_size != item["size"]:
                    findings.append({"code": "size_mismatch", "path": path,
                                     "expected": item["size"], "actual": before.st_size})
                digest = hashlib.sha256()
                count = 0
                while True:
                    # Reading one extra byte detects concurrent growth without unbounded I/O.
                    remaining = min(max_asset_bytes - count, max_total_bytes - hashed_bytes)
                    block = os.read(fd, min(65536, remaining + 1))
                    if not block:
                        break
                    count += len(block)
                    hashed_bytes += len(block)
                    if count > max_asset_bytes or hashed_bytes > max_total_bytes:
                        raise InputError("Asset grew beyond configured read limits")
                    digest.update(block)
                after = os.fstat(fd)
                if count != before.st_size or (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                    raise InputError("Asset changed during inspection")
                if digest.hexdigest() != item["sha256"].lower():
                    findings.append({"code": "sha256_mismatch", "path": path,
                                     "expected": item["sha256"].lower(), "actual": digest.hexdigest()})
                checked += 1
            finally:
                os.close(fd)
        return result(findings, {"required_assets": len(files), "checked_assets": checked,
                                "hashed_bytes": hashed_bytes, "extra_files_checked": False})
    finally:
        os.close(root_fd)


def audit(manifest, root, *, max_files=1000, max_asset_bytes=268435456, max_total_bytes=1073741824):
    """Return stable JSON data for an explicit manifest and confined local asset root."""
    try:
        return _audit(manifest, root, max_files, max_asset_bytes, max_total_bytes)
    except InputError as exc:
        return result(error=str(exc))
    except (OSError, UnsafeAsset, TypeError, ValueError, RecursionError):
        return result(error="Invalid manifest or selected input cannot be read safely")


def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument("manifest", help="Local UTF-8 JSON manifest")
    parser.add_argument("root", help="Explicitly selected directory containing release assets")
    parser.add_argument("--max-files", type=int, default=1000)
    parser.add_argument("--max-asset-bytes", type=int, default=268435456)
    parser.add_argument("--max-total-bytes", type=int, default=1073741824)
    try:
        args = parser.parse_args(argv)
        outcome = audit(args.manifest, args.root, max_files=args.max_files,
                        max_asset_bytes=args.max_asset_bytes, max_total_bytes=args.max_total_bytes)
    except InputError as exc:
        outcome = result(error=str(exc))
    print(json.dumps(outcome, sort_keys=True, ensure_ascii=True))
    return {"pass": 0, "findings": 1, "error": 2}[outcome["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
