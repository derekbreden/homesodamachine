"""What each slow drive has to deliver through the XH crimp stroke.

force-and-form explorer, jst-crimp-study, 2026-09-28.
Run:  python3 drives.py > drives.out.txt

Uses the force family in stroke_model.py. For each drive, the demand at the
input (torque or force) is the crimp force times the drive's local velocity
ratio ds/d(input), maximised over the whole stroke. Also how far the bottom of
the stroke moves when the input is off by a given amount ("BDC sensitivity").
Part data carry labels; sources are in ../ideas/.
"""
from math import sin, cos, sqrt, pi, radians, degrees, asin
from stroke_model import total_force, CASES

S_MAX = 1.6   # mm above BDC where the model force is ~0


def crank(e, Lc, case, extra=0.0):
    """Eccentric (radius e) and connecting link Lc driving a ram.
    Returns (max torque N*m, angle from BDC deg, s mm there)."""
    best = (0.0, 0.0, 0.0)
    th = 0.0
    while th < pi:
        y = e * (1 - cos(th)) + Lc - sqrt(Lc * Lc - (e * sin(th)) ** 2)
        dy = e * sin(th) + (e * e * sin(th) * cos(th)) / sqrt(Lc * Lc - (e * sin(th)) ** 2)
        F = total_force(y, case) + extra
        T = F * dy / 1000.0          # N*mm -> N*m
        if T > best[0]:
            best = (T, degrees(th), y)
        th += radians(0.05)
    return best


def crank_bdc_error(e, Lc, dth_deg):
    th = radians(dth_deg)
    return e * (1 - cos(th)) + Lc - sqrt(Lc * Lc - (e * sin(th)) ** 2)


def toggle(L, case):
    """Symmetric two-link toggle, links L, knee pushed sideways by x.
    Ram height above BDC s = 2L - 2*sqrt(L^2 - x^2). Knee force = F*ds/dx.
    Returns (max knee force N, x mm, s mm there, x needed to open 5 mm)."""
    best = (0.0, 0.0, 0.0)
    x = 0.0
    while True:
        s = 2 * L - 2 * sqrt(L * L - x * x)
        if s > S_MAX:
            break
        dsdx = 2 * x / sqrt(L * L - x * x)
        F = total_force(s, case) * dsdx
        if F > best[0]:
            best = (F, x, s)
        x += 0.005
    x_open = sqrt(L * L - (L - 2.5) ** 2)   # s = 5 mm opening for loading
    return best + (x_open,)


def screw_force(T, lead_mm, eta):
    return 2 * pi * T * eta / (lead_mm / 1000.0)


if __name__ == "__main__":
    print("=" * 78)
    print("A. Eccentric crank (the shape of a mini-applicator press, run slowly)")
    print("=" * 78)
    print("e = crank radius (stroke = 2e); Lc = link length. Extra = applicator springs,")
    print("feed cam and hold-down, 0-150 N added over the whole stroke [estimate].")
    for e, Lc in ((15.0, 60.0), (20.0, 80.0)):
        for case in ("central", "high", "high+cut", "steep"):
            for extra in (0.0, 150.0):
                T, th, y = crank(e, Lc, case, extra)
                print(f"stroke {2*e:.0f} mm, {case:8s}, extra {extra:3.0f} N: peak crank torque "
                      f"{T:5.2f} N*m at {th:5.1f} deg from BDC (ram {y:.3f} mm up)")
    print()
    print("BDC sensitivity of a crank (ram height error from crank angle error):")
    for e, Lc in ((15.0, 60.0), (20.0, 80.0)):
        for d in (0.5, 1.0, 2.0, 5.0):
            print(f"  stroke {2*e:.0f} mm, {d:3.1f} deg off BDC -> ram {1000*crank_bdc_error(e, Lc, d):6.2f} um high")
    print()
    print("Drive options for the crank (output torque available):")
    # [source] StepperOnline 23HS30-2804S-RVS30-G30: NEMA 23 1.9 N*m holding,
    # 30:1 worm NMRVS30, 65 % efficiency, 20 N*m max permissible output, self-locking.
    T_motor = 1.9 * 0.6            # running torque at low speed ~60 % of holding [estimate]
    for ratio in (30, 50):
        T_out = min(T_motor * ratio * 0.65, 20.0)
        print(f"  NEMA 23 (~{T_motor:.1f} N*m running) + {ratio}:1 worm (65 %): "
              f"{T_motor*ratio*0.65:5.1f} N*m, capped at the 20 N*m gearbox rating -> {T_out:.1f} N*m")
    print("  -> every case above needs well under 10 N*m at the crank: a slow crank press")
    print("     is inside the rating of a NEMA 23 + worm with margin.")
    rpm = 2.0
    print(f"  at {rpm} rpm the crank makes one crimp every {60/rpm:.0f} s")

    print()
    print("=" * 78)
    print("B. Toggle (knee) linkage: knee force needed, BDC set by the straight links")
    print("=" * 78)
    for L in (20.0, 30.0, 40.0):
        for case in ("central", "high", "high+cut", "steep"):
            F, x, s, x_open = toggle(L, case)
            print(f"L={L:4.0f} mm, {case:8s}: peak knee force {F:6.0f} N at x={x:5.2f} mm "
                  f"(ram {s:.3f} mm up); knee moves {x_open:4.1f} mm to open 5 mm")
    print()
    print("BDC sensitivity of a toggle: ram height s = x^2/L near straight")
    for L in (20.0, 30.0, 40.0):
        for x in (0.1, 0.2, 0.5):
            s = 2 * L - 2 * sqrt(L * L - x * x)
            print(f"  L={L:4.0f} mm, knee {x:3.1f} mm short of straight -> ram {1000*s:6.2f} um high")
    print()
    print("What can push the knee (force available):")
    print(f"  NEMA 17 ~0.4 N*m, 2 mm lead trapezoid (eta 0.3): {screw_force(0.4, 2, 0.30):5.0f} N")
    print(f"  NEMA 17 ~0.4 N*m, 8 mm lead trapezoid (eta 0.5): {screw_force(0.4, 8, 0.50):5.0f} N")
    for kgcm, arm in ((25, 25.0), (60, 25.0), (60, 40.0)):
        T = kgcm * 9.81 / 100.0
        print(f"  hobby servo {kgcm} kg*cm ({T:.1f} N*m) on a {arm:.0f} mm arm: {T/(arm/1000):5.0f} N")
    for bore in (25.0, 32.0):
        for p_psi in (60, 90):
            p = p_psi * 6894.76 / 1e6
            A = pi * bore ** 2 / 4
            print(f"  air cylinder {bore:.0f} mm bore at {p_psi} psi: {p*A:5.0f} N")

    print()
    print("=" * 78)
    print("C. Direct screw (no linkage): force at the die equals screw thrust")
    print("=" * 78)
    for name, T, lead, eta in (("NEMA 23 1.9 N*m, 2 mm trapezoid", 1.9, 2.0, 0.30),
                               ("NEMA 23 1.9 N*m, 1605 ball screw (5 mm)", 1.9, 5.0, 0.90),
                               ("NEMA 23 + 5:1 belt, 1605 ball screw", 1.9 * 5 * 0.95, 5.0, 0.90),
                               ("NEMA 17 0.4 N*m, 2 mm trapezoid", 0.4, 2.0, 0.30)):
        print(f"  {name:42s}: {screw_force(T*0.6, lead, eta)/1000:5.2f} kN at 60 % of holding torque")
    print("  BDC sensitivity: 1:1. A lost step or frame stretch moves BDC directly.")
    print("  2 mm lead, 200 full steps: 10 um/step; with 1/16 microstepping 0.6 um nominal,")
    print("  but microstep position under kN load is not trustworthy [estimate]. A direct")
    print("  screw needs a hard stop or a gauge on the die to set crimp height.")

    print()
    print("=" * 78)
    print("D. Arbor press (rack and pinion) driven at its handle")
    print("=" * 78)
    # [source] Harbor Freight Central Machinery 1 t arbor press #59766: $79.99,
    # "20:1 leverage", 2,000 lb, 5-1/2 in max height, 29.6 lb.
    lev = 20.0
    for F_act in (500.0, 1000.0, 1500.0):
        print(f"  {F_act:5.0f} N pushed at the handle end (20:1): {F_act*lev/1000:5.1f} kN at the ram "
              "(if pushed square to the handle)")
    r_handle = 250.0      # mm, handle radius [assumption]
    r_pinion = r_handle / lev
    for stroke_act in (50.0, 100.0):
        ang = stroke_act / r_handle
        print(f"  actuator stroke {stroke_act:.0f} mm at a {r_handle:.0f} mm handle radius -> pinion turns "
              f"{degrees(ang):4.1f} deg -> ram moves {ang*r_pinion:4.1f} mm (pinion radius {r_pinion:.1f} mm, assumed)")
    print("  No geometric BDC: rack position follows the handle 1:1 through the pinion.")
    print("  -> the crimp height has to come from a hard stop at the die, not from the drive.")

    print()
    print("=" * 78)
    print("E. A ratchet hand tool closed by a linear actuator (tool's own linkage)")
    print("=" * 78)
    print("  The SN-2549's handle-to-die ratio is not published; compound-toggle ratchet")
    print("  crimpers are commonly quoted 15-40:1 near closure [estimate]. Handle force:")
    for MA in (10.0, 15.0, 25.0, 40.0):
        for case in ("central", "high"):
            F = total_force(0.0, case)
            print(f"   MA {MA:4.0f}:1, {case:7s}: {F/MA:5.0f} N at the handle grip point")
    print("  A 12 V actuator rated 500-1500 N covers every row with margin; its stroke")
    print("  needs to cover the handle's grip-point travel, ~40-60 mm [estimate].")
