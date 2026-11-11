//! Runs the production rim-perimeter editor on a saved faucet test plate.

use std::{env, io, path::Path};

#[path = "../../../../../tools/hsm/print-prep/src/rim_contour.rs"]
mod implementation;

use implementation::{RimSpec, apply};

fn main() -> io::Result<()> {
    let args: Vec<_> = env::args().collect();
    if args.len() != 12 {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "usage: contour INPUT.gcode OUTPUT.gcode OBJECT_ID CX CY CZ TILT_DEG RADIUS_X RADIUS_Y FIRST_ANGLE LAST_ANGLE",
        ));
    }
    let parse = |i: usize| {
        args[i]
            .parse::<f64>()
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidInput, e))
    };
    let spec = RimSpec {
        identify_id: args[3]
            .parse()
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidInput, e))?,
        center_mm: [parse(4)?, parse(5)?, parse(6)?],
        seat_fall_angle_degrees: parse(7)?,
        semi_axes_mm: [parse(8)?, parse(9)?],
        supported_angles_degrees: [parse(10)?, parse(11)?],
    };
    let report = apply(Path::new(&args[1]), Path::new(&args[2]), spec)?;
    println!(
        "{{\"arc_count\":{},\"emitted_contact_segments\":{},\"modified_native_paths\":{},\"extrusion_added_mm\":{:.5},\"extrusion_removed_mm\":{:.5},\"estimated_motion_delta_seconds\":{:.5},\"maximum_contact_depth_below_prior_peak_mm\":{:.5},\"minimum_contact_z_mm\":{:.5}}}",
        report.arc_count,
        report.emitted_contact_segments,
        report.modified_native_paths,
        report.extrusion_added_mm,
        report.extrusion_removed_mm,
        report.estimated_motion_delta_seconds,
        report.maximum_contact_depth_below_prior_peak_mm,
        report.minimum_contact_z_mm
    );
    Ok(())
}
