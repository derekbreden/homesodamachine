//! The keystone replica draws the vendor-observed shell, cantilever latch and open IDC comb.
use anyhow::{Context, Result};
use hsm_kernel::{Body, Loop, Plane, Profile, Solid, part, v2, v3};
use serde_json::Value;
use std::path::PathBuf;

fn dim(data: &Value, name: &str) -> f64 {
    data[name].as_f64().unwrap_or_else(|| panic!("missing keystone dimension {name}"))
}

fn pair(data: &Value, name: &str) -> [f64; 2] {
    [data[name][0].as_f64().unwrap(), data[name][1].as_f64().unwrap()]
}

fn block(width: f64, height: f64, radius: f64, front: f64, rear: f64, center_z: f64) -> Result<Solid> {
    Plane::XZ.at(v3(0., front, center_z)).extrude(
        &Profile::new(Loop::rounded_rect(v2(0., 0.), width, height, radius)?), front - rear)
}

/// The profile lies in the axial plane; its straight segments describe molded ramps.
fn axial_prism(points: &[(f64, f64)], width: f64) -> Result<Solid> {
    Plane::YZ.at(v3(-width / 2., 0., 0.)).extrude(
        &Profile::polygon(&points.iter().map(|&(y, z)| v2(y, z)).collect::<Vec<_>>()), width)
}

fn build(data: &Value) -> Result<Solid> {
    let e = &data["photo_estimates"];
    let face_w = dim(data, "FACE_W");
    let face_h = dim(data, "FACE_H");
    let lip = dim(data, "LIP_D");
    let depth = dim(data, "DEPTH");
    let slip = dim(data, "FIT_SLIP");
    let rear = -dim(data, "BODY_DEPTH");
    let neck_w = dim(data, "POCKET_W") - slip;
    let core_h = dim(e, "rear_body_height_mm");
    let neck_end = -dim(e, "neck_depth_mm");
    let mut jack = block(face_w, face_h, dim(e, "face_corner_radius_mm"), 0., -lip, 0.)?
        .union(&block(neck_w, core_h, dim(e, "rear_corner_radius_mm"), -lip, neck_end, 0.)?)?
        .union(&block(face_w, core_h, dim(e, "rear_corner_radius_mm"), neck_end, rear, 0.)?)?;

    let latch_w = dim(e, "latch_width_mm");
    let root = dim(e, "latch_root_y_mm");
    let tip = dim(e, "latch_tip_y_mm");
    let floor = dim(e, "latch_beam_floor_z_mm");
    let beam_top = floor + dim(e, "latch_beam_thickness_mm");
    let thumb_top = dim(data, "POCKET_RISE") + (dim(data, "POCKET_H") - slip) / 2.;
    let thumb_rear = tip - dim(e, "thumb_length_mm");
    // The latch's neck stands above an open gap, with its root attached to the rear shell.
    let root_block = Solid::cuboid(v3(-latch_w / 2., root, core_h / 2. - 0.2),
        v3(latch_w / 2., root + 2.2, beam_top));
    let beam = axial_prism(&[(root, floor), (tip, floor), (tip, beam_top), (root, beam_top)], latch_w)?;
    let thumb = axial_prism(&[(thumb_rear, beam_top - 0.1), (tip, beam_top - 0.1),
        (tip, thumb_top), (thumb_rear + 0.8, thumb_top)], latch_w)?;
    jack = jack.union(&root_block)?.union(&beam)?.union(&thumb)?;

    let low = dim(data, "POCKET_RISE") - (dim(data, "POCKET_H") - slip) / 2.;
    let hook_y = pair(e, "lower_hook_y_mm");
    let hook_w = dim(e, "lower_hook_width_mm");
    let hook = axial_prism(&[(hook_y[0], -core_h / 2. + 0.2),
        (hook_y[0], low), (hook_y[1] - 0.8, low),
        (hook_y[1], low + 0.8), (hook_y[1], -core_h / 2. + 0.2)], hook_w)?;
    jack = jack.union(&hook)?;

    // The existing receptacle owns these capture clearances and the seating datum.
    let top = dim(data, "POCKET_RISE") + dim(data, "POCKET_H") / 2.;
    let bottom = dim(data, "POCKET_RISE") - dim(data, "POCKET_H") / 2.;
    for (catch, zc) in [
        (pair(data, "CATCH_UPPER"), top - pair(data, "CATCH_UPPER")[0] / 2.),
        (pair(data, "CATCH_LOWER"), bottom + pair(data, "CATCH_LOWER")[0] / 2.),
    ] {
        let capture = Solid::cuboid(
            v3(-dim(data, "POCKET_W") / 2. - slip, -depth, zc - catch[0] / 2. - slip),
            v3(dim(data, "POCKET_W") / 2. + slip, -depth + catch[1] + slip, zc + catch[0] / 2. + slip));
        jack = jack.cut(&capture)?;
    }

    let port_z = -1.;
    let port_w = dim(data, "PORT_W");
    let port_h = dim(data, "PORT_H");
    let port_depth = dim(data, "PORT_DEPTH");
    let port = block(port_w, port_h, 0.05, 0.1, -port_depth, port_z)?;
    let notch_h = dim(data, "LATCH_SLOT_H");
    let notch_z = port_z - port_h / 2. - notch_h / 2. + 1.2;
    let notch = block(dim(data, "LATCH_SLOT_W"), notch_h, 0.05, 0.1, -port_depth, notch_z)?;
    jack = jack.cut(&port)?.cut(&notch)?;
    let chamfer = dim(e, "entry_chamfer_mm");
    let mouth = Solid::loft(&[
        Profile::rect(v2(0., port_z), port_w + chamfer * 2., port_h + chamfer * 2.)
            .place(&Plane::XZ.at(v3(0., 0.02, 0.))),
        Profile::rect(v2(0., port_z), port_w, port_h)
            .place(&Plane::XZ.at(v3(0., -chamfer, 0.))),
    ])?;
    jack = jack.cut(&mouth)?;

    let idc_y = pair(e, "idc_terminal_y_mm");
    let slot_w = dim(e, "idc_slot_width_mm");
    let recess = dim(e, "idc_recess_depth_mm");
    for side in [-1., 1.] {
        for y in idc_y {
            let (xa, xb) = if side < 0. { (-face_w / 2. - 0.1, -face_w / 2. + recess) }
                else { (face_w / 2. - recess, face_w / 2. + 0.1) };
            let slot = Solid::cuboid(v3(xa, y - slot_w / 2., -core_h / 2. - 0.1),
                v3(xb, y + slot_w / 2., dim(e, "idc_slot_roof_z_mm")));
            jack = jack.cut(&slot)?;
        }
        let [ya, yb] = pair(e, "side_recess_y_mm");
        let [za, zb] = pair(e, "side_recess_z_mm");
        let shallow = dim(e, "side_recess_depth_mm");
        let (xa, xb) = if side < 0. { (-face_w / 2. - 0.1, -face_w / 2. + shallow) }
            else { (face_w / 2. - shallow, face_w / 2. + 0.1) };
        jack = jack.cut(&Solid::cuboid(v3(xa, ya, za), v3(xb, yb, zb)))?;
    }
    Ok(jack)
}

fn main() -> Result<()> {
    let dir = PathBuf::from(std::env::args().nth(1).context("keystone output directory")?);
    std::fs::create_dir_all(&dir)?;
    let data = serde_json::from_str(include_str!("replica-parameters.json"))?;
    let jack = build(&data)?;
    let color = hsm_sandbox::material("M_DONOR_BLACK")?;
    println!("{}", part::write_shown(&dir, "riteav-keystone", &[Body {
        name: "riteav-keystone", color: Some(color), solid: &jack,
    }])?);
    Ok(())
}
