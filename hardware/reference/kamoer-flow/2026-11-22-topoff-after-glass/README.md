# Does a slow top-off deliver more right after a full glass?

The previous morning record ([37aec3c88](https://github.com/derekbreden/homesodamachine/tree/37aec3c881a181c8dd621a9e84197800bab6860f/hardware/reference/kamoer-flow/2026-11-22-topoff-and-sitting)) caught one raised 11-burst top-off on each pump just after a run of full glasses, at about the dose Codex's overnight top-offs on pump A had shown. This record asks whether that history raises the top-off, on the same bench, cup, camera path, programs and frozen forecasts. Pump A withdraws concentrate from the cup; pump B returns it.

## What came out

**Three glasses and a pause do not reliably raise the next top-off.** The event before the raised pour was repeated twice, once with positioning gates on A during the pause and once without. Neither first top-off reached the registered cut for a raised pour on either pump, so by the registered rule a run of three glasses is ruled out as a reliable cause on both heads. On A the repeat without gates came close to the cut and the one with gates did not move at all. [Rule, cut and rulings](results/reproduce.json) · [Every pour](results/pours.csv)

**A single glass followed by a top-off on the same pump often does.** The one-glass contrast and the delay cycles, where each pump's top-off followed its own glass with no other motion of that pump between, raised A's top-off in most cases and B's in most of the delay cycles, at every delay tried. Each top-off that followed a top-off on the same pump fell back toward the rested dose. On A every top-off that came straight after its own glass ran above every rested top-off; the one with a positioning gate on A between glass and top-off did not. The original delay plan's rule, registered first and run after the amendment, calls A supported at the shortest delay and leaves B unresolved, because one of B's rested top-offs was itself raised. Those cycles ran once per delay except the shortest, which ran twice; the longest ran once.

**Settling is not what raised them.** Every top-off was bracketed by a no-pump photograph taken one top-off duration before its starting photograph, in the same camera stream. The level change over that bracket, scaled to the pour and taken in the pump's direction, is the settling correction; it is a small fraction of the raise on the primary sightline for every top-off. Raw and corrected doses sit side by side in [the pour table](results/pours.csv).

What sets the raised state is not identified. The data point at the pump's own last motion: a glass leaves it raised for at least the delays tried, while a short gate or another top-off on that pump brings it back. That reading rests on a handful of pours per head and is untested.

## What was tested

The plan and its limits were committed before any pump ran ([f39b7a6c9](https://github.com/derekbreden/homesodamachine/commit/f39b7a6c9b7c78b4c3374caca92f195deab8ef6f)). It was stopped before its first measured pour, after two positioning gates, and amended to reproduce the raised pour's history first ([39ddefc13](https://github.com/derekbreden/homesodamachine/commit/39ddefc13d7ee6100428d7693516161208c4a0f8)). The amended run took the rested top-offs first, before any glass, then the three-glass episodes and the one-glass contrast. The original delay cycles ran afterwards, without repeating the rested top-offs, until the registered deadline skipped the last one. [Design and amendment](design.json) · [Programs and forecasts](programs.json) · [Model](model-used.json)

The controller ran its installed firmware with the laptop supplying meter signals ([`run.py`](acquisition/run.py)). The camera path, the reader and its NumPy filters are those of the previous record ([`cam.py`](camera/cam.py), [`optics`](optics)). [`camera/endpoints`](camera/endpoints) holds the sightline pixels of every photograph; `python3 optics/replay_endpoints.py .` replays them and `python3 analysis/score.py logs` rebuilds the tables.

## Bench state at the end

The cup was returned to the level found at the start of the session's earlier record. The controller read back idle pumps, all valves closed, volume at zero, flavor A and both ratios as found. The camera controls read back exactly as found ([found](logs/uvc-as-found.txt), [restored](logs/uvc-restored.txt)). [Journals](logs)
