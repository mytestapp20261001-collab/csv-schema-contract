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

def split_quoted(value, delimiter=","):
    parts, start, quoted, escaped = [], 0, False, False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
        elif quoted and char == "\\":
            escaped = True
        elif char == '"':
            quoted = not quoted
        elif char == delimiter and not quoted:
            parts.append(value[start:index].strip(" \t")); start = index + 1
    require(not quoted and not escaped, "unterminated quoted string")
    parts.append(value[start:].strip(" \t"))
    return parts

def parameter_value(raw):
    if raw.startswith('"'):
        require(len(raw) >= 2 and raw.endswith('"'), "invalid quoted value")
        out, escaped = [], False
        for char in raw[1:-1]:
            if escaped:
                out.append(char); escaped = False
            elif char == "\\":
                escaped = True
            else:
                require(char != '"', "unescaped quote")
                out.append(char)
        require(not escaped, "unterminated quoted escape")
        return "".join(out)
    require(bool(TOKEN.fullmatch(raw)), "invalid token value")
    return raw

import hashlib
import unicodedata
from urllib.parse import unquote_to_bytes


def decode_extended(raw):
    require(not raw.startswith('"'),'filename* must not be quoted')
    fields=raw.split("'",2)
    require(len(fields)==3,'extended value requires charset and language separators')
    charset,language,value=fields
    require(charset.lower() in ('utf-8','iso-8859-1'),'only UTF-8 and ISO-8859-1 extended values supported')
    require(not language or bool(re.fullmatch(r'[A-Za-z]{1,8}(?:-[A-Za-z0-9]{1,8})*',language)), 'unsupported language tag shape')
    require(bool(re.fullmatch(r"(?:[!#$&+.^_`|~0-9A-Za-z-]|%[0-9A-Fa-f]{2})*",value)), 'invalid extended value or percent escape')
    try: return unquote_to_bytes(value).decode(charset,'strict')
    except UnicodeError as exc: raise InputError('extended filename cannot be decoded strictly') from exc


def inspect_filename(value):
    findings=[]
    if not value: findings.append('empty_filename')
    if len(value)>255: findings.append('long_filename_component')
    if '/' in value or '\\' in value: findings.append('contains_path_separator')
    if value in ('.','..') or '..' in re.split(r'[/\\]',value): findings.append('dot_path_segment')
    if value.startswith(('/','\\')) or re.match(r'^[A-Za-z]:',value): findings.append('absolute_or_drive_path')
    if any(unicodedata.category(c) in ('Cc','Cf') for c in value): findings.append('control_or_format_character')
    if value.rstrip(' .')!=value or value.lstrip(' ')!=value: findings.append('edge_space_or_dot')
    if re.search(r'[<>:"|?*]',value): findings.append('windows_reserved_character')
    stem=value.split('.')[0].upper().rstrip(' ')
    if stem in ('CON','PRN','AUX','NUL') or re.fullmatch(r'(?:COM|LPT)[1-9¹²³]',stem): findings.append('windows_device_name')
    if re.search(r'%[0-9a-fA-F]{2}',value): findings.append('literal_percent_escape_can_be_misinterpreted')
    if unicodedata.normalize('NFC',value)!=value: findings.append('unicode_normalization_changes_name')
    extension=value.rsplit('.',1)[-1].lower() if '.' in value else ''
    if extension in {'exe','com','bat','cmd','sh','ps1','js','vbs','scr','msi','lnk','desktop'}:
        findings.append('potentially_executable_extension')
    return findings


def audit(data):
    schema(data,('content_disposition',))
    value=header(data['content_disposition'])
    require(value.isascii(),'non-ASCII literal header outside supported subset; use filename*')
    parts=split_quoted(value,';')
    require(bool(TOKEN.fullmatch(parts[0])),'disposition type must be a token')
    require(len(parts)<=65,'at most 64 disposition parameters supported')
    params={}; findings=[]
    for raw in parts[1:]:
        key,sep,val=raw.partition('='); key=key.strip(' \t').lower(); val=val.strip(' \t')
        require(bool(sep) and bool(TOKEN.fullmatch(key)),'invalid disposition parameter')
        decoded=decode_extended(val) if key=='filename*' else parameter_value(val)
        params.setdefault(key,[]).append(decoded)
    for key,values in params.items():
        if len(values)>1: findings.append(issue('duplicate_parameter',parameter=key))
    candidates=[]
    for key in ('filename','filename*'):
        for index,name in enumerate(params.get(key,[])):
            for code in inspect_filename(name): findings.append(issue(code,parameter=key,index=index))
            candidates.append({'parameter':key,'index':index,'characters':len(name),
                               'filename_sha256':hashlib.sha256(name.encode('utf-8')).hexdigest()})
    if not candidates: findings.append(issue('missing_filename'))
    ambiguous=any(len(values)>1 for values in params.values())
    selected=None if ambiguous else 'filename*' if 'filename*' in params else 'filename' if 'filename' in params else None
    return result(findings, disposition=parts[0].lower(), selected_parameter=selected,
                  candidates=candidates, ignored_parameter_names=sorted(set(params)-{'filename','filename*'}),
                  filename_echoed=False, files_written=0)

if __name__ == '__main__':
    raise SystemExit(main())
