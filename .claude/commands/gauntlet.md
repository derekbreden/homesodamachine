---
description: One unattended iteration — take the worst run, move its chain, commit, and let the ratchet decide whether it stands. Drive it with /loop.
argument-hint: [run to take — omit to take the worst one still open tonight]
disable-model-invocation: true
---

One iteration. Take a run, move whatever chain it takes, and let the ratchet judge it. Nobody
is watching this turn, so the deliverable is committed state and nothing else.

Requested: **$ARGUMENTS**

`/routes` carries the procedure — read it and follow it for the move itself. This adds only
what changes when there is no one to read the report: the ratchet, the marking, and the stop.

## The campaign, and why an iteration is not judged on improving anything

A run's fix is usually a chain of several moves, and the early ones cost something. Y-F moved
west in `6cf29906` — the move that lets fluid-21 leave carb-1's column, and the one three
sessions were waiting on — and it took debt from 12.67 to 12.87. Judged alone it looks like a
regression. It is a valley, and the moves it frees are on the other side.

So the unit of judgement is a **campaign**: one run, up to **10 iterations**, one baseline.

- **Each iteration** may stand unless it breaks a gate. Costing debt is allowed. Losing a
  corner is allowed. Moving no geometry at all is allowed — a decoupling is real work.
- **The campaign** has to have paid by the time the budget runs out: more corners at spec, or
  the same corners and less debt. That is where iterations that went nowhere get undone,
  together.

## Before you start

```
git log --oneline --grep='^Gauntlet:' -30
python3 hardware/printed-parts/enclosure/enclosure-assembly/ugly.py
```

The log is tonight's memory — your context may have been compacted, the repo has not. Every
trailer carries the run, the iteration number, the budget and the baseline, so the log alone
tells you which campaign is open and how much of it is left.

**Stop and report only if:** every gate passes, or every run on the board has already had a
campaign tonight. Otherwise there is work.

## The iteration

1. **Which campaign.** From the log: if a campaign is open and under budget, continue it — the
   run and baseline are already fixed and are not yours to change. Otherwise open one on
   `$ARGUMENTS`, or on the board's worst run that has not had a campaign tonight.

2. **Move it**, following `/routes`. No subagents. One build.

3. **Commit it**, whatever colour it came out:

   ```
   Gauntlet: <run-id> iteration <n>/10 since <baseline-sha>
   ```

   `git tag gauntlet/$(date +%Y-%m-%d)-<seq>` so it can be found and undone by hand.

4. **Judge the iteration:**

   ```
   python3 .../ugly.py --since HEAD~1
   ```

   Exit 0 — it stands. Push, and the campaign continues.
   Exit 1 — it broke a gate. `git revert --no-edit HEAD`, push both, and the iteration is
   spent. The attempt stays in history to be read; main's head does not carry it.
   Exit 2 — the tool could not judge. Fix that before you commit anything else; do not treat
   it as a pass.

5. **Judge the campaign** when the run reaches spec, or the tenth iteration lands:

   ```
   python3 .../ugly.py --since <baseline-sha> --gained
   ```

   Exit 0 — it paid. Close it, say so in the log with a `Gauntlet: <run> closed` commit or in
   the next message, and take the next run.
   Exit 1 — it did not. Revert the whole campaign as one inverse commit:
   `git revert --no-commit <baseline-sha>..HEAD && git commit` — message naming the run, the
   budget it spent, and the link nobody could re-answer. Then take the next run.

6. **Report one paragraph**: the run, what moved, the iteration line, and where the campaign
   stands against its budget. Lead with the state. No offers, no plan for next time — the next
   iteration reads the log, not your prose.

## What the ratchet is not

It counts corners at spec, gates, and debt. It cannot see a run that reaches its radius by
riding somewhere absurd, a body parked where no bracket could reach it, or a picture that
looks wrong. A green ratchet means the work may stand overnight, not that the move was good —
Derek reviews the tags in the morning and reverts what the numbers could not judge.

So: do not optimise for the ratchet. Move the body the run actually needs moved, and let the
ratchet be the floor it has to clear.

The budget is not a verdict on the run either. A campaign that spends ten iterations and gets
reverted has established which chain does not pay, and the log carries that to the next night.
Write the link nobody could re-answer into the revert message, because that sentence is the
whole yield of those ten builds.
