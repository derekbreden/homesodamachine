//! The gas module reference preserves its mounting datums and idealizes the sensor's stepped exterior.
use anyhow::Result;
use hsm_kernel::{Solid, V3, v3};
use hsm_sandbox::{material, out, show};

const PCB_X: f64 = 32.;
const PCB_Y: f64 = 20.;
const PCB_T: f64 = 1.6;
const CAN_D: f64 = 19.;
const CAN_H: f64 = 14.;
const PIN_LEN: f64 = 6.;
const PIN_SQ: f64 = 0.64;
const PIN_PITCH: f64 = 2.54;
const PIN_COUNT: usize = 4;
const PIN_ROW_INSET: f64 = 3.;

// The manufacturer's undimensioned exterior is proportioned within the retained module envelope.
const CAN_BASE_HEIGHT_FRACTION: f64 = 0.32;
const CAN_SHOULDER_HEIGHT_FRACTION: f64 = 0.10;
const CAN_SHOULDER_DIAMETER_FRACTION: f64 = 0.89;
const CAP_BOTTOM_DIAMETER_FRACTION: f64 = 0.84;
const CAP_TOP_DIAMETER_FRACTION: f64 = 0.66;

fn main() -> Result<()> {
    let dir = out()?;
    let pcb = Solid::cuboid(
        v3(-PCB_X / 2., -PCB_Y / 2., PIN_LEN),
        v3(PCB_X / 2., PCB_Y / 2., PIN_LEN + PCB_T),
    );
    let can_z = PIN_LEN + PCB_T;
    let radius = CAN_D / 2.;
    let base_height = CAN_H * CAN_BASE_HEIGHT_FRACTION;
    let shoulder_height = CAN_H * CAN_SHOULDER_HEIGHT_FRACTION;
    let cap_z = can_z + base_height + shoulder_height;
    let base = Solid::cylinder(v3(0., 0., can_z), V3::Z, radius, base_height)?
        .union(&Solid::cone(
            v3(0., 0., can_z + base_height),
            V3::Z,
            radius * CAN_SHOULDER_DIAMETER_FRACTION,
            radius * CAP_BOTTOM_DIAMETER_FRACTION,
            shoulder_height,
        )?)?;
    // Mesh weave and the sensing elements do not define a printed part's contact surfaces.
    let cap = Solid::cone(
        v3(0., 0., cap_z),
        V3::Z,
        radius * CAP_BOTTOM_DIAMETER_FRACTION,
        radius * CAP_TOP_DIAMETER_FRACTION,
        can_z + CAN_H - cap_z,
    )?;
    let pin_x = -PCB_X / 2. + PIN_ROW_INSET;
    let pins: Vec<Solid> = (0..PIN_COUNT)
        .map(|index| {
            let y = (index as f64 - (PIN_COUNT - 1) as f64 / 2.) * PIN_PITCH;
            Solid::cuboid(
                v3(pin_x - PIN_SQ / 2., y - PIN_SQ / 2., 0.),
                v3(pin_x + PIN_SQ / 2., y + PIN_SQ / 2., PIN_LEN),
            )
        })
        .collect();
    let pins = Solid::compose(&pins);
    let mesh_color = material("M_STAINLESS")?.map(|channel| channel * 0.55);
    show(&dir, "mq6-gas-sensor", &[
        ("mq6-gas-sensor", material("C_MQ6")?, &pcb),
        ("sensor-base", material("M_STAINLESS")?, &base),
        ("sensor-cap", mesh_color, &cap),
        ("header-pins", material("M_ZINC_PLATED_STEEL")?, &pins),
    ])
}
