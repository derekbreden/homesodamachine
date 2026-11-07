//! The supplied kit's items as solids, in the poses the kit page draws them: the machine's outer
//! shell and display, the faucet with its lever and plate, the filtered line, both water tees,
//! the regulator with its red tether and washer, the collet press, the power cord, the booklet
//! and the bagged cold kit. Items made here, not modelled elsewhere, are illustration props.
use anyhow::{Context, Result};
use hsm_faucet_numbers::{paths, shell};
use hsm_kernel::*;
use serde_json::Value;

/// An item's bodies, by name.
pub type Shown = Vec<(String, Solid)>;

fn block(p: V3, size: V3) -> Solid {
    Solid::cuboid(p, p + size)
}

fn cylinder(p: V3, d: f64, length: f64, axis: V3) -> Result<Solid> {
    Solid::cylinder(p, axis, d / 2., length)
}

fn ring(p: V3, outer: f64, inner: f64, length: f64, axis: V3) -> Result<Solid> {
    cylinder(p, outer, length, axis)?.cut(&cylinder(p - axis * 0.5, inner, length + 1., axis)?)
}

fn rounded(plane: Plane, width: f64, height: f64, radius: f64, length: f64) -> Result<Solid> {
    plane.extrude(&Profile::new(Loop::rounded_rect(V2::ZERO, width, height, radius)?), length)
}

fn numbers(v: &Value) -> Result<Vec<f64>> {
    v.as_array().context("a list of numbers")?.iter().map(|v| v.as_f64().context("a number")).collect()
}

/// A tube of diameter `d` along `p`'s legs, each corner swept round on `r`: short straight
/// pieces with a ball at every joint, overlapping rather than joined.
fn bend(out: &mut Shown, name: &str, p: &[V3], d: f64, r: f64) -> Result<()> {
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
    for &q in &samples[1..samples.len() - 1] {
        parts.push(Solid::sphere(q, d / 2.)?);
    }
    for (i, solid) in parts.into_iter().enumerate() {
        out.push((format!("{name}/{}", i + 1), solid));
    }
    Ok(())
}

/// The appliance's outer shell, split where its two halves meet, its display and funnel cover.
pub fn machine(facts: &Value) -> Result<Shown> {
    let b = numbers(&facts["box"]["outer"])?;
    let outer: [f64; 6] = b.clone().try_into().map_err(|_| anyhow::anyhow!("the box's outer bounds"))?;
    let p = hsm_enclosure_interface::swept::profile(&outer);
    let side = [
        v2(b[2], b[4]),
        v2(b[3], b[4]),
        v2(b[3], b[5]),
        v2(p.roof[0], b[5]),
        v2(p.end[0], p.end[1]),
        v2(p.start[0], p.start[1]),
    ];
    let shell = Plane::YZ.at(v3(b[0], 0., 0.)).extrude(&Profile::polygon(&side), b[1] - b[0])?;
    let mut out = vec![
        ("lower".into(), shell.intersect(&block(v3(-500., -500., 0.), v3(1000., 1000., 200.)))?),
        ("upper".into(), shell.intersect(&block(v3(-500., -500., 200.1), v3(1000., 1000., 500.)))?),
    ];
    let display = Plane::new(V3::from(p.origin), V3::X, V3::from(p.normal))?;
    out.push(("display-frame".into(), display.extrude(&Profile::rect(V2::ZERO, 132.7, 83.3), 0.8)?));
    out.push(("display-screen".into(), display.extrude(&Profile::rect(V2::ZERO, 103.5, 62.1), 1.)?));
    let c = numbers(&facts["bodies"]["funnel-cover"])?;
    out.push((
        "funnel-cover".into(),
        rounded(Plane::XY.at(v3((c[0] + c[3]) / 2., (c[1] + c[4]) / 2., c[2])), c[3] - c[0], c[4] - c[1], 5., c[5] - c[2])?,
    ));
    Ok(out)
}

/// The faucet's lever at rest: its block and tapering arm, clear of the soda tube's port.
fn lever() -> Result<Solid> {
    let plateau = shell::ZONE2_Z_TOP;
    let tube_r = shell::SODA_FAUCET_TUBE_OD / 2.;
    let cut = cylinder(v3(0., paths::WATER_Y + 0.125, plateau + 1.), 2. * (tube_r + 1.), 50., V3::Z)?;
    let base = block(v3(-6.5, -6., plateau + 1.), v3(13., 15., 12.));
    let p0 = Plane::XZ.offset(6.).shifted(v2(0., plateau + 4.5 + 8.5 / 2.));
    let p1 = Plane::XZ.offset(42.).shifted(v2(0., plateau + 10. + 3. / 2.));
    let taper = Solid::loft(&[Profile::rect(V2::ZERO, 13., 8.5).place(&p0), Profile::rect(V2::ZERO, 13., 3.).place(&p1)])?;
    base.union(&taper)?.cut(&cut)
}

/// The faucet above the counter, its tails cut short, and the steel plate set beside it.
pub fn faucet_and_plate(model: &str) -> Result<Shown> {
    let bodies = import::model(model)?;
    let clip = block(v3(-1000., -1000., -110.), v3(2000., 2000., 370.));
    let cropped = ["westbrass", "drain_tube", "display_signal_ribbon", "flavor_tube_pos_x", "flavor_tube_neg_x"];
    let mut out = vec![];
    for name in [
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
    ] {
        let body = import::body(&bodies, name)?;
        out.push((name.into(), if cropped.contains(&name) { body.intersect(&clip)? } else { body.clone() }));
    }
    out.push(("lever".into(), lever()?));
    let plate = import::body(&bodies, "under_counter_plate")?;
    out.push(("under_counter_plate".into(), plate.translate(v3(95., 0., -plate.bounds().min.z - 70.))));
    Ok(out)
}

/// The filter cartridge on its white run, which bends away at both ends.
pub fn filtered_line() -> Result<Shown> {
    const FILTER_D: f64 = 63.;
    const FILTER_L: f64 = 311.;
    let (z, half) = (FILTER_D / 2., FILTER_L / 2.);
    let mut out = vec![("cartridge".into(), cylinder(v3(-half + 26., 110., z), FILTER_D, FILTER_L - 52., V3::X)?)];
    for (name, x) in [("in", -half), ("out", half - 26.)] {
        out.push((format!("quick-connect-{name}"), cylinder(v3(x, 110., z), FILTER_D * 0.62, 26., V3::X)?));
    }
    for (name, x, end) in [("in", -half, -330.), ("out", half, 330.)] {
        bend(&mut out, &format!("white-run-{name}"), &[v3(x, 110., z), v3(end, 110., z), v3(end, -40., z)], TUBE_D, 55.)?;
    }
    Ok(out)
}

/// The kit's quarter-inch tube.
const TUBE_D: f64 = 6.35;

/// The John Guest push-fit port the white tee's branch takes, from the published drawing of
/// its equal tee: one family across every fitting on this water path.
const JG_SOCKET_D: f64 = 6.55;
const JG_INSERTION: f64 = 15.7;
const JG_COLLAR_D: f64 = 16.3;
const JG_COLLAR_LENGTH: f64 = 8.1;
const JG_COLLET_D: f64 = 9.7;
const JG_COLLET_BORE: f64 = 6.70;
const JG_COLLET_PROUD: f64 = 3.2;
/// The branch port's face, out from the run's axis.
const BRANCH_FACE_X: f64 = 26.;

fn hex(p: V3, flats: f64, length: f64, axis: V3, bore: f64) -> Result<Solid> {
    let radius = flats / 3_f64.sqrt();
    let points: Vec<_> = (0..6)
        .map(|i| {
            let angle = i as f64 * std::f64::consts::PI / 3.;
            v2(radius * angle.cos(), radius * angle.sin())
        })
        .collect();
    let x = if axis.x.abs() > 0.9 { V3::Y } else { V3::X };
    Plane::new(p, x, axis)?.extrude(&Profile::polygon(&points), length)?.cut(&cylinder(p - axis * 0.5, bore, length + 1., axis)?)
}

/// The white angle-stop adapter tee, unscrewed and open, standing on its bottom swivel at `p`.
fn white_tee(out: &mut Shown, p: V3) -> Result<()> {
    let branch = p + V3::Z * 31.;
    let mut add = |name: &str, solid: Solid| out.push((name.to_owned(), solid));
    add("tee-bottom-three-eighths-swivel", hex(p, 19., 18., V3::Z, 11.2)?);
    add("tee-bottom-brass-thread-neck", cylinder(p + V3::Z * 18., 12., 9., V3::Z)?);
    add("tee-white-polypropylene-body", cylinder(p + V3::Z * 20., 17., 20., V3::Z)?);
    let top = p + V3::Z * 40.;
    let thread = 21.;
    add("tee-top-three-eighths-compression-thread-root", cylinder(top, 9.4, thread, V3::Z)?);
    for i in 0..((thread - 1.) / 2.).floor().max(1.) as usize {
        add(
            &format!("tee-top-three-eighths-compression-thread-crest-{}", i + 1),
            cylinder(top + V3::Z * (0.8 + i as f64 * 2.), 10.5, 0.75, V3::Z)?,
        );
    }
    let face = branch + V3::X * BRANCH_FACE_X;
    let collar = face - V3::X * (JG_COLLET_PROUD + JG_COLLAR_LENGTH);
    let arm = cylinder(branch, 12., collar.x - p.x, V3::X)?.union(&cylinder(collar, JG_COLLAR_D, JG_COLLAR_LENGTH, V3::X)?)?;
    let socket = cylinder(face - V3::X * JG_INSERTION, JG_SOCKET_D, JG_INSERTION + 0.2, V3::X)?;
    add("tee-quarter-inch-branch-body", arm.cut(&socket)?);
    add(
        "tee-quarter-inch-release-collet",
        ring(face - V3::X * JG_COLLET_PROUD, JG_COLLET_D, JG_COLLET_BORE, JG_COLLET_PROUD, V3::X)?,
    );
    add("tee-branch-valve-stem-boss", cylinder(branch + V3::Y * 4., 11., 8., V3::Y)?);
    add("tee-branch-quarter-turn-hub", cylinder(branch + V3::Y * 10., 12., 6., V3::Y)?);
    add("tee-branch-quarter-turn-lever", block(branch + v3(-3.75, 11., 1.5), v3(7.5, 4., 11.)));
    add("tee-branch-lever-end", cylinder(branch + v3(0., 11., 12.5), 7.5, 4., V3::Y)?);
    add("tee-free-bottom-gasket", ring(p, 10.8, 5.4, 0.7, V3::Z)?);
    add("tee-open-top-waterway", cylinder(p + V3::Z * 61., 5.4, 0.6, V3::Z)?);
    add("tee-open-branch-grab-ring", ring(face - V3::X * 4., JG_SOCKET_D - 0.2, 5., 1.4, V3::X)?);
    Ok(())
}

/// The black push-connect tee beside the white adapter tee.
pub fn water_tees(black_tee: &str) -> Result<Shown> {
    let mut out = vec![];
    for body in import::payload(black_tee)? {
        out.push((format!("black-tee/{}", body.name), body.solid.translate(v3(30., 0., 0.))));
    }
    white_tee(&mut out, v3(-12., 0., -30.8))?;
    Ok(out)
}

/// The regulator's outlet mouth, from its frozen reference model, and how far the tether sits in it.
const REGULATOR_MOUTH_Z: f64 = -42.5;
const TETHER_IN_MOUTH: f64 = 4.;

/// The regulator without its printed markings, the red tether out of its outlet, and the spare
/// nylon washer.
pub fn regulator_and_tether(regulator: &str) -> Result<Shown> {
    let mut out = vec![];
    for body in import::payload(regulator)? {
        if !["black-print", "red-print", "band-"].iter().any(|s| body.name.contains(s)) {
            out.push((body.name, body.solid));
        }
    }
    let p = v3(0., 0., REGULATOR_MOUTH_Z);
    bend(&mut out, "red-tether", &[p + V3::Z * TETHER_IN_MOUTH, p - V3::Z * 46., p - V3::Z * 46. + V3::X * 120.], TUBE_D, 22.)?;
    let washer = Profile::circle(V2::ZERO, 14.).with_hole(Loop::circle(V2::ZERO, 10.));
    out.push(("washer".into(), Plane::XZ.at(v3(-108., 0., -62.)).extrude(&washer, 2.)?));
    Ok(out)
}

pub fn collet_press(model: &str) -> Result<Shown> {
    Ok(import::model(model)?.into_iter().map(|b| (b.name, b.solid)).collect())
}

/// The cord's appliance plug, its coiled cable and the mains plug.
pub fn power_cord() -> Result<Shown> {
    let body = rounded(Plane::XY.at(v3(0., 0., -9.5)), 28., 35., 3., 19.)?;
    let nose = rounded(Plane::XY.at(v3(0., -25., -7.5)), 24., 15., 2., 15.)?;
    let mut plug = body.union(&nose)?;
    for (x, z) in [(-6., 0.), (6., 0.), (0., 4.)] {
        plug = plug.cut(&block(v3(x - 1.2, -36., z - 2.), v3(2.4, 10., 4.)))?;
    }
    let mut out = vec![("c13-plug".into(), plug)];
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
    out.push(("cord".into(), Plane::new(points[0], V3::X, V3::Y)?.sweep(&Profile::circle(V2::ZERO, 3.25), &path)?));
    out.push(("mains".into(), rounded(Plane::XY.at(v3(100., -14., -8.5)), 22., 28., 3., 17.)?));
    for x in [-6., 6.] {
        out.push((format!("prong-{x}"), block(v3(99. + x, -40., -1.), v3(2., 12., 6.))));
    }
    out.push(("ground".into(), cylinder(v3(100., -40., -4.), 4.5, 13., V3::Y)?));
    Ok(out)
}

/// A closed booklet.
pub fn install_guide() -> Shown {
    [
        ("pages", v3(-45., -35., 0.), v3(90., 70., 4.)),
        ("lower", v3(-46., -36., -0.6), v3(92., 72., 0.6)),
        ("upper", v3(-46., -36., 4.), v3(92., 72., 0.6)),
        ("spine", v3(-46.4, -36., 0.), v3(0.8, 72., 4.)),
        ("panel", v3(-33., -22.5, 4.61), v3(66., 45., 0.1)),
    ]
    .into_iter()
    .map(|(name, p, size)| (name.into(), block(p, size)))
    .collect()
}

/// The cold kit's bag, standing, with its zipper and tag.
pub fn cold_kit() -> Result<Shown> {
    Ok(vec![
        ("bag".into(), rounded(Plane::XZ.at(v3(0., 9., 52.)), 90., 104., 6., 18.)?),
        ("zipper".into(), block(v3(-41.5, -10., 92.), v3(83., 20., 2.))),
        ("tag".into(), block(v3(-25., -9.45, 34.5), v3(50., 0.3, 27.))),
    ])
}
