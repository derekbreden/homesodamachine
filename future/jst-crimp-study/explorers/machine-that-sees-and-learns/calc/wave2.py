"""Wave-2 numbers for machine-that-sees-and-learns.

Run: python3 wave2.py > wave2.out.txt

Sections
  1. v5 / v1: the contact's box as its own roll gauge in the silhouette
  2. v1 / v7: lateral capture when the bundle is splayed or the tip curled; Y from tip and edge
  3. v7: where each control loop has to close (latency against crawl speed and loop stiffness)
  4. v7: camera timing for lighting states, and why the stream stays open all run
  5. v8: the watched tack: force, drive, anvil stress, wing-contact order, grip window
  6. v3: pulling coupons to failure: soldered lug against a bare-copper wrap on a pin
  7. v7: asks, person minutes and supervisor cost, first day against steady state
  8. v7: the first day, hour by hour

Labels: [calc] computed here; [estimate]; [assumption]; others cite their source.
Contact dimensions are the clone-drawing readings in context/xh-facts.md section 1.
"""
import math

def head(n, title):
    print()
    print("=" * 78)
    print(f"{n}. {title}")
    print("=" * 78)

# ---------------------------------------------------------------------------
head(1, "v5 / v1: the contact's box as its own roll gauge in the side silhouette")
# Viewed along X (across the wire), a rigid rectangle W (along X) x H (along Z) rolled by r about
# the wire axis (Y) shows a Z extent of H|cos r| + W|sin r|.
box_W = (1.85, 1.95)       # box width across the wire [xh-facts s1, clone 1.85-1.90; JST 1.95]
box_H = (2.20, 2.40)       # box height [xh-facts s1, clone 2.2-2.35; JST envelope 2.4]
crimp = [(0.73, 1.60), (0.90, 1.90)]   # conductor crimp H x W bounds [ribbon-as-pallet calc P s5]
print("Box silhouette growth with roll (the box is square-sided; use its front 1 mm, ahead of the lance):")
for W, H in ((1.85, 2.20), (1.95, 2.40)):
    row = []
    for deg in (0.5, 1, 2, 3):
        r = math.radians(deg)
        d = H * math.cos(r) + W * math.sin(r) - H
        row.append(f"{deg:>3} deg +{d*1000:4.0f} um")
    print(f"  box {W:.2f} x {H:.2f}: " + "   ".join(row))
print("Roll recovered from the box, then the crimp height corrected by W_c sin r:")
edge_sigma_um = {"A ELP 45 px/mm": (1.6, 9.4), "D 122 px/mm": (0.6, 3.5)}   # vision_budget s3
for cam, (lo, hi) in edge_sigma_um.items():
    # small roll: dh_box ~ W r - H r^2/2; near r = 1 deg the slope is ~W - H r
    slope = 1.9 - 2.3 * math.radians(1)       # mm per rad near 1 deg
    for s in (lo, hi):
        sr = (s / 1000) / slope               # rad
        print(f"  {cam}: box edge-pair sigma {s:.1f} um -> roll sigma {math.degrees(sr):.2f} deg"
              f" -> crimp-height error from correction {1.6*sr*1000:.1f}-{1.9*sr*1000:.1f} um")
print("  Near zero roll the box's growth is first-order in |r| only once r exceeds the")
print("  measurement noise; below ~0.3 deg the box says 'flat' and the crimp error is")
print("  under ~0.01 mm anyway (row 0.5 deg above).")
print("Reference for the box's true height:")
print("  the lot's minimum box silhouette height, from a +/-4 deg roll sweep of five contacts at lot")
print("  start (the sweep ribbon-as-pallet names as Repair B, done once per lot instead of per crimp).")
print("  In line (v1) the nest picture at step 3 is a check on it, good only to the box slot's clearance:")
slot_clear = (0.03, 0.10)     # box slot clearance over box width [estimate]
for c in slot_clear:
    r = math.atan(c / 2.3)
    print(f"  box slot {c:.2f} mm wider than the box: roll in the nest up to {math.degrees(r):.1f} deg"
          f" -> box reads up to +{(2.3*math.cos(r)+1.9*math.sin(r)-2.3)*1000:.0f} um at step 3")
print("  Box-to-box spread inside a lot (unmeasured) adds straight to the roll estimate: +/-10 um of")
print("  spread is +/-0.3 deg, +/-0.01 mm of crimp-height error. Five contacts under the camera measure it.  [calc]")
print("Residual after correction, rounded-bottom crimp (width term about half the rectangle's):")
for deg in (1, 2, 3):
    r = math.radians(deg)
    for H, W in crimp:
        rect = W * math.sin(r)
        rnd = 0.5 * rect
        print(f"  roll {deg} deg, crimp {H}x{W}: rectangle term {rect*1000:.0f} um, rounded {rnd*1000:.0f} um;"
              f" correcting with the rectangle term over-corrects a rounded crimp by up to {(rect-rnd)*1000:.0f} um")
print("  -> correct by the mean of the two bounds and flag any crimp rolled > 2 deg for a re-seat;")
print("     then the residual stays within ~+/-0.01-0.015 mm.  [calc, crimp cross-section shape assumed]")

# ---------------------------------------------------------------------------
head(2, "v1: lateral capture when the bundle splays or the tip curls; Y from the tip and the edge")
barrel_open = (1.68, 1.90)    # open conductor barrel width [xh-facts s1]
for bundle, label in ((0.72, "gathered 60 x 0.08 mm"), (1.0, "loosely splayed"), (1.2, "splayed")):
    caps = [(w - bundle) / 2 for w in barrel_open]
    print(f"  bundle {bundle:.2f} mm ({label}): lateral capture +/-{caps[0]:.2f}..{caps[1]:.2f} mm")
print("Lateral error the pallet can deliver at the tip, 7 mm proud:")
for ang in (0.5, 1.0, 2.0, 3.0):
    print(f"  groove exit {ang:.1f} deg off the Y axis -> {7*math.tan(math.radians(ang)):.2f} mm at the tip")
print("  plus comb-face pitch stack +/-0.1 mm [ribbon-as-pallet calc R s1] and a lateral set left by the fan's")
print("  own bends. A gathered bundle has room for 1-2 deg of exit error; a splayed one has little.")
print("  -> the picture's lateral job is small for good tips and decisive for the bad ones; it is")
print("     also what finds the bad ones.  [calc]")
print("Axial: one flush cut gives every tip one line, but the insulation edge of each conductor is")
print("where its own strip tore:")
for scatter in (0.1, 0.2, 0.3):
    for window in (0.5, 1.0):
        print(f"  edge scatter +/-{scatter:.1f} mm against a {window:.1f} mm window: uses {2*scatter/window:.0%} of it")
print("  -> Y is set per conductor from both the tip (brush) and the edge (window) as seen;")
print("     the tip line from the cut is the starting prediction.  [calc]")

# ---------------------------------------------------------------------------
head(3, "v7: where each control loop has to close")
speeds = {"approach": 2.0, "crawl through compaction": 0.05, "crawl, faster": 0.1}   # mm/s [estimate]
latencies = {
    "HX711 one sample (80 SPS) in MCU": 0.0125,
    "HX717 one sample (320 SPS) in MCU": 0.0031,
    "Mac over USB serial, typical": 0.03,
    "Mac, bad moment (USB or scheduler hiccup)": 0.5,
    "Mac, GC pause / sleep / crash": 5.0,
}
k_loops = {"steel local loop": (15e3, 30e3), "printed frame": (2.8e3, 12e3)}   # N/mm [force-and-form calc]
print("Klipper samples: HX711 80 SPS, HX717 320 SPS [source: klipper3d.org/Load_Cell.html, fetched 2026-09-28].")
for sname, v in speeds.items():
    print(f"  {sname} at {v} mm/s:")
    for lname, t in latencies.items():
        d_um = v * t * 1000
        s = f"    {lname:44s} travel {d_um:8.1f} um"
        if v < 1:
            fs = [f"{k[0]*d_um/1000:6.0f}-{k[1]*d_um/1000:6.0f} N ({kn})" for kn, k in k_loops.items()]
            s += "   force overshoot once solid: " + "; ".join(fs)
        print(s)
print("  -> At crawl, an MCU decides within a micron. The Mac is also fast enough on an ordinary")
print("     day (1.5 um, ~20-45 N on steel), but not on a bad one; so the MCU owns every stroke and")
print("     its limits, and the Mac only commands whole strokes and reads their traces.")
print("  -> At approach speed even the MCU travels 6-25 um per sample: the stroke must drop to crawl")
print("     at a taught height before the wing tips can touch, not on the first force rise.  [calc]")
comp = (0.1, 0.2)
for v in (0.05, 0.1):
    for name, sps in (("HX711", 80), ("HX717", 320)):
        print(f"  samples through the last {comp[0]}-{comp[1]} mm at {v} mm/s, {name}: "
              f"{comp[0]/v*sps:.0f}-{comp[1]/v*sps:.0f}")
print("Time scale of each loop, and who closes it  [estimate]:")
loops = [
    ("force limit and stroke envelope", "MCU", 0.003, 0.0125),
    ("drop to crawl at a taught height", "MCU", 0.0125, 0.05),
    ("heartbeat: MCU holds any uncommitted move if the Mac is silent", "MCU", 1.0, 2.0),
    ("visual servo round: move, settle, capture, fit", "Mac runner", 1.0, 3.0),
    ("gate decision by thresholds", "Mac runner", 0.2, 1.0),
    ("borderline judged by Claude (one call)", "Mac runner -> Claude", 5.0, 30.0),
    ("ask answered by Derek", "person", 60.0, 8 * 3600.0),
    ("trend across a ribbon end / unit", "supervisor session", 600.0, 6 * 3600.0),
    ("destructive re-check (v3 mini-campaign)", "supervisor proposes, Derek approves", 5 * 86400.0, 30 * 86400.0),
]
for name, who, a, b in loops:
    def fmt(t):
        if t < 1: return f"{t*1000:.0f} ms"
        if t < 120: return f"{t:.0f} s"
        if t < 7200: return f"{t/60:.0f} min"
        if t < 2 * 86400: return f"{t/3600:.0f} h"
        return f"{t/86400:.0f} d"
    print(f"  {name:62s} {who:36s} {fmt(a):>7s} - {fmt(b)}")

# ---------------------------------------------------------------------------
head(4, "v7: camera timing for lighting states; one stream for the whole run")
print("Facts carried from the repo [repo: tools/panelcam.targets.conf]:")
print("  - the ELP's lens 'parks when the stream starts' and lands ~60 units differently by direction;")
print("  - full 4656x3496 arrives only as MJPG; the YUV mode tears and runs under 1 fps;")
print("  - AVFoundation indices move, so a camera is named, not numbered.")
print("  -> a capture app that opens the stream once per run, walks focus once, and hands frames")
print("     out on request, instead of one app launch per picture (which re-parks focus each time).")
for fps in (5, 10, 15):              # MJPG full-res frame rate [assumption: not measured here]
    for discard in (2, 4):           # frames already buffered when the light changes [assumption]
        per_state = (discard + 1) / fps + 0.02
        print(f"  {fps:2d} fps, discard {discard} frames after a light change: {per_state:.2f} s per state;"
              f" 8 states {8*per_state:.1f} s; 4 states {4*per_state:.1f} s")
print("  A 1 mm indicator LED in a corner of the field, driven with the lights, shows in each frame")
print("  which lighting state it was taken under, so a stale buffered frame is rejected by sight,")
print("  not by a guessed discard count.  [estimate]")

# ---------------------------------------------------------------------------
head(5, "v8: the watched tack")
ins_force = (33, 132)          # N to close one insulation barrel [xh-facts calc C1 s4, via change-the-question c1b]
print(f"Insulation barrel closing force per contact: {ins_force[0]}-{ins_force[1]} N [xh-facts calc C1 s4].")
for kgcm in (25, 35):
    T = kgcm * 0.0981           # N m
    for arm_mm in (20, 25):
        F = T / (arm_mm / 1000)
        for lever in (1, 3):
            print(f"  {kgcm} kg.cm servo, {arm_mm} mm horn, lever {lever}:1 -> {F*lever:5.0f} N at the former")
print("  NEMA 17 on a Tr8x2 screw: ~280 N [hand-tool-as-press calc s2]. Either closes a tack;")
print("  a hard stop sets the tack height, so the drive only has to exceed the forming force.")
area = 2.3                     # mm2 of insulation barrel floor on the anvil [change-the-question calc s5]
for F in ins_force:
    print(f"  anvil stress under the insulation barrel at {F} N: {F/area:.0f} MPa "
          f"(PETG yields ~50; steel insert under the barrel)")
print("Order of wing contact in an ordinary one-stroke crimp (both crimpers on one ram):")
ins_wing = (2.75, 3.20); ins_ch = (1.8, 2.1)       # open wing height; final insulation height [xh-facts s1; f&f wave2 s5]
con_wing = (1.50, 1.60); con_ch = (0.73, 0.88)     # [xh-facts s1; KONNRA / C1 estimate]
ins_rem = (ins_wing[0] - ins_ch[1], ins_wing[1] - ins_ch[0])
con_rem = (con_wing[0] - con_ch[1], con_wing[1] - con_ch[0])
print(f"  insulation wings meet their crimper with ~{ins_rem[0]:.2f}-{ins_rem[1]:.2f} mm of stroke left")
print(f"  conductor wings meet theirs with          ~{con_rem[0]:.2f}-{con_rem[1]:.2f} mm left")
print("  -> on these clone dimensions the insulation barrel starts closing first in a one-stroke")
print("     crimp and is largely formed before conductor compaction (the last 0.1-0.2 mm).")
print("     A tack, then the full stroke, keeps that order with a pause in it. Two-squeeze hand")
print("     tools (conductor first) are the other order.  [calc on clone dims; crimper mouth")
print("     flare, which shifts both first touches, is not modelled]")
print("The grip window of a loose tack  [force-and-form calc wave2 s5, estimates]:")
print("  insulation barrel squeezing the jacket 10 %: strands slip in the jacket at 0.4-3.1 N")
print("  squeezing 30 %: 1.1-9.4 N (the jacket never slips in the barrel before the strands do)")
r_j = 0.85                     # jacket radius, mm
for F in (0.4, 1.0, 3.0):
    print(f"  grip {F:.1f} N -> roll torque it resists ~{F*r_j:.2f} N.mm at the jacket's radius")
print("  the parted conductor's own torsion is 0.33-0.58 N.mm/rad [ribbon-as-pallet calc P s5]:")
print("  a 0.4 N tack holds roll unless the conductor is twisted more than ~0.6-1 rad by handling.")
print("What handling asks of the tack  [estimate]:")
print("  contact weight 0.043 g -> 0.0004 N; lowering box-first into a vertical keyed slot with")
print("  chamfers: <0.05-0.2 N of friction and <0.05 N.mm of squaring torque if it arrives within")
print("  a few degrees. A tack at 5-15 % squeeze (0.2-1.5 N) carries it.")
print("Backing a failed tack out, contact slid forward off the tip:")
E = (2.5, 5.5); A_j = 1.863   # jacket modulus MPa [Gent, f&f wave2]; jacket section mm2
for F in (0.4, 1.0, 1.5):
    for seg in (1.5, 3.0):
        strains = [F / (e * A_j) for e in E]
        print(f"  release force {F:.1f} N, jacket free {seg:.1f} mm between key grip and tack:"
              f" stretches {min(strains)*seg:.2f}-{max(strains)*seg:.2f} mm while it slides (elastic, returns)")
print("  -> a loose tack comes off with the jacket edge dragged forward a few tenths of a mm and")
print("     returning; a tight one drags the jacket along the strands. The look after the back-out")
print("     decides between 'new contact, same strip' and 're-strip or cut back'.  [estimate]")
print("Time at the tack station, one conductor  [estimate]:")
tack = [("contact into the nest (plate pick or strip index)", 5, 25),
        ("look: contact seated, lance, wings", 1, 3),
        ("hover look, predict X/Y, key down, side look", 8, 20),
        ("tack: former down to its stop at ~1 mm/s, force trace", 3, 6),
        ("look: top-down, 4-8 lighting states, focus 2 slices", 6, 15),
        ("carry to the crimp nest (20-40 mm), seat, one side look", 6, 12)]
a = sum(t[1] for t in tack); b = sum(t[2] for t in tack)
for n, lo, hi in tack:
    print(f"  {n:62s} {lo:3d} {hi:3d} s")
print(f"  tack side of one conductor: {a}-{b} s; the heavy crimp follows at its own station")

# ---------------------------------------------------------------------------
head(6, "v3: gripping a coupon for a pull to failure")
print("Soldered far-end lug (ribbon-as-pallet's repair): 10 mm of tinned bundle in solder, 500-750 N,")
print("  above wire break; one joint per coupon with the bench Hakko.  [ribbon-as-pallet calc P s4]")
for mu in (0.2, 0.3, 0.5):
    for turns in (2, 3):
        th = 2 * math.pi * turns
        print(f"  bare copper wrapped {turns} turns on a steel pin, mu {mu}: clamp after the wrap"
              f" carries {100*math.exp(-mu*th):.2f} N of a 100 N pull")
for pin in (3.0, 5.0):
    print(f"  0.08 mm strand bent over a {pin:.0f} mm pin: surface strain {0.08/pin:.1%}"
          f" (annealed copper elongates 20-30 %)")
print("  -> stripping 25-30 mm of the coupon's far end and wrapping the bare bundle two turns on")
print("     a 3-5 mm pin before a screw clamp holds a pull to failure with no jacket in the path;")
print("     wire break may start at the pin entry at some fraction below straight break [estimate:")
print("     80-95 %], still above the 39-54 N region the campaign resolves.")
for n in (150,):
    print(f"  preparation for {n} coupons: soldered lugs ~{n*1.0/60:.1f}-{n*1.5/60:.1f} h; wraps ~{n*0.5/60:.1f}-{n*0.8/60:.1f} h"
          f" [estimate 60-90 s and 30-50 s each]")

# ---------------------------------------------------------------------------
head(7, "v7: asks, person minutes and supervisor cost")
crimps = 53
modes = [("day 1, 'ask all' gates for the first ribbon end, then thresholds untuned", 0.35, 0.50, 0.10, 0.20),
         ("first units, thresholds from day-1 labels", 0.10, 0.20, 0.03, 0.06),
         ("steady state after ~5 units of labels", 0.05, 0.10, 0.01, 0.03)]
print("rates per crimp  [estimate]: borderline (judged by Claude) / asked of Derek")
for name, blo, bhi, alo, ahi in modes:
    print(f"  {name}")
    print(f"    borderline {blo:.0%}-{bhi:.0%} -> {crimps*blo:.0f}-{crimps*bhi:.0f} Claude calls per unit;"
          f" asks {alo:.0%}-{ahi:.0%} -> {crimps*alo:.0f}-{crimps*ahi:.0f} asks per unit")
    print(f"    person time at 20-40 s an ask: {crimps*alo*20/60:.0f}-{crimps*ahi*40/60:.0f} min per unit")
def vtok(w, h):
    return math.ceil(w / 28) * math.ceil(h / 28)       # [source: Claude vision docs, wave 1]
models = {"Opus 5.5": (4, 20), "Sonnet 5.5": (2, 10), "Haiku 4.5": (1, 5)}   # $/MTok [claude-api skill table, cached 2026-09-25]
cache_read_price = {"Opus 5.5": 0.20, "Sonnet 5.5": 0.20, "Haiku 4.5": 0.10}  # $/MTok; Opus/Sonnet from the skill table, Haiku 0.1x input [assumption]
ask_in_new = 4 * vtok(1000, 1000) + 2500               # four crops + numbers + record
ask_in_cached = 30000                                  # standing instructions + labelled reference crops
ask_out = 1500
report_in = 60000; report_out = 4000                   # unit report over the day's log summaries
print("Supervisor session costs  [estimate; prices as the wave-1 calc, from the claude-api skill table]:")
for m, (pi, po) in models.items():
    per_ask = (ask_in_new * pi + ask_in_cached * cache_read_price[m] + ask_out * po) / 1e6
    rep = (report_in * pi + report_out * po) / 1e6
    for name, blo, bhi, alo, ahi in modes:
        calls = crimps * (bhi + ahi)
        print(f"  {m:11s} {name[:34]:34s} ~{calls:4.0f} events x ${per_ask:.3f} + report ${rep:.2f}"
              f" = ${calls*per_ask+rep:5.2f} per unit")
print("  claude -p reports total_cost_usd in its JSON output, so the runner logs actual spend")
print("  per event [source: code.claude.com/docs/en/headless, fetched 2026-09-28].")

# ---------------------------------------------------------------------------
head(8, "v7: the first day of running, hour by hour  [estimate]")
day = [("power-on doctor: ports by name, heartbeats, e-stop loop, load-cell zero and noise", 0.5),
       ("home; walk focus once per view; fiducials; gauge pin -> px/mm; save calibration 1", 0.75),
       ("reference strokes: empty nest x5, contact without wire x5 -> force envelope floor", 0.5),
       ("dry lay-ins on a scrap 5P end, no contacts: servo rounds, key drops, side looks", 0.75),
       ("5 scrap crimps, 'ask all': Derek reads every gate and after-picture at the bench", 1.0),
       ("cut, micrometer and pull those 5 (booth pull, luggage scale) -> first labels", 0.75),
       ("lunch while the log is summarised; thresholds 2 proposed and approved", 0.75),
       ("first real ends: five 4P ends (J3, J5, J9, J11, J13), 20 crimps, 'ask borderline'", 1.5),
       ("insert those by hand (as today), test on the wafer board, compare with the log", 0.75),
       ("evening: supervisor writes the day's report; Derek reads it on his phone", 0.25)]
t = 0
for name, h in day:
    t += h
    print(f"  {t-h:4.2f}-{t:4.2f} h  {name}")
print(f"  total ~{t:.1f} h with Derek near the bench; ~25 crimps made; ~20-40 asks answered")
