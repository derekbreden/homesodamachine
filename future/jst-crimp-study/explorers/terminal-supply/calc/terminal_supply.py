"""terminal-supply explorer, jst-crimp-study, wave 1 (2026-09-28).

Numbers behind the supply-side arrangements: how much contact supply a unit
and the program use, how precisely a carrier strip locates a contact, what the
carrier can carry as a handle, how far a ribbon must be split to meet a strip,
what a hanging rail can discriminate, what a mating post can hold, and how
close to a seated neighbour a crimp die can work.

Run:  python3 terminal_supply.py > terminal_supply.out.txt

Labels:
  [repo]      this repository
  [mfr]       manufacturer document (links in ../ideas and ../../../context/xh-facts.md)
  [mfr-an]    manufacturer document for an analogous 2.5 mm contact (Wurth WR-WTB)
  [source]    other published source (clone drawings S19-S22 in xh-facts.md)
  [estimate]  judgement, range given
  [assumption] nobody has measured it
"""
from math import pi, tan, atan, radians, degrees, sqrt

def hdr(t):
    print()
    print("=" * 76)
    print(t)
    print("=" * 76)

# ---------------------------------------------------------------- inputs
CRIMPS_PER_UNIT = 53            # [repo] cable-assemblies.md, shared-context
UNITS = 1 + 10 + 50             # [repo] future/README.md: kitchen unit, ten, Founder 50
SPARE = 0.10                    # [assumption] spares, rework, set-up scrap

P_STRIP = 7.10                  # [mfr-an] Wurth 646 101 137 22 carrier pitch 7.10 mm
P_STRIP_RANGE = (7.0, 9.5)      # [source]/[estimate] HDGC drawing scales ~7.0, DLL ~8.5,
                                #   facts pass 7-9.5; one 100-pc strip settles it
CARRIER_W = 3.0                 # [mfr-an] Wurth carrier width 3.00 mm
HOLE_D = 1.50                   # [source] HDGC pilot hole; [mfr-an] Wurth 1.50
T = 0.20                        # [source] stock 0.20 +/- 0.02 C5191
RHO_BRONZE = 8.8e-3             # g/mm^3
TAB = (0.8, 1.15)               # [source] tab carrier-edge to contact rear, HDGC..CJT
L_CONTACT = (5.8, 6.73)         # [source] clone overall length (JST 6.1 or 6.5 [mfr])
M_CONTACT = 0.043               # g [source] LCSC BXH-001T-P0.6

# open-barrel and box envelope, clone drawings [source S19-S22]
BOX_W = (1.85, 1.90)            # +/-0.10
BOX_H = (2.20, 2.35)            # +/-0.10
CB_OPEN_W = (1.80, 1.90)        # conductor barrel open width, +/-0.25
IB_OPEN_W = (2.70, 3.00)        # insulation barrel open width, +/-0.25
IB_OPEN_H = (2.75, 3.20)
LANCE_TIP_FROM_FRONT = (2.44, 2.57)
LANCE_PROUD = (0.67, 0.90)

XH_PITCH = 2.50                 # [mfr]
RIB_PITCH = 1.70                # [source] BNTECHGO
INS_OD = 1.70
HSG_H = 7.75                    # [mfr] XHP height along mating axis

# ---------------------------------------------------------------- 1
hdr("1. How much supply, and how often it is refilled")
prog = CRIMPS_PER_UNIT * UNITS
prog_sp = prog * (1 + SPARE)
print(f"crimps per unit {CRIMPS_PER_UNIT}; program {UNITS} units -> {prog} crimps, "
      f"{prog_sp:.0f} with {SPARE:.0%} spare")
for p in (P_STRIP,) + P_STRIP_RANGE:
    print(f"  strip at pitch {p:.2f} mm: one unit = {CRIMPS_PER_UNIT*p/1000:.2f} m of strip; "
          f"program = {prog_sp*p/1000:.1f} m")
print("supply forms, units covered per refill:")
forms = [
    ("cut strip 100 pc (Digi-Key 455-1135-100-ND / LCSC min 100)", 100),
    ("cut strip 500 pc (Digi-Key 455-1135-500-ND)", 500),
    ("small reel 1,000 pc (Wurth-size, 200 mm reel)", 1000),
    ("JST reel 8,000 pc (SXH-001T-P0.6)", 8000),
    ("clone reel 9,000 pc (HDGC)", 9000),
]
for name, n in forms:
    print(f"  {name:62s} {n/CRIMPS_PER_UNIT:6.1f} units")
print("reel geometry check: 1,000 pc at 7.10 mm = 7.1 m on a 200 mm reel with a 100 mm hub [mfr-an]")
L8k = 8000 * P_STRIP / 1000
print(f"  8,000 pc = {L8k:.0f} m of strip; if wound like the Wurth reel (7.1 m per ~50 mm of radial build)"
      f" it needs roughly a 330-400 mm reel [estimate]")

# price per unit's contacts, observed 2026-09-28 in xh-facts.md section 6
print("contact cost per unit (53):")
for name, each in (("SXH-001T-P0.6 LCSC @100", 0.0127), ("SXH-001T-P0.6 Digi-Key 100 lot", 0.0471),
                   ("BXH-001T-P0.6 Digi-Key loose", 0.0444), ("CJT A2501-TP clone reel, LCSC", 0.0079)):
    print(f"  {name:36s} ${each*CRIMPS_PER_UNIT:5.2f} per unit, ${each*prog_sp:6.0f} per program")

# loose contacts in a hopper
env = 6.2 * 2.9 * 3.1            # mm^3 bounding box, open contact [estimate from clone dims]
for pf in (0.10, 0.20):          # [estimate] bulk packing fraction of tangly open-barrel parts
    per_cc = 1000 / (env / pf)
    print(f"  loose, bulk packing {pf:.2f}: ~{per_cc:.0f} contacts per cc -> 200 cc hopper holds "
          f"~{200*per_cc:.0f} = {200*per_cc/CRIMPS_PER_UNIT:.0f} units")
print(f"  mass: 53 contacts = {53*M_CONTACT:.2f} g; the program's {prog_sp:.0f} = {prog_sp*M_CONTACT:.0f} g")

# ---------------------------------------------------------------- 2
hdr("2. Locating a contact by its carrier strip")
print("Pilot hole on the contact centreline, one per contact [source S19; mfr-an Wurth].")
for pin in (1.45, 1.48):
    print(f"  hole {HOLE_D:.2f} (+/-0.02 stamped [estimate]) with pin {pin:.2f}: "
          f"float {(HOLE_D-0.02-pin)/2:+.3f} to {(HOLE_D+0.02-pin)/2:+.3f} mm radial")
print("  a tapered pin driven home takes the float out entirely: it centres, then the hold-down clamps")
print("hole-to-contact-centreline within one reel: +/-0.02-0.05 mm [estimate, progressive-die stamping]")
print("between reels / brands: tab length 0.8+/-0.2 (HDGC), 1.00+/-0.15 (DLL) [source] ->")
print("  axial barrel position relative to the carrier edge can differ ~0.2-0.4 mm between lots:")
print("  re-teach the axial offset once per reel (camera finds the barrel's rear edge vs the hole)")
print("What the die needs [xh-facts; MKS-L manual 6-10]:")
print(f"  bellmouth ~1-2 x stock = {T:.2f}-{2*T:.2f} mm -> axial placement window ~+/-0.1 mm")
print("  lateral: the punch lead-in centres an open barrel offset by ~0.1 mm; 'twisting' and 'rolling'")
print("  come from a contact not square on the anvil [MKS-L 7-8, 7-9] -> hold the carrier flat")
print("Indexing error does not accumulate if the station locates on holes each cycle:")
for n in (1, 10, 53):
    acc = 0.02 * sqrt(n)         # random pitch error 0.02 mm per pitch, root-sum-square
    print(f"  sprocket counting {n:3d} pitches: +/-{acc:.2f} mm (rss of 0.02/pitch) ; pin at station: +/-0.03")

# ---------------------------------------------------------------- 3
hdr("3. Carrier scrap")
a_blank = CARRIER_W * P_STRIP - pi / 4 * HOLE_D**2 - 2.5 * 1.2   # minus hole and slot [estimate slot 2.5x1.2]
v = a_blank * T
m = v * RHO_BRONZE
print(f"carrier per contact ~{a_blank:.1f} mm^2 x {T} mm = {v:.2f} mm^3 = {m*1000:.0f} mg")
print(f"per unit: {CRIMPS_PER_UNIT*m:.1f} g of bronze, {CRIMPS_PER_UNIT*P_STRIP:.0f} mm of empty carrier;"
      f" program ~{prog_sp*m:.0f} g, {prog_sp*P_STRIP/1000:.0f} m")
print("  continuous: a take-up spool of ~60 mm hub holds a unit's 0.38 m in 2 turns [calc]")

# ---------------------------------------------------------------- 4
hdr("4. The carrier as a handle after the crimp")
SY = 550.0                       # MPa [estimate] C5191 half-hard yield (xh-facts calc uses the same)
for wt in (0.6, 0.8, 1.0):       # tab neck width [estimate, reading clone drawings]
    Fc = SY * wt * T
    Mp = SY * wt * T**2 / 4
    print(f"  tab neck {wt:.1f} wide: in-plane push to yield {Fc:4.0f} N; out-of-plane plastic moment "
          f"{Mp:.1f} N*mm")
for e in (0.8, 1.2):             # push line offset: floor plane to box centre, mm
    print(f"    unguided push with the resistance {e} mm above the floor plane: tab yields at "
          f"{SY*0.8*T**2/4/e:.1f} N (0.8 mm neck)")
print("  insertion force of an XH contact into XHP is not public: bracket 3-20 N [estimate]")
print("  -> the tab can steer the contact and push it while the cavity guides it (moment reacted);")
print("     it cannot push it home unguided. A fork behind the insulation barrel finishes the seat.")
print("Trimmed handle so neighbours fit the 2.5 mm pitch:")
wh = 2.3
lig = (wh - HOLE_D) / 2
print(f"  handle {wh} mm wide centred on the {HOLE_D} hole leaves ligaments {lig:.2f} mm each side;"
      f" both carry {2*lig*T*SY:.0f} N")
print(f"  gap to the neighbour's handle at {XH_PITCH} mm pitch: {XH_PITCH-wh:.1f} mm")
print("Does the carrier edge hit the housing's rear face before the contact seats?")
front_wall = (0.8, 1.0)          # [assumption] housing front wall ahead of the contact box
for fw in front_wall:
    for Lc in (6.1, 6.5):        # [mfr] JST catalog lengths, editions disagree
        inside = HSG_H - fw - Lc  # contact rear inside the rear face by this much
        for tab in TAB:
            margin = tab - inside
            print(f"  front wall {fw}, contact {Lc}: rear {inside:+.2f} inside face; tab {tab}: "
                  f"carrier edge {margin:+.2f} {'outside (clears)' if margin > 0 else 'INSIDE -> blocks seat'}")

# ---------------------------------------------------------------- 5
hdr("5. Comb: all of a ribbon's conductors crimped to consecutive strip contacts")
for n in (3, 4, 5):
    for p in (P_STRIP, 9.5):
        outer = (n - 1) / 2 * (p - RIB_PITCH)
        L20 = outer / tan(radians(20))
        print(f"  {n}P at strip pitch {p:.1f}: outer conductor moves {outer:5.1f} mm; "
              f"at a 20 deg fan it needs {L20:4.0f} mm of split web (+ ~6 mm straight)")
for n in (3, 4, 5):
    outer = (n - 1) / 2 * (XH_PITCH - RIB_PITCH)
    print(f"  compare {n}P into XHP at 2.5 mm: outer moves {outer:.1f} mm -> {outer/tan(radians(20)):.0f} mm")

# ---------------------------------------------------------------- 6
hdr("6. Hanging rail: what a slot can tell apart")
print("A contact hangs box-down from its insulation wings; everything else is below the rail")
print("tolerances: box +/-0.10, open barrels +/-0.25 [source]")
def passes(dim_lo, dim_hi, tol, slot):
    lo, hi = dim_lo - tol, dim_hi + tol
    if hi < slot: return "always passes"
    if lo > slot: return "never passes"
    return f"MAYBE ({lo:.2f}-{hi:.2f} vs {slot:.2f})"
for slot in (2.0, 2.05, 2.1, 2.3, 2.4):
    print(f" slot {slot:.2f}: box W {passes(*BOX_W, 0.10, slot):28s} box H {passes(*BOX_H, 0.10, slot):28s}"
          f" cond barrel {passes(*CB_OPEN_W, 0.25, slot):28s} ins wings W {passes(*IB_OPEN_W, 0.25, slot)}")
print("-> a single slot of ~2.4 lets the box and conductor barrel through and hangs on the wings,")
print("   but lets the box hang either way round (box H also < 2.4): 4 roll states.")
print("-> a stepped rail, 2.4 at the barrels and 2.05 at the box, accepts the box only W-across:")
print("   2 roll states left (U open fore or aft along the rail); a contact that arrives box H-across")
print("   rides ~2 mm high on the step and a height wiper knocks it back into the hopper.")
print("   The last 2 states are told apart by camera (U opening seen from above) or by the lance side.")

# ---------------------------------------------------------------- 7
hdr("7. Holding a contact by mating it onto a 0.64 mm square post")
# per-contact normal force and unmating force are not in any public JST document
# Molex KK 254 on 0.64 mm posts: normal force 200 g min, unmating 57 g min [source, search summary
# of Molex PS-10-07-001, not opened]
for Nt, mu in ((1.0, 0.2), (2.0, 0.3), (4.0, 0.4)):
    print(f"  total normal force {Nt:.0f} N, friction {mu}: axial hold {Nt*mu:.1f} N "
          f"({Nt*mu/(M_CONTACT*9.81e-3):,.0f} x the contact's weight)")
print("  loads it must resist: weight 0.0004 N; conductor sliding into an open U ~0.01-0.1 N [estimate];")
print("  during the crimp the die clamps the barrels and the post only locates the box")
print("  release: pull the crimped wire back, 0.2-2 N; a 22 AWG conductor breaks at ~85-100 N [xh-facts]")
print("Post stiffness, square 0.64 mm, cantilever k = 3EI/L^3:")
a = 0.64
I = a**4 / 12
for E, name in ((100e3, "brass"), (200e3, "steel")):
    for L in (3, 6, 10, 17):
        k = 3 * E * I / L**3
        print(f"  {name:5s} L {L:2d} mm: {k:8.2f} N/mm")
print("  -> a 3 mm post is stiff (locates); a 17 mm post through a housing is soft (the die and the")
print("     cavity steer it; it only needs to carry the contact, not to fight the die)")

# ---------------------------------------------------------------- 8
hdr("8. Crimping at the housing's rear face next to a seated neighbour")
# stage depth s = how far the box front is inside the rear face; lance must stay outside
for s in (1.0, 1.5, 2.0):
    lance_margin = min(LANCE_TIP_FROM_FRONT) - s
    cb = (2.6 - s, 4.0 - s)      # conductor barrel ~2.6-4.0 from front [estimate from clone drawings]
    ib = (4.5 - s, 6.0 - s)      # insulation barrel ~4.5-6.0 from front [estimate]
    print(f" staged {s:.1f} mm deep: lance tip {lance_margin:+.2f} mm outside the face; conductor barrel "
          f"{cb[0]:.1f}-{cb[1]:.1f} mm behind the face; insulation barrel {ib[0]:.1f}-{ib[1]:.1f}")
print("Neighbour's wire (1.7 OD) leaves the face at 2.5 mm pitch; the punch straddles the barrel.")
for half, what in ((1.35, "conductor punch 2.7 wide"), (1.75, "conductor punch 3.5 wide"),
                   (1.75, "insulation punch 3.5 wide"), (2.0, "insulation punch 4.0 wide")):
    need = half + INS_OD / 2 + 0.2 - XH_PITCH     # extra lateral room the neighbour must give
    print(f"  {what}: neighbour must move {max(need,0):.2f} mm sideways where the punch is")
    for d in (0.5, 1.0, 2.0, 3.0):
        th = degrees(atan(max(need, 0) / d))
        print(f"      at {d:.1f} mm behind the face -> neighbour bent {th:4.1f} deg from the face")
print("Why not thin die walls instead: a punch wall 0.5 mm thick x 1.5 mm long carrying a side load")
for Fs in (100, 300):            # N [estimate] outward push of curling wings on one wall
    lever = 1.5                  # mm, wall height above the reaction
    sig = 6 * Fs * lever / (1.5 * 0.5**2)
    print(f"  side load {Fs} N at {lever} mm: bending stress ~{sig:,.0f} MPa (tool steel ~2,000-2,500 yield)")
print("-> bending the seated neighbour ~20-30 deg at the face clears the dies from ~1 mm back;")
print("   staging 1.5 mm deep puts the conductor barrel 1.1-2.5 mm back, the insulation 3.0-4.5.")

# ---------------------------------------------------------------- 9
hdr("9. Separating a crimped contact from its carrier")
print("shear the tab: 48-158 N at the edge [xh-facts calc C1]")
for lev in (4, 6):
    print(f"  flush cutter with jaw leverage {lev}: {48/lev:.0f}-{158/lev:.0f} N at the handle")
for Tq, arm in ((0.9, 20), (1.1, 25)):  # MG996R-class 9.4-11 kg*cm [estimate from listings]
    print(f"  servo {Tq} N*m on a {arm} mm arm: {Tq/arm*1000:.0f} N")
# bend-off: Coffin-Manson on the tab
for R in (0.2, 0.4):
    eps = T / (2 * R + T)
    for ef, c in ((0.3, -0.6), (0.6, -0.6)):
        N2 = (eps / ef) ** (1 / c)
        print(f"  bend the tab around R {R} mm: strain amplitude {eps:.2f}; eps_f' {ef}: "
              f"~{max(N2/2, 0.5):.1f} full cycles to break [estimate]")
print("  -> a sharp +/-90 deg bend breaks the tab in 1-5 cycles; the break lands at the neck, not flush")

# ---------------------------------------------------------------- 10
hdr("10. Time, to show slowness costs nothing here [estimate]")
steps = {"strip index + pilot pin": 5, "present conductor to the waiting contact": 30,
         "slow crimp stroke": 30, "sever / release": 10, "camera look": 10, "retries, average": 15}
cyc = sum(steps.values())
for k_, v_ in steps.items():
    print(f"  {k_:44s} {v_:3d} s")
print(f"  per crimp ~{cyc} s -> a unit's 53 in {cyc*53/60:.0f} min; a loose-part rail feeder adds nothing to")
print("  that (it fills its escapement while the crimp runs)")
