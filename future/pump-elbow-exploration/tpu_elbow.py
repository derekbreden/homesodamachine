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

    def local(self, installed=False):
        rb = (self.installed_barb_od if installed else self.barb_od) / 2
        rt = (self.installed_tube_od if installed else self.tube_od) / 2
        bore_b = (reference.crest() if installed else self.barb_bore) / 2
        bore_t = (6.35 if installed else self.tube_bore) / 2
        k = rt
        past = self.axis + k
        foot_offset = self.axis / math.sqrt(2) + self.passage / 2 + self.wall
        x = lambda r, a, b: cq.Solid.makeCylinder(r, b-a, cq.Vector(a, 0, 0), cq.Vector(1, 0, 0))
        y = lambda r, a, b: cq.Solid.makeCylinder(r, b-a, cq.Vector(self.axis, a, 0), cq.Vector(0, 1, 0))
        outer = x(rb, -self.barb_depth, 0).fuse(
            cq.Solid.makeBox(past, 2*k, 2*k, cq.Vector(0, -k, -k)), y(rt, 0, self.mouth))
        span = 4 * (self.barb_depth + self.mouth)
        clip = (cq.Solid.makeBox(span, span, span, cq.Vector(0, -span/2, -span/2))
                .rotate((0, 0, 0), (0, 0, 1), -45)
                .translate(cq.Vector(foot_offset/math.sqrt(2), -foot_offset/math.sqrt(2), 0)))
        outer = outer.cut(clip)
        lead = self.entry * math.tan(math.radians(60))
        cavity = x(bore_b, -self.barb_depth-.01, .01).fuse(
            cq.Solid.makeCone(bore_b+self.entry, bore_b, lead,
                             cq.Vector(-self.barb_depth, 0, 0), cq.Vector(1, 0, 0)),
            x(self.passage/2, -.01, self.axis+.05),
            y(self.passage/2, -.05, self.tube_stop+.01),
            y(bore_t, self.tube_stop, self.mouth+.01),
            cq.Solid.makeCone(bore_t, bore_t+self.entry, lead,
                             cq.Vector(self.axis, self.mouth-lead, 0), cq.Vector(0, 1, 0)))
        return outer.cut(cavity).clean()

    def print_shape(self):
        s = 1 / math.sqrt(2)
        posed = self.local().moved(cq.Location(cq.Plane(
            origin=(0, 0, 0), xDir=(s, 0, -s), normal=(0, -1, 0))))
        b = posed.BoundingBox()
        return posed.translate(cq.Vector(-(b.xmin+b.xmax)/2, -(b.ymin+b.ymax)/2, -b.zmin))

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
