# Tube shape review

The enclosure assembly's **Tubes** tool in [/3d](https://homesodamachine.com/3d#step:manifold-layout%2Fenclosure-assembly.step)
compares the drawn route with illustrative shapes between its fitting exits and actual ties.
The tool is optional. It covers the 17 exposed LLDPE runs; the copper and reinforced hose
remain drawn geometry.

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
hidden parts and other tubes in their CAD positions. The documented CARGEN sleeves on carb-1
and carb-2 contribute their 12.7 mm outer radius. The selected tube's own CAD body is excluded;
fitting and tie contact exemptions cover only their recorded interface intervals.

Contact is reported rather than resolved. A line through a part is not a feasible installed
shape. The contact list distinguishes locations already occupied by the CAD route from
possible new locations, at the path sampling resolution. Surface screening does not detect
self-contact or guarantee clearance for a tube wholly enclosed inside a solid. Neighbouring
tubes remain at their drawn positions during a single-run review.

## The six ties in the exposed runs

These readings use straight stock and coil curvature in both senses about XY, XZ and YZ,
at an assumed 250 mm coil radius. Each range covers those seven scenarios. Shift is the
largest displacement of a material station from its CAD position, in millimetres.

| Run | Hold retained | Hold omitted | Reading |
| --- | ---: | ---: | --- |
| fluid-18 | 59.9–66.0 | 78.7–93.7 | The post limits movement. Even with it, the free shapes reach surrounding hardware. |
| fluid-28 | 14.0–15.0 | 26.5–28.4 | The retained rib avoids the new contact locations seen when it is omitted. |
| water-3 | 35.7–43.9 | 50.8–64.0 | The post limits movement; the free shapes still reach the cap and neighbouring plumbing. |
| co2-2 | 8.4–8.5 | 35.1–43.0 | The rib strongly limits movement. The retained shapes still reach the main board. |
| carb-1 | 10.1–10.4 | 30.7–41.6 | The rib limits movement; omitting it introduces contact toward V-K and the funnel. |
| fluid-14 | 11.8–13.8 | 45.1–49.5 | The cap rib strongly limits movement; retained shapes reach fluid-18 and V-K. |

The retained straight-stock fluid-18 shape shifts 62.5 mm and has possible new contacts at
front-top, back-top, the Seaflo pump and water-6. Its post's seat axis lies about 0.7 mm from
the authored arc; the model holds the actual seat axis. That difference describes the tie
straightening the approach and does not by itself establish a misplaced post.

For fluid-28, the retained straight-stock shape shifts 14.2 mm with no new sampled contact
locations. Omitting its rib gives 27.0 mm and introduces contact at water-3, back-top and the
ASSE drip pan. This is a clear example of a tie doing useful work without reproducing the
drawn corners.

The co2-2 result is smaller in displacement but adjacent to the main board. All seven
retained scenarios identify that contact. The free shapes of water-3 and fluid-18 also meet
their surroundings with their existing holds present. These are contact-sensitive routes;
the unloaded model cannot determine where an installed tube settles against those bodies.

Several visibly different shapes have no new sampled contacts in the straight-stock case:
fluid-24 shifts 32.6 mm, fluid-26 13.2 mm and fluid-16 9.7 mm. Displacement alone is not an
anchor requirement. Carb-2 remains straight with zero displacement; its sleeve has contacts
already present in the CAD envelope. Fluid-4 is the deliberately loose, hand-positioned
drain run; its large free excursion does not represent its placed operating shape.

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

The interactive solver runs in a worker. The 17 runs and six single-hold omissions give 161
cases across the seven assumptions above; all converge. On the development Mac the median
solve is about 7 ms and the slowest about 81 ms. For fluid-18, refining the nominal 6 mm
sampling to 3 mm changes the shape by less than 0.08 mm across those assumptions, with and
without its post. The solver reports length residuals and unfinished or infeasible results.

The numerical tests cover developed length, finite restraints, endpoint directions, analytic
bending cases, symmetry, refinement and infeasibility. Contact tests cover triangle crossings,
local sleeve radii and bounded interface exemptions. Browser tests exercise the real assembly,
hold omission, changing assumptions, mobile framing, model changes and stale-data refusal.

The producer's optional `--reference` mode is experimental offline gravity/contact tooling.
It is not used by the viewer or by the readings above. Viewer behaviour and implementation
are described in [`web/README.md`](/web/README.md#tube-shape-review).
