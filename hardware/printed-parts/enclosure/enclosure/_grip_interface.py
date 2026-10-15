"""Accepted curved grip receiver and flat-wing insert geometry.

The enclosure passes its dimensions to this interface. Production walls and
receiver coupons use the same reliefs, slots, cover and assembly placement.
"""
import cadquery as cq
from overhang_round import transition


class GripInterface:
    """One pair of mirrored handholds in the enclosure coordinate frame."""

    def __init__(self, shell, *, floor_z=0.0):
        self.shell = shell
        self.BODY_AIR = self.shell.fits.slip
        self.LENGTH = self.shell.handhold_length - 2 * self.BODY_AIR
        self.X_EXT = self.shell.appliance_width / 2
        _seat, _tip, _heat, _cap = self.shell._boss_x(self.X_EXT, -1)
        self.INNER_FACE = _cap + self.shell.handhold_wall
        self.OUTER_FLAT = self.X_EXT - transition(self.shell.handhold_edge_r)[1]
        self.WIDTH = self.OUTER_FLAT - self.INNER_FACE - self.BODY_AIR
        self.X_CENTER = (self.OUTER_FLAT + self.INNER_FACE + self.BODY_AIR) / 2
        self.ROOF = (floor_z - self.shell.floor_t + self.shell.handhold_height
                     + self.shell.fits.supported_surface)
        self.CROWN = self.ROOF + self.shell.handhold_roof
        # Accepted flat-wing section; the cover and both wings share the bed.
        self.THICK = 3.36
        self.WING_THICK = 1.68
        self.WING_REACH = 2.4
        self.WING_SPAN = 5.0
        self.WING_END_R = 0.6
        self.CORNER_R = 0.6
        self.TOUCH_R = 0.6
        self.WING_END_AIR = self.shell.fits.slip
        self.BEARING_AIR = 0.45
        self.BACK_AIR = self.shell.fits.supported_surface
        self.ENTRY_WIDTH = 1.1
        self.ENTRY_DEPTH = 0.4
        self.BACK = self.ROOF - self.BACK_AIR

    def box(self, x0, x1, y0, y1, z0, z1):
        return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))

    def rounded(self, width, height, z0, z1, radius):
        return (cq.Workplane('XY').workplane(offset=z0).rect(width, height)
                .extrude(z1-z0).edges('|Z').fillet(radius).val())

    def wing(self, end):
        return self.rounded(self.WING_REACH+1, self.WING_SPAN, 0,
                            self.WING_THICK, self.WING_END_R).translate(
            (end*(self.LENGTH/2+(self.WING_REACH-1)/2), 0, 0))

    def cover(self):
        """One interchangeable strip; the finger face prints upward without supports."""
        body = self.rounded(self.LENGTH, self.WIDTH, 0, self.THICK, self.CORNER_R)
        edges = [e for e in body.Edges() if abs(e.BoundingBox().zmin - self.THICK) < 1e-06]
        body = body.fillet(self.TOUCH_R, edges)
        return body.fuse(self.wing(-1), self.wing(1)).clean()

    def placed(self, shape, side=1, drop=0):
        """Local X→world Y and Z→world -Z; mirror the east placement for the west."""
        east = (shape.rotate((0, 0, 0), (1, 1, 0), 180)
                .translate((self.X_CENTER, self.shell.handhold_y, self.BACK-drop)))
        return east if side == 1 else east.mirror('YZ')

    def receiver_reliefs(self):
        """Clear the two inside R6 shoulders up to the original roof datum.

        The mouth remains on the existing end-wall plane. Only stock below the
        structural roof is removed. The relief continues through the exterior so
        the outer corner cannot leave a tapered remnant beside the cover.
        """
        reliefs = []
        mouth = self.shell.handhold_length / 2
        for end in (-1, 1):
            x0, x1 = sorted((end * (mouth - self.shell.handhold_corner_r), end * mouth))
            reliefs.append(self.box(
                x0, x1, -self.WIDTH/2-self.BODY_AIR, self.X_EXT-self.X_CENTER+1,
                -self.BACK_AIR, self.shell.handhold_corner_r-self.BACK_AIR+0.01))
        return reliefs

    def receiver_slots(self):
        """Straight through-slots in the existing 3 mm end walls.

        Their mouths are at Y174/254, with no receiver stock projecting into the
        handhold. The open rear exits avoid thin pocket backs and give support access.
        """
        slots = []
        for end in (-1, 1):
            mouth = self.shell.handhold_length / 2
            x0, x1 = sorted((end*(self.LENGTH/2-0.1),
                             end*(mouth+self.shell.handhold_wall+0.1)))
            y0, y1 = (-self.WING_SPAN/2-self.WING_END_AIR,
                       self.WING_SPAN/2+self.WING_END_AIR)
            roof = self.WING_THICK + self.BEARING_AIR
            slot = self.box(x0, x1, y0, y1, -self.BACK_AIR, roof)
            lead = (cq.Workplane('XZ', origin=(0, y1, 0))
                    .polyline([(end*mouth, roof),
                               (end*(mouth+self.ENTRY_WIDTH), roof),
                               (end*mouth, roof+self.ENTRY_DEPTH)])
                    .close().extrude(y1-y0).val())
            slots.append(slot.fuse(lead))
        return slots

    def apply_receiver(self, solid, piece):
        """Apply to either connected bottom half, retaining the existing Y joint.

        Each slot belongs to the end wall in its own half. The reliefs and slots are
        remote from the seam, cross-pins, socket jamb and inner-wall scarf.
        """
        if piece not in ('front', 'back'):
            raise ValueError(piece)
        end_index = 0 if piece == 'front' else 1
        relief = self.receiver_reliefs()[end_index]
        slot = self.receiver_slots()[end_index]
        for side in (-1, 1):
            solid = solid.cut(self.placed(relief, side)).cut(self.placed(slot, side)).clean()
        return solid
