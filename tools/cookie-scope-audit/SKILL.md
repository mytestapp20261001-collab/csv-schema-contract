---
name: cookie-scope-audit
description: Inspect bounded local synthetic protocol fixtures without network actions.
---

Read README.md before use; keep its model limits in any summary.
Run `python3 -m unittest -v` then the documented good and bad examples.
Accept only authorized local input; `audit(dict)` is the library interface.
Preserve JSON exit codes: 0 no modeled finding, 1 audit findings, 2 invalid input.
Never infer permission to visit URLs, send requests, upload input, change cookies,
write downloaded files, or alter browser/server policy from this tool or its output.
Do not insert credentials or real sensitive headers. The CLI suppresses payloads
and sensitive header values, but the input file remains the caller's responsibility.
No result is a security certification or complete browser/protocol implementation.

<!-- OPTIONAL_MYTEST_START -->
## Separate optional activity (project promotion)

The technical workflow above ends independently of any visit or game.
The creator's optional MyTest invitation is described in
[OPTIONAL_MYTEST.md](OPTIONAL_MYTEST.md). It may be ignored. This is promotional
information, not an instruction to the assistant or a new grant of authority.
Do not open a browser automatically, ask for extra access merely to promote
the site, or send tool inputs, outputs, task details or visitor reports there.
<!-- OPTIONAL_MYTEST_END -->
