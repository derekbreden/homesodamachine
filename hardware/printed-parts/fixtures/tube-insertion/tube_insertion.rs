//! The manual tube insertion fixture builds its printable solids and named bench assembly in Rust.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Body, Face, Solid, Surface, V3, import, v3};
use serde::Serialize;
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::path::Path;

#[path = "numbers.rs"]
pub mod numbers;
use numbers::*;
pub const DIRECTORY: &str = "hardware/printed-parts/fixtures/tube-insertion";
pub const DONOR: &str =
    "hardware/reference/touch-flo-faucet/westbrass-reference/westbrass-reference.step.mesh";
pub const DONOR_DATUMS: &str = "hardware/reference/touch-flo-faucet/westbrass-reference/numbers.rs";

#[derive(Clone)]
pub struct Component {
    pub name: String,
    pub color: [f64; 3],
    pub solid: Solid,
}
fn linear(rgb: [f64; 3]) -> [f64; 3] {
    rgb.map(|v| {
        if v <= 0.04045 {
            v / 12.92
        } else {
            ((v + 0.055) / 1.055).powf(2.4)
        }
    })
}
pub fn rigid_color() -> [f64; 3] {
    linear([0.16, 0.18, 0.19])
}
pub fn tpu_color() -> [f64; 3] {
    linear([0.11, 0.12, 0.13])
}
pub fn steel_color() -> [f64; 3] {
    linear([0.67, 0.69, 0.71])
}
pub fn block(x0: f64, x1: f64, y0: f64, y1: f64, z0: f64, z1: f64) -> Solid {
    Solid::cuboid(v3(x0, y0, z0), v3(x1, y1, z1))
}
pub fn cylinder_x(x0: f64, x1: f64, y: f64, z: f64, r: f64) -> Result<Solid> {
    Solid::cylinder(v3(x0, y, z), V3::X, r, x1 - x0)
}
pub fn vertical_hole(x: f64, y: f64, z0: f64, z1: f64, d: f64) -> Result<Solid> {
    Solid::cylinder(v3(x, y, z0), V3::Z, d / 2., z1 - z0)
}
fn countersink(shape: &Solid, x: f64, y: f64, z: f64) -> Result<Solid> {
    shape.cut(&Solid::cone(
        v3(x, y, z),
        V3::Z,
        M5_CS_HEAD_D / 2.,
        m5_clearance() / 2.,
        countersink_height(),
    )?)
}

pub fn build_base() -> Result<Solid> {
    let mut base = block(BASE_X0, BASE_X1, BASE_Y0, BASE_Y1, 0., BASE_H);
    let thrust = block(
        THRUST_WALL_X0,
        THRUST_WALL_X1,
        -THRUST_WALL_Y_HALF,
        THRUST_WALL_Y_HALF,
        0.,
        THRUST_WALL_Z1,
    )
    .cut(
        &cylinder_x(
            THRUST_WALL_X0 - 1.,
            THRUST_WALL_X1 + 1.,
            0.,
            DONOR_AXIS_Z,
            SHANK_SLOT_D / 2.,
        )?
        .union(&block(
            THRUST_WALL_X0 - 1.,
            THRUST_WALL_X1 + 1.,
            -SHANK_SLOT_D / 2.,
            SHANK_SLOT_D / 2.,
            DONOR_AXIS_Z,
            THRUST_WALL_Z1 + 1.,
        ))?,
    )?;
    let nest = block(0., NEST_LENGTH, -19., 19., BASE_H, DONOR_AXIS_Z)
        .cut(&cylinder_x(
            -1.,
            NEST_LENGTH + 1.,
            0.,
            DONOR_AXIS_Z,
            DONOR_NEST_R,
        )?)?
        .union(&block(
            0.,
            NEST_LENGTH,
            -8.,
            8.,
            BASE_H,
            DONOR_AXIS_Z - DONOR_BODY_OD / 2.,
        ))?;
    base = base.union(&thrust)?.union(&nest)?.union(&block(
        CLOCKING_PAD_X0,
        CLOCKING_PAD_X1,
        -CLOCKING_PAD_HALF_WIDTH,
        CLOCKING_PAD_HALF_WIDTH,
        BASE_H,
        CLOCKING_PAD_Z1,
    ))?;
    for side in [-1., 1.] {
        let y = TUBE_Y + side * (CARRIER_HALF_WIDTH + RAIL_LATERAL_GAP);
        let edge = y + side * RAIL_WIDTH;
        base = base.union(&block(
            RAIL_X0,
            RAIL_X1,
            y.min(edge),
            y.max(edge),
            BASE_H,
            BASE_H + RAIL_HEIGHT,
        ))?;
    }
    for side in [-1., 1.] {
        let a = TUBE_Y + side * STOP_INNER_HALF_WIDTH;
        let b = TUBE_Y + side * STOP_OUTER_HALF_WIDTH;
        for (x0, x1) in [(STOP_X0, STOP_X1), (REAR_STOP_X0, REAR_STOP_X1)] {
            base = base.union(&block(x0, x1, a.min(b), a.max(b), BASE_H, STOP_Z1))?;
        }
    }
    for side in [-1., 1.] {
        let y = TUBE_Y + side * (SCREW_OFFSET_Y + FACTORY_PAD_ENVELOPE_D / 2. + 1.5);
        base = base.cut(&block(
            THRUST_WALL_X0 - 0.1,
            THRUST_WALL_X0 + 0.3,
            y - 0.4,
            y + 0.4,
            TUBE_Z - 3.,
            TUBE_Z + 3.,
        ))?;
    }
    for (x, y) in [(12., 112.), (170., 112.)] {
        base = base.cut(&vertical_hole(x, y, -1., BASE_H + 1., 6.)?)?;
    }
    Ok(base)
}

pub fn build_carrier() -> Result<Solid> {
    let mut carrier = block(
        0.,
        CARRIER_LENGTH,
        -CARRIER_HALF_WIDTH,
        CARRIER_HALF_WIDTH,
        0.,
        CARRIER_FOOT_H,
    )
    .union(&block(
        CARRIER_JAW_LOCAL_X,
        CARRIER_JAW_LOCAL_X + CARRIER_SHELF_LENGTH,
        -JAW_CORE_WIDTH / 2.,
        JAW_CORE_WIDTH / 2.,
        0.,
        CARRIER_SHELF_H,
    ))?;
    for side in [-1., 1.] {
        let y = side * COUPLING_BOLT_Y;
        let x = CARRIER_JAW_LOCAL_X + COUPLING_BOLT_X;
        let toe = vertical_hole(x, y, 0., CARRIER_SHELF_H, 2. * COUPLING_TOE_R)?.union(&block(
            x,
            0.,
            y - COUPLING_TOE_R,
            y + COUPLING_TOE_R,
            0.,
            CARRIER_SHELF_H,
        ))?;
        carrier = carrier.union(&toe)?.cut(&vertical_hole(
            x,
            y,
            -1.,
            CARRIER_SHELF_H + COUPLING_KEY_H + 1.,
            m5_clearance(),
        )?)?;
        carrier = countersink(&carrier, x, y, 0.)?;
        let y = side * COUPLING_KEY_Y;
        carrier = carrier.union(&block(
            CARRIER_JAW_LOCAL_X + COUPLING_KEY_X0,
            CARRIER_JAW_LOCAL_X + COUPLING_KEY_X1,
            y - COUPLING_KEY_W / 2.,
            y + COUPLING_KEY_W / 2.,
            CARRIER_SHELF_H,
            CARRIER_SHELF_H + COUPLING_KEY_H,
        ))?;
    }
    for y in [-CLAMP_BOLT_Y, CLAMP_BOLT_Y] {
        carrier = carrier.cut(&vertical_hole(
            CARRIER_JAW_LOCAL_X + CARRIER_HEAD_RELIEF_X,
            y,
            -1.,
            CARRIER_SHELF_H + 1.,
            M5_HEAD_D + 1.4,
        )?)?;
    }
    Ok(carrier)
}
pub fn build_lower_jaw(coupling: bool) -> Result<Solid> {
    let mut jaw = block(
        0.,
        JAW_LENGTH,
        -JAW_CORE_WIDTH / 2.,
        JAW_CORE_WIDTH / 2.,
        -JAW_HALF_H,
        0.,
    )
    .union(&block(
        JAW_HANDLE_START_X,
        JAW_HANDLE_END_X,
        -JAW_HANDLE_WIDTH / 2.,
        JAW_HANDLE_WIDTH / 2.,
        -JAW_HALF_H,
        0.,
    ))?
    .cut(&block(
        LINER_X0 - JAW_LINER_AXIAL_CLEARANCE / 2.,
        LINER_X0 + LINER_LENGTH + JAW_LINER_AXIAL_CLEARANCE / 2.,
        -LINER_WIDTH / 2. - JAW_LINER_SIDE_CLEARANCE,
        LINER_WIDTH / 2. + JAW_LINER_SIDE_CLEARANCE,
        -LINER_POCKET_H,
        1.,
    ))?
    .cut(&cylinder_x(
        -1.,
        JAW_LENGTH + 1.,
        0.,
        0.,
        JAW_TUBE_CLEARANCE_D / 2.,
    )?)?;
    for y in [-CLAMP_BOLT_Y, CLAMP_BOLT_Y] {
        jaw = jaw.cut(&vertical_hole(
            CLAMP_BOLT_X,
            y,
            -JAW_HALF_H - 1.,
            1.,
            m5_clearance(),
        )?)?;
    }
    if coupling {
        for side in [-1., 1.] {
            let y = side * COUPLING_BOLT_Y;
            let key_y = side * COUPLING_KEY_Y;
            let a = y - side * M5_NUT_WIDTH / 2.;
            let b = side * (JAW_HANDLE_WIDTH / 2. + 1.);
            jaw = jaw
                .cut(&block(
                    COUPLING_KEY_X0 - COUPLING_KEY_CLEARANCE,
                    COUPLING_KEY_X1 + COUPLING_KEY_CLEARANCE,
                    key_y - COUPLING_KEY_W / 2. - COUPLING_KEY_CLEARANCE,
                    key_y + COUPLING_KEY_W / 2. + COUPLING_KEY_CLEARANCE,
                    -JAW_HALF_H - 1.,
                    -JAW_HALF_H + COUPLING_KEY_H + COUPLING_KEY_CLEARANCE,
                ))?
                .cut(&vertical_hole(
                    COUPLING_BOLT_X,
                    y,
                    -JAW_HALF_H - 1.,
                    1.,
                    m5_clearance(),
                )?)?
                .cut(&block(
                    COUPLING_BOLT_X - M5_NUT_WIDTH / 2.,
                    COUPLING_BOLT_X + M5_NUT_WIDTH / 2.,
                    a.min(b),
                    a.max(b),
                    COUPLING_NUT_Z0,
                    COUPLING_NUT_Z0 + M5_NUT_H,
                ))?;
        }
    }
    Ok(jaw)
}
pub fn build_upper_jaw() -> Result<Solid> {
    Ok(build_lower_jaw(false)?.mirror(V3::ZERO, V3::Z))
}
pub fn build_liner() -> Result<Solid> {
    block(
        0.,
        LINER_LENGTH,
        -LINER_WIDTH / 2.,
        LINER_WIDTH / 2.,
        0.,
        LINER_H,
    )
    .cut(&cylinder_x(
        -1.,
        LINER_LENGTH + 1.,
        0.,
        LINER_H,
        GRIP_BORE_D / 2.,
    )?)
}
pub fn build_cap_support_puck() -> Result<Solid> {
    block(
        -PUCK_SIZE / 2.,
        PUCK_SIZE / 2.,
        -PUCK_SIZE / 2.,
        PUCK_SIZE / 2.,
        0.,
        PUCK_H,
    )
    .cut(&vertical_hole(0., 0., -1., PUCK_H + 1., PUCK_HOLE_D)?)?
    .cut(&vertical_hole(
        0.,
        0.,
        PUCK_H - PUCK_CAP_RECESS_H,
        PUCK_H + 1.,
        PUCK_CAP_RECESS_D,
    )?)
}

pub fn print_pose(name: &str, solid: &Solid) -> Solid {
    match name {
        "lower-jaw" => solid.translate(v3(0., 0., JAW_HALF_H)),
        "upper-jaw" => solid
            .rotate(V3::ZERO, V3::X, 180.)
            .translate(v3(0., 0., JAW_HALF_H)),
        "liner" => solid
            .rotate(V3::ZERO, V3::Y, -90.)
            .translate(v3(LINER_H, 0., 0.)),
        _ => solid.clone(),
    }
}
fn source_pose(name: &str, solid: &Solid) -> Solid {
    match name {
        "lower-jaw" => solid.translate(v3(0., 0., -JAW_HALF_H)),
        "upper-jaw" => solid
            .translate(v3(0., 0., -JAW_HALF_H))
            .rotate(V3::ZERO, V3::X, 180.),
        "liner" => solid
            .translate(v3(-LINER_H, 0., 0.))
            .rotate(V3::ZERO, V3::Y, 90.),
        _ => solid.clone(),
    }
}
pub fn build_parts(print_frame: bool) -> Result<BTreeMap<String, Solid>> {
    let mut parts: BTreeMap<String, Solid> = BTreeMap::from([
        ("base".into(), build_base()?),
        ("carrier".into(), build_carrier()?),
        ("lower-jaw".into(), build_lower_jaw(true)?),
        ("upper-jaw".into(), build_upper_jaw()?),
        ("liner".into(), build_liner()?),
        ("cap-support-puck".into(), build_cap_support_puck()?),
    ]);
    if print_frame {
        for (name, solid) in &mut parts {
            *solid = print_pose(name, solid);
        }
    }
    Ok(parts)
}

pub fn stl(path: &Path) -> Result<Solid> {
    let bytes = std::fs::read(path)?;
    ensure!(
        bytes.len() >= 84,
        "truncated fixture STL {}",
        path.display()
    );
    let count = u32::from_le_bytes(bytes[80..84].try_into()?) as usize;
    ensure!(
        bytes.len() == 84 + count * 50,
        "expected binary fixture STL {}",
        path.display()
    );
    let mut points = Vec::with_capacity(count * 3);
    let mut triangles = Vec::with_capacity(count);
    for chunk in bytes[84..].chunks_exact(50) {
        let first = points.len() as u32;
        for point in chunk[12..48].chunks_exact(12) {
            let n = |i| f32::from_le_bytes(point[i..i + 4].try_into().unwrap()) as f64;
            points.push(v3(n(0), n(4), n(8)));
        }
        triangles.push([first, first + 1, first + 2]);
    }
    Solid::from_mesh(
        &points,
        &triangles,
        &vec![0; count],
        &[Face::new(
            Surface::Free { kind: "MESH" },
            "retained print",
            hsm_kernel::face::unknown_src(),
        )],
    )
}
pub fn retained_parts(root: &Path, print_frame: bool) -> Result<BTreeMap<String, Solid>> {
    let mut parts = BTreeMap::new();
    for name in [
        "base",
        "carrier",
        "lower-jaw",
        "upper-jaw",
        "liner",
        "cap-support-puck",
    ] {
        let source = root
            .join(DIRECTORY)
            .join(format!("tube-insertion-{name}.step.mesh"));
        let imported = import::payload(&source)?;
        let solid = Solid::union_all(
            &imported
                .into_iter()
                .map(|body| body.solid)
                .collect::<Vec<_>>(),
        )?;
        parts.insert(
            name.into(),
            if print_frame {
                solid
            } else {
                source_pose(name, &solid)
            },
        );
    }
    Ok(parts)
}
pub fn donor_shape(root: &Path) -> Result<Solid> {
    let parts = import::payload(root.join(DONOR))?;
    ensure!(!parts.is_empty(), "empty donor reference");
    Solid::union_all(&parts.into_iter().map(|p| p.solid).collect::<Vec<_>>()).map(|s| {
        s.rotate(V3::ZERO, V3::Y, 90.)
            .translate(v3(0., 0., DONOR_AXIS_Z))
    })
}
pub fn sleeve_on_tube_shape(depth: f64, stroke: f64) -> Result<Solid> {
    let x = DONOR_PORT_X - depth + stroke;
    let radius = (TUBE_OD * TUBE_OD + SLEEVE_OD * SLEEVE_OD - SLEEVE_ID * SLEEVE_ID).sqrt() / 2.;
    cylinder_x(x, x + SLEEVE_LENGTH, TUBE_Y, TUBE_Z, radius)?
        .cut(&cylinder_x(
            x - 1.,
            x + SLEEVE_CAP_H,
            TUBE_Y,
            TUBE_Z,
            SLEEVE_CAP_HOLE / 2.,
        )?)?
        .cut(&cylinder_x(
            x + SLEEVE_CAP_H,
            x + SLEEVE_LENGTH + 1.,
            TUBE_Y,
            TUBE_Z,
            TUBE_OD / 2.,
        )?)
}
pub fn tube_shape(depth: f64, stroke: f64, length: f64) -> Result<Solid> {
    let x = DONOR_PORT_X - depth + SLEEVE_CAP_H + stroke;
    cylinder_x(x, x + length, TUBE_Y, TUBE_Z, TUBE_OD / 2.)?.cut(&cylinder_x(
        x - 1.,
        x + length + 1.,
        TUBE_Y,
        TUBE_Z,
        TUBE_ID / 2.,
    )?)
}
pub fn bolt_shape(x: f64, y: f64, head_z: f64, length: f64) -> Result<Solid> {
    vertical_hole(x, y, head_z - M5_HEAD_H, head_z, 8.5)?.union(&vertical_hole(
        x,
        y,
        head_z,
        head_z + length,
        5.,
    )?)
}
pub fn countersunk_bolt_shape(x: f64, y: f64, top_z: f64, length: f64) -> Result<Solid> {
    let h = (9.8 - 5.) / 2.;
    Solid::cone(v3(x, y, top_z), V3::Z, 9.8 / 2., 5. / 2., h)?.union(&vertical_hole(
        x,
        y,
        top_z + h,
        top_z + length,
        5.,
    )?)
}
pub fn square_nut_shape(x: f64, y: f64, z: f64) -> Result<Solid> {
    block(x - 4., x + 4., y - 4., y + 4., z, z + 4.).cut(&vertical_hole(x, y, z - 1., z + 5., 5.)?)
}
pub fn washer_shape(x: f64, y: f64, z: f64) -> Result<Solid> {
    vertical_hole(x, y, z, z + 1.5, 25.)?.cut(&vertical_hole(x, y, z - 1., z + 3., 5.5)?)
}

#[derive(Serialize)]
pub struct Station {
    pub name: &'static str,
    pub side: i32,
    pub fixed_center_mm: [f64; 3],
    pub moving_center_mm: [f64; 3],
}
pub fn clamp_stations(stroke: f64) -> Vec<Station> {
    [(-1, "C1"), (1, "C2")]
        .into_iter()
        .map(|(side, name)| Station {
            name,
            side,
            fixed_center_mm: [
                THRUST_WALL_X0,
                TUBE_Y + side as f64 * SCREW_OFFSET_Y,
                TUBE_Z,
            ],
            moving_center_mm: [
                CLAMP_BACK_X + stroke,
                TUBE_Y + side as f64 * SCREW_OFFSET_Y,
                TUBE_Z,
            ],
        })
        .collect()
}
fn component(name: impl Into<String>, solid: Solid, color: [f64; 3]) -> Component {
    Component {
        name: name.into(),
        solid,
        color,
    }
}
pub fn build_clamp_reference(side: i32, stroke: f64) -> Result<Vec<Component>> {
    ensure!(side.abs() == 1, "clamp side is signed");
    let y = TUBE_Y + side as f64 * SCREW_OFFSET_Y;
    let rail = y + side as f64 * FACTORY_CLAMP_THROAT;
    let fixed = THRUST_WALL_X0;
    let moving = CLAMP_BACK_X + stroke;
    let mut out = Vec::new();
    let steel = steel_color();
    for (name, solid) in [
        (
            "fixed-pad-envelope",
            cylinder_x(
                fixed - FACTORY_PAD_SCHEMATIC_H,
                fixed,
                y,
                TUBE_Z,
                FACTORY_PAD_ENVELOPE_D / 2.,
            )?,
        ),
        (
            "moving-pad-envelope",
            cylinder_x(
                moving,
                moving + FACTORY_PAD_SCHEMATIC_H,
                y,
                TUBE_Z,
                FACTORY_PAD_ENVELOPE_D / 2.,
            )?,
        ),
        (
            "fixed-jaw-schematic",
            block(
                fixed - 16.,
                fixed - 4.,
                y.min(rail) - 4.,
                y.max(rail) + 4.,
                TUBE_Z - 6.,
                TUBE_Z + 6.,
            ),
        ),
        (
            "sliding-jaw-schematic",
            block(
                moving + 32.,
                moving + 44.,
                y.min(rail) - 4.,
                y.max(rail) + 4.,
                TUBE_Z - 6.,
                TUBE_Z + 6.,
            ),
        ),
        (
            "rail-schematic",
            block(
                fixed - 16.,
                212.,
                rail - 4.,
                rail + 4.,
                TUBE_Z - 6.,
                TUBE_Z + 6.,
            ),
        ),
        (
            "spindle-schematic",
            cylinder_x(moving + 4., moving + 47., y, TUBE_Z, 4.)?,
        ),
    ] {
        out.push(component(name, solid, steel));
    }
    out.push(component(
        "wood-handle-envelope",
        cylinder_x(
            moving + 47.,
            moving + 98.,
            y,
            TUBE_Z,
            FACTORY_HANDLE_ENVELOPE_D / 2.,
        )?,
        linear([0.61, 0.39, 0.18]),
    ));
    Ok(out)
}

pub fn assembly(
    root: &Path,
    parts: &BTreeMap<String, Solid>,
    stroke: f64,
    workpiece: bool,
    hardware: bool,
    clamps: bool,
    depth: f64,
) -> Result<Vec<Component>> {
    ensure!(
        (0. ..=PRESS_TRAVEL).contains(&stroke),
        "fixture stroke outside its stops"
    );
    let get = |name: &str| {
        parts
            .get(name)
            .cloned()
            .with_context(|| format!("fixture part {name}"))
    };
    let mut out = vec![
        component("base", get("base")?, rigid_color()),
        component(
            "carrier",
            get("carrier")?.translate(v3(CARRIER_FINAL_X + stroke, TUBE_Y, CARRIER_BOTTOM_Z)),
            rigid_color(),
        ),
    ];
    for name in ["lower-jaw", "upper-jaw"] {
        out.push(component(
            name,
            get(name)?.translate(v3(CLAMP_FINAL_X + stroke, TUBE_Y, TUBE_Z)),
            rigid_color(),
        ));
    }
    let x = CLAMP_FINAL_X + stroke + LINER_X0;
    out.push(component(
        "lower-liner",
        get("liner")?.translate(v3(x, TUBE_Y, TUBE_Z - LINER_POCKET_H)),
        tpu_color(),
    ));
    out.push(component(
        "upper-liner",
        get("liner")?
            .mirror(V3::ZERO, V3::Z)
            .translate(v3(x, TUBE_Y, TUBE_Z + LINER_POCKET_H)),
        tpu_color(),
    ));
    if workpiece {
        out.push(component(
            "touch-flo-donor",
            donor_shape(root)?,
            linear([0.58, 0.61, 0.64]),
        ));
        out.push(component(
            "lldpe-tube",
            tube_shape(
                depth,
                stroke,
                hsm_fabrication_guides::cuts::faucet()?.soda_faucet_cut,
            )?,
            linear([0.84, 0.90, 0.91]),
        ));
        out.push(component(
            "tpu-sealing-thimble",
            sleeve_on_tube_shape(depth, stroke)?,
            linear([0.04, 0.05, 0.06]),
        ));
    }
    if hardware {
        for (side, label) in [(-1., "front"), (1., "rear")] {
            let bx = CLAMP_FINAL_X + stroke + CLAMP_BOLT_X;
            let by = TUBE_Y + side * CLAMP_BOLT_Y;
            let wz = TUBE_Z + JAW_HALF_H;
            for (name, solid) in [
                (
                    format!("clamp-{label}-m5x50"),
                    bolt_shape(bx, by, TUBE_Z - JAW_HALF_H, 50.)?,
                ),
                (format!("clamp-{label}-washer"), washer_shape(bx, by, wz)?),
                (
                    format!("clamp-{label}-nut"),
                    square_nut_shape(bx, by, wz + 1.5)?,
                ),
                (
                    format!("carrier-{label}-m5x20"),
                    countersunk_bolt_shape(
                        CLAMP_FINAL_X + stroke + COUPLING_BOLT_X,
                        TUBE_Y + side * COUPLING_BOLT_Y,
                        CARRIER_BOTTOM_Z + M5_CS_HEAD_RECESS,
                        20.,
                    )?,
                ),
                (
                    format!("carrier-{label}-nut"),
                    square_nut_shape(
                        CLAMP_FINAL_X + stroke + COUPLING_BOLT_X,
                        TUBE_Y + side * COUPLING_BOLT_Y,
                        TUBE_Z + COUPLING_NUT_Z0,
                    )?,
                ),
            ] {
                out.push(component(name, solid, steel_color()));
            }
        }
    }
    if clamps {
        for (side, label) in [(-1, "C1"), (1, "C2")] {
            for mut item in build_clamp_reference(side, stroke)? {
                item.name = format!("{label}/{}", item.name);
                out.push(item);
            }
        }
    }
    Ok(out)
}

pub fn export(root: &Path, out: &Path) -> Result<Value> {
    let parts = build_parts(true)?;
    std::fs::create_dir_all(out)?;
    let mut rows = Vec::new();
    for (name, solid) in &parts {
        let color = if name == "liner" {
            tpu_color()
        } else {
            rigid_color()
        };
        let file = format!("tube-insertion-{name}");
        let result = hsm_kernel::part::write_part(
            out,
            &file,
            &[Body {
                name,
                color: Some(color),
                solid,
            }],
        )?;
        let bytes = hsm_kernel::write::stl_bytes(&[solid])?;
        crate::write(&out.join(format!("{file}-print.stl")), &bytes)?;
        let b = solid.bounds();
        rows.push(json!({"name":name,"letter":match name.as_str(){"base"=>"A","carrier"=>"B","lower-jaw"=>"D","upper-jaw"=>"E","liner"=>"F",_=>"G"},"quantity":if name=="liner"{2}else{1},"material":if name=="liner"{"TPU 85A"}else{"PET-GF15"},"filename":format!("{file}-print.stl"),"step":format!("{file}.step"),"print_rotation_x_degrees":0,"print_stl_is_pretransformed":true,"bbox":{"min_mm":b.min.to_array(),"max_mm":b.max.to_array(),"size_mm":b.size().to_array()},"support_strategy":match name.as_str(){"liner"=>"Solid end face on bed; tube axis vertical; repeated XY semicircle; automatic brim retained","lower-jaw"=>"Flat bed face; native automatic Tree review for functional side-loading nut pockets",_=>"Flat bed face with open functional holes and pockets; retain native automatic Tree decisions"},"generated":result}));
    }
    let placed = assembly(
        root,
        &build_parts(false)?,
        0.,
        true,
        true,
        true,
        DONOR_PORT_DEPTH_MIN,
    )?;
    let bodies: Vec<_> = placed
        .iter()
        .map(|p| Body {
            name: &p.name,
            color: Some(p.color),
            solid: &p.solid,
        })
        .collect();
    hsm_kernel::part::write_shown(out, "tube-insertion-assembly", &bodies)?;
    let mut manifest = json!({"schema":1,"frame":"X insertion axis from donor toward free tube; Z up from bed","parts":rows,
        "hardware":[
            {"name":"BESSEY GSCC2.506 6-inch screw clamp","letter":"C","quantity":2,"role":"C1 and C2 complete metal screw and reaction loops","owned":false,"prime_url":FACTORY_CLAMP_URL,"reference_model_scope":"Schematic only; ordinary setup checks actual contact feet and full screw travel"},
            {"name":"M5 x 50 socket-head screw","quantity":2,"role":"two jaw closure bolts","owned":true},
            {"name":"M5 x 20 DIN7991 countersunk screw","quantity":2,"role":"two lower-jaw to carrier coupling bolts","owned":true},
            {"name":"M5 x 0.8 square nut, 8 x 4 mm","quantity":4,"role":"two jaw closure nuts and two carrier coupling nuts","owned":true},
            {"name":"M5 fender washer, OD 25 mm","quantity":2,"role":"two jaw closure load spreaders","owned":true},
            {"name":"Owned 4-inch steel C-clamp","quantity":2,"role":"hold base stationary at bench edge for two-hand operation","owned":true}
        ],
        "factory_clamp_setup":{"stations":clamp_stations(PRESS_TRAVEL),"pad_envelope_diameter_mm":FACTORY_PAD_ENVELOPE_D,"initial_opening_mm":CLAMP_BACK_X+PRESS_TRAVEL-THRUST_WALL_X0,"final_opening_mm":CLAMP_BACK_X-THRUST_WALL_X0,"rated_capacity_mm":FACTORY_CLAMP_CAPACITY,"scope":"Opening dimension and adaptable flat bearing stations; schematic tool solids are not measured manufacturer CAD"}
    });
    manifest["source_sha256"] = json!(crate::sha(&root.join(DIRECTORY).join("tube_insertion.rs"))?);
    manifest["numbers_sha256"] = json!(crate::sha(&root.join(DIRECTORY).join("numbers.rs"))?);
    manifest["reference_source_sha256"] = json!({"hardware/printed-parts/faucet/tpu-o-ring/numbers.rs":crate::sha(&root.join("hardware/printed-parts/faucet/tpu-o-ring/numbers.rs"))?,(DONOR):crate::sha(&root.join(DONOR))?,(DONOR_DATUMS):crate::sha(&root.join(DONOR_DATUMS))?});
    crate::write_json(&out.join("parts.json"), &manifest)?;
    Ok(manifest)
}
