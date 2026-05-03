# Posts

Daily Updates feed for homesodamachine.com/blog. Each markdown file in this
directory is one day's post. Posts are committed to git like any other
file; on deploy, the server hashes every `posts/*.md`, diffs against the
`post_hashes` table in Postgres, and fires an FCM push notification per
new or changed post (see `lib/push.js`). The post's frontmatter title is
the notification heading. Treat committing a new post as a publish action
— it pages every subscriber.

## The format

Filename: `posts/YYYY-MM-DD-HHMM.md` where HHMM is the time of the latest
commit covered, in 24-hour US Central time.

Frontmatter:

```yaml
---
date: <ISO-8601 timestamp of the latest commit covered, with -05:00 offset>
title: <short noun phrase, 2–5 words, like "Faucet and Site">
covers_from: <`git rev-parse <oldest-commit-covered>^`>
covers_through: <hash of newest commit covered>
---
```

Body: a flat bullet list. **1–3 top-level categories. 2 is the sweet
spot.** Each category has this exact shape:

```
- <headline, 8 words or fewer>
  - Before today <state, ~5–15 words>
  - After today, <state, ~10–25 words>
```

If "after" splits cleanly into 2–4 distinct things, expand it:

```
  - After today, it has:
    - <thing>
    - <thing>
    - <thing>
```

**Collapsing "did not exist".** Always draft each category in the full
before/after form first. On a final pass, if the before-line is "this
part did not exist" (or equivalent null state: "had no spec," "did not
exist yet") AND the after expands into a sub-list, drop the
before/after labels entirely — the headline plus the sub-list carry
the change. Apply this only when the before-state is the trivial null.
Example:

```
- The carbonator got an insulating shell
  - Before today this part did not exist
  - After today, it has:
    - An inner cylinder hugging the cold tank with a foam gap
    - An outer cylinder with cradle pockets for the two flavor bags
    - A split into a bottom cup and an upper shell that nest together for printing
```

collapses to

```
- The carbonator got an insulating shell
  - An inner cylinder hugging the cold tank with a foam gap
  - An outer cylinder with cradle pockets for the two flavor bags
  - A split into a bottom cup and an upper shell that nest together for printing
```

Do not collapse when the before describes specific prior state ("we had
not got to the lever yet," "the link was a hand-rolled reliability
layer"). The before/after labels are carrying meaning there.

That is the entire format. No prose paragraphs. No headline arcs. No
"also today" tail.

A 2-category post is ~70 words. 3 categories is ~110 words. If you're at
150+, you're padding.

## What to do

### Day narrative, not diff narrative

You are describing what happened in the world today, not what landed
in the repo. This is a real physical project being built in a garage;
commits are evidence of activity, not the activity itself. A single
commit that adds a dated snapshot in `hardware/` or `marketing/`
(e.g. `welding-progress-*.md`, `build-readiness-*.md`,
`first-weld.md`) can represent days or weeks of off-repo work — read
it fully and weigh it as a candidate category, not as "docs cleanup."
A one-line ledger update saying "X1 Pro arrived" is a heavier
real-world inflection than 22 viewer commits. Reconstruct the day
from the user's perspective: what did they *do* today, what
capability is new in their world, what would they tell someone in
person tonight?

### Categorize by outcome, not activity

This is the rule you will get wrong if you forget anything else. You are
reporting **what is true now that wasn't true before**, not what was
attempted along the way. Group commits by what visibly changed in the
project — what a stranger would recognize as one thing — even if it took
30 commits across many files and many sub-arcs.

- Right: "the printed faucet got more complete" — one category,
  regardless of how many sub-tasks it contained.
- Wrong: "the lever was finalized; the back wall went in; the cutouts
  shrank; the material changed" — four activities, not four outcomes.

Before/after lines describe **state**:

- Right: "Before today we had not got to the lever yet."
- Wrong: "Lever ramp finalized as 18° wedge."

The threshold for whether something earns a category is **relative to
the window**. A small hardware tweak doesn't earn a slot if there are
already two strong outcomes, but it absolutely does if the day is
otherwise quiet — a one-bullet-only day looks malnourished. The decision
is always "what's the best 1–3 bullet picture of this window," not "what
passes an absolute bar."

### Voice

Match the gold-standard posts (see Examples). Specifically:

- Conversational first-person plural ("we got past", "we have")
- Colloquial grammar where natural ("had not got")
- Concrete specifics: numbers, counts, what concretely changed
- Parenthetical translations on first use of brand or technical terms a
  stranger wouldn't know: "STEP file (3D drawing)", "Mermaid file
  (flowchart)", "BLE (Bluetooth)"
- **Each post must stand alone.** No "yesterday," no implicit references
  to prior posts. A reader landing cold needs enough to track.
- Past tense for completed work, present tense if the work is genuinely
  mid-flight at the end of the window
- **Headlines lead with subjects, not verbs.** "HomeSodaMachine.com is
  now a live site." Not "Started a rear-panel nameplate." Verb-led
  headlines describe activity; you want state.
- **Sub-bullets in the expanded form are noun phrases, not full
  sentences.** "A polished iOS-style look." Not "The pump tray and
  coupler tray widened to 170mm."
- **Title is "X and Y" — no commas.** "Faucet and Site." Not
  "Pump Case, Strut, iOS."
- **Three sub-bullets in the expanded form.** Two reads thin, four reads
  dense. Three is calibrated.
- **Before-line ≤15 words, plain verbs.** "Before today we had not got
  to the lever yet." Avoid "consisted of," "had been engineered to,"
  25-word setups.
- **Small/punchy first, big/expanded second.** Put the heavier
  expanded-form category at the bottom of the post.

### What's banned

- Project-internal jargon: zone numbers (`Zone 4`, `ZONE4_Z_TOP`),
  CadQuery API names (`loft`, `ruled=False`, `copyWorkplane`), function
  names, file paths, code identifiers, code-named parts
- Journey language: "ten hours of attempts," "after three reverts,"
  "wrestled with X"
- Marketing voice: "exciting," "shipped 🚀," emoji, "huge," "stay
  tuned," "milestone"
- References to yourself, to the routine, or to the date in prose (the
  date is in frontmatter)

### Project terminology

Use the project's canonical terms. The two most-confused:

- **Bill of materials**, not "parts list." The file is `hardware/bom.md`
  and its H1 is "Bill of Materials — One Consumer Unit." Commit messages
  use the `bom:` prefix. The README's "Parts List" section is a separate
  Amazon-shopping framing for outside readers — not the engineering
  source of truth. The abbreviation "BOM" is fine in titles for
  terseness; spell out "bill of materials" in body prose.
- **The carbonator's foam shell**, not "flavor reservoir housing." The
  foam-bag-shell (`hardware/printed-parts/foam-bag-shell/`) wraps the
  carbonator tank and includes pockets for the soft flavor bags. The
  plan-b hardshell flavor reservoir
  (`hardware/printed-parts/plan-b/reservoir/`) is a different concept
  that landed as docs only on 2026-05-02 — don't conflate them in earlier
  posts.

### Skip rules

If the window is only formatting, dependency bumps, comment-only edits,
or `chore:` cleanups: skip the post entirely (don't write a file). If
only one substantive commit: write a single-bullet post on it. If the
day has zero commits: skip and report.

### When you don't have full context

If something looks like a project-naming or terminology question and
you're not sure ("is this part really called X or Y?"): **don't guess
and don't reflexively defer to the agent that drafted it either.** Read
`hardware/bom.md`, `hardware/future.md`, the part's own README, and
recent commit messages. Prior posts in this directory are also a strong
signal of established naming. If still ambiguous after that, ask the
user before writing.

Use the term that was canonical on the post's date — not the term
that's canonical now. The repo evolves; the post is anchored to its
window. A part renamed three weeks after the post window should still
appear under its earlier name. Same for capabilities: don't pull
later-acquired terminology ("Plan A", "the printed reservoir", "the
website") into windows where those concepts didn't exist yet.

## Procedure

1. Find the day's commits:

   ```
   git log --since="<DATE> 00:00 -0500" --until="<NEXT_DATE> 00:00 -0500" \
     --pretty=format:"%h %ai %s"
   ```

2. Read the diffs for substantive commits — `git show <hash>` per file
   that changed substantively. Commit messages are summaries, not
   truth; a subject like "Revert experimentation back to ruled=False
   side lofts" is meaningless until you see the diff.

3. Group commits into 1–3 outcomes. Collapse aggressively. Skip the
   reverts, the bisection sweeps, the "Had to remake your commit sorry"
   commits — those belong inside the arc they're part of, not as
   separate items.

4. Write the post to `posts/YYYY-MM-DD-HHMM.md`. Verify each headline
   is 8 words or fewer (this is the rule that drifts most often). Verify
   the post stands alone — no "yesterday," no references to the prior
   day's post.

5. Don't auto-commit unless explicitly instructed. The act of committing
   pages every subscriber, so a human review pass before publish is the
   default.

## Examples

These two posts were calibrated through several rounds with the project
owner. Match this voice exactly. If your draft is twice as long, or has
a prose paragraph anywhere, or starts using zone numbers, something has
drifted.

- `posts/2026-04-29-2238.md` — the canonical 2-category post.
- `posts/2026-05-01-1703.md` — second gold standard.
