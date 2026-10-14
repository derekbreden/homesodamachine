"""Parametric, single-piece TPU elbow for installed pump-layout exploration.

Dimensions are candidate dimensions. Two overlapping passage cylinders form
the open corner. Pressure holding and lifetime require physical evidence.
"""
from dataclasses import dataclass
from pathlib import Path
import math
import sys

import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "hardware/printed-parts/diaphragm-pump-sleeve"))
import diaphragm_pump_sleeve as reference


@dataclass(frozen=True)
class Elbow:
    tube_depth: float = 15.0
    barb_depth: float = 11.0
    barb_bore: float = 9.0
    tube_bore: float = 6.1
    wall: float = 2.8
    passage: float = 4.4
    tube_stop: float = 3.5
    band_width: float = 9.0
    band_air: float = 1.0
    entry: float = 0.4

    @property
    def barb_od(self):
        return self.barb_bore + 2 * self.wall

    @property
    def tube_od(self):
        return self.tube_bore + 2 * self.wall

    @property
    def installed_barb_od(self):
        return reference.installed_od(self.barb_od, self.barb_bore, reference.crest())

    @property
    def installed_tube_od(self):
        return reference.installed_od(self.tube_od, self.tube_bore, 6.35)

    @property
    def axis(self):
        return -(self.barb_depth - self.band_width) + self.band_air + self.installed_tube_od / 2

    @property
    def mouth(self):
        return self.tube_stop + self.tube_depth

    @property
    def neck_length(self):
        """Smooth reduction ends before the complete 9 mm tube clamp seat."""
        return self.tube_stop + 3.0

    def local(self, installed=False, exterior=False):
        rb = (self.installed_barb_od if installed else self.barb_od) / 2
        rt = (self.installed_tube_od if installed else self.tube_od) / 2
        bore_b = (reference.crest() if installed else self.barb_bore) / 2
        bore_t = (6.35 if installed else self.tube_bore) / 2
        foot_offset = self.axis / math.sqrt(2) + self.passage / 2 + self.wall
        x = lambda r, a, b: cq.Solid.makeCylinder(r, b-a, cq.Vector(a, 0, 0), cq.Vector(1, 0, 0))
        y = lambda r, a, b: cq.Solid.makeCylinder(r, b-a, cq.Vector(self.axis, a, 0), cq.Vector(0, 1, 0))

        # Exact fifth-degree Bezier: r(t) = rb + (rt-rb)*(10t³-15t⁴+6t⁵).
        # Radius, slope and curvature meet both circular ends. The decreasing
        # radius makes the neck's lower skin steeper than its 45-degree axis.
        # The expanded placement envelope also extends the smooth reduction;
        # its larger heel must remain contained in the neck on the +Y side.
        # This is conservative envelope stock, not a deformation prediction.
        length = self.neck_length + (1.0 if installed else 0.0)
        profile = (cq.Workplane("XY").moveTo(0, 0).lineTo(rb, 0)
                   .bezier([(rb, length/5), (rb, 2*length/5),
                            (rt, 3*length/5), (rt, 4*length/5), (rt, length)],
                           includeCurrent=True)
                   .lineTo(0, length).close())
        neck = profile.revolve(360, (0, 0, 0), (0, 1, 0)).val().translate((self.axis, 0, 0))
        heel = cq.Solid.makeSphere(rb, cq.Vector(self.axis, 0, 0), angleDegrees1=-90)
        # Sequential unions retain the tangent sphere quadrant in OCC.
        outer = (x(rb, -self.barb_depth, self.axis).fuse(heel)
                 .fuse(neck).fuse(y(rt, length, self.mouth)))
        span = 4 * (self.barb_depth + self.mouth)
        clip = (cq.Solid.makeBox(span, span, span, cq.Vector(0, -span/2, -span/2))
                .rotate((0, 0, 0), (0, 0, 1), -45)
                .translate(cq.Vector(foot_offset/math.sqrt(2), -foot_offset/math.sqrt(2), 0)))
        outer = outer.cut(clip)
        if exterior:
            return outer if installed else outer.clean()
        lead = self.entry * math.tan(math.radians(60))
        cavity = x(bore_b, -self.barb_depth-.01, 0).fuse(
            cq.Solid.makeCone(bore_b+self.entry, bore_b, lead,
                             cq.Vector(-self.barb_depth, 0, 0), cq.Vector(1, 0, 0)),
            x(self.passage/2, 0, self.axis),
            y(self.passage/2, 0, self.tube_stop),
            y(bore_t, self.tube_stop, self.mouth+.01),
            cq.Solid.makeCone(bore_t, bore_t+self.entry, lead,
                             cq.Vector(self.axis, self.mouth-lead, 0), cq.Vector(0, 1, 0)))
        body = outer.cut(cavity)
        # Expanded envelopes are placement hypotheses. Keeping their native
        # face boundaries avoids a costly same-domain merge at tangent skins.
        return body if installed else body.clean()

    def print_shape(self, exterior=False):
        s = 1 / math.sqrt(2)
        posed = self.local(exterior=exterior).moved(cq.Location(cq.Plane(
            origin=(0, 0, 0), xDir=(s, 0, -s), normal=(0, -1, 0))))
        # The analytic foot plane is exact. Spline bounding boxes include a
        # conservative tolerance and would otherwise leave the foot above Z0.
        foot_offset = self.axis / math.sqrt(2) + self.passage / 2 + self.wall
        # The mouth rims are the extrema in print X; local Z is symmetric.
        xmin = (-self.barb_depth-self.barb_od/2) / math.sqrt(2)
        xmax = (self.axis+self.tube_od/2+self.mouth) / math.sqrt(2)
        return posed.translate(cq.Vector(-(xmin+xmax)/2, 0, foot_offset))

    def frame(self, tip, axis, toward):
        p = cq.Vector(*tip)
        x = cq.Vector(*axis).normalized()
        t = cq.Vector(*toward)
        y = (t - x*t.dot(x)).normalized()
        return p, x, y

    def placed(self, tip, axis, toward):
        p, x, y = self.frame(tip, axis, toward)
        return self.local(True).moved(cq.Location(cq.Plane(origin=p, xDir=x, normal=x.cross(y))))

    def tube_port(self, tip, axis, toward):
        p, x, y = self.frame(tip, axis, toward)
        return (p+x*self.axis+y*self.mouth).toTuple(), y.toTuple()

    def bands(self, tip, axis, toward):
        """Closed bands only. Their wing/screw envelopes are not represented."""
        p, x, y = self.frame(tip, axis, toward)
        out = {}
        for name, origin, normal, diameter in (
            ("barb", p-x*self.barb_depth, x, self.installed_barb_od),
            ("tube", p+x*self.axis+y*(self.mouth-self.band_width), y, self.installed_tube_od),
        ):
            outer = cq.Solid.makeCylinder(diameter/2+.6, self.band_width, origin, normal)
            inner = cq.Solid.makeCylinder(diameter/2, self.band_width, origin, normal)
            out[name] = outer.cut(inner)
        return out
