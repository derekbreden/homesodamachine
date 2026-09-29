"""Numbers for hand-tool-as-press's wave-2 exchange on procedure-is-the-machine.

Run: python3 exchange_procedure.py > exchange_procedure.out.txt

1. Copper set in conductors pressed down by p1/p5's slotted presser (every neighbour, N-1
   times) and lifted once by a lifter (p2's selector, a3's lifter): residual deflection and
   tip pull-back after release, elastic-plastic strands plus an elastic silicone tube.
2. What sits behind the strip line on a side-feed contact: where p1/p5's fork (3 mm behind
   the strip line) lands relative to the tab, carrier and shear.
3. p4's proof pull taken while the punch still holds the crimp at bottom dead centre:
   friction from die clamping against the 15-20 N proof load.
4. p5 with a die stop and a disc-spring stack: crimp height scatter, and shaft torque, as a
   function of frame stiffness.
5. p5 driving a hand tool's handle from the camshaft (combination p5 x a1): torque and cam
   size for a squeeze lobe.
6. Axial chain (insulation edge in the window) with the contact's own reference added, and
   with a camera-measured bare length corrected by a Y move.
7. p4 cycle with a hand-tool head, and the person's wait with one or two heads.

Sources: strands 60 x 0.08 mm tinned copper [digest wave 1]; E_Cu 115 GPa; annealed strand
yield 60-120 MPa (the digest's ~67 mm set radius corresponds to ~65 MPa) [estimate];
silicone tube I = 0.397 mm^4, E 2-6 MPa [study: ribbon-as-pallet calc/pallet_geometry];
clone contact dimensions [xh-facts §1]; crimp force 0.8-2.6 kN, compaction last 0.10-0.20 mm
[xh-facts §4]; p5 eccentric e = 2.5 mm, NEMA 17 + 30:1 worm 3.1 N*m, NEMA 17 + 50:1 4.5 N*m
[study: procedure-is-the-machine calc/cam_drive]; handle force <= 220 N and 15-40x gain
near closure [calc hand_tool_press §1, §4].
"""

import math

E_CU = 115000.0      # MPa
D_STRAND = 0.08      # mm
N_STRAND = 60
I_SIL = 0.397        # mm^4, silicone tube (ribbon-as-pallet)


def hr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


# ---------------------------------------------------------------- section 1 helpers
def strand_moment(kappa, sy, n=161):
    """Moment of one circular elastic-perfectly-plastic strand at curvature kappa (1/mm)."""
    r = D_STRAND / 2
    m = 0.0
    dy = 2 * r / n
    for i in range(n):
        y = -r + (i + 0.5) * dy
        b = 2 * math.sqrt(max(r * r - y * y, 0.0))
        s = max(-sy, min(sy, E_CU * kappa * y))
        m += s * y * b * dy
    return m


def bundle_moment(kappa, sy, e_sil):
    return N_STRAND * strand_moment(kappa, sy) + e_sil * I_SIL * kappa


def ei_total(e_sil):
    ei_cu = N_STRAND * E_CU * math.pi * D_STRAND ** 4 / 64
    return ei_cu + e_sil * I_SIL


def kappa_of_moment(m, sy, e_sil):
    lo, hi = 0.0, 5.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if bundle_moment(mid, sy, e_sil) < m:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def cantilever(L, F, sy, e_sil, n=120):
    """Tip load F on a cantilever of free length L; returns (tip deflection loaded,
    residual tip deflection, residual axial pull-back) in small-deflection theory."""
    dx = L / n
    kap, kres = [], []
    eit = ei_total(e_sil)
    for i in range(n):
        x = (i + 0.5) * dx
        m = F * (L - x)
        k = kappa_of_moment(m, sy, e_sil)
        kap.append(k)
        kres.append(max(k - m / eit, 0.0))
    def tip(ks):
        d = 0.0
        for i, k in enumerate(ks):
            x = (i + 0.5) * dx
            d += k * (L - x) * dx
        return d
    def pullback(ks):
        th, pb = 0.0, 0.0
        for k in ks:
            th += k * dx
            pb += 0.5 * th * th * dx
        return pb
    return tip(kap), tip(kres), pullback(kres)


def solve_F(L, delta, sy, e_sil):
    lo, hi = 0.0, 10.0
    for _ in range(50):
        mid = (lo + hi) / 2
        d, _, _ = cantilever(L, mid, sy, e_sil, n=60)
        if d < delta:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main():
    hr("1. Copper set: a conductor pressed down (p1/p5 presser) or lifted (p2 selector, a3 lifter)")
    for sy in (60.0, 120.0):
        mp = N_STRAND * strand_moment(10.0, sy)
        ky = 2 * sy / (E_CU * D_STRAND)
        print(f"strand yield {sy:.0f} MPa: yield radius {1/ky:5.1f} mm, bundle plastic moment {mp:.2f} N*mm")
    print("EI copper (strands free to slip) %.1f N*mm^2; silicone 2-6 MPa adds %.1f-%.1f"
          % (ei_total(0), 2 * I_SIL, 6 * I_SIL))
    print()
    print("Cantilever from the comb face (free length L), tip pushed a distance delta, released.")
    print("Small-deflection theory, so figures at delta/L > 0.4 are rough [estimate].")
    print(f"{'L mm':>5}{'delta':>7}{'sy MPa':>8}{'E_sil':>7}{'F mN':>7}{'resid mm':>10}{'kept %':>8}{'pull-back mm':>14}")
    for L in (10, 15, 20, 30):
        for delta in (4.0, 7.0):
            for sy in (60.0, 120.0):
                for es in (2.0, 6.0):
                    F = solve_F(L, delta, sy, es)
                    d, dr, pb = cantilever(L, F, sy, es)
                    print(f"{L:>5}{delta:>7.1f}{sy:>8.0f}{es:>7.0f}{1000*F:>7.0f}{dr:>10.2f}"
                          f"{100*dr/d:>8.0f}{pb:>14.2f}")
    print("-> below ~30 mm of free length a 4-7 mm press or lift keeps most of itself: the")
    print("   conductor comes back down (or up) by several millimetres and its tip sits short by")
    print("   a few tenths to over a millimetre. In p1/p5 every conductor is pressed down N-1")
    print("   times before its own turn (8 times on J1's ninth key); in p2/a3 each is lifted")
    print("   once, just before its own crimp.")

    hr("2. What lies behind the strip line on a side-feed contact (p1/p5 fork at 3 mm)")
    print("clone dimensions [xh-facts §1]: window 0.5-0.8, insulation barrel 0.8-1.5, tab 0.7-1.15")
    for win, ib, tab in ((0.5, 0.8, 0.7), (0.65, 1.15, 0.9), (0.8, 1.5, 1.15)):
        ib_front = win / 2
        ib_rear = ib_front + ib
        carrier = ib_rear + tab
        print(f"  window {win:.2f}, ins. barrel {ib:.2f}, tab {tab:.2f}: insulation barrel "
              f"{ib_front:.2f}-{ib_rear:.2f} mm behind the strip line; tab {ib_rear:.2f}-{carrier:.2f}; "
              f"carrier edge (shear line) at {carrier:.2f}")
    print("-> a fork 3 mm behind the strip line sits over the tab or the carrier edge, the line")
    print("   where the applicator's floating shear and its punch act [study: exchange")
    print("   borrowed-machines--on--ribbon-as-pallet, MKS-L manual]. p5 keeps the fork closed")
    print("   from 30 to 330 deg, through the punch stroke at 170-240 deg.")
    print("Free length from fork to strand tip, and the tip wander under a light 0.02 N brush")
    print("(EI 14.1-18.1 N*mm^2 [study: procedure-is-the-machine calc/selector_and_bow §4]):")
    for fork in (3.0, 5.0, 6.0):
        L = fork + 2.4
        lo = 0.02 * L ** 3 / (3 * 18.1)
        hi = 0.02 * L ** 3 / (3 * 14.1)
        print(f"  fork {fork:.0f} mm behind the strip line -> {L:.1f} mm free -> wander {lo:.2f}-{hi:.2f} mm")
    print("  lateral window: insulation into the narrowest clone insulation barrel +/-0.33 mm")

    hr("3. p4 proof pull while the punch holds the crimp at bottom dead centre")
    print("If the dies still clamp the barrels, the pull meets die friction before it meets the")
    print("crimp's own grip. Friction on the barrels = mu x residual die force.")
    print(f"{'die force held N':>18}{'mu 0.15':>10}{'mu 0.3':>10}{'mu 0.5':>10}   vs proof 15-20 N")
    for f in (50, 200, 800, 2000):
        print(f"{f:>18}{0.15*f:>10.0f}{0.3*f:>10.0f}{0.5*f:>10.0f}")
    print("-> above ~100 N of held die force, a crimp with no grip of its own passes a 20 N pull.")
    print("   Holding at the hard stop leaves most of the 0.8-2.6 kN in the loop. The pull has to")
    print("   go through the box (hook or blade in the neck, dies open), as p1 and p5 do.")

    hr("4. p5 with a die stop plus a preloaded disc-spring stack in the rod")
    print("Without a stop (p5 as written): crimp height moves by force scatter / loop stiffness.")
    for k in (5, 10, 15, 30):
        print(f"  loop {k:>2} kN/mm: +/-300 N -> +/-{0.3/k*1000:4.0f} um; +/-600 N -> +/-{0.6/k*1000:4.0f} um")
    print("With a stop: steel stop blocks beside the punch (10 x 10 mm, 30 mm long loop through")
    ks = 200000 * 100 / 30 / 1000
    print(f"  the punch holder and anvil holder) are ~{ks:.0f} kN/mm; +/-600 N -> +/-{0.6/ks*1000:.1f} um.")
    print("  The frame then only has to deliver the dies to the stop, through the crimp force.")
    print("  Die contact must happen early enough in the crank that the frame's deflection at")
    print("  crimp force (plus 0.1 mm margin into the stack) is used up before BDC:")
    e = 2.5
    F = 2600.0
    print(f"  e = {e} mm, crimp force at die closure {F/1000:.1f} kN, NEMA17+30:1 = 3.1 N*m, +50:1 = 4.5 N*m")
    print(f"{'frame kN/mm':>12}{'overtravel mm':>15}{'crank deg':>11}{'torque N*m':>12}")
    for k in (2, 5, 10, 20, 40):
        x = F / (k * 1000) + 0.10
        c = 1 - x / e
        if c < -1:
            print(f"{k:>12}{x:>15.2f}   exceeds stroke")
            continue
        th = math.acos(c)
        dhdth = e * math.sin(th)
        T = F * dhdth / 1000
        print(f"{k:>12}{x:>15.2f}{math.degrees(th):>11.0f}{T:>12.2f}")
    print("-> with a stop, crimp height no longer depends on loop stiffness. The frame still has")
    print("   to be ~10 kN/mm or stiffer for a NEMA 17 through a 50:1 worm to finish the stroke,")
    print("   because a soft frame moves the crimp force away from bottom dead centre where the")
    print("   eccentric has little advantage. The stack caps an obstruction at preload + travel.")

    hr("5. Combination p5 x a1: the camshaft squeezes a hand tool's handle")
    print("Handle need <= 220 N, rising only over the last ~8 mm of grip travel (die compaction")
    print("magnified 15-40x); approach ~45 mm at a light return-spring load (~20 N) [estimate].")
    print(f"{'lobe':>28}{'lift mm':>9}{'deg':>6}{'dr/dtheta mm/rad':>18}{'force N':>9}{'torque N*m':>12}")
    for name, lift, deg, force in (("approach", 45, 120, 20), ("squeeze", 8, 40, 220),
                                   ("squeeze, spring link 275 N", 8, 40, 275), ("squeeze, gentler", 8, 60, 220)):
        drdt = lift / math.radians(deg)
        T = force * drdt / 1000
        print(f"{name:>28}{lift:>9}{deg:>6}{drdt:>18.1f}{force:>9}{T:>12.2f}")
    print("  cam radius: base 30 mm + 53 mm lift -> ~83 mm, a ~170 mm plate cam, or a 4:1 lever")
    print("  (cam lift 13 mm at 4x the force, same torque).")
    for Lr in (8, 16):
        p = math.sqrt(275 * 5000 / (math.pi * 8 * Lr))
        print(f"  follower 16 mm dia x {Lr} mm on PET-CF (E ~5 GPa), 275 N: Hertz line contact ~{p:.0f} MPa")
    print("-> a NEMA 17 through p5's 30:1 worm (3.1 N*m) turns a squeeze lobe spread over ~40 deg;")
    print("   a PET-CF lobe is near its compressive limit under a narrow roller, so the squeeze")
    print("   lobe wants a wide roller or a steel insert. The spring link caps die force at")
    print("   ~1.25x the handle need if the tool jams (procedure-is-the-machine exchange calc §4).")

    hr("6. Axial chain: insulation edge in the window, with the contact's own reference added")
    base = {"trim blade to cassette datum": 0.05, "cassette to station": 0.05,
            "strip length (V-jaw at 2.4 mm, slug tears)": 0.20}
    contact = {"pilot hole on a pin (strip)": 0.075, "box rear shoulder on a blade": 0.08,
               "box front on a stop (loose kit contact)": 0.25}
    rss0 = math.sqrt(sum(v * v for v in base.values()))
    print(f"p1 chain without lift scatter (k is never lifted in p1): RSS +/-{rss0:.2f} mm")
    for name, v in contact.items():
        r = math.sqrt(rss0 ** 2 + v * v)
        print(f"  + contact located by {name:<40} +/-{v:.3f} -> RSS +/-{r:.2f}")
    print("with the bare length measured by the ELP camera (0.02 mm/px) and the cassette or the")
    print("tool moved in Y to put the insulation edge mid-window (strip term -> +/-0.03):")
    for name, v in contact.items():
        r = math.sqrt(0.05 ** 2 + 0.05 ** 2 + 0.03 ** 2 + v * v)
        print(f"  contact by {name:<40} -> RSS +/-{r:.2f}")
    print("  usable window about +/-0.3 mm [study: procedure-is-the-machine calc/transfer_capture §3]")
    print("-> a loose kit contact referenced by its box front uses most of the window by itself;")
    print("   the box's rear shoulder (a blade in the neck) or the pilot hole keeps it small.")
    print("   Measuring the bare length and correcting in Y removes the dominant strip term.")

    hr("7. p4 with a hand-tool head: cycle and the person's wait")
    steps = [("clamp, strip pull", 6), ("feed to touch-off", 4), ("tool approach 45 mm at 15 mm/s", 3),
             ("squeeze last 8 mm at 2 mm/s", 4), ("open", 3), ("proof pull via blade", 3),
             ("release, camera", 3)]
    t = sum(s for _, s in steps)
    for n, s in steps:
        print(f"  {n:<34}{s:>4} s")
    print(f"  machine cycle ~{t} s [estimate]")
    person = 5 + 8
    print(f"  person per conductor: present 5 s + insert 8 s = {person} s [p4's estimates]")
    for heads in (1, 2):
        cyc = t / heads
        wait = max(0, cyc - person)
        print(f"  {heads} head(s): conductor every {max(cyc, person):.0f} s, person waits {wait:.0f} s per conductor;"
              f" 53 conductors -> {53*max(cyc, person)/60:.0f} min")
    print("-> one squeezer at ~26 s keeps the person waiting ~13 s a conductor; two squeezers")
    print("   ($18-21 tools, one pusher each) alternating bring the person's own pace back.")


if __name__ == "__main__":
    main()
