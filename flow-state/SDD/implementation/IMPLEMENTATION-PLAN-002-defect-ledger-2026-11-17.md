# IMPLEMENTATION-PLAN-002-defect-ledger: The defect ledger

## Executive Summary

- **Based on Specification:** SPEC-002-defect-ledger.md
- **Research Foundation:** RESEARCH-002-defect-ledger.md
- **Start Date:** 2026-11-17
- **Author:** Claude (with the owner)
- **Status:** In Progress (scaffold only; no slice started)
- **Delivery mode:** per-slice  (read from SPEC frontmatter)

## Specification Alignment

### Requirements Implementation Status
- [ ] REQ-001: see SPEC - Status: Not Started
- [ ] REQ-002: see SPEC - Status: Not Started
- [ ] REQ-003: see SPEC - Status: Not Started
- [ ] REQ-004: see SPEC - Status: Not Started
- [ ] REQ-005: see SPEC - Status: Not Started
- [ ] REQ-006: see SPEC - Status: Not Started
- [ ] REQ-007: see SPEC - Status: Not Started
- [ ] REQ-008: see SPEC - Status: Not Started
- [ ] REQ-009: see SPEC - Status: Not Started
- [ ] REQ-010: see SPEC - Status: Not Started
- [ ] REQ-011: see SPEC - Status: Not Started
- [ ] REQ-012: see SPEC - Status: Not Started
- [ ] REQ-013: see SPEC - Status: Not Started
- [ ] REQ-014: see SPEC - Status: Not Started
- [ ] REQ-015: see SPEC - Status: Not Started
- [ ] REQ-016: see SPEC - Status: Not Started
- [ ] REQ-017: see SPEC - Status: Not Started
- [ ] REQ-018: see SPEC - Status: Not Started
- [ ] REQ-019: see SPEC - Status: Not Started
- [ ] REQ-020: see SPEC - Status: Not Started
- [ ] REQ-021: see SPEC - Status: Not Started
- [ ] REQ-022: see SPEC - Status: Not Started
- [ ] SEC-001: see SPEC - Status: Not Started
- [ ] SEC-002: see SPEC - Status: Not Started
- [ ] SEC-003: see SPEC - Status: Not Started
- [ ] SEC-004: see SPEC - Status: Not Started
- [ ] SEC-005: see SPEC - Status: Not Started
- [ ] UX-001: see SPEC - Status: Not Started
- [ ] UX-002: see SPEC - Status: Not Started

### Edge Case Implementation
- [ ] EDGE-001 - not started
- [ ] EDGE-002 - not started
- [ ] EDGE-003 - not started
- [ ] EDGE-004 - not started
- [ ] EDGE-005 - not started
- [ ] EDGE-006 - not started
- [ ] EDGE-007 - not started
- [ ] EDGE-008 - not started
- [ ] EDGE-009 - not started
- [ ] EDGE-010 - not started
- [ ] EDGE-011 - not started
- [ ] EDGE-012 - not started
- [ ] EDGE-013 - not started
- [ ] EDGE-014 - not started
- [ ] EDGE-015 - not started
- [ ] EDGE-016 - not started
- [ ] EDGE-017 - not started
- [ ] EDGE-018 - not started
- [ ] EDGE-019 - not started
- [ ] EDGE-020 - not started

### Failure Scenario Handling
- [ ] FAIL-001 - not started
- [ ] FAIL-002 - not started
- [ ] FAIL-003 - not started
- [ ] FAIL-004 - not started
- [ ] FAIL-005 - not started
- [ ] FAIL-006 - not started
- [ ] FAIL-007 - not started

## Implementation Progress

### Completed Components
- None yet.

### In Progress
- **Current Focus:** none (scaffold only)
- **Files Being Modified:** none
- **Next Steps:** SLICE-001, driven by the orchestrator

### Blocked/Pending
- None.

## Test Implementation

### Web-Facing Behavior
- **Feature has web-facing behavior (UI, JS, HTMX, browser flows):** No (a stdlib Python script, markdown skill/flow files, docs)
- **E2E tests required:** N/A — no browser surface

### Unit Tests
- [x] `agent-engineering/skills/sdd-flow/scripts/tests/test_ledger.py` — SLICE-001: 19 tests (scripts run as subprocesses); whole suite `python3 -m unittest discover -s scripts/tests` from `skills/sdd-flow`: 194 tests, OK (2026-11-17, after the last edit). The 4i step's position and the owner-table row are checked by reading.
- [x] `test_ledger.py` — SLICE-002: 14 tests added (34 in the module); whole suite from `skills/sdd-flow`: 209 tests, OK (2026-11-17, after the last edit). 4i/4j, artifact-paths, SKILL.md, sdd-lite step 6/7/anti-pattern 1 and the three bodies' `No findings.` rule are checked by reading.

### Integration Tests
- [ ] N/A unless a slice's acceptance check names one

### E2E Tests (Playwright — if web-facing)
- N/A

### Test Coverage
- Unit Tests: 0 tests
- Integration Tests: 0
- E2E Tests: N/A
- Target Coverage: as specified in SPEC
- Coverage Gaps: all (not started)

### Test Changes
None.

## Technical Decisions Log

### Architecture Decisions
- None yet.

### New Structure
- `agent-engineering/skills/sdd-flow/scripts/ledger.py` (new file, named in the brief): the defect ledger's only reader and writer; no existing script reads or writes defect records (`growth.py` gave its conventions). SLICE-001 builds `add`, `reviews --kind feature`, the shared reader (`read_ledger`, `line_problem`), the setup file (`read_setup`), the JSON input (`read_input`), the lock (`take_lock`) and the one replace (`write`); one module, no layer.
- SLICE-002, in `ledger.py`: `parsed_lines` (the lines outside fenced blocks; `parse_chain` reads only these — a separate generator because the fence state spans lines and the per-line loop in `parse_chain` already carries the section state); `KINDS` (the file-name pattern per `--kind`, used by `loop_of`, the refusal and `parse_args`); `REVIEWS_KEYS` (the `reviews` input keys, beside `ADD_KEYS`). No new file.
- `agent-engineering/skills/sdd-flow/scripts/tests/test_ledger.py` (new file, named in the brief): one test module per script is the pattern.

### Implementation Deviations
- SLICE-001 (interpretation, REQ-021): a `user` `source` ending `, escape` must be `<brief file name>, escape` (so `BRIEF x.md, escape` is refused, as the acceptance check asks); any other `user` source is a reference under SEC-001 only.
- SLICE-001 (interpretation, UX-001/REQ-004): every refusal is one stdout line `refused: …` (so 4j builds its line from stdout alone, REQ-004), not stderr.
- SLICE-001 (RISK-002 materialised, REQ-007): the 5.4.0 code-review, final-check and slice-review bodies write neither accepted no-finding form (`No findings.` / `0 HIGH, 0 MEDIUM, 0 LOW`) into the review file — the counts go only to the `progress.md` marker. Per RISK-002 this is reported to the orchestrator and no body is edited; SLICE-001 writes nothing for a file with no `FINDING` line, and SLICE-002's refusal (exit 3) would refuse every clean real review unless this is settled.
- SLICE-002 (interpretation, SEC-001/UX-001): a `classes` value that fails the class pattern is refused naming its finding ID, not echoing the value (SEC-001: checked before it is echoed).
- SLICE-002 (interpretation, REQ-004): a blockquote line is never parsed because no finding, `Earlier Findings`, count or `No findings.` rule matches a line starting `>`; no separate blockquote guard (one was written and removed: its mutation could not fail any test, so it was dead code).
- SLICE-002 (interpretation, REQ-005): `brief` is required with `--kind lite` and refused with the other kinds (exit 2); a brief path whose file name breaks REQ-021 is refused (exit 3).

## Performance Metrics

- None specified beyond the Quantitative Ledger bounds in the SPEC.

## Security Validation

- [ ] SEC-001 to SEC-005 proven per SPEC (see `## Security Proofs`)

## Documentation Created

- [ ] API documentation: N/A
- [ ] User documentation: skill + README (SLICE-004/005)
- [ ] Configuration documentation: N/A

## Context Management

### Essential Files Loaded
- None yet.

## Session Notes

### Critical Discoveries
- None yet.

### Next Priorities
1. SLICE-001
2. SLICE-002
3. SLICE-003

## Control Site Status

| Control | Site | Status |
|---------|------|--------|

## Security Proofs

> One line per guard of a security rule (`references/security-verification.md` §1, §3): `<rule> <file>:<symbol>: <what was removed> → <failing test id>`. Written by the implementer and by fixers; the final check reads it.

SLICE-001 (Run in a scratch copy: yes; the copy was checked once to run its own code):
- SEC-001 scripts/ledger.py:text_problem: length cap check removed → test_ledger.LedgerTest.test_bad_values_are_refused_with_nothing_written
- SEC-001 scripts/ledger.py:text_problem: printable (Unicode C*/Z*) check removed → test_ledger.LedgerTest.test_bad_values_are_refused_with_nothing_written
- SEC-001 scripts/ledger.py:text_problem: ` | ` / `===` check removed → test_ledger.LedgerTest.test_bad_values_are_refused_with_nothing_written
- SEC-001 (REQ-003 read) scripts/ledger.py:read_ledger: per-line `line_problem` check removed → test_ledger.LedgerTest.test_invalid_ledger_is_refused_by_add_and_reviews
- SEC-002 scripts/ledger.py:check_paths: symlink / outside-SDD refusal removed → test_ledger.LedgerTest.test_symlinked_ledger_path_is_refused
- SEC-005 (REQ-022) scripts/ledger.py:parse_args: refusal of any flag but --root/--kind/--input removed → test_ledger.LedgerTest.test_bad_command_line_or_input_is_refused
- SEC-004 (REQ-021 shapes) scripts/ledger.py:source_ok: source shape check removed → test_ledger.LedgerTest.test_field_shapes; scripts/ledger.py:line_problem: where shape check removed → test_ledger.LedgerTest.test_field_shapes
- UX-001 scripts/ledger.py:content_refusal: line value added to the refusal → test_ledger.LedgerTest.test_invalid_ledger_is_refused_by_add_and_reviews
- REQ-001 (lock, no lost write) scripts/ledger.py:take_lock: flock removed → test_ledger.LedgerTest.test_held_lock_refuses_add_and_reviews
SLICE-002 (Run in a scratch copy: yes; the copy was checked once to run its own code):
- REQ-004/EDGE-017 (forgery) scripts/ledger.py:parsed_lines: fence skip removed → test_ledger.LedgerTest.test_quoted_finding_lines_write_nothing
- REQ-004/FAIL-002 scripts/ledger.py:parse_chain: duplicate FINDING ID refusal removed → test_ledger.LedgerTest.test_duplicate_finding_id_in_one_file_is_refused
- REQ-007/FAIL-002 scripts/ledger.py:parse_chain: no-finding-line refusal removed → test_ledger.LedgerTest.test_review_with_no_finding_line_is_refused
- REQ-007/FAIL-002 scripts/ledger.py:parse_chain: stated-counts check removed → test_ledger.LedgerTest.test_review_with_no_finding_line_is_refused
- REQ-005 scripts/ledger.py:cmd_reviews: refusal of a classes/checks key naming no finding of the chain removed → test_ledger.LedgerTest.test_key_naming_no_finding_of_the_chain_refuses_the_call
- SEC-001 scripts/ledger.py:cmd_reviews: classes value pattern check removed → test_ledger.LedgerTest.test_bad_classes_or_checks_value_is_refused_even_for_an_ignored_id
- SEC-001 scripts/ledger.py:cmd_reviews: checks value text_problem (cap, ` | `) removed → test_ledger.LedgerTest.test_bad_classes_or_checks_value_is_refused_even_for_an_ignored_id
- REQ-021 scripts/ledger.py:cmd_reviews: lite brief file-name check removed → test_ledger.LedgerTest.test_lite_brief_name_with_a_space_is_refused
- REQ-005 scripts/ledger.py:loop_of: REVIEW-SLICE- name check for --kind slice removed → test_ledger.LedgerTest.test_slice_kind_refuses_a_file_of_another_name
- SEC-005 (sdd-lite's close-out): every value in the JSON input through a quoted heredoc — by reading `skills/sdd-lite/SKILL.md` step 6; no guard in code.

- SEC-005's shell test (`'`, backtick, `$(touch …)` from a file and from stdin via `sh -c` quoted heredoc) passes: test_shell_characters_in_input_are_written_verbatim — no shell is used, so there is no guard to remove; the 4i caller passes every value in the JSON input (by reading).

## Slice Progress

| SLICE-ID  | Name | Status | Acceptance check | Test result | Notes |
|-----------|------|--------|------------------|-------------|-------|
| SLICE-001 | A cycle's review findings reach the defect ledger | Complete | `test_ledger.py` — a fixture code review plus two final-check rounds (shaped as the 5.4.0 bodies write them) produces one line per HIGH or MEDIUM ID w (full check: SPEC `## Delivery Slices` SLICE-001) | passing | SDD/.records/reviews/REVIEW-SLICE-SLICE-001-defect-ledger-iter1-2026-11-17.md |
| SLICE-002 | Every review chain and sdd-lite's review are recorded; a bad review is refused | Complete | `test_ledger.py` — slice chains with `F1` in two slices give two lines (full check: SPEC `## Delivery Slices` SLICE-002) | passing | SDD/.records/reviews/REVIEW-SLICE-SLICE-002-defect-ledger-iter1-2026-11-17.md |
| SLICE-003 | The bug-fix rule | Not Started | `test_ledger.py` — `lookup` prints the header and at most 5 lines oldest first, `Seen before: none` for a class with none (full check: SPEC `## Delivery Slices` SLICE-003) | — | — |
| SLICE-004 | The owner's way in — summary, `/defect-ledger`, the monthly automation | Not Started | `test_ledger.py` — `summary` over a temp repo whose default branch is `master`, with a feature branch checked out and an uncommitted line: only the co (full check: SPEC `## Delivery Slices` SLICE-004) | — | — |
| SLICE-005 | Docs match | Not Started | both diagrams show the new steps (4i ledger step, the approve line, the lookup, sdd-lite's close-out) (full check: SPEC `## Delivery Slices` SLICE-005) | — | — |

**Status enum (binding):** `Not Started`, `In Progress`, `Complete`. A slice stuck in its review loop stays `In Progress`; the stop (`## Awaiting Slice Resolution` in `progress.md`) says why. The slice-start phase flips Status to `In Progress`; the orchestrator sets `Complete`, `Test result`, and `Notes` as its last edit before the slice's commit.
