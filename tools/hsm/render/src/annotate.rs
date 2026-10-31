//! What a look answers and burns into its frame (tools/look.sh): the pixels it clicks, the rays it
//! casts, the box gaps it dimensions, and the legend, callout labels, millimetre grid and scale
//! bar laid over the picture, all read through the camera the frame was drawn with.

use crate::camera::Camera;
use crate::job::Job;
use crate::pick;
use crate::plan::{Plan, Role, hex_css, kept};
use crate::scene::{Aabb, Scene};
use glam::DVec3;

/// The first of these at least `raw`, else 1000: the grid's step and the scale bar's length.
fn nice(raw: f64) -> f64 {
    for p in [1.0, 2.0, 5.0, 10.0, 20.0, 25.0, 50.0, 100.0, 200.0, 500.0] {
        if raw <= p {
            return p;
        }
    }
    1000.0
}

/// A number as JavaScript prints it: no trailing zeros, and no minus on zero.
pub fn js(v: f64) -> String {
    if v == 0.0 { "0".into() } else { format!("{v}") }
}

/// `Number.prototype.toFixed`.
pub fn fixed(v: f64, places: usize) -> String {
    let v = if v == 0.0 { 0.0 } else { v };
    format!("{v:.places$}")
}

/// `+v.toFixed(places)`: rounded, then printed as a number.
pub fn rounded(v: f64, places: usize) -> f64 {
    fixed(v, places).parse().unwrap_or(v)
}

pub fn join(v: &[f64]) -> String {
    v.iter().map(|&x| js(x)).collect::<Vec<_>>().join(",")
}

fn join_rounded(v: DVec3, places: usize) -> String {
    join(&[v.x, v.y, v.z].map(|x| rounded(x, places)))
}

/// A click at a pixel: the first front face of a body with faces on the frame that stands
/// inside every cutting plane.
pub struct Pick {
    pub px: [f64; 2],
    pub hit: Option<(usize, DVec3, f64)>,
}

pub fn pick(scene: &Scene, plan: &Plan, camera: &Camera, clips: &[[f64; 4]], px: [f64; 2]) -> Pick {
    let (from, dir) = pick::pixel_ray(camera, px[0], px[1]);
    let faced = |mi: usize| {
        matches!(
            plan.roles[scene.meshes[mi].body],
            Role::Solid | Role::Xray | Role::Shell | Role::Highlight
        )
    };
    let hit = pick::cast(scene, from, dir, f64::INFINITY, true, faced)
        .into_iter()
        .find(|h| kept(clips, h.point))
        .map(|h| (scene.meshes[h.mesh].body, h.point, h.distance));
    Pick { px, hit }
}

/// A `--ray`: the run from a point to the first surface of any body in the model, whatever the
/// frame hides or cuts, or to the cast's limit.
pub struct Cast {
    pub from: [f64; 3],
    pub dir: [f64; 3],
    pub limit: f64,
    pub hit: Option<(usize, f64)>,
    pub end: DVec3,
}

pub fn cast(scene: &Scene, plan: &Plan, from: [f64; 3], dir: [f64; 3], limit: f64) -> Cast {
    let origin = DVec3::from(from);
    let d = DVec3::from(dir).normalize();
    let first = pick::cast(scene, origin, d, limit, false, |mi| {
        plan.roles[scene.meshes[mi].body] != Role::Dropped
    })
    .into_iter()
    .next();
    Cast {
        from,
        dir,
        limit,
        hit: first.map(|h| (scene.meshes[h.mesh].body, h.distance)),
        end: first.map_or(origin + d * limit, |h| h.point),
    }
}

/// A `--gap`: the two bodies' boxes, on the axis where they stand closest apart.
pub enum Gap {
    Missing(String, String),
    Overlap(String, String),
    Found {
        a: String,
        b: String,
        axis: usize,
        mm: f64,
        /// The ends of the witness line, on the two box faces.
        ends: [DVec3; 2],
        faces: [f64; 2],
    },
}

pub fn gap(scene: &Scene, a: &str, b: &str) -> Gap {
    let boxed = |n: &str| scene.bodies.iter().find(|x| x.name == n).map(|x| x.bbox).filter(|bb| !bb.is_empty());
    let (Some(ba), Some(bb)) = (boxed(a), boxed(b)) else {
        return Gap::Missing(a.into(), b.into());
    };
    let mut best: Option<(usize, f64, f64, f64)> = None;
    for k in 0..3 {
        let g = (ba.min[k] - bb.max[k]).max(bb.min[k] - ba.max[k]);
        if g > 0.0 && best.is_none_or(|(_, bg, _, _)| g < bg) {
            best = Some((k, g, ba.max[k].min(bb.max[k]), ba.min[k].max(bb.min[k])));
        }
    }
    let Some((axis, g, lo, hi)) = best else {
        return Gap::Overlap(a.into(), b.into());
    };
    let mid: [f64; 3] = std::array::from_fn(|k| (ba.min[k].max(bb.min[k]) + ba.max[k].min(bb.max[k])) / 2.0);
    let (mut p1, mut p2) = (DVec3::from(mid), DVec3::from(mid));
    p1[axis] = lo;
    p2[axis] = hi;
    Gap::Found {
        a: a.into(),
        b: b.into(),
        axis,
        mm: rounded(g, 2),
        ends: [p1, p2],
        faces: [lo, hi],
    }
}

const AXES: [&str; 3] = ["x", "y", "z"];

pub struct Line {
    pub a: (f64, f64),
    pub b: (f64, f64),
}

pub struct GridLine {
    pub line: Line,
    pub zero: bool,
}

pub struct Tick {
    pub x: f64,
    pub y: f64,
    pub text: String,
}

pub struct Label {
    pub name: String,
    pub left: bool,
    pub tint: Option<u32>,
    pub anchor: (f64, f64),
    pub y: f64,
    pub on_screen: bool,
}

pub struct Dim {
    pub line: Line,
    pub faces: Vec<Line>,
    pub text: String,
}

pub struct CastMark {
    pub line: Line,
    pub hit: bool,
    pub text: String,
}

pub struct PickMark {
    pub x: f64,
    pub y: f64,
    pub name: Option<String>,
}

pub struct Scale {
    pub x: f64,
    pub y: f64,
    pub px: f64,
    pub mm: f64,
}

/// Everything a look lays over its frame, and the lines it prints beside it.
pub struct Annotations {
    pub width: f64,
    pub height: f64,
    pub grid_lines: Vec<GridLine>,
    pub ticks: Vec<Tick>,
    pub labels: Vec<Label>,
    pub dims: Vec<Dim>,
    pub casts: Vec<CastMark>,
    pub picks: Vec<PickMark>,
    pub scale: Scale,
    pub legend: Vec<String>,
    /// The grid's step and the two axes it is drawn on.
    pub grid: Option<(f64, String)>,
    /// The lines a look prints for a shot.
    pub text: Vec<String>,
}

pub struct Look<'a> {
    pub scene: &'a Scene,
    pub job: &'a Job,
    pub plan: &'a Plan,
    pub camera: &'a Camera,
    pub picks: &'a [Pick],
    pub casts: &'a [Cast],
    pub gaps: &'a [Gap],
    /// The bodies `select` named that are on the frame, in name order.
    pub selected: &'a [String],
    pub title: String,
    pub out: String,
}

impl Look<'_> {
    fn screen(&self, p: DVec3) -> (f64, f64) {
        let (x, y, _) = self.camera.to_screen(p);
        (x, y)
    }

    fn line(&self, a: DVec3, b: DVec3) -> Line {
        Line {
            a: self.screen(a),
            b: self.screen(b),
        }
    }

    fn body_name(&self, b: usize) -> String {
        let n = &self.scene.bodies[b].name;
        if n.is_empty() { "(unnamed)".into() } else { n.clone() }
    }

    pub fn annotate(&self) -> Annotations {
        let (w, h) = (self.camera.width as f64, self.camera.height as f64);
        let cam = self.camera;
        let target = cam.target;
        let z = cam.target_depth();
        let corner_lo = cam.unproject(-1.0, -1.0, z);
        let corner_hi = cam.unproject(1.0, 1.0, z);
        let mm_per_px = cam.mm_per_px();
        let view_dir = -cam.back();

        // The grid: lines of constant world coordinate on the two axes least along the view,
        // across the rectangle the frame covers at the target's depth.
        let mut grid_lines = Vec::new();
        let mut ticks = Vec::new();
        let ortho = self.job.is_ortho();
        let mut grid = None;
        if self.job.grid.unwrap_or(ortho) {
            let mut axes: Vec<usize> = vec![0, 1, 2];
            axes.sort_by(|&a, &b| view_dir[a].abs().total_cmp(&view_dir[b].abs()));
            let (in_plane, depth) = ([axes[0], axes[1]], axes[2]);
            let lo = |k: usize| corner_lo[k].min(corner_hi[k]);
            let hi = |k: usize| corner_lo[k].max(corner_hi[k]);
            let step = nice((hi(in_plane[0]) - lo(in_plane[0])).max(hi(in_plane[1]) - lo(in_plane[1])) / 9.0);
            grid = Some((step, format!("{}/{}", AXES[in_plane[0]], AXES[in_plane[1]])));
            for (i, &a) in in_plane.iter().enumerate() {
                let other = in_plane[1 - i];
                let mut v = (lo(a) / step).ceil() * step;
                while v <= hi(a) {
                    let (mut p1, mut p2) = (DVec3::ZERO, DVec3::ZERO);
                    p1[a] = v;
                    p2[a] = v;
                    p1[other] = lo(other);
                    p2[other] = hi(other);
                    p1[depth] = target[depth];
                    p2[depth] = target[depth];
                    let l = self.line(p1, p2);
                    if l.a.0.is_finite() && l.b.0.is_finite() {
                        ticks.push(Tick {
                            x: l.a.0.max(30.0).min(w - 30.0),
                            y: l.a.1.max(16.0).min(h - 10.0),
                            text: format!("{}{}", AXES[a], js(v)),
                        });
                        grid_lines.push(GridLine {
                            line: l,
                            zero: v.abs() < 1e-9,
                        });
                    }
                    v += step;
                }
            }
        }

        // The two box faces a gap is measured between, as lines across the frame.
        let depth_axis = (0..3).fold(0, |best, k| if view_dir[k].abs() > view_dir[best].abs() { k } else { best });
        let face = |axis: usize, v: f64| {
            let mut q1 = DVec3::from(std::array::from_fn::<f64, 3, _>(|k| corner_lo[k].min(corner_hi[k])));
            let mut q2 = DVec3::from(std::array::from_fn::<f64, 3, _>(|k| corner_lo[k].max(corner_hi[k])));
            q1[depth_axis] = target[depth_axis];
            q2[depth_axis] = target[depth_axis];
            q1[axis] = v;
            q2[axis] = v;
            self.line(q1, q2)
        };
        let finite = |l: &Line| [l.a.0, l.a.1, l.b.0, l.b.1].iter().all(|v| v.is_finite());
        let dims = self
            .gaps
            .iter()
            .filter_map(|g| match g {
                Gap::Found { axis, mm, ends, faces, .. } => {
                    let line = self.line(ends[0], ends[1]);
                    finite(&line).then(|| Dim {
                        line,
                        faces: faces.iter().map(|&v| face(*axis, v)).filter(|l| finite(l)).collect(),
                        text: format!("{} mm box", js(*mm)),
                    })
                }
                _ => None,
            })
            .collect();
        let casts = self
            .casts
            .iter()
            .filter_map(|c| {
                let line = self.line(DVec3::from(c.from), c.end);
                finite(&line).then(|| CastMark {
                    line,
                    hit: c.hit.is_some(),
                    text: match c.hit {
                        Some((b, mm)) => format!("{} mm → {}", js(rounded(mm, 2)), self.body_name(b)),
                        None => format!("{} mm no contact", js(c.limit)),
                    },
                })
            })
            .collect();
        let picks = self
            .picks
            .iter()
            .map(|p| PickMark {
                x: p.px[0],
                y: p.px[1],
                name: p.hit.map(|(b, _, _)| self.body_name(b)),
            })
            .collect();

        let bar_mm = nice(w * 0.16 * mm_per_px);
        let bar_px = bar_mm / mm_per_px;
        let scale = Scale {
            x: w - bar_px - 26.0,
            y: h - 24.0,
            px: bar_px,
            mm: bar_mm,
        };

        // The legend.
        let roles = &self.plan.roles;
        let count = |r: &[Role]| roles.iter().filter(|x| r.contains(x)).count();
        let (solid, xray, shell, ghost, hidden) = (
            count(&[Role::Solid, Role::Highlight]),
            count(&[Role::Xray]),
            count(&[Role::Shell]),
            count(&[Role::Ghost]),
            count(&[Role::Hidden]),
        );
        let mut hidden_names: Vec<String> = (0..roles.len())
            .filter(|&b| roles[b] == Role::Hidden)
            .map(|b| self.body_name(b))
            .collect();
        hidden_names.sort();
        let (c, u) = self.job.cam_up();
        let zoom = self.job.zoom.unwrap_or(match self.job.frame {
            crate::job::Framing::Posed => 3.0,
            crate::job::Framing::Look => 2.5,
        });
        let mut legend = vec![self.title.clone()];
        legend.push(format!(
            "{}  cam {}  up {}  target {}{}",
            if ortho { format!("ortho span ±{} mm", fixed(cam.half, 1)) } else { format!("persp zoom {}", js(zoom)) },
            join(&c),
            join(&u),
            [target.x, target.y, target.z].map(|v| fixed(v, 1)).join(","),
            self.job.orbit.as_ref().map(|o| format!("  orbit {o}")).unwrap_or_default(),
        ));
        legend.push(format!(
            "{solid} solid  {}{}{ghost} ghost (edges only)  {hidden} hidden   {} mm/px",
            if xray > 0 { format!("{xray} x-ray  ") } else { String::new() },
            if shell > 0 { format!("{shell} shell  ") } else { String::new() },
            fixed(mm_per_px, 3),
        ));
        if !self.job.clip.is_empty() {
            let bands: Vec<String> = self.job.clip.iter().map(|c| format!("{}[{},{}]", c.axis, js(c.lo), js(c.hi))).collect();
            legend.push(format!("clip  {}  (cuts left open)", bands.join("  ")));
        }
        if let Some(s) = &self.job.section {
            legend.push(format!("section  at {}  normal {}  (cut faces filled)", join(&s.at), join(&s.normal)));
        }
        if !hidden_names.is_empty() {
            let more = hidden_names.len().saturating_sub(6);
            legend.push(format!(
                "hiding  {}{}",
                hidden_names[..hidden_names.len().min(6)].join(" "),
                if more > 0 { format!(" +{more} more") } else { String::new() }
            ));
        }
        for g in self.gaps {
            legend.push(match g {
                Gap::Missing(a, b) => format!("gap  {a},{b} — no such body"),
                Gap::Overlap(a, b) => format!("gap  {a},{b} — boxes overlap on every axis"),
                Gap::Found { a, b, axis, mm, .. } => format!(
                    "gap  {a} → {b}  {} mm on {}  (BOX faces, dashed — not a surface distance)",
                    js(*mm),
                    AXES[*axis]
                ),
            });
        }
        for c in self.casts {
            legend.push(match c.hit {
                Some((b, mm)) => format!(
                    "ray  {} → {}  {} mm to {} at {}",
                    join(&c.from),
                    join(&c.dir),
                    js(rounded(mm, 2)),
                    self.body_name(b),
                    join_rounded(c.end, 2)
                ),
                None => format!(
                    "ray  {} → {}  no contact in {} mm (the cast's limit)",
                    join(&c.from),
                    join(&c.dir),
                    js(c.limit)
                ),
            });
        }
        for p in self.picks {
            legend.push(match p.hit {
                Some((b, at, mm)) => format!(
                    "pick  {} px → {} — AMBER — at {}, {} mm from the eye",
                    join(&p.px),
                    self.body_name(b),
                    join_rounded(at, 2),
                    js(rounded(mm, 2))
                ),
                None => format!("pick  {} px → nothing; the frame is empty at that pixel", join(&p.px)),
            });
        }
        if !self.job.select.is_empty() {
            legend.push(format!(
                "select  {} → {}",
                self.job.select.join(" "),
                if self.selected.is_empty() { "no body on this frame".into() } else { format!("{} — AMBER", self.selected.join(" ")) }
            ));
        }
        if let Some((step, axes)) = &grid {
            legend.push(format!("grid  {} mm on {axes}", js(*step)));
        }
        legend.extend(self.job.caption.iter().cloned());
        let legend_bottom = 10.0 + legend.len() as f64 * 17.0 + 14.0;

        // Callout labels in the two margins, each leader-lined to its body's centre.
        let mut labels = Vec::new();
        if self.job.labels.unwrap_or(!self.job.only.is_empty()) {
            let mut left = Vec::new();
            let mut right = Vec::new();
            for (b, body) in self.scene.bodies.iter().enumerate() {
                if roles[b] != Role::Solid || body.bbox.is_empty() {
                    continue;
                }
                let s = self.screen(DVec3::from(body.bbox.center()));
                if s.0 < w / 2.0 { left.push((b, s)) } else { right.push((b, s)) }
            }
            for (list, is_left) in [(left, true), (right, false)] {
                let mut list = list;
                list.sort_by(|a, b| a.1.1.total_cmp(&b.1.1));
                const PITCH: f64 = 21.0;
                let top = if is_left { legend_bottom + 14.0 } else { 22.0 };
                let bot = h - 46.0;
                let mut ys = Vec::with_capacity(list.len());
                let mut prev = f64::NEG_INFINITY;
                for (_, s) in &list {
                    let want = if s.1.is_finite() { s.1 } else { top };
                    let y = want.max(prev + PITCH).max(top);
                    ys.push(y);
                    prev = y;
                }
                let n = ys.len();
                for i in (0..n).rev() {
                    if ys[i] > bot {
                        ys[i] = bot - (n - 1 - i) as f64 * PITCH;
                    }
                    if i > 0 && ys[i] - ys[i - 1] < PITCH {
                        ys[i - 1] = ys[i] - PITCH;
                    }
                }
                for (i, (b, s)) in list.into_iter().enumerate() {
                    labels.push(Label {
                        name: self.body_name(b),
                        left: is_left,
                        tint: self.plan.tints[b],
                        anchor: s,
                        y: ys[i].max(16.0),
                        on_screen: s.0.is_finite()
                            && s.1.is_finite()
                            && s.0 > -50.0
                            && s.0 < w + 50.0
                            && s.1 > -50.0
                            && s.1 < h + 50.0,
                    });
                }
            }
        }

        // The block a look prints for the shot.
        let mut text = vec![
            String::new(),
            format!("wrote {}  ({}x{})", self.out, cam.width, cam.height),
            format!(
                "  view      {}  cam {}  up {}",
                self.job.view.clone().or_else(|| self.job.orbit.clone()).unwrap_or_else(|| "custom".into()),
                join(&c),
                join(&u)
            ),
            format!(
                "  framing   {}  target {}  {} mm/px  scale bar {} mm",
                if ortho { format!("ortho, span ±{} mm", fixed(cam.half, 2)) } else { format!("perspective, zoom {}", js(zoom)) },
                join_rounded(target, 2),
                fixed(mm_per_px, 4),
                js(bar_mm)
            ),
        ];
        let mut solid_box = Aabb::EMPTY;
        for (b, body) in self.scene.bodies.iter().enumerate() {
            if roles[b] == Role::Solid {
                solid_box.union(&body.bbox);
            }
        }
        if !solid_box.is_empty() {
            let r = |v: f64| js(rounded(v, 2));
            text.push(format!(
                "  subject   x[{},{}] y[{},{}] z[{},{}]  (the solid set's box — what framed the shot)",
                r(solid_box.min[0]),
                r(solid_box.max[0]),
                r(solid_box.min[1]),
                r(solid_box.max[1]),
                r(solid_box.min[2]),
                r(solid_box.max[2])
            ));
        }
        text.push(format!(
            "  frame     covers world lo {} → hi {} at the target plane",
            join_rounded(corner_lo, 2),
            join_rounded(corner_hi, 2)
        ));
        text.push(format!(
            "  bodies    {solid} solid   {xray} x-ray   {}{ghost} ghost (edges only)   {hidden} hidden",
            if shell > 0 { format!("{shell} shell   ") } else { String::new() }
        ));
        if !hidden_names.is_empty() {
            text.push(format!("  hiding    {}", hidden_names.join(" ")));
        }
        for l in &legend {
            for key in ["gap", "ray", "pick", "select"] {
                if let Some(rest) = l.strip_prefix(key).and_then(|r| r.strip_prefix(' ')) {
                    text.push(format!("  {:<10}{}", key, rest.trim_start()));
                }
            }
        }
        if let Some((step, axes)) = &grid {
            text.push(format!("  grid      {} mm on {axes}", js(*step)));
        }
        if !labels.is_empty() {
            text.push(format!("  labelled  {}", labels.iter().map(|l| l.name.as_str()).collect::<Vec<_>>().join(" ")));
        }
        if ghost > 0 && self.job.context.as_deref().unwrap_or("ghost") == "ghost" {
            text.push(format!(
                "  note      nothing was removed except the {hidden} above; ghosts are edges, still in frame"
            ));
        }

        Annotations {
            width: w,
            height: h,
            grid_lines,
            ticks,
            labels,
            dims,
            casts,
            picks,
            scale,
            legend,
            grid,
            text,
        }
    }
}

/// The colour a label's leader, dot and chip are drawn in.
pub fn label_ink(tint: Option<u32>) -> String {
    tint.map(hex_css).unwrap_or_else(|| "#ffd479".into())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn numbers_print_as_javascript_prints_them() {
        assert_eq!(js(1.0), "1");
        assert_eq!(js(-0.0), "0");
        assert_eq!(js(0.707107), "0.707107");
        assert_eq!(js(rounded(12.499, 2)), "12.5");
        assert_eq!(fixed(-0.0, 2), "0.00");
        assert_eq!(join(&[1.0, -1.0, 1.0]), "1,-1,1");
    }

    #[test]
    fn nice_steps() {
        assert_eq!(nice(0.3), 1.0);
        assert_eq!(nice(21.0), 25.0);
        assert_eq!(nice(700.0), 1000.0);
    }
}
