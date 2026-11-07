//! The pump's mount on the lid: one broad lid-rooted cradle the bare pump lowers into, its two
//! fixed rails on rail stops at either end, and the snap cap that closes over the motor, its two
//! spring wings hooking under ledges in the cradle's flanks. The cradle's seat clears the pump's
//! whole scanned barrel, its rooms keep the rails and the lead corridor open, and the cap's bore
//! holds the motor can over the snap band. The pump's frame is its reference's: X along the motor
//! from the motor/head seam, Z up from the foot plane.
use crate::P3;
use crate::design::{Can, Placed, PumpMount, Section, above_core, pump_reference};

/// The spring wing the pump's snap cap shares with the rear snaps' caps, whose numbers these are
/// (`hardware/manifold-layout/rear_snaps.py`, held for the build in machine-data's generated
/// `rear_snaps`): the stock outside the cap's neck, the flat bearing past the receiver's edge, the
/// relaxed spring's face off that edge, the wing's section, its free length from root to hook and
/// the round at its root; the ledge's height off the split, and the hook's solid nose and pointed
/// lead-in.
pub mod wing {
    pub const WALL: f64 = 3.0;
    pub const REACH: f64 = 2.6;
    pub const SIDE: f64 = 0.5;
    pub const WING: f64 = 2.0;
    pub const FREE_LENGTH: f64 = 22.25;
    pub const ROOT_RADIUS: f64 = 1.5;
    pub const LEDGE: f64 = 3.0;
    pub const NOSE_LAND: f64 = 1.6;
    pub const TIP_RISE: f64 = 3.0;
    /// The hook's whole rise above its catch.
    pub const HOOK: f64 = NOSE_LAND + TIP_RISE;
}

/// The cap's split: its wings root on the pump's axis.
pub const SPLIT: f64 = 0.;
/// The angle and the end stock a screwdriver's approach to a wing is stated with; the cradle's
/// broad wings leave it no enclosed tunnel.
pub const TOOL_ANGLE_DEGREES: f64 = -65.;
pub const TOOL_END_STOCK: f64 = 10.;
/// The half-width of the straight channel between the cradle's rail seats, which the lid's recess
/// under the pump's molded cover shares.
pub const CHANNEL_HALF_WIDTH: f64 = 24.81;
/// The cradle's stock outside the cap's wings, each side.
pub const FLANK_STOCK: f64 = 3.;

/// One of the pump's fixed rails, and the room the cradle leaves it: its side across the pump's
/// native Y, the room's outer face, and the rail's lower face and inner return as planes
/// `z = a·x + b·y + c`.
#[derive(Clone, Copy, Debug)]
pub struct Rail {
    pub side: i64,
    pub outer_y: f64,
    pub floor_planes: [P3; 2],
}

/// The snap cap's station on the cradle's flanks, in the cap's section frame: X across the pump,
/// Z up from the split, Y along the pump in the enclosure.
#[derive(Clone, Copy, Debug)]
pub struct Station {
    /// The pump's axis across, in the enclosure's X.
    pub axis_x: f64,
    /// The cap's ends along the pump, in the enclosure's Y.
    pub y0: f64,
    pub y1: f64,
    pub split: f64,
    /// Half the cradle's neck the wings close round, the ledge's inner face, the wings' inner and
    /// outer faces, and the hook's inner face.
    pub neck: f64,
    pub ledge: f64,
    pub inner: f64,
    pub outer: f64,
    pub hook: f64,
    /// Heights off the split: the ledge's bearing, the hook's catch and tip, and the pocket's
    /// ceiling over it.
    pub bearing: f64,
    pub catch: f64,
    pub tip: f64,
    pub ceiling: f64,
    /// The wings' root, its round, and the hook's solid nose.
    pub root: f64,
    pub root_radius: f64,
    pub nose_land: f64,
    pub tool_angle_degrees: f64,
    pub tool_end_stock: f64,
    /// The east tool entry's outer edge, on the aft airline opening's inner plane.
    pub tool_outer_edge: f64,
}

/// The pump's mount, worked from its scan and the above-core design.
#[derive(Clone, Debug)]
pub struct Cradle {
    /// The pump's placement in the enclosure, and how the design holds it.
    pub frame: Placed,
    pub selected: PumpMount,
    /// The motor can as the pump's reference measures it.
    pub can: Can,
    /// The motor band the cradle seats, along the pump's native X, and that band's axis centre in
    /// the enclosure.
    pub band: [f64; 2],
    pub centre: P3,
    /// The cradle's seat, which clears the whole scanned barrel on the running fit.
    pub seat_bore_radius: f64,
    /// The snap cap's bore over the snap band, on the head-on fit.
    pub bore_radius: f64,
    /// The open corridor under the molded wire cover, across the pump's native Y.
    pub cover_room: [f64; 2],
    pub rails: [Rail; 2],
    /// The snap band the cap spans, and the pockets its wings ride in.
    pub cap_band: [f64; 2],
    pub pocket_band: [f64; 2],
    pub station: Station,
    pub stock_half_width: f64,
    /// The solid stock the pockets leave at each end of the motor band.
    pub end_stock: [f64; 2],
}

/// The scanned barrel's points between `first` and `last` along the pump, the end sections
/// interpolated where they fall between stations.
fn section_points(sections: &[Section], first: f64, last: f64) -> Vec<P3> {
    let mut points: Vec<P3> = sections
        .iter()
        .filter(|row| first <= row.x_mm && row.x_mm <= last)
        .flat_map(|row| row.vertices_mm.iter().copied())
        .collect();
    for end in [first, last] {
        let pair = sections.windows(2).find(|w| w[0].x_mm <= end && end <= w[1].x_mm);
        let [a, b] = pair.expect("the scan's stations span the motor band") else { unreachable!() };
        let share = (end - a.x_mm) / (b.x_mm - a.x_mm);
        points.extend(a.vertices_mm.iter().zip(&b.vertices_mm).map(|(p, q)| {
            [p[0] + (q[0] - p[0]) * share, p[1] + (q[1] - p[1]) * share, p[2] + (q[2] - p[2]) * share]
        }));
    }
    points
}

fn largest(values: impl Iterator<Item = f64>) -> f64 {
    values.fold(f64::NEG_INFINITY, f64::max)
}

fn least(values: impl Iterator<Item = f64>) -> f64 {
    values.fold(f64::INFINITY, f64::min)
}

/// The pump's mount.
pub fn cradle() -> &'static Cradle {
    static CRADLE: std::sync::OnceLock<Cradle> = std::sync::OnceLock::new();
    CRADLE.get_or_init(work)
}

fn work() -> Cradle {
    let fits = crate::fits();
    let reference = pump_reference();
    let selected = above_core().pump_mount.clone();
    let frame = above_core().parts.pump.clone();
    let can = reference.motor_can_envelope.clone();
    let [first, last] = selected.motor_band_native_x_mm;
    let points = section_points(&reference.casing_sections, first, last);

    let low_z = least(points.iter().map(|p| p[2]));
    let can_top = can.axis_point_mm[2] + can.radius_mm;
    let mut cover_sides = vec![];
    for side in &reference.rigid_underside.wire_cover_side_profiles {
        let [a, b, c] = side.side_plane.coefficients;
        for x in [first, last] {
            for z in [low_z, can_top] {
                cover_sides.push(a * x + b * z + c);
            }
        }
    }
    // The rounded cover and barrel joins take admission air past the fitted side planes: the open
    // lead corridor takes twice the running fit each side.
    let cover_room = [
        least(cover_sides.iter().copied()) - 2. * fits.running,
        largest(cover_sides.iter().copied()) + 2. * fits.running,
    ];

    let rails = [0, 1].map(|i| {
        let rail = &reference.rigid_underside.rail_face_planes[i];
        let a = rail.planes.outer_upper.z_ax_plus_by_plus_c;
        let b = rail.planes.outer_lower.z_ax_plus_by_plus_c;
        let c = rail.planes.inner_return.z_ax_plus_by_plus_c;
        let corners = [first, last].map(|x| ((b[0] - a[0]) * x + b[2] - a[2]) / (a[1] - b[1]));
        let outer_y = if rail.side > 0 {
            largest(corners.into_iter()) + fits.running
        } else {
            least(corners.into_iter()) - fits.running
        };
        Rail { side: rail.side, outer_y, floor_planes: [b, c] }
    });

    let [o0, o1, o2] = can.axis_point_mm;
    let axis = can.axis_direction;
    let axis_z = |x: f64| o2 + axis[2] * (x - o0) / axis[0];
    let radial = |p: &P3| (p[1] - o1).hypot(p[2] - axis_z(p[0]));
    // The casing's envelope keeps the barrel's observed high spots: one round room clears the
    // whole rigid surface above the axis.
    let barrel_radius = can.radius_mm.max(largest(points.iter().filter(|p| p[2] >= axis_z(p[0])).map(radial)));
    let in_open_room = |p: &P3| {
        if cover_room[0] <= p[1] && p[1] <= cover_room[1] {
            return true;
        }
        rails.iter().any(|rail| {
            let side = rail.side as f64;
            0. <= p[1] * side
                && p[1] * side <= rail.outer_y * side
                && rail.floor_planes.iter().all(|&[a, b, c]| {
                    p[2] >= a * p[0] + b * p[1] + c - fits.running * (1. + a * a + b * b).sqrt() - 1.0e-8
                })
        })
    };
    // The lower seat admits the whole scanned barrel on the running fit; the removable cap keeps
    // the head-on fit.
    let seat_bore_radius =
        barrel_radius.max(largest(points.iter().filter(|p| !in_open_room(p)).map(radial))) + fits.running;

    let middle = (first + last) / 2.;
    let centre = frame.pose().point([middle, o1, axis_z(middle)]);

    let cap_band = selected.snap_band_native_x_mm;
    let upper = section_points(&reference.casing_sections, cap_band[0], cap_band[1]);
    let bore_radius =
        can.radius_mm.max(largest(upper.iter().filter(|p| p[2] >= axis_z(p[0])).map(radial))) + fits.slip;
    let neck = largest([bore_radius].into_iter().chain(rails.iter().map(|r| r.outer_y.abs()))) + wing::WALL;

    // The rear snaps' station: the ledge a reach and the running fit past the neck, the wings'
    // free length up from their root to the catch, the catch on the supported fit.
    let catch_fit = fits.slip + fits.supported_surface;
    let ledge = neck + wing::REACH + fits.running;
    let inner = ledge + wing::SIDE;
    let root = SPLIT;
    let catch = (root + wing::FREE_LENGTH).max(SPLIT + wing::LEDGE + catch_fit);
    let tip = catch + wing::HOOK;
    let outer = inner + wing::WING;
    let ty = frame.translation_mm[1];
    let station = Station {
        axis_x: centre[0],
        y0: ty + cap_band[0],
        y1: ty + cap_band[1],
        split: SPLIT,
        neck,
        ledge,
        inner,
        outer,
        hook: ledge - wing::REACH,
        bearing: catch - catch_fit,
        catch,
        tip,
        ceiling: tip + 2. * fits.running,
        root,
        root_radius: wing::ROOT_RADIUS,
        nose_land: wing::NOSE_LAND,
        tool_angle_degrees: TOOL_ANGLE_DEGREES,
        tool_end_stock: TOOL_END_STOCK,
        tool_outer_edge: centre[0] - outer,
    };
    Cradle {
        band: [first, last],
        centre,
        seat_bore_radius,
        bore_radius,
        cover_room,
        rails,
        cap_band,
        pocket_band: [cap_band[0] - fits.running, cap_band[1] + fits.running],
        stock_half_width: station.outer,
        end_stock: [cap_band[0] - fits.running - first, last - cap_band[1] - fits.running],
        station,
        frame,
        selected,
        can,
    }
}
