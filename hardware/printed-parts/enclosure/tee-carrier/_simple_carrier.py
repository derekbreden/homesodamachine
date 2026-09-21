"""Broad-wall carrier geometry for the complete enclosure assembly trial.

Native paths and stock are geometric evidence; actual feel, retention and
rigidity are evaluated in the assembled enclosure. tee_carrier.py owns exports.
"""
from __future__ import annotations

import cadquery as cq

TOL = 1e-5
STAGING_Y = 33.0
SHELF_ADDED_Y = 0.0
SIDE_WEB_ADDED_Y = .90
SIDE_WEB_Z0 = 182.175
UPPER_CHEEK_ADDED_Y = 3.7


def box(xs, ys, zs):
    return cq.Solid.makeBox(xs[1]-xs[0], ys[1]-ys[0], zs[1]-zs[0],
                            cq.Vector(xs[0], ys[0], zs[0]))


def bounds(s):
    if not s.Solids() or s.Volume() < TOL:
        return None
    b = s.BoundingBox()
    return {v: [getattr(b,v+"min"),getattr(b,v+"max")] for v in "xyz"}


def teardrop(x,y,z,d,length):
    r=d/2
    cyl=cq.Solid.makeCylinder(r,length,cq.Vector(x,y,z),cq.Vector(0,1,0))
    p=cq.Plane(origin=(0,y,0),xDir=(1,0,0),normal=(0,-1,0))
    roof=cq.Workplane(p).polyline(((x-r/2**.5,z+r/2**.5),
                                  (x+r/2**.5,z+r/2**.5),(x,z+r*2**.5)))\
        .close().extrude(-length).val()
    return cyl.fuse(roof).clean()


def close_cups(blank,I):
    r=I["spring_bore_d"]/2
    x,z=I["spring_stations"][1]["x"],I["spring_stations"][1]["z"]
    y0,y1=I["spring_window_y"]
    xi=I["grip_back_x"]
    p=cq.Plane(origin=(0,y0,0),xDir=(1,0,0),normal=(0,-1,0))
    fill=cq.Workplane(p).polyline(((xi,z-r),(x,z-r),(x,z+r),
                                  (xi,z+r+x-xi))).close().extrude(y0-y1).val()
    cut=teardrop(x,y0-.1,z,I["spring_bore_d"],I["spring_bore_depth"]+.1)
    add=fill.cut(cut)
    return blank.fuse(add).fuse(add.mirror("YZ")).clean(), add


def relieve_rim(blank,I):
    # The deeper fixed cup ends 0.25 mm before the moving mouth at release.
    # A rectangular, openly accessible notch clears its outside during the
    # outward seating motion; bar stock and both spring floors are untouched.
    z=I["spring_stations"][1]["z"]
    r=(I["spring_bore_d"]+4)/2+.25
    notch=box((I["grip_rim_x"][0]-.01,I["grip_rim_x"][1]+.01),
              (I["grip_rim_y"][0]-.01,I["spring_bore_mouth_y"]),
              (z-r,z+r))
    removed=blank.intersect(notch)
    return blank.cut(notch).cut(notch.mirror("YZ")).clean(),removed


def relieve_entry_corner(blank,I,M):
    # The release-station outer tee must pass the inboard grip corner while
    # the half is still 3.25 mm inboard. Retain the complete web connection,
    # aft backing and outer guide-bearing region; remove one broad corner.
    outer=max(M["spec"]["tee_xs"])
    xend=outer+8.25+I["half_entry_shoulder_inset_x"]+.25
    cut=box((I["grip_back_x"]-.1,xend),
            (I["guide_body_y"][0]-.1,I["bearing_y"]-I["aft_limit_offset_y"]+.25),
            (I["printed_guide_body_z"][0]-.1,I["station_trough_top_z"]-.05))
    removed=blank.intersect(cut)
    return blank.cut(cut).cut(cut.mirror("YZ")).clean(),removed


def build_shapes(M, shapes):
    """Native broad-wall halves from the live continuous blank and fore lap."""
    I=dict(M["interface"])
    plain=shapes["continuous-blank"]
    blank,cup_add=close_cups(plain,I)
    blank,rim_removed=relieve_rim(blank,I)
    blank,entry_removed=relieve_entry_corner(blank,I,M)
    yf,ya=I["web_fore_y"],I["web_aft_y"]
    z0,z1=I["web_z"]
    fy,fz=I["flange_y"],I["flange_z"]
    shelf=box((-I["flange_x"],I["flange_x"]),fy,fz)
    shelf_y=(fy[0],fy[1]+SHELF_ADDED_Y)
    no_shelf=blank.cut(shelf)
    left=no_shelf.intersect(box((-150,-13),(0,200),(100,300)))
    right=no_shelf.intersect(box((-9.5,150),(0,200),(100,300)))
    zmid=(fz[0]+fz[1])/2
    shelf_top=z1
    # 31.85 mm overlap with 0.10 mm face clearance. The 4 mm left transition
    # remains half-depth for the 3.25 mm outward assembly motion.
    ls=box((-I["flange_x"],-26),shelf_y,fz).fuse(
        box((-26,9.85),shelf_y,(fz[0],zmid-.05)))
    rs=box((26,I["flange_x"]),shelf_y,fz).fuse(
        box((-22,26),shelf_y,(zmid+.05,shelf_top)))
    left=left.fuse(ls).fuse(shapes["fore-lap"])
    # A broad upper cheek makes the shelf a captured, load-bearing overlap.
    # It also bridges the left transition where only the lower shelf ply
    # remains during the incoming half's 3.25 mm outward seating motion.
    cap_y=(ya+6.21,shelf_y[1]+UPPER_CHEEK_ADDED_Y)
    cap=box((-26,20.5),cap_y,(shelf_top+.1,shelf_top+2.6))
    cap_root=box((-34,-26),cap_y,(fz[0],shelf_top+2.6))
    left=left.fuse(cap).fuse(cap_root)
    # A single full-height rail, with substantial closed end bridges and
    # a continuous backing wall; no separate headed keys or screw holes.
    rail_z=(z0+5,z1-5)
    neck=box((-2.5,8.5),(yf,ya-3.8),rail_z)
    head=box((-6.5,9.25),(ya-3.8,ya-1.8),rail_z)
    left=left.fuse(neck).fuse(head)
    housing=box((-9.5,15),(yf,ya),I["web_z"])
    right=right.fuse(rs).fuse(housing)
    entry=box((-3.5,12.75),(yf-.1,ya-3.65),(rail_z[0]-.15,rail_z[1]+.15))
    pocket=box((-6.65,12.75),(ya-3.8,ya-1.65),(rail_z[0]-.15,rail_z[1]+.15))
    right=right.cut(entry).cut(pocket)
    # The arriving right web must pass above the left shelf. Continue the
    # shelf's sliding clearance through that web, including its 3.25 mm
    # inboard pose. This is a declared interruption of the receiver rail.
    shelf_entry=box((-9.6,13.35),(yf-.1,ya+.6),(fz[0]-.10,zmid+.05))
    right=right.cut(shelf_entry)
    # Broad inner-web backing stands above the inner coils' forward features
    # throughout their underside entry. Its lower face clears their observed
    # Z181.925 upper extent by 0.25 mm. Its depth includes the complete
    # valve-entry route's 0.25 mm running air in the production derivation.
    # Stop below the shelf plies so their lateral entry remains unobstructed.
    left=left.fuse(box((-I["flange_x"],-13),(ya,ya+M["spec"]["side_web_added_y"]),(M["spec"]["side_web_z0"],fz[0])))
    right=right.fuse(box((15,I["flange_x"]),(ya,ya+M["spec"]["side_web_added_y"]),(M["spec"]["side_web_z0"],fz[0])))
    # All existing tie access and the strap on the rear plane remain clear
    # through the added receiver housing and fore-lap stock.
    for site in I["tie_sites"]:
        for x in site["slot_xs"]:
            cut=box((x-M["spec"]["tie_slot_x"]/2,x+M["spec"]["tie_slot_x"]/2),
                    (yf-6.1,ya+1.1),
                    (site["band_z"]-1.75,site["band_z"]+2))
            left=left.cut(cut)
            right=right.cut(cut)
        strap=box((min(site["slot_xs"])-.5,max(site["slot_xs"])+.5),
                  (ya,ya+1.1),(site["band_z"]-1.25,site["band_z"]+1.25))
        left=left.cut(strap)
        right=right.cut(strap)
    # Troughs and the upper tube relief continue through the added joint stock.
    for x in M["spec"]["tee_xs"]:
        trough=cq.Solid.makeCylinder(I["station_trough_r"],
            I["station_trough_top_z"]-(z0-1),
            cq.Vector(x,I["station_trough_axis_y"],z0-1),cq.Vector(0,0,1))
        stub=box((x-I["station_trough_r"],x+I["station_trough_r"]),
            (yf-6.1,I["stub_relief_y"]),(I["stub_relief_z0"],z1+1))
        left=left.cut(trough).cut(stub)
        right=right.cut(trough).cut(stub)
    # A broad cantilever behind the structural shelf catches the seated state.
    # Its full 51.75 x 9 x 3 mm wall is the spring. The beam interfaces fore
    # carry bending; this wall is not counted as a structural beam flange.
    back=shelf_y[1]
    low,high=fz[0]+1.925,fz[0]+10.925
    stop_root=box((-34,-26),(back-3,back+3.71),(fz[0],high))
    stop=box((-29,-26),(back+.71,back+3.71),(low,high))
    # Trim the rear of the root at the free wall's height: otherwise the
    # whole root, rather than the defined stop, would obstruct snap travel.
    stop_root=stop_root.cut(box((-34,-25.99),(back+.71,back+5),
                                (low,high+.1)))
    left=left.fuse(stop_root).fuse(stop)
    root=box((26,32),(back-3,back+5.91),(low,high))
    wall=box((-25.75,26),(back+2.91,back+5.91),(low,high))
    lip=box((-25.75,-22.75),(back+1.71,back+2.91),
            (low+.5,high-.5))
    right_rigid=right.fuse(root).clean()
    right=right_rigid.fuse(wall).fuse(lip).clean()
    left=left.clean()
    return M,I,plain,blank,left,right,right_rigid,wall,lip,head,neck,cup_add,rim_removed
