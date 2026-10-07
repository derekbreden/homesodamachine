"""Simple native floor stock for an aft-growing funnel.

The wet cavity is the production rounded-mouth loft and straight drain bore.
A second copy of its ramp 6.6 mm below it supplies the floor stock. The actual
native minimum between the two lateral surfaces is checked by the generator;
it is 6.347 mm for the +90 mm study. The side collar retains 6 mm stock.
The plug, drain, brim, seat and cleaning datums retain their production values.
"""
import cadquery as cq
from cadquery.occ_impl.shapes import cut as cut_shapes, fuse as fuse_shapes
import funnel as f

FLOOR_VERTICAL_STOCK = 6.6


def build_solids(drop=f.drop, ramp_wall=f.collar_wall, outer_air=0.0):
    w,d=f.collar_w,f.collar_d
    bw,bd=w-2*f.collar_wall,d-2*f.collar_wall
    top=f.brim_thickness;rz=top-f.chute_h;nz=rz-f._ramp_rise
    end=-drop+f.plug_lift;x,y=f.neck_dx,f.neck_dy
    wet=f._loft_rc(bw,bd,0,0,rz,f.spout_id/2,x,y,nz,f.mouth_corner_r)
    # 1.1 times the air below the floor supplies at least the air in the normal
    # direction for the sampled/native floor grades; the actual final gap is checked.
    h=FLOOR_VERTICAL_STOCK+1.1*outer_air
    dry=f._loft_rc(bw+2*outer_air,bd+2*outer_air,0,0,rz-h,
                  f.spout_id/2+outer_air,x,y,nz-h,f.mouth_corner_r+outer_air)
    collar=f._rounded_box(w+2*outer_air,d+2*outer_air,f.collar_corner_r+outer_air,
                         rz-h-.01,.05+outer_air)
    brim=f._rounded_box(w+2*(f.brim_overhang+outer_air),d+2*(f.brim_overhang+outer_air),
                       f.brim_corner_r+outer_air,-outer_air,top+outer_air)
    cylinder=f._cyl(f.spout_id/2+f.spout_wall+outer_air,nz+outer_air,end-outer_air,x,y)
    plug=f.elbow_cradle.plug_outline(f.plug_width/2,0,0,f.plug_height).translate((x,y,end))
    if outer_air:
        plug=f.normal_envelope(plug,outer_air)
    solid=fuse_shapes(dry,collar,brim,cylinder,plug,tol=.0001).clean()
    solid=solid.intersect(f._box(1000,1000,end-outer_air,top+1,0,0)).clean()
    assert solid.isValid() and len(solid.Solids())==1
    cavity=fuse_shapes(f._rounded_box(bw,bd,f.mouth_corner_r,rz,top+1),wet,
                      f._cyl(f.spout_id/2,nz+.01,end-1,x,y),tol=.0001).clean()
    meta=dict(w=w,d=d,cx=0,cy=0,ncx=x,ncy=y,bore_w=bw,bore_d=bd,
      mouth_corner_r=f.mouth_corner_r,brim_overhang=f.brim_overhang,brim_margin=f.brim_margin,
      collar_wall=f.collar_wall,out_w=w+2*f.brim_overhang,out_d=d+2*f.brim_overhang,
      out_cx=0,out_cy=0,rim_ring=f.collar_wall+f.brim_overhang,spout_id=f.spout_id,
      top_z=top,ramp_top_z=rz,neck_z=nz,spout_land_z=nz-f.neck_blend_drop,
      end_z=end,neck_blend_drop=f.neck_blend_drop,sealing_radius=f.sealing_id/2,
      sealing_land=f.sealing_land,outlet_profile='straight cylindrical bore',
      floor_vertical_stock_mm=FLOOR_VERTICAL_STOCK)
    return solid,cavity,meta


def floor_surfaces():
    bw,bd=f.collar_w-12,f.collar_d-12
    rz=f.brim_thickness-f.chute_h;nz=rz-f._ramp_rise
    wet=f._loft_rc(bw,bd,0,0,rz,3,f.neck_dx,f.neck_dy,nz,f.mouth_corner_r)
    dry=wet.translate((0,0,-FLOOR_VERTICAL_STOCK))
    return tuple(cq.Compound.makeCompound([face for face in shape.Faces()
                 if face.geomType()!='PLANE']) for shape in (wet,dry))


def backing_envelope(shape,distance):
    """Conservative simple backing around the wet ramp for the tooling screen."""
    rz=f.brim_thickness-f.chute_h
    h=FLOOR_VERTICAL_STOCK+(distance-f.collar_wall)/.95+.5
    down=shape.translate((0,0,-h))
    ring=f._rounded_box(f.collar_w-12+2*distance,f.collar_d-12+2*distance,
        f.mouth_corner_r+distance,rz-h-.01,rz+distance)
    return fuse_shapes(shape,down,ring,tol=.0001).clean()


def core_finishing_stock(shape,distance,top):
    """A simple inset mouth and raised floor with measured normal finishing reserve."""
    rz=f.brim_thickness-f.chute_h;nz=rz-f._ramp_rise
    raised=distance*1.1
    bw,bd=f.collar_w-12-2*distance,f.collar_d-12-2*distance
    ramp=f._loft_rc(bw,bd,0,0,rz+raised,3-distance,
                   f.neck_dx,f.neck_dy,nz+raised,f.mouth_corner_r-distance)
    collar=f._rounded_box(bw,bd,f.mouth_corner_r-distance,rz+raised-.01,top)
    inset=fuse_shapes(ramp,collar,tol=.0001).clean()
    assert inset.isValid() and len(inset.Solids())==1
    assert inset.cut(shape,tol=.0001).Volume(tol=1e-9)<.0001
    boundary=cq.Compound.makeCompound([face for face in shape.Faces()
                                      if face.Center().z<top-.0001])
    measured=boundary.distance(inset)
    assert measured>=distance-.001,measured
    return inset
