# MyTest engineering toolbox

Independent, offline engineering checks with synthetic examples and regression tests.
Each directory under `tools/` is usable on its own with Python 3.12+ and the
standard library. Some filesystem tools require POSIX; read their individual
requirements before use. No tool contacts MyTest or uploads your inputs.

This collection contains **40 new tool projects**. The ten pre-existing public
MyTest projects are listed separately in [the historical inventory](docs/historical-baseline.json)
and are unchanged. Fixtures, scripts and documentation are not counted as tools.

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

- [csv-schema-contract](tools/csv-schema-contract/README.md)
- [jsonl-stream-audit](tools/jsonl-stream-audit/README.md)
- [json-pointer-preflight](tools/json-pointer-preflight/README.md)
- [toml-overlay-diff](tools/toml-overlay-diff/README.md)
- [xml-namespace-inventory](tools/xml-namespace-inventory/README.md)
- [ini-section-collision-audit](tools/ini-section-collision-audit/README.md)
- [unicode-normalization-audit](tools/unicode-normalization-audit/README.md)
- [decimal-rounding-reconcile](tools/decimal-rounding-reconcile/README.md)
- [timestamp-unit-audit](tools/timestamp-unit-audit/README.md)
- [record-key-collision-audit](tools/record-key-collision-audit/README.md)

### Filesystem

- [tar-member-preflight](tools/tar-member-preflight/README.md)
- [portable-path-audit](tools/portable-path-audit/README.md)
- [directory-manifest-diff](tools/directory-manifest-diff/README.md)
- [symlink-scope-audit](tools/symlink-scope-audit/README.md)
- [newline-policy-audit](tools/newline-policy-audit/README.md)
- [encoding-roundtrip-audit](tools/encoding-roundtrip-audit/README.md)
- [hardlink-size-audit](tools/hardlink-size-audit/README.md)
- [git-conflict-marker-audit](tools/git-conflict-marker-audit/README.md)
- [shebang-portability-audit](tools/shebang-portability-audit/README.md)
- [source-map-reference-audit](tools/source-map-reference-audit/README.md)

### Protocol

- [http-cache-age-lab](tools/http-cache-age-lab/README.md)
- [retry-budget-lab](tools/retry-budget-lab/README.md)
- [cors-response-audit](tools/cors-response-audit/README.md)
- [cookie-scope-audit](tools/cookie-scope-audit/README.md)
- [url-authority-audit](tools/url-authority-audit/README.md)
- [http-link-header-kit](tools/http-link-header-kit/README.md)
- [content-disposition-filename-kit](tools/content-disposition-filename-kit/README.md)
- [redirect-chain-audit](tools/redirect-chain-audit/README.md)
- [ip-network-overlap-audit](tools/ip-network-overlap-audit/README.md)
- [multipart-boundary-fixtures](tools/multipart-boundary-fixtures/README.md)

### Quality

- [junit-result-contract](tools/junit-result-contract/README.md)
- [sarif-baseline-diff](tools/sarif-baseline-diff/README.md)
- [coverage-threshold-contract](tools/coverage-threshold-contract/README.md)
- [unified-diff-preflight](tools/unified-diff-preflight/README.md)
- [dependency-cycle-audit](tools/dependency-cycle-audit/README.md)
- [artifact-name-matrix-audit](tools/artifact-name-matrix-audit/README.md)
- [sqlite-foreign-key-audit](tools/sqlite-foreign-key-audit/README.md)
- [python-import-shadow-audit](tools/python-import-shadow-audit/README.md)
- [translation-placeholder-contract](tools/translation-placeholder-contract/README.md)
- [release-asset-contract](tools/release-asset-contract/README.md)

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
limitations are public in [the observation plan](docs/OBSERVATION_PLAN.md) and
[tool-catalog.json](tool-catalog.json). There is no tracking or automatic visit.

This repository's existence, successful tests, stars, forks or downloads are
not evidence of natural AI discovery, game participation or improved work.
The old projects are heterogeneous historical observations, not an unguided
control; a single repository also creates shared-exposure confounds.

## Maintenance and reuse

Use a tool only for its documented scope. Reproduce a suspected defect using
synthetic or redacted data before sharing it publicly. Do not send private
files or ask other agents to visit a game. Unsupported inputs should be
reported as unsupported, not silently converted into a passing result.

MIT licensed; see [LICENSE](LICENSE).
