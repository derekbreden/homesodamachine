//! This manufacturing study puts a turned acetal valve and a purchased dry solenoid in the pull-out tip.
use anyhow::Result;
use hsm_faucet::Gooseneck;
use hsm_faucet_numbers::shell;
use hsm_kernel::{Loop, Path, Plane, Profile, Solid, V3, v2, v3};
use hsm_sandbox::{out, part, show};
use std::path::Path as Dir;

#[allow(dead_code)]
#[path = "../balance.rs"]
mod balance;
#[allow(dead_code)]
#[path = "../front_seat.rs"]
mod front_seat;
mod poppet;

type Color = [f64; 3];
const ACETAL: Color = [0.79, 0.72, 0.54];
const MOVING_ACETAL: Color = [0.93, 0.82, 0.53];
const STEEL: Color = [0.47, 0.54, 0.59];
const SEAL: Color = [0.045, 0.26, 0.14];
const MOTOR: Color = [0.13, 0.17, 0.20];
const INLET: Color = [0.03, 0.29, 0.63];
const RETURN: Color = [0.02, 0.58, 0.53];
const BACK: f64 = 15.65;
const MOUTH: f64 = -4.91;
const MOUNT_FACE: f64 = -2.55;
const MOUTH_BELL_R: f64 = 3.16;
const BARREL_R: f64 = 5.90;
const RETURN_N: f64 = -4.42;
const RETURN_R: f64 = 0.48;
const LINER_R: f64 = 3.43;
const SOCKET: V3 = v3(5.55, 0., 4.38);
const BYPASS: V3 = v3(8.1, 0., 5.62);
const GASKET_HEIGHT: f64 = 0.64;
const TUBE_R: f64 = 25.4 * 5. / 64.;
const TUBE_ID_R: f64 = TUBE_R - 25.4 * 0.010;
const MOTOR_S: f64 = 36.475;
const MOTOR_LEN: f64 = 25.4 * 0.550;
const MOTOR_R: f64 = 25.4 * 0.520 / 2.;
const BUSH_S: f64 = MOTOR_S - 25.4 * 0.250;
const LIFT: f64 = 0.6;
const PIN_TRAVEL: f64 = 0.06;
const SLOT: f64 = 25.4 * 0.062;
const PIN_S: f64 = MOTOR_S - 25.4 * 0.562 - LIFT - PIN_TRAVEL;
const CLEVIS_S: f64 = PIN_S - 25.4 * 0.125;
const TIE: V3 = v3(-4.48, 0., 4.45);
const LIMITER_R: f64 = 1.38;

struct Piece {
    name: &'static str,
    color: Color,
    solid: Solid,
    exploded: V3,
    section: bool,
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

fn lugged(part: &Solid, front: f64, rear: f64) -> Result<Solid> {
    let mut result = part.clone();
    for offset in [TIE, -TIE] {
        result = result
            .union(&axial(1.9, front, rear)?.translate(offset))?
            .cut(&axial(LIMITER_R + 0.025, front - 0.05, rear + 0.05)?.translate(offset))?;
    }
    Ok(result)
}

fn nut_envelope(radius: f64, front: f64, back: f64) -> Result<Solid> {
    let hex: Vec<_> = (0..6)
        .map(|i| {
            let angle = i as f64 * std::f64::consts::TAU / 6.;
            v2(radius * angle.cos(), radius * angle.sin())
        })
        .collect();
    Plane::new(V3::Y * front, V3::X, V3::Y)?.extrude(&Profile::polygon(&hex), back - front)
}

fn liner() -> Result<Solid> {
    let shell = turn(&[
        (front_seat::KEEPER_BORE_R, front_seat::CLAMP_S),
        (LINER_R, front_seat::CLAMP_S),
        (LINER_R, 4.3),
        (2.96, 4.6),
        (2.96, 8.7),
        (LINER_R, 9.0),
        (LINER_R, 12.18),
        (2.62, 12.18),
        (2.62, 13.53),
        (LINER_R, 13.53),
        (LINER_R, 14.90),
        (balance::BORE_R, 14.90),
        (balance::BORE_R, balance::PISTON_S),
        (2.38, 11.55),
        (2.65, 11.4),
        (2.65, 2.2),
        (front_seat::KEEPER_BORE_R, 2.1),
    ])?;
    let radial = SOCKET.unit();
    let cross = V3::Y.cross(radial);
    let at = V3::Y * 6.7;
    shell.cut(&bore(at - 4. * radial, at + 4. * radial, 1.25)?)?.cut(&bore(
        at - 4. * cross,
        at + 4. * cross,
        1.25,
    )?)
}

/// The rear reference drill intersects a short angled hole drilled through the outlet mouth.
fn gallery() -> Result<Solid> {
    let channel = axial(RETURN_R, -0.22, BACK + 0.01)?.translate(v3(0., 0., RETURN_N));
    let from_mouth = |s| v3(0., s, -4.10 - 1.34 * s);
    let mouth = bore(from_mouth(MOUTH), from_mouth(0.43), 0.37)?;
    let back_slot = Solid::cuboid(v3(-RETURN_R, 14.92, RETURN_N), v3(RETURN_R, BACK + 0.01, -1.5));
    channel.union(&back_slot)?.union(&mouth)
}

/// The die-cut gasket surrounds the bore and its outlet drilling in one closed loop.
fn rear_gasket(inset: f64, outset: f64, start: f64, end: f64) -> Result<Solid> {
    let boundary = |offset| {
        hsm_kernel::hull_loop(&[
            hsm_kernel::Wrapped::Circle { c: v2(0., 0.), r: 3.60 + offset },
            hsm_kernel::Wrapped::Circle { c: v2(0., -RETURN_N), r: 0.64 + offset },
        ])
    };
    let profile = Profile::new(boundary(outset)?).with_hole(boundary(inset)?);
    Plane::new(V3::Y * start, V3::X, V3::Y)?.extrude(&profile, end - start)
}

fn wet(p: &mut Vec<Piece>, lift: f64) -> Result<()> {
    use front_seat as seat;
    let axis = V3::Y;
    let reference = gallery()?;
    let radial = SOCKET.unit();
    let tangent = axis.cross(radial);
    let oblique = |s| axis * s + SOCKET + radial * ((s - 12.8) * 0.55);
    let inlet_drill = |side| bore(oblique(4.95) + tangent * side, oblique(13.98) + tangent * side, 1.09);
    let cross_feed = inlet_drill(-0.46)?.union(&inlet_drill(0.46)?)?;
    let feed_port = axial(TUBE_ID_R, 6.55, 9.15)?.translate(SOCKET);
    let inlet_socket = axial(TUBE_R + 0.035, 9.0, 14.05)?.translate(SOCKET);
    let inlet_gland = axial(TUBE_R + 0.63, 11.65, 12.7)?.translate(SOCKET);
    let relief = axial(2.22, 13.9, 20.1)?.translate(SOCKET);
    let pocket = turn(&[
        (0., MOUTH - 0.1),
        (MOUTH_BELL_R, MOUTH - 0.1),
        (MOUTH_BELL_R, MOUTH),
        (seat::BORE_R, -3.42),
        (seat::BORE_R, -0.48),
        (seat::THROAT_R, seat::FLOOR_S),
        (seat::WASHER_R + 0.04, seat::FLOOR_S),
        (seat::WASHER_R + 0.04, seat::FLOOR_S + 0.149),
        (LINER_R + 0.04, seat::FLOOR_S + 0.149),
        (LINER_R + 0.04, BACK + 0.1),
        (0., BACK + 0.1),
    ])?;
    let nose = axial(BARREL_R, -0.88, BACK)?
        .union(&turn(&[
            (0., MOUTH),
            (3.80, MOUTH),
            (4.0, MOUTH + 0.20),
            (4.0, MOUNT_FACE - 1.28),
            (3.79, MOUNT_FACE - 1.28),
            (3.79, MOUNT_FACE - 0.38),
            (4.0, MOUNT_FACE - 0.38),
            (4.0, -0.84),
            (0., -0.84),
        ])?)?
        .union(&bore(oblique(6.8), oblique(10.4), 2.55)?)?
        .union(&axial(3.08, 4.05, 13.9)?.translate(SOCKET))?;
    let back_seal = rear_gasket(-0.12, 1.01, BACK - GASKET_HEIGHT, BACK + 0.04)?;
    let mut shell = lugged(&nose, 2.6, BACK)?.cut_all(&[
        pocket,
        reference.clone(),
        cross_feed.clone(),
        feed_port.clone(),
        inlet_socket.clone(),
        inlet_gland,
        back_seal,
        relief.clone(),
    ])?;
    for offset in [TIE, -TIE] {
        shell = shell
            .cut(&nut_envelope(2.16, 0.76, 2.60)?.translate(offset))?
            .cut(&axial(LIMITER_R + 0.025, 2.59, BACK + 0.02)?.translate(offset))?;
    }
    add(p, "Acetal_pressure_body_and_outlet", ACETAL, shell, V3::ZERO, true);
    let grip_washer = annulus(6.37, 4.06, MOUNT_FACE - 0.38, MOUNT_FACE)?;
    add(p, "Stainless_grip_face_washer", STEEL, grip_washer, axis * -5., true);
    let clip_front = MOUNT_FACE - 1.17;
    let mut clip = annulus(5.25, 3.79, clip_front, MOUNT_FACE - 0.38)?
        .cut(&Solid::cuboid(v3(-0.22, clip_front - 0.02, 0.), v3(0.22, MOUNT_FACE, 7.)))?;
    for x in [-1.19, 1.19] {
        let offset = v3(x, 0., 5.43);
        clip = clip
            .union(&axial(1.10, clip_front, MOUNT_FACE - 0.38)?.translate(offset))?
            .cut(&axial(0.60, clip_front - 0.02, MOUNT_FACE)?.translate(offset))?;
    }
    add(p, "Outlet_mount_circlip", STEEL, clip, axis * -8., true);
    add(p, "Captive_EPDM_seat", SEAL, seat::installed_washer()?, axis * -4.5, true);
    let insert = liner()?;
    add(p, "Acetal_seat_cage_and_balance_bore", ACETAL, insert.clone(), v3(-12., 0., 0.), true);
    add(
        p,
        "Cage_static_seal",
        SEAL,
        balance::compressed_ring(5.0, 1.0, 2.62, LINER_R + 0.04, (12.18 + 13.53) / 2.)?,
        v3(-12., 0., 0.),
        true,
    );
    let stem = poppet::turning()?.translate(axis * lift);
    add(p, "One_piece_acetal_poppet", MOVING_ACETAL, stem.clone(), v3(-23., 0., 0.), false);
    add(
        p,
        "Moving_balance_piston_seal",
        SEAL,
        balance::piston_seal()?.translate(axis * lift),
        v3(-23., 0., 0.),
        true,
    );
    let gland = turn(&[
        (poppet::GUIDE_R, poppet::GUIDE_IN),
        (3.10, poppet::GUIDE_IN),
        (3.10, BACK),
        (BARREL_R, BACK),
        (BARREL_R, balance::DRY_BORE_S),
        (3.67, balance::DRY_BORE_S),
        (3.67, poppet::GUIDE_END),
        (poppet::GUIDE_R, poppet::GUIDE_END),
        (poppet::GUIDE_R, poppet::GLAND_END),
        (poppet::GLAND_R, poppet::GLAND_END),
        (poppet::GLAND_R, poppet::GLAND_START),
        (poppet::GUIDE_R, poppet::GLAND_START),
    ])?;
    let boss = annulus(3.41, 2.10, 14.90, BACK + 0.01)?
        .cut(&axial(poppet::GLAND_R, poppet::GLAND_START, poppet::GLAND_END)?)?
        .cut(&Solid::cuboid(v3(-0.60, 14.89, -3.5), v3(0.60, BACK + 0.02, -1.6)))?;
    add(
        p,
        "Acetal_rod_gland",
        ACETAL,
        lugged(&gland.union(&boss)?, BACK, balance::DRY_BORE_S)?.cut(&relief)?,
        axis * 7.,
        true,
    );
    add(p, "Rear_face_seal", SEAL, rear_gasket(-0.06, 0.86, BACK - GASKET_HEIGHT, BACK)?, axis * 3.4, true);
    add(p, "Dry_rod_seal", SEAL, poppet::rod_seal()?, axis * 7., true);
    add(
        p,
        "Supply_tube_seal",
        SEAL,
        balance::compressed_ring(4.0, 0.75, TUBE_R, TUBE_R + 0.63, 12.175)?.translate(SOCKET),
        v3(5., 1., 0.),
        true,
    );
    for (n, sleeve, offset) in [
        ("Tie_screw_left", "Compression_limiter_left", TIE),
        ("Tie_screw_right", "Compression_limiter_right", -TIE),
    ] {
        let nut = nut_envelope(2.10, 0.95, 2.60)?;
        let screw = axial(0.98, 0.85, 19.56)?.union(&axial(1.67, 19.55, 20.37)?)?.union(&nut)?;
        add(p, n, STEEL, screw.translate(offset), offset.unit() * 4., false);
        add(
            p,
            sleeve,
            STEEL,
            annulus(LIMITER_R, 1.035, 2.60, 19.55)?.translate(offset),
            offset.unit() * 2.,
            true,
        );
    }
    let low_at_lip =
        axial(seat::SEAT_D / 2., seat::SEAT_S, seat::SEAT_S + lift + poppet::CROWN_R)?.cut(&stem)?;
    let outlet = turn(&[
        (0., MOUTH),
        (MOUTH_BELL_R, MOUTH),
        (seat::BORE_R, -3.42),
        (seat::BORE_R, -0.48),
        (seat::THROAT_R, seat::FLOOR_S),
        (seat::THROAT_R, seat::SEAT_S),
        (0., seat::SEAT_S),
    ])?;
    let pressure = axial(2.64, seat::CLAMP_S, 11.57)?
        .union(&axial(balance::BORE_R, 11.53, balance::PISTON_S + lift)?)?
        .union(&cross_feed.intersect(&axial(11., 4.0, 9.0)?)?)?
        .union(&feed_port)?
        .cut(&insert)?
        .cut(&stem)?
        .cut(&seat::installed_washer()?)?
        .cut(&low_at_lip)?;
    add(p, "Water_supply_at_seat", INLET, pressure, V3::ZERO, true);
    let drain = outlet
        .union(&low_at_lip)?
        .union(&reference.intersect(&axial(BARREL_R, MOUTH, BACK)?)?)?
        .union(&axial(balance::BORE_R, balance::PISTON_END_S + lift, BACK)?)?
        .union(&axial(3.46, 14.90, BACK)?)?
        .cut(&boss)?
        .cut(&gland)?
        .cut(&stem)?;
    add(p, "Water_outlet_and_balance_reference", RETURN, drain, V3::ZERO, true);
    Ok(())
}

/// The fork, mounting bush and can use the purchased solenoid's external dimensions.
fn drive(p: &mut Vec<Piece>, lift: f64) -> Result<()> {
    let axis = V3::Y;
    let move_by = axis * lift;
    let spring_front = poppet::SPRING_FRONT + lift;
    let fixed = BUSH_S - 0.2;
    add(
        p,
        "Slotted_spring_thrust_washer",
        STEEL,
        poppet::spring_washer()?.translate(move_by),
        v3(-16., 4., 0.),
        false,
    );
    poppet::pin_and_fork(p, lift)?;
    let spring_r = 2.99;
    let wire_r: f64 = 0.225;
    let active_turns = 6.;
    let end_pitch = 2. * wire_r;
    if lift == 0. {
        let spring_rate = 70_000. * end_pitch.powi(4) / (8. * (2.0_f64 * spring_r).powi(3) * active_turns);
        let installed_length = fixed - spring_front;
        let seat_load = 1.30;
        eprintln!(
            "Return spring selection: seated {:.2} N at {:.2} mm, nominal {:.3} N/mm, free {:.2} mm",
            seat_load,
            installed_length,
            spring_rate,
            installed_length + seat_load / spring_rate
        );
    }
    let first = spring_front + wire_r;
    let active_pitch = (fixed - wire_r - first - 2. * end_pitch) / active_turns;
    let coil = |s, pitch, turns| -> Result<Solid> {
        let start = v3(spring_r, s, 0.);
        Plane::new(start, V3::X, v3(0., pitch, -std::f64::consts::TAU * spring_r))?.helix_sweep(
            &Profile::circle(v2(0., 0.), wire_r),
            axis * s,
            axis,
            pitch,
            turns,
        )
    };
    let spring = coil(first, end_pitch, 1.)?
        .union(&coil(first + end_pitch, active_pitch, active_turns)?)?
        .union(&coil(fixed - wire_r - end_pitch, end_pitch, 1.)?)?;
    add(p, "Stainless_return_spring", STEEL, spring, v3(-11., 8., 0.), false);
    let base = lugged(&annulus(5.4, 3.70, balance::DRY_BORE_S, 19.55)?, balance::DRY_BORE_S, 19.55)?;
    let retainer = bore(v3(4.1, 19.13, 2.45), SOCKET + axis * 19.13, 0.90)?
        .union(&annulus(2.80, TUBE_R + 0.035, 18.73, 19.55)?.translate(SOCKET))?;
    let mut cage = base
        .union(&retainer)?
        .cut(&axial(TUBE_R + 0.035, 17.6, 20.5)?.translate(SOCKET))?
        .cut(&axial(TUBE_R + 0.29, 17.65, 18.73)?.translate(SOCKET))?;
    for x in [-4.53, 4.53] {
        cage = cage.union(&axial(0.86, 19.47, BUSH_S)?.translate(v3(x, 0., 0.)))?;
    }
    let thread_r = (25.4 * 0.375 - 0.64952 * 25.4 / 32.) / 2.;
    let lock_face = MOTOR_S - 1.80;
    let cap =
        annulus(5.72, 2.57, fixed, BUSH_S)?.union(&annulus(5.72, thread_r + 0.01, BUSH_S, lock_face)?)?;
    add(p, "Aluminum_threaded_actuator_carrier", STEEL, cage.union(&cap)?, axis * 11., true);
    let lock = nut_envelope(5.74, lock_face, MOTOR_S)?.cut(&axial(
        thread_r + 0.01,
        lock_face - 0.05,
        MOTOR_S + 0.05,
    )?)?;
    add(p, "Actuator_jam_nut", STEEL, lock, axis * 13., true);
    let motor = axial(MOTOR_R, MOTOR_S, MOTOR_S + MOTOR_LEN)?
        .union(&annulus(thread_r, 2.50, BUSH_S, MOTOR_S + 0.02)?)?
        .cut(&axial(2.50, MOTOR_S - 0.02, MOTOR_S + 2.10)?)?;
    add(p, "Bought_Ledex_195200_237", MOTOR, motor, axis * 24., false);
    Ok(())
}

/// A turned hose barb with an angled socket joins the formed tube and the crimped hose.
fn tubing(p: &mut Vec<Piece>, neck: &Gooseneck, frame: &Plane) -> Result<()> {
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
    let at_socket = |shape: Solid| shape.placed(&Plane::XY, &inlet_frame);
    let start = SOCKET + V3::Y * 9.;
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
        .line_to(rail(-1.90));
    let tube = Plane::new(start, V3::X, V3::Y)?
        .sweep(&Profile::circle(v2(0., 0.), TUBE_R).with_hole(Loop::circle(v2(0., 0.), TUBE_ID_R)), &path)?;
    let front_bead = torus(TUBE_R, 0.23, 18.50)?.translate(SOCKET);
    let rear_bead = at_socket(torus(TUBE_R, 0.25, -6.48)?);
    add(p, "Stock_316L_soda_tube", STEEL, tube.union(&front_bead)?.union(&rear_bead)?, v3(5., 0., 3.), false);
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
    .placed(&Plane::XY, &hose_frame);
    let socket = turn(&[
        (0., -6.18),
        (3.08, -6.18),
        (3.08, -5.19),
        (2.78, -5.19),
        (2.78, -4.65),
        (3.26, -4.65),
        (3.26, 0.06),
        (0., 0.06),
    ])?;
    let tip_stop = -1.90;
    let water = bore(join - hose * 1.36, join + hose * 12.12, 2.06)?;
    let gland = axial(TUBE_R + 0.63, -4.30, -3.24)?;
    let socket_cut = axial(TUBE_R + 0.035, -6.25, tip_stop)?.union(&gland)?.union(&axial(
        TUBE_ID_R,
        tip_stop - 0.01,
        0.62,
    )?)?;
    let adapter = barb.union(&at_socket(socket))?.cut(&at_socket(socket_cut))?.cut(&water)?;
    add(p, "Acetal_integral_hose_barb_and_socket", ACETAL, adapter, v3(4., 7., 0.), false);
    let ferrule = turn(&[
        (TUBE_R + 0.025, -6.99),
        (3.30, -6.99),
        (3.30, -4.90),
        (2.84, -4.90),
        (2.84, -5.19),
        (3.10, -5.19),
        (3.10, -6.18),
        (TUBE_R + 0.33, -6.18),
        (TUBE_R + 0.33, -6.73),
        (TUBE_R + 0.025, -6.73),
    ])?;
    add(p, "Swaged_tube_bead_retainer", STEEL, at_socket(ferrule), v3(4., 3., 0.), false);
    add(
        p,
        "Hose_adapter_tube_seal",
        SEAL,
        at_socket(balance::compressed_ring(4.0, 0.75, TUBE_R, TUBE_R + 0.63, -3.77)?),
        v3(4., 5., 0.),
        false,
    );
    Ok(())
}

type View = Vec<(String, Color, Solid)>;

fn write(dir: &Dir, name: &str, view: &View) -> Result<()> {
    let shapes: Vec<_> = view.iter().map(|(n, c, s)| (n.as_str(), *c, s)).collect();
    show(dir, name, &shapes)
}

/// The section exposes the pressure galleries and preserves the complete acetal turning.
fn wet_view(p: &[Piece], lift: f64) -> Result<View> {
    let half = Solid::cuboid(v3(0., -7., -20.), v3(26., 32., 27.));
    let mut view = Vec::new();
    for a in p {
        let is_water = a.name.starts_with("Water_");
        let shown = if a.name == "Water_supply_at_seat" {
            let annular_cut = Solid::cuboid(v3(0., -7., -20.), v3(1.95, 32., 27.));
            a.solid.cut(&annular_cut)?
        } else if a.section {
            a.solid.cut(&half)?
        } else {
            a.solid.clone()
        };
        if !shown.is_empty() {
            view.push((
                a.name.into(),
                a.color,
                shown.rotate(V3::ZERO, V3::Z, -90.).rotate(V3::ZERO, V3::X, 90.),
            ));
        }
        if lift > 0. && is_water && a.name == "Water_outlet_and_balance_reference" {
            let curtain =
                axial(front_seat::SEAT_D / 2., front_seat::SEAT_S, front_seat::SEAT_S + lift)?.cut(&half)?;
            view.push((
                "Open_seat_flow_gap".into(),
                RETURN,
                curtain.rotate(V3::ZERO, V3::Z, -90.).rotate(V3::ZERO, V3::X, 90.),
            ));
        }
    }
    Ok(view)
}

fn main() -> Result<()> {
    let dir = out()?;
    let neck = Gooseneck::shell();
    let tip = hsm_faucet::display::tip_plane(&neck)?;
    let pitch = (-2.0_f64).to_radians();
    let frame = Plane::new(tip.origin, tip.x, tip.z * pitch.cos() - tip.y * pitch.sin())?;
    let mut closed = vec![];
    let mut open = vec![];
    wet(&mut closed, 0.)?;
    wet(&mut open, LIFT)?;
    drive(&mut closed, 0.)?;
    drive(&mut open, LIFT)?;
    write(&dir, "seat-closed", &wet_view(&closed, 0.)?)?;
    write(&dir, "seat-open", &wet_view(&open, LIFT)?)?;
    let moving: View = closed
        .iter()
        .filter(|p| {
            [
                "One_piece_acetal_poppet",
                "Moving_balance_piston_seal",
                "Slotted_spring_thrust_washer",
                "Stainless_captive_clevis_pin",
                "Ledex_clevis_plunger",
                "Stainless_return_spring",
            ]
            .contains(&p.name)
        })
        .map(|p| (p.name.into(), p.color, p.solid.translate(p.exploded * 0.45).rotate(V3::ZERO, V3::Z, -90.)))
        .collect();
    write(&dir, "moving-assembly", &moving)?;
    tubing(&mut closed, &neck, &frame)?;
    let mut bench = Vec::new();
    for p in closed.iter().filter(|a| !a.name.starts_with("Water_")) {
        let display = p.solid.translate(p.exploded).rotate(V3::ZERO, V3::Z, -90.);
        bench.push((p.name.into(), p.color, display));
    }
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
            installed.push((name.clone(), body.color.unwrap_or(STEEL), body.solid));
            full.push(installed.last().unwrap().clone());
        }
    }
    for q in closed.iter().filter(|a| !a.name.starts_with("Water_")) {
        installed.push((q.name.into(), q.color, q.solid.placed(&Plane::XY, &frame)));
        full.push(installed.last().unwrap().clone());
    }
    write(&dir, "installed-cutaway", &installed)?;
    write(&dir, "installed", &full)
}
