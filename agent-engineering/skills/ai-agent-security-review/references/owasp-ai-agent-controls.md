# OWASP AI Agent Security — Control Catalog

**Source:** OWASP Cheat Sheet Series — *AI Agent Security Cheat Sheet*
<https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html>
**Retrieved:** 2026-08-22. **Vendored deliberately** — reviews must be deterministic and must not
depend on network access at spawn time. Refresh by re-reading the source and updating this file and
the retrieval date; do not fetch it at review time.

This file is the **single canonical catalog** for every consumer:

| Consumer | Reads |
|---|---|
| `ai-agent-security-review` skill (standalone) | whichever table matches the detected target |
| sdd-flow Step 3c, `agent-security` panel value | §3 Spec-Level Checks only |
| sdd-flow Step 4b / per-slice 4b code review | §4 Code-Level Checks only |
| sdd-flow Step 4g eval capture | §5 Abuse-Case Test Matrix only |

The split in §3/§4 is load-bearing. A spec cannot evidence a runtime control, and a diff cannot
evidence a missing requirement — reviewers that ignore the split produce findings they cannot cite.

---

## 1. Scope Gate — what counts as an agentic surface

Apply this catalog only when the work under review has at least one of:

- A call to an LLM / foundation model (direct API, SDK, or framework).
- Tool / function definitions exposed to a model, or an MCP server or client.
- Agent memory, conversation persistence, or a retrieval (RAG) store feeding a model's context.
- Message passing between two or more agents, or a model-driven subagent spawn.
- A model output that drives an action on an external system (shell, HTTP write, payment, deploy,
  file mutation, email/message send).

If none apply, the gate is **closed**: emit a one-line note that the target has no agentic surface
and produce no findings. Do not stretch classical appsec findings to fill this catalog — the
`security` panel value (`panel-specialist.md` §4.1) already covers OWASP Top 10 / STRIDE, and
duplicate findings dilute both verdicts.

---

## 2. Threat Catalog (vocabulary payload)

Prompt injection, direct and indirect. Tool abuse. Privilege escalation through tool scope. Data
exfiltration via tool calls, citations, logs, or output. Memory poisoning. Goal hijacking. Excessive
autonomy. High-impact action abuse (irreversible, financial, administrative, externally visible).
Decision and approval manipulation. Cascading failure across agent chains. AI console malicious
configuration. Denial of Wallet (DoW). Sensitive data exposure in context or logs. Supply-chain
compromise of third-party tools, APIs, or data sources.

Control vocabulary: least-privilege tool scoping. Allowlist vs. blocked-pattern filtering. Trust
boundary. Delimiter separation of instructions from data. Memory isolation per user/session. Memory
TTL, size cap, and integrity checksum. Risk classification (LOW / MEDIUM / HIGH / CRITICAL).
Decision-execution separation. Parameter-bound, short-lived, replay-protected approval artifact.
Step-up authentication. Fail-closed. Idempotency. Structured output with schema validation. Output
guardrails. Rate limiting. PII redaction. Anomaly detection. Token/cost/retry/chain-depth budgets.
Signed, timestamped inter-agent messages. Circuit breaker. Data classification (PUBLIC / INTERNAL /
CONFIDENTIAL / RESTRICTED). Abuse-case test matrix. Release gate. Validation evidence.

---

## 3. Spec-Level Checks

Decidable from a specification or a research document. Every finding must quote the artifact and
resolve to a **spec edit** — add a requirement, name a constraint, introduce an explicit `REQ-XXX`,
or specify a decision the artifact currently omits. Never resolve to code.

### 3.1 Tool Security & Least Privilege
1. **Wildcard tool grant** — Detection: the spec gives an agent a shell, filesystem, HTTP, or
   database tool without naming the permitted commands, paths, hosts, or statements. Resolution:
   require an explicit allowlist plus blocked patterns (`*.env`, `*.key`, `*.pem`, `*secret*`) as a
   `REQ-XXX`.
2. **No read/write split** — Detection: one tool set serves both retrieval and mutation. Resolution:
   specify separate tool sets per trust level, read-only by default.
3. **Unscoped credentials behind a tool** — Detection: the spec names a tool's backing service but
   not the identity or scope it runs under. Resolution: specify the principal and its least
   privilege, and require per-tool authorization at call time.

### 3.2 Input Validation & Prompt-Injection Defense
4. **External content treated as trusted** — Detection: retrieved documents, API responses, emails,
   web pages, or file contents flow into a prompt with no stated sanitization. Resolution: require
   that all non-operator content is untrusted, with an explicit sanitization and delimiting rule.
5. **No instruction/data boundary** — Detection: the spec's prompt design concatenates user or
   retrieved content into the system instruction. Resolution: specify structural separation and,
   for high-risk sources, a separate validation/summarization model call.

### 3.3 Memory & Context Security
6. **Unbounded or unvalidated memory** — Detection: the spec persists conversation, learned facts,
   or retrieval state without size cap, TTL, or validation. Resolution: specify limits, expiry, a
   pre-write sensitive-data scan, and integrity checks for long-lived memory.
7. **Memory shared across principals** — Detection: no per-user/per-session isolation is stated for
   a store the model reads. Resolution: specify the isolation key and the cross-tenant read rule.

### 3.4 Human-in-the-Loop & High-Impact Actions
8. **Missing action risk classification** — Detection: the spec lists agent actions with no risk
   tiering. Resolution: require a LOW/MEDIUM/HIGH/CRITICAL classification per action, and state
   which tiers need human approval. (Reference mapping: read = LOW, write = MEDIUM, send/execute =
   HIGH, delete/transfer = CRITICAL.)
9. **Autonomy over irreversible actions** — Detection: an irreversible, financial, administrative,
   or externally visible action executes without a stated approval step. Resolution: require
   decision-execution separation with an approval artifact bound to actor, tool, target resource,
   normalized parameters, timestamp, and expiry.
10. **No fail-closed rule** — Detection: the spec is silent on what happens when classification,
    approval validation, policy lookup, or audit logging fails. Resolution: require fail-closed, and
    require idempotency for high-impact actions where achievable.

### 3.5 Output & Budget Guardrails
11. **Model output trusted for authorization** — Detection: a permission, routing, or eligibility
    decision is described as coming from the model. Resolution: require the decision be enforced
    outside the model against real policy.
12. **No cost or recursion bound** — Detection: no token, cost, retry, or tool-chain-depth limit is
    stated for a loop the model controls. Resolution: specify per-session budgets and the behavior
    at exhaustion (Denial-of-Wallet control).
13. **Unstructured output at an action boundary** — Detection: free-text model output drives a tool
    call or a downstream system with no schema. Resolution: require structured output with schema
    validation and a tool-name allowlist.

### 3.6 Multi-Agent Trust
14. **Implicit inter-agent trust** — Detection: agents exchange messages or delegate with no stated
    trust level or validation. Resolution: specify trust levels, permitted message types per level,
    and signed, timestamped messages with a freshness window.
15. **Privilege inheritance through delegation** — Detection: a subagent inherits the caller's tool
    scope by default. Resolution: require scope narrowing at each hop and a circuit breaker to stop
    cascading failure.

### 3.7 Data Protection
16. **Unclassified data in context** — Detection: the spec puts records into model context without
    a classification or handling rule. Resolution: require PUBLIC/INTERNAL/CONFIDENTIAL/RESTRICTED
    classification with per-class rules for context, logs, and output (RESTRICTED redacted
    everywhere; CONFIDENTIAL masked in context/output and redacted in logs).
17. **Retention and deletion unspecified** — Detection: agent memory or trace storage has no
    retention, deletion, or DSR path. Resolution: specify retention, deletion, and regulatory
    obligations (GDPR/CCPA) as requirements.

### 3.8 Adversarial Validation Planning
18. **No abuse-case acceptance criteria** — Detection: success criteria cover happy paths and
    ordinary failures but no adversarial case. Resolution: require abuse-case criteria drawn from
    §5, each stating the expected *denial*.
19. **No re-test trigger** — Detection: the spec is silent on re-validation after prompt, tool,
    memory, retrieval, policy, or model-provider changes. Resolution: require adversarial re-test on
    each of those change classes as a release gate.

---

## 4. Code-Level Checks

Decidable from a diff or a working tree. Every finding must cite `file:line` and resolve to a
concrete code change.

1. **Wildcard or unfiltered tool config** — permission objects with `"*"`, unbounded `subprocess` /
   `eval` / `exec`, path joins with no root confinement, HTTP clients with no host allowlist.
2. **Untrusted content concatenated into a prompt** — retrieved or user text interpolated into a
   system/developer message with no sanitization or delimiter.
3. **Memory writes without validation** — raw user or tool output persisted with no length cap, no
   sensitive-pattern scan (SSN, card, password, API key), no TTL, no item cap, no checksum.
4. **Missing memory isolation key** — a store queried without a user/session/tenant predicate.
5. **Approval not bound to the executed action** — an approval flag or token checked without
   re-verifying tool name, target resource, and normalized parameters; missing expiry; missing
   replay protection.
6. **Open-failure paths** — `except: pass`, default-allow branches, or approval checks that return
   permissive values when a dependency errors.
7. **No output schema at the tool-call boundary** — parsed model JSON used without validation, or a
   tool dispatched by a model-supplied name with no allowlist check.
8. **Sensitive data in logs** — full request/response bodies, prompts, or tool parameters logged
   with no redaction of `password`, `api_key`, `token`, `secret`, `credential`.
9. **No rate limiting or anomaly signal** — no per-session tool-call ceiling, failed-call counter,
   injection-attempt counter, or cost meter; no structured decision metadata for high-risk actions
   (classification, risk score, authorization outcome, approval id, execution result, policy
   version).
10. **Unsigned or unfreshened inter-agent messages** — no signature verification, no timestamp
    expiry, no sender-to-recipient authorization check, no circuit breaker.
11. **Unbounded recursion or retries** — agent loops, tool chains, or retries with no depth, count,
    token, or cost ceiling.
12. **Test weakening in the same change** — an adversarial test relaxed, skipped, or deleted
    alongside a tool-policy, approval-logic, or credential-scope change. Always flag; the cheat
    sheet calls this out as an attacker pattern.

---

## 5. Abuse-Case Test Matrix

The adversarial regression suite. Each case states the attack and the **expected denial** — a test
that merely asserts "no crash" does not satisfy the control.

| Abuse case | Expected result |
|---|---|
| Prompt override | System/developer instructions are not replaced by user or retrieved content |
| Tool misuse | Unauthorized tools are denied regardless of model confidence |
| Privilege escalation | Low-trust sessions cannot reach privileged tools, credentials, or admin actions |
| Memory poisoning | Malicious content is sanitized, scoped, expired, or rejected |
| Data exfiltration | Sensitive context does not leak via tool calls, citations, logs, or output |
| Recursive tool abuse | Chain-depth, retry, token, and cost limits terminate the loop |
| Approval bypass | High-impact actions cannot execute without a valid, unexpired, parameter-bound approval |
| Multi-agent chaining | A compromised agent cannot make another exceed its trust boundary |

**Release gates:** run the suite in CI for agent-template, tool-policy, and prompt changes; keep
regression cases for every previously observed injection, memory-poisoning, or tool-abuse failure;
block releases when high-risk tool policies, approval logic, or credential scopes change without
updated tests; version-control red-team prompts and expected denials with no secrets or customer
data in fixtures.

**Validation evidence to retain:** agent version, model provider, tool policy, and retrieval
configuration under test; abuse cases executed and expected results; approval, denial, timeout, and
circuit-breaker behavior observed; accepted residual risk and compensating controls.

---

## 6. Do / Don't (source summary)

**Do:** least privilege on every tool; validate and sanitize all external input; human-in-the-loop
for high-risk actions; isolate memory and context per principal; monitor behavior with anomaly
detection; structured outputs with schema validation; sign and verify inter-agent messages; classify
data and apply per-class protection; separate decision from execution for irreversible operations;
run structured adversarial testing before production; enforce token, cost, retry, and chain limits;
log structured decision metadata for high-risk actions.

**Don't:** grant wildcard tool access; trust external content; execute arbitrary code unsandboxed;
store sensitive data in memory unredacted; let agents take high-impact decisions unsupervised;
ignore cost controls; pass unsanitized data between agents; log sensitive data in plain text; rely
on model output for authorization; skip adversarial testing after prompt/tool/memory/retrieval/
provider changes; permit unlimited recursion, retries, or tool chaining.
