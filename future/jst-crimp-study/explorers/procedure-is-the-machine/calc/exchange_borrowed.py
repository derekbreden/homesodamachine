"""Wave 2 exchange: procedure-is-the-machine on borrowed-machines.

Run:  python3 exchange_borrowed.py > exchange_borrowed.out.txt

Numbers behind ../../../exchange/procedure-is-the-machine--on--borrowed-machines.md.
Inputs from xh-facts, the digest and the borrowed-machines calcs are labelled where
they are used; every other geometric or timing input is an [estimate] and is printed
beside its result so the conclusion can be re-run when a measurement arrives.
"""
from math import sqrt, pi, cos, sin, radians, degrees, atan, exp, log

OD = 1.7            # conductor OD, mm [facts]
R = OD / 2
RIB = 1.7           # ribbon pitch [facts]
XH = 2.5            # housing pitch [facts]
BUNDLE = 0.72       # strand bundle [facts calc]
WALL = (OD - BUNDLE) / 2


def hr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


# --------------------------------------------------------------------------- 1
hr("1. Free space around a carrier-fed anvil (side-feed strip still attached)")
print("Side-feed carrier joins at the rear of the insulation barrel, in the contact's floor plane,")
print("pilot holes on each contact's centreline under the wire's path [digest]. So every conductor")
print("lying in the row at the target's X crosses the carrier strip, and below the floor plane is")
print("strip, track and shear there: no neighbour can DROP under the anvil level. Above is the punch.")
print("Upstream (feed-in side) the next contacts stand on the carrier with open wings; downstream the")
print("carrier is empty. Status of neighbour n (n<0 upstream) left in the row at spacing s:")
WING_HALF = 1.5     # clone open insulation wings 2.46-3.0 wide [facts] -> half ~1.5
for pc in (7.1, 9.5):                     # carrier pitch: 7.1 Wurth analog [digest]; 9.5 upper scaled [facts est]
    for hp in (3.0, 6.0):                 # punch/holder half-width at anvil level [borrowed est]
        print(f"\n  carrier pitch {pc} mm, punch half-width {hp} mm")
        print("   spacing  " + "  ".join(f"n={n:+d}" .rjust(9) for n in (-3, -2, -1, 1, 2, 3)))
        for s in (1.7, 2.5, 3.6, 4.35, 5.35):
            cells = []
            for n in (-3, -2, -1, 1, 2, 3):
                y = n * s
                if abs(y) - R < hp:
                    st = "PUNCH"
                elif n < 0 and any(abs(abs(y) - m * pc) < WING_HALF + R for m in (1, 2, 3)):
                    st = "WAITING"
                else:
                    st = "clear"
                cells.append(st.rjust(9))
            print(f"   {s:5.2f}    " + "  ".join(cells))
print("\n-> PUNCH: crushed unless moved out of plane (only up/back are open, and up is the punch).")
print("   WAITING: lies on the next contact's open wings on the strip.")
print("   With the strip attached, the free places are behind the tooling (fold-back, b1) and on")
print("   the downstream side beyond the punch. A fan (b3) works because b3 cuts the contact free")
print("   first; p1/p5's slotted presser (drop neighbours ~7 mm) does not work over an attached strip.")

# --------------------------------------------------------------------------- 2
hr("2. b1/b1b: when can the crimped conductor leave the anvil before the pre-feed feeds?")


def s_crank(phi_deg, r, l):
    p = radians(phi_deg)
    return r * (1 - cos(p)) + l - sqrt(l * l - (r * sin(p)) ** 2)


def phi_at(s_target, r, l):
    lo, hi = 0.0, 180.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if s_crank(mid, r, l) < s_target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


r_c, l_c = 15.0, 100.0   # b1b crank, 30 mm stroke [borrowed]
print("crank 15 mm, rod 100 mm (30 mm stroke); angle measured from BDC on the upstroke")
for s_clear in (4.0, 6.0):       # punch + hold-down above the box top + clearance [estimate]
    for s_feed in (15.0, 20.0):  # height at which the feed finger starts to move [assumption]
        a1, a2 = phi_at(s_clear, r_c, l_c), phi_at(s_feed, r_c, l_c)
        slow = (a2 - a1) / 360 * 10.0
        fast = (a2 - a1) / 360 * 0.5
        print(f"  clear at {s_clear:.0f} mm ({a1:5.1f} deg), feed from {s_feed:.0f} mm ({a2:5.1f} deg): window "
              f"{a2 - a1:5.1f} deg = {slow:4.2f} s at 10 s/rev (and the stepper can simply stop there); "
              f"{fast*1000:4.0f} ms at a 0.5 s press cycle")
withdraw = 0.15 + 0.15 + 7.0 / 25.0
print(f"  withdrawal on b1's shuttle: foot up 0.15 s + fork open 0.15 s + 7 mm X at 25 mm/s = {withdraw:.2f} s [estimate]")
print("-> a relay-fired bought press feeds the next contact while fork, foot and crimped contact are")
print("   still on the axis; a stoppable crank (b1b) can dwell in the window for as long as it likes.")

# --------------------------------------------------------------------------- 3
hr("3. Over-travel: a crank or eccentric near BDC is a displacement source (b1b and p5)")


def dsdphi(phi_deg, r, l, d=1e-4):
    return (s_crank(phi_deg + d, r, l) - s_crank(phi_deg - d, r, l)) / (2 * radians(d))


def overtravel(r, l, T_avail, k, delta, P0=None, ks=None):
    """Obstruction of height delta above normal BDC, loop stiffness k (N/mm).
    Optional disc-spring stack in the rod: preload P0 (N), rate ks (N/mm), in series."""
    keff = k * ks / (k + ks) if ks else None
    phi0 = phi_at(delta, r, l)
    n = 4000
    for i in range(n + 1):
        phi = phi0 * (1 - i / n)
        s = s_crank(phi, r, l)
        x = max(0.0, delta - s)
        F = k * x
        if P0 is not None and F > P0:
            F = P0 + keff * (x - P0 / k)
        T = F * dsdphi(max(phi, 1e-6), r, l) / 1000.0   # N*m
        if T > T_avail:
            return ("stalls", F, s)
    return ("passes BDC", F, 0.0)


drives = [("b1b crank r=15 l=100, NEMA23+10:1", 15.0, 100.0, 10.8),
          ("p5 eccentric e=2.5 l=40, NEMA17+30:1 worm", 2.5, 40.0, 3.1),
          ("p5 eccentric e=2.5 l=40, NEMA23+30:1 worm", 2.5, 40.0, 12.6)]
for name, r, l, T in drives:
    print(f"\n  {name}, {T} N*m at the shaft")
    for k in (20e3, 40e3, 100e3):
        row = []
        for delta in (0.1, 0.2, 0.4):
            st, F, s = overtravel(r, l, T, k, delta)
            st2, F2, s2 = overtravel(r, l, T, k, delta, P0=4000.0, ks=4000.0)
            row.append(f"d={delta}: {F/1000:5.1f} kN {st[:6]} | stack {F2/1000:4.1f} kN")
        print(f"    loop {k/1000:4.0f} kN/mm  " + "   ".join(row))
print("\n  obstruction d = extra height above normal BDC, e.g. a doubled contact (+2 x 0.2 mm stock),")
print("  a folded conductor or a foreign part; force shown is the obstruction's alone (add ~3 kN crimp).")
print("  'stack' = preloaded disc springs in the rod, 4 kN preload, 4 kN/mm [estimate]; below 4 kN the")
print("  stack does not move, so crimp height is unaffected, and its travel can trip a switch.")

# --------------------------------------------------------------------------- 4
hr("4. b2: what the actuator does to a hand tool when the dies bottom")
for MA in (8, 12, 20):
    need = (800 / MA, 2600 / MA)
    hand = 300 * MA
    for Fa in (1500, 2000):
        print(f"  MA {MA:2d}: crimp needs {need[0]:4.0f}-{need[1]:4.0f} N at the handle; a hand's ~300 N makes "
              f"{hand/1000:4.1f} kN at the die; actuator stalled at {Fa} N makes {Fa*MA/1000:4.1f} kN "
              f"({Fa/300:.1f}x the hand)")
print("  spring link between actuator and handle, preloaded to ~1.25 x the largest handle need:")
for MA in (8, 12, 20):
    P = 1.25 * 2600 / MA
    print(f"    MA {MA:2d}: preload ~{P:4.0f} N; die force capped near {P*MA/1000:4.1f} kN; stack travel trips 'closed'")
for v, F in ((5.7, 1500), (15.0, 500), (30.0, 225)):
    t = 40.0 / v
    print(f"  actuator {F} N at {v} mm/s: 40 mm of handle travel in {t:4.1f} s [catalog class, estimate]")

# --------------------------------------------------------------------------- 5
hr("5. The person's attended minutes per unit, one task library for every row")
# task library [estimate], the same one used in person_timeline.py
T = dict(cut=20, peel=40, strip=8, hand_crimp=15, insert=8, label=30)
N_C, N_E, N_H = 53, 14, 10


def m(sec):
    return sec / 60.0


today = N_E * (T["cut"] + T["peel"]) + N_C * (T["strip"] + T["hand_crimp"] + T["insert"]) + N_H * T["label"]
rows = [("today, by hand", today, "")]
hand_split_strip = N_E * T["peel"] + N_C * T["strip"]
b1 = N_E * T["cut"] + hand_split_strip + N_E * (60 + 20) + N_C * T["insert"] + N_H * T["label"]
rows.append(("b1 (hand split/strip, fold 60 s/end, hand insert)", b1, "borrowed per-end times"))
b1b4 = N_E * T["cut"] + N_E * 80 + N_E * (60 + 20) + N_C * T["insert"] + N_H * T["label"]
rows.append(("b1 + b4 laser (80 s/end person at the laser)", b1b4, ""))
b1lid = N_E * T["cut"] + hand_split_strip + N_E * (5 + 20) + N_C * T["insert"] + N_H * T["label"]
rows.append(("b1 + fold-back lid (5 s/end)", b1lid, "section 12 condition"))
b1lid_ins = N_E * T["cut"] + hand_split_strip + N_E * (5 + 20) + N_H * (10 + T["label"])
rows.append(("b1 + lid + insertion extension", b1lid_ins, "housing drop 10 s"))
b1_all = N_E * T["cut"] + N_E * 30 + N_E * (5 + 20) + N_H * (10 + T["label"])
rows.append(("b1 + lid + insertion + in-pose score/peel (dock 30 s)", b1_all, "no flips, no comb"))
cyc = 30.0          # b2 machine cycle per crimp, borrowed cycle_and_arm
pre = N_E * (T["cut"] + T["peel"]) + N_C * T["strip"] + N_H * T["label"]
b2_serial = pre + N_C * cyc + N_C * T["insert"]
rows.append(("b2 hand-presented, 30 s cycle, insert after", b2_serial, "attended = every cycle"))
b2_pipe = pre + N_C * max(cyc, 10 + T["insert"])
rows.append(("b2 hand-presented, insert k-1 during cycle k (p4)", b2_pipe, ""))
cyc_fast = 3 + 6 + 4 + 1.5 + 2.7 + 2.7     # faster actuator, 15 mm/s [estimate]
b2_fast = pre + N_C * max(cyc_fast, 5 + T["insert"])
rows.append((f"b2 + 15 mm/s actuator ({cyc_fast:.0f} s) + p4 clamp + pipelined", b2_fast, ""))
for name, sec, note in rows:
    print(f"  {name:58s} {m(sec):5.1f} min  {note}")
print("  Compare rows, not absolutes: the same library gives 46 min for XH work alone, the ledger 45 min")
print("  for every harness [repo labor.md]. What moves the number: folding, splitting/stripping and")
print("  insertion leaving the person; a person-paced cycle longer than a hand crimp adds minutes.")

# --------------------------------------------------------------------------- 6
hr("6. b3: crimp on a fan, trim on a straight line, house at 2.5 mm -> outer conductors too long")
L_split, L_cant = 20.0, 8.0      # b3: 20 mm split, last 8 mm cantilevered straight [borrowed]


def roots(n):
    return [(i - (n - 1) / 2) * RIB for i in range(n)]


for fan in (3.6, 4.35, 5.35):
    out = []
    for label, n in (("4P", 4), ("5P", 5), ("J4 7", 7), ("J1 9", 9)):
        rs = roots(n)
        Xs = []
        for i, y0 in enumerate(rs):
            yf = (i - (n - 1) / 2) * fan
            yh = (i - (n - 1) / 2) * XH
            length = sqrt((L_split - L_cant) ** 2 + (yf - y0) ** 2) + L_cant
            Xs.append(sqrt(length ** 2 - (yh - y0) ** 2))
        ex = max(Xs) - min(Xs)
        bow = 0.64 * sqrt(ex * L_split)
        out.append(f"{label}: +{ex:4.2f} mm (bow ~{bow:3.1f})")
    print(f"  fan {fan:4.2f} mm: " + "; ".join(out))
print("-> per-conductor insertion leaves this as a bow behind the housing; gang insertion needs fronts")
print("   within ~+/-0.3 mm, so it fails for 5P and wider unless each tip is trimmed back by its excess")
print("   (a stepped trim edge on the fan fixture, one step per groove).")

# --------------------------------------------------------------------------- 7
hr("7. b1: trimmed straight at ribbon pitch, housed at 2.5 mm -> outer conductors too short")
for Ls in (8.0, 12.0, 15.0):
    out = []
    for label, n_roots in (("4P", 4), ("5P", 5), ("J2 6", 6), ("J4 7", 7), ("J1 9", 9)):
        rs = roots(n_roots)
        d = max(abs((i - (n_roots - 1) / 2) * XH - y0) for i, y0 in enumerate(rs))
        short = Ls - sqrt(Ls * Ls - d * d)
        out.append(f"{label} {short:4.2f}")
    print(f"  split {Ls:4.1f} mm: outermost front short by (mm) " + ", ".join(out))
print("-> single ribbons stay inside +/-0.3 mm; J1 (and J4 at 8 mm) do not. Trim in the housing's pose")
print("   (a per-loom curved trim slot in the cassette) or accept that the web root peels back a little.")

# --------------------------------------------------------------------------- 8
hr("8. b4: can a +/-45 deg beam reach the flank, and can a slot comb fit, at a given pitch?")
for a in (45.0, 60.0):
    pmin = R + R / cos(radians(a))
    print(f"  beam {a:.0f} deg from vertical reaches the 90 deg flank only if pitch > {pmin:4.2f} mm")
for f in (0.6, 0.8):
    top = BUNDLE / 2 + WALL * (1 - f)
    flank45 = BUNDLE / 2 + WALL * (1 - f * cos(radians(45)) ** 2)
    print(f"  score {f:.0%} of wall top/bottom, 45 deg passes at the flank (cos^2): neck {2*top:4.2f} tall x "
          f"{2*flank45:4.2f} wide")
    for p in (1.7, 2.5, 3.0):
        # below ~2.05 mm pitch the 45 deg beam cannot reach the flank: it stays full wall
        flank = flank45 if p > R + R / cos(radians(45)) else R
        slot_lo = 2 * flank + 0.05
        gap = p - 2 * flank
        tooth = p - min(OD - 0.1, slot_lo + 0.2)
        fits = "fits" if (slot_lo < OD - 0.1 and gap > 0.4 and tooth > 0.3) else "no"
        print(f"    pitch {p:3.1f}: slot must be {slot_lo:4.2f}-{OD-0.1:4.2f} mm, gap between necks {gap:4.2f} mm -> comb {fits}")
print("  at ribbon pitch the flanks of touching conductors are shadowed and unscored, and there is no")
print("  gap for a tooth; the comb needs the conductors spread to ~2.1-2.5 mm first, or a pinch pull.")

# --------------------------------------------------------------------------- 9
hr("9. Peel one conductor at a time along a pre-slit web (split on demand)")
for tear in (15.0, 25.0):                 # N/mm [source: Primasil, via borrowed b4]
    for t in (0.05, 0.1, 0.2, 0.4, 0.6):  # ligament left under a partial slit, or whole web [assumption]
        print(f"  tear strength {tear:.0f} N/mm, ligament {t:4.2f} mm -> {tear*t:5.1f} N to peel")
print("-> a slit to ~70-90 % of the web leaves ~1-5 N of peel, low enough for a fork or hook, and the")
print("   tear follows the slit; the clamp edge is where the peel stops, so it is the split root.")

# --------------------------------------------------------------------------- 10
hr("10. Axial chain (insulation edge in the window) with b4's laser score and slit root")


def rss(v):
    return sqrt(sum(x * x for x in v))


s_lift, h_lift = 20.0, 8.0
dds = (s_lift - sqrt(s_lift ** 2 - h_lift ** 2))
dds_ds = 1 - s_lift / sqrt(s_lift ** 2 - h_lift ** 2)
p1_terms = [0.05, 0.05, 0.20, abs(dds_ds) * 3.0]
b4_terms = [0.07, 0.05, 0.05, abs(dds_ds) * 0.3]
print(f"  p1 wave 1: trim 0.05, cassette 0.05, V-jaw strip 0.20, split root +/-3 mm -> {abs(dds_ds)*3:4.2f}:"
      f" RSS +/-{rss(p1_terms):4.2f} mm")
print(f"  with b4: score line to datum 0.07, cassette 0.05, tear at score 0.05, laser root +/-0.3 mm -> "
      f"{abs(dds_ds)*0.3:4.3f}: RSS +/-{rss(b4_terms):4.2f} mm")
print("  (the insulation edge is the score, placed by the laser relative to the cassette, not by the tip)")

# --------------------------------------------------------------------------- 11
hr("11. Copper strands through b1's fold-back reversals")
d = 0.08
for Rb in (1.5, 2.5):
    eps = d / (2 * Rb)
    for ef, c in ((0.3, -0.5), (0.6, -0.6)):
        Nf = 0.5 * (eps / 2 / ef) ** (1 / c)
        print(f"  bend radius {Rb} mm: strand strain {eps*100:3.1f} %; Coffin-Manson (ef'={ef}, c={c}) life ~{Nf:5.0f} cycles")
print("  b1 uses about two full reversals per conductor (park, lay forward, re-park, straighten):")
print("  well under 1 % of life [estimate]; what remains is a set kink at the split root.")

# --------------------------------------------------------------------------- 12
hr("12. A grooved lid that fans split conductors by closing on them: one-shot capture limit")
for k in (1, 2, 3, 4):
    wmax = RIB * k / (k - 0.5)
    print(f"  conductor {k} from the centre is caught by its own groove only if groove pitch < {wmax:4.2f} mm there")
print("-> one-shot capture into 4 mm parking grooves fails beyond the first neighbour; the lid must close")
print("   from the root outward (zipper) or the grooves must start at ribbon pitch and diverge slowly.")

# --------------------------------------------------------------------------- 13
hr("13. b5: SO-101 backlash if every dock is approached the same way")
print("  borrowed calc: backlash 0.87 deg/joint -> 6.0 mm RSS; repeatability 0.17 deg -> 1.2 mm RSS")
print("  approaching every dock from above with the same payload keeps each joint loaded the same way,")
print("  so taught waypoints absorb the backlash and ~1.2 mm RSS (2.2 worst) remains: inside 5 mm lead-ins.")
print("  A flip reverses gravity on the wrist only: 0.87 deg x ~10-80 mm = 0.15-1.2 mm.")
