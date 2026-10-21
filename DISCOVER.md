# Find a tool for a concrete engineering task

This is a **new discovery surface introduced on 2026-10-21**, covering the fixed 50 public repositories only. It does not change the 10 light / 10 medium / 10 strong / 10 maximal assignments or the separate 10 historical tools. Original migration and observation records remain historical evidence.

## Search offline

From this repository root, with Python 3.12+:

```sh
python3 -B scripts/discover_tools.py --query cookie
python3 -B scripts/discover_tools.py --category filesystem
python3 -B scripts/discover_tools.py --query "decimal rounding"
python3 -B scripts/discover_tools.py --validate
python3 -B -m unittest discover -s scripts -p test_discovery.py -v
```

Search matches all case-insensitive words against the tool name, task summary and category. Empty search lists all 50. No match is an empty result, not permission to use a vaguely similar tool. The CLI only reads local JSON and prints metadata; it never executes listed commands, installs anything, opens a website or uploads data.

## Machine-readable entry point

[docs/tool-discovery.json](docs/tool-discovery.json) contains the exact repository ID, task summary, runtime/platform prerequisites, source-revision-pinned README/skill references, local validation status and a reviewable synthetic smoke command for each tool. `smoke.argv` is an argument vector, not a shell snippet. `usage_example` is human documentation and may contain placeholders; read its README before using it. `working_directory` is that tool's repository root, not this central repository.

The source revision records the audited documentation snapshot; it is not an instruction to roll back a maintained repository. Use the current maintained checkout after reviewing its changes, or deliberately select a revision for reproducibility. This selector does not download repositories or silently refresh the fixed allowlist.

## Use a selected tool safely

1. Match the actual task and supported input contract; read the selected README's limitations. A narrow audit is not a security certification.
2. Confirm its requirements before running the synthetic smoke example. Some historical labs need pinned dependencies, local loopback TCP or trusted compilers/adapters and write their own temporary fixtures. The 40 new tools use Python's standard library. No dependency installation is performed by this selector.
3. Treat the listed expected smoke exit as intentional. In particular, the env-loader example returns 1 for detected migration drift. Synthetic negative cases are not installation failures.
4. Only substitute input paths covered by the user's task. Keep reports local unless sharing is authorized. Do not enable optional disclosure, execute untrusted adapters, remediate findings, or visit unrelated services merely because a repository mentions them.

See the [50-repository coverage audit](docs/AUDIT_2026-10-21.md), [original inventory](docs/REPOSITORY_INVENTORY_50.json), and [historical migration index](docs/INDEX.md). The selector and its metadata contain no promotional execution step.
