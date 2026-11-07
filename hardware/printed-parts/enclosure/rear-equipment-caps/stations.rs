//! The snap stations of the rear receivers the caps close, figured as back-top figures the
//! receivers it cuts (`enclosure/back-top/supports.rs`): from the hardware's measured seat runs,
//! the layout's frames and the fits, with the same formulas, so each cap is drawn from the
//! station of the receiver it snaps into. The water regulator's station is written down in the
//! layout; the other three are figured here.
use hsm_enclosure_numbers::catalog::{clearance, running, slip};
use hsm_enclosure_numbers::layout::{Pose, Station, layout};
use hsm_enclosure_numbers::{P2, P3};
use serde::Deserialize;
use std::sync::OnceLock;

/// A receiver's wall.
pub const WALL: f64 = 3.0;
/// A cap's spring wing: its section, its flat bearing past the receiver edge, its relaxed face
/// off that edge, its free length from root to hook, the round at its root, and how far below
/// its axis a rear wing roots.
const WING: f64 = 2.0;
pub const REACH: f64 = 2.6;
const SIDE: f64 = 0.5;
const FREE_LENGTH: f64 = 22.25;
pub const ROOT_RADIUS: f64 = 1.5;
const REAR_ROOT_DROP: f64 = 10.0;
/// The ledge's height off the split, and the hook's solid nose and pointed lead-in above it.
const LEDGE: f64 = 3.0;
pub const NOSE_LAND: f64 = 1.6;
const TIP_RISE: f64 = 3.0;
/// How far past a cap's ends a turned run still counts toward the widest the cap clears.
const CAP_OVERLAP: f64 = 0.25;
/// The Pisco's seat splits this far above its axis, and its runs take this radial relief past
/// running air.
const PISCO_SPLIT_RISE: f64 = 7.0;
const PISCO_RADIAL_RELIEF: f64 = 0.25;
/// The meter's air at its spring station, collar passages and wire chamber, and its receiver's
/// and its cap's spans about its station.
pub const METER_AIR: f64 = 0.75;
const METER_SEAT: P2 = [-30.01, 29.99];
const METER_CAP: P2 = [-19.01, 18.99];

/// The Multiplex ASSE 1022, by its reference: its port axis's height, its bonnet's station, each
/// wrench's widest radius, flats and clocking, and its vent's barb tip and stem. The chain turns
/// it a quarter about its axis in the seat.
pub mod asse {
    use hsm_enclosure_numbers::P3;
    pub const BODY_CENTER_Z: f64 = 27.45;
    pub const BONNET_X: f64 = 47.65;
    pub struct Wrench {
        pub widest: f64,
        pub across_flats: f64,
        pub clock: f64,
    }
    pub const WRENCHES: [Wrench; 2] = [
        Wrench { widest: 16.17, across_flats: 28.65, clock: 0.3 },
        Wrench { widest: 16.55, across_flats: 28.73, clock: 0.9 },
    ];
    pub const TURN: f64 = 90.0;
    pub const VENT_TIP: P3 = [24.65, 0.07, 0.0];
    pub const VENT_D: f64 = 7.70;
}

/// The Digiten flow meter, by its reference: its body's centre, the housing's axial profile and
/// its step out to the cover flange, the soda port's neck and collar, and the housing's underside.
pub mod meter {
    use hsm_enclosure_numbers::P2;
    pub const BODY_CENTER_X: f64 = 0.0;
    pub const BODY_CENTER_Z: f64 = 8.9;
    pub const HOUSING_PROFILE: [P2; 10] = [[-9.4, 13.9], [-8.1, 15.1], [7.3, 15.45], [7.3, 17.5], [10.6, 17.5],
                                           [10.6, 17.45], [14.8, 17.45], [14.8, 17.5], [17.2, 17.5], [18.7, 13.2]];
    pub const FLANGE_Y: f64 = 7.3;
    pub const PORT_NECK_RADIUS: f64 = 7.95;
    pub const PORT_COLLAR_RADIUS: f64 = 9.15;
    pub const UNDERSIDE_Y: f64 = -9.4;
}

/// The ASSE chain's and the Pisco's measured seat runs, `[lo, hi, radius]` along each reference's
/// own axial coordinate, and the ASSE coupling's fore end.
#[derive(Deserialize)]
struct SeatProfiles {
    asse: AsseRuns,
    pisco: Runs,
}

#[derive(Deserialize)]
struct AsseRuns {
    seat_runs: Vec<P3>,
    gagira_fore_x: f64,
}

#[derive(Deserialize)]
struct Runs {
    seat_runs: Vec<P3>,
}

fn profiles() -> &'static SeatProfiles {
    static PROFILES: OnceLock<SeatProfiles> = OnceLock::new();
    PROFILES.get_or_init(|| {
        serde_json::from_str(include_str!("../enclosure/rear-seat-profiles.json")).expect("the rear seat profiles parse")
    })
}

/// The Pisco's fitted exterior: where its outlet fitting and its outlet collet start, and its
/// radius along its axis from the mouth.
#[derive(Deserialize)]
struct Candidates {
    pisco_rvfup_quarter: Candidate,
}

#[derive(Deserialize)]
struct Candidate {
    fitted_exterior: FittedExterior,
}

#[derive(Deserialize)]
pub struct FittedExterior {
    pub component_ranges_mm: ComponentRanges,
    pub profile_z_radius_mm: Vec<P2>,
}

#[derive(Deserialize)]
pub struct ComponentRanges {
    pub outlet_fitting: P2,
    pub outlet_collet: P2,
}

pub fn pisco_exterior() -> &'static FittedExterior {
    static PISCO: OnceLock<Candidates> = OnceLock::new();
    &PISCO
        .get_or_init(|| {
            serde_json::from_str(include_str!("../../../reference/compact-inline-candidates/dimensions.json"))
                .expect("the inline candidates' dimensions parse")
        })
        .pisco_rvfup_quarter
        .fitted_exterior
}

/// The relieved rear wall face the seats stand on.
fn rear() -> f64 {
    layout().rear_wall.interior_panel_relief.ymax
}

/// The cap's spring wing clears its hook this far: one face's slip and its supported finish.
pub fn catch_air() -> f64 {
    clearance(false, true, false)
}

/// One snap station's flank numbers about its axis, from the seat's neck half-width, the cap's
/// span, the split the seat parts at and where its wings root.
fn station(axis_x: f64, neck: f64, [y0, y1]: P2, split: f64, root: f64) -> Station {
    let ledge = neck + REACH + running();
    let inner = ledge + SIDE;
    let catch = (root + FREE_LENGTH).max(split + LEDGE + catch_air());
    let tip = catch + (NOSE_LAND + TIP_RISE);
    Station { axis_x, y0, y1, split, neck, ledge, inner, outer: inner + WING, bearing: catch - catch_air(),
              ceiling: tip + 2.0 * running(), root, root_radius: ROOT_RADIUS }
}

/// The ASSE chain's station: its cap spans from the bonnet to the coupling's fore end, and its
/// seat stands down to the body's axis, past the widest the cap's span reaches.
pub fn asse_station() -> Station {
    let frame = &layout().rear_plumbing.chain_frame;
    let c = running();
    let centre = frame.point([0.0, 0.0, asse::BODY_CENTER_Z]);
    let along = |x: f64| frame.point([x, 0.0, asse::BODY_CENTER_Z])[1];
    let span = [along(asse::BONNET_X) - slip(), along(profiles().asse.gagira_fore_x) - slip()];
    let profile = runs(&profiles().asse.seat_runs, frame, c);
    let widest = widest(&profile, span).chain(asse::WRENCHES.iter().map(|w| w.widest + c))
        .fold(f64::NEG_INFINITY, f64::max);
    let split = centre[2] + c;
    station(centre[0], half_width(widest, split, centre[2]) + WALL, span, split, centre[2] - REAR_ROOT_DROP)
}

/// The Pisco's station: its cap spans from its outlet collet to a full rear receiver end wall,
/// and its seat splits above its axis with full walls beside the widened passage.
pub fn pisco_station() -> Station {
    let frame = &layout().rear_plumbing.gas_frame;
    let c = running();
    let mouth = frame.point([0.0; 3]);
    let span = [mouth[1] - pisco_exterior().component_ranges_mm.outlet_collet[0] + c + 0.01, rear() - WALL - c];
    let profile = runs(&profiles().pisco.seat_runs, frame, c + PISCO_RADIAL_RELIEF);
    let widest = widest(&profile, span).fold(f64::NEG_INFINITY, f64::max);
    let split = mouth[2] + PISCO_SPLIT_RISE;
    station(mouth[0], half_width(widest, split, mouth[2]) + (WALL - REACH - c), span, split,
            mouth[2] - REAR_ROOT_DROP)
}

/// Where the flow meter stands in the machine: its housing's axis at `y`, `z`, its soda port's
/// axis at X and Z `soda`, the split west of which its cap holds the housing, and its receiver's
/// and its cap's spans along Y.
pub struct Meter {
    frame: &'static Pose,
    pub y: f64,
    pub z: f64,
    pub soda: P2,
    pub split: f64,
    pub seat: P2,
    pub cap: P2,
}

impl Meter {
    pub fn placed() -> Meter {
        let frame = &layout().parts.digiten_flow;
        let centre = frame.point([meter::BODY_CENTER_X, 0.0, meter::BODY_CENTER_Z]);
        let port = frame.point([0.0; 3]);
        let ty = frame.translation_mm[1];
        let x = |y: f64| frame.point([meter::BODY_CENTER_X, y, meter::BODY_CENTER_Z])[0];
        Meter { frame, y: centre[1], z: centre[2], soda: [port[0], port[2]], split: x(meter::FLANGE_Y) - METER_AIR,
                seat: [ty + METER_SEAT[0], ty + METER_SEAT[1]], cap: [ty + METER_CAP[0], ty + METER_CAP[1]] }
    }

    /// The machine's X at a station along the housing's axis.
    pub fn x(&self, y: f64) -> f64 {
        self.frame.point([meter::BODY_CENTER_X, y, meter::BODY_CENTER_Z])[0]
    }

    /// The meter's station, in its snap's own frame about the split: the neck clears the soda
    /// port's collar, and the wings root at the housing's underside.
    pub fn station(&self) -> Station {
        station(0.0, self.soda[1] + meter::PORT_COLLAR_RADIUS + METER_AIR - self.z + WALL, self.cap, 0.0,
                self.x(meter::UNDERSIDE_Y) - METER_AIR - self.split)
    }
}

/// A circle's half-chord at height `z` off its axis.
fn half_width(radius: f64, z: f64, axis_z: f64) -> f64 {
    (radius * radius - (z - axis_z) * (z - axis_z)).max(0.0).sqrt()
}

/// A seat's turned runs in the machine's frame: the reference's runs along its axial coordinate,
/// which the frame carries aft, each grown by `air`.
fn runs(seat_runs: &[P3], frame: &Pose, air: f64) -> Vec<P3> {
    let t = frame.translation_mm[1];
    seat_runs.iter().rev().map(|&[lo, hi, r]| [t - hi, t - lo, r + air]).collect()
}

/// The widest of the runs a cap's span reaches.
fn widest(runs: &[P3], [y0, y1]: P2) -> impl Iterator<Item = f64> + '_ {
    runs.iter().filter(move |r| r[1] >= y0 - CAP_OVERLAP && r[0] <= y1 + CAP_OVERLAP).map(|r| r[2])
}

/// Linear interpolation along a profile, held at its ends; a repeated station takes its later
/// point.
pub fn interpolate(points: &[P2], x: f64) -> f64 {
    let last = points.len() - 1;
    if x < points[0][0] {
        return points[0][1];
    }
    if x >= points[last][0] {
        return points[last][1];
    }
    let i = points.partition_point(|p| p[0] <= x).saturating_sub(1);
    let ([a, ra], [b, rb]) = (points[i], points[i + 1]);
    if b == a { rb } else { ra + (rb - ra) * (x - a) / (b - a) }
}

/// A measured radial profile as a short outward line profile: each station takes the widest
/// radius within `axial` of it, plus `radial`, and a chord replaces the stations it stays
/// outside of by no more than the merge tolerance, so short shoulders survive.
pub fn clearance_profile(profile: &[P2], radial: f64, axial: f64) -> Vec<P2> {
    const TOLERANCE: f64 = 0.06;
    let mut stations: Vec<f64> = profile.iter().flat_map(|p| [p[0] - axial, p[0] + axial]).collect();
    stations.sort_by(f64::total_cmp);
    stations.dedup();
    let points: Vec<P2> = stations
        .iter()
        .map(|&t| {
            let ends = interpolate(profile, t - axial).max(interpolate(profile, t + axial));
            let widest = profile
                .iter()
                .filter(|p| p[0] >= t - axial - 1e-8 && p[0] <= t + axial + 1e-8)
                .fold(ends, |r, p| r.max(p[1]));
            [t, widest + radial]
        })
        .collect();
    let mut kept = vec![points[0]];
    let mut i = 0;
    while i + 1 < points.len() {
        let mut best = i + 1;
        for j in i + 2..points.len() {
            let chord = [points[i], points[j]];
            let (low, high) = points[i..=j].iter().map(|p| interpolate(&chord, p[0]) - p[1])
                .fold((f64::INFINITY, f64::NEG_INFINITY), |(lo, hi), d| (lo.min(d), hi.max(d)));
            if low >= -1e-8 && high <= TOLERANCE {
                best = j;
            }
        }
        kept.push(points[best]);
        i = best;
    }
    kept
}
