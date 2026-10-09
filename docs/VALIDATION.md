# Release validation — 2026-10-09

The release contains 40 independent tool projects; the ten historical projects
are unchanged. Local Linux tests ran on Python 3.12.14 and 3.13.5, with 747
unittest cases across 40 suites passing on each runtime. The catalog and
documentation-boundary validator also passed. Tests use synthetic inputs.

Independent review added 65 targeted cases across 11 selected tools, including
malformed input, filesystem boundaries and sensitive-output checks. This was
selected coverage, not an independent review of every tool or a certification.
It found and prompted regression fixes for empty source-map query/fragment
delimiters, equivalent IPv6 cookie hosts, and missing unified-diff file headers
after a new Git section. The original failing cases were rechecked separately.

All source Python files were parsed, local documentation links checked, and
all four documentation-only invitation groups checked at ten tools each.
Each tool documents its own supported subset and limitations.

Remote CI is a separate check: consult the Actions run for the exact commit.
Neither test results nor publication establish natural discovery or game use.

## Subsequent full usability review

The initial result above is retained as historical evidence. See [the full
50-tool audit](FULL_AUDIT_2026-10-09.md) for later independently found defects,
corrections and the new 794-test-per-runtime acceptance result.
