//! The manual tube-fixture review measures travel, pad backing and native printable parts on request.
use crate::tube_fixture::{self as jig, numbers::*};
use anyhow::Result;
use hsm_kernel::{Bounds, Solid, v3};
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::path::Path;

fn bounds(solid: &Solid) -> Value {
    let b = solid.bounds();
    json!({"min_mm":b.min.to_array(),"max_mm":b.max.to_array(),"size_mm":b.size().to_array()})
}
fn overlaps(a: Bounds, b: Bounds) -> bool {
    let (a0, a1, b0, b1) = (
        a.min.to_array(),
        a.max.to_array(),
        b.min.to_array(),
        b.max.to_array(),
    );
    (0..3).all(|i| a1[i].min(b1[i]) - a0[i].max(b0[i]) > 1e-6)
}
fn stationary(name: &str) -> bool {
    matches!(name, "base" | "touch-flo-donor")
        || [
            "/fixed-pad-envelope",
            "/fixed-jaw-schematic",
            "/rail-schematic",
        ]
        .iter()
        .any(|suffix| name.ends_with(suffix))
}
pub fn review(root: &Path, out: &Path) -> Result<()> {
    let parts = jig::build_parts(false)?;
    let printed = jig::build_parts(true)?;
    let part_results:Vec<_>=printed.iter().map(|(name,shape)|json!({"part":name,"valid_mesh":shape.check().is_ok(),"solid_count":shape.components().len(),"bbox":bounds(shape),"volume_mm3":shape.volume()})).collect();
    let intentional = [
        (
            ["lldpe-tube", "lower-liner"],
            "Uncompressed TPU grip reference; elastic compression is unmodelled.",
        ),
        (
            ["lldpe-tube", "upper-liner"],
            "Uncompressed TPU grip reference; elastic compression is unmodelled.",
        ),
        (
            ["lower-liner", "upper-liner"],
            "Liners project beyond their pockets at rigid closure; the uncompressed overlap is intentional.",
        ),
        (
            ["touch-flo-donor", "tpu-sealing-thimble"],
            "Expanded TPU overlaps the nominal port before elastic compression.",
        ),
    ];
    let initial = jig::assembly(root, &parts, 0., true, true, true, DONOR_PORT_DEPTH_MIN)?;
    let mut failures = Vec::new();
    let mut queries = 0;
    let mut pair_count = 0;
    let increment = 0.5;
    let states = (PRESS_TRAVEL / increment).round() as usize + 1;
    for i in 0..states {
        let stroke = i as f64 * increment;
        let placed: BTreeMap<_, _> = initial
            .iter()
            .map(|p| {
                (
                    p.name.as_str(),
                    if stationary(&p.name) {
                        p.solid.clone()
                    } else {
                        p.solid.translate(v3(stroke, 0., 0.))
                    },
                )
            })
            .collect();
        let names: Vec<_> = placed.keys().copied().collect();
        for (j, &a) in names.iter().enumerate() {
            for &b in &names[j + 1..] {
                pair_count += 1;
                if a.contains('/') && b.contains('/') && a.split('/').next() == b.split('/').next()
                {
                    continue;
                }
                if intentional
                    .iter()
                    .any(|(p, _)| (p[0] == a && p[1] == b) || (p[1] == a && p[0] == b))
                    || !overlaps(placed[a].bounds(), placed[b].bounds())
                {
                    continue;
                }
                queries += 1;
                let volume = placed[a].intersect(&placed[b])?.volume();
                if volume > 1e-5 {
                    failures.push(json!({"stroke_mm":stroke,"parts":[a,b],"overlap_mm3":volume}));
                }
            }
        }
    }
    let base = jig::build_base()?;
    let lower = jig::build_lower_jaw(true)?.translate(v3(CLAMP_FINAL_X, TUBE_Y, TUBE_Z));
    let upper = jig::build_upper_jaw()?.translate(v3(CLAMP_FINAL_X, TUBE_Y, TUBE_Z));
    let jaw = lower.union(&upper)?;
    let mut bearing = Vec::new();
    for station in jig::clamp_stations(0.) {
        for (role, solid, x, inward, y) in [
            (
                "fixed",
                &base,
                THRUST_WALL_X0,
                1.,
                station.fixed_center_mm[1],
            ),
            (
                "moving",
                &jaw,
                CLAMP_BACK_X,
                -1.,
                station.moving_center_mm[1],
            ),
        ] {
            let edge = x + inward * 0.1;
            let slab = jig::cylinder_x(
                x.min(edge),
                x.max(edge),
                y,
                TUBE_Z,
                FACTORY_PAD_ENVELOPE_D / 2.,
            )?;
            bearing.push(json!({"station":station.name,"role":role,"contact_center_mm":[x,y,TUBE_Z],"pad_envelope_diameter_mm":FACTORY_PAD_ENVELOPE_D,"missing_backing_mm3_in_0p1mm_slab":slab.cut(solid)?.volume()}));
        }
    }
    let lip_play = |stroke| {
        RAIL_LATERAL_GAP * (1. + 2. * (CARRIER_FINAL_X + stroke - DONOR_PORT_X) / CARRIER_LENGTH)
    };
    let tube_length = hsm_fabrication_guides::cuts::faucet()?.soda_faucet_cut;
    let report = json!({
        "purpose":"Answer the manual fixture geometry question from current native solids.",
        "schema":3,
        "scope":"Dimensional and mesh fit review of the twin screw-clamp fixture; factory clamp envelopes are schematic, not measured manufacturer CAD.",
        "physical_acceptance_record":"physical-acceptance.json",
        "source_sha256":crate::sha(&root.join(jig::DIRECTORY).join("tube_insertion.rs"))?,
        "numbers_sha256":crate::sha(&root.join(jig::DIRECTORY).join("numbers.rs"))?,
        "review_source_sha256":crate::sha(&root.join(jig::DIRECTORY).join("review_geometry.rs"))?,
        "reference_source_sha256":{(jig::DONOR):crate::sha(&root.join(jig::DONOR))?,(jig::DONOR_DATUMS):crate::sha(&root.join(jig::DONOR_DATUMS))?,"hardware/printed-parts/faucet/tpu-o-ring/numbers.rs":crate::sha(&root.join("hardware/printed-parts/faucet/tpu-o-ring/numbers.rs"))?},
        "parts":part_results,
        "travel_review":{"stroke_range_mm":[0.,PRESS_TRAVEL],"increment_mm":increment,"states":states,"pairwise_bounds_reviews":pair_count,"mesh_intersection_queries":queries,"unintended_intersections":failures,"tube_length_mm":tube_length,"included":"Printed rigid parts, reference donor, tube, liners, thimble, fasteners and schematic factory clamps.","intentional_interference":intentional.iter().map(|(parts,reason)|json!({"parts":parts,"reason":reason})).collect::<Vec<_>>()},
        "factory_bearing_review":bearing,
        "location_and_grip":{
            "tube_axis_yz_mm":[TUBE_Y,TUBE_Z],"donor_round_base_tangent_floor_z_mm":TUBE_Z-DONOR_BODY_OD/2.,"donor_flat_clocking_pad_z_mm":CLOCKING_PAD_Z1,"lower_jaw_shelf_z_mm":TUBE_Z-JAW_HALF_H,"guide_bearing_span_mm":CARRIER_LENGTH,"guide_lateral_gap_each_mm":RAIL_LATERAL_GAP,
            "carrier_foot_final_x_range_mm":[CARRIER_FINAL_X,CARRIER_FINAL_X+CARRIER_LENGTH],"carrier_foot_initial_x_range_mm":[CARRIER_FINAL_X+PRESS_TRAVEL,CARRIER_FINAL_X+CARRIER_LENGTH+PRESS_TRAVEL],
            "nominal_guide_only_lip_play_final_mm":lip_play(0.),"nominal_guide_only_lip_play_initial_mm":lip_play(PRESS_TRAVEL),"guide_play_scope":"Geometric free play with the lower jaw metal-coupled without slip; no measured working alignment allowance is inferred.",
            "grip_bore_mm":GRIP_BORE_D,"tube_od_mm":TUBE_OD,"liner_grip_length_mm":LINER_LENGTH,"liner_center_x_mm":LINER_X0+LINER_LENGTH/2.,"closure_screw_x_mm":CLAMP_BOLT_X,"closure_screw_axial_offset_mm":CLAMP_BOLT_X-(LINER_X0+LINER_LENGTH/2.),"crossbar_center_x_mm":(JAW_HANDLE_START_X+JAW_HANDLE_END_X)/2.,
            "liner_proud_height_each_mm":LINER_H-LINER_POCKET_H,"paired_rigid_face_closure_reserve_mm":2.*(LINER_H-LINER_POCKET_H),"jaw_pocket_front_end_wall_mm":LINER_X0-JAW_LINER_AXIAL_CLEARANCE/2.,"jaw_pocket_rear_end_wall_mm":JAW_LENGTH-LINER_X0-LINER_LENGTH-JAW_LINER_AXIAL_CLEARANCE/2.,"jaw_pocket_backing_mm":JAW_BACK_H,"liner_minimum_backing_mm":LINER_H-GRIP_BORE_D/2.,"liner_end_contact_area_mm2":LINER_WIDTH*LINER_H-0.5*std::f64::consts::PI*(GRIP_BORE_D/2.).powi(2),
            "carrier_countersink_retained_shelf_mm":CARRIER_SHELF_H-countersink_height(),"carrier_nut_floor_mm":COUPLING_NUT_Z0+JAW_HALF_H,"carrier_screw_tip_z_mm":CARRIER_BOTTOM_Z+M5_CS_HEAD_RECESS+20.,"carrier_screw_tip_relief_mm":TUBE_Z-(CARRIER_BOTTOM_Z+M5_CS_HEAD_RECESS+20.),"carrier_countersink_radial_stock_mm":COUPLING_TOE_R-M5_CS_HEAD_D/2.,"carrier_nut_z_range_mm":[TUBE_Z+COUPLING_NUT_Z0,TUBE_Z+COUPLING_NUT_Z0+4.],
            "liner_print_pose":"Tube axis vertical; preformed half-round block.","clamp_front_final_x_mm":CLAMP_FINAL_X,"arch_axial_clearance_mm":CLAMP_FINAL_X-DONOR_ARCH_X,"factory_pad_to_shank_slot_near_clearance_mm":SCREW_OFFSET_Y-TUBE_Y-SHANK_SLOT_D/2.-FACTORY_PAD_ENVELOPE_D/2.
        },
        "setup_source":"README.md",
        "evidence_source":"load-basis.md",
        "evidence_scope":"Force, as-printed strength, grip, quantitative sliding clearance and lifetime require physical evidence. Geometric overtravel stops provide no load or leak-tightness qualification. Factory envelopes require actual-tool setup."
    });
    crate::write_json(out, &report)?;
    println!(
        "tube fixture: {states} travel states, {queries} mesh queries, {} overlaps; {}",
        failures.len(),
        out.display()
    );
    Ok(())
}
