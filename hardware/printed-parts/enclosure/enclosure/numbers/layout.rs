//! The above-core layout back-top's rear wall is drawn from: where the parts it carries stand,
//! the wall's openings and labels, and the rear plumbing's frames, read typed from its data file.
use crate::{Bounds, P2, P3};
use serde::Deserialize;
use std::sync::OnceLock;

/// A rigid placement: rotation rows and a translation.
#[derive(Clone, Copy, Deserialize)]
pub struct Pose {
    pub rotation: [P3; 3],
    pub translation_mm: P3,
}

impl Pose {
    /// A point of the part's own frame, in the machine's.
    pub fn point(&self, p: P3) -> P3 {
        let v = self.vector(p);
        std::array::from_fn(|k| v[k] + self.translation_mm[k])
    }

    /// A direction of the part's own frame, in the machine's.
    pub fn vector(&self, v: P3) -> P3 {
        self.rotation.map(|r| r[0] * v[0] + r[1] * v[1] + r[2] * v[2])
    }
}

#[derive(Deserialize)]
pub struct Extent {
    pub xmin: f64,
    pub xmax: f64,
    pub ymin: f64,
    pub ymax: f64,
    pub zmin: f64,
    pub zmax: f64,
}

impl Extent {
    pub fn bounds(&self) -> Bounds {
        [self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax]
    }
}

#[derive(Deserialize)]
pub struct Enclosure {
    pub rear_y_mm: f64,
    pub roof_z_mm: f64,
}

#[derive(Deserialize)]
pub struct WetPort {
    pub center_x_mm: f64,
    pub center_z_mm: f64,
    pub bore_diameter_mm: f64,
}

#[derive(Deserialize)]
pub struct C14Opening {
    pub profile_clearance_mm: f64,
    pub flange_pocket_depth_mm: f64,
    pub cord_access_width_mm: f64,
    pub cord_access_height_mm: f64,
    pub cord_access_radius_mm: f64,
    pub mount_pitch_mm: f64,
}

#[derive(Deserialize)]
pub struct KeystoneOpening {
    pub face_center_mm: P3,
}

#[derive(Deserialize)]
pub struct DryOpenings {
    pub c14: C14Opening,
    pub keystone: KeystoneOpening,
}

#[derive(Deserialize)]
pub struct RearWall {
    pub rear_wall: Extent,
    pub interior_panel_relief: Extent,
    pub wet_ports: Vec<WetPort>,
    pub dry_openings: DryOpenings,
}

#[derive(Deserialize)]
pub struct NameplatePlace {
    pub center_x_mm: f64,
    pub center_z_mm: f64,
    pub face_y_mm: f64,
}

#[derive(Deserialize)]
pub struct Identification {
    pub width_mm: f64,
    pub channel_floor_z_mm: f64,
    pub nameplate: NameplatePlace,
}

#[derive(Deserialize)]
pub struct FluidGrid {
    pub columns_x_mm: Vec<f64>,
}

#[derive(Deserialize)]
pub struct Parts {
    pub psu: Pose,
    #[serde(rename = "relay-1")]
    pub relay_1: Pose,
    #[serde(rename = "relay-2")]
    pub relay_2: Pose,
    #[serde(rename = "c14-inlet")]
    pub c14_inlet: Pose,
    #[serde(rename = "valve-v-a")]
    pub valve_v_a: Pose,
    #[serde(rename = "vk-solenoid")]
    pub vk_solenoid: Pose,
    #[serde(rename = "asse1022-assembly")]
    pub asse1022_assembly: Pose,
    #[serde(rename = "digiten-flow")]
    pub digiten_flow: Pose,
}

#[derive(Deserialize)]
pub struct Snapshots {
    pub reg: Pose,
}

/// One snap station's flank numbers: the receiver's walls, ledges and hook planes about its axis.
#[derive(Clone, Copy, Deserialize)]
pub struct Station {
    pub axis_x: f64,
    pub y0: f64,
    pub y1: f64,
    pub split: f64,
    pub neck: f64,
    pub ledge: f64,
    pub inner: f64,
    pub outer: f64,
    pub bearing: f64,
    pub ceiling: f64,
    pub root: f64,
    pub root_radius: f64,
}

#[derive(Deserialize)]
pub struct CavityFit {
    pub receiver_radial_mm: f64,
    pub cap_radial_mm: f64,
    pub axial_mm: f64,
}

#[derive(Deserialize)]
pub struct RegulatorMount {
    pub station: Station,
    pub axis: P2,
    pub seat_y: P2,
    /// The height of the regulator cap's underside.
    pub cap_bottom: f64,
    pub cavity_fit: CavityFit,
}

#[derive(Deserialize)]
pub struct Joint {
    #[serde(rename = "PLINTH")]
    pub plinth: f64,
}

#[derive(Deserialize)]
pub struct RearPlumbing {
    pub joint: Joint,
    pub chain_frame: Pose,
    pub gas_frame: Pose,
    /// How far the inlet adapter's fitted room stands above the captured chain's pose.
    pub asse_adapter_rise_mm: f64,
    pub snap_ceiling_z_mm: f64,
    pub snap_tip_rise_mm: f64,
    pub snap_tip_air_mm: f64,
    pub regulator_mount: RegulatorMount,
}

#[derive(Deserialize)]
pub struct Layout {
    pub enclosure: Enclosure,
    pub parts: Parts,
    pub snapshots: Snapshots,
    pub fluid_grid: FluidGrid,
    pub rear_wall: RearWall,
    pub rear_plumbing: RearPlumbing,
    pub rear_identification: Identification,
}

pub fn layout() -> &'static Layout {
    static LAYOUT: OnceLock<Layout> = OnceLock::new();
    LAYOUT.get_or_init(|| {
        serde_json::from_str(include_str!("../../../../manifold-layout/above-core.json"))
            .expect("the above-core layout parses")
    })
}

/// The physically approved planar lead-in shared by the equipment caps and pump retainer.
pub fn snap_tip_rise() -> f64 {
    layout().rear_plumbing.snap_tip_rise_mm
}

/// The clearance beyond a complete snap point in its matching receiver.
pub fn snap_tip_air() -> f64 {
    layout().rear_plumbing.snap_tip_air_mm
}
