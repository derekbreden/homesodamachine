"""Forty-five-degree print roofs for the permanent TPU wet parts.

A teardrop section, a circle with a point, swept along one flow turn that lies in
its part's branch plane. The point faces up in the part's print frame: toward the
turn's centre for a passage roof, away from it for an exterior heel on the bed.
Socket sealing lands are not supplied to this function.
"""
import math
import cadquery as cq


def teardrop_sweep(segment, radius, *, inward, flank=45.):
    """One turn's teardrop solid; `flank` is each side's angle from the point axis."""
    s=cq.Vector(*segment['start_mm']);m=cq.Vector(*segment['midpoint_mm']);e=cq.Vector(*segment['end_mm'])
    t=cq.Vector(*segment['start_tangent']).normalized()
    centre=(m-s)-t*(m-s).dot(t)
    point=(centre if inward else centre*-1).normalized()
    across=t.cross(point).normalized()
    beta=math.radians(flank);theta=math.pi/2-beta
    apex=s+point*(radius/math.sin(beta))
    root=s+point*(radius*math.cos(theta))
    a=root+across*(radius*math.sin(theta));b=root-across*(radius*math.sin(theta))
    profile=cq.Wire.assembleEdges([cq.Edge.makeLine(apex,a),
                                   cq.Edge.makeThreePointArc(a,s-point*radius,b),
                                   cq.Edge.makeLine(b,apex)])
    path=cq.Wire.assembleEdges([cq.Edge.makeThreePointArc(s,m,e)])
    return cq.Solid.sweep(profile,[],path,makeSolid=True,isFrenet=False)
