# Kill test — currents, fix commits 2026-08-16..2026-11-16 (49 candidates, 628 commits)

Labels are a reading of each commit message plus git blame of the lines it changed. Unconfirmed by the owner.

## Escapes — reached production, or the operator's first real run (22 defects)
| Fix | Introduced by | Found by | Class | Loop that should have caught it |
|---|---|---|---|---|
| 610bf144 | fc5e45ee (SPEC SLICE-003, agentbrief) | weekly digest eval, 8 stories published | source-chrome-as-content | publish-time content gate / source fixture test |
| 5291b456 | (added rule; agentbrief chrome) | production census | source-chrome-as-content | same |
| 60a2f970 | (no editorial-boundary scoping) | published digest | source-chrome-as-content | same |
| 80c6408c | 204ffbcf (SPEC-065) | publishable artifact | bad-title-published | title-shape predicate at publish (made one in the fix) |
| 3a3866a7 | 204ffbcf / 989b9a88 (SPEC-065/074) | live Downstream feed | bad-title-published | same |
| f4523d5b | 204ffbcf | digest | unbounded-llm-output | output-shape check at sink |
| 8b224747 | f1976fa8 / 54f5c68d | deploy tracker guard refused 4 deploys | tracker-leak | the guard worked, but after merge; run it in tests |
| e569c6bc | b4240187 (SPEC-075) | dropped lead story in production | overmatching-identity | test with multi-story roundup fixture |
| 0de173b5 | c28fd929 (SPEC-012) | one tweet killed the run | overmatching-identity | pattern unit test |
| 2614e496 | c28fd929 (SPEC-012) | live X items retired | transient-as-permanent | error-mapping test |
| b230dc20 + 490af1bc | b6dc539d (SPEC-073) | empty digest section 08-24 | transient-as-empty | retry/empty-response test |
| f4ac6a8b | df5f6593 (SPEC-088) | production metric 55% | metric-window-mismatch | unit test over aged rows |
| 9352dded | f1ad282e | operator sent to wrong probe | probe-wrong-diagnosis | probe test with disabled source |
| 148e650f | b4240187 | prod health note | probe-wrong-diagnosis | render test |
| 275cbbe2 | 989b9a88 (SPEC-074) | daily false yellow | alarm-on-low-volume | probe test on quiet window |
| 68f610fe | 989b9a88 (SPEC-074) | daily false yellow | alarm-on-low-volume | same |
| 73be4ae9 | c28fd929 | daily false yellow | probe-reads-unready-page | integration (live page) |
| 646ba596 | 983dd17c (SPEC-094) | found later: alert went nowhere | alert-goes-nowhere | deploy review / final check |
| 0c30b2ac + 40c5ce5b | e199b321 (SPEC-095) | first production capture | untested-external-contract | contract test against recorded response |
| 8faff70d | 951cd8c6 (SPEC-106 close) | first real run after close | fake-diverges-from-real-data | test fixture from a real file |
| 942d64b9 | 02e52a76 | first dry run on the Mac (before damage) | dev-writes-prod-sink | config review / test |
| bd38f183 | (external: senders moved 10-23) | noticed after a week of 0 records | silent-zero-ingest | doctor probe on zero ingest |

## Test-suite defects found after merge (6) — currents has no CI and no pre-commit hook
74bace5d (test patch leaks into global datetime), 6dcdcb09 (test depends on today's date), b36e45d2 (test passes only after another test opened the DB), 5b070d34 (tests read the live production DB), 0c2d0c44 (Linux-only assumptions, found on the Mac), b7ce8ff9 (an existing ADR test failed on master: not run before merge). Class: test-isolation (5), check-not-run (1). Loop: CI on a clean machine.

## Caught before production by a rehearsal, after reviews passed (SPEC-100 cluster, SPEC-097)
214a39be ("two review iterations accepted it"; scratch rehearsal found it), 79481fb2, ef62948a, 25730307, f2fd3298 (live gate run). 3b1e29b7 / 88ff8d2a is a requirement withdrawn, not a code defect. 94fb57c3/87695588, 79dc4d51, 88ff8d2a are duplicates (parallel threads).

## Not escapes
In-cycle review fixes: 61280086, 23d3aae3, 6e5a780e, 072ae653, 6f660027 (HIGH caught by the SPEC-084 review), 9390da29. Unclear: 30a91a1b (no message body), 099bffc8 (prompt wording, no failure).
