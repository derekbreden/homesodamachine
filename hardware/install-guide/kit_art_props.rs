//! The kit page's component surfaces and source-dimensioned presentation props.
use super::{Shown, add, bend, block, cylinder, filter, numbers, point};
use anyhow::{Context, Result};
use hsm_kernel::part::Numbers;
use hsm_kernel::*;
use serde_json::Value;
use std::path::Path as FilePath;

fn put(out: &mut Shown, name: &str, solid: Solid) {
    add(out, name, solid, [0., 0., 0.]);
}

fn save(directory: &FilePath, name: &str, out: &Shown) -> Result<()> {
    let bodies: Vec<_> = out
        .iter()
        .map(|(name, solid, color)| Body {
            name,
            solid,
            color: Some(*color),
        })
        .collect();
    hsm_kernel::step::write_model(directory.join(format!("{name}.kit.npz")), &bodies)
}

fn rounded(plane: Plane, width: f64, height: f64, radius: f64, length: f64) -> Result<Solid> {
    plane.extrude(
        &Profile::new(Loop::rounded_rect(V2::ZERO, width, height, radius)?),
        length,
    )
}

fn machine(spec: &Value) -> Result<Shown> {
    let b = numbers(&spec["outer"]);
    let p = &spec["profile"];
    let roof = numbers(&p["roof"]);
    let end = numbers(&p["end"]);
    let start = numbers(&p["start"]);
    let side = [
        v2(b[2], b[4]),
        v2(b[3], b[4]),
        v2(b[3], b[5]),
        v2(roof[0], b[5]),
        v2(end[0], end[1]),
        v2(start[0], start[1]),
    ];
    let shell = Plane::YZ
        .at(v3(b[0], 0., 0.))
        .extrude(&Profile::polygon(&side), b[1] - b[0])?;
    let mut out = vec![];
    put(
        &mut out,
        "lower",
        shell.intersect(&block(v3(-500., -500., 0.), v3(1000., 1000., 200.)))?,
    );
    put(
        &mut out,
        "upper",
        shell.intersect(&block(v3(-500., -500., 200.1), v3(1000., 1000., 500.)))?,
    );
    let display = Plane::new(point(&p["origin"]), V3::X, point(&p["normal"]))?;
    put(
        &mut out,
        "display-frame",
        display.extrude(&Profile::rect(V2::ZERO, 132.7, 83.3), 0.8)?,
    );
    put(
        &mut out,
        "display-screen",
        display.extrude(&Profile::rect(V2::ZERO, 103.5, 62.1), 1.)?,
    );
    let c = numbers(&spec["cover"]);
    put(
        &mut out,
        "funnel-cover",
        rounded(
            Plane::XY.at(v3((c[0] + c[3]) / 2., (c[1] + c[4]) / 2., c[2])),
            c[3] - c[0],
            c[4] - c[1],
            5.,
            c[5] - c[2],
        )?,
    );
    Ok(out)
}

fn faucet(spec: &Value) -> Result<Shown> {
    let bodies = import::model(spec["inputs"]["faucet"].as_str().context("faucet model")?)?;
    let mut out = vec![];
    let names = [
        "westbrass",
        "drain_tube",
        "display_signal_ribbon",
        "soda_faucet_tube",
        "tpu_o_ring",
        "flavor_tube_pos_x",
        "flavor_tube_neg_x",
        "above_counter_plate",
        "above_counter_gasket",
        "shell_base",
        "shell_tip",
        "faucet-display-cover-seated",
        "faucet_display",
        "faucet_display_screen",
    ];
    let clip = block(v3(-1000., -1000., -110.), v3(2000., 2000., 370.));
    for name in names {
        let body = import::body(&bodies, name)?;
        let cropped = [
            "westbrass",
            "drain_tube",
            "display_signal_ribbon",
            "flavor_tube_pos_x",
            "flavor_tube_neg_x",
        ]
        .contains(&name);
        let solid = if cropped {
            body.intersect(&clip)?
        } else {
            body.clone()
        };
        put(&mut out, name, solid);
    }
    let (lever, _) = super::cad_art_props::lever(&numbers(&spec["lever"]))?;
    put(&mut out, "lever", lever);
    let plate = import::body(&bodies, "under_counter_plate")?;
    put(
        &mut out,
        "under_counter_plate",
        plate.translate(v3(95., 0., -plate.bounds().min.z - 70.)),
    );
    Ok(out)
}

fn tees(spec: &Value) -> Result<Shown> {
    let mut out = vec![];
    for body in import::payload(spec["inputs"]["black_tee"].as_str().context("black tee")?)? {
        put(
            &mut out,
            &format!("black-tee/{}", body.name),
            body.solid.translate(v3(30., 0., 0.)),
        );
    }
    for body in import::model(
        spec["inputs"]["white_tee"]
            .as_str()
            .context("white tee scene")?,
    )? {
        if body.name.starts_with("tee-") {
            put(
                &mut out,
                &body.name,
                body.solid.translate(v3(-57., -77., -182.8)),
            );
        }
    }
    Ok(out)
}

fn regulator(n: &Numbers, spec: &Value) -> Result<Shown> {
    let mut out = vec![];
    for body in import::payload(spec["inputs"]["regulator"].as_str().context("regulator")?)? {
        if !["black-print", "red-print", "band-"]
            .iter()
            .any(|s| body.name.contains(s))
        {
            put(&mut out, &body.name, body.solid);
        }
    }
    let p = point(&spec["regulator"]["mouth"]);
    let inserted = spec["regulator"]["insert"].as_f64().unwrap();
    bend(
        &mut out,
        "red-tether",
        &[
            p + V3::Z * inserted,
            p - V3::Z * 46.,
            p - V3::Z * 46. + V3::X * 120.,
        ],
        n.f("tube_d")?,
        22.,
        [0., 0., 0.],
    )?;
    let washer = Profile::circle(V2::ZERO, 14.).with_hole(Loop::circle(V2::ZERO, 10.));
    put(
        &mut out,
        "washer",
        Plane::XZ.at(v3(-108., 0., -62.)).extrude(&washer, 2.)?,
    );
    Ok(out)
}

fn cord() -> Result<Shown> {
    let body = rounded(Plane::XY.at(v3(0., 0., -9.5)), 28., 35., 3., 19.)?;
    let nose = rounded(Plane::XY.at(v3(0., -25., -7.5)), 24., 15., 2., 15.)?;
    let mut plug = body.union(&nose)?;
    for (x, z) in [(-6., 0.), (6., 0.), (0., 4.)] {
        plug = plug.cut(&block(v3(x - 1.2, -36., z - 2.), v3(2.4, 10., 4.)))?;
    }
    let mut out = vec![];
    put(&mut out, "c13-plug", plug);
    let points = [
        v3(0., 17., 0.),
        v3(0., 43., 0.),
        v3(40., 62., 0.),
        v3(80., 35., 0.),
        v3(40., 0., 0.),
        v3(15., 35., 0.),
        v3(65., 55., 0.),
        v3(100., 0., 0.),
    ];
    let mut parameters = vec![0.];
    for pair in points.windows(2) {
        parameters.push(parameters.last().unwrap() + (pair[1] - pair[0]).norm());
    }
    let path = Path::new(points[0]).clamped_spline(&points, &parameters, [V3::Y, -V3::Y])?;
    let cable =
        Plane::new(points[0], V3::X, V3::Y)?.sweep(&Profile::circle(V2::ZERO, 3.25), &path)?;
    put(&mut out, "cord", cable);
    put(
        &mut out,
        "mains",
        rounded(Plane::XY.at(v3(100., -14., -8.5)), 22., 28., 3., 17.)?,
    );
    for x in [-6., 6.] {
        put(
            &mut out,
            &format!("prong-{x}"),
            block(v3(99. + x, -40., -1.), v3(2., 12., 6.)),
        );
    }
    put(
        &mut out,
        "ground",
        cylinder(v3(100., -40., -4.), 4.5, 13., V3::Y)?,
    );
    Ok(out)
}

fn book() -> Shown {
    let mut out = vec![];
    for (name, p, size) in [
        ("pages", v3(-45., -35., 0.), v3(90., 70., 4.)),
        ("lower", v3(-46., -36., -0.6), v3(92., 72., 0.6)),
        ("upper", v3(-46., -36., 4.), v3(92., 72., 0.6)),
        ("spine", v3(-46.4, -36., 0.), v3(0.8, 72., 4.)),
        ("panel", v3(-33., -22.5, 4.61), v3(66., 45., 0.1)),
    ] {
        put(&mut out, name, block(p, size));
    }
    out
}

fn bag() -> Result<Shown> {
    let mut out = vec![];
    put(
        &mut out,
        "bag",
        rounded(Plane::XZ.at(v3(0., 9., 52.)), 90., 104., 6., 18.)?,
    );
    put(
        &mut out,
        "zipper",
        block(v3(-41.5, -10., 92.), v3(83., 20., 2.)),
    );
    put(
        &mut out,
        "tag",
        block(v3(-25., -9.45, 34.5), v3(50., 0.3, 27.)),
    );
    Ok(out)
}

pub fn write(n: &Numbers, directory: &FilePath) -> Result<()> {
    let spec = n.get("kit_art")?;
    save(directory, "machine", &machine(&spec["machine"])?)?;
    save(directory, "faucet-and-plate", &faucet(&spec)?)?;
    let mut filtered = vec![];
    filter(n, &mut filtered)?;
    save(directory, "filtered-line", &filtered)?;
    save(directory, "water-tees", &tees(&spec)?)?;
    save(directory, "regulator-and-tether", &regulator(n, &spec)?)?;
    let collet: Shown = import::model(spec["inputs"]["collet"].as_str().context("collet model")?)?
        .into_iter()
        .map(|b| (b.name, b.solid, [0., 0., 0.]))
        .collect();
    save(directory, "collet-press", &collet)?;
    save(directory, "power-cord", &cord()?)?;
    save(directory, "install-guide", &book())?;
    save(directory, "cold-kit", &bag()?)?;
    Ok(())
}
