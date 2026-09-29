"""Force versus punch position for one XH crimp (SXH-001T-P0.6 on 22 AWG ribbon).

force-and-form explorer, jst-crimp-study, 2026-09-28.
Run:  python3 stroke_model.py > stroke_model.out.txt

Inputs come from ../../../context/xh-facts.md and its calc (C1):
  - peak conductor force at bottom dead centre (BDC) 0.75-2.3 kN   [calc C1 est.]
  - insulation wing forming 33-132 N                              [calc C1 est.]
  - carrier cut-off shear 48-158 N (only when cut in the stroke)  [calc C1 est.]
  - punch travel from first wing-tip touch to BDC ~0.92 mm         [calc C1 est.]
  - compaction happens in the last ~0.10-0.20 mm                   [calc C1 est.]
Everything else is labelled where it appears. The model is a family of shapes,
not a prediction: the point is which drive loads come out of which part of the
stroke, and which conclusions survive every shape in the family.

s = height of the conductor punch above its BDC position (mm). s = 0 at BDC.
"""
from math import exp

TRAVEL = 0.92          # mm, first wing-tip touch to BDC            [calc C1]


def f_conductor(s, F_peak, s_c, n, F_curl):
    """Conductor barrel force (N) at height s above BDC.

    curl phase (s_c < s < TRAVEL): wings ride the punch arches and curl; force
      rises linearly from ~0.2*F_curl to F_curl                 [estimate]
    compaction (0 <= s <= s_c): strands and wings are squeezed; power law from
      F_curl up to F_peak at BDC                                  [estimate, shape]
    """
    if s >= TRAVEL:
        return 0.0
    if s > s_c:
        frac = (TRAVEL - s) / (TRAVEL - s_c)
        return F_curl * (0.2 + 0.8 * frac)
    x = (s_c - s) / s_c
    return F_curl + (F_peak - F_curl) * x ** n


def f_insulation(s, F_ins):
    """Insulation barrel: taller wings touch first, form over ~1 mm, and finish
    near the same BDC (stepped punch)                               [estimate]"""
    s_touch = TRAVEL + 0.6     # insulation wings stand ~0.6 mm taller   [estimate]
    if s >= s_touch or s < 0:
        return 0.0
    return F_ins * min(1.0, (s_touch - s) / 0.8)


def f_cutoff(s, F_cut, s_cut=0.45, width=0.25):
    """Carrier cut-off shear, only in an applicator-style stroke; a short force
    blip at a set point in the stroke                               [estimate]"""
    return F_cut if (s_cut - width / 2) <= s <= (s_cut + width / 2) else 0.0


CASES = {
    #            F_peak  s_c   n   F_curl F_ins F_cut
    "low":      (750.0, 0.10, 2.0, 120.0, 33.0, 0.0),
    "central":  (1600.0, 0.15, 2.5, 200.0, 80.0, 0.0),
    "high":     (2300.0, 0.20, 3.0, 300.0, 132.0, 0.0),
    "high+cut": (2300.0, 0.20, 3.0, 300.0, 132.0, 158.0),
    "steep":    (2300.0, 0.10, 4.0, 300.0, 132.0, 0.0),
}


def total_force(s, case):
    F_peak, s_c, n, F_curl, F_ins, F_cut = CASES[case]
    return (f_conductor(s, F_peak, s_c, n, F_curl) + f_insulation(s, F_ins)
            + f_cutoff(s, F_cut))


def profile(case, ds=0.001, s_max=1.6):
    pts = []
    s = s_max
    while s >= -1e-9:
        pts.append((round(s, 4), total_force(max(s, 0.0), case)))
        s -= ds
    return pts


if __name__ == "__main__":
    print("=" * 76)
    print("1. Force at chosen heights above BDC (N), each case in the family")
    print("=" * 76)
    heights = [1.4, 1.0, 0.8, 0.6, 0.4, 0.3, 0.2, 0.15, 0.10, 0.05, 0.02, 0.0]
    print("s (mm)   " + "".join(f"{c:>10s}" for c in CASES))
    for s in heights:
        print(f"{s:6.2f}   " + "".join(f"{total_force(s, c):10.0f}" for c in CASES))

    print()
    print("=" * 76)
    print("2. Work per crimp and where it is spent")
    print("=" * 76)
    for c in CASES:
        pts = profile(c)
        W = 0.0
        W_last = 0.0
        for (s1, f1), (s2, f2) in zip(pts, pts[1:]):
            dW = 0.5 * (f1 + f2) * (s1 - s2) * 1e-3   # J
            W += dW
            if s1 <= 0.2:
                W_last += dW
        print(f"{c:9s}: {W:.3f} J total, {W_last:.3f} J ({100*W_last/W:.0f} %) in the last 0.2 mm")

    print()
    print("=" * 76)
    print("3. What a slow stroke changes (bounded, each with its label)")
    print("=" * 76)
    # [source] CuFe2P copper-alloy sheet: tensile strength rises ~5-7.7 % from
    # 0.0002 /s (0.01 mm/s) to 5.65 /s; crimp tools travel up to 0.5 m/s.
    # https://pmc.ncbi.nlm.nih.gov/articles/PMC11242886/
    for label, rise in (("5 %", 0.05), ("7.7 %", 0.077)):
        print(f"flow stress at press speed is ~{label} above quasi-static -> a slow stroke "
              f"needs ~{100*rise/(1+rise):.1f} % less peak force for the same geometry")
    # springback of the crimp itself ~ sigma_y/E-like: scales with flow stress
    print("elastic springback scales with flow stress/E: a few % smaller when slow "
          "(a thousandth of a mm on ~0.01-0.03 mm) [estimate]")
    # temperature rise if all work stays in the contact and strands
    m_contact, m_cu = 0.043e-3, 0.0302 * 2.4 * 8.96e-3 * 1e-3  # kg; 2.4 mm strip of 0.302 mm^2
    cp = 385.0                                                 # J/kg K, copper/bronze
    for c in ("central", "high"):
        pts = profile(c)
        W = sum(0.5 * (f1 + f2) * (s1 - s2) * 1e-3 for (s1, f1), (s2, f2) in zip(pts, pts[1:]))
        dT = W / ((m_contact + m_cu) * cp)
        print(f"{c}: adiabatic upper bound on temperature rise {dT:.0f} K "
              "(at production speed); a stroke of seconds conducts it away [calc]")
    # stroke speed examples
    for t_stroke in (0.1, 1.0, 10.0, 60.0):
        v = TRAVEL / t_stroke
        print(f"forming travel {TRAVEL} mm in {t_stroke:5.1f} s -> {v:8.3f} mm/s "
              f"(production press ~ {0.5e3:.0f} mm/s peak)")
    print("inertia: a crank press reaches BDC with ram and flywheel momentum; a slow "
          "drive reaches it quasi-statically, so BDC is set only by geometry and "
          "stiffness [estimate]")

    print()
    print("=" * 76)
    print("4. Force/position sensitivity near BDC (matters for stopping rules)")
    print("=" * 76)
    for c in CASES:
        f0 = total_force(0.0, c)
        f1 = total_force(0.01, c)
        f5 = total_force(0.05, c)
        print(f"{c:9s}: F(0)={f0:5.0f} N  F(0.01)={f1:5.0f} N  F(0.05)={f5:5.0f} N  "
              f"slope near BDC ~{(f0-f1)/0.01/1000:5.1f} kN/mm")
    print("-> a stop-at-force rule and a stop-at-position rule differ; see metrology.py")
