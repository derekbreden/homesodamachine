//! This concept study shuts off soda at the pull-out tip with silicone as the only made part the water touches.
use anyhow::Result;
use hsm_faucet::Gooseneck;
use hsm_faucet_numbers::shell;
use hsm_kernel::{Loop, Path, Plane, Profile, Solid, V3, v2, v3};
use hsm_sandbox::{material, out, part, show};
use std::f64::consts::{PI, TAU};
use std::path::Path as Dir;

#[allow(dead_code)]
#[path = "../../../assembly/calibration_inputs.rs"]
mod calibration_inputs;

type Color = [f64; 3];
const MOTOR: Color = [0.13, 0.17, 0.20];
const INLET: Color = [0.03, 0.29, 0.63];
const OUTLET: Color = [0.02, 0.58, 0.53];

// Stations run along the valve axis from the dispense face back into the grip, in mm.
const MOUTH: f64 = -4.91;
const MOUNT_FACE: f64 = -2.55;
const BARREL_R: f64 = 5.90;
const CARRIER_R: f64 = 5.7;
/// The silicone sleeve around the tube socket; the housing wraps it 0.75 mm thick, clear of flavor line A and the display.
const LOBE_R: f64 = 2.5;
const BODY_R: f64 = 4.6;
const POCKET_R: f64 = BODY_R + 0.05;
const SPOUT_R: f64 = 2.5;
const SPOUT_BORE_R: f64 = 1.75;
const PLENUM_R: f64 = 3.6;
/// The seat lip, the clamp rim and the diaphragm's wet face share this plane.
const SEAT_S: f64 = 8.4;
const PORT_R: f64 = 1.4;
const LIP_R: f64 = 2.0;
const CHAMBER_R: f64 = 3.4;
const CHAMBER_FLOOR: f64 = 7.3;
const HOLE_RING: f64 = 2.7;
const HOLE_R: f64 = 0.9;
const SOCKET_DEPTH: f64 = 4.6;
const BOSS_R: f64 = 2.4;
const BOSS_T: f64 = 1.2;
const WEB_T: f64 = 0.5;
/// The diaphragm's rim as the carrier compresses it.
const RIM_T: f64 = 1.0;
const CLAMP_S: f64 = SEAT_S + RIM_T;
const HOUSING_END: f64 = 10.4;
const NOSE_S: f64 = SEAT_S + BOSS_T;
const FLANGE_S: f64 = 14.0;
const FLANGE_END: f64 = 15.2;
const STOP_S: f64 = 13.6;
const SPRING_SEAT_S: f64 = 27.0;
const BUSHING_BORE_S: f64 = 29.0;
const CUP_S: f64 = 35.5;
const CUP_R: f64 = 7.5;
/// The M2 × 8 low-head screws thread into the housing lugs and seat in counterbores in the carrier lugs.
const HEAD_S: f64 = 13.0;
const HEAD_R: f64 = 1.75;
const BEAD_S: f64 = 10.9;
/// Where the tube's end stops in the barb's angled socket, along the socket from the hose axis.
const TIP_STOP: f64 = -1.90;
const CLIP_S: f64 = 11.2;
const CLIP_END: f64 = 12.2;
/// Diaphragm lift at full flow, and the pusher's travel with its free play.
const LIFT: f64 = 0.70;
const STROKE: f64 = 0.75;
const SOCKET: V3 = v3(5.55, 0., 4.38);
const BYPASS: V3 = v3(8.1, 0., 5.62);
const TIE: V3 = v3(-4.48, 0., 4.45);
const TUBE_R: f64 = 25.4 * 5. / 64.;
const TUBE_ID_R: f64 = TUBE_R - 25.4 * 0.010;
const MOTOR_S: f64 = 36.475;
const MOTOR_LEN: f64 = 25.4 * 0.550;
const MOTOR_R: f64 = 25.4 * 0.520 / 2.;
const BUSH_S: f64 = MOTOR_S - 25.4 * 0.250;
const MOTOR_END: f64 = MOTOR_S + MOTOR_LEN;
const CUP_END: f64 = MOTOR_END + 0.85;
const PIN_S: f64 = MOTOR_S - 25.4 * 0.562 - STROKE;
const CLEVIS_S: f64 = PIN_S - 25.4 * 0.125;
const SLOT: f64 = 25.4 * 0.062;
const SPRING_R: f64 = 3.95;
const WIRE_R: f64 = 0.25;
const ACTIVE_TURNS: f64 = 6.;
const SPRING_PRELOAD_N: f64 = 4.4;
/// Load left pressing the boss onto the lip at the pressure the valve still holds.
const SEAT_MARGIN_N: f64 = 1.0;
/// Ledex 195200-237 typical pull, inches of stroke against ounces, from its data sheet.
const LEDEX_INTERMITTENT: [(f64, f64); 8] =
    [(0.010, 22.0), (0.020, 17.0), (0.030, 14.7), (0.040, 11.9), (0.050, 9.4), (0.060, 7.5), (0.080, 5.1), (0.100, 3.6)];
const LEDEX_CONTINUOUS: [(f64, f64); 8] =
    [(0.010, 16.5), (0.020, 10.4), (0.030, 6.2), (0.040, 4.2), (0.050, 3.1), (0.060, 2.2), (0.080, 1.5), (0.100, 1.0)];
const NEWTONS_PER_OUNCE: f64 = 0.278_014;

struct Piece {
    name: &'static str,
    color: Color,
    solid: Solid,
    exploded: V3,
    section: bool,
}

struct Palette {
    silicone: Color,
    petgf: Color,
    steel: Color,
}

fn add(pieces: &mut Vec<Piece>, name: &'static str, color: Color, solid: Solid, exploded: V3, section: bool) {
    pieces.push(Piece { name, color, solid, exploded, section });
}

fn axial(radius: f64, start: f64, end: f64) -> Result<Solid> {
    Solid::cylinder(V3::Y * start, V3::Y, radius, end - start)
}

fn bore(a: V3, b: V3, radius: f64) -> Result<Solid> {
    Solid::cylinder(a, b - a, radius, (b - a).norm())
}

fn annulus(outer: f64, inner: f64, a: f64, b: f64) -> Result<Solid> {
    axial(outer, a, b)?.cut(&axial(inner, a - 0.05, b + 0.05)?)
}

fn turn(profile: &[(f64, f64)]) -> Result<Solid> {
    let points: Vec<_> = profile.iter().map(|&(r, s)| v2(r, s)).collect();
    Plane::XY.revolve(&Profile::polygon(&points), 360., v2(0., 0.), v2(0., 1.))
}

fn torus(radius: f64, section_radius: f64, station: f64) -> Result<Solid> {
    Solid::torus(V3::Y * station, V3::Y, radius, section_radius)
}

fn radial(degrees: f64) -> V3 {
    let a = degrees.to_radians();
    v3(a.cos(), 0., a.sin())
}

/// The supply drilling runs in the half plane of the tube socket; the three outlet holes stand clear of it.
fn socket_azimuth() -> f64 {
    SOCKET.z.atan2(SOCKET.x).to_degrees()
}

fn outlet_holes() -> Result<Vec<Solid>> {
    [90., 180., 270.]
        .iter()
        .map(|turn| Ok(axial(HOLE_R, 1.3, CHAMBER_FLOOR + 0.01)?.translate(radial(socket_azimuth() + turn) * HOLE_RING)))
        .collect()
}

fn supply_drilling() -> Result<Solid> {
    bore(SOCKET + V3::Y * (SOCKET_DEPTH + 0.3), V3::Y * 3.7, 1.1)
}

/// One silicone casting carries the tube socket, the supply port and its seat lip, the outlet holes and the spout.
fn silicone_body() -> Result<Solid> {
    let outer = turn(&[
        (0., MOUTH),
        (SPOUT_R - 0.3, MOUTH),
        (SPOUT_R, MOUTH + 0.3),
        (SPOUT_R, 0.),
        (BODY_R, 0.),
        (BODY_R, SEAT_S),
        (0., SEAT_S),
    ])?;
    let lobe = axial(LOBE_R, 3.0, SEAT_S)?.translate(SOCKET);
    let mut cavities = vec![
        axial(SPOUT_BORE_R, MOUTH - 0.1, 0.4)?,
        turn(&[(0., 0.35), (SPOUT_BORE_R, 0.35), (PLENUM_R, 1.0), (PLENUM_R, 1.6), (0., 1.6)])?,
        turn(&[(LIP_R, CHAMBER_FLOOR), (CHAMBER_R, CHAMBER_FLOOR), (CHAMBER_R, SEAT_S + 0.05), (LIP_R, SEAT_S + 0.05)])?,
        axial(PORT_R, 3.6, SEAT_S + 0.05)?,
        supply_drilling()?,
        axial(TUBE_R, SOCKET_DEPTH, SEAT_S + 0.05)?.translate(SOCKET),
    ];
    cavities.extend(outlet_holes()?);
    outer.union(&lobe)?.cut_all(&cavities)
}

/// The diaphragm is molded flat; at `lift` the supply has raised its boss off the lip.
fn diaphragm(lift: f64) -> Result<Solid> {
    let s = SEAT_S;
    turn(&[
        (0., s + lift),
        (BOSS_R, s + lift),
        (CHAMBER_R, s),
        (BODY_R, s),
        (BODY_R, CLAMP_S),
        (CHAMBER_R, CLAMP_S),
        (CHAMBER_R, s + WEB_T),
        (BOSS_R, s + WEB_T + lift),
        (BOSS_R, s + BOSS_T + lift),
        (0., s + BOSS_T + lift),
    ])
}

/// The front housing boxes the silicone in, carries the face clip groove and takes the two screws.
fn housing(clearance: &Solid) -> Result<Solid> {
    let shell = turn(&[
        (SPOUT_R + 0.05, MOUTH + 0.5),
        (3.8, MOUTH + 0.5),
        (4.0, MOUTH + 0.7),
        (4.0, MOUNT_FACE - 1.28),
        (3.79, MOUNT_FACE - 1.28),
        (3.79, MOUNT_FACE - 0.38),
        (4.0, MOUNT_FACE - 0.38),
        (4.0, -0.84),
        (BARREL_R, -0.84),
        (BARREL_R, HOUSING_END),
        (POCKET_R, HOUSING_END),
        (POCKET_R, 0.),
        (SPOUT_R + 0.05, 0.),
    ])?;
    let mut housing = shell.union(&axial(LOBE_R + 0.8, 2.0, CLAMP_S)?.translate(SOCKET))?;
    for offset in [TIE, -TIE] {
        housing = housing.union(&axial(2.1, 3.0, HOUSING_END)?.translate(offset))?;
    }
    let mut cuts = vec![
        axial(POCKET_R, 0., HOUSING_END + 0.05)?,
        axial(LOBE_R + 0.05, 2.9, SEAT_S + 0.05)?.translate(SOCKET),
        clearance.clone(),
    ];
    for offset in [TIE, -TIE] {
        cuts.push(axial(0.8, 4.4, HOUSING_END + 0.05)?.translate(offset));
    }
    housing.cut_all(&cuts)
}

/// The rear carrier clamps the diaphragm rim, stops the pusher, seats the spring and cups the solenoid.
fn carrier(clearance: &Solid) -> Result<Solid> {
    let shell = turn(&[
        (CHAMBER_R, CLAMP_S),
        (BODY_R, CLAMP_S),
        (BODY_R, HOUSING_END),
        (CARRIER_R, HOUSING_END),
        (CARRIER_R, CUP_S),
        (CUP_R, CUP_S),
        (CUP_R, CUP_END),
        (6.25, CUP_END),
        (6.25, MOTOR_END + 0.1),
        (MOTOR_R + 0.05, MOTOR_END + 0.1),
        (MOTOR_R + 0.05, MOTOR_S),
        (4.85, MOTOR_S),
        (4.85, BUSHING_BORE_S),
        (3.0, BUSHING_BORE_S),
        (3.0, SPRING_SEAT_S),
        (4.4, SPRING_SEAT_S),
        (4.4, STOP_S),
        (CHAMBER_R, STOP_S),
    ])?;
    let mut carrier = shell.union(&annulus(3.0, 0.5, CLIP_S, CLIP_END)?.translate(SOCKET))?;
    for offset in [TIE, -TIE] {
        carrier = carrier.union(&axial(2.1, HOUSING_END, HEAD_S + 2.0)?.translate(offset))?;
    }
    let outward = SOCKET.unit();
    let clip_frame = Plane::new(SOCKET, outward, outward.cross(V3::Y))?;
    let snap = Solid::cuboid(v3(0., CLIP_S - 0.05, -(TUBE_R - 0.08)), v3(4.5, CLIP_END + 0.05, TUBE_R - 0.08))
        .placed(&Plane::XY, &clip_frame);
    let vent = bore(radial(socket_azimuth() + 180.) * 3.0 + V3::Y * 11.6, radial(socket_azimuth() + 180.) * 6.5 + V3::Y * 11.6, 0.6)?;
    let mut cuts = vec![
        clearance.clone(),
        axial(2.4, HOUSING_END - 0.05, CLIP_S)?.translate(SOCKET),
        snap,
        vent,
    ];
    for offset in [TIE, -TIE] {
        cuts.push(axial(1.1, HOUSING_END - 0.05, HEAD_S + 0.05)?.translate(offset));
        cuts.push(axial(HEAD_R + 0.1, HEAD_S, HEAD_S + 2.05)?.translate(offset));
    }
    for i in 0..3 {
        let slit = Solid::cuboid(v3(-0.5, MOTOR_S + 7., 5.5), v3(0.5, CUP_END + 0.1, 8.5));
        cuts.push(slit.rotate(V3::ZERO, V3::Y, socket_azimuth() + 60. + 120. * f64::from(i)));
    }
    carrier.cut_all(&cuts)
}

/// The printed pusher presses the diaphragm boss and is pinned to the solenoid plunger.
fn pusher() -> Result<Solid> {
    turn(&[
        (0., NOSE_S),
        (1.8, NOSE_S),
        (1.8, FLANGE_S),
        (4.2, FLANGE_S),
        (4.2, FLANGE_END),
        (3.5, FLANGE_END),
        (3.5, 24.5),
        (2.4, 24.5),
        (2.4, 17.0),
        (0., 17.0),
    ])?
    .cut(&bore(v3(-3.6, PIN_S, 0.), v3(3.6, PIN_S, 0.), 0.80)?)
}

fn spring(travel: f64) -> Result<Solid> {
    let front = FLANGE_END + travel + WIRE_R;
    let end_pitch = 2. * WIRE_R;
    let active_pitch = (SPRING_SEAT_S - WIRE_R - front - 2. * end_pitch) / ACTIVE_TURNS;
    let coil = |s, pitch, turns| -> Result<Solid> {
        let start = v3(SPRING_R, s, 0.);
        Plane::new(start, V3::X, v3(0., pitch, -TAU * SPRING_R))?.helix_sweep(
            &Profile::circle(v2(0., 0.), WIRE_R),
            V3::Y * s,
            V3::Y,
            pitch,
            turns,
        )
    };
    coil(front, end_pitch, 1.)?
        .union(&coil(front + end_pitch, active_pitch, ACTIVE_TURNS)?)?
        .union(&coil(SPRING_SEAT_S - WIRE_R - end_pitch, end_pitch, 1.)?)
}

fn parts(p: &mut Vec<Piece>, palette: &Palette, clearance: &Solid, lift: f64) -> Result<()> {
    let travel = if lift > 0. { STROKE } else { 0. };
    let moving = V3::Y * travel;
    add(p, "Silicone_valve_body_and_spout", palette.silicone, silicone_body()?, V3::ZERO, true);
    add(p, "Silicone_diaphragm", palette.silicone, diaphragm(lift)?, V3::Y * 5., true);
    add(p, "PET_GF_front_housing", palette.petgf, housing(clearance)?, V3::Y * -16., true);
    add(p, "PET_GF_rear_carrier", palette.petgf, carrier(clearance)?, V3::Y * 14., true);
    add(p, "PET_GF_pusher", palette.petgf, pusher()?.translate(moving), v3(0., 14., -15.), true);
    add(p, "Stainless_return_spring", palette.steel, spring(travel)?, v3(0., 14., -26.), false);
    let radius = 25.4 * 0.185 / 2.;
    let hole = bore(v3(-3., PIN_S, 0.), v3(3., PIN_S, 0.), 25.4 * 0.062 / 2.)?;
    let plunger = axial(radius, CLEVIS_S, MOTOR_S + 1.25)?
        .cut(&Solid::cuboid(v3(-SLOT / 2., CLEVIS_S - 0.1, -3.), v3(SLOT / 2., CLEVIS_S + 25.4 * 0.250, 3.)))?
        .cut(&hole)?;
    add(p, "Ledex_plunger", MOTOR, plunger.translate(moving), V3::Y * 30., false);
    let pin = bore(v3(-3.45, PIN_S, 0.), v3(3.45, PIN_S, 0.), 0.775)?;
    add(p, "Stainless_cross_pin", palette.steel, pin.translate(moving), v3(9., 14., -15.), false);
    let thread_r = (25.4 * 0.375 - 0.64952 * 25.4 / 32.) / 2.;
    let motor = axial(MOTOR_R, MOTOR_S, MOTOR_END)?
        .union(&annulus(thread_r, 2.50, BUSH_S, MOTOR_S + 0.02)?)?
        .cut(&axial(2.50, MOTOR_S - 0.02, MOTOR_S + 2.10)?)?;
    add(p, "Bought_Ledex_195200_237", MOTOR, motor, V3::Y * 30., true);
    for (name, offset) in [("Stainless_screw_left", TIE), ("Stainless_screw_right", -TIE)] {
        let screw = axial(1.0, HEAD_S - 8.0, HEAD_S)?.union(&axial(HEAD_R, HEAD_S, HEAD_S + 1.3)?)?;
        add(p, name, palette.steel, screw.translate(offset), V3::Y * 24. + offset.unit() * 3., false);
    }
    add(p, "Stainless_grip_face_washer", palette.steel, annulus(6.37, 4.06, MOUNT_FACE - 0.38, MOUNT_FACE)?, V3::Y * -22., true);
    let clip_front = MOUNT_FACE - 1.17;
    let mut clip = annulus(5.25, 3.79, clip_front, MOUNT_FACE - 0.38)?
        .cut(&Solid::cuboid(v3(-0.22, clip_front - 0.02, 0.), v3(0.22, MOUNT_FACE, 7.)))?;
    for x in [-1.19, 1.19] {
        let offset = v3(x, 0., 5.43);
        clip = clip
            .union(&axial(1.10, clip_front, MOUNT_FACE - 0.38)?.translate(offset))?
            .cut(&axial(0.60, clip_front - 0.02, MOUNT_FACE)?.translate(offset))?;
    }
    add(p, "Stainless_face_circlip", palette.steel, clip, V3::Y * -26., true);
    water(p, lift)
}

/// The water in the valve: supply blue up to the seat, outlet turquoise from the seat to the mouth.
fn water(p: &mut Vec<Piece>, lift: f64) -> Result<()> {
    let supply = axial(PORT_R, 3.6, SEAT_S)?
        .union(&supply_drilling()?)?
        .union(&axial(TUBE_ID_R, SOCKET_DEPTH, CLIP_END)?.translate(SOCKET))?;
    add(p, "Water_supply_to_seat", INLET, supply, V3::ZERO, true);
    let mut outlet = axial(SPOUT_BORE_R, MOUTH, 0.4)?
        .union(&turn(&[(0., 0.35), (SPOUT_BORE_R, 0.35), (PLENUM_R, 1.0), (PLENUM_R, 1.6), (0., 1.6)])?)?
        .union(&turn(&[(LIP_R, CHAMBER_FLOOR), (CHAMBER_R, CHAMBER_FLOOR), (CHAMBER_R, SEAT_S), (LIP_R, SEAT_S)])?)?;
    for hole in outlet_holes()? {
        outlet = outlet.union(&hole)?;
    }
    add(p, "Water_outlet_to_mouth", OUTLET, outlet, V3::ZERO, true);
    if lift > 0. {
        let gap = turn(&[(0., SEAT_S), (CHAMBER_R, SEAT_S), (BOSS_R, SEAT_S + lift), (0., SEAT_S + lift)])?;
        add(p, "Water_open_seat_gap", OUTLET, gap, V3::ZERO, true);
    }
    Ok(())
}

struct Route {
    path: Path,
    start: V3,
    hose_frame: Plane,
    inlet_frame: Plane,
    join: V3,
    hose: V3,
}

/// The soda tube keeps the acetal study's lane: straight from the socket, out past the solenoid, round to the hose.
fn route(neck: &Gooseneck, frame: &Plane) -> Result<Route> {
    let (point, tangent, normal) = neck.frame(neck.length() - 58.);
    let (xy, n) = frame.local(point + normal * shell::TUBE_SHELL_CENTER_Y);
    let join = v3(xy.x, xy.y, n);
    let hose = v3(-tangent.dot(frame.x), -tangent.dot(frame.y), -tangent.dot(frame.z));
    let axis_frame =
        |origin, direction: V3| Plane::new(origin, V3::X - direction * direction.x, V3::X.cross(direction));
    let hose_frame = axis_frame(join, hose)?;
    let azimuth = 38.0_f64.to_radians();
    let across = v3(-azimuth.cos(), 0., -azimuth.sin());
    let bend_cos = 0.45_f64;
    let bend_sin = (1. - bend_cos.powi(2)).sqrt();
    let inlet = V3::Y * bend_cos + across * bend_sin;
    let elbow = join - hose * 0.75;
    let rail = |s| elbow + inlet * s;
    let inlet_frame = axis_frame(elbow, inlet)?;
    let start = SOCKET + V3::Y * SOCKET_DEPTH;
    let bend = SOCKET + V3::Y * 20.1;
    let side = BYPASS + V3::Y * 35.3;
    let last = rail(-6.90);
    let bend_radius = 9.0;
    let knee = last - V3::Y * (bend_radius * bend_sin) - across * (bend_radius * (1. - bend_cos));
    let approach = V3::Y * ((knee.y - side.y) / 2.5);
    let path = Path::new(start)
        .line_to(bend)
        .bezier(&[bend, bend + V3::Y * 5.45, side - V3::Y * 5.45, side])?
        .bezier(&[side, side + approach, knee - approach, knee])?
        .arc_center(knee + across * bend_radius, last, V3::Y.cross(across))?
        .line_to(rail(TIP_STOP));
    Ok(Route { path, start, hose_frame, inlet_frame, join, hose })
}

fn tube_clearance(route: &Route) -> Result<Solid> {
    Plane::new(route.start, V3::X, V3::Y)?.sweep(&Profile::circle(v2(0., 0.), TUBE_R + 0.15), &route.path)
}

/// A tube shop bends and beads the stainless tube and laser-welds it into a turned stainless barb.
fn tubing(p: &mut Vec<Piece>, palette: &Palette, route: &Route) -> Result<()> {
    let tube = Plane::new(route.start, V3::X, V3::Y)?
        .sweep(&Profile::circle(v2(0., 0.), TUBE_R).with_hole(Loop::circle(v2(0., 0.), TUBE_ID_R)), &route.path)?
        .union(&torus(TUBE_R, 0.30, BEAD_S)?.translate(SOCKET))?;
    add(p, "Stainless_soda_tube", palette.steel, tube, SOCKET.unit() * 16., true);
    let barb = turn(&[
        (0., -3.8),
        (3.25, -3.8),
        (3.75, -2.72),
        (3.75, 0.),
        (3.50, 0.),
        (3.50, 2.32),
        (3.77, 2.43),
        (3.50, 3.63),
        (3.50, 6.36),
        (3.78, 6.47),
        (3.50, 7.67),
        (3.50, 9.78),
        (3.75, 9.89),
        (3.44, 11.48),
        (3.13, 12.),
        (0., 12.),
    ])?
    .placed(&Plane::XY, &route.hose_frame);
    let at_socket = |shape: Solid| shape.placed(&Plane::XY, &route.inlet_frame);
    let socket = turn(&[(0., -6.18), (3.08, -6.18), (3.08, -5.19), (3.26, -4.65), (3.26, 0.06), (0., 0.06)])?;
    let socket_cut = axial(TUBE_R + 0.035, -6.25, TIP_STOP)?.union(&axial(TUBE_ID_R, TIP_STOP - 0.01, 0.62)?)?;
    let water = bore(route.join - route.hose * 1.36, route.join + route.hose * 12.12, 2.06)?;
    let barb = barb.union(&at_socket(socket))?.cut(&at_socket(socket_cut))?.cut(&water)?;
    add(p, "Stainless_hose_barb_welded_to_tube", palette.steel, barb, SOCKET.unit() * 16. + V3::Y * 6., false);
    Ok(())
}

type View = Vec<(String, Color, Solid)>;

fn write(dir: &Dir, name: &str, view: &View) -> Result<()> {
    let shapes: Vec<_> = view.iter().map(|(n, c, s)| (n.as_str(), *c, s)).collect();
    show(dir, name, &shapes)
}

/// Turns the socket's half plane to the cut, so the section shows the supply drilling and one outlet hole.
fn socket_up() -> Result<Plane> {
    let a = socket_azimuth().to_radians();
    Plane::new(V3::ZERO, v3(a.sin(), 0., a.cos()), v3(-a.cos(), 0., a.sin()))
}

fn lengthwise(solid: &Solid) -> Solid {
    solid.rotate(V3::ZERO, V3::Z, -90.).rotate(V3::ZERO, V3::X, 90.)
}

fn section_view(p: &[Piece], names: Option<&[&str]>) -> Result<View> {
    let turned = socket_up()?;
    let half = Solid::cuboid(v3(-30., -12., -20.), v3(0., 60., 30.));
    let mut view = Vec::new();
    for a in p.iter().filter(|a| names.map_or(true, |n| n.contains(&a.name))) {
        let placed = a.solid.placed(&Plane::XY, &turned);
        let shown = if a.section { placed.cut(&half)? } else { placed };
        if !shown.is_empty() {
            view.push((a.name.into(), a.color, lengthwise(&shown)));
        }
    }
    Ok(view)
}

fn interpolate(table: &[(f64, f64)], stroke_mm: f64) -> f64 {
    let inches = stroke_mm / 25.4;
    let ounces = table
        .windows(2)
        .find(|w| inches <= w[1].0)
        .map(|w| w[0].1 + (inches - w[0].0) / (w[1].0 - w[0].0) * (w[1].1 - w[0].1))
        .unwrap_or(table[table.len() - 1].1);
    ounces * NEWTONS_PER_OUNCE
}

/// Reports the seated loads, the hold pressure, the solenoid's margin and the flow restriction.
fn report() {
    let port = PI * PORT_R.powi(2);
    let supply_bar = calibration_inputs::SECONDARY_REGULATOR_BAR;
    let load = |bar: f64| bar / 10. * port;
    let rate = 70_000. * (2. * WIRE_R).powi(4) / (8. * (2. * SPRING_R).powi(3) * ACTIVE_TURNS);
    let installed = SPRING_SEAT_S - FLANGE_END;
    let hold_bar = (SPRING_PRELOAD_N - SEAT_MARGIN_N) / port * 10.;
    let pull_needed = SPRING_PRELOAD_N - load(supply_bar);
    let pull_available = interpolate(&LEDEX_INTERMITTENT, STROKE);
    let hold_needed = SPRING_PRELOAD_N + rate * STROKE;
    let hold_available = interpolate(&LEDEX_CONTINUOUS, 0.254);
    let flow = 2. / 60_000.;
    let drop = |area_mm2: f64, cd: f64| 0.5 * 1000. * (flow / (cd * area_mm2 * 1e-6)).powi(2) / 1e5;
    let curtain = 2. * PI * PORT_R * LIFT;
    let holes = 3. * PI * HOLE_R.powi(2);
    let spout = PI * SPOUT_BORE_R.powi(2);
    let total = drop(port, 0.65) + drop(curtain, 0.65) + drop(holes, 0.65) + drop(spout, 0.8);
    eprintln!(
        "Spring: {SPRING_PRELOAD_N:.2} N closed at {installed:.1} mm, {rate:.3} N/mm, free {:.1} mm",
        installed + SPRING_PRELOAD_N / rate
    );
    eprintln!(
        "Seat: {port:.2} mm² supply port; {:.2} N lifting the closed boss at {supply_bar:.1} bar; holds to {hold_bar:.1} bar with {SEAT_MARGIN_N:.1} N left on the lip",
        load(supply_bar)
    );
    eprintln!(
        "Opening at {supply_bar:.1} bar: {pull_needed:.2} N needed at {STROKE:.2} mm; Ledex 195200-237 intermittent {pull_available:.2} N"
    );
    eprintln!("Holding open: {hold_needed:.2} N spring at full travel; Ledex continuous at 0.25 mm {hold_available:.2} N, before flow assist");
    eprintln!("Flow: about {total:.2} bar across the valve at 2 L/min (port, curtain, outlet holes, spout)");
}

fn main() -> Result<()> {
    let dir = out()?;
    let palette = Palette {
        silicone: material("M_SILICONE_CLEAR")?,
        petgf: material("M_PETGF_BLACK")?,
        steel: material("M_STAINLESS")?,
    };
    let neck = Gooseneck::shell();
    let tip = hsm_faucet::display::tip_plane(&neck)?;
    let pitch = (-2.0_f64).to_radians();
    let frame = Plane::new(tip.origin, tip.x, tip.z * pitch.cos() - tip.y * pitch.sin())?;
    let route = route(&neck, &frame)?;
    let clearance = tube_clearance(&route)?;
    let mut closed = vec![];
    let mut open = vec![];
    parts(&mut closed, &palette, &clearance, 0.)?;
    parts(&mut open, &palette, &clearance, LIFT)?;
    tubing(&mut closed, &palette, &route)?;
    tubing(&mut open, &palette, &route)?;
    report();
    let front: Vec<&str> = open.iter().map(|p| p.name).filter(|n| !n.contains("barb")).collect();
    write(&dir, "section-closed", &section_view(&closed, Some(&front))?)?;
    write(&dir, "section-open", &section_view(&open, Some(&front))?)?;
    let wet = [
        "Silicone_valve_body_and_spout",
        "Silicone_diaphragm",
        "Stainless_soda_tube",
        "Water_supply_to_seat",
        "Water_outlet_to_mouth",
        "Water_open_seat_gap",
    ];
    write(&dir, "wet-path", &section_view(&open, Some(&wet))?)?;
    let solid_parts = || closed.iter().filter(|a| !a.name.starts_with("Water_"));
    let assembled: View = solid_parts().map(|p| (p.name.into(), p.color, p.solid.rotate(V3::ZERO, V3::Z, -90.))).collect();
    write(&dir, "assembly", &assembled)?;
    let bench: View = solid_parts()
        .map(|p| (p.name.into(), p.color, p.solid.translate(p.exploded).rotate(V3::ZERO, V3::Z, -90.)))
        .collect();
    write(&dir, "exploded", &bench)?;
    let mut installed = Vec::new();
    let mut full = Vec::new();
    let window = Solid::cuboid(v3(0., -8., -35.), v3(25., 85., 25.)).placed(&Plane::XY, &frame);
    let flange_relief = axial(BARREL_R + 0.12, -0.89, 0.91)?.placed(&Plane::XY, &frame);
    for body in part("faucet-layout/pullout-concept/docked-above-counter.step")? {
        let name = &body.name;
        if name == "pull_off_curved_grip" {
            let face_boss =
                turn(&[(4.07, MOUNT_FACE), (6.47, MOUNT_FACE), (7.53, -1.04), (7.53, -0.73), (4.07, -0.73)])?
                    .placed(&Plane::XY, &frame);
            let mut grip = body.solid.union(&face_boss)?.cut(&flange_relief)?;
            for offset in [TIE, -TIE] {
                let keyway = axial(2.16, 2.38, 20.75)?.translate(offset).placed(&Plane::XY, &frame);
                grip = grip.cut(&keyway)?;
            }
            full.push((name.clone(), body.color.unwrap_or(MOTOR), grip.clone()));
            installed.push((name.clone(), body.color.unwrap_or(MOTOR), grip.cut(&window)?));
        } else if name == "soft_hose_strain_relief"
            || name.starts_with("screen_")
            || (name.starts_with("head_") && !name.starts_with("head_valve_"))
        {
            installed.push((name.clone(), body.color.unwrap_or(MOTOR), body.solid));
            full.push(installed.last().unwrap().clone());
        }
    }
    for q in solid_parts() {
        installed.push((q.name.into(), q.color, q.solid.placed(&Plane::XY, &frame)));
        full.push(installed.last().unwrap().clone());
    }
    write(&dir, "installed-cutaway", &installed)?;
    write(&dir, "installed", &full)
}
