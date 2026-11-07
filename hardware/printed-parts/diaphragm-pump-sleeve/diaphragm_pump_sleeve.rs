//! The diaphragm pump sleeve's files: the relaxed TPU elbow, posed to stand on its foot with both
//! mouths up, as it prints.
//!
//!     diaphragm-pump-sleeve [<output directory>]
use anyhow::{Result, bail};
use hsm_diaphragm_pump_sleeve_numbers as sleeve;
use hsm_kernel::part::write_part;
use hsm_kernel::profile::RLoop;
use hsm_kernel::*;
use std::path::PathBuf;

const NAME: &str = "diaphragm-pump-sleeve";
const OUTPUT: &str = "hardware/printed-parts/diaphragm-pump-sleeve";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: diaphragm-pump-sleeve [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    // The model and payload start from the same simplified print surface as the STL.
    let solid = build()?.simplified()?;
    let colour = hsm_catalog::linear(sleeve::COLOUR_SRGB);
    let bodies = [Body { name: NAME, color: Some(colour), solid: &solid }];
    println!("{}", write_part(&out, NAME, &bodies)?);
    Ok(())
}

fn neck(radius_b: f64, radius_t: f64, length: f64) -> Result<Solid> {
    let control = [
        v3(radius_b, 0.0, 0.0),
        v3(radius_b, length / 5.0, 0.0),
        v3(radius_b, 2.0 * length / 5.0, 0.0),
        v3(radius_t, 3.0 * length / 5.0, 0.0),
        v3(radius_t, 4.0 * length / 5.0, 0.0),
        v3(radius_t, length, 0.0),
    ];
    let curve = Spline::bezier(&control)?;
    // The smoothstep radius has max |d²r/dt²| = |rt-rb| * 10/sqrt(3).
    // Chord error is at most that bound * dt²/8; tangent turn is at most
    // the same bound * dt/length. Both follow the kernel's one curve rule.
    let second = (radius_t - radius_b).abs() * 10.0 / 3.0_f64.sqrt();
    let linear = (second / (8.0 * LINEAR)).sqrt();
    let angular = second / (length * ANGULAR);
    let count = (linear.max(angular).ceil() as usize).max(1).next_power_of_two();
    let (_, end) = curve.range();
    let mut points = vec![V3::ZERO];
    points.extend((0..=count).map(|i| curve.point(end * i as f64 / count as f64)));
    points.push(v3(0.0, length, 0.0));
    let mut segments = vec![0];
    segments.extend(std::iter::repeat_n(1, count));
    segments.extend([0, 0]);
    let region = Region {
        loops: vec![RLoop { pts: points, seg: segments }],
        curves: vec![Curve::Line, Curve::Free("quintic Bezier")],
    };
    Solid::revolve(&region, V3::ZERO, V3::Y, 360.0)
}

fn build() -> Result<Solid> {
    let rb = sleeve::barb_od() / 2.0;
    let rt = sleeve::tube_od() / 2.0;
    let axis = sleeve::tube_axis();
    let depth = sleeve::BARB_DEPTH;
    let length = sleeve::neck_length();
    let mouth = sleeve::tube_mouth();
    let x = |r, lo, hi| Solid::cylinder(v3(lo, 0.0, 0.0), V3::X, r, hi - lo);
    let y = |r, lo, hi| Solid::cylinder(v3(axis, lo, 0.0), V3::Y, r, hi - lo);
    let reduction = neck(rb, rt, length)?.transformed(&Affine::translation(v3(axis, 0.0, 0.0)));
    let outer = x(rb, -depth, axis)?
        .union(&Solid::sphere(v3(axis, 0.0, 0.0), rb)?)?
        .union(&reduction)?
        .union(&y(rt, length, mouth)?)?;
    let span = sleeve::foot_span();
    let s = sleeve::print_s();
    let foot = Solid::cuboid(v3(0.0, -span / 2.0, -span / 2.0),
                             v3(span, span / 2.0, span / 2.0))
        .transformed(&Affine::rotation(V3::ZERO, V3::Z, -45.0))
        .transformed(&Affine::translation(v3(sleeve::foot() * s, -sleeve::foot() * s, 0.0)));
    let outer = outer.cut(&foot)?;
    let bore_b = sleeve::BARB_BORE / 2.0;
    let bore_t = sleeve::TUBE_BORE / 2.0;
    let passage = sleeve::PASSAGE / 2.0;
    let stop = sleeve::TUBE_STOP;
    let entry = sleeve::ENTRY;
    let entry_height = sleeve::entry_height();
    let cavity = x(bore_b, -depth - 0.01, 0.0)?
        .union(&Solid::cone(v3(-depth, 0.0, 0.0), V3::X,
                            bore_b + entry, bore_b, entry_height)?)?
        .union(&x(passage, 0.0, axis)?)?
        .union(&y(passage, 0.0, stop)?)?
        .union(&y(bore_t, stop, mouth + 0.01)?)?
        .union(&Solid::cone(v3(axis, mouth - entry_height, 0.0), V3::Y,
                            bore_t, bore_t + entry, entry_height)?)?;
    let body = outer.cut(&cavity)?;
    let pose = Plane::new(V3::ZERO, v3(s, 0.0, -s), v3(0.0, -1.0, 0.0))?;
    let shift = sleeve::print_shift();
    Ok(body.transformed(&pose.to_world())
        .transformed(&Affine::translation(v3(shift[0], shift[1], shift[2]))))
}
