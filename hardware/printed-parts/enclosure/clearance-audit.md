# Enclosure clearance audit

The assembly has **two unintended collision families** and **six additional fit families below 0.15 mm**. The quadrant seams and tee-carrier guides meet the running-clearance target.

Current fit confirmations: the [copper-slot covers](../cold-core/copper-plugs/README.md)
have **0.44 mm clearance** to the valve tray, with zero overlap on both sides
([verification](../cold-core/copper-plugs/clearance-check.json)). Derek confirms that the
**enclosure display fits well in the current prints**; F1's exact-size reference envelope
does not establish a physical fit problem. The pump casing passages provide **0.25 mm per
side** in the current pump tray. The detailed reading below identifies its own geometry inputs.

Reading: **2026-09-13**, geometry at `7ed198a4ca7b3a067128dfaad158629be31ae3fe`. All dimensions below are millimetres. The [evidence](clearance-audit.json) retains input hashes, exact distances, intersection volumes, witness coordinates, section measurements and motion results.

The target is **0.15 mm per face, measured normal to the mating surfaces**. [fits.py](/hardware/printed-parts/cadlib/fits.py) applies that figure to printed running fits and exempts the datums that screws, bearings and stops close against. Purchased-part fits below the same threshold are identified separately. A larger gap passes this minimum; its actual value is recorded below.

| ID | Interface | Reading | Classification |
|---|---|---:|---|
| C1 | Both copper plugs / front-top aft valve tray and foot | **0.560 mm penetration**, **292.621 mm³ overlap each** | Rigid printed parts intersect |
| C2 | Internal soda-water outlet tube / reservoir B | **0.034010 mm penetration**, **0.022162 mm³ overlap** | Tube intersects reservoir corner |
| F1 | Enclosure display body / housing passage | **0.000 mm** on four sides | Nominal hardware envelope has no insertion allowance |
| F2 | Funnel fore ramp / front-top | **0.036369 mm** normal gap | Sloped fit is short by 0.113631 mm |
| F3 | Pump cartridge and cap / fixed bulkhead | **0.100 mm** | Both printed aft faces are short by 0.050 mm |
| F4 | Nameplate bevel / pocket bevel | **0.106066 mm** | Printed bevel fit is short by 0.043934 mm |
| F5 | Pump jack and rear keystone / body pockets | **0.125 mm per side** | Modeled purchased-part fit, short by 0.025 mm |
| F6 | Four pump tube casings / cartridge passages | **0.125 mm per side** | Stated purchased-part fit, short by 0.025 mm |

## Collisions

**C1 — Copper plugs.** Each PETG plug has a 1 mm outer flange ahead of the foam shell. The shell starts at Y178.000; the plug reaches Y177.000; front-top's fore-facing aft valve tray and its foot reach Y177.560. Their common solid is a rectangular strip:

- West: X−81.750…−73.250, Y177.000…177.560, Z160.000…221.475.
- Port: X73.250…81.750, with the same Y/Z limits.

Each intersection spans **8.5 × 0.56 × 61.475 mm**. It is present in the exact STEP geometry and in the current front-top STL: **292.620 mm³ per plug** in the print mesh. The plugs are rigid PETG, not a compressible gasket. At least **0.710 mm additional separation** is required at these faces to reach 0.15 mm air.

Source: [enclosure.py](/hardware/printed-parts/enclosure/enclosure/enclosure.py), `_valve_trays`, lines 8011–8013 and 8031–8035; [copper_plugs.py](/hardware/printed-parts/cold-core/copper-plugs/copper_plugs.py), flange dimensions at lines 135–149. World points **(±77.5, 177.28, 190)** lie inside the interference.

**C2 — Internal soda-water outlet.** `cold-core/line-carb-water-out` enters reservoir B's R6 centerward corner near **(65.117, 266.428, 207.612)**. An exact boolean produces one common solid of **0.0221615123 mm³**; its deepest measured penetration is **0.034010 mm**. This contact is unrelated to a fitting, support or seal.

Source: [\_internal_routes.py](/hardware/printed-parts/cold-core/_internal_routes.py), the `carb-water-out` path at lines 360–366. Its route fitter accepts up to **0.1 mm³** overlap at lines 530 and 546, which admits this contact without establishing any free clearance. The intersecting region spans X64.490…65.744, Y266.309…266.548, Z206.708…208.515.

## Undersized free fits

**F1 — Display body.** The housing passage and the reference body are both **106 × 69 mm**, sharing all four lateral planes away from the glass's axial seat. Exact common volume is zero, but there is no insertion allowance. A 0.15 mm allowance on each side corresponds to **106.3 × 69.3 mm** at the existing position. A witness on the +X face is **(53.5, 43.006989, 316.993011)**. The source reference is a keepout envelope, not a measurement of the purchased module; the physical fit remains unverified.

Source: [enclosure.py](/hardware/printed-parts/enclosure/enclosure/enclosure.py), lines 434–435 and 3255–3260; [waveshare_43b_display.py](/hardware/reference/waveshare-43b-display/waveshare_43b_display.py), line 46. The glass and gasket edges are surrounded by the display cover's correctly offset inner wall and have 0.15 mm lateral air.

**F2 — Funnel ramp.** The four vertical collar faces have **0.150000 mm** clearance. The sloped fore ramp has **0.036368522187 mm**. The keepout loft grows its rectangle and circle in XY by 0.15 while retaining their heights; that construction does not maintain the same distance normal to the slope. Closest points are front-top **(−74.968866, 81.429412, 338.498291)** and funnel **(−74.959923, 81.429450, 338.533543)**. The front-top STL agrees with the shell witness within **0.0000004 mm**. The brim underside is the separate bearing datum. The funnel is cast silicone; this reading does not establish its insertion force or deformation.

Source: [enclosure.py](/hardware/printed-parts/enclosure/enclosure/enclosure.py), `_funnel_keepout_source` at lines 3529–3552 and its application at line 8933.

**F3 — Cartridge and cap aft faces.** Both parts end at **Y79.419**, ahead of the bulkhead's **Y79.519** face. The 0.100 mm gap is explicitly running clearance. The cartridge's floor bearing is a separate zero-gap datum. Increasing only `cap_kiss` to 0.15 would violate the existing **3 mm pump-skirt band** constraint; that stock and the clearance require a coordinated adjustment.

Source: [enclosure.py](/hardware/printed-parts/enclosure/enclosure/enclosure.py), `cap_kiss` at line 1558, `pump_cartridge_aft_y` at lines 5299–5310 and the cap's shared aft plane at line 6145.

**F4 — Nameplate bevel.** Straight pocket edges have 0.150000 mm air. All eight planar/rounded bevel faces have **0.106066017 mm** normal air. Giving both parts the same 45° bevel while enlarging the pocket outline by 0.15 yields **0.15 / √2** on the bevel. The pocket floor is an intentional clamping datum. Example opposing bevel centers: plate **(88.925, 464, 262.9)**, pocket **(89.075, 464, 262.9)**.

Source: [enclosure.py](/hardware/printed-parts/enclosure/enclosure/enclosure.py), `_nameplate` at lines 3382–3414; [nameplate.py](/hardware/printed-parts/enclosure/nameplate/nameplate.py), `SLIP`, `BEVEL` and the chamfer at line 474.

**F5 — Both keystone pockets.** `FIT_SLIP = 0.25` is subtracted once from each full modeled body dimension. That leaves **0.125 mm on each side**, confirmed in the rear pocket and the pump-jack pocket. Their shoulders and catches are separate locating contacts. The reference is representative geometry; actual purchased body dimensions remain unverified.

Source: [riteav_keystone.py](/hardware/reference/riteav-keystone/riteav_keystone.py), lines 95 and 175; pump receptacle placement in [enclosure.py](/hardware/printed-parts/enclosure/enclosure/enclosure.py), line 5810.

**F6 — Pump casing passages.** The four **Ø12.75 mm** casing envelopes have **13.00 mm** passages, giving **0.125 mm** per side. All four actual passage sections reproduce that value. The source specifies these dimensions explicitly; the main pump reference solids do not model the casings individually.

Source: [kamoer_kphm400.py](/hardware/reference/kamoer-kphm400/kamoer_kphm400.py), lines 62–70; [enclosure.py](/hardware/printed-parts/enclosure/enclosure/enclosure.py), lines 1590–1593 and 5417. A 0.15 mm radial fit around the stated casing corresponds to **13.05 mm**.

## Other readings below 0.15 mm

These are specified hardware or process fits, rather than additional violations of the shared printed-to-printed running-fit rule.

| Interface | Reading | Basis |
|---|---:|---|
| Copper tails through foam-shell slots and plug arches | 0.075 mm nominal radial | Ø6.35 copper in a 6.50 opening; copper is lowered into an open slot |
| Routed inlet copper / port plug at the entrance bend | 0.027874 mm minimum | Exact placed solids; the bend approaches the front edge of the arch |
| Reed bridge / carbonator | 0.050 mm | Authored seating allowance beneath the clamping wrap |
| PRV shroud / stated Ø18.8 elbow seat | 0.100 mm nominal radial | Ø19.0 shroud bore; source-derived hardware fit |
| Carbonator endcaps / tube | 0.127 mm | Metal weld fit, outside the printed running-fit rule |
| PRV vent tube / foam-shell route opening | 0.148450 mm | Exact swept geometry, 0.001550 mm below the nominal target |
| PRV vent tube / shroud | 0.149503 mm | Exact swept geometry, 0.000497 mm below the nominal target |

The shared **Ø6.65 mm** fluid-line openings provide 0.15 mm radial air around the CAD's **Ø6.35 mm** tube. Against the **Ø6.50 mm** tube documented at the upper end of the measured spool band, the allowance is **0.075 mm per side**. A physical 0.15 mm-per-side requirement at that upper diameter corresponds to **Ø6.80 mm**, before any printer compensation. Sources: [\_cold_core_interface.py](/hardware/printed-parts/cold-core/_cold_core_interface.py), lines 114–120; [copper_plugs.py](/hardware/printed-parts/cold-core/copper-plugs/copper_plugs.py), lines 104–114; [reed_bridge.py](/hardware/printed-parts/cold-core/reed-bridge/reed_bridge.py), line 162; [prv_shroud.py](/hardware/printed-parts/cold-core/prv-shroud/prv_shroud.py), line 86.

## Verified fits and contacts

| Interface family | Reading | Coverage |
|---|---:|---|
| Quadrant Z-seam arms, feet, heads and channels | 0.150 mm | Both flanks, both columns; local face sections |
| Y-seam flank/ceiling tongues and upper pin passages | 0.150 mm | Both flanks and ceiling |
| Floor and handhold 45° scarf laps | 0.150 mm normal | Correct `slip * √2` closure offset |
| Display-cover outer border and deeper inner seat | 0.150 mm | Straight edges and rounded corners |
| Funnel vertical collar | 0.150 mm | All four faces |
| Carrier web guides, flat grip undersides, roofs and retaining rims | 0.150 mm | Both halves; source-built solids and current front-top |
| Carrier / fore valves; aft coils | 0.150 / 0.350 mm | Release and park, fresh component geometry |
| All ten Wago pockets; MQ6 grooves; core corner stops | 0.150 mm | Non-datum faces |
| All five bulkhead-ring pocket outlines | 0.150 mm | Circular and straight boundaries |
| Pump cap / cartridge | 0.200 mm | Whole-shape minimum and cap lift |
| Pump heads / cartridge; motors / cap | 0.150 / 0.635 mm | Actual head surfaces and stated motor diameter |
| Maximum-OD springs / fixed and moving seats | 0.165 mm | Ø6.07 maximum OD in Ø6.40 bores |
| Tee journals | 0.250 mm nominal radial | Hardware journal clearance |
| ASSE, flow-meter, tube and body anchors | 0.200 mm | Seated sections; axial datums treated separately |
| ASSE drip pan / sleeve | 0.300 mm | Printed running fit |
| Electronics non-datum flank faces | 0.250 mm | Main board, PSU and relay mounting region |
| C14 pocket/shroud | 0.500 mm nominal | Flange seating face is a datum |
| Compressor posts / donor bores | 1.000 mm radial | Four posts; isolation stack has a separate preload allowance |
| Condenser fore grooves / sheet flanges | 0.300 mm | Fore stops and aft mounting faces are datums |
| Condenser aft fingers / fin envelope | 1.000 mm nominal | No exact overlap |
| Fuse clamp side channel | 0.200 mm | Pinching and heat-transfer faces are datums |
| Bulkhead barrels / wall bores | 0.430 mm radial | All five crossings |
| Rear customer collars / tubes | 0.165 mm radial | Calibrated collar bore |
| Reservoirs / foam-shell sidewalls | 0.500 mm | Both reservoirs above floor supports |
| Foam-cap bottom lid pads / reliefs | 0.200 mm nominal | Shared pad/relief construction |
| Standing cap columns / lid holes | 0.400 mm nominal | Shared cap interface construction |
| M3 seam screw shanks / heads | 0.450 / 0.325 mm radial | Ø3.9 passages and Ø6.15 counterbores |

The six quadrant pairs have **zero exact overlap** in their assembled positions. **24 Z-slide stations** and **10 Y-telescope stations** also have zero overlap. The top catches engage when either top is lifted. These station checks supplement the measured running faces; they are not a continuous closure proof.

The carrier's complete insertion and operating-envelope check passes **367 checks**, with **0.15 mm X/Z air** around each carrier sweep and **zero unintended overlap**. Both end stops, forty independent transverse-capture checks and the upper/lower bearings engage. Additional exact measurements cover cartridge/cap extraction, spring maximum diameter, pump casings, jack pockets and installed valve/coil distances.

Intentional contacts include seam shoulders and screw interfaces; cartridge floor bearing; carrier center lap and stroke stops; pump bracket/boss seats; spring ends; display-cover lands and gasket faces; funnel brim; nameplate/ring pocket floors; Wago insertion stops; hardware mounting faces; cold-core floor/rear/hold-down datums; and reservoir floor supports. Each reservoir has **666.338 mm²** of floor-support contact with **zero overlap**. Heat-set pilots, soft seals and made-up tube joints are process or compression fits. The core's nominal coil solid has declared overlaps where the real wrap rises over the reed bridge; those do not establish a new enclosure collision.

## Measurement coverage and existing checks

The screen contains **207 named placed CAD bodies**, including all **62 cold-core bodies**, plus a separate foam-envelope comparison. It considers the **21,321 distinct-body pair population** and **145 additional envelope pairs**. Nameplate lettering and its plate are treated as regions of one print. Bounding boxes eliminate distant pairs; a 0.20001 mm mesh horizon, allowing for the mesh's 0.02 mm deflection, selects close pairs for OpenCascade distance queries. **313 exact pair-distance results** are retained, with **zero unanswered queries**. Focused face/section tests address free surfaces hidden by whole-part datum contacts. All 208 B-reps, including the extra envelope, are valid.

The pack and seated components are built from source. The six enclosure pieces use the current standalone STEPs, including the completed front-top and cartridge work. Source-derived and stored enclosure boxes agree within **0.000000101 mm**. Geometry sources remain unchanged during the build. The current watertight front-top STL independently confirms the plug collisions and the display/funnel surface locations. The aggregate enclosure STEP is not the source for those updated parts.

The existing enclosure scorecard does **not** establish these 0.15 mm fits:

- [\_scorecard.py](/hardware/manifold-layout/_scorecard.py), lines 117–123, replaces cold-core internals with the foam envelope. The protruding copper plugs therefore receive no enclosure-wall collision check.
- The same file, lines 1259–1270, omits printed enclosure pieces from the component clearance pass. It cannot report undersized component-to-wall air.
- [\_internal_routes.py](/hardware/printed-parts/cold-core/_internal_routes.py), lines 530 and 546, uses an overlap-volume allowance rather than a minimum-distance requirement.
- [\_meshes.py](/hardware/scripts/_meshes.py) states a 0.02 mm chord deflection. Its bounded mesh measurements suit the existing 1 mm pack-clearance gate; this audit resolves near-threshold candidates on exact surfaces.

These are nominal geometry readings. Display and keystone hardware use representative envelopes; pump casing checks use the stated diameters. Printer error, slicer compensation, support-contact finish, casting change and loaded deflection are not measured by this audit.
