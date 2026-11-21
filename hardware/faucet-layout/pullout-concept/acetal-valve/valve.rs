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

type Color = [f64; 3];
const ACETAL: Color = [0.79, 0.72, 0.54];
const STEEL: Color = [0.47, 0.54, 0.59];
const SEAL: Color = [0.045, 0.26, 0.14];
const MOTOR: Color = [0.13, 0.17, 0.20];
const INLET: Color = [0.03, 0.29, 0.63];
const RETURN: Color = [0.02, 0.58, 0.53];
const FACE: f64 = -0.55;
const BACK: f64 = 15.65;
const BARREL_R: f64 = 5.90;
const RETURN_N: f64 = -4.42;
const RETURN_R: f64 = 0.48;
const LINER_R: f64 = 3.43;
const SOCKET: V3 = v3(5.55, 0., 4.38);
const BYPASS: V3 = v3(8.1, 0., 4.8);
const REAR_SEAL_OFFSET: V3 = v3(-0.60, 0., -0.55);
const REAR_SEAL_R: f64 = 4.76;
const TUBE_R: f64 = 25.4 * 5. / 64.;
const TUBE_ID_R: f64 = TUBE_R - 25.4 * 0.010;
const MOTOR_S: f64 = 33.3;
const MOTOR_LEN: f64 = 25.4 * 0.550;
const MOTOR_R: f64 = 25.4 * 0.520 / 2.;
const BUSH_S: f64 = MOTOR_S - 25.4 * 0.250;
const LIFT: f64 = 0.6;
const SLOT: f64 = 25.4 * 0.062;
const CLEVIS_S: f64 = MOTOR_S - 25.4 * 0.562 - LIFT;
const PIN_S: f64 = CLEVIS_S + 25.4 * 0.125;
const TIE: V3 = v3(-4.48, 0., 4.45);
const DRY_THREAD_R: f64 = 0.56;

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
            .cut(&axial(1.03, front - 0.05, rear + 0.05)?.translate(offset))?;
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
        (LINER_R, 10.25),
        (2.79, 10.25),
        (2.79, 11.25),
        (LINER_R, 11.25),
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

/// Both ends of the straight reference drilling open on a face that can be machined and inspected.
fn gallery() -> Result<Solid> {
    let channel = axial(RETURN_R, FACE - 0.01, BACK + 0.01)?.translate(v3(0., 0., RETURN_N));
    let back_slot = Solid::cuboid(v3(-RETURN_R, BACK - 0.58, RETURN_N), v3(RETURN_R, BACK + 0.01, -1.5));
    channel.union(&back_slot)
}

fn wet(p: &mut Vec<Piece>, lift: f64) -> Result<()> {
    use front_seat as seat;
    let axis = V3::Y;
    let reference = gallery()?;
    let radial = SOCKET.unit();
    let feed_row = axis * 6.7;
    let cross_feed = bore(feed_row - radial * 7.1, feed_row + SOCKET, 1.58)?;
    let feed_port = axial(TUBE_ID_R, 6.55, 9.15)?.translate(SOCKET);
    let inlet_socket = axial(TUBE_R + 0.035, 9.0, 14.05)?.translate(SOCKET);
    let inlet_gland = axial(TUBE_R + 0.63, 11.65, 12.7)?.translate(SOCKET);
    let relief = axial(2.22, 13.9, 20.1)?.translate(SOCKET);
    let pocket = turn(&[
        (0., FACE - 0.1),
        (seat::BORE_R, FACE - 0.1),
        (seat::THROAT_R, seat::FLOOR_S),
        (seat::WASHER_R + 0.04, seat::FLOOR_S),
        (seat::WASHER_R + 0.04, 0.16),
        (LINER_R + 0.04, 0.16),
        (LINER_R + 0.04, BACK + 0.1),
        (0., BACK + 0.1),
    ])?;
    let nose = axial(BARREL_R, FACE, BACK)?
        .union(&bore(feed_row - radial * 6.6, feed_row + SOCKET, 2.65)?)?
        .union(&axial(3.08, 4.05, 13.9)?.translate(SOCKET))?;
    let front_seal = annulus(5.69, 5.01, FACE - 0.04, FACE + 0.40)?;
    let back_seal = annulus(REAR_SEAL_R + 0.32, REAR_SEAL_R - 0.32, BACK - 0.40, BACK + 0.04)?
        .translate(REAR_SEAL_OFFSET);
    let tap = bore(feed_row - radial * 6.65, feed_row - radial * 4.05, 1.83)?;
    let mut shell = lugged(&nose, 2.6, BACK)?.cut_all(&[
        pocket,
        reference.clone(),
        cross_feed.clone(),
        feed_port.clone(),
        tap,
        inlet_socket.clone(),
        inlet_gland,
        front_seal,
        back_seal,
        relief.clone(),
    ])?;
    for offset in [TIE, -TIE] {
        shell = shell
            .cut(&nut_envelope(2.16, 0.76, 2.60)?.translate(offset))?
            .cut(&axial(1.03, 2.59, BACK + 0.02)?.translate(offset))?;
    }
    add(p, "Acetal_pressure_body", ACETAL, shell, V3::ZERO, true);
    let screw = bore(feed_row - radial * 6.69, feed_row - radial * 4.20, 1.81)?.union(&bore(
        feed_row - radial * 7.19,
        feed_row - radial * 6.69,
        2.34,
    )?)?;
    add(p, "Cross_drilling_closure", STEEL, screw, radial * -4., false);
    add(
        p,
        "Cross_drilling_face_seal",
        SEAL,
        Solid::torus(feed_row - radial * 6.65, radial, 2.10, 0.13)?,
        radial * -2.,
        true,
    );
    let nozzle = turn(&[
        (seat::BORE_R, -2.15),
        (4.25, -2.15),
        (4.25, -0.88),
        (BARREL_R, -0.88),
        (BARREL_R, FACE),
        (4.94, FACE),
        (4.94, -0.78),
        (seat::BORE_R, -0.78),
    ])?;
    add(p, "Acetal_outlet_collector", ACETAL, nozzle, axis * -11., true);
    add(p, "Outlet_face_seal", SEAL, torus(5.35, 0.28, FACE + 0.16)?, axis * -7.8, true);
    add(p, "Captive_EPDM_seat", SEAL, seat::installed_washer()?, axis * -4.5, true);
    let insert = liner()?;
    add(p, "Acetal_seat_cage_and_balance_bore", ACETAL, insert.clone(), v3(-12., 0., 0.), true);
    add(p, "Cage_static_seal", SEAL, torus(3.13, 0.35, 10.75)?, v3(-12., 0., 0.), true);
    let stem = turn(&[
        (0., seat::SEAT_S + 0.12),
        (1.88, seat::SEAT_S + 0.12),
        (seat::SEAT_D / 2. - seat::LIP_HALF_WIDTH, seat::SEAT_S),
        (seat::SEAT_D / 2. + seat::LIP_HALF_WIDTH, seat::SEAT_S),
        (seat::POPPET_R, seat::SEAT_S + 0.14),
        (seat::POPPET_R, 1.53),
        (seat::STEM_R, 1.53),
        (seat::STEM_R, 17.83),
        (DRY_THREAD_R, 17.83),
        (DRY_THREAD_R, 19.75),
        (0., 19.75),
    ])?
    .union(&balance::piston()?)?
    .translate(axis * lift);
    add(p, "Turned_316L_solid_poppet", STEEL, stem.clone(), v3(-23., 0., 0.), false);
    add(
        p,
        "Moving_balance_piston_seal",
        SEAL,
        balance::piston_seal()?.translate(axis * lift),
        v3(-23., 0., 0.),
        true,
    );
    let gland = turn(&[
        (balance::BORE_R, BACK),
        (BARREL_R, BACK),
        (BARREL_R, balance::DRY_BORE_S),
        (balance::ROD_GUIDE_R, balance::DRY_BORE_S),
        (balance::ROD_GUIDE_R, 17.57),
        (balance::ROD_GROOVE_R, 17.57),
        (balance::ROD_GROOVE_R, balance::ROD_GROOVE_S),
        (balance::ROD_GUIDE_R, balance::ROD_GROOVE_S),
        (balance::ROD_GUIDE_R, balance::LOW_CHAMBER_END_S),
        (balance::BORE_R, balance::LOW_CHAMBER_END_S),
    ])?;
    let boss = annulus(3.41, 2.10, 14.90, BACK + 0.01)?
        .cut(&Solid::cuboid(v3(-0.60, 14.89, -3.5), v3(0.60, BACK + 0.02, -1.6)))?;
    add(
        p,
        "Acetal_rod_gland",
        ACETAL,
        lugged(&gland.union(&boss)?, BACK, balance::DRY_BORE_S)?.cut(&relief)?,
        axis * 7.,
        true,
    );
    add(
        p,
        "Rear_face_seal",
        SEAL,
        torus(REAR_SEAL_R, 0.28, BACK - 0.16)?.translate(REAR_SEAL_OFFSET),
        axis * 3.4,
        true,
    );
    add(p, "Dry_rod_seal", SEAL, balance::rod_seal()?, axis * 7., true);
    add(p, "Supply_tube_seal", SEAL, torus(2.27, 0.36, 12.175)?.translate(SOCKET), v3(5., 1., 0.), true);
    for (n, offset) in [("Tie_screw_left", TIE), ("Tie_screw_right", -TIE)] {
        let nut = nut_envelope(2.10, 0.95, 2.60)?;
        let screw = axial(0.98, 0.85, 19.56)?.union(&axial(1.67, 19.55, 20.37)?)?.union(&nut)?;
        add(p, n, STEEL, screw.translate(offset), offset.unit() * 4., false);
    }
    let outlet = seat::outlet_volume()?;
    let mut low_at_lip = outlet.clone();
    if lift > 0. {
        low_at_lip = low_at_lip.union(&outlet.translate(axis * lift))?.union(&axial(
            seat::SEAT_D / 2.,
            seat::SEAT_S,
            seat::SEAT_S + lift,
        )?)?;
    }
    let pressure = axial(2.64, seat::CLAMP_S, 11.57)?
        .union(&axial(balance::BORE_R, 11.53, balance::PISTON_S + lift)?)?
        .union(&bore(feed_row - radial * 4.20, feed_row + SOCKET, 1.58)?)?
        .union(&feed_port)?
        .cut(&insert)?
        .cut(&stem)?
        .cut(&seat::installed_washer()?)?
        .cut(&low_at_lip)?;
    add(p, "Water_supply_at_seat", INLET, pressure, V3::ZERO, true);
    let drain = axial(seat::BORE_R, -2.15, seat::FLOOR_S)?
        .union(&axial(4.94, -0.78, FACE)?)?
        .union(&reference)?
        .union(&axial(balance::BORE_R, 14.2 + lift, balance::LOW_CHAMBER_END_S)?)?
        .union(&axial(3.46, 14.90, BACK)?)?
        .union(&outlet)?
        .cut(&boss)?
        .cut(&stem)?;
    add(p, "Water_outlet_and_balance_reference", RETURN, drain, V3::ZERO, true);
    Ok(())
}

/// The fork, mounting bush and can use the purchased solenoid's external dimensions.
fn drive(p: &mut Vec<Piece>, lift: f64) -> Result<()> {
    let axis = V3::Y;
    let move_by = axis * lift;
    let spring_front = 18.78;
    let fixed = BUSH_S - 0.2;
    let fork_pockets =
        axial(2.52, 17.98, 19.84)?.cut(&Solid::cuboid(v3(-0.69, 17.96, -2.60), v3(0.69, 19.86, 2.60)))?;
    let eye = annulus(3.55, DRY_THREAD_R + 0.015, 17.88, spring_front)?
        .union(&annulus(1.28, DRY_THREAD_R + 0.015, 18.5, 19.77)?)?
        .cut(&fork_pockets)?;
    let tongue = Solid::cuboid(v3(-0.67, 19.69, -1.37), v3(0.67, PIN_S + 1.29, 1.37)).cut(&axial(
        DRY_THREAD_R + 0.015,
        19.60,
        19.78,
    )?)?;
    let pin = bore(v3(-2.45, PIN_S, 0.), v3(2.45, PIN_S, 0.), 0.775)?;
    let pin_clear = bore(v3(-2.75, PIN_S, 0.), v3(2.75, PIN_S, 0.), 0.806)?;
    add(
        p,
        "Dry_threaded_link_eye",
        STEEL,
        eye.union(&tongue)?.cut(&pin_clear)?.translate(move_by),
        v3(-22., 4., 0.),
        false,
    );
    add(p, "Stock_clevis_pin", STEEL, pin.translate(move_by), v3(-29., 4., 0.), false);
    let fork = axial(25.4 * 0.185 / 2., CLEVIS_S, MOTOR_S + 1.3)?
        .cut(&Solid::cuboid(v3(-SLOT / 2., CLEVIS_S - 0.1, -3.), v3(SLOT / 2., PIN_S + 1.54, 3.)))?
        .cut(&pin_clear)?;
    add(p, "Ledex_clevis_plunger", MOTOR, fork.translate(move_by), axis * 18., false);
    let spring_r = 2.99;
    let pitch = (fixed - spring_front - lift - 0.32) / 8.;
    let start = v3(spring_r, spring_front + lift + 0.16, 0.);
    let spring = Plane::new(start, V3::X, v3(0., pitch, -std::f64::consts::TAU * spring_r))?.helix_sweep(
        &Profile::circle(v2(0., 0.), 0.16),
        v3(0., start.y, 0.),
        axis,
        pitch,
        8.,
    )?;
    add(p, "Stock_return_spring", STEEL, spring, v3(-11., 8., 0.), false);
    let base = lugged(&annulus(5.4, 3.70, balance::DRY_BORE_S, 19.55)?, balance::DRY_BORE_S, 19.55)?;
    let retainer = bore(v3(4.1, 19.13, 2.45), SOCKET + axis * 19.13, 0.90)?
        .union(&annulus(2.80, TUBE_R + 0.035, 18.73, 19.55)?.translate(SOCKET))?;
    let mut cage = base
        .union(&retainer)?
        .cut(&axial(TUBE_R + 0.035, 17.6, 20.5)?.translate(SOCKET))?
        .cut(&axial(TUBE_R + 0.29, 17.65, 18.73)?.translate(SOCKET))?;
    for x in [-4.53, 4.53] {
        cage = cage.union(&axial(0.86, 19.47, fixed + 0.60)?.translate(v3(x, 0., 0.)))?;
    }
    let cap = annulus(5.72, 2.55, fixed, BUSH_S)?.union(&annulus(5.72, 4.755, BUSH_S, MOTOR_S)?)?;
    add(
        p,
        "Acetal_motor_mount_and_tube_keeper",
        ACETAL,
        cage.union(&cap)?.cut(&axial(4.80, BUSH_S - 0.005, MOTOR_S + 0.01)?)?,
        axis * 11.,
        true,
    );
    let motor = axial(MOTOR_R, MOTOR_S, MOTOR_S + MOTOR_LEN)?
        .union(&annulus(25.4 * 0.375 / 2., 2.43, BUSH_S, MOTOR_S + 0.02)?)?
        .cut(&axial(2.43, MOTOR_S - 0.02, MOTOR_S + 2.05)?)?;
    add(p, "Bought_Ledex_195200_234", MOTOR, motor, axis * 24., false);
    Ok(())
}

/// A formed stock tube and an end-drilled acetal adapter connect the existing crimped hose to the valve.
fn tubing(p: &mut Vec<Piece>, neck: &Gooseneck, frame: &Plane) -> Result<()> {
    let (point, tangent, normal) = neck.frame(neck.length() - 58.);
    let join_world = point + normal * shell::TUBE_SHELL_CENTER_Y;
    let (xy, n) = frame.local(join_world);
    let join = v3(xy.x, xy.y, n);
    let d = v3(-tangent.dot(frame.x), -tangent.dot(frame.y), -tangent.dot(frame.z));
    let start = SOCKET + V3::Y * 9.;
    let first = SOCKET + V3::Y * 20.1;
    let side = BYPASS + V3::Y * 31.2;
    let approach = BYPASS + V3::Y * 40.;
    let straight = v3(8.0, 47.2, 4.15);
    let slope = v3(-0.25, 1., -0.34);
    let rail = |s| straight + slope * (s - straight.y);
    let socket_bore = |r, a, b| bore(rail(a), rail(b), r);
    let stop_s = 53.1;
    let path = Path::new(start)
        .line_to(first)
        .bezier(&[first, first + V3::Y * 4.2, side - V3::Y * 4.2, side])?
        .line_to(approach)
        .bezier(&[approach, approach + V3::Y * 2.60, straight - slope * 2.85, straight])?
        .line_to(rail(stop_s));
    let tube = Plane::new(start, V3::X, V3::Y)?
        .sweep(&Profile::circle(v2(0., 0.), TUBE_R).with_hole(Loop::circle(v2(0., 0.), TUBE_ID_R)), &path)?;
    let bead = torus(TUBE_R, 0.23, 18.50)?.translate(SOCKET);
    add(p, "Stock_316L_soda_tube", STEEL, tube.union(&bead)?, v3(5., 0., 3.), false);
    let port = rail(stop_s + 1.1);
    let diagonal = (join - port).unit();
    let hose_face = Plane::new(join, V3::X, d)?;
    let trim = hose_face.extrude(&Profile::rect(v2(0., 0.), 36., 36.), 16.)?;
    let distal_seal = socket_bore(TUBE_R + 0.63, 50.9, 51.95)?;
    let adapter = socket_bore(3.02, 50.1, stop_s + 3.6)?
        .union(&bore(port - diagonal * 0.32, join, 2.62)?)?
        .union(&bore(join - d * 2.35, join, 3.65)?)?
        .cut(&trim)?
        .cut(&socket_bore(TUBE_R + 0.035, 50.0, stop_s)?)?
        .cut(&distal_seal)?
        .cut(&socket_bore(TUBE_ID_R, stop_s - 0.05, stop_s + 1.75)?)?
        .cut(&bore(port - diagonal * 0.22, join + diagonal * 3.0, TUBE_ID_R)?)?
        .cut(&bore(join - d * 1.35, join + d * 0.06, 3.0)?)?;
    add(p, "Acetal_drilled_hose_adapter", ACETAL, adapter, v3(5., 7., 3.), false);
    add(
        p,
        "Hose_adapter_tube_seal",
        SEAL,
        Solid::torus(rail(51.425), slope, 2.27, 0.36)?,
        v3(5., 4., 3.),
        false,
    );
    Ok(())
}

type View = Vec<(String, Color, Solid)>;

fn write(dir: &Dir, name: &str, view: &View) -> Result<()> {
    let shapes: Vec<_> = view.iter().map(|(n, c, s)| (n.as_str(), *c, s)).collect();
    show(dir, name, &shapes)
}

/// A section looks into the balance drilling and leaves the moving metal intact.
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
    let frame = hsm_faucet::display::tip_plane(&neck)?;
    let mut closed = vec![];
    let mut open = vec![];
    wet(&mut closed, 0.)?;
    wet(&mut open, LIFT)?;
    write(&dir, "seat-closed", &wet_view(&closed, 0.)?)?;
    write(&dir, "seat-open", &wet_view(&open, LIFT)?)?;
    drive(&mut closed, 0.)?;
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
        let barb = name == "head_valve_integral_hose_barb" || name.starts_with("head_valve_barb_ridge_");
        if name == "pull_off_curved_grip" {
            let grip = body.solid.cut(&flange_relief)?;
            full.push((name.clone(), body.color.unwrap_or(MOTOR), grip.clone()));
            installed.push((name.clone(), body.color.unwrap_or(MOTOR), grip.cut(&window)?));
        } else if barb
            || name == "soft_hose_strain_relief"
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
