"""Printed flexure knobs: range vs stiffness, remote-centre pivots at the dot,
creep, heat, resolution.  Estimates for ideas/flexure-trim-head.md.

Materials (sources / labels):
  PETG  (Bambu PETG Basic): flexural modulus XY 1670 MPa [published, cited in the repo];
        bending strength XY 75 MPa, Z 56 MPa [Bambu store page, observed 2026-09-28];
        Tg ~80 C [repo]; CTE ~65e-6/K [estimate, typical PETG].
        Long-term allowable stress for a held flexure: 8 MPa [estimate, ~10% of
        bending strength, chosen for creep/fatigue margin] -> 0.48 % strain.
  PET-GF (Polymaker Fiberon PET-GF15): E ~3500 MPa [estimate; TDS not read],
        allowable 10 MPa [estimate] -> 0.29 %; CTE ~35e-6/K [estimate].
  1095 spring steel shim (blue tempered), clamped in printed blocks:
        E 205 GPa; allowable 400 MPa [estimate, well below yield] -> 0.20 %;
        CTE 11e-6/K; no creep at room temperature.

Formulas (thin leaves, small deflection):
  leaf in pure bending (cross-spring or notch-type pivot): eps = t*theta/(2L)
  fixed-guided leaf (parallelogram): eps = 3 t delta / L^2 ; drive stiffness 2*E*b*t^3/L^3 for two leaves
  remote-centre pivot (two fixed-guided leaves aimed at a centre D away):
        the coupler end of each leaf moves ~D*theta -> eps = 3 t D theta / L^2
        stiffness about the remote centre ~ 2 * (E b t^3 / L^3) * D^2
Run: python3 flexures.py
"""
import math
import numpy as np

MATS = {
    "PETG (1.2 mm leaf)": dict(E=1670.0, eps=8 / 1670.0, t=1.2, cte=65e-6),
    "PET-GF (1.2 mm leaf)": dict(E=3500.0, eps=10 / 3500.0, t=1.2, cte=35e-6),
    "1095 shim (0.25 mm leaf)": dict(E=205000.0, eps=400 / 205000.0, t=0.25, cte=11e-6),
}
B = 20.0      # leaf width, mm


def parallelogram(E, eps, t, L, b=B, s=50.0):
    k_drive = 2 * E * b * t**3 / L**3               # N/mm
    delta = eps * L**2 / (3 * t)                    # mm range (one side)
    k_axial = 2 * E * b * t / L                     # N/mm along the leaves
    k_tilt = (E * b * t / L) * s**2 / 2             # N*mm/rad, leaves in push-pull, spacing s
    k_out = 2 * E * t * b**3 / L**3                 # N/mm out of plane
    return k_drive, delta, k_axial, k_tilt, k_out


def rcc(E, eps, t, L, D, b=B):
    theta = eps * L**2 / (3 * t * D)                # rad range
    k_theta = 2 * (E * b * t**3 / L**3) * D**2      # N*mm/rad about the remote centre
    return theta, k_theta


def fourbar_drift(D, L, sep, theta_deg):
    """Two rigid links (pseudo-rigid model, gamma 0.85) aimed at a remote centre at the
    origin from distance D, separated by `sep` at their near ends.  Turn the coupler by
    theta and report how far the coupler point that started at the origin has moved."""
    g = 0.85 * L
    # near (coupler) pivots at distance D from the origin, far (ground) pivots at D+g, along lines through the origin
    ang = math.asin(sep / 2 / D)
    dirs = [np.array([math.sin(a), -math.cos(a)]) for a in (ang, -ang)]
    Q = [D * d for d in dirs]                      # coupler pivots
    P = [(D + g) * d for d in dirs]                # ground pivots
    # coupler rigid body: points Q0, Q1 and the tracked point O=(0,0)
    th = math.radians(theta_deg)

    def residual(x):
        # x: coupler translation (tx, ty) for a given rotation th; links must keep length g
        tx, ty = x
        R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
        res = []
        for q, p in zip(Q, P):
            q2 = R @ q + np.array([tx, ty])
            res.append(np.linalg.norm(q2 - p) - g)
        return np.array(res)
    x = np.zeros(2)
    for _ in range(50):
        r = residual(x)
        J = np.zeros((2, 2))
        for j in range(2):
            dx = np.zeros(2); dx[j] = 1e-7
            J[:, j] = (residual(x + dx) - r) / 1e-7
        step = np.linalg.solve(J, -r)
        x += step
        if np.linalg.norm(step) < 1e-12:
            break
    return np.linalg.norm(x)          # the tracked point (origin) moves by the translation, since R@0 = 0


if __name__ == "__main__":
    print("1. Parallelogram translation stage, two leaves L=40 mm, width 20, spacing 50")
    for name, m in MATS.items():
        kd, dl, ka, kt, ko = parallelogram(m["E"], m["eps"], m["t"], 40.0)
        print(f"  {name:26s} range +/-{dl:4.2f} mm | drive {kd:6.2f} N/mm | axial {ka:7.0f} N/mm | "
              f"out-of-plane {ko:6.0f} N/mm | tilt {kt/1000:6.0f} N*m/rad")
    for L in (60.0, 80.0):
        m = MATS["PETG (1.2 mm leaf)"]
        kd, dl, ka, kt, ko = parallelogram(m["E"], m["eps"], m["t"], L)
        print(f"  PETG, L={L:.0f}: range +/-{dl:4.2f} mm, drive {kd:5.2f} N/mm, out-of-plane {ko:5.0f} N/mm")

    print("\n2. Remote-centre pivot (two leaves aimed at the dot from D), leaf L, range and stiffness about the dot")
    for name, m in MATS.items():
        for L in (40.0, 80.0):
            for D in (70.0, 150.0, 250.0):
                th, kth = rcc(m["E"], m["eps"], m["t"], L, D)
                print(f"  {name:26s} L={L:3.0f} D={D:3.0f}: range +/-{math.degrees(th):4.2f} deg, "
                      f"stiffness about the dot {kth/1000:7.2f} N*m/rad")
    print("   (the flexure's own stiffness about the dot is low; the setting is held by the micrometer + preload spring,")
    print("    the other five directions by leaf axial and out-of-plane stiffness)")

    print("\n3. Remote-centre drift: how far the pivot point wanders from the dot as the pivot turns (pseudo-rigid four-bar)")
    for D in (70.0, 150.0, 250.0):
        for L, sep in ((40.0, 60.0), (80.0, 60.0), (80.0, 120.0)):
            dr = [fourbar_drift(D, L, sep, a) for a in (0.5, 1.0, 2.0)]
            print(f"  D={D:3.0f} L={L:3.0f} leaf separation {sep:3.0f}: drift at 0.5/1/2 deg = "
                  + " / ".join(f"{d*1000:6.1f}" for d in dr) + " um")

    print("\n4. Gravity through the head: tilt of a printed parallelogram under a moment")
    for name, m in MATS.items():
        *_, kt, _ = parallelogram(m["E"], m["eps"], m["t"], 40.0)
        for M in (2.2, 0.3):     # N*m: full 1.5 kg gun at 150 mm; relieved to ~2 N at 150 mm
            tilt = M * 1000 / kt
            print(f"  {name:26s} M={M:3.1f} N*m: tilt {math.degrees(tilt)*60:6.2f} arcmin -> {tilt*150:6.3f} mm at 150 mm")

    print("\n5. Creep of a load-carrying PETG leaf vs a displacement-held one [estimates]")
    print("  load-controlled: creep compliance growth ~ +30-60 % over 1000 h at ~10-20 % of strength (typical amorphous PET/PETG, estimate)")
    print("    -> a gravity-induced tilt of 0.02 mm at 150 mm grows by 0.006-0.012 mm over a session-to-months span;")
    print("  displacement-controlled (micrometer holds position): the leaf relaxes instead; position is kept by the steel")
    print("    micrometer, only the contact force drops -> a steel spring in parallel supplies the contact force.")

    print("\n6. Thermal growth of the printed loop (gun body warms; lens-alarm threshold is ambient +15-20 C per manual)")
    for name, m in MATS.items():
        label = "steel/aluminium-framed loop" if "shim" in name else name.split(" (")[0] + " printed loop"
        cte = 17e-6 if "shim" in name else m["cte"]
        for dT in (5, 15):
            print(f"  {label:28s} 120 mm of loop, dT {dT:2d} K: {120*cte*dT*1000:5.1f} um")

    print("\n7. Resolution with a 0.01 mm micrometer on a 5:1 lever")
    for D in (70.0, 150.0):
        r_drive = 40.0
        print(f"  translation stage: 2 um per division;  RCC with drive point {r_drive:.0f} mm from its leaves, centre D={D:.0f}: "
              f"{math.degrees(0.002 / (D + r_drive)):.5f} deg per division (drive arm measured from the remote centre)")
