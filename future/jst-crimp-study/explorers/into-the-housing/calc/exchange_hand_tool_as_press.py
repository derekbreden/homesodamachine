"""Numbers for exchange/into-the-housing--on--hand-tool-as-press.md.

Each section tests one claim in hand-tool-as-press's ideas against the insertion
view. Inputs are labelled; run with python3 and keep the .out.txt beside it.

Coordinates as in ../handover.md: Y along the contact, +Y toward the box
(front); the lance hangs from the floor side of the box, pointing rearward (-Y)
and outward from the floor.
"""
import math

def hr(title):
    print()
    print("=" * 76)
    print(title)
    print("=" * 76)

# ---------------------------------------------------------------------------
hr("1. The neck: box shoulder, flap blade, brush, lance tip and anvil face")
# [source S22, CJT A2501-T] box 2.00, lance tip 2.44 +/-0.20 behind front, 0.67 proud
# [xh-facts §1] lance 0.6-0.9 proud, tip 2.4-2.6 behind front (clone drawings)
# [estimate, i2] box-to-conductor-barrel transition 0.2-0.5 mm
# [hand-tool-as-press a1] flap blade 0.3 mm; its front face on the box's rear shoulder
box = 2.00
blade = 0.30
print("Y measured from the contact's front (box nose). Conductor-barrel front = box + transition.")
print(" transition | cond-barrel front | blade occupies | room left for brush | lance tip 2.24 / 2.44 / 2.64 vs cond-barrel front")
for t in (0.2, 0.3, 0.4, 0.5):
    cbf = box + t
    brush = t - blade
    rel = [lt - cbf for lt in (2.24, 2.44, 2.64)]
    print(f"   {t:4.2f}     |      {cbf:4.2f}        | {box:4.2f}-{box+blade:4.2f}     |   {brush:+5.2f} mm        | "
          + "  ".join(f"{r:+5.2f}" for r in rel))
print("-> positive lance values: the lance tip sits BEHIND the conductor barrel's front edge,")
print("   i.e. over the die if the die's front face is flush with that edge. In hand use the")
print("   lance must hang just in front of the anvil face (or in a relief), within a few tenths.")
print("   The neck holds four things inside ~0.2-0.5 mm of Y: box shoulder, blade, brush, lance tip.")

# ---------------------------------------------------------------------------
hr("2. Drawing a crimped contact rearward (-Y) out of the open nest")
# the lance is a barb that resists -Y; it hangs below the barrel floor, just in front of the anvil face
print("Lift needed (Z, away from the anvil) before a rearward draw clears the lance:")
print(" anvil cradle depth [assumption] | lance proud | margin | lift before drawing back")
for cradle in (0.2, 0.4, 0.6):
    for lance in (0.6, 0.9):
        print(f"            {cradle:3.1f} mm             |   {lance:3.1f} mm   |  0.2   |   {cradle+lance+0.2:4.2f} mm")
print("Open-nest passage (a2 load step, a2b drop): end-view height the gap must pass")
for wing_h in (2.75, 3.20):
    for lance in (0.6, 0.9):
        print(f"  open insulation wings {wing_h:4.2f} tall + lance {lance:3.1f} below floor = {wing_h+lance:4.2f} mm"
              f"  (a2 assumes ~3.5 mm)")

# ---------------------------------------------------------------------------
hr("3. Gravity against the lance (a2b)")
m = 0.043e-3  # kg, LCSC listing [xh-facts §1]
W = m * 9.81
print(f"contact weight = {W*1000:.2f} mN")
for fold in (1.0, 3.0, 5.0):  # [estimate] force to fold a lance on a ramp, well under the 14.7 N insertion max analog
    print(f"  lance fold force {fold:3.1f} N [estimate] = {fold/W:,.0f} x the contact's weight")
print("-> a falling contact cannot fold its own lance; the chute must keep the lance off the")
print("   anvil for the whole drop, and anything the lance touches stops the contact.")

# ---------------------------------------------------------------------------
hr("4. Proof pull with the contact sitting low in the nest (a2 step 8, a3 step 5)")
ret = 14.7  # N, Molex Mini-SPOX retention min, used as the XH analog [into-the-housing calc §6]
for p in (19.6, 23.5):
    print(f"  proof pull {p:4.1f} N = {p/ret:4.2f} x the analog lance retention minimum ({ret} N)")
print("-> if the lance tip meets the anvil face before the box shoulder meets the blade,")
print("   the lance carries a load above what a housing ever asks of it.")

# ---------------------------------------------------------------------------
hr("5. a2c: inserting one contact at a time from a head that holds the web")
# XHP height 7.75 [mfr S2]; front wall 0.4-0.8 [assumption, i2 calc §4]; approach standoff 0.5
EI_soft, EI_stiff = 14.5, 18.1  # N*mm^2 [into-the-housing calc §1]
print(" travel to seat (box nose from rear face to front wall) + 0.5 mm approach:")
for fw in (0.4, 0.8):
    print(f"   front wall {fw}: travel = {7.75 - fw + 0.5:4.2f} mm")
print(" If the head (web) advances by that travel, every already-seated neighbour bows:")
print("   free length c | travel f | arch height h = sqrt(3 c f / 8) | Euler force to hold the bow (K=0.5)")
for c in (20, 25, 30, 35):
    for f in (7.45, 7.85):
        h = math.sqrt(3 * c * f / 8)
        P1 = math.pi**2 * EI_soft / (0.5 * c)**2
        P2 = math.pi**2 * EI_stiff / (0.5 * c)**2
        print(f"      {c:3d} mm     | {f:4.2f} mm |          {h:4.1f} mm            |   {P1:4.2f}-{P2:4.2f} N")
print("-> the latch is not threatened (under 1.5 N) but every seated conductor swings ~7-10 mm")
print("   into the working space on every push. Worse: once conductor 1 is latched in a housing")
print("   held by the fixed nest, the head can no longer carry the ribbon to the stripper or the")
print("   crimper (stations tens of mm apart; the split is 25-35 mm). The per-conductor order")
print("   strip k -> crimp k -> insert k stops after k = 1.")

# ---------------------------------------------------------------------------
hr("6. Permanent set from lifting or offsetting one conductor (a2 fork, a3 lifter)")
E = 117e3  # MPa copper
d = 0.08   # mm strand
print(" strand yield | yield strain | radius at which a strand yields")
ry = {}
for sy in (60, 120, 250):
    ey = sy / E
    ry[sy] = d / (2 * ey)
    print(f"   {sy:3d} MPa    |  {ey*1e4:4.1f}e-4    |  {ry[sy]:5.1f} mm")
print(" (annealed tinned strands, JST's wire class, sit near the 60-70 MPa rows: ~67-78 mm; the digest uses ~67 mm)")
print()
print(" Cantilever lift h at the tip of free length L: root radius = L^2/(3h); axial pull-back 0.6 h^2/L")
print("   L (mm) | h (mm) | root radius | yields at 60 / 120 / 250 MPa | tip pull-back")
for L in (20, 25, 30, 35):
    for h in (3, 6, 9, 12, 16, 20):
        r = L**2 / (3 * h)
        flags = " / ".join("yes" if r < ry[s] else "no " for s in (60, 120, 250))
        print(f"    {L:3d}   |  {h:3d}   |  {r:6.1f} mm  |        {flags}        |  {0.6*h*h/L:4.2f} mm")
print("-> lifts above ~3-5 mm on a 20-35 mm split set annealed strands. The conductor comes")
print("   back with a kink; if it springs back only partly, its tip (and contact) sits short by")
print("   a fraction of the pull-back, up to ~1-2 mm at 9-16 mm lifts: outside a +/-0.3 mm")
print("   gang-push front line unless the fronts are squared afterwards.")

# ---------------------------------------------------------------------------
hr("7. a3's row: free conductor between comb face and the contact's rear, under a gang push")
stick = 8.0  # mm, stripped tip proud of the comb face [a3]
strip = 2.4  # JST
print(" insulation barrel length [estimate 0.8-1.5] -> free length from comb face to contact rear")
for ib in (0.8, 1.2, 1.5):
    free = stick - strip - ib
    print(f"   {ib:3.1f} mm -> {free:4.1f} mm free")
print(" Euler limits from into-the-housing calc §1 at 14.7 N: K=2 1.56-1.74, K=1 3.1-3.5, K=0.5 6.2-7.0 mm")
print("                                          at  8.0 N: K=2 2.1-2.4,  K=1 4.2-4.7, K=0.5 8.5-9.5 mm")
print("-> 4-5 mm free buckles unless the nose is held square (K~0.5) or a clamp closes right")
print("   behind each insulation crimp after the crimping is done.")

# ---------------------------------------------------------------------------
hr("8. a3 tip-down: the crimp is made rolled 90 degrees from the insertion orientation")
print(" Jaws close in X, the row runs in X: the barrels open in X, the lance points along X.")
for bh in (2.2, 2.4):
    print(f"  rolled box height {bh} now lies across the row: gap to the next box at 2.5 mm pitch = {2.5-bh:4.2f} mm")
print("  (the row still fits physically; every lance points sideways instead of toward the window face)")
print()
print(" Twisting each conductor 90 degrees back (or before the crimp) over its free length L:")
th = math.pi / 2
for L in (20, 25, 30, 35):
    g = (d / 2) * th / L                  # strand torsion shear strain at its surface
    r_out = 0.35                          # mm, outer strand radius in a ~0.72 mm bundle
    helix = 0.5 * (r_out * th / L) ** 2   # axial strain of the outer strand as a helix
    print(f"   L {L:2d} mm: strand surface shear {g*1e4:4.1f}e-4 vs yield ~{(60/1.732)/44e3*1e4:3.1f}e-4 (60 MPa)"
          f" / {(250/1.732)/44e3*1e4:4.1f}e-4 (250 MPa); outer-strand helix strain {helix*1e4:4.2f}e-4")
print("-> the strands take a partial torsional set; how much roll remains after release is")
print("   the silicone-torsion unknown already open in i1. The cavity lead-in squares perhaps")
print("   +/-10-15 degrees [estimate].")

# ---------------------------------------------------------------------------
hr("9. a5: how gentle can the insulation crimp be and still fit the cavity?")
OD = 1.7
A = math.pi / 4 * OD**2
wall = 0.20
print(f" silicone conductor area {A:.2f} mm^2 (OD {OD}); barrel stock {wall} mm")
for die_w in (1.8, 1.9, 1.95):
    inner_w = die_w - 2 * wall
    inner_h = A / (math.pi / 4 * inner_w)   # oval of the same area, silicone ~incompressible
    outer_h = inner_h + 2 * wall
    print(f"  closed width {die_w:4.2f}: inner {inner_w:4.2f} -> oval height {inner_h:4.2f}, "
          f"closed height {outer_h:4.2f} mm vs 2.4 envelope ({2.4-outer_h:+4.2f})")
print("-> on 1.7 mm silicone the closed insulation barrel is at the XH end-view envelope")
print("   (1.95 x 2.4 [mfr S1]) even with no compression: a 'gentle' second squeeze has ~0.1 mm")
print("   of height to spare, and a wing tip that does not tuck spends it. Silicone that flows")
print("   out of the short barrel lowers the height [assumption]; the cavity's own rear-entry")
print("   size is unmeasured.")

# ---------------------------------------------------------------------------
hr("10. Pusher at the cavity for a2c's finger")
for cav in (2.0, 2.1):
    for slot in (1.35, 1.45, 1.55):
        tine = (cav - 0.05 - slot) / 2
        print(f"  cavity {cav}: slot {slot} -> tine {tine:4.2f} mm each side")
print("  a2c's '~0.4 mm per tine' around a 1.45 slot = 2.25 mm wide: does not enter a 2.0-2.1 cavity.")
print("  The last 0.2-1.25 mm of the push is inside the cavity [i2 calc §4].")

# ---------------------------------------------------------------------------
hr("11. Electrical identity at the gang push: far-end block x wired header")
for n in (4, 7, 9):
    for t_us in (5, 20):
        scan = n * n * t_us * 1e-6
        print(f"  {n} conductors x {n} posts, {t_us:2d} us per read: full scan {scan*1e3:5.2f} ms"
              f" -> {0.2*scan*1e3:6.3f} um of push per scan at 0.2 mm/s")
print("-> every contact's arrival on its post is timed to well under a micron of housing travel.")

# ---------------------------------------------------------------------------
hr("12. Gang push: where the force belongs")
for n in (4, 5, 7, 9):
    print(f"  {n} contacts x 3-25 N = {3*n}-{25*n} N")
T, eta, lead = 0.3, 0.3, 2.0
print(f"  NEMA 17 at {T} N*m on a {lead:.0f} mm lead screw, efficiency {eta}: {2*math.pi*T*eta/(lead/1000):.0f} N")
print("-> a fixture-mounted screw pushes J1; a belt gantry axis ('tens of N', a3) does not.")

# ---------------------------------------------------------------------------
hr("13. A C-frame die set whose lower arm reaches over the row (a4 + a3)")
for F in (1500, 3000):
    for L in (7, 10):
        for w in (6, 8):
            t = math.sqrt(6 * F * L / (w * 1000))   # sigma_allow 1000 MPa, hardened steel
            lift = t + 0.85 + 0.5 + 0.5  # arm + neighbour half-OD + floor-to-axis + clearance
            print(f"  {F/1000:3.1f} kN at {L:2d} mm, arm {w} mm wide: thickness >= {t:4.2f} mm -> conductor lift ~{lift:4.1f} mm")
print("-> ~5-7 mm of lift, with the barrels opening away from the ribbon plane (insertion")
print("   orientation), independent of where an SN nest sits on its jaw. By section 6 a 5-7 mm")
print("   lift on a 25-35 mm split still sets annealed strands a little.")

# ---------------------------------------------------------------------------
hr("14. a2b: does its own weight straighten a hanging split conductor?")
# copper 0.302 mm^2 x 8.96 g/cm^3; silicone ~1.9 mm^2 x ~1.15 g/cm^3 [estimate]
lin = 0.302 * 8.96e-3 + 1.9 * 1.15e-3   # g/mm
print(f" linear mass ~{lin*1000:.1f} mg/mm [estimate]")
for L in (25, 35):
    w = lin * 1e-3 * 9.81                # N/mm
    print(f"  {L} mm of split conductor weighs {w*L*1000:.1f} mN; as a horizontal cantilever its own"
          f" weight makes {w*L*L/2:.3f} N*mm at the root")
for r in (20, 40, 67):
    print(f"  holding a {r} mm radius elastically takes EI/r = {EI_soft/r:.2f}-{EI_stiff/r:.2f} N*mm")
print("-> gravity is ~2-13 % of the moments in play, and a bend the copper has set has no")
print("   restoring moment at all. The hanging tip goes where its history puts it; the fork and")
print("   a close guide set its line, not its weight.")

# ---------------------------------------------------------------------------
hr("15. How thin can a crimp punch's side wall be? (a4 narrowed dies; i1b, i2 narrow punch)")
# wall = cantilever of height H (crimp height) loaded by lateral pressure k*p over its height
H = 0.9
print(" die pressure p [xh-facts §4 400-900 MPa] x lateral ratio k [assumption 0.4-1.0]; H = 0.9 mm")
print("   k*p (MPa) | wall 0.25 | 0.45 | 0.70 | 1.00 mm  -> bending stress (MPa); hardened steel ~1500-2000 working")
for kp in (160, 360, 600, 900):
    row = [3 * kp * H * H / t**2 for t in (0.25, 0.45, 0.70, 1.00)]
    print(f"     {kp:4d}    | " + " | ".join(f"{s:6.0f}" for s in row))
for kp in (160, 360, 600, 900):
    tmin = math.sqrt(3 * kp * H * H / 1750)
    print(f"   k*p {kp:3d}: wall >= {tmin:4.2f} mm -> punch around a 1.9 mm crimp >= {1.9 + 2*tmin:4.2f} mm wide")
print("-> in-row crimping at 2.5 mm pitch (3.3 mm free between neighbour wires) only works at")
print("   the gentle end of the range; a one-nest die 6-8 mm wide, fit for a 5 mm shuttle pitch")
print("   (8.3 mm free), carries it with room to spare.")
