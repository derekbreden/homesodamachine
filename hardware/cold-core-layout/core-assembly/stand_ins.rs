//! The solids the core places that no printed file holds: the carbonator, its fittings and its
//! earth bond, the clamp screws, the reservoirs' grips, air tubes and rods, the floats, the reeds
//! and the probes. A bought part is drawn as its catalog envelope: what it owes the core is where
//! its mouths are and how much room it takes.
use anyhow::Result;
use hsm_carbonator_numbers::{self as carbonator, Plate, Port, bond, collet, male_elbow, prv, street_elbow};
use hsm_cold_core_assembly_numbers::{self as numbers, Clamp, clamp, to92};
use hsm_kernel::math::{acos, cos, degrees, radians, sin};
use hsm_kernel::*;
use hsm_reservoir_numbers as reservoir;

fn v(p: [f64; 3]) -> V3 {
    v3(p[0], p[1], p[2])
}

/// A solid built on +Z, stood on `axis` by the least rotation, a half turn about X onto −Z.
pub fn orient(solid: &Solid, axis: V3) -> Solid {
    let axis = axis.unit();
    let z = v3(0., 0., 1.);
    let dot = z.dot(axis).clamp(-1., 1.);
    if dot > 1. - 1e-12 {
        solid.clone()
    } else if dot < -1. + 1e-12 {
        solid.rotate(V3::ZERO, v3(1., 0., 0.), 180.)
    } else {
        solid.rotate(V3::ZERO, z.cross(axis), degrees(acos(dot)))
    }
}

pub fn cylinder(radius: f64, height: f64, at: V3, axis: V3) -> Result<Solid> {
    Ok(orient(&Plane::XY.cylinder(radius, height)?, axis).translate(at))
}

/// A solid built on +X, stood so its +X runs along `axis` with its origin at `at`.
fn stand_x_along(solid: &Solid, at: V3, axis: V3) -> Solid {
    let axis = axis.unit();
    let x = v3(1., 0., 0.);
    let dot = x.dot(axis).clamp(-1., 1.);
    let turned = if dot > 1. - 1e-12 {
        solid.clone()
    } else if dot < -1. + 1e-12 {
        solid.rotate(V3::ZERO, v3(0., 0., 1.), 180.)
    } else {
        solid.rotate(V3::ZERO, x.cross(axis), degrees(acos(dot)))
    };
    turned.translate(at)
}

fn hex_points(radius: f64) -> Vec<V2> {
    (0..6)
        .map(|i| {
            let angle = radians(60. * i as f64);
            v2(radius * cos(angle), radius * sin(angle))
        })
        .collect()
}

fn hex(across_flats: f64, height: f64) -> Result<Solid> {
    hex_radius(across_flats / 3_f64.sqrt(), height)
}

fn hex_radius(radius: f64, height: f64) -> Result<Solid> {
    Plane::XY.extrude(&Profile::polygon(&hex_points(radius)), height)
}

// --- The casing's clamp screws ------------------------------------------------------------------

/// A clamp screw: its shank down or up from its head's seat, its head the other way, and the hex
/// socket in the head's face.
pub fn clamp_screw(c: &Clamp) -> Result<Solid> {
    let at = v3(c.xy[0], c.xy[1], c.seat);
    let shaft = cylinder(clamp::SHANK_RADIUS, clamp::LENGTH, at, V3::Z * c.direction)?;
    let head = cylinder(clamp::HEAD_RADIUS, clamp::HEAD_HEIGHT, at, V3::Z * -c.direction)?;
    let (h0, h1) = if c.direction < 0. {
        (c.seat, c.seat + clamp::HEAD_HEIGHT)
    } else {
        (c.seat - clamp::HEAD_HEIGHT, c.seat)
    };
    let (s0, s1) = if c.direction < 0. {
        (h1 - clamp::SOCKET_DEPTH, h1 + clamp::SOCKET_OVERRUN)
    } else {
        (h0 - clamp::SOCKET_OVERRUN, h0 + clamp::SOCKET_DEPTH)
    };
    let radius = clamp::SOCKET_AF / cos(std::f64::consts::PI / 6.) / 2.;
    let socket = Plane::XY.at(v3(at.x, at.y, s0)).extrude(&Profile::polygon(&hex_points(radius)), s1 - s0)?;
    shaft.union(&head)?.cut(&socket)
}

// --- The carbonator -----------------------------------------------------------------------------

/// The tube, its bore through, and the earth bond's tapped hole through its upper rim.
pub fn tube() -> Result<Solid> {
    let z = carbonator::BOTTOM_Z;
    let outer = cylinder(hsm_carbonator_tube_numbers::OD / 2., carbonator::HEIGHT, V3::Z * z, V3::Z)?;
    let bore =
        cylinder(hsm_carbonator_tube_numbers::ID / 2., carbonator::HEIGHT + 2., V3::Z * (z - 1.), V3::Z)?;
    let datums = carbonator::bond();
    let outward = v(datums.contact_outward);
    let tap = cylinder(
        bond::THREAD_DIAMETER / 2.,
        bond::TUBE_WALL + 2.,
        v(datums.contact_point) + outward,
        -outward,
    )?;
    outer.cut(&bore)?.cut(&tap)
}

/// One plate: its ports tapped through, and its rod register drilled blind from its inside face.
pub fn plate(side: Plate) -> Result<Solid> {
    let [z0, z1] = match side {
        Plate::Bottom => carbonator::BOTTOM_PLATE_Z,
        Plate::Top => carbonator::TOP_PLATE_Z,
    };
    let height = carbonator::PLATE_THICKNESS;
    let mut plate = cylinder(carbonator::PLATE_DIAMETER / 2., height, V3::Z * z0, V3::Z)?;
    for &(_, on, y) in &carbonator::PORTS {
        if on == side {
            plate = plate.cut(&cylinder(
                carbonator::PORT_TAP_DIAMETER / 2.,
                height + 2.,
                v3(0., y, z0 - 1.),
                V3::Z,
            )?)?;
        }
    }
    let (inside, direction) = match side {
        Plate::Bottom => (z1, -V3::Z),
        Plate::Top => (z0, V3::Z),
    };
    let [x, y] = carbonator::rod_xy();
    plate.cut(&cylinder(
        carbonator::REGISTER_DIAMETER / 2.,
        carbonator::REGISTER_DEPTH,
        v3(x, y, inside),
        direction,
    )?)
}

/// The float rod, register to register.
pub fn carbonator_rod() -> Result<Solid> {
    let [x, y] = carbonator::rod_xy();
    let [z0, z1] = carbonator::ROD_Z;
    cylinder(carbonator::ROD_DIAMETER / 2., z1 - z0, v3(x, y, z0), V3::Z)
}

/// The float's upper stop, on the top plate's inside face round the rod.
pub fn upper_stop() -> Result<Solid> {
    let [x, y] = carbonator::rod_xy();
    let ceiling = carbonator::INTERIOR_Z[1];
    let (z0, z1) = (ceiling - carbonator::UPPER_STOP_HEIGHT, ceiling);
    let at = v3(x, y, z0);
    let outer = cylinder(carbonator::UPPER_STOP_DIAMETER / 2., z1 - z0, at, V3::Z)?;
    outer.cut(&cylinder(carbonator::UPPER_STOP_BORE / 2., z1 - z0 + 2., at - V3::Z, V3::Z)?)
}

/// The earth bond's screw, its head outside the rim on the lockwasher.
pub fn earth_screw() -> Result<Solid> {
    let datums = carbonator::bond();
    let head = Plane::XY
        .cylinder(bond::SCREW_HEAD_DIAMETER / 2., bond::SCREW_HEAD_HEIGHT)?
        .translate(-V3::Z * bond::SCREW_HEAD_HEIGHT);
    let shaft = Plane::XY.cylinder(bond::SCREW_DIAMETER / 2., bond::SCREW_LENGTH)?;
    Ok(orient(&head.union(&shaft)?, v(datums.screw_axis)).translate(v(datums.screw_underhead)))
}

/// The earth bond's lockwasher, under the screw's head.
pub fn earth_lockwasher() -> Result<Solid> {
    let datums = carbonator::bond();
    let (at, axis) = (v(datums.screw_underhead), v(datums.screw_axis));
    let h = bond::WASHER_THICKNESS;
    cylinder(bond::WASHER_DIAMETER / 2., h, at, axis)?.cut(&cylinder(
        bond::WASHER_BORE / 2.,
        h + 2.,
        at - axis,
        axis,
    )?)
}

/// A port's elbow, built in the frame its axes cross in: +Z up the male leg, +X out the socket.
struct ElbowFrame {
    x: V3,
    y: V3,
    z: V3,
    placement: Affine,
}

impl ElbowFrame {
    fn new(port: &Port) -> Self {
        let x = v(port.out).unit();
        let z = v(port.up).unit();
        let y = z.cross(x).unit();
        Self { x, y, z, placement: Affine::from_columns(x, y, z, v(port.corner)) }
    }

    fn local(&self, vector: V3) -> V3 {
        v3(vector.dot(self.x), vector.dot(self.y), vector.dot(self.z))
    }

    /// A hex leg along `local_axis`, clocked as a hex stood on `native_axis` is.
    fn hex(&self, across_flats: f64, height: f64, native_axis: V3, local_axis: V3) -> Result<Solid> {
        let dot = V3::Z.dot(native_axis).clamp(-1., 1.);
        let native_x = if dot > 1. - 1e-12 || dot < -1. + 1e-12 {
            V3::X
        } else {
            Affine::rotation(V3::ZERO, V3::Z.cross(native_axis), degrees(acos(dot))).vector(V3::X)
        };
        Plane::new(V3::ZERO, self.local(native_x), local_axis)?
            .extrude(&Profile::polygon(&hex_points(across_flats / 3_f64.sqrt())), height)
    }
}

/// A cylinder sampled more finely round, where the street elbow's bores intersect; the analytic
/// circle is the same.
fn street_cylinder(radius: f64, height: f64, at: V3, axis: V3) -> Result<Solid> {
    let (curve_axis, x, y) = hsm_kernel::rule::axis_frame(axis);
    let n = hsm_kernel::rule::ring_count(radius) * 2;
    let points = (0..n)
        .map(|i| {
            let angle = std::f64::consts::TAU * i as f64 / n as f64;
            at + (x * cos(angle) + y * sin(angle)) * radius
        })
        .collect();
    let region = Region {
        loops: vec![hsm_kernel::profile::RLoop { pts: points, seg: vec![0; n] }],
        curves: vec![Curve::Circle { c: at, axis: curve_axis, r: radius }],
    };
    Solid::extrude(&region, axis, axis * height)
}

/// A top-plate port's street elbow: a hex leg up to the plate and one out to the socket, the male
/// stub into the plate, the bore through both legs and the tapped socket.
pub fn street_elbow(port: &Port) -> Result<Solid> {
    let frame = ElbowFrame::new(port);
    let (c, up, out) = (V3::ZERO, V3::Z, V3::X);
    let up_leg = carbonator::TOP_AXIS_OFFSET;
    let out_leg = street_elbow::LEG;
    let male_len = port.male_length();
    let leg_up = frame.hex(street_elbow::HEX_AF, up_leg, frame.z, up)?;
    let leg_out = frame.hex(street_elbow::HEX_AF, out_leg, frame.x, out)?;
    let stub = street_cylinder(street_elbow::MALE_RADIUS, male_len, c + up * up_leg, up)?;
    let solid = leg_up.union(&leg_out)?.union(&stub)?;
    let radius = street_elbow::BORE / 2.;
    let bore_up = street_cylinder(radius, up_leg + male_len + 1., c, up)?;
    let bore_out = street_cylinder(radius, out_leg + 1., c, out)?;
    let depth = street_elbow::SOCKET_DEPTH.min(out_leg);
    let socket = street_cylinder(street_elbow::SOCKET_RADIUS, depth, c + out * (out_leg - depth), out)?;
    Ok(solid.cut(&bore_up)?.cut(&bore_out)?.cut(&socket)?.transformed(&frame.placement))
}

/// A bottom-plate port's push-fit male elbow: the socket body out from the corner, the post over
/// the thread, the thread up into the plate, the tube's socket and the flow bores.
pub fn male_elbow(port: &Port) -> Result<Solid> {
    let frame = ElbowFrame::new(port);
    let (c, up, out) = (V3::ZERO, V3::Z, V3::X);
    let radius = male_elbow::BODY_DIAMETER / 2.;
    let reach = male_elbow::MOUTH_REACH;
    let axis_reach = male_elbow::AXIS_REACH;
    let thread_length = male_elbow::THREAD;
    let socket_body = cylinder(radius, reach, c, out)?;
    let post = cylinder(male_elbow::POST_WIDTH / 2., radius + axis_reach, c - up * radius, up)?;
    let thread = cylinder(street_elbow::MALE_RADIUS, thread_length, c + up * axis_reach, up)?;
    let solid = socket_body.union(&post)?.union(&thread)?;
    let insertion = male_elbow::INSERTION;
    let socket = cylinder(male_elbow::TUBE_OD / 2., insertion, c + out * (reach - insertion), out)?;
    let bore_radius = male_elbow::FLOW_BORE / 2.;
    let bore_out = cylinder(bore_radius, reach, c, out)?;
    let bore_up = cylinder(bore_radius, axis_reach + thread_length + 1., c, up)?;
    Ok(solid.cut(&socket)?.cut(&bore_out)?.cut(&bore_up)?.transformed(&frame.placement))
}

/// The PRV, made up on its socket's mouth: the stub back into the socket, the hex and the cap out.
pub fn sv125(port: &Port) -> Result<Solid> {
    let (at, axis) = (v(port.mouth), v(port.axis).unit());
    let length = prv::MALE_LENGTH;
    let stub = cylinder(street_elbow::MALE_RADIUS, length, at - axis * length, axis)?;
    let base = orient(&hex(prv::HEX_AF, prv::HEX_HEIGHT)?, axis).translate(at);
    let cap = cylinder(prv::CAP_RADIUS, prv::CAP_HEIGHT, at + axis * prv::HEX_HEIGHT, axis)?;
    stub.union(&base)?.union(&cap)
}

/// The water inlet's jet cap, on its elbow's male tip, pointing into the carbonator.
pub fn jet() -> Result<Solid> {
    let port = carbonator::port("water-in");
    let (at, axis) = (v(port.male_tip()), v(port.up));
    let height = carbonator::jet::CAP_THICKNESS;
    cylinder(carbonator::jet::CAP_DIAMETER / 2., height, at, axis)?.cut(&cylinder(
        carbonator::jet::PASSAGE_DIAMETER / 2.,
        height,
        at,
        axis,
    )?)
}

/// The push-fit adapter made up on `port`'s socket: its collet standing outside the socket.
pub fn collet(port: &Port) -> Result<Solid> {
    let axis = v(port.axis);
    let origin = v(port.mouth) + axis * collet::STANDOFF;
    let collet_body = Plane::XY.cylinder(collet::COLLET_DIAMETER / 2., collet::COLLET_LENGTH)?;
    let wrench = hex_radius(collet::HEX_ACROSS_CORNERS / 2., collet::HEX_LENGTH)?.translate(v3(
        0.,
        0.,
        collet::COLLET_LENGTH,
    ));
    let shank = Plane::XY.cylinder(collet::SHANK_DIAMETER / 2., collet::SHANK_LENGTH)?.translate(v3(
        0.,
        0.,
        collet::COLLET_LENGTH + collet::HEX_LENGTH,
    ));
    let body = collet_body.union(&wrench)?.union(&shank)?.rotate(V3::ZERO, v3(0., 1., 0.), 90.);
    Ok(stand_x_along(&body, origin, axis * -1.))
}

// --- Level sensing ------------------------------------------------------------------------------

/// An Aero float on its rod, centred at `at`: the guided body with its magnet's pocket, and the
/// magnet in it.
pub fn float_capsule(at: [f64; 3]) -> Result<[Solid; 2]> {
    use hsm_aero_float_numbers as float;
    let (at, axis) = (v(at), V3::Z);
    let height = float::height();
    let base = at - axis * (height / 2.);
    let outer = cylinder(float::DIAMETER / 2., height, base, axis)?;
    let bore = cylinder(float::BORE_DIAMETER / 2., height + 2., base - axis, axis)?;
    let seat = at + axis * (float::magnet_seat() - height / 2.);
    let annulus = |outside: f64, inside: f64, h: f64| -> Result<Solid> {
        let ring = Plane::XY.cylinder(outside / 2., h)?.cut(&Plane::XY.cylinder(inside / 2., h)?)?;
        Ok(orient(&ring, axis).translate(seat))
    };
    let pocket = annulus(float::POCKET_OD, float::POCKET_ID, float::POCKET_DEPTH)?;
    let magnet = annulus(float::MAGNET_OD, float::MAGNET_ID, float::MAGNET_THICKNESS)?;
    Ok([outer.cut(&bore)?.cut(&pocket)?, magnet])
}

/// A reed's glass, upright, centred at `at`.
pub fn reed(at: [f64; 3]) -> Result<Solid> {
    let (at, axis) = (v(at), V3::Z);
    cylinder(numbers::REED_RADIUS, numbers::REED_LENGTH, at - axis * (numbers::REED_LENGTH / 2.), axis)
}

/// A reservoir's level rod, up from its foot.
pub fn reservoir_rod(foot: [f64; 3]) -> Result<Solid> {
    cylinder(carbonator::ROD_DIAMETER / 2., reservoir::rod_length(), v(foot), V3::Z)
}

/// A TO-92 probe, upright, centred at `at`.
pub fn to92_probe(at: [f64; 3]) -> Result<Solid> {
    let (at, axis) = (v(at), V3::Z);
    let outline =
        Profile::new(Loop::rounded_rect(v2(0., 0.), to92::WIDTH, to92::WIDTH, to92::CORNER_RADIUS)?);
    let body = Plane::XY.extrude(&outline, to92::HEIGHT)?;
    Ok(orient(&body, axis).translate(at - axis * (to92::HEIGHT / 2.)))
}

// --- The reservoirs' ports ----------------------------------------------------------------------

/// A flush TPU grip in a reservoir cap's plate at `xy`, the plate's underside at `z0`: its waist,
/// a flare into each face's countersink, and the tube's bore with a lead-in at each end.
pub fn grip(grip: &reservoir::Grip, xy: [f64; 2], z0: f64) -> Result<Solid> {
    let z1 = z0 + reservoir::PLATE_THICKNESS;
    let at = v3(xy[0], xy[1], z0);
    let waist = grip.waist_d / 2.;
    let flare = grip.flare_d / 2.;
    let depth = flare - waist;
    let spool = cylinder(waist, z1 - z0, at, V3::Z)?
        .union(&Solid::cone(at, V3::Z, flare, waist, depth)?)?
        .union(&Solid::cone(at + V3::Z * (z1 - depth - z0), V3::Z, waist, flare, depth)?)?;
    let radius = grip.bore_d / 2.;
    let lead = grip.lead_d / 2.;
    let h = grip.lead_h;
    let opening = cylinder(radius, z1 - z0 + 0.2, at - V3::Z * 0.1, V3::Z)?
        .union(&Solid::cone(at, V3::Z, lead, radius, h)?)?
        .union(&Solid::cone(at + V3::Z * (z1 - h - z0), V3::Z, radius, lead, h)?)?;
    spool.cut(&opening)
}

/// A reservoir's air tube at `xy`, from `z0` up to `z1`.
pub fn air_tube(xy: [f64; 2], [z0, z1]: [f64; 2]) -> Result<Solid> {
    let at = v3(xy[0], xy[1], z0);
    let height = z1 - at.z;
    cylinder(reservoir::AIR_TUBE_OD / 2., height, at, V3::Z)?.cut(&cylinder(
        reservoir::AIR_TUBE_ID / 2.,
        height + 0.2,
        at - V3::Z * 0.1,
        V3::Z,
    )?)
}
