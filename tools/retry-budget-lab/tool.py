#!/usr/bin/env python3
"""Bounded offline audit. No network access or external state changes."""
import argparse
import json
import math
import re
import sys
import stat
from pathlib import Path

MAX_BYTES = 262144
TOKEN = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+\Z")

class InputError(ValueError):
    pass

class Parser(argparse.ArgumentParser):
    def error(self, message):
        # argparse messages may contain raw options, paths, or caller secrets.
        raise InputError("invalid command-line arguments")

def require(condition, message):
    if not condition:
        raise InputError(message)

def schema(data, required, optional=()):
    require(isinstance(data, dict), "input must be an object")
    require(set(required) <= data.keys(), "missing required input field")
    require(data.keys() <= set(required) | set(optional), "unknown input field")

def integer(value, minimum=0, maximum=253402300799):
    require(type(value) is int and minimum <= value <= maximum, "integer outside supported range")
    return value

def string(value, limit=8192):
    require(isinstance(value, str) and len(value) <= limit, "string outside supported length")
    require(not any(0xD800 <= ord(c) <= 0xDFFF for c in value), "invalid Unicode scalar")
    return value

def header(value):
    string(value)
    require(not any(ord(c) < 32 and c != "\t" or ord(c) == 127 for c in value), "header contains control characters")
    return value

def result(findings, **fields):
    return {"schema_version": 1, "ok": not findings, "findings": findings, **fields}

def issue(code, **extra):
    return {"code": code, **extra}

def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, "duplicate JSON key")
        obj[key] = value
    return obj

def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument("--input", default="-", help="JSON file, or - for stdin (maximum 256 KiB)")
    parser.add_argument("--pretty", action="store_true", help="indent JSON output")
    args = None
    try:
        args = parser.parse_args(argv)
        if args.input == "-":
            raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        else:
            require(stat.S_ISREG(Path(args.input).stat().st_mode), "input path must be a regular file")
            with open(args.input, "rb") as stream:
                raw = stream.read(MAX_BYTES + 1)
        require(len(raw) <= MAX_BYTES, "input exceeds 256 KiB")
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(InputError("non-finite JSON number")))
        out = audit(data)
    except InputError as exc:
        out = {"schema_version": 1, "ok": False, "error": {"code": "invalid_input", "message": str(exc)}}
        code = 2
    except (OSError, UnicodeError, ValueError, RecursionError, OverflowError):
        out = {"schema_version": 1, "ok": False, "error": {"code": "invalid_input", "message": "unreadable, malformed, or excessively nested input"}}
        code = 2
    else:
        code = 0 if out["ok"] else 1
    print(json.dumps(out, sort_keys=True, ensure_ascii=True, allow_nan=False, indent=2 if args is not None and args.pretty else None))
    return code

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime, format_datetime

def http_date(raw):
    # Deliberately IMF-fixdate only, not an obsolete HTTP-date parser.
    header(raw)
    require(bool(re.fullmatch(r"[A-Z][a-z]{2}, [0-9]{2} [A-Z][a-z]{2} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2} GMT", raw)), "expected IMF-fixdate")
    try:
        parsed = parsedate_to_datetime(raw)
        require(format_datetime(parsed, usegmt=True) == raw, "invalid IMF-fixdate or weekday")
        return int(parsed.timestamp())
    except (ValueError, TypeError, OverflowError) as exc:
        raise InputError("invalid IMF-fixdate") from exc

def audit(data):
    schema(data, ("now", "deadline", "completed_attempts", "max_attempts", "base_delay_seconds", "cap_delay_seconds", "attempt_budget_seconds", "retry_safe"), ("retry_after",))
    now, deadline = integer(data["now"]), integer(data["deadline"])
    completed, maximum = integer(data["completed_attempts"], 1, 100), integer(data["max_attempts"], 1, 100)
    require(completed <= maximum, "completed_attempts exceeds max_attempts")
    base, cap = integer(data["base_delay_seconds"], 0, 86400), integer(data["cap_delay_seconds"], 0, 86400)
    require(base <= cap, "base delay exceeds cap")
    duration = integer(data["attempt_budget_seconds"], 1, 86400)
    require(type(data["retry_safe"]) is bool, "retry_safe must be boolean")
    server = 0; source = "absent"
    if "retry_after" in data:
        raw = header(data["retry_after"]).strip(" \t")
        if re.fullmatch(r"[0-9]+", raw):
            require(len(raw) <= 12, "Retry-After seconds outside supported range")
            server = int(raw); source = "delay-seconds"
        else:
            server = max(0, http_date(raw)-now); source = "IMF-fixdate"
    backoff = min(cap, base * 2**(completed-1))
    wait = max(backoff, server)
    next_start, finish = now + wait, now + wait + duration
    findings = []
    if not data["retry_safe"]:
        findings.append(issue("caller_has_not_established_retry_safety"))
    if completed >= maximum:
        findings.append(issue("attempt_limit_reached"))
    if finish > deadline:
        findings.append(issue("deadline_budget_exhausted"))
    return result(findings, eligible_under_supplied_policy=not findings, retry_after_source=source,
                  server_minimum_wait_seconds=server, deterministic_backoff_seconds=backoff,
                  selected_wait_seconds=wait, next_attempt_start=next_start,
                  next_attempt_reserved_finish=finish, deadline_slack_seconds=deadline-finish,
                  attempts_remaining=maximum-completed, requests_sent=0)

if __name__ == "__main__":
    raise SystemExit(main())
