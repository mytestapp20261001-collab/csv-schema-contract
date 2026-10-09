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

from urllib.parse import urlsplit
import ipaddress


def serialized_origin(raw):
    string(raw, 2048)
    if raw == 'null':
        return raw
    require(raw.isascii() and not any(c.isspace() for c in raw) and '\\' not in raw and '%' not in raw, 'origin must be an ASCII serialized HTTP(S) origin')
    try:
        u = urlsplit(raw)
        require(u.scheme in ('http','https') and u.hostname is not None and not u.username and not u.password,
                'origin must be an HTTP(S) origin without credentials')
        require(not u.path and not u.query and not u.fragment and '@' not in u.netloc, 'origin cannot contain path, query, fragment or userinfo')
        host = u.hostname
        if ':' in host:
            host = '[' + ipaddress.IPv6Address(host).compressed + ']'
        else:
            require(len(host) <= 253 and bool(re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', host)), 'unsupported origin host')
            last = host.rsplit('.',1)[-1]
            if last.isdigit() or last.lower().startswith('0x'):
                require(str(ipaddress.IPv4Address(host)) == host, 'numeric-looking origin host must be canonical IPv4')
            require(all(0 < len(label) <= 63 and not label.startswith('-') and not label.endswith('-') for label in host.split('.')), 'unsupported origin label')
        port = u.port
        expected = u.scheme + '://' + host + (':' + str(port) if port is not None and port != {'http':80,'https':443}[u.scheme] else '')
        require(raw == expected, 'origin must already be canonical, with no default port')
    except (ValueError,TypeError) as exc:
        raise InputError('invalid or unsupported serialized origin') from exc
    return raw


def audit(data):
    schema(data, ('origin','credentials','preflight','method','unsafe_request_headers','status','response_headers'))
    origin = serialized_origin(data['origin'])
    credentials = data['credentials']
    require(credentials in ('omit','same-origin','include'), 'invalid credentials mode')
    require(type(data['preflight']) is bool, 'preflight must be boolean')
    method = string(data['method'],128)
    require(bool(TOKEN.fullmatch(method)), 'method must be an HTTP token')
    status = integer(data['status'],100,599)
    unsafe = data['unsafe_request_headers']
    require(isinstance(unsafe,list) and len(unsafe) <= 100, 'unsafe_request_headers must be a list up to 100 names')
    for name in unsafe:
        require(bool(TOKEN.fullmatch(string(name,128))), 'invalid request header name')
    unsafe = sorted(set(name.lower() for name in unsafe))
    entries = data['response_headers']
    require(isinstance(entries,list) and len(entries) <= 100, 'response_headers must be up to 100 [name,value] pairs')
    headers = {}
    for entry in entries:
        require(isinstance(entry,list) and len(entry)==2, 'response header must be [name,value]')
        name, value = entry
        require(bool(TOKEN.fullmatch(string(name,128))), 'invalid response header name')
        headers.setdefault(name.lower(),[]).append(header(value).strip(' \t'))
    findings=[]
    ao=headers.get('access-control-allow-origin',[])
    ac=headers.get('access-control-allow-credentials',[])
    if len(ao) != 1:
        findings.append(issue('missing_or_duplicate_allow_origin'))
    elif ao[0] != origin and not (ao[0]=='*' and credentials != 'include'):
        findings.append(issue('origin_not_allowed'))
    if len(ac)>1:
        findings.append(issue('duplicate_allow_credentials'))
    if credentials=='include' and ac != ['true']:
        findings.append(issue('credentialed_response_requires_literal_true'))
    def tokens(name, lower=False):
        values = headers.get(name,[])
        if not values:
            return []
        values = [v.strip(' \t') for line in values for v in line.split(',')]
        if not all(TOKEN.fullmatch(v) for v in values):
            findings.append(issue('invalid_token_list', header=name))
            return []
        return [v.lower() for v in values] if lower else values
    if data['preflight']:
        if not 200 <= status <= 299:
            findings.append(issue('preflight_status_not_success'))
        methods = tokens('access-control-allow-methods')
        allowed = tokens('access-control-allow-headers',lower=True)
        if method not in ('GET','HEAD','POST') and method not in methods and not ('*' in methods and credentials!='include'):
            findings.append(issue('method_not_allowed'))
        for index,name in enumerate(unsafe):
            wildcard = '*' in allowed and credentials!='include' and name!='authorization'
            if name not in allowed and not wildcard:
                findings.append(issue('request_header_not_allowed', sorted_header_index=index,
                                      authorization_requires_explicit_match=name=='authorization'))
    vary = tokens('vary',lower=True)
    notes=[]
    if len(ao)==1 and ao[0]!='*' and 'origin' not in vary and '*' not in vary:
        notes.append('review_Vary_Origin_if_response_is_cacheable_and_origin_dependent')
    return result(findings, modeled_check_passed=not findings, preflight=data['preflight'],
                  distinct_unsafe_header_count=len(unsafe), notes=notes, network_requests=0)

if __name__ == '__main__':
    raise SystemExit(main())
