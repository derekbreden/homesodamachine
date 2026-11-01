//! The standing valve plates and the finite socket-to-barrel clearance their docs read.
use anyhow::{Context, Result, ensure};
use hsm_kernel::part::Numbers;
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V3, v2, v3, write_model};
use serde_json::{Value, json};

fn array(v: &Value) -> Result<&Vec<Value>> {
    v.as_array().context("a stock list")
}

fn number(v: &Value) -> Result<f64> {
    v.as_f64().context("a stock coordinate")
}

fn point(v: &Value) -> Result<V3> {
    let p = array(v)?;
    ensure!(p.len() == 3, "a point has three coordinates");
    Ok(v3(number(&p[0])?, number(&p[1])?, number(&p[2])?))
}

fn cylinder(v: &Value, along_y: bool) -> Result<Solid> {
    let p = array(v)?;
    ensure!(p.len() == 5, "a cylinder has a centre, radius and run");
    let (x, y, z, r, h) = (
        number(&p[0])?,
        number(&p[1])?,
        number(&p[2])?,
        number(&p[3])?,
        number(&p[4])?,
    );
    // The doc total resolves 0.01 cm³. A midpoint on each standard chord retains that
    // reading for the shallow circular channels and blind sockets.
    let count = 2 * hsm_kernel::rule::ring_count(r);
    let point = |i: usize| {
        let angle = std::f64::consts::TAU * i as f64 / count as f64;
        v2(r * angle.cos(), r * angle.sin())
    };
    let segments = (0..count)
        .map(|i| Seg::Arc {
            a: point(i),
            b: point(i + 1),
            c: v2(0.0, 0.0),
            ccw: true,
        })
        .collect();
    let profile = Profile::new(Loop::new(segments)?);
    if along_y {
        Plane::XZ.at(v3(x, y - h / 2.0, z)).extrude(&profile, -h)
    } else {
        Plane::XY.at(v3(x, y, z)).extrude(&profile, h)
    }
}

fn tray(v: &Value) -> Result<Solid> {
    let stock = Solid::cuboid(point(&v["slab"][0])?, point(&v["slab"][1])?);
    let mut cuts = array(&v["sockets"])?
        .iter()
        .map(|v| cylinder(v, false))
        .collect::<Result<Vec<_>>>()?;
    cuts.extend(
        array(&v["channels"])?
            .iter()
            .map(|v| cylinder(v, true))
            .collect::<Result<Vec<_>>>()?,
    );
    stock.cut_all(&cuts)
}

fn web(n: &Numbers) -> Result<f64> {
    let channel = array(n.get("web_channel")?)?;
    let (cx, cy, cz, cr, run) = (
        number(&channel[0])?,
        number(&channel[1])?,
        number(&channel[2])?,
        number(&channel[3])?,
        number(&channel[4])?,
    );
    let mut gap = f64::INFINITY;
    for socket in array(n.get("web_sockets")?)? {
        let p = array(socket)?;
        let (x, y, z0, r, h) = (
            number(&p[0])?,
            number(&p[1])?,
            number(&p[2])?,
            number(&p[3])?,
            number(&p[4])?,
        );
        let distance = if (cy - run / 2.0..=cy + run / 2.0).contains(&y) {
            // The port spans the socket axis. Its closest radial point is at the socket's
            // nearest X rim and axial cap (or the port's Z when it lies between the caps).
            // The cap is essential: subtracting the two infinite-cylinder radii misses it.
            let dx = ((x - cx).abs() - r).max(0.0);
            let dz = cz - cz.clamp(z0.min(z0 + h), z0.max(z0 + h));
            (dx.hypot(dz) - cr).max(0.0)
        } else {
            cylinder(socket, false)?.gap(&cylinder(n.get("web_channel")?, true)?)?
        };
        gap = gap.min(distance);
    }
    Ok(gap)
}

fn main() -> Result<()> {
    let args = std::env::args().collect::<Vec<_>>();
    ensure!(
        args.len() == 3,
        "usage: {} <numbers.json> <--check|model.npz>",
        args[0]
    );
    let n = Numbers::read(&args[1])?;
    let mut shapes = vec![];
    let mut rows = vec![];
    for plan in array(n.get("trays")?)? {
        let shape = tray(plan)?;
        rows.push(json!({"name":plan["name"], "volume":shape.volume(),
                         "valid":shape.check().is_ok()}));
        shapes.push(shape);
    }
    if args[2] != "--check" {
        let bodies = rows
            .iter()
            .zip(&shapes)
            .map(|(row, solid)| Body {
                name: row["name"].as_str().unwrap(),
                color: None,
                solid,
            })
            .collect::<Vec<_>>();
        write_model(&args[2], &bodies)?;
    }
    println!(
        "{}",
        json!({"trays":rows, "web":web(&n)?, "extrusion_w":n.f("extrusion_w")?})
    );
    Ok(())
}
