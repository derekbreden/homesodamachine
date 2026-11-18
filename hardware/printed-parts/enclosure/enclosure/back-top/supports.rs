//! The seats back-top carries for the rear plumbing: the ASSE chain's, the Pisco regulator's,
//! the flow meter's and the water regulator's. Each is a block cut round its part's measured
//! profile, with the flank pockets its snap cap's spring wings ride in.
use crate::catalog::{clearance, running, slip};
use crate::layout::{Pose, Station, layout, snap_tip_air, snap_tip_rise, PISCO_WING_AFT_Y, REAR_SNAP_CHAMFER_SLOPE, REAR_SNAP_WALL_TOP_Z};
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
/// bearing fit and the bearing's length.
const PISCO_SPLIT_RISE: f64 = 7.0;
const PISCO_RADIAL_RELIEF: f64 = 0.25;
const PISCO_CAP_FIT: f64 = 0.15;
const PISCO_BEARING_LENGTH: f64 = 3.0;
/// The meter's air at its spring station, collar passages and wire chamber; its housing's fit;
/// how far the soda union's stub may leave it aft of its station; and its seat's and cap's spans
/// about its station.
const METER_AIR: f64 = 0.75;
const METER_HOUSING_FIT: f64 = 0.15;
const VAR: f64 = 0.5;
const METER_FIT_SWEEP: P2 = [SLIDE + VAR, METER_HOUSING_FIT];
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
        hsm_enclosure_numbers::input::json("hardware/printed-parts/enclosure/enclosure/rear-seat-profiles.json").expect("the rear seat profiles parse")
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
            hsm_enclosure_numbers::input::json("hardware/reference/compact-inline-candidates/dimensions.json")
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
            hsm_enclosure_numbers::input::json("hardware/reference/yzmsz-water-regulator/reference-parameters.json")
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

/// The rear snap bay has one ceiling floor between the flanks and flush to the rear wall.
pub fn ceiling_bay_bounds() -> Bounds {
    let (asse, pisco) = (asse_station(), pisco_station());
    let [west, east] = back_top_flank_face();
    [west, east, asse.y0.min(pisco.y0) - running() - WALL, rear(),
     back_top_ceiling_face() - INTO, ceiling_floor_z()]
}

/// The common ceiling floor clears the complete ASSE and Pisco wing points.
pub fn ceiling_floor_z() -> f64 {
    asse_station().ceiling.max(pisco_station().ceiling)
}

/// Ceiling-mounted stock reaches into the roof skin above the common pocket.
pub fn ceiling_anchor_z() -> f64 {
    ceiling_floor_z() + INTO
}

/// The rear wall beside the Pisco keeps its existing plan up to the common wall plane.
pub fn rear_snap_wall_bounds() -> Bounds {
    let s = pisco_station();
    [s.axis_x + s.outer, side(), s.y1 + running(), rear(),
     ceiling_bay_bounds()[4] - INTO, REAR_SNAP_WALL_TOP_Z]
}

/// The meter and water regulator tip pockets stay clear through the stock they join.
pub fn tip_clearances(g: &mut Graph) -> Vec<Shape> {
    let mut cuts = Vec::new();
    let frame = &layout().parts.digiten_flow;
    let centre = frame.point([meter::BODY_CENTER_X, 0.0, meter::BODY_CENTER_Z]);
    let port = frame.point([0.0; 3]);
    let wx = |y| frame.point([meter::BODY_CENTER_X, y, meter::BODY_CENTER_Z])[0];
    let mx = wx(meter::FLANGE_Y) - METER_AIR;
    let ty = frame.translation_mm[1];
    let mut st = station(0.0, port[2] + meter::PORT_COLLAR_RADIUS + METER_AIR - centre[2] + WALL,
                     [ty + METER_CAP[0], ty + METER_CAP[1]], 0.0,
                     wx(meter::UNDERSIDE_Y) - METER_AIR - mx);
    st.ceiling = side() - mx;
    for pocket in meter_catch_pockets(g, &st) {
        let pocket = g.rotate(pocket, [0.0; 3], [0.0, 1.0, 0.0], 90.0);
        cuts.push(g.translate(pocket, [mx, 0.0, centre[2]]));
    }
    for pocket in tip_pockets(g, &layout().rear_plumbing.regulator_mount.station) {
        cuts.push(g.rotate(pocket, [0.0; 3], [0.0, 0.0, 1.0], 90.0));
    }
    cuts
}

fn tip_pockets(g: &mut Graph, st: &Station) -> Vec<Shape> {
    [-1.0, 1.0].into_iter()
        .map(|side| catch_pocket(g, st, side, [st.y0 - running(), st.y1 + running()]))
        .collect()
}

/// A catch's chamfer rises from its edge to its wall at the shared snap slope.
fn corbel_slope() -> f64 {
    REAR_SNAP_CHAMFER_SLOPE
}

/// How far a corbelled catch rises from the ledge's edge to the neck.
fn corbel_rise(s: &Station) -> f64 {
    (s.ledge - s.neck) * corbel_slope()
}

/// One flank's pocket above the bearing plane, from the neck out past the wing to the pocket's
/// ceiling. A corbelled flank keeps the corbel, which climbs the neck from the ledge's edge.
fn catch_pocket(g: &mut Graph, s: &Station, side: f64, [y0, y1]: P2) -> Shape {
    let at = |x: f64| s.axis_x + side * x;
    g.prism(1, y0, y1, vec![[at(s.neck), s.ceiling], [at(s.outer + 1.0), s.ceiling], [at(s.outer + 1.0), s.bearing],
                             [at(s.ledge), s.bearing], [at(s.neck), s.bearing + corbel_rise(s)]])
}

/// Each sideways meter channel returns to the flank on a matching bevel beyond the hook.
fn meter_catch_pockets(g: &mut Graph, s: &Station) -> Vec<Shape> {
    let middle = (s.bearing + s.ceiling + (s.ledge - s.outer) / corbel_slope()) / 2.0;
    let near = s.ledge - (middle - s.bearing) * corbel_slope();
    [-1.0, 1.0].into_iter().map(|side| {
        let at = |x: f64| s.axis_x + side * x;
        g.prism(1, s.y0 - running(), s.y1 + running(),
            vec![[at(s.outer), s.ceiling], [at(s.outer + 1.0), s.ceiling],
                 [at(s.outer + 1.0), s.bearing], [at(s.ledge), s.bearing], [at(near), middle]])
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

/// A rear receiver interior that prints with no support: its name, its bounds, and which of its
/// faces, low then high along X, Y and Z, the box that keeps supports out grows past; a top that
/// grows reaches the roof. A face beside a reachable catch, an exposed shoulder or a supported
/// lip stays put, so their support stands clear.
pub struct Interior {
    pub name: &'static str,
    pub bounds: Bounds,
    pub grows: [bool; 6],
    pub reason: &'static str,
}

/// Fitted rooms and chamfered wing channels stay clear of support; accessible body floors
/// retain their own support targets.
pub fn interiors() -> Vec<Interior> {
    let a = running();
    let (asse, pisco) = (asse_station(), pisco_station());
    let whole = |s: &Station| [s.axis_x - s.outer - a, s.axis_x + s.outer + a, s.y0 - a, s.y1 + a, s.split - a, s.ceiling + a];
    let (stock, cap, meter) = meter_print_stock();
    let lower_pocket = [stock[0], stock[1], cap[0] - a, cap[1] + a, stock[4],
                        meter_wire_chamber_bounds()[4] - 2.0 * a];
    let mount = &layout().rear_plumbing.regulator_mount;
    let [y0, y1] = regulator_seat();
    let regulator_room = [-y1, -y0, mount.axis[0] - mount.station.outer - a, mount.axis[0] + mount.station.outer + a,
                          SPLIT, back_top_ceiling_face() + INTO];
    let middle = (meter.bearing + meter.ceiling + meter.ledge - meter.outer) / 2.0;
    let near = meter.ledge - (middle - meter.bearing);
    let upper_pocket = [stock[0] + meter.bearing, side(), cap[0] - a, cap[1] + a,
                        stock[5] - meter.outer + near - a, stock[5] + a];
    vec![
        Interior { name: "ASSE receiver", bounds: whole(&asse), grows: [true; 6],
                   reason: "The fitted room and both chamfered catches print without support." },
        Interior { name: "Pisco receiver", bounds: whole(&pisco), grows: [true; 6],
                   reason: "The fitted room and both corbelled catches print without support." },
        Interior { name: "Flow meter lower cap pocket", bounds: lower_pocket,
                   grows: [true, true, false, false, true, false],
                   reason: "Keep support out of the lower hook pocket below the wire chamber floor." },
        Interior { name: "Flow meter upper cap pocket", bounds: upper_pocket, grows: [false; 6],
                   reason: "The catch and its return to the flank are chamfered, with no flat pocket floor to support." },
        Interior { name: "Water regulator receiver", bounds: regulator_room, grows: [true, true, false, false, true, true],
                   reason: "The fitted room and both chamfered catches print without support." },
    ]
}

/// The meter's downhill slide and wire floors face the bed in the ceiling-down pose.
/// Supports peel away through the receiver's open west face.
pub fn meter_floor_targets() -> Vec<(String, Bounds)> {
    let frame = &layout().parts.digiten_flow;
    let centre = frame.point([meter::BODY_CENTER_X, 0.0, meter::BODY_CENTER_Z]);
    let (stock, _, _) = meter_print_stock();
    let [fore, aft] = METER_FIT_SWEEP;
    let fit = METER_HOUSING_FIT;
    let a = running();
    let mut targets = Vec::new();
    for (channel, radius, span) in [
        ("boss channel", meter::BOSS_RADIUS, meter::BOSS_Y),
        ("screw-head channel", meter::SCREW_HEAD_RADIUS, meter::SCREW_HEAD_Y),
    ] {
        let [x0, x1] = span.map(|y| frame.point([meter::BODY_CENTER_X, y, meter::BODY_CENTER_Z])[0]);
        let radius = radius + fit;
        let floor = centre[2] - meter::BOSS_Z - radius;
        for (end, dy) in [("fore", -meter::BOSS_X), ("aft", meter::BOSS_X)] {
            let y = centre[1] + dy;
            targets.push((
                format!("Accessible flow meter {end} {channel} floor"),
                [(x0 - fit).max(stock[0]), x1 + fit, y - fore - radius, y + aft + radius, floor - a, floor + a],
            ));
        }
    }
    let [_, x1, y0, y1, floor, _] = meter_wire_chamber_bounds();
    targets.push(("Accessible flow meter wire chamber floor".into(), [stock[0], x1, y0, y1, floor - a, floor + a]));
    targets
}

/// The water regulator seat's span along its own axis, its far end a wall past the cap.
fn regulator_seat() -> P2 {
    let mount = &layout().rear_plumbing.regulator_mount;
    let [a, b] = mount.seat_y;
    [a, b.max(mount.station.y1 + running() + WALL)]
}

/// The meter receiver's stock, its cap's span, and its snap station about the meter's centre.
fn meter_print_stock() -> (Bounds, P2, Station) {
    let frame = &layout().parts.digiten_flow;
    let centre = frame.point([meter::BODY_CENTER_X,0.0,meter::BODY_CENTER_Z]);
    let port = frame.point([0.0;3]);
    let wx = |y: f64| frame.point([meter::BODY_CENTER_X,y,meter::BODY_CENTER_Z])[0];
    let mx = wx(meter::FLANGE_Y)-METER_AIR;
    let ty = frame.translation_mm[1];
    let cap = [ty+METER_CAP[0],ty+METER_CAP[1]];
    let mut s = station(0.0,port[2]+meter::PORT_COLLAR_RADIUS+METER_AIR-centre[2]+WALL,
                    cap,0.0,wx(meter::UNDERSIDE_Y)-METER_AIR-mx);
    s.ceiling = side() - mx;
    ([mx,side()+INTO,ty+METER_SEAT[0],ty+METER_SEAT[1],centre[2]-s.outer,centre[2]+s.outer],cap,s)
}

/// The cut for the lead's exit, shared by the receiver and its print support request.
fn meter_wire_chamber_bounds() -> Bounds {
    let frame = &layout().parts.digiten_flow;
    let (stock, _, station) = meter_print_stock();
    let centre = frame.point([meter::BODY_CENTER_X, 0.0, meter::BODY_CENTER_Z]);
    let root = frame.point(meter::WIRE_ROOT);
    let half = meter::WIRE_ROOT_WIDTH / 2.0;
    let [fore, aft] = METER_FIT_SWEEP;
    let air = METER_AIR;
    [stock[0] - 1.0,
     side(),
     frame.point([-half, 0.0, 0.0])[1] - fore - air,
     frame.point([half, 0.0, 0.0])[1] + aft + air,
     (root[2] - meter::WIRE_DROP).min(centre[2] - station.neck),
     root[2] + meter::WIRE_BOSS_LEN + air]
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

/// Each wing lane opens beside its ledge and into the catch room above it; the ends locate the cap.
fn wing_lanes(g: &mut Graph, s: &Station) -> Vec<Shape> {
    let a = running();
    let mut out = Vec::new();
    for side in [-1.0, 1.0] {
        let far = s.axis_x + side * (s.outer + 1.0);
        let ledge = s.axis_x + side * s.ledge;
        let (x0, x1) = sorted(ledge, far);
        out.push(g.box_([x0, x1, s.y0 - a, s.y1 + a, s.split - 1.0, s.bearing]));
    }
    out
}

/// The vertical rear receivers combine open wing lanes with chamfered catches.
fn pockets(g: &mut Graph, s: &Station) -> Vec<Shape> {
    let mut out = wing_lanes(g, s);
    out.extend(tip_pockets(g, s));
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

/// The ASSE chain's seat keeps plain end walls around its turned body, wrench flats and wing lanes.
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
    let mut cuts = vec![room];
    cuts.extend(pockets(g, &st));
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

/// The Pisco's seat has plain end walls around the fitted passage and angled wing catches.
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
    let mut cuts = vec![room];
    let mut wing = st;
    wing.y1 = PISCO_WING_AFT_Y;
    cuts.extend(pockets(g, &wing));
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
    let [fore, aft] = METER_FIT_SWEEP;
    let fit = METER_HOUSING_FIT;
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
    let ty = frame.translation_mm[1];
    let cap_y = [ty + METER_CAP[0], ty + METER_CAP[1]];
    let west = wx(meter::UNDERSIDE_Y);
    let mut st = station(0.0, soda[1] + collar + air - mz + WALL, cap_y, 0.0, west - air - mx);
    st.ceiling = side() - mx;
    let wire = g.box_(meter_wire_chamber_bounds());
    cup = g.union(cup, &[wire]);
    let stock = g.box_([mx, side() + INTO, ty + METER_SEAT[0], ty + METER_SEAT[1], mz - st.outer, mz + st.outer]);
    // The continuous roof bevel carries both end shoulders from the flank.
    let corbels: Vec<Shape> = [meter_roof_corbel()].into_iter()
        .map(|[x0, x1, y0, y1, top]| g.prism(1, y0, y1, vec![[x0, top], [x1, top], [x1, top + (x1 - x0) * corbel_slope()]]))
        .collect();
    let stock = g.union(stock, &corbels);
    let mut cuts = vec![cup];
    let mut lanes = wing_lanes(g, &st);
    lanes.extend(meter_catch_pockets(g, &st));
    for pocket in lanes {
        let pocket = g.rotate(pocket, [0.0; 3], [0.0, 1.0, 0.0], 90.0);
        cuts.push(g.translate(pocket, [mx, 0.0, mz]));
    }
    g.cut(stock, &cuts)
}

/// The meter roof grows from its complete open edge to the flank on a continuous bevel.
fn meter_roof_corbel() -> [f64; 5] {
    let (stock, _, _) = meter_print_stock();
    [stock[0], stock[1], stock[2], stock[3], stock[5]]
}

/// The water regulator's seat: built in its snap's frame round the measured profile, then turned
/// a quarter about Z onto the ceiling.
fn regulator(g: &mut Graph) -> Shape {
    let l = layout();
    let mount = &l.rear_plumbing.regulator_mount;
    let (st, axis) = (&mount.station, mount.axis);
    let [a, b] = regulator_seat();
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
