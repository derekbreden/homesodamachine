# Request-to-view measurements

`measure.mjs` records the time from a user's request to source edits, agent reviews and
matching geometry drawn by the published viewer. Run it when measuring an actual request.
It installs no watcher and adds no build or commit work.

Start with the original user-message timestamp, including time already spent investigating:

```sh
node tools/iteration/measure.mjs start \
  --received-at "$HSM_REQUEST_AT" --request "$HSM_REQUEST_WORDS" --run enclosure-fit
```

The printed path names the request record. Use it for meaningful milestones; repeated
`review` marks count the agent's evaluations. `--at` records an already-known event time.
`--artifact` binds a milestone to the exact bytes inspected without copying them.
Each event keeps its observation time separately from `recorded_at`: source revisions
and artifact hashes are captured when the mark is recorded, including for backdated marks.

```sh
node tools/iteration/measure.mjs mark "$HSM_ITERATION_RECORD" source-edit \
  --artifact hardware/printed-parts/enclosure/enclosure/exterior.json
node tools/iteration/measure.mjs mark "$HSM_ITERATION_RECORD" review \
  --note 'Inspected the corner and measured its clearance'
node tools/iteration/measure.mjs mark "$HSM_ITERATION_RECORD" local-view
node tools/iteration/measure.mjs mark "$HSM_ITERATION_RECORD" published
node tools/iteration/measure.mjs mark "$HSM_ITERATION_RECORD" live-view \
  --note 'Verified the requested search results in the live browser'
```

The observer opens the existing published model and compares actual mounted geometry with
the selected local assembly's immutable mesh and placement keys. A new manifest with old
GPU geometry does not satisfy the comparison. It records the first matching draw and the
draw in which all selected target bodies are eligible together. Other bodies can still be arriving.
The selected solids need visible ancestors and materials, a visible canvas, camera-frustum
intersection and depth bounds inside the clipping planes. Available renderer/material
clipping planes are considered too. These checks establish eligibility for a completed
draw; they cannot establish occlusion or unobstructed pixels.

```sh
python3 tools/run.py -- node tools/iteration/measure.mjs watch "$HSM_ITERATION_RECORD" \
  --mesh hardware/manifold-layout/enclosure-assembly.step.mesh \
  --part enclosure-front-top --part enclosure-front-bottom
```

Use `--source` with an imported payload's repository-relative path instead of `--part` to
select its installed bodies. `--url` selects an existing published view; the default link
finds the selected bodies in the assembly. `--timeout` bounds observation.

To open the reference viewer ahead of an edit, add `--next`. Wait for its ready message,
then edit and run the normal selective print build in another terminal. The observer waits
for the selected local geometry to change before matching it on the website. This mode
captures the bodies changed in the next local update; unchanged selected bodies do not
count as the first changed view. Start another observation for a later producer or attempt.
The evidence and report retain that first-update scope; `all-live-view` in this mode covers
the changed bodies in that update, not every body across later producer updates.

Add `--delivery` to record receipt of the website's existing change notification, the selected
model's member URL, and its target mounting events alongside the matching draw. These timestamps
separate publication delivery from browser work without changing the running website. Notification
receipt follows server adoption and includes transport to the reference browser; it does not time
the server's internal phases. `HSM_PUBLISH_TIMING` names an optional JSONL trace for the same build's
publication planning, uploads, Git network work, commit/push and notification request.

The instrumented evidence records matching mounted geometry eligible for a completed
reference-browser draw. It says nothing about unobstructed pixels or the first composite
on Derek's device. Opening the observer after publication includes its own loading time.
A `published` mark is only a publication milestone. A manual `live-view` mark requires a
note and is labeled as manual observation, including browser UI assertions unrelated to
geometry. Keep historical observations identified in their notes.

Finish and read the request:

```sh
node tools/iteration/measure.mjs mark "$HSM_ITERATION_RECORD" complete
node tools/iteration/measure.mjs report "$HSM_ITERATION_RECORD"
node tools/iteration/measure.mjs report "$HSM_ITERATION_RECORD" --json
```

The run keeps the request, append-only milestone events, source revisions and selected
artifact hashes under `.cache/runs/`. Independent marks made while the observer runs
remain in the event stream. No model trees, rendered images or browser profiles are kept.

The focused tool tests run on demand:

```sh
node --test tools/iteration/measure.test.mjs
```

The draw-eligibility fixture uses the published viewer's own Three.js in a private browser:

```sh
python3 tools/run.py -- node --test tools/iteration/visibility.browser.mjs
```
