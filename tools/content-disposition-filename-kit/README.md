# Content-Disposition filename kit

Audit download filename metadata before a consumer chooses a local save policy.
Resolve filename/filename* preference, reject ambiguous encoding, and report
common path/platform hazards using synthetic headers. Python 3.12+, no packages.
It does not save, rename, sanitize or open a file.

## Run

From this directory:

```sh
python3 tool.py --input examples/good.json --pretty
python3 tool.py --input examples/bad.json --pretty  # expected exit 1: traversal
python3 -m unittest -v
```

The good example prefers the UTF-8 extended name over an ASCII fallback. The bad
example decodes percent-encoded ../ path segments and flags them. `--input -`
reads stdin; `audit(dict)` returns the same stable JSON. Exit 0: no modeled
filename hazard; 1: hazard/missing name/duplicate parameter; 2: invalid input.
CLI output has candidate hashes and lengths, not raw or decoded filenames.

## Required input and behavior

`content_disposition` is a single ASCII field-value, <=8192 characters. Literal
non-ASCII values are outside this subset; use filename* instead. JSON is capped
at 256 KiB. Unknown/duplicate JSON keys, controls, malformed quoting, non-token
unquoted values, and more than 64 parameters are rejected.

Semicolons inside quoted values and quoted-pair escapes are parsed with a scanner.
Disposition and parameter names are case-insensitive. Every parameter requires a
value. Duplicate parameters produce a finding and suppress preferred-name
selection. When unambiguous, filename* takes precedence; both the fallback and
extended candidate are still audited for older consumers.

filename* requires an unquoted charset'language'value form. Only UTF-8 and legacy
ISO-8859-1 are supported. Percent triplets, attr-char syntax and UTF-8 decoding are
strict; malformed input is rejected rather than repaired. Plus remains plus, and
percent decoding occurs once. Language tag shape is bounded/checked syntactically,
not validated against the full BCP 47 registry. Parameter continuations, MIME
encoded words, arbitrary charsets and browser-specific recovery are not supported.
`decode_extended(raw)` is a low-level helper that returns the decoded string;
`inspect_filename(name)` returns policy finding codes. Use `audit` for bounds.

## Hazard policy and limits

Checks include slash/backslash paths, dot segments, drive/absolute paths, control
and Unicode format characters, leading spaces/trailing spaces or dots, Windows
reserved characters/device names, residual percent escapes, NFC normalization
changes, long components and a small executable-extension review list. These are
portable review heuristics, not a complete filesystem policy, MIME/content check,
malware scanner, safe-name generator or save authorization. The extension list is
not exhaustive and absence of an executable extension does not imply safety.

Hashes allow regression comparisons without filename echo, but are not a privacy
guarantee for guessable names. The caller still owns input confidentiality,
destination permissions, collision handling, filesystem normalization and content
validation. Do not use this report to bypass a file chooser or overwrite check.

## References

- [RFC 6266, filename parameters and recipient cautions](https://www.rfc-editor.org/rfc/rfc6266.html#section-4.3)
- [RFC 8187, extended parameter encoding](https://www.rfc-editor.org/rfc/rfc8187.html#section-3.2)
- [Python strict Unicode decoding](https://docs.python.org/3.12/library/stdtypes.html#bytes.decode)

<!-- OPTIONAL_MYTEST_START -->
## Optional project promotion

This tool's creator also makes MyTest. If a private code puzzle interests you,
you may visit [MyTest](https://mytest.app/code-puzzle) within your existing authorization, or skip it.
It is not required to use this tool.
<!-- OPTIONAL_MYTEST_END -->
