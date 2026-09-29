"""Wave-2 exchange: machine-that-sees-and-learns reading terminal-supply's arrangements.

Numbers for exchange/machine-that-sees-and-learns--on--terminal-supply.md:
what a camera can and cannot see past a carrier strip, where a taught conductor position goes
wrong, and the handful of mechanical loads that decide whether a supply idea keeps its datum.

Explorer: machine-that-sees-and-learns. Run: python3 on_terminal_supply.py > on_terminal_supply.out.txt
Inputs are labelled where they are used. Contact dimensions are the clone drawings in
context/xh-facts.md s1; carrier pitch 7.1 mm is the Wurth analog terminal-supply found.
"""
import math

E_PB = 110e3      # MPa, phosphor bronze C5191 [estimate, handbook value]
G_PB = 41e3       # MPa, E / (2 (1 + 0.33)) [estimate]
SY_PB = 500.0     # MPa tensile yield, C5191 half-hard [estimate; terminal-supply used 550]
TAU_Y = SY_PB / math.sqrt(3)
T = 0.20          # mm stock [xh-facts s1, clone drawings]
PITCH = 7.1       # mm carrier pitch [terminal-supply, Wurth analog]
PXMM = {"ELP stock @100 mm": 45, "ELP + 20 D @50 mm": 86, "M12 12 mm @100 mm": 122}  # [vision_budget s1]


def hdr(s):
    print()
    print("=" * 84)
    print(s)
    print("=" * 84)


# ---------------------------------------------------------------------------------------
hdr("1. Seeing a strip-fed contact in silhouette, across the strip, before the stroke")
# The across-the-nest silhouette (v1 camera 2) looks along the strip (X). Upstream, the next
# fresh contact stands one pitch away with wings of the same height. Downstream is empty carrier.
w_cb = (1.68, 1.90)      # open conductor barrel width [xh-facts s1]
w_ib = (2.46, 3.00)      # open insulation barrel width [xh-facts s1]
for name, (lo, hi) in (("conductor barrel", w_cb), ("insulation barrel", w_ib)):
    print(f"  gap to the upstream neighbour at the {name}: {PITCH-hi:.2f}-{PITCH-lo:.2f} mm "
          f"(pitch {PITCH} minus open width {lo}-{hi})")
print()
print("  A grazing view from upstream, tilted down by theta, passes over the upstream neighbour.")
print("  The silhouette's top edge is the ray that grazes OUR FAR wing tip; that ray meets the")
print("  neighbour's nearer wing one full pitch later, so it clears it (excess height dh within one")
print("  strip, 0.02 mm to spare) when")
print("      tan(theta) >= (dh + 0.02) / pitch")
print("  Our near wing tip sits w*tan(theta) below that edge, so a 0.08 mm strand lying on the near")
print("  tip sticks up by only  0.08 - w*tan(theta)")
w = 1.90
for dh in (0.0, 0.05, 0.10, 0.15, 0.25):
    th = math.degrees(math.atan((dh + 0.02) / PITCH))
    bump = 0.08 - w * math.tan(math.radians(th))
    px = "  ".join(f"{bump*v:4.1f} px @{v}" for v in PXMM.values())
    print(f"    neighbour {dh:.2f} mm taller -> theta >= {th:4.2f} deg; strand bump {bump*1000:4.0f} um = {px}")
print("  -> with neighbours within ~0.15 mm of our wing height the grazing view works, and a strand on")
print("     the near wing tip shows as a 2-7 px bump. Much above that the neighbour forces a tilt that")
print("     hides a strand (a bent-up neighbour wing does exactly that).")
print("     A white vane slid into the 4.1-5.4 mm gap from the box side, lit from above, puts the")
print("     backlight between the two contacts and removes the squeeze.")
print("  Downstream the carrier is empty, so the camera can also sit downstream at theta ~0 if the")
print("  backlight is that vane (the light cannot come from beyond the upstream neighbour).")

# ---------------------------------------------------------------------------------------
hdr("2. The ribbon's other conductors against fresh contacts waiting on the strip")
# Conductors at fan pitch f land at x = j*f from the station (j = 1..n-1 on one side).
# A conductor (1.7 OD) collides with a fresh contact at m*PITCH if it lands within
# half the insulation-wing width (3.0/2) + half the OD (0.85) of it.
clear = 3.0 / 2 + 1.7 / 2
print(f"  collision if |j*f - m*{PITCH}| < {clear:.2f} mm (open insulation wings 3.0, conductor 1.7)")
for n in (3, 4, 5):
    free = []
    f = 1.7
    while f <= 15.0 + 1e-9:
        ok = all(min(abs(j * f - m * PITCH) for m in range(1, 12)) >= clear for j in range(1, n))
        free.append((round(f, 1), ok))
        f += 0.1
    ranges, start = [], None
    for fv, ok in free:
        if ok and start is None:
            start = fv
        if not ok and start is not None:
            ranges.append((start, round(fv - 0.1, 1)))
            start = None
    if start is not None:
        ranges.append((start, free[-1][0]))
    txt = ", ".join(f"{a}-{b}" for a, b in ranges) if ranges else "none"
    print(f"  {n}P, all {n-1} others on the upstream side: collision-free fan pitch (1.7-15 mm): {txt}")
for f in (1.7, 2.5, 3.5, 5.5):
    hits = [j for j in range(1, 5) if min(abs(j * f - m * PITCH) for m in range(1, 12)) < clear]
    print(f"    fan pitch {f}: upstream conductors j = {hits} sit on a fresh contact")
print("  -> a flat fan cannot keep 4P/5P conductors off the fresh contacts; only the conductors on")
print("     the empty-carrier (downstream) side are free. The rest must be lifted out of plane, or")
print("     crimping must run so that every waiting conductor is downstream (then each crimped one")
print("     is upstream and must stay lifted). Either way it is a per-conductor lift, and a look at")
print("     'no other tip below the fresh wing tips' belongs in the gate.")

# ---------------------------------------------------------------------------------------
hdr("3. Axial shortfall that a fan puts into each conductor (why one taught Y is not enough)")
# A conductor bent out by theta, run s along the angle, then bent back parallel, loses
# s(1-cos theta) of reach; with lateral move d = s sin theta that is d*tan(theta/2).
cases = [("5P into XH 2.5 mm pitch, outer", 1.6),
         ("J1 5P+4P into XHP-9, outermost", 3.2),
         ("5P fanned to 5.5 mm (v1 fan-comb), outer", 2 * (5.5 - 1.7)),
         ("5P to 7.1 mm strip pitch (a2b comb), outer", 2 * (7.1 - 1.7))]
for name, d in cases:
    row = "  ".join(f"{a:2d} deg: {d*math.tan(math.radians(a/2)):4.2f}" for a in (10, 20, 30))
    print(f"  {name:44s} d = {d:4.1f} mm -> shortfall  {row} mm")
print("  Compare: insulation edge must land in the window, ~0.5-1.0 mm long (+/-0.25 to +/-0.5 mm)")
print("  [vision_budget s4]; strip length itself is 2.4 (JST) or 1.6-2.1 (clone spec) and silicone")
print("  tears. If the ribbon end is cut square before it is fanned, the outer conductors' insulation")
print("  edges stand 0.3-1.9 mm behind the centre one. A per-slot taught Y absorbs the repeatable")
print("  part; the insulation edge as seen, per conductor, absorbs the rest. Cutting and stripping")
print("  after fanning, against one datum line on the pallet, removes most of it at the source.")

# ---------------------------------------------------------------------------------------
hdr("4. a2b: a proof pull reacted through the carrier tag")
# The wire's load enters the contact through the crimp, e above the tab's mid-plane.
for neck in (0.6, 0.8, 1.0):
    mp = neck * T ** 2 / 4 * SY_PB          # plastic moment of the neck, N*mm
    row = "  ".join(f"e={e:.2f}: {mp/e:4.1f} N" for e in (0.35, 0.55, 0.85, 1.20))
    print(f"  neck {neck} mm, Mp {mp:.1f} N*mm -> tab yields at a pull of  {row}")
print("  e: 0.35 mm is the conductor axis after a ~0.88 mm crimp less half the stock; 0.85 the")
print("  insulated wire's axis; 1.2 adds the 30 deg lift a2b uses to clear the pad.")
print("  -> any proof pull above ~2-16 N bends the tab; a 20 N pull always does. The tab carries")
print("     66-110 N only if the load lies in its own plane, and a pull on the wire never does.")
print()
print("  The tag hole as the datum for the box tip (5.0-6.5 mm ahead of the hole):")
for deg in (1, 2, 3, 5):
    lo, hi = (L * math.tan(math.radians(deg)) for L in (5.0, 6.5))
    print(f"    {deg} deg of bend-up/down or neck set -> box tip off by {lo:.2f}-{hi:.2f} mm "
          f"(cavity entry window ~+/-0.2 mm [vision_budget/arm_and_feeder s1])")

# ---------------------------------------------------------------------------------------
hdr("5. a2c: bending the strip +/-90 deg about the tab twists the carrier")
for L in (7.1, 14.2, 30.0, 50.0, 100.0):
    gamma = (math.pi / 2) * T / L           # surface shear strain of a thin strip twisted 90 deg
    tau = G_PB * gamma
    print(f"  90 deg twist spread over {L:5.1f} mm of carrier: shear strain {gamma:.4f}, "
          f"stress {tau:6.0f} MPa (shear yield ~{TAU_Y:.0f})")
print("  -> the next contact is one pitch (7.1 mm) upstream: a +/-90 deg swing of the strip yields")
print("     the carrier there and rolls that contact. Only a carrier already cut free can swing.")

# ---------------------------------------------------------------------------------------
hdr("6. a2: dropping the carrier 0.3-0.5 mm between two pinned neighbours")
# Drop plate ~5 mm wide at the station; carrier held by pins at +/-7.1 mm: an S-bend of span
# L = 7.1 - 2.5 on each side, guided at both ends. Gross section 3.0 x 0.2; the slot between
# holes may halve the width [assumption].
b = 3.0
I = b * T ** 3 / 12
Z = b * T ** 2 / 6
L = PITCH - 2.5
d_y = (SY_PB * Z) * 2 / L * L ** 3 / (12 * E_PB * I)   # deflection at first yield = sy L^2 / (3 E t)
print(f"  S-bend span {L:.1f} mm each side; first yield at {d_y:.2f} mm of drop, whatever the carrier's")
print("  width (the slots only decide where the hinge forms)")
for drop in (0.3, 0.4, 0.5):
    set_ = max(0.0, drop - d_y)
    roll = math.degrees(set_ / L)
    print(f"    a {drop} mm drop leaves ~{set_:.2f} mm of set, a kink of ~{roll:.1f} deg at the next pilot hole")
print("  -> the next contact can arrive rolled by ~1.5-4 deg. Inside the 5-11 deg roll window")
print("     [digest], but it eats half of it; the waiting-contact picture measures roll directly.")
print("     Dropping only the downstream (scrap) side keeps the upstream carrier flat.")

# ---------------------------------------------------------------------------------------
hdr("7. What a vacuum nozzle can push")
for kpa in (50, 80):
    for d in (0.5, 0.8, 1.0):
        area = math.pi * (d / 2) ** 2
        n = kpa * 1e-3 * area            # N (kPa * mm^2 = mN)
        print(f"  {kpa} kPa, nozzle bore {d} mm: holds {n*1000:5.1f} mN normal, ~{0.3*n*1000:4.1f} mN sideways (mu 0.3)")
print("  contact weight 0.42 mN [xh-facts s1, 0.043 g]; post grip 200-2000 mN [terminal-supply calc s7]")
print("  -> a nozzle can place a contact into an open nest; it cannot push one onto a post or into a")
print("     cavity against any friction. A post must come to a contact that is backed by a stop.")

# ---------------------------------------------------------------------------------------
hdr("8. a5: a bare contact staged 1.0-2.0 mm into the cavity mouth can pivot")
for c in (0.03, 0.05, 0.10):
    for eng in (1.0, 1.5, 2.0):
        tilt = math.degrees(math.atan(2 * c / eng))
        # conductor barrel centre ~0.7 mm behind the face at 2.0 mm staging, ~2.5 at 1.0 [terminal-supply s8]
        cb = {1.0: 2.3, 1.5: 1.8, 2.0: 1.3}[eng]
        print(f"  clearance {c:.2f}/side, {eng} mm engaged: +/-{tilt:4.1f} deg; conductor barrel centre "
              f"{cb} mm out moves +/-{cb*math.tan(math.radians(tilt)):.2f} mm")
print("  -> at 1.5 mm engagement the barrel can sit 0.07-0.25 mm off the anvil unless something")
print("     pushes it down; an anvil rising to a fixed height then bends the transition instead.")

# ---------------------------------------------------------------------------------------
hdr("9. Measuring each waiting contact's axial position instead of re-teaching per reel")
for name, v in PXMM.items():
    print(f"  {name:18s}: +/-0.1 mm bellmouth window = +/-{0.1*v:4.1f} px; edge fit 0.05-0.3 px "
          f"= {0.05/v*1000:.1f}-{0.3/v*1000:.1f} um")
print("  -> each contact's barrel edge against the anvil's fiducial is read to a few um; a fence on a")
print("     small stepper can move the strip in Y by the error every cycle.")

# ---------------------------------------------------------------------------------------
hdr("10. a4: what continuity through the post can tell")
rho = 0.0172e-6 * 1.02   # ohm*m, tinned copper [estimate]
A = 0.302e-6             # m^2 copper [xh-facts s7]
r_m = rho / A
print(f"  22 AWG ribbon conductor: {r_m*1000:.0f} mohm per metre")
for L in (0.1, 0.6, 15.2):
    print(f"    {L:5.1f} m -> {r_m*L*1000:7.1f} mohm")
print("  a crimp itself: ~0.2-1 mohm; post-to-box contact on a 0.2-2 N grip: ~5-30 mohm and variable")
print("  [estimates]. -> the path reads 'joined' or 'open'; it cannot grade the crimp. It also needs")
print("  the far end bared (a pogo pin on the cut face, or the spool's slip ring).")

# ---------------------------------------------------------------------------------------
hdr("11. a3: the U's direction read in silhouette from below the slot")
notch = (2.75 - 2.35, 3.20 - 2.20)     # insulation wing height minus box height [xh-facts s1]
for name, v in PXMM.items():
    print(f"  {name:18s}: notch between wing tips, {notch[0]:.2f}-{notch[1]:.2f} mm deep = "
          f"{notch[0]*v:4.0f}-{notch[1]*v:4.0f} px")
print("  Backlit from below, the hanging contact's outline is the box's rectangle inside the")
print("  insulation U; light passes between the wing tips on the open side only.")

# ---------------------------------------------------------------------------------------
hdr("12. a2b: how far the box tip moves on the tab neck under a small side load")
neck_b, neck_L = 0.8, 1.0                       # mm, neck width and length [terminal-supply, clone drawings]
I_n = neck_b * T ** 3 / 12
k_rot = E_PB * I_n / neck_L                     # N*mm/rad, elastic rotation stiffness of the neck
M_el = SY_PB * neck_b * T ** 2 / 6              # N*mm, first yield
print(f"  neck {neck_b} x {T} x {neck_L} mm: rotation stiffness ~{k_rot:.0f} N*mm/rad; first yield at {M_el:.1f} N*mm")
for F in (0.05, 0.1, 0.2, 0.5):
    lo, hi = (F * L * L / k_rot for L in (5.0, 6.5))
    y = "  (neck yields)" if F * 5.0 > M_el else ""
    print(f"    side load {F:4.2f} N at the box (5.0-6.5 mm out): tip moves {lo:.3f}-{hi:.3f} mm{y}")
print("  -> a conductor's drape (~0.05-0.1 N) moves the box tip 0.02-0.07 mm; a firmer tug moves it")
print("     by the whole cavity window. An offset measured at inspection holds only if the load is the")
print("     same at insertion; a look at the box tip just before the mouth does not depend on that.")
