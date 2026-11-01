//! The faucet's organizer, upright: round stock and its five eased passages.
//! `umbilical_organizer.py` keeps the mounting axes and the dimensions.
use anyhow::{Result, anyhow};
use hsm_faucet::{pair, rows};
use hsm_kernel::part::{args, write_printed};
use hsm_kernel::*;

fn main() -> Result<()> {
    let (n, out) = args()?;
    let length = n.f("length")?;
    let past = n.f("bore_overrun")?;
    let stock = Solid::cylinder(V3::ZERO, V3::Z, n.f("stock_radius")?, length)?;
    let mut body = stock.chamfer(&stock.edges("%Circle")?, n.f("outside_ease")?)?;
    for bore in rows(n.get("bores")?)? {
        let (x, y) = pair(&bore["center"])?;
        let f = |key: &str| bore[key].as_f64().ok_or_else(|| anyhow!("no {key} for {}", bore["name"]));
        let entry = f("entry")?;
        let cutters = if bore["name"] == "SIG" {
            let section = |z: f64, grow: f64| {
                let r = n.f("slot_depth")? / 2.0 + grow;
                let half = (n.f("slot_length")? - n.f("slot_depth")?) / 2.0;
                let conic = |cx, t0, t1| LoftEdge::Conic {
                    c: v3(cx, y, z), x: v3(r, 0.0, 0.0), y: v3(0.0, r, 0.0), t0, t1,
                };
                Ok::<_, anyhow::Error>(LoftSection::new(vec![
                    LoftEdge::Line { a: v3(x-half, y-r, z), b: v3(x+half, y-r, z) },
                    conic(x+half, -std::f64::consts::FRAC_PI_2, std::f64::consts::FRAC_PI_2),
                    LoftEdge::Line { a: v3(x+half, y+r, z), b: v3(x-half, y+r, z) },
                    conic(x-half, std::f64::consts::FRAC_PI_2, 3.0*std::f64::consts::FRAC_PI_2),
                ]))
            };
            vec![
                Solid::extrude(&section(-past, 0.0)?.region(), V3::Z, v3(0.0, 0.0, length + 2.0 * past))?,
                Solid::thru_sections(&[section(0.0, entry)?, section(entry, 0.0)?], true)?,
                Solid::thru_sections(&[section(length - entry, 0.0)?, section(length, entry)?], true)?,
            ]
        } else {
            let radius = f("radius")?;
            vec![
                Solid::cylinder(v3(x, y, -past), V3::Z, radius, length + 2.0 * past)?,
                Solid::cone(v3(x, y, 0.0), V3::Z, radius + entry, radius, entry)?,
                Solid::cone(v3(x, y, length - entry), V3::Z, radius, radius + entry, entry)?,
            ]
        };
        body = body.cut(&Solid::union_all(&cutters)?)?;
    }
    let name = n.text("name")?;
    println!("{}", write_printed(&out, name, &[Body {
        name, color: Some(n.color("color")?), solid: &body,
    }])?);
    Ok(())
}
