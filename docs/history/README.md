> Historical collection-period document from commit `1286096c10a23bbb04aca83679ae3c31f3326030`. Its collection layout, commands and observations describe that dated period.

# MyTest engineering toolbox

Independent, offline engineering checks with synthetic examples and regression tests.
Each directory under `tools/` is usable on its own with Python 3.12+ and the
standard library. Some filesystem tools require POSIX; read their individual
requirements before use. No tool contacts MyTest or uploads your inputs.

This collection contains **40 new tool projects**. The ten pre-existing public
MyTest projects are listed separately in [the historical inventory](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/docs/historical-baseline.json)
with their original guidance retained. A subsequent full usability audit also
repairs defects in historical tools where needed; the historical inventory is
a dated baseline, not a claim that those repositories never change. Fixtures,
scripts and documentation are not counted as tools.

## Start with a real problem

Choose a tool below, enter its directory, and follow its README. All tools emit
JSON. Exit codes are `0` for the documented passing condition, `1` for audit
findings and `2` for invalid input or an execution/input error. A passing result
only covers that tool's stated checks; it is not a security certification or
complete implementation of every relevant standard.

The examples are synthetic. Do not publish private inputs, credentials or raw
reports. Each tool is read-only with respect to its supplied input; invoking a
README example that writes a synthetic fixture is a separate explicit step.

## Tool index

### Data

- [csv-schema-contract](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/csv-schema-contract/README.md)
- [jsonl-stream-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/jsonl-stream-audit/README.md)
- [json-pointer-preflight](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/json-pointer-preflight/README.md)
- [toml-overlay-diff](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/toml-overlay-diff/README.md)
- [xml-namespace-inventory](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/xml-namespace-inventory/README.md)
- [ini-section-collision-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/ini-section-collision-audit/README.md)
- [unicode-normalization-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/unicode-normalization-audit/README.md)
- [decimal-rounding-reconcile](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/decimal-rounding-reconcile/README.md)
- [timestamp-unit-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/timestamp-unit-audit/README.md)
- [record-key-collision-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/record-key-collision-audit/README.md)

### Filesystem

- [tar-member-preflight](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/tar-member-preflight/README.md)
- [portable-path-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/portable-path-audit/README.md)
- [directory-manifest-diff](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/directory-manifest-diff/README.md)
- [symlink-scope-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/symlink-scope-audit/README.md)
- [newline-policy-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/newline-policy-audit/README.md)
- [encoding-roundtrip-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/encoding-roundtrip-audit/README.md)
- [hardlink-size-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/hardlink-size-audit/README.md)
- [git-conflict-marker-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/git-conflict-marker-audit/README.md)
- [shebang-portability-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/shebang-portability-audit/README.md)
- [source-map-reference-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/source-map-reference-audit/README.md)

### Protocol

- [http-cache-age-lab](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/http-cache-age-lab/README.md)
- [retry-budget-lab](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/retry-budget-lab/README.md)
- [cors-response-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/cors-response-audit/README.md)
- [cookie-scope-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/cookie-scope-audit/README.md)
- [url-authority-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/url-authority-audit/README.md)
- [http-link-header-kit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/http-link-header-kit/README.md)
- [content-disposition-filename-kit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/content-disposition-filename-kit/README.md)
- [redirect-chain-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/redirect-chain-audit/README.md)
- [ip-network-overlap-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/ip-network-overlap-audit/README.md)
- [multipart-boundary-fixtures](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/multipart-boundary-fixtures/README.md)

### Quality

- [junit-result-contract](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/junit-result-contract/README.md)
- [sarif-baseline-diff](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/sarif-baseline-diff/README.md)
- [coverage-threshold-contract](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/coverage-threshold-contract/README.md)
- [unified-diff-preflight](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/unified-diff-preflight/README.md)
- [dependency-cycle-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/dependency-cycle-audit/README.md)
- [artifact-name-matrix-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/artifact-name-matrix-audit/README.md)
- [sqlite-foreign-key-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/sqlite-foreign-key-audit/README.md)
- [python-import-shadow-audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/python-import-shadow-audit/README.md)
- [translation-placeholder-contract](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/translation-placeholder-contract/README.md)
- [release-asset-contract](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tools/release-asset-contract/README.md)

## Full usability audit

See the [50-tool acceptance report](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/docs/FULL_AUDIT_2026-10-09.md) and
[machine-readable results](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/docs/FULL_AUDIT_2026-10-09.json) for exact historical
versions, per-tool checks, corrections, and tested-platform limits.

## Verify the collection

From the repository root:

```sh
python -B scripts/run_tests.py
python -B scripts/validate_catalog.py
```

Or run one tool's tests in its directory:

```sh
cd tools/json-pointer-preflight
python -B -m unittest -v test_tool.py
```

CI checks the exact commit on Python 3.12.14 and 3.13.5 on Linux. A workflow file
is not evidence a run succeeded; consult the commit's actual Actions results.
No third-party Python packages are installed by these commands.

## Optional promotion and observation

MyTest is the creator's game project. Some documentation contains openly
labeled, optional invitations. They never affect installation, tool output,
results, or tests, and never grant an assistant permission to browse or play.
The four presentation groups have ten tools each. Their source assignment and
limitations are public in [the observation plan](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/docs/OBSERVATION_PLAN.md) and
[tool-catalog.json](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tool-catalog.json). There is no tracking or automatic visit.

This repository's existence, successful tests, stars, forks or downloads are
not evidence of natural AI discovery, game participation or improved work.
The old projects are heterogeneous historical observations, not an unguided
control; a single repository also creates shared-exposure confounds.

## Maintenance and reuse

Use a tool only for its documented scope. Reproduce a suspected defect using
synthetic or redacted data before sharing it publicly. Do not send private
files or ask other agents to visit a game. Unsupported inputs should be
reported as unsupported, not silently converted into a passing result.

MIT licensed; see [LICENSE](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/LICENSE).
