# Tube shape review

The enclosure assembly's **Tubes** tool in [/3d](https://homesodamachine.com/3d#step:manifold-layout%2Fenclosure-assembly.step)
compares the drawn route with illustrative shapes between its fitting exits and actual ties.
The tool is optional. It covers the 21 exposed 1/4-inch LLDPE runs in
[`tube-routes.json`](/web/public/tube-routes.json); the copper remains drawn geometry. The
three 4 mm lines, `fluid-18`, `fluid-28` and `drain-vent`, carry no stock assumption in the
export, so the tool does not offer them.

Choose a run and **Show run**. Cyan dashes mark the CAD centreline, coloured lines mark the
assumed shapes, white squares mark fitting exits, and green dots mark retained holds.
**Temporarily omit a hold** removes that restraint from the calculation. It changes no part
or assembly instruction. **Reset assumptions** restores the holds and stock assumptions.
The contact list, holds and unsupported spans each focus the corresponding location.

## What the calculation holds

The tube keeps its exposed developed length, both fitting exit directions and the position
and direction of each finite seat. A tie fixes the same material station along the tube;
sliding through the tie is not modeled. Between those restraints, the drawn corners are free
to relax. Straight stock and either sense of an assumed coil curvature are available, with
adjustable coil radius and plane.

This is an unloaded centreline model with uniform bending stiffness. Gravity, pressure,
friction, torsion and insulation stiffness are absent. A converged result is a local numerical
solution under those assumptions. The scenarios are neither measured springback nor bounds
on the installed shape. The stock's minimum bend radius is a diagnostic, not an enforced
constitutive law.

Tube-sized capsules are checked against the displayed assembly's triangle surfaces, including
hidden parts and other tubes in their CAD positions. The export records no sleeve on any
run, so the soda inlet's foam piece is not in the check. The selected tube's own CAD body is excluded;
fitting and tie contact exemptions cover only their recorded interface intervals.

Contact is reported rather than resolved. A line through a part is not a feasible installed
shape. The contact list distinguishes locations already occupied by the CAD route from
possible new locations, at the path sampling resolution. Surface screening does not detect
self-contact or guarantee clearance for a tube wholly enclosed inside a solid. Neighbouring
tubes remain at their drawn positions during a single-run review.

## The holds in the exposed runs

The only holds are Reservoir A's two paired seats on the cold-core lid, at Y205 and Y304,
each closed by one narrow tie around `fluid-14` and `fluid-16`. These readings use straight
stock and coil curvature in both senses about XY, XZ and YZ, at an assumed 250 mm coil
radius. Each range covers those seven assumptions. Shift is the largest displacement of a
material station from its CAD position, in millimetres.

| Run | Both seats retained | Fore seat omitted | Aft seat omitted |
| --- | ---: | ---: | ---: |
| fluid-14 | 35.9–73.5 | 65.6–113.8 | 64.2–80.9 |
| fluid-16 | not length-feasible | 59.7–60.1 | 51.3–66.8 |

With both seats retained, one of `fluid-16`'s exported spans is shorter than the distance
between the points it joins, so no assumption is length-feasible; omitting either seat makes
it solvable.

Among the unheld runs, `fluid-26` shifts 54.4–57.0 mm, `fluid-24` 40.2–51.3 mm and
`above-core-va-fore-feed` 17.0–17.3 mm. Every other feasible run stays within 4.2 mm.
Displacement alone is not an anchor requirement; the tool's contact list shows where each
shape meets its surroundings.

## Data and numerical checks

[`tube_routes.py`](/hardware/scripts/tube_routes.py) exports full-precision paths from the
assembly, verifies them against the saved STEP tube bodies, and records fitting mouths,
exit axes, actual seat centres and seat lengths. Source fingerprints cover the displayed STEP,
complete viewer surface payload and the routing inputs. Build-only intermediates are recorded
separately; the web server holds their resulting assembly. The tool refuses a mismatched or
stale export. Refresh with:

```sh
tools/cad-venv/bin/python hardware/scripts/tube_routes.py
```

The interactive solver runs in a worker. The 21 runs and four single-seat omissions give 175
cases across the seven assumptions above, and 153 converge. Twenty-one are not
length-feasible: `above-core-tee-regulator` and `above-core-tee-vk-link` in every assumption,
and `fluid-16` with both seats retained, each with an exported span shorter than the distance
between its retained points. `fluid-16` with its fore seat omitted stalls under coil−
about XZ. On the development Mac the median solve is about 1 ms and the slowest about
279 ms. For `fluid-14`, refining the nominal 6 mm sampling to 3 mm changes the shape by at
most 0.51 mm across those assumptions. The solver reports length residuals and unfinished
or infeasible results.

The numerical tests cover developed length, finite restraints, endpoint directions, analytic
bending cases, symmetry, refinement and infeasibility. Contact tests cover triangle crossings,
local sleeve radii and bounded interface exemptions. Browser tests exercise the real assembly,
hold omission, changing assumptions, mobile framing, model changes and stale-data refusal.

The producer's optional `--reference` mode is experimental offline gravity/contact tooling.
It is not used by the viewer or by the readings above. Viewer behaviour and implementation
are described in [`web/README.md`](/web/README.md#tube-shape-review).
