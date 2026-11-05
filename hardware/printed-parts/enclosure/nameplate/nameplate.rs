//! The four-screw nameplate and its recessed insert receiver. `nameplate.py` carries the dimensions,
//! original SVG control points and the unit's QR polygons.
mod snap_geometry;

use anyhow::{Result, anyhow, ensure};
use hsm_kernel::part::{Numbers, args, write_part, write_shown};
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V2, v2, v3};
use hsm_enclosure_components::write_colored_part;
use serde_json::{Value, json};

fn f(v: &Value, key: &str) -> Result<f64> {
    v[key].as_f64().ok_or_else(|| anyhow!("`{key}` is not a number"))
}

fn list(v: &Value) -> Result<&Vec<Value>> {
    v.as_array().ok_or_else(|| anyhow!("expected a list"))
}

fn point(v: &Value) -> Result<V2> {
    let a = list(v)?;
    ensure!(a.len() == 2, "a point needs two coordinates");
    Ok(v2(a[0].as_f64().ok_or_else(|| anyhow!("non-numeric x"))?,
          a[1].as_f64().ok_or_else(|| anyhow!("non-numeric y"))?))
}

fn points(v: &Value) -> Result<Vec<V2>> {
    list(v)?.iter().map(point).collect()
}

/// The master's segments without a fitted or polygonal intermediate.
fn outline(v: &Value) -> Result<Loop> {
    let mut segs = vec![];
    for v in list(v)? {
        let (kind, coords) = v.as_object().and_then(|v| v.iter().next())
            .ok_or_else(|| anyhow!("a segment has no controls"))?;
        let p = points(coords)?;
        segs.push(match (kind.as_str(), p.as_slice()) {
            ("line", &[a, b]) => Seg::Line { a, b },
            ("quad", &[a, c, b]) => Seg::Quad { a, c, b },
            ("cubic", &[a, c1, c2, b]) => Seg::Cubic { a, c1, c2, b },
            ("arc", &[a, middle, b]) => {
                let c = (a + b) * 0.5;
                ensure!(((middle - c).norm() - (a - c).norm()).abs() < 1e-8,
                        "the faucet master arc must be a semicircle");
                Seg::Arc { a, b, c, ccw: (middle - a).cross(b - middle) > 0.0 }
            }
            _ => return Err(anyhow!("invalid {kind} segment")),
        });
    }
    Loop::new(segs)
}

fn inside(p: V2, poly: &[V2]) -> bool {
    let mut odd = false;
    for i in 0..poly.len() {
        let (a, b) = (poly[i], poly[(i + 1) % poly.len()]);
        if (a.y > p.y) != (b.y > p.y)
            && p.x < a.x + (p.y - a.y) / (b.y - a.y) * (b.x - a.x)
        {
            odd = !odd;
        }
    }
    odd
}

/// One outlined SVG text group: the font's outer winding, with counters in the smallest
/// surrounding letter. The control points stay on the original curves.
fn lettering(v: &Value) -> Result<Vec<Profile>> {
    let loops = list(v)?.iter().map(outline).collect::<Result<Vec<_>>>()?;
    let areas: Vec<f64> = loops.iter().map(Loop::area).collect();
    let largest = (0..loops.len()).max_by(|&a, &b| areas[a].abs().total_cmp(&areas[b].abs()))
        .ok_or_else(|| anyhow!("empty wordmark group"))?;
    let sense = areas[largest] > 0.0;
    let outer: Vec<usize> = (0..loops.len()).filter(|&i| (areas[i] > 0.0) == sense).collect();
    let polys: Vec<Vec<V2>> = loops.iter().map(|lp| {
        Profile::new(lp.clone()).place(&Plane::XY).loops[0].pts.iter()
            .map(|p| v2(p.x, p.y)).collect()
    }).collect();
    let mut profiles: Vec<Profile> = outer.iter().map(|&i| Profile::new(loops[i].clone())).collect();
    for h in (0..loops.len()).filter(|&i| (areas[i] > 0.0) != sense) {
        let parent = outer.iter().enumerate().filter(|&(_, &i)| inside(polys[h][0], &polys[i]))
            .min_by(|a, b| areas[*a.1].abs().total_cmp(&areas[*b.1].abs()))
            .map(|(k, _)| k).ok_or_else(|| anyhow!("a wordmark counter has no letter"))?;
        profiles[parent].holes.push(loops[h].clone());
    }
    Ok(profiles)
}

fn xz(profile: &Profile, y: f64, depth: f64) -> Result<Solid> {
    Plane::XZ.at(v3(0.0, y, 0.0)).extrude(profile, -depth)
}

fn boxed(v: &Value) -> Result<Solid> {
    let a = list(v)?.iter().map(|x| x.as_f64().ok_or_else(|| anyhow!("non-numeric bound")))
        .collect::<Result<Vec<_>>>()?;
    ensure!(a.len() == 6, "a box needs six bounds");
    Ok(Solid::cuboid(v3(a[0], a[2], a[4]), v3(a[1], a[3], a[5])))
}

fn blank(n: &Numbers) -> Result<Solid> {
    snap_geometry::plate_blank(n.get("snap")?)
}

fn wordmark(n: &Numbers, depth: f64) -> Result<Solid> {
    let mut parts = vec![];
    for group in list(n.get("wordmark")?)? {
        for profile in lettering(group)? {
            parts.push(xz(&profile, n.f("thick")? - n.f("ink_depth")?, depth)?);
        }
    }
    Ok(Solid::compose(&parts))
}

fn artwork(n: &Numbers, depth: f64) -> Result<Solid> {
    let y = n.f("thick")? - n.f("ink_depth")?;
    let logo = n.get("logo")?;
    let mut parts = vec![
        xz(&Profile::new(outline(&logo["faucet"])?), y, depth)?,
        xz(&Profile::circle(point(&logo["drop_center"])?, f(logo, "drop_radius")?), y, depth)?,
        wordmark(n, depth)?,
    ];
    for polygon in list(n.get("qr")?)? {
        let rings = list(polygon)?;
        let mut profile = Profile::polygon(&points(&rings[0])?);
        for hole in &rings[1..] {
            profile.holes.push(Loop::polygon(&points(hole)?));
        }
        parts.push(xz(&profile, y, depth)?);
    }
    Ok(Solid::compose(&parts))
}

fn receiver(n: &Numbers) -> Result<Solid> {
    snap_geometry::receiver(n.get("snap")?)
}

fn plate(n: &Numbers) -> Result<(Solid, Solid)> {
    let body = blank(n)?.cut(&artwork(n, n.f("ink_depth")?)?)?;
    let ink = artwork(n, n.f("ink_depth")? + n.f("artwork_rise")?)?;
    Ok((body, ink))
}

fn check(n: &Numbers) -> Result<Value> {
    let (body, ink) = plate(n)?;
    let receiver = receiver(n)?;
    body.check()?;
    ink.check()?;
    receiver.check()?;
    ensure!(body.components().len() == 1 && receiver.components().len() == 1,
            "the plate and receiver must each be one solid");
    let overlap = body.intersect(&ink)?.volume();
    ensure!(overlap < 1e-6, "the body and ink share {overlap} mm³");
    let quiet_overlap = wordmark(n, n.f("ink_depth")?)?.intersect(&boxed(n.get("qr_quiet")?)?)?.volume();
    ensure!(quiet_overlap < 1e-6, "the wordmark enters the QR quiet zone");
    ensure!(n.get("qr_fits")?.as_bool() == Some(true), "the QR quiet zone exceeds the plate");
    let mount=n.get("snap")?;
    let seated=blank(n)?.intersect(&receiver)?.volume();
    ensure!(seated<1e-6,"seated nameplate intersects receiver by {seated} mm³");
    let screw_art_overlap=artwork(n,n.f("ink_depth")?+n.f("artwork_rise")?)?
        .intersect(&snap_geometry::plate_cuts(mount)?)?.volume();
    ensure!(screw_art_overlap<1e-6,"fastener openings enter artwork by {screw_art_overlap} mm³");
    let bearing=f(mount,"thick")?-f(mount,"counterbore_depth")?;
    let engagement=f(mount,"screw_length")?-bearing;
    let radial_stock=f(mount,"insert_stock_radius")?-f(mount,"insert_diameter")?/2.;
    let insert_rear_air=-f(mount,"insert_stock_rear")?-f(mount,"insert_length")?;
    ensure!(bearing>=2. && f(mount,"floor_stock")?>=3. && radial_stock>=3.,"fastener bearing or surrounding stock is insufficient");
    ensure!(engagement<=f(mount,"insert_length")? && engagement>=3.5,"screw engagement exceeds short insert");
    ensure!(f(mount,"pilot_rear")?<=f(mount,"insert_stock_rear")?,"the insert bore must open through the rear wall");
    Ok(json!({"valid_body":true,"valid_receiver":true,"plate_components":body.components().len(),
        "receiver_components":receiver.components().len(),"mount":mount,
        "seated_overlap_mm3":seated,"screw_artwork_overlap_mm3":screw_art_overlap,
        "bearing_floor_mm":bearing,"insert_engagement_mm":engagement,
        "insert_radial_stock_mm":radial_stock,"insert_rear_wall_air_mm":insert_rear_air,
        "receiver_floor_stock_mm":f(mount,"floor_stock")?,"pilot_reach_mm":-f(mount,"pilot_rear")?,
        "bore":"Standalone receiver through; production upper pair ends against existing support-floor backing.",
        "head_proud_mm":f(mount,"head_height")?-f(mount,"counterbore_depth")?,
        "artwork_rise_mm":n.f("artwork_rise")?,"payload":n.text("payload")?,
        "body_ink_overlap_mm3":overlap,"quiet_zone_overlap_mm3":quiet_overlap}))
}

fn main() -> Result<()> {
    if std::env::args().nth(2).as_deref() == Some("--check") {
        let n = Numbers::read(std::env::args().nth(1).unwrap_or_default())?;
        println!("{}", check(&n)?);
        return Ok(());
    }
    let (n, out) = args()?;
    let (plate, ink) = plate(&n)?;
    plate.check()?;
    ink.check()?;
    let name = n.text("name")?;
    let ink_name = format!("{name}-ink");
    let said = write_colored_part(&out, name, &[
        Body { name, color: Some(n.color("black")?), solid: &plate },
        Body { name: &ink_name, color: Some(n.color("white")?), solid: &ink },
    ], &plate.union(&ink)?)?;
    println!("{said}");
    if n.f("unit")? == 1.0 {
        let hardware=snap_geometry::hardware(n.get("snap")?)?;
        let bodies=hardware.iter().map(|(name,solid,color)| Body {
            name:name.as_str(),solid,color:Some(*color)
        }).collect::<Vec<_>>();
        println!("{}",write_shown(&out,"nameplate-fasteners",&bodies)?);
        let receiver = receiver(&n)?;
        println!("{}", write_part(&out, "nameplate-receiver", &[Body {
            name: "nameplate-receiver", color: Some(n.color("receiver_color")?), solid: &receiver,
        }])?);
    }
    Ok(())
}
