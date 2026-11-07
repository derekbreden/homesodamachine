//! Illustration props and the two closed faucet crops for the installation pictures.
use anyhow::{Context, Result};
use hsm_kernel::part::args;
use hsm_kernel::*;
use serde_json::Value;

mod cad_art_props;

type Shown = Vec<(String, Solid, [f64; 3])>;

fn numbers(v: &Value) -> Vec<f64> {
    v.as_array().unwrap().iter().map(|v| v.as_f64().unwrap()).collect()
}

fn point(v: &Value) -> V3 {
    let a = numbers(v);
    v3(a[0], a[1], a[2])
}

fn color(n: &hsm_kernel::part::Numbers, name: &str) -> [f64; 3] {
    let c = numbers(&n.get("colors").unwrap()[name]);
    [c[0], c[1], c[2]]
}

fn add(out: &mut Shown, name: &str, solid: Solid, c: [f64; 3]) {
    out.push((name.to_owned(), solid, c));
}

fn block(p: V3, size: V3) -> Solid {
    Solid::cuboid(p, p + size)
}

fn cylinder(p: V3, d: f64, length: f64, axis: V3) -> Result<Solid> {
    Solid::cylinder(p, axis, d / 2., length)
}

fn bend(out: &mut Shown, name: &str, p: &[V3], d: f64, r: f64, c: [f64; 3]) -> Result<()> {
    let mut samples = vec![p[0]];
    for i in 1..p.len() - 1 {
        let u = (p[i] - p[i - 1]).unit();
        let v = (p[i + 1] - p[i]).unit();
        let centre = p[i] - u * r + v * r;
        for step in 0..=20 {
            let t = std::f64::consts::FRAC_PI_2 * step as f64 / 20.;
            samples.push(centre + (u * t.sin() - v * t.cos()) * r);
        }
    }
    samples.push(*p.last().unwrap());
    let mut parts = vec![];
    for w in samples.windows(2) {
        let delta = w[1] - w[0];
        if delta.norm() > 1e-9 {
            parts.push(cylinder(w[0], d, delta.norm(), delta.unit())?);
        }
    }
    for &p in &samples[1..samples.len() - 1] {
        parts.push(Solid::sphere(p, d / 2.)?);
    }
    for (i, solid) in parts.into_iter().enumerate() {
        add(out, &format!("{name}/{}", i + 1), solid, c);
    }
    Ok(())
}

fn countertop(n: &hsm_kernel::part::Numbers, out: &mut Shown, wide: bool) -> Result<()> {
    let a = numbers(&n.get("faucet")?["counter"]);
    let (x, y, cx) = if wide { (320., 210., 0.) } else { (142., 68., -8.) };
    let slab = block(v3(cx - x / 2., -y / 2., a[0]), v3(x, y, a[1]));
    let hole = cylinder(v3(0., a[2], a[0] - 1.), a[3] * 2., a[1] + 2., V3::Z)?;
    add(out, "countertop", slab.cut(&hole)?, color(n, "STONE"));
    Ok(())
}

fn faucet(n: &hsm_kernel::part::Numbers, out: &mut Shown, opening: bool) -> Result<()> {
    countertop(n, out, opening)?;
    let a = n.get("faucet")?;
    let (lo, hi, lift) = if opening { (-70., 40., 128.) } else { (-88., -30., 0.) };
    let clip = block(v3(-300., -300., lo), v3(600., 600., hi - lo));
    let bodies = import::payload(a["payload"].as_str().context("faucet payload")?)?;
    let selected = if opening {
        vec![("flavor_tube_pos_x", "BLACK_PART"), ("flavor_tube_neg_x", "BLACK_PART"),
             ("soda_umbilical_tube", "BLUE_TUBE"), ("drain_tube", "WHITE_TUBE"),
             ("display_signal_ribbon", "BLACK_PART"), ("westbrass", "STEEL")]
    } else {
        vec![("westbrass", "STEEL"), ("flavor_tube_pos_x", "BLACK_PART"),
             ("flavor_tube_neg_x", "BLACK_PART_LIT"), ("flavor_umbilical_tube_pos_x", "BLACK_PART"),
             ("flavor_umbilical_tube_neg_x", "BLACK_PART_LIT"), ("soda_umbilical_tube", "BLUE_TUBE")]
    };
    for (name, material) in selected {
        for body in bodies.iter().filter(|body| body.name == name) {
            let bounds = body.solid.bounds();
            if bounds.max.z <= lo || bounds.min.z >= hi { continue; }
            let cropped = body.solid.intersect(&clip)?.translate(v3(0., 0., lift));
            if !cropped.tris().is_empty() {
                add(out, if opening && name == "westbrass" { "shank" } else { name },
                    cropped, color(n, material));
            }
        }
    }
    if !opening {
        let wt = a["washer_t"].as_f64().unwrap();
        let nh = a["nut_h"].as_f64().unwrap();
        let z = -a["shank_length"].as_f64().unwrap();
        let washer = Profile::circle(V2::ZERO, 12.).with_hole(Loop::circle(V2::ZERO, 6.1));
        add(out, "retained-washer", Plane::XY.at(v3(0., 0., z + nh)).extrude(&washer, wt)?, color(n, "STEEL"));
        let hex: Vec<_> = (0..6).map(|k| {
            let t = k as f64 * std::f64::consts::PI / 3.;
            v2(11. * t.cos(), 11. * t.sin())
        }).collect();
        let nut = Profile::polygon(&hex).with_hole(Loop::circle(V2::ZERO, 6.1));
        add(out, "retained-nut", Plane::XY.at(v3(0., 0., z)).extrude(&nut, nh)?, color(n, "NUT_STEEL"));
        for body in bodies.iter().filter(|body| body.name == "under_counter_plate") {
            add(out, "under-counter-plate", body.solid.translate(v3(a["plate_x"].as_f64().unwrap(), 0., 0.)),
                color(n, "PLATE_STEEL"));
        }
    }
    Ok(())
}

fn cabinet(n: &hsm_kernel::part::Numbers, out: &mut Shown) -> Result<()> {
    let b = n.list("box")?;
    let c = n.list("clearances")?;
    let cy = n.list("cylinder")?;
    let x0 = b[0] - c[0] - c[2] - 30.;
    let x1 = b[1] + c[0] + 30.;
    add(out, "cabinet-floor", block(v3(x0, b[2] - 40., -24.), v3(x1 - x0, b[3] - b[2] + c[1] + 80., 18.)), color(n, "CABINET"));
    for (name, x, y, sx, sy) in [("behind", b[0], b[3], b[1] - b[0], c[1]),
        ("side-west", b[0] - c[0], b[2], c[0], b[3] - b[2]),
        ("side-east", b[1], b[2], c[0], b[3] - b[2])] {
        add(out, &format!("clear-{name}"), block(v3(x, y, -6.), v3(sx, sy, 10.)), color(n, "CORAL"));
    }
    add(out, "co2-cylinder", cylinder(v3(b[0] - c[0] - c[2] / 2., b[2] + 150., -6.), cy[0], cy[1], V3::Z)?, color(n, "CYLINDER"));
    Ok(())
}

fn filter(n: &hsm_kernel::part::Numbers, out: &mut Shown) -> Result<()> {
    let f = n.list("filter")?;
    let z = f[0] / 2.;
    let half = f[1] / 2.;
    add(out, "cartridge", cylinder(v3(-half + 26., 110., z), f[0], f[1] - 52., V3::X)?, color(n, "FILTER_BODY"));
    for (name, x) in [("in", -half), ("out", half - 26.)] {
        add(out, &format!("quick-connect-{name}"), cylinder(v3(x, 110., z), f[0] * 0.62, 26., V3::X)?, color(n, "FILTER_CAP"));
    }
    for (name, x, end) in [("in", -half, -330.), ("out", half, 330.)] {
        bend(out, &format!("white-run-{name}"), &[v3(x, 110., z), v3(end, 110., z), v3(end, -40., z)],
             n.f("tube_d")?, 55., color(n, "WHITE_TUBE"))?;
    }
    Ok(())
}

fn bottle(n: &hsm_kernel::part::Numbers, out: &mut Shown) -> Result<()> {
    let b = n.list("bottle")?;
    let shoulder = b[3];
    let body = shoulder + 26.;
    let mut parts = vec![
        ("bottle-neck", cylinder(V3::ZERO, b[2], b[3], V3::Z)?, "BOTTLE_PET"),
        ("bottle-shoulder", Solid::cone(v3(0., 0., shoulder), V3::Z, b[2] / 2., b[0] / 2., 26.)?, "BOTTLE_PET"),
        ("bottle-body", cylinder(v3(0., 0., body), b[0], b[1], V3::Z)?, "CONCENTRATE"),
        ("bottle-base", cylinder(v3(0., 0., body + b[1]), b[0] * 0.62, 4., V3::Z)?, "BOTTLE_PET")];
    for (_, shape, _) in &mut parts { *shape = shape.rotate(V3::ZERO, V3::X, 90. - b[4]); }
    let low = parts.iter().map(|(_, s, _)| s.bounds().min.z).fold(f64::INFINITY, f64::min);
    let mouth = v3(b[6], b[7], b[8] + b[5] - low);
    for (name, shape, c) in parts { add(out, name, shape.translate(mouth), color(n, c)); }
    Ok(())
}

fn c13(n: &hsm_kernel::part::Numbers, out: &mut Shown) -> Result<()> {
    let c = n.get("c13")?;
    let station = numbers(&c["station"]);
    let mouth = numbers(&c["mouth"]);
    let slip = c["slip"].as_f64().unwrap();
    let wall = c["wall"].as_f64().unwrap();
    let length = c["body"].as_f64().unwrap();
    let nose = c["nose"].as_f64().unwrap();
    let boot = c["boot"].as_f64().unwrap();
    let diameters = numbers(&c["boot_d"]);
    let plane = Plane::new(V3::ZERO, V3::X, V3::Y)?;
    let rounded = |w, h, r| -> Result<Profile> { Ok(Profile::new(Loop::rounded_rect(V2::ZERO, w, h, r)?)) };
    let mut body = plane.extrude(&rounded(mouth[0] - 2. * slip + 2. * wall, mouth[1] - 2. * slip + 2. * wall, 3.)?, length)?;
    body = body.chamfer(&body.edges(">Y")?, 1.2)?;
    body = body.union(&plane.offset(-nose).extrude(&rounded(mouth[0] - 2. * slip, mouth[1] - 2. * slip, mouth[2] - slip)?, nose)?)?;
    let blade = numbers(&c["blade_size"]);
    for station in c["blades"].as_array().unwrap() {
        let p = numbers(station);
        body = body.cut(&block(v3(p[0] - blade[0] / 2. - 0.3, -nose - 0.5, p[1] - blade[1] / 2. - 0.3),
                               v3(blade[0] + 0.6, nose + 0.5 + 6., blade[1] + 0.6)))?;
    }
    let relief = Solid::cone(v3(0., length, 0.), V3::Y, diameters[0] / 2., diameters[1] / 2., boot)?;
    let tail = length + boot;
    let p = [v3(0., tail, 0.), v3(0., tail + 26., 0.), v3(7., tail + 48., -58.), v3(11., tail + 55., -175.)];
    let mut parameters = vec![0.];
    for w in p.windows(2) { parameters.push(parameters.last().unwrap() + (w[1] - w[0]).norm()); }
    let path = Path::new(p[0]).clamped_spline(&p, &parameters, [V3::Y, -V3::Z])?;
    let cord = plane.at(p[0]).sweep(&Profile::circle(V2::ZERO, c["cable_d"].as_f64().unwrap() / 2.), &path)?;
    let moved = v3(station[0], station[2] + 0.5, station[1]);
    for (i, part) in [body, relief, cord].into_iter().enumerate() {
        add(out, &format!("c13-cordset/{}", i + 1), part.translate(moved), color(n, "CORDSET"));
    }
    Ok(())
}

fn main() -> Result<()> {
    let (n, directory) = args()?;
    if n.get("cad_art").is_ok() {
        return cad_art_props::write(&n, &directory);
    }
    for name in n.get("scenes")?.as_array().unwrap() {
        let name = name.as_str().unwrap();
        let mut props = vec![];
        match name {
            "opening" => faucet(&n, &mut props, true)?,
            "plate-sideways" => faucet(&n, &mut props, false)?,
            "cabinet-plan" => cabinet(&n, &mut props)?,
            "filter-in-cabinet" => filter(&n, &mut props)?,
            "bottle-in-funnel" => bottle(&n, &mut props)?,
            "the-socket" => c13(&n, &mut props)?,
            "regulator" => {
                let t = n.get("tether")?;
                let p = point(&t["mouth"]);
                bend(&mut props, "red-tether", &[p + V3::Z * t["insert"].as_f64().unwrap(), p - V3::Z * 46., p - V3::Z * 46. + V3::X * 120.],
                     n.f("tube_d")?, 22., color(&n, "RED_TUBE"))?;
            }
            _ => {}
        }
        let bodies: Vec<_> = props.iter().map(|(name, solid, color)| Body { name, solid, color: Some(*color) }).collect();
        write_payload(directory.join(format!("{name}.props.mesh")), &bodies, None, None)?;
    }
    Ok(())
}
