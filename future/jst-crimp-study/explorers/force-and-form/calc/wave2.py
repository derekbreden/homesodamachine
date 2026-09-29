"""Wave-2 numbers for force-and-form (jst-crimp-study, 2026-09-28).

Run:  python3 wave2.py > wave2.out.txt

Sections
  1  f1: the insulation barrel's bore at capture, against a 1.7 mm conductor
  2  harvested SN jaws: closing on an arc (in the tool) against closing straight
  3  f3: a flush pilot pin from below at the lead contact's own hole
  4  f4: how far the crimper must open for the head to leave along the wire
  5  f6: the insulation crimp on 0.49 mm silicone (grip, cut, fit in the cavity)
  6  f6: what the insulation blade's own force curve can see
  7  f6: bend-and-look, how wide a cut gapes on the outside of a bend
  8  f7: die sources, tolerances against what a crimp die needs
  9  f5b: half-row cassette at 5.0 mm, rows and forces per unit
 10  f3: chasing a measured crimp height in several hits
 11  f3: the proof pull borne on the box's rear face

Labels: [mfr], [source], [estimate], [assumption], [calc], as in the study.
Inputs from ../../../context/xh-facts.md unless marked.
"""
from math import pi, sqrt, sin, atan, degrees, radians, tan

T = 0.20             # contact stock thickness, mm            [source S19-S21]
D_WIRE = 1.70        # conductor OD, mm (+/-0.1)              [source S29]
D_BUN = 0.72         # strand bundle diameter, mm (0.69-0.74) [calc C1]
WALL = (D_WIRE - D_BUN) / 2   # ~0.49 mm silicone wall


def hdr(s):
    print()
    print("=" * 78)
    print(s)
    print("=" * 78)


# ---------------------------------------------------------------------------
hdr("1. f1: insulation barrel bore at capture (change-the-question Break 3)")
print("""Model [estimate]: at capture the insulation wing tips are pinched to the insulation
crimper's channel (inner width at the tips = channel - 2t). Each wing is a straight
plate hinged at the floor corner (the root yields first: ~6-10 N plastic hinge
[ctq calc 6]), so the clear width falls linearly from the floor's inner width at
Z = 0 to the pinched tip width at the tip height. The conductor (1.7 mm) lies on
the floor; it fits if the clear width at every height exceeds its chord there.""")


def chord(z, d=D_WIRE):
    """Width of a d-diameter circle resting on the floor, at height z above the floor."""
    r = d / 2
    if z <= 0 or z >= d:
        return 0.0
    return 2 * sqrt(max(0.0, r * r - (z - r) ** 2))


worst = []
for floor_w in (1.60, 1.70, 1.80, 1.90, 2.00):          # insulation-barrel floor inner width [assumption]
    for ch in (1.80, 2.00):                              # insulation crimper channel [mfr analog 1.8]
        for h_tip in (2.40, 2.70):                       # tip height above the floor at capture [estimate]
            tip_w = ch - 2 * T
            clr = 99.0
            zc = 0.0
            for i in range(1, 170):
                z = i * 0.01
                w = floor_w + (tip_w - floor_w) * z / h_tip
                c = w - chord(z)
                if c < clr:
                    clr, zc = c, z
            worst.append((floor_w, ch, h_tip, clr, zc))
            print(f"  floor {floor_w:.2f}  channel {ch:.2f} (tips {tip_w:.2f} apart)  tip height {h_tip:.2f}:"
                  f"  least clearance {clr:+.2f} mm at Z {zc:.2f}")
print("""-> The tips' 1.4-1.6 mm is not the bore the conductor meets: they sit 0.7-1.0 mm
   above the conductor's top. The conductor meets the wings at its equator, where
   they are still near the floor width. Least clearance runs from -0.17 mm (floor
   1.6, narrow channel) to +0.17 mm (floor 2.0). Clear at a floor of 1.9 mm or more,
   within +/-0.05 mm at 1.8, and 0.03-0.17 mm of interference at 1.6-1.7: at worst
   0.085 mm a side on a 0.49 mm wall (~17 % local squeeze), not 0-0.4 mm.
   A contact rated for 1.9 mm insulation takes a 1.9 mm wire laid into its open
   barrel, which argues for a floor near 1.8-2.0 mm [assumption]. One kit contact
   seen end-on under the ELP camera settles it.""")

# ---------------------------------------------------------------------------
hdr("2. Harvested SN jaws: closing on an arc (tool) against closing straight (die set)")
print("""The moving jaw turns about a pin parallel to the wire, so near closure the crimper
rolls in the crimp's own cross-section. R = distance from the pivot to the XH nest
[assumption: 10-35 mm; unmeasured]. Wing tips ~1.8 mm apart [source S19-S22].""")
for R in (10.0, 15.0, 25.0, 35.0):
    for travel, label in ((0.92, "first wing touch (curl starts)"), (0.20, "compaction starts")):
        th = travel / R                        # rad, rotation still to go
        dH = 1.8 * sin(th)                     # one wing touched this much earlier
        drift = travel ** 2 / (2 * R)          # sideways drift of the nest over the rest of the stroke
        print(f"  R {R:4.0f} mm, {label:31s}: crimper still {degrees(th):4.2f} deg off,"
              f" one wing leads by {dH:.3f} mm, sideways drift {drift*1000:4.1f} um")
print("""-> In the tool, one wing meets the crimper 0.05-0.17 mm of travel before the other,
   and the nest drifts sideways 12-42 um over the curl. By compaction the roll is
   under 1.2 deg (0.01-0.04 mm across the crimp). A straight die set touches both
   wings together and drifts nothing. Closing SN jaws straight should therefore
   crimp as the tool does or more symmetrically, provided the closed relative pose
   of the jaws (where they bottom) is reproduced. That is what seating the jaws by
   closing them on each other before tightening does [source: SN jaw-change
   procedure via hand-tool-as-press]. This retires wave 1's main worry about die
   route a in f3; the jaw seat geometry remains to be copied.""")

# ---------------------------------------------------------------------------
hdr("3. f3: pilot the lead contact from below with a flush-topped pin")
hole = 1.50                                            # [source S19; Wurth 1.50]
for pin_d, ch in ((1.45, 0.10), (1.47, 0.15), (1.48, 0.20)):
    print(f"  pin {pin_d:.2f} mm in a {hole:.2f} hole: float +/-{(hole-pin_d)/2:.3f} mm;"
          f" a {ch:.2f} x 45 deg lead-in on the pin catches a strip within +/-{ch + (hole-pin_d)/2:.2f} mm")
print("""  The pin rises through the track plate and stops with its flat top level with the
  carrier's top face (0.20 mm engaged). The conductor, threaded over the carrier,
  slides over a flush steel face: no bump, no tilt. A sprung hold-down on the
  carrier either side of the wire path keeps the carrier on the pin.
-> Location +/-0.01-0.03 mm at the lead contact itself, inside the +/-0.1 mm window,
   and the upstream tapered pins (terminal-supply a2) only have to bring the strip
   within +/-0.1-0.2 mm. A pin from above would stand 0.3-0.5 mm into the wire path
   and tilt the conductor 6.5-12.8 deg [ctq calc off 2].""")

# ---------------------------------------------------------------------------
hdr("4. f4: how far the crimper opens so the head can leave along the wire")
box_h = 2.40        # contact end view height [mfr S1]
ins_h = 2.10        # a loose silicone insulation crimp's height, from section 5 [calc]
lance = 0.90        # lance below the floor [source S19-S22], rides out through a slotted relief
print(f"  tallest thing that must pass between crimper and anvil going toward the box: box {box_h} mm;")
print(f"  insulation crimp ~{ins_h} mm; lance {lance} mm below the floor, which would drag across the anvil")
print("  top unless the anvil drops (a lengthwise relief slot would leave the barrel floor unsupported).")
for gap, drop in ((2.6, 0.0), (5.0, 0.0), (5.0, 1.5)):
    print(f"  crimper opened {gap:.1f} mm, anvil dropped {drop:.1f} mm: clearance over the box {gap-box_h:+.1f} mm,"
          f" under the lance {drop-lance:+.1f} mm")
print("""-> The knee's 5 mm opening passes the box with 2.6 mm to spare, and a 1.5 mm anvil
   drop clears the lance by 0.6 mm. The exit is
   along the conductor toward the box (the C's spine stands ahead of the box, its
   throat toward the comb). Sideways is closed by neighbours at 5 mm, and dropping
   the head moves the crimper onto the crimp [ctq calc off 3]. A rear funnel would
   have to open: split funnel, or no funnel.""")

# ---------------------------------------------------------------------------
hdr("5. f6: the insulation crimp on 0.49 mm silicone")
A_bun = pi / 4 * D_BUN ** 2                          # gross bundle area incl. voids
A_sil = pi / 4 * (D_WIRE ** 2 - D_BUN ** 2)
print(f"wire {D_WIRE} mm OD, bundle {D_BUN} mm, wall {WALL:.2f} mm; bundle {A_bun:.3f} mm2, silicone {A_sil:.3f} mm2")
print("""Model [estimate]:
  - silicone is incompressible (Poisson ~0.49); what the barrel squeezes out of the
    section leaves axially as collars at the barrel's ends (fraction e);
  - enclosed inner area = bundle + (1-e) x silicone = phi x W_i x H_i, phi 0.85
    (between an ellipse 0.785 and a rectangle 1.0), W_i = W_o - 2t, H_o = H_i + 2t;
  - the bundle sits mid-height, so the silicone over it at the centre is s = (H_i - d)/2;
  - the curled wing tips of a B/F insulation crimp press p = 0.1-0.3 mm deeper than
    the roof's mean inner surface [estimate], leaving s_tip = s - p over the strands;
  - local compression under a tip c = 1 - s_tip / wall. Cut-through risk [estimate,
    blunt 0.2 mm edge on a 200-500 % elongation elastomer]: c <= 0.5 low,
    0.5-0.7 real, > 0.7 likely.
Contact end-view envelope 1.95 W x 2.4 H [mfr S1]; KONNRA clone spec at 22 AWG:
insulation crimp height 1.80 +/-0.10, width <= 2.05 [source via ribbon-as-pallet].""")
PHI = 0.85
rows = []
for W_o in (1.80, 1.90, 2.00, 2.05):
    W_i = W_o - 2 * T
    for e in (0.0, 0.1, 0.2, 0.3):
        A_enc = A_bun + (1 - e) * A_sil
        H_i = A_enc / (PHI * W_i)
        H_o = H_i + 2 * T
        s = (H_i - D_BUN) / 2
        c_lo = 1 - (s - 0.1) / WALL
        c_hi = 1 - (s - 0.3) / WALL
        fits = "fits" if (W_o <= 1.95 + 1e-9 and H_o <= 2.40) else ("W over" if W_o > 1.95 else "H over")
        rows.append((W_o, e, H_o, s, c_lo, c_hi, fits))
        print(f"  W {W_o:.2f}  e {e:.1f}: H {H_o:.2f} mm, silicone over bundle {s:.2f},"
              f" under tips {max(0,s-0.3):.2f}-{max(0,s-0.1):.2f}, local compression {c_lo:.2f}-{min(1,c_hi):.2f}  [{fits}]")
print("""-> Pressing this wire to KONNRA's 1.80 mm height (a PVC-wire number) needs 20-30 %
   of the jacket squeezed out of the barrel as collars and leaves 0.0-0.26 mm of
   silicone under the tips: local compression 0.47-1.0, cut-through likely.
   At 1.8-1.9 mm wide (inside the 1.95 mm envelope) and 2.0-2.3 mm tall (e 0-0.2)
   it leaves 0.08-0.49 mm under the tips (compression 0-0.8) and stays inside the
   2.4 mm height. Each 0.1 mm of insulation crimp height moves the silicone under
   the tips by ~0.05 mm. Widths of 2.0-2.05 exceed JST's 1.95 catalog envelope
   (KONNRA allows <= 2.05).
   The window for this wire is narrow and has a floor (cut) and a ceiling (cavity
   envelope), both set by position, not by force.""")

# grip
print("\nGrip of the insulation crimp on the conductor [estimate]:")
for E in (2.5, 5.5):                                # MPa, Shore 50A / 70A via Gent's relation [calc]
    for cm in (0.10, 0.30):                          # mean wall compression at the centre
        p = 2.8 * E * cm                             # MPa, thin-layer compression modulus ~2.8 E [estimate]
        for L in (0.8, 1.5):                         # insulation barrel length [estimate, clone drawings]
            lo = 0.3 * p * pi * D_BUN * L
            hi = 0.6 * p * pi * D_BUN * L
            f_sil = p * (1.6 * L)
            print(f"  E {E} MPa, compression {cm:.2f}, barrel {L} mm: pressure {p:4.1f} MPa,"
                  f" bundle slips in the jacket at {lo:4.1f}-{hi:4.1f} N; silicone pushes back {f_sil:4.1f} N")
print("""-> A few newtons (0.5-8 N): the strands slip inside the jacket long before the jacket
   slips in the barrel. On this wire the insulation crimp is not a pull-out grip in
   any useful sense (the conductor crimp's 39.2 N is); its jobs are to hold the
   jacket so bending happens behind the barrel, to keep the contact square in the
   cavity, and not to cut the jacket. Silicone pushes back 1-13 N against the
   30-130 N the insulation wings take to form: the jacket is invisible in the
   stroke's force, so its crimp must be set by position.""")

# Shore to E (Gent) for the record
for S in (50, 60, 70):
    E = 0.0981 * (56 + 7.62336 * S) / (0.137505 * (254 - 2.54 * S))
    print(f"  Gent's relation: Shore {S}A -> E ~ {E:.1f} MPa")

# ---------------------------------------------------------------------------
hdr("6. f6: what the insulation blade's own force curve can see")
k_sil = (1.3, 13.0)
print(f"  silicone squeeze: {k_sil[0]}-{k_sil[1]} N over the last 0.1-0.3 mm -> ~5-130 N/mm [section 5]")
tip_area = 2 * 0.20 * 1.2                           # two tip edges 0.2 x 1.2 mm
for sy in (250, 350):
    f_ind = tip_area * sy
    print(f"  tips on strands: {tip_area:.2f} mm2 of tip edge at {sy} MPa strand flow -> {f_ind:.0f} N"
          f" within ~0.05 mm -> ~{f_ind/0.05/1000:.1f} kN/mm")
print("""-> On its own drive and load cell, the insulation blade sees wing forming (a plateau
   of tens of newtons), a gentle silicone slope, and then a slope 20-500 x steeper
   the moment the tips reach copper. That is a cut-through sentinel. It fires after
   the fact (the jacket is already cut), so its job is to flag, and to tell the
   height sweep where the floor of the window is. Inside a single stepped crimper,
   the same event is buried under 0.8-2.4 kN of conductor compaction.""")

# ---------------------------------------------------------------------------
hdr("7. f6: bend-and-look, how wide a cut gapes on the outside of a bend")
for R in (1.0, 2.0, 3.0):
    eps = (D_WIRE / 2) / (R + D_WIRE / 2)
    for depth in (0.2, 0.49):
        gape = 2.5 * eps * depth                    # edge-crack opening ~2-3 x strain x depth [estimate]
        print(f"  bend over a pin of radius {R:.0f} mm: outer-surface strain {eps:.2f}; a {depth:.2f} mm deep cut gapes"
              f" ~{gape:.2f} mm = {gape*36:.0f} px at 36 px/mm [px/mm unconfirmed, sees-and-learns]")
print("""-> A through-cut at a wing tip opens 0.2-0.6 mm on a 60-90 deg bend over a pin of
   radius 1-3 mm (diameter 2-6 mm; final_w3.py §1 gives diameters) and shows bright tinned strands on black silicone: a camera sees it at any
   plausible scale. A shallow nick opens too, as a dark line under raking light.
   Continuity cannot see a cut at the insulation barrel: the wing tips touch the
   same conductor the contact is crimped to.""")

# ---------------------------------------------------------------------------
hdr("8. f7: die sources, tolerances against what a crimp die needs")
need = {"conductor channel width": 0.01, "anvil width (clearance in channel)": 0.02,
        "stop / shut height (adjustable)": 0.10, "holders, strippers, stop blocks": 0.15}
src = [("SendCutSend laser cut (1095, 4130, MagnaCut, mild)", 0.127, "[source: sendcutsend.com, +/-.005 in]"),
       ("JLCCNC wire EDM (stated)", 0.05, "[source: jlccnc.com via f&f wave 1]"),
       ("good wire-EDM shop", 0.005, "[estimate]"),
       ("precision ground flat stock, thickness", 0.013, "[assumption: +/-.0005 in typical]"),
       ("SN-2549 jaw set (as made)", 0.01, "[assumption: EDM-cut, unmeasured]")]
for feat, tol in need.items():
    ok = [n for n, t, _ in src if t <= tol + 1e-9]
    print(f"  {feat:36s} needs ~+/-{tol:.3f} mm: " + ("; ".join(ok) if ok else "none of the cheap routes"))
print("  Sources:")
for n, t, lab in src:
    print(f"    {n:52s} +/-{t:.3f} mm  {lab}")
for anvil, lab in ((1.5875, "1/16 in ground flat or parting blade"), (1.50, "1.5 mm gauge plate")):
    for clr in (0.04, 0.08):
        print(f"  anvil {anvil:.3f} mm ({lab}) + {clr:.2f} clearance -> channel {anvil+clr:.2f} mm,"
              f" crimp width ~{anvil+clr:.2f} (JST analog 1.50 [mfr S14]; KONNRA 1.75 +/-0.15)")
print("""-> Laser cutting is for holders, shoes, stop blocks and strippers. A crimper channel
   wants EDM from a good shop, or harvested steel. An anvil blade can be bought as
   ground stock stood on edge, because its width is the stock's ground thickness.""")

# ---------------------------------------------------------------------------
hdr("9. f5b: half-row cassette at 5.0 mm, rows and forces per unit")
per = (0.78, 1.68, 2.43)                            # kN per contact: low, central, high [f&f stroke_model]
rows_unit = {"T4 x5 (J3,J5,J9,J11,J13)": [2, 2] * 5, "J1 XHP-9": [5, 4], "J2 XHP-6 (cav 3 empty)": [2, 3],
             "J4 XHP-7": [4, 3], "J6 XHP-5": [3, 2], "J7 XHP-7": [4, 3]}
strokes = 0
crimps = 0
for k, v in rows_unit.items():
    strokes += len(v)
    crimps += sum(v)
    print(f"  {k:28s} half-rows {v}")
print(f"  -> {strokes} strokes per unit for {crimps} crimps")
for n in (1, 2, 3, 4, 5):
    print(f"  row of {n}: {n*per[0]:4.1f} / {n*per[1]:4.1f} / {n*per[2]:4.1f} kN (low / central / high);"
          f" 1 t arbor press ~8.9 kN: {'yes' if n*per[2] <= 8.9 else ('central only' if n*per[1] <= 8.9 else 'no')}")
share3 = sum(x for v in rows_unit.values() for x in v if x <= 3) / crimps
print(f"  share of crimps in rows of three or fewer: {share3*100:.0f} % (ctq calc off 4 says 68 %)")
for cr in (3.5, 4.4):
    print(f"  insulation crimper {cr} mm wide at 5.0 mm pitch: {5.0-cr:.1f} mm of steel between stations")

# ---------------------------------------------------------------------------
hdr("10. f3: chasing a measured crimp height in several hits")
print("""Physics: for monotonic loading in one direction, unloading is elastic and reloading
retraces elastically up to the previous peak before flow resumes on the same
hardening curve (isotropic hardening; the Bauschinger effect acts on reversed
loading, not here) [source: standard plasticity; assumption that friction states
reset little]. So several hits to a final depth form the crimp as one stroke to
that depth does, and each re-touch between hits reads the true unloaded height.""")
target = 0.80
sb = 0.030        # springback at the target depth, mm [estimate, metrology section 2]
sb_err = 0.008    # how well hit k predicts springback of hit k+1 [estimate]
depth = target - 0.10
for k in range(1, 5):
    h = depth + sb
    print(f"  hit {k}: dies to {depth:.3f} under load -> re-touch reads {h:.3f} (target {target:.3f})")
    if abs(h - target) <= 0.01:
        break
    depth = max(depth - 0.2, target - sb + (sb_err if k == 1 else 0.0))
print("""-> Two or three hits land inside +/-0.01 mm of a target read by the gauge, with no
   wedge or stop to set. The stop then only guards against over-travel. What it
   cannot fix: the target itself (reference crimp, copper-corrected), and hits that
   go too deep (a crimp cannot be un-crimped), so every approach comes from above.""")

# ---------------------------------------------------------------------------
hdr("11. f3 and f1: the proof pull borne on the box's rear face")
for area, lab in ((0.38, "top wall edge only (1.9 x 0.2)"), (0.78, "top wall plus upper side walls")):
    for F in (20.0, 39.2):
        print(f"  {F:4.1f} N on {area:.2f} mm2 ({lab}): {F/area:5.0f} MPa against ~500 MPa bronze yield")
print("""-> A blade lowered from above into the neck in front of the conductor crimp and
   bearing on the box's rear face carries the proof pull at 25-100 MPa: no mark.
   The same blade, insulated from the anvil and lowered before threading, is the
   wire stop and the touch sensor: strand tip on blade closes blade -> strands ->
   barrel -> contact -> anvil. The brush length is the blade's offset from the
   conductor barrel's front (hand-tool-as-press a1 uses the same blade, sensed
   through the far end).""")
