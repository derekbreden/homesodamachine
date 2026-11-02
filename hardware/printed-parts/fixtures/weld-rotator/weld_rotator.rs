//! The authored cap-weld rotator, in its existing world and print frames.
use anyhow::{ensure, Result};
use hsm_kernel::part::{self, AssemblyBody, Numbers};
use hsm_kernel::{v2, v3, Body, Curve, Edges, Loop, Pen, Plane, Profile, Solid, V2, V3};
use serde_json::json;
use std::collections::BTreeMap;

struct D<'a>(&'a Numbers);
impl D<'_> {
    fn f(&self, key: &str) -> f64 { self.0.f(key).expect(key) }
    fn list(&self, key: &str) -> Vec<f64> { self.0.list(key).expect(key) }
    fn points(&self, key: &str) -> Vec<(f64, f64)> {
        self.0.get(key).expect(key).as_array().expect(key).iter().map(|p| {
            let p = p.as_array().expect(key);
            (p[0].as_f64().expect(key), p[1].as_f64().expect(key))
        }).collect()
    }
    fn color(&self, key: &str) -> [f64; 3] {
        let p = &self.0.get("colors").expect("colors")[key];
        [p[0].as_f64().unwrap(), p[1].as_f64().unwrap(), p[2].as_f64().unwrap()]
    }
}
type Parts = BTreeMap<&'static str, Solid>;
fn box_at(x0: f64, x1: f64, y0: f64, y1: f64, z0: f64, z1: f64) -> Solid {
    Solid::cuboid(v3(x0, y0, z0), v3(x1, y1, z1))
}
fn cylinder(x: f64, y: f64, z: f64, r: f64, h: f64) -> Result<Solid> {
    Solid::cylinder(v3(x, y, z), V3::Z, r, h)
}
fn annulus(outer: f64, inner: f64, h: f64, z: f64) -> Result<Solid> {
    Plane::XY.at(v3(0.0, 0.0, z)).extrude(
        &Profile::circle(V2::ZERO, outer).with_hole(Loop::circle(V2::ZERO, inner)), h)
}
fn polygon(points: &[(f64, f64)], z: f64, h: f64) -> Result<Solid> {
    Plane::XY.at(v3(0.0, 0.0, z)).extrude(
        &Profile::polygon(&points.iter().map(|&(x,y)| v2(x,y)).collect::<Vec<_>>()), h)
}
fn polar(r: f64, angle: f64) -> (f64, f64) {
    let a = angle.to_radians(); (r * a.cos(), r * a.sin())
}
fn radial(angle: f64, r: f64, z: f64, diameter: f64, depth: f64) -> Result<Solid> {
    let (x, y) = polar(r, angle); let (dx, dy) = polar(-1.0, angle);
    Solid::cylinder(v3(x,y,z), v3(dx,dy,0.0), diameter / 2.0, depth)
}
fn counterbore(d: &D, x: f64, y: f64, z: f64, through: f64) -> Result<Solid> {
    Solid::union_all(&[
        cylinder(x,y,z,d.f("M3_SHANK_D")/2.0,through)?,
        cylinder(x,y,z-d.f("M3_HEAD_DEPTH"),d.f("M3_HEAD_D")/2.0,d.f("M3_HEAD_DEPTH")+0.01)?,
    ])
}
fn slot(x0: f64, x1: f64, y: f64, diameter: f64, z: f64, h: f64) -> Result<Solid> {
    Solid::union_all(&[
        box_at(x0,x1,y-diameter/2.0,y+diameter/2.0,z,z+h),
        cylinder(x0,y,z,diameter/2.0,h)?, cylinder(x1,y,z,diameter/2.0,h)?,
    ])
}
fn teardrop(d: &D, radius: f64, x: f64, z: f64, y0: f64, y1: f64) -> Result<Solid> {
    let a = d.f("GROUND_TEARDROP_ROOF_ANGLE").to_radians();
    let half = radius * a.sin(); let tangent = z + radius * a.cos();
    let roof = Plane::XZ.at(v3(0.0,y0,0.0)).extrude(&Profile::polygon(&[
        v2(x-half,tangent),v2(x+half,tangent),v2(x,z+radius/a.cos()),
    ]), -(y1-y0))?;
    Solid::cylinder(v3(x,y0,z),V3::Y,radius,y1-y0)?.union(&roof)
}
fn sector(outer: f64, inner: f64, half: f64, z: f64, h: f64) -> Result<Solid> {
    let (x,y) = polar(outer+5.0,half);
    annulus(outer,inner,h,z)?.intersect(&polygon(&[(0.0,0.0),(x,-y),(x,y)],z,h)?)
}
fn belt(d: &D, center: f64, z0: f64, z1: f64, margin: f64) -> Result<Solid> {
    let inner=d.f("BELT_TOOTH_HEIGHT")+d.f("BELT_PITCH_LINE_OFFSET")+margin;
    let outer=d.f("BELT_THICKNESS")-d.f("BELT_TOOTH_HEIGHT")-d.f("BELT_PITCH_LINE_OFFSET")+margin;
    let (big,small)=(d.f("TABLE_PITCH_R"),d.f("MOTOR_PITCH_R"));
    let a=((big-small)/center).acos();
    let ring=|offset:f64| -> Result<Loop> {
        let (rb,rs)=(big+offset,small+offset);
        let bu=v2(rb*a.cos(),rb*a.sin());let bl=v2(bu.x,-bu.y);
        let su=v2(center+rs*a.cos(),rs*a.sin());let sl=v2(su.x,-su.y);
        Pen::new(bu).arc_center(V2::ZERO,bl,true).line_to(sl)
            .arc_center(v2(center,0.0),su,true).line_to(bu).close()
    };
    // The authored tangent wraps and spans form one continuous annular section.
    // Keep their exact shared endpoints so the cut has no internal span caps.
    Plane::XY.at(v3(0.0,0.0,z0)).extrude(
        &Profile::new(ring(outer)?).with_hole(ring(-inner)?),z1-z0)
}
fn race_tool(d: &D) -> Result<Solid> {
    let mut region=Profile::circle(v2(d.f("BALL_RACE_R"),d.f("BALL_CENTER_Z")),
                                   d.f("RACE_CUT_R")).place(&Plane::XZ);
    // This bearing surface curves in two directions. Halve each existing
    // meridian arc so its error and the rotary error fit the shared rule.
    for ring in &mut region.loops {
        let (mut points,mut edges)=(Vec::new(),Vec::new());
        for i in 0..ring.pts.len() {
            let (a,b,edge)=(ring.pts[i],ring.pts[(i+1)%ring.pts.len()],ring.seg[i]);
            points.push(a);edges.push(edge);
            if let Curve::Circle{c,axis,..}=region.curves[edge as usize] {
                let (u,v,n)=(a-c,b-c,axis.unit());
                let turn=u.cross(v).dot(n).atan2(u.dot(v));
                for j in 1..2 {
                    let (s,co)=(turn*j as f64/2.0).sin_cos();
                    points.push(c+u*co+n.cross(u)*s+n*(n.dot(u)*(1.0-co)));
                    edges.push(edge);
                }
            }
        }
        ring.pts=points;ring.seg=edges;
    }
    Solid::revolve(&region,V3::ZERO,V3::Z,360.0)
}
fn rounded_box(x: f64,y: f64,w: f64,h: f64,z: f64,height: f64,r: f64) -> Result<Solid> {
    Plane::XY.at(v3(0.0,0.0,z)).extrude(&Profile::new(Loop::rounded_rect(v2(x,y),w,h,r)?),height)
}
fn base(d: &D) -> Result<Solid> {
    let height=d.f("BASE_Z");let mut cuts=vec![
        cylinder(0.0,0.0,0.0,d.f("SPOOL_CLEARANCE_D")/2.0,height)?,
        cylinder(0.0,0.0,0.0,d.f("SPOOL_POCKET_D")/2.0,d.f("SPOOL_POCKET_H"))?,
        race_tool(d)?,
    ];
    for x in [d.f("BASE_X_MIN")+d.f("BENCH_HOLE_MARGIN"),d.f("BASE_X_MAX")-d.f("BENCH_HOLE_MARGIN")] {
        for y in [d.f("BASE_Y_MIN")+d.f("BENCH_HOLE_MARGIN"),d.f("BASE_Y_MAX")-d.f("BENCH_HOLE_MARGIN")] {
            cuts.push(cylinder(x,y,0.0,d.f("BENCH_HOLE_D")/2.0,height)?);
        }
    }
    for (x,y) in d.points("BASE_FOOT_CENTERS") { for dx in [-d.f("BASE_FOOT_SCREW_X"),d.f("BASE_FOOT_SCREW_X")] {
        cuts.push(cylinder(x+dx,y,0.0,d.f("NEST_SCREW_D")/2.0,height)?);
        cuts.push(cylinder(x+dx,y,height-d.f("M3_HEAD_DEPTH"),d.f("M3_HEAD_D")/2.0,d.f("M3_HEAD_DEPTH")+0.01)?);
    }}
    for (x,y) in d.points("TOWER_MOUNT_POINTS").into_iter().chain(d.points("GROUND_BASE_POINTS")) {
        cuts.push(cylinder(x,y,height-d.f("M5_INSERT_DEPTH"),d.f("M5_INSERT_D")/2.0,d.f("M5_INSERT_DEPTH")+0.01)?);
    }
    rounded_box(d.f("BASE_CENTER_X"),0.0,d.f("BASE_X"),d.f("BASE_Y"),0.0,height,d.f("BASE_CORNER_R"))?.cut_all(&cuts)
}
fn foot(d: &D) -> Result<Solid> {
    let h=d.f("BASE_FOOT_H");let mut cuts=vec![];
    for x in [-d.f("BASE_FOOT_SCREW_X"),d.f("BASE_FOOT_SCREW_X")] {
        cuts.push(cylinder(x,0.0,0.0,d.f("NEST_SCREW_D")/2.0,h)?);
        cuts.push(cylinder(x,0.0,h-d.f("BASE_FOOT_INSERT_DEPTH"),d.f("BASE_FOOT_INSERT_D")/2.0,d.f("BASE_FOOT_INSERT_DEPTH")+0.01)?);
    }
    rounded_box(0.0,0.0,d.f("BASE_FOOT_X"),d.f("BASE_FOOT_Y"),0.0,h,4.0)?.cut_all(&cuts)
}
fn toothed_ring(d: &D) -> Result<Solid> {
    let width=|r:f64|d.f("GROOVE_ROOT_HALF_W")+(d.f("GROOVE_TIP_HALF_W")-d.f("GROOVE_ROOT_HALF_W"))*(r-d.f("PULLEY_ROOT_R"))/d.f("PULLEY_GROOVE_DEPTH");
    let (outer,inner)=(d.f("PULLEY_TIP_R")+d.f("GROOVE_OVERCUT"),d.f("PULLEY_ROOT_R")-d.f("GROOVE_UNDERCUT"));
    let groove=polygon(&[(outer,-width(outer)),(inner,-width(inner)),(inner,width(inner)),(outer,width(outer))],d.f("PULLEY_TOOTH_Z0"),d.f("PULLEY_TOOTH_H"))?;
    let cuts=(0..d.f("TABLE_PULLEY_TEETH") as usize).map(|i|groove.rotate(V3::ZERO,V3::Z,i as f64*360.0/d.f("TABLE_PULLEY_TEETH"))).collect::<Vec<_>>();
    let core=annulus(d.f("PULLEY_TIP_R"),d.f("PULLEY_INNER_R"),d.f("PULLEY_Z1")-d.f("PULLEY_Z0"),d.f("PULLEY_Z0"))?.cut_all(&cuts)?;
    Solid::union_all(&[core,
        annulus(d.f("PULLEY_FLANGE_R"),d.f("PULLEY_INNER_R"),d.f("PULLEY_FLANGE_H"),d.f("PULLEY_Z0"))?,
        annulus(d.f("PULLEY_FLANGE_R"),d.f("PULLEY_INNER_R"),d.f("PULLEY_FLANGE_H"),d.f("PULLEY_Z1")-d.f("PULLEY_FLANGE_H"))?,
    ])
}
fn turntable(d: &D, pulley: &Solid) -> Result<Solid> {
    let solid=Solid::union_all(&[
        annulus(d.f("PLATTER_R"),d.f("SERVICE_BORE_D")/2.0,d.f("PLATTER_Z1")-d.f("PLATTER_Z0"),d.f("PLATTER_Z0"))?,
        annulus(d.f("PEDESTAL_R"),d.f("SERVICE_BORE_D")/2.0,d.f("NEST_SEAT_Z")-d.f("PLATTER_Z1"),d.f("PLATTER_Z1"))?,
        pulley.clone(),annulus(d.f("REGISTER_OD")/2.0,d.f("SERVICE_BORE_D")/2.0,d.f("REGISTER_H"),d.f("NEST_SEAT_Z"))?,
    ])?;
    let mut cuts=vec![];
    for angle in d.list("NEST_RETAINER_ANGLES") {let (x,y)=polar(d.f("NEST_SCREW_R"),angle);
        cuts.push(cylinder(x,y,d.f("NEST_SEAT_Z")-d.f("NEST_INSERT_DEPTH"),d.f("NEST_INSERT_D")/2.0,d.f("NEST_INSERT_DEPTH")+0.01)?);}
    for (angles,radius,depth) in [("SPOOL_SCREW_ANGLES","SPOOL_SCREW_R","SPOOL_INSERT_DEPTH"),("RACE_RING_SCREW_ANGLES","RACE_RING_SCREW_R","RACE_RING_INSERT_DEPTH")] {
        for angle in d.list(angles) {let (x,y)=polar(d.f(radius),angle);cuts.push(cylinder(x,y,d.f("PLATTER_Z0")-0.01,d.f("M3_INSERT_D")/2.0,d.f(depth)+0.01)?);}
    }
    solid.cut_all(&cuts)
}
fn race_ring(d: &D) -> Result<Solid> {
    let mut cuts=vec![race_tool(d)?];
    for angle in d.list("RACE_RING_SCREW_ANGLES") {let (x,y)=polar(d.f("RACE_RING_SCREW_R"),angle);
        cuts.push(counterbore(d,x,y,d.f("RACE_RING_Z0")+d.f("M3_HEAD_DEPTH"),d.f("RACE_RING_H")-d.f("M3_HEAD_DEPTH")+0.02)?);}
    annulus(d.f("RACE_RING_OUTER_R"),d.f("RACE_RING_INNER_R"),d.f("RACE_RING_H"),d.f("RACE_RING_Z0"))?.cut_all(&cuts)
}
fn spool(d: &D) -> Result<Solid> {
    let solid=Solid::union_all(&[
        annulus(d.f("SPOOL_FLANGE_OD")/2.0,d.f("SERVICE_BORE_D")/2.0,d.f("SPOOL_FLANGE_H"),d.f("SPOOL_FLANGE_Z0"))?,
        annulus(d.f("SPOOL_HUB_OD")/2.0,d.f("SERVICE_BORE_D")/2.0,d.f("PLATTER_Z0")-d.f("SPOOL_HUB_Z0"),d.f("SPOOL_HUB_Z0"))?,
    ])?;
    let cuts=d.list("SPOOL_SCREW_ANGLES").into_iter().map(|angle|{let (x,y)=polar(d.f("SPOOL_SCREW_R"),angle);
        counterbore(d,x,y,d.f("SPOOL_FLANGE_Z0")+d.f("M3_HEAD_DEPTH"),d.f("PLATTER_Z0")-d.f("SPOOL_FLANGE_Z0")-d.f("M3_HEAD_DEPTH")+0.02)}).collect::<Result<Vec<_>>>()?;
    solid.cut_all(&cuts)
}
fn cage(d: &D) -> Result<Solid> {
    let cuts=(0..d.f("BALL_COUNT") as usize).map(|i|{let(x,y)=polar(d.f("BALL_RACE_R"),360.0*i as f64/d.f("BALL_COUNT"));
        cylinder(x,y,d.f("CAGE_Z"),d.f("CAGE_POCKET_D")/2.0,d.f("CAGE_H"))}).collect::<Result<Vec<_>>>()?;
    annulus(d.f("CAGE_OUTER_R"),d.f("CAGE_INNER_R"),d.f("CAGE_H"),d.f("CAGE_Z"))?.cut_all(&cuts)
}
fn nest(d: &D) -> Result<Solid> {
    let (inner,outer)=(d.f("NEST_CENTER_BORE_D")/2.0,(d.f("REGISTER_OD")+d.f("REGISTER_SLIP"))/2.0);
    let depth=d.f("REGISTER_SOCKET_DEPTH");
    let roof=Plane::XZ.revolve(&Profile::polygon(&[v2(inner,depth),v2(outer,depth),v2((inner+outer)/2.0,depth+d.f("REGISTER_ROOF_H"))]),360.0,V2::ZERO,v2(0.0,1.0))?;
    let base=annulus(d.f("NEST_OD")/2.0,inner,d.f("NEST_BASE_H"),0.0)?.cut_all(&[annulus(outer,inner,depth,0.0)?,roof])?;
    let solid=Solid::union_all(&[base,
        annulus(d.f("PILOT_OD")/2.0,d.f("PILOT_ID")/2.0,d.f("PILOT_H"),d.f("NEST_BASE_H"))?,
        annulus(d.f("OUTER_COLLAR_OD")/2.0,d.f("OUTER_BORE_D")/2.0,d.f("NEST_OUTER_H"),d.f("NEST_BASE_H"))?,
    ])?;
    let mut cuts=vec![];
    for angle in d.list("TUBE_ADJUSTER_ANGLES") {
        cuts.push(radial(angle,d.f("OUTER_COLLAR_OD")/2.0+0.1,d.f("TUBE_ADJUSTER_Z"),d.f("TUBE_ADJUSTER_INSERT_D"),d.f("TUBE_ADJUSTER_INSERT_DEPTH")+0.2)?);
        let start=d.f("OUTER_COLLAR_OD")/2.0-d.f("TUBE_ADJUSTER_INSERT_DEPTH");
        cuts.push(radial(angle,start,d.f("TUBE_ADJUSTER_Z"),d.f("M3_ADJUSTER_SHANK_D"),start-d.f("OUTER_BORE_D")/2.0+0.2)?);
    }
    for angle in d.list("NEST_RETAINER_ANGLES") {let (x,y)=polar(d.f("NEST_SCREW_R"),angle);
        cuts.push(cylinder(x,y,0.0,d.f("NEST_SCREW_D")/2.0,d.f("NEST_BASE_H"))?);
        cuts.push(cylinder(x,y,d.f("NEST_BASE_H")-d.f("M3_HEAD_DEPTH"),d.f("NEST_RETAINER_ACCESS_D")/2.0,d.f("M3_HEAD_DEPTH")+d.f("NEST_OUTER_H")+0.01)?);
    }
    solid.cut_all(&cuts)
}
fn motor_tower(d: &D) -> Result<Solid> {
    let mut pieces=vec![];
    for sign in [-1.0,1.0] {
        let (a,b)=if sign<0.0{(-d.f("TOWER_Y_HALF"),-d.f("TOWER_FOOT_Y0"))}else{(d.f("TOWER_FOOT_Y0"),d.f("TOWER_Y_HALF"))};
        pieces.push(box_at(d.f("TOWER_X0"),d.f("TOWER_X1"),a,b,d.f("TOWER_Z0"),d.f("TOWER_FOOT_Z1")));
        let (a,b)=if sign<0.0{(-d.f("TOWER_Y_HALF"),-d.f("TOWER_RAIL_Y0"))}else{(d.f("TOWER_RAIL_Y0"),d.f("TOWER_Y_HALF"))};
        pieces.push(box_at(d.f("TOWER_X0"),d.f("TOWER_X1"),a,b,d.f("TOWER_FOOT_Z1"),d.f("TOWER_Z1")));
    }
    pieces.push(box_at(d.f("TOWER_REAR_X0"),d.f("TOWER_X1"),-d.f("TOWER_Y_HALF"),d.f("TOWER_Y_HALF"),d.f("TOWER_Z0"),d.f("TOWER_Z1")));
    let seat=d.f("TOWER_FOOT_Z1")-d.f("M5_HEAD_DEPTH");let mut cuts=vec![];
    for (x,y) in d.points("TOWER_MOUNT_POINTS") {
        cuts.push(cylinder(x,y,d.f("TOWER_Z0")-0.01,d.f("M5_SHANK_D")/2.0,seat-d.f("TOWER_Z0")+0.02)?);
        cuts.push(cylinder(x,y,seat,d.f("M5_HEAD_D")/2.0,d.f("TOWER_Z1")-seat+0.01)?);
    }
    for x in d.list("TOWER_RAIL_INSERT_X") {for sign in [-1.0,1.0] {
        cuts.push(cylinder(x,sign*d.f("TOWER_RAIL_INSERT_Y"),d.f("TOWER_Z1")-d.f("TOWER_RAIL_INSERT_DEPTH"),d.f("M3_INSERT_D")/2.0,d.f("TOWER_RAIL_INSERT_DEPTH")+0.01)?);
    }}
    Solid::union_all(&pieces)?.cut_all(&cuts)
}
fn motor_carriage(d: &D) -> Result<Solid> {
    let center=d.f("MOTOR_CENTER_NOMINAL");let mut cuts=vec![];
    for c in [d.f("MOTOR_CENTER_MIN"),center,d.f("MOTOR_CENTER_MAX")] {
        cuts.push(belt(d,c,d.f("BELT_Z0")-1.0,d.f("BELT_Z1")+1.0,d.f("CARRIAGE_BELT_MARGIN"))?.translate(v3(center-c,0.0,0.0)));
    }
    cuts.push(cylinder(center,0.0,d.f("CARRIAGE_ARM_Z0")-0.01,d.f("CARRIAGE_PILOT_D")/2.0,d.f("CARRIAGE_SKIN_Z0")-d.f("CARRIAGE_ARM_Z0")+0.02)?);
    let arms=box_at(d.f("CARRIAGE_X0"),d.f("CARRIAGE_X1"),-d.f("CARRIAGE_Y_HALF"),d.f("CARRIAGE_Y_HALF"),d.f("CARRIAGE_ARM_Z0"),d.f("CARRIAGE_SKIN_Z0")).cut_all(&cuts)?;
    let skin=box_at(d.f("CARRIAGE_X0"),d.f("CARRIAGE_X1"),-d.f("CARRIAGE_Y_HALF"),d.f("CARRIAGE_Y_HALF"),d.f("CARRIAGE_SKIN_Z0"),d.f("MOTOR_FACE_Z")).cut(&cylinder(center,0.0,d.f("CARRIAGE_SKIN_Z0")-0.01,d.f("CARRIAGE_PILOT_D")/2.0,d.f("CARRIAGE_SKIN_H")+0.02)?)?;
    let mut pieces=vec![arms,skin];let mut cuts=vec![];
    for sign in [-1.0,1.0] {
        let (y0,y1)=if sign<0.0{(-d.f("CARRIAGE_WALL_Y1"),-d.f("CARRIAGE_WALL_Y0"))}else{(d.f("CARRIAGE_WALL_Y0"),d.f("CARRIAGE_WALL_Y1"))};
        pieces.push(box_at(center-d.f("CARRIAGE_WALL_X_HALF"),center+d.f("CARRIAGE_WALL_X_HALF"),y0,y1,d.f("MOTOR_FACE_Z"),d.f("MOTOR_FACE_Z")+d.f("CARRIAGE_WALL_H")));
        for x in [-d.f("MOTOR_CLAMP_SCREW_X"),d.f("MOTOR_CLAMP_SCREW_X")] {
            let origin=v3(center+x,sign*(d.f("CARRIAGE_WALL_Y1")+0.01),d.f("MOTOR_CLAMP_SCREW_Z"));
            cuts.push(Solid::cylinder(origin,v3(0.0,-sign,0.0),d.f("M3_ADJUSTER_SHANK_D")/2.0,d.f("CARRIAGE_WALL_Y1")-d.f("CARRIAGE_WALL_Y0")+0.02)?);
            cuts.push(Solid::cylinder(origin,v3(0.0,-sign,0.0),d.f("M3_INSERT_D")/2.0,d.f("MOTOR_CLAMP_INSERT_DEPTH")+0.01)?);
        }
        let x=d.f("MOTOR_MOUNT_X");let y=sign*d.f("MOTOR_MOUNT_Y");
        cuts.push(cylinder(x,y,d.f("CARRIAGE_ARM_Z0")-0.01,d.f("M5_SHANK_D")/2.0,d.f("MOTOR_FACE_Z")-d.f("CARRIAGE_ARM_Z0")+0.02)?);
        cuts.push(Solid::cone(v3(x,y,d.f("CARRIAGE_ARM_Z0")),V3::Z,d.f("MOTOR_MOUNT_CSK_D")/2.0,d.f("M5_SHANK_D")/2.0,d.f("MOTOR_MOUNT_CSK_DEPTH"))?);
        for x in d.list("TOWER_RAIL_INSERT_X") {
            let x0=x-(d.f("MOTOR_CENTER_MAX")-center);let x1=x+(center-d.f("MOTOR_CENTER_MIN"));
            cuts.push(slot(x0,x1,sign*d.f("TOWER_RAIL_INSERT_Y"),2.0*d.f("MOTOR_SLOT_R"),d.f("CARRIAGE_ARM_Z0")-0.01,d.f("MOTOR_FACE_Z")-d.f("CARRIAGE_ARM_Z0")+0.02)?);
            cuts.push(slot(x0,x1,sign*d.f("TOWER_RAIL_INSERT_Y"),d.f("M3_HEAD_D"),d.f("MOTOR_FACE_Z")-d.f("M3_HEAD_DEPTH"),d.f("M3_HEAD_DEPTH")+0.01)?);
        }
    }
    Solid::union_all(&pieces)?.cut_all(&cuts)
}
fn clamp_pad(d: &D) -> Result<Solid> {
    let cuts=[-d.f("MOTOR_CLAMP_SCREW_X"),d.f("MOTOR_CLAMP_SCREW_X")].into_iter().map(|x|
        Solid::cylinder(v3(x,-d.f("MOTOR_CLAMP_PAD_Y")/2.0,d.f("MOTOR_CLAMP_PAD_Z")/2.0),V3::Y,d.f("MOTOR_CLAMP_SOCKET_D")/2.0,d.f("MOTOR_CLAMP_SOCKET_DEPTH"))).collect::<Result<Vec<_>>>()?;
    box_at(-d.f("MOTOR_CLAMP_PAD_X")/2.0,d.f("MOTOR_CLAMP_PAD_X")/2.0,-d.f("MOTOR_CLAMP_PAD_Y")/2.0,d.f("MOTOR_CLAMP_PAD_Y")/2.0,0.0,d.f("MOTOR_CLAMP_PAD_Z")).cut_all(&cuts)
}
fn ground_tower(d: &D) -> Result<Solid> {
    let solid=Solid::union_all(&[
        box_at(d.f("GROUND_FOOT_X0"),d.f("GROUND_FOOT_X1"),d.f("GROUND_FOOT_Y0"),d.f("GROUND_FOOT_Y1"),d.f("GROUND_FOOT_Z0"),d.f("GROUND_FOOT_Z1")),
        box_at(d.f("GROUND_POST_X0"),d.f("GROUND_POST_X1"),d.f("GROUND_POST_Y0"),d.f("GROUND_POST_Y1"),d.f("GROUND_FOOT_Z1"),d.f("GROUND_TOP_Z")),
    ])?;
    let mut cuts=vec![];
    for (x,y) in d.points("GROUND_BASE_POINTS") {
        cuts.push(cylinder(x,y,d.f("GROUND_FOOT_Z0"),d.f("M5_SHANK_D")/2.0,d.f("GROUND_FOOT_Z1")-d.f("GROUND_FOOT_Z0"))?);
        cuts.push(cylinder(x,y,d.f("GROUND_FOOT_Z1")-d.f("M5_HEAD_DEPTH"),d.f("M5_HEAD_D")/2.0,d.f("M5_HEAD_DEPTH"))?);
    }
    for (x,y) in d.points("GROUND_ARM_POINTS") {cuts.push(cylinder(x,y,d.f("GROUND_TOP_Z")-d.f("GROUND_ARM_INSERT_DEPTH"),d.f("GROUND_ARM_INSERT_D")/2.0,d.f("GROUND_ARM_INSERT_DEPTH")+0.01)?);}
    solid.cut_all(&cuts)
}
fn ground_arm(d: &D) -> Result<Solid> {
    let z=d.f("GROUND_TOP_Z");let top=z+d.f("GROUND_ARM_H");
    let spring=Solid::union_all(&[
        box_at(d.f("GROUND_PAD_X0"),d.f("GROUND_PAD_X1"),d.f("GROUND_PAD_Y0"),d.f("GROUND_PAD_Y1"),z,top),
        box_at(d.f("GROUND_BEAM_X0"),d.f("GROUND_BEAM_X1"),d.f("GROUND_BEAM_Y0"),d.f("GROUND_BEAM_Y1"),z,top),
        box_at(d.f("GROUND_BEAM_X0"),d.f("GROUND_HOLDER_BACK_FACE_X"),-d.f("GROUND_NOSE_Y")/2.0,d.f("GROUND_NOSE_Y")/2.0,z,top),
    ])?;
    let points=[(d.f("GROUND_BEAM_X0"),d.f("GROUND_PAD_Y1")),(d.f("GROUND_BEAM_X1"),d.f("GROUND_PAD_Y1")),(d.f("GROUND_BEAM_X0"),d.f("GROUND_NOSE_Y")/2.0),(d.f("GROUND_BEAM_X1"),-d.f("GROUND_NOSE_Y")/2.0)];
    let edges=Edges(spring.edges("|Z")?.iter().filter(|e|points.iter().any(|&(x,y)|(e.center.x-x).hypot(e.center.y-y)<1e-6)).cloned().collect());
    ensure!(edges.len()==points.len(),"ground spring corner selection changed");
    let h=d.f("GROUND_SHOE_Z0");let h1=h+d.f("GROUND_HOLDER_H");
    let solid=Solid::union_all(&[
        spring.fillet(&edges,d.f("GROUND_SPRING_FILLET_R"))?,
        box_at(d.f("GROUND_HOLDER_BACK_FACE_X")-d.f("GROUND_HOLDER_BACK_T"),d.f("GROUND_HOLDER_BACK_FACE_X"),d.f("GROUND_HOLDER_CLAMP_OUTER_Y"),d.f("GROUND_HOLDER_FIXED_OUTER_Y"),h,h1),
        box_at(d.f("GROUND_HOLDER_BACK_FACE_X"),d.f("GROUND_HOLDER_FRONT_X"),d.f("GROUND_HOLDER_CLAMP_OUTER_Y"),d.f("GROUND_HOLDER_CLAMP_INNER_Y"),h,h1),
        box_at(d.f("GROUND_HOLDER_BACK_FACE_X"),d.f("GROUND_HOLDER_FRONT_X"),d.f("GROUND_HOLDER_FIXED_INNER_Y"),d.f("GROUND_HOLDER_FIXED_OUTER_Y"),h,h1),
        box_at(d.f("GROUND_HOLDER_SHELF_X0"),d.f("GROUND_HOLDER_FRONT_X"),d.f("GROUND_HOLDER_CLAMP_OUTER_Y"),d.f("GROUND_HOLDER_FIXED_OUTER_Y"),h-d.f("GROUND_HOLDER_SHELF_H"),h),
    ])?;
    let mut cuts=vec![];
    for (x,y) in d.points("GROUND_ARM_POINTS") {
        cuts.push(cylinder(x,y,z,d.f("GROUND_ARM_SHANK_D")/2.0,d.f("GROUND_ARM_H"))?);
        cuts.push(cylinder(x,y,top-d.f("M3_HEAD_DEPTH"),d.f("M3_HEAD_D")/2.0,d.f("M3_HEAD_DEPTH"))?);
    }
    for (diameter,end) in [("GROUND_SHOE_CLAMP_SHANK_D",d.f("GROUND_HOLDER_CLAMP_INNER_Y")+0.1),("GROUND_SHOE_CLAMP_INSERT_D",d.f("GROUND_HOLDER_CLAMP_OUTER_Y")+d.f("GROUND_SHOE_CLAMP_INSERT_DEPTH"))] {
        cuts.push(teardrop(d,d.f(diameter)/2.0,d.f("GROUND_SHOE_CLAMP_X"),d.f("GROUND_SHOE_CLAMP_Z"),d.f("GROUND_HOLDER_CLAMP_OUTER_Y")-0.1,end)?);
    }
    solid.cut_all(&cuts)
}
fn motor(d: &D, center: f64) -> Result<Solid> {
    let z=d.f("MOTOR_FACE_Z");Solid::union_all(&[
        box_at(center-d.f("MOTOR_FRAME")/2.0,center+d.f("MOTOR_FRAME")/2.0,-d.f("MOTOR_FRAME")/2.0,d.f("MOTOR_FRAME")/2.0,z,z+d.f("MOTOR_BODY_LENGTH")),
        cylinder(center,0.0,z-d.f("MOTOR_PILOT_LENGTH"),d.f("MOTOR_PILOT_DIAMETER")/2.0,d.f("MOTOR_PILOT_LENGTH"))?,
        cylinder(center,0.0,z-d.f("MOTOR_SHAFT_LENGTH"),d.f("MOTOR_SHAFT_DIAMETER")/2.0,d.f("MOTOR_SHAFT_LENGTH"))?,
    ])
}
fn motor_pulley(d: &D, center: f64) -> Result<Solid> {
    Solid::union_all(&[
        annulus(d.f("MOTOR_PULLEY_CORE_D")/2.0,d.f("MOTOR_SHAFT_DIAMETER")/2.0,d.f("MOTOR_LAND_Z1")-d.f("MOTOR_LAND_Z0"),d.f("MOTOR_LAND_Z0"))?,
        annulus(d.f("MOTOR_PULLEY_FLANGE_D")/2.0,d.f("MOTOR_SHAFT_DIAMETER")/2.0,d.f("MOTOR_PULLEY_FLANGE_LENGTH"),d.f("MOTOR_PULLEY_Z0"))?,
        annulus(d.f("MOTOR_PULLEY_FLANGE_D")/2.0,d.f("MOTOR_SHAFT_DIAMETER")/2.0,d.f("MOTOR_PULLEY_FLANGE_LENGTH"),d.f("MOTOR_PULLEY_Z1")-d.f("MOTOR_PULLEY_FLANGE_LENGTH"))?,
    ]).map(|s|s.translate(v3(center,0.0,0.0)))
}
fn tube(d: &D) -> Result<Solid> {
    annulus(d.f("TUBE_OD")/2.0,d.f("TUBE_ID")/2.0,d.f("TUBE_LENGTH"),d.f("NEST_SEAT_Z")+d.f("NEST_BASE_H"))
}
fn build(d: &D) -> Result<Parts> {
    let pulley=toothed_ring(d)?;
    let coupon=pulley.intersect(&sector(d.f("PULLEY_FLANGE_R")+1.0,d.f("PULLEY_INNER_R")-1.0,d.f("COUPON_TEETH")*360.0/d.f("TABLE_PULLEY_TEETH")/2.0,d.f("PULLEY_Z0"),d.f("PULLEY_Z1")-d.f("PULLEY_Z0"))?)?.translate(v3(0.0,0.0,-d.f("PULLEY_Z0")));
    let mut parts=BTreeMap::from([
        ("base",base(d)?),("base-foot",foot(d)?),("turntable",turntable(d,&pulley)?),
        ("race-ring",race_ring(d)?),("spool",spool(d)?),("pulley-coupon",coupon),
        ("ball-cage",cage(d)?),("tube-nest",nest(d)?),("motor-tower",motor_tower(d)?),
        ("motor-carriage",motor_carriage(d)?),("motor-clamp-pad",clamp_pad(d)?),
        ("ground-tower",ground_tower(d)?),("ground-arm",ground_arm(d)?),
        ("ground-shoe",box_at(d.f("GROUND_SHOE_BACK_X"),d.f("GROUND_SHOE_FRONT_X"),-d.f("GROUND_SHOE_Y")/2.0,d.f("GROUND_SHOE_Y")/2.0,d.f("GROUND_SHOE_Z0"),d.f("GROUND_SHOE_Z0")+d.f("GROUND_SHOE_Z"))),
    ]);
    for (name,solid) in &mut parts {
        solid.check()?;ensure!(solid.volume()>0.0,"{name} has no volume");
        solid.forget_backend();
    }
    Ok(parts)
}
fn assembly(d: &D, parts: &Parts) -> Result<Vec<(String,Solid,[f64;3])>> {
    let pet=d.color("M_PETGF_BLACK");let mut rows=vec![];
    for (i,(x,y)) in d.points("BASE_FOOT_CENTERS").into_iter().enumerate() {
        rows.push((format!("base-foot-{}",i+1),parts["base-foot"].translate(v3(x,y,-d.f("BASE_FOOT_H"))),pet));
    }
    for (part,name) in [("base","stationary-base"),("motor-tower","motor-tower"),("motor-carriage","motor-carriage"),("ground-tower","ground-tower"),("ground-arm","ground-flexure-arm"),("turntable","turntable-90t"),("race-ring","upper-race-ring"),("ball-cage","ball-cage"),("spool","spool")] {
        rows.push((name.into(),parts[part].clone(),pet));
    }
    let y=d.f("MOTOR_FRAME")/2.0+d.f("MOTOR_CLAMP_PAD_Y")/2.0;
    rows.push(("motor-clamp-pad-negative-y".into(),parts["motor-clamp-pad"].translate(v3(d.f("MOTOR_CENTER_NOMINAL"),-y,d.f("MOTOR_FACE_Z")+2.0)),pet));
    rows.push(("motor-clamp-pad-positive-y".into(),parts["motor-clamp-pad"].rotate(V3::ZERO,V3::Z,180.0).translate(v3(d.f("MOTOR_CENTER_NOMINAL"),y,d.f("MOTOR_FACE_Z")+2.0)),pet));
    rows.push(("c110-ground-shoe".into(),parts["ground-shoe"].clone(),d.color("M_COPPER")));
    rows.push(("tube-nest".into(),parts["tube-nest"].translate(v3(0.0,0.0,d.f("NEST_SEAT_Z"))),pet));
    let balls=(0..d.f("BALL_COUNT") as usize).map(|i|{let (x,y)=polar(d.f("BALL_RACE_R"),360.0*i as f64/d.f("BALL_COUNT"));Solid::sphere(v3(x,y,d.f("BALL_CENTER_Z")),d.f("BALL_D")/2.0)}).collect::<Result<Vec<_>>>()?;
    rows.push(("10mm-pp-balls".into(),Solid::compose(&balls),d.color("M_TPU_BLACK")));
    rows.push(("23hs30-2804s".into(),motor(d,d.f("MOTOR_CENTER_NOMINAL"))?,d.color("M_STAINLESS")));
    rows.push(("20t-htd5m-pulley".into(),motor_pulley(d,d.f("MOTOR_CENTER_NOMINAL"))?,d.color("M_ALUMINIUM")));
    let z=(d.f("BELT_Z0")+d.f("BELT_Z1"))/2.0-d.f("BELT_WIDTH")/2.0;
    rows.push(("550-5m-15-belt".into(),belt(d,d.f("MOTOR_CENTER_NOMINAL"),z,z+d.f("BELT_WIDTH"),0.0)?,d.color("M_TPU_BLACK")));
    rows.push(("5in-316l-tube".into(),tube(d)?,d.color("M_STAINLESS")));
    Ok(rows)
}
fn main() -> Result<()> {
    let (n,out)=part::args()?;let d=D(&n);let mut parts=build(&d)?;
    let mut files=vec![];let mut bodies=vec![];
    for (&name,solid) in &mut parts {
        let stem=if name=="turntable" {"weld-rotator-turntable-90t".to_owned()}else{format!("weld-rotator-{name}")};
        let color=d.color(if name=="ground-shoe"{"M_COPPER"}else{"M_PETGF_BLACK"});
        let said=if name=="ground-shoe" {part::write_shown(&out,&stem,&[Body{name:"c110-ground-shoe",color:Some(color),solid}])?}
            else{part::write_part(&out,&stem,&[Body{name,color:Some(color),solid}])?};
        files.extend(said["files"].as_array().unwrap().iter().cloned());
        bodies.extend(said["bodies"].as_array().unwrap().iter().cloned());
        solid.forget_backend();
    }
    let mut rows=assembly(&d,&parts)?;
    for (_,solid,_) in &mut rows { solid.forget_backend(); }
    let mut lower=rows[0].1.bounds().min;let mut upper=rows[0].1.bounds().max;
    for (_,s,_) in &rows {let b=s.bounds();lower=lower.min(b.min);upper=upper.max(b.max);}
    let size=upper-lower;let linear=(size.x+size.y+size.z)/3.0*d.f("presentation_ratio");
    let angular=d.f("BALL_D")/2.0*(1.0-(d.f("presentation_angle")/2.0).cos());
    let tolerance=linear.min(angular);
    let shown=rows.iter_mut().map(|(_,s,_)| {
        let mut shown=s.simplified_to(tolerance)?;
        s.forget_backend();shown.forget_backend();Ok(shown)
    }).collect::<Result<Vec<_>>>()?;
    let instances=rows.iter().zip(&shown).map(|((name,fine,color),presentation)|AssemblyBody{name,color:Some(*color),fine,presentation}).collect::<Vec<_>>();
    let said=part::write_assembly_with_root(&out,"weld-rotator-assembly","weld-rotator",&instances,Some(&json!({"presentation_tolerance_mm":tolerance})))?;
    files.extend(said["files"].as_array().unwrap().iter().cloned());
    println!("{}",json!({"files":files,"bodies":bodies}));
    Ok(())
}
