//! The reed sweep rig's files: each printed piece on the face it prints on, the numbers the
//! rig's controller and its log reader take, and the rig drawn assembled round the bought slide,
//! the tube, a float and four reeds.
//!
//!     reed-sweep-rig <output directory> [--fits]
//!
//! `--fits` measures the built solids against each other instead and prints how the pieces sit:
//! what touches, what clears, and by how much.
use anyhow::{Result, ensure};
use hsm_aero_float_numbers as float;
use hsm_carbonator_tube_numbers as tube;
use hsm_kernel::part::{write_part, write_shown};
use hsm_kernel::{Body, Font, HAlign, Kind, Plane, Profile, Solid, V3, VAlign, v2, v3};
use hsm_reed_bridge_numbers as bridge;
use hsm_sandbox::{material, out};
use serde_json::json;

#[path = "numbers.rs"]
mod n;
use n::{slide, switch};

const X: V3 = v3(1., 0., 0.);
const Y: V3 = v3(0., 1., 0.);
const Z: V3 = v3(0., 0., 1.);
/// What a cutting tool runs on past the face it leaves by, so no two faces coincide.
const PAST: f64 = 1.;

fn main() -> Result<()> {
    let dir = out()?;
    let font = Font::find("Helvetica Neue", Kind::Bold)?;
    let petgf = material("M_PETGF_BLACK")?;

    let cradle = piece("cradle", cradle()?)?;
    let comb = piece("comb", comb(&font)?)?;
    let rod_printed = piece("rod", rod(home_pin(), n::ROLLER_PRELOAD)?)?;
    let rod = piece("rod", rod(home_pin(), 0.)?)?;
    let sleds = n::sleds()
        .into_iter()
        .map(|(name, offset)| Ok((name, piece(name, sled(offset, &name.to_uppercase(), &font)?)?)))
        .collect::<Result<Vec<_>>>()?;
    if std::env::args().nth(2).as_deref() == Some("--fits") {
        return fits(&cradle, &comb, &sleds);
    }

    // Each piece on the face it prints on.
    let printed = |file: &str, name: &str, solid: &Solid| -> Result<()> {
        write_part(&dir, file, &[Body { name, color: Some(petgf), solid }])?;
        let size = solid.bounds().size();
        println!("{file}: {:.1} x {:.1} x {:.1} mm, {:.1} cm3", size.x, size.y, size.z, solid.volume() / 1000.);
        Ok(())
    };
    printed("reed-sweep-rig-cradle", "cradle", &cradle)?;
    printed("reed-sweep-rig-comb", "reed-comb", &comb.translate(v3(0., 0., -n::POCKET_FLOOR)))?;
    printed("reed-sweep-rig-rod", "push-rod", &rod_on_its_side(&rod_printed))?;
    for (name, sled) in &sleds {
        printed(&format!("reed-sweep-rig-sled-{name}"), &format!("float-sled-{name}"), &sled_on_its_top(sled))?;
    }

    std::fs::write(dir.join("reed-sweep-rig-datums.json"), serde_json::to_string_pretty(&numbers())? + "\n")?;

    // The rig assembled, with the sled at its home.
    let (_, nominal) = sleds.iter().find(|(name, _)| *name == "nominal").expect("a nominal sled");
    let at_home = v3(n::HOME_BEFORE_TAB, 0., n::BORE_BOTTOM_Z);
    let sled = nominal.translate(at_home);
    let (tube, float, reeds) = (tube()?, float_at(n::HOME_BEFORE_TAB)?, reeds()?);
    let (frame, screw, carriage, motor) = slide_drawn()?;
    let (board, lever_switch, striker) = switch_drawn()?;
    let (steel, alloy, glass, brass) = (material("M_STAINLESS")?, material("M_ALUMINIUM")?, material("M_GLASS")?, material("M_BRASS")?);
    // The catalog keeps the foamed ASA's colour as a hex string, which the sandbox's reader does not take.
    let aero = [0.855, 0.776, 0.552];
    write_shown(
        &dir,
        "reed-sweep-rig-assembly",
        &[
            Body { name: "cradle", color: Some(petgf), solid: &cradle },
            Body { name: "reed-comb", color: Some(petgf), solid: &comb },
            Body { name: "float-sled-nominal", color: Some(petgf), solid: &sled },
            Body { name: "push-rod", color: Some(petgf), solid: &rod },
            Body { name: "carbonator-tube", color: Some(steel), solid: &tube },
            Body { name: "aero-float", color: Some(aero), solid: &float },
            Body { name: "reeds", color: Some(glass), solid: &reeds },
            Body { name: "slide-frame", color: Some(alloy), solid: &frame },
            Body { name: "slide-screw", color: Some(steel), solid: &screw },
            Body { name: "slide-carriage", color: Some(alloy), solid: &carriage },
            Body { name: "slide-motor", color: Some(steel), solid: &motor },
            Body { name: "home-switch-board", color: Some(brass), solid: &board },
            Body { name: "home-switch", color: Some(steel), solid: &lever_switch },
            Body { name: "striker-screw", color: Some(steel), solid: &striker },
        ],
    )?;
    println!("{}", dir.join("reed-sweep-rig-assembly.step").display());
    Ok(())
}

/// A printed piece: one closed solid.
fn piece(name: &str, solid: Solid) -> Result<Solid> {
    solid.check()?;
    ensure!(solid.components().len() == 1, "the {name} is {} pieces", solid.components().len());
    Ok(solid)
}

fn slab(x0: f64, x1: f64, y0: f64, y1: f64, z0: f64, z1: f64) -> Solid {
    Solid::cuboid(v3(x0, y0.min(y1), z0), v3(x1, y0.max(y1), z1))
}

/// The roller's axis along the rig when the sled stands at its home.
fn home_pin() -> f64 {
    n::HOME_BEFORE_TAB + n::roller_from_sled_face()
}

// --- The cradle --------------------------------------------------------------------------------

/// The slab the comb and the tube lie on, with the keepers either side of the tube, the home
/// switch's pad on the nose, and the cheeks that take the slide's far end.
fn cradle() -> Result<Solid> {
    let hw = n::CRADLE_HALF_WIDTH;
    let (x0, x1) = (-n::NOSE, tube::LENGTH + n::TAIL);
    let sunk = n::SLAB - PAST;
    let mut stock = vec![slab(x0, x1, -hw, hw, 0., n::SLAB)];
    for side in [-1., 1.] {
        stock.push(slab(n::KEEPER_INSET, tube::LENGTH - n::KEEPER_INSET, side * n::KEEPER_INNER, side * n::KEEPER_OUTER, sunk, n::keeper_top()));
    }
    let (pad_x0, pad_x1) = switch_pad_span();
    let pad_half = switch::BOARD_LENGTH / 2. + n::SWITCH_PAD_MARGIN;
    stock.push(slab(pad_x0, pad_x1, -pad_half, pad_half, sunk, n::switch_pad_top()));
    let reach = slide::BASE_WIDTH / 2. + n::CHEEK_CLEARANCE;
    for side in [-1., 1.] {
        let inner = n::SLIDE_OFFSET + side * reach;
        stock.push(slab(x0 - n::CHEEK_LENGTH, x0 + n::CHEEK_ROOT, inner, inner + side * n::CHEEK, 0., n::CHEEK_HEIGHT));
    }
    let body = Solid::union_all(&stock)?;

    let (room, top) = (n::COMB_CLEARANCE, n::switch_pad_top() + PAST);
    let half = n::COMB_HALF_WIDTH + room;
    let mut tools = vec![
        slab(-n::TAB - room, n::comb_end() + room, -half, half, n::POCKET_FLOOR, top),
        slab(n::comb_end(), x1 + PAST, n::WIRE_TROUGH.0, n::WIRE_TROUGH.1, n::POCKET_FLOOR, top),
    ];
    for side in [-1., 1.] {
        let base = v3(switch_hole_x(), side * switch::HOLE_PITCH / 2., n::switch_pad_top() - n::INSERT_DEPTH);
        tools.push(Solid::cylinder(base, Z, n::INSERT_HOLE / 2., n::INSERT_DEPTH + PAST)?);
    }
    body.cut_all(&tools)
}

fn switch_pad_span() -> (f64, f64) {
    (n::SWITCH_EDGE_X - switch::BOARD_WIDTH - n::SWITCH_PAD_MARGIN, n::SWITCH_EDGE_X + n::SWITCH_PAD_LEAD)
}

fn switch_hole_x() -> f64 {
    n::SWITCH_EDGE_X - switch::HOLE_INSET
}

// --- The reed comb -----------------------------------------------------------------------------

/// The strip under the tube: its crown carries the tube on the reed line, its pockets lay each
/// reed's glass along that line, and its tab is the stop the tube's rim and the sled share.
fn comb(font: &Font) -> Result<Solid> {
    let hw = n::COMB_HALF_WIDTH;
    let (x0, x1) = (-n::TAB, n::comb_end());
    let top = n::BORE_BOTTOM_Z + n::TAB_RISE;
    let over = top + PAST;
    let blank = slab(x0, x1, -hw, hw, n::POCKET_FLOOR, top);

    let floor = n::POCKET_FLOOR + n::COMB_FLOOR;
    let deep = n::POCKET_FLOOR + n::GROOVE_FLOOR;
    let lead_floor = floor + bridge::REED_GLASS_DIAMETER / 2. - n::LEAD_DROP;
    let (length, width) = (bridge::pocket_length(), bridge::pocket_width());
    let slit = n::LEAD_SLIT / 2.;
    let stations = n::stations();
    let grooves_from = stations[0].1 - length / 2. - n::LEAD_RUN;
    // The saddle from the tube's rim on, less the land the tube rests on.
    let land = slab(-PAST, x1 + 2. * PAST, -n::CROWN_LAND, n::CROWN_LAND, n::POCKET_FLOOR - PAST, n::TUBE_BOTTOM_Z);
    let mut tools = vec![
        Solid::cylinder(v3(0., 0., n::saddle_axis_z()), X, n::saddle_radius(), x1 + PAST)?.cut(&land)?,
        slab(grooves_from, x1 + PAST, n::SIGNAL_GROOVE.0, n::SIGNAL_GROOVE.1, deep, over),
        slab(grooves_from, x1 + PAST, n::RETURN_GROOVE.0, n::RETURN_GROOVE.1, deep, over),
    ];
    // Where the saddle stands at the station numbers' line, off the reed line.
    let label_z = n::saddle_axis_z() - (n::saddle_radius().powi(2) - n::STATION_LABEL_Y.powi(2)).sqrt();
    for (number, (_, at)) in stations.into_iter().enumerate() {
        let plane = Plane::XY.at(v3(at, n::STATION_LABEL_Y, label_z - n::STATION_LABEL_DEPTH));
        tools.push(plane.text(font, &(number + 1).to_string(), n::STATION_LABEL_SIZE, n::STATION_LABEL_DEPTH + PAST, HAlign::Center, VAlign::Center)?);
        let (near, far) = (at - length / 2., at + length / 2.);
        tools.push(slab(near, far, -width / 2., width / 2., floor, over));
        // The near lead runs to the signal groove, the far lead to the return's.
        tools.push(slab(near - n::LEAD_RUN, near + PAST, -slit, slit, lead_floor, over));
        tools.push(slab(near - n::LEAD_RUN, near - n::LEAD_RUN + n::LEAD_NOTCH, -slit, n::SIGNAL_GROOVE.0 + PAST, deep, over));
        tools.push(slab(far - PAST, far + n::LEAD_RUN, -slit, slit, lead_floor, over));
        tools.push(slab(far + n::LEAD_RUN - n::LEAD_NOTCH, far + n::LEAD_RUN, n::RETURN_GROOVE.1 - PAST, slit, deep, over));
    }
    blank.cut_all(&tools)
}

// --- The float sled ----------------------------------------------------------------------------

/// A sled in its own frame: lengths from its near face, heights from the bore's lowest line. The
/// float lies in the vee with its bottom face on the datum wall, and `offset` moves its seat away
/// from the reeds.
fn sled(offset: f64, label: &str, font: &Font) -> Result<Solid> {
    let (hw, length, top) = (n::SLED_HALF_WIDTH, n::sled_length(), n::SLED_TOP);
    let block = slab(0., length, -hw, hw, -PAST, top);
    let clear = Solid::cylinder(v3(-PAST, 0., n::BORE_RADIUS), X, n::BORE_RADIUS - n::SLED_UNDER, length + 2. * PAST)?;
    let mut stock = vec![block.intersect(&clear)?];
    let (edge, land) = (n::runner_edge(), n::runner_land());
    for side in [-1., 1.] {
        stock.push(slab(0., length, side * (edge - n::RUNNER_WIDTH), side * edge, land, land + n::RUNNER_DEPTH));
    }
    let body = Solid::union_all(&stock)?;

    // The vee the float lies in: its faces meet the float either side of its lowest line.
    let apex = n::vee_apex(offset);
    let (seat, back) = (n::seat_start(), n::back_wall_start());
    let wide = 2. * hw;
    let vee = Plane::YZ.at(v3(seat, 0., 0.)).extrude(&Profile::polygon(&[v2(0., apex), v2(wide, apex + wide), v2(-wide, apex + wide)]), back - seat)?;
    let hw_text = hw - n::LABEL_DEPTH;
    let names = [
        Plane::new(v3(length / 2., hw_text, (top + n::LABEL_FLOOR) / 2.), v3(-1., 0., 0.), Y)?,
        Plane::new(v3(length / 2., -hw_text, (top + n::LABEL_FLOOR) / 2.), X, v3(0., -1., 0.))?,
    ];
    let mut tools = vec![
        vee,
        slab(seat, back, -n::OPEN_HALF_WIDTH, n::OPEN_HALF_WIDTH, -2. * PAST, top + PAST),
        slab(n::FRONT_WALL, n::FRONT_WALL + n::SLOT, -n::SLOT_HALF_SPAN, n::SLOT_HALF_SPAN, n::SLOT_FLOOR, top + PAST),
        slab(-PAST, seat + PAST, -n::SLOT_HALF_SPAN, n::SLOT_HALF_SPAN, n::SLOT_WALL_TOP, top + PAST),
        slab(back - PAST, length + PAST, -n::GAUGE_WINDOW_HALF_WIDTH, n::GAUGE_WINDOW_HALF_WIDTH, -2. * PAST, n::GAUGE_WINDOW_HEIGHT),
    ];
    for plane in names {
        tools.push(plane.text(font, label, n::LABEL_SIZE, n::LABEL_DEPTH + PAST, HAlign::Center, VAlign::Center)?);
    }
    let body = body.cut_all(&tools)?;

    // The leaf: rooted in one rail along the vee's face, free of the other by a slit, with a pad
    // that stands in the float's way.
    let half = |z: f64| z - apex;
    let (low, start) = (n::LEAF_BOTTOM, n::leaf_start());
    let outline = Profile::polygon(&[
        v2(-half(low) - n::LEAF_ROOT, low),
        v2(half(low) - n::LEAF_SLIT, low),
        v2(half(top) - n::LEAF_SLIT, top),
        v2(-half(top) - n::LEAF_ROOT, top),
    ]);
    let leaf = Plane::YZ.at(v3(start, 0., 0.)).extrude(&outline, n::LEAF)?;
    let pad = slab(start - n::LEAF_PAD, start + n::LEAF / 2., -n::LEAF_PAD_HALF_WIDTH, n::LEAF_PAD_HALF_WIDTH, low + n::LEAF_PAD_RISE, top);
    Solid::union_all(&[body, leaf, pad])
}

/// The sled as it prints: top face on the bed, runners up.
fn sled_on_its_top(sled: &Solid) -> Solid {
    sled.rotate(V3::ZERO, X, 180.).translate(v3(0., 0., n::SLED_TOP))
}

// --- The push rod ------------------------------------------------------------------------------

/// The rod with its roller's axis at `pin` along the rig: the pad that bolts down on the
/// carriage, the bar along the carriage's side with its flexure, the leg down into the tube's
/// mouth, the stem and roller that stand in the sled's slot, and the finger that carries the
/// striker screw. `drop` lowers everything the flexure carries: none as the rod rides the sled,
/// the preload as it prints.
fn rod(pin: f64, drop: f64) -> Result<Solid> {
    let half = n::ROD_THICKNESS / 2.;
    let (bottom, foot, roller) = (slide::CARRIAGE_TOP, n::leg_bottom() - drop, n::BORE_BOTTOM_Z + n::ROLLER_RISE - drop);
    let top = bottom + n::BAR;
    let carriage = pin - n::ROD_REACH;
    let back = carriage - slide::CARRIAGE_LENGTH / 2.;
    let (behind, ahead, stem) = (pin - n::LEG_BEHIND, pin + n::LEG_AHEAD, n::STEM / 2.);
    // The flexure, on the bar's own middle line.
    let (flex_from, flex_to) = (back + slide::CARRIAGE_LENGTH + n::FLEXURE_START, back + slide::CARRIAGE_LENGTH + n::FLEXURE_START + n::FLEXURE_LENGTH);
    let (under, over) = ((bottom + top - n::FLEXURE) / 2., (bottom + top + n::FLEXURE) / 2.);
    let outline = Profile::polygon(&[
        v2(back, bottom),
        v2(flex_from, bottom),
        v2(flex_from + n::FLEXURE_TAPER, under),
        v2(flex_to - n::FLEXURE_TAPER, under),
        v2(flex_to, bottom),
        v2(behind, bottom),
        v2(behind, foot + n::FINGER_HEIGHT),
        v2(behind - n::FINGER, foot + n::FINGER_HEIGHT),
        v2(behind - n::FINGER, foot),
        v2(pin - stem, foot),
        v2(pin - stem, roller),
        v2(pin + stem, roller),
        v2(pin + stem, foot),
        v2(ahead, foot),
        v2(ahead, top),
        v2(flex_to, top),
        v2(flex_to - n::FLEXURE_TAPER, over),
        v2(flex_from + n::FLEXURE_TAPER, over),
        v2(flex_from, top),
        v2(back, top),
    ]);
    let side = Plane::XZ.at(v3(0., half, 0.)).extrude(&outline, n::ROD_THICKNESS)?;
    let wheel = Solid::cylinder(v3(pin, -half, roller), Y, n::ROLLER / 2., n::ROD_THICKNESS)?;
    let pad = slab(back, back + slide::CARRIAGE_LENGTH, half - PAST, n::SLIDE_OFFSET + slide::CARRIAGE_WIDTH / 2., bottom, bottom + n::PAD);
    let body = Solid::union_all(&[side, wheel, pad])?;

    let mut tools = vec![Solid::cylinder(v3(behind - n::FINGER - PAST, 0., n::striker_z() - drop), X, n::INSERT_HOLE / 2., n::STRIKER_HOLE_DEPTH + PAST)?];
    for along in [-1., 1.] {
        for across in [-1., 1.] {
            let base = v3(carriage + along * slide::HOLE_PITCH / 2., n::SLIDE_OFFSET + across * slide::HOLE_PITCH / 2., bottom - PAST);
            tools.push(Solid::cylinder(base, Z, n::M4_CLEARANCE / 2., n::PAD + 2. * PAST)?);
        }
    }
    body.cut_all(&tools)
}

/// The rod as it prints: on the side its bar and pad share.
fn rod_on_its_side(rod: &Solid) -> Solid {
    let laid = rod.rotate(V3::ZERO, X, 90.);
    let low = laid.bounds().min;
    laid.translate(v3(-low.x, -low.y, -low.z))
}

// --- What the rig is drawn round ---------------------------------------------------------------

fn tube() -> Result<Solid> {
    let outer = Solid::cylinder(v3(0., 0., n::TUBE_AXIS_Z), X, tube::OUTER_RADIUS, tube::LENGTH)?;
    outer.cut(&Solid::cylinder(v3(-PAST, 0., n::TUBE_AXIS_Z), X, n::BORE_RADIUS, tube::LENGTH + 2. * PAST)?)
}

/// The float on the nominal sled, with the sled's near face at `sled`.
fn float_at(sled: f64) -> Result<Solid> {
    let axis = n::BORE_BOTTOM_Z + n::seat_axis(0.);
    let start = sled + n::seat_start();
    let body = Solid::cylinder(v3(start, 0., axis), X, float::DIAMETER / 2., float::height())?;
    body.cut(&Solid::cylinder(v3(start - PAST, 0., axis), X, float::BORE_DIAMETER / 2., float::height() + 2. * PAST)?)
}

fn reeds() -> Result<Solid> {
    let axis = n::POCKET_FLOOR + n::COMB_FLOOR + bridge::REED_GLASS_DIAMETER / 2.;
    let glass = n::stations()
        .into_iter()
        .map(|(_, at)| Solid::cylinder(v3(at - bridge::REED_GLASS_LENGTH / 2., 0., axis), X, bridge::REED_GLASS_DIAMETER / 2., bridge::REED_GLASS_LENGTH))
        .collect::<Result<Vec<_>>>()?;
    Ok(Solid::compose(&glass))
}

/// The slide with its carriage where the sled's home puts it: the frame, the screw, the carriage
/// and the motor.
fn slide_drawn() -> Result<(Solid, Solid, Solid, Solid)> {
    let (far, mid) = (-n::NOSE, n::SLIDE_OFFSET);
    let near = far - slide::FRAME_LENGTH;
    let half = slide::BASE_WIDTH / 2.;
    let block = near + slide::END_PLATE + slide::COUPLING_BAY;
    let frame = Solid::compose(&[
        slab(near + slide::END_PLATE, far - slide::END_PLATE, mid - half, mid + half, 0., slide::BASE_HEIGHT),
        slab(far - slide::END_PLATE, far, mid - half, mid + half, 0., slide::END_PLATE_HEIGHT),
        slab(near, near + slide::END_PLATE, mid - slide::MOTOR_PLATE_WIDTH / 2., mid + slide::MOTOR_PLATE_WIDTH / 2., 0., slide::MOTOR_PLATE_HEIGHT),
        slab(block, block + slide::BEARING_BLOCK, mid - half, mid + half, slide::BASE_HEIGHT, slide::END_PLATE_HEIGHT),
    ]);
    let screw = Solid::cylinder(v3(block, mid, slide::SCREW_AXIS), X, slide::SCREW_DIAMETER / 2., far - slide::END_PLATE - block)?;
    let at = home_pin() - n::ROD_REACH;
    let carriage = slab(
        at - slide::CARRIAGE_LENGTH / 2.,
        at + slide::CARRIAGE_LENGTH / 2.,
        mid - slide::CARRIAGE_WIDTH / 2.,
        mid + slide::CARRIAGE_WIDTH / 2.,
        slide::CARRIAGE_BOTTOM,
        slide::CARRIAGE_TOP,
    );
    let motor = slab(near - slide::MOTOR_LENGTH, near, mid - slide::MOTOR_FACE / 2., mid + slide::MOTOR_FACE / 2., slide::SCREW_AXIS - slide::MOTOR_FACE / 2., slide::SCREW_AXIS + slide::MOTOR_FACE / 2.);
    Ok((frame, screw, carriage, motor))
}

/// The home switch on its pad and the striker screw in the rod's finger, at the sled's home.
fn switch_drawn() -> Result<(Solid, Solid, Solid)> {
    let (edge, top) = (n::SWITCH_EDGE_X, n::switch_pad_top());
    let deck = top + switch::BOARD_THICKNESS;
    let board = slab(edge - switch::BOARD_WIDTH, edge, -switch::BOARD_LENGTH / 2., switch::BOARD_LENGTH / 2., top, deck);
    let body = slab(edge - switch::BODY_WIDTH, edge, -switch::BODY_LENGTH / 2., switch::BODY_LENGTH / 2., deck, deck + switch::BODY_HEIGHT);
    let finger_end = home_pin() - n::LEG_BEHIND - n::FINGER;
    let under_head = finger_end - n::STRIKER_PROUD;
    let striker = Solid::compose(&[
        Solid::cylinder(v3(under_head - n::STRIKER_HEAD_HEIGHT, 0., n::striker_z()), X, n::STRIKER_HEAD / 2., n::STRIKER_HEAD_HEIGHT)?,
        Solid::cylinder(v3(under_head, 0., n::striker_z()), X, n::STRIKER_SHANK / 2., n::STRIKER_LENGTH)?,
    ]);
    Ok((board, body, striker))
}

// --- How the pieces sit ------------------------------------------------------------------------

/// The clearance between two solids and the volume they share, as one line.
fn fit(what: &str, a: &Solid, b: &Solid) -> Result<()> {
    println!("{what:<58} clears {:>7.3} mm, shares {:>8.3} mm3", a.gap(b)?, a.shared_volume(b)?);
    Ok(())
}

/// Every fit the rig depends on, measured on the solids: at the sled's home, and with the sled
/// as deep as it goes.
fn fits(cradle: &Solid, comb: &Solid, sleds: &[(&str, Solid)]) -> Result<()> {
    let (tube, reeds) = (tube()?, reeds()?);
    let (frame, _, _, _) = slide_drawn()?;
    let (_, lever_switch, striker) = switch_drawn()?;
    fit("tube on the comb's crown", &tube, comb)?;
    fit("tube and the cradle's keepers", &tube, cradle)?;
    fit("reeds under the tube's wall", &reeds, &tube)?;
    fit("reeds in the comb's pockets", &reeds, comb)?;
    fit("comb in the cradle's pocket", comb, cradle)?;
    for (name, sled) in sleds {
        let offset = n::sleds().into_iter().find(|(known, _)| known == name).expect("a known sled").1;
        let axis = n::BORE_BOTTOM_Z + n::seat_axis(offset);
        let start = n::HOME_BEFORE_TAB + n::seat_start();
        let float = Solid::cylinder(v3(start, 0., axis), X, float::DIAMETER / 2., float::height())?;
        let placed = sled.translate(v3(n::HOME_BEFORE_TAB, 0., n::BORE_BOTTOM_Z));
        fit(&format!("{name} sled's runners on the bore"), &placed, &tube)?;
        fit(&format!("{name} sled's float off the wall"), &float, &tube)?;
        fit(&format!("{name} sled's vee, datum wall and leaf on the float"), &float, &placed)?;
    }
    let (_, nominal) = sleds.iter().find(|(name, _)| *name == "nominal").expect("a nominal sled");
    for (place, at) in [("home", n::HOME_BEFORE_TAB), ("deepest", n::sled_deepest())] {
        let sled = nominal.translate(v3(at, 0., n::BORE_BOTTOM_Z));
        let rod = rod(at + n::roller_from_sled_face(), 0.)?;
        fit(&format!("at {place}: roller in the sled's slot"), &rod, &sled)?;
        fit(&format!("at {place}: rod and the float"), &rod, &float_at(at)?)?;
        fit(&format!("at {place}: rod and the tube"), &rod, &tube)?;
        fit(&format!("at {place}: rod and the cradle"), &rod, cradle)?;
        fit(&format!("at {place}: rod and the comb"), &rod, comb)?;
        fit(&format!("at {place}: rod and the slide's frame"), &rod, &frame)?;
        fit(&format!("at {place}: sled and the comb's tab"), &sled, comb)?;
    }
    fit("at home: striker screw and the switch", &striker, &lever_switch)?;
    fit("slide's frame between the cradle's cheeks", &frame, cradle)?;
    Ok(())
}

// --- The numbers the controller and the log reader take ----------------------------------------

fn numbers() -> serde_json::Value {
    let stations: Vec<_> = n::stations().into_iter().map(|(name, at)| json!({"station": name, "reed_centre_mm": at})).collect();
    let glass = n::reed_recess() + bridge::REED_GLASS_DIAMETER / 2. + tube::WALL;
    let sleds: Vec<_> = n::sleds()
        .into_iter()
        .map(|(name, offset)| {
            let axis = n::seat_axis(offset);
            json!({
                "sled": name,
                "float_axis_above_bore_mm": axis,
                "float_to_wall_gap_mm": axis - float::DIAMETER / 2.,
                "magnet_axis_to_glass_centre_mm": axis + glass,
            })
        })
        .collect();
    json!({
        "frame": "X is millimetres into the tube from the rim that seats on the comb's tab, which stands for the carbonator's bottom rim.",
        "stations": stations,
        "sleds": sleds,
        "machine": {
            "magnet_axis_to_glass_centre_mm": float::ROD_AXIS_FROM_INNER_WALL + tube::WALL + bridge::REED_GLASS_DIAMETER / 2.,
            "float_guide_radial_clearance_mm": float::GUIDE_RADIAL_CLEARANCE,
        },
        "reed_below_wall_mm": n::reed_recess(),
        "magnet_from_sled_face_mm": n::magnet_from_sled_face(),
        "sled_face": {"at_tab_mm": n::SLED_AT_TAB, "home_mm": n::HOME_BEFORE_TAB, "deepest_mm": n::sled_deepest()},
        "magnet": {
            "at_tab_mm": n::SLED_AT_TAB + n::magnet_from_sled_face(),
            "deepest_mm": n::sled_deepest() + n::magnet_from_sled_face(),
        },
        "slide": {"travel_mm": slide::TRAVEL, "screw_lead_mm": slide::SCREW_LEAD, "motor_steps_per_turn": slide::MOTOR_STEPS},
        "carriage_spare_travel_mm": {
            "behind_home": slide::TRAVEL - carriage_ahead_at(n::HOME_BEFORE_TAB),
            "ahead_at_deepest": carriage_ahead_at(n::sled_deepest()),
        },
    })
}

/// How far the carriage still has to run toward the tube when the sled's near face is at `sled`.
fn carriage_ahead_at(sled: f64) -> f64 {
    let carriage = sled + n::roller_from_sled_face() - n::ROD_REACH;
    -n::NOSE - slide::END_PLATE - slide::CARRIAGE_LENGTH / 2. - carriage
}
