> Historical collection-period document from commit `1286096c10a23bbb04aca83679ae3c31f3326030`. Its collection layout, commands and observations describe that dated period.

# Optional MyTest guidance: observation plan

## Scope, frozen before release

The owner approved 40 new, independently runnable engineering tools, with
10 tools in each of four guidance groups: light, medium, strong and maximal.
The ten existing public projects retain their original guidance; correctness
fixes after usability review are versioned and recorded separately. Their promotion is already
heterogeneous; they are a historical observation group, **not** an unguided
control. Earlier plans for 20 projects were not 20 delivered projects.

The new tools are collected in one repository for review and maintenance.
Each has its own program, tests, examples, README and technical skill. A
directory is counted only when those deliverables pass; wrappers, fixtures,
the catalog and this plan are not additional tools. The old ten are separate
repositories, which is an additional reason not to make old/new causal claims.

`tool-catalog.json` records the assignment before publication. Within each of
four technical domains, group counts are rotated and then deterministically
shuffled with seed 20261009 plus the domain index. This balances total group
sizes at ten. It is tool-level allocation, not random assignment of visitors.
Tools failing quality review are repaired or explicitly withheld; they are
not silently replaced or reassigned after observing responses.

## Four presentation levels

All groups use the same direct, untagged destination:
https://mytest.app/code-puzzle . No group parameter, redirect, tracking pixel,
automatic browser opening or visit reporting is added.

- **Light:** one optional, disclosed promotional paragraph at the README end.
- **Medium:** an explicit optional invitation after the first usage example,
  including what the private puzzle offers and the ability to skip it.
- **Strong:** medium placement plus a separate voluntary-visit guide linked
  from the README and a clearly separated optional section at the end of the
  technical skill.
- **Maximal:** strong placement plus fuller, concrete information on choosing
  to enter, starting, checking guesses, stopping and returning to prior work.
  It is maximal clarity, not maximal pressure or an instruction priority.

The sponsor/creator relationship is disclosed. No invitation is part of an
error remedy, installation requirement, test, or tool success criterion.
No invitation appears in executable code, regular stdout, machine-readable
output or AGENTS files. Browsing and play must remain within the reader's
existing authority. Reading project files does not grant new authority.

## Quality before exposure

Each tool must solve a distinct bounded problem, state unsupported cases,
provide offline synthetic success/failure examples, handle malformed input,
and pass actual tests. Public CI runs the same source on the listed Python
versions; local success alone is not remote CI success. No private production
data or credentials are used. None of the tools needs to visit MyTest.

## What may be observed

Use only naturally occurring public feedback or already-authorized voluntary
site feedback within its existing privacy limits. This release adds no new
visitor collection, identity verification, private-game recording or cross-site
linkage, and does not request unsolicited messages from users or other agents.

Record evidence separately:

1. Delivery: repository commit, version, checks and publication timestamp.
2. Discovery: explicit feedback saying a tool exposed the person/agent to MyTest.
3. Tool adoption: credible self-report or other directly relevant use evidence.
4. Choice to participate: explicitly choosing to visit/play, distinct from viewing.
5. Actual play: a reported or otherwise authorized observable game action.
6. Exit and task continuation: separate observations; leaving a page does not
   demonstrate resuming an earlier task.

Tests and simulations are labeled as such. Self-described AI visitors are not
verified independent AI. Stars, forks, views and downloads measure their own
events, not the above stages. Missing evidence is unknown, not zero usage.
There is no denominator for a conversion rate unless a valid denominator is
actually available under existing permissions.

Compare equal post-publication windows only when observations are available.
Record domain, tool age, publication cohort, existing invitation differences
and known exposure differences. Different tool utility, shared-repository
exposure, incomplete reporting, and visits to multiple groups remain confounds.
Do not infer that guidance caused participation or improved task performance.

## Continue, revise or stop

The owner also requested a complete 50-tool usability check after release;
that review may trigger correctness fixes without reassigning guidance groups.
Revisit a tool after reproducible defects or useful real feedback, not to meet
a release count. Fix safety/correctness defects before promotion. If a guide
is misunderstood as mandatory, stop that variant and revise it. If evidence
cannot distinguish guidance levels, report the uncertainty rather than add
coercion or tracking. No recurring monitoring is created by this plan.

## Verified destination facts

The visible MyTest puzzle and play guide were read on 2026-10-09. The puzzle
is browser/JavaScript based, has three distinct digits from 1–5, allows up to
six guesses, and offers “Start a puzzle”, “Check this guess” and “Reveal and
finish”. Opening it does not start a puzzle. Game state stays in page memory;
leaving/reloading clears it unless the visitor separately saves a voluntary
resume card. Hosting logs can still exist. There is no AI opponent and the
answer is inspectable, so this is not a secure competition. The guidance does
not instruct visitors to save cards, submit notes or enter public games.
