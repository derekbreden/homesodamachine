//! The four-screw plate and blind-insert receiver share one dimension record.
use anyhow::Result;
use hsm_kernel::{Loop, Plane, Profile, Solid, v2, v3};
use serde_json::Value;

fn f(n: &Value, key: &str) -> f64 { n[key].as_f64().expect("mount dimension") }
pub fn stations(n:&Value) -> Vec<(f64,f64)> {
    n["stations"].as_array().unwrap().iter().map(|p|
        (p[0].as_f64().unwrap(),p[1].as_f64().unwrap())).collect()
}
fn xz(profile: Profile, y0:f64, y1:f64) -> Result<Solid> {
    Plane::XZ.at(v3(0.,y0,0.)).extrude(&profile,-(y1-y0))
}
pub fn cylinder_y(x:f64,z:f64,r:f64,y0:f64,y1:f64) -> Result<Solid> {
    xz(Profile::new(Loop::circle(v2(x,z),r)),y0,y1)
}
pub fn plate_cuts(n:&Value) -> Result<Solid> {
    let mut cuts=vec![];
    for (x,z) in stations(n) {
        cuts.push(cylinder_y(x,z,f(n,"clearance_diameter")/2.,-0.1,f(n,"thick")+1.)?);
        cuts.push(cylinder_y(x,z,f(n,"counterbore_diameter")/2.,
            f(n,"thick")-f(n,"counterbore_depth"),f(n,"thick")+1.)?);
    }
    Solid::union_all(&cuts)
}
pub fn plate_blank(n:&Value) -> Result<Solid> {
    xz(Profile::new(Loop::rounded_rect(v2(0.,0.),f(n,"width"),f(n,"height"),
        f(n,"corner"))?),0.,f(n,"thick"))?.cut(&plate_cuts(n)?)
}
pub fn receiver_stock(n:&Value) -> Result<Solid> {
    let (bottom,top)=(f(n,"frame_bottom"),f(n,"frame_top"));
    let t=f(n,"thick");
    let frame=xz(Profile::new(Loop::rounded_rect(v2(0.,(bottom+top)/2.),
        f(n,"frame_width"),top-bottom,f(n,"frame_corner"))?),f(n,"floor_rear"),t)?;
    // Back-top prints roof down: one 45 degree crown runs to the enclosure skin.
    let crown=Plane::YZ.at(v3(-f(n,"frame_width"),0.,0.)).extrude(&Profile::polygon(&[
        v2(f(n,"crown_y")-0.01,top+0.01),v2(t+0.01,top+0.01),
        v2(t+0.01,top-f(n,"field_proud")-0.01)
    ]),2.*f(n,"frame_width"))?;
    let mut parts=vec![frame.cut(&crown)?];
    // These short, broad insert lands coincide with the enclosure's existing
    // rear wall. They keep the standalone receiver model complete as well.
    for (x,z) in stations(n) {
        parts.push(cylinder_y(x,z,f(n,"insert_stock_radius"),
            f(n,"insert_stock_rear"),f(n,"floor_rear")+0.1)?);
    }
    Solid::union_all(&parts)
}
pub fn receiver_cuts(n:&Value) -> Result<Solid> {
    let mouth=xz(Profile::new(Loop::rounded_rect(v2(0.,0.),f(n,"mouth_width"),
        f(n,"mouth_height"),f(n,"corner")+f(n,"slip"))?),0.,f(n,"thick")+1.)?;
    let mut cuts=vec![mouth.clone(),mouth.translate(v3(0.,0.,-f(n,"supported")))];
    for (x,z) in stations(n) {
        // Upper bores end against the adjoining support floors. Lower bores
        // continue through the rear land into the cold-core clearance.
        let rear=if z>0. { f(n,"insert_stock_rear") } else { f(n,"pilot_rear") };
        cuts.push(cylinder_y(x,z,f(n,"pilot_diameter")/2.,rear,0.01)?);
    }
    Solid::union_all(&cuts)
}
pub fn receiver(n:&Value) -> Result<Solid> {
    receiver_stock(n)?.cut(&receiver_cuts(n)?)
}
/// Installed hardware envelopes. Threads and knurls are represented by their
/// major diameters; the insert's 0.3 mm radial thermal interference is intentional.
pub fn hardware(n:&Value) -> Result<Vec<(String,Solid,[f64;3])>> {
    let mut parts=vec![];
    let seat=f(n,"thick")-f(n,"counterbore_depth");
    for (i,(x,z)) in stations(n).into_iter().enumerate() {
        let screw=cylinder_y(x,z,f(n,"screw_diameter")/2.,seat-f(n,"screw_length"),seat)?
            .union(&cylinder_y(x,z,f(n,"head_diameter")/2.,seat,seat+f(n,"head_height"))?)?;
        let points=(0..6).map(|k| {
            let a=std::f64::consts::PI*k as f64/3.;
            let r=f(n,"hex_key")/2./(std::f64::consts::PI/6.).cos();
            v2(x+r*a.cos(),z+r*a.sin())
        }).collect::<Vec<_>>();
        let socket=xz(Profile::polygon(&points),seat+1.4,seat+f(n,"head_height")+0.1)?;
        parts.push((format!("nameplate-screw-{}",i+1),screw.cut(&socket)?,[0.025,0.025,0.025]));
        let insert=cylinder_y(x,z,f(n,"insert_diameter")/2.,-f(n,"insert_length"),0.)?
            .cut(&cylinder_y(x,z,1.3,-f(n,"insert_length")-0.1,0.1)?)?;
        parts.push((format!("nameplate-insert-{}",i+1),insert,[0.65,0.38,0.09]));
    }
    Ok(parts)
}
