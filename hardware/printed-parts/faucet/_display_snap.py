"""Faucet-display cantilever trial geometry in local (x, s, n) coordinates.

The fixed shell carries two arms; a descending cover presses their lead-ins
inward until its ledges pass the flat retaining faces. The arms are unloaded
when seated. Physical force, retention and repeatability remain trial results.
"""
from __future__ import annotations

import cadquery as cq

BEAM_INNER_X = 10.3
BEAM_THICKNESS = 3.0
BEAM_OUTER_X = BEAM_INNER_X + BEAM_THICKNESS
BEAM_HEIGHT = 3.0
BEAM_TIP_S = 20.0
BEAM_ROOT_S = 48.0
ROOT_LENGTH = 5.0
ROOT_FILLET = 1.25
ROOT_SPREAD = 1.5
TOOTH_LENGTH = 3.0
TOOTH_S_END = BEAM_TIP_S + TOOTH_LENGTH
HARDWARE_GAP = 0.5
RADIAL_SLIP = 0.15
BEARING_SLIP = 0.15
ENGAGEMENT = 0.30
OVERTRAVEL = 0.50
RECEIVER_WALL = 3.0


def box(x0, x1, s0, s1, n0, n1):
    return cq.Workplane(obj=cq.Solid.makeBox(
        x1 - x0, s1 - s0, n1 - n0, cq.Vector(x0, s0, n0)))


def _hand(body, side):
    if side not in (-1, 1):
        raise ValueError("side must be -1 or +1")
    return body if side == 1 else body.mirror("YZ")


def beam_n_range(feet_n):
    top = feet_n - HARDWARE_GAP
    return top - BEAM_HEIGHT, top


def build_beam(feet_n, side=1, engagement=ENGAGEMENT):
    """One 3 × 3 mm arm with rounded root and a 45-degree tooth lead-in."""
    if not 0.0 < engagement < OVERTRAVEL:
        raise ValueError("engagement must be inside the hard-stop travel")
    bottom, top = beam_n_range(feet_n)
    arm = box(BEAM_INNER_X, BEAM_OUTER_X,
              BEAM_TIP_S, BEAM_ROOT_S, bottom, top)
    anchor = box(BEAM_INNER_X - ROOT_SPREAD, BEAM_OUTER_X + ROOT_SPREAD,
                 BEAM_ROOT_S, BEAM_ROOT_S + ROOT_LENGTH, bottom, top)
    body = arm.union(anchor)
    roots = [edge for edge in body.val().Edges()
             if abs(edge.Center().y - BEAM_ROOT_S) < 1e-5
             and abs(edge.Length() - BEAM_HEIGHT) < 1e-5
             and any(abs(edge.Center().x - x) < 1e-5
                     for x in (BEAM_INNER_X, BEAM_OUTER_X))]
    if len(roots) != 2:
        raise ValueError("cantilever root edges are not the expected pair")
    body = body.newObject(roots).fillet(ROOT_FILLET)
    projection = RADIAL_SLIP + engagement
    tooth_outer = BEAM_OUTER_X + projection
    points = [(BEAM_OUTER_X - 0.02, BEAM_TIP_S, bottom),
              (tooth_outer, BEAM_TIP_S, bottom),
              (tooth_outer, BEAM_TIP_S, top - projection),
              (BEAM_OUTER_X, BEAM_TIP_S, top),
              (BEAM_OUTER_X - 0.02, BEAM_TIP_S, top)]
    wire = cq.Wire.makePolygon([cq.Vector(*p) for p in points], close=True)
    tooth = cq.Workplane(obj=cq.Solid.extrudeLinear(
        wire, [], cq.Vector(0.0, TOOTH_LENGTH, 0.0)))
    return _hand(body.union(tooth), side)


def build_receiver(feet_n, side=1):
    """Cover ledge: 3 mm radial/normal stock and a flat retaining face."""
    bottom, _ = beam_n_range(feet_n)
    inner = BEAM_OUTER_X + RADIAL_SLIP
    top = bottom - BEARING_SLIP
    return _hand(box(inner, inner + RECEIVER_WALL,
                     BEAM_TIP_S - RADIAL_SLIP, TOOTH_S_END + RADIAL_SLIP,
                     top - RECEIVER_WALL, top), side)


def build_motion_clearance(feet_n, side=1):
    """Box around the free arm; its inner face is the 0.5 mm travel stop.

    Subtract before adding the arm. The root's last 1.25 mm carries its
    fillet and stays within the shell's solid anchor region.
    """
    bottom, top = beam_n_range(feet_n)
    return _hand(box(BEAM_INNER_X - OVERTRAVEL,
                     BEAM_OUTER_X + RADIAL_SLIP + OVERTRAVEL,
                     BEAM_TIP_S - RADIAL_SLIP,
                     BEAM_ROOT_S - ROOT_FILLET,
                     bottom - RADIAL_SLIP, top + RADIAL_SLIP), side)


def nominal_strain(engagement=ENGAGEMENT):
    """Ideal rectangular-beam surface strain, excluding local/print effects."""
    length = BEAM_ROOT_S - ROOT_FILLET - TOOTH_S_END
    return 1.5 * BEAM_THICKNESS * engagement / length ** 2
