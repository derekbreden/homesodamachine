"""terminal-supply explorer, jst-crimp-study, final pass (2026-09-28).

Numbers behind the settled idea files and the three combinations developed in
this pass (x2, x3, a4c):

  1. Post capture at the box entry (a4, a4b, a6, x1): the entry, not the box
     inside, is what the pin passes.
  2. A bare contact lying barrels-up in a channel: its rest on the lance, and
     the lance groove that lets it lie flat (a6 pocket plate, x1 spear block,
     a4 loading nest, a4b/a5/x3 shuttle nests).
  3. The push after a crimp made at or outside the housing, and where that
     travel is stored (a5, a4b), against a single push (x3, a4c).
  4. The lance and a flat anvil's front edge (a5, a6, x1, x3, a4c).
  5. a2d: the punch holder against a crimped neighbour; the flat skip-2 strip
     without a crown; split lengths.
  6. x2: crown station, then sort and push (a2d + into-the-housing i6 + a6's
     post head).
  7. x3: stage every other cavity, crimp, leave, one push (a5 + i2b).
  8. a4c: bare contacts crimped on a post bed through the housing, one push
     (a4b + i6b + i2b's order).
  9. Force ladder: seat pull, retention, proof pull, pull-out.

Run:  python3 w3.py > w3.out.txt

Labels:
  [mfr] [source] [calc] [estimate] [assumption]
  [xh] context/xh-facts.md
  [ith-w3 X]  into-the-housing calc exchange_terminal_supply_w3.out.txt section X
  [mtsl n]    machine-that-sees-and-learns calc on_terminal_supply.out.txt section n
  [ts n]      this explorer's terminal_supply.out.txt; [w2 n] wave2.out.txt
"""
from math import pi, sqrt, atan, degrees, radians, tan, cos, sin


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


# ---------------------------------------------------------------- inputs
POST = 0.64               # mm square header post [mfr S1]
ENTRY = (0.60, 0.70)      # mm box entry, clone drawings [xh S19, S21]
BOX_W = (1.85, 1.90)      # mm clone box width [xh]
BOX_H = (2.20, 2.35)      # mm clone box height [xh]
T = 0.20                  # stock [xh]
LANCE_P = (0.6, 0.9)      # lance stands proud of the floor side [xh]
TIP_XH = (2.4, 2.6)       # lance tip behind the box front, xh-facts table [xh S19-S22]
TIP_ITH = (2.24, 2.64)    # the range into-the-housing used [ith-w3 D]
TRANS = (0.4, 0.6)        # transition box->conductor barrel, reading clone drawings [w2 5]
WIRE = 1.70               # insulation OD [xh]
STRANDS = 0.72            # strand bundle [xh]
XH = 2.50                 # housing pitch [mfr]
HSG_H = 7.75              # housing height along the mating axis [mfr S2]
FRONT_WALL = (0.8, 1.0)   # [assumption]
CRIMP_IB = (1.8, 2.0)     # crimped insulation barrel width [source KONNRA via ribbon-as-pallet]
CRIMP_CB = 1.5            # crimped conductor barrel width [estimate]
OPEN_IB = (2.46, 3.00)    # clone open insulation wings [xh]
OPEN_CB = (1.68, 1.90)    # clone open conductor barrel [xh]
E_STEEL = 200e3
I_POST = POST ** 4 / 12


# ---------------------------------------------------------------- 1
hdr("1. Post capture at the box entry")
print("The pin passes the box's formed entry (0.60-0.70 mm on clone drawings), not the box inside.")
print("[w2 5] used the inside (~1.45 x 1.80) and gave +/-0.41 / +/-0.58; that figure is withdrawn.")
for e in ENTRY:
    for c in (0.10, 0.20, 0.28):
        flat = POST - 2 * c
        print(f"  entry {e:.2f}, pin tip chamfer {c:.2f}/side (flat {flat:.2f}): capture +/-{(e-flat)/2:.2f} mm")
print("Where the pin must arrive, for a head steered by the backlit outline of the contact:")
for gantry, fit in ((0.02, 0.02), (0.05, 0.03)):
    tot = sqrt(gantry**2 + fit**2 + 0.03**2)   # 0.03: entry centre vs outline (box height tol / 2) [estimate]
    print(f"  axis +/-{gantry}, outline fit +/-{fit}, entry-to-outline +/-0.03 -> +/-{tot:.2f} mm (rss)")
print("-> +/-0.04-0.07 mm needed against +/-0.08-0.31 captured: a 0.20-0.28 mm chamfer (near-pointed")
print("   tip) keeps a margin of ~3x. What breaks the margin is height, not aim (section 2).")


# ---------------------------------------------------------------- 2
hdr("2. A bare contact lying barrels-up: rest on the lance, and the lance groove")
print("The lance hangs 0.6-0.9 mm below the floor side, its tip 2.24-2.64 mm behind the front; the")
print("centre of mass is ~2.75 mm behind the front [ith-w3 E], so on a flat floor the contact rocks:")
print("  nose-up 8-16 deg (box-front floor 0.9-1.7 mm high) or nose-down 13-22 deg [ith-w3 E].")
print("  0.9-1.7 mm is 4-20x the capture of section 1: the pin meets the box face, not the entry.")
print("A groove along the whole channel floor, under the lance:")
LANCE_W = (0.5, 0.8)      # lance tongue width [estimate, not on the drawings read]
for g in (0.8, 1.0):
    for bw in BOX_W:
        ledge = (bw - g) / 2
        print(f"  groove {g:.1f} wide, box {bw:.2f}: box floor rests on ledges {ledge:.2f} mm each side;"
              f" lance {LANCE_W[0]}-{LANCE_W[1]} clears by {(g-LANCE_W[1])/2:.2f}-{(g-LANCE_W[0])/2:.2f}/side")
print("  depth >= 1.0 mm clears a 0.9 mm lance by >= 0.1 mm.")
print("  With the floor down flat, the entry centre stands at floor + box height / 2:")
for bh in BOX_H:
    print(f"    box {bh:.2f} tall: entry centre {bh/2:.2f} mm above the floor (lot spread +/-0.05 [estimate])")
print("-> the pin's height is set from the channel floor to ~+/-0.05 mm, inside the capture.")
print("   The same groove belongs in every bare-contact pocket: a6's pocket plate, x1's spear")
print("   block, a4's loading nest, the shuttle nests of a4b, a5, x3 and a4c.")


# ---------------------------------------------------------------- 3
hdr("3. The push after a crimp at or outside the housing, and where it is stored")
seated_front = [HSG_H - fw for fw in FRONT_WALL]   # box front inside the rear face when seated
print(f"Seated box front {min(seated_front):.2f}-{max(seated_front):.2f} mm inside the rear face "
      f"(housing {HSG_H} [mfr] - front wall {FRONT_WALL} [assumption]); same as [ith-w3 A]")
for s in (1.0, 1.5, 2.0):
    lo, hi = min(seated_front) - s, max(seated_front) - s
    print(f"  a5 staged {s:.1f} mm: push after the crimp {lo:.2f}-{hi:.2f} mm")
for proud, eng in ((9.0, 1.5), (9.0, 1.8)):
    front_out = proud - eng
    print(f"  a4b post {proud} proud, box on {eng}: box front {front_out:.1f} outside -> push "
          f"{front_out+min(seated_front):.2f}-{front_out+max(seated_front):.2f} mm")
print("One web clamp, square-cut ends, each contact seated taut: a contact crimped T short of its")
print("seat needs its conductor T longer at the crimp. As a shallow arch over span L, sag ~sqrt(3LT/8):")
for name, Tt in (("a5, 1.5 staged", 5.35), ("a4b, 9 mm post", 14.2)):
    row = ", ".join(f"L {L}: {sqrt(3*L*Tt/8):4.1f}" for L in (20, 25, 30, 40))
    print(f"  {name:16s} T {Tt:5.2f}: sag {row} mm")
print("  [ith-w3 B] gives the clamped hump: 7-8 mm (a5) and 12-13 mm (a4b), tightest radius 2.6-5.7 mm,")
print("  past the strands' ~67 mm yield radius, so the hump keeps its shape and the push draws it")
print("  straight with a few hundredths of a newton.")
print("If the housing steps in X under a fixed web after the first latch, seated conductors drag:")
for n in (4, 5, 7, 9):
    print(f"  XHP-{n}: up to {(n-1)*XH:.1f} mm sideways -> the web clamp rides the housing's stage")
print("Or the web follows each push: the web clamp's Y advances T with the fork, so conductor k is")
print("straight at its crimp; every seated conductor bows by T while the web is forward, and straightens")
print("when it returns. Strand strain in that bow, and bending cycles to failure (Coffin-Manson,")
print("eps_f' 0.3-0.6, c -0.6 [estimate]):")
for r in (2.6, 5.7):
    eps = 0.04 / r
    lives = []
    for ef in (0.3, 0.6):
        lives.append(0.5 * ((eps / 2) / ef) ** (1 / -0.6))
    print(f"  tightest radius {r} mm: strand strain {eps*100:.1f} % -> ~{min(lives):.0f}-{max(lives):.0f} bows "
          f"(a housing asks at most 8)")
print("  -> fatigue is not what limits it; the waiting conductors are: they advance T too, and must wait")
print("     lifted above the housing's top so they do not reach its rear face.")
print("A single push after every crimp stores nothing: every conductor gets its T at once (x3, a4c).")
print("Any Y stagger between neighbours at the crimp is stored in the finished loom by that push")
print("(the housing seats the nearer contacts first and then carries them on), so all contacts of")
print("one housing are crimped at one Y when one move seats them.")


# ---------------------------------------------------------------- 4
hdr("4. The lance and a flat anvil's front edge")
print("Flat anvil: front edge >= lance tip + 0.1 behind the box front, and <= conductor barrel front")
print("(box 2.0 + transition t). Margin = (2.0 + t) - (tip + 0.1).")
for label, tips in (("xh-facts table 2.4-2.6", TIP_XH), ("into-the-housing 2.24-2.64", TIP_ITH)):
    print(f"  lance tip {label}:")
    for t in TRANS:
        row = ", ".join(f"tip {tp:.2f}: {(2.0+t)-(tp+0.1):+.2f}" for tp in tips)
        print(f"    t {t:.1f}: {row} mm")
print("-> on either range a flat anvil fits in about half the cases. The other half needs a lance")
print("   slot in the anvil's front (0.8-1.0 mm wide), with the conductor barrel's first 0.1-0.3 mm")
print("   carried on the slot's shoulders. Settled by one side photo of a kit contact.")
print("   The SN-2549 crimps kit contacts today, so its XH anvil already satisfies this for them.")


# ---------------------------------------------------------------- 5
hdr("5. a2d: the punch holder against a crimped neighbour; the flat skip-2 strip; split")
print("Crimped conductors keep their contacts at the station's Y, at +/-p. The widest part there is")
print("the box, 1.85-1.95 wide (half 0.98), not the conductor (half 0.85).")
for blade in (2.5, 2.7, 3.0):
    p_cond = blade / 2 + WIRE / 2 + 0.3
    p_box = blade / 2 + 1.95 / 2 + 0.3
    print(f"  blade {blade:.1f}: p >= {p_box:.2f} mm (against a crimped box) vs {p_cond:.2f} (against a wire)")
print("Height: the holder must stay above the neighbour's box top (2.2-2.4 above the floor) at the")
print("bottom of the stroke:")
for what, ch in (("conductor crimper, crimp height 0.75-0.9", (0.75, 0.9)),
                 ("insulation crimper, crimp height 1.8-2.0", (1.8, 2.0))):
    need = (2.4 + 0.3 - ch[1], 2.4 + 0.3 - ch[0])
    print(f"  {what}: blade stands >= {need[0]:.1f}-{need[1]:.1f} mm out of its holder")
print("A flat skip-2 strip (no crown) keeps a 5P clear to p 2.9 mm and a 4P to 3.9 mm [w2 1]:")
for blade in (2.5, 2.7, 3.0):
    p = blade / 2 + 1.95 / 2 + 0.3
    print(f"  blade {blade:.1f} -> p {p:.2f}: 5P flat {'clear' if p <= 2.9 else 'NOT clear'}, "
          f"4P flat {'clear' if p <= 3.9 else 'NOT clear'}")
print("-> with a narrow knife-set blade a flat skip-2 strip already lets a 4P or 5P lie flat; the")
print("   crown adds the level view, the wrap hold-down, and any width (J1's nine as one ribbon).")
print("Split to fan a ribbon end to p at a 20 deg fan, + ~6 mm straight [ith-w3 H]:")
for name, n in (("3P", 3), ("4P", 4), ("5P", 5), ("J4/J7 pair (7-8)", 8), ("J1 (9)", 9)):
    row = ", ".join(f"p {p:.1f}: {((n-1)/2*(p-1.7))/tan(radians(20))+6:4.1f}" for p in (2.8, 3.0, 3.5))
    print(f"  {name:18s} {row} mm")


# ---------------------------------------------------------------- 6
hdr("6. x2: crown station, then sort and push")
print("At the pick (staging plane, fan pitch p): the post head's fork straddles the wire behind the")
print("insulation barrel; tines 0.4 mm; holder <= 2.0 mm wide at the box.")
TINE = 0.4
HOLDER_HALF = 1.0
for p in (2.8, 3.0, 3.5):
    gap = p - WIRE
    tine_room = gap - TINE - 0.1           # 0.1 clearance to the wire on its own side
    holder = p - 0.975 - HOLDER_HALF
    print(f"  p {p:.1f}: gap between insulation surfaces {gap:.2f}; after a tine {tine_room:+.2f}; "
          f"holder to neighbour box {holder:+.2f} mm")
print("At the target row (2.5 mm, placed neighbours):")
tine_outer = WIRE / 2 + 0.1 + TINE
print(f"  tine outer edge {tine_outer:.2f} from the wire axis vs neighbour wire surface {XH-WIRE/2:.2f}: "
      f"{XH-WIRE/2-tine_outer:+.2f} mm")
print(f"  holder half {HOLDER_HALF:.2f} vs neighbour box edge {XH-0.975:.3f}: {XH-0.975-HOLDER_HALF:+.2f} mm")
print("Spear on a staged crimp: the conductor alone buckles at P ~ 150-160/L^2 N [ith-w3 H]:")
for L in (20, 25, 30):
    print(f"  free {L} mm: ~{155/L**2:.2f} N, against a 0.2-2 N spear -> the fork reacts it")
print("Proof pull at station A: 20 N from the carriage's Y through its cell, against a pull fork on")
print("the crown land behind conductor k's insulation barrel:")
bear = 2 * TINE * 0.6
print(f"  two tines 0.4 wide bearing 0.6 mm high: {20/bear:.0f} MPa on the fork")
edge = 2 * T * 0.9
print(f"  crimped insulation barrel rear edge, 2 x 0.2 x ~0.9 mm: {20/edge:.0f} MPa, below bronze's 450-650")
print("Machine time per unit [estimate]:")
for name, a in (("strip at A (a2d 94 min)", 94), ("loose at A (a6 100 min)", 100)):
    lo, hi = a + 60 + 7, a + 87 + 7
    print(f"  {name}: + sort, pull, push 60-87 min + carriage moves 7 min = {lo/60:.1f}-{hi/60:.1f} h")


# ---------------------------------------------------------------- 7
hdr("7. x3: stage every other cavity, crimp, leave, one push")
print("Clearance per side at 2.5 mm pitch [ith-w3 C, J], narrow stepped dies (3.1 conductor step,")
print("0.8 walls; 2.5-2.7 insulation step):")
rows = [
    ("odd pass: waiting even conductor 1.7 OD vs 3.1 conductor step", XH - 1.55 - WIRE / 2),
    ("odd pass: waiting even conductor 1.7 OD vs 2.7 insulation step", XH - 1.35 - WIRE / 2),
    ("odd pass: waiting even conductor, 3.5 ordinary punch", XH - 1.75 - WIRE / 2),
    ("even pass: crimped conductor barrel 1.5 vs 3.1 step", XH - 1.55 - CRIMP_CB / 2),
    ("even pass: crimped insulation barrel 1.95 vs 2.5 step", XH - 1.25 - 1.95 / 2),
    ("even pass: crimped insulation barrel 1.95 vs 2.7 step", XH - 1.35 - 1.95 / 2),
    ("even staging: open wings 2.46 vs crimped ins. barrel 1.95", XH - 1.23 - 1.95 / 2),
    ("even staging: open wings 3.00 vs crimped ins. barrel 1.95", XH - 1.50 - 1.95 / 2),
]
for n, v in rows:
    print(f"  {n:62s} {v:+.2f} mm")
print("  -> the waiting side needs a lift (a loft or finger) for an ordinary punch; the even pass")
print("     admits only the narrow stepped dies.")
print("Push: 5.25-5.45 mm for every contact at once (section 3). Gang force:")
for n in (4, 5, 7, 9):
    print(f"  XHP-{n}: {n}x9.8 = {n*9.8:.0f} N (KONNRA clone insertion) to {n}x25 = {n*25} N margin")
print("Stagings per housing (odd, then even; J2's cavity 3 empty):")
for name, cav in (("XHP-4", [1, 2, 3, 4]), ("XHP-5", [1, 2, 3, 4, 5]), ("J2 XHP-6", [1, 2, 4, 5, 6]),
                  ("XHP-7", list(range(1, 8))), ("XHP-9", list(range(1, 10)))):
    odd = [c for c in cav if c % 2 == 1]
    even = [c for c in cav if c % 2 == 0]
    print(f"  {name:9s}: odd {odd} then even {even}")
cyc = {"stage (shuttle, post, look)": 40, "lay conductor in (finger / web), steer": 30,
       "slow stroke": 30, "look after": 10, "proof pull by the finger clamp": 15, "retries, avg": 15}
per = sum(cyc.values())
print(f"Time [estimate]: ~{per} s per contact + ~90 s per housing for the push and pull-backs ->"
      f" {(per*53+90*10)/3600:.1f} h per unit")


# ---------------------------------------------------------------- 8
hdr("8. a4c: bare contacts crimped on a post bed through the housing, one push")
print("Posts 0.64 mm square steel, cantilevered from a bed behind the mating face, through the")
print("housing (front opening loose, cavity larger than the post), standing ~9 mm out of the rear face:")
for L in (17, 19):
    k = 3 * E_STEEL * I_POST / L**3
    Pcr = pi**2 * E_STEEL * I_POST / (4 * L**2)
    print(f"  free length {L} mm: {k:.2f} N/mm sideways; tip-loaded Euler buckling {Pcr:.0f} N "
          f"(push-on 0.2-2 N)")
print("  -> soft: the die centres the barrels for 0.2-0.3 N of post bending; the push-on is safe.")
print("Where the dies work, relative to the post tips (Y from the tip, + away from the housing):")
eng = 1.5
box_front = -eng
print(f"  box {box_front:+.1f} to {box_front+2.0:+.1f}; lance tip {box_front+2.4:+.1f} to {box_front+2.6:+.1f};"
      f" conductor barrel {box_front+2.0+0.4:+.1f} to {box_front+2.0+0.6+1.5:+.1f};"
      f" insulation barrel ~{box_front+4.5:+.1f} to {box_front+6.0:+.1f} mm")
print("  empty neighbour posts end at 0.0, so an anvil whose front edge stands behind the lance")
print("  (>= +1.0) never meets them: in the odd pass the dies' width is limited only by the waiting")
print("  conductors, which wait lifted.")
print("Loading nest for the even pass, between crimped neighbours whose boxes stand at +/-2.5:")
box_edge = XH - 0.975
print(f"  neighbour box edge {box_edge:.3f} mm from the station axis -> a tongue nest <= {2*(box_edge-0.15):.2f} mm wide")
print("  (odd pass: bare neighbour posts at 2.5 - 0.32 = 2.18 -> a walled nest <= 4.06 wide)")
print("Housing travel: 13.95-14.45 mm, once, for every contact (section 3; [ith-w3 A]).")
print("Post pitch: the bed must be 2.50 mm. A 2.54 mm header is off at the ends by:")
for n in (4, 5, 7, 9):
    print(f"  {n} posts: +/-{(n-1)*0.04/2:.2f} mm")


# ---------------------------------------------------------------- 9
hdr("9. Force ladder [ith-w3 K]")
for pull in (5.0, 10.0):
    print(f"  seat pull {pull:4.1f} N: {pull/14.7*100:3.0f} % of 14.7 N (Molex analog retention), "
          f"{pull/19.6*100:3.0f} % of 19.6 N (KONNRA)")
print("  -> 5 N latch test < 14.7-19.6 N retention < ~20 N proof pull (before insertion) < 39.2 N pull-out")
