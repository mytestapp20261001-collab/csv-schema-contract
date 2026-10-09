# TAR Member Preflight

Audit TAR extraction hazards and member budgets before choosing an extraction policy.

## Scope

This is a TAR metadata policy gate, distinct from a ZIP filename-collision checker. It checks links (all links are findings), link destinations outside the archive, members beneath links, special/sparse members, privileged mode bits, traversal/Windows drive paths, duplicate destinations, member counts, individual declared sizes, and cumulative declared sizes. Supports plain TAR and gzip TAR only; bz2/xz are deliberately rejected.

Input is read with a compressed-byte budget. A separate expanded-stream budget limits decompression and extended-header reads. The tool never calls extract or extractfile, creates no output directory, and prints member indexes rather than archive names or link targets. A member/total budget finding may stop the scan (`summary.complete=false`); stream/input limits and malformed archives return exit 2. No authenticity, payload integrity, complete format conformance, or safe future extraction is certified. TAR end markers/trailing bytes follow Python tarfile behavior. Use an appropriate extraction filter separately when extraction is authorized.

## CLI

```sh
python3 tool.py archive.tar.gz --max-members 10000 --max-member-bytes 67108864 --max-total-bytes 268435456
```

## Runtime, output, and boundaries

Python 3.12 standard library only. Run on a POSIX host with `O_NOFOLLOW` and descriptor-relative opens; unsupported hosts return a JSON input error. The portability audit targets names for other systems without claiming it runs safely on every system. Every input path component must be a real non-symlink. Scans use descriptor-relative no-follow traversal; input files are never modified. No network, upload, subprocess execution of inputs, dependency installation, credential access, or permission changes. Examples/tests create only synthetic temporary fixtures.

Each CLI emits one stable JSON object with `schema_version: 1`, `tool`, `status`, summary and coded findings; input errors have a sanitized `error` object. Exit 0 = no findings, 1 = policy findings/differences, 2 = malformed/unreadable/unsupported input or resource limit preventing a complete audit. `--help` is argparse text and exits 0. Public `audit(...)` returns the same object; it never calls `sys.exit`. `--max-findings` bounds detail while preserving the total finding count. Limits must be positive; use `--help` for defaults. Read errors are never silently treated as a pass. Scans are not atomic snapshots; keep input trees/files stable during an audit. Input paths containing a symlink before `..` are rejected rather than silently normalized.

## Verified synthetic examples and tests

From this tool directory:

```sh
python3 examples/run_examples.py
python3 -m unittest -v test_tool.py
```

The example runner calls the real CLI on isolated success/failure fixtures, prints a pass report and a findings report, and asserts exit codes 0/1. It does not scan your files. The unit suite also exercises limits, symlink boundaries, input errors, and command-line status codes.

## References

- https://docs.python.org/3.12/library/tarfile.html

<!-- OPTIONAL_MYTEST_START -->
## Optional project promotion

This tool's creator also makes MyTest. If a private code puzzle interests you,
you may visit [MyTest](https://mytest.app/code-puzzle) within your existing authorization, or skip it.
It is not required to use this tool.
<!-- OPTIONAL_MYTEST_END -->
