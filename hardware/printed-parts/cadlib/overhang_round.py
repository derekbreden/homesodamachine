"""Additive print-down chamfer tangent to a retained round.

The outward run is one half of the build rise: 0.12 mm per 0.24 mm layer.
The profile is qualified on the PET-GF tee carrier. Bearing planes and the
original part envelope remain the limits of each fill.
"""
import math
import cadquery as cq

OUTWARD_PER_HEIGHT = .5


def transition(radius):
    slope = OUTWARD_PER_HEIGHT
    height = radius-radius*slope/math.sqrt(1+slope*slope)
    inset = radius-radius/math.sqrt(1+slope*slope)
    return height,inset+slope*height


def roof_rim(before, rounded, x_face, inward, y0, y1, roof, corner, radius):
    """Fill only a hand-pocket's upper exterior round, including its corner returns.

    The pocket's flat ceiling and its original YZ corner centres stay fixed.
    At each depth, a quarter-ellipse joins the unchanged standing side return
    to the filled roof profile. The smooth loft samples the circular depth
    profile every two degrees and includes both chamfer endpoints explicitly.
    The final union is additive and stays within the unrounded stock.
    """
    height,foot = transition(radius)
    tangent_depth = foot-OUTWARD_PER_HEIGHT*height
    depths = {radius*(1-math.sin(math.radians(a))) for a in range(0,91,2)}
    depths.update((0.0,radius,foot,tangent_depth))
    wires=[]
    for depth in sorted(depths):
        side = radius-math.sqrt(max(0,radius*radius-(radius-depth)**2))
        top = side if depth <= tangent_depth else max(0,(foot-depth)/OUTWARD_PER_HEIGHT)
        x = x_face+inward*depth
        base = roof-corner-1
        zl = roof-corner
        left,right = y0+corner,y1-corner
        def v(y,z): return cq.Vector(x,y,z)
        edges=[cq.Edge.makeLine(v(y0-side,base),v(y1+side,base)),
               cq.Edge.makeLine(v(y1+side,base),v(y1+side,zl)),
               cq.Edge.makeEllipse(corner+side,corner+top,(x,right,zl),
                                   (1,0,0),(0,1,0),0,90),
               cq.Edge.makeLine(v(right,roof+top),v(left,roof+top)),
               cq.Edge.makeEllipse(corner+side,corner+top,(x,left,zl),
                                   (1,0,0),(0,1,0),90,180),
               cq.Edge.makeLine(v(y0-side,zl),v(y0-side,base))]
        wires.append(cq.Wire.assembleEdges(edges))
    air = cq.Solid.makeLoft(wires,ruled=False)
    xa,xb=sorted((x_face,x_face+inward*radius))
    cap=cq.Solid.makeBox(xb-xa,y1-y0+2*radius,corner+radius+.001,
                        cq.Vector(xa,y0-radius,roof-corner))
    fill=before.intersect(cap).cut(air)
    return rounded.fuse(fill).clean()


def three_side_fill(inner,outer,low,high,radius,plane):
    """Two rounded outer corners and an open inner edge, on a print-bottom plane."""
    height,foot=transition(radius)
    def section(h,inset):
        r=radius-inset
        cx=outer-radius
        q=math.sqrt(2)
        at=cq.Plane(origin=plane.origin+plane.zDir*h,xDir=plane.xDir,normal=plane.zDir)
        return (cq.Workplane(at).moveTo(inner,low+inset).lineTo(cx,low+inset)
                .threePointArc((cx+r/q,low+radius-r/q),(outer-inset,low+radius))
                .lineTo(outer-inset,high-radius)
                .threePointArc((cx+r/q,high-radius+r/q),(cx,high-inset))
                .lineTo(inner,high-inset).close().wire().val())
    return cq.Solid.makeLoft([section(0,foot),
                             section(height,foot-OUTWARD_PER_HEIGHT*height)],ruled=True)


def rectangular_edge_fill(x0,x1,y0,y1,z_top,radius):
    """An additive cap at a box's +Z/±X edges (printed with +Z on the bed).

    Intersection with the unrounded envelope keeps standing plan corners and
    other faces exact. The cap ends at the original circular tangent.
    """
    height,foot=transition(radius)
    fills=[]
    for side,edge in ((-1,x0),(1,x1)):
        pts=[(edge-side*radius,z_top),(edge-side*foot,z_top),
             (edge-side*(foot-OUTWARD_PER_HEIGHT*height),z_top-height),
             (edge-side*radius,z_top-height)]
        wire=cq.Wire.makePolygon([cq.Vector(x,y0,z) for x,z in pts]+[cq.Vector(pts[0][0],y0,pts[0][1])])
        fills.append(cq.Solid.extrudeLinear(wire,[],cq.Vector(0,y1-y0,0)))
    return cq.Compound.makeCompound(fills)
