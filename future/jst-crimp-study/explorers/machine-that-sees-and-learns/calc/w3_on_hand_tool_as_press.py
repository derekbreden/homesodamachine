"""Wave-3 exchange numbers: machine-that-sees-and-learns on hand-tool-as-press.

Run: python3 w3_on_hand_tool_as_press.py > w3_on_hand_tool_as_press.out.txt

Sections
  1. a1b: the proof pull with the dies re-closed "a few newtons" on the crimped barrels
  2. a1b: where the force wall lives when the stroke goes through a hand tool's linkage
  3. a2 / a2b / a3: the side-entry stand-out with crimped neighbours and a clearance
  4. Strip length against conductor-barrel length: JST 2.4 mm and the clone 1.6-2.1 mm
  5. a5: a 1.8 mm-thick PA-09 die over the conductor barrel, and where the excess goes
  6. a4: eccentric torque once frame stretch and disc-spring preload set the die-contact angle
  7. W1 (v8 tack station + a4 one-nest die set): room between lifted neighbours, passage, stroke
  8. W2 (v8 tack station + a6 foot-closed SN-2549): jaw opening and pedal travel, person time
  9. The closed insulation barrel's height: ellipse against a squarer section
 10. a3: slide-on capture against where a pulled-out tip actually is

Labels: [calc] computed here; [estimate]; [assumption]; others cite their source.
htp = hand-tool-as-press; ith = into-the-housing; ff = force-and-form; rap = ribbon-as-pallet.
Contact dimensions are the clone-drawing readings in context/xh-facts.md section 1.
"""
import math


def head(n, title):
    print()
    print("=" * 78)
    print(f"{n}. {title}")
    print("=" * 78)


# ---------------------------------------------------------------------------
head(1, "a1b: proof pull with the dies re-closed on the crimped barrels")
# a1b: "the pusher closes again until the force rises a few newtons on the crimped barrels".
# The load cell is at the grip, so a grip-side rise is multiplied by the end-of-stroke gain.
gains = (15, 30, 40)              # htp calc s1, [assumption] 15-40
grip_rise = (2.0, 5.0)           # "a few newtons" at the grip
mus = (0.15, 0.3, 0.5)           # die-on-tin friction, htp exchange_procedure s3 uses 0.15-0.5
print("held die force = grip rise x gain; extra grip on the strands ~ mu x held die force")
print("(htp calc/exchange_procedure.out.txt s3: 50 N held -> 8-25 N, 200 N -> 30-100 N)")
for g in grip_rise:
    for G in gains:
        F = g * G
        fr = [m * F for m in mus]
        print(f"  grip rise {g:3.1f} N x gain {G:2d} = {F:5.0f} N at the dies -> extra grip "
              f"{fr[0]:4.0f} / {fr[1]:4.0f} / {fr[2]:4.0f} N at mu 0.15 / 0.3 / 0.5   vs a 20 N proof")
print("For the re-closure to add no more than 2 N (10 % of a 20 N proof):")
for m in mus:
    Fmax = 2.0 / m
    print(f"  mu {m:4.2f}: held die force <= {Fmax:4.1f} N -> at the grip <= "
          f"{Fmax/40:4.2f}-{Fmax/15:4.2f} N (gain 40-15)")
print("What the grip can resolve [estimate]: HX711 on a 50 kg S-cell ~0.05-0.2 N of noise;")
print("the empty-tool curve (return spring, pawl, pins) repeats to perhaps +/-0.5-1 N at the grip.")
for G in (15, 40):
    print(f"  gain {G}: +/-0.5-1 N at the grip = +/-{0.5*G:3.0f}-{1.0*G:3.0f} N of unknown die force")
print("-> a grip-side 'few newtons' is 30-200 N at the dies; a crimp with little grip of its own")
print("   passes a 20 N pull by die friction. The re-closure cannot be set light enough from the")
print("   grip to keep the test honest.")
print()
print("Position hold instead (dies stopped short of the barrels, pull reacts on the jaw face):")
box = 2.0
for t in (0.2, 0.35, 0.5):          # transition box rear -> conductor-barrel front [ith ex s1 estimate]
    for lt in (2.24, 2.64):         # lance tip from the nose, CJT 2.44 +/- 0.20 [ith ex s1]
        lance_vs_face = (lt - box) - t      # + = behind the face (over the die), - = in front
        box_travel = t                      # box rear shoulder travel to the face
        if lance_vs_face < 0:
            first = "lance tip meets the face first" if -lance_vs_face < box_travel else "box shoulder first"
            print(f"  transition {t:.2f}, lance tip {lt:.2f}: tip {-lance_vs_face:.2f} mm in front of the "
                  f"face, box shoulder {box_travel:.2f} mm away -> {first}")
        else:
            print(f"  transition {t:.2f}, lance tip {lt:.2f}: tip {lance_vs_face:.2f} mm behind the face, "
                  f"so it hangs in a relief in the anvil; a -Y pull carries it along the relief, and what "
                  f"meets steel first depends on the relief's rear end")
print("-> with the dies open to a position, the lance, not the box, meets steel first wherever the")
print("   tip hangs in front of the anvil face, and at best ties with an unknown relief otherwise.")
print("   The pull belongs on a backed plate on the box's rear walls with the lance relieved.")


# ---------------------------------------------------------------------------
head(2, "a1b: where the force wall lives when the stroke goes through a hand tool")
v_grip = 2.0                   # mm/s at the grip [htp calc s3]
print(f"grip speed {v_grip} mm/s [htp calc s3]; die speed = grip speed / gain")
for G in (3, 6, 15, 30, 40):
    print(f"  gain {G:2d}: die moves {v_grip/G*1000:5.0f} um/s; HX711 at 80 SPS -> "
          f"{v_grip/G/80*1000:5.2f} um of die per sample")
print("-> near closure (gain 15-40) the die already crawls at 0.05-0.13 mm/s, which is v7's")
print("   crawl; a hand tool gives the slow approach to compaction for free.")
print()
print("Overshoot past a force wall, a1b (no ratchet, dies meet face to face):")
print("grip-side stiffness after die contact k_g = 1/(1/k_h + G^2/k_d)")
print("k_h handles + pins + cradle 20-100 N/mm [estimate]; k_d die loop 5-30 kN/mm [estimate]")
rows = []
for G in (15, 40):
    for kh in (20.0, 100.0):
        for kd in (5000.0, 30000.0):
            kg = 1.0 / (1.0 / kh + G * G / kd)
            rows.append((G, kh, kd, kg))
for lat, name in ((0.0125, "MCU, one HX711 sample"), (0.03, "Mac, typical USB round trip"),
                  (0.5, "Mac, bad moment")):
    dg = v_grip * lat
    dies = [G * kg * dg for (G, kh, kd, kg) in rows]
    print(f"  {name:28s} {lat*1000:5.1f} ms -> {dg*1000:6.0f} um of grip -> "
          f"{min(dies):5.0f}-{max(dies):5.0f} N extra at the dies")
print("-> a 0.5 s stall on the Mac costs roughly as much as it does in a steel press at crawl")
print("   (v7: 375-750 N): the handle crawls the die but the pusher does not crawl. a1b's")
print("   wall is set and enforced on the station MCU, and the Mac commands whole squeezes.")


# ---------------------------------------------------------------------------
head(3, "a2 / a2b / a3: side-entry stand-out when the neighbours already carry crimps")
# htp calc wave2 s3 uses h = a + 1.9 (1.9 = 1.05 floor-to-axis + 0.85 bare neighbour radius, no clearance).
floor_to_axis = 1.05
tops = (("bare neighbour (jacket r)", 0.85),
        ("crimped neighbour, insulation barrel", 1.25),
        ("crimped neighbour, box", 1.35))
print("stand-out h = a + floor-to-axis 1.05 + neighbour's top above its axis + clearance")
for a in (6.0, 9.0, 12.0):
    for name, top in tops:
        for c in (0.0, 0.3):
            h = a + floor_to_axis + top + c
            out = []
            for L in (20.0, 25.0, 35.0):
                R = L * L / (3 * h)
                pb = 0.6 * h * h / L
                out.append(f"L{L:.0f}: R {R:4.1f}, pull-back {pb:4.2f}")
            print(f"  a {a:4.1f} {name:38s} c {c:.1f}: h {h:5.2f} | " + " | ".join(out))
print("-> with crimped neighbours and 0.3 mm clearance the stand-out is a + 2.7 mm, 0.8 mm more than")
print("   htp's a + 1.9 (their own C-frame budget, calc wave2 s4, already counts the 1.35 mm box).")
print("   The neighbours' boxes lie just ahead of the jaw's front face, in the plane of a1's locator")
print("   plate and flap: the plate must stay inside the jaw half's depth on the row's side, or it")
print("   adds to a. Root radius 9-49 mm against the 67-78 mm at which the strands yield.")


# ---------------------------------------------------------------------------
head(4, "Strip length against conductor-barrel length (JST 2.4 mm, clone 1.6-2.1 mm)")
# JST: L = E + A/2 + alpha [mfr S5]. Put the tip b past the barrel's front (brush) and the
# insulation edge mid-window: strip S = E + A/2 + b.
print("S = E (conductor barrel) + A/2 (half the window) + b (brush 0.1-0.2)  [mfr S5 form]")
E_cl = (1.25, 1.5)          # clone conductor barrel [xh-facts s1 estimate from clone drawings]
A = (0.5, 0.8)              # window between barrels [htp exchange_procedure s2 uses 0.5-0.8]
b = (0.1, 0.2)
s_lo = E_cl[0] + A[0] / 2 + b[0]
s_hi = E_cl[1] + A[1] / 2 + b[1]
print(f"  clone drawings: E {E_cl[0]}-{E_cl[1]}, A {A[0]}-{A[1]} -> S {s_lo:.2f}-{s_hi:.2f} mm "
      f"(KONNRA clone spec: 1.6-2.1 [digest])")
S_jst = 2.4
Eg_lo = S_jst - A[1] / 2 - b[1]
Eg_hi = S_jst - A[0] / 2 - b[0]
print(f"  JST S = 2.4 [mfr S6] with the same A and b -> implied genuine E {Eg_lo:.2f}-{Eg_hi:.2f} mm")
print("  Engineer's rule 'die thickness = barrel length' [mfr S18] with PA-09's 1.8 mm-thick 1.6 die,")
print("  listed for SXH-001T-P0.6 [mfr S17] -> E ~1.8 mm if that die is the conductor die [estimate]")
print()
print("Using one contact's strip length on the other:")
for Ec in E_cl:
    for Ac in A:
        edge = S_jst - 0.15               # insulation edge behind the barrel front, 2.4 strip
        rear = Ec + Ac                    # window's rear end (insulation barrel's front)
        over = edge - rear
        tag = (f"bare strands {over:.2f} mm into the insulation barrel" if over > 0
               else f"edge {-over:.2f} mm inside the window")
        print(f"  2.4 mm strip on a clone contact E {Ec:.2f}, A {Ac:.2f}: {tag}")
for Eg in (1.8, 2.0):
    for S in (1.6, 2.1):
        edge = S - 0.15
        under = Eg - edge
        tag = (f"jacket {under:.2f} mm under the conductor barrel" if under > 0
               else f"edge {-under:.2f} mm behind the conductor barrel")
        print(f"  {S:.1f} mm strip on a genuine contact E {Eg:.1f}: {tag}")
print("-> the two published strip lengths fit two barrel lengths; each is wrong on the other")
print("   contact by up to ~0.5 mm, in the direction of a named defect (strands in the insulation")
print("   barrel; insulation under the conductor barrel [mfr S5]). The strip stop follows the")
print("   contact source; a picture of the edge in the window catches either error.  [estimate]")


# ---------------------------------------------------------------------------
head(5, "a5: a 1.8 mm-thick die over the conductor barrel")
die_t = 1.8                # PA-09 1.6/1.9 die thickness [mfr S18]
for E in (1.25, 1.5, 1.8, 2.0):
    for bm in (0.1, 0.2):
        ahead = die_t + bm - E            # die front face ahead of the barrel's front edge
        for t in (0.2, 0.5):
            onto_box = ahead - t
            tag = f"onto the box's rear by {onto_box:.2f}" if onto_box > 0 else f"{-onto_box:.2f} short of the box"
            print(f"  E {E:.2f}, bellmouth {bm:.1f}, transition {t:.1f}: die face {ahead:+.2f} ahead of the "
                  f"barrel front -> {tag}")
print("-> on clone-length barrels (1.25-1.5) a 1.8 mm die placed for bellmouth reaches the box by up")
print("   to ~0.5 mm; placed flush with the box instead, it loses the bellmouth. On a ~1.8 mm barrel")
print("   it fits. One kit contact under the ELP says which case a5 is in.")


# ---------------------------------------------------------------------------
head(6, "a4: eccentric torque when frame stretch and preload set the die-contact angle")
# Model: ram height above BDC y = e(1-cos phi). Dies meet (unloaded geometry) at y_c above BDC.
# Die gap g = (y - y_c) + F/k_f. Crimp: F = Fc (1 - g/0.15) for 0 <= g <= 0.15 (compaction).
# Dies solid (g would be < 0): interference d = y_c - y; F = k_f d up to preload P; then the
# disc stack (rate k_s) in series. Torque = F * e * sin(phi).
def force_at(y, y_c, k_f, k_s, P, Fc, zc=0.15):
    d = y_c - y
    # try crimp branch
    F = Fc * (1 - (y - y_c) / zc) / (1 + Fc / (zc * k_f))
    if F <= 0:
        return 0.0
    g = (y - y_c) + F / k_f
    if g >= 0:
        return F
    if k_f * d <= P:
        return k_f * d
    return P + (d - P / k_f) / (1.0 / k_f + 1.0 / k_s)


def peak_torque(e, y_c, k_f, k_s, P, Fc):
    best = (0.0, 0.0, 0.0)
    n = 4000
    for i in range(n + 1):
        phi = math.radians(60.0) * (1 - i / n)
        y = e * (1 - math.cos(phi))
        F = force_at(y, y_c, k_f, k_s, P, Fc)
        tau = F * e * math.sin(phi) / 1000.0  # N*m (F in N, e in mm)
        if tau > best[0]:
            best = (tau, math.degrees(phi), F)
    F_bdc = force_at(0.0, y_c, k_f, k_s, P, Fc)
    return best, F_bdc


P = 3500.0                  # preload [htp a4]
k_s = 3000.0                # N/mm, disc stack rate [estimate from htp calc s6: 0.3-0.6 mm over 1-2 kN]
print("preload 3.5 kN [htp a4]; stack rate ~3 kN/mm [estimate]; crimp peak Fc at die contact")
print("frame stiffness k_f [estimate]: 10-12 mm shaft on bushings 0.02-0.04 mm at 3 kN, bushing play,")
print("laminated holders 0.01-0.05, button cell ~0.06 at 3 kN (htp: ~0.1 mm at full scale) -> 15-30 kN/mm")
for e in (2.0, 2.5):
    for Fc in (1500.0, 2600.0):
        for k_f in (15000.0, 20000.0, 30000.0, 40000.0):
            # a4 as written: dies meet 0.15 mm above BDC
            (tau, ang, F), Fb = peak_torque(e, 0.15, k_f, k_s, P, Fc)
            met = "dies meet" if Fb >= Fc else "dies do NOT meet"
            eng = "stack engages" if Fb > P else "stack idle"
            # design for stack engagement: y_c = P/k_f + 0.05
            yc2 = P / k_f + 0.05
            (tau2, ang2, F2), Fb2 = peak_torque(e, yc2, k_f, k_s, P, Fc)
            print(f"  e {e:.1f} Fc {Fc/1000:.1f} kN k_f {k_f/1000:4.0f} kN/mm | y_c 0.15: F_BDC {Fb/1000:4.2f} kN "
                  f"({met}, {eng}), peak {tau:4.2f} N*m | y_c {yc2:.3f}: F_BDC {Fb2/1000:4.2f} kN, "
                  f"peak {tau2:4.2f} N*m at {ang2:4.1f} deg")
print("add 30-50 % for eccentric and guide friction [htp calc s5 assumption]:")
print("  5840-31ZY worm gearmotor: ~2.3 N*m working, 6.9 stall [htp, nfpshop]")
print("  bench NEMA 23 (~1.0 N*m running) through 3:1 belt: ~2.7-3 N*m")
print("  bench NEMA 23 through a 10:1 planetary (Prime, STEPPERONLINE B0BPGMZ5LM, $48, 10 N*m permissible): ~9.6 N*m")
print("-> a4's 'eccentric 0.15 mm past die contact' is a rigid-frame figure. With a button cell and")
print("   bushings in the loop (15-30 kN/mm) the frame takes most of the 0.15 mm: below ~17 kN/mm a")
print("   2.6 kN crimp keeps the dies apart (crimp height then follows frame stiffness, which is what")
print("   the stack was for), and below ~23 kN/mm the stack never engages. The peak at BDC is 2.3-3.7 kN,")
print("   not the 4-5 kN of htp calc s6. Setting die contact at preload/k_f + 0.05 = 0.17-0.28 mm above")
print("   BDC engages the stack at every stiffness; the peak torque is then 1.6-1.95 N*m before")
print("   friction, 2.0-2.9 N*m with it: above the worm's 2.3 N*m working figure at the top, at the")
print("   edge of the NEMA 23 through 3:1, well inside the NEMA 23 through a 10:1 planetary.")
print("   The overtravel is found on the machine: step y_c down until the button cell shows the")
print("   stack's knee on an empty stroke (dies face to face, no contact).")


# ---------------------------------------------------------------------------
head(7, "W1: v8's tack station feeding a4's one-nest die set, on v1's lifted-neighbour pallet")
pitch = 5.0                 # v1 fan pitch
h_axis = 5.0                # neighbours' axis above the working floor plane (v1: ~5 mm above the anvil plane)
jr = 0.85
box_half = (0.925, 0.975)   # box 1.85-1.95 wide
lance = (0.6, 0.9)
box_top_above_axis = 1.35
print(f"neighbours at pitch {pitch} mm, axis {h_axis} mm above the working contact's floor [v1]")
for name, half in (("bare neighbour", jr), ("crimped neighbours' boxe", box_half[1])):
    for c in (0.0, 0.3):
        w = 2 * (pitch - half) - 2 * c
        print(f"  width free between {name}s, clearance {c:.1f}: {w:.2f} mm "
              f"(htp a4 one-nest piece 6-8 mm; ith ex s15 punch around the crimp 2.8-4.1 mm)")
z_low = h_axis - floor_to_axis - lance[1]
z_high = h_axis + box_top_above_axis
print(f"  crimped neighbours occupy Z {z_low:.2f} (lance tip) to {z_high:.2f} (box top) above the working floor")
print(f"  side view at C under the neighbours: Z 0 to ~{z_low-0.2:.2f}; the working contact's tallest part")
print(f"  (tacked insulation barrel 2.3-2.5 [v8 estimate]) is inside it")
print()
print("Passage for a tacked contact carried in along +Y under the open punch, floor lifted to clear the anvil:")
carry = (1.0, 1.7)          # ith ex s2: cradle + lance + margin
tall = (2.4, 2.5)           # max(tacked insulation barrel 2.3-2.5, box 2.2-2.4)
closed = (0.73, 0.90)       # conductor-section punch at BDC ~ crimp height
for e in (1.5, 2.0, 2.5):
    for cl in closed:
        open_bot = cl + 2 * e
        need = carry[1] + tall[1]
        print(f"  e {e:.1f} (stroke {2*e:.1f}), conductor punch at BDC {cl:.2f}: open at {open_bot:.2f}; "
              f"tallest carried point {need:.2f} -> clearance {open_bot-need:+.2f} mm")
print("-> e 2.0-2.5 (a4's own range) passes a tacked contact with 0.5-1.7 mm to spare; e 1.5 does not.")
print()
print("Holder: the part of the punch assembly at the neighbours' height must be <= the free width above.")
for cl in closed:
    need_exposed = z_high + 0.3 - cl
    print(f"  punch at BDC {cl:.2f}: narrow section (die piece plus holder neck) must reach "
          f"{need_exposed:.2f} mm up from the punch's crimping edge")
neck_area = 7.0 * 10.0
for F in (3500.0, 4500.0):
    print(f"  holder neck 7 x 10 mm at {F/1000:.1f} kN: {F/neck_area:4.0f} MPa (steel)")
print()
print("Without the tack (v1 laying in directly under a4's open punch):")
for h in (4.55, 5.0):
    for e in (2.0, 2.5):
        open_bot = 0.73 + 2 * e
        print(f"  waiting axis {h:.2f}, e {e:.1f}: working conductor's top {h+jr:.2f} under a punch open at "
              f"{open_bot:.2f} -> clearance {open_bot-(h+jr):+.2f} mm (plus Z curl 0-0.55 [rap calc s6])")
for w in (6.0, 7.0):
    for ang in (30.0, 35.0, 40.0):
        z = (w / 2) / math.tan(math.radians(ang))
        print(f"  oblique cam {ang:.0f} deg from vertical under a {w:.0f} mm punch: sight line leaves the "
              f"punch's footprint at Z {z:.2f} (must be below the open punch, 4.7-5.9)")
print("-> v1 laying in under a4's open punch has +0.33 mm at best (keys at 4.55, e 2.5) before 0-0.55 mm")
print("   of curl, and the oblique camera clears a 6 mm punch only from 35-40 deg. The tack moves the")
print("   lay-in and the strict look to where nothing is overhead, and a4 keeps its short stroke.")


# ---------------------------------------------------------------------------
head(8, "W2: v8's tack station, then a6's foot-closed SN-2549 with a seat instead of a blade")
open_ins = (2.75, 3.2)
open_need = [w + l for w in open_ins for l in lance]
tacked_need = [t + l for t in (2.3, 2.5) for l in lance]
print(f"  open contact: wings + lance {min(open_need):.2f}-{max(open_need):.2f} mm, +1 mm carry -> "
      f"{min(open_need)+1:.2f}-{max(open_need)+1:.2f}  [ith ex s2]")
print(f"  tacked contact: tacked barrel + lance {min(tacked_need):.2f}-{max(tacked_need):.2f} mm, +1 mm -> "
      f"{min(tacked_need)+1:.2f}-{max(tacked_need)+1:.2f}")
save = (min(open_need) - min(tacked_need), max(open_need) - max(tacked_need))
print(f"  jaw opening saved {save[0]:.2f}-{save[1]:.2f} mm; at the open-end gain 3-6 that is "
      f"{save[0]*3:.1f}-{save[1]*6:.1f} mm of grip, {2*save[0]*3:.1f}-{2*save[1]*6:.1f} mm of pedal at 2:1")
print("Person time at C, per crimp [estimate]:")
steps = (("bend conductor k out, carry the tacked contact in high, set it on the seat", 4, 7),
         ("half-press, glance at the seat frame or lamp", 2, 4),
         ("full press", 2, 3),
         ("lift and draw back along the ramp", 2, 3),
         ("booth: drop in, pull, read (v5 in a6's pull jig)", 10, 15),
         ("keyhole", 3, 5))
lo = sum(s[1] for s in steps)
hi = sum(s[2] for s in steps)
for s in steps:
    print(f"  {s[0]:66s} {s[1]:2d}-{s[2]:2d} s")
print(f"  total {lo}-{hi} s -> 53 crimps {lo*53/60:.0f}-{hi*53/60:.0f} min; without booth and keyhole "
      f"{(lo-13)*53/60:.0f}-{(hi-20)*53/60:.0f} min")
print("  plus loading 14 ends into pallets for station T, 10-30 min per unit [digest]")
print("  today ~22 min [htp calc wave2 s9]; the minutes do not fall, the fine act goes away")


# ---------------------------------------------------------------------------
head(9, "Closed insulation barrel height on 1.7 mm silicone: section shape")
A_sil = math.pi / 4 * 1.7 ** 2
print(f"  jacket section {A_sil:.2f} mm^2, stock 0.2, no silicone flows out (e = 0)")
for W in (1.80, 1.90, 1.95):
    Wi = W - 0.4
    for name, phi in (("ellipse (ith ex s9, htp keyhole s8)", math.pi / 4),
                      ("phi 0.85 (ff wave2 s5)", 0.85), ("phi 0.90", 0.90)):
        Hi = A_sil / (phi * Wi)
        print(f"  W {W:.2f}: {name:36s} H {Hi + 0.4:.2f} mm vs 2.4 envelope ({2.4 - Hi - 0.4:+.2f})")
print("-> the ellipse is the tallest reading; a B/F crimp's section sits between ellipse and rectangle,")
print("   so the room under the 2.4 mm envelope is ~0.1-0.3 mm rather than ~0.07, before any silicone")
print("   leaves as collars (ff: 0.15-0.3 mm lower at 10-20 % flow). a5's 'floor and ceiling ~0.1 mm")
print("   apart' is the pessimistic end.")


# ---------------------------------------------------------------------------
head(10, "a3: slide-on capture against where a pulled-out tip is")
cap = {"gathered 0.72": (0.48, 0.59), "splayed 1.0": (0.34, 0.45), "splayed 1.2": (0.24, 0.35)}
print("  lateral capture of the open conductor barrel [v1 calc wave2 s2]:")
for k, v in cap.items():
    print(f"    bundle {k}: +/-{v[0]:.2f}-{v[1]:.2f} mm")
proud = 8.0                 # a3: tips ~8 mm proud of the comb
for ang in (1.0, 2.0, 3.0):
    lat = proud * math.tan(math.radians(ang))
    for curl in (0.0, 0.55):
        rss = math.hypot(lat, curl)
        print(f"  comb exit {ang:.0f} deg at {proud:.0f} mm proud -> {lat:.2f} mm; with curl {curl:.2f} "
              f"[rap calc s6]: {rss:.2f} mm")
print("-> a3's '+/-0.5 mm' holds for gathered tips with a good comb exit; splayed tips and a curled")
print("   2-3 deg exit exceed their capture. A picture of the tip before the slide-on (v1 step 4-5)")
print("   finds them, and the gantry corrects or sends the tip to a twist.")
