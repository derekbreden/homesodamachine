//! The nameplate's shared receiver record in the normal enclosure graph.
use crate::compiled::{Env, Val};
use anyhow::Result;
use serde_json::json;
#[path="../../../../hardware/printed-parts/enclosure/nameplate/snap_dimensions.rs"]
mod dimensions;

fn spec(wing:&Val) -> Result<serde_json::Value> {
    Ok(dimensions::dimensions(wing.attr("WIDTH")?.num()?,wing.attr("HEIGHT")?.num()?,
        wing.attr("THICK")?.num()?,wing.attr("FACE_SLIP")?.num()?,
        wing.attr("SUPPORTED_END_AIR")?.num()?,wing.attr("FIELD_PROUD")?.num()?))
}

pub fn numbers(numbers:Val, e:&Env) -> Result<Val> {
    for key in ["wing_projection","wing_span","wing_thick","wing_corner","receiver"] {
        numbers.delete(key.into())?;
    }
    numbers.set("snap".into(),Val::decode(spec(&e.get("wing")?)?)?)?;
    Ok(numbers)
}

pub fn apply(graph:&Val, piece:Val, plan:Val, wing:Val) -> Result<Val> {
    let s=spec(&wing)?;
    let t=s["thick"].as_f64().unwrap();
    let x=plan.get("center_x_mm".into())?.num()?;
    let y=plan.get("face_y_mm".into())?.num()?-t;
    let z=plan.get("center_z_mm".into())?.num()?;
    let half=s["frame_width"].as_f64().unwrap()/2.;
    let bounds=json!([-half,half,-7.25,t,s["frame_bottom"],s["frame_top"]]);
    let add=|op:&str|->Result<Val>{
        let shape=graph.attr("add")?.call(vec![op.into()],vec![
            ("snap".into(),Val::decode(s.clone())?),
            ("bounds".into(),Val::decode(bounds.clone())?)])?;
        shape.attr("translate")?.call(vec![Val::decode(json!([x,y,z]))?],vec![])
    };
    let stock=piece.attr("fuse")?.call(vec![add("nameplate-stock")?],vec![])?;
    stock.attr("cut")?.call(vec![add("nameplate-cuts")?],vec![])
}

pub fn plain_lips(station:Val, face:Val, wing:Val) -> Result<Val> {
    let s=spec(&wing)?;
    let x=station.attr("x")?.num()?;
    let z=station.attr("z")?.num()?;
    let y=face.num()?;
    let half=s["frame_width"].as_f64().unwrap()/2.;
    Val::decode(json!([[x-half,x+half,y-11.,y+1.,
        z+s["frame_bottom"].as_f64().unwrap(),z+s["frame_top"].as_f64().unwrap()]]))
}
