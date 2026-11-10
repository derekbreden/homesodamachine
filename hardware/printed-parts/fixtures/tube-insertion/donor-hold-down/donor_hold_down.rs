//! The manual TPU donor cover follows the retained donor exterior and the insertion fixture's stations.
use crate::{artwork, tube_fixture as jig};
use anyhow::Result;
use hsm_kernel::{Body, Region, Solid, V3, v3};
use jig::numbers::*;
use serde_json::{Value, json};
use std::path::Path;

pub const DIRECTORY: &str = "hardware/printed-parts/fixtures/tube-insertion/donor-hold-down";
const BODY_RADIUS: f64 = DONOR_BODY_OD / 2.;
const BODY_X0: f64 = 0.;
const BODY_X1: f64 = donor::PLATEAU_Z;
const SIDE_BACKING: f64 = 3.25;
const BODY_HALF_WIDTH: f64 = BODY_RADIUS + SIDE_BACKING;
const BODY_BOTTOM_Z: f64 = DONOR_AXIS_Z;
const FACE_Z: f64 = THRUST_WALL_Z1 + 2.;
const TONGUE_X0: f64 = THRUST_WALL_X0 + 0.5;
const TONGUE_X1: f64 = THRUST_WALL_X1;
const TONGUE_WIDTH: f64 = SHANK_SLOT_D + 1.;
const TONGUE_BOTTOM_Z: f64 = DONOR_AXIS_Z + BODY_RADIUS;
const LEAD_HEIGHT: f64 = 0.75;
const LEAD_IN_PER_SIDE: f64 = 0.75;

fn donor_exterior(root: &Path) -> Result<Solid> {
    let port = jig::cylinder_x(
        donor::PLATEAU_Z - DONOR_PORT_DEPTH_MIN,
        donor::PLATEAU_Z,
        TUBE_Y,
        TUBE_Z,
        donor::PORT_DIAMETER / 2.,
    )?;
    jig::donor_shape(root)?.union(&port)
}
pub fn build_pad(root: &Path, print_frame: bool) -> Result<Solid> {
    let body = jig::block(
        BODY_X0,
        BODY_X1,
        -BODY_HALF_WIDTH,
        BODY_HALF_WIDTH,
        BODY_BOTTOM_Z,
        FACE_Z,
    )
    .cut(&donor_exterior(root)?)?;
    let half = TONGUE_WIDTH / 2.;
    let mut points = vec![
        [-half + LEAD_IN_PER_SIDE, TONGUE_BOTTOM_Z],
        [-half, TONGUE_BOTTOM_Z + LEAD_HEIGHT],
        [-half, FACE_Z],
        [half, FACE_Z],
        [half, TONGUE_BOTTOM_Z + LEAD_HEIGHT],
        [half - LEAD_IN_PER_SIDE, TONGUE_BOTTOM_Z],
    ];
    points.reverse();
    let profile = Region::polygon(
        points
            .into_iter()
            .map(|[y, z]| v3(TONGUE_X0, y, z))
            .collect(),
    );
    let tongue = Solid::extrude(&profile, V3::X, V3::X * (TONGUE_X1 - TONGUE_X0))?;
    let pad = body.union(&tongue)?;
    Ok(if print_frame {
        pad.rotate(V3::ZERO, V3::X, 180.)
            .translate(v3(0., 0., FACE_Z))
    } else {
        pad
    })
}
pub fn export(root: &Path, out: &Path) -> Result<()> {
    std::fs::create_dir_all(out)?;
    let printed = build_pad(root, true)?;
    hsm_kernel::part::write_part(
        out,
        "donor-hold-down",
        &[Body {
            name: "tpu-hand-pad",
            color: Some(artwork::color([0.11, 0.12, 0.13])),
            solid: &printed,
        }],
    )?;
    crate::write(
        &out.join("donor-hold-down-print.stl"),
        &hsm_kernel::write::stl_bytes(&[&printed])?,
    )?;
    let crop = jig::block(
        THRUST_WALL_X0 - 2.,
        DONOR_ARCH_X + 1.,
        -24.,
        24.,
        20.,
        FACE_Z + 2.,
    );
    let base = jig::build_base()?.intersect(&crop)?;
    let donor = jig::donor_shape(root)?.intersect(&crop)?;
    let pad = build_pad(root, false)?;
    hsm_kernel::part::write_shown(
        out,
        "donor-hold-down-fit",
        &[
            Body {
                name: "existing-base-contact-zone",
                color: Some(jig::rigid_color()),
                solid: &base,
            },
            Body {
                name: "donor-contact-zone",
                color: Some(artwork::color([0.58, 0.61, 0.64])),
                solid: &donor,
            },
            Body {
                name: "tpu-hand-pad",
                color: Some(artwork::color([0.20, 0.43, 0.78])),
                solid: &pad,
            },
        ],
    )?;
    let record: Value = json!({
        "material":"TPU 85A","quantity":1,"print_bounds_mm":printed.bounds().size().to_array(),
        "print_face":"Broad flat hand face at print Z=0; upper-half donor cavity upward",
        "flat_face_above_petgf_mm":FACE_Z-THRUST_WALL_Z1,
        "donor_contact_region":"Upper half of the cylindrical body, rounded transition and flat-sided column, with both flanks wrapped down to the centreline",
        "donor_contact_axial_range_mm":[BODY_X0,BODY_X1],"donor_transition_radius_mm":jig::numbers::donor::TRANSITION_RADIUS,
        "donor_flat_starts_axial_mm":jig::numbers::donor::CYLINDER_HEIGHT+jig::numbers::donor::TRANSITION_RADIUS,
        "donor_coverage_fraction_of_cross_section":0.5,"donor_cylinder_wrap_degrees":180.,"donor_coverage_lower_z_mm":BODY_BOTTOM_Z,
        "donor_flat_contact_z_mm":DONOR_AXIS_Z+jig::numbers::donor::BODY_FLAT_THICKNESS/2.,
        "donor_flat_contact_width_mm":2.*(BODY_RADIUS.powi(2)-(jig::numbers::donor::BODY_FLAT_THICKNESS/2.).powi(2)).sqrt(),
        "body_flat_backing_mm":FACE_Z-DONOR_AXIS_Z-jig::numbers::donor::BODY_FLAT_THICKNESS/2.,
        "minimum_side_backing_mm":SIDE_BACKING,"body_end_at_lever_attachment_plane_mm":BODY_X1,
        "existing_canyon_width_mm":SHANK_SLOT_D,"retention_tongue_width_mm":TONGUE_WIDTH,
        "nominal_interference_per_side_mm":(TONGUE_WIDTH-SHANK_SLOT_D)/2.,
        "thread_clearance_mm":TONGUE_BOTTOM_Z-DONOR_AXIS_Z-DONOR_SHANK_OD/2.,
        "tongue_canyon_engagement_mm":THRUST_WALL_Z1-TONGUE_BOTTOM_Z,
        "full_width_canyon_engagement_mm":THRUST_WALL_Z1-TONGUE_BOTTOM_Z-LEAD_HEIGHT,
        "lower_cradle_axial_overlap_mm":NEST_LENGTH-BODY_X0,"lower_wrap_edge_above_cradle_mm":BODY_BOTTOM_Z-DONOR_AXIS_Z,
        "rear_face_clearance_mm":TONGUE_X0-THRUST_WALL_X0,"tongue_entry_width_mm":TONGUE_WIDTH-2.*LEAD_IN_PER_SIDE,
        "tongue_entry_lead_height_mm":LEAD_HEIGHT,
        "flat_bed_contact_area_mm2":(BODY_X1-BODY_X0)*2.*BODY_HALF_WIDTH+(TONGUE_X1-TONGUE_X0)*TONGUE_WIDTH,
        "volume_mm3":printed.volume(),"status":"Fit candidate; retention and hand-pressure performance unmeasured",
        "load_path":"Hand pressure through the conforming transition/flat face to the donor metal; tongue interference retains the pad in the existing canyon",
        "lever_scope":"The continuous half-body cover runs from the cylindrical base to the donor plateau plane, ending below the lever attachment and extending to the donor centreline on both sides. The lever stays attached and down at unpressed rest; its installed transform is not measured.",
        "print_support_basis":"With the hand face down, successive sections shrink as the conforming half-body cavity opens; the retention tongue narrows at its entry tip.",
        "source_sha256":crate::sha(&root.join(DIRECTORY).join("donor_hold_down.rs"))?,
        "fixture_source_sha256":crate::sha(&root.join(jig::DIRECTORY).join("tube_insertion.rs"))?,
        "datum_source_sha256":crate::sha(&root.join(jig::DONOR_DATUMS))?
    });
    crate::write_json(&out.join("dimensions.json"), &record)?;
    println!("donor hold-down: {}", out.display());
    Ok(())
}
