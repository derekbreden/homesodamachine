"""Order-of-magnitude isocenter walk for the gantry arm in the isocentric
couch-and-gantry arrangement (ideas/isocentric-couch-and-gantry.md).

Question: when the hole-axis angle e changes, gravity's direction relative to
the arm changes, so the arm's sag changes and the nozzle moves even though the
mechanism "rotates about the dot".  How big is that coupling for a few arm
sections?

Model [assumptions, all labelled]:
- Arm = straight cantilever spoke from the hole-axis rotary table (at the
  isocenter's X line) out along the grip axis to the roll bearing, L = 300 mm.
- Carried load W = 2.5 kg (gun ~1.2 kg [Unknown; ~1 kg circulated as an agent
  estimate], shell 0.3, standoff slide 0.2, roll body + bearings 0.8), acting at
  the spoke tip as a force plus a moment W * c with c = 150 mm (the load's
  centre sits back along the gun toward the dot).
- Only the component of gravity perpendicular to the spoke bends it: W g cos(e).
- The nozzle sits near the spoke root (the gun runs back along the spoke), so
  its motion is the tip deflection minus tip rotation times L.
- Rotary-table tilt compliance and bearing compliance are NOT included; they
  are unknown and are exactly what the isocenter walk test measures.
"""
import math

G = 9.81
L = 300.0          # mm
W = 2.5 * G        # N
C = 150.0          # mm, load centre back from the tip toward the dot

sections = {
    # name: (E in N/mm^2, I in mm^4)
    "2020 aluminium extrusion": (69000, 6.9e3),
    "2040 aluminium (stiff way)": (69000, 4.7e4),
    "4040 aluminium extrusion": (69000, 1.1e5),
    "50x50x3 aluminium box": (69000, 2.0e5),
    "printed PET-GF box 60x60, 4 mm walls": (4000, 6.0e5),
}


def nozzle_motion(e_deg, E, I):
    wp = W * math.cos(math.radians(e_deg))      # perpendicular load, N
    m = wp * C                                   # tip moment from offset load (reduces tip load effect)
    # tip deflection/rotation for tip force wp and tip moment -m (moment opposes, load acts inboard)
    d_tip = wp * L**3 / (3 * E * I) - m * L**2 / (2 * E * I)
    th_tip = wp * L**2 / (2 * E * I) - m * L / (E * I)
    return d_tip - th_tip * L                    # nozzle near the root, gun runs back along L


if __name__ == "__main__":
    print("nozzle motion perpendicular to the spoke (mm) and its change 20->45 deg")
    for name, (E, I) in sections.items():
        a, b = nozzle_motion(20, E, I), nozzle_motion(45, E, I)
        print(f"  {name:40s} e=20: {a:+.3f}  e=45: {b:+.3f}  walk: {b-a:+.3f}")
