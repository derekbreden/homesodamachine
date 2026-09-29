"""Geometry that the order of operations forces on a ribbon end held in one place.

Run: python3 selector_and_bow.py > selector_and_bow.out.txt

1. Selecting one conductor out of the row: how far it (or its neighbours) must move, and what
   that does to the tip position.
2. Fanning wider than housing pitch for crimping, then converging for insertion: the length
   mismatch it builds in if the tips were trimmed in the fanned pose.
3. Inserting one conductor at a time while the ribbon stays clamped: the bow each conductor
   needs so its contact can come from behind the housing.
4. How far a conductor tip wanders under a small side load, by stick-out.

Sources: ribbon pitch 1.7 mm, OD 1.7 mm, XH pitch 2.5 mm [source S29, mfr S1 via xh-facts];
EI of the 60 x 0.08 mm conductor with silicone 14.1-18.1 N*mm^2 [study: into-the-housing
calc/insertion_geometry.out.txt]; contact length 6.1-6.7 mm [mfr/source, xh-facts §1].
"""

import math

PITCH_RIBBON = 1.7
PITCH_XH = 2.5
OD = 1.7
EI = (14.1, 18.1)  # N*mm^2


def section(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def main():
    section("1. Selecting one conductor: out-of-plane separation and tip retraction")
    print("Neighbours at 2.5 mm pitch leave 3.30 mm between them [study: into-the-housing].")
    print("A crimp jaw wider than that must see its neighbours moved out of the plane by at least")
    print("the jaw's depth below (or above) the conductor axis plus OD/2 plus clearance.")
    for jaw_depth in (2.0, 4.0, 6.0, 8.0):
        h = jaw_depth + OD / 2 + 1.0
        print(f"  jaw reaches {jaw_depth:.0f} mm past the conductor axis -> separation h >= {h:.1f} mm")
    print("\nLifting the active conductor by h at a point s behind its tip region, pivoting at the")
    print("web split, pulls its tip back by s - sqrt(s^2 - h^2); the change with s is what a")
    print("ragged hand-peeled split point (+/-3 mm) does to the tip:")
    print(f"{'s mm':>6}{'h mm':>6}{'angle':>8}{'retract':>9}{'d/ds':>8}{'tip var +/-3mm':>16}")
    for s in (15, 20, 25, 30):
        for h in (6, 8, 10):
            if h >= s:
                continue
            r = s - math.sqrt(s * s - h * h)
            dds = 1 - s / math.sqrt(s * s - h * h)
            print(f"{s:>6}{h:>6}{math.degrees(math.atan(h/s)):>7.1f}d{r:>8.2f}{dds:>8.3f}"
                  f"{abs(dds)*3:>15.2f}")
    print("-> retraction is a constant offset if every conductor is lifted the same way; the")
    print("   split-point scatter adds 0.1-0.6 mm, which is the same order as the axial window")
    print("   (insulation edge between the barrels, brush visible, +/-0.3 mm [estimate]).")
    print("   Trimming each tip in the lifted pose, at the crimp station, removes it.")

    section("2. Fan to a working pitch, trim, then converge to 2.5 mm: built-in length error")
    print("Ribbon conductors sit at 1.7 mm; the fan runs over length Lf from the web split to a")
    print("comb where the conductors are parallel at working pitch w. Tips trimmed on a straight")
    print("line in that pose are equal in x, not in length. Converged to 2.5 mm, the outermost")
    print("conductor carries the excess below as slack (bow amplitude ~ 0.64*sqrt(excess*L)).")
    for n, name in ((9, "J1 5P+4P"), (5, "J6 5P"), (4, "J11 4P")):
        print(f"\n{name}, {n} conductors")
        print(f"{'w mm':>6}{'Lf':>6}{'outer shift':>13}{'excess vs 2.5':>15}{'bow mm':>8}")
        for w in (2.5, 4.0, 5.0, 6.0):
            for Lf in (20.0, 30.0, 40.0):
                i = n - 1
                y_rib = (i - (n - 1) / 2) * PITCH_RIBBON
                y_w = (i - (n - 1) / 2) * w
                y_h = (i - (n - 1) / 2) * PITCH_XH
                len_w = math.hypot(Lf, y_w - y_rib)
                len_h = math.hypot(Lf, y_h - y_rib)
                ex = len_w - len_h
                bow = 0.64 * math.sqrt(max(ex, 0) * Lf)
                if Lf == 30.0 or w == 2.5:
                    print(f"{w:>6.1f}{Lf:>6.0f}{y_w - y_rib:>12.1f} {ex:>14.2f}{bow:>8.1f}")
    print("-> crimping in the row at 2.5 mm needs neighbours moved out of plane (section 1);")
    print("   crimping at a wider pitch needs the trim done in the converged pose, or a per-")
    print("   conductor trim, or an arc-shaped trim line, or the slack accepted.")

    section("3. One-at-a-time insertion with the ribbon clamped: bow per conductor")
    L_c = 6.4
    retract = L_c + 1.0
    print(f"The contact must start {retract:.1f} mm behind its seated position (contact ~{L_c} mm")
    print("long, plus 1 mm clearance): the conductor between its web split and the gripper")
    print("has to shorten its reach by that much, by bowing.")
    print(f"{'free length mm':>15}{'tent height':>13}{'sine amplitude':>16}")
    for Lb in (15.0, 20.0, 30.0, 40.0):
        half = Lb / 2
        base = (Lb - retract) / 2
        tent = math.sqrt(max(half * half - base * base, 0))
        amp = (2 / math.pi) * math.sqrt(retract * Lb)  # small-slope sine estimate
        print(f"{Lb:>15.0f}{tent:>12.1f} {amp:>15.1f}")
    print("-> each conductor rises ~8-11 mm out of the row while it is pushed home; the")
    print("   bow straightens as the contact seats. Gang insertion (the housing slides onto")
    print("   every contact at once) needs no bow: the order 'crimp all, then insert' removes it.")

    section("4. Tip wander of an unsupported stick-out under a side load (cantilever)")
    print(f"{'stick-out mm':>13}" + "".join(f"{f'F={F} N':>12}" for F in (0.02, 0.05, 0.2)))
    for L in (5.0, 8.0, 10.0, 15.0):
        cells = []
        for F in (0.02, 0.05, 0.2):
            dmin = F * L ** 3 / (3 * EI[1])
            dmax = F * L ** 3 / (3 * EI[0])
            cells.append(f"{dmin:.2f}-{dmax:.2f}")
        print(f"{L:>13.0f}" + "".join(f"{c:>12}" for c in cells))
    print("0.02 N is a light brush; 0.2 N a firm nudge [estimate]. Gravity on 10 mm of conductor")
    w = 2.0e-3 * 9.81  # ~2 g/m? see below
    # conductor mass per mm: copper 0.302 mm^2 * 8.96 g/cm^3 + silicone ~2.0 mm^2 * 1.15 g/cm^3
    m_per_mm = (0.302 * 8.96 + 2.0 * 1.15) / 1000.0  # g/mm
    q = m_per_mm / 1000 * 9.81  # N/mm
    for L in (10.0, 15.0):
        sag = q * L ** 4 / (8 * EI[0])
        print(f"  sags {sag:.3f} mm at {L:.0f} mm stick-out (self weight, {m_per_mm*1000:.1f} g/m)")
    print("-> a tip is where the trim put it only until something touches it; each station")
    print("   that needs the tip to +/-0.1-0.3 mm should capture it (fork, funnel, jaw) at the")
    print("   moment of use, 2-5 mm from the tip.")


if __name__ == "__main__":
    main()
