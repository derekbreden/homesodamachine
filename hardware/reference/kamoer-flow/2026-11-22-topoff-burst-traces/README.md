# Burst-by-burst traces of the slow top-off

The previous records left each pump's 11-burst top-off delivering in two bands, a normal one and a raised one, without a single cause. Start and finish photographs cannot say what a raised pour is made of. This record keeps every camera frame across each traced top-off, reads the cup in every frame, and lines the trace up with the controller's bursts. Pump A withdraws concentrate from the cup; pump B returns it below the surface.

## What came out

**By the registered cut, the bursts resolve; by the noise that matters, single bursts do not.** The cut compared each burst's step with the frame scatter of the still cup before the pour, and almost every step passed it on both pumps. While the pump runs, though, the surface moves from frame to frame by about as much as one burst delivers, on both pumps and both sightlines. One burst's step is read from a few frames either side of it, so its size is uncertain by a large fraction of itself. Comparisons across several pours are steadier than any single burst. Each pour's trace still adds up to its photographed dose. [Per-pour summary](results/trace-summary.json) · [Every burst](results/bursts.csv) · [Frame-by-frame traces](results/traces)

**A raised pour is larger through the whole pour, not at its start.** Among A's traced top-offs, some ran raised and some normal. The registered readings came out as follows ([readings](results/readings.json)):

- *Every burst larger by about the same factor:* holds by its rule, at just the number of burst positions the rule asks for.
- *Two burst sizes mixed in a raised pour:* false. Raised pours did not split into a low and a high band.
- *The extra in the first burst or two:* false. The first two bursts carry a small share of the difference.
- *The extra arriving in the gaps between bursts:* false. On A the level moves back toward the cup between bursts in every pour, raised or not.
- *Same bursts, a normal pour giving some back in the gaps:* neither held nor false. The median step differs between raised and normal pours by more than the rule's "same" and less than its "different". Normal pours gave back much more between bursts than raised ones.

Taken together, a raised pour on A delivers more at each burst and gives less of it back between bursts, in roughly equal parts. How the step and the give-back divide depends on how the surface rings after each burst, so that division is the least certain part of this result.

**The raised state held for a whole cycle.** Each cycle was a glass and two top-offs on A, then the same on B. Both of A's top-offs in a cycle came out raised, or both came out normal, whether the top-off followed A's glass or another top-off. B ran raised in every traced pour this round, so B has no normal pour to compare against. Its surface read as well as A's during the pour.

## What was tested

The cut for a resolved burst, the cycle design and the readings to tell apart were committed before any pump ran ([95784de68](https://github.com/derekbreden/homesodamachine/commit/95784de68ab7407abf23eadc914d82a9c3a1ad25), [design](design.json)). One A top-off was traced first as the resolution test; the cycles followed. Each traced top-off holds every second frame of the 30 fps stream, from a still photograph one top-off duration before the pour to the finishing photograph. Burst times are the firmware policy replay's gates, placed from the controller's first pour receipt ([`run.py`](acquisition/run.py), [`policy_trace.cpp`](acquisition/policy_trace.cpp)). Each frame is read alone by Codex's frozen reader ([`traces.py`](analysis/traces.py), [`readings.py`](analysis/readings.py)). The programs, forecasts, model, camera path and reader are those of the previous records ([`programs.json`](programs.json), [`model-used.json`](model-used.json), [`cam.py`](camera/cam.py), [`optics`](optics)).

Each traced pour's frames are in [`traces/`](traces), with their times and the clock offset that places the bursts. The trace tables in [`results/traces`](results/traces) give time from the first burst, the level on each sightline, and whether a burst was on. From this directory, `python3 analysis/traces.py && python3 analysis/readings.py` rebuilds every table, and `python3 optics/replay_endpoints.py .` replays the photographs.

## Bench state at the end

The cup was returned to the level found that morning. The controller read back idle pumps, all valves closed, volume at zero, flavor A and both ratios as found. The camera controls read back exactly as found ([found](logs/uvc-as-found.txt), [restored](logs/uvc-restored.txt)). The optional repeats of the delay cycles and the top-off on A after a glass on B were not run. [Journals](logs)
