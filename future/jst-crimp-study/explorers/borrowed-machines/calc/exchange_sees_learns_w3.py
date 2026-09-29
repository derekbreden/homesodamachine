"""Numbers for the wave-3 exchange: borrowed-machines on machine-that-sees-and-learns.

jst-crimp-study, explorer borrowed-machines, wave 3, 2026-09-28.
Run:  python3 exchange_sees_learns_w3.py > exchange_sees_learns_w3.out.txt

Cited in ../../../exchange/borrowed-machines--on--machine-that-sees-and-learns-w3.md
as [calc W §n].

Inputs: context/xh-facts.md section 1 (clone drawings), machine-that-sees-and-learns
calc/wave2.out.txt §5 and calc/w3_on_hand_tool_as_press.out.txt §9 (their numbers,
cited as [SL ...]), this explorer's calc/presses.py (crank 15 mm, rod 100 mm) and
calc/wave2.py §2 (ribbon buckling), ribbon-as-pallet calc P §3 (tab bending), and the
Prime row for the IMX298 M12 module (sourcing/amazon-prime.md). Labels: [calc] computed
here; [estimate] and [assumption] mine; others cite their source. Nothing measured.
"""
from math import pi, sqrt, sin, cos, tan, atan, acos, asin, radians, degrees


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


# ---------------------------------------------------------------------------
hdr("1. The stroke that follows a tack: which crimper touches first")
ins_open = (2.75, 3.20)       # open insulation wing height, clone [xh-facts s1]
con_left = (0.62, 0.87)       # conductor wings meet their crimper with this much stroke left [SL wave2 s5]
tack_h = (2.3, 2.5)           # v8's tack height [SL v8, estimate]
finals = {
    "final 1.8-2.1 (SL wave2 s5 input)": (1.8, 2.1),
    "final 2.03-2.46 (SL w3 s9, W 1.80-1.95, no silicone flow)": (2.03, 2.46),
}
print(f"conductor wings meet their crimper with {con_left[0]:.2f}-{con_left[1]:.2f} mm of stroke left [SL wave2 s5]")
for name, (flo, fhi) in finals.items():
    un = (ins_open[0] - fhi, ins_open[1] - flo)
    tk = (tack_h[0] - fhi, tack_h[1] - flo)
    print(f"  {name}:")
    print(f"    untacked: insulation wings meet their crimper with {un[0]:+.2f} to {un[1]:+.2f} mm left")
    print(f"    after a {tack_h[0]}-{tack_h[1]} mm tack: insulation crimper meets the tacked barrel with {tk[0]:+.2f} to {tk[1]:+.2f} mm left")
print("  -> after a tack the conductor wings are met first in most combinations; with the SL w3 s9")
print("     heights the tack can be at or below the final height (negative rows), i.e. not a tack")
print("     but the crimp. A tack height has to be set relative to the final height at the same")
print("     width (v3's tack arm already does this), not as an absolute 2.3-2.5 mm.  [calc]")

# ---------------------------------------------------------------------------
hdr("2. Where the bare bundle sits in the open conductor barrel when the jacket is held")
R_j = (0.80, 0.90)            # jacket radius, OD 1.7 +/-0.1 [xh-facts s7]
r_b = (0.345, 0.37)           # bundle radius, 0.69-0.74 [xh-facts s7]
squeeze = (0.05, 0.15)        # tack squeeze of the jacket height [SL v8]
# assumption: insulation-barrel floor and conductor-barrel floor in one plane (clone drawings)
lo0 = R_j[0] - r_b[1]; hi0 = R_j[1] - r_b[0]
print(f"bundle bottom above the conductor-barrel floor, jacket resting on the insulation floor: {lo0:.2f}-{hi0:.2f} mm")
lo1 = lo0 - squeeze[1] * 2 * R_j[1] / 2; hi1 = hi0 - squeeze[0] * 2 * R_j[0] / 2
print(f"  after a 5-15 % tack squeeze (jacket centre drops by half the height loss): {lo1:.2f}-{hi1:.2f} mm")
print(f"  bundle top: {lo1 + 2*r_b[0]:.2f}-{hi1 + 2*r_b[1]:.2f} mm, against conductor wing tips at 1.50-1.60 mm")
print("  -> a gathered bundle held by its jacket hovers ~0.3-0.5 mm off the barrel floor; a strand ON")
print("     the floor has left the bundle. That is a depth difference to look for.  [calc, assumption on floor plane]")
# lighting elevation that can reach the floor past the walls
print("Lowest LED elevation (from horizontal) that still lights the floor at mid-barrel:")
for name, h, d in (("along the axis, over a 2.3-2.5 mm tacked insulation barrel", (2.3, 2.5), (1.1, 1.75)),
                   ("across, over 1.5-1.6 mm conductor wings", (1.5, 1.6), (0.84, 0.95))):
    a1 = degrees(atan(h[0] / d[1])); a2 = degrees(atan(h[1] / d[0]))
    print(f"  {name}: {a1:.0f}-{a2:.0f} deg")
print("Shadow of the hovering bundle on the floor, offset h/tan(elevation):")
for elev in (60, 67, 75):
    off = (lo1 / tan(radians(elev)), hi1 / tan(radians(elev)))
    px = [f"{off[0]*k:.0f}-{off[1]*k:.0f} px at {k} px/mm" for k in (45, 86, 122)]
    print(f"  elevation {elev} deg: offset {off[0]:.2f}-{off[1]:.2f} mm -> " + "; ".join(px))
print("Depth of field at the same magnifications (DOF ~ 2 N c (1+m)/m^2, c = 2 px):")
pix = 0.00112                 # IMX298 pixel pitch, mm [assumption: 1.12 um]
for k in (45, 86, 122):
    m = k * pix
    c = 2 * pix
    for N in (2.0, 2.8):
        dof = 2 * N * c * (1 + m) / m**2
        print(f"  {k:3d} px/mm (m {m:.3f}), f/{N}: DOF ~{dof:.2f} mm")
print("  -> two focus slices do not separate a 0.3-0.5 mm stand-off at these magnifications;")
print("     the displaced shadow under near-vertical LEDs (60-75 deg) does, from ~86 px/mm.  [estimate]")

# ---------------------------------------------------------------------------
hdr("3. Room under a raised applicator crimper for a tack former and a mirror (combination A)")
stroke = (30.0, 40.0)         # mini-applicator 30 mm [b1b, WERI]; JST CDS 40 mm [xh-facts s2]
crimp_face_bdc = (0.8, 2.1)   # crimper faces at bottom = crimp heights above the anvil [facts, SL]
hang = (0.0, 8.0)             # hold-down / stripper parts hanging below the crimper faces at TDC [assumption]
free_lo = stroke[0] + crimp_face_bdc[0] - hang[1]
free_hi = stroke[1] + crimp_face_bdc[1] - hang[0]
print(f"clear height over the anvil with the crank at top dead centre: ~{free_lo:.0f}-{free_hi:.0f} mm [estimate]")
former = 2.4 + 12.0           # former plate bottom at tack height + 12 mm plate
guide = former + 3.0
print(f"  former plate at its tack stop reaches {former:.1f} mm; its guide top ~{guide:.1f} mm")
mir = 10.0
mir_bottom = 2.5 + 1.5
mir_top = mir_bottom + mir * sin(radians(45))
print(f"  10 mm first-surface mirror at 45 deg, lower edge {mir_bottom:.1f} mm up: top at {mir_top:.1f} mm; sight line ~{(mir_bottom+mir_top)/2:.1f} mm up")
print("  -> both fit under the raised crimpers of a 30 mm-stroke applicator, one at a time,")
print("     if nothing on the ram hangs more than ~8 mm below the crimper faces (the jack test measures it).")

# ---------------------------------------------------------------------------
hdr("4. Backing out of a failed tack while the contact is still on its carrier")
rel = (0.4, 1.5)              # force to slide a loose tack off [SL v8]
tab = (4.0, 12.0)             # carrier tab bends at this pull, unheld [ribbon-as-pallet calc P s3]
print(f"tack release {rel[0]}-{rel[1]} N against a tab that bends at {tab[0]}-{tab[1]} N unheld:"
      f" margin {tab[0]/rel[1]:.1f}-{tab[1]/rel[0]:.0f}x")
print("  -> the carrier holds the box during a back-out; no rear shoulder in the neck is needed.")
print("     The empty tacked contact is then crimped empty (envelope 'contact, no wire') and blown")
print("     off the anvil in the dwell, or the next pre-feed pushes it into the incoming contact.  [calc]")

# ---------------------------------------------------------------------------
hdr("5. A crank near bottom dead centre: constant turning against a profiled crawl")
r, L = 15.0, 100.0            # b1b crank and rod [presses.py]


def s_of(th):
    """ram height above BDC for crank angle th (rad) measured from BDC"""
    return r * (1 - cos(th)) + L * (1 - sqrt(1 - (r * sin(th) / L) ** 2))


def th_of(s):
    lo, hi = 0.0, pi / 2
    for _ in range(80):
        mid = (lo + hi) / 2
        if s_of(mid) < s:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def dsdth(th):
    h = 1e-6
    return (s_of(th + h) - s_of(th - h)) / (2 * h)


rates = {"HX711 80 SPS": 80, "HX717 320 SPS": 320, "ADS1220 1000 SPS [assumption]": 1000}
k_loop = (40e3, 100e3)        # N/mm, short stiff obstruction in b1b's loop [procedure calc s3, via b1b]
print("ram speed at constant crank speed, and travel per load-cell sample:")
for T in (10.0, 30.0, 40.0):
    w = 2 * pi / T
    print(f"  one revolution in {T:.0f} s:")
    for s in (1.7, 0.5, 0.3, 0.1):
        th = th_of(s)
        v = dsdth(th) * w
        per = "; ".join(f"{n.split()[0]} {v/sps*1000:.1f} um ({v/sps*k_loop[0]:.0f}-{v/sps*k_loop[1]:.0f} N)"
                        for n, sps in rates.items())
        print(f"    {s:.1f} mm above BDC ({degrees(th):4.1f} deg): {v:.2f} mm/s; per sample {per}")
print("profiled crawl: the MCU slows the crank so the ram moves at a set speed from a taught angle")
for vc in (0.05, 0.1):
    for s0 in (0.95, 1.7):
        print(f"  crawl {vc} mm/s from {s0} mm above BDC: {s0/vc:.0f} s")
for vc in (0.05,):
    th = th_of(0.05)
    w_need = vc / dsdth(th)
    usteps = 3200 * 30
    print(f"  at 0.05 mm above BDC a {vc} mm/s crawl needs {w_need:.3f} rad/s at the crank,"
          f" {w_need/(2*pi)*usteps:.0f} microsteps/s at 3200/rev through 30:1")
comp_k = (5e3, 20e3)          # N/mm, slope of compaction (0.75-2.3 kN over 0.1-0.2 mm) [estimate]
band = 200.0                  # N above the envelope before the MCU calls a fault [estimate]
print("a doubled contact met ~0.2 mm early, caught by a position-indexed envelope:")
for label, v in (("profiled 0.05 mm/s", 0.05), ("constant 30 s/rev at 0.3 mm", dsdth(th_of(0.3)) * 2 * pi / 30)):
    for n, sps in rates.items():
        d = v / sps
        print(f"  {label}, {n}: stops at ~{band + d*comp_k[0]:.0f}-{band + d*comp_k[1]:.0f} N"
              f" (one sample of travel {d*1000:.1f} um into {comp_k[0]/1e3:.0f}-{comp_k[1]/1e3:.0f} kN/mm)")
print("  -> with a crawl profile and an envelope indexed to crank angle, the stop comes at a few")
print("     hundred newtons; the 4 kN disc stack stays as the ceiling if the MCU is wrong.  [estimate]")

# ---------------------------------------------------------------------------
hdr("6. The crank as the height knob and as its own re-touch gauge")
for gear, name in ((10, "10:1 planetary"), (30, "30:1 worm")):
    per_ustep = 2 * pi / (3200 * gear)
    row = []
    for s in (0.02, 0.05, 0.1, 0.2):
        row.append(f"{s} mm: {dsdth(th_of(s))*per_ustep*1000:.2f} um")
    print(f"  {name}, 3200 microsteps/rev: ram travel per microstep at " + "; ".join(row))
for bits, name in ((12, "AS5600 12-bit on the crankshaft"), (14, "14-bit magnetic encoder on the crankshaft")):
    step = 2 * pi / 2**bits
    row = [f"{s} mm: {dsdth(th_of(s))*step*1000:.1f} um" for s in (0.01, 0.03, 0.05)]
    print(f"  {name}: height per count at " + "; ".join(row))
for F in (1000, 3000):
    th = th_of(0.1)
    Tq = F * dsdth(th) / 1000 / 0.85
    print(f"  holding {F} N at 0.1 mm above BDC: {Tq:.2f} N*m at the crank ({Tq/10:.2f} N*m at the motor through 10:1)")
print("  -> stopped short of BDC, the crank sets height in fractions of a micron, and a 10 N re-touch")
print("     read by the shaft encoder measures the unloaded crimp to ~1 um of geometry once r, L and")
print("     BDC are calibrated with one gauge block. Bearing play is taken up in the same direction")
print("     at 10 N as at 3 kN. With both crimpers on one ram the re-touch reads whichever barrel")
print("     springs back higher, the same ambiguity an indicator across the dies has.  [calc]")

# ---------------------------------------------------------------------------
hdr("7. v1b with a press that cannot ride the bed: where Y comes from")
F = 20.0
gt2 = 20 * 2 / (2 * pi)       # 20-tooth GT2 pitch radius, mm
print(f"  proof pull {F:.0f} N on the bed belt (20T GT2, r {gt2:.2f} mm): {F*gt2/1000:.3f} N*m at the motor")
for lead, eff in ((8.0, 0.3), (8.0, 0.5), (2.0, 0.3)):
    print(f"  proof pull {F:.0f} N on a Tr8 lead screw, lead {lead:.0f} mm, efficiency {eff}: "
          f"{F*lead/(2*pi*eff)/1000:.3f} N*m at the motor")
print("  -> an Ender stood on its back puts the carriage in X and the gantry's lead screws along")
print("     the wire; the pallet then gets both axes it needs at a bench-fixed press, and the")
print("     proof pull sits on a lead screw instead of a belt. Z (key height) is set once.  [estimate]")

# ---------------------------------------------------------------------------
hdr("8. A catch plate that tells the box from the crimped barrels by width (b1)")
box_W = (1.85, 1.95); box_H = (2.20, 2.40)     # [xh-facts s1]
ins_W = (1.80, 1.95); ins_H = (2.03, 2.46)     # [SL w3 s9]
con_W = (1.50, 1.60)                           # [xh-facts s1 estimate row]
print(f"  box W {box_W[0]}-{box_W[1]} vs insulation crimp W {ins_W[0]}-{ins_W[1]}:"
      f" slot must exceed {ins_W[1]} and stay under {box_W[0]} -> margin {box_W[0]-ins_W[1]:+.2f} to {box_W[1]-ins_W[0]:+.2f} mm")
print(f"  box H {box_H[0]}-{box_H[1]} vs insulation crimp H {ins_H[0]}-{ins_H[1]}: margin {box_H[0]-ins_H[1]:+.2f} to {box_H[1]-ins_H[0]:+.2f} mm")
print("  -> neither width nor height separates box from insulation crimp across lots; the plate has")
print("     to enter the neck and bear on the box's rear face, with the lance in a notch (ribbon-as-")
print("     pallet's lance-notched plate). b1's 'slot narrower than the box, wider than the barrels'")
print("     only works lot by lot, if at all.  [calc]")

# ---------------------------------------------------------------------------
hdr("9. v6's split: which way the ribbon is drawn under the blade")
EI = 56.0 * 25.0 / (2.046 * pi**2)            # from wave2 s2: 5P fixed-pinned 56 N over 5 mm
print(f"  5P bending stiffness about its thin axis ~{EI:.0f} N*mm^2 [from calc wave2 s2]")
for Lf in (25.0, 30.0, 35.0):
    fp = 2.046 * pi**2 * EI / Lf**2
    print(f"  free {Lf:.0f} mm between clamp and blade (blade end held down on its rib): buckles at {fp:.2f} N")
for webs in (1, 4):
    print(f"  drag of {webs} web(s) cut by an edge at 0.2-3 N each [calc wave2 s2 estimate]: {0.2*webs:.1f}-{3.0*webs:.0f} N")
print("  -> blade entering at the tip and the ribbon drawn so the blade runs toward the clamp puts")
print("     the free length in compression above its 1.1-2.2 N buckling load unless a lid guides it;")
print("     plunging at the root and drawing so the blade runs out at the tip puts it in tension, and")
print("     the root is where the blade went in (b6's rule).  [calc]")

# ---------------------------------------------------------------------------
hdr("10. v7's crawl distance against cycle_and_cost's press line")
first = (0.65, 1.40)          # first wing touch, stroke left [SL wave2 s5]
start = (first[0] + 0.3, first[1] + 0.3)
for v in (0.05, 0.1):
    print(f"  crawl from {start[0]:.2f}-{start[1]:.2f} mm at {v} mm/s: {start[0]/v:.0f}-{start[1]/v:.0f} s"
          f"  (cycle_and_cost s1 books 1 mm: {1/v:.0f} s)")
print("  -> the press line is 0-14 s short at the upper end; per unit 0-12 min.  [calc]")

# ---------------------------------------------------------------------------
hdr("11. Combination A: tack at the anvil of the crank applicator, one conductor  [estimate]")
steps = [
    ("Y index, fork lays conductor in, foot seats it", 8, 15),
    ("side look, continuity to the grounded applicator", 3, 8),
    ("former swings in, tacks to its stop, forming curve", 5, 8),
    ("former out; foot lifts; fork opens and parks", 2, 4),
    ("mirror in; top look, 4-8 lighting states", 6, 15),
    ("mirror out; crank to BDC with profiled crawl from 0.95-1.7 mm", 20, 42),
    ("dwell: withdraw, catch, 20 N pull, after-look", 20, 35),
    ("crank finishes; feed; fork parks the crimp in the band", 8, 15),
]
a = sum(x[1] for x in steps); b = sum(x[2] for x in steps)
for n, lo, hi in steps:
    print(f"  {n:62s} {lo:3d}-{hi:3d} s")
print(f"  per conductor {a}-{b} s; per 53-crimp unit {53*a/3600:.1f}-{53*b/3600:.1f} h unattended")

# ---------------------------------------------------------------------------
hdr("12. v8's per-unit time from its own parts")
t = (29, 81); c = (40, 80)
print(f"  tack side {t[0]}-{t[1]} s + C {c[0]}-{c[1]} s = {t[0]+c[0]}-{t[1]+c[1]} s per crimp;"
      f" x53 = {53*(t[0]+c[0])/3600:.1f}-{53*(t[1]+c[1])/3600:.1f} h (v8 states ~1-2 h)")

# ---------------------------------------------------------------------------
hdr("13. v4: can a light nozzle level a barrels-up contact that rests on its lance?")
E = 110e3                     # phosphor bronze, MPa
sy = (450.0, 650.0)           # yield, MPa [assumption, as ribbon-as-pallet calc P s3]
proud = (0.6, 0.9)            # lance stands proud of the floor [xh-facts s1]
print("lance as a cantilever from the floor [assumption: length 1.5-2.5 mm, width 0.5-0.8 mm, stock 0.20 mm]:")
for Ll in (1.5, 2.0, 2.5):
    for w in (0.5, 0.8):
        t = 0.20
        I = w * t**3 / 12
        k = 3 * E * I / Ll**3
        d_yield = (2 * sy[0] * Ll**2 / (3 * E * t), 2 * sy[1] * Ll**2 / (3 * E * t))
        print(f"  L {Ll} w {w}: stiffness {k:5.1f} N/mm; pressing flat ({proud[0]}-{proud[1]} mm) takes"
              f" {k*proud[0]:4.1f}-{k*proud[1]:4.1f} N; first yield at {d_yield[0]:.2f}-{d_yield[1]:.2f} mm of tip travel")
for Fn in (0.2, 0.5):
    print(f"  a {Fn} N nozzle spring moves the lance tip {Fn/60:.3f}-{Fn/5:.3f} mm (stiffness 5-60 N/mm)")
print("  -> a nozzle on a few tenths of a newton does not level the contact; it lands on a box top")
print("     tilted 11-17 deg. Pressing it flat takes newtons and, as a plain cantilever, passes the")
print("     lance's first yield. The pick has to seal on the tilted top (bellows cup, or a nozzle face")
print("     cut at the tilt), or the contact lies flat first in v4b's lance-relieved pocket.  [estimate]")

# ---------------------------------------------------------------------------
hdr("14. Combination A on b1c's cam shaft: room under the crimpers against shaft angle")
top = 30.0 + 0.8              # crimper faces at TDC above the anvil, 30 mm stroke, low crimp height
for phi in (0, 20, 40, 60, 80, 90, 115):
    ph = radians(phi)
    down = r * (1 - cos(ph)) + L * (1 - sqrt(1 - (r * sin(ph) / L) ** 2))
    print(f"  {phi:3d} deg after TDC: ram {down:5.1f} mm down; crimper faces ~{top-down:4.1f} mm above the anvil"
          f" (less any part hanging below them)")
print("  -> a 14-17 mm former and an 11 mm mirror need the shaft stopped at 0-40 deg; b1c's gate at")
print("     ~115 deg leaves ~9 mm. On b1c the lay-in, tack and top look move to a stop near TDC,")
print("     and the 20-80 deg fork swing no longer races the ram.  [calc]")
