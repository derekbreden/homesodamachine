"""force-and-form, final pass: numbers behind the settled idea files.

Run: python3 final_w3.py > final_w3.out.txt

 1. Bend-and-look: pin DIAMETER against jacket strain and cut gape; which way the wire
    must bend; room needed below the barrel for a downward bend (f6).
 2. f9b (dock, tack, shear on strip): what the tab shear does to a tacked contact held
    under the tack comb; tab shear force.
 3. f9b / f3 / f1: the neck blade used only for the proof pull (dropped after the crimp),
    against the neck blade used as a depth stop; bearing on the box's rear face; how
    long a jacket grip must be for a 20 N pull to reach the copper.
 4. f1: the fork that holds neighbours out of the SN-2549's jaw plane leaves a set.
 5. f8: 0.7 mm crimper walls (2.9 mm crimper) beside a seated neighbour.
 6. f5b: both half-rows in one shoe at housing pitch (crimper plate with relief grooves).
 7. Target crimp height against the machine's own channel width; what a +/-0.05 mm
    channel costs, and how a measured height takes it back (f3, f7, f1b, f10).
 8. f2c: one output pallet at housing pitch instead of two at 5.0 mm.
 9. Latch retention against the proof pull.
10. Axial reference: touch-off on a neck blade against a camera-measured bare length.

Labels: [assumption] and [estimate] are unmeasured; sources are named where used.
Inputs from xh-facts.md unless stated.
"""

import math

D_WIRE = 1.7      # conductor OD, mm [xh-facts §7]
WALL = 0.49       # silicone wall, mm [xh-facts §7]
BUNDLE = 0.72     # strand bundle, mm [xh-facts §7]
T_STOCK = 0.20    # contact stock, mm [xh-facts §1, clone drawings]


def hdr(s):
    print("\n" + "=" * 86)
    print(s)
    print("=" * 86)


# ---------------------------------------------------------------------------
hdr("1. f6 bend-and-look: pin diameter, strain, gape, bend direction, room below")
print("Outer-surface strain of the jacket bent over a pin of diameter d: eps = r_w / (d/2 + r_w),")
print("r_w = 0.85 mm. A cut of depth a gapes ~2.5 x eps x a [estimate, edge-crack opening].")
for d in (1.0, 2.0, 3.0):
    eps = (D_WIRE / 2) / (d / 2 + D_WIRE / 2)
    gapes = [2.5 * eps * a for a in (0.2, WALL)]
    print(f"  pin diameter {d:.0f} mm (radius {d/2:.1f}): strain {eps:.2f}; a 0.20 mm cut gapes {gapes[0]:.2f} mm, "
          f"a through-cut (0.49) {gapes[1]:.2f} mm = {gapes[0]*36:.0f}-{gapes[1]*36:.0f} px at 36 px/mm [px/mm unconfirmed]")
print("  (calc/wave2.py §7 labels its pins by radius: its '1 / 2 / 3 mm pin' rows are radius 1 / 2 / 3,")
print("   i.e. diameters 2 / 4 / 6 mm. f6's 2 mm hardened dowel is a diameter: strain 0.46.)")
print("Which way: the wing tips of a B/F insulation crimp sit on TOP and press into the jacket's")
print("top [calc wave2 §5]. A cut there opens only on the outside of the bend, so the wire's tail")
print("must bend DOWN (away from the tips). Bending UP closes the cut while the camera looks.")
for ang in (60, 90):
    r_pin = 1.0
    # the wire's axis, wrapped over the pin, sweeps below its own straight line by at least
    sweep = (r_pin + D_WIRE / 2) * (1 - math.cos(math.radians(ang))) + D_WIRE / 2 * math.sin(math.radians(ang))
    print(f"  {ang} deg down over a 2 mm pin just behind the barrel: the wire sweeps >= {sweep:.1f} mm below its axis"
          f" within the first ~3 mm")
print("-> room below the barrel: ~3 mm, clear of any strip track, carrier or anvil. f3's strip")
print("   track lies there, so either a section of track drops after the tab cut, or the bend")
print("   happens at a separate bend nest (open below) the carriage visits after release.")

# ---------------------------------------------------------------------------
hdr("2. f9b: shearing the tabs of tacked contacts on the rail, under the tack comb")
print("Tab ~0.8-1.0 wide x 0.20 thick [xh-facts §1; calc X §5]. Phosphor bronze yield 450-600 MPa")
print("[assumption, C5191 spring temper range]. Shear strength ~0.6-0.8 x UTS 550-650 MPa.")
for b in (0.8, 1.0):
    for sy in (450, 600):
        Mp = sy * b * T_STOCK ** 2 / 4       # plastic moment, rectangular section
        for arm in (0.8, 1.5):               # insulation barrel length between rail edge and comb's contact
            print(f"  tab {b:.1f} wide, sy {sy}: plastic moment {Mp:.1f} N mm; comb reacts it over a {arm:.1f} mm"
                  f" barrel with {Mp/arm:4.1f} N")
for b in (0.8, 1.0):
    for tau in (330, 520):
        print(f"  tab {b:.1f} wide, tau {tau} MPa: shear {tau*b*T_STOCK:5.0f} N per tab")
print("-> The carrier going down behind the rail edge can only put the tab's plastic moment into")
print("   the contact, 2.4-6 N mm; the comb, standing at its stop on the loosely closed wings, holds")
print("   it with 2-8 N. The 50-160 N of shear goes rail edge -> tab -> shear punch, all steel; the")
print("   tack itself carries none of it. What is left: whether the comb's stop sits exactly on the")
print("   wings it just formed (it does if it never lifts between tack and shear).")

# ---------------------------------------------------------------------------
hdr("3. The neck blade for the proof pull only; the jacket grip a pull needs")
box_rear_to_lance_tip = (2.44 - 0.20 - 2.0, 2.44 + 0.20 - 2.0)
print(f"Lance tip {2.44}+/-0.20 mm behind the front; box 2.0 mm: tip {box_rear_to_lance_tip[0]:.2f}-"
      f"{box_rear_to_lance_tip[1]:.2f} mm behind the box's rear, under the transition [calc on_ith §1].")
for brush in (0.1, 0.3):
    t_pull = 0.05 + 0.30 + 0.05 + brush
    t_stop = 0.05 + 0.30 + 0.25 + brush
    print(f"  brush {brush:.1f}: blade dropped AFTER the crimp (brush known, no scatter gap): t >= {t_pull:.2f} mm;"
          f" blade in place while threading: t >= {t_stop:.2f} mm [calc FP §5]")
print("  clone-drawing length budget: t = 0.30-2.28 mm [calc on_ith §1d]")
area_upper = 2 * 0.2 * 1.3 + 1.5 * 0.2
for F in (20, 39.2):
    print(f"  blade bearing on the box's rear face above floor + 1.0 mm ({area_upper:.2f} mm2): {F:.1f} N ->"
          f" {F/area_upper:.0f} MPa (bronze yield ~450-600)")
print("Jacket grip for a pull that must reach the copper: strands slip inside a squeezed jacket at")
print("0.5-2.1 N per mm of grip at 10 % squeeze, 1.4-6.3 N/mm at 30 % [calc FP §4].")
for sq, lo, hi in (("10 %", 0.5, 2.1), ("30 %", 1.4, 6.3)):
    print(f"  {sq}: a 20 N pull needs {20/hi:4.1f}-{20/lo:4.1f} mm of jaw")
print("-> A 3-5 mm throat jaw reaches 20 N only at ~30 % squeeze and the stiffer silicone.")
print("   The ribbon pallet's web clamp (all conductors, 10-20 mm long) is the surer reaction:")
print("   pull by moving the pallet, the neck blade holding the box.")

# ---------------------------------------------------------------------------
hdr("4. f1: the fork holds neighbours clear of the SN-2549's jaw plate")
print("Neighbour tips must stand h above conductor i's tip (barrels 3-4 mm into the nest plus")
print("clearance: h 4-6 mm [estimate]). All conductors have the same length L from the web.")
print("A neighbour bent aside by angle a at the fork line shortens its reach by L(1 - cos a).")
for L in (20, 30, 40, 50):
    angs = [math.degrees(math.acos(1 - h / L)) for h in (4, 6)]
    print(f"  split {L} mm: {angs[0]:.0f}-{angs[1]:.0f} deg")
print("Elastic alternative: bend the whole neighbour in one arc of radius >= 67 mm (copper's")
print("set radius [ribbon-as-pallet pg §4]); it shortens by only L^3/(24 R^2):")
for L in (20, 30, 40):
    print(f"  split {L} mm: {L**3/(24*67**2):.2f} mm, against 4-6 mm needed")
print("-> The neighbours take a set at the fork line in any version of f1. What can be chosen is")
print("   its direction: every non-working conductor bent the same way (one side, out of the")
print("   ribbon plane), so the row carries one uniform set for the insertion comb to take out.")

# ---------------------------------------------------------------------------
hdr("5. f8: 0.7 mm walls, a 2.9 mm crimper beside a seated neighbour")
W_ch, L_b, h_load = 1.5, 1.4, 0.7
for tw in (0.7, 0.8):
    width = W_ch + 2 * tw
    for od in (1.6, 1.7, 1.8):
        free = 2 * (2.5 - od / 2)
        a_side = (free - width) / 2
        for opening in (1.95, 2.10):
            play = (opening - od) / 2
            print(f"  walls {tw:.1f} -> crimper {width:.1f}; wire OD {od:.1f}: {a_side:+.2f} a side at the"
                  f" equator; play in a {opening:.2f} opening {play:.2f} -> net {a_side - play:+.2f}")
for F in (1680, 2430):
    p = F / (W_ch * L_b)
    for k in (0.3, 0.5):
        M = k * p * h_load * L_b * h_load / 2
        s = M / (L_b * 0.7 ** 2 / 6)
        print(f"  F {F} N, k {k}: 0.7 mm wall root stress {s:5.0f} MPa before the shoulders brace its lower end")
print("-> 0.7 mm walls give back 0.10 mm a side (net 0.00 to +0.08 against a seated neighbour's")
print("   play); stress 720-1,740 MPa at k 0.3-0.5 unbraced, less once the walls land on the")
print("   shoulders. The floating nest is then the only place the +/-0.14 mm RSS X offset can go.")

# ---------------------------------------------------------------------------
hdr("6. f5b branch: both half-rows in one shoe at 2.5 mm, the crimper plate grooved over the other plane")
P = 5.0
for label, ch, relief in (("conductor step", 1.50, 1.70), ("insulation step", 1.85, 2.00)):
    wall = (P - ch - relief) / 2
    print(f"  {label}: channel {ch:.2f} + relief over the crimped plane {relief:.2f} -> walls {wall:.2f} mm")
for mouth in (2.56, 2.8, 3.1):
    wall = (P - mouth - 2.0) / 2
    print(f"  insulation flare mouth {mouth:.2f} (open wings {mouth-0.1:.2f} + 0.1) beside a 2.0 relief:"
          f" wall at the plate's bottom edge {wall:+.2f} mm")
for open_w in (2.46, 2.7, 3.0):
    for crimped in (1.8, 2.05):
        gap = 2.5 - open_w / 2 - crimped / 2
        print(f"  open plane-B wings {open_w:.2f} beside a crimped plane-A insulation barrel {crimped:.2f} at 2.5 mm:"
              f" {gap:+.2f} mm")
print("-> The conductor step keeps 0.9 mm walls (the rule asks 0.7-0.85). The insulation step")
print("   works at 0.57 mm (30-130 N). What fails is the flare that must catch OPEN plane-B wings")
print("   beside CRIMPED plane A: at clone wing widths of 2.7-3.0 mm the plate's bottom edge keeps")
print("   0.10 mm down to nothing, and 3.0 mm wings touch a 2.05 mm crimp. With 2.46 mm wings")
print("   it holds (0.22 mm edge). A tack on plane B first (change-the-question c1c) removes it.")

# ---------------------------------------------------------------------------
hdr("7. Target crimp height against the machine's own channel width")
print("Compaction scales with W x H. References: JST SXA analog 1.50 x 0.80 = 1.20 mm2 [mfr S14];")
print("context estimate 1.50 x 0.88 = 1.32; KONNRA clone 1.75 x 0.73 = 1.28 [ribbon-as-pallet w3 §7].")
for W in (1.45, 1.50, 1.54, 1.58, 1.63, 1.67, 1.75):
    print(f"  channel {W:.2f}: target H {1.20/W:.2f}-{1.32/W:.2f} mm")
print("  a +/-0.05 mm channel error on 1.5 mm changes compaction by +/-3.3 % at a fixed height;")
print(f"  at H 0.80 the height that restores W x H moves by -/+{0.80*0.05/1.5:.3f} mm")
print("-> The copper correction from the JST reference lead (change-the-question c2) must be done")
print("   at the machine's measured channel width. A channel cut to +/-0.05 mm and measured with")
print("   pin gauges is usable when height is set per die (wedge, stop or chased hits). What")
print("   no tolerance here covers is the roof's form: arches and cusp.")

# ---------------------------------------------------------------------------
hdr("8. f2c: one output pallet at housing pitch, filled in cavity order")
for ins_w in (1.8, 1.9, 2.05):
    print(f"  crimped insulation barrels {ins_w:.2f} wide at 2.5 mm: {2.5-ins_w:.2f} mm between them")
for pocket in (2.05, 2.10):
    print(f"  box pockets {pocket:.2f} wide at 2.5 mm: steel ribs {2.5-pocket:.2f} mm; box 1.85-1.95 -> play"
          f" {pocket-1.95:.2f}-{pocket-1.85:.2f}")
print("-> Crimped contacts fit side by side at housing pitch, so a single-conductor station can")
print("   fill one 2.5 mm pallet in cavity order and one push (or one housing move) inserts the")
print("   whole end with zero stored feed. The pallet must ride with the web (on the carriage):")
print("   a bench-fixed pallet tethers the carriage to every contact already placed.")

# ---------------------------------------------------------------------------
hdr("9. Latch retention against the proof pull")
print("  latched contact holds: Molex analog 14.7 N [calc on_ith §7]; KONNRA XH clone spec >= 19.6 N")
print("  [source via ribbon-as-pallet a6]; JST pull-out minimum 39.2 N [mfr S6]; UL 486A 35.6 N")
print("-> A ~20 N proof pull after latching sits at the clone's minimum retention: the pull must come")
print("   before insertion, against the box's rear face. After latching, only a light tug (<= 5 N).")

# ---------------------------------------------------------------------------
hdr("10. Axial reference: touch-off on a blade against a camera-measured bare length")
scatter = 0.20   # strip-length scatter, +/- mm [procedure-is-the-machine calc wave2 §3]
cam = 0.03       # silhouette edge error [estimate]
print(f"  touch-off: brush exact; insulation edge scatters with the strip, +/-{scatter:.2f} mm")
print(f"  camera bare length, edge set mid-window: insulation edge +/-{math.hypot(cam, 0.02):.2f}, brush"
      f" +/-{math.hypot(scatter, cam):.2f}")
print(f"  camera, error split between brush and window: each +/-{math.hypot(scatter/2, cam):.2f}")
print("  window between the barrels ~0.4-0.6 mm long, 'approximately 50/50' [mfr S5]; brush 0.1-0.3")
print("-> The camera turns one +/-0.2 mm error into two +/-0.1 mm ones, each inside its window. The")
print("   neck blade stays out of the tips' way and does the proof pull after the crimp.")
