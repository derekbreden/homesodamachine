//! Catalog stand-ins from `_fittings.py`'s dimensions and source-frame placements.
use anyhow::{Context, Result};
use hsm_kernel::math::{acos, cos, degrees, radians, sin};
use hsm_kernel::*;
use serde_json::Value;

pub fn number(row: &Value, key: &str) -> Result<f64> {
    row[key]
        .as_f64()
        .with_context(|| format!("fitting number {key}"))
}

pub fn point(value: &Value) -> Result<V3> {
    Ok(v3(
        value[0].as_f64().context("point x")?,
        value[1].as_f64().context("point y")?,
        value[2].as_f64().context("point z")?,
    ))
}

/// The native minimal rotation from +Z, including its fixed +X half-turn at -Z.
pub fn orient(solid: &Solid, axis: V3) -> Solid {
    let axis = axis.unit();
    let z = v3(0., 0., 1.);
    let dot = z.dot(axis).clamp(-1., 1.);
    if dot > 1. - 1e-12 {
        solid.clone()
    } else if dot < -1. + 1e-12 {
        solid.rotate(V3::ZERO, v3(1., 0., 0.), 180.)
    } else {
        solid.rotate(V3::ZERO, z.cross(axis), degrees(acos(dot)))
    }
}

pub fn cylinder(radius: f64, height: f64, at: V3, axis: V3) -> Result<Solid> {
    Ok(orient(&Plane::XY.cylinder(radius, height)?, axis).translate(at))
}

fn hex(across_flats: f64, height: f64) -> Result<Solid> {
    hex_radius(across_flats / 3_f64.sqrt(), height)
}

fn hex_radius(radius: f64, height: f64) -> Result<Solid> {
    let points: Vec<V2> = (0..6)
        .map(|i| {
            let angle = radians(60. * i as f64);
            v2(radius * cos(angle), radius * sin(angle))
        })
        .collect();
    Plane::XY.extrude(&Profile::polygon(&points), height)
}

/// Cardinal construction frame, retaining each native hex profile's independent clocking.
struct ElbowFrame {
    x: V3,
    y: V3,
    z: V3,
    placement: Affine,
}

impl ElbowFrame {
    fn new(row: &Value) -> Result<Self> {
        let x = point(&row["out"])?.unit();
        let z = point(&row["up"])?.unit();
        let y = z.cross(x).unit();
        Ok(Self {
            x,
            y,
            z,
            placement: Affine::from_columns(x, y, z, point(&row["corner"])?),
        })
    }

    fn local(&self, vector: V3) -> V3 {
        v3(vector.dot(self.x), vector.dot(self.y), vector.dot(self.z))
    }

    fn hex(
        &self,
        across_flats: f64,
        height: f64,
        native_axis: V3,
        local_axis: V3,
    ) -> Result<Solid> {
        let dot = V3::Z.dot(native_axis).clamp(-1., 1.);
        let native_x = if dot > 1. - 1e-12 {
            V3::X
        } else if dot < -1. + 1e-12 {
            V3::X
        } else {
            Affine::rotation(V3::ZERO, V3::Z.cross(native_axis), degrees(acos(dot))).vector(V3::X)
        };
        let radius = across_flats / 3_f64.sqrt();
        let points: Vec<V2> = (0..6)
            .map(|i| {
                let a = radians(i as f64 * 60.);
                v2(radius * cos(a), radius * sin(a))
            })
            .collect();
        Plane::new(V3::ZERO, self.local(native_x), local_axis)?
            .extrude(&Profile::polygon(&points), height)
    }
}

/// Extra circle samples at the intersecting street-elbow bores; the analytic curve is unchanged.
fn street_cylinder(radius: f64, height: f64, at: V3, axis: V3) -> Result<Solid> {
    let (curve_axis, x, y) = hsm_kernel::rule::axis_frame(axis);
    let n = hsm_kernel::rule::ring_count(radius) * 2;
    let points = (0..n)
        .map(|i| {
            let angle = std::f64::consts::TAU * i as f64 / n as f64;
            at + (x * cos(angle) + y * sin(angle)) * radius
        })
        .collect();
    let region = Region {
        loops: vec![hsm_kernel::profile::RLoop {
            pts: points,
            seg: vec![0; n],
        }],
        curves: vec![Curve::Circle {
            c: at,
            axis: curve_axis,
            r: radius,
        }],
    };
    Solid::extrude(&region, axis, axis * height)
}

pub fn street_elbow(dim: &Value, row: &Value) -> Result<Solid> {
    let frame = ElbowFrame::new(row)?;
    let c = V3::ZERO;
    let up = V3::Z;
    let out = V3::X;
    let up_leg = number(row, "up_leg")?;
    let out_leg = number(row, "out_leg")?;
    let male_len = number(row, "male_len")?;
    let af = number(dim, "ELBOW_HEX_AF")?;
    let leg_up = frame.hex(af, up_leg, frame.z, up)?;
    let leg_out = frame.hex(af, out_leg, frame.x, out)?;
    let stub = street_cylinder(number(dim, "ELBOW_MALE_R")?, male_len, c + up * up_leg, up)?;
    let solid = leg_up.union(&leg_out)?.union(&stub)?;
    let radius = number(dim, "ELBOW_BORE")? / 2.;
    let bore_up = street_cylinder(radius, up_leg + male_len + 1., c, up)?;
    let bore_out = street_cylinder(radius, out_leg + 1., c, out)?;
    let depth = number(dim, "SOCKET_DEPTH")?.min(out_leg);
    let socket = street_cylinder(
        number(dim, "SOCKET_R")?,
        depth,
        c + out * (out_leg - depth),
        out,
    )?;
    Ok(solid
        .cut(&bore_up)?
        .cut(&bore_out)?
        .cut(&socket)?
        .transformed(&frame.placement))
}

pub fn male_elbow(dim: &Value, row: &Value) -> Result<Solid> {
    let frame = ElbowFrame::new(row)?;
    let c = V3::ZERO;
    let up = V3::Z;
    let out = V3::X;
    let radius = number(dim, "MALE_ELBOW_BODY_D")? / 2.;
    let reach = number(dim, "MALE_ELBOW_MOUTH_REACH")?;
    let axis_reach = number(dim, "MALE_ELBOW_AXIS_REACH")?;
    let thread_length = number(dim, "MALE_ELBOW_THREAD")?;
    let socket_body = cylinder(radius, reach, c, out)?;
    let post = cylinder(
        number(dim, "MALE_ELBOW_POST_W")? / 2.,
        radius + axis_reach,
        c - up * radius,
        up,
    )?;
    let thread = cylinder(
        number(dim, "ELBOW_MALE_R")?,
        thread_length,
        c + up * axis_reach,
        up,
    )?;
    let solid = socket_body.union(&post)?.union(&thread)?;
    let insertion = number(dim, "MALE_ELBOW_INSERTION")?;
    let socket = cylinder(
        number(dim, "MALE_ELBOW_TUBE_OD")? / 2.,
        insertion,
        c + out * (reach - insertion),
        out,
    )?;
    let bore_radius = number(dim, "MALE_ELBOW_FLOW_BORE")? / 2.;
    let bore_out = cylinder(bore_radius, reach, c, out)?;
    let bore_up = cylinder(bore_radius, axis_reach + thread_length + 1., c, up)?;
    Ok(solid
        .cut(&socket)?
        .cut(&bore_out)?
        .cut(&bore_up)?
        .transformed(&frame.placement))
}

pub fn sv125(dim: &Value, at: V3, axis: V3) -> Result<Solid> {
    let axis = axis.unit();
    let length = number(dim, "PRV_MALE_LEN")?;
    let stub = cylinder(
        number(dim, "ELBOW_MALE_R")?,
        length,
        at - axis * length,
        axis,
    )?;
    let hex_height = number(dim, "PRV_HEX_H")?;
    let base = orient(&hex(number(dim, "PRV_HEX_AF")?, hex_height)?, axis).translate(at);
    let cap = cylinder(
        number(dim, "PRV_CAP_R")?,
        number(dim, "PRV_CAP_H")?,
        at + axis * hex_height,
        axis,
    )?;
    stub.union(&base)?.union(&cap)
}

/// The body and magnet remain separate fine-model entries under their shared child name.
pub fn float_capsule(dim: &Value, at: V3, axis: V3) -> Result<[Solid; 2]> {
    let axis = axis.unit();
    let height = number(dim, "height")?;
    let base = at - axis * (height / 2.);
    let outer = cylinder(number(dim, "diameter")? / 2., height, base, axis)?;
    let bore = cylinder(
        number(dim, "bore_diameter")? / 2.,
        height + 2.,
        base - axis,
        axis,
    )?;
    let seat = at + axis * (number(dim, "magnet_seat")? - height / 2.);
    let annulus = |outside: &str, inside: &str, thickness: &str| -> Result<Solid> {
        let h = number(dim, thickness)?;
        let ring = Plane::XY
            .cylinder(number(dim, outside)? / 2., h)?
            .cut(&Plane::XY.cylinder(number(dim, inside)? / 2., h)?)?;
        Ok(orient(&ring, axis).translate(seat))
    };
    let pocket = annulus("pocket_od", "pocket_id", "pocket_depth")?;
    let magnet = annulus("magnet_od", "magnet_id", "magnet_thickness")?;
    Ok([outer.cut(&bore)?.cut(&pocket)?, magnet])
}

pub fn reed(dim: &Value, at: V3, axis: V3) -> Result<Solid> {
    let axis = axis.unit();
    let height = number(dim, "REED_GLASS_LEN")?;
    cylinder(
        number(dim, "REED_GLASS_R")?,
        height,
        at - axis * (height / 2.),
        axis,
    )
}

pub fn to92(dim: &Value, at: V3, axis: V3) -> Result<Solid> {
    let axis = axis.unit();
    let width = number(dim, "TO92_W")?;
    let height = number(dim, "TO92_H")?;
    let outline = Profile::new(Loop::rounded_rect(
        v2(0., 0.),
        width,
        width,
        number(dim, "TO92_CORNER_R")?,
    )?);
    let body = Plane::XY.extrude(&outline, height)?;
    Ok(orient(&body, axis).translate(at - axis * (height / 2.)))
}

pub fn stand_x_along(solid: &Solid, at: V3, axis: V3) -> Solid {
    let axis = axis.unit();
    let x = v3(1., 0., 0.);
    let dot = x.dot(axis).clamp(-1., 1.);
    let turned = if dot > 1. - 1e-12 {
        solid.clone()
    } else if dot < -1. + 1e-12 {
        solid.rotate(V3::ZERO, v3(0., 0., 1.), 180.)
    } else {
        solid.rotate(V3::ZERO, x.cross(axis), degrees(acos(dot)))
    };
    turned.translate(at)
}

pub fn jg_connector(dim: &Value, at: V3, axis: V3) -> Result<Solid> {
    let collet_length = number(dim, "COLLET_LENGTH")?;
    let hex_length = number(dim, "HEX_LENGTH")?;
    let collet = Plane::XY.cylinder(number(dim, "COLLET_D")? / 2., collet_length)?;
    let wrench = hex_radius(number(dim, "HEX_ACROSS_CORNERS")? / 2., hex_length)?.translate(v3(
        0.,
        0.,
        collet_length,
    ));
    let shank = Plane::XY
        .cylinder(number(dim, "SHANK_D")? / 2., number(dim, "SHANK_LENGTH")?)?
        .translate(v3(0., 0., collet_length + hex_length));
    let body = collet
        .union(&wrench)?
        .union(&shank)?
        .rotate(V3::ZERO, v3(0., 1., 0.), 90.);
    Ok(stand_x_along(&body, at, axis))
}
