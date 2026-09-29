"""The camshaft machine (p5): force from a worm-driven eccentric, where in the turn it arrives,
and the timing of one revolution per conductor.

Run: python3 cam_drive.py > cam_drive.out.txt
The p5 timing sketch is drawn by ../sketches/make_sketches_w3.py.

Crimp force need: 0.8-2.6 kN peak at bottom dead centre, design 3 kN [calc C1 via xh-facts §4].
Energy ~0.3-0.4 J per crimp [calc C1].
Motor and gear figures are [assumption] for a generic NEMA 17 / NEMA 23 and a worm reducer.
"""

import math
import os

NEED = 3000.0  # N at BDC, design figure


def punch_y(theta, e, l):
    """Punch drop below top dead centre for crank angle theta (0 = TDC, pi = BDC)."""
    return e * (1 - math.cos(theta)) + l - math.sqrt(l * l - (e * math.sin(theta)) ** 2)


def dy_dtheta(theta, e, l, h=1e-6):
    return (punch_y(theta + h, e, l) - punch_y(theta - h, e, l)) / (2 * h)


def section(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def main():
    section("1. Torque at the camshaft")
    motors = [("NEMA 17, 0.3 N*m usable at low speed", 0.3), ("NEMA 23, 1.2 N*m usable", 1.2)]
    worms = [(30, 0.35), (50, 0.30)]  # ratio, efficiency (self-locking worms are poor) [assumption]
    torques = {}
    for mname, tm in motors:
        for r, eta in worms:
            T = tm * r * eta
            torques[(mname, r)] = T
            print(f"  {mname:<38} x {r}:1 worm, eta {eta:.2f} -> {T:5.1f} N*m")

    section("2. Force at the punch from an eccentric (crank e, rod l) near bottom dead centre")
    for e in (2.0, 2.5):
        l = 40.0
        stroke = 2 * e
        print(f"\neccentric e = {e} mm (stroke {stroke:.0f} mm), rod {l:.0f} mm")
        print(f"{'deg before BDC':>15}{'height above BDC':>18}{'mm/rad':>8}"
              + "".join(f"{f'F @ {T:.0f} N*m':>13}" for T in (3.0, 6.0, 15.0)))
        for phi_deg in (40, 30, 22, 15, 10, 5, 2):
            th = math.pi - math.radians(phi_deg)
            height = punch_y(math.pi, e, l) - punch_y(th, e, l)
            k = dy_dtheta(th, e, l)  # mm per rad
            fs = [T / (k / 1000.0) for T in (3.0, 6.0, 15.0)]
            print(f"{phi_deg:>15}{height:>18.3f}{k:>8.3f}" + "".join(f"{f/1000:>11.1f}kN" for f in fs))
    print("\n-> compaction happens in the last ~0.10-0.20 mm [xh-facts §4], i.e. the last")
    print("   ~15-25 deg of crank; there even 3 N*m at the shaft gives >3 kN, rising toward BDC.")
    print("   A NEMA 17 through a 30:1 worm is enough; the frame and bearings, not the motor,")
    print("   set what the machine can do.")

    section("3. Frame stiffness for crimp-height repeatability")
    for dF in (300.0, 600.0):
        for tol in (0.01, 0.02):
            print(f"  force scatter +/-{dF:.0f} N, crimp-height budget +/-{tol} mm -> "
                  f"loop stiffness >= {dF/tol/1000:.0f} kN/mm")
    print("  A printed PETG loop is tens to a hundred times softer than steel [estimate]; the")
    print("  force loop (anvil -> frame -> eccentric bearing -> rod -> punch) is steel plate and")
    print("  bearings, and printed parts carry only the light cams.")

    section("4. One revolution per conductor: timing")
    T_rev = 40.0
    phases = [
        ("index ribbon carriage to conductor k", 0, 30, "stepper, cam switch triggers"),
        ("selector lifts k; fork closes behind strip line", 30, 70, "face cam, printed"),
        ("strip jaws close, pull 3 mm, open (slug drops)", 70, 130, "two face cams"),
        ("lay-in finger sets conductor into contact", 130, 170, "face cam"),
        ("punch down: wings curl, compaction, BDC at 240", 170, 240, "steel eccentric"),
        ("carrier tab sheared at BDC", 230, 240, "same stroke"),
        ("punch up", 240, 290, "steel eccentric"),
        ("camera frame + proof pull 15-20 N", 290, 330, "cam switch + spring"),
        ("fork opens, selector down, strip feed pawl advances", 330, 360, "face cam + pawl"),
    ]
    for name, a, b, how in phases:
        print(f"  {a:>3}-{b:<3} deg  {(b-a)/360*T_rev:5.1f} s  {name:<52} {how}")
    crimp_zone = 22 / 360 * T_rev
    print(f"  compaction (last 22 deg) lasts {crimp_zone:.1f} s at {T_rev:.0f} s/rev: slow enough to log")
    print(f"  force against angle with an HX711 load-cell amplifier at its 80 Hz setting")
    print(f"  -> {crimp_zone*80:.0f} samples through compaction [source: prior-art §6, SparkFun HX711 guide]")
    print(f"  per unit: 53 revolutions = {53*T_rev/60:.0f} min of cycling, plus cassette changes")
    energy = 0.4
    print(f"  mean shaft power over the compaction: {energy/crimp_zone:.2f} W")



def write_svg(phases, T_rev):
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "sketches", "p5-cam-timing.svg")
    W, H = 900, 420
    x0, x1 = 300, 860
    def X(deg):
        return x0 + (x1 - x0) * deg / 360.0
    rows = [
        ("Ribbon index (stepper)", [(0, 30, 1.0)]),
        ("Selector lift + fork", [(30, 70, "up"), (70, 330, 1.0), (330, 360, "down")]),
        ("Strip jaws", [(70, 90, "up"), (90, 115, 1.0), (115, 130, "down")]),
        ("Strip pull (3 mm)", [(90, 115, "up"), (115, 130, 1.0)]),
        ("Lay-in finger", [(130, 170, "up"), (170, 290, 1.0), (290, 310, "down")]),
        ("Punch (eccentric)", "crank"),
        ("Tab cut-off", [(230, 240, 1.0)]),
        ("Camera + proof pull", [(290, 330, 1.0)]),
        ("Strip feed pawl", [(330, 360, 1.0)]),
    ]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'font-family="Helvetica, Arial, sans-serif" font-size="12">',
             f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
             f'<text x="20" y="26" font-size="16" font-weight="bold">p5 camshaft: one revolution per conductor '
             f'(schematic timing, {T_rev:.0f} s/rev)</text>',
             '<text x="20" y="46" fill="#555">Angles are an illustration of the sequence, not a design. '
             'Punch line is the eccentric: bottom dead centre at 240 deg.</text>']
    top = 70
    rh = 36
    for deg in range(0, 361, 30):
        parts.append(f'<line x1="{X(deg):.1f}" y1="{top-6}" x2="{X(deg):.1f}" y2="{top+rh*len(rows)}" '
                     f'stroke="#ddd"/>')
        parts.append(f'<text x="{X(deg):.1f}" y="{top-10}" text-anchor="middle" fill="#666">{deg}</text>')
    for i, (name, spec) in enumerate(rows):
        yb = top + rh * i + rh - 8
        yt = top + rh * i + 10
        parts.append(f'<text x="20" y="{yb-6}">{name}</text>')
        parts.append(f'<line x1="{x0}" y1="{yb}" x2="{x1}" y2="{yb}" stroke="#bbb"/>')
        if spec == "crank":
            pts = []
            for d in range(0, 361, 3):
                th = math.radians((d - 60) % 360)  # TDC at 60 deg, BDC at 240
                drop = (1 - math.cos(th)) / 2
                pts.append(f"{X(d):.1f},{yt + (yb-yt)*(1-drop):.1f}")
            # inverted: low line = punch down
            pts2 = []
            for d in range(0, 361, 3):
                th = math.radians((d - 60) % 360)
                drop = (1 - math.cos(th)) / 2
                pts2.append(f"{X(d):.1f},{yt + (yb-yt)*drop:.1f}")
            parts.append(f'<polyline points="{" ".join(pts2)}" fill="none" stroke="#b03030" stroke-width="2"/>')
            parts.append(f'<text x="{X(240):.1f}" y="{yb+12}" text-anchor="middle" fill="#b03030" font-size="10">'
                         f'BDC: compaction</text>')
            continue
        path = [f"M {x0} {yb}"]
        level = 0.0
        for a, b, v in spec:
            if v == "up":
                path.append(f"L {X(a):.1f} {yb - (yb-yt)*level:.1f} L {X(b):.1f} {yt:.1f}")
                level = 1.0
            elif v == "down":
                path.append(f"L {X(a):.1f} {yb - (yb-yt)*level:.1f} L {X(b):.1f} {yb:.1f}")
                level = 0.0
            else:
                path.append(f"L {X(a):.1f} {yb - (yb-yt)*level:.1f} L {X(a):.1f} {yt:.1f} "
                            f"L {X(b):.1f} {yt:.1f}")
                level = 1.0
                if not any(s2[0] == b for s2 in spec):
                    path.append(f"L {X(b):.1f} {yb:.1f}")
                    level = 0.0
        path.append(f"L {x1} {yb}")
        parts.append(f'<path d="{" ".join(path)}" fill="none" stroke="#2a5d9f" stroke-width="2"/>')
    parts.append(f'<text x="{x0}" y="{top + rh*len(rows) + 22}" fill="#555">crank angle, degrees '
                 f'(0-360 = one conductor)</text>')
    parts.append('</svg>')
    with open(out, "w") as f:
        f.write("\n".join(parts))
    print(f"\nwrote {os.path.relpath(out, here)}")


if __name__ == "__main__":
    main()
