# Worked Example

A real project, lightly generalised. It is here because every one of the six questions would have caught something, and none was asked until the work was nearly done.

## The proposal

A daily news digest published about one item in eight that an independent judge would have excluded. The idea: have the scoring step return three extra scores per item — is it in the domain, is there something to act on, is it newsworthy — and decide "publish" from them with a rule in code.

The design that was approved built, as its first tier, the tooling to measure that idea properly: a check that the experiment's setup was frozen before any result was read, committed per-item results files, a converter for a competing approach's logs, a report over both, and a written operator procedure. Seven slices. The tier's own text said the digest would not improve in it.

## What happened

- The first four slices took four and a half days and about a hundred subagent runs. Each went through four to six rounds of review.
- The last three slices, the same kind of work, took five hours after the review process was lightened to one review per slice.
- The first run that tested the idea itself — re-scoring days the judge had already graded — was slice five. It took forty minutes.
- A few minutes of analysis on its output showed the three scores did not separate excluded items from included ones. One of the three was useful; a threshold on the existing score did about as well as any rule over the new ones.
- The work was stopped.

## The six questions, asked at the design gate

1. **Kill test — fails.** The cheapest run: re-score three already-graded days with the three extra scores and see whether any rule separates the judge's excludes from its includes. The graded days and the scoring harness both existed. The plan put this run fifth of seven.
2. **Ceiling — fails.** A quarter of the excluded items scored high on everything and were out of reach of any rule over the scores. Moving the existing publish threshold caught about as many. Both facts were in data already on hand.
3. **Ratio — fails.** The change: one prompt edit and a few lines of code. The apparatus: seven slices, about thirty requirements. The reason given was experimental rigour, for an experiment not yet shown to be worth running.
4. **What a user sees — fails.** After the first tier: nothing. The tier was preparation, sized as a product.
5. **Rule or code — fails, with one exception.** Most safeguards enforced the order of an experiment on the one person running it; a dated paragraph would have done. Several requirements said "never" with no stated boundary, and one of them took five rounds of review to close — by a scope decision, not by code. The exception: one tool wrote article text to disk, and committing it could not be undone. That safeguard earned its review.
6. **Budget and tripwire — fails.** Seven slices at an unstated cost each, the production-grade review process applied to offline scripts, and no point at which anyone would be asked whether to continue. The first slice took six review rounds; a tripwire at three would have stopped the work on day two.

## The verdict that was available

**Reorder, then probably stop.** Run the kill test first, on existing data, with the stop condition written down: "if no rule over the three scores catches at least half the excluded items while losing fewer than one included item in ten, stop." It would have failed, in an afternoon, before any tooling was built.

## What the example teaches

- **A plan can pass every review and still be in the wrong order.** Each review asked whether the work was correct and complete. None asked whether it should come before the run that tested the idea.
- **Rigour belongs after the first look, not before it.** A frozen, checked experiment is how to confirm a promising result. It is not how to find out whether there is one.
- **The cost was in the process, not the scope.** Seven slices were planned and seven were built. What multiplied was the rounds per slice. Lightening the process cut the cost about tenfold and still found one real defect per slice.
- **The tripwire is the cheapest part of the report.** Nobody needs to predict the cost. They need a condition that makes someone look at it.
