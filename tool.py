#!/usr/bin/env python3
"""Offline, read-only audit. Python 3.12+, standard library only."""
import argparse
import json
import math
import re
import stat
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

MAX_BYTES = 8 * 1024 * 1024
MAX_RECORDS = 50000
MAX_FINDINGS = 100

class InputError(ValueError):
    """A safe, non-payload-bearing input error code."""

class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise InputError("invalid_arguments")

def read_text(path):
    p = Path(path)
    if not stat.S_ISREG(p.stat().st_mode):
        raise InputError("regular_file_required")
    with p.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise InputError("file_size_limit")
    return data.decode("utf-8")

def reject_constant(value):
    raise InputError("non_finite_json_number")

def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("duplicate_json_member")
        result[key] = value
    return result

def parse_json(text):
    try:
        result = json.loads(text, object_pairs_hook=unique_pairs,
                            parse_float=Decimal, parse_constant=reject_constant)
    except InputError:
        raise
    except (ValueError, RecursionError, InvalidOperation):
        raise InputError("invalid_json") from None
    stack, nodes = [(result, 0)], 0
    while stack:
        value, depth = stack.pop()
        nodes += 1
        if depth > 128 or nodes > 200000:
            raise InputError("json_structure_limit")
        if isinstance(value, dict):
            stack.extend((v, depth + 1) for v in value.values())
        elif isinstance(value, list):
            stack.extend((v, depth + 1) for v in value)
    return result

class Report:
    def __init__(self, tool):
        self.tool, self.findings, self.count = tool, [], 0
    def add(self, code, **location):
        self.count += 1
        if len(self.findings) < MAX_FINDINGS:
            self.findings.append(dict(code=code, **location))
    def finish(self, **summary):
        return {"tool": self.tool, "status": "fail" if self.count else "pass",
                "summary": dict(summary, finding_count=self.count),
                "findings": self.findings,
                "findings_truncated": self.count > len(self.findings)}

def emit_main(run):
    try:
        result = run()
        code = 1 if result["status"] == "fail" else 0
    except InputError as exc:
        result, code = {"tool": TOOL, "status": "error", "error": str(exc)}, 2
    except (OSError, UnicodeError):
        result, code = {"tool": TOOL, "status": "error", "error": "unreadable_utf8_input"}, 2
    except (ValueError, RecursionError, InvalidOperation):
        result, code = {"tool": TOOL, "status": "error", "error": "invalid_input"}, 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False))
    return code

TOOL = "csv-schema-contract"

import csv
import io
from datetime import date

TYPES = {"string", "integer", "decimal", "boolean", "date"}

def validate_contract(contract):
    if not isinstance(contract, dict) or set(contract) - {"columns", "allow_extra", "header_order"}:
        raise InputError("invalid_contract")
    columns = contract.get("columns")
    if not isinstance(columns, list) or not 1 <= len(columns) <= 1000:
        raise InputError("invalid_contract_columns")
    seen = set()
    for column in columns:
        if not isinstance(column, dict) or set(column) - {"name", "type", "required"}:
            raise InputError("invalid_column_contract")
        name = column.get("name")
        if not isinstance(name, str) or not name or len(name) > 1024 or name in seen:
            raise InputError("invalid_contract_column_name")
        seen.add(name)
        if not isinstance(column.get("type"), str) or column["type"] not in TYPES or type(column.get("required", True)) is not bool:
            raise InputError("invalid_column_contract")
    for option in ("allow_extra", "header_order"):
        if type(contract.get(option, False)) is not bool:
            raise InputError("invalid_contract_option")
    return columns

def valid_type(value, kind):
    if kind == "string":
        return True
    if kind == "integer":
        return bool(re.fullmatch(r"[+-]?[0-9]+", value))
    if kind == "decimal":
        return bool(re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", value))
    if kind == "boolean":
        return value in ("true", "false")
    try:
        return bool(re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value)) and bool(date.fromisoformat(value))
    except ValueError:
        return False

def _audit_csv(text, contract):
    columns = validate_contract(contract)
    report = Report(TOOL)
    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    try:
        header = next(reader)
    except StopIteration:
        raise InputError("empty_csv") from None
    except csv.Error:
        raise InputError("malformed_csv") from None
    if not header or len(header) > 1000:
        raise InputError("invalid_header_width")
    index = {}
    for position, name in enumerate(header, 1):
        if name in index:
            report.add("duplicate_header", column=position, first_column=index[name] + 1)
        else:
            index[name] = position - 1
        if not name:
            report.add("empty_header", column=position)
    names = [c["name"] for c in columns]
    for position, column in enumerate(columns, 1):
        if column["name"] not in index:
            report.add("missing_column", contract_column=position)
    if not contract.get("allow_extra", False):
        for position, name in enumerate(header, 1):
            if name not in names:
                report.add("unexpected_column", column=position)
    if contract.get("header_order", False) and [h for h in header if h in names] != names:
        report.add("header_order_mismatch", row=1)
    rows = 0
    try:
        for row in reader:
            rows += 1
            if rows > MAX_RECORDS:
                raise InputError("row_limit")
            if len(row) > 1000:
                raise InputError("row_width_limit")
            if len(row) != len(header):
                report.add("row_width", row=rows + 1, expected=len(header), actual=len(row))
            for contract_index, column in enumerate(columns, 1):
                col = index.get(column["name"])
                if col is None or col >= len(row):
                    continue
                value = row[col]
                if value == "":
                    if column.get("required", True):
                        report.add("missing_value", row=rows + 1, column=col + 1)
                elif not valid_type(value, column["type"]):
                    report.add("type_mismatch", row=rows + 1, column=col + 1,
                               expected_type=column["type"])
    except csv.Error:
        raise InputError("malformed_csv") from None
    return report.finish(rows=rows, columns=len(header), contract_columns=len(columns))

def audit(text, contract):
    previous = csv.field_size_limit()
    try:
        csv.field_size_limit(65536)
        return _audit_csv(text, contract)
    finally:
        csv.field_size_limit(previous)

def run():
    parser = Parser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("--contract", required=True)
    args = parser.parse_args()
    return audit(read_text(args.input), parse_json(read_text(args.contract)))

if __name__ == "__main__":
    sys.exit(emit_main(run))
