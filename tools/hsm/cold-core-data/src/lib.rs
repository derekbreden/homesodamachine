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

pub fn bond_constants() -> Value {
    json!({"RIM_AZIMUTH_XY": [23.2, 48.0], "TUBE_OUTER_RADIUS": 63.5,
           "TUBE_WALL": 0.065 * 25.4, "RIM_HEIGHT": 0.25 * 25.4,
           "HOLE_HEIGHT": 3.5, "TAP_DRILL_DIAMETER": 2.5,
           "THREAD_DIAMETER": 3.0, "THREAD_PITCH": 0.5,
           "SCREW_LENGTH": 4.0, "SCREW_DIAMETER": 3.0,
           "SCREW_HEAD_DIAMETER": 5.5, "SCREW_HEAD_HEIGHT": 3.0,
           "RING_TONGUE_THICKNESS": 0.8, "RING_EYE_DIAMETER": 8.0,
           "RING_BARREL_DIAMETER": 4.2, "RING_BARREL_LENGTH": 6.0,
           "WASHER_DIAMETER": 6.0, "WASHER_BORE": 3.2, "WASHER_THICKNESS": 0.4,
           "WASHER_PART": "M3 DIN 6797 A external-tooth lockwasher, A2 stainless",
           "WASHER_SOURCE": "https://damesa.com/en/products/fasteners/washers/din-6797-external-tooth-lock-washer-form-a"})
}

pub fn bond(top_plate_outer_z: f64) -> Value {
    let constants = bond_constants();
    let n = |key: &str| constants[key].as_f64().unwrap();
    let scale = 23.2_f64.hypot(48.);
    let (ux, uy) = (23.2 / scale, 48. / scale);
    let z = top_plate_outer_z + n("HOLE_HEIGHT");
    let radial = |radius: f64, height: f64| [ux * radius, uy * radius, height];
    let head_radius = n("TUBE_OUTER_RADIUS") + n("RING_TONGUE_THICKNESS") + n("WASHER_THICKNESS");
    let tip_radius = head_radius - n("SCREW_LENGTH");
    json!({
        "body": "carbonator-tube",
        "base_center_mm": radial(n("TUBE_OUTER_RADIUS"), top_plate_outer_z),
        "hole_center_mm": radial(n("TUBE_OUTER_RADIUS") - n("TUBE_WALL") / 2., z),
        "hole_axis": [-ux, -uy, 0.], "tap_drill_diameter_mm": n("TAP_DRILL_DIAMETER"),
        "thread": "M3 x 0.5 through", "thread_diameter_mm": n("THREAD_DIAMETER"),
        "thread_pitch_mm": n("THREAD_PITCH"), "thread_engagement_mm": n("TUBE_WALL"),
        "nominal_engaged_threads": n("TUBE_WALL") / n("THREAD_PITCH"),
        "rim_top_z_mm": top_plate_outer_z + n("RIM_HEIGHT"),
        "hole_height_above_plate_mm": n("HOLE_HEIGHT"),
        "hole_height_below_rim_mm": n("RIM_HEIGHT") - n("HOLE_HEIGHT"),
        "contact_point_mm": radial(n("TUBE_OUTER_RADIUS"), z),
        "contact_outward": [ux, uy, 0.],
        "wire_exit_mm": radial(n("TUBE_OUTER_RADIUS") + n("RING_BARREL_DIAMETER") / 2., z + 9.),
        "wire_outward": [0., 0., 1.], "screw_axis": [-ux, -uy, 0.],
        "screw_underhead_mm": radial(head_radius, z), "screw_length_mm": n("SCREW_LENGTH"),
        "screw_tip_mm": radial(tip_radius, z),
        "screw_projection_inside_tube_mm": n("TUBE_OUTER_RADIUS") - n("TUBE_WALL") - tip_radius,
        "screw_source": "304 stainless M3x12 stock shortened and end-finished to M3x4",
        "ring_tongue_thickness_mm": n("RING_TONGUE_THICKNESS"),
        "ring_eye_diameter_mm": n("RING_EYE_DIAMETER"),
        "ring_barrel_diameter_mm": n("RING_BARREL_DIAMETER"),
        "ring_barrel_length_mm": n("RING_BARREL_LENGTH"),
        "lockwasher_part": constants["WASHER_PART"], "lockwasher_source": constants["WASHER_SOURCE"],
        "hardware_bodies": ["carbonator-earth-screw", "carbonator-earth-lockwasher"],
        "clamp_order_from_head": ["M3x4 stainless screw", constants["WASHER_PART"],
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
        "aero-measurements" => Ok(floats::aero_measurements()),
        "aero-numbers" => Ok(floats::aero_numbers(&input["colors"])),
        "rod" => Ok(rod()),
        "rod-fit" => Ok(rod_fit(
            number(input, "rod_diameter")?,
            number(input, "register_depth")?,
        )),
        "bond-constants" => Ok(bond_constants()),
        "bond" => Ok(bond(number(input, "top_plate_outer_z")?)),
        "mandrel" => Ok(mandrel::datums(
            number(input, "evap_tail_low_z")?,
            number(input, "evap_tail_high_z")?,
        )),
        "mandrel-numbers" => Ok(mandrel::numbers(
            number(input, "evap_tail_low_z")?,
            number(input, "evap_tail_high_z")?,
            &input["color"],
        )),
        "mandrel-report" => Ok(json!(mandrel::report(
            number(input, "evap_tail_low_z")?,
            number(input, "evap_tail_high_z")?
        ))),
        "mandrel-variables" => Ok(mandrel::variables(
            number(input, "evap_tail_low_z")?,
            number(input, "evap_tail_high_z")?,
        )),
        "coil" => coil::request(input),
        op => bail!("unknown cold-core data operation {op}"),
    }
}

fn formatted(value: f64, spec: &str) -> String {
    hsm_documents::format_number(value, spec).expect("cold-core formatting specification")
}
