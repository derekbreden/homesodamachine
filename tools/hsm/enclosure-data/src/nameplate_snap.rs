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

/// File references keep the purchased hardware out of the printable plate's 3MF.
pub fn append_hardware(e:&Env) -> Result<()> {
    let model=crate::compiled::binary("truediv",e.get("directory")?,"nameplate-fasteners.step.npz".into())?;
    for index in 0..8 {
        let name=format!("nameplate-{}-{}",if index%2==0 {"screw"} else {"insert"},index/2+1);
        let instance=e.get("_model_instance")?.call(vec![model.clone(),name.into()],vec![
            ("indices".into(),Val::decode(json!([index]))?),
            ("transform".into(),e.get("transform")?)])?;
        e.get("instances")?.attr("append")?.call(vec![instance],vec![])?;
    }
    Ok(())
}
