//! The written-down designs the cap's numbers are read from: the above-core design
//! (`hardware/manifold-layout/above-core.json`), where the parts on the crown stand and how the
//! pump is held; reservoir A's routes (`reservoir-a-routes.json` beside it); and the G Ganen
//! pump's scanned envelope and the JG elbow's measured body, from their references.
use crate::P3;
use hsm_cold_core_layout::cap::Pose;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::sync::OnceLock;

/// A part's placement in the above-core design: its pose and the reference model it carries.
#[derive(Clone, Debug, Deserialize)]
pub struct Placed {
    pub rotation: [[f64; 3]; 3],
    pub translation_mm: P3,
    #[serde(default)]
    pub reference: Option<String>,
}

impl Placed {
    pub fn pose(&self) -> Pose {
        Pose { rotation: self.rotation, translation: self.translation_mm }
    }
}

#[derive(Deserialize)]
pub struct Parts {
    #[serde(rename = "g-ganen-pump")]
    pub pump: Placed,
    #[serde(rename = "valve-v-b")]
    pub valve_v_b: Placed,
    pub pcba: Placed,
}

#[derive(Deserialize)]
pub struct Snapshots {
    #[serde(rename = "vb-outlet-return")]
    pub vb_outlet_return: Placed,
}

#[derive(Deserialize)]
pub struct VbMount {
    pub seat_wall_bounds_mm: [P3; 2],
}

/// The V-A feed's seat on the lid.
#[derive(Deserialize)]
pub struct FeedSnap {
    pub centre_world_mm: P3,
    pub along_world: P3,
}

#[derive(Deserialize)]
pub struct ForeRoutes {
    pub va_feed_snap: FeedSnap,
}

/// How the lid holds the pump: the motor bands the cradle and the snap cap take, the rail stops,
/// the cap's arch and the lid's recess under the molded cover, with the design's own account of
/// each.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct PumpMount {
    pub motor_band_native_x_mm: [f64; 2],
    pub snap_band_native_x_mm: [f64; 2],
    pub rail_stop_native_z_mm: f64,
    pub rail_stop_native_x_mm: [[f64; 2]; 2],
    pub insertion: String,
    pub print_pose: String,
    pub cap_arch_wall_mm: f64,
    pub contact_scope: String,
    pub axial_end_stock_mm: f64,
    pub rail_stop_contact_native_y_mm: [f64; 2],
    pub cap_east_roof_half_width_mm: f64,
    pub cover_channel_recess_mm: f64,
    pub cover_channel_fore_native_x_mm: f64,
}

#[derive(Deserialize)]
pub struct AboveCore {
    pub parts: Parts,
    pub snapshots: Snapshots,
    pub vb_mount: VbMount,
    pub cap_guides_world_mm: BTreeMap<String, P3>,
    pub gas_guide_world_mm: P3,
    pub fore_routes: ForeRoutes,
    pub pump_mount: PumpMount,
}

pub fn above_core() -> &'static AboveCore {
    static DESIGN: OnceLock<AboveCore> = OnceLock::new();
    DESIGN.get_or_init(|| {
        serde_json::from_str(include_str!("../../../../manifold-layout/above-core.json"))
            .expect("the above-core design parses")
    })
}

// --- Reservoir A's routes ----------------------------------------------------------------------

/// One run of a route as the design writes it: a straight run between two points, or a turn
/// about a centre and axis through an angle.
#[derive(Clone, Debug, Deserialize)]
#[serde(tag = "kind", rename_all = "lowercase")]
pub enum Run {
    Line {
        points_mm: [P3; 2],
    },
    Arc {
        start_mm: P3,
        center_mm: P3,
        axis: P3,
        angle_rad: f64,
        radius_mm: f64,
        end_mm: P3,
    },
}

#[derive(Deserialize)]
pub struct RoutePath {
    pub segments: Vec<Run>,
    #[serde(default)]
    pub reverse: bool,
}

#[derive(Deserialize)]
pub struct ReservoirRoutes {
    pub paths: BTreeMap<String, RoutePath>,
}

pub fn reservoir_routes() -> &'static ReservoirRoutes {
    static ROUTES: OnceLock<ReservoirRoutes> = OnceLock::new();
    ROUTES.get_or_init(|| {
        serde_json::from_str(include_str!("../../../../manifold-layout/reservoir-a-routes.json"))
            .expect("reservoir A's routes parse")
    })
}

// --- The pump's scanned envelope ---------------------------------------------------------------

/// The pump's motor can, as its reference measures it: a cylinder through the straight barrel.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Can {
    pub axis_point_mm: P3,
    pub axis_direction: P3,
    pub radius_mm: f64,
    pub x_stations_mm: [f64; 2],
    pub scope: String,
}

/// One scanned section across the casing at a station along the pump's native X.
#[derive(Deserialize)]
pub struct Section {
    pub x_mm: f64,
    pub vertices_mm: Vec<P3>,
}

#[derive(Deserialize)]
pub struct SidePlane {
    pub coefficients: P3,
}

#[derive(Deserialize)]
pub struct SideProfile {
    pub side_plane: SidePlane,
}

#[derive(Deserialize)]
pub struct FacePlane {
    pub z_ax_plus_by_plus_c: P3,
}

#[derive(Deserialize)]
pub struct RailPlanes {
    pub outer_upper: FacePlane,
    pub outer_lower: FacePlane,
    pub inner_return: FacePlane,
}

#[derive(Deserialize)]
pub struct RailFaces {
    pub side: i64,
    pub planes: RailPlanes,
}

#[derive(Deserialize)]
pub struct Underside {
    pub wire_cover_side_profiles: Vec<SideProfile>,
    pub rail_face_planes: Vec<RailFaces>,
}

#[derive(Deserialize)]
pub struct PumpReference {
    pub casing_sections: Vec<Section>,
    pub motor_can_envelope: Can,
    pub rigid_underside: Underside,
}

pub fn pump_reference() -> &'static PumpReference {
    static PUMP: OnceLock<PumpReference> = OnceLock::new();
    PUMP.get_or_init(|| {
        serde_json::from_str(include_str!(
            "../../../../reference/g-ganen-pump/reference-parameters.json"
        ))
        .expect("the pump's reference parameters parse")
    })
}

// --- The JG elbow's measured body --------------------------------------------------------------

#[derive(Deserialize)]
pub struct Leg {
    /// Stations along the leg and the fixed body's radius at each.
    pub fixed_body: Vec<[f64; 2]>,
}

#[derive(Deserialize)]
pub struct Legs {
    pub z: Leg,
}

#[derive(Deserialize)]
pub struct ElbowScan {
    pub profiles: Legs,
}

pub fn elbow_scan() -> &'static ElbowScan {
    static SCAN: OnceLock<ElbowScan> = OnceLock::new();
    SCAN.get_or_init(|| {
        serde_json::from_str(include_str!(
            "../../../../reference/jg-pp0308e-elbow/scan-measurements.json"
        ))
        .expect("the JG elbow's scan parses")
    })
}
