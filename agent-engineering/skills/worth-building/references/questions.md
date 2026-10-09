# The Six Questions

The standard `worth-building` applies. Each question has: what it asks, how to answer it from evidence, what a failing answer looks like, and what the failure usually means for the verdict.

Answer from the target's own words, the conversation, and code or data you can read. An answer you cannot ground is **unknown**, with a line saying what would settle it.

## 1. Kill test

**What is the cheapest run that could show the idea is wrong, and does it come first?**

- Name the run concretely: the input, what is run on it, the output, and the result that would mean stop.
- Ask whether it can run today. Look for data that already holds the answer, an eval that already exists, a script that is one small change away.
- Find where the plan puts it. Count what is built before it.
- The stop condition is written before the run, in a sentence. That is all the protection a first look needs.

**Fails when:** the first run that tests the idea comes after most of the build; or the plan has no such run and only tests that its own parts work.

**Usually means:** reorder.

## 2. Ceiling

**If the idea works perfectly, how much does it improve — and does something simpler get most of that?**

- Find the number the work is meant to move, and its value today.
- Work out the best case from what the plan itself says: how many of the bad cases can this approach reach at all?
- Name the simplest alternative — a threshold moved, a setting changed, a rule added by hand — and what it would get.
- If no number exists, say what a user would notice in the best case.

**Fails when:** the best case is small against the cost; a share of the problem is out of reach of the approach whatever happens; or the simple alternative does about as well.

**Usually means:** stop, or shrink to the simple alternative.

## 3. Ratio

**How big is the change itself, and how big is everything being built around it?**

- The change is what Step 2 named: what is different in the product if the idea is right.
- Everything else is apparatus: harnesses, converters, reports, checks, procedures, migration paths.
- State both in the plan's own units — lines, files, slices, requirements.

**Fails when:** the apparatus is many times the change and the plan gives no reason. A stated reason — the change cannot be undone, the result will be published, money moves on it — is an answer; "to be safe" is not.

**Usually means:** shrink.

## 4. What a user sees

**After each stage ships, what is different for a reader, an operator, or a customer?**

- Take the plan stage by stage (tier, milestone, slice) and write one phrase for each.
- "Nothing yet" is an honest answer for a stage. It makes that stage preparation.

**Fails when:** the first stage, or most of the stages, change nothing anyone sees, and the plan treats them as deliverables instead of as the price of one.

**Usually means:** reorder or shrink — preparation should be as small as a script unless argued otherwise.

## 5. Rule or code

**For each safeguard the plan builds: what does it protect against, and would a written rule do?**

- List the safeguards: checks, refusals, pins, locks, validations, enforced orderings.
- For each, name the adversary: an attacker, a careless future contributor, an accident, or the one careful person who will run it.
- For each, ask whether the failure can be undone.
- Flag every "never", "always", "every", and "any" that has no stated boundary. A guarantee with no edge cannot be finished: each review finds the next case outside it.

**Fails when:** code enforces discipline on the person who wrote the plan; a reversible failure gets the same enforcement as an irreversible one; or an unbounded guarantee is written as a requirement.

**Keep the code when:** the failure cannot be undone — data lost, a secret or private text published, money spent, a message sent. This is where enforcement and heavy review earn their cost.

**Usually means:** shrink.

## 6. Budget and tripwire

**How many units of work, at what cost each — and where is the point to stop and look again?**

- Count the plan's own units: slices, milestones, review rounds per slice.
- Cost per unit is *estimated* at a design gate and *measured* after the first unit. Say which.
- Match the review weight to the risk, and let the risk conditions win. Code that runs in production, handles untrusted input, or can do something that cannot be undone gets the full process — wherever it runs. Only code with none of those may take a lighter one, such as a single review. Lighter review is a recommendation to the user, never a way round verification the governing workflow requires: say what you recommend and let the workflow's owner change it.
- Set the tripwire: an observable condition, checked after the first unit, at which the work stops for a `recheck`. "The first slice takes more than three review rounds." "The first milestone takes more than two days."

**Fails when:** the total is not stated; the same review weight is applied to everything; or there is no point at which anyone would be asked whether to carry on.

**Usually means:** proceed with a tripwire, or — on `recheck`, when the measured cost is several times the estimate — shrink, naming the process and not the scope as what is too large.

## Reading the answers together

- **One failing question is a finding; a pattern is a verdict.** Kill test late *and* nothing visible until the end is a reorder. A low ceiling *and* a simple alternative is a stop.
- **Scope and process are different problems.** When the cost is in the number of things built, shrink the plan. When it is in the rounds each thing takes, lighten the process and leave the plan alone.
- **A kill test that has run settles question 1 only.** If it failed, the verdict is stop, whatever the rest says. If it passed, the idea works — the ceiling and the simpler alternative are still open, unless the same run measured them, and cost comes after.
