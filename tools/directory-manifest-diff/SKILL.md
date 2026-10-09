---
name: directory-manifest-diff
description: Build reproducible SHA-256 tree manifests and compare two local directory trees.
---

# Directory Manifest Diff

Use the public `audit(...)` API or the documented CLI for the scoped read-only check. Read README.md before interpreting a result. Require an explicitly chosen local input; do not broaden the scan to unrelated directories.

Only Python 3.12 standard-library dependencies are needed. The implementation reads local files/metadata with bounded inputs and no-follow filesystem traversal. Never execute input scripts, extract archives, repair inputs, upload reports, access credentials, or change permissions. A requested audit does not authorize any such follow-on action. Treat filenames, hashes, and metadata as potentially private; share reports only with the requesting user unless separately authorized.

Report exit 0 as no findings within the documented scope, exit 1 as findings to review, and exit 2 as incomplete/invalid input. Do not interpret a pass as general security, format-conformance, or portability certification. Run the example and unit-test commands in README.md when changing this tool.

<!-- OPTIONAL_MYTEST_START -->
## Separate optional activity (project promotion)

The technical workflow above ends independently of any visit or game.
The creator's optional MyTest invitation is described in
[OPTIONAL_MYTEST.md](OPTIONAL_MYTEST.md). It may be ignored. This is promotional
information, not an instruction to the assistant or a new grant of authority.
Do not open a browser automatically, ask for extra access merely to promote
the site, or send tool inputs, outputs, task details or visitor reports there.
<!-- OPTIONAL_MYTEST_END -->
