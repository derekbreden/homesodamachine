"""procedure-is-the-machine on ribbon-as-pallet, wave 3: numbers for the exchange file
../../../exchange/procedure-is-the-machine--on--ribbon-as-pallet-w3.md

Run:  python3 exchange_ribbon_w3.py > exchange_ribbon_w3.out.txt

Labels: [source]/[mfr] as cited in ../../../context/xh-facts.md; [estimate] and
[assumption] are mine. Nothing here was measured. The fan S-bend rule (R 5 mm, 30 deg)
is ribbon-as-pallet's own (their calc/stations_wave2.py section 3), copied so the numbers
are comparable with theirs.
"""
from math import pi, sqrt, sin, cos, acos, asin, atan, radians, degrees

RIB = 1.7          # conductor pitch = OD [source S29]
XH = 2.5           # housing pitch [mfr S1]
BUNDLE = (0.69, 0.74)   # strand bundle dia [calc C1]
OD = (1.6, 1.8)    # 1.7 +/- 0.1 [source S29]
T_STOCK = 0.20     # contact stock [source S19-S21]


def hdr(t):
    print()
    print("=" * 88)
    print(t)
    print("=" * 88)


def s_bend(delta, R=5.0, th_deg=30.0):
    """ribbon-as-pallet's fan rule: two arcs R and a straight at theta. (axial, path)."""
    delta = abs(delta)
    if delta == 0:
        return 0.0, 0.0
    th = radians(th_deg)
    d_arc = 2 * R * (1 - cos(th))
    if delta <= d_arc:
        t = acos(1 - delta / (2 * R))
        return 2 * R * sin(t), 2 * R * t
    s = (delta - d_arc) / sin(th)
    return 2 * R * sin(th) + s * cos(th), 2 * R * th + s


def offsets(n, pitch):
    return [(i - (n - 1) / 2) * (pitch - RIB) for i in range(n)]


def s_profile(delta, L, R=5.0, th_deg=30.0, npts=4000):
    """y(x) samples of the S-bend of lateral move delta, then straight to x = L."""
    th = radians(th_deg)
    pts = []
    d = abs(delta)
    if d == 0:
        return [(L * i / npts, 0.0) for i in range(npts + 1)]
    d_arc = 2 * R * (1 - cos(th))
    if d <= d_arc:
        t = acos(1 - d / (2 * R))
        s_len = 0.0
    else:
        t = th
        s_len = (d - d_arc) / sin(th)
    # parametric by arc length
    seg = []
    # arc 1: centre (0, R), angle 0..t
    for k in range(400):
        a = t * k / 400
        seg.append((R * sin(a), R * (1 - cos(a))))
    x1, y1 = R * sin(t), R * (1 - cos(t))
    for k in range(400):
        u = s_len * k / 400
        seg.append((x1 + u * cos(t), y1 + u * sin(t)))
    x2, y2 = x1 + s_len * cos(t), y1 + s_len * sin(t)
    for k in range(401):
        a = t * k / 400
        seg.append((x2 + R * sin(t) - R * sin(t - a), y2 + (R * (1 - cos(t)) - R * (1 - cos(t - a)))))
    xe, ye = seg[-1]
    xs = [p[0] for p in seg]
    ys = [p[1] for p in seg]
    out = []
    j = 0
    for i in range(npts + 1):
        x = L * i / npts
        if x >= xe:
            out.append((x, ye))
            continue
        while j < len(xs) - 2 and xs[j + 1] < x:
            j += 1
        f = (x - xs[j]) / max(xs[j + 1] - xs[j], 1e-12)
        out.append((x, ys[j] + f * (ys[j + 1] - ys[j])))
    return out


def path_len(prof, H=0.0, L=None):
    """length of (x, y(x), z(x)) with z a full cosine hump of height H over [0, L]."""
    if L is None:
        L = prof[-1][0]
    tot = 0.0
    for (xa, ya), (xb, yb) in zip(prof[:-1], prof[1:]):
        za = H / 2 * (1 - cos(2 * pi * xa / L))
        zb = H / 2 * (1 - cos(2 * pi * xb / L))
        tot += sqrt((xb - xa) ** 2 + (yb - ya) ** 2 + (zb - za) ** 2)
    return tot


# ---------------------------------------------------------------------------------------
hdr("1. Equal-path fan: grooves of equal length so tips and strip lines stay on one line")
print("ribbon-as-pallet's fan rule (R 5 mm, 30 deg S, then straight), each ribbon fanned alone.")
print("Every groove spans the outer conductor's axial length L_f. An inner groove gets a")
print("vertical cosine hump of height H over the whole L_f (overlapping its own lateral S) so")
print("its path equals the outer one's. Then a flush cut and strip made before the fan stay on")
print("one line after it; every tip recedes by the same r_max, which the split must allow.")
for pitch in (2.5, 5.0, 7.1):
    for n in (3, 4, 5):
        offs = offsets(n, pitch)
        Lf = max(s_bend(o)[0] for o in offs)
        profs = [s_profile(o, Lf) for o in offs]
        paths = [path_len(p) for p in profs]
        pmax = max(paths)
        rmax = pmax - Lf
        cells = []
        for o, prof, p in zip(offs, profs, paths):
            if o < 0:
                continue
            need = pmax - p
            if need < 1e-4:
                cells.append(f"offset {o:.1f}: 0")
                continue
            lo, hi = 0.0, 20.0
            for _ in range(60):
                mid = (lo + hi) / 2
                if path_len(prof, mid, Lf) < pmax:
                    lo = mid
                else:
                    hi = mid
            H = (lo + hi) / 2
            Rmin = Lf ** 2 / (2 * pi ** 2 * H)
            cells.append(f"offset {o:.1f}: +{need:.2f} mm -> hump {H:.1f} mm, R_min {Rmin:.1f}")
        print(f"  {n}P at {pitch:3.1f} mm: L_f {Lf:5.1f} mm, all tips recede {rmax:4.2f} mm | " + "; ".join(cells))
print("-> at 7.1 mm strip pitch a 5P's centre groove needs a ~5.1 mm hump over ~21 mm, bent at")
print("   ~R 4.5, near the fan rule's own R 5. At 5 mm a ~3.2 mm hump; at 2.5 mm under 1 mm. The")
print("   hump costs fan-block height and leaves the same class of set the S-bends already leave.")
print()
print("How much the fan's shape matters (outer conductor recession, lateral move delta):")
for n, pitch, L in ((5, 2.5, 8.0), (5, 2.5, 15.0), (5, 7.1, 21.0), (5, 7.1, 30.0), (4, 2.5, 15.0)):
    d = abs(offsets(n, pitch)[0])
    a, p = s_bend(d)
    ax_their = a
    rec_their = p - a
    # gentle cosine S over the whole length L
    tot = 0.0
    N = 4000
    for i in range(N):
        xa, xb = L * i / N, L * (i + 1) / N
        ya = d / 2 * (1 - cos(pi * xa / L))
        yb = d / 2 * (1 - cos(pi * xb / L))
        tot += sqrt((xb - xa) ** 2 + (yb - ya) ** 2)
    rec_gentle = tot - L
    rec_diag = L - sqrt(L * L - d * d)
    print(f"  {n}P to {pitch} mm (delta {d:.2f}) over {L:4.1f} mm: compact R5/30 S {rec_their:.2f} mm "
          f"(S itself {ax_their:.1f} mm long); gentle S over the whole length {rec_gentle:.2f} mm; "
          f"straight diagonal {rec_diag:.2f} mm")
print("-> ribbon-as-pallet's 0.31 mm (5P at 2.5 mm) is the compact S; this explorer's wave-2")
print("   0.09-0.16 mm (exchange_borrowed §7) is the straight diagonal over the split. Both are")
print("   right for their shapes; the groove shape is a design choice that sets the recession.")

# ---------------------------------------------------------------------------------------
hdr("2. Docking capture: how much lateral room the open barrels really give")
print("Clone drawings: conductor barrel open W 1.68-1.90, insulation barrel open W 2.46-3.00,")
print("each +/-0.25 [source S19-S22]; JST catalog end-view envelope 1.95 x 2.4 [mfr S1].")
print("Whether a drawn width is the inside opening or the outside of the wings is not stated.")
for name, (wlo, whi), (olo, ohi) in (("conductor barrel / strands", (1.68, 1.90), BUNDLE),
                                     ("insulation barrel / jacket", (2.46, 3.00), OD)):
    for reading, sub in (("drawn = inside", 0.0), ("drawn = outside", 2 * T_STOCK)):
        nom = ((wlo + whi) / 2 - sub - (olo + ohi) / 2) / 2
        worst = (wlo - 0.25 - sub - ohi) / 2
        print(f"  {name:28s} {reading:16s}: half-gap nominal {nom:+.2f} mm, worst (min W - tol, max OD) {worst:+.2f} mm")
jst_inside = 1.95 - 2 * T_STOCK
print(f"  JST 1.95 mm envelope read as open insulation wings: inside {jst_inside:.2f} mm against a 1.7 mm jacket"
      f" -> {(jst_inside-1.7)/2:+.2f} mm (interference; the jacket must be pressed in)")
fan, seat, stamp, lean, groove = 0.10, 0.02, 0.05, 0.10, 0.05
rss = sqrt(fan ** 2 + seat ** 2 + stamp ** 2 + lean ** 2 + groove ** 2)
print(f"  placement error [estimates]: fan block {fan}, seat {seat}, stamping {stamp}, tip lean at 9 mm {lean},"
      f" conductor in groove {groove} -> worst {fan+seat+stamp+lean+groove:.2f}, RSS {rss:.2f} mm")
print("-> a2's '+/-0.5 mm, five times the placement error' holds at the clone drawings' nominal read")
print("   as inside widths. Read as outside widths at the low tolerance the jacket's capture falls to")
print("   ~0.1 mm or below, under the RSS placement error. The $4.71 strip measures which.")

# ---------------------------------------------------------------------------------------
hdr("3. a2e's proof pull against a carrier held only by two end grips")
print("A pull on conductor k (-Y, toward the carrier side) pushes contact k's tab against the")
print("carrier edge: an in-plane point load on the carrier strip, which spans between the grips on")
print("the outermost spares. Carrier width unmeasured [assumption 2.5-4.0 mm], 0.20 mm thick,")
print("E 110 GPa, C5191 yield ~450-650 MPa [assumption, as borrowed-machines calc X §5]; the pilot hole at k")
print("reduces the section further (not counted).")
E = 110000.0
P = 20.0
for n in (3, 4, 5):
    for ps in (7.1,):
        L = (n + 3) * ps
        for w in (2.5, 3.0, 4.0):
            I = T_STOCK * w ** 3 / 12
            c = w / 2
            d_ss = P * L ** 3 / (48 * E * I)
            s_ss = (P * L / 4) * c / I
            d_ff = P * L ** 3 / (192 * E * I)
            s_ff = (P * L / 8) * c / I
            print(f"  {n}P, grips {L:4.1f} mm apart, carrier {w} mm wide: pinned ends {d_ss:5.2f} mm / {s_ss:5.0f} MPa;"
                  f" fixed ends {d_ff:4.2f} mm / {s_ff:4.0f} MPa")
Ls = 7.1
for w in (2.5, 3.0):
    I = T_STOCK * w ** 3 / 12
    print(f"  with slot pins at +/-3.55 mm (a2's strip pallet), {w} mm carrier: fixed ends "
          f"{P*Ls**3/(192*E*I)*1000:.0f} um / {(P*Ls/8)*(w/2)/I:.0f} MPa")
print("-> with end grips only, a 20 N pull on a middle contact bends a 2.5-3 mm carrier 0.2-2.7 mm")
print("   at 350-1360 MPa, at or past yield on 4P and 5P rows; the conductor moves with its contact,")
print("   so the pull does not isolate")
print("   the crimp. Slot pins at every slot, or a blade in each contact's neck (pull through the")
print("   box), carry it.")

# ---------------------------------------------------------------------------------------
hdr("4. a2e: how far the row runs past the anvil")
for n in (3, 4, 5):
    for ps in (6.8, 7.1):
        crimped = (n - 1) * ps
        spares = (n + 1) * ps
        print(f"  {n}P at {ps}: last real contact on the anvil -> crimped ones to {crimped:4.1f} mm downstream,"
              f" the two leading spares and their grip to {spares:4.1f} mm")
print("-> a2e's 'up to four strip pitches (28 mm for a 5P)' counts the crimped contacts only; the")
print("   leading spares and the end grip reach ~43 mm past the anvil for a 5P.")

# ---------------------------------------------------------------------------------------
hdr("5. a2e's press: the applicator's standard crank against a short eccentric")
print("With the feed removed, the ram only has to lift its crimper legs clear of the next open")
print("contact's wings (2.75-3.2 mm) plus margin. Force model [estimate, digest]: compaction")
print("F_peak falling linearly to 0 over the last dc mm; 300 N of wing curl from 0.2 to 0.9 mm;")
print("ram return spring F_s acting throughout. Torque = F x throw x sin(theta) (rod obliquity")
print("ignored). 10 s per revolution, HX711 at 80 Hz.")
def torque_max(e, Fp, dc, Fs):
    best = 0.0
    for k in range(1, 18000):
        th = pi * k / 18000
        h = e * (1 - cos(th))           # height above BDC
        F = Fs
        if h < dc:
            F += Fp * (1 - h / dc)
        if 0.2 <= h < 0.9:
            F += 300.0
        best = max(best, F * e * sin(th))
    return best
for e in (3.0, 4.0, 15.0, 20.0):
    for Fp, dc in ((2600.0, 0.15), (3000.0, 0.2)):
        for Fs in (100.0, 300.0):
            T = torque_max(e, Fp, dc, Fs)
            th02 = acos(1 - 0.2 / e)
            samples = th02 / (2 * pi) * 10 * 80
            print(f"  throw {e:4.1f} mm (stroke {2*e:4.1f}), F_peak {Fp/1000:.1f} kN over {dc} mm, spring {Fs:.0f} N:"
                  f" peak torque {T/1000:5.2f} N*m; samples in last 0.2 mm {samples:4.0f}")
print("  Prime row 86: STEPPERONLINE NEMA 17 + 26.85:1 planetary, 3 N*m permissible, 5 N*m momentary.")
print("  Prime row 85: NEMA 23 planetary 10:1, 10 N*m permissible (motor not included).")
print("-> a 3-4 mm eccentric needs ~1.0-1.7 N*m, inside a NEMA 17 planetary's 3 N*m; a 15-20 mm crank")
print("   needs ~2.2-6 N*m, set mostly by the return spring. The shorter throw also roughly doubles the")
print("   samples through compaction. Shut height is then set once by the eccentric's bearing blocks.")

# ---------------------------------------------------------------------------------------
hdr("6. A pilot in the carrier slot beside the anvil contact")
for ps in (6.8, 7.1):
    slot_x = ps / 2
    pilot_r = 0.6
    clear = ps - slot_x - RIB / 2 - pilot_r
    print(f"  strip pitch {ps}: slot centre {slot_x:.2f} mm from the anvil contact; a 1.2 mm pilot clears the"
          f" neighbouring conductor by {clear:.2f} mm (both sides)")
print("  pilot must lead the crimpers: reach the carrier plane before the insulation crimper meets")
print("  the wing tips (2.75-3.2 mm) -> protrude >= ~3.5 mm below the crimper faces, with a relief")
print("  under the carrier where the removed shear blade sat [assumption: OTP laid out like MKS-L].")
for kf in (1.0, 3.0):
    F = kf * 0.3 + 0.5
    print(f"  float spring {kf} N/mm, correction 0.3 mm, friction 0.5 N: {F:.1f} N on a 0.2 mm slot edge"
          f" over ~0.3 mm -> {F/(0.2*0.3):.0f} MPa bearing")

# ---------------------------------------------------------------------------------------
hdr("7. The person's minutes: ribbon-as-pallet arrangements, and the reel-end docking bench")
T = {"cut": 20, "peel": 40, "strip": 8, "hcrimp": 15, "insert": 8, "test": 30,
     "load_pallet": 30,          # lay end in pallet, close lid, far end into pogo block
     "hand_prep": 83,            # a1b seats: zip 15, fan 10, flush cut 8, a8 bench strip 30, 4 moves 20
     "dock": 42,                 # a2e: snip + lay strip 20, seat 10, start 2, lift off 10
     "a1b_crimp": 17,            # detent + push 5, lever with pause 8, draw back 4
     "insert_end": 45,           # a6 by hand: swap block 15, clamp + push 20, look 10
     "pair": 20, "cross": 60, "label": 20, "transfer": 10}
N_END, N_CR, N_H = 14, 53, 10
rows = []
today = N_END * (T["cut"] + T["peel"]) + N_CR * (T["strip"] + T["hcrimp"] + T["insert"]) + N_H * T["test"]
rows.append(("today, by hand (wave-2 task library)", today, 0, 0))
a1b = (N_END * (T["cut"] + T["load_pallet"] + T["hand_prep"] + T["insert_end"]) + N_CR * T["a1b_crimp"]
       + 4 * T["pair"] + 2 * T["cross"] + N_H * T["test"])
rows.append(("a1b hand shuttle, applicator on the jack", a1b, 0, 0))
a2e_hand = (N_END * (T["cut"] + T["load_pallet"] + T["hand_prep"] + T["dock"] + T["insert_end"])
            + 4 * T["pair"] + 2 * T["cross"] + N_H * T["test"])
m_end = (4 * 1.6 + 7 * 1.8 + 3 * 2.1) / 14 * 60   # ribbon-as-pallet calc W2 §8, mix of ends
rows.append(("a2e, prep at a1b seats, hand insertion", a2e_hand, m_end, N_END))
a2e_stage = (N_END * (T["cut"] + T["load_pallet"] + T["transfer"] + T["dock"] + T["insert_end"])
             + 4 * T["pair"] + 2 * T["cross"] + N_H * T["test"])
rows.append(("a2e, prep on a1's stage, hand insertion", a2e_stage, m_end, 2 * N_END))
a1 = N_END * (T["cut"] + T["load_pallet"] + 15) + 2 * T["cross"] + N_H * T["label"]
rows.append(("a1 pallet tour (their calc §10: ~156 min machine)", a1, 156 * 60 / N_END, N_END))
# reel-end docking bench (X1): per-reel runs, contacts from reel, singles housed by machine
# rewinds (3 spools per 5 units, ~6 min each), reel-run upkeep, J1/J2 half-housed housings placed
# in the nest (machine inserts the second ribbon), J4/J7 first ribbon machine-inserted through a
# gapped closing block, the second ribbon's crossing contacts (J4 3, J7 2) inserted by hand
reel = (3 / 5 * (300 + 60) + 60 + 2 * 20 + (20 + T["cross"] + 3 * T["insert"])
        + (20 + T["cross"] + 2 * T["insert"]) + N_H * T["label"])
rows.append(("X1 reel-end docking bench (per-reel runs)", reel, 5.4 * 7 * 5.5 * 60, 7))
print(f"{'arrangement':<52}{'person min':>11}{'alone per call':>16}{'calls':>7}")
for name, p, alone, calls in rows:
    a = "-" if alone == 0 else (f"{alone/60:.1f} min" if alone < 3600 else f"{alone/3600:.1f} h")
    print(f"{name:<52}{p/60:>11.0f}{a:>16}{calls:>7}")
print()
print("Rhythm check for a2e with hand prep (p4b's rule): per end the machine runs")
print(f"  ~{m_end:.0f} s; the person's work that can overlap it (cut, load, prep the next end, insert the")
print(f"  previous one) is ~{T['cut']+T['load_pallet']+T['hand_prep']+T['insert_end']:.0f} s. The person sets the pace; the machine waits.")
print("Reading: the crimp is a small share of the person's time in every ribbon-as-pallet row.")
print("What sets minutes is who carries and prepares pallets and who inserts. Durations are")
print("[estimate]; compare rows, not absolute minutes. X1's 'alone' is one 4P reel run (35 ends,")
print("~5.5 min each [estimate]); its ~7 calls a unit are ~3 reel runs (amortised) and 4 pair events")
print("at the partner nest (J1, J2 placed; J4, J7 placed plus 5 crossing contacts inserted by hand).")

# ---------------------------------------------------------------------------------------
hdr("8. a8b's head at 5 mm crimp pitch (a1, a1c, a4)")
for pitch in (5.0, 2.5):
    edge = pitch - RIB / 2
    snout = 2 * (edge - 0.25)
    print(f"  pitch {pitch}: neighbour's jacket edge {edge:.2f} mm from k's axis -> a snout at most {snout:.1f} mm across,"
          f" reaching >= ~6 mm ahead of the 15 mm (6700) bearing section")
print("  otherwise k is lifted clear: h >= bearing radius 7.5 + 0.85 + margin ~ 9 mm; residual rise")
print("  at h 8 mm is 2.1-5.6 mm at 20 mm free, 0.3-3.6 mm at 25 mm [calc wave2 §1(b)].")

# ---------------------------------------------------------------------------------------
hdr("9. Spool curl on the protrusion a zip station needs (35-50 mm past the clamp)")
for hub, (rlo, rhi) in ((25, (55.0, 242.0)), (35, (118.0, 7141.0)), (50, (438.0, 1e9))):
    cells = []
    for L in (35.0, 50.0):
        lo = rhi - sqrt(max(rhi * rhi - L * L, 0))
        hi = rlo - sqrt(max(rlo * rlo - L * L, 0)) if rlo > L else rlo
        cells.append(f"{L:.0f} mm rises {lo:4.1f}-{hi:4.1f} mm")
    print(f"  hub radius {hub} mm (residual curl radius {rlo:.0f}-{'inf' if rhi > 1e8 else f'{rhi:.0f}'} mm, "
          f"calc wave2 §2): " + "; ".join(cells))
print("-> a7's nicker V-noses sit just above and below a 1.7 mm ribbon; off a 25 mm hub the tip is")
print("   2.5-32 mm out of plane and misses them.")
print("   A guide over the protrusion up to the nicker, a roller straightener, or an")
print("   80 mm-hub rewind (no new set) keeps it in plane.")

# ---------------------------------------------------------------------------------------
hdr("10. Closing the fan for insertion: excess length and where it goes")
for n in (4, 5):
    for pitch in (5.0, 7.1):
        oc, oh = offsets(n, pitch), offsets(n, XH)
        exc = []
        for a, b in zip(oc, oh):
            ra = s_bend(a)[1] - s_bend(a)[0]
            rb = s_bend(b)[1] - s_bend(b)[0]
            exc.append(ra - rb)
        top = max(exc)
        second = sorted(set(round(x, 2) for x in exc))[-2]
        bows = ", ".join(f"{sqrt(4*L*top)/pi:.1f} mm over {L:.0f}" for L in (5.0, 10.0, 20.0))
        print(f"  {n}P from {pitch} to 2.5 mm: outer +{top:.2f}, next +{second:.2f} mm; if the fronts are forced"
              f" to one line the outer bows {bows} mm of free span")
print("   (gap between jackets at 2.5 mm pitch: 0.8 mm)")
print("-> 'a slight bow' is 1.5-5 mm for a 5P closed from strip pitch. Left free, the same excess is a")
print("   V staircase: outer contacts ~2.5 mm ahead, the next ~1.2 mm, the centre last.")

# ---------------------------------------------------------------------------------------
hdr("11. Contacts per unit and strip lots")
conductors = 55   # 53 crimped + J2 and J7 trimmed positions
for spares, label in ((4, "N+4 (a2e, grips on spare contacts)"), (2, "N+2 (a2)"), (0, "N+0 (grips in the carrier's end slots)")):
    per_unit = conductors + N_END * spares
    print(f"  {label:40s}: {per_unit:3d} contacts per unit; 100-piece strips per unit {per_unit/100:.2f};"
          f" 8,000 reel ~{8000/per_unit:.0f} units; at $0.0235 ${per_unit*0.0235:.2f}/unit")

# ---------------------------------------------------------------------------------------
hdr("12. X1: a redo at the reel clamp costs the whole parted end, not 6 mm")
cut = 35.0  # parted 24-33 mm at 7.1 mm (incl. equal-path recession) + contact ~6 mm [estimate]
for p in (0.005, 0.02, 0.05):
    ends = {3: 4, 4: 7, 5: 3}
    e_mm = sum(cnt * (1 - (1 - p) ** n) * cut for n, cnt in ends.items())
    print(f"  per-crimp failure {p*100:.1f} %: ~{e_mm:4.1f} mm of reel per unit ({e_mm/6000*100:.2f} % of ~6.0 m)")
print("-> a failed crimp is cut off at the clamp face with its whole split and started again; the")
print("   loom is not yet cut, so no loom is lost.")
