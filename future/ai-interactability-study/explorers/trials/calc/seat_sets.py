"""Which rotations of a puck can land on a turntable that has more than one set of three grooves?  (wave 3, answering datum's question
about a symmetric seat pattern.)  A rotation r seats the puck when each of its three balls lands in a groove (any groove of any set) and
the three balls use three different grooves.  Angles in degrees, balls of the puck at BALLS.

Also prints how much of harmonic k of a tube-owned error a designed turn r exposes: |e^(i k r) - 1| = 2 |sin(k r / 2)|
(0 means that harmonic looks the same before and after the turn and cannot be told from the rig's own).
"""
import itertools, math

def seatings(balls, grooves, tol=0.5):
    out = []
    for r in range(360):
        used = []
        ok = True
        for b in balls:
            hit = [i for i, g in enumerate(grooves) if abs(((b + r - g + 180) % 360) - 180) <= tol]
            if not hit:
                ok = False
                break
            used.append(hit[0])
        if ok and len(set(used)) == 3:
            out.append(r)
    return out

def expose(r, kmax=4):
    return [round(2 * abs(math.sin(math.radians(k * r) / 2)), 2) for k in range(1, kmax + 1)]

cases = {
    'A  three asymmetric (0,115,240), one groove set':            ([0, 115, 240], [0, 115, 240]),
    'B  three symmetric (0,120,240), one groove set':              ([0, 120, 240], [0, 120, 240]),
    'C  asymmetric balls, two sets 100 deg apart':                 ([0, 115, 240], [0, 115, 240, 100, 215, 340]),
    'D  asymmetric balls, two sets 70 deg apart':                  ([0, 115, 240], [0, 115, 240, 70, 185, 310]),
    'E  asymmetric balls, three sets 40 deg apart':                ([0, 115, 240], [0, 115, 240, 40, 155, 280, 80, 195, 320]),
}
for name, (balls, grooves) in cases.items():
    s = seatings(balls, grooves)
    print(name)
    print('   rotations that seat:', s)
    for r in s:
        if r:
            print(f'   turn {r:3d} deg exposes harmonics 1..4 of a tube-owned error with weights', expose(r))
print()
print('Work index modulo 180 (the plate has two symmetric ports): the seat orientations 0, 120, 240 of case B read as', [r % 180 for r in (0, 120, 240)], 'so the ports still tell the three seatings apart')
print('Case A needs no index from the work for phase (the seats give it); case B does.')
