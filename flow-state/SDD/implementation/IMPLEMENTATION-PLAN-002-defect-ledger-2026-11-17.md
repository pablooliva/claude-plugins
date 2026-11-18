# IMPLEMENTATION-PLAN-002-defect-ledger: The defect ledger

## Executive Summary

- **Based on Specification:** SPEC-002-defect-ledger.md
- **Research Foundation:** RESEARCH-002-defect-ledger.md
- **Start Date:** 2026-11-17
- **Author:** Claude (with the owner)
- **Completion Date:** 2026-11-18
- **Implementation Duration:** 2 days (2026-11-17 to 2026-11-18)
- **Status:** Complete ✓
- **Safety-Net Status:** 2 mid-phase handoffs at the 4f completion step (the first wrote no document; this continuation finished it)
- **Delivery mode:** per-slice  (read from SPEC frontmatter)

## Specification Alignment

### Requirements Implementation Status
- [x] REQ-001: see SPEC - Status: Complete — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-002: see SPEC - Status: Complete — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-003: see SPEC - Status: Complete — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-004: see SPEC - Status: Complete — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-005: see SPEC - Status: Complete — SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-006: see SPEC - Status: Complete — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-007: see SPEC - Status: Complete — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-008: see SPEC - Status: Complete — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-009: see SPEC - Status: Complete — SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-010: see SPEC - Status: Complete — SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-011: see SPEC - Status: Complete — SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-012: see SPEC - Status: Complete — SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-013: see SPEC - Status: Complete — SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-014: see SPEC - Status: Complete — SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-015: see SPEC - Status: Complete — SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-016: see SPEC - Status: Complete — SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-017: see SPEC - Status: Complete — SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-018: see SPEC - Status: Complete — SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-019: see SPEC - Status: Complete — SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-020: see SPEC - Status: Complete — SLICE-005 (REVIEW-SLICE-SLICE-005-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-021: see SPEC - Status: Complete — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] REQ-022: see SPEC - Status: Complete — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] SEC-001: see SPEC - Status: Validated — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] SEC-002: see SPEC - Status: Validated — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] SEC-003: see SPEC - Status: Validated — SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] SEC-004: see SPEC - Status: Validated — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] SEC-005: see SPEC - Status: Validated — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] UX-001: see SPEC - Status: Satisfied — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] UX-002: see SPEC - Status: Satisfied — SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5

### Edge Case Implementation
- [x] EDGE-001 - Handled (tested) — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-002 - Handled (tested) — SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-003 - Handled (tested) — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-004 - Handled (tested) — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-005 - Handled (tested) — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-006 - Handled (tested) — SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-007 - Handled (tested) — SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-008 - Handled (tested) — SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-009 - Handled (tested) — SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-010 - Handled (tested) — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-011 - Handled (tested) — SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-012 - Handled (tested) — SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-013 - Handled (tested) — SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-014 - Handled (tested) — SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-015 - Handled (tested) — SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-016 - Handled (tested) — SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-017 - Handled (tested) — SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-018 - Handled (tested) — SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-019 - Handled (tested) — SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] EDGE-020 - Handled (tested) — SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5

### Failure Scenario Handling
- [x] FAIL-001 - Error handling Implemented — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] FAIL-002 - Error handling Implemented — SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] FAIL-003 - Error handling Implemented — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] FAIL-004 - Error handling Implemented — SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] FAIL-005 - Error handling Implemented — SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] FAIL-006 - Error handling Implemented — SLICE-004 (REVIEW-SLICE-SLICE-004-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5
- [x] FAIL-007 - Error handling Implemented — SLICE-001 (REVIEW-SLICE-SLICE-001-defect-ledger-*); SLICE-002 (REVIEW-SLICE-SLICE-002-defect-ledger-*); SLICE-003 (REVIEW-SLICE-SLICE-003-defect-ledger-*); FINAL-CHECK-FEATURE-defect-ledger-iter1..5

## Implementation Progress

### Completed Components
- SLICE-001 to SLICE-005, all committed (HEAD `8ad6f5a`); the 4b feature code review (iter 0), its 4c fix and the 4e.5 final check (iterations 1–5, passed at iteration 5 with 0 HIGH, 0 MEDIUM, 0 LOW) are in the working tree, uncommitted; the orchestrator owns the commit.

### In Progress
- None.

### Blocked/Pending
- None. The owner decides the growth overrun (source 1.8x, tests 2.8x) at the 4h commit checkpoint.

## Test Implementation

### Web-Facing Behavior
- **Feature has web-facing behavior (UI, JS, HTMX, browser flows):** No (a stdlib Python script, markdown skill/flow files, docs)
- **E2E tests required:** N/A — no browser surface

### Unit Tests
- [x] `agent-engineering/skills/sdd-flow/scripts/tests/test_ledger.py` — SLICE-001: 19 tests (scripts run as subprocesses); whole suite `python3 -m unittest discover -s scripts/tests` from `skills/sdd-flow`: 194 tests, OK (2026-11-17, after the last edit). The 4i step's position and the owner-table row are checked by reading.
- [x] `test_ledger.py` — SLICE-002: 14 tests added (34 in the module); whole suite from `skills/sdd-flow`: 209 tests, OK (2026-11-17, after the last edit). 4i/4j, artifact-paths, SKILL.md, sdd-lite step 6/7/anti-pattern 1 and the three bodies' `No findings.` rule are checked by reading.
- [x] `test_ledger.py` — SLICE-004: 6 tests added (5 `summary`, 1 the monthly report script extracted from `skills/defect-ledger/SKILL.md` and run with a fake `bb` and a fixture plugin cache); 10 merged away by the owner's simplifications (see `### Test Changes`): 35 + 6 = 41 in the module; whole suite from `skills/sdd-flow`: 216 tests, OK (2026-11-18, after the last edit). The skill's `log`/`report`/`lookup` rules and that it runs no `bb automation` subcommand are checked by reading.

- [x] `test_ledger.py` — 4c fix of the feature review iter 0: 2 tests added (`test_add_and_reviews_number_on_after_a_very_long_id`, F1; `test_first_write_cut_short_leaves_no_setup_file_and_the_retry_works`, F2): 43 in the module; whole suite from `skills/sdd-flow`: 218 tests, OK (2026-11-18, after the last edit).

### Integration Tests
- No separate module: the integration legs live in `test_ledger.py` — the real CLI (`run_ledger(..., real=True)`: `subprocess.run([sys.executable, ledger.py, ...])`, exit code and stdout asserted), real Git (the `summary` tests build temporary repositories and commit fixtures), a held lock in a second process, a file-size limit on a child process (F2), and a fake `bb` CLI plus a fixture plugin cache at the monthly-report boundary (`test_monthly_report_script_files_one_task`). Reproduce: `python3 -m unittest discover -s scripts/tests` from `skills/sdd-flow`.

### E2E Tests (Playwright — if web-facing)
- N/A

### Test Verification Gate — Results

- **Gate Passed:** Yes
- **Suite Execution:** 222 tests run, 222 passed, 0 failed (100% pass rate; `python3 -m unittest discover -s scripts/tests` from `agent-engineering/skills/sdd-flow`, 2026-11-18, run at 4f)
- **Unit Tests:** 47 `test_` methods in `test_ledger.py` — cover REQ-001..007, 010, 012, 014..019, 021, 022 and the EDGE/FAIL/SEC/UX items of SLICE-001..004 (script halves)
- **Integration Tests:** the legs in `test_ledger.py` (real CLI processes, real Git repositories, a held lock in a second process, a fake `bb` and a fixture plugin cache) — N/A as a separate module
- **E2E Tests:** N/A — no browser surface
- **Uncovered Requirements:** none without a test or a proof by reading: the flow halves of REQ-008/009/011–014 and the Markdown procedures (the approval step, `/defect-ledger log`, the 4i/4j wording) are proven by reading under the SPEC's Tier 1 rule (DEFER-008, Tier 2 harness)

### Test Coverage
- Tests: 47 `test_` methods in `test_ledger.py` (unit and integration legs in one module, above); suite 222/222 OK
- E2E Tests: N/A (no browser surface)
- Target Coverage: as specified in SPEC
- Coverage Gaps: the flow halves of REQ-008/009/011–014 and the Markdown procedures are proven by reading (DEFER-008, Tier 2 harness); no live model run, no real BB task created

4c fix of the feature review iter 0 (Run in a scratch copy: yes):
- REQ-001/003 (F1) scripts/ledger.py:next_number: HEAD's `ledger.py` (no digit-cap lift) → test_ledger.LedgerTest.test_add_and_reviews_number_on_after_a_very_long_id (exit 1, `ValueError: Exceeds the limit (4300 digits)`); the lift alone removed → same test
- REQ-002 (F2) scripts/ledger.py:write: the setup file written in place again (`write_text`) → test_ledger.LedgerTest.test_first_write_cut_short_leaves_no_setup_file_and_the_retry_works (a 10-byte `{"loops": ` setup left behind)

SLICE-004 fix iter 5 (Run in a scratch copy: yes; each mutation below failed there, so the copy ran its own code):
- REQ-015 (F6, an `<app>` binds to the checkout its syntax names) scripts/ledger.py:cmd_summary: the "/"-in-NAME rule replaced by round 4's existing-folder rule → test_ledger.LedgerTest.test_summary_gives_an_unreadable_application_one_line (`qa=blue=2026` from the apps folder reported the other checkout); replaced by a plain first-`=` split → same test (the absolute `name=version` checkout)
- REQ-018 (F4, the implicit application keeps its root's bytes) skills/defect-ledger/SKILL.md:report: default is `summary "./$(git rev-parse --show-cdup)"` (no root name passes through a command substitution) — by executing it in scratch from a subdirectory of a committed checkout whose name ends in a newline: one record reported; the old `--show-toplevel` default reported `not reachable`. Markdown procedure; no test.

### Test Changes
- 4e.5 fix FEATURE iter 5 (strengthened, nothing loosened; UX-001 requires the line number): `test_rejected_review_derived_field_is_not_echoed` asserts `review file <name>: line 7: source ` (was `review file <name>: a finding's source`, which carried no line); its review now has a heading and a fenced FINDING before the finding, so line 7 is the physical line. Added `test_summary_tells_a_broken_local_default_ref_from_an_absent_one` (F8).
- 4e.5 fix FEATURE iter 4 (nothing loosened): `test_refused_review_files_write_nothing` asserts the refused file's name as `texts[-1][0]` (it was `CODE_REVIEW`, the last file of every earlier row) so the new `REVIEW-other.md` row is checked the same way; rows added there and in `test_bad_command_line_or_input_is_refused`, `test_bad_setup_file_is_refused_by_add_and_reviews` (a lookup per row) and `test_summary_gives_an_unreadable_application_one_line` (`showfail`).
- 4c fix of the feature review iter 0: `test_refused_review_files_write_nothing` runs every row through the real CLI (was the `nothing` row only; F6, strengthened). F7 (TEST_INTEGRITY §7, the test made real to the spec): `test_feature_chain_…` asserts the set of the twelve REQ-001 fields, not their order (REQ-001 names a set); `test_ledger_file_shapes_…` parses the appended line and checks it is `\n`-ended with no `\r`, and that all three lines read back as D-1..D-3, instead of matching the final member's bytes (EDGE-016 asks only that the file reads and the appended line is separated). No case or refusal dropped.
- SLICE-004 fix iter 5 (nothing loosened): `test_summary_gives_an_unreadable_application_one_line` gains the `blue=2026` / `qa=blue=2026` checkouts run from their folder (`run_ledger` takes `cwd`), and `assertIn("lines: 2", out)` becomes the exact per-section list of `lines:` counts (F6).
- SLICE-004 fix iter 2 (nothing loosened): case `trailing` (a committed checkout whose folder name ends in a space; heading and `open findings: 1` asserted) added to `test_summary_gives_an_unreadable_application_one_line` (F9).
- SLICE-004 fix iter 1 (nothing loosened): every `summary` test now runs the script as a process (F7; the `summary` helper's `real` flag removed, exit 0 asserted through the process boundary); cases added — `collide` in `test_summary_threshold_…` (F1), `nested`, `linked` and a newline-bearing alias and folder name in `test_summary_gives_an_unreadable_application_one_line` (F2, F8), a `preview-99.0.0` entry, a release-less cache (`no release`) and the chosen path in `test_monthly_report_script_files_one_task` (F3).
- SLICE-004 (owner's simplifications, 2026-11-18; no assertion or case dropped, every guard's mutation re-checked under the surviving name):
  - T1: tests call `ledger.main` in-process by default (`run_ledger(..., real=False)`); real processes kept for the exit-0 smoke run of each command (`test_feature_chain_…`, `test_add_open_escape`, `test_lookup_prints_at_most_five_…`, `test_close_changes_only_…`, `test_summary_counts_only_the_committed_default_branch`), the lock holder and all three writer refusals, both legs of the shell test, the command-line refusals, one exit-3 review refusal (`nothing`), the lookup and close legs of `test_invalid_ledger_…`, the bad-setup add and reviews runs and `test_lookup_failure_on_the_filesystem_…` (guard check notes 1–2).
  - T2: `test_bad_values_are_refused_with_nothing_written` and `test_field_shapes` → `test_add_values_are_accepted_or_refused_with_nothing_written` (every accepted and refused case; each refused case now runs from no ledger and from an existing one); `test_mis_shaped_where_in_a_hand_edited_ledger_is_refused_on_read` → two rows (`where with a line range`, `where with a space`) of `test_invalid_ledger_is_refused_by_add_and_reviews`, beside its `planted where` row — REQ-012's reference updated in the SPEC.
  - T3: `test_duplicate_member_in_a_hand_edited_line_is_refused_by_lookup_and_close` → the `duplicate member` row (its raw bytes) of `test_invalid_ledger_…` (lookup and close real, no-traceback check) — REQ-012's reference updated; `test_ledger_without_setup_file_is_refused` → the `missing beside the ledger` row of `test_bad_setup_file_is_refused_by_add_and_reviews`. The busy-class close test is kept whole (its condition: both halves and the no-echo check), so nothing of it is folded.
  - T4: `test_clean_review_in_each_accepted_form_writes_nothing` + `test_clean_review_as_each_body_writes_it_is_accepted` → `test_clean_review_writes_nothing` (all five fixtures); `test_slice_kind_refuses_a_file_of_another_name`, `test_review_with_no_finding_line_is_refused`, `test_duplicate_finding_id_in_one_file_is_refused`, `test_lite_brief_name_with_a_space_is_refused` → `test_refused_review_files_write_nothing` (each scenario as it was, the good file first where it was); `test_close_keeps_every_byte_outside_the_three_values` → `test_close_changes_only_status_check_added_and_closed` (five lines, explicit date, CRLF, blank line, no final newline, mode 0640; byte equality); `test_classes_key_for_a_recorded_finding_is_ignored` → the second replay of `test_second_run_over_the_same_chain_adds_nothing`.
  - T5: `assertRefused`, `assert_unavailable`, `close_data`, `DEFAULT_SETUP`; the dead `None` filter in `escape()` removed (no caller passed `None`).
- test_held_lock_refuses_add_and_reviews, test_invalid_ledger_is_refused_by_add_and_reviews, test_symlinked_ledger_path_is_refused, test_bad_command_line_or_input_is_refused: extended (nothing loosened) so `close` and `lookup` re-run their fixtures — EDGE-001/FAIL-003 (SLICE-003 re-run), REQ-001 lock test (Technical Constraints), SEC-002, REQ-022. The symlink fixture's outside file now holds one open line (was empty) so a `close` or `lookup` through the link is observable.

## Technical Decisions Log

### Architecture Decisions
- One script owns the defect ledger's reads and writes (`ledger.py`); consumers check structure only, field validity is the script's (REQ-012 amendment, 2026-11-18). See `### New Structure`.

### New Structure
- `agent-engineering/skills/sdd-flow/scripts/ledger.py` (new file, named in the brief): the defect ledger's only reader and writer; no existing script reads or writes defect records (`growth.py` gave its conventions). SLICE-001 builds `add`, `reviews --kind feature`, the shared reader (`read_ledger`, `line_problem`), the setup file (`read_setup`), the JSON input (`read_input`), the lock (`take_lock`) and the one replace (`write`); one module, no layer.
- SLICE-002, in `ledger.py`: `parsed_lines` (the lines outside fenced blocks; `parse_chain` reads only these — a separate generator because the fence state spans lines and the per-line loop in `parse_chain` already carries the section state); `KINDS` (the file-name pattern per `--kind`, used by `loop_of`, the refusal and `parse_args`); `REVIEWS_KEYS` (the `reviews` input keys, beside `ADD_KEYS`). No new file.
- SLICE-003, in `ledger.py`: `cmd_close` and `cmd_lookup` (the two new commands; they reuse `read_ledger`, `read_setup`, `check_paths`, `take_lock`, `text_problem` and `write`, whose newline fix-up now runs only when lines are appended, so `close` keeps every other byte); `CLOSE_KEYS` (beside `ADD_KEYS`); `DELIMITERS` (the two lookup delimiter lines, defined once). No new file.
- `agent-engineering/skills/sdd-flow/scripts/tests/test_ledger.py` (new file, named in the brief): one test module per script is the pattern.
- SLICE-004, in `ledger.py`: `cmd_summary`, `app_section` (one application's committed-branch read and its one-line cases), `report` (the arithmetic of REQ-015/017), `shares` (largest remainder), `git` (the one argument-list subprocess call); `parse_ledger` and `setup_of` (the existing checks of `read_ledger` and `read_setup`, split from their file reads so `summary` checks bytes from `git show` with the same code). Owner's simplifications: `open_ledger` (S1, the shared preflight of the four commands), `new_line` (S6, the line builder of `add` and `reviews`), `today`, `order` (lookup's id sort, reused by `summary`), `DATE_RE` (S8), the `COMMANDS` table (S5: flags, input keys, handler). No new layer.
- `agent-engineering/skills/defect-ledger/SKILL.md` (new file, named in the brief): the owner's skill (`report`, `log`, `lookup`) and the monthly report's `bb automation create` / `update` commands with their inline script; a skill needs its own folder.

### Implementation Deviations
- 4c fix of the feature review iter 0 (F1, REQ-001): `next_number` lifts Python 3.11+'s int/str digit limit (`sys.set_int_max_str_digits(0)`) for the process, so both writers allocate past an id of any length; (F2, REQ-002) the setup file is published by the same temp-file + rename as the defect ledger (`publish`, split from `write`), so an interrupted first write leaves no setup file.
- SLICE-001 (interpretation, REQ-021): a `user` `source` ending `, escape` must be `<brief file name>, escape` (so `BRIEF x.md, escape` is refused, as the acceptance check asks); any other `user` source is a reference under SEC-001 only.
- SLICE-001 (interpretation, UX-001/REQ-004): every refusal is one stdout line `refused: …` (so 4j builds its line from stdout alone, REQ-004), not stderr.
- SLICE-001 (RISK-002 materialised, REQ-007): the 5.4.0 code-review, final-check and slice-review bodies write neither accepted no-finding form (`No findings.` / `0 HIGH, 0 MEDIUM, 0 LOW`) into the review file — the counts go only to the `progress.md` marker. Per RISK-002 this is reported to the orchestrator and no body is edited; SLICE-001 writes nothing for a file with no `FINDING` line, and SLICE-002's refusal (exit 3) would refuse every clean real review unless this is settled.
- SLICE-002 (interpretation, SEC-001/UX-001): a `classes` value that fails the class pattern is refused naming its finding ID, not echoing the value (SEC-001: checked before it is echoed).
- SLICE-002 (interpretation, REQ-004): a blockquote line is never parsed because no finding, `Earlier Findings`, count or `No findings.` rule matches a line starting `>`; no separate blockquote guard (one was written and removed: its mutation could not fail any test, so it was dead code).
- SLICE-002 (interpretation, REQ-005): `brief` is required with `--kind lite` and refused with the other kinds (exit 2); a brief path whose file name breaks REQ-021 is refused (exit 3).
- SLICE-003 (interpretation, REQ-011): the research document's literal first line is `Bug fix: yes|no` (above the title), with a `## Bug Fix` section (cause, then class) for `yes`.
- SLICE-003 (interpretation, REQ-012): a lookup refusal prints `Seen before: unavailable — refused: <reason>` between the delimiters (the UX-001 line keeps its `refused:` prefix).
- SLICE-003 (interpretation, REQ-014): the id recorded in `progress.md` is the block `## Escape Line - D-<n>` (or `## Escape Line - refused: …`), which 4i reads to close; the design-brief spawn also gets LEDGER (`ledger.py`, docstring only) so `Missed by` points at the one loop list rather than restating it.
- SLICE-003 fix iter 1 (State Check MEDIUM F5, recorded not fixed): the approved-brief -> open move is a Markdown procedure (`design-gate.md`, `sdd-lite/SKILL.md`) with no executable flow harness; its script half (`add` of a user escape line opens it pending) is `test_add_open_escape`. A model-run flow scenario is not built in this slice. Superseded by the owner's amendment (2026-11-17): the flow half is proven at Tier 1 by the script tests plus the review reading the Markdown step; the executable flow harness is DEFER-008 (Tier 2).
- SLICE-003 fix iter 1 (F6 and F7, flow-boundary halves, owner to decide): prompt-override and approval-bypass denial at the consumer/flow boundary cannot be tested without running a model flow. Script halves are tested (`test_lookup_prints_a_planted_instruction_only_between_the_delimiters_on_one_line`; `test_close_refusals_leave_the_ledger_unchanged`, `test_close_old_id_of_a_busy_class_binds_to_its_where`); the procedures keep the write after `approve` only and close by the id recorded in `progress.md`. Reported to the orchestrator as open. Resolved by the owner's amendment (2026-11-17): SPEC-002 now says the flow halves of the iter-0 F5/F6/F7 (and iter-1 F1/F4/F5) are proven by the named script tests plus the review reading the Markdown step; the harness is DEFER-008 (Tier 2). No longer open.
- SLICE-003 (spec amendment, REQ-012, owner, 2026-11-18): field validity of every lookup row is `ledger.py`'s (validated on read, REQ-021); the design brief and sdd-lite check structure only, replacing their six-field consumer checks.
- SLICE-004 (interpretation, REQ-015): the `not evaluated` list holds the `fixed` lines with a real check (`check_added` not `none`/`pending`) that are left out only for being `unclassified` or `outside-cycle`; a `fixed` line with `none` is no candidate for *no catches since added*, so it is not listed.
- SLICE-004 (interpretation, REQ-015/017): the section's format — `## <name> — at threshold` or `— below threshold — counts only`, `<loop>: <n> (<p>%)`, `no CI` / `no <loop>`, `open escapes: <n>` and `open findings: <n>` with indented rows at threshold, `unclassified: <n> | ids`, `escape rate`, `repeated classes: <n>` with indented rows, `no catches since added: <n>` with indented rows; an unreadable application's section is `## <name>` and one line. `other` is printed only when a line has an unlisted `found_by`.
- SLICE-004 (interpretation, REQ-016): "the branch `origin/HEAD` records" is read as that remote-tracking ref (`refs/remotes/origin/<branch>`), as last fetched; `summary` never fetches.
- SLICE-004 (interpretation, REQ-019): the tracker prefix goes in the automation's `--env-json` as `DEFECT_LEDGER_TRACKER` (placeholder in the skill), beside `DEFECT_LEDGER_APPS`; the task is filed with `--description <text>` (one argument).
- SLICE-004 (owner's T1 vs TEST_INTEGRITY §1.4): most refusal cases run in-process by the owner's direction; every stdout/stderr/exit-code rule the guard check's notes 1–2 name keeps a real-process run (see `### Test Changes`).
- SLICE-004 (simplifications applied): T5, T2, S4, S8 (file-name constants, `today()`, `DATE_RE`, `strip()` once; the `isinstance` in `main`'s except kept — two clauses would need a helper and add lines), S6, T3 (two of three folds; see `### Test Changes`), T4, T1, S1, S5, M1 (sdd-lite step 1 now points to `bodies/design-brief.md` rule 19, which keeps the full rule for its spawned body; sdd-lite keeps the data-only sentence and its stderr `refused:` line). Not taken: S2, S3, S7, M2.
- SLICE-004 (completion instruction, REQ-019; fix iter 1 F5): **at 4j, this feature's completion report adds, after `Shipped:`, the line "Run these yourself to create the monthly defect ledger report:" followed by both fenced blocks of `skills/defect-ledger/SKILL.md` § The monthly report, copied whole (the `SCRIPT=…` + `bb automation create` block and the `bb automation update` block).** The flow never runs them.
- SLICE-004 fix iter 1 (F4, scope, owner-sanctioned): SLICE-004 also touched MODULE-002 — `skills/sdd-lite/SKILL.md` step 1 only, by the owner-directed M1 simplification (2026-11-18); the brief names the file. SPEC-002 SLICE-004 `Modules touched` now says so.
- SLICE-004 fix iter 1 (F6, growth, owner to decide at 4h): no further removal keeps the behaviour, guards and their proofs; the fixes for F1–F3/F7/F8 add lines. A revised budget is the owner's decision at the commit checkpoint.
- SLICE-003 fix iter 9 (F5, location): `phases/rare/resume.md` carries the escape-recovery resume rule as part of MODULE-002 (cycle writers); the flow keeps all resume rules in that file; one rule, no new file. — resolved: SPEC amended (owner, 2026-11-18) to name the file.
- 4e.5 fix FEATURE iter 4 (F4 of the void REVIEW attempt 1, review-only under DEFER-008): `/defect-ledger log`'s show-exact-input / wait / re-approve-any-change step is a Markdown procedure; `add` receives the same JSON whether the owner approved it or not, so no script guard can tell the two apart and none was added (an invented approval token would be checked by nothing). Proven by reading at Tier 1 as SPEC's DEFER-008 rule says; the executable model-run harness is DEFER-008 (Tier 2).

## Performance Metrics

- None specified beyond the Quantitative Ledger bounds in the SPEC.

## Security Validation

- [x] SEC-001 to SEC-005 proven per SPEC (see `## Security Proofs` and the final check's `## Security Verification`, iterations 1–5)

## Documentation Created

- [ ] API documentation: N/A
- [x] User documentation: skill + README (SLICE-004/005)
- [ ] Configuration documentation: N/A

## Context Management

### Essential Files Loaded
- `scripts/ledger.py`, `scripts/tests/test_ledger.py`, `skills/defect-ledger/SKILL.md`, `skills/sdd-lite/SKILL.md`, SPEC-002, `REVIEW-002-defect-ledger-20261118.md`.

## Session Notes

### Critical Discoveries
- The ledger's guards sit in one script (`ledger.py`); every flow step reaches it through one JSON input, so no value is parsed by a shell (REQ-022). The flow halves stay Markdown procedures proven by reading (DEFER-008).

### Next Priorities
1. 4h: the owner decides the growth overrun (source 1.8x, tests 2.8x) and the commit
2. 4j: surface the two monthly-report commands (see `### Implementation Deviations`; both are in the implementation summary)

## Control Site Status

| Control | Site | Status |
|---------|------|--------|

## Security Proofs

> One line per guard of a security rule (`references/security-verification.md` §1, §3): `<rule> <file>:<symbol>: <what was removed> → <failing test id>`. Written by the implementer and by fixers; the final check reads it.

SLICE-001 (Run in a scratch copy: yes; the copy was checked once to run its own code):
- SEC-001 scripts/ledger.py:text_problem: length cap check removed → test_ledger.LedgerTest.test_add_values_are_accepted_or_refused_with_nothing_written
- SEC-001 scripts/ledger.py:text_problem: printable (Unicode C*/Z*) check removed → test_ledger.LedgerTest.test_add_values_are_accepted_or_refused_with_nothing_written
- SEC-001 scripts/ledger.py:text_problem: ` | ` / `===` check removed → test_ledger.LedgerTest.test_add_values_are_accepted_or_refused_with_nothing_written
- SEC-001 (REQ-003 read) scripts/ledger.py:read_ledger: per-line `line_problem` check removed → test_ledger.LedgerTest.test_invalid_ledger_is_refused_by_add_and_reviews
- SEC-002 scripts/ledger.py:check_paths: symlink / outside-SDD refusal removed → test_ledger.LedgerTest.test_symlinked_ledger_path_is_refused
- SEC-005 (REQ-022) scripts/ledger.py:parse_args: refusal of any flag but --root/--kind/--input removed → test_ledger.LedgerTest.test_bad_command_line_or_input_is_refused
- SEC-004 (REQ-021 shapes) scripts/ledger.py:source_ok: source shape check removed → test_ledger.LedgerTest.test_add_values_are_accepted_or_refused_with_nothing_written; scripts/ledger.py:line_problem: where shape check removed → test_ledger.LedgerTest.test_add_values_are_accepted_or_refused_with_nothing_written
- UX-001 scripts/ledger.py:content_refusal: line value added to the refusal → test_ledger.LedgerTest.test_invalid_ledger_is_refused_by_add_and_reviews
- REQ-001 (lock, no lost write) scripts/ledger.py:take_lock: flock removed → test_ledger.LedgerTest.test_held_lock_refuses_add_and_reviews
SLICE-002 (Run in a scratch copy: yes; the copy was checked once to run its own code):
- REQ-004/EDGE-017 (forgery) scripts/ledger.py:parsed_lines: fence skip removed → test_ledger.LedgerTest.test_quoted_finding_lines_write_nothing
- REQ-004/FAIL-002 scripts/ledger.py:parse_chain: duplicate FINDING ID refusal removed → test_ledger.LedgerTest.test_refused_review_files_write_nothing
- REQ-007/FAIL-002 scripts/ledger.py:parse_chain: no-finding-line refusal removed → test_ledger.LedgerTest.test_refused_review_files_write_nothing
- REQ-007/FAIL-002 scripts/ledger.py:parse_chain: stated-counts check removed → test_ledger.LedgerTest.test_refused_review_files_write_nothing
- REQ-005 scripts/ledger.py:cmd_reviews: refusal of a classes/checks key naming no finding of the chain removed → test_ledger.LedgerTest.test_key_naming_no_finding_of_the_chain_refuses_the_call
- SEC-001 scripts/ledger.py:cmd_reviews: classes value pattern check removed → test_ledger.LedgerTest.test_bad_classes_or_checks_value_is_refused_even_for_an_ignored_id
- SEC-001 scripts/ledger.py:cmd_reviews: checks value text_problem (cap, ` | `) removed → test_ledger.LedgerTest.test_bad_classes_or_checks_value_is_refused_even_for_an_ignored_id
- REQ-021 scripts/ledger.py:cmd_reviews: lite brief file-name check removed → test_ledger.LedgerTest.test_refused_review_files_write_nothing
- REQ-005 scripts/ledger.py:loop_of: REVIEW-SLICE- name check for --kind slice removed → test_ledger.LedgerTest.test_refused_review_files_write_nothing
- SEC-005 (sdd-lite's close-out): every value in the JSON input through a quoted heredoc — by reading `skills/sdd-lite/SKILL.md` step 6; no guard in code.

- SEC-005's shell test (`'`, backtick, `$(touch …)` from a file and from stdin via `sh -c` quoted heredoc) passes: test_shell_characters_in_input_are_written_verbatim — no shell is used, so there is no guard to remove; the 4i caller passes every value in the JSON input (by reading).
SLICE-003 (Run in a scratch copy: yes; the copy ran its own code — every mutation below failed there):
- REQ-010 (binding) scripts/ledger.py:cmd_close: `where` differs refusal removed → test_ledger.LedgerTest.test_close_old_id_of_a_busy_class_binds_to_its_where
- EDGE-006 (fixed → fixed forbidden) scripts/ledger.py:cmd_close: not-open refusal removed → test_ledger.LedgerTest.test_close_refusals_leave_the_ledger_unchanged
- EDGE-007 (no other field changes) scripts/ledger.py:cmd_close: rewrite altered `where` too → test_ledger.LedgerTest.test_close_changes_only_status_check_added_and_closed
- SEC-001 scripts/ledger.py:cmd_lookup: class pattern check removed → test_ledger.LedgerTest.test_lookup_refuses_a_class_outside_the_pattern_between_delimiters
- SEC-001 scripts/ledger.py:cmd_lookup: 5-line cap removed → test_ledger.LedgerTest.test_lookup_prints_at_most_five_lines_oldest_first_between_delimiters
- REQ-012 scripts/ledger.py:main: delimiter lines around `Seen before: unavailable` removed → test_ledger.LedgerTest.test_lookup_refuses_a_class_outside_the_pattern_between_delimiters, test_invalid_ledger_is_refused_by_add_and_reviews
- SEC-002 scripts/ledger.py:cmd_close: check_paths removed → test_ledger.LedgerTest.test_symlinked_ledger_path_is_refused; scripts/ledger.py:cmd_lookup: check_paths removed → same test
- REQ-001 (lock) scripts/ledger.py:cmd_close: flock replaced by a no-op fd → test_ledger.LedgerTest.test_held_lock_refuses_add_and_reviews
- SEC-005 (REQ-022) scripts/ledger.py:COMMANDS: `close` allowed a value flag → test_ledger.LedgerTest.test_bad_command_line_or_input_is_refused
- REQ-003/FAIL-003 (close, lookup paths) scripts/ledger.py:read_ledger: shared guard, one path per command in test_ledger.LedgerTest.test_invalid_ledger_is_refused_by_add_and_reviews (SLICE-001's mutation of it already fails that test).
- SEC-001 consumer rule / SEC-005 callers (design-gate.md 2.5a/2.5b, end-of-feature.md 4i, sdd-lite steps 1, 3, 6, bodies/design-brief.md rule 19, artifact-paths.md): by reading; no guard in code.

SLICE-004 (Run in a scratch copy: yes; the copy was checked once to run its own code). Every guard above was re-checked after the owner's simplifications, under the test names now shown (renamed by SLICE-004's merges); each mutation failed. Where the guard moved into a shared helper (`open_ledger`: check_paths, the lock, the read check), one mutation per command path was made (the guard skipped for that command only), and each failed: check_paths for add, reviews, close, lookup → test_symlinked_ledger_path_is_refused; the lock for add, reviews, close → test_held_lock_refuses_add_and_reviews; the read check for add, reviews, close, lookup → test_invalid_ledger_is_refused_by_add_and_reviews. New:
- SEC-001 (REQ-015) scripts/ledger.py:cmd_summary: delimiter lines around each section removed → test_ledger.LedgerTest.test_summary_gives_an_unreadable_application_one_line
- REQ-003/FAIL-003 (summary path) scripts/ledger.py:app_section: `parse_ledger` replaced by a plain JSON read → test_ledger.LedgerTest.test_summary_gives_an_unreadable_application_one_line
- UX-001 (summary path) scripts/ledger.py:content_refusal: line value added to the refusal → test_ledger.LedgerTest.test_summary_gives_an_unreadable_application_one_line
- REQ-002/FAIL-005 scripts/ledger.py:app_section: setup-missing refusal removed → test_ledger.LedgerTest.test_summary_gives_an_unreadable_application_one_line
- REQ-016 (never the working tree) scripts/ledger.py:app_section: `git show` replaced by a working-tree read → test_ledger.LedgerTest.test_summary_counts_only_the_committed_default_branch
- SEC-002 (REQ-019) skills/defect-ledger/SKILL.md:inline script: application-name check removed → test_ledger.LedgerTest.test_monthly_report_script_files_one_task
- SEC-001 (REQ-019) skills/defect-ledger/SKILL.md:inline script: the data notice as the task body's first line removed → test_ledger.LedgerTest.test_monthly_report_script_files_one_task
- SEC-002 (probe) skills/defect-ledger/SKILL.md:inline script: `bb` run as one shell string → test_ledger.LedgerTest.test_monthly_report_script_files_one_task (a ledger value holding a backtick and `$(touch <marker>)` then runs; with the argument list it creates no marker)
- SEC-003 (report-only; one `bb tasks create`) and SEC-005 (the skill's `log`: exact command, JSON input, owner's approval, values from the owner's request only): by reading `skills/defect-ledger/SKILL.md`; the script test asserts exactly one `bb` call.

SLICE-004 fix iter 1 (Run in a scratch copy: yes; control mutation — threshold 30→31 — failed first, so the copy ran its own code; each mutation below failed):
- REQ-017 (F1) scripts/ledger.py:report.feature: outside-cycle key back to the bare id → test_ledger.LedgerTest.test_summary_threshold_is_five_features_or_thirty_lines
- REQ-016 isolation (F2) scripts/ledger.py:app_section: `--show-toplevel` = folder check replaced by `rev-parse --git-dir` → test_ledger.LedgerTest.test_summary_gives_an_unreadable_application_one_line
- SEC-001 (F8) scripts/ledger.py:cmd_summary: display name escaping removed → test_ledger.LedgerTest.test_summary_gives_an_unreadable_application_one_line
- SEC-002/privilege (F3) skills/defect-ledger/SKILL.md:inline script: release-only (`N.N.N`) filter removed → test_ledger.LedgerTest.test_monthly_report_script_files_one_task; chosen `ledger.py` path dropped from the printed line → same test

SLICE-004 fix iter 2 (Run in a scratch copy: yes; each mutation below failed, so the copy ran its own code):
- REQ-016 root check (F9) scripts/ledger.py:app_section: byte comparison of `--show-toplevel` with the root plus one newline put back to `.strip()` → test_ledger.LedgerTest.test_summary_gives_an_unreadable_application_one_line (`trailing` case)
- REQ-016 isolation (F2, re-checked) scripts/ledger.py:app_section: root comparison replaced by Git's exit status alone → same test (`nested` case)

SLICE-004 fix iter 4 (Run in a scratch copy: yes; the copy ran its own code — every mutation below failed there):
- REQ-015 (data exfiltration: only REQ-015 fields leave) scripts/ledger.py:report: `source` added to the open-findings rows → test_ledger.LedgerTest.test_monthly_report_script_files_one_task (sentinel `source` and `introduced_by` absent from summary stdout and the BB task body)

SLICE-004 fix iter 7 (Run in a scratch copy: yes; the copy ran its own code — every mutation below failed there):
- SEC-002 (F1, committed read) scripts/ledger.py:app_section: refusal of a mode-120000 ledger or setup entry (`git ls-tree`) removed → test_ledger.LedgerTest.test_summary_gives_an_unreadable_application_one_line (`linksetup`, `linkledger`: symlinks whose text is valid JSON; the next applications still report)
- REQ-016/FAIL-005 (F2) scripts/ledger.py:parse_ledger: `RecursionError` dropped from the decode refusal → test_ledger.LedgerTest.test_summary_gives_an_unreadable_application_one_line (`deep`: traceback, exit 1); scripts/ledger.py:setup_of: same → same test (`deepsetup`)
- SEC-001/REQ-015 (F3) scripts/ledger.py:cmd_summary: per-character escape of non-printable characters removed → same test (`x\n## alias` heading split); put back to whole-name JSON escaping → same test (`München` heading)
- F4 (`/defect-ledger log` approval): not proven by an executable test — no script-level test can tell an owner-approved `add` from an unapproved one; by reading per SPEC's Tier 1 rule (DEFER-008; the "By reading the flow text" line names `/defect-ledger log`). Left open for the owner.

SLICE-004 fix iter 8 (Run in a scratch copy: yes; the copy ran its own code — every mutation below failed there on Python 3.15.2, the two `RecursionError` mutations also on 3.12.16 and 3.9.6):
- SEC-002/FAIL-005 (F1, metadata) scripts/ledger.py:app_section: refusal when `git ls-tree` of the one resolved commit fails or omits the defect ledger removed → test_ledger.LedgerTest.test_summary_gives_an_unreadable_application_one_line (`metafail`: a PATH `git` that fails only that app's `ls-tree`; `good`, `linked`, `trailing` after it still report). Every read now uses the commit resolved once by `rev-parse --verify <ref>^{commit}`.
- SEC-002 (F1) scripts/ledger.py:app_section: mode-120000 refusal removed → same test (`linksetup`, `linkledger`), still failing.
- REQ-016/FAIL-005 (F2) scripts/ledger.py:parse_ledger and setup_of: `RecursionError` dropped, each separately → same test (`deep`, `deepsetup`; fixture now 10**6 levels — 20,000 decoded on 3.14/3.15)

SLICE-004 fix iter 9 (Run in a scratch copy: yes; the copy ran its own code — a broken section heading failed there first; every mutation below failed on Python 3.12.16):
- REQ-016/SEC-002 (F1) scripts/ledger.py:app_section: each of the three reads rebound to `branch` separately — `show <ref>:SDD/defects.jsonl`, `show <ref>:SDD/defects-setup.json`, `ls-tree <ref>` → test_ledger.LedgerTest.test_summary_gives_an_unreadable_application_one_line (`moving`: the PATH `git` advances master, right after `rev-parse … ^{commit}`, to a commit whose defect ledger is a symlink and whose setup is `[]`; the section must still be the first commit's `lines: 1`). The move fires after the commit is resolved rather than after the first `show`, so a rebound defect ledger read is caught too.
- SEC-002/FAIL-005 (F2) same symbol: the `metafail` refusal removed → same test, also when run through an interpreter path with spaces (`…/py dir/python with spaces`), where the test passes unmutated; the `ls-tree` rebinding is caught there too. The PATH `git` is now `#!/bin/sh` with `exec <shlex-quoted sys.executable> -c <code> "$@"`.

4e.5 fix FEATURE iter 2 (Run in a scratch copy: yes — installed 5.3.0 `snapshot.py scratch`, one fresh copy per mutation, removed after; every mutation below failed there, so the copy ran its own code):
- UX-001/REQ-012 (F1) scripts/ledger.py:main: the OSError refusal names only `SDD/defects.jsonl`, `SDD/defects-setup.json` or `SDD/`, never `error.filename` → put back to `str(error.filename)` → test_ledger.LedgerTest.test_lookup_failure_on_the_filesystem_is_still_a_delimited_unavailable (root `a\nb`, defect ledger a directory: lookup gave 4 stdout lines instead of 3; add must give one line)
- SEC-002/privilege (F2) skills/defect-ledger/SKILL.md:inline script: a release is kept only when its `ledger.py` resolves to the same place under the resolved cache → predicate removed → test_ledger.LedgerTest.test_monthly_report_script_files_one_task (a `9.0.0` entry linking out of the cache and a `9.1.0` script linking out were chosen; the task body became `WRONG`)
- SEC-001/REQ-004 (F3) scripts/ledger.py:parsed_lines: split on the normalized `\n` only → put back to `str.splitlines()` → test_ledger.LedgerTest.test_quoted_finding_lines_write_nothing (U+2028, U+2029, U+0085, VT, FF, FS, GS, RS in prose: F9 was written)
- SEC-002 (F4) scripts/ledger.py:check_paths: `is_symlink()` removed alone → test_ledger.LedgerTest.test_symlinked_ledger_path_is_refused (`ledger link in`, `setup link in`: links to a file inside SDD/ were written through); the real-path check removed alone → same test (`linked parent`: a plain defect ledger under a linked SDD/ was written)
- SEC-002 (F5) skills/defect-ledger/SKILL.md:inline script: the application arguments joined into one → test_ledger.LedgerTest.test_monthly_report_script_files_one_task (a second application at `two words`; `app` became not reachable and `two` lost its section)

4e.5 fix FEATURE iter 3 (Run in a scratch copy: yes — installed 5.3.0 `snapshot.py scratch`, PYTHONDONTWRITEBYTECODE=1; the copy ran its own code: `parsed_lines` broken first, 21 errors; each mutation alone in the full suite, then removed):
- SEC-001/REQ-004/EDGE-017 (F6) scripts/ledger.py:parsed_lines: closing-fence tail `strip(" \t")` → put back to `strip()` → test_ledger.LedgerTest.test_quoted_finding_lines_write_nothing (`fence tail` U+2028, U+2029, U+0085, VT, FF, FS, GS, RS: a fence closed early and F9 was written; 8 failures)
- same class, scripts/ledger.py:parse_chain: `## ` heading text `strip(" \t")` → `strip()` → test_ledger.LedgerTest.test_earlier_line_outside_its_section_is_ignored (`## Earlier Findings` + U+2028 / U+0085 opened the Earlier section; F3 became fixed); the `bare` line `strip(" \t")` → `strip()` → test_ledger.LedgerTest.test_refused_review_files_write_nothing (`No findings.` + U+2028, `0 HIGH, 0 MEDIUM, 0 LOW` + U+0085 accepted as a clean review)
4e.5 fix FEATURE iter 4 (Run in a scratch copy: yes — installed 5.3.0 `snapshot.py scratch`; each mutation alone, the named test run, the fixed file put back; every mutation failed there, so the copy ran its own code):
- SEC-001/REQ-007/FAIL-002 (F7) scripts/ledger.py:parse_chain: markers matched on `raw.rstrip(" \t")` (unindented only) → put back to `strip(" \t")` → test_ledger.LedgerTest.test_refused_review_files_write_nothing (`indented clean line`, `tab-indented zero counts`: chain accepted, F4 written, exit 0)
- REQ-004/REQ-005 (F3) scripts/ledger.py:loop_of: feature code review must be `REVIEW-<###>-…` → put back to any `REVIEW-` but `REVIEW-SLICE-` → same test (`feature kind, out-of-kind REVIEW- name`: written as code-review, exit 0)
- UX-001/REQ-022 (F11) scripts/ledger.py:read_input: `RecursionError` dropped from the decode refusal → test_ledger.LedgerTest.test_bad_command_line_or_input_is_refused (`nested past the decoder's limit`: traceback, exit 1)
- UX-001 (F8) scripts/ledger.py:cmd_reviews: content diagnostic (file, field, rule) put back to `input_refusal` → test_ledger.LedgerTest.test_rejected_review_derived_field_is_not_echoed (review-derived source value echoed)
- REQ-016/FAIL-005 (F2) scripts/ledger.py:app_section: unresolvable recorded branch refusal removed → test_ledger.LedgerTest.test_summary_tells_an_unreadable_default_branch_from_an_absent_ledger (`no ledger yet`); `ledger.returncode` dropped from the read refusal → test_ledger.LedgerTest.test_summary_gives_an_unreadable_application_one_line (`showfail`)
- REQ-001 (F5) scripts/ledger.py:take_lock: `.records/.gitignore` (`*`) write on folder creation removed → test_ledger.LedgerTest.test_first_write_creates_the_records_ignore_file_and_keeps_an_existing_folder_as_it_is
- REQ-002 (F6) scripts/ledger.py:setup_of: `"user" in loops` removed → test_ledger.LedgerTest.test_bad_setup_file_is_refused_by_add_and_reviews (`no user loop`: lookup succeeded)

4e.5 fix FEATURE iter 5 (Run in a scratch copy: yes — installed 5.3.0 `snapshot.py scratch`; each mutation alone, the named test run, the fixed file put back; every mutation failed there, so the copy ran its own code):
- REQ-016/FAIL-005 (F8) scripts/ledger.py:app_section: default-branch selection falls through only on a call git reports as absent (exit 1, no stderr); any other result, a broken ref included, gives the `refused: its default branch cannot be read` line → condition put back to any non-zero exit → test_ledger.LedgerTest.test_summary_tells_a_broken_local_default_ref_from_an_absent_one (local `main` broken, no `origin/HEAD`, no `master`: `no ledger yet`; the next application still reported)
- UX-001 (F9) scripts/ledger.py:parsed_lines/parse_chain/cmd_reviews: each kept line carries its physical line number through fence filtering; a finding keeps its first FINDING line's number; the review-content refusal is `content_refusal` (file, line, field, rule; no value) → numbers taken after filtering → test_ledger.LedgerTest.test_rejected_review_derived_field_is_not_echoed (CLI; `line 4` instead of `line 7`)

## Slice Progress

| SLICE-ID  | Name | Status | Acceptance check | Test result | Notes |
|-----------|------|--------|------------------|-------------|-------|
| SLICE-001 | A cycle's review findings reach the defect ledger | Complete | `test_ledger.py` — a fixture code review plus two final-check rounds (shaped as the 5.4.0 bodies write them) produces one line per HIGH or MEDIUM ID w (full check: SPEC `## Delivery Slices` SLICE-001) | passing | SDD/.records/reviews/REVIEW-SLICE-SLICE-001-defect-ledger-iter1-2026-11-17.md |
| SLICE-002 | Every review chain and sdd-lite's review are recorded; a bad review is refused | Complete | `test_ledger.py` — slice chains with `F1` in two slices give two lines (full check: SPEC `## Delivery Slices` SLICE-002) | passing | SDD/.records/reviews/REVIEW-SLICE-SLICE-002-defect-ledger-iter1-2026-11-17.md |
| SLICE-003 | The bug-fix rule | Complete | `test_ledger.py` — `lookup` prints the header and at most 5 lines oldest first, `Seen before: none` for a class with none (full check: SPEC `## Delivery Slices` SLICE-003) | passing | SDD/.records/reviews/REVIEW-SLICE-SLICE-003-defect-ledger-iter11-2026-11-18.md |
| SLICE-004 | The owner's way in — summary, `/defect-ledger`, the monthly automation | Complete | `test_ledger.py` — `summary` over a temp repo whose default branch is `master`, with a feature branch checked out and an uncommitted line: only the co (full check: SPEC `## Delivery Slices` SLICE-004) | passing | SDD/.records/reviews/REVIEW-SLICE-SLICE-004-defect-ledger-iter9-2026-11-18.md |
| SLICE-005 | Docs match | Complete | both diagrams show the new steps (4i ledger step, the approve line, the lookup, sdd-lite's close-out) (full check: SPEC `## Delivery Slices` SLICE-005) | passing | SDD/.records/reviews/REVIEW-SLICE-SLICE-005-defect-ledger-iter2-2026-11-18.md |

**Status enum (binding):** `Not Started`, `In Progress`, `Complete`. A slice stuck in its review loop stays `In Progress`; the stop (`## Awaiting Slice Resolution` in `progress.md`) says why. The slice-start phase flips Status to `In Progress`; the orchestrator sets `Complete`, `Test result`, and `Notes` as its last edit before the slice's commit.

## Implementation Completion Summary

### What Was Built
A committed defect ledger per application (`SDD/defects.jsonl` plus `SDD/defects-setup.json`) written by one stdlib script, `agent-engineering/skills/sdd-flow/scripts/ledger.py` (`add`, `reviews`, `close`, `lookup`, `summary`). sdd-flow writes the review chains at 4i (feature and per-slice) and sdd-lite at its close-out; a bug-fix task is recognised in research, looked up by class, shown in the brief as `## Escape` with *Seen before*, opened on approval and closed at the end.

The owner's way in is the new `/defect-ledger` skill (`report`, `log`, `lookup`) and a monthly report-only BB automation whose `bb automation create` and `update` commands the skill and the completion report show; the flow never runs them. Docs, both diagrams, the root `CLAUDE.md` and the glossary match, at version 5.5.0.

Key decisions: values reach the script only as one JSON object (no shell parsing), `close` binds to the defect's `where`, `summary` reads only the committed default branch from one pinned commit, and every refusal is one `refused: …` line that never echoes review-derived text.

### Requirements Validation
All requirements of SPEC-002 are implemented and tested or proven by reading:
- Functional Requirements: 22/22 Complete
- Performance Requirements: none in this spec
- Security Requirements: 5/5 Validated
- User Experience Requirements: 2/2 Satisfied

### Test Coverage Achieved
- **Test Suite Result:** 222/222 tests passed (100%)
- **Unit Tests:** 47 `test_` methods in `test_ledger.py` (a coverage percentage is not measured; SPEC names none)
- **Integration Tests:** legs in `test_ledger.py` (real CLI, real Git, second-process lock, fake `bb`)
- **E2E/Playwright Tests:** N/A — no browser surface
- **Edge Case Coverage:** 20/20 EDGE-XXX scenarios covered (script halves tested; flow halves by reading, DEFER-008)
- **Failure Scenario Coverage:** 7/7 FAIL-XXX scenarios handled

### Inline Investigation Summary
- Searches run (Grep/Glob): not tracked by this completion run (it read the documents named in its prompt and extracted sections)
- Files read for analysis: the plan, the SPEC, the tier plan, the final check's security tables (iterations 4 and 5), `skills/defect-ledger/SKILL.md` § The monthly report
