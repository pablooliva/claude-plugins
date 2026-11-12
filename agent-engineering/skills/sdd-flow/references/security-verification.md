# Security Verification — the final check's adversarial pass

The one definition of the security verification that the final check (4e.5, `bodies/final-check.md`) runs once per feature, after every fix has landed. The final check and its fix read it; the implementer bodies read §3 so the tests they write already meet it; completion reads §5. The path reaches each of them as **SECURITY** in its prompt. No body restates it.

**Why this exists.** What the flow's earlier proof found that mattered were security gaps — a policy bypassed by an alternate spelling, upstream error text passed through to a user, a check skipped when a setting is unset — found by a reader trying to break the code, not by counting the places a rule is enforced. This pass keeps that reader and nothing else. Every other rule of the spec is held by an ordinary test, which the Test Integrity Lens checks (`references/test-integrity.md`).

---

## 1. What a security rule is

The verification checks these, and only these:

1. **Every SPEC requirement whose ID starts `SEC-`.**
2. **Any other SPEC requirement that states a security rule** — who may do what, what may be read, written, recorded, or shown, what is refused — under a `REQ`, `EDGE`, `FAIL`, or other ID. The verifier decides from the text; in doubt it is one.
3. **With the `agent_security` gate open** (the prompt passes CATALOG): each abuse case of the catalog's §5 that the panel review's `Abuse cases to cover` block names, or that the code's agentic surface makes relevant — keyed `ABUSE-<case>` (e.g. `ABUSE-approval-bypass`), its rule being the case's expected denial.

The review lists every rule it checked, with its key, at the top of its `## Security Verification` section. A spec with no security rule is checked all the same: the section says `No security rule in this spec` and the pass raises nothing of its own.

**Not a rule here:** the application's tracing rules (stated once by the tracing standard and checked by the Tracing Lens), unless the SPEC restates one with a `SEC-` ID; and the plugin's own files in the application — `evals/run.py` and the files `/observability-init` rendered — which are tested where their templates are made. Neither is broken, nor tested, by this pass. A rule whose path runs through a plugin file is checked in the application's own code on that path.

## 2. What the verification looks for

For each rule, read the code that must hold it, from every entry point a user or another system can reach, and look for **a path on which the rule does not hold.** Try at least these, and record each tried:

- **Respellings and aliases** — the same forbidden thing under another name: case, Unicode or URL encoding, a path with `..` or a link, an alias, a second field that means the same.
- **Error paths** — the rule holds on success but not when a dependency fails, a parse fails, a timeout fires, or an exception is caught and passed over.
- **Unset settings** — a check that is skipped, or allows, when its setting is empty or absent.
- **Missing configuration** — a default the code relies on that the deployment does not set; a file, key, or allowlist that is absent.
- **Values echoed back** — upstream error text, internal names, paths, keys, or another user's data returned to a caller or written to a log a user can read.

Each path found is **one finding: HIGH** when a user or caller can reach it, **MEDIUM** when it needs a setting or state the spec says the deployment does not have. A rule that holds on every path tried, but that no test would catch if its guard were removed (§3), is **MEDIUM** — the code is right today and nothing keeps it right.

## 3. What a proving test is

A rule's guard is **proven** when a test drives the real entry point with the adverse input or condition really present (not mocked away), asserts the denial the rule states, and **fails when the guard is removed.** To show it:

1. Make a scratch copy of the working tree (`references/test-integrity.md` §8).
2. In the copy, delete or neutralise the guard — one guard at a time.
3. Run the test in the copy. It must fail, for the reason the rule gives.
4. Remove the copy.

Never mutate the working tree itself. Record each mutation as one line: `<key> <file>:<symbol>: <what was removed> → <failing test id>`. A guard shared by several paths needs one test per path the verification found, not one per guard.

## 4. Rounds, fixes, and what is left

- **A finding is fixed by changing the code and adding a proving test (§3),** and the fix shows the failure — its return and the IMPLEMENTATION-PLAN's `### Security Proofs` list carry the mutation line. A finding is never closed by a test alone when the path is open, nor by a code change with no test.
- **At most two fix rounds:** verify → fix → verify → fix → verify. A verification after a fix checks the earlier findings first, then reads what the fix changed for new paths.
- **What is still open after the third verification stops the flow** for the owner (`## Awaiting Final Check Resolution`, `phases/implementation-whole-feature.md` → 4e.5).

## 5. What the review writes

```markdown
## Security Verification

Rules checked: SEC-001, SEC-004, REQ-012 (states who may export), ABUSE-approval-bypass
Reviewed by: <model>

| Rule | Paths tried | Path where it does not hold | Proving test (mutation line) | Result |
|---|---|---|---|---|
| SEC-001 | respelling, error path, unset setting | — | SEC-001 src/api/export.py:check_scope: removed scope check → tests/api/test_export.py::test_refuses_other_tenant | holds, proven |
| SEC-004 | respelling, echoed value | upstream error text returned at src/gateway.py:proxy | — | finding 3 (HIGH) |
```

Findings go in the review's one numbered `## Findings` list, tagged `[security]`. Completion copies the table's last state into the implementation summary's `### Security Verification`.
