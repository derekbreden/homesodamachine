"""terminal-supply on change-the-question, wave 2 exchange (2026-09-28).

Numbers behind ../../../exchange/terminal-supply--on--change-the-question.md.
Each section answers one conflict or combination named there.

Run:  python3 on_change_the_question.py > on_change_the_question.out.txt

Labels:
  [repo]       this repository
  [mfr]        manufacturer document
  [mfr-an]     Wurth WR-WTB 2.50 mm female crimp contact 646 101 137 22 (1,000 reel)
               and 646 001 137 22 (10,000 reel), drawing rev C/H 2017, read 2026-09-28:
               https://www.we-online.com/components/products/datasheet/64610113722.pdf
               https://www.we-online.com/components/products/datasheet/64600113722.pdf
  [source]     clone drawings S19-S22 in ../../../context/xh-facts.md
  [ctq]        change-the-question calc ../../change-the-question/calc/ctq.out.txt
  [ts]         my wave-1 calc terminal_supply.out.txt
  [estimate]   judgement, range given
  [assumption] nobody has measured it
"""
from math import pi, sqrt, tan, atan, radians, degrees


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


def rss(xs):
    return sqrt(sum(x * x for x in xs))


# ------------------------------------------------------------------ inputs
HOUSINGS_PER_UNIT = 10          # [repo] cable-assemblies.md
CRIMPS_PER_UNIT = 53            # [repo]
T4_ENDS_PER_UNIT = 5            # [ctq s1] J3, J5, J9, J11, J13
T4_RUN_LONG, T4_RUN_SHORT = 21, 38   # [ctq s9] T4 ends per 15.2 m 4P spool
P_STRIP = 7.10                  # [mfr-an]
RIB = 1.70                      # [source] ribbon pitch
HALF = 2 * RIB                  # c1 half-row pitch 3.4
XH = 2.50

# ------------------------------------------------------------------ 1
hdr("1. Who touches the contacts in c1, and how often the machine calls the person")
t_pocket = (6, 10)              # s per contact dropped into a pocket with tweezers [estimate]
print(f"c1 as written: the person drops {CRIMPS_PER_UNIT} loose contacts into pockets per unit")
print(f"  at {t_pocket[0]}-{t_pocket[1]} s each [estimate]: "
      f"{CRIMPS_PER_UNIT*t_pocket[0]/60:.1f}-{CRIMPS_PER_UNIT*t_pocket[1]/60:.1f} min of fine handling per unit")
print("calls per unit (one machine cycle = one housing; a pair is laid edge to edge in one clamp):")
rows = [
    ("c1, two pallets, loaded by hand", HOUSINGS_PER_UNIT, CRIMPS_PER_UNIT),
    ("c1, one pallet used twice (its branch 5)", 2 * HOUSINGS_PER_UNIT, CRIMPS_PER_UNIT),
    ("c1 + strip-fed pallet loader (section 3)", HOUSINGS_PER_UNIT, 0),
    ("c5 T4 run + c1 + strip loader + housing stick, long ends",
     T4_ENDS_PER_UNIT / T4_RUN_LONG + (HOUSINGS_PER_UNIT - T4_ENDS_PER_UNIT), 0),
    ("c5 T4 run + c1 + strip loader + housing stick, short ends",
     T4_ENDS_PER_UNIT / T4_RUN_SHORT + (HOUSINGS_PER_UNIT - T4_ENDS_PER_UNIT), 0),
]
for name, calls, hand in rows:
    print(f"  {name:62s} calls/unit {calls:5.2f}   contacts by hand {hand}")
print("  (the last two keep the five non-T4 housings attended: 5 calls; T4 costs one call per spool run)")

# ------------------------------------------------------------------ 2
hdr("2. The Wurth WR-WTB 2.50 contact is not an XH-sized box [mfr-an]")
wurth = dict(box_w=1.45, box_h=2.00, ins_open_w=2.30, ins_open_h=2.15,
             cond_open_w=1.85, cond_open_h=1.62, length=7.0, tab=10.8 - 7.0 - 3.0,
             lance_proud=0.65, lance_tip_from_front=2.30)
xh_box_w = (1.85, 1.95)         # clone drawings / JST envelope [source, mfr]
xh_box_h = (2.20, 2.40)
print(f"Wurth section C-C box {wurth['box_w']} x {wurth['box_h']} mm; XH box {xh_box_w[0]}-{xh_box_w[1]} x "
      f"{xh_box_h[0]}-{xh_box_h[1]} mm")
print(f"  narrower by {xh_box_w[0]-wurth['box_w']:.2f}-{xh_box_w[1]-wurth['box_w']:.2f} mm, "
      f"lower by {xh_box_h[0]-wurth['box_h']:.2f}-{xh_box_h[1]-wurth['box_h']:.2f} mm")
print(f"  length box front to insulation-barrel rear {wurth['length']} mm (XH 6.1/6.5 JST, 5.8-6.73 clones)")
print(f"  tab (10.8 overall - 7.0 contact - 3.00 carrier) = {wurth['tab']:.2f} mm")
print(f"  pilot-hole centre to contact rear = 3.00/2 + tab = {1.5 + wurth['tab']:.2f} mm")
print(f"  lance {wurth['lance_proud']} +/-0.1 proud on the floor side, tip {wurth['lance_tip_from_front']} mm behind the front")
print("  -> its 2.3 mm open wings belong to a smaller box; the 0.20 mm 'Wurth' gap at 2.5 mm pitch")
print("     in [ctq s3] is a property of a different connector, not of an XH-compatible option.")
print("     646 101 137 22 and 646 001 137 22 are the same contact on 1,000- and 10,000-piece reels.")

# ------------------------------------------------------------------ 3
hdr("3. Loading c1's pallet from strip: sever before the wire arrives")
stock = 0.20
print("With no wire over the tab, every pilot hole is free, including the station's own:")
print("  pin in the station hole + pins either side; a blade from above can cut anywhere along the tab.")
for tab in (0.7, 0.8, 1.0, 1.15):
    cut_from_edge = tab - 1.25 * stock
    print(f"  tab {tab:.2f} mm: to leave a 1.0-1.5 x t stub ({stock:.2f}-{1.5*stock:.2f} mm) cut "
          f"{tab-1.5*stock:.2f}-{tab-stock:.2f} mm from the carrier edge")
print("  (drop-shear with the wire present parts the tab where the anvil's rear edge sits; here the line")
print("   is chosen freely, and the stub criterion [mfr S5] is met by blade position alone)")
ins_w = (2.46, 3.25)           # clone open insulation wings incl. tolerance [source]
for p in (HALF, 5.0):
    print(f"  pallet at {p:.1f} mm: gap between open wing tips {p-ins_w[1]:.2f}-{p-ins_w[0]:.2f} mm")
print("  -> load at 5.0 mm (cam plate open), close to 3.4 for the lay, reopen to 5.0 to insert")
t_load = (10, 15)
print(f"  loader cycle {t_load[0]}-{t_load[1]} s per contact [estimate]: a T4 end's 4 in "
      f"{4*t_load[0]}-{4*t_load[1]} s, J1's 9 in {9*t_load[0]}-{9*t_load[1]} s, overlapped with crimping")

# ------------------------------------------------------------------ 4
hdr("4. Tack first, then crimp in the row: tacked neighbours are narrow [ctq s3 punch estimate]")
clear = 0.10
punch_cond_half = (1.75, 1.90)  # [ctq s3 estimate]
punch_ins_half = (1.90, 2.00)   # insulation crimp W 1.8-2.0 + ~1 mm walls [estimate]
neigh = [
    ("open insulation wings, clone worst 3.25", 3.25),
    ("open insulation wings, clone nominal 2.8", 2.80),
    ("tacked insulation barrel, loose 2.0-2.2", 2.20),
    ("open conductor wings, clone worst 2.15", 2.15),
]
for name, w in neigh:
    room = HALF - w / 2 - clear
    print(f"  at 3.4 mm beside {name:40s}: half-room {room:.2f} mm")
print(f"  conductor punch half-width {punch_cond_half[0]}-{punch_cond_half[1]}, insulation section "
      f"{punch_ins_half[0]}-{punch_ins_half[1]} [estimate]")
print("  -> beside open clone wings the room (1.67-1.90) is under the punch: c1 needs its lift;")
print("     beside tacked neighbours (2.20-2.23) both sections fit with 0.2-0.4 mm: no lift needed.")
print("Lateral clearance while carrier k rises past its neighbours (c1's lift):")
for name, wk, wn in [("open vs open, clone worst", 3.25, 3.25),
                     ("open vs open, clone nominal", 2.80, 2.80),
                     ("tacked vs tacked", 2.20, 2.20)]:
    g = HALF - (wk + wn) / 2
    print(f"  {name:28s}: wing-tip gap {g:.2f} mm -> carrier guided to +/-{g/2:.2f} mm or wings clash")

# ------------------------------------------------------------------ 5
hdr("5. What sets bellmouth in c1: the chain from punch to barrel along the contact axis")
chain_c1 = [("punch to frame (machined)", 0.01, 0.01),
            ("frame to pallet slide, datum stop on clamp frame", 0.03, 0.05),
            ("pallet to carrier guide (printed, also lifts and spreads)", 0.05, 0.10),
            ("carrier pocket rear shoulder (printed)", 0.05, 0.10),
            ("box rear face to conductor-barrel rear edge (part)", 0.05, 0.10)]
lo = [c[1] for c in chain_c1]; hi = [c[2] for c in chain_c1]
for n, a, b in chain_c1:
    print(f"  +/-{a:.2f}-{b:.2f}  {n}")
print(f"  c1 as written: RSS +/-{rss(lo):.2f}-{rss(hi):.2f} mm, worst case +/-{sum(lo):.2f}-{sum(hi):.2f} mm")
chain_st = [("front stop to punch, one steel block", 0.01, 0.02),
            ("box front face to conductor-barrel rear edge (part)", 0.05, 0.10)]
lo2 = [c[1] for c in chain_st]; hi2 = [c[2] for c in chain_st]
print(f"  box-front stop at the station, carrier sprung forward: RSS +/-{rss(lo2):.2f}-{rss(hi2):.2f}, "
      f"worst +/-{sum(lo2):.2f}-{sum(hi2):.2f}")
print("  window needed: bellmouth ~1-2 x stock -> about +/-0.1 mm [xh-facts s5; ts s2]")
print("  per-lot camera re-teach removes the part's lot offset, leaving within-lot scatter +/-0.03-0.05")

# ------------------------------------------------------------------ 6
hdr("6. Half-rows onto consecutive strip contacts (my a2b 'comb', with c1's split)")
ang = radians(20)
print("  n   full-row move/split (ts s5)      half-row move/split at 3.4 -> 7.1")
for n in (2, 3, 4, 5):
    full = (n - 1) / 2 * (P_STRIP - RIB)
    half = (n - 1) / 2 * (P_STRIP - HALF)
    print(f"  {n}   {full:5.2f} mm / {full/tan(ang):5.1f} mm            {half:5.2f} mm / {half/tan(ang):5.1f} mm   (+ ~6 mm straight)")
print("  T4 is two half-rows of 2: 1.85 mm each way, ~5 mm of fan, where a whole 4P needs 22 mm.")
print("  A pair needs no comb: one wedge dropped between the two conductors spreads them symmetrically.")
print("  Pins cannot rise through a hole that has insulation over it; a tapered pin that stops flush")
print("  with the carrier's top face still centres on the hole's lower edge (stock 0.20 mm).")

# ------------------------------------------------------------------ 7
hdr("7. How hard a tack holds on silicone (c1b), against what it must resist [estimate]")
D, wall = 1.6, 0.49
cases = [("low", 1.0, 1.0, 0.05, 0.8, 0.3),
         ("mid", 3.0, 2.0, 0.10, 1.0, 0.5),
         ("high", 10.0, 3.0, 0.20, 1.5, 0.8)]
for name, E, f, d, Lb, mu in cases:
    p = f * E * d / wall
    A = pi * D * 0.75 * Lb
    N = p * A
    print(f"  {name:4s}: E {E:4.1f} MPa x confinement {f:.0f}, squeeze {d:.2f} mm of {wall} wall, barrel {Lb} mm, "
          f"mu {mu}: normal {N:5.1f} N -> slide grip {mu*N:5.2f} N")
print("  loads on a tacked flag: its weight 0.0004 N; box into a keyed slot 0.1-0.5 N [estimate];")
print("  box onto a 0.64 mm post 0.2-1.6 N [ts s7]. A tack under ~2 N may slip on a post, not in a slot.")

# ------------------------------------------------------------------ 8
hdr("8. c3: a printed folding arch at the wing edge; soldering a contact still on its strip")
for mat, Estar, Y in (("PETG", 2.4e3, 48), ("PET-CF", 6.0e3, 80)):
    for F, L, R in ((8, 1.3, 0.1), (8, 1.3, 0.05), (40, 1.3, 0.1)):
        q = F / L
        b = sqrt(4 * q * R / (pi * Estar))
        pmax = 2 * q / (pi * b)
        print(f"  {mat:6s} wing-edge load {F:3d} N over {L} mm, edge radius {R}: contact p_max {pmax:5.0f} MPa "
              f"(yield ~{Y} [estimate])")
print("  -> a printed arch dents where each wing tip first slides; the fold profile must be steel.")
for k in (50, 70):
    for w in (0.6, 1.0):
        G = k * (w * 1e-3) * (0.2e-3) / (0.8e-3)
        print(f"  tab neck k {k} W/mK, {w} mm wide, 0.2 thick, 0.8 long: {G*230:4.1f} W lost at 230 K rise")
print("  -> against a 60-70 W iron the tab is a thermal choke: soldering on the strip is not starved.")

# ------------------------------------------------------------------ 9
hdr("9. c5: what one unattended T4 spool run consumes")
for name, ends in (("long (700 mm)", T4_RUN_LONG), ("short (400 mm)", T4_RUN_SHORT)):
    c = 4 * ends
    print(f"  {name:15s}: {ends} ends, {c} contacts = {c*P_STRIP/1000:.2f} m of strip "
          f"({c/100:.2f} x 100-pc strips), {ends} XHP-4 housings")
    for pitch, what in ((5.7, "stacked by depth incl. lock ramp"), (7.75, "stacked by height")):
        print(f"      housing stick {ends*pitch:5.0f} mm tall ({what}, {pitch} mm each) [mfr S2 dims]")
    t_end = (8, 12)
    print(f"      at {t_end[0]}-{t_end[1]} min per end [estimate]: {ends*t_end[0]/60:.1f}-{ends*t_end[1]/60:.1f} h unattended")

# ------------------------------------------------------------------ 10
hdr("10. c1 step 8: how far the housing with row A can move out of row B's way")
for L in (12, 15, 20):
    behind = (3.0, 4.5)        # conductor tip to insulation-barrel rear [estimate: 2.4 strip + window + barrel]
    inset = (0.45, 1.25)       # contact rear inside the housing rear face [ts s4]
    free_lo = L - behind[1] - inset[1]
    free_hi = L - behind[0] - inset[0]
    print(f"  split {L} mm: free conductor between web root and housing rear face ~{free_lo:.1f}-{free_hi:.1f} mm")
print("  -> the housing is tethered within ~6-17 mm of the root; any lift sends row A's wires")
print("     back across the zone over (or under) pallet B where comb, punch and ram work.")
