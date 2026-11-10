//! The cap-weld tube rotator's numbers, in millimetres and degrees. The PET-GF fixture stands the
//! carbonator's stainless tube upright in a nest on a ball-race turntable and turns it under the
//! hand-held laser-weld head. A stepper on a sliding carriage drives the turntable's printed
//! pulley through a bought HTD-5M belt, and a copper shoe on a printed leaf spring carries the
//! welder's continuity path to the tube.
//!
//! World frame: Z is the rotary axis, up through the tube; X points from the tube's axis toward
//! the motor; Z = 0 is the base's bottom face. The feet, the nest and the clamp pads are cut in
//! frames of their own and placed in this one.
use hsm_catalog::fits;

const INCH: f64 = 25.4;

/// The closure bench sheet's recipe settings; the operator controls the lap and overlap.
pub mod recipe {
    /// The endcap's outer face below the tube rim.
    pub const ENDCAP_RECESS: f64 = 0.25 * super::INCH;
    /// The starting bead travel, in millimetres per second.
    pub const TRAVEL_NOMINAL: f64 = 8.;
    /// The bead's travel beyond its starting tack, in degrees.
    pub const OVERLAP_DEGREES: f64 = 20.;
}

/// The clear passage down through the nest, the turntable, the spool and the base, for the purge
/// hose to the welded end's lower port.
pub const SERVICE_BORE_D: f64 = 90.;

/// The stainless tube the rotator turns, as bought.
pub mod tube {
    use super::INCH;

    /// The tube's outside.
    pub const OD: f64 = 5. * INCH;
    /// The tube's wall.
    pub const WALL: f64 = 0.065 * INCH;
    /// The tube's bore.
    pub const ID: f64 = OD - 2. * WALL;
    /// The tube's length.
    pub const LENGTH: f64 = 6. * INCH;
}

/// The bought HTD-5M belt, and the two pulleys it runs on: the turntable's printed one and the
/// bought one on the motor's shaft.
pub mod belt {
    use std::f64::consts::PI;

    /// The tooth pitch along the pitch line.
    pub const PITCH: f64 = 5.;
    /// The closed belt's length along its pitch line.
    pub const PITCH_LENGTH: f64 = 550.;
    /// The belt's width.
    pub const WIDTH: f64 = 15.;
    /// How far the pitch line runs outside a pulley's tip circle.
    pub const PITCH_LINE_OFFSET: f64 = 0.5715;
    /// How far each tooth stands in from the land that rides the tip circle.
    pub const TOOTH_HEIGHT: f64 = 2.06;
    /// The belt's thickness, from its teeth's tips to its back.
    pub const THICKNESS: f64 = 3.81;
    /// The teeth of the turntable's printed pulley.
    pub const TABLE_TEETH: u32 = 90;
    /// The teeth of the bought pulley on the motor's shaft.
    pub const MOTOR_TEETH: u32 = 20;
    /// The teeth's tips, in from the pitch line.
    pub const INNER: f64 = TOOTH_HEIGHT + PITCH_LINE_OFFSET;
    /// The belt's back, out from the pitch line.
    pub const OUTER: f64 = THICKNESS - TOOTH_HEIGHT - PITCH_LINE_OFFSET;

    /// A pulley's pitch diameter, from its teeth.
    pub const fn pitch_diameter(teeth: u32) -> f64 {
        teeth as f64 * PITCH / PI
    }

    /// The turntable pulley's pitch radius.
    pub const TABLE_PITCH_R: f64 = pitch_diameter(TABLE_TEETH) / 2.;
    /// The motor pulley's pitch radius.
    pub const MOTOR_PITCH_R: f64 = pitch_diameter(MOTOR_TEETH) / 2.;

    /// The shafts' centre distance the belt's length sets: the larger root of the open-belt
    /// length equation.
    pub fn center_distance() -> f64 {
        let (large, small) = (pitch_diameter(TABLE_TEETH), pitch_diameter(MOTOR_TEETH));
        let b = PI * (large + small) / 2. - PITCH_LENGTH;
        let d = large - small;
        let c = d * d / 4.;
        (-b + (b * b - 8. * c).sqrt()) / 4.
    }

    /// The angle, in radians from the line of centres, of the radius to each span's tangent
    /// point for shafts `center` apart. One angle serves both pulleys of an open drive.
    pub fn tangent_angle(center: f64) -> f64 {
        ((TABLE_PITCH_R - MOTOR_PITCH_R) / center).acos()
    }
}

/// The bought motor pulley: a uxcell pulley for the belt, flanged at both ends, bored for the
/// motor's shaft.
pub mod motor_pulley {
    /// Its overall length.
    pub const LENGTH: f64 = 20.;
    /// Each flange's diameter.
    pub const FLANGE_DIAMETER: f64 = 35.;
    /// Each flange's length along the shaft.
    pub const FLANGE_LENGTH: f64 = 2.;
}

/// The bought stepper, a STEPPERONLINE 23HS30-2804S, hung face-down on the carriage.
pub mod motor {
    /// The square frame's side.
    pub const FRAME: f64 = 57.3;
    /// The body's length behind the face.
    pub const BODY_LENGTH: f64 = 76.5;
    /// The shaft's diameter.
    pub const SHAFT_DIAMETER: f64 = 6.35;
    /// The shaft's length past the face.
    pub const SHAFT_LENGTH: f64 = 21.;
    /// The pilot boss on the face.
    pub const PILOT_DIAMETER: f64 = 38.1;
    /// How far the pilot stands proud of the face.
    pub const PILOT_LENGTH: f64 = 1.6;
    /// The side of the square the flange holes lie on.
    pub const MOUNT_SQUARE: f64 = 47.14;
}

/// The M3 screws' bores.
pub mod m3 {
    /// The clearance a screw passes through to a head seated in a recess.
    pub const SHANK_D: f64 = 3.5;
    /// The bore an adjusting screw runs in.
    pub const ADJUSTER_SHANK_D: f64 = 3.4;
    /// A head's recess.
    pub const HEAD_D: f64 = 6.2;
    /// A head's recess depth.
    pub const HEAD_DEPTH: f64 = 3.2;
    /// The bore a heat-set insert is pressed into; every M3 station takes the same insert.
    pub const INSERT_D: f64 = 4.;
}

/// The M5 screws: the towers' screws down into the base's heat-set inserts, and the motor's
/// flange screws.
pub mod m5 {
    /// The printed passage an M5 thread passes: the shared fit.
    pub fn shank_d() -> f64 {
        super::fits().m5_thread_pass_dia
    }

    /// A tower screw's head seat.
    pub const HEAD_D: f64 = 9.;
    /// How far a tower screw's head seat sits below the top of the foot it is sunk into.
    pub const HEAD_DEPTH: f64 = 4.5;
    /// The base's insert bore.
    pub const INSERT_D: f64 = 7.;
    /// The base's insert depth below its top face.
    pub const INSERT_DEPTH: f64 = 9.7;
}

/// The stationary base: one bed-sized print carrying the lower race, the bench-clamp holes and
/// the towers' inserts, so the race and the motor's stations read one bed plane.
pub mod base {
    /// Its length along X.
    pub const X: f64 = 300.;
    /// Its width along Y.
    pub const Y: f64 = 250.;
    /// Its thickness, which is its top face's height.
    pub const Z: f64 = 12.;
    /// Its centre along X: off the tube's axis toward the motor, so the motor's tower stands on it.
    pub const CENTER_X: f64 = 30.;
    /// The round on its vertical corners.
    pub const CORNER_R: f64 = 12.;
    /// Its −X edge.
    pub const X_MIN: f64 = CENTER_X - X / 2.;
    /// Its +X edge, beyond the motor.
    pub const X_MAX: f64 = CENTER_X + X / 2.;
    /// Its edge along −Y.
    pub const Y_MIN: f64 = -Y / 2.;
    /// Its edge along +Y.
    pub const Y_MAX: f64 = Y / 2.;
    /// The bench-clamp holes through its corners.
    pub const BENCH_HOLE_D: f64 = 10.;
    /// How far each bench-clamp hole stands in from both edges at its corner.
    pub const BENCH_HOLE_MARGIN: f64 = 18.;

    /// The bench-clamp holes' centres.
    pub const fn bench_holes() -> [[f64; 2]; 4] {
        let (x0, x1) = (X_MIN + BENCH_HOLE_MARGIN, X_MAX - BENCH_HOLE_MARGIN);
        let (y0, y1) = (Y_MIN + BENCH_HOLE_MARGIN, Y_MAX - BENCH_HOLE_MARGIN);
        [[x0, y0], [x0, y1], [x1, y0], [x1, y1]]
    }
}

/// The four riser feet under the base, each held by two screws down through the base into its
/// inserts. Their frame: standing on Z = 0, centred on their own vertical axis.
pub mod foot {
    /// A foot's length along X.
    pub const X: f64 = 44.;
    /// A foot's width along Y.
    pub const Y: f64 = 32.;
    /// The feet's height: the clear room below the base the lower ports are reached through.
    pub const H: f64 = 24.;
    /// The round on a foot's vertical corners.
    pub const CORNER_R: f64 = 4.;
    /// Where the feet stand under the base.
    pub const CENTERS: [[f64; 2]; 4] = [[-75., -100.], [-75., 100.], [135., -100.], [135., 100.]];
    /// Each foot's two screws, this far either side of its centre along X.
    pub const SCREW_X: f64 = 10.;
    /// The depth of the insert at the top of each foot's screw holes.
    pub const INSERT_DEPTH: f64 = 5.2;
}

/// The ball race between the base and the turntable: stock polypropylene balls spaced by a
/// printed cage, running in a groove in the base's top face and one in the race ring, both
/// printed as top faces.
pub mod bearing {
    use super::{base, race_ring};

    /// The balls' diameter.
    pub const BALL_D: f64 = 10.;
    /// How many balls the cage spaces.
    pub const BALL_COUNT: usize = 36;
    /// The balls' circle.
    pub const RACE_R: f64 = 82.5;
    /// The balls' centres, above the base's top face.
    pub const BALL_Z: f64 = base::Z + 3.;
    /// What each groove's section radius adds to the ball's.
    pub const CLEARANCE: f64 = 0.15;
    /// Each groove's section radius.
    pub const GROOVE_R: f64 = BALL_D / 2. + CLEARANCE;
    /// The cage's thickness.
    pub const CAGE_H: f64 = 2.;
    /// The cage's bore, inside the balls' circle.
    pub const CAGE_INNER_R: f64 = RACE_R - 7.5;
    /// The cage's outside, beyond the balls' circle.
    pub const CAGE_OUTER_R: f64 = RACE_R + 7.5;
    /// Each ball's pocket in the cage.
    pub const CAGE_POCKET_D: f64 = BALL_D + 0.55;
    /// The cage's foot: the cage centred between the base's race face and the ring's.
    pub const CAGE_Z: f64 = (base::Z + race_ring::Z0) / 2. - CAGE_H / 2.;
}

/// The upper race ring: printed groove-up, then screwed groove-down to the platter's flat
/// underside with flush screws up into the platter's inserts.
pub mod race_ring {
    use super::base;

    /// Its groove face, above the base's.
    pub const Z0: f64 = base::Z + 5.;
    /// Its thickness.
    pub const H: f64 = 6.;
    /// Its top face, on the platter's underside.
    pub const Z1: f64 = Z0 + H;
    /// Its bore.
    pub const INNER_R: f64 = 68.;
    /// Its outside.
    pub const OUTER_R: f64 = 92.;
    /// Its screws' circle.
    pub const SCREW_R: f64 = 72.5;
    /// Its screws' angles about the axis.
    pub const SCREW_ANGLES: [f64; 3] = [30., 150., 270.];
    /// The depth of the platter's inserts its screws take.
    pub const INSERT_DEPTH: f64 = 6.;
}

/// The turntable: the platter, the pedestal that carries the nest above the belt, the printed
/// pulley and the register ring the nest centres on, in one piece.
pub mod turntable {
    use super::{pulley, race_ring};

    /// The platter's radius.
    pub const PLATTER_R: f64 = 94.;
    /// The platter's flat underside, the face the race ring and the spool screw up into.
    pub const PLATTER_Z0: f64 = race_ring::Z1;
    /// The platter's top face, the pulley's foot.
    pub const PLATTER_Z1: f64 = 32.;
    /// The pedestal's radius: just past the pulley's bore, so the two join.
    pub const PEDESTAL_R: f64 = pulley::INNER_R + 1.5;
}

/// The turntable's printed pulley: the belt's grooves cut on its exact pitch as clearance
/// trapezoids, between two flanges.
pub mod pulley {
    use super::{belt, turntable};

    /// The tip circle: the pitch line's offset inside the pitch circle.
    pub const TIP_R: f64 = belt::TABLE_PITCH_R - belt::PITCH_LINE_OFFSET;
    /// How deep each groove runs in from the tip circle.
    pub const GROOVE_DEPTH: f64 = 2.15;
    /// The grooves' root circle.
    pub const ROOT_R: f64 = TIP_R - GROOVE_DEPTH;
    /// The ring's bore.
    pub const INNER_R: f64 = 64.5;
    /// The ring's foot, on the platter's top face.
    pub const Z0: f64 = turntable::PLATTER_Z1;
    /// The flanges' thickness, below and above the tooth zone.
    pub const FLANGE_H: f64 = 1.;
    /// The tooth zone's foot, on the lower flange.
    pub const TOOTH_Z0: f64 = Z0 + FLANGE_H;
    /// The tooth zone's height: the belt's width and room either side.
    pub const TOOTH_H: f64 = 17.;
    /// The ring's top, over the upper flange.
    pub const Z1: f64 = TOOTH_Z0 + TOOTH_H + FLANGE_H;
    /// The flanges' radius, past the tip circle to keep the belt on.
    pub const FLANGE_R: f64 = TIP_R + 3.;
    /// A groove's half-width at the tip circle: room for the belt's tooth and the pitch error a
    /// printed pulley gathers over its engaged teeth.
    pub const GROOVE_TIP_HALF_W: f64 = 1.8;
    /// A groove's half-width at the root circle.
    pub const GROOVE_ROOT_HALF_W: f64 = 1.3;
    /// How far each groove's cutter runs out past the tip circle.
    pub const GROOVE_OVERCUT: f64 = 1.;
    /// How far each groove's cutter runs in past the root circle.
    pub const GROOVE_UNDERCUT: f64 = 0.15;
    /// A groove's half-width at `radius`: its flank line, carried straight past the tip and the
    /// root so the overcut does not pinch the opening.
    pub fn groove_half_width(radius: f64) -> f64 {
        GROOVE_ROOT_HALF_W + (GROOVE_TIP_HALF_W - GROOVE_ROOT_HALF_W) * (radius - ROOT_R) / GROOVE_DEPTH
    }
}

/// The spool: the hub and the lift-catch flange in one piece, put up through the base and screwed
/// into the platter. The flange rides in the base's pocket, clear of the shoulder above it, so it
/// catches lift without carrying running load.
pub mod spool {
    /// The hub's outside.
    pub const HUB_OD: f64 = 112.;
    /// The base's bore the hub passes.
    pub const CLEARANCE_D: f64 = 114.;
    /// The flange's outside.
    pub const FLANGE_OD: f64 = 124.;
    /// The pocket in the base's underside the flange rides in.
    pub const POCKET_D: f64 = 126.;
    /// The pocket's depth.
    pub const POCKET_H: f64 = 6.;
    /// The flange's underside.
    pub const FLANGE_Z0: f64 = 1.;
    /// The flange's thickness.
    pub const FLANGE_H: f64 = 4.;
    /// The hub's foot, on the flange.
    pub const HUB_Z0: f64 = FLANGE_Z0 + FLANGE_H;
    /// Its screws' circle.
    pub const SCREW_R: f64 = 51.;
    /// Its screws' angles about the axis.
    pub const SCREW_ANGLES: [f64; 3] = [60., 180., 300.];
    /// The depth of the platter's inserts its screws take.
    pub const INSERT_DEPTH: f64 = 6.8;
}

/// The tube nest: the replaceable register the tube's end lands in, with an ID pilot inside the
/// tube and an outer guide round it, three radial adjusters through its collar bearing on the
/// tube's outside, centred on the turntable's register ring and held by three retainers driven
/// from above. Its frame: its seat face on Z = 0.
pub mod nest {
    use super::{SERVICE_BORE_D, m3};

    /// The seat on the pedestal's top the nest lands on.
    pub const SEAT_Z: f64 = 52.;
    /// The nest's outside.
    pub const OD: f64 = 150.;
    /// The base plate's thickness, under the pilot and the collar.
    pub const BASE_H: f64 = 10.;
    /// The bore through the base plate: the service passage.
    pub const CENTER_BORE_D: f64 = SERVICE_BORE_D;
    /// The ID pilot's outside, inside the tube's bore.
    pub const PILOT_OD: f64 = 123.3;
    /// The ID pilot's bore.
    pub const PILOT_ID: f64 = 100.;
    /// The ID pilot's height: short of a welded plate's recess, so it takes a welded end too.
    pub const PILOT_H: f64 = 4.5;
    /// The outer guide's bore, round the tube's outside.
    pub const OUTER_BORE_D: f64 = 127.8;
    /// The collar round the outer guide.
    pub const OUTER_COLLAR_OD: f64 = OD;
    /// The collar's height above the base plate.
    pub const OUTER_H: f64 = 10.;
    /// The register ring on the turntable's seat the nest centres on.
    pub const REGISTER_OD: f64 = 112.;
    /// The register ring's height.
    pub const REGISTER_H: f64 = 3.;
    /// What the nest's register socket adds to the ring's diameter.
    pub const REGISTER_SLIP: f64 = 0.25;
    /// The socket's straight depth, past the ring's top.
    pub const REGISTER_SOCKET_DEPTH: f64 = REGISTER_H + 0.2;
    /// The ridge of the socket's roof above its straight depth: half the socket's width, so each
    /// roof face rises as far as it runs.
    pub const REGISTER_ROOF_H: f64 = (REGISTER_OD + REGISTER_SLIP - SERVICE_BORE_D) / 4.;
    /// The retainers' circle.
    pub const SCREW_R: f64 = 61.;
    /// The retainers' angles about the axis.
    pub const RETAINER_ANGLES: [f64; 3] = [0., 120., 240.];
    /// The straight well from above to a retainer's head, through the pilot.
    pub const RETAINER_ACCESS_D: f64 = m3::HEAD_D;
    /// The depth, below the seat, of the turntable's inserts the retainers screw into.
    pub const INSERT_DEPTH: f64 = 5.2;
    /// The tube adjusters' angles, between the retainers.
    pub const ADJUSTER_ANGLES: [f64; 3] = [60., 180., 300.];
    /// The depth of an adjuster's insert in the collar's outside face.
    pub const ADJUSTER_INSERT_DEPTH: f64 = 5.2;
    /// The adjusters' axis: its bore's crown at the pilot's top, so the tips bear on the tube
    /// over the pilot.
    pub const ADJUSTER_Z: f64 = BASE_H + PILOT_H - m3::ADJUSTER_SHANK_D / 2.;
}

/// The drive: where the bought belt puts the motor's shaft, how far the carriage slides to
/// tension it, and the belt plane the motor pulley's land sets.
pub mod drive {
    use super::{belt, motor, motor_pulley, pulley};

    /// The motor shaft's distance from the turntable's axis that the belt sets, where the belt is
    /// put on.
    pub fn center_nominal() -> f64 {
        belt::center_distance()
    }

    /// How far in from there the carriage's slots let the motor go.
    pub const TRAVEL_IN: f64 = 1.;
    /// How far out from there the carriage's slots let the motor go, to tension the belt.
    pub const TRAVEL_OUT: f64 = 7.;

    /// The motor shaft's least distance from the turntable's axis.
    pub fn center_min() -> f64 {
        center_nominal() - TRAVEL_IN
    }

    /// The motor shaft's greatest distance from the turntable's axis.
    pub fn center_max() -> f64 {
        center_nominal() + TRAVEL_OUT
    }

    /// The running gap from the motor pulley's flange up to the motor's face pilot.
    pub const PILOT_GAP: f64 = 0.25;
    /// The motor pulley's lower face: its land centred in the printed pulley's tooth zone.
    pub const MOTOR_PULLEY_Z0: f64 = pulley::TOOTH_Z0 + pulley::TOOTH_H / 2. - motor_pulley::LENGTH / 2.;
    /// The motor pulley's upper face.
    pub const MOTOR_PULLEY_Z1: f64 = MOTOR_PULLEY_Z0 + motor_pulley::LENGTH;
    /// The motor's face, hung down over its pulley past the pilot and the running gap.
    pub const FACE_Z: f64 = MOTOR_PULLEY_Z1 + motor::PILOT_LENGTH + PILOT_GAP;
    /// The foot of the motor pulley's land, between its flanges: the belt's band.
    pub const LAND_Z0: f64 = MOTOR_PULLEY_Z0 + motor_pulley::FLANGE_LENGTH;
    /// The top of the motor pulley's land.
    pub const LAND_Z1: f64 = MOTOR_PULLEY_Z1 - motor_pulley::FLANGE_LENGTH;
    /// The motor pulley's tip circle, the diameter its land is drawn at.
    pub const MOTOR_PULLEY_CORE_D: f64 = 2. * (belt::MOTOR_PITCH_R - belt::PITCH_LINE_OFFSET);
}

/// The motor tower: two rails outside the belt's spans, tied by a rear wall behind the motor
/// pulley's wrap, on the base's four M5 stations. Each rail stands on a wider foot that seats the
/// M5 heads; the carriage seats on the rails' tops.
pub mod tower {
    use super::{base, drive};

    /// The rails' end toward the turntable.
    pub const X0: f64 = 110.;
    /// The rails' far end, and the rear wall's back face.
    pub const X1: f64 = 178.;
    /// The rails' outer faces, either side of the line of centres.
    pub const Y_HALF: f64 = 45.;
    /// The feet's inner faces.
    pub const FOOT_Y0: f64 = 30.;
    /// The rails' inner faces above the feet, clear of the belt's spans.
    pub const RAIL_Y0: f64 = 33.;
    /// The tower's foot, on the base's top face.
    pub const Z0: f64 = base::Z;
    /// The feet's top.
    pub const FOOT_Z1: f64 = base::Z + 8.;
    /// The rails' top, the carriage's seat: the carriage's depth below the motor's face.
    pub const Z1: f64 = drive::FACE_Z - 8.;
    /// The rear wall's front face.
    pub const REAR_X0: f64 = 151.;
    /// The M5 stations down into the base.
    pub const MOUNT_POINTS: [[f64; 2]; 4] = [[116., -36.], [116., 36.], [164., -36.], [164., 36.]];
    /// The carriage screws' inserts in the rails' tops, along X.
    pub const RAIL_INSERT_X: [f64; 2] = [130., 150.];
    /// Those inserts, either side of the line of centres.
    pub const RAIL_INSERT_Y: f64 = 41.;
    /// Those inserts' depth.
    pub const RAIL_INSERT_DEPTH: f64 = 6.;
}

/// The motor carriage: a thin pilot skin under the motor's face, arms that follow the belt's swept
/// path with clearance, slotted screws into the rails' tops, and two side walls whose screws push
/// the clamp pads onto the motor's frame. The face pilot in the skin takes the belt's tension.
pub mod carriage {
    use super::{drive, m5, motor, tower};

    /// Its end toward the turntable.
    pub const X0: f64 = 94.;
    /// Its far end.
    pub const X1: f64 = 165.;
    /// Its sides, either side of the line of centres.
    pub const Y_HALF: f64 = tower::Y_HALF;
    /// The arms' underside, on the rails' tops.
    pub const ARM_Z0: f64 = tower::Z1;
    /// The skin's thickness under the motor's face.
    pub const SKIN_H: f64 = 2.;
    /// The skin's underside.
    pub const SKIN_Z0: f64 = drive::FACE_Z - SKIN_H;
    /// The hole that registers the motor's face pilot and passes the pulley's flanges.
    pub const PILOT_D: f64 = 38.6;
    /// The arms' clearance round the belt's swept path.
    pub const BELT_MARGIN: f64 = 2.;
    /// The side walls' inner faces.
    pub const WALL_Y0: f64 = 32.;
    /// The side walls' outer faces.
    pub const WALL_Y1: f64 = 37.5;
    /// The side walls' half-length along X: the motor's frame and room either end.
    pub const WALL_X_HALF: f64 = motor::FRAME / 2. + 0.35;
    /// The side walls' height above the motor's face.
    pub const WALL_H: f64 = 16.;
    /// The half-width of the slots its screws slide in.
    pub const SLOT_R: f64 = 1.8;
    /// The motor's two rear flange holes, either side of the line of centres; the front pair
    /// falls in the belt's swept path and stays open.
    pub const MOUNT_Y: f64 = motor::MOUNT_SQUARE / 2.;
    /// A flange screw's countersunk head.
    pub const MOUNT_HEAD_D: f64 = 9.8;
    /// What the countersink adds to the head.
    pub const MOUNT_HEAD_CLEARANCE: f64 = 0.4;
    /// The countersink's mouth in the arms' underside.
    pub const MOUNT_CSK_D: f64 = MOUNT_HEAD_D + MOUNT_HEAD_CLEARANCE;

    /// The rear flange holes along X.
    pub fn mount_x() -> f64 {
        drive::center_nominal() + motor::MOUNT_SQUARE / 2.
    }

    /// The countersink's depth: its mouth down to the shank's passage at a right-angled cone.
    pub fn mount_csk_depth() -> f64 {
        (MOUNT_CSK_D - m5::shank_d()) / 2.
    }
}

/// The motor's clamp: two printed pads either side of its frame, pushed on by screws through the
/// carriage's side walls. The pads hold the motor down and square. Their frame: centred on their
/// own axis, their foot on Z = 0, their screws' sockets on −Y.
pub mod clamp {
    use super::{drive, motor};

    /// A pad's length along X.
    pub const PAD_X: f64 = 48.;
    /// A pad's thickness, between the wall and the motor's frame.
    pub const PAD_Y: f64 = 3.;
    /// A pad's height.
    pub const PAD_Z: f64 = 12.;
    /// Each wall's two screws, this far either side of the motor's centre along X.
    pub const SCREW_X: f64 = 18.;
    /// The screws' height.
    pub const SCREW_Z: f64 = drive::FACE_Z + 8.;
    /// The inserts' depth in the walls' outer faces.
    pub const INSERT_DEPTH: f64 = 5.2;
    /// The socket in a pad that takes a screw's tip.
    pub const SOCKET_D: f64 = 2.85;
    /// The socket's depth.
    pub const SOCKET_DEPTH: f64 = 2.2;
    /// The pads' centres either side of the line of centres, against the motor's frame.
    pub const PAD_Y_CENTER: f64 = motor::FRAME / 2. + PAD_Y / 2.;
    /// The pads' foot: centred on their screws.
    pub const PAD_Z0: f64 = SCREW_Z - PAD_Z / 2.;
}

/// The continuity path: a stationary C110 shoe, cut from flat bar and stood with its mill width
/// vertical, held on the tube by a replaceable PET-GF leaf spring on a printed tower, so the
/// welder's interlock path runs neither through the bearing nor round the vessel.
pub mod ground {
    use super::base;

    /// The tower's M5 stations down into the base.
    pub const BASE_POINTS: [[f64; 2]; 2] = [[-99.5, -60.], [-99.5, -40.]];
    /// The tower's foot along X, from its outer end.
    pub const FOOT_X0: f64 = -118.;
    /// The tower's foot along X, to its end toward the tube.
    pub const FOOT_X1: f64 = -96.;
    /// The tower's foot along Y, from its −Y side.
    pub const FOOT_Y0: f64 = -68.;
    /// The tower's foot along Y, to its +Y side.
    pub const FOOT_Y1: f64 = -32.;
    /// The tower's foot's underside, on the base's top face.
    pub const FOOT_Z0: f64 = base::Z;
    /// The tower's foot's top, where the M5 heads seat.
    pub const FOOT_Z1: f64 = base::Z + 8.;
    /// The post along X, from its outer face.
    pub const POST_X0: f64 = -117.;
    /// The post along X, to its face toward the tube.
    pub const POST_X1: f64 = -103.;
    /// The post along Y, from its −Y face.
    pub const POST_Y0: f64 = -66.;
    /// The post along Y, to its +Y face.
    pub const POST_Y1: f64 = -34.;
    /// The post's top, the arm's seat.
    pub const TOP_Z: f64 = 76.;
    /// The arm's thickness.
    pub const ARM_H: f64 = 10.;
    /// The arm's two screws down into the post's inserts.
    pub const ARM_POINTS: [[f64; 2]; 2] = [[-109., -59.], [-109., -41.]];
    /// The arm's pad on the post, along X from its outer end.
    pub const PAD_X0: f64 = -117.;
    /// The pad along X, to its end toward the tube.
    pub const PAD_X1: f64 = -99.;
    /// The pad along Y, from its −Y side.
    pub const PAD_Y0: f64 = -65.;
    /// The pad along Y, to its +Y side.
    pub const PAD_Y1: f64 = -35.;
    /// The leaf spring's centre line along X.
    pub const BEAM_CENTER_X: f64 = -104.5;
    /// The leaf spring's thickness, in the plane it bends in.
    pub const BEAM_T: f64 = 5.;
    /// The leaf spring's −X face.
    pub const BEAM_X0: f64 = BEAM_CENTER_X - BEAM_T / 2.;
    /// The leaf spring's +X face.
    pub const BEAM_X1: f64 = BEAM_CENTER_X + BEAM_T / 2.;
    /// The leaf spring along Y, from the pad.
    pub const BEAM_Y0: f64 = -40.;
    /// The leaf spring along Y, to its tip past the nose.
    pub const BEAM_Y1: f64 = 5.;
    /// The nose's width along Y: the bar from the spring's tip out to the shoe's holder.
    pub const NOSE_Y: f64 = 10.;
    /// The round at the spring's roots, where it meets the pad and the nose.
    pub const SPRING_FILLET_R: f64 = 2.;
    /// The shoe's face on the tube.
    pub const SHOE_FRONT_X: f64 = -62.5;
    /// The bar's nominal thickness, the shoe's depth along X.
    pub const SHOE_T: f64 = 6.;
    /// The shoe's back face, seated on the holder's back wall.
    pub const SHOE_BACK_X: f64 = SHOE_FRONT_X - SHOE_T;
    /// The shoe's width along Y: one crosscut from the bar.
    pub const SHOE_Y: f64 = 25.;
    /// The room either side of the shoe in its holder.
    pub const SHOE_SIDE_CLEARANCE: f64 = 0.4;
    /// The shoe's height: the bar's mill width, stood vertical.
    pub const SHOE_Z: f64 = 50.;
    /// The shelf under the shoe.
    pub const HOLDER_SHELF_H: f64 = 3.;
    /// The shoe's underside, on the shelf.
    pub const SHOE_Z0: f64 = TOP_Z + HOLDER_SHELF_H;
    /// The holder's height up the shoe.
    pub const HOLDER_H: f64 = 12.;
    /// The holder's back wall.
    pub const HOLDER_BACK_T: f64 = 3.;
    /// The back wall's face the loaded tube seats the shoe's back on.
    pub const HOLDER_BACK_FACE_X: f64 = SHOE_BACK_X;
    /// The holder's jaws' ends toward the tube.
    pub const HOLDER_FRONT_X: f64 = -64.;
    /// The fixed jaw's thickness.
    pub const HOLDER_SIDE_T: f64 = 3.;
    /// The clamp jaw's thickness, which takes the clamp screw's insert.
    pub const HOLDER_CLAMP_T: f64 = 7.;
    /// The shelf's outer end, under the back wall.
    pub const HOLDER_SHELF_X0: f64 = HOLDER_BACK_FACE_X - HOLDER_BACK_T;
    /// The clamp jaw's inner face, on −Y.
    pub const HOLDER_CLAMP_INNER_Y: f64 = -(SHOE_Y / 2. + SHOE_SIDE_CLEARANCE);
    /// The clamp jaw's outer face.
    pub const HOLDER_CLAMP_OUTER_Y: f64 = HOLDER_CLAMP_INNER_Y - HOLDER_CLAMP_T;
    /// The fixed jaw's inner face, on +Y.
    pub const HOLDER_FIXED_INNER_Y: f64 = SHOE_Y / 2. + SHOE_SIDE_CLEARANCE;
    /// The fixed jaw's outer face.
    pub const HOLDER_FIXED_OUTER_Y: f64 = HOLDER_FIXED_INNER_Y + HOLDER_SIDE_T;
    /// The clamp screw's shank bore through the clamp jaw.
    pub const SHOE_CLAMP_SHANK_D: f64 = 3.4;
    /// The depth of the clamp screw's insert in the jaw's outer face.
    pub const SHOE_CLAMP_INSERT_DEPTH: f64 = 5.2;
    /// The clamp screw's axis along X: on the shoe's middle.
    pub const SHOE_CLAMP_X: f64 = SHOE_FRONT_X - SHOE_T / 2.;
    /// The clamp screw's axis height: the holder's middle.
    pub const SHOE_CLAMP_Z: f64 = SHOE_Z0 + HOLDER_H / 2.;
    /// The roof over the clamp screw's sideways bores, from the vertical, so they print without
    /// support.
    pub const TEARDROP_ROOF_ANGLE: f64 = 36.;
    /// The arm's screws' shank bore.
    pub const ARM_SHANK_D: f64 = 3.4;
    /// The depth of the post's inserts under the arm's screws.
    pub const ARM_INSERT_DEPTH: f64 = 5.2;
}
