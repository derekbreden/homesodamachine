//! The cap-weld tube rotator's files: each PET-GF piece in the frame it is cut in, the copper
//! ground shoe the page draws, and the assembly with the balls, the motor, its pulley, the belt
//! and the tube in place, drawn simplified beside its fine model.
//!
//!     weld-rotator [<output directory>]
use anyhow::{Context, Result, bail, ensure};
use hsm_catalog::{aluminium, copper, petgf_black, stainless, tpu_black};
use hsm_kernel::part::{AssemblyBody, write_assembly_with_root, write_part, write_shown};
use hsm_kernel::{Body, Curve, Edges, Loop, Pen, Plane, Profile, Solid, V2, V3, v2, v3};
use hsm_print_payload::{ANGULAR_DEFLECTION, LINEAR_DEFLECTION_RATIO};
use hsm_weld_rotator_numbers::{
    SERVICE_BORE_D, base, bearing, belt, carriage, clamp, drive, foot, ground, m3, m5, motor,
    motor_pulley, nest, pulley, race_ring, spool, tower, tube, turntable,
};
use serde_json::json;
use std::path::PathBuf;

const OUTPUT: &str = "hardware/printed-parts/fixtures/weld-rotator";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: weld-rotator [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let mut pieces = Pieces::build()?;

    let colour = Some(petgf_black());
    for (file, name, solid) in pieces.printed() {
        println!("{}", write_part(&out, file, &[Body { name, color: colour, solid }])?);
        solid.forget_backend();
    }
    let shoe = Body { name: "c110-ground-shoe", color: Some(copper()), solid: &pieces.shoe };
    println!("{}", write_shown(&out, "weld-rotator-ground-shoe", &[shoe])?);
    pieces.shoe.forget_backend();

    let mut rows = assembly(&pieces)?;
    drop(pieces);
    for row in &mut rows {
        row.solid.forget_backend();
    }
    let tolerance = presentation_tolerance(&rows);
    let mut drawn = Vec::with_capacity(rows.len());
    for row in &mut rows {
        let mut shown = row.solid.simplified_to(tolerance)?;
        row.solid.forget_backend();
        shown.forget_backend();
        drawn.push(shown);
    }
    let bodies: Vec<AssemblyBody> = rows
        .iter()
        .zip(&drawn)
        .map(|(row, shown)| AssemblyBody { name: &row.name, color: Some(row.color), fine: &row.solid, presentation: shown })
        .collect();
    let document = json!({"presentation_tolerance_mm": tolerance});
    let said = write_assembly_with_root(&out, "weld-rotator-assembly", "weld-rotator", &bodies, Some(&document))?;
    println!("{said}");
    Ok(())
}

/// The rotator's pieces, each in the frame its files carry.
struct Pieces {
    base: Solid,
    foot: Solid,
    turntable: Solid,
    race_ring: Solid,
    spool: Solid,
    cage: Solid,
    nest: Solid,
    motor_tower: Solid,
    carriage: Solid,
    clamp_pad: Solid,
    ground_tower: Solid,
    ground_arm: Solid,
    shoe: Solid,
}

impl Pieces {
    fn build() -> Result<Pieces> {
        let ring = toothed_ring()?;
        Ok(Pieces {
            base: closed("base", base_piece()?)?,
            foot: closed("base foot", foot_piece()?)?,
            turntable: closed("turntable", turntable_piece(&ring)?)?,
            race_ring: closed("race ring", race_ring_piece()?)?,
            spool: closed("spool", spool_piece()?)?,
            cage: closed("ball cage", cage_piece()?)?,
            nest: closed("tube nest", nest_piece()?)?,
            motor_tower: closed("motor tower", motor_tower_piece()?)?,
            carriage: closed("motor carriage", carriage_piece()?)?,
            clamp_pad: closed("motor clamp pad", clamp_pad_piece()?)?,
            ground_tower: closed("ground tower", ground_tower_piece()?)?,
            ground_arm: closed("ground arm", ground_arm_piece()?)?,
            shoe: closed("ground shoe", shoe_piece())?,
        })
    }

    /// The printed pieces: the file each is written to, the body its files name, and its solid.
    fn printed(&mut self) -> [(&'static str, &'static str, &mut Solid); 12] {
        [
            ("weld-rotator-ball-cage", "ball-cage", &mut self.cage),
            ("weld-rotator-base", "base", &mut self.base),
            ("weld-rotator-base-foot", "base-foot", &mut self.foot),
            ("weld-rotator-ground-arm", "ground-arm", &mut self.ground_arm),
            ("weld-rotator-ground-tower", "ground-tower", &mut self.ground_tower),
            ("weld-rotator-motor-carriage", "motor-carriage", &mut self.carriage),
            ("weld-rotator-motor-clamp-pad", "motor-clamp-pad", &mut self.clamp_pad),
            ("weld-rotator-motor-tower", "motor-tower", &mut self.motor_tower),
            ("weld-rotator-race-ring", "race-ring", &mut self.race_ring),
            ("weld-rotator-spool", "spool", &mut self.spool),
            ("weld-rotator-tube-nest", "tube-nest", &mut self.nest),
            ("weld-rotator-turntable-90t", "turntable", &mut self.turntable),
        ]
    }
}

/// `solid`, a closed surface holding volume, without the boolean form its construction kept.
fn closed(piece: &str, mut solid: Solid) -> Result<Solid> {
    solid.check().with_context(|| format!("the {piece}"))?;
    ensure!(solid.volume() > 0., "the {piece} holds no volume");
    solid.forget_backend();
    Ok(solid)
}

/// The box between two corners.
#[track_caller]
fn cuboid(x0: f64, x1: f64, y0: f64, y1: f64, z0: f64, z1: f64) -> Solid {
    Solid::cuboid(v3(x0, y0, z0), v3(x1, y1, z1))
}

/// An upright cylinder of radius `r`, standing `h` from the centre of its foot.
#[track_caller]
fn cylinder(x: f64, y: f64, z: f64, r: f64, h: f64) -> Result<Solid> {
    Solid::cylinder(v3(x, y, z), V3::Z, r, h)
}

/// A ring about the axis, standing `h` from `z`.
#[track_caller]
fn annulus(outer: f64, inner: f64, h: f64, z: f64) -> Result<Solid> {
    let section = Profile::circle(V2::ZERO, outer).with_hole(Loop::circle(V2::ZERO, inner));
    Plane::XY.at(v3(0., 0., z)).extrude(&section, h)
}

/// A polygon in plan, standing `h` from `z`.
#[track_caller]
fn prism(points: &[[f64; 2]], z: f64, h: f64) -> Result<Solid> {
    let points: Vec<V2> = points.iter().map(|&[x, y]| v2(x, y)).collect();
    Plane::XY.at(v3(0., 0., z)).extrude(&Profile::polygon(&points), h)
}

/// A box with rounded vertical corners, centred on (`x`, `y`), standing `height` from `z`.
#[track_caller]
fn rounded_box(x: f64, y: f64, length: f64, width: f64, z: f64, height: f64, r: f64) -> Result<Solid> {
    let section = Profile::new(Loop::rounded_rect(v2(x, y), length, width, r)?);
    Plane::XY.at(v3(0., 0., z)).extrude(&section, height)
}

/// The point `r` out from the axis at `degrees` about it.
fn polar(r: f64, degrees: f64) -> [f64; 2] {
    let a = degrees.to_radians();
    [r * a.cos(), r * a.sin()]
}

/// A level bore at `degrees` about the axis, from `r` out, running `depth` in toward the axis.
#[track_caller]
fn radial(degrees: f64, r: f64, z: f64, diameter: f64, depth: f64) -> Result<Solid> {
    let ([x, y], [dx, dy]) = (polar(r, degrees), polar(-1., degrees));
    Solid::cylinder(v3(x, y, z), v3(dx, dy, 0.), diameter / 2., depth)
}

/// An M3 screw's way up from its head's seat at `z`: the shank's clearance `through` long, and the
/// head's recess below the seat.
#[track_caller]
fn counterbore(x: f64, y: f64, z: f64, through: f64) -> Result<Solid> {
    Solid::union_all(&[
        cylinder(x, y, z, m3::SHANK_D / 2., through)?,
        cylinder(x, y, z - m3::HEAD_DEPTH, m3::HEAD_D / 2., m3::HEAD_DEPTH + 0.01)?,
    ])
}

/// A vertical slot `diameter` wide whose ends' centres are `x0` and `x1` along X, standing `h`
/// from `z`.
#[track_caller]
fn slot(x0: f64, x1: f64, y: f64, diameter: f64, z: f64, h: f64) -> Result<Solid> {
    let r = diameter / 2.;
    Solid::union_all(&[cuboid(x0, x1, y - r, y + r, z, z + h), cylinder(x0, y, z, r, h)?, cylinder(x1, y, z, r, h)?])
}

/// A bore along Y, from `y0` to `y1`, that prints without support in a piece printed flat: the
/// whole round bore under a roof of two planes tangent to it.
#[track_caller]
fn teardrop(radius: f64, x: f64, z: f64, y0: f64, y1: f64) -> Result<Solid> {
    let a = ground::TEARDROP_ROOF_ANGLE.to_radians();
    let (half, tangent) = (radius * a.sin(), z + radius * a.cos());
    let roof = Profile::polygon(&[v2(x - half, tangent), v2(x + half, tangent), v2(x, z + radius / a.cos())]);
    let roof = Plane::XZ.at(v3(0., y0, 0.)).extrude(&roof, -(y1 - y0))?;
    Solid::cylinder(v3(x, y0, z), V3::Y, radius, y1 - y0)?.union(&roof)
}

/// The belt round both pulleys for a motor shaft `center` from the turntable's axis: its two wraps
/// and two spans as one section from the teeth's tips to its back, grown by `margin`, standing
/// from `z0` to `z1`.
#[track_caller]
fn belt_band(center: f64, z0: f64, z1: f64, margin: f64) -> Result<Solid> {
    let a = belt::tangent_angle(center);
    // The wraps and spans meet at shared tangent points, so the band is one section and the cut
    // it makes has no seams between them.
    let ring = |offset: f64| -> Result<Loop> {
        let (rb, rs) = (belt::TABLE_PITCH_R + offset, belt::MOTOR_PITCH_R + offset);
        let upper = v2(rb * a.cos(), rb * a.sin());
        let lower = v2(upper.x, -upper.y);
        let small_upper = v2(center + rs * a.cos(), rs * a.sin());
        let small_lower = v2(small_upper.x, -small_upper.y);
        Pen::new(upper)
            .arc_center(V2::ZERO, lower, true)
            .line_to(small_lower)
            .arc_center(v2(center, 0.), small_upper, true)
            .line_to(upper)
            .close()
    };
    let section = Profile::new(ring(belt::OUTER + margin)?).with_hole(ring(-(belt::INNER + margin))?);
    Plane::XY.at(v3(0., 0., z0)).extrude(&section, z1 - z0)
}

/// The cutter both race grooves are cut by: the ball's section, grown by the clearance, turned
/// about the axis. The groove curves both ways, so each arc of the section is halved for its
/// error and the turn's to fit the rule together.
#[track_caller]
fn race_groove() -> Result<Solid> {
    let section = Profile::circle(v2(bearing::RACE_R, bearing::BALL_Z), bearing::GROOVE_R);
    let mut region = section.place(&Plane::XZ);
    for ring in &mut region.loops {
        let (mut points, mut edges) = (vec![], vec![]);
        for i in 0..ring.pts.len() {
            let (a, b, edge) = (ring.pts[i], ring.pts[(i + 1) % ring.pts.len()], ring.seg[i]);
            points.push(a);
            edges.push(edge);
            if let Curve::Circle { c, axis, .. } = region.curves[edge as usize] {
                let (u, v, n) = (a - c, b - c, axis.unit());
                let (s, co) = (u.cross(v).dot(n).atan2(u.dot(v)) / 2.).sin_cos();
                points.push(c + u * co + n.cross(u) * s + n * (n.dot(u) * (1. - co)));
                edges.push(edge);
            }
        }
        ring.pts = points;
        ring.seg = edges;
    }
    Solid::revolve(&region, V3::ZERO, V3::Z, 360.)
}

/// The stationary base: the bed with the lower race in its top face, the spool's bore and the
/// pocket its flange rides in, the bench-clamp holes, the feet's screws and the towers' inserts.
fn base_piece() -> Result<Solid> {
    let height = base::Z;
    let mut cuts = vec![
        cylinder(0., 0., 0., spool::CLEARANCE_D / 2., height)?,
        cylinder(0., 0., 0., spool::POCKET_D / 2., spool::POCKET_H)?,
        race_groove()?,
    ];
    for [x, y] in base::bench_holes() {
        cuts.push(cylinder(x, y, 0., base::BENCH_HOLE_D / 2., height)?);
    }
    for [x, y] in foot::CENTERS {
        for x in [x - foot::SCREW_X, x + foot::SCREW_X] {
            cuts.push(cylinder(x, y, 0., m3::SHANK_D / 2., height)?);
            cuts.push(cylinder(x, y, height - m3::HEAD_DEPTH, m3::HEAD_D / 2., m3::HEAD_DEPTH + 0.01)?);
        }
    }
    for [x, y] in tower::MOUNT_POINTS.into_iter().chain(ground::BASE_POINTS) {
        let depth = m5::INSERT_DEPTH;
        cuts.push(cylinder(x, y, height - depth, m5::INSERT_D / 2., depth + 0.01)?);
    }
    rounded_box(base::CENTER_X, 0., base::X, base::Y, 0., height, base::CORNER_R)?.cut_all(&cuts)
}

/// A riser foot: its two screws' clearance up through it, and their inserts at its top.
fn foot_piece() -> Result<Solid> {
    let (h, depth) = (foot::H, foot::INSERT_DEPTH);
    let mut cuts = vec![];
    for x in [-foot::SCREW_X, foot::SCREW_X] {
        cuts.push(cylinder(x, 0., 0., m3::SHANK_D / 2., h)?);
        cuts.push(cylinder(x, 0., h - depth, m3::INSERT_D / 2., depth + 0.01)?);
    }
    rounded_box(0., 0., foot::X, foot::Y, 0., h, foot::CORNER_R)?.cut_all(&cuts)
}

/// The turntable's printed pulley: the ring with a groove at every tooth, and its two flanges.
fn toothed_ring() -> Result<Solid> {
    let (outer, inner) = (pulley::TIP_R + pulley::GROOVE_OVERCUT, pulley::ROOT_R - pulley::GROOVE_UNDERCUT);
    let width = pulley::groove_half_width;
    let flank = [[outer, -width(outer)], [inner, -width(inner)], [inner, width(inner)], [outer, width(outer)]];
    let groove = prism(&flank, pulley::TOOTH_Z0, pulley::TOOTH_H)?;
    let teeth = belt::TABLE_TEETH;
    let grooves: Vec<Solid> =
        (0..teeth).map(|i| groove.rotate(V3::ZERO, V3::Z, i as f64 * 360. / teeth as f64)).collect();
    let (z0, z1) = (pulley::Z0, pulley::Z1);
    let core = annulus(pulley::TIP_R, pulley::INNER_R, z1 - z0, z0)?.cut_all(&grooves)?;
    Solid::union_all(&[
        core,
        annulus(pulley::FLANGE_R, pulley::INNER_R, pulley::FLANGE_H, z0)?,
        annulus(pulley::FLANGE_R, pulley::INNER_R, pulley::FLANGE_H, z1 - pulley::FLANGE_H)?,
    ])
}

/// The turntable: the platter, the pedestal, the pulley and the register ring the nest centres
/// on, with the inserts the nest's retainers, the spool and the race ring screw into.
fn turntable_piece(ring: &Solid) -> Result<Solid> {
    let bore = SERVICE_BORE_D / 2.;
    let (z0, z1) = (turntable::PLATTER_Z0, turntable::PLATTER_Z1);
    let solid = Solid::union_all(&[
        annulus(turntable::PLATTER_R, bore, z1 - z0, z0)?,
        annulus(turntable::PEDESTAL_R, bore, nest::SEAT_Z - z1, z1)?,
        ring.clone(),
        annulus(nest::REGISTER_OD / 2., bore, nest::REGISTER_H, nest::SEAT_Z)?,
    ])?;
    let mut cuts = vec![];
    for angle in nest::RETAINER_ANGLES {
        let [x, y] = polar(nest::SCREW_R, angle);
        let depth = nest::INSERT_DEPTH;
        cuts.push(cylinder(x, y, nest::SEAT_Z - depth, m3::INSERT_D / 2., depth + 0.01)?);
    }
    let underside = [
        (spool::SCREW_ANGLES, spool::SCREW_R, spool::INSERT_DEPTH),
        (race_ring::SCREW_ANGLES, race_ring::SCREW_R, race_ring::INSERT_DEPTH),
    ];
    for (angles, radius, depth) in underside {
        for angle in angles {
            let [x, y] = polar(radius, angle);
            cuts.push(cylinder(x, y, z0 - 0.01, m3::INSERT_D / 2., depth + 0.01)?);
        }
    }
    solid.cut_all(&cuts)
}

/// The upper race ring: the groove in its underside and its screws' counterbores from below.
fn race_ring_piece() -> Result<Solid> {
    let mut cuts = vec![race_groove()?];
    for angle in race_ring::SCREW_ANGLES {
        let [x, y] = polar(race_ring::SCREW_R, angle);
        let seat = race_ring::Z0 + m3::HEAD_DEPTH;
        cuts.push(counterbore(x, y, seat, race_ring::H - m3::HEAD_DEPTH + 0.02)?);
    }
    annulus(race_ring::OUTER_R, race_ring::INNER_R, race_ring::H, race_ring::Z0)?.cut_all(&cuts)
}

/// The spool: the flange and the hub up to the platter, with its screws' counterbores from below.
fn spool_piece() -> Result<Solid> {
    let bore = SERVICE_BORE_D / 2.;
    let solid = Solid::union_all(&[
        annulus(spool::FLANGE_OD / 2., bore, spool::FLANGE_H, spool::FLANGE_Z0)?,
        annulus(spool::HUB_OD / 2., bore, turntable::PLATTER_Z0 - spool::HUB_Z0, spool::HUB_Z0)?,
    ])?;
    let mut cuts = vec![];
    for angle in spool::SCREW_ANGLES {
        let [x, y] = polar(spool::SCREW_R, angle);
        let seat = spool::FLANGE_Z0 + m3::HEAD_DEPTH;
        let through = turntable::PLATTER_Z0 - spool::FLANGE_Z0 - m3::HEAD_DEPTH + 0.02;
        cuts.push(counterbore(x, y, seat, through)?);
    }
    solid.cut_all(&cuts)
}

/// The ball cage: a flat ring with a pocket at every ball.
fn cage_piece() -> Result<Solid> {
    let count = bearing::BALL_COUNT;
    let pockets = (0..count)
        .map(|i| {
            let [x, y] = polar(bearing::RACE_R, 360. * i as f64 / count as f64);
            cylinder(x, y, bearing::CAGE_Z, bearing::CAGE_POCKET_D / 2., bearing::CAGE_H)
        })
        .collect::<Result<Vec<_>>>()?;
    annulus(bearing::CAGE_OUTER_R, bearing::CAGE_INNER_R, bearing::CAGE_H, bearing::CAGE_Z)?.cut_all(&pockets)
}

/// The tube nest: the base plate with its register socket under a two-faced roof, the ID pilot and
/// the outer guide's collar, the adjusters' inserts and bores through the collar, and the
/// retainers' clearance and straight wells from above.
fn nest_piece() -> Result<Solid> {
    let (inner, outer) = (nest::CENTER_BORE_D / 2., (nest::REGISTER_OD + nest::REGISTER_SLIP) / 2.);
    let depth = nest::REGISTER_SOCKET_DEPTH;
    let ridge = [v2(inner, depth), v2(outer, depth), v2((inner + outer) / 2., depth + nest::REGISTER_ROOF_H)];
    let roof = Plane::XZ.revolve(&Profile::polygon(&ridge), 360., V2::ZERO, v2(0., 1.))?;
    let socket = annulus(outer, inner, depth, 0.)?;
    let plate = annulus(nest::OD / 2., inner, nest::BASE_H, 0.)?.cut_all(&[socket, roof])?;
    let solid = Solid::union_all(&[
        plate,
        annulus(nest::PILOT_OD / 2., nest::PILOT_ID / 2., nest::PILOT_H, nest::BASE_H)?,
        annulus(nest::OUTER_COLLAR_OD / 2., nest::OUTER_BORE_D / 2., nest::OUTER_H, nest::BASE_H)?,
    ])?;
    let mut cuts = vec![];
    let (collar, z, insert) = (nest::OUTER_COLLAR_OD / 2., nest::ADJUSTER_Z, nest::ADJUSTER_INSERT_DEPTH);
    for angle in nest::ADJUSTER_ANGLES {
        cuts.push(radial(angle, collar + 0.1, z, m3::INSERT_D, insert + 0.2)?);
        let start = collar - insert;
        cuts.push(radial(angle, start, z, m3::ADJUSTER_SHANK_D, start - nest::OUTER_BORE_D / 2. + 0.2)?);
    }
    for angle in nest::RETAINER_ANGLES {
        let [x, y] = polar(nest::SCREW_R, angle);
        cuts.push(cylinder(x, y, 0., m3::SHANK_D / 2., nest::BASE_H)?);
        let well = m3::HEAD_DEPTH + nest::OUTER_H + 0.01;
        cuts.push(cylinder(x, y, nest::BASE_H - m3::HEAD_DEPTH, nest::RETAINER_ACCESS_D / 2., well)?);
    }
    solid.cut_all(&cuts)
}

/// The motor tower: the rails on their feet and the rear wall, the M5 screws' passages with their
/// heads' wells from above, and the carriage screws' inserts in the rails' tops.
fn motor_tower_piece() -> Result<Solid> {
    let (x0, x1, y) = (tower::X0, tower::X1, tower::Y_HALF);
    let mut pieces = vec![];
    for ((foot0, foot1), (rail0, rail1)) in
        [((-y, -tower::FOOT_Y0), (-y, -tower::RAIL_Y0)), ((tower::FOOT_Y0, y), (tower::RAIL_Y0, y))]
    {
        pieces.push(cuboid(x0, x1, foot0, foot1, tower::Z0, tower::FOOT_Z1));
        pieces.push(cuboid(x0, x1, rail0, rail1, tower::FOOT_Z1, tower::Z1));
    }
    pieces.push(cuboid(tower::REAR_X0, x1, -y, y, tower::Z0, tower::Z1));
    let seat = tower::FOOT_Z1 - m5::HEAD_DEPTH;
    let mut cuts = vec![];
    for [x, y] in tower::MOUNT_POINTS {
        cuts.push(cylinder(x, y, tower::Z0 - 0.01, m5::shank_d() / 2., seat - tower::Z0 + 0.02)?);
        cuts.push(cylinder(x, y, seat, m5::HEAD_D / 2., tower::Z1 - seat + 0.01)?);
    }
    let depth = tower::RAIL_INSERT_DEPTH;
    for x in tower::RAIL_INSERT_X {
        for y in [-tower::RAIL_INSERT_Y, tower::RAIL_INSERT_Y] {
            cuts.push(cylinder(x, y, tower::Z1 - depth, m3::INSERT_D / 2., depth + 0.01)?);
        }
    }
    Solid::union_all(&pieces)?.cut_all(&cuts)
}

/// The motor carriage: the arms cut clear of the belt's path at every point of the tension travel,
/// the skin with its pilot hole, the side walls with the clamp screws' inserts, the motor's
/// flange screws countersunk from below, and the slots its screws slide in.
fn carriage_piece() -> Result<Solid> {
    let center = drive::center_nominal();
    let (arm, skin, face) = (carriage::ARM_Z0, carriage::SKIN_Z0, drive::FACE_Z);
    let (x0, x1, half) = (carriage::X0, carriage::X1, carriage::Y_HALF);
    let mut cuts = vec![];
    for at in [drive::center_min(), center, drive::center_max()] {
        let band = belt_band(at, drive::LAND_Z0 - 1., drive::LAND_Z1 + 1., carriage::BELT_MARGIN)?;
        cuts.push(band.translate(v3(center - at, 0., 0.)));
    }
    cuts.push(cylinder(center, 0., arm - 0.01, carriage::PILOT_D / 2., skin - arm + 0.02)?);
    let arms = cuboid(x0, x1, -half, half, arm, skin).cut_all(&cuts)?;
    let pilot = cylinder(center, 0., skin - 0.01, carriage::PILOT_D / 2., carriage::SKIN_H + 0.02)?;
    let mut pieces = vec![arms, cuboid(x0, x1, -half, half, skin, face).cut(&pilot)?];
    let mut cuts = vec![];
    for sign in [-1., 1.] {
        let (y0, y1) = if sign < 0. {
            (-carriage::WALL_Y1, -carriage::WALL_Y0)
        } else {
            (carriage::WALL_Y0, carriage::WALL_Y1)
        };
        let wall = carriage::WALL_X_HALF;
        pieces.push(cuboid(center - wall, center + wall, y0, y1, face, face + carriage::WALL_H));
        let inward = v3(0., -sign, 0.);
        for x in [center - clamp::SCREW_X, center + clamp::SCREW_X] {
            let outside = v3(x, sign * (carriage::WALL_Y1 + 0.01), clamp::SCREW_Z);
            let through = carriage::WALL_Y1 - carriage::WALL_Y0 + 0.02;
            cuts.push(Solid::cylinder(outside, inward, m3::ADJUSTER_SHANK_D / 2., through)?);
            cuts.push(Solid::cylinder(outside, inward, m3::INSERT_D / 2., clamp::INSERT_DEPTH + 0.01)?);
        }
        let (x, y) = (carriage::mount_x(), sign * carriage::MOUNT_Y);
        cuts.push(cylinder(x, y, arm - 0.01, m5::shank_d() / 2., face - arm + 0.02)?);
        let mouth = carriage::MOUNT_CSK_D / 2.;
        cuts.push(Solid::cone(v3(x, y, arm), V3::Z, mouth, m5::shank_d() / 2., carriage::mount_csk_depth())?);
        let y = sign * tower::RAIL_INSERT_Y;
        for x in tower::RAIL_INSERT_X {
            let (x0, x1) = (x - (drive::center_max() - center), x + (center - drive::center_min()));
            cuts.push(slot(x0, x1, y, 2. * carriage::SLOT_R, arm - 0.01, face - arm + 0.02)?);
            cuts.push(slot(x0, x1, y, m3::HEAD_D, face - m3::HEAD_DEPTH, m3::HEAD_DEPTH + 0.01)?);
        }
    }
    Solid::union_all(&pieces)?.cut_all(&cuts)
}

/// A motor clamp pad, with the sockets its screws' tips seat in.
fn clamp_pad_piece() -> Result<Solid> {
    let (x, y, z) = (clamp::PAD_X / 2., clamp::PAD_Y / 2., clamp::PAD_Z);
    let sockets = [-clamp::SCREW_X, clamp::SCREW_X]
        .into_iter()
        .map(|at| Solid::cylinder(v3(at, -y, z / 2.), V3::Y, clamp::SOCKET_D / 2., clamp::SOCKET_DEPTH))
        .collect::<Result<Vec<_>>>()?;
    cuboid(-x, x, -y, y, 0., z).cut_all(&sockets)
}

/// The ground tower: the foot with its M5 passages and heads' seats, and the post with the arm's
/// inserts in its top.
fn ground_tower_piece() -> Result<Solid> {
    let (z0, z1) = (ground::FOOT_Z0, ground::FOOT_Z1);
    let solid = Solid::union_all(&[
        cuboid(ground::FOOT_X0, ground::FOOT_X1, ground::FOOT_Y0, ground::FOOT_Y1, z0, z1),
        cuboid(ground::POST_X0, ground::POST_X1, ground::POST_Y0, ground::POST_Y1, z1, ground::TOP_Z),
    ])?;
    let mut cuts = vec![];
    for [x, y] in ground::BASE_POINTS {
        cuts.push(cylinder(x, y, z0, m5::shank_d() / 2., z1 - z0)?);
        cuts.push(cylinder(x, y, z1 - m5::HEAD_DEPTH, m5::HEAD_D / 2., m5::HEAD_DEPTH)?);
    }
    let depth = ground::ARM_INSERT_DEPTH;
    for [x, y] in ground::ARM_POINTS {
        cuts.push(cylinder(x, y, ground::TOP_Z - depth, m3::INSERT_D / 2., depth + 0.01)?);
    }
    solid.cut_all(&cuts)
}

/// The ground arm: the leaf spring from its pad to the nose, rounded at its roots, the shoe's
/// holder with its back wall, jaws and shelf, the arm's counterbored screws, and the clamp
/// screw's support-free bores through the clamp jaw.
fn ground_arm_piece() -> Result<Solid> {
    let (z, top) = (ground::TOP_Z, ground::TOP_Z + ground::ARM_H);
    let (beam0, beam1, nose) = (ground::BEAM_X0, ground::BEAM_X1, ground::NOSE_Y / 2.);
    let spring = Solid::union_all(&[
        cuboid(ground::PAD_X0, ground::PAD_X1, ground::PAD_Y0, ground::PAD_Y1, z, top),
        cuboid(beam0, beam1, ground::BEAM_Y0, ground::BEAM_Y1, z, top),
        cuboid(beam0, ground::HOLDER_BACK_FACE_X, -nose, nose, z, top),
    ])?;
    let roots = [[beam0, ground::PAD_Y1], [beam1, ground::PAD_Y1], [beam0, nose], [beam1, -nose]];
    let at_root = |p: V3| roots.iter().any(|&[x, y]| (p.x - x).hypot(p.y - y) < 1e-6);
    let edges = Edges(spring.edges("|Z")?.iter().filter(|e| at_root(e.center)).cloned().collect());
    ensure!(edges.len() == roots.len(), "the spring is rounded at the corners where it meets the pad and the nose");
    let (h0, h1) = (ground::SHOE_Z0, ground::SHOE_Z0 + ground::HOLDER_H);
    let (back, front) = (ground::HOLDER_BACK_FACE_X, ground::HOLDER_FRONT_X);
    let (clamp_out, clamp_in) = (ground::HOLDER_CLAMP_OUTER_Y, ground::HOLDER_CLAMP_INNER_Y);
    let (fixed_in, fixed_out) = (ground::HOLDER_FIXED_INNER_Y, ground::HOLDER_FIXED_OUTER_Y);
    let solid = Solid::union_all(&[
        spring.fillet(&edges, ground::SPRING_FILLET_R)?,
        cuboid(back - ground::HOLDER_BACK_T, back, clamp_out, fixed_out, h0, h1),
        cuboid(back, front, clamp_out, clamp_in, h0, h1),
        cuboid(back, front, fixed_in, fixed_out, h0, h1),
        cuboid(ground::HOLDER_SHELF_X0, front, clamp_out, fixed_out, h0 - ground::HOLDER_SHELF_H, h0),
    ])?;
    let mut cuts = vec![];
    for [x, y] in ground::ARM_POINTS {
        cuts.push(cylinder(x, y, z, ground::ARM_SHANK_D / 2., ground::ARM_H)?);
        cuts.push(cylinder(x, y, top - m3::HEAD_DEPTH, m3::HEAD_D / 2., m3::HEAD_DEPTH)?);
    }
    let bores = [(ground::SHOE_CLAMP_SHANK_D, clamp_in + 0.1), (m3::INSERT_D, clamp_out + ground::SHOE_CLAMP_INSERT_DEPTH)];
    for (diameter, end) in bores {
        cuts.push(teardrop(diameter / 2., ground::SHOE_CLAMP_X, ground::SHOE_CLAMP_Z, clamp_out - 0.1, end)?);
    }
    solid.cut_all(&cuts)
}

/// The copper ground shoe, in its holder.
fn shoe_piece() -> Solid {
    let (y, z0) = (ground::SHOE_Y / 2., ground::SHOE_Z0);
    cuboid(ground::SHOE_BACK_X, ground::SHOE_FRONT_X, -y, y, z0, z0 + ground::SHOE_Z)
}

/// One body of the assembly: its name, its solid in place, and its colour.
struct Row {
    name: String,
    solid: Solid,
    color: [f64; 3],
}

/// The assembly: the pieces in place, then the balls, the motor, its pulley, the belt and the
/// tube.
fn assembly(p: &Pieces) -> Result<Vec<Row>> {
    let pet = petgf_black();
    let row = |name: &str, solid: Solid, color: [f64; 3]| Row { name: name.to_owned(), solid, color };
    let mut rows = vec![];
    for (i, &[x, y]) in foot::CENTERS.iter().enumerate() {
        rows.push(row(&format!("base-foot-{}", i + 1), p.foot.translate(v3(x, y, -foot::H)), pet));
    }
    let in_place = [
        ("stationary-base", &p.base),
        ("motor-tower", &p.motor_tower),
        ("motor-carriage", &p.carriage),
        ("ground-tower", &p.ground_tower),
        ("ground-flexure-arm", &p.ground_arm),
        ("turntable-90t", &p.turntable),
        ("upper-race-ring", &p.race_ring),
        ("ball-cage", &p.cage),
        ("spool", &p.spool),
    ];
    for (name, solid) in in_place {
        rows.push(row(name, solid.clone(), pet));
    }
    let (center, y, z) = (drive::center_nominal(), clamp::PAD_Y_CENTER, clamp::PAD_Z0);
    rows.push(row("motor-clamp-pad-negative-y", p.clamp_pad.translate(v3(center, -y, z)), pet));
    let turned = p.clamp_pad.rotate(V3::ZERO, V3::Z, 180.);
    rows.push(row("motor-clamp-pad-positive-y", turned.translate(v3(center, y, z)), pet));
    rows.push(row("c110-ground-shoe", p.shoe.clone(), copper()));
    rows.push(row("tube-nest", p.nest.translate(v3(0., 0., nest::SEAT_Z)), pet));
    rows.push(row("10mm-pp-balls", balls()?, tpu_black()));
    rows.push(row("23hs30-2804s", motor_body(center)?, stainless()));
    rows.push(row("20t-htd5m-pulley", motor_pulley_body(center)?, aluminium()));
    let z = (drive::LAND_Z0 + drive::LAND_Z1) / 2. - belt::WIDTH / 2.;
    rows.push(row("550-5m-15-belt", belt_band(center, z, z + belt::WIDTH, 0.)?, tpu_black()));
    let foot_z = nest::SEAT_Z + nest::BASE_H;
    rows.push(row("5in-316l-tube", annulus(tube::OD / 2., tube::ID / 2., tube::LENGTH, foot_z)?, stainless()));
    Ok(rows)
}

/// The balls on their circle.
fn balls() -> Result<Solid> {
    let count = bearing::BALL_COUNT;
    let balls = (0..count)
        .map(|i| {
            let [x, y] = polar(bearing::RACE_R, 360. * i as f64 / count as f64);
            Solid::sphere(v3(x, y, bearing::BALL_Z), bearing::BALL_D / 2.)
        })
        .collect::<Result<Vec<_>>>()?;
    Ok(Solid::compose(&balls))
}

/// The motor hung face-down with its shaft at `center`: its frame, its face pilot and its shaft.
fn motor_body(center: f64) -> Result<Solid> {
    let (z, half) = (drive::FACE_Z, motor::FRAME / 2.);
    Solid::union_all(&[
        cuboid(center - half, center + half, -half, half, z, z + motor::BODY_LENGTH),
        cylinder(center, 0., z - motor::PILOT_LENGTH, motor::PILOT_DIAMETER / 2., motor::PILOT_LENGTH)?,
        cylinder(center, 0., z - motor::SHAFT_LENGTH, motor::SHAFT_DIAMETER / 2., motor::SHAFT_LENGTH)?,
    ])
}

/// The motor's pulley on its shaft at `center`: its land and its two flanges.
fn motor_pulley_body(center: f64) -> Result<Solid> {
    let (bore, flange) = (motor::SHAFT_DIAMETER / 2., motor_pulley::FLANGE_DIAMETER / 2.);
    let length = motor_pulley::FLANGE_LENGTH;
    let (land0, land1) = (drive::LAND_Z0, drive::LAND_Z1);
    let pulley = Solid::union_all(&[
        annulus(drive::MOTOR_PULLEY_CORE_D / 2., bore, land1 - land0, land0)?,
        annulus(flange, bore, length, drive::MOTOR_PULLEY_Z0)?,
        annulus(flange, bore, length, drive::MOTOR_PULLEY_Z1 - length)?,
    ])?;
    Ok(pulley.translate(v3(center, 0., 0.)))
}

/// The distance the assembly's drawing is simplified to: the viewer's budget for the assembly's
/// size, or the sag a ball's outline shows at the viewer's angular deflection, whichever is finer.
fn presentation_tolerance(rows: &[Row]) -> f64 {
    let first = rows[0].solid.bounds();
    let (mut lower, mut upper) = (first.min, first.max);
    for row in rows {
        let b = row.solid.bounds();
        lower = lower.min(b.min);
        upper = upper.max(b.max);
    }
    let size = upper - lower;
    let linear = (size.x + size.y + size.z) / 3. * LINEAR_DEFLECTION_RATIO;
    let angular = bearing::BALL_D / 2. * (1. - (ANGULAR_DEFLECTION / 2.).cos());
    linear.min(angular)
}
