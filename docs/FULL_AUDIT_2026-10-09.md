# Full 50-tool usability audit — 2026-10-09

## Acceptance result

All 50 projects passed their documented Linux usage paths after the corrections below. Every project received source/documentation review, actual README positive and negative runs, its complete existing test suite, and additional independent malformed-input or semantic-boundary checks. Expected negative-control exits are successful checks, not unexplained failures. This is finite verification, not a guarantee of no defects on every platform.

The 40 collection tools ran 794 unittest methods on each of CPython 3.12.14 and 3.13.5. Each was also copied into a standalone directory and checked from an external working directory for help, missing input and its full suite: 120/120 checks passed. Catalog, local links and documentation-only guidance checks passed.

The historical tools used exact remote-main snapshots verified by Git blob, not presumed-current local directories. Node 24.19.0, npm 11.9.0, Playwright 1.63.0, CMake 3.31.10 and 4.4.4, and pinned Protobuf 7.36.2 were actually exercised where applicable. Official locked npm/PyPI setup was verified in isolated directories. Other versions shown by CI are separate evidence, not claimed local runs.

No private inputs, production database or Site deployment were used. Guidance groups were not reassigned; existing promotional text was preserved. Tests, traffic from tests, and publication are not natural tool adoption or MyTest participation.

## Historical projects (10)

| Tool | Validated commit | Suite tests | Result and limits |
|---|---|---:|---|
| [har-redaction-fixtures](https://github.com/mytestapp20261001-collab/har-redaction-fixtures) | [b327ae82](https://github.com/mytestapp20261001-collab/har-redaction-fixtures/commit/b327ae82fada8495a33ebc987cde1916eec1561d) | 30 | Pass. Synthetic known markers only; not general HAR privacy certification. |
| [playwright-run-audit](https://github.com/mytestapp20261001-collab/playwright-run-audit) | [9b9f4032](https://github.com/mytestapp20261001-collab/playwright-run-audit/commit/9b9f4032cfd2dc1414ec67f63e941a21e6e06807) | 28 | Pass. Post-selection runner receipts; not proof of selection correctness or authenticity. |
| [env-loader-audit](https://github.com/mytestapp20261001-collab/env-loader-audit) | [0aeade00](https://github.com/mytestapp20261001-collab/env-loader-audit/commit/0aeade00933da83c66f1fa65c6f907bfe44359a5) | 59 | Pass. POSIX; bounded dotenv/Node model, non-exhaustive startup flags. |
| [resume-download-integrity-kit](https://github.com/mytestapp20261001-collab/resume-download-integrity-kit) | [eb4de719](https://github.com/mytestapp20261001-collab/resume-download-integrity-kit/commit/eb4de719b6ccd1322757cd0685c9e7be73b0149a) | 13 | Pass. Trusted adapters and synthetic loopback TCP; not a sandbox or production downloader. |
| [sqlite-wal-restore-lab](https://github.com/mytestapp20261001-collab/sqlite-wal-restore-lab) | [192ae258](https://github.com/mytestapp20261001-collab/sqlite-wal-restore-lab/commit/192ae25894933ae297c92706232c02614f6b3a84) | 15 | Pass. Synthetic SQLite/WAL restoration lab; no live production database. |
| [lsp-position-edit-kit](https://github.com/mytestapp20261001-collab/lsp-position-edit-kit) | [af6354d1](https://github.com/mytestapp20261001-collab/lsp-position-edit-kit/commit/af6354d16a6295b0f2095a70494461490ba2873c) | 24 | Pass. 13-case trusted-adapter LSP acceptance kit, not full conformance. |
| [zip-member-preflight](https://github.com/mytestapp20261001-collab/zip-member-preflight) | [a253f5b7](https://github.com/mytestapp20261001-collab/zip-member-preflight/commit/a253f5b7d9c12a8fc3e5ec99eb80101f04513d13) | 46 | Pass. Metadata/name hazards only; no extraction, CRC/content integrity or malware proof. |
| [make-rebuild-contract-kit](https://github.com/mytestapp20261001-collab/make-rebuild-contract-kit) | [56e6aadb](https://github.com/mytestapp20261001-collab/make-rebuild-contract-kit/commit/56e6aadbcd7d9c78225b23a5466d6c3156b71e74) | 22 | Pass. GNU Make/GCC build contract; not every build system. |
| [cmake-relocation-lab](https://github.com/mytestapp20261001-collab/cmake-relocation-lab) | [83bb1307](https://github.com/mytestapp20261001-collab/cmake-relocation-lab/commit/83bb1307f55389eab5bc6c21eea07a601741e694) | 24 | Pass. CMake/GCC Linux relocation lab; no cross-platform packaging guarantee. |
| [protobuf-relay-preservation-lab](https://github.com/mytestapp20261001-collab/protobuf-relay-preservation-lab) | [1ab20267](https://github.com/mytestapp20261001-collab/protobuf-relay-preservation-lab/commit/1ab2026770f3ba387b2ca02aa44adb90593a52b0) | 23 | Pass. One schema pair and fixed semantic projection; not cross-language compatibility proof. |

HAR additionally tested strict invalid-UTF-8 rejection and FIFO nonblocking rejection (both repaired). Resume-download setup/import errors now return exit 2 while expected download-policy failures remain exit 1. Protobuf missing/incompatible runtime now returns setup exit 2 instead of a traceback/negative-control exit 1. All have regression tests.

Playwright additionally completed nine real runner integrations and a removed-receipt negative check. LSP received independent Unicode-coordinate oracles, ZIP bounded mutation and collision checks, and Make/CMake real stale/overbuild/relocation negative controls. SQLite ran synthetic content-tamper and restoration checks.

## Collection projects (40)

The source validated below is the commit containing this report. The previous audited baseline was ba546c1aee3ca079fdafe6a5629843369946559f. Each number is unittest methods per Python runtime; independent property assertions are deliberately not added to these counts.

| Tool | Group | Tests/runtime | Result, correction and limits |
|---|---|---:|---|
| [csv-schema-contract](../tools/csv-schema-contract/README.md) | light | 25 | Pass. Correction: Enforce data-row field limit, not just header limit. Excel CSV subset; 1,000 fields per record; not spreadsheet-formula safety. |
| [jsonl-stream-audit](../tools/jsonl-stream-audit/README.md) | strong | 23 | Pass. No new defect found in this review. Bounded local export, not a live incremental stream. |
| [json-pointer-preflight](../tools/json-pointer-preflight/README.md) | medium | 22 | Pass. No new defect found in this review. Plain RFC 6901; no fragments, JSONPath or patch application. |
| [toml-overlay-diff](../tools/toml-overlay-diff/README.md) | medium | 23 | Pass. No new defect found in this review. Explicit shallow/deep policy; not application-specific merging. |
| [xml-namespace-inventory](../tools/xml-namespace-inventory/README.md) | medium | 25 | Pass. Correction: Correct locator documentation to element-start lines; regression added. Inventory only; DTD rejected; locations identify element starts. |
| [ini-section-collision-audit](../tools/ini-section-collision-audit/README.md) | light | 25 | Pass. Correction: Do not invent a line after terminal LF. Small LF-delimited dialect, no interpolation or inheritance. |
| [unicode-normalization-audit](../tools/unicode-normalization-audit/README.md) | light | 22 | Pass. No new defect found in this review. NFC and character categories, not confusable detection. |
| [decimal-rounding-reconcile](../tools/decimal-rounding-reconcile/README.md) | strong | 22 | Pass. No new defect found in this review. Explicit bounded rounding mathematics, not accounting policy. |
| [timestamp-unit-audit](../tools/timestamp-unit-audit/README.md) | maximal | 22 | Pass. No new defect found in this review. Integer Unix seconds/milliseconds/microseconds; ambiguity remains explicit. |
| [record-key-collision-audit](../tools/record-key-collision-audit/README.md) | maximal | 25 | Pass. No new defect found in this review. Direct scalar keys; not database collation equivalence. |
| [tar-member-preflight](../tools/tar-member-preflight/README.md) | light | 12 | Pass. No new defect found in this review. POSIX metadata audit, plain/gzip TAR; no extraction or payload proof. |
| [portable-path-audit](../tools/portable-path-audit/README.md) | medium | 11 | Pass. No new defect found in this review. Name portability policy, not execution on every target filesystem. |
| [directory-manifest-diff](../tools/directory-manifest-diff/README.md) | strong | 11 | Pass. No new defect found in this review. Bounded stable trees; not an atomic concurrent snapshot. |
| [symlink-scope-audit](../tools/symlink-scope-audit/README.md) | medium | 15 | Pass. Correction: Accept harmless redundant root-prefix separators/dots without collapsing unsafe parent transitions. POSIX in-memory resolution within selected root; no external lookup. |
| [newline-policy-audit](../tools/newline-policy-audit/README.md) | maximal | 12 | Pass. No new defect found in this review. Explicit byte/newline policy, not content semantics. |
| [encoding-roundtrip-audit](../tools/encoding-roundtrip-audit/README.md) | maximal | 12 | Pass. No new defect found in this review. Explicit encoding required; no automatic detection. |
| [hardlink-size-audit](../tools/hardlink-size-audit/README.md) | strong | 12 | Pass. No new defect found in this review. Allocated-byte estimate, not compressed/shared physical storage truth. |
| [git-conflict-marker-audit](../tools/git-conflict-marker-audit/README.md) | medium | 15 | Pass. Correction: Correct terminal-LF line counting. Text marker grammar, no Git invocation or conflict resolution. |
| [shebang-portability-audit](../tools/shebang-portability-audit/README.md) | light | 13 | Pass. No new defect found in this review. Documented env -S subset, not shell execution. |
| [source-map-reference-audit](../tools/source-map-reference-audit/README.md) | strong | 19 | Pass. Correction: Validate raw sourceRoot and source independently before prefixing. Relative local references only; no VLQ/complete source-map validation. |
| [http-cache-age-lab](../tools/http-cache-age-lab/README.md) | medium | 17 | Pass. Correction: Return sanitized JSON/exit 2 for CLI argument errors; retain text help/exit 0. Documented cache-age model; restricted HTTP-date syntax. |
| [retry-budget-lab](../tools/retry-budget-lab/README.md) | strong | 15 | Pass. Correction: Return sanitized JSON/exit 2 for CLI argument errors; retain text help/exit 0. Deterministic schedule; no jitter or real network timing. |
| [cors-response-audit](../tools/cors-response-audit/README.md) | maximal | 22 | Pass. Correction: Return sanitized JSON/exit 2 for CLI argument errors; retain text help/exit 0. Partial response policy, not browser-conformance testing. |
| [cookie-scope-audit](../tools/cookie-scope-audit/README.md) | strong | 28 | Pass. Correction: Return sanitized JSON/exit 2 for CLI argument errors; retain text help/exit 0. Scope model without Public Suffix List/browser storage behavior. |
| [url-authority-audit](../tools/url-authority-audit/README.md) | strong | 26 | Pass. No new defect found in this review. Documented urllib/IDNA policy; no DNS or network requests. |
| [http-link-header-kit](../tools/http-link-header-kit/README.md) | light | 25 | Pass. Correction: Return sanitized JSON/exit 2 for CLI argument errors; retain text help/exit 0. Documented Link subset; no target fetching or title* decoding. |
| [content-disposition-filename-kit](../tools/content-disposition-filename-kit/README.md) | light | 24 | Pass. Correction: Return sanitized JSON/exit 2 for CLI argument errors; retain text help/exit 0. Filename hazard heuristics; no download or filesystem creation. |
| [redirect-chain-audit](../tools/redirect-chain-audit/README.md) | maximal | 35 | Pass. No new defect found in this review. Supplied chain only; no redirect fetching or DNS checks. |
| [ip-network-overlap-audit](../tools/ip-network-overlap-audit/README.md) | maximal | 21 | Pass. No new defect found in this review. IP prefix arithmetic; not routing/firewall behavior. |
| [multipart-boundary-fixtures](../tools/multipart-boundary-fixtures/README.md) | medium | 22 | Pass. Correction: Reject bare-CR delimiters; preserve binary payload; correct offsets documentation and CLI errors. CRLF framing subset; not a full MIME parser; large findings possible. |
| [junit-result-contract](../tools/junit-result-contract/README.md) | medium | 17 | Pass. No new defect found in this review. Flat non-namespaced JUnit subset, not complete industry schema. |
| [sarif-baseline-diff](../tools/sarif-baseline-diff/README.md) | light | 17 | Pass. No new defect found in this review. SARIF subset, first physical location; not all SARIF properties. |
| [coverage-threshold-contract](../tools/coverage-threshold-contract/README.md) | strong | 24 | Pass. Correction: Exact decimal threshold comparison and bounded, sanitized extreme exponents. Supplied counters only; exact bounded decimal thresholds. |
| [unified-diff-preflight](../tools/unified-diff-preflight/README.md) | light | 29 | Pass. No new defect found in this review. Text diff structure only; binary unsupported; does not apply patches. |
| [dependency-cycle-audit](../tools/dependency-cycle-audit/README.md) | maximal | 19 | Pass. Correction: Count self-loops inside a multi-node SCC only once per component. Supplied directed graph; no dependency resolution. |
| [artifact-name-matrix-audit](../tools/artifact-name-matrix-audit/README.md) | light | 18 | Pass. No new defect found in this review. Naming contract only; not all filesystem equivalences. |
| [sqlite-foreign-key-audit](../tools/sqlite-foreign-key-audit/README.md) | strong | 15 | Pass. Correction: Reject selected parent components before normalization can hide symlinks. Linux offline stable DB only; no WAL sidecars or production operation. |
| [python-import-shadow-audit](../tools/python-import-shadow-audit/README.md) | maximal | 15 | Pass. Correction: Reject selected parent components before normalization can select a different root. Current-runtime name inventory; does not import target code. |
| [translation-placeholder-contract](../tools/translation-placeholder-contract/README.md) | maximal | 18 | Pass. No new defect found in this review. Documented placeholder syntax; not all template languages. |
| [release-asset-contract](../tools/release-asset-contract/README.md) | medium | 21 | Pass. Correction: Reject hidden-parent traversal and Unicode Cc asset names (DEL/C1 included). POSIX bounded manifest/hash audit; no provenance certification. |

## Reproduce and interpret

From this repository root, run `python -B scripts/run_tests.py` and `python -B scripts/validate_catalog.py`. Run each historical repository's documented commands at the commit linked above, including its negative controls. The new boundary cases are checked into the affected regression suites; test fixtures are synthetic.

Remote release acceptance is separate from this local report. Inspect the [Actions run for the exact containing commit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/actions). A workflow file or a push alone is not proof of a green run. Historical fixes retain their own repository CI and normal history.

The initial 40-tool release had 747 tests per runtime; this audit increased that to 794 and closed the independently reproduced failures. Original test success had not exposed those defects. The original baseline record remains a dated observation, not current HEAD.

## Remaining boundaries

- Linux x86_64 was tested; Windows/macOS execution was not. POSIX/Linux-only tools fail closed where required primitives are absent.
- Read-only filesystem audits assume stable inputs, not hostile concurrent mutation. Selected paths containing parent components are rejected by three no-follow tools before normalization.
- Tool-specific standards subsets remain explicit. Passing a checker does not certify security, all protocol behavior, privacy of arbitrary inputs, or production compatibility.
- Names/paths in tools that explicitly report them can be sensitive. Review local reports before sharing. Some tools bound input rather than the size of all resulting findings.
- There is no remaining reproduced defect from this review. New reproducible failures should reopen the affected tool; no recurring monitor was created.
