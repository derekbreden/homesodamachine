//! Source-frame cold-core components. Imported fine models retain their raw record slots.
use crate::core_fittings::{self as fittings, cylinder, number as f, point as p};
use anyhow::{Context, Result, bail};
use hsm_kernel::math::{cos, radians, sin};
use hsm_kernel::part::Numbers;
use hsm_kernel::*;
use serde_json::Value;

pub struct Piece {
    pub name: String,
    pub color: Option<[f64; 3]>,
    pub fine: Solid,
    pub printed_presentation: bool,
}

fn array(value: &Value) -> Result<&Vec<Value>> {
    value.as_array().context("body array")
}

fn placed(mut solid: Solid, row: &Value, seat_lift: Option<f64>) -> Result<Solid> {
    if row["mirror_x"].as_bool() == Some(true) {
        solid = solid.mirror(V3::ZERO, V3::X);
    }
    if let Some(lift) = seat_lift {
        solid = solid.translate(V3::Z * lift);
    }
    if let Some(rotations) = row["rotations"].as_array() {
        for turn in rotations {
            let degrees = f(turn, "degrees")?;
            if degrees != 0. {
                solid = solid.rotate(V3::ZERO, p(&turn["axis"])?, degrees);
            }
        }
    }
    if row["translation"].is_array() {
        let translation = p(&row["translation"])?;
        if translation != V3::ZERO {
            solid = solid.translate(translation);
        }
    }
    if row["transform"].is_object() {
        let t = &row["transform"];
        solid = solid.transformed(&Affine::from_columns(
            p(&t["columns"][0])?,
            p(&t["columns"][1])?,
            p(&t["columns"][2])?,
            p(&t["translation"])?,
        ));
    }
    if let Some(rotations) = row["after_rotations"].as_array() {
        for turn in rotations {
            let degrees = f(turn, "degrees")?;
            if degrees != 0. {
                solid = solid.rotate(V3::ZERO, p(&turn["axis"])?, degrees);
            }
        }
    }
    if row["after_translation"].is_array() {
        let translation = p(&row["after_translation"])?;
        if translation != V3::ZERO {
            solid = solid.translate(translation);
        }
    }
    Ok(solid)
}

fn clamp(dim: &Value, row: &Value) -> Result<Solid> {
    let xy = &row["xy"];
    let seat = f(row, "seat")?;
    let at = v3(
        xy[0].as_f64().context("clamp x")?,
        xy[1].as_f64().context("clamp y")?,
        seat,
    );
    let direction = f(row, "direction")?;
    let shaft = cylinder(
        f(dim, "shaft_radius")?,
        f(dim, "shaft_length")?,
        at,
        V3::Z * direction,
    )?;
    let head_height = f(dim, "head_height")?;
    let head = cylinder(f(dim, "head_radius")?, head_height, at, V3::Z * -direction)?;
    let (h0, h1) = if direction < 0. {
        (seat, seat + head_height)
    } else {
        (seat - head_height, seat)
    };
    let depth = f(dim, "socket_depth")?;
    let overrun = f(dim, "tool_overrun")?;
    let (s0, s1) = if direction < 0. {
        (h1 - depth, h1 + overrun)
    } else {
        (h0 - overrun, h0 + depth)
    };
    let radius = f(dim, "socket_af")? / cos(std::f64::consts::PI / 6.) / 2.;
    let points: Vec<V2> = (0..6)
        .map(|i| {
            let angle = radians(i as f64 * 60.);
            v2(radius * cos(angle), radius * sin(angle))
        })
        .collect();
    let socket = Plane::XY
        .at(v3(at.x, at.y, s0))
        .extrude(&Profile::polygon(&points), s1 - s0)?;
    shaft.union(&head)?.cut(&socket)
}

fn tube(dim: &Value, bond: &Value) -> Result<Solid> {
    let z = f(dim, "carbonator_bottom_z")?;
    let height = f(dim, "carbonator_height")?;
    let outer = cylinder(f(dim, "TUBE_OD")? / 2., height, V3::Z * z, V3::Z)?;
    let bore = cylinder(
        f(dim, "TUBE_ID")? / 2.,
        height + 2.,
        V3::Z * (z - 1.),
        V3::Z,
    )?;
    let outward = p(&bond["contact_outward"])?;
    let tap = cylinder(
        f(bond, "THREAD_DIAMETER")? / 2.,
        f(bond, "TUBE_WALL")? + 2.,
        p(&bond["contact_point_mm"])? + outward,
        -outward,
    )?;
    outer.cut(&bore)?.cut(&tap)
}

fn plate(dim: &Value, side: &str) -> Result<Solid> {
    let z = &dim[if side == "bottom" {
        "bottom_plate_z"
    } else {
        "top_plate_z"
    }];
    let z0 = z[0].as_f64().context("plate base")?;
    let z1 = z[1].as_f64().context("plate top")?;
    let height = f(dim, "PLATE_T")?;
    let mut plate = cylinder(f(dim, "PLATE_D")? / 2., height, V3::Z * z0, V3::Z)?;
    for port in array(&dim["ports"])? {
        if port["plate"].as_str() == Some(side) {
            plate = plate.cut(&cylinder(
                f(dim, "PORT_TAP_D")? / 2.,
                height + 2.,
                v3(0., f(port, "y")?, z0 - 1.),
                V3::Z,
            )?)?;
        }
    }
    let inside = if side == "bottom" { z1 } else { z0 };
    let direction = if side == "bottom" { -V3::Z } else { V3::Z };
    let xy = &dim["ROD_XY"];
    plate.cut(&cylinder(
        f(dim, "register_diameter")? / 2.,
        f(dim, "REGISTER_DEPTH")?,
        v3(
            xy[0].as_f64().context("rod x")?,
            xy[1].as_f64().context("rod y")?,
            inside,
        ),
        direction,
    )?)
}

fn carbonator_rod(dim: &Value, stop: bool) -> Result<Solid> {
    let xy = &dim["ROD_XY"];
    let ceiling = dim["interior_z"][1].as_f64().context("interior ceiling")?;
    let (z0, z1) = if stop {
        (ceiling - f(dim, "UPPER_STOP_H")?, ceiling)
    } else {
        (
            dim["interior_z"][0].as_f64().context("interior floor")? - f(dim, "REGISTER_DEPTH")?,
            ceiling + f(dim, "REGISTER_DEPTH")?,
        )
    };
    let at = v3(
        xy[0].as_f64().context("rod x")?,
        xy[1].as_f64().context("rod y")?,
        z0,
    );
    if stop {
        let outer = cylinder(f(dim, "UPPER_STOP_D")? / 2., z1 - z0, at, V3::Z)?;
        outer.cut(&cylinder(
            f(dim, "UPPER_STOP_BORE")? / 2.,
            z1 - z0 + 2.,
            at - V3::Z,
            V3::Z,
        )?)
    } else {
        cylinder(f(dim, "ROD_D")? / 2., z1 - z0, at, V3::Z)
    }
}

fn earth_hardware(dim: &Value, washer: bool) -> Result<Solid> {
    let at = p(&dim["screw_underhead_mm"])?;
    let axis = p(&dim["screw_axis"])?;
    if washer {
        let h = f(dim, "WASHER_THICKNESS")?;
        cylinder(f(dim, "WASHER_DIAMETER")? / 2., h, at, axis)?.cut(&cylinder(
            f(dim, "WASHER_BORE")? / 2.,
            h + 2.,
            at - axis,
            axis,
        )?)
    } else {
        let head_height = f(dim, "SCREW_HEAD_HEIGHT")?;
        let head = Plane::XY
            .cylinder(f(dim, "SCREW_HEAD_DIAMETER")? / 2., head_height)?
            .translate(-V3::Z * head_height);
        let shaft = Plane::XY.cylinder(f(dim, "SCREW_DIAMETER")? / 2., f(dim, "SCREW_LENGTH")?)?;
        Ok(fittings::orient(&head.union(&shaft)?, axis).translate(at))
    }
}

fn grommet(dim: &Value, row: &Value) -> Result<Solid> {
    let s = &row["specification"];
    let z0 = f(row, "z")?;
    let z1 = z0 + f(dim, "plate_thickness")?;
    let xy = &row["xy"];
    let at = v3(
        xy[0].as_f64().context("grip x")?,
        xy[1].as_f64().context("grip y")?,
        z0,
    );
    let waist = f(s, "waist_d")? / 2.;
    let flare = f(s, "flare_d")? / 2.;
    let depth = flare - waist;
    let spool = cylinder(waist, z1 - z0, at, V3::Z)?
        .union(&Solid::cone(at, V3::Z, flare, waist, depth)?)?
        .union(&Solid::cone(
            at + V3::Z * (z1 - depth - z0),
            V3::Z,
            waist,
            flare,
            depth,
        )?)?;
    let radius = f(s, "bore_d")? / 2.;
    let lead = f(s, "lead_d")? / 2.;
    let h = f(s, "lead_h")?;
    let opening = cylinder(radius, z1 - z0 + 0.2, at - V3::Z * 0.1, V3::Z)?
        .union(&Solid::cone(at, V3::Z, lead, radius, h)?)?
        .union(&Solid::cone(
            at + V3::Z * (z1 - h - z0),
            V3::Z,
            radius,
            lead,
            h,
        )?)?;
    spool.cut(&opening)
}

fn coil(dim: &Value) -> Result<Solid> {
    let radius = f(dim, "WIND_R")?;
    let angle = radians(f(dim, "AZ_IN")?);
    let start = v3(
        radius * cos(angle),
        radius * sin(angle),
        f(dim, "evap_tail_low_z")?,
    );
    let pitch = f(dim, "PITCH")?;
    let tangent = v3(
        -sin(angle) * radius,
        cos(angle) * radius,
        pitch / (2. * std::f64::consts::PI),
    )
    .unit();
    let plane = Plane::new(start, V3::Z, tangent)?;
    let region = Profile::circle(V2::ZERO, f(dim, "TUBE_R")?).place(&plane);
    Solid::helix_sweep_with_tolerance(
        &region,
        start,
        V3::Z * start.z,
        V3::Z,
        pitch,
        f(dim, "TOTAL_WRAPS")?,
        f(dim, "path_chord_mm")?,
    )
}

fn coil_tail(dim: &Value, row: &Value) -> Result<Solid> {
    let segments = array(&row["segments"])?;
    let first = segments.first().context("coil tail has no segments")?;
    let start = p(&first["start"])?;
    let tangent = p(&first["tangent"])?;
    let mut path = Path::new(start);
    for segment in segments {
        let end = p(&segment["end"])?;
        match segment["kind"].as_str() {
            Some("straight") => path = path.line_to(end),
            Some("bend") => {
                let angle = radians(f(segment, "angle")?) / 2.;
                let radius = f(segment, "radius")?;
                let mid = p(&segment["start"])?
                    + p(&segment["tangent"])? * (radius * sin(angle))
                    + p(&segment["normal"])? * (radius * (1. - cos(angle)));
                path = path.arc_through(mid, end)?;
            }
            _ => bail!("unknown coil-tail segment"),
        }
    }
    let plane = Plane::new(start, V3::Z, tangent)?;
    let region = Profile::circle(V2::ZERO, f(dim, "TUBE_R")?).place(&plane);
    Solid::sweep_with_tolerance(&region, &path, f(dim, "path_chord_mm")?)
}

pub fn build(numbers: &Numbers) -> Result<Vec<Piece>> {
    let mut pieces: Vec<Piece> = vec![];
    let carbonator = numbers.get("carbonator")?;
    for row in array(numbers.get("bodies")?)? {
        let name = row["name"].as_str().context("body name")?;
        let kind = row["kind"].as_str().context("body kind")?;
        let solids = match kind {
            "model" => {
                let read =
                    import::model(row["model"].as_str().context("explicit fine-model path")?)?;
                let lift = row["seat_top"].as_f64().map(|top| {
                    top - read
                        .iter()
                        .map(|b| b.solid.bounds().max.z)
                        .fold(f64::NEG_INFINITY, f64::max)
                });
                read.into_iter()
                    .map(|b| placed(b.solid, row, lift))
                    .collect::<Result<Vec<_>>>()?
            }
            "cap-clamp" => vec![clamp(numbers.get("cap_clamp")?, row)?],
            "carbonator-tube" => vec![tube(carbonator, numbers.get("bond")?)?],
            "endcap" => vec![plate(
                carbonator,
                row["side"].as_str().context("plate side")?,
            )?],
            "carbonator-rod" => vec![carbonator_rod(carbonator, false)?],
            "carbonator-stop" => vec![carbonator_rod(carbonator, true)?],
            "carbonator-earth-screw" => vec![earth_hardware(numbers.get("bond")?, false)?],
            "carbonator-earth-lockwasher" => vec![earth_hardware(numbers.get("bond")?, true)?],
            "street-elbow" => vec![fittings::street_elbow(numbers.get("fittings")?, row)?],
            "male-elbow" => vec![fittings::male_elbow(numbers.get("fittings")?, row)?],
            "grommet" => vec![grommet(numbers.get("ports")?, row)?],
            "air-tube" => {
                let dim = numbers.get("ports")?;
                let xy = &row["xy"];
                let at = v3(
                    xy[0].as_f64().context("air x")?,
                    xy[1].as_f64().context("air y")?,
                    f(row, "z0")?,
                );
                let height = f(row, "z1")? - at.z;
                vec![
                    cylinder(f(dim, "air_tube_od")? / 2., height, at, V3::Z)?.cut(&cylinder(
                        f(dim, "air_tube_id")? / 2.,
                        height + 0.2,
                        at - V3::Z * 0.1,
                        V3::Z,
                    )?)?,
                ]
            }
            "coil" => vec![coil(numbers.get("coil")?)?],
            "coil-tail" => vec![coil_tail(numbers.get("coil")?, row)?],
            "jet" => {
                let dim = numbers.get("jet")?;
                let at = p(&row["at"])?;
                let axis = p(&row["axis"])?;
                let height = f(dim, "JET_CAP_T")?;
                vec![
                    cylinder(f(dim, "JET_CAP_D")? / 2., height, at, axis)?.cut(&cylinder(
                        f(dim, "JET_PASSAGE_D")? / 2.,
                        height,
                        at,
                        axis,
                    )?)?,
                ]
            }
            "collet" => vec![fittings::jg_connector(
                numbers.get("collet")?,
                p(&row["at"])?,
                p(&row["axis"])?,
            )?],
            "float" => {
                fittings::float_capsule(numbers.get("float")?, p(&row["at"])?, V3::Z)?.into()
            }
            "reed" => vec![fittings::reed(
                numbers.get("fittings")?,
                p(&row["at"])?,
                V3::Z,
            )?],
            "probe" => vec![fittings::to92(
                numbers.get("fittings")?,
                p(&row["at"])?,
                V3::Z,
            )?],
            "prv" => vec![fittings::sv125(
                numbers.get("fittings")?,
                p(&row["at"])?,
                p(&row["axis"])?,
            )?],
            "reservoir-rod" => {
                let reservoir = pieces
                    .iter()
                    .find(|b| Some(b.name.as_str()) == row["reservoir"].as_str())
                    .context("rod reservoir has not been placed")?;
                let bounds = reservoir.fine.bounds();
                let x = f(row, "x")?;
                let y = f(row, "y")?;
                let radius = f(carbonator, "ROD_D")? / 2.;
                let probe = cylinder(
                    radius,
                    (bounds.min.z + bounds.max.z) / 2. - bounds.min.z + 1.,
                    v3(x, y, bounds.min.z - 1.),
                    V3::Z,
                )?;
                let hit = reservoir.fine.intersect(&probe)?;
                let z = if hit.volume() > 1e-9 {
                    hit.bounds().max.z
                } else {
                    bounds.min.z
                };
                vec![cylinder(
                    radius,
                    numbers.get("internals")?["RES_ROD_LEN"]
                        .as_f64()
                        .context("rod length")?,
                    v3(x, y, z),
                    V3::Z,
                )?]
            }
            _ => bail!("unknown core body kind {kind}"),
        };
        let color = Some(p(&row["color"])?.to_array());
        let printed_presentation = row["printed_presentation"].as_bool().unwrap_or(false);
        pieces.extend(solids.into_iter().map(|fine| Piece {
            name: name.to_owned(),
            color,
            fine,
            printed_presentation,
        }));
    }
    Ok(pieces)
}
