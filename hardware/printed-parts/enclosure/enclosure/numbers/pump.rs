//! The fitted pump: its molded case profiles in the case frame, and the tray dimensions the
//! enclosure holds it by. The case frame puts the footprint's corner at the origin; the pump's
//! axis stands at the footprint centre, its skirt top at Z=0 and its head toward Z−.
use crate::catalog::running;
use crate::P2;
use std::sync::OnceLock;

/// The Kamoer KPHM400's measured reference dimensions, in its bracket frame.
pub struct Reference {
    pub rear_axis_y_shift: f64,
    pub tube_casing_w: f64,
    pub outlet_span_x: f64,
    pub skirt_depth: f64,
    pub head_front_below_skirt: f64,
    pub skirt_y: f64,
    pub skirt_y_max: f64,
    pub skirt_y_plus_air: f64,
    pub skirt_upper_band: f64,
    pub skirt_body_y: f64,
    pub skirt_support_xy_air: f64,
    pub skirt_support_y_minus: f64,
    pub skirt_support_y_plus: f64,
    pub head_w: f64,
    pub head_depth: f64,
    pub motor_dia: f64,
    pub motor_reach: f64,
    pub outlet_relief: f64,
    pub outlet_relief_top_z: f64,
}

pub const KAMOER: Reference = Reference {
    rear_axis_y_shift: -1.0,
    tube_casing_w: 12.75,
    outlet_span_x: 72.50,
    skirt_depth: 8.0,
    head_front_below_skirt: 41.15,
    skirt_y: 62.5,
    skirt_y_max: 30.11,
    skirt_y_plus_air: 0.30,
    skirt_upper_band: 3.0,
    skirt_body_y: 54.0,
    skirt_support_xy_air: 0.15,
    skirt_support_y_minus: 5.0,
    skirt_support_y_plus: 3.482,
    head_w: 62.61,
    head_depth: 47.88,
    motor_dia: 35.73,
    motor_reach: 62.55,
    outlet_relief: 2.075,
    outlet_relief_top_z: -36.295,
};

impl Reference {
    pub fn barb_pitch(&self) -> f64 {
        self.outlet_span_x - self.tube_casing_w
    }
    pub fn skirt_body_y_max(&self) -> f64 {
        self.skirt_y_max + self.skirt_y_plus_air - self.skirt_support_y_plus - self.skirt_support_xy_air
    }
    pub fn skirt_body_y_min(&self) -> f64 {
        self.skirt_body_y_max() - self.skirt_body_y
    }
    pub fn head_front_z(&self) -> f64 {
        -self.head_depth
    }
    pub fn motor_end_z(&self) -> f64 {
        self.motor_reach
    }
    pub fn outlet_relief_run(&self) -> f64 {
        self.head_depth + self.outlet_relief_top_z
    }
}

/// The pump case's stock numbers, in the case frame, as its polygonal stock is built from them.
pub mod stock {
    pub const FOOTPRINT_X: f64 = 70.0;
    pub const FOOTPRINT_Y: f64 = 70.0;
    pub const CORNER_R: f64 = 6.0;
    pub const WALL_THICKNESS: f64 = 3.0;
    pub const BASE_THICKNESS: f64 = 3.0;
    pub const RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT: f64 = 18.0;
    pub const SKIRT_UPPER_HEIGHT: f64 = 21.0;
    pub const SKIRT_WIDE_FLARE_PER_SIDE: f64 = 3.0;
    pub const SKIRT_NARROW_TAPER_PER_SIDE: f64 = 4.0;
    pub const SKIRT_WIDE_STRAIGHT_HEIGHT: f64 = 4.5;
    pub const BORE_SQUARE_SIDE: f64 = 43.0;
    pub const TOWER_HEIGHT: f64 = 60.0;
    pub const CYLINDER_ID: f64 = 37.0;
    pub const LOWER_HEIGHT: f64 = 23.0;
    pub const SNAP_PROTRUSION_PER_SIDE: f64 = 2.5;
    pub const TUBE_PROTRUSION_LENGTH: f64 = 11.3;
    pub const LOWER_CAP_THICKNESS: f64 = 3.0;
    pub const LEDGE_DEPTH: f64 = 1.5;
    pub const LEDGE_SHELF_SPAN: f64 = 26.03;
    pub const BORE_SPAN: f64 = 53.0;
    pub const TOWER_CAP_THICKNESS: f64 = 3.0;
    pub const CYLINDER_CARDINAL_STEP: f64 = 0.5;
    pub const OVERCUT: f64 = 0.1;
}

/// The pump case's polygonal stock, in the case frame.
pub struct Case {
    pub footprint_x: f64,
    pub footprint_y: f64,
    pub corner_r: f64,
    pub wall_thickness: f64,
    pub center_x: f64,
    pub center_y: f64,
    pub footprint_half_extent: f64,
    pub base_thickness: f64,
    pub ramp_from_skirt_to_octagon_height: f64,
    pub skirt_upper_height: f64,
    pub skirt_wall: f64,
    pub skirt_wide_flare_per_side: f64,
    pub skirt_narrow_taper_per_side: f64,
    pub skirt_wide_straight_height: f64,
    pub skirt_support_band: f64,
    pub ledge_depth: f64,
    pub ledge_shelf_span: f64,
    pub bore_half_span: f64,
    pub vertex_far: f64,
    pub vertex_near: f64,
    pub tower_height: f64,
    pub tower_cap_thickness: f64,
    pub cylinder_id: f64,
    pub cylinder_r_inner: f64,
    pub lower_height: f64,
    pub lower_cap_thickness: f64,
    pub lower_footprint_straight: f64,
    pub cutter_half_extent: f64,
    pub overcut: f64,
    pub arc_segments: usize,
    pub bore_depth: f64,
    pub bore_bottom_z: f64,
    pub cylinder_r_outer: f64,
    pub cylinder_top_z: f64,
    pub cylinder_bottom_z: f64,
    pub skirt_base_half_extent: f64,
    pub skirt_wide_half_extent: f64,
    pub skirt_narrow_half_extent: f64,
    pub skirt_mid_narrow_half_extent: f64,
    pub skirt_transition_y_mid: P2,
    pub skirt_transition_y_end: P2,
    pub skirt_z_steps: [f64; 4],
    pub skirt_bottom_z: f64,
    pub lower_ramp_height: f64,
    pub lower_cap_top_z: f64,
    pub lower_cap_bottom_z: f64,
    pub pos_y_face_y: f64,
}

pub fn case() -> &'static Case {
    static CASE: OnceLock<Case> = OnceLock::new();
    CASE.get_or_init(Case::new)
}

impl Case {
    fn new() -> Case {
        let footprint_x = stock::FOOTPRINT_X;
        let footprint_y = stock::FOOTPRINT_Y;
        let corner_r = stock::CORNER_R;
        let wall_thickness = stock::WALL_THICKNESS;
        let footprint_half_extent = footprint_x / 2.0;
        let base_thickness = stock::BASE_THICKNESS;
        let ramp_from_skirt_to_octagon_height = stock::RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT;
        let skirt_upper_height = stock::SKIRT_UPPER_HEIGHT;
        let skirt_wide_flare_per_side = stock::SKIRT_WIDE_FLARE_PER_SIDE;
        let skirt_narrow_taper_per_side = stock::SKIRT_NARROW_TAPER_PER_SIDE;
        let skirt_wide_straight_height = stock::SKIRT_WIDE_STRAIGHT_HEIGHT;
        let bore_square_side: f64 = stock::BORE_SQUARE_SIDE;
        let bore_half_diag = bore_square_side * 2.0_f64.sqrt() / 2.0;
        let bore_half_span = stock::BORE_SPAN / 2.0;
        let tower_height = stock::TOWER_HEIGHT;
        let cylinder_id = stock::CYLINDER_ID;
        let lower_height = stock::LOWER_HEIGHT;
        let snap_protrusion_per_side = stock::SNAP_PROTRUSION_PER_SIDE;
        let tube_protrusion_length = stock::TUBE_PROTRUSION_LENGTH;
        let case_outer_x: f64 = footprint_x + 2.0 * snap_protrusion_per_side;
        let case_outer_y: f64 = footprint_y + 2.0 * skirt_wide_flare_per_side + tube_protrusion_length;
        let vertex_far = bore_half_span;
        let bore_depth = base_thickness + ramp_from_skirt_to_octagon_height;
        let cylinder_r_outer = vertex_far + wall_thickness + stock::CYLINDER_CARDINAL_STEP;
        let skirt_base_half_extent = footprint_half_extent;
        let skirt_narrow_half_extent = skirt_base_half_extent - skirt_narrow_taper_per_side;
        let skirt_narrow_straight_height =
            skirt_wide_straight_height - (skirt_narrow_taper_per_side - skirt_wide_flare_per_side);
        let skirt_z_steps = [
            -skirt_upper_height,
            -skirt_wide_flare_per_side,
            -(skirt_narrow_taper_per_side - skirt_wide_flare_per_side),
            -skirt_narrow_straight_height,
        ];
        let skirt_bottom_z: f64 = skirt_z_steps.iter().sum();
        let lower_cap_top_z = skirt_bottom_z - lower_height;
        let lower_cap_thickness = stock::LOWER_CAP_THICKNESS;
        Case {
            footprint_x,
            footprint_y,
            corner_r,
            wall_thickness,
            center_x: footprint_x / 2.0,
            center_y: footprint_y / 2.0,
            footprint_half_extent,
            base_thickness,
            ramp_from_skirt_to_octagon_height,
            skirt_upper_height,
            skirt_wall: wall_thickness,
            skirt_wide_flare_per_side,
            skirt_narrow_taper_per_side,
            skirt_wide_straight_height,
            skirt_support_band: skirt_narrow_taper_per_side,
            ledge_depth: stock::LEDGE_DEPTH,
            ledge_shelf_span: stock::LEDGE_SHELF_SPAN,
            bore_half_span,
            vertex_far,
            vertex_near: bore_half_diag - bore_half_span,
            tower_height,
            tower_cap_thickness: stock::TOWER_CAP_THICKNESS,
            cylinder_id,
            cylinder_r_inner: cylinder_id / 2.0,
            lower_height,
            lower_cap_thickness,
            lower_footprint_straight: skirt_wide_straight_height,
            cutter_half_extent: case_outer_x.max(case_outer_y) / 2.0 + 5.0,
            overcut: stock::OVERCUT,
            arc_segments: 8,
            bore_depth,
            bore_bottom_z: bore_depth,
            cylinder_r_outer,
            cylinder_top_z: footprint_half_extent + base_thickness - cylinder_r_outer,
            cylinder_bottom_z: bore_depth + tower_height,
            skirt_base_half_extent,
            skirt_wide_half_extent: skirt_base_half_extent + skirt_wide_flare_per_side,
            skirt_narrow_half_extent,
            skirt_mid_narrow_half_extent: skirt_base_half_extent - skirt_wide_flare_per_side,
            skirt_transition_y_mid: [skirt_wide_flare_per_side, -skirt_wide_flare_per_side],
            skirt_transition_y_end: [skirt_wide_flare_per_side, -skirt_narrow_taper_per_side],
            skirt_z_steps,
            skirt_bottom_z,
            lower_ramp_height: skirt_base_half_extent + skirt_wide_flare_per_side - skirt_narrow_half_extent,
            lower_cap_top_z,
            lower_cap_bottom_z: lower_cap_top_z - lower_cap_thickness,
            pos_y_face_y: footprint_y / 2.0 + footprint_half_extent,
        }
    }

    /// A skirt section: a wide half and a narrow half, each with its own corner radius,
    /// joined by straight transitions on the ±X sides.
    #[allow(clippy::too_many_arguments)]
    pub fn split(
        &self, wide: f64, wide_radius: f64, narrow: f64, narrow_radius: f64, ty_plus: f64, ty_minus: f64,
        wide_y: f64, narrow_y: f64,
    ) -> Vec<P2> {
        let n = self.arc_segments;
        let wr = wide_radius.max(0.01);
        let nr = narrow_radius.max(0.01);
        let mut result = Vec::new();
        for (cx, cy, r, start) in [
            (wide - wr, wide_y - wr, wr, 0.0),
            (-wide + wr, wide_y - wr, wr, 90.0),
            (-narrow + nr, -narrow_y + nr, nr, 180.0),
            (narrow - nr, -narrow_y + nr, nr, 270.0),
        ] {
            if start == 180.0 {
                let a = [-wide, ty_plus];
                let b = [-narrow, ty_minus];
                result.push(a);
                if b != a {
                    result.push(b);
                }
            }
            for i in 0..=n {
                let a = (start + 90.0 * i as f64 / n as f64).to_radians();
                result.push([cx + r * a.cos(), cy + r * a.sin()]);
            }
        }
        let a = [narrow, ty_minus];
        let b = [wide, ty_plus];
        result.push(a);
        if b != a {
            result.push(b);
        }
        result
    }

    /// The skirt's five sections from its top down, offset inward by `wall`.
    pub fn skirt_set(&self, wall: f64) -> [Vec<P2>; 5] {
        let shift = wall * (2.0_f64.sqrt() - 1.0);
        let base = self.skirt_base_half_extent - wall;
        let wide = self.skirt_wide_half_extent - wall;
        let narrow = self.skirt_narrow_half_extent - wall;
        let mid_narrow = self.skirt_mid_narrow_half_extent - wall;
        let radius = self.corner_r - wall;
        let symmetric = self.split(base, radius, base, radius, shift, shift, base, base);
        let [mid_plus, mid_minus] = self.skirt_transition_y_mid;
        let mid = self.split(wide, radius, mid_narrow, radius, mid_plus + shift, mid_minus + shift, base, base);
        let [end_plus, end_minus] = self.skirt_transition_y_end;
        let end = self.split(wide, radius, narrow, radius, end_plus + shift, end_minus + shift, base, base);
        [symmetric.clone(), symmetric, mid, end.clone(), end]
    }

    /// The lower case's four sections from the skirt's bottom down, offset inward by `wall`.
    pub fn lower_set(&self, wall: f64) -> [Vec<P2>; 4] {
        let seam_shift = wall * (2.0_f64.sqrt() - 1.0);
        let narrow = self.skirt_narrow_half_extent - wall;
        let base = self.skirt_base_half_extent - wall;
        let radius = self.corner_r - wall;
        let ty = self.skirt_transition_y_end[1] + seam_shift;
        let symmetric = self.split(narrow, radius, narrow, radius, ty, ty, base, base);
        let [_, _, _, _, top] = self.skirt_set(wall);
        [top.clone(), top, symmetric.clone(), symmetric]
    }

    pub fn lower_z_steps(&self) -> [f64; 3] {
        let uniform = self.lower_height - self.lower_ramp_height - self.lower_footprint_straight;
        [-self.lower_footprint_straight, -self.lower_ramp_height, -uniform]
    }

    /// Every section's level, skirt and lower case together, from the skirt's top down.
    pub fn stack_levels(&self) -> Vec<f64> {
        let mut out = vec![0.0];
        let mut z = 0.0;
        for dz in self.skirt_z_steps.iter().chain(self.lower_z_steps().iter()) {
            z += dz;
            out.push(z);
        }
        out
    }

    /// The sections at those levels.
    pub fn stack_profiles(&self, wall: f64) -> Vec<Vec<P2>> {
        let mut out: Vec<Vec<P2>> = self.skirt_set(wall).into_iter().collect();
        out.extend(self.lower_set(wall).into_iter().skip(1));
        out
    }

    /// The pump bore: an octagon about the origin whose four axis faces each carry a ledge, a
    /// diagonal ramp in to the shelf and back out.
    pub fn bore_profile(&self) -> Vec<P2> {
        let (vf, vn) = (self.vertex_far, self.vertex_near);
        let vertices = [[vn, vf], [vf, vn], [vf, -vn], [vn, -vf], [-vn, -vf], [-vf, -vn], [-vf, vn], [-vn, vf]];
        let mut points = Vec::new();
        for i in 0..8 {
            let [x, y] = vertices[i];
            let [end_x, end_y] = vertices[(i + 1) % 8];
            points.push([x, y]);
            if i % 2 != 0 {
                continue;
            }
            let (dx, dy) = (end_x - x, end_y - y);
            let length = dx.hypot(dy);
            let heading = dy.atan2(dx).to_degrees();
            let (mx, my) = ((x + end_x) / 2.0, (y + end_y) / 2.0);
            let (ux, uy) = (dx / length, dy / length);
            let (mut nx, mut ny) = (uy, -ux);
            if nx * -mx + ny * -my < 0.0 {
                (nx, ny) = (-nx, -ny);
            }
            let inward_left = nx * -uy + ny * ux > 0.0;
            let ramp = self.ledge_depth * 2.0_f64.sqrt();
            let entry = (length - self.ledge_shelf_span) / 2.0;
            let shelf = self.ledge_shelf_span - 2.0 * self.ledge_depth;
            let turn = if inward_left { 45_f64.to_radians() } else { -45_f64.to_radians() };
            let mut cursor = [x, y];
            let mut direction = heading.to_radians();
            for (distance, angle) in [(entry, 0.0), (ramp, turn), (shelf, -turn), (ramp, -turn)] {
                direction += angle;
                cursor[0] += distance * direction.cos();
                cursor[1] += distance * direction.sin();
                points.push(cursor);
            }
        }
        points
    }
}

/// A closed polygon with each edge moved `distance` along its left normal, the corners where
/// neighbouring moved edges meet.
pub fn offset_polygon(points: &[P2], distance: f64) -> Vec<P2> {
    let n = points.len();
    let edges: Vec<[f64; 4]> = (0..n)
        .map(|i| {
            let [x1, y1] = points[i];
            let [x2, y2] = points[(i + 1) % n];
            let (dx, dy) = (x2 - x1, y2 - y1);
            let length = dx.hypot(dy);
            assert!(length != 0.0, "cannot offset a zero length polygon edge");
            [dx, dy, -dy / length, dx / length]
        })
        .collect();
    (0..n)
        .map(|i| {
            let prev = (i + n - 1) % n;
            let [adx, ady, anx, any] = edges[prev];
            let [bdx, bdy, bnx, bny] = edges[i];
            let (ax, ay) = (points[prev][0] + distance * anx, points[prev][1] + distance * any);
            let (bx, by) = (points[i][0] + distance * bnx, points[i][1] + distance * bny);
            let det = adx * bdy - ady * bdx;
            if det.abs() < 1e-10 {
                [bx, by]
            } else {
                let t = ((bx - ax) * bdy - (by - ay) * bdx) / det;
                [ax + t * adx, ay + t * ady]
            }
        })
        .collect()
}

/// The pump tray: the case and reference as the enclosure locates them, and its outlet joins.
pub struct Tray {
    pub head_half: f64,
    pub head_depth: f64,
    pub head_front_z: f64,
    pub boss_half: f64,
    pub boss_depth: f64,
    pub can_half: f64,
    pub motor_crown: f64,
    pub rear_axis_y_shift: f64,
    pub outlet_half: f64,
    pub outlet_pitch: f64,
    pub fitting_w: f64,
    pub shaft_w: f64,
    pub outlet_open_half: f64,
    pub skirt_depth: f64,
    pub skirt_body_open_y_bounds: P2,
    pub skirt_open_y_max: f64,
    pub skirt_upper_band: f64,
    pub outlet_axis_z: f64,
    pub case_half: f64,
    pub shoulder: f64,
}

pub fn tray() -> &'static Tray {
    static TRAY: OnceLock<Tray> = OnceLock::new();
    TRAY.get_or_init(|| {
        let p = &KAMOER;
        let c = case();
        let air = running();
        let outlet_pitch = p.barb_pitch();
        let shaft_w = p.tube_casing_w + 2.0 * running();
        Tray {
            head_half: p.head_w / 2.0,
            head_depth: 48.88,
            head_front_z: p.head_front_z(),
            boss_half: c.bore_half_span,
            boss_depth: c.bore_bottom_z,
            can_half: c.cylinder_id / 2.0,
            motor_crown: p.motor_end_z(),
            rear_axis_y_shift: p.rear_axis_y_shift,
            outlet_half: p.outlet_span_x / 2.0,
            outlet_pitch,
            fitting_w: p.tube_casing_w,
            shaft_w,
            outlet_open_half: (outlet_pitch + shaft_w) / 2.0,
            skirt_depth: p.skirt_depth,
            skirt_body_open_y_bounds: [p.skirt_body_y_min() - air, p.skirt_body_y_max() + air],
            skirt_open_y_max: p.skirt_y_max + p.skirt_y_plus_air,
            skirt_upper_band: p.skirt_upper_band,
            outlet_axis_z: c.skirt_bottom_z,
            case_half: c.footprint_half_extent,
            shoulder: 3.0,
        }
    })
}

/// Where an outlet's under-tangent plane meets the seam and the tube's circle.
pub struct Tangent {
    pub seam: f64,
    pub wall: f64,
    pub u: f64,
    pub z: f64,
}

/// The fore miter that widens the case's outlet room to the tube opening.
pub struct Miter {
    pub body_half: f64,
    pub y0: f64,
    pub open_half: f64,
    pub y_open: f64,
}

impl Tray {
    pub fn half_width(&self) -> f64 {
        self.case_half
    }

    pub fn depth(&self) -> f64 {
        self.boss_depth + self.shoulder
    }

    /// Where the outlet passage starts fore of the pump axis, for a well `air` off the case.
    pub fn outlet_passage_start_y(&self, air: f64) -> f64 {
        let c = case();
        let offset = c.skirt_wall - air;
        c.skirt_transition_y_end[0] + offset * (2.0_f64.sqrt() - 1.0)
    }

    pub fn outlet_fore_miter(&self, air: f64) -> Miter {
        let c = case();
        let body_half = c.skirt_wide_half_extent - (c.skirt_wall - air);
        let open_half = self.outlet_open_half;
        assert!(
            open_half >= body_half - 1e-9,
            "the {} mm tube opening is narrower than the {} mm case-derived outlet room",
            2.0 * open_half,
            2.0 * body_half
        );
        let y0 = self.outlet_passage_start_y(air);
        Miter { body_half, y0, open_half, y_open: y0 + (open_half - body_half) }
    }

    pub fn outlet_under_tangent(&self, air: f64) -> Tangent {
        let c = case();
        let body = self.outlet_fore_miter(air).body_half;
        let r = self.shaft_w / 2.0;
        let seam = c.skirt_bottom_z - c.lower_footprint_straight;
        let wall = body - self.outlet_pitch / 2.0;
        let rise = self.outlet_axis_z - seam;
        let reach = wall * wall + rise * rise;
        assert!(
            reach > r * r,
            "the room edge stands {:.3} mm off a tube axis, inside its {} mm opening",
            reach.sqrt(),
            r
        );
        let run = (reach - r * r).sqrt();
        let u = r * (r * wall + run * rise) / reach;
        let z = self.outlet_axis_z + r * (run * wall - r * rise) / reach;
        Tangent { seam, wall, u, z }
    }
}
