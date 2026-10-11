# Standalone repository migration — publication handoff

The 39 newly created standalone repositories are accepted at the exact IDs,
commits, root trees and CI runs in [their publication receipts](PUBLISHED_REPOSITORIES_39.json).
The coordinator's mapping is dated `2026-10-10T14:54:33.148Z`. Read-only official
GitHub repository/main/job queries independently confirmed all 39 IDs, commits,
trees and 78 successful CPython 3.12.14/3.13.5 jobs during this document preparation.
The reused csv repository is now renamed and accepted at its fixed published
commit, with two successful Python CI jobs, as recorded in
[csv deployment acceptance](CSV_DEPLOYMENT_ACCEPTANCE.md).

The [complete inventory](REPOSITORY_INVENTORY_50.json) contains exactly 40 accepted
split-tool identities plus ten unchanged historical identities. All 50 IDs and
HEADs were rechecked on 2026-10-11; original grouping and source evidence remain
unchanged. The observation task has not been updated by this publication.

## Fixed source and unchanged csv behavior

The sole original source is [the fixed public collection commit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/commit/1286096c10a23bbb04aca83679ae3c31f3326030),
tree `7871f1cce8288ab969037a45fa6b21c9027098b0`. Its complete official recursive
tree contains 309 blobs: 296 tool files and 13 collection files. Nine csv files
and 287 files in the other 39 tools account for those 296 original tool files.
The [fixed catalog](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/tool-catalog.json),
[original baseline](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/docs/historical-baseline.json)
and [full audit](https://github.com/mytestapp20261001-collab/mytest-engineering-toolbox/blob/1286096c10a23bbb04aca83679ae3c31f3326030/docs/FULL_AUDIT_2026-10-09.json)
remain the source evidence. The audit JSON blob is `648526bf89bee29f95ae1da5a685b7d8ff6c039c`.

The complete csv source directory is raised to repository root. Its nine original
files, algorithm, examples, tests, verification record, README and technical skill
remain byte-identical. The homepage keeps only its original light invitation,
including exact wording, placement and order. MIT LICENSE and `.gitignore`, pinned
Actions, two-version matrix, `contents: read`, `persist-credentials: false`, README
runner and preservation checker remain unchanged from the tested v1 packaging.
Only neutral docs/catalog/status records change in this final candidate.
`apply_guidance.py` is not run. No feature or stronger promotion is added.

The final handoff contains the complete csv tree, an external per-file manifest
(SHA256, Git blob SHA-1 and mode), its independently calculated root tree SHA and
actual local test logs. The root tree hash and a future commit's own hash are not
embedded inside that tree: doing so would create self-referential hash changes.
Later csv receipts can name the already published prior commit in a short normal
successor document; no recursive sequence of self-hash corrections is needed.

## Historical versions and ancestry

[historical-baseline.json](historical-baseline.json) retains its original bytes,
verification date and initial SHA prefixes. The separate
[2026-10-10 identity snapshot](HISTORICAL_IDENTITIES_2026-10-10.json) reports current
public HEADs and checks them against the unchanged
[post-audit validated commits](history/FULL_AUDIT_2026-10-09.json).
Seven old repositories still match their initial prefixes. HAR, resume-download
and Protobuf match the later 2026-10-09 audit corrections; all ten match validated
commits. Those three earlier correctness fixes are not modifications from this
migration. The old ten were not rerun or changed by this final preparation.

Preserve the reused repository's full `beb0e5d` → `ba546c1` → `1286096` ancestry
through a normal parent commit. Re-read current main before committing; reconcile
any advance rather than forcing or discarding it. Do not delete/recreate this
identity or recreate the former collection name. Preserve its redirect so the
fixed-SHA source links remain available after rename. Historical collection files
remain in old commits; the new root contains only csv and neutral migration docs.

Rename, normal publication and remote acceptance are documented in the dated
csv receipt. The coordinator separately owns the existing observation prompt.
The main MyTest project and historical repositories were not modified.

## Observation and verification boundaries

Keep collection-period and standalone-period observations separate. csv inherits
the collection's repository identity, Git history, past exposure and additional
neutral-index traffic. These differences remain confounds when comparing it with
new identities. Record each tool's individual publication time and use equal
standalone windows only where authorized evidence supports them.

The four new groups retain assignment date `2026-10-09`, seed `20261009`, technical
domains and exactly ten tools per group. This is tool-level allocation, not visitor
randomization. The old ten retain heterogeneous original invitations and dated
qualitative labels; they are historical observations, not an unguided control.
Do not pool them into the four-group denominators or produce causal rankings.

Delivery/CI, discovery, tool adoption, voluntary participation, actual play and
return to prior work are separate evidence. Stars/forks/views/downloads and test
traffic do not establish games, natural visits or work improvements. Missing
evidence is unknown. No new site tracking, identity verification, origin/source
collection, cross-site linkage, unsolicited contact or game recording is added.

Local csv acceptance covers Linux x86_64 CPython 3.12.14 and 3.13.5 at repository
root and external working directories. It does not claim Windows/macOS,
production/private-input, hostile-concurrency or exhaustive security conformance.
Actual csv remote CI passed at the fixed commit documented in the deployment receipt.
