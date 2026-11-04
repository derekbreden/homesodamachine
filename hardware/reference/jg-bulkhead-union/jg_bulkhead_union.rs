//! Manual reconstruction of the PP1208E exterior from its native-scale scan.
use anyhow::{Context, Result};
use hsm_kernel::part::{args, write_part};
use hsm_kernel::{Body, Plane, Profile, Solid, V2, V3, v2, v3};
use serde_json::Value;

fn f(v: &Value, key: &str) -> Result<f64> {
    v[key].as_f64().with_context(|| format!("numeric {key}"))
}
fn turned(v: &Value) -> Result<Solid> {
    let rows = v.as_array().context("turned profile")?;
    let mut points = vec![v2(rows[0][0].as_f64().context("start")?, 0.)];
    for p in rows {
        points.push(v2(p[0].as_f64().context("axial position")?,
                       p[1].as_f64().context("radius")?));
    }
    points.push(v2(points.last().unwrap().x, 0.));
    Plane::XY.revolve(&Profile::polygon(&points), 360., V2::ZERO, v2(1., 0.))
}
fn hex(v: &Value, lo: f64, hi: f64) -> Result<Solid> {
    let cy = v["center_yz_mm"][0].as_f64().context("hex Y")?;
    let cz = v["center_yz_mm"][1].as_f64().context("hex Z")?;
    let radius = f(v, "across_flats_mm")? / (2. * (std::f64::consts::PI / 6.).cos());
    let clock = f(v, "vertex_clock_degrees")?.to_radians();
    let corners: Vec<_> = (0..6).map(|k| {
        let a = clock + k as f64 * std::f64::consts::PI / 3.;
        v2(radius * a.cos(), radius * a.sin())
    }).collect();
    Plane::YZ.at(v3(lo, cy, cz)).extrude(&Profile::polygon(&corners), hi-lo)
}
fn main() -> Result<()> {
    let (n, out) = args()?;
    let seat = n.f("panel_seat_local_x_mm")?;
    let near = n.f("outboard_mouth_local_x_mm")?;
    let far = n.f("inboard_mouth_local_x_mm")?;
    let barrel_end = n.f("barrel_end_local_x_mm")?;
    let crest = n.f("barrel_crest_diameter_mm")? / 2.;
    let start = n.f("body_hex_start_local_x_mm")?;
    let profiles = n.get("profiles")?;
    let outside_hex = hex(n.get("body_hex")?, start, near + 0.1)?
        .union(&Solid::cuboid(v3(seat-0.1, -20., -20.), v3(start, 20., 20.)))?;
    let outside = turned(&profiles["outboard"])?.intersect(&outside_hex)?;
    let barrel = Solid::cylinder(v3(barrel_end-0.02, 0., 0.), V3::X,
                                 crest, seat-barrel_end+0.04)?;
    let inside = turned(&profiles["inboard"])?;
    let mut fitting = outside.union(&barrel)?.union(&inside)?;
    let published = n.get("published")?;
    let tube_r = f(published, "tube_od_mm")? / 2.;
    let insertion = f(published, "tube_stop_depth_mm")?;
    fitting = fitting.cut(&Solid::cylinder(v3(far-0.1, 0., 0.), V3::X,
                                           f(published, "through_bore_mm")?/2., near-far+0.2)?)?
        .cut(&Solid::cylinder(v3(far-0.1, 0., 0.), V3::X, tube_r, insertion+0.1)?)?
        .cut(&Solid::cylinder(v3(near+0.1, 0., 0.), -V3::X, tube_r, insertion+0.1)?)?;
    let nut_range = n.list("nut_axial_range_local_mm")?;
    let stop = n.f("nut_hex_stop_local_x_mm")?;
    let nut_mask = hex(n.get("nut_hex")?, nut_range[0]-0.1, stop)?
        .union(&Solid::cuboid(v3(stop, -20., -20.), v3(nut_range[1]+0.1, 20., 20.)))?;
    let nut = turned(&profiles["nut"])?.intersect(&nut_mask)?
        .cut(&Solid::cylinder(v3(nut_range[0]-0.1, 0., 0.), V3::X,
                              crest+0.1, nut_range[1]-nut_range[0]+0.2)?)?;
    let installed_frame = |s: Solid| s.rotate(V3::ZERO, V3::Z, 90.).translate(v3(0., -seat, 0.));
    let fitting = installed_frame(fitting);
    let nut = installed_frame(nut);
    let color = Some(n.color("color")?);
    println!("{}", write_part(&out, "jg-bulkhead-union", &[
        Body { name: "fitting", color, solid: &fitting },
        Body { name: "nut", color, solid: &nut },
    ])?);
    Ok(())
}
