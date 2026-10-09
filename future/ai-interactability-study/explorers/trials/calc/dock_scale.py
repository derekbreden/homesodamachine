"""What can three load cells under a gun dock tell us?  All ILLUSTRATIVE: gun+shell mass, seat geometry, cell noise and
umbilical pull are [unknown]; the X1 Pro envelope is 253 x 143 x 34 mm [manual p.17].

Model: the shell rests on three seats forming a triangle. A horizontal umbilical pull F_h acting at height h above the seat
plane, and a vertical pull F_v, change the three vertical reactions. We solve statics and report the change per cell and
the equivalent 'grams' seen, then compare with an assumed cell noise floor.
"""
import numpy as np
seats = np.array([[-60., -40.], [60., -40.], [0., 70.]])     # mm, plan positions of the 3 seats (ILLUSTRATIVE)
cog = np.array([0., 5.]); m_kg = 1.5; h_cog = 60.0            # ILLUSTRATIVE
g = 9.81
def reactions(F_h_xy=(0., 0.), h=100.0, F_v=0.0, tip_xy=(0., 0.)):
    """F_h_xy in N (x,y). Pull applied at height h above the seats, at plan point tip_xy. F_v upward pull (N)."""
    W = m_kg * g - F_v
    # unknowns R1..R3: sum R = W ; moments about x and y
    fx, fy = F_h_xy
    # weight at cog; horizontal force at height h gives moments M_x = -fy*h... (about seat plane), M_y = fx*h
    Mx_ext = W*cog[1]/1000 - fy*h/1000 - F_v*0    # N*m about x axis (y lever arms)
    My_ext = -W*cog[0]/1000 + fx*h/1000
    A = np.array([[1, 1, 1], [*(seats[:, 1]/1000)], [*(-seats[:, 0]/1000)]])
    b = np.array([W, Mx_ext, My_ext])
    return np.linalg.solve(A, b)
R0 = reactions()
print("baseline reactions (N):", np.round(R0, 3), " total kg:", round(R0.sum()/g, 3))
print("\nHorizontal umbilical pull at 100 mm above the seats (N) -> change in each cell, in grams-equivalent")
for F in (0.2, 0.5, 1.0, 2.0, 5.0):
    for name, vec in (("along x", (F, 0)), ("along y", (0, F))):
        d = (reactions(vec) - R0)/g*1000
        print(f"  {F:4.1f} N {name}: dR = {np.round(d,1)} g   total change {round(d.sum(),1)} g")
print("\nVertical umbilical pull (N) -> total change in grams")
for F in (0.1, 0.5, 1.0):
    print(f"  {F} N up: {round((reactions(F_v=F).sum()-R0.sum())/g*1000,1)} g")
print("\nCell noise floor assumed 1-5 g (ILLUSTRATIVE; hobby bar cell + 24-bit ADC, unchecked). Smallest horizontal pull visible at 5 g:")
for noise in (1, 2, 5, 10):
    # smallest F such that any cell changes by > noise
    for F in np.linspace(0.01, 5, 500):
        d = np.abs((reactions((F, 0)) - R0)/g*1000)
        if d.max() > noise:
            print(f"  noise {noise:2d} g -> {F:.2f} N along x"); break
print("\nA 1 mm shift of the centre of gravity (e.g. the umbilical hanging differently near the grip) changes the cells by:")
cog0 = cog.copy()
for axis, name in ((0, "x"), (1, "y")):
    cog[:] = cog0; cog[axis] += 1.0
    d = (reactions() - R0)/g*1000
    print(f"  1 mm along {name}: dR = {np.round(d,1)} g")
cog[:] = cog0
print("Horizontal pulls leave the TOTAL unchanged: a single bathroom-scale reading cannot see them; three cells can.")
