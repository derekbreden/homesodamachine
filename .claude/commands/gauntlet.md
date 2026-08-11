---
description: One unattended iteration — take the worst check, move its chain, commit, and let the ratchet decide whether it stands. Drive it with /loop.
argument-hint: [check to take — omit to take the worst one still open tonight]
disable-model-invocation: true
---

One iteration. Take a check, move whatever chain it takes, and let the ratchet judge it. Nobody
is watching this turn, so the deliverable is committed state and nothing else.

Requested: **$ARGUMENTS**

`calibration/Chain.md` carries the move itself — the chain, the one commit, the red that is
committed red. Read it in full; it is short. This adds only what changes when there is no one
to read the report: the ratchet, the marking, and the stop.

## The campaign, and why an iteration is not judged on improving anything

A check's fix is usually a chain of several moves, and the early ones cost something. A move
that frees the next one is a valley, and what it frees is on the other side. Judged alone it
looks like a regression.

So the unit of judgement is a **campaign**: one check, up to **10 iterations**, one baseline.

- **Each iteration** may stand unless it breaks a gate. Costing another check ground is
  allowed. Moving no geometry at all is allowed — a decoupling is real work.
- **The campaign** has to have paid by the time the budget runs out: a gate gained, or a goal
  count risen with no gate lost. That is where iterations that went nowhere get undone,
  together.

## Before you start

```
git log --oneline --grep='^Gauntlet:' -30
jq -r '.checks[] | "\(.status)  \(.id)  \(.value)"' hardware/manifold-layout/enclosure-assembly.scorecard.json
```

The log is tonight's memory — your context may have been compacted, the repo has not. Every
trailer carries the check, the iteration number, the budget and the baseline, so the log alone
tells you which campaign is open and how much of it is left.

**Stop and report only if:** every gate passes, or every failing check has already had a
campaign tonight. Otherwise there is work.

## The iteration

1. **Which campaign.** From the log: if a campaign is open and under budget, continue it — the
   check and baseline are already fixed and are not yours to change. Otherwise open one on
   `$ARGUMENTS`, or on the worst failing check that has not had a campaign tonight.

2. **Move it**, following `Chain.md`: state the target as a condition, print every derivation
   that reads the body you are moving, move all of it. No subagents. One build.

3. **Commit it**, whatever colour it came out:

   ```
   Gauntlet: <check-id> iteration <n>/10 since <baseline-sha>
   ```

   `git tag gauntlet/$(date +%Y-%m-%d)-<seq>` so it can be found and undone by hand.

4. **Judge the iteration.** The sidecar is committed, so the standing at any ref is readable,
   and the whole judgement is the difference between two of them:

   ```
   SC=hardware/manifold-layout/enclosure-assembly.scorecard.json
   diff <(git show HEAD~1:$SC | jq -r '.checks[]|"\(.id) \(.status) \(.value)"') \
        <(jq -r '.checks[]|"\(.id) \(.status) \(.value)"' $SC)
   ```

   **A gate that was `pass` and now is not ends the iteration** — nothing else does. Costing a
   goal count is allowed, and no lines at all is allowed. If it stands, push and the campaign
   continues. If it broke a gate, `git revert --no-edit HEAD`, push both, and the iteration is
   spent: the attempt stays in history to be read, main's head does not carry it.

   If the sidecar does not read at that ref, or the build that wrote it is older than the
   source beside it (`source.generated`, `source.commit`), you cannot judge. Fix that before
   you commit anything else; do not treat it as a pass.

5. **Judge the campaign** when the check passes, or the tenth iteration lands — the same diff,
   against the baseline:

   ```
   diff <(git show <baseline-sha>:$SC | jq -r '.checks[]|"\(.id) \(.status) \(.value)"') \
        <(jq -r '.checks[]|"\(.id) \(.status) \(.value)"' $SC)
   ```

   It paid if a gate went `fail` → `pass`, or a goal count rose with no gate lost. Close it,
   say so in the log with a `Gauntlet: <check> closed` commit or in the next message, and take
   the next check.
   It did not pay if the standing is level or behind. Revert the whole campaign as one inverse
   commit: `git revert --no-commit <baseline-sha>..HEAD && git commit` — message naming the
   check, the budget it spent, and the link nobody could re-answer. Then take the next check.

6. **Report one paragraph**: the check, what moved, the iteration line, and where the campaign
   stands against its budget. Lead with the state. No offers, no plan for next time — the next
   iteration reads the log, not your prose.

## What the ratchet is not

It counts gate statuses and goal counts. It cannot see a run that reaches its radius by riding
somewhere absurd, a body parked where no bracket could reach it, or a picture that looks wrong.
A green ratchet means the work may stand overnight, not that the move was good — Derek reviews
the tags in the morning and reverts what the numbers could not judge.

So: do not optimise for the ratchet. Move the body the machine actually needs moved, and let
the ratchet be the floor it has to clear.

The budget is not a verdict on the check either. A campaign that spends ten iterations and gets
reverted has established which chain does not pay, and the log carries that to the next night.
Write the link nobody could re-answer into the revert message, because that sentence is the
whole yield of those ten builds.
