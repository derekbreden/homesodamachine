//! The seats back-top carries for the rear plumbing: the ASSE chain's, the Pisco regulator's,
//! the flow meter's and the water regulator's. Each is a block cut round its part's measured
//! profile, with the flank pockets its snap cap's spring wings ride in.
use crate::catalog::{clearance, running, slip};
use crate::layout::{Pose, Station, layout, snap_tip_air, snap_tip_rise};
use crate::plan::{Bounds, Graph, Op, P2, P3, Shape};
use crate::quadrant::sorted;
use crate::shapes::place;
use crate::shell::back_top_ceiling_face;
use crate::walls::back_top_flank_face;
use serde::Deserialize;
use std::sync::OnceLock;

/// The aft travel that puts the noses through the wall, and how far a taped joint may leave the
/// ASSE body's drawn station either way.
const SLIDE: f64 = 16.0;
const THREAD: f64 = 1.5;
/// A seat's wall, the plane the Pisco's and the water regulator's seats stand down to, and how
/// far each seat runs into the walls it joins.
const WALL: f64 = 3.0;
const SPLIT: f64 = 335.0;
const INTO: f64 = 0.5;
/// A cap's spring wing: its section, its flat bearing past the receiver edge, its relaxed face
/// off that edge, its free length from root to hook, the round at its root, and how far below
/// its axis a rear wing roots.
const WING: f64 = 2.0;
const REACH: f64 = 2.6;
const SIDE: f64 = 0.5;
const FREE_LENGTH: f64 = 22.25;
const ROOT_RADIUS: f64 = 1.5;
const REAR_ROOT_DROP: f64 = 10.0;
/// The ledge's height off the split, and the hook's solid nose and pointed lead-in above it.
const LEDGE: f64 = 3.0;
const NOSE_LAND: f64 = 1.6;
/// How far past a cap's ends a turned run still counts toward the widest the cap clears.
const CAP_OVERLAP: f64 = 0.25;
/// The Pisco: its seat's split above its axis, its radial relief past running air, its cap's
/// bearing fit and the bearing's length, and how far past the wings its fore flank exits open.
const PISCO_SPLIT_RISE: f64 = 7.0;
const PISCO_RADIAL_RELIEF: f64 = 0.25;
const PISCO_CAP_FIT: f64 = 0.15;
const PISCO_BEARING_LENGTH: f64 = 3.0;
const PISCO_SERVICE_FLANK: f64 = 3.2;
/// The meter's air at its spring station, collar passages and wire chamber; its housing's fit;
/// how far the soda union's stub may leave it aft of its station; and its seat's and cap's spans
/// about its station.
const METER_AIR: f64 = 0.75;
const METER_HOUSING_FIT: f64 = 0.15;
const VAR: f64 = 0.5;
const METER_SEAT: P2 = [-30.01, 29.99];
const METER_CAP: P2 = [-19.01, 18.99];

/// The Multiplex ASSE 1022, by its reference: its port axis's height, its bonnet's station, and
/// each wrench's run along the body, widest radius, flats and clocking. The chain turns it a
/// quarter about its axis in the seat.
mod asse {
    pub const BODY_CENTER_Z: f64 = 27.45;
    pub const BONNET_X: f64 = 47.65;
    pub struct Wrench {
        pub x: [f64; 2],
        pub widest: f64,
        pub across_flats: f64,
        pub clock: f64,
    }
    pub const WRENCHES: [Wrench; 2] = [
        Wrench { x: [17.75, 36.10], widest: 16.17, across_flats: 28.65, clock: 0.3 },
        Wrench { x: [36.10, 49.20], widest: 16.55, across_flats: 28.73, clock: 0.9 },
    ];
    pub const TURN: f64 = 90.0;
}

/// The Digiten flow meter, by its reference: its body's centre, the housing's axial profile and
/// its step out to the cover flange, the four cover bosses and their screw heads, the soda port's
/// collar, the wire lead's root, and the housing's underside.
mod meter {
    use crate::plan::{P2, P3};
    pub const BODY_CENTER_X: f64 = 0.0;
    pub const BODY_CENTER_Z: f64 = 8.9;
    pub const HOUSING_PROFILE: [P2; 10] = [[-9.4, 13.9], [-8.1, 15.1], [7.3, 15.45], [7.3, 17.5], [10.6, 17.5],
                                           [10.6, 17.45], [14.8, 17.45], [14.8, 17.5], [17.2, 17.5], [18.7, 13.2]];
    pub const FLANGE_Y: f64 = 7.3;
    pub const BOSS_X: f64 = 12.5;
    pub const BOSS_Z: f64 = 14.0;
    pub const BOSS_RADIUS: f64 = 3.45;
    pub const BOSS_Y: P2 = [0.0, 17.2];
    pub const SCREW_HEAD_RADIUS: f64 = 2.65;
    pub const SCREW_HEAD_Y: P2 = [17.2, 18.9];
    pub const PORT_NECK_END: f64 = 19.6;
    pub const PORT_COLLAR_END: f64 = 26.8;
    pub const PORT_COLLAR_RADIUS: f64 = 9.15;
    pub const WIRE_ROOT: P3 = [0.0, 14.8, 26.5];
    pub const WIRE_ROOT_WIDTH: f64 = 6.0;
    pub const WIRE_ROOT_DEPTH: f64 = 3.0;
    pub const WIRE_BOSS_LEN: f64 = 1.5;
    pub const WIRE_DROP: f64 = 3.0;
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
        serde_json::from_str(include_str!("../rear-seat-profiles.json")).expect("the rear seat profiles parse")
    })
}

/// The Pisco's fitted exterior: where its outlet collet starts, and its radius along its axis.
#[derive(Deserialize)]
struct Candidates {
    pisco_rvfup_quarter: Candidate,
}

#[derive(Deserialize)]
struct Candidate {
    fitted_exterior: FittedExterior,
}

#[derive(Deserialize)]
struct FittedExterior {
    component_ranges_mm: ComponentRanges,
    profile_z_radius_mm: Vec<P2>,
}

#[derive(Deserialize)]
struct ComponentRanges {
    outlet_collet: P2,
}

fn pisco_exterior() -> &'static FittedExterior {
    static PISCO: OnceLock<Candidates> = OnceLock::new();
    &PISCO
        .get_or_init(|| {
            serde_json::from_str(include_str!("../../../../reference/compact-inline-candidates/dimensions.json"))
                .expect("the inline candidates' dimensions parse")
        })
        .pisco_rvfup_quarter
        .fitted_exterior
}

/// The water regulator's measured radius along its axis.
#[derive(Deserialize)]
struct Regulator {
    profile_x_radius_mm: Vec<P2>,
}

fn regulator_profile() -> &'static [P2] {
    static REGULATOR: OnceLock<Regulator> = OnceLock::new();
    &REGULATOR
        .get_or_init(|| {
            serde_json::from_str(include_str!("../../../../reference/yzmsz-water-regulator/reference-parameters.json"))
                .expect("the water regulator's reference parses")
        })
        .profile_x_radius_mm
}

/// The relieved rear wall face the seats stand on.
fn rear() -> f64 {
    layout().rear_wall.interior_panel_relief.ymax
}

/// The east flank's inner face the meter's seat stands on.
fn side() -> f64 {
    back_top_flank_face()[1]
}

/// The plane the snap seats' stock rises to under the ceiling.
fn ceiling() -> f64 {
    layout().rear_plumbing.snap_ceiling_z_mm
}

/// The rear plumbing's seats, in the order back-top fuses them: the ASSE chain's, the Pisco's,
/// the meter's and the water regulator's.
pub fn supports(g: &mut Graph) -> [Shape; 4] {
    [asse(g), pisco(g), meter(g), regulator(g)]
}

/// The complete tip pockets stay open after the receivers join the enclosure ceiling and flank.
pub fn tip_clearances(g: &mut Graph) -> Vec<Shape> {
    let mut cuts = Vec::new();
    for st in [asse_station(), pisco_station()] {
        cuts.extend(tip_pockets(g, &st));
    }
    let frame = &layout().parts.digiten_flow;
    let centre = frame.point([meter::BODY_CENTER_X, 0.0, meter::BODY_CENTER_Z]);
    let port = frame.point([0.0; 3]);
    let wx = |y| frame.point([meter::BODY_CENTER_X, y, meter::BODY_CENTER_Z])[0];
    let mx = wx(meter::FLANGE_Y) - METER_AIR;
    let ty = frame.translation_mm[1];
    let st = station(0.0, port[2] + meter::PORT_COLLAR_RADIUS + METER_AIR - centre[2] + WALL,
                     [ty + METER_CAP[0], ty + METER_CAP[1]], 0.0,
                     wx(meter::UNDERSIDE_Y) - METER_AIR - mx);
    for pocket in tip_pockets(g, &st) {
        let pocket = g.rotate(pocket, [0.0; 3], [0.0, 1.0, 0.0], 90.0);
        cuts.push(g.translate(pocket, [mx, 0.0, centre[2]]));
    }
    for pocket in tip_pockets(g, &layout().rear_plumbing.regulator_mount.station) {
        cuts.push(g.rotate(pocket, [0.0; 3], [0.0, 0.0, 1.0], 90.0));
    }
    cuts
}

fn tip_pockets(g: &mut Graph, st: &Station) -> Vec<Shape> {
    [-1.0, 1.0].into_iter().map(|side| {
        let (x0, x1) = sorted(st.axis_x + side * st.neck, st.axis_x + side * (st.outer + 1.0));
        g.box_([x0, x1, st.y0 - running(), st.y1 + running(), st.bearing, st.ceiling])
    }).collect()
}

/// The cap's spring wing clears its hook this far: one face's slip and its supported finish.
fn catch_air() -> f64 {
    clearance(false, true, false)
}

/// One snap station's flank numbers about its axis, from the seat's neck half-width, the cap's
/// span, the split the seat parts at and where its wings root.
fn station(axis_x: f64, neck: f64, [y0, y1]: P2, split: f64, root: f64) -> Station {
    let ledge = neck + REACH + running();
    let inner = ledge + SIDE;
    let catch = (root + FREE_LENGTH).max(split + LEDGE + catch_air());
    let tip = catch + (NOSE_LAND + snap_tip_rise());
    Station { axis_x, y0, y1, split, neck, ledge, inner, outer: inner + WING, bearing: catch - catch_air(),
              ceiling: tip + snap_tip_air(), root, root_radius: ROOT_RADIUS }
}

/// Inaccessible rear receiver interiors. Their catches bridge between the full end shoulders.
pub fn bridge_regions() -> Vec<(&'static str, Bounds, f64)> {
    [("ASSE receiver", asse_station()), ("Pisco receiver", pisco_station())]
        .into_iter().map(|(name, s)| {
            let a = running();
            (name, [s.axis_x - s.outer - a, s.axis_x + s.outer + a,
                    s.y0 - a, s.y1 + a, s.split - a, s.ceiling + a], s.y1 - s.y0 + 2.0 * a)
        }).collect()
}

/// The meter and regulator stocks keep supports out of their fitted cap pockets.
pub fn side_support_regions() -> Vec<(&'static str, Bounds, f64, P3)> {
    let frame = &layout().parts.digiten_flow;
    let centre = frame.point([meter::BODY_CENTER_X, 0.0, meter::BODY_CENTER_Z]);
    let port = frame.point([0.0; 3]);
    let wx = |y: f64| frame.point([meter::BODY_CENTER_X, y, meter::BODY_CENTER_Z])[0];
    let mx = wx(meter::FLANGE_Y) - METER_AIR;
    let ty = frame.translation_mm[1];
    let st = station(0.0, port[2]+meter::PORT_COLLAR_RADIUS+METER_AIR-centre[2]+WALL,
                     [ty+METER_CAP[0],ty+METER_CAP[1]],0.0,wx(meter::UNDERSIDE_Y)-METER_AIR-mx);
    let meter = [mx,side()+INTO,ty+METER_SEAT[0],ty+METER_SEAT[1],centre[2]-st.outer,centre[2]+st.outer];
    let mount = &layout().rear_plumbing.regulator_mount;
    let [a,b] = mount.seat_y;
    let b = b.max(mount.station.y1+running()+WALL);
    let regulator = [-b,-a,mount.axis[0]-mount.station.outer,mount.axis[0]+mount.station.outer,
                     SPLIT,back_top_ceiling_face()+INTO];
    vec![("Flow meter receiver",meter,METER_CAP[1]-METER_CAP[0],[0.0,1.0,0.0]),
         ("Water regulator receiver",regulator,b-a,[1.0,0.0,0.0])]
}

/// Catch bridge modifiers include the solid shoulders at both ends of each pocket.
pub fn catch_bridges() -> Vec<(&'static str, Bounds, f64, P3)> {
    let a = running();
    let mut bridges: Vec<_> = [("ASSE receiver", asse_station()), ("Pisco receiver", pisco_station())]
        .into_iter().map(|(name, s)| {
            (name, [s.axis_x-s.outer-a,s.axis_x+s.outer+a,
                    s.y0-a-WALL,s.y1+a+WALL,s.split-a,s.bearing+a],
             s.y1-s.y0+2.0*a,[0.0,1.0,0.0])
        }).collect();
    let s = &layout().rear_plumbing.regulator_mount.station;
    bridges.push(("Water regulator receiver",
        [-s.y1-a-WALL,-s.y0+a+WALL,s.axis_x-s.outer-a,s.axis_x+s.outer+a,s.split-a,s.bearing+a],
        s.y1-s.y0+2.0*a,[1.0,0.0,0.0]));
    let (stock, cap) = meter_print_stock();
    let mut roof = stock;
    roof[4] = stock[5]-WALL;
    roof[5] += a;
    bridges.push(("Flow meter receiver roof",roof,cap[1]-cap[0],[0.0,1.0,0.0]));
    bridges
}

/// Short removable trees hold the sideways meter's exposed end shoulders clear of the plumbing.
pub fn meter_support_trees() -> anyhow::Result<Vec<serde_json::Value>> {
    use serde_json::json;
    let (stock, cap) = meter_print_stock();
    let mut trees = Vec::new();
    for (name,y0,y1) in [("Meter fore shoulder tree",stock[2],cap[0]-WALL-4.0*running()),
                          ("Meter aft shoulder tree",cap[1]+WALL+4.0*running(),stock[3])] {
        let y = (y0+y1)/2.0;
        let x = side()-WALL/2.0-running();
        let root = back_top_ceiling_face();
        let contact = stock[5]+crate::catalog::supported();
        let r = WALL/2.0-running();
        let inner = stock[0]+WALL/2.0;
        let head = contact+2.0*running()+0.1;
        trees.push(json!({"name":name,"bounds_source_mm":[stock[0]+running(),side()-running(),y-r,y+r,contact,root+0.01],
            "root_source_mm":[x,y,root],"neck_length_mm":1.0,"neck_flare_mm":WALL,"trunk_radius_mm":r,
            "inner_contact_x_mm":inner,"contact_box_source_mm":[stock[0]+running(),side()-running(),y-r,y+r,contact,head],
            "root_radius_mm":running()*2.0,"contact_gap_mm":contact-stock[5],
            "reason":"Pull the exposed fork to break its neck at the roof; the trunk stays beside the Pisco pocket and branches below it."}));
    }
    Ok(trees)
}

fn meter_print_stock() -> (Bounds, P2) {
    let frame = &layout().parts.digiten_flow;
    let centre = frame.point([meter::BODY_CENTER_X,0.0,meter::BODY_CENTER_Z]);
    let port = frame.point([0.0;3]);
    let wx = |y: f64| frame.point([meter::BODY_CENTER_X,y,meter::BODY_CENTER_Z])[0];
    let mx = wx(meter::FLANGE_Y)-METER_AIR;
    let ty = frame.translation_mm[1];
    let cap = [ty+METER_CAP[0],ty+METER_CAP[1]];
    let s = station(0.0,port[2]+meter::PORT_COLLAR_RADIUS+METER_AIR-centre[2]+WALL,
                    cap,0.0,wx(meter::UNDERSIDE_Y)-METER_AIR-mx);
    ([mx,side()+INTO,ty+METER_SEAT[0],ty+METER_SEAT[1],centre[2]-s.outer,centre[2]+s.outer],cap)
}

fn asse_station() -> Station {
    let frame = &layout().rear_plumbing.chain_frame;
    let c = running();
    let centre = frame.point([0.0, 0.0, asse::BODY_CENTER_Z]);
    let along = |x: f64| frame.point([x, 0.0, asse::BODY_CENTER_Z])[1];
    let span = [along(asse::BONNET_X) - slip(), along(profiles().asse.gagira_fore_x) - slip()];
    let profile = runs(&profiles().asse.seat_runs, frame, 0, c);
    let widest = widest(&profile, span).chain(asse::WRENCHES.iter().map(|w| w.widest + c))
        .fold(f64::NEG_INFINITY, f64::max);
    let split = centre[2] + c;
    station(centre[0], half_width(widest, split, centre[2]) + WALL, span, split, centre[2] - REAR_ROOT_DROP)
}

fn pisco_station() -> Station {
    let frame = &layout().rear_plumbing.gas_frame;
    let c = running();
    let mouth = frame.point([0.0; 3]);
    let span = [mouth[1] - pisco_exterior().component_ranges_mm.outlet_collet[0] + c + 0.01, rear() - WALL - c];
    let profile = runs(&profiles().pisco.seat_runs, frame, 2, c + PISCO_RADIAL_RELIEF);
    let widest = widest(&profile, span).fold(f64::NEG_INFINITY, f64::max);
    let split = mouth[2] + PISCO_SPLIT_RISE;
    station(mouth[0], half_width(widest, split, mouth[2]) + (WALL - REACH - c), span, split,
            mouth[2] - REAR_ROOT_DROP)
}

/// Both flank pockets of one station: beside the ledge from the split to the bearing plane,
/// beside the neck above it to the pocket's ceiling, and the round at the wing's root. The
/// station's ends are the cap's shoulders.
fn pockets(g: &mut Graph, s: &Station) -> Vec<Shape> {
    let a = running();
    let mut out = Vec::new();
    for side in [-1.0, 1.0] {
        let far = s.axis_x + side * (s.outer + 1.0);
        let (ledge, neck) = (s.axis_x + side * s.ledge, s.axis_x + side * s.neck);
        let near = s.axis_x + side * (s.inner - s.root_radius - a);
        for (edge, z0, z1) in [(ledge, s.split - 1.0, s.bearing), (neck, s.bearing, s.ceiling),
                               (near, s.root - a, s.root + s.root_radius + a)] {
            let (x0, x1) = sorted(edge, far);
            out.push(g.box_([x0, x1, s.y0 - a, s.y1 + a, z0, z1]));
        }
    }
    out
}

/// A circle's half-chord at height `z` off its axis.
fn half_width(radius: f64, z: f64, axis_z: f64) -> f64 {
    (radius * radius - (z - axis_z) * (z - axis_z)).max(0.0).sqrt()
}

/// A seat's turned runs in the machine's frame: the reference's runs along its axial coordinate,
/// which the frame's `column` carries aft, each grown by `air`.
fn runs(seat_runs: &[P3], frame: &Pose, column: usize, air: f64) -> Vec<P3> {
    assert!(frame.rotation.map(|row| row[column]) == [0.0, -1.0, 0.0],
            "the radial seat profile needs its declared axial reference orientation");
    let t = frame.translation_mm[1];
    seat_runs.iter().rev().map(|&[lo, hi, r]| [t - hi, t - lo, r + air]).collect()
}

/// The widest of the runs a cap's span reaches.
fn widest(runs: &[P3], [y0, y1]: P2) -> impl Iterator<Item = f64> + '_ {
    runs.iter().filter(move |r| r[1] >= y0 - CAP_OVERLAP && r[0] <= y1 + CAP_OVERLAP).map(|r| r[2])
}

fn turned(g: &mut Graph, profile: Vec<P3>, axis: P2) -> Shape {
    let radius = profile.iter().map(|r| r[2]).fold(f64::NEG_INFINITY, f64::max);
    let bounds = [axis[0] - radius, axis[0] + radius, profile[0][0], profile[profile.len() - 1][1],
                  axis[1] - radius, axis[1] + radius];
    g.add(Op::TurnedRuns { centre: axis, profile }, vec![], Some(bounds))
}

/// A wrench's hex along Y about the axis, clocked, its corners turned to `corner`.
fn hex_prism(g: &mut Graph, axis: P2, apothem: f64, clock: f64, [y0, y1]: P2, corner: f64) -> Shape {
    let rr = apothem / (std::f64::consts::PI / 6.0).cos();
    let points = (0..6)
        .map(|i| {
            let a = (clock + 60.0 * i as f64).to_radians();
            [axis[0] + rr * a.sin(), axis[1] - rr * a.cos()]
        })
        .collect();
    let hex = g.prism(1, y0, y1, points);
    let round = g.cylinder(1, corner, axis[0], axis[1], y0, y1);
    g.intersect(hex, &[round])
}

/// Linear interpolation along a profile, held at its ends; a repeated station takes its later
/// point.
fn interpolate(points: &[P2], x: f64) -> f64 {
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
fn clearance_profile(profile: &[P2], radial: f64, axial: f64) -> Vec<P2> {
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

/// The ASSE chain's seat: its turned body and both wrenches' hexes, with a bevel at the lower
/// fore corner for the neighbouring Pisco cap's service path.
fn asse(g: &mut Graph) -> Shape {
    let frame = &layout().rear_plumbing.chain_frame;
    let (c, s) = (running(), slip());
    let centre = frame.point([0.0, 0.0, asse::BODY_CENTER_Z]);
    let axis = [centre[0], centre[2]];
    let along = |x: f64| frame.point([x, 0.0, asse::BODY_CENTER_Z])[1];
    let profile = runs(&profiles().asse.seat_runs, frame, 0, c);
    let cap_y = [along(asse::BONNET_X) - s, along(profiles().asse.gagira_fore_x) - s];
    let wrenches = asse::WRENCHES.map(|w| {
        let (y0, y1) = sorted(along(w.x[0]), along(w.x[1]));
        ([y0, y1], w.across_flats / 2.0, w.clock + asse::TURN, w.widest)
    });
    let split = axis[1] + c;
    let st = asse_station();
    let stock = g.box_([axis[0] - st.outer, axis[0] + st.outer, cap_y[0] - c - WALL, rear() + INTO, split,
                        ceiling() + INTO]);
    let mut room = turned(g, profile, axis);
    for ([y0, y1], apothem, clock, corner) in wrenches {
        let lo = ((y0 - THREAD) * 10.0).floor() / 10.0;
        let hi = ((y1 + THREAD) * 10.0).ceil() / 10.0;
        let hex = hex_prism(g, axis, apothem + c, clock, [lo - SLIDE, hi], corner + c);
        room = g.union(room, &[hex]);
    }
    let x = st.axis_x + st.neck + WALL;
    let far = st.axis_x + st.outer + WALL + 1.0;
    let corner = g.prism(1, st.y0 - c - WALL - 0.1, st.y0 + c,
                         vec![[x, split - 0.1], [far, split - 0.1], [far, split + WALL], [x + WALL, split + WALL]]);
    let mut cuts = vec![room];
    cuts.extend(pockets(g, &st));
    cuts.push(corner);
    g.cut(stock, &cuts)
}

/// The Pisco's runs with one ring bearing at its widest station, within its insertion sweep.
fn bearing_profile(runs: &[P3], profile: &[P2], mouth_y: f64) -> Vec<P3> {
    let [z, r] = profile.iter().copied().reduce(|best, p| if p[1] > best[1] { p } else { best })
        .expect("the Pisco's fitted exterior has a profile");
    let (y0, y1) = (mouth_y - z - PISCO_BEARING_LENGTH / 2.0, mouth_y - z + PISCO_BEARING_LENGTH / 2.0);
    let bearing = r + PISCO_CAP_FIT;
    let mut out = Vec::new();
    for &[a, b, radius] in runs {
        let mut cuts = vec![a, b];
        cuts.extend([y0, y1].into_iter().filter(|&v| a < v && v < b));
        cuts.sort_by(f64::total_cmp);
        cuts.dedup();
        for w in cuts.windows(2) {
            let mid = (w[0] + w[1]) / 2.0;
            out.push([w[0], w[1], if y0 <= mid && mid <= y1 { bearing } else { radius }]);
        }
    }
    out
}

/// The Pisco's seat: full receiver walls beside its widened passage, its cap's span from the
/// outlet neck to a full rear end wall, and its fore flank exits open below the bearing plane.
fn pisco(g: &mut Graph) -> Shape {
    let frame = &layout().rear_plumbing.gas_frame;
    let c = running();
    let mouth = frame.point([0.0; 3]);
    let (axis, mouth_y) = ([mouth[0], mouth[2]], mouth[1]);
    let profile = runs(&profiles().pisco.seat_runs, frame, 2, c + PISCO_RADIAL_RELIEF);
    let exterior = pisco_exterior();
    let cap_y = [mouth_y - exterior.component_ranges_mm.outlet_collet[0] + c + 0.01, rear() - WALL - c];
    let split = axis[1] + PISCO_SPLIT_RISE;
    let st = pisco_station();
    let profile = bearing_profile(&profile, &exterior.profile_z_radius_mm, mouth_y);
    let stock = g.box_([axis[0] - st.outer, axis[0] + st.outer, cap_y[0] - c - WALL, rear() + INTO, split,
                        ceiling() + INTO]);
    let room = turned(g, profile, axis);
    let half = st.outer + PISCO_SERVICE_FLANK + c;
    let service = g.box_([axis[0]-half,axis[0]+half,st.y0-c-WALL-1.0,st.y0+c,
                          split-1.0,st.bearing-WALL]);
    let mut cuts = vec![room];
    cuts.extend(pockets(g, &st));
    cuts.push(service);
    g.cut(stock, &cuts)
}

fn stadium(g: &mut Graph, y: f64, z: f64, radius: f64, span: P2, fore: f64, aft: f64) -> Shape {
    let bounds = [span[0], span[1], y - fore - radius, y + aft + radius, z - radius, z + radius];
    g.add(Op::StadiumX { y, z, radius, fore, aft, span }, vec![], Some(bounds))
}

/// The meter's seat on the east flank: its housing, cover bosses and screw heads swept aft along
/// its slide, the soda port's collar sleeves, and the chamber its wire lead leaves through. Its
/// station stands across X, so its pockets turn a quarter about Y onto its axis.
fn meter(g: &mut Graph) -> Shape {
    let frame = &layout().parts.digiten_flow;
    let at = |p: P3| frame.point(p);
    let centre = at([meter::BODY_CENTER_X, 0.0, meter::BODY_CENTER_Z]);
    let (my, mz) = (centre[1], centre[2]);
    let port = at([0.0; 3]);
    let soda = [port[0], port[2]];
    let wx = |y: f64| at([meter::BODY_CENTER_X, y, meter::BODY_CENTER_Z])[0];
    let wy = |x: f64| at([x, 0.0, 0.0])[1];
    let air = METER_AIR;
    let mx = wx(meter::FLANGE_Y) - air;
    let (fore, aft, fit) = (SLIDE + VAR, METER_HOUSING_FIT, METER_HOUSING_FIT);
    let x0 = mx - 1.0;
    let housing: Vec<P2> = clearance_profile(&meter::HOUSING_PROFILE, fit, fit).into_iter().map(|[y, r]| [wx(y), r]).collect();
    let radius = housing.iter().map(|p| p[1]).fold(f64::NEG_INFINITY, f64::max);
    let bounds = [housing[0][0], housing[housing.len() - 1][0], my - fore - radius, my + aft + radius,
                  mz - radius, mz + radius];
    let mut cup = g.add(Op::StadiumProfileX { y: my, z: mz, fore, aft, points: housing }, vec![], Some(bounds));
    for dy in [-meter::BOSS_X, meter::BOSS_X] {
        for dz in [-meter::BOSS_Z, meter::BOSS_Z] {
            let boss = stadium(g, my + dy, mz + dz, meter::BOSS_RADIUS + fit,
                               [wx(meter::BOSS_Y[0]) - fit, wx(meter::BOSS_Y[1]) + fit], fore, aft);
            let head = stadium(g, my + dy, mz + dz, meter::SCREW_HEAD_RADIUS + fit,
                               [wx(meter::SCREW_HEAD_Y[0]) - fit, wx(meter::SCREW_HEAD_Y[1]) + fit], fore, aft);
            cup = g.union(cup, &[boss, head]);
        }
    }
    let collar = meter::PORT_COLLAR_RADIUS;
    for sign in [-1.0, 1.0] {
        let (ya, yb) = sorted(wy(sign * meter::PORT_NECK_END), wy(sign * meter::PORT_COLLAR_END));
        let sleeve = g.cylinder(1, collar + air, soda[0], soda[1], ya - fore - air, yb + (VAR + slip()));
        let reach = g.box_([x0, soda[0] + collar + 1.0, ya - fore - 2.0, yb + aft + 2.0, soda[1] - collar - 1.0,
                            soda[1] + collar + 1.0]);
        let sleeve = g.intersect(sleeve, &[reach]);
        cup = g.union(cup, &[sleeve]);
    }
    let root = at(meter::WIRE_ROOT);
    let half = meter::WIRE_ROOT_WIDTH / 2.0;
    let ty = frame.translation_mm[1];
    let cap_y = [ty + METER_CAP[0], ty + METER_CAP[1]];
    let west = wx(meter::UNDERSIDE_Y);
    let st = station(0.0, soda[1] + collar + air - mz + WALL, cap_y, 0.0, west - air - mx);
    let wire = g.box_([x0, wx(meter::WIRE_ROOT[1] + meter::WIRE_ROOT_DEPTH / 2.0) + air, wy(-half) - fore - air,
                       wy(half) + aft + air, (root[2] - meter::WIRE_DROP).min(mz - st.neck),
                       root[2] + meter::WIRE_BOSS_LEN + air]);
    cup = g.union(cup, &[wire]);
    let stock = g.box_([mx, side() + INTO, ty + METER_SEAT[0], ty + METER_SEAT[1], mz - st.outer, mz + st.outer]);
    let mut cuts = vec![cup];
    for pocket in pockets(g, &st) {
        let pocket = g.rotate(pocket, [0.0; 3], [0.0, 1.0, 0.0], 90.0);
        cuts.push(g.translate(pocket, [mx, 0.0, mz]));
    }
    g.cut(stock, &cuts)
}

/// The water regulator's seat: built in its snap's frame round the measured profile, then turned
/// a quarter about Z onto the ceiling.
fn regulator(g: &mut Graph) -> Shape {
    let l = layout();
    let mount = &l.rear_plumbing.regulator_mount;
    let (st, axis) = (&mount.station, mount.axis);
    let [a, b] = mount.seat_y;
    let b = b.max(st.y1 + running() + WALL);
    let stock = g.box_([axis[0] - st.outer, axis[0] + st.outer, a, b, SPLIT, back_top_ceiling_face() + INTO]);
    let fit = &mount.cavity_fit;
    let profile = clearance_profile(regulator_profile(), fit.receiver_radial_mm, fit.axial_mm);
    let radius = profile.iter().map(|p| p[1]).fold(f64::NEG_INFINITY, f64::max);
    let bounds = [profile[0][0], profile[profile.len() - 1][0], -radius, radius, -radius, radius];
    let room = g.add(Op::RadialProfile { points: profile }, vec![], Some(bounds));
    // The seat's frame is the regulator's snapshot turned a quarter back about Z.
    let pose = &l.snapshots.reg;
    let [r0, r1, r2] = pose.rotation;
    let [t0, t1, t2] = pose.translation_mm;
    let room = place(g, room, [r1, r0.map(|v| -v), r2], [t1, -t0, t2]);
    let mut cuts = vec![room];
    cuts.extend(pockets(g, st));
    let seat = g.cut(stock, &cuts);
    g.rotate(seat, [0.0; 3], [0.0, 0.0, 1.0], 90.0)
}
