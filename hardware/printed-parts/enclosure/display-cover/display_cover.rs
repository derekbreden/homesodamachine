//! The face-up display bezel and its matching visible screws and short inserts.
use anyhow::Result;
use hsm_enclosure_numbers::display_mount as m;
use hsm_kernel::{Body, Loop, Plane, Profile, Solid, v2, v3};
use hsm_kernel::part::{args, write_part};
use serde_json::json;

fn cylinder(x: f64, y: f64, radius: f64, lo: f64, hi: f64) -> Result<Solid> {
    Plane::XY.at(v3(0., 0., lo)).extrude(&Profile::new(Loop::circle(v2(x, y), radius)), hi - lo)
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let outer = Loop::rounded_rect(v2(0., 0.), m::WIDTH, m::HEIGHT, m::CORNER)?;
    let window = Loop::rounded_rect(v2(0., 0.), m::WINDOW[0], m::WINDOW[1], m::WINDOW[2])?;
    let mut cover = Plane::XY.at(v3(0., 0., -m::THICK)).extrude(
        &Profile { outer, holes: vec![window] }, m::THICK)?;
    let seat = -m::COUNTERBORE_DEPTH;
    let mut hardware = Vec::new();
    for (i, [x, y]) in m::STATIONS.into_iter().enumerate() {
        cover = cover.cut(&cylinder(x, y, m::CLEARANCE_DIA / 2., -m::THICK - 1., 1.)?)?
            .cut(&cylinder(x, y, m::COUNTERBORE_DIA / 2., seat, 1.)?)?;
        let screw = cylinder(x, y, m::SCREW_DIA / 2., seat - m::SCREW_LENGTH, seat)?
            .union(&cylinder(x, y, m::HEAD_DIA / 2., seat, seat + m::HEAD_HEIGHT)?)?;
        let hex = (0..6).map(|k| {
            let a = k as f64 * std::f64::consts::PI / 3.;
            let r = m::SOCKET_FLATS / 3_f64.sqrt();
            v2(x + r * a.cos(), y + r * a.sin())
        }).collect::<Vec<_>>();
        let socket = Plane::XY.at(v3(0., 0., seat + 1.4)).extrude(&Profile::polygon(&hex), 1.7)?;
        hardware.push((format!("display-screw-{}", i + 1), screw.cut(&socket)?, [0.025, 0.025, 0.025]));
        let insert = cylinder(x, y, m::INSERT_DIA / 2., -m::THICK - m::INSERT_LENGTH, -m::THICK)?
            .cut(&cylinder(x, y, 1.3, -m::THICK - m::INSERT_LENGTH - 0.1, -m::THICK + 0.1)?)?;
        hardware.push((format!("display-insert-{}", i + 1), insert, [0.65, 0.38, 0.09]));
    }
    println!("{}", write_part(&out, "display-cover", &[Body {
        name: "display-cover", color: Some(n.color("color")?), solid: &cover,
    }])?);
    let parts = hardware.iter().map(|(name, solid, color)| Body {
        name: name.as_str(), solid, color: Some(*color),
    }).collect::<Vec<_>>();
    println!("{}", write_part(&out, "display-cover-fasteners", &parts)?);
    std::fs::write(out.join("mount-dimensions.json"), serde_json::to_vec_pretty(&json!({
        "screw": "Black M3 x 6 socket-head cap screw",
        "insert": "ruthex RX-M3S x 4 short heat-set insert",
        "gasket_thickness_mm": m::GASKET_THICK,
        "glass_thickness_mm": m::GLASS_THICK,
        "cover_mm": [m::WIDTH, m::HEIGHT, m::THICK], "corner_radius_mm": m::CORNER,
        "window_mm": m::WINDOW, "stations_local_xy_mm": m::STATIONS,
        "clearance_diameter_mm": m::CLEARANCE_DIA, "counterbore_diameter_mm": m::COUNTERBORE_DIA,
        "counterbore_depth_mm": m::COUNTERBORE_DEPTH, "head_diameter_mm": m::HEAD_DIA,
        "head_height_mm": m::HEAD_HEIGHT, "head_proud_mm": m::HEAD_HEIGHT - m::COUNTERBORE_DEPTH,
        "screw_length_mm": m::SCREW_LENGTH, "insert_length_mm": m::INSERT_LENGTH,
        "insert_diameter_mm": m::INSERT_DIA, "pilot_diameter_mm": m::PILOT_DIA,
        "pilot_depth_mm": m::PILOT_DEPTH, "required_backing_mm": m::BACKING,
        "screw_engagement_mm": m::SCREW_LENGTH - m::THICK + m::COUNTERBORE_DEPTH,
        "screw_to_outer_border_mm": [m::WIDTH / 2. - m::STATIONS[1][0], m::HEIGHT / 2. - m::STATIONS[2][1]],
    }))?)?;
    Ok(())
}
