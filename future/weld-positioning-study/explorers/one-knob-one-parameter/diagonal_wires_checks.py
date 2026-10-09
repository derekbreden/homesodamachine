"""Checks on the one-wire-per-parameter layout found by diagonal_wires.py
(read from diagonal_wires_layout.json).

1. Natural frequencies of the gun on its six wires vs the 80 Hz wobble
   (and 160 Hz), and the dot's vibration for an assumed 1 N wobble reaction.
2. How precisely each rotation wire must lie in its plane: move an attachment
   2 mm out of its plane and see what the other knobs leak.
3. Anchor loads, for sizing the micrometer anchors (direct vs 5:1 lever).

Inertia [assumed]: gun + shell 1.5 kg as a 250 x 120 x 34 mm block about its CG.
Wire: 1/16 in 7x7 stainless, EA ~130 kN, 400 mm free length; geometric
stiffness T/L included; anchor frame rigid (it is not).
Run: python3 diagonal_wires_checks.py
"""
import json, math, pathlib
import numpy as np
import diagonal_wires as W

cfg = json.loads(pathlib.Path(__file__).with_name("diagonal_wires_layout.json").read_text())
q = cfg["q"]
pre = [(np.array(s), np.array(d), f) for s, d, f in cfg["pre"]]
wires = W.layout(q)
names = [w[0] for w in wires]
T0 = W.tensions(wires, pre)


def skew(c):
    return np.array([[0, -c[2], c[1]], [c[2], 0, -c[0]], [-c[1], c[0], 0]])


def stiffness(wires, tens, EA=130e3):
    """6x6 stiffness about the dot in N/mm and N*mm/rad, for twist (v, omega)."""
    K = np.zeros((6, 6))
    for (nm, a, u, L), t in zip(wires, tens):
        r = a - W.D
        # axial
        j = np.concatenate([u, np.cross(r, u)])
        K += (EA / L) * np.outer(j, j)
        # geometric (lateral) stiffness of a taut string, T/L in the two directions normal to u
        for e in np.linalg.svd(np.eye(3) - np.outer(u, u))[0][:, :2].T:
            je = np.concatenate([e, np.cross(r, e)])
            K += (t / L) * np.outer(je, je)
    return K


def modes():
    K = stiffness(wires, T0)
    # convert to SI: N/m, N*m/rad, N (coupling terms N/rad per m)
    S = np.diag([1e3, 1e3, 1e3, 1e-3 * 1e3, 1e-3 * 1e3, 1e-3 * 1e3])
    # K is in N/mm for (v mm) and N*mm/rad for rotations. v[m] = v[mm]/1000.
    # K_SI[vv] = K[vv]*1000 ; K_SI[vw] = K[vw] (N/rad per mm -> N/rad per m *1000 /1000) ; K_SI[ww] = K[ww]/1000
    Ks = K.copy()
    Ks[:3, :3] *= 1e3
    Ks[3:, 3:] *= 1e-3
    m = W.MASS
    c = (W.CG - W.D) / 1000.0
    Rg = W.Rg
    Icg_local = np.diag([m * (0.25**2 + 0.12**2) / 12, m * (0.25**2 + 0.034**2) / 12, m * (0.12**2 + 0.034**2) / 12])
    Icg = Rg @ Icg_local @ Rg.T
    Idot = Icg + m * (np.dot(c, c) * np.eye(3) - np.outer(c, c))
    M = np.zeros((6, 6))
    M[:3, :3] = m * np.eye(3)
    M[:3, 3:] = -m * skew(c)
    M[3:, :3] = m * skew(c)
    M[3:, 3:] = Idot
    w2, vecs = np.linalg.eig(np.linalg.solve(M, Ks))
    order = np.argsort(w2.real)
    f = np.sqrt(np.abs(w2.real[order])) / (2 * math.pi)
    print("1. Natural frequencies on the wires (Hz):", np.round(f, 0))
    # forced response at the nozzle: 1 N sideways (gun local x) at 80 and 160 Hz, damping ratio zeta
    tip = W.gp([0, 0, 0])
    fdir = W.Rg @ np.array([1.0, 0, 0])
    Fw = np.concatenate([fdir, np.cross((tip - W.D) / 1000.0, fdir)])
    for fz in (60, 80, 120, 160):
        w = 2 * math.pi * fz
        for zeta in (0.02, 0.1):
            # modal damping approximated by C = 2 zeta * sqrt(K M) via eigenbasis
            Phi = vecs[:, order].real
            Mm = Phi.T @ M @ Phi; Km = Phi.T @ Ks @ Phi
            wn = np.sqrt(np.abs(np.diag(Km) / np.diag(Mm)))
            Fm = Phi.T @ Fw
            qm = Fm / (np.diag(Km) - w**2 * np.diag(Mm) + 1j * 2 * zeta * wn * w * np.diag(Mm))
            x = Phi @ qm
            print(f"   1 N at the nozzle, {fz:3d} Hz, zeta {zeta}: dot vibrates {np.linalg.norm(np.abs(x[:3]))*1e6:6.1f} um amplitude")


def plane_tolerance():
    print("\n2. A rotation wire 2 mm out of its plane: leakage of its knob into the other angles (deg per deg)")
    K0 = W.knob_matrix(wires)
    for nm, normal, pk in (("W_grip", np.cross(W.h_ax, W.z_ax), "G"), ("W_hole", np.cross(W.g_ax, W.z_ax), "H"),
                           ("W_vert", np.cross(W.g_ax, W.h_ax), "V")):
        i = names.index(nm)
        ww = list(wires)
        n, a, u, L = ww[i]
        ww[i] = (n, a + 2.0 * normal / np.linalg.norm(normal), u, L)
        K = W.knob_matrix(ww)
        j = W.PNAMES.index(pk)
        main = K[j, i]
        leaks = {W.PNAMES[k]: K[k, i] / main for k in range(6) if k != j}
        print(f"   {nm}: " + ", ".join(f"{p} {v:+.4f}" + (" mm/deg" if p in ("X", "Z") else "") for p, v in leaks.items()))
    # and leak of the OTHER knobs when this one is out of plane
    print("   (an out-of-plane wire mainly makes the *other two* rotation knobs leak into its rotation:)")
    for nm, normal in (("W_grip", np.cross(W.h_ax, W.z_ax)), ("W_hole", np.cross(W.g_ax, W.z_ax)), ("W_vert", np.cross(W.g_ax, W.h_ax))):
        i = names.index(nm)
        ww = list(wires)
        n, a, u, L = ww[i]
        ww[i] = (n, a + 2.0 * normal / np.linalg.norm(normal), u, L)
        K = W.knob_matrix(ww)
        out = []
        for other, pk in (("W_grip", "G"), ("W_hole", "H"), ("W_vert", "V")):
            if other == nm:
                continue
            io = names.index(other); jo = W.PNAMES.index(pk)
            worst = max(abs(K[k, io] / K[jo, io]) for k in (3, 4, 5) if k != jo)
            out.append(f"{other} leaks {worst:.3f} deg/deg")
        print(f"   {nm} 2 mm out of plane -> " + "; ".join(out))


def anchor_loads():
    print("\n3. Wire tensions at rest (anchor loads) and on a 5:1 micrometer lever")
    for nm, t in zip(names, T0):
        print(f"   {nm:7s} {t:5.1f} N  -> micrometer sees {t/5:4.1f} N on a 5:1 lever; resolution x5")


if __name__ == "__main__":
    modes(); plane_tolerance(); anchor_loads()
