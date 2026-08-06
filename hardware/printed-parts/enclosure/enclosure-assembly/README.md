# Enclosure assembly

The [enclosure](/hardware/printed-parts/enclosure/enclosure/) wrapped around the contents in shared
coordinates — the internal subsystems placed by [`_contents.py`](/hardware/printed-parts/enclosure/enclosure-assembly/_contents.py), which the
enclosure is sized around, plus the through-wall connector bodies
(`_contents.panel_bodies()`), the display, and the hopper funnel. The contents
keep their per-part colors; the enclosure is translucent so the arrangement
reads through it.

The export prints the pack envelope and verifies every pair of placed solids
non-intersecting (and the connector bodies against the enclosure walls); a
clash fails the run.

## Looking at it

[`tools/around.sh`](/tools/around.sh) is this assembly read the way the viewer reads it: every
body solid in its own colour, the four enclosure quadrants and the funnel off, perspective, no
labels. It walks a CIRCLE rather than standing on one of six named views —

```
tools/around.sh                              # one slow turn, 15° a frame, 24 frames
tools/around.sh --spin x                     # tumble front→top→back instead of turntable
tools/around.sh --at 73,127,261 --near 0.95  # stand close to a point and turn there
tools/around.sh --click 500,350              # what is at that pixel? (amber, named)
tools/around.sh --show tee-y-a               # light a body you can already name
```

— and the frames are meant to be read IN ORDER. A silhouette that is ambiguous at one angle is
resolved by the frame either side of it, which is the thing three elevations cannot show. One
STEP parse serves the whole sweep, so a finer step costs milliseconds a frame.

`--click` casts from that pixel exactly as the viewer's component picker does and paints what it
hit in the picker's own amber. **That is the check**, not a convenience: a name is the name of the
thing you meant only when the thing that lit up is the thing you meant. Look at the frame before
quoting the name. `--show` is the same amber addressed by name instead — depth-test off, so a body
behind another still reads.

Both are `--pick` and `--select` on [`render-view.js`](/tools/render/render-view.js), with
`--orbit`, and work on any STEP in the tree. `look.sh` is the other question: it names a subject
and drops everything else to edges, for *where is this body*. This one is *what is this thing, and
what is it next to*.

## Regenerate

The enclosure sizes itself from the contents bbox and the funnel seats itself
against both, so rebuild in this order:

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/enclosure.py                    # ~2½ min
tools/cad-venv/bin/python hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py               # ~35 s
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py  # ~2–3 min
```

→ `enclosure-assembly.step`. The contents are placed in-process by `_contents.py`
(shared with the enclosure); there is no separate contents STEP.

**A build's figure is the machine it runs on, not the cache it hits.** The scorecard cache
(`.enclosure-assembly.scorecard-cache.pkl`, keyed in `_scorecard_cache_key`) holds the
COMPONENT verdict — every part against every other part — and is keyed on where the bodies
stand, not on where the routes run. It is worth about **40 s**: the scorecard phase is ~13 s
on a hit and ~51 s on a miss. Everything else is the same work either way.

Measured back to back on an idle machine, miss then hit: **160 s** and **172 s** total. The
hit ran LONGER, because the phases the cache does not touch vary more than the cache saves —
the pack build read 61 and 78 s across runs, the three elevations 20 and 47 s. A figure here
is worth a minute either side.

What that means for reading a build: **the cache is not why a build is slow, and neither is
the scorecard.** A build far outside these figures is contending with another one. Check
`ps` and `$TMPDIR/hsm-cad-lock/` before timing anything, and see the note on the lock below —
several builds at once cost each other far more than a core count predicts, because OCCT's
worker threads serialise on dyld's global loader lock while unwinding C++ exceptions.

Where a build's time goes, on an idle machine:

```
import + pack build                                61–78 s
scorecard                                          13 s hit / 51 s miss
STEP export                                        21–26 s
three elevations                                   20–47 s
docgen writeback + thumbnail                        5–8 s
```

Import is no longer part of that first figure: `scorecard.PORTS` and `PLACEMENT_RULES` are
built on first use, so importing the module is 0.1 s and the pack is placed when a port is
first asked for. A probe or `need.py` that never builds now pays neither.

`HSM_CARD_ONLY=bend-radius,mounted` computes those rows and stands the rest down — worth the
scorecard phase's own ~107 s of checks on a miss. A stood-down row reads "not computed",
never "pass", and no partial card reports BUILD-READY.

`HSM_SKIP_VIEWS=1` drops the three elevations; `HSM_SKIP_THUMBNAILS=1` drops the `.step.png`.
The next build that runs without them writes both back.

Each build takes the global CAD lock ([`_run_lock.py`](/hardware/scripts/_run_lock.py)),
which tees its console and records its exit status where anything waiting can read them:

```
$TMPDIR/hsm-cad-lock/build.<pid>.log       the console, as it prints
$TMPDIR/hsm-cad-lock/build.<pid>.result    {"code": 0} when it is done
```

A second call for the same script follows the build already running rather than starting
a second one — printing what that build prints and exiting on its status — when it began
after the last edit to anything it reads.

Where it cannot follow, it WAITS: a live build someone is waiting on keeps the machine until
it is done, and only `HSM_BUILD_SUPERSEDE=1` sends it a SIGTERM. A watcher's own rebuild is
the one holder stopped on sight, since it fires again on the next save. `HSM_NO_BUILD_LOCK=1`
takes no lock at all and is what a probe should carry.

`HSM_BUILD_LOCK_PROTECT` is not the other half of that: it is worn by the HOLDER and stops
others stopping it. Carrying it does not stop the wearer stopping everyone else.

A build that takes the lock waits out whoever holds it, so its wall clock is the queue plus
its own work. `HSM_NO_BUILD_LOCK=1` takes no lock and waits for nobody, and prints what it is
running beside.
