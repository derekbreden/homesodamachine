//! The corbeled pump bay and motor rooms beneath the display housing, with the wiring
//! corridors and the opening the side-loading cartridge rises through.
use crate::catalog::{clearance, running};
use crate::display;
use crate::funnel;
use crate::plan::{Bounds, Graph, Op, P2, P3, Shape};
use crate::pump::{case, offset_polygon, tray};
use crate::shell::{FRONT_PLANE_Y, WALL, Z_SEAM, shell};
use crate::spec::Box;
use crate::structure::profile;
use hsm_enclosure_retainer_numbers::{channels, datums};

/// The shared electrical corridor's diamond half span.
const SHARED_HALF_SPAN: f64 = 11.0;
/// The pump cross run's roof half span.
const INTERNAL_WIRE_HALF_SPAN: f64 = 6.0;
/// The display link's diamond half span.
const DISPLAY_LINK_HALF_SPAN: f64 = 9.0;
/// The bay's air over the motors' ends.
const BAY_CROWN_AIR: f64 = 1.7;
/// The shared corridor's axis over the motors' ends, the cross run's over that, and the
/// corridor's rear end aft of the tee wall.
const SHARED_RISE: f64 = 2.776;
const CROSS_RISE: f64 = 4.0;
const SHARED_AFT: f64 = 0.664;
/// The display link: its inner end back off the PCB's terminal, its entry fore of it.
const LINK_BACK: f64 = 6.0;
const LINK_ENTRY: f64 = 2.0;
/// The chimney the display link climbs: its plan, its top and the link's inner end in it.
const CHIMNEY_X: P2 = [-10.0, 10.0];
const CHIMNEY_Y: P2 = [72.0, 84.0];
const CHIMNEY_TOP: f64 = 334.0;
const LINK_INNER: P3 = [0.0, 78.0, 321.0];

/// The mount's broad stock, from the pumps' bearing plane to the roof, trimmed to the exterior.
pub fn stock(g: &mut Graph, b: &Box, silhouette: Shape) -> Shape {
    let d = datums(b);
    let fill = g.box_([
        b.inner[0] - 1.0,
        b.inner[1] + 1.0,
        FRONT_PLANE_Y - 1.0,
        funnel::housing_back_y(funnel::CENTER_Y),
        d.bearing_z,
        b.outer[5] + 1.0,
    ]);
    g.intersect(fill, &[silhouette])
}

/// The opening the cartridge loads up through, from under the seam to its bearing plane.
pub fn loading_opening(g: &mut Graph, b: &Box) -> Shape {
    let d = datums(b);
    g.box_([
        d.x0 - running(),
        d.x1 + running(),
        d.y0 - running(),
        shell().bay_back_y(&b.pack.collet_plate),
        Z_SEAM - 20.0,
        d.bearing_z,
    ])
}

/// The cartridge's clearance opens below a roof growing inward from the front and tee walls.
fn corbeled_opening(g: &mut Graph, b: &Box) -> Shape {
    let d = channels(b);
    let fore = d.fore_y - running();
    let aft = d.aft_y + running();
    let middle = (fore + aft) / 2.0;
    let spring = d.top_z + running();
    g.yz_prism(d.x0 - running(), d.x1 + running(), vec![
        [fore, Z_SEAM - 1.0],
        [aft, Z_SEAM - 1.0],
        [aft, spring],
        [middle, spring + middle - fore],
        [fore, spring],
    ])
}

/// The radius the motor cans' terminal crown opens to under the bay's crown.
fn terminal_crown_r(b: &Box) -> f64 {
    let t = tray();
    let crown = b.pump_bay[2] - running();
    let opening = b
        .pack
        .pump_trays
        .iter()
        .map(|p| p[2])
        .fold(f64::NEG_INFINITY, f64::max)
        + t.motor_crown
        + BAY_CROWN_AIR
        - shell().pump_cartridge_z_clearance;
    t.can_half + crown - opening
}

fn cone(g: &mut Graph, x: f64, y: f64, radii: P2, z0: f64, height: f64) -> Shape {
    let r = radii[0].max(radii[1]);
    g.add(
        Op::Cone {
            axis: 2,
            centre: [x, y],
            radii,
            span: [z0, z0 + height],
        },
        vec![],
        Some([x - r, x + r, y - r, y + r, z0, z0 + height]),
    )
}

/// Each pump's inverse: the room its boss takes, the can over it and the terminal crown's
/// flare to a teardrop roof.
fn inverse_cuts(g: &mut Graph, b: &Box) -> Vec<Shape> {
    let (t, e) = (tray(), shell());
    let finish = clearance(false, true, false);
    let radius = terminal_crown_r(b);
    let mut out = Vec::new();
    for &[x, y0, z] in &b.pack.pump_trays {
        let flange = z - e.pump_seated_drop;
        let y = y0 + t.rear_axis_y_shift;
        let room = g.prism(
            2,
            0.0,
            t.boss_depth,
            offset_polygon(&case().bore_profile(), e.cap_boss_air),
        );
        let lifted = g.translate(room, [0.0, 0.0, finish]);
        let room = g.union(room, &[lifted]);
        out.push(g.translate(room, [x, y, flange]));
        let shoulder = offset_polygon(&case().bore_profile(), e.cap_boss_air)
            .iter()
            .map(|p| p[0].hypot(p[1]))
            .fold(0.0, f64::max);
        out.push(cone(g, x, y, [shoulder, 0.0],
                      flange + t.boss_depth + finish, shoulder));
        let start = flange + t.motor_crown - WALL;
        out.push(g.zcyl(
            t.can_half,
            x,
            y,
            flange + t.boss_depth + finish - 0.01,
            start + 0.01,
        ));
        let rise = radius - t.can_half;
        out.push(cone(g, x, y, [t.can_half, radius], start, rise));
        out.push(cone(g, x, y, [radius, 0.0], start + rise, radius));
    }
    out
}

fn box_points(b: &Bounds) -> Vec<P3> {
    (0..8)
        .map(|i| [b[(i >> 2) & 1], b[2 + ((i >> 1) & 1)], b[4 + (i & 1)]])
        .collect()
}

fn diamond([x, y, z]: P3, r: f64) -> [P3; 4] {
    [[x - r, y, z], [x, y, z + r], [x + r, y, z], [x, y, z - r]]
}

/// A display-plane point placed in the machine frame.
fn on_display(rotation: &[P3; 3], translation: &P3, p: P3) -> P3 {
    std::array::from_fn(|k| {
        rotation[k][0] * p[0] + rotation[k][1] * p[1] + rotation[k][2] * p[2] + translation[k]
    })
}

/// The convex hull of the points' YZ shadow, run over their X span: a corridor no wire's
/// passage leaves.
fn corridor(g: &mut Graph, points: &[P3]) -> (Shape, Vec<P3>) {
    let mut plan: Vec<P2> = points.iter().map(|p| [p[1], p[2]]).collect();
    plan.sort_by(|a, b| a[0].total_cmp(&b[0]).then(a[1].total_cmp(&b[1])));
    plan.dedup();
    let turn = |a: P2, b: P2, c: P2| (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
    let chain = |sequence: &mut dyn Iterator<Item = P2>| {
        let mut out: Vec<P2> = Vec::new();
        for p in sequence {
            while out.len() > 1 && turn(out[out.len() - 2], out[out.len() - 1], p) <= 1e-9 {
                out.pop();
            }
            out.push(p);
        }
        out.pop();
        out
    };
    let mut outline = chain(&mut plan.iter().copied());
    outline.extend(chain(&mut plan.iter().rev().copied()));
    let span = [
        points.iter().map(|p| p[0]).fold(f64::INFINITY, f64::min),
        points
            .iter()
            .map(|p| p[0])
            .fold(f64::NEG_INFINITY, f64::max),
    ];
    let hull: Vec<P3> = span
        .iter()
        .flat_map(|&x| outline.iter().map(move |&[y, z]| [x, y, z]))
        .collect();
    (g.prism(0, span[0], span[1], outline), hull)
}

/// The wiring's passages over the motors: the shared corridor back to the tee wall and its
/// opening up the housing face, the cross run between the pumps, and the display link up the
/// chimney to the PCB's terminal. Each comes with the points that bound it.
fn wire_cuts(g: &mut Graph, b: &Box) -> Vec<(Shape, Vec<P3>)> {
    let d = datums(b);
    let motor_end = d.flange_z + tray().motor_crown;
    let rear_z = motor_end + SHARED_RISE;
    let cross_z = rear_z + CROSS_RISE;
    let rear_y = b.pack.collet_plate.wall_aft_y + SHARED_AFT;
    let cy = d.motor_y;

    let r = SHARED_HALF_SPAN;
    let shared = g.prism(
        1,
        cy,
        rear_y,
        vec![
            [-r, rear_z],
            [0.0, rear_z + r],
            [r, rear_z],
            [0.0, rear_z - r],
        ],
    );
    let mut shared_points = diamond([0.0, cy, rear_z], r).to_vec();
    shared_points.extend(diamond([0.0, rear_y, rear_z], r));
    let opening = [
        -r,
        r,
        funnel::housing_back_y(funnel::CENTER_Y),
        rear_y,
        rear_z,
        b.pump_bay[2] + 0.01,
    ];

    let r = INTERNAL_WIRE_HALF_SPAN;
    let xs = b.pack.pump_trays.iter().map(|p| p[0]);
    let (xa, xb) = (
        xs.clone().fold(f64::INFINITY, f64::min),
        xs.fold(f64::NEG_INFINITY, f64::max),
    );
    let floor = motor_end - WALL;
    let section = vec![
        [cy - r, floor],
        [cy + r, floor],
        [cy + r, cross_z],
        [cy, cross_z + r],
        [cy - r, cross_z],
    ];
    let cross_points: Vec<P3> = [xa, xb]
        .iter()
        .flat_map(|&x| section.iter().map(move |&[y, z]| [x, y, z]))
        .collect();
    let cross = g.prism(0, xa, xb, section);

    let (rotation, translation) = display::frame(&b.outer);
    let normal = profile(&b.outer).normal;
    let terminal = on_display(
        &rotation,
        &translation,
        [
            display::BODY_OFFSET_X,
            display::BODY_OFFSET_SLOPE,
            -(display::FACET_THICKNESS + display::pcb_cut_through() - 1.0),
        ],
    );
    let link: P3 = std::array::from_fn(|k| terminal[k] - normal[k] * LINK_BACK);
    let entry: P3 = std::array::from_fn(|k| terminal[k] + normal[k] * LINK_ENTRY);
    let r = DISPLAY_LINK_HALF_SPAN;
    let local: Vec<P3> = diamond(entry, r)
        .into_iter()
        .chain(diamond(link, r))
        .map(|p| {
            let delta: P3 = std::array::from_fn(|k| p[k] - translation[k]);
            std::array::from_fn(|k| (0..3).map(|j| rotation[j][k] * delta[j]).sum())
        })
        .collect();
    let bounds: Bounds = std::array::from_fn(|i| {
        let values = local.iter().map(|p| p[i / 2]);
        if i % 2 == 0 {
            values.fold(f64::INFINITY, f64::min) - 1.0
        } else {
            values.fold(f64::NEG_INFINITY, f64::max) + 1.0
        }
    });
    let chimney = [
        CHIMNEY_X[0],
        CHIMNEY_X[1],
        CHIMNEY_Y[0],
        CHIMNEY_Y[1],
        rear_z,
        CHIMNEY_TOP,
    ];
    let mut cloud: Vec<P3> = box_points(&bounds)
        .into_iter()
        .map(|p| on_display(&rotation, &translation, p))
        .collect();
    cloud.extend(diamond(link, r));
    cloud.extend(diamond(LINK_INNER, r));
    cloud.extend(box_points(&chimney));
    let (link_body, link_points) = corridor(g, &cloud);

    vec![
        (shared, shared_points),
        (g.box_(opening), box_points(&opening)),
        (cross, cross_points),
        (link_body, link_points),
    ]
}

/// The room over the motors' crowns up to the PCB, wrapping the cross run and the display link.
fn upper_wire_room(g: &mut Graph, b: &Box, wires: &[(Shape, Vec<P3>)]) -> Shape {
    let (t, d) = (tray(), datums(b));
    let radius = terminal_crown_r(b);
    let base = d.flange_z + t.motor_crown - WALL + radius - t.can_half;
    let peak = base + radius;
    let (x0, x1) = (
        display::BODY_OFFSET_X - display::pcb_x() / 2.0,
        display::BODY_OFFSET_X + display::pcb_x() / 2.0,
    );
    // The crowns' run is the PCB's span across the box, where the display stands on the facet.
    let at = display::centre_x(&b.outer);
    let mut cloud: Vec<P3> = [x0 + at, x1 + at]
        .iter()
        .flat_map(|&x| {
            [
                [d.motor_y - radius, base],
                [d.motor_y + radius, base],
                [d.motor_y, peak],
            ]
            .map(|[y, z]| [x, y, z])
        })
        .collect();
    let (rotation, translation) = display::frame(&b.outer);
    let pcb = [
        x0,
        x1,
        display::BODY_OFFSET_SLOPE - display::pcb_slope() / 2.0,
        display::BODY_OFFSET_SLOPE + display::pcb_slope() / 2.0,
        -display::FACET_THICKNESS - display::pcb_cut_through(),
        display::GLASS_SEAT,
    ];
    cloud.extend(
        box_points(&pcb)
            .into_iter()
            .map(|p| on_display(&rotation, &translation, p)),
    );
    // The room wraps the cross run and the link within the PCB's span; past it, each is cut in
    // its own right.
    let (lo, hi) = (x0 + at, x1 + at);
    for (_, points) in &wires[2..] {
        cloud.extend(points.iter().map(|p| [p[0].clamp(lo, hi), p[1], p[2]]));
    }
    corridor(g, &cloud).0
}

/// Everything the mount takes out of front-top: the loading opening, the pumps' inverse, the
/// wiring's passages and the room over the motors.
pub fn fixed_cuts(g: &mut Graph, b: &Box) -> Vec<Shape> {
    let mut out = vec![loading_opening(g, b), corbeled_opening(g, b)];
    out.extend(inverse_cuts(g, b));
    let wires = wire_cuts(g, b);
    out.extend(wires.iter().map(|(shape, _)| *shape));
    out.push(upper_wire_room(g, b, &wires));
    out
}
