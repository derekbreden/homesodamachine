"""Wave-2 numbers for the hand-tool-as-press explorer.

Run: python3 wave2.py > wave2.out.txt

Every input carries its label. Contact geometry is from ../../../context/xh-facts.md
(clone drawings) and from into-the-housing's exchange calc
(../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt, cited "ith ex §n").
Nothing here is measured.
"""
import math


def hr(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


E_STEEL = 200e3  # MPa

# ---------------------------------------------------------------------------
hr("1. The neck: what fits between the box's rear face and the conductor barrel")
# ---------------------------------------------------------------------------
# Transition box-rear -> conductor-barrel front 0.2-0.5 mm [estimate, ith ex §1].
# Brush wanted: strands visible past the barrel's front edge, short of the box
# [mfr S5]; take 0.1-0.2 mm as the target brush [estimate].
print("room left for the brush = transition - blade stack (negative = the blade does not fit)")
stacks = [("0.30 steel (wave 1)", 0.30),
          ("0.20 steel", 0.20),
          ("0.15 steel", 0.15),
          ("0.10 steel + 0.025 polyimide", 0.125),
          ("0.10 steel + 0.05 polyimide", 0.15)]
trans = (0.2, 0.3, 0.4, 0.5)
print("  blade stack                        " + "".join(f"  t={t:.1f}" for t in trans))
for name, th in stacks:
    print(f"  {name:34s}" + "".join(f"{t - th:+7.2f}" for t in trans))
print("-> a brush of 0.1-0.2 mm plus a blade needs a transition of >= 0.25-0.35 mm even")
print("   with a 0.1 mm blade. A 0.2 mm transition leaves no room for any blade with a")
print("   brush: the contact is then located some other way (pilot pin, camera, box front).")

# ---------------------------------------------------------------------------
hr("2. Can the blade itself carry a proof pull?")
# ---------------------------------------------------------------------------
# Two tines, each w wide, cantilevered length L from the flap arm's clamp to the
# box shoulder. Load F shared by two tines. Spring steel working ~1,000-1,400 MPa.
print("unbacked tine bending stress at a 20 N pull (two tines share it)")
F = 20.0
for t in (0.10, 0.15, 0.20, 0.30):
    for w, L in ((1.5, 2.0), (1.5, 4.0), (2.5, 2.0), (2.5, 4.0)):
        s = 6 * (F / 2) * L / (w * t * t)
        tag = "ok" if s < 1000 else ("marginal" if s < 1400 else "yields")
        print(f"  t {t:.2f}  tine {w:.1f} wide, arm {L:.1f}  -> {s:7.0f} MPa  {tag}")
print("-> an unbacked thin blade cannot carry a proof pull. Either a rigid face backs it")
print("   (the die's front face, only at hold), or the pull is taken elsewhere: with the")
print("   dies re-closed on the crimp (a1b), or in a separate backed pull slot (a2, a6).")
# Box rear walls as the bearing face, relieved below the floor for the lance
wall = 0.20
perim = 2 * 2.2 + 1.95  # two sides + top above the floor [xh-facts §1, clone box 1.85-1.95 x 2.2-2.4]
A = wall * perim
for Fp in (20, 39.2):
    print(f"  box rear walls above the floor: {A:.2f} mm^2 -> {Fp:.1f} N gives {Fp / A:.0f} MPa "
          f"(phosphor bronze yields at ~400-600 MPa)")

# ---------------------------------------------------------------------------
hr("3. The side-entry jaw law: crimp orientation against how far the conductor stands out")
# ---------------------------------------------------------------------------
# A side-entry hand tool's nest axis is normal to its jaw plane. With the conductor
# along Y, the jaw plane is XZ. If the barrels are to open normal to the ribbon plane
# (insertion orientation), the jaws close normal to the ribbon plane and the jaw's long
# axis lies ALONG the row. Then conductor k must stand out of the ribbon plane by the
# depth of the jaw half that faces the ribbon (a), plus a clearance, or every neighbour
# must lie beyond the jaw tip (impossible for an interior conductor).
# If instead the jaw closes ACROSS the row (long axis normal to the plane), the lift is
# only the nest-to-tip distance, but every crimp is rolled 90 deg (ith ex §8).
print("stand-out h needed, and what it does to a split conductor of free length L")
print("(cantilever root radius L^2/(3h), tip pull-back 0.6 h^2/L [ith ex §6]; annealed strands yield")
print(" below ~67-78 mm radius [digest])")
cases = [("rolled 90 deg: nest-to-tip 3 mm + 1.5", 4.5),
         ("rolled 90 deg: nest-to-tip 6 mm + 1.5", 7.5),
         ("upright: jaw half a = 6 mm + 1.9", 7.9),
         ("upright: jaw half a = 9 mm + 1.9", 10.9),
         ("upright: jaw half a = 12 mm + 1.9", 13.9),
         ("C-frame arm (sec 4), low", 6.5),
         ("C-frame arm (sec 4), high", 9.5)]
for name, h in cases:
    row = []
    for L in (25, 35):
        R = L * L / (3 * h)
        pb = 0.6 * h * h / L
        row.append(f"L{L}: R {R:5.1f} mm, pull-back {pb:4.2f} mm")
    print(f"  {name:40s} h {h:5.1f} | " + " | ".join(row))
print("-> no side-entry hand tool gives both the insertion orientation and a small lift.")
print("   Upright crimps cost ~8-14 mm of stand-out (jaw half depth unmeasured), which sets")
print("   the copper; the fronts must be squared afterwards (front plate, late rear clamp).")

# ---------------------------------------------------------------------------
hr("4. C-frame one-nest die head (a4b): lower arm reaching over the row from the front")
# ---------------------------------------------------------------------------
# Neighbours' crimped boxes reach up to ~+1.35 mm above the conductor axis
# (floor at jacket bottom -0.85 - 0.2 stock, box 2.4 tall) [estimate, xh-facts §1].
# Arm bottom clears them by 0.3; anvil insert 1.0 mm on the arm; working conductor axis
# 1.05 above the contact floor.
sig = 1000.0  # MPa, hardened tool steel, static with margin [assumption]
print("arm thickness t = sqrt(6 F L / (b sigma)), sigma 1000 MPa; lift = 1.65 + t + 1.0 + 1.05")
for Fk in (1.5, 3.0):
    for L in (6, 8, 10, 13):
        for b in (6, 8):
            t = math.sqrt(6 * Fk * 1000 * L / (b * sig))
            lift = 1.65 + t + 1.0 + 1.05
            # tip deflection of the arm (matters only if the dies do not bottom)
            I = b * t ** 3 / 12
            d = Fk * 1000 * L ** 3 / (3 * E_STEEL * I)
            print(f"  {Fk:.1f} kN, arm {L:2d} mm long, {b} wide: t {t:4.2f} mm, lift {lift:4.1f} mm, "
                  f"arm deflection {d * 1000:4.0f} um")
print("-> ~6-9 mm of lift with the barrels upright, whatever the SN jaw's shape. The arm")
print("   length is set by the working contact's box (it sticks out ~2.5 mm ahead of the")
print("   barrels) and the neighbours' crimped noses on the same line.")

# ---------------------------------------------------------------------------
hr("5. The treadle (a6): a foot closes the hand tool through a cord")
# ---------------------------------------------------------------------------
# Grip force needed: <= ~220 N (hand max, wave-1 calc §1); the estimate band is
# 50-175 N. Cord pulls the grip centre along the closing direction. A 608 bearing
# as the turning pulley (~5 % loss each) [estimate].
print("foot force and foot travel for a heel-hinged treadle of ratio r (toe arm / cord arm)")
for Fg in (100, 175, 220):
    for r in (1.5, 2.0, 3.0):
        Ff = Fg / r / 0.95 / 0.95
        print(f"  grip {Fg:3d} N, r {r:.1f}: foot {Ff:5.0f} N")
print("  cord travel = grip travel: 51-56 mm with the tool's full opening [wave-1 calc §3];")
print("  ~25-35 mm with a printed opening limiter [estimate: the jaw needs ~5 mm of gap")
print("  (3.35-4.10 mm passage [ith ex §2] + ~1 mm lift before drawing back), and the")
print("  open-end gain is assumed 3-6]")
for travel in (30, 55):
    print(f"  cord travel {travel} mm -> foot travel {1.5 * travel:.0f} / {2 * travel:.0f} / {3 * travel:.0f} mm at r 1.5 / 2 / 3")
print("-> r = 2 with an opening limiter: <= ~120 N at the toe over ~60 mm. Presses per unit")
print("   ~106 (a half-press to hold and a full press to crimp, 53 crimps) [calc].")
print("   Seated ankle pedals are comfortable to tens of newtons for frequent use and leg-")
print("   driven pedals take several hundred [estimate]; this is occasional work.")
# Two-stage pedal: a light detent spring holds the first-click position
print("  two-stage treadle: stage 1 stop at the first ratchet tooth (half-press = hold),")
print("  stage 2 through a stronger spring (full press = crimp) [design, unmeasured tooth position]")

# ---------------------------------------------------------------------------
hr("6. Sensing a foot-closed crimp: load cell in the cord, angle sensor on the pulley")
# ---------------------------------------------------------------------------
r_pulley = 11.0  # mm, 608 bearing OD 22 used as the pulley [assumption]
counts = 4096    # AS5600 [source: wave-1 sourcing]
print(f"  AS5600 on a {2 * r_pulley:.0f} mm pulley: {2 * math.pi * r_pulley / counts * 1000:.1f} um of cord per count")
for gain in (15, 30):
    print(f"  through a gain of {gain}: {2 * math.pi * r_pulley / counts / gain * 1000:.2f} um of die per count, before compliance")
cap = 50 * 9.81
print(f"  S-type 50 kg cell: {cap:.0f} N capacity; HX711 at 10-80 SPS; a 3 s full press at 80 SPS")
print("  gives ~240 samples over the stroke and ~15-40 in compaction (last 1.5-8 mm of grip).")
print("-> the same force-against-travel curve a1 logs, with a foot as the motor.")

# ---------------------------------------------------------------------------
hr("7. The pull jig (a6): capstan and a readable spring")
# ---------------------------------------------------------------------------
print("capstan: hold force = pull x exp(-mu*theta)")
for mu in (0.3, 0.6):
    for turns in (1, 2, 3):
        th = 2 * math.pi * turns
        print(f"  mu {mu:.1f}, {turns} turn(s): 20 N needs {20 * math.exp(-mu * th):6.2f} N of hold at the tail")
print("spring-steel leaf as the gauge, cantilever L, width b, thickness t, load 20 N at the tip")
for (L, b, t) in ((40, 10, 0.8), (40, 10, 1.0), (30, 10, 1.0), (40, 12, 1.2)):
    I = b * t ** 3 / 12
    k = 3 * E_STEEL * I / L ** 3
    s = 6 * 20 * L / (b * t * t)
    print(f"  leaf {L}x{b}x{t}: k {k:5.2f} N/mm, 20 N -> {20 / k:5.2f} mm, stress {s:4.0f} MPa")
print("-> a 40 x 10 x 1.0 mm leaf reads 20 N as ~2.6 mm of tip travel at ~480 MPa; a printed")
print("   pointer or the camera reads it. A digital luggage scale on the hook does the same job.")

# ---------------------------------------------------------------------------
hr("8. A keyhole fit gauge (a6, a1b)")
# ---------------------------------------------------------------------------
# JST end-view envelope 1.95 x 2.4 [mfr S1]; the closed insulation barrel on 1.7 mm
# silicone is 2.26-2.46 mm tall for closed widths 1.95-1.80 (ith ex §9).
for w, h in ((1.95, 2.26), (1.90, 2.33), (1.80, 2.46)):
    ok = "passes a 1.95 x 2.4 opening" if (w <= 1.95 and h <= 2.40) else "stops at a 1.95 x 2.4 opening"
    print(f"  closed insulation barrel {w:.2f} wide x {h:.2f} tall: {ok}")
# Keyhole: the cavity section with a lance notch on the floor side and a side slot
# narrower than the wire, so the crimp passes nose first all the way and the wire
# leaves sideways; nothing is drawn back over the lance.
for slot in (1.3, 1.5):
    print(f"  side slot {slot:.1f} mm: the 1.7 mm silicone wire squeezes out sideways "
          f"({(1.7 - slot) / 1.7 * 100:.0f} % diametral squeeze) [estimate]; a 1.9-2.0 mm crimp cannot")
print("-> a stencil-steel keyhole (cavity section, lance notch, side slot) passes a good crimp")
print("   nose first and lets the wire out sideways. It stops flared wings, strands outside,")
print("   a spike of tab and a half-crimp. It says nothing about crimp height. The opening is")
print("   copied from a sliced kit housing measured under the ELP, not from the catalog.")

# ---------------------------------------------------------------------------
hr("9. Person time: the jig bench against today's hand procedure (all estimates)")
# ---------------------------------------------------------------------------
steps_today = [("pick a contact, place it by eye in the nest, one click", 12),
               ("feed the conductor, judge depth by eye, squeeze", 10),
               ("look at it", 3)]
steps_bench = [("drop a contact on the locator against its stop, flap down", 6),
               ("half-press the treadle (hold)", 2),
               ("bend the conductor out, feed to the light", 7),
               ("full press", 4),
               ("lift, draw back; proof pull in the jig", 12),
               ("through the fit gauge", 4)]
a = sum(t for _, t in steps_today)
b = sum(t for _, t in steps_bench)
print(f"  today   ~{a} s a crimp -> {a * 53 / 60:.0f} min for 53")
print(f"  bench   ~{b} s a crimp -> {b * 53 / 60:.0f} min for 53, pull and gauge included")
print(f"  bench without pull and gauge ~{b - 16} s -> {(b - 16) * 53 / 60:.0f} min")
print("-> the bench does not save minutes; it buys repeatable placement, a light for depth,")
print("   a pull and a gauge on every crimp, and (with the cord cell) a force log.")
