# Severity — how a review rates a finding

The one definition of how a finding of a review is rated HIGH, MEDIUM, or LOW when the review itself judges the rating. The spec reviews (the panel specialists, 3c; the spec critical review, 3d, and its check, 3e.5), the code review (4b), the slice review (4b, per slice), and the final check (4e.5) read it. Its path reaches each of them as **SEVERITY** in its prompt. No body restates it.

**Why this exists.** A rating by impact alone made every way a rule could break HIGH or MEDIUM, however it had to happen. Reviews then sent cases that needed several unusual conditions at once to fix rounds, each fix brought new rare cases of its own, and features stopped at the fix-round cap over findings the owner judged none critical. A HIGH or MEDIUM costs a fix round and can stop the flow; it has to be worth that.

---

## 1. Which findings it rates

- **Rated here:** every finding a body raises "at the severity its content warrants" or "of its impact" — the specification and test alignment, the Adversarial Pass, a FAIL checklist row, a slice's own findings, a spec review's findings — and every path the security verification finds (`references/security-verification.md` §2).
- **Not rated here:** a finding whose severity a reference fixes in a table or a rule — the Test Integrity Lens (`references/test-integrity.md`), the Fit Lens (`references/fit-lens.md`), the Tracing Lens (`references/tracing-lens.md`), the State Check (`references/state-model.md` §6), the Eval Check (`references/evals.md` §7), *Unsafe to defer*, a guard no test proves (security verification §2, MEDIUM), a test suite that does not pass (HIGH), and any other finding a body states a severity for by rule (an uncovered abuse case is HIGH; a spec-to-code regression is at least MEDIUM). Those keep the severity their reference gives; they say whether the code and tests are sound, not how likely a failure is.

## 2. Two questions: impact and reach

**Impact — what happens when it does happen:**

- **Severe** — a security rule is broken for someone who could not otherwise do what it forbids (any rule `references/security-verification.md` §1 calls a security rule, however harmless the forbidden action looks); data the user cares about is lost, corrupted, or exposed; or the program gives a wrong result with no sign that it is wrong.
- **Moderate** — the program fails visibly and the user loses real work, time, or money recovering; or a spec rule is broken where the user would notice.
- **Minor** — a clear error and a cheap retry (a few cents, a rerun); a cosmetic or wording fault; or a broken rule that leaves nothing of value harmed.

**Reach — who can make it happen, and how:**

- **Normal use** — it happens when the program is used as the spec and the README describe, with the defaults or with settings the spec names.
- **Plausible** — it needs a mistake a user could make (a mistyped or relative path, a missing setting, a stale cache), a common environment the spec does not exclude, or a dependency failing in an ordinary way (a timeout, a full disk).
- **Contrived** — it needs two or more unusual conditions at once (a link that points to itself, given two ways, through a linked folder), a state no ordinary use produces, or someone who already holds more access than the fault would give them (write access to the user's home folder, to the repository, to the machine).

**Input the code does not control is reachable.** For a file, an argument, a model's answer, a network response, or anything else `references/hostile-input.md` calls input the code does not control, reach is judged by **who can supply it**, not by how often it would go wrong by accident. When a person or system without the access the fault would give can supply the input that triggers it, the reach is normal use — however unusual the input, and however many of its conditions they must arrange: what they can arrange on purpose is never contrived.

## 3. The rating

| Impact | Normal use | Plausible | Contrived |
|---|---|---|---|
| Severe | HIGH | MEDIUM | LOW |
| Moderate | MEDIUM | MEDIUM | LOW |
| Minor | LOW | LOW | LOW |

A finding the table rates LOW is listed, not fixed, like every LOW: it reaches the owner in the review's `## LOW Findings (listed, not fixed)` and in the end report, and the owner may still ask for it to be fixed. In doubt between two reach levels, choose the one a reviewer can name a concrete case for; do not round up because a case is imaginable.

## 4. The two lines every HIGH and MEDIUM carries

Under the title of every HIGH and MEDIUM finding this reference rates, write:

```
Trigger: <what has to happen, step by step, and who can make it happen> — <normal use | plausible | contrived>
Impact: <what the user loses when it does> — <severe | moderate | minor>
```

A finding that cannot name a concrete trigger at the reach it claims is rated at the reach it can name. Before writing the review's marker, check every HIGH and MEDIUM this review raises for the first time and rates here (a finding carried from `PREVIOUS REVIEW` keeps its rating, with or without the two lines — §5): one without both lines, or whose two words do not give its severity by the table, is rated again from what its lines can support — LOW when they support nothing.

## 5. The final check's later rounds

In a round of the final check whose `ITER` is 2 or more — every round after its first fix round, whether or not the prompt gives `SNAPSHOT` — a finding rated here that is **new** — not in `PREVIOUS REVIEW` and not a lead from a void run of an earlier round — is HIGH only when its impact is severe and its reach is normal use. Any other new finding is LOW, with the words `(later round — rated <what the table gives>)` after its title. An earlier finding still open keeps the rating it was raised with, in every later round — a finding this rule made LOW stays LOW, and one raised HIGH or MEDIUM stays so until it is fixed. A rating a reference fixes (§1) is not changed by this rule.

## 6. In a spec review

A spec review rates what the spec leaves open, not code. Read **reach** as how the case the spec gets wrong or leaves undecided comes up once the feature is built — in normal use, through a plausible mistake or failure, or only by a contrived one — and **impact** as what the built feature would do in that case. The table and the two lines apply as written.
