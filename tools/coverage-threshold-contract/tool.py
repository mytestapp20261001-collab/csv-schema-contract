#!/usr/bin/env python3
"""Offline, bounded contract audit. Python 3.12 standard library only."""
import argparse
import json
import math
from decimal import Decimal, DecimalException
import sys
from pathlib import Path

MAX_BYTES = 2 * 1024 * 1024
MAX_ITEMS = 10000
class BadInput(ValueError):
    pass
class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise BadInput("invalid command arguments")

def require(condition, message):
    if not condition:
        raise BadInput(message)

def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, "duplicate JSON object key")
        result[key] = value
    return result

def reject_constant(value):
    raise BadInput("nonfinite JSON number")

def read_text(path):
    require(Path(path).is_file(), "input must be a regular file")
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, "input exceeds 2 MiB limit")
    return raw.decode("utf-8-sig")

def finite_float(value):
    require(len(value) <= 128, "decimal token exceeds 128 characters")
    try:
        parsed = Decimal(value)
    except DecimalException as exc:
        raise BadInput("invalid or unsupported decimal") from exc
    require(parsed.is_finite() and abs(parsed.as_tuple().exponent) <= 1000, "unsupported decimal exponent")
    return parsed

def load_json(path):
    return json.loads(read_text(path), object_pairs_hook=pairs, parse_constant=reject_constant, parse_float=finite_float)

def report(findings, **summary):
    return {"schema_version": 1, "tool": TOOL, "status": "findings" if findings else "pass", "summary": summary, "findings": findings}

def finding(code, **where):
    return {"code": code, **where}

def run(build_parser, action):
    try:
        parser = Parser(description=__doc__)
        build_parser(parser)
        result = action(parser.parse_args())
        status = 1 if result["status"] == "findings" else 0
    except (ValueError, OSError, UnicodeError, RecursionError, OverflowError) as exc:
        message = str(exc) if isinstance(exc, BadInput) else "unreadable or malformed input"
        result = {"schema_version": 1, "tool": TOOL, "status": "error", "error": message}
        status = 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True, allow_nan=False))
    return status

TOOL = "coverage-threshold-contract"

def audit(data):
    require(isinstance(data, dict) and set(data) <= {"thresholds", "files"}, "expected thresholds/files object")
    thresholds, files = data.get("thresholds"), data.get("files")
    require(isinstance(thresholds, dict) and thresholds and set(thresholds) <= {"line", "branch"}, "require line and/or branch thresholds")
    ratios = {}
    exact_thresholds = {}
    for metric, value in thresholds.items():
        require(type(value) in (int, float, Decimal), "threshold must be a number")
        decimal = finite_float(str(value))
        require(0 <= decimal <= 100, "threshold must be finite 0..100")
        ratios[metric] = decimal.as_integer_ratio()
        exact_thresholds[metric] = str(decimal)
    require(isinstance(files, list) and len(files) <= MAX_ITEMS, "files must be a bounded array")
    findings, totals, seen = [], {key: [0, 0] for key in thresholds}, set()
    if not files:
        findings.append(finding("no_coverage_files"))
    for i, item in enumerate(files):
        require(isinstance(item, dict) and set(item) <= {"path", "line", "branch"}, "invalid coverage file object")
        path = item.get("path")
        require(isinstance(path, str) and 0 < len(path) <= 1024, "file path must be a nonempty string")
        if path in seen:
            findings.append(finding("duplicate_file", file_index=i))
        seen.add(path)
        for metric in ("line", "branch"):
            if metric not in item:
                if metric in thresholds:
                    findings.append(finding("missing_metric", file_index=i, metric=metric))
                continue
            value = item[metric]
            require(isinstance(value, dict) and set(value) == {"covered", "total"}, "metric requires covered and total")
            covered, total = value["covered"], value["total"]
            require(type(covered) is int and type(total) is int and 0 <= covered <= total <= 10**12, "coverage counts must satisfy 0 <= covered <= total <= 10^12")
            if metric not in thresholds:
                continue
            totals[metric][0] += covered
            totals[metric][1] += total
            if total == 0:
                findings.append(finding("zero_denominator", file_index=i, metric=metric))
            elif covered * 100 * ratios[metric][1] < ratios[metric][0] * total:
                findings.append(finding("below_threshold", file_index=i, metric=metric, percent=round(covered * 100 / total, 6), threshold=float(thresholds[metric]), threshold_decimal=exact_thresholds[metric]))
    aggregates = {key: {"covered": counts[0], "total": counts[1], "percent": round(counts[0]*100/counts[1], 6) if counts[1] else None} for key, counts in totals.items()}
    return report(findings, files=len(files), aggregates=aggregates, policy="each_file")

def configure(parser):
    parser.add_argument("input", help="local coverage contract JSON")
if __name__ == "__main__":
    sys.exit(run(configure, lambda args: audit(load_json(args.input))))
