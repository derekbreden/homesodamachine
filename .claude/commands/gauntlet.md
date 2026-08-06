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

## Before you start

```
git -C . log --oneline --grep='^Gauntlet:' -20
python3 hardware/printed-parts/enclosure/enclosure-assembly/ugly.py
```

The log is tonight's memory — your context may have been compacted, the repo has not. **Stop
now and report if any of these hold:**

- every gate passes — the machine is done, there is nothing to iterate on
- the last **three** `Gauntlet:` commits were all reverted — it is thrashing, and another
  attempt spends a build to learn nothing
- the run you are about to take already appears in **two** reverted `Gauntlet:` commits
  tonight — take the next one down the board instead, and if that rule empties the board,
  stop

## The iteration

1. **Take the run** — `$ARGUMENTS` if named, else the board's worst that the rules above
   leave open.
2. **Move it**, following `/routes`. No subagents. One build.
3. **Commit it**, whatever colour it came out, with these two trailers on the message:

   ```
   Gauntlet: <run-id> iteration <n>
   Ratchet: pending
   ```

   Then tag it so it can be found and undone by hand:
   `git tag gauntlet/$(date +%Y-%m-%d)-<n>`

4. **Judge it**:

   ```
   python3 hardware/printed-parts/enclosure/enclosure-assembly/ugly.py --since HEAD~1
   ```

   Exit 0 — it stands. Push.

   Exit 1 — `git revert --no-edit HEAD`, then push both. The failed attempt stays in history
   where it can be read; main's head does not carry it. Say in the revert's message which
   number moved the wrong way.

5. **Report one paragraph**: the run, what moved, the ratchet line, and whether it stands.
   Lead with the state. No offers, no plan for next time — the next iteration reads the log,
   not your prose.

## What the ratchet is not

It counts corners at spec, gates, and debt. It cannot see a run that reaches its radius by
riding somewhere absurd, a body parked where no bracket could reach it, or a picture that
looks wrong. A green ratchet means the iteration may stand overnight, not that the move was
good — Derek reviews the tags in the morning and reverts what the numbers could not judge.

So: do not optimise for the ratchet. Move the body the run actually needs moved, and let the
ratchet be the floor it has to clear.
