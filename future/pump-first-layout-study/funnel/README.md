# Aft-growing funnel geometry

The selected study extends the funnel mouth, cover and removable frame 60 mm aft. The
display edge, flush brim, drain, elbow cradle and straight cleaning lift retain
their installed datums. The native cavity holds **715.057 mL to the brim** and
**463.244 mL with 10 mm headroom**. This is an increase of **259.875 mL,
57.09%**, using the same cavity integration as the installed 455.182 mL funnel.

| Native cavity reading | Installed reference | Aft-growing study |
| --- | ---: | ---: |
| Capacity to brim | 455.182 mL | 715.057 mL |
| Capacity with 10 mm headroom | 295.170 mL | 463.244 mL |
| Collar | 165 × 117.683 mm | 165 × 177.683 mm |
| Mouth | 153 × 105.683 mm | 153 × 165.683 mm |
| Brim rear edge, world Y | 230.392 mm | 290.392 mm |
| Frame rear edge, world Y | 235.692 mm | 295.692 mm |

[`capacity-sweep.json`](capacity-sweep.json) integrates the actual rounded mouth,
lofted ramp and straight drain for the installed and selected geometries. The capacity is neither
an enclosing-box estimate nor a scaled mesh. The liquid cavity and physical
parts have separate native B-reps in [`candidate.json`](candidate.json).

[`capacity-levels.json`](capacity-levels.json) checks useful liquid levels in
that cavity. A **440 mL fill leaves 10.923 mm headroom**, and 500 mL leaves
8.540 mm. The preferred native inspection fill is 500 mL at Z346.460, below
the cover's Z349 skirt ends. A 600 mL fill stands at Z350.431 and exceeds that
closed-cover headspace. Pouring splash and actual drain rate require physical evidence.

## Working interfaces

The collar centre is X0,Y194.55. The R20 collar surrounds the R14 mouth; the
R27 brim is 179 × 191.683 mm. Its underside is Z349 and its top is flush at
Z355. The front brim remains Y98.708. The frame's front remains Y95.458,
with 0.25 mm air to the display wall at Y95.208 and the complete 3 mm roof
landing. The cover has its complete 3 mm plate, locating skirt, four friction
pads and front lifting edge.

The drain remains **X1.85,Y164.55,Z306.05**. Its 6 mm cylindrical bore grips
the retained 6.35 mm LLDPE stub over 5.015 mm. The 36 × 41.025 mm integral
silicone plug bears on the existing cradle's hooks and locates in the 36.6 mm
frame socket. The stub remains in the elbow when the silicone lifts out.
The elbow's collet pass, cradle-wing slots, 3 mm socket web and support faces
are retained. The downstream source-valve route is provided by the pump study.

The native PET-GF frame is one solid with its underside at Z299.9, socket
floor Z302.9 and production rail datum Z306.9. Both full-width corbels are
30 degrees from vertical. Their lower feet are at Y119.1 and Y270. The
removable frame carries the **complete 3 mm brim bearing**; its Boolean
missing-volume check is zero. The front surround finishes at Z355 and stops
at Y199.75, 0.25 mm before the shell seam. The rear body remains below Z349.
All new shell receivers and channels use the production rail profile.

The raised cartridge valve and its lid-rooted cradle have 1 mm-air underside
corridors through their full 102.2 mm factory closing travel in
[`underframe-reliefs.json`](underframe-reliefs.json). The valve corridor ends
at Z306.25 and the cradle corridor at Z308.3. The complete
production rails, their 3 mm roots, and the brim bearing remain unchanged.
The fixed Gate-A R14 elbow has a separate native underside relief with 1 mm
air. Its complete clearance tool ends below the Z306.9 rail band. The retained
cartridge lead passes through its native bulkhead bore and ridge clip, then
through a 1 mm-air frame chase whose upper surface is Z304.15. That chase leaves
the complete source 5.25 mm floor band through Z309.4 untouched and changes no
forward shell or cartridge passage.
The relieved frame is a valid single solid, retains its full 3 mm
brim bearing, and has at least 9.164 mm native separation from removed stock to
the silicone after the conservative forming reserve. The fitting relief does
not change the liquid cavity or its capacity. The supply tee's native clearance
is recorded against the published routing body in the same report.

The wet ramp retains the production rounded-mouth loft, with the drain toward
its front. A second ramp 6.6 mm vertically below it supplies the floor stock.
The native minimum between the actual wet and dry lateral surfaces is
**6.347 mm**, exceeding the 6 mm floor requirement; the collar retains 6 mm
stock. The simplest floor construction is in [`layout_funnel.py`](layout_funnel.py).
[`ramp-grade.json`](ramp-grade.json) records 6,669 normal samples for the
60 mm candidate, with a minimum sampled grade of 6.283 degrees. That sampled
reading does not establish the continuous minimum or complete draining.

## Shell stock and motion

[`shells.json`](shells.json) describes the native shell stock prepared for the
study assembly. The aft upper bay is cleared inside X±98.5,Y218.8–465.3,
Z253.40001–352. The 9 mm flanks, 6 mm rear wall, lower core boundary, seams,
front cartridge interfaces and exact rear C14, keystone and nameplate stock
are retained. Native original rear port, chip-pocket, C14 insert and wall-relief
tools are exported for the study's complete matched rear-interface placement.

[`roof-stock.json`](roof-stock.json) supplies the production 12 mm ceiling
stock, with the enlarged funnel opening already carved. The complete study
fuses that stock to the prepared shell and opens the final hardware crown
pockets. The source stock has a 3 mm outer roof; its manifest is an intermediate
integration artifact, not a finished uniformly 3 mm ceiling specification.

[`motion-check.json`](motion-check.json) records the silicone lift, cover lift
with intentional friction-pad contact, and frame entry through front-top.
`shells.json` adds sampled closing travel of both upper shells and customer
silicone/cover lifts against them. Every checked unintended overlap is zero.
Factory assembly keeps the front-top and its retained frame open while the bay
hardware, roof hatch and ground station are installed. The front-top/frame
closes afterward, with flexible fluid24/14/18/28 and J1/J2 linked during the
final make-up. J13's retained contact end rides on front-top with its complete
modeled run parked through the empty display passage;
[`front-loom-handling.json`](../wiring/front-loom-handling.json) proves that
constant-length article over the entire closing stroke. The display and J9
wiring are installed after closure. The hatch remains seated; final manual
lead dressing and XH insertion through the open funnel/display apertures are
outside the parked-run geometry proof.
[`frame-continuous-closure-check.json`](frame-continuous-closure-check.json)
proves the complete casting/cradle bounding sweeps continuously over the
102.2 mm frame travel, with 1 mm air. That local proof does not establish the full
factory sequence against every installed item. Customer cleaning lifts the
cover and silicone vertically; it does not require removing the frame.

These native checks apply to the named emitted parts. The full study's final
hardware and roof-host checks cover the completed arrangement. Saved geometry
does not establish loaded brim support, molded-part fit, support-removal effort
or lifetime. The accepted cradle-v4 result applies to its frozen articles;
the current frame/cradle physical scope remains as recorded in the
[funnel records](../../../hardware/printed-parts/zone-c/funnel/README.md) and
[mechanical qualification index](../../../hardware/mechanical-qualification/README.md).

## Complete casting tooling

[`candidate-aft-60-tooling.json`](candidate-aft-60-tooling.json) records the
native cavity, core, complete silicone casting and 6 × 25 mm stock steel rod.
The rounded clamping flange is **211 × 223.683 mm, R43**, preserving the
16 mm margin around the R27 brim. Its enclosing circle is **271.961 mm**
inside the acquired 299.72 mm chamber, leaving **13.879 mm radial clearance**.
The closure hardware lies inside that flange circle. Physical chamber
insertion is unqualified.

The cavity has a 5 mm base, 63.435 degree corbel, eight accessible bolt-head
pockets, eight original bolt stations on straight flanks, and two asymmetric
locators. The core has its flat dry back, tapered access and open 6.4 mm rod
guide. The lower 6.4 mm seat is 1.5 mm deep with 5 mm floor backing. The
rod's guide engagement is 7.7 mm, with 4.235 mm above the open guide.
The minimum native cavity backing is **5.010 mm** and core backing is
**7.339 mm**. The nominal finishing reserve is at least 0.30 mm.

Native checks cover complete casting equality, closed liquid containment,
parting, seven core-release poses, rod withdrawal, guide passages and
72 combined rod offset/tilt/lift poses. The new long mold uses a rectangular
liquid-complement check covering its full depth. Its nominal connected raw
liquid space is 354.155 mL; a 10% mixing allowance gives 389.571 mL. That
geometric allocation includes finishing stock and connected passages.

The [retained molding procedure](../../../hardware/printed-parts/zone-c/funnel-mold/README.md)
provides the material and process record. The new parts require their own native
slice, actual finishing/release sample, casting and physical fit evidence.
Wall count, infill and a chamber envelope do not establish pressure capacity,
stiffness or life. The applied-load screen uses the enlarged 165 × 177.683 mm
footprint and records its assumptions explicitly.

## Reproduce the study artifacts

Run from the repository root, using the installed CAD environment. Each command
reads the production source without changing its files. Native B-reps, STEP and
inspection meshes are disposable files under `.cache/pump-first-layout/funnel/`.

```sh
tools/cad-venv/bin/python future/pump-first-layout-study/funnel/capacity_sweep.py
tools/cad-venv/bin/python future/pump-first-layout-study/funnel/ramp_grade.py
tools/cad-venv/bin/python future/pump-first-layout-study/funnel/build_candidate.py
tools/cad-venv/bin/python future/pump-first-layout-study/funnel/prepare_mating.py
tools/cad-venv/bin/python future/pump-first-layout-study/funnel/build_shells.py
tools/cad-venv/bin/python future/pump-first-layout-study/funnel/roof_stock.py
tools/cad-venv/bin/python future/pump-first-layout-study/funnel/check_candidate.py
tools/cad-venv/bin/python future/pump-first-layout-study/funnel/capacity_levels.py
tools/cad-venv/bin/python future/pump-first-layout-study/funnel/build_mold_candidate.py
tools/cad-venv/bin/python future/pump-first-layout-study/funnel/underframe_reliefs.py
```

The producers default to the selected `candidate.json` aft datum. The pristine
60 mm frame is retained separately for reproducing its final underside reliefs.
