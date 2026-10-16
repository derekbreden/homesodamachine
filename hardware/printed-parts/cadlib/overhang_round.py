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


def pocket_rim(before, x_face, inward, y0, y1, z0, roof, corner, radius, floor=True):
    """Round a hand pocket's complete exterior rim, with the chamfer under its roof.

    The pocket spans y0..y1 and z0..roof with `corner` YZ corner rounds, and
    `inward` points from its exterior face, x = x_face, into the stock. A pocket
    without a floor opens out through z0. The rim rolls `radius` round the whole
    opening; under the roof the roll runs on into the additive chamfer of
    `transition`, and at each depth a quarter-ellipse joins the standing side
    return to that roof profile. The pocket's flat ceiling and its original YZ
    corner centres stay fixed.

    The rim's air is two smooth lofts that sample the circular depth profile
    every two degrees and include both chamfer endpoints. They meet at the
    chamfer's foot, where the roof creases into the flat ceiling; inboard of it
    only the corner returns are lofted, so the ceiling between them remains the
    pocket's own plane. A section 0.01 mm either side of the foot holds both
    lofts on the profile's own tangent there, so the walls and floor roll across
    the joint without a crease.
    """
    height,foot = transition(radius)
    tangent_depth = foot-OUTWARD_PER_HEIGHT*height
    depths = {radius*(1-math.sin(math.radians(a))) for a in range(0,91,2)}
    depths.update((0.0,radius,foot,tangent_depth,foot-.01,foot+.01))
    zl,zf = roof-corner,z0+corner
    left,right = y0+corner,y1-corner
    def section(depth,ceiling):
        side = radius-math.sqrt(max(0,radius*radius-(radius-depth)**2))
        top = side if depth <= tangent_depth else max(0,(foot-depth)/OUTWARD_PER_HEIGHT)
        x = x_face+inward*depth
        def v(y,z): return cq.Vector(x,y,z)
        def arc(cy,cz,rz,a0,a1):
            return cq.Edge.makeEllipse(corner+side,rz,(x,cy,cz),(1,0,0),(0,1,0),a0,a1)
        if floor:
            low = zf
            under=[arc(left,zf,corner+side,180,270),
                   cq.Edge.makeLine(v(left,z0-side),v(right,z0-side)),
                   arc(right,zf,corner+side,270,360)]
        else:
            low = z0-1
            under=[cq.Edge.makeLine(v(y0-side,low),v(y1+side,low))]
        across=([cq.Edge.makeLine(v(right,roof+top),v(left,roof+top))] if ceiling else
                [cq.Edge.makeLine(v(right,roof),v(right,zl)),
                 cq.Edge.makeLine(v(right,zl),v(left,zl)),
                 cq.Edge.makeLine(v(left,zl),v(left,roof))])
        edges=[*under,
               cq.Edge.makeLine(v(y1+side,low),v(y1+side,zl)),
               arc(right,zl,corner+top,0,90),
               *across,
               arc(left,zl,corner+top,90,180),
               cq.Edge.makeLine(v(y0-side,zl),v(y0-side,low))]
        return cq.Wire.assembleEdges(edges)
    depths = sorted(depths)
    return before.cut(
        cq.Solid.makeLoft([section(d,True) for d in depths if d <= foot],ruled=False),
        cq.Solid.makeLoft([section(d,False) for d in depths if d >= foot],ruled=False)).clean()


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
