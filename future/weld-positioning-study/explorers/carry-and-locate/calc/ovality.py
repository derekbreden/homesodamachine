"""Rim carriage: how bore ovality leaks into the dot's radial position when the carriage's
centre is set by two radial (pinch) contacts at +/-a from the station, vs a gun fixed to the base.
Bore radius r(theta) = R + e*cos(2(theta - phi)); phi turns as the tube turns."""
import numpy as np
for a in (15, 30, 45, 60):
    ar = np.radians(a)
    phis = np.radians(np.linspace(0, 180, 181))
    errs = []
    for ph in phis:
        a1 = np.cos(2*(ar - ph)); a2 = np.cos(2*(-ar - ph))          # per unit e
        cx = (a1 + a2) / (2*np.cos(ar))
        errs.append(np.cos(2*(0 - ph)) - cx)
    print(f"pinches at +/-{a:2d} deg: dot radial error amplitude {max(np.abs(errs)):.2f} e")
print("gun fixed to the rotator base: ovality alone gives +/-1.00 e, plus eccentric runout (TIR/2)")
print("local bore follower at the station: 0 e")
