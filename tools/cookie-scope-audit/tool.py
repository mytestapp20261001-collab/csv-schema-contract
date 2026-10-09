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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="-", help="JSON file, or - for stdin (maximum 256 KiB)")
    parser.add_argument("--pretty", action="store_true", help="indent JSON output")
    args = parser.parse_args(argv)
    try:
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
    print(json.dumps(out, sort_keys=True, ensure_ascii=True, allow_nan=False, indent=2 if args.pretty else None))
    return code

from urllib.parse import urlsplit
import ipaddress


def endpoint(raw):
    string(raw,8192)
    require(raw.isascii() and not any(c.isspace() or ord(c)<32 for c in raw) and '\\' not in raw, 'URL must use the strict ASCII HTTP(S) subset')
    try:
        u=urlsplit(raw)
        require(u.scheme in ('http','https') and u.hostname and '@' not in u.netloc, 'URL must have HTTP(S) host and no credentials')
        host=u.hostname
        _=u.port
        require('%' not in host, 'encoded or scoped host unsupported')
        # Compare IP literals by address identity, independent of textual IPv6 compression.
        try: host=str(ipaddress.ip_address(host))
        except ValueError:
            require(len(host)<=253 and all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label) for label in host.split('.')), 'unsupported DNS host')
        return u.scheme,host,u.path or '/'
    except (ValueError,TypeError) as exc:
        raise InputError('invalid URL endpoint') from exc


def domain_match(host, domain):
    if host==domain: return True
    try: ipaddress.ip_address(host)
    except ValueError: return host.endswith('.'+domain)
    return False


def path_match(request, cookie):
    return request==cookie or request.startswith(cookie) and (cookie.endswith('/') or request[len(cookie):].startswith('/'))


def audit(data):
    schema(data,('set_cookie','response_url','request_url','same_site','top_level_navigation','safe_method'))
    for name in ('same_site','top_level_navigation','safe_method'):
        require(type(data[name]) is bool, 'request context values must be boolean')
    source_scheme,source_host,source_path=endpoint(data['response_url'])
    target_scheme,target_host,target_path=endpoint(data['request_url'])
    raw=header(data['set_cookie'])
    require(raw.isascii(), 'Set-Cookie must use ASCII in this subset')
    chunks=raw.split(';')
    name,sep,value=chunks[0].strip(' \t').partition('=')
    require(bool(sep) and bool(TOKEN.fullmatch(name)), 'invalid cookie name/value pair')
    value=value.strip(' \t')
    if value.startswith('"'):
        require(len(value)>=2 and value.endswith('"'), 'invalid quoted cookie value')
        value=value[1:-1]
    require(bool(re.fullmatch(r'[\x21\x23-\x2b\x2d-\x3a\x3c-\x5b\x5d-\x7e]*',value)), 'invalid cookie-octet value; combined Set-Cookie fields unsupported')
    attrs={}; findings=[]
    require(len(chunks)<=65,'too many cookie attributes')
    for chunk in chunks[1:]:
        key,eq,val=chunk.strip(' \t').partition('=')
        require(bool(TOKEN.fullmatch(key)),'invalid cookie attribute')
        key=key.lower(); val=val.strip(' \t') if eq else None
        if key in attrs: findings.append(issue('duplicate_attribute',attribute=key))
        attrs[key]=val
    secure='secure' in attrs
    for flag in ('secure','httponly'):
        if flag in attrs and attrs[flag] is not None:
            findings.append(issue('flag_has_value',attribute=flag))
    domain=source_host
    host_only='domain' not in attrs
    source_domain=True
    if not host_only:
        domain=attrs['domain'] or ''
        domain=domain[1:] if domain.startswith('.') else domain
        domain=domain.lower()
        valid=bool(domain) and len(domain)<=253 and all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',label) for label in domain.split('.'))
        if not valid:
            findings.append(issue('unsupported_or_invalid_domain_attribute'))
        source_domain=valid and domain_match(source_host,domain)
        if not source_domain: findings.append(issue('domain_not_valid_for_setting_host'))
    default_path=source_path.rsplit('/',1)[0] if source_path.count('/')>1 else '/'
    path=attrs.get('path')
    path_fallback=not isinstance(path,str) or not path.startswith('/')
    if path_fallback: path=default_path
    if 'path' in attrs and path_fallback: findings.append(issue('path_attribute_uses_default_path'))
    target_domain=target_host==source_host if host_only else domain_match(target_host,domain)
    target_path=path_match(target_path,path)
    secure_context=not secure or source_scheme=='https' and target_scheme=='https'
    samesite=(attrs.get('samesite') or 'lax').lower()
    if samesite not in ('strict','lax','none'):
        findings.append(issue('unknown_samesite_defaulted_to_lax')); samesite='lax'
    site_ok = samesite=='none' or data['same_site'] or samesite=='lax' and data['top_level_navigation'] and data['safe_method']
    if samesite=='none' and not secure:
        findings.append(issue('samesite_none_requires_secure'))
    prefix_ok=True
    if name.lower().startswith('__secure-'):
        prefix_ok=secure and source_scheme=='https'
    if name.lower().startswith('__host-'):
        prefix_ok=secure and source_scheme=='https' and host_only and attrs.get('path')=='/'
    if not prefix_ok: findings.append(issue('cookie_prefix_conditions_not_met'))
    deleted=False
    if 'max-age' in attrs:
        ma=attrs['max-age']
        if not isinstance(ma,str) or not re.fullmatch(r'-?[0-9]{1,19}',ma):
            findings.append(issue('invalid_or_unsupported_max_age'))
        else:
            deleted=int(ma)<=0
            if deleted: findings.append(issue('max_age_requests_deletion'))
    conditions={'setting_domain':bool(source_domain),'request_domain':bool(target_domain),'request_path':bool(target_path),
                'secure_transport':secure_context,'samesite_context':site_ok,'prefix':prefix_ok}
    for key,value in conditions.items():
        if not value and key not in ('setting_domain','prefix'):
            findings.append(issue('scope_condition_not_met',condition=key))
    unresolved=['cookie_store_and_expiration','browser_privacy_policy']
    if not host_only: unresolved.append('public_suffix_list')
    if 'partitioned' in attrs: unresolved.append('partition_key')
    return result(findings, host_only=host_only, secure=secure, http_only='httponly' in attrs,
                  samesite_policy=samesite, path_uses_default=path_fallback, conditions=conditions,
                  modeled_conditions_match=all(conditions.values()) and not deleted and not (samesite=='none' and not secure),
                  unresolved_checks=unresolved, unmodeled_attributes=sorted(set(attrs)-{'domain','path','secure','httponly','samesite','max-age'}),
                  cookie_value_echoed=False)

if __name__ == '__main__':
    raise SystemExit(main())
