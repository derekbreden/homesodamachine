//! Cold-core stock, float sizing, coil forming and manufacturing datums, in mm.
//! The Python interfaces carry these results to callers whose recipes are still Python.

#![recursion_limit = "512"]

use anyhow::{Context, Result, bail};
use serde_json::{Value, json};

pub mod coil;
pub mod compiled;
pub mod floats;
pub mod interface;
pub mod mandrel;

fn number(value: &Value, name: &str) -> Result<f64> {
    value[name]
        .as_f64()
        .with_context(|| format!("missing number {name}"))
}

pub fn stock() -> Value {
    use hsm_carbonator_tube_numbers as tube;
    json!({"carbonator_outer_radius": tube::OUTER_RADIUS,
           "carbonator_height": tube::LENGTH,
           "TUBE_OD": tube::OD, "TUBE_WALL": tube::WALL, "TUBE_ID": tube::ID})
}

pub fn rod() -> Value {
    json!({"finished_length": 5.110, "length_tolerance": 0.005,
           "diameter_tolerance": 0.002, "inside_face_span": 5.000,
           "inside_face_span_tolerance": 0.010, "edge_break_maximum": 0.003,
           "end_squareness_degrees": 0.5, "register_depth_tolerance": 0.005,
           "register_point_degrees": 135.0, "register_point_tolerance_degrees": 0.5})
}

/// Independent-extreme axial stack, including the drill point and rod-end form.
pub fn rod_fit(diameter: f64, depth: f64) -> Value {
    let d = rod();
    let n = |key: &str| d[key].as_f64().unwrap();
    let seat = |depth: f64, diameter: f64, point: f64, edge: f64| {
        depth - (diameter / 2. - edge) / (point / 2.).to_radians().tan()
    };
    let end_error =
        (diameter + n("diameter_tolerance")) * n("end_squareness_degrees").to_radians().tan();
    let nominal = seat(depth, diameter, n("register_point_degrees"), 0.);
    let low = seat(
        depth - n("register_depth_tolerance"),
        diameter + n("diameter_tolerance"),
        n("register_point_degrees") - n("register_point_tolerance_degrees"),
        0.,
    ) - end_error;
    let high = seat(
        depth + n("register_depth_tolerance"),
        diameter - n("diameter_tolerance"),
        n("register_point_degrees") + n("register_point_tolerance_degrees"),
        n("edge_break_maximum"),
    ) + end_error;
    json!({
        "nominal_engagement": n("finished_length") - n("inside_face_span") - nominal,
        "nominal_clearance": n("inside_face_span") + 2. * nominal - n("finished_length"),
        "minimum_engagement": n("finished_length") - n("length_tolerance")
            - n("inside_face_span") - n("inside_face_span_tolerance") - high,
        "minimum_clearance": n("inside_face_span") - n("inside_face_span_tolerance")
            + 2. * low - n("finished_length") - n("length_tolerance"),
        "seat_minimum": low, "seat_maximum": high
    })
}

/// The carbonator's earth bond's own numbers, from the carbonator's crate.
pub fn bond_constants() -> Value {
    use hsm_carbonator_numbers::bond as b;
    json!({"RIM_AZIMUTH_XY": b::RIM_AZIMUTH_XY, "TUBE_OUTER_RADIUS": b::TUBE_OUTER_RADIUS,
           "TUBE_WALL": b::TUBE_WALL, "RIM_HEIGHT": b::RIM_HEIGHT,
           "HOLE_HEIGHT": b::HOLE_HEIGHT, "TAP_DRILL_DIAMETER": b::TAP_DRILL_DIAMETER,
           "THREAD_DIAMETER": b::THREAD_DIAMETER, "THREAD_PITCH": b::THREAD_PITCH,
           "SCREW_LENGTH": b::SCREW_LENGTH, "SCREW_DIAMETER": b::SCREW_DIAMETER,
           "SCREW_HEAD_DIAMETER": b::SCREW_HEAD_DIAMETER, "SCREW_HEAD_HEIGHT": b::SCREW_HEAD_HEIGHT,
           "RING_TONGUE_THICKNESS": b::RING_TONGUE_THICKNESS, "RING_EYE_DIAMETER": b::RING_EYE_DIAMETER,
           "RING_BARREL_DIAMETER": b::RING_BARREL_DIAMETER, "RING_BARREL_LENGTH": b::RING_BARREL_LENGTH,
           "WASHER_DIAMETER": b::WASHER_DIAMETER, "WASHER_BORE": b::WASHER_BORE,
           "WASHER_THICKNESS": b::WASHER_THICKNESS,
           "WASHER_PART": b::WASHER_PART, "WASHER_SOURCE": b::WASHER_SOURCE})
}

/// The earth bond's datums for a top plate whose outer face is at `top_plate_outer_z`, from the
/// carbonator's crate, with what the BOM and the docs say of its hardware.
pub fn bond(top_plate_outer_z: f64) -> Value {
    use hsm_carbonator_numbers::{BOND_BODY, bond as b};
    let d = b::datums(top_plate_outer_z);
    json!({
        "body": BOND_BODY,
        "base_center_mm": d.base_center,
        "hole_center_mm": d.hole_center,
        "hole_axis": d.hole_axis, "tap_drill_diameter_mm": b::TAP_DRILL_DIAMETER,
        "thread": "M3 x 0.5 through", "thread_diameter_mm": b::THREAD_DIAMETER,
        "thread_pitch_mm": b::THREAD_PITCH, "thread_engagement_mm": b::TUBE_WALL,
        "nominal_engaged_threads": b::TUBE_WALL / b::THREAD_PITCH,
        "rim_top_z_mm": d.rim_top_z,
        "hole_height_above_plate_mm": b::HOLE_HEIGHT,
        "hole_height_below_rim_mm": b::RIM_HEIGHT - b::HOLE_HEIGHT,
        "contact_point_mm": d.contact_point,
        "contact_outward": d.contact_outward,
        "wire_exit_mm": d.wire_exit,
        "wire_outward": d.wire_outward, "screw_axis": d.screw_axis,
        "screw_underhead_mm": d.screw_underhead, "screw_length_mm": b::SCREW_LENGTH,
        "screw_tip_mm": d.screw_tip,
        "screw_projection_inside_tube_mm": d.screw_projection_inside_tube,
        "screw_source": b::SCREW_SOURCE,
        "ring_tongue_thickness_mm": b::RING_TONGUE_THICKNESS,
        "ring_eye_diameter_mm": b::RING_EYE_DIAMETER,
        "ring_barrel_diameter_mm": b::RING_BARREL_DIAMETER,
        "ring_barrel_length_mm": b::RING_BARREL_LENGTH,
        "lockwasher_part": b::WASHER_PART, "lockwasher_source": b::WASHER_SOURCE,
        "hardware_bodies": ["carbonator-earth-screw", "carbonator-earth-lockwasher"],
        "clamp_order_from_head": ["M3x4 stainless screw", b::WASHER_PART,
            "M3 closed ring tongue", "bare upper tube rim tapped M3x0.5"]
    })
}

pub fn request(input: &Value) -> Result<Value> {
    if let Some(result) = hsm_documents::interop::native_object(input) {
        let result = result?;
        compiled::register_io()?;
        return Ok(result);
    }
    match input["op"].as_str().context("request needs op")? {
        "compiled" => {
            let result = compiled::request(input)?;
            compiled::register_io()?;
            Ok(result)
        }
        "compiled-invoke" => {
            let result = compiled::invoke(input)?;
            compiled::register_io()?;
            Ok(result)
        }
        "stock" => Ok(stock()),
        "interface-base" => interface::base(&input["fits"]),
        "interface-reservoir-conduit" => interface::reservoir_conduit(
            input["kind"]
                .as_str()
                .context("reservoir conduit needs kind")?,
            input["side"]
                .as_i64()
                .context("reservoir conduit needs side")?,
        ),
        "float" => Ok(floats::aero_datums()),
        "float-waterline" => Ok(json!(floats::waterline(
            input["mass_g"].as_f64(),
            input["liquid_density"].as_f64()
        ))),
        "float-edge" => Ok(json!(floats::edge_distance(
            number(input, "rod_axis")?,
            number(input, "reed_axis")?,
            input["float_edge"].as_bool().unwrap_or(false)
        ))),
        "rod" => Ok(rod()),
        "rod-fit" => Ok(rod_fit(
            number(input, "rod_diameter")?,
            number(input, "register_depth")?,
        )),
        "bond-constants" => Ok(bond_constants()),
        "bond" => Ok(bond(number(input, "top_plate_outer_z")?)),
        "mandrel" => Ok(mandrel::datums()),
        "mandrel-numbers" => Ok(mandrel::numbers(&input["color"])),
        "mandrel-report" => Ok(json!(mandrel::report())),
        "mandrel-variables" => Ok(mandrel::variables()),
        "coil" => coil::request(input),
        op => bail!("unknown cold-core data operation {op}"),
    }
}

fn formatted(value: f64, spec: &str) -> String {
    hsm_documents::format_number(value, spec).expect("cold-core formatting specification")
}
