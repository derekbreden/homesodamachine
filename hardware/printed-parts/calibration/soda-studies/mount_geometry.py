"""A rear-face bearing and simple locator for the intact source snap host.

The host uses native X/S/N coordinates. The adapter extends behind its S55
crop, while a short elliptical locator enters only the existing passage. Its
clearance is a measured minimum, not a uniform offset from the passage wall.
The original host, grooves and exterior surfaces are unchanged.
"""
from __future__ import annotations

import cadquery as cq
import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert

from source_features import transform_shape

REAR_S_MM = 55.
BEARING_END_S_MM = 60.25
LOCATOR_INSERTION_MM = 1.8
LOCATOR_RADII_MM = (5.6, 8.)
LOCATOR_CENTER_N_MM = -1.9
# Manual CAD reading for the frozen complete source host, throughout the full
# insertion: minimum surface separation 0.2015646773 mm, intersection 0 mm³.
# Physical fit is unmeasured; the gap varies around the elliptical locator.
MEASURED_LOCATOR_MINIMUM_AIR_MM = .2015646773
DEFAULT_ORIGIN_MM = (0., -1., 66.45)


def _native_adapter(host):
    native = host.native_shape()
    face = max((face for face in native.Faces()
                if face.BoundingBox().ylen < 1e-5 and abs(face.Center().y-REAR_S_MM) < 1e-4),
               key=lambda face: face.Area())
    # The source inner wire contains finite hyperbola segments. Represent those
    # same bounded conics as rational B-splines before extrusion: OCC's domain
    # unifier overflows on their analytic hyperbolic extrusion surfaces. This
    # changes only the adapter representation, with no added profile breaks.
    profile = cq.Face(BRepBuilderAPI_NurbsConvert(face.wrapped, True).Shape())
    bearing = cq.Solid.extrudeLinear(profile.outerWire(), profile.innerWires(),
                                    cq.Vector(0, BEARING_END_S_MM-REAR_S_MM, 0))
    plane = cq.Plane(origin=(0, REAR_S_MM, LOCATOR_CENTER_N_MM),
                     xDir=(1, 0, 0), normal=(0, -1, 0))
    ellipse = cq.Workplane(plane).ellipse(*LOCATOR_RADII_MM).val()
    locator = cq.Solid.extrudeLinear(ellipse, [], cq.Vector(0, -LOCATOR_INSERTION_MM, 0))
    column = cq.Solid.extrudeLinear(ellipse.translate((0, -LOCATOR_INSERTION_MM, 0)), [],
                                   cq.Vector(0, BEARING_END_S_MM-REAR_S_MM+LOCATOR_INSERTION_MM, 0))
    # The rear column backs the whole locator footprint from the basin, keeping
    # its first deposits supported. The web joins that column to the annular
    # bearing wholly behind the crop; neither changes any original host wall.
    web = cq.Solid.makeBox(22., BEARING_END_S_MM-REAR_S_MM, 4.,
                          cq.Vector(-11., REAR_S_MM, -1.))
    return bearing.fuse(web).fuse(column), locator, face, profile


def source_host_foot(host, origin=DEFAULT_ORIGIN_MM):
    """Return the adapter in the basin's shared manufacturing/display frame.

    Pose is Rx -90°, then Rz 180°, then translation by origin. At the default
    origin the rear bearing spans world Z6.20..11.45 and the continuously
    backed locator reaches Z13.25, 1.8 mm into the original host's passage.
    """
    body, _, _, _ = _native_adapter(host)
    matrix = np.array([[-1., 0., 0., float(origin[0])],
                       [0., 0., -1., float(origin[1])],
                       [0., -1., 0., float(origin[2])],
                       [0., 0., 0., 1.]])
    return transform_shape(body, matrix).clean()
