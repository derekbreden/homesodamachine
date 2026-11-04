//! Hidden pointed spring leaves and their matching receiver, shared by the
//! complete plate and enclosure-back-top. All dimensions come from one record.
use anyhow::{Context, Result};
use hsm_kernel::{Loop, Pen, Plane, Profile, Solid, v2, v3};
use serde_json::Value;

fn f(n: &Value, key: &str) -> f64 { n[key].as_f64().expect("snap dimension") }
fn ends(n: &Value, key: &str) -> (f64, f64) {
    (n[key][0].as_f64().unwrap(), n[key][1].as_f64().unwrap())
}
fn box_(x0:f64,x1:f64,y0:f64,y1:f64,z0:f64,z1:f64) -> Solid {
    Solid::cuboid(v3(x0,y0,z0),v3(x1,y1,z1))
}
fn xz(profile: Profile, y0:f64, y1:f64) -> Result<Solid> {
    Plane::XZ.at(v3(0.,y0,0.)).extrude(&profile,-(y1-y0))
}
fn mirror(shape: &Solid, side:f64) -> Solid {
    if side < 0. { shape.mirror(v3(0.,0.,0.),v3(1.,0.,0.)) } else { shape.clone() }
}

fn bent_leaf(n:&Value, side:f64, travel:f64) -> Result<Solid> {
    let (a,b)=(f(n,"leaf_inner"),f(n,"leaf_outer"));
    let (ra,rb)=ends(n,"root_x");
    let (z0,z1)=ends(n,"root_z");
    let r=f(n,"root_radius");
    let top=f(n,"leaf_top_z");
    let (y0,y1)=ends(n,"leaf_y");
    let q=r/2_f64.sqrt();
    let start=z1+r;
    let end=ends(n,"hook_z").0;
    let shift=|s:f64| travel*s*s*(3.-s)/2.;
    let mut pen=Pen::new(v2(ra,z0)).line_to(v2(rb,z0)).line_to(v2(rb,z1))
        .arc_through(v2(rb-q,z1+r-q),v2(b,start))?;
    if travel == 0. {
        pen=pen.line_to(v2(b,top)).line_to(v2(a,top)).line_to(v2(a,start));
    } else {
        for i in 1..=25 {
            let s=i as f64/25.;
            pen=pen.line_to(v2(b-shift(s),start+(end-start)*s));
        }
        pen=pen.line_to(v2(b-travel,top)).line_to(v2(a-travel,top))
            .line_to(v2(a-travel,end));
        for i in (0..25).rev() {
            let s=i as f64/25.;
            pen=pen.line_to(v2(a-shift(s),start+(end-start)*s));
        }
    }
    let outline=pen.arc_through(v2(ra+q,z1+r-q),v2(ra,z1))?.close()?;
    Ok(mirror(&xz(Profile::new(outline),y0,y1)?,side))
}

pub fn hook(n:&Value, side:f64) -> Result<Solid> {
    let x=f(n,"leaf_outer");
    let (ya,yb)=ends(n,"leaf_y");
    let (za,zb)=ends(n,"hook_z");
    // A single uninterrupted ramp to the point, with a flat retaining shoulder.
    let shape=Plane::XY.at(v3(0.,0.,za)).extrude(&Profile::polygon(&[
        v2(x-0.05,ya),v2(x,ya),v2(x+f(n,"hook_projection"),yb),v2(x-0.05,yb)
    ]),zb-za)?;
    Ok(mirror(&shape,side))
}

pub fn plate_blank(n:&Value) -> Result<Solid> {
    plate_at_deflection(n,0.)
}

/// A clearance pose for the manual insertion sweep. The hook moves inward as a
/// rigid head; the intervening beam follows the cantilever displacement curve.
/// This checks passage and available travel, not stress or material fatigue.
pub fn plate_at_deflection(n:&Value,travel:f64) -> Result<Solid> {
    let mut parts=vec![xz(Profile::new(Loop::rounded_rect(v2(0.,0.),
        f(n,"width"),f(n,"height"),f(n,"corner"))?),0.,f(n,"thick"))?];
    for side in [-1.,1.] {
        let (xa,xb)=ends(n,"root_x");
        let (za,zb)=ends(n,"root_z");
        parts.push(mirror(&box_(xa,xb,-4.,0.05,za,zb),side));
        parts.push(bent_leaf(n,side,travel)?);
        parts.push(hook(n,side)?.translate(v3(-side*travel,0.,0.)));
    }
    Solid::union_all(&parts)
}

pub fn receiver_stock(n:&Value) -> Result<Solid> {
    let (bottom,top)=(f(n,"frame_bottom"),f(n,"frame_top"));
    let rear=f(n,"floor_rear");
    let t=f(n,"thick");
    let frame=xz(Profile::new(Loop::rounded_rect(v2(0.,(bottom+top)/2.),
        f(n,"frame_width"),top-bottom,f(n,"frame_corner"))?),rear,t)?;
    // Back-top prints roof down: a 45 degree crown runs to the enclosure skin.
    let crown=Plane::YZ.at(v3(-f(n,"frame_width"),0.,0.)).extrude(&Profile::polygon(&[
        v2(f(n,"crown_y")-0.01,top+0.01),v2(t+0.01,top+0.01),v2(t+0.01,top-3.01)
    ]),2.*f(n,"frame_width"))?;
    let mut parts=vec![frame.cut(&crown)?];
    for side in [-1.,1.] {
        parts.push(mirror(&box_(f(n,"pocket_inner")-f(n,"pocket_stock"),
            f(n,"root_pocket_outer")+f(n,"pocket_stock"),
            f(n,"pocket_rear")-f(n,"pocket_stock"),rear+0.1,
            f(n,"pocket_bottom")-f(n,"pocket_stock"),
            f(n,"pocket_top")+f(n,"pocket_stock")),side));
    }
    Solid::union_all(&parts)
}

pub fn receiver_cuts(n:&Value) -> Result<Solid> {
    let air=f(n,"slip");
    let mouth=xz(Profile::new(Loop::rounded_rect(v2(0.,0.),f(n,"mouth_width"),
        f(n,"mouth_height"),f(n,"corner")+air)?),-air,f(n,"thick")+1.)?;
    let mut cuts=vec![mouth.clone(),mouth.translate(v3(0.,0.,-f(n,"supported")))];
    for side in [-1.,1.] {
        let inner=f(n,"pocket_inner");
        let rear=f(n,"pocket_rear");
        let zsplit=-5.-f(n,"supported");
        for cut in [
            box_(inner,f(n,"root_pocket_outer"),rear,-air,
                f(n,"pocket_bottom"),zsplit),
            box_(inner,f(n,"pocket_outer"),rear,f(n,"catch_rear"),
                zsplit,f(n,"pocket_top")),
            box_(inner,f(n,"catch_inner"),f(n,"catch_rear")-0.01,-air,
                zsplit,f(n,"pocket_top")),
            // Front access releases the leaf and permits lifting that side.
            // Two bearing bands remain either side of the centered tool opening.
            box_(f(n,"release_inner_x"),f(n,"release_outer_x"),rear,f(n,"thick")+1.,
                -f(n,"release_width_z")/2.,f(n,"release_width_z")/2.),
        ] { cuts.push(mirror(&cut,side)); }
    }
    Solid::union_all(&cuts).context("nameplate receiver cuts")
}

pub fn receiver(n:&Value) -> Result<Solid> {
    receiver_stock(n)?.cut(&receiver_cuts(n)?)
}
