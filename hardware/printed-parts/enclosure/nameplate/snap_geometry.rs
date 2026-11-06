//! The four-screw plate and blind-insert receiver share one dimension record.
use anyhow::Result;
use hsm_kernel::{Loop, Plane, Profile, Solid, v2, v3};
use serde_json::Value;

/// The rear nameplate's receiver: plate back at Y=0, face +Y, height +Z.
#[derive(Clone, Debug, PartialEq)]
pub struct Snap {
    pub width: f64,
    pub height: f64,
    pub thick: f64,
    pub corner: f64,
    pub slip: f64,
    pub supported: f64,
    pub frame_width: f64,
    pub frame_bottom: f64,
    pub frame_top: f64,
    pub frame_corner: f64,
    pub floor_rear: f64,
    pub floor_stock: f64,
    pub insert_stock_rear: f64,
    pub insert_stock_radius: f64,
    pub field_proud: f64,
    pub crown_y: f64,
    pub mouth_width: f64,
    pub mouth_height: f64,
    pub stations: Vec<[f64; 2]>,
    pub clearance_diameter: f64,
    pub counterbore_diameter: f64,
    pub counterbore_depth: f64,
    pub screw_length: f64,
    pub screw_diameter: f64,
    pub head_diameter: f64,
    pub head_height: f64,
    pub hex_key: f64,
    pub insert_diameter: f64,
    pub insert_length: f64,
    pub pilot_diameter: f64,
    pub pilot_rear: f64,
}

impl Snap {
    /// The dimension record as the nameplate's Python module writes it.
    pub fn read(n: &Value) -> Snap {
        let f = |key: &str| n[key].as_f64().expect("mount dimension");
        Snap {
            width: f("width"),
            height: f("height"),
            thick: f("thick"),
            corner: f("corner"),
            slip: f("slip"),
            supported: f("supported"),
            frame_width: f("frame_width"),
            frame_bottom: f("frame_bottom"),
            frame_top: f("frame_top"),
            frame_corner: f("frame_corner"),
            floor_rear: f("floor_rear"),
            floor_stock: f("floor_stock"),
            insert_stock_rear: f("insert_stock_rear"),
            insert_stock_radius: f("insert_stock_radius"),
            field_proud: f("field_proud"),
            crown_y: f("crown_y"),
            mouth_width: f("mouth_width"),
            mouth_height: f("mouth_height"),
            stations: n["stations"].as_array().unwrap().iter()
                .map(|p| [p[0].as_f64().unwrap(), p[1].as_f64().unwrap()]).collect(),
            clearance_diameter: f("clearance_diameter"),
            counterbore_diameter: f("counterbore_diameter"),
            counterbore_depth: f("counterbore_depth"),
            screw_length: f("screw_length"),
            screw_diameter: f("screw_diameter"),
            head_diameter: f("head_diameter"),
            head_height: f("head_height"),
            hex_key: f("hex_key"),
            insert_diameter: f("insert_diameter"),
            insert_length: f("insert_length"),
            pilot_diameter: f("pilot_diameter"),
            pilot_rear: f("pilot_rear"),
        }
    }

    fn stations(&self) -> impl Iterator<Item = (f64, f64)> + '_ {
        self.stations.iter().map(|p| (p[0], p[1]))
    }
}

fn xz(profile: Profile, y0: f64, y1: f64) -> Result<Solid> {
    Plane::XZ.at(v3(0., y0, 0.)).extrude(&profile, -(y1 - y0))
}
pub fn cylinder_y(x: f64, z: f64, r: f64, y0: f64, y1: f64) -> Result<Solid> {
    xz(Profile::new(Loop::circle(v2(x, z), r)), y0, y1)
}
pub fn snap_plate_cuts(n: &Snap) -> Result<Solid> {
    let mut cuts = vec![];
    for (x, z) in n.stations() {
        cuts.push(cylinder_y(x, z, n.clearance_diameter / 2., -0.1, n.thick + 1.)?);
        cuts.push(cylinder_y(x, z, n.counterbore_diameter / 2.,
            n.thick - n.counterbore_depth, n.thick + 1.)?);
    }
    Solid::union_all(&cuts)
}
pub fn snap_plate_blank(n: &Snap) -> Result<Solid> {
    xz(Profile::new(Loop::rounded_rect(v2(0., 0.), n.width, n.height,
        n.corner)?), 0., n.thick)?.cut(&snap_plate_cuts(n)?)
}
pub fn snap_receiver_stock(n: &Snap) -> Result<Solid> {
    let (bottom, top) = (n.frame_bottom, n.frame_top);
    let t = n.thick;
    let frame = xz(Profile::new(Loop::rounded_rect(v2(0., (bottom + top) / 2.),
        n.frame_width, top - bottom, n.frame_corner)?), n.floor_rear, t)?;
    // Back-top prints roof down: one 45 degree crown runs to the enclosure skin.
    let crown = Plane::YZ.at(v3(-n.frame_width, 0., 0.)).extrude(&Profile::polygon(&[
        v2(n.crown_y - 0.01, top + 0.01), v2(t + 0.01, top + 0.01),
        v2(t + 0.01, top - n.field_proud - 0.01)
    ]), 2. * n.frame_width)?;
    let mut parts = vec![frame.cut(&crown)?];
    // These short, broad insert lands coincide with the enclosure's existing
    // rear wall. They keep the standalone receiver model complete as well.
    for (x, z) in n.stations() {
        parts.push(cylinder_y(x, z, n.insert_stock_radius,
            n.insert_stock_rear, n.floor_rear + 0.1)?);
    }
    Solid::union_all(&parts)
}
pub fn snap_receiver_cuts(n: &Snap) -> Result<Solid> {
    let mouth = xz(Profile::new(Loop::rounded_rect(v2(0., 0.), n.mouth_width,
        n.mouth_height, n.corner + n.slip)?), 0., n.thick + 1.)?;
    let mut cuts = vec![mouth.clone(), mouth.translate(v3(0., 0., -n.supported))];
    for (x, z) in n.stations() {
        // Upper bores end against the adjoining support floors. Lower bores
        // continue through the rear land into the cold-core clearance.
        let rear = if z > 0. { n.insert_stock_rear } else { n.pilot_rear };
        cuts.push(cylinder_y(x, z, n.pilot_diameter / 2., rear, 0.01)?);
    }
    Solid::union_all(&cuts)
}
/// Installed hardware envelopes. Threads and knurls are represented by their
/// major diameters; the insert's 0.3 mm radial thermal interference is intentional.
pub fn snap_hardware(n: &Snap) -> Result<Vec<(String, Solid, [f64; 3])>> {
    let mut parts = vec![];
    let seat = n.thick - n.counterbore_depth;
    for (i, (x, z)) in n.stations().enumerate() {
        let screw = cylinder_y(x, z, n.screw_diameter / 2., seat - n.screw_length, seat)?
            .union(&cylinder_y(x, z, n.head_diameter / 2., seat, seat + n.head_height)?)?;
        let points = (0..6).map(|k| {
            let a = std::f64::consts::PI * k as f64 / 3.;
            let r = n.hex_key / 2. / (std::f64::consts::PI / 6.).cos();
            v2(x + r * a.cos(), z + r * a.sin())
        }).collect::<Vec<_>>();
        let socket = xz(Profile::polygon(&points), seat + 1.4, seat + n.head_height + 0.1)?;
        parts.push((format!("nameplate-screw-{}", i + 1), screw.cut(&socket)?, [0.025, 0.025, 0.025]));
        let insert = cylinder_y(x, z, n.insert_diameter / 2., -n.insert_length, 0.)?
            .cut(&cylinder_y(x, z, 1.3, -n.insert_length - 0.1, 0.1)?)?;
        parts.push((format!("nameplate-insert-{}", i + 1), insert, [0.65, 0.38, 0.09]));
    }
    Ok(parts)
}

pub fn plate_cuts(n: &Value) -> Result<Solid> {
    snap_plate_cuts(&Snap::read(n))
}
pub fn plate_blank(n: &Value) -> Result<Solid> {
    snap_plate_blank(&Snap::read(n))
}
pub fn receiver_stock(n: &Value) -> Result<Solid> {
    snap_receiver_stock(&Snap::read(n))
}
pub fn receiver_cuts(n: &Value) -> Result<Solid> {
    snap_receiver_cuts(&Snap::read(n))
}
pub fn receiver(n: &Value) -> Result<Solid> {
    receiver_stock(n)?.cut(&receiver_cuts(n)?)
}
pub fn hardware(n: &Value) -> Result<Vec<(String, Solid, [f64; 3])>> {
    snap_hardware(&Snap::read(n))
}
