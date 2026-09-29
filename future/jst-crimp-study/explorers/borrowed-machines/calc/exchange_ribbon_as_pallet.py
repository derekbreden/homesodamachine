"""Numbers for the wave-2 exchange: borrowed-machines on ribbon-as-pallet.

jst-crimp-study, explorer borrowed-machines, wave 2, 2026-09-28.
Run:  python3 exchange_ribbon_as_pallet.py > exchange_ribbon_as_pallet.out.txt

Cited in ../../../exchange/borrowed-machines--on--ribbon-as-pallet.md as [calc X §n].
Inputs are taken from ../../../context/xh-facts.md (clone drawings, JST
catalog), from ribbon-as-pallet's calc/pallet_geometry.py (conductor
mechanics, fan geometry), from this explorer's calc/presses.py (frame
stiffness, crank dwell), and from the JST MKS-L applicator instruction manual
(media.digikey.com MKSL_Instr_Man.pdf, fetched 2026-09-28). Labels:
[source] cited elsewhere, [estimate] and [assumption] mine. Nothing measured.
"""
from math import pi, sqrt, sin, cos, tan, atan, acos, radians, degrees, exp, floor


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


def s_bend_length(delta, R, theta_max_deg):
    """Axial length of an S-bend (arc R, straight at theta, arc R) giving an
    offset delta. Same construction as ribbon-as-pallet calc §2."""
    delta = abs(delta)
    th_max = radians(theta_max_deg)
    d_arc_max = 2 * R * (1 - cos(th_max))
    if delta <= d_arc_max:
        th = acos(1 - delta / (2 * R))
        return 2 * R * sin(th)
    s = (delta - d_arc_max) / sin(th_max)
    return 2 * R * sin(th_max) + s * cos(th_max)


# ---------------------------------------------------------------------------
hdr("1. a1 lay-in: where the finger acts, and how much free conductor a 5 mm drop needs")
# Contact along its axis, from the conductor tip (front of the conductor barrel) backwards.
cb = (1.25, 1.50)      # conductor barrel length [estimate, clone drawings, xh-facts §1]
gap = (0.5, 0.8)       # gap between barrels [ribbon-as-pallet estimate]
ib = (0.8, 1.5)        # insulation barrel length [estimate, clone drawings]
OVERHANG = 9.0         # a1: fan block front face to tip [ribbon-as-pallet calc §2]
H_DROP = 5.0           # a1: neighbours held h ~ 5 mm above the anvil plane
fb = (3.0, 4.0)        # a1: finger acts 3-4 mm behind the insulation barrel
t_ibr = (cb[0] + gap[0] + ib[0], cb[1] + gap[1] + ib[1])
t_fin = (t_ibr[0] + fb[0], t_ibr[1] + fb[1])
free = (OVERHANG - t_fin[1], OVERHANG - t_fin[0])
print(f"tip to rear of insulation barrel: {t_ibr[0]:.2f}-{t_ibr[1]:.2f} mm")
print(f"tip to finger: {t_fin[0]:.2f}-{t_fin[1]:.2f} mm")
print(f"free conductor between fan block face and finger at a 9 mm overhang: {free[0]:.2f}-{free[1]:.2f} mm")
print(f"\nfree length an S-bend needs to drop {H_DROP} mm and come back level:")
for R in (2.0, 3.0, 5.0):
    row = []
    for th in (30, 45, 60, 90):
        row.append(f"{th:2d} deg: {s_bend_length(H_DROP, R, th):5.1f}")
    print(f"  R = {R:.0f} mm | " + " | ".join(row) + " mm")
L_need = s_bend_length(H_DROP, 5.0, 30)
L_tight = s_bend_length(H_DROP, 2.0, 60)
for name, L in (("R 5 mm, 30 deg (a1's own fan rule)", L_need), ("R 2 mm, 60 deg (harsh)", L_tight)):
    ov = (t_fin[0] + L, t_fin[1] + L)
    print(f"  {name}: overhang needed {ov[0]:.1f}-{ov[1]:.1f} mm -> "
          f"parted length grows by {ov[0]-OVERHANG:.1f}-{ov[1]-OVERHANG:.1f} mm over a1's 20-35 mm")
print("-> at a 9 mm overhang the finger acts 1-3.5 mm from the block face and cannot drop the")
print("   conductor 5 mm there. The block has to stand ~5-10 mm further back at the crimp station.")

print("\nSlope of the conductor at a single-point finger (no moment applied there):")
for L in (3.0, 6.0, 11.3, 15.0):
    el = atan(1.5 * H_DROP / L)            # elastic cantilever, point load at the end: slope = 3d/2L
    pl = atan(H_DROP / L)                  # plastic hinge at the block face, straight link
    lead = t_fin[0]                        # conductor ahead of the finger, down to the tip
    print(f"  free length {L:4.1f} mm: slope at finger {degrees(pl):4.1f} (hinge) to {degrees(el):4.1f} deg (elastic); "
          f"the tip would sit {lead*tan(pl):.1f}-{lead*tan(el):.1f} mm below the finger (it meets the anvil first)")
print("-> a point finger leaves the stripped tip pointing down into the box, not lying in the barrels.")
print("   Levelling needs a moment at the contact: a flat sole >= ~3 mm long along the conductor,")
print("   pressing it onto the carrier/shear-blade line, which lies in the contact's floor plane.")

# ---------------------------------------------------------------------------
hdr("2. a1 neighbours at crimp pitch 5 mm over the applicator's upstream side")
CP = 5.0
OPEN_HALF = (1.23, 1.50)   # open insulation barrel half-width [source, clone drawings]
BARE_HALF = 0.85
print("Neighbour conductor spans (x +/- 0.85) against waiting contacts on the strip (k*p_s +/- 1.23..1.50),")
print("both on the upstream side of the anvil, crimp pitch 5.0 mm:")
for ps in (6.8, 7.1, 8.0, 9.5):
    hits = []
    for j in range(1, 9):
        x = j * CP
        k = round(x / ps)
        near = [kk for kk in (k - 1, k, k + 1) if kk >= 1]
        clash = any(abs(x - kk * ps) < BARE_HALF + OPEN_HALF[1] for kk in near)
        hits.append("X" if clash else ".")
    print(f"  strip pitch {ps:3.1f} mm: neighbours 1..8 upstream  {' '.join(hits)}   (X = over a waiting contact)")
print("-> with neighbours in the anvil plane, some fall into waiting contacts at every plausible strip pitch,")
print("   so a1's h is needed on the upstream side.")
wing_h = (2.75, 3.20)
print(f"h to clear bare waiting contacts' wings ({wing_h[0]}-{wing_h[1]} mm) with 0.5 mm margin: "
      f"{wing_h[0]+BARE_HALF+0.5:.2f}-{wing_h[1]+BARE_HALF+0.5:.2f} mm")
for top in (3.0, 5.0, 8.0):
    print(f"h to clear a guide/pressure plate whose top is {top:.0f} mm above the strip [estimate]: {top+BARE_HALF+0.5:.1f} mm")
print("Free length the active conductor's S-bend needs as h rises (then add the 5.6-7.8 mm tip-to-finger):")
for hh in (4.3, 6.3, 9.3):
    print(f"  h {hh:.1f} mm: R 5 / 30 deg {s_bend_length(hh, 5.0, 30):5.1f} mm; R 2 / 60 deg {s_bend_length(hh, 2.0, 60):5.1f} mm")
print("Upstream neighbours per loom when every other conductor is on the upstream side (worst end of the row):")
for name, n in (("4P", 4), ("5P", 5), ("J1 5P+4P fanned as one", 9)):
    print(f"  {name}: up to {n-1} neighbours spread over X = 5..{CP*(n-1):.0f} mm upstream")
print("   The MKS-L's pressure plate, guide plates and feed finger sit on this side of the anvil")
print("   [mfr MKS-L manual pp. 9, 16-19; extent ~10-60 mm read from a photo, estimate].")

# ---------------------------------------------------------------------------
hdr("3. Feed timing: the next contact arriving while the crimped one is still on the anvil")
MP = 0.36          # N*mm plastic moment of the 60 x 0.08 bundle [ribbon-as-pallet calc §4]
for ps in (6.8, 7.1, 9.5):
    for lever in (6.0, 9.0):
        F = MP / lever
        ang = degrees(atan(ps / lever))
        print(f"  strip pitch {ps:3.1f}, lever {lever:.0f} mm from block to contact: yields at {F*1e3:.0f} mN; "
              f"pushed one pitch sideways -> {ang:.0f} deg permanent bend")
print("-> any feed finger (newtons [estimate]) wins. If the feed moves before the pallet has backed")
print("   the crimped contact off the anvil, the conductor is bent sideways 35-55 deg for good, or the")
print("   incoming contact's wings snag the crimped barrels and the feed jams. A hand-held wire yields")
print("   harmlessly; a pallet 6-9 mm back does not.")

# ---------------------------------------------------------------------------
hdr("4. What an applicator's own geometry guarantees about neighbours")
CL = 0.2
print("Upstream on the strip, one pitch from the anvil, a waiting contact stands open with 2.75-3.2 mm wings.")
print("So the tooling's lowest ~3 mm must fit inside (p_s - open half-width - clearance) on that side:")
for ps in (6.8, 7.1, 8.0, 9.5):
    lim = (ps - OPEN_HALF[1] - CL, ps - OPEN_HALF[0] - CL)
    print(f"  strip pitch {ps:3.1f}: tooling half-width at the wings <= {lim[0]:.2f}-{lim[1]:.2f} mm "
          f"(plates <= {2*lim[0]:.1f}-{2*lim[1]:.1f} mm)")
print("Neighbour in the anvil plane at a1's 5.0 mm crimp pitch needs:")
print(f"  bare conductor: half-width <= {5.0-BARE_HALF-CL:.2f} mm; crimped contact (1.03 half): <= {5.0-1.03-CL:.2f} mm")
print("-> an applicator's tooling is narrow enough, by its function, for neighbours at ONE STRIP PITCH")
print("   on the upstream side (a2's docked row). Nothing about its function guarantees 5 mm (a1).")

# ---------------------------------------------------------------------------
hdr("5. a2: the 0.2 mm tab as the contact's only support, and the gang shear")
E = 110e3                         # MPa, phosphor bronze
for sy in (450.0, 650.0):         # [estimate] C5191 spring temper yield
    for b in (0.8, 1.0):          # tab width [estimate from clone drawings]
        t = 0.20
        My = sy * b * t ** 2 / 6
        Mp = 1.5 * My
        I = b * t ** 3 / 12
        th_y = My * 0.8 / (E * I)             # rotation over a 0.8 mm tab at first yield
        print(f"  sy {sy:.0f} MPa, tab {b:.1f} x {t:.2f}: first yield {My:.2f} N*mm (full plastic {Mp:.2f}); "
              f"vertical force to yield at the barrels (2.5 mm) {My/2.5:.2f} N, at the box (5 mm) {My/5:.2f} N; "
              f"elastic lift at 3 mm before yield {th_y*3*1e3:.0f} um")
print("-> the head's lower jaw has ~0.05-0.1 mm of Z window before it bends a tab for good.")
print("   Its Z must come from the strip pallet (a rail flush with the contact floor), not the carriage.")
shear = (50.0, 160.0)            # N per tab [xh-facts calc C1 §4]
for n in (3, 4, 5):
    print(f"  shearing {n} tabs at once: {n*shear[0]:.0f}-{n*shear[1]:.0f} N; each contact must be clamped on a die")
    print(f"    edge at its rear, because {shear[0]:.0f}-{shear[1]:.0f} N at 1-3 mm is 20-200x the tab's own yield moment")

# ---------------------------------------------------------------------------
hdr("6. a2 / a2d: a scissor or ratchet tool's jaw runs along the row")
print("The die axis is normal to the jaw plane, so with contacts along Y and crimping in Z the jaw lies")
print("along X, the row direction. Neighbours at strip pitch inside the jaw's reach toward its pivot:")
for ps in (7.1, 14.2):
    for J in (10, 15, 20, 30):
        n = floor((J + OPEN_HALF[1]) / ps)
        print(f"  pitch {ps:4.1f} mm, nest-to-pivot jaw extent {J:2d} mm: {n} neighbour(s) under or over the jaw")
print("-> cutting the jaw down to its XH nest removes the far side, not the pivot side. A cut-down")
print("   SN-2549 reaches every contact of a row only if the neighbours on its pivot side are gone.")

# ---------------------------------------------------------------------------
hdr("7. a3: height above the board with the backshell at the split root")
MATED = 9.8       # housing on the header [mfr, xh-facts §3]
BS = 12.0         # backshell length along the loom [ribbon-as-pallet a3]
for name, pl in (("fold-back parking (b1)", (8, 15)), ("housing fan only", (14, 18)),
                 ("a2, 7 mm strip pitch, per ribbon", (21, 30)), ("a1, 5 mm crimp pitch", (20, 35))):
    print(f"  {name:34s}: parted {pl[0]}-{pl[1]} mm -> top of backshell {MATED+pl[0]+BS:.0f}-{MATED+pl[1]+BS:.0f} mm above the board")

# ---------------------------------------------------------------------------
hdr("8. a3: grip by a 180 deg wrap (the IDC strain-relief fold) instead of ridges")
for mu in (0.3, 0.5, 0.8, 1.0):
    g = exp(mu * pi)
    print(f"  mu {mu:.1f}: capstan gain e^(mu*pi) = {g:5.1f}; a clip holding 3 N on the tail resists {3*g:5.0f} N")
A_si = pi / 4 * (1.7 ** 2 - 0.72 ** 2) + 0.2    # jacket plus a share of web [estimate]
print(f"silicone per conductor ~{A_si:.1f} mm^2 x 8-11 MPa = {A_si*8:.0f}-{A_si*11:.0f} N; "
      "the 22 AWG copper breaks at ~85-100 N [source]")
print("-> a fold over a bar with a snap cover reaches tens of newtons at low clamp pressure; bite ridges")
print("   need high local pressure on a material that tears at 15-25 N/mm.")

# ---------------------------------------------------------------------------
hdr("9. In-line crimp height: frame stretch read from the force peak")
for k in (13.0, 23.0, 39.0):      # kN/mm, O-frame cases from presses.py §2
    dF = 0.15 * 2.0               # kN, +/-15 % of a typical 2 kN peak (as presses.py §2)
    res = 0.03                    # kN, ~1 % of range as a usable HX711 resolution [estimate]
    print(f"  frame {k:4.0f} kN/mm: +/-15 % force -> +/-{dF/k*1e3:4.1f} um of crimp height; "
          f"30 N resolution -> {res/k*1e3:.1f} um")
print("-> geometry fixes where the ram would stop; stretch under the actual peak moves it. Peak force")
print("   over frame stiffness gives each crimp's height deviation, once a micrometer sets the baseline.")

# ---------------------------------------------------------------------------
hdr("10. Force samples in the last 0.2 mm: lever press, bought press, crank")
STROKE = 30.0
for T, kind in ((0.5, "bought press, linear approx"), (1.5, "hand lever, linear"), (10.0, "linear drive, 10 s")):
    t = 0.2 / STROKE * T
    print(f"  {kind:28s}: {t*1e3:5.1f} ms in the last 0.2 mm -> {80*t:4.1f} HX711 samples at 80 Hz")
print("  crank, 10 s per turn (presses.py §1b): 243 ms -> 19.4 samples; 20 s -> 38.8")
print("-> a1's stroke trace and a1b's lever press see a force curve only if the bottom of the stroke")
print("   is slow; a crank's dwell at BDC gives ~3.6x the time of a linear stroke of the same period.")

# ---------------------------------------------------------------------------
hdr("11. a2b: what a single load reading sees in a gang stroke")
peak = (0.8, 2.6)     # kN per contact [xh-facts §4]
curl = (0.05, 0.3)    # kN wing curl without a conductor [xh-facts §4]
for n in (3, 4, 5, 9):
    lo = (peak[0] - curl[1]) / (n * peak[0])
    hi = (peak[1] - curl[0]) / (n * peak[1])
    print(f"  {n} contacts: missing conductor drops the total {100*min(lo,hi):.0f}-{100*max(lo,hi):.0f} %; "
          f"missing contact {100/n:.0f} %; one strand of 60 {1.7/n:.2f} %")
print("-> a load cell under the die set sees a missing wire or contact against a +/-4 % band;")
print("   the camera says which; strands stay invisible to force.")
