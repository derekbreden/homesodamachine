"""neoFit ACVUS-44 stem check valve: a 1/4" OD stem on one end and a 1/4" OD tube socket on the
other, with the check between them.

The exterior is the silhouette of Fresh Water Systems' side photograph, scaled by the stem's
6.35 mm. The README has the source and what the trace does not establish.

Frame: +X = the part's axis, the stem tip at X = 0 facing -X and the socket mouth at X = LENGTH
facing +X, as the John Guest reducer stems in this tree stand. Centered on Y and Z.
"""
import cadquery as cq

STEM_D = 6.35
# (mm from the stem tip, radius): the photograph's silhouette, one sample every 2 px.
PROFILE = (
    (0.0, 1.10), (0.24, 1.94), (0.48, 2.47), (0.83, 2.86), (1.31, 3.13), (1.79, 3.175),
    (8.34, 3.175), (8.81, 2.95), (9.53, 3.175), (15.60, 3.175),
    (15.84, 4.20), (16.08, 5.21), (16.43, 6.22), (16.79, 6.94), (17.27, 7.50), (17.98, 7.89),
    (23.70, 7.89), (24.29, 7.68), (24.77, 7.23), (25.25, 6.46), (25.60, 5.39), (25.96, 4.91),
    (33.46, 4.97), (33.70, 5.33), (34.18, 6.01), (34.65, 6.55), (35.37, 7.03), (38.22, 7.11),
    (38.46, 7.32), (38.94, 7.68), (43.23, 7.89), (43.82, 7.83), (44.30, 7.44), (44.54, 7.26),
    (45.85, 7.29), (46.44, 7.03), (47.04, 6.28), (47.40, 5.21), (47.52, 5.15), (47.87, 6.13),
    (48.23, 6.76), (49.30, 6.79), (49.78, 6.52), (50.00, 6.13),
)
LENGTH = PROFILE[-1][0]
SHOULDER = 15.60            # where the stem meets the collar: a host collet's mouth stops it here
INSERTION = 16.891          # tube into the socket: neoFit's 1/4" female engagement
SOCKET_D = 6.50             # the tube's bore in the socket
BORE_D = 4.30               # the passage through the stem and the check


def stem_tip():
    """The free tip of the stem: (position, outward axis). It enters a host socket up to
    SHOULDER, its tip short of the host's tube stop."""
    return (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0)


def tube_port():
    """The socket mouth the 1/4" OD tube pushes into: (position, outward axis). The tube travels
    INSERTION in."""
    return (LENGTH, 0.0, 0.0), (1.0, 0.0, 0.0)


def build():
    outline = [(0.0, 0.0), *PROFILE, (LENGTH, 0.0)]
    body = cq.Workplane('XY').polyline(outline).close().revolve(360, (0, 0, 0), (1, 0, 0)).val()
    socket = cq.Solid.makeCylinder(SOCKET_D / 2.0, INSERTION + 0.1, cq.Vector(LENGTH - INSERTION, 0, 0),
                                   cq.Vector(1, 0, 0))
    bore = cq.Solid.makeCylinder(BORE_D / 2.0, LENGTH - INSERTION + 0.2, cq.Vector(-0.1, 0, 0), cq.Vector(1, 0, 0))
    return body.cut(socket).cut(bore).clean()


if __name__ == '__main__':
    shape = build()
    bb = shape.BoundingBox()
    print(f'ACVUS-44: {bb.xlen:.2f} long, Ø{bb.ylen:.2f} max, {shape.Volume():.0f} mm^3')
