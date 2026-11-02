//! Six tube collars, their bores and three faces of recessed identification.
use anyhow::{Result, anyhow};
use hsm_faucet::{pair, rows};
use hsm_kernel::part::{args, write_shown};
use hsm_kernel::*;
use serde_json::Value;

fn profiles(value: &Value, scale: f64) -> Result<Vec<Profile>> {
    let outline = |value: &Value| -> Result<Loop> {
        Loop::new(rows(value)?.iter().map(|seg| {
            let (kind, values) = seg.as_object().and_then(|o| o.iter().next())
                .ok_or_else(|| anyhow!("letter segments have controls"))?;
            let p = rows(values)?.iter().map(|v| {
                let (x,y) = pair(v)?; Ok(v2(x,y)*scale)
            }).collect::<Result<Vec<_>>>()?;
            Ok(match (kind.as_str(),p.as_slice()) {
                ("line", &[a,b]) => Seg::Line {a,b},
                ("quad", &[a,c,b]) => Seg::Quad {a,c,b},
                ("cubic", &[a,c1,c2,b]) => Seg::Cubic {a,c1,c2,b},
                _ => return Err(anyhow!("invalid letter {kind} segment")),
            })
        }).collect::<Result<_>>()?)
    };
    rows(value)?.iter().map(|p| Ok(Profile {
        outer: outline(&p["outer"])?,
        holes: rows(&p["holes"])?.iter().map(&outline).collect::<Result<_>>()?,
    })).collect()
}

fn main() -> Result<()> {
    let (n,out) = args()?;
    let r = n.f("od")?/2.0;
    let rise = n.f("rise")?;
    let length = n.f("length")?;
    let depth = n.f("word_depth")?;
    let scale = n.f("word_size")?/n.f("word_profiles_em")?;
    let outline = Profile::new(Pen::new(v2(-r,0.0)).line_to(v2(-r,rise))
        .line_to(v2(r,rise)).line_to(v2(r,0.0))
        .arc_through(v2(0.0,-r),v2(-r,0.0))?.close()?);
    let stock = Plane::new(v3(0.0,length,0.0),V3::X,-V3::Y)?.extrude(&outline,length)?;
    for station in rows(n.get("stations")?)? {
        let name = station["name"].as_str().ok_or_else(|| anyhow!("collar name"))?;
        let bore = station["bore"].as_f64().ok_or_else(|| anyhow!("collar bore"))?;
        let blank = stock.cut(&Solid::cylinder(V3::ZERO,V3::Y,bore/2.0,length)?)?;
        let flat = Solid::compose(&profiles(&station["word_profiles"],scale)?.iter()
            .map(|p|Plane::XY.extrude(p,depth)).collect::<Result<Vec<_>>>()?);
        let mut letters = vec![];
        for face in [0,1,-1] {
            let turned = if face == 0 {
                flat.rotate(V3::ZERO,V3::Z,90.0)
            } else {
                let side = flat.rotate(V3::ZERO,V3::X,90.0).rotate(V3::ZERO,V3::Z,90.0);
                if face < 0 {side.rotate(V3::ZERO,V3::Z,180.0)} else {side}
            };
            let b = turned.bounds();
            let shift = if face == 0 {
                v3(-(b.min.x+b.max.x)/2.0,length/2.0-(b.min.y+b.max.y)/2.0,
                   rise-depth-b.min.z)
            } else {
                v3(if face > 0 {r-b.max.x} else {-r-b.min.x},
                   length/2.0-(b.min.y+b.max.y)/2.0,
                   rise/2.0-(b.min.z+b.max.z)/2.0)
            };
            letters.push(turned.translate(shift));
        }
        let word = Solid::compose(&letters);
        let body = blank.cut(&word)?;
        let word_name = format!("{name}-word");
        let color = |key:&str| -> Result<[f64;3]> {
            let a=rows(&station[key])?;
            Ok([a[0].as_f64().unwrap(),a[1].as_f64().unwrap(),a[2].as_f64().unwrap()])
        };
        let mut said = write_shown(&out,name,&[
            Body{name,color:Some(color("color")?),solid:&body},
            Body{name:&word_name,color:Some(color("word_color")?),solid:&word},
        ])?;
        let stl = format!("{name}.stl");
        write_stl(out.join(&stl),&[&blank])?;
        said["files"].as_array_mut().unwrap().push(Value::String(stl));
        println!("{said}");
    }
    Ok(())
}
