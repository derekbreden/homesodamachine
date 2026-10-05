# Gun positioner: independent review

An engineering and safety review of the gun positioner and its controller. It is the
counterpart to the design files, which say what to build. This page holds the loads, margins
and conditions the design must meet, and the measurements that show it does. Every figure
here is a screening estimate or an acceptance condition; none is a physically demonstrated
capacity. Sources:

- [`gun_positioner.py`](../printed-parts/fixtures/gun-positioner/gun_positioner.py) and its
  [`requirements.json`](../printed-parts/fixtures/gun-positioner/requirements.json) and
  [`geometry-check.json`](../printed-parts/fixtures/gun-positioner/geometry-check.json):
  screening masses and moments from the solids, with 6061 plate, 1.55 kg/m 4040 and catalog
  masses for the purchased parts.
- [`src_gun_positioner`](../../firmware/src_gun_positioner/README.md) and
  [`control.md`](control.md).
- StepperOnline drawing A0842 (17HS19-2004S1); the PIB F8-16M drawing; BIGTREETECH's
  TMC2209 V1.3 schematic; the FoMaKo K20UH manual; the X1 Pro manual.

Scope is dry development. The controller has no laser output, and the rotator stays
pedal-controlled.

## Loads

Screening estimates from the CAD solids of `gun_positioner.py` (sha256 e219feaa319f).
Fasteners, wiring and the supported umbilical are not modelled; allow about 10 % until the
carried pieces are weighed. The actual-load gate under
[Holding on power loss](#holding-on-power-loss) bounds the real values.

| Quantity | Screening value | Design envelope |
|---|---|---|
| Mass carried by Z | 26.7 kg, 262 N; about 290 N with hardware | 300 N, including measured cable pull and uncertainty |
| Mass carried by X / Y | 45.7 kg / 37.2 kg | — |
| Pitch gravity moment | 7.7–10.4 N·m, one sign; 78 N at the screw at the minimum dL/dθ | 100 N normal actuator force; 15 N·m shaft output |
| Roll gravity moment | 0.75–0.88 N·m; 6.3 N at the screw | 10 N·m |
| Yaw gravity moment | 0 | 10 N·m |
| Gun | 1.31 kg with feed and 4 ft of umbilical, plus a 0.25 kg shell allowance; the CAD carries 1.56 kg | — |

The angular actuators work at a minimum effective lever of 133.6 mm, where 15 N·m is
112 N at the screw.

## Holding on power loss

A Tr8×2 screw (lead angle 5.20°, flank 15°) self-locks only above a thread friction of
μ ≈ 0.088. Retention therefore comes from a passive friction brake on the screw side of
each belt.

- **Brake:** an anti-rotated, free-tilting steel washer (M12, 13 × 37 × 3 mm) presses on the
  13–22 mm annulus of a 243-locked fixed-end flange nut (mean radius 8.94 mm). A soft central
  spring (25 mm free, accepted at 20–40 N/mm) loads it from a seat plate on four M6 posts.
- **Drag windows,** against frictionless back-drive (F × 2 mm / 2π) at the design envelope:

  | Axis | Window | Nominal | Back-drive at the envelope | Twice the back-drive |
  |---|---|---|---|---|
  | Z | 0.20–0.23 N·m | 0.215 | 0.0955 N·m at 300 N | 0.191 N·m |
  | Pitch | 0.06–0.08 N·m | 0.07 | 0.0318 N·m at 100 N | 0.0637 N·m |
  | Roll | 0.02–0.04 N·m | 0.03 | from the measured cable moment | — |

  X, Y and yaw carry no gravity and have no brake.
- **Acceptance is conditional on the measured load:** the brake's measured lower bound
  (T − U) must be at least twice the ideal back-drive of the measured actual load, and the
  whole interval must lie in the window. At the 100 N envelope, pitch therefore needs at
  least 0.0637 N·m, inside 0.06–0.08.
- **Spring force:** at μ 0.15–0.35 the windows need 64–171 N on Z, 19–60 N on pitch and 6–30 N
  on roll.
  - At 20 N/mm, 171 N is 8.6 mm of compression; check the spring's solid height against it.
  - A spring near 20 N/mm holds ±0.01–0.04 mm of face runout to ±0.1–1.3 % of Z drag.
  - The seat position is finished by measured torque, not by thread counts or an assumed μ.
- **Conditions:**
  - The washer tilts freely on the spring; its two M3×50 guide bolts do not bind it.
  - The friction face stays free of screw grease; grease drops μ about threefold. Re-measure after any lubrication.
  - The flange supports the washer fully, and contact is checked through a complete turn.
  - Thrust-stack preload stays at or above the spring force divided by 2.83.
- **Torque measurement, screw horizontal, gun removed:** a balanced metal service lever replaces
  the pulley on the rotating flange (four M3 bolts), with the hanging mass at exactly 100 mm.
  - Mass per drag at 100 mm:

    | Drag (N·m) | 0.02 | 0.03 | 0.04 | 0.06 | 0.07 | 0.08 | 0.20 | 0.215 | 0.23 |
    |---|---|---|---|---|---|---|---|---|---|
    | Mass (g) | 20.4 | 30.6 | 40.8 | 61.2 | 71.4 | 81.6 | 203.9 | 219.2 | 234.5 |

  - Breakaway in both directions at eight shaft phases 45° apart. A hanging mass acts
    directly only at the horizontal load-hole phases; elsewhere the load goes through the
    characterized tangential cord redirect.
  - Weigh cup, cord and load. Pass: the whole interval [T − U, T + U] lies inside the window.
- **Installed Z, screw vertical:** the cord leaves the lever horizontally and tangentially over
  a 608 redirect on a clamped metal bracket and turns 90° into the hanging load.
  - Wheel loss in both directions with two 200 g cups: movement begins with no more than 5 g
    imbalance, which bounds the correction at 0.00491 N·m. Load-dependent loss up to the
    235 g Z maximum, tangent alignment and the bracket go into U as well.
- **Actual load bound, before loaded motion:**
  - Weigh each carried piece on the 2 kg scale (heavier subassemblies on the 500 N gauge),
    including fasteners, wires, gun and supported umbilical.
  - Z: the 500 mm 4040 test column, braced to the station by two spare corner brackets,
    carries the 70 × 160 mm gauge backing. A jack angle below it feeds the backing up on a
    fully threaded M6 screw, at most 1/12 turn (0.083 mm) per step, relocked each time, so the
    gauge and its 60 × 40 mm platen take the load under the Z-head upright with an
    independent catch within 1 mm. Only then is the actuator output disconnected. Record
    increasing and decreasing onset with the real cable over the accepted poses; a resting
    reading alone can hide rail stiction. The larger onset plus uncertainty, or the summed
    carried weight if that is larger, stays within 300 N. The column never carries powered
    travel, and nothing is lifted by hand.
  - Pitch and roll: the real gun and cable stay on their output hubs. Parked on independent
    supports, the rotor load passes to the gauge or characterized cord before its actuator
    clevis opens. The balanced 100 mm load lever bolts to the separate drive-lever hub on its
    four M5×45 bolts, with the output-hub attachment and both hub clamps kept. The
    normal supports are then cleared from the measurement path, the catch kept close. At
    each accepted pose the 500 N gauge on its 70 × 110 mm backing, or weighed cups and the
    redirect for the small roll forces, measures the signed tangential onset in both
    directions, with no unrestrained move or catch contact.
  - The larger absolute threshold plus its complete uncertainty bounds the output moment,
    bearing resistance and the cable's free couple included; the open clevis excludes screw,
    brake, motor and belt drag. The two thresholds are not subtracted, and friction is not
    assumed symmetric. Dividing by the minimum measured dL/dθ over the accepted path gives
    actuator force; the 133.6 mm geometry lever applies only once the pin and radius
    dimensions pass the geometry screen. Pitch must stay within 100 N.
  - The loose powered-test cartridge does not measure the installed load. Restore the clevis
    and hub hardware, preload and witness marks, and a fresh observed datum, before motion.
- **Power-cut screen:** tube removed, cameras retracted, laser key off; independent steel
  tethers and a metal support stand with at most 5 mm catch gap and 10 mm clearance from fixed
  metal.
  - Real gun and supported cable at the accepted gravity poses, the Z endpoints and pitch −20°
    and +10°.
  - The owned indicator on rigid metal; record the powered baseline and both camera views,
    cut 24 V motor power, read at 0, 1, 5 and 10 min.
  - Pass: no indicator-resolved growth, no visible jump or slip, no catch contact. The
    indicator reads in 12.7 µm increments, so this is a coarse screen; claims at the 5–10 µm
    level need an independent reference.
- **Recheck:** before each loaded session, inspect the washer, guide bolts, seats, witness
  marks and tethers, and check full-turn breakaway. Repeat the torque and power-cut screens
  after the first 30 minutes, thermal settling, cleaning, adjustment, replacement, any slip
  or an unexplained response.

## Motor torque and current

Holding torque is estimated by scaling drawing A0842 (0.59 N·m with both phases at 2.0 A)
as about 0.295 N·m per A RMS. RMS current is (CS + 1)/32 × V_FS/(R_sense + 0.02 Ω)/√2 with
R110 sense resistors.

| Axis | Current scale, VSENSE | Nominal current | Holding-torque estimate | Screening demand at the motor | Ratio |
|---|---|---|---|---|---|
| Z | 22, 0 (V_FS 325 mV) | 1.271 A RMS, 1.797 A peak | ≈0.375 N·m | (0.0955/0.20 + 0.23)/(4 × 0.9) = 0.197 N·m | 1.9× |
| Pitch | 14, 1 (V_FS 180 mV) | 0.459 A RMS | ≈0.135 N·m | (0.0318/0.20 + 0.08)/3.6 = 0.066 N·m | 2.0× |
| X, Y, yaw, roll | 10, 1 | 0.337 A RMS | ≈0.099 N·m | no gravity load | — |

- The demand assumes 20 % screw efficiency, the 300 N and 100 N envelopes and the full drag
  window. The ratios are screens, not a running-torque or thermal margin.
- **Current tolerance:** the TMC2209 reference is ±5 % and the sense resistors are not
  individually measured. At +5 % reference and −5 % sense, Z peaks at 1.97 A, inside the
  motor's 2.0 A phase rating. The currents are nominal, not calibrated.
- **Loaded motion acceptance:** forward and reverse at the final per-axis current and every
  permitted speed, with the brake inside its window, each move observed completing and
  settling by indicator or camera rather than by the returned count.
- **Thermal gate:** at final current, rate and duty, three consecutive 5-minute intervals show
  no rising trend beyond instrument repeatability, and every motor-case reading plus its
  uncertainty stays at or below 50 °C. Log the Z driver heatsink as well: at 1.27 A RMS it
  depends on its heatsink and the fan. Repeat response, retention and datum checks after
  settling.
- **Stall force:** at 20–40 % screw efficiency the holding estimates drive about 0.85–1.7 kN on
  Z, 0.31–0.61 kN on pitch and 0.22–0.45 kN on the other axes. The force links bound all of
  them; motor current is not a force limit.

## Screw ends

- **Fixed end:** F8-16M pair either side of a 6.35 mm bulkhead, held by one Loctite-243-locked
  brass nut each side, degreased, cured 24 h and witness-marked.
  - A jammed pair alone does not hold against reversing torque.
- **F8-16M:** Ca 3.92 kN, C0a 4.99 kN per the PIB drawing; budget listings state 2.5 / 3.0 kN.
  - The shaft washer (8.0 bore, 15.8 OD) and housing washer (8.2 bore, 16.0 OD) differ; check each with the caliper.
  - The bulkhead has a 10.5 mm clearance hole. Its flat face supports the housing race over the 10.5–16 mm annulus; the 8.2–10.5 mm inner band is unsupported.
  - Center the housing race at assembly and qualify the assembled thrust reaction at the screening load. No counterbore is required.
- **Preload:** finger-tight on the 22 mm flange, 0.1–0.3 N·m, giving about 120–350 N.
  - A wrenched 1 N·m is about 1.1 kN; do not wrench it.
  - Measure the thrust stack and preload before the threadlocker cures.
- **Radial support:** KP08 bearings on metal risers (11.35 mm fixed, 5 mm floating, finished
  to the received center height) guide the screw crest; they are not axial retainers.
- **Z compression:** gravity keeps the 400 mm Z screw in tension because its thrust end is at
  the top. Upward obstruction loads it in compression, bounded by the 350 N upward ceiling;
  the 5.5 mm-root Euler screen is 554 N (1.58×). Guarded powered tests must show no bow,
  capture impact, yielding or loss of load.
- **Moving nut:** one brass nut per screw. Backlash and reversal are measured as part of qualification and learned by the observation loop, not removed mechanically.

## Overload

At the stall forces above, the gimbal sees up to 41–82 N·m on pitch and 30–60 N·m on yaw and
roll at the 133.6 mm minimum lever. The plain 12 mm shafts reach torsional yield near 40 N·m
on the 205 MPa assumption, and the hub clamps are proofed only to 1.2 times the torque the
links allow (30–32.5 N·m on the pitch drive path, 25.2–27.5 N·m elsewhere). Nothing in the
drivers detects a stall: StallGuard works only in StealthChop, and the firmware runs
SpreadCycle. The force links are therefore the machine's force limit.

- **Seated detents:** each link direction is a pair of 16 OD × 20 mm die springs pressing a
  seat washer against a metal shoulder.
  - Below preload the load passes through a stiff metal-to-metal path; above it, only that direction's springs move.
  - The nominal rate is 43 N/mm per spring, 86 N/mm per pair; graded rates govern.

  | Link | Seated preload (compression) | Nominal trip | Static acceptance | Powered ceiling | Compression at capture, +1.0 mm |
  |---|---|---|---|---|---|
  | Yaw, roll | 100 N (1.16 mm) | +0.30 mm, 125.8 N | 100–140 N | 140 N | 2.16 mm |
  | Pitch, both signs | 130 N (1.51 mm) | +0.30 mm, 155.8 N | 148–165 N | 165 N | 2.51 mm |
  | X, Y; Z upward | 250 N (2.91 mm) | +0.75 mm, 314.5 N | 250–350 N | 350 N | 3.91 mm |
  | Z downward | 400 N (4.65 mm) | +0.75 mm, 464.5 N | 440–500 N | 500 N | 5.65 mm |

  - The largest compression is 71 % of the 8 mm catalog rating. At capture every spring's
    actual compression stays below 8.0 mm and below its measured free-minus-solid length less
    1.0 mm.
  - Z downward is the positive screw-length, gravity-loaded direction; controller +Z shortens
    the screw. The Z link carries the stage weight in that direction at rest, so a downward
    obstruction trips at roughly 440–500 N less the weight, and an upward one only once the
    external force exceeds the weight by the 250–350 N band.
- **Spring grading:** measure free length, solid length and force through the working range
  on the guarded force fixture, and grade each direction's pair together.
  - Compression C = preload / (k1 + k2). Outer force spacer = 20 − C + 1.5 mm washer, adjusted
    for actual free length; nut outer spacer = that − 10.825 mm. Matched metal shims or
    finished tube lengths only; never printed shims in the load path.
  - The central 8.35 mm spacer is unchanged: it sets the ±1.0 mm capture independently of preload.
- **Firmware response:** the limit loops are sampled every 250 µs. At 1,000 counts/s the nominal nut advance is under 0.2 µm per millisecond after the switch opens. The force at stop is measured in the trip tests, not assumed.
- **Overload switches:** two independent NC lever switches per link, in series with that axis's limit loop.
  - Slotted mounts set at the measured trip force, nominal ±0.30 mm angular and ±0.75 mm XYZ.
  - Remaining overtravel at least 0.8 mm angular and 0.35 mm XYZ, plus 0.1 mm setup tolerance.
  - Re-close differential ≤ 0.3 mm, so a re-seated link clears.
  - A cam with a flat dwell after trip.
- **Pre-session check:** with the drivers disabled, push each link both ways by hand and confirm that `open_limit_mask` latches. A missed actuator is otherwise invisible until a crash.
- **Static trip test:** laser key off, drill motor unplugged, carriage and gun removed.
  - The 500 N gauge bolts by four M4 rear screws (41 × 73 mm centers) to a 70 × 110 × 6.35 mm
    backing plate, held vertically in the drill-press vise with the load axis up. Use the
    gauge's own screws only if they engage fully without bottoming; otherwise finish four
    M4×25 to the measured stack.
  - A metal platen reacts only on the fixed cage; the quill pusher touches only the output
    shuttle, never end plates, tie bolts, spacers or the nut cartridge. Guard the springs.
    Reverse the loose link for the other sign.
  - Read the trip force while watching the loop open. Pass: the reading with the gauge's
    full-scale uncertainty and the fixture allowance lies inside the static acceptance band;
    ±5 N of instrument allowance alone is not a complete budget.
- **Powered force test:** vessel and real gun removed; the spare screw, cut to 200 mm, in a
  test cartridge whose fixed metal foot is clamped to the table, and the output fork ahead of
  the screw tip.
  - The gauge backing is clamped vertically with the load axis down, its button on the center
    of the metal output bridge. Both fork arms attach only to the output shuttle, outside the
    fixed cage, so every fixed reaction returns through the gauge and vise. Reverse cartridge
    and fork for the other direction.
  - Pass: at every permitted current, speed and acceleration, the powered peak with tool and
    fixture uncertainty stays at or below the ceiling.
  - A low-current stall below preload demonstrates only the ceiling: observe, press STOP and
    abort without retry. Prove that all six axes inhibit and latch by opening each loop with a
    controlled external load or by hand. Do not raise current to force a trip.
  - After any trip, support the load mechanically, disconnect power, re-center and inspect the
    link, and restore a fresh observed datum.
- **Gun crash mount:** the force links protect the machine, not the gun or the tube. A stuck wire pulls about 140 N.
  - **Axial:** two seated, captured pods. NC trip at 0.25 mm, capture ±1.0 mm.
    - Preloads are set asymmetrically, with the real gun and cable fitted, so 20–30 N of nozzle force added to the gravity and cable baseline trips each direction.
    - Each pod runs on two ground, hardened Ø8 rods in bronze bushings, spaced to carry the pod's moment; collars only locate the rods.
    - Measure the spring rate and solid length on every spring before sizing spacers. The listed rate and travel of the selected spring do not agree with its wire size.
  - **Transverse:** a three-ball magnetic rear plate on metal side carriers.
    - The hardened balls sit in hardened dowel vees held by metal keepers; no ball bears on aluminum.
    - The magnets are shimmed to a measured pull-off only after the seats are fully seated. Their contact pull rating does not predict nozzle release.
  - **Retention and insulation:** short steel tethers and a padded metal catch hold the released tray. TPU insulates the gun.
  - **Re-seating:** the magnetic snap pinches fingers.
  - **Contacts:** two channels, each one bidirectional axial COM–NC cam switch plus one plate-presence switch held pressed at rest and wired COM–NO.
    - Either axial sign, a release or a missing plate opens both channels.
    - Channel A is in the STOP relay coil string, channel B in the sense loop.
    - Re-close differential ≤ 0.2 mm; overtravel ≥ 0.95 mm, measured on each switch.
  - **Threshold test:** weighed masses through the characterized 608 cord redirect, at each
    accepted pose, in both axial signs and the transverse directions. Two outboard fork arms
    and a bridge apply the cord load at the measured virtual nozzle endpoint, through a
    cross-drilled M6 stud, with the consumable wire removed and nothing pressing the nozzle
    optics, guide, trigger or vents.
    - The added force is the hanging load against a seated, zero-load gravity and cable
      baseline recorded at that pose, not a gauge total less an estimated gun weight.
    - The scale passes its check first: two minutes warm, level and draft-free; 0, 500,
      1000, 1500 and 2000 g ascending and descending for three cycles against a 1 kg OIML M1
      weight and a 1000 g M2 set. Every error ≤ 0.3 g and zero returning within ±0.1 g;
      recalibrate span with the 1 kg weight and repeat if it fails.
    - The weights carry a stated class, not a certificate. Their OIML R111 tolerances total 130 mg at 1500 g and 224 mg at 2000 g.
    - Each aliquot is weighed separately below 2 kg and carries 1.0 g of uncertainty, summed linearly.
    - The redirect is characterized with 200 g cups (≤ 5 g imbalance) and again at the
      intended 2–3 kg load, since bearing friction grows with load.
    - Pass: the full interval [F − U, F + U] lies within 20–30 N of added nozzle force, and both
      channels open every time. The 500 N gauge cannot accept this band.
    - After each release the mount re-seats securely, the pose is re-observed and calibrated afresh, and the recovery is logged.

## Geometry

- **Shafts and hubs:** four plain, undrilled 12 mm 304 shafts (yaw, two pitch stubs, roll)
  carry seven 38.1 × 38.1 × 25 mm 6061 hubs, each reamed to 12 mm, slit 1.5 mm and closed by
  two M4×50 12.9 bolts. Clamp torque is capped at 3.0 N·m including tool tolerance: 25 in-lb
  (2.82 N·m) on the ±4 % cam-over torque screwdriver, at the head with the nut held. The rods
  carry no certificate, so screening uses the annealed ASTM A276 minimum yield of 205 MPa
  (118 MPa in shear).
  - Combined stress at each shaft's worst section, at the design envelope / the link ceiling
    (165 N pitch and 140 N yaw and roll at up to 150 mm, 24.8 and 21 N·m):

    | Shaft and section | Bending | Torque | Von Mises | Factor on 205 MPa |
    |---|---|---|---|---|
    | Yaw, output hub to lower bearing | 4.3 N·m | 10 / 21 N·m | 57 / 110 MPa | 3.6 / 1.9 |
    | Pitch stub with the lever, at its bearing | 4.2 / 7.0 N·m | 15 / 24.8 N·m | 81 / 133 MPa | 2.5 / 1.5 |
    | Other pitch stub, hub to bearing | 3.2 N·m | 0 | 19 MPa | — |
    | Roll, output hub to bearing | 3.8 N·m | 10 / 21 N·m | 56 / 110 MPa | 3.7 / 1.9 |

  - **Shaft ends:** a centered 4.2 × 16 mm blind bore with at least 10 mm of usable M5 thread
    sits inside each flush 25 mm output hub; the hub's inner edge, which carries full torque
    and bending, stays solid. The bore costs 1.5 % of polar section. Clamp pressure appears at
    the bore surface as about 2.3 times its value in hoop compression, so the clamp-bolt
    torque is a limit, not a minimum.
  - **Positive axial capture:** eight M5×12 end screws, each through a 2 mm OD 20 steel washer
    and an M5 washer (9.2 mm engagement, Loctite 243, witness-marked), hold 20 mm OD ×
    12.5 mm ID aluminum spacer stacks against the hubs and bearing inner races, with no more
    than 0.5 mm of axial freedom per side. The yaw shaft hangs about 210 N from its top
    retainer onto the upper inner race. Spacers bear only on the inner race, never on the
    stationary seal or outer ring.
  - **Hub proof:** each hub is proofed ungripped on its own marked final shaft seat, the
    tapped end included, in both signs. A reaction hub beside it, with a visible 1 mm gap so
    no face carries load past the clamps, reacts through a four-M5 metal plate held in the
    vise, never by vise compression of a split hub. One KP001 sits outboard, the end keeper is
    off or visibly clear, and an independent catch stands by. A dedicated balanced 140 mm
    proof lever (300 × 30 × 6.35 mm) carries the gauge force, so the 100 mm service lever is
    unchanged. Both clamps carry the full torque.

    | Hubs | Proof band | Gauge force | Shaft at the band top |
    |---|---|---|---|
    | Pitch drive lever and negative-side pitch output | 30–32.5 N·m (1.2 × the 24.75 N·m link ceiling) | about 224 N | 188 MPa, 0.92 of 205 |
    | Yaw, roll and positive-side pitch output | 25.2–27.5 N·m (1.2 × 21 N·m) | about 188 N | 163 MPa, 0.79 of 205 |

    - The shaft figures combine torque, the lever's transverse force at 28.2 mm from the
      reacted boundary and about 50 MPa of clamp pressure at the specimen hub's inner edge.
    - Pass, at the clamp torque cap: the whole measured interval lies inside the band, with
      the actual radius, the gauge's full-scale tolerance, contact position, alignment and
      fixture allowance included, and nothing remains offset on unloading. A hub that slips is
      rejected, not tightened further.
    - Residual twist on a scribed line along the free span, or a change in straightness,
      rejects the shaft, not only the hub.
    - Repeat after cycling and thermal exposure. Nominal bolt torque establishes no capacity.
- **Clearance:** the CAD screen covers a finite set of poses with a proxy gun and records
  every collision it excluded.
  - The candidate working subset is yaw ±5°, pitch ±10°, roll ±5° and ±0.25 mm of endpoint
    offset, with XYZ correlated to hold the calibrated endpoint at the seam.
  - Poses outside the checked set are not cleared. A physical static sweep of the actual gun,
    tray, fixture, vessel, camera lenses and umbilical precedes motion.
  - The firmware enforces per-actuator bounds only. It has no general vessel keep-out.
- **Gimbal conditioning:** falls as |cos(60° + pitch)|, to 0.17 at +20°. Pitch limits are:

  | Limit | Range |
  |---|---|
  | Soft | −20° … +10° |
  | Switch | −21° … +11° |
  | Metal | −22° … +12° |

- **Fiber:** roll beyond small angles twists the fiber, which the X1 manual forbids. Both boom
  saddles swivel on 608 bearings. Radius ≥ 350 mm active and no torsion are accepted per path,
  by observation along each working path.
- **Heat:** the X1 Pro peaks at 700 W at 1080 nm. Printed parts near the tube mouth sit behind metal shields; printed parts are not beam shields.
- **Rails:** the selected SBR12 listing ([B08913HVM7](https://www.amazon.com/dp/B08913HVM7))
  prints two load tables that disagree, 600/1020 and 420/610, without units. Screening reads
  the lower static figure as 610 N per SBR12UU block. Maximum block force, with a rigid
  carriage and equal block stiffness, and the static factor against 610 N:

  | Stage | Carried mass | Gravity | Gravity + 30 N at the dot | Gravity + 140 N at the dot |
  |---|---|---|---|---|
  | X | 45.7 kg | 302 N (2.0×) | 323 N (1.9×) | 420 N (1.5×) |
  | Y | 37.2 kg | 276 N (2.2×) | 290 N (2.1×) | 347 N (1.8×) |
  | Z | 26.7 kg | 156 N (3.9×) | 168 N (3.6×) | 248 N (2.5×) |

  - The crash mount releases at 20–30 N of added nozzle force, so the 140 N stuck-wire case
    should not reach the rails. The open bushing is weaker in lift-off than the table assumes.
  - A catalog figure is not an assembly capacity. Accepted use rests on the 30 N crash gate,
    block play at ±20 N reversal on the indicator, and loaded deflection and correction
    observed by the cameras with the actual assembled mass on the accepted path.

## Controller

Verified in source on 2026-10-04:

- **Step gating:** no path emits STEP edges with STOP open, a limit or overload loop open, the supply low, a driver faulted or the heartbeat lapsed, or before REF and ARM.
- **Faults:** latch until CLEAR. CLEAR requires closed loops and drops the axis to Unreferenced.
- **Supply cycles:** a VM cycle clears driver verification. ARM re-reads every driver.
- **UART buses:** SLAVECONF sets SENDDELAY = 2 on every driver, as a three-driver shared bus requires.
- **Watchdog:** fed only while the safety tick advances.
- **Current profiles:** the bench profile runs every axis at current scale 10 with VSENSE 1; the loaded-development build runs Z at 22 with VSENSE 0 and pitch at 14 with VSENSE 1. Configuration writes each driver's CHOPCONF, VSENSE included, and accepts the driver only when the read-back matches. The host client refuses a STATUS whose current scales, rate or configured VSENSE differ from the named profile, or whose decoded VSENSE differs while `drivers_ok`.
- **Commands:**
  - STOP is recognized by prefix.
  - Acknowledgements name their command and sequence.
  - STATUS reports profile, per-axis current scales, configured and decoded VSENSE, decoded microsteps, `drivers_ok`, `vm_epoch` and `timer_ticks`.
- **Policy tests:** check explicitly and pass with `-DNDEBUG`.
- **Driver modules (BTT TMC2209 V1.3 schematic):**
  - R110 sense resistors.
  - PDN_UART is header pin 5, the A4988 MS3 position, with a 20 kΩ pull-down. CLK also has a 20 kΩ pull-down.
  - SPREAD has only an unpopulated pull-up position (R7) and no header pin. The firmware's check that `DRV_STATUS.stealth` stays 0 confirms SpreadCycle.
  - Three modules on one bus present about 6.7 kΩ to ground. Each bus has a 1.8 kΩ pull-up and a 330 Ω TX series resistor, and the Pico drives TX high except while it reads a reply.
  - Rotating a module 180° puts VM on DIR; the carriers mark the EN/VM end.
- **Fuses:** the fast AGC fuses carry datasheet DC ratings. Their margin against the inrush onto the 24 V bus capacitance, into the 5 V converter and into the fan is confirmed at the cold-start gate. The Z motor draws about 0.2 A from 24 V at 1.27 A RMS phase current, well inside its 1 A branch fuse.

## Before any live weld

The current build never commands or enables emission. Connecting it to the X1 Pro is a
separate gate with its own design review and protection selection, based on the maker's beam
hazard data. These facts bound that gate:

- **Emission veto:** the only documented hardware input that stops emission is the X1's external e-stop on the rear DB25 "EX CTRL" port. Its pins, voltage and latching are unmeasured.
- **Gun mount insulation:** a conductive gun-to-frame path could permanently satisfy the X1's clip-conduction interlock, so the mount is insulated.
- **Aiming dot:** whether the dot stays lit with the key out and the loop open is unverified; a dry-run lockout depends on it.
- **Trigger:** how a machine-held gun is triggered is undecided.

## On arrival

- **TMC2209 modules:** sense resistors print R110; silkscreen matches the schematic.
- **SBR12 rails:** base holes are listed Ø4.0, which passes M3, not M4. Transfer-drill from the actual rails.
- **KP08:** bolt spacing is not printed on the selected listing. Transfer-drill, and finish the risers to the received center height.
- **Five-pack motors:** the label reads 17HS19-2004S1. Mount on face and pilot only.
- **M8×50 hinge and axle bolts:** 50 mm under the head is 28 mm of thread and 22 mm of smooth shank; the 9.65 mm thread-start spacers assume that split. Measure it.
- **Large washers:** the M3 and M4 large washers are 12 mm OD × 1.0 mm. Check them against each grip before fitting the hinge retainers and KP08 risers.
- **Tube:** 8 × 6 and 10 × 8 mm tube carries clamp loads as cut spacers; face each to its drawn length, and drill the hinge and swivel contacts to 8.5 mm.
- **Springs:**
  - Grade the friction-brake, detent and crash-pod springs on the guarded force fixture with the force gauge.
  - Pair detent springs within ±5 % rate and ±0.1 mm free length.
  - Check the brake spring's solid height against 8.6 mm of compression.
- **Gimbal shafts:** measure the 304 rods (diameter and straightness); with no certificate,
  their yield stays the 205 MPa assumption. Drill and tap the ends centered, with cutting
  fluid and the spiral-flute tap, and check 10 mm of usable thread before fitting the M5×12.
- **KP001 inner race:** measure its face OD before cutting the 20 mm spacers; relieve or
  chamfer any spacer whose face would reach the seal.
- **FoMaKo tripod socket:** measure the depth before choosing the washer stack; the published documents do not state it.
