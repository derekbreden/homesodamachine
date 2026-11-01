//! Rounded stock in the machine display's own frame.
use anyhow::{Result, anyhow, ensure};
use hsm_kernel::part::{args, write_part};
use hsm_kernel::{Body, Loop, Plane, Profile, Solid, v2, v3};
use serde_json::Value;

fn rounded(value: &Value) -> Result<Solid> {
    let values = value
        .as_array()
        .ok_or_else(|| anyhow!("display stock has dimensions"))?;
    ensure!(
        values.len() == 7,
        "display stock has width, height, radius, two faces and a centre"
    );
    let p = values
        .iter()
        .map(|v| {
            v.as_f64()
                .ok_or_else(|| anyhow!("a display dimension is numeric"))
        })
        .collect::<Result<Vec<_>>>()?;
    let outer = Loop::rounded_rect(v2(p[5], p[6]), p[0], p[1], p[2])?;
    Plane::XY.at(v3(0.0, 0.0, p[3])).extrude(
        &Profile {
            outer,
            holes: vec![],
        },
        p[4] - p[3],
    )
}

pub fn write() -> Result<()> {
    let (n, out) = args()?;
    let mut body = rounded(n.get("outer")?)?;
    for wing in n
        .get("wings")?
        .as_array()
        .ok_or_else(|| anyhow!("display wings are a list"))?
    {
        body = body.union(&rounded(wing)?)?;
    }
    body = body.cut(&rounded(n.get("window")?)?)?;
    println!(
        "{}",
        write_part(
            &out,
            n.text("name")?,
            &[Body {
                name: n.text("name")?,
                color: Some(n.color("color")?),
                solid: &body
            },]
        )?
    );
    Ok(())
}
