//! The enclosure's construction plan: typed solid operations, each with conservative bounds.
//!
//! A feature records operations here and the kernel evaluates the finished graph. A cut skips
//! every cutter whose bounds miss the stock's, so a feature far from a piece costs nothing.
//! Identical operations on identical operands share one node.
use crate::text::Artwork;
use serde_json::{Map, Value, json};
use std::collections::HashMap;
use std::panic::Location;
use std::rc::Rc;

pub use hsm_enclosure_numbers::{Bounds, P2, P3};

/// One edge of a line-and-cubic outline.
#[derive(Clone, Debug, PartialEq)]
pub enum Seg {
    Line(P2, P2),
    Cubic(P2, P2, P2, P2),
}

/// One step of a pen outline: an arc through a midpoint to an end, or a line to a point.
#[derive(Clone, Debug, PartialEq)]
pub enum Step {
    Arc(P2, P2),
    Line(P2),
}

#[derive(Clone, Debug, PartialEq)]
pub struct VentColumn {
    pub cutters: Vec<usize>,
    pub probe: Bounds,
    pub side: f64,
}

#[derive(Clone, Debug, PartialEq)]
pub struct FlankVents {
    pub columns: Vec<VentColumn>,
    pub courses: Vec<P2>,
    pub clearance: f64,
    pub tolerance: f64,
    pub island_min: usize,
}

#[derive(Clone, Debug, PartialEq)]
pub struct HandholdAir {
    pub bed: f64,
    pub roof: f64,
    pub crown: f64,
    pub y: P2,
    pub depth: f64,
    pub corner: f64,
    pub radius: f64,
    pub end_stock: f64,
    pub cutter_depth: f64,
    pub slope: f64,
}

/// The C14 inlet's flange outline, by its landmarks in the panel plane.
#[derive(Clone, Debug, PartialEq)]
pub struct Flange {
    pub clearance: f64,
    pub span: P2,
    pub shoulder: P2,
    pub round_mid: P2,
    pub tangent_start: P2,
    pub ear_tangent: P2,
    pub nose: P2,
    pub taper_angle_deg: f64,
}

/// The rear nameplate's receiver, by the dimension record its plate shares.
pub use crate::snap_geometry::Snap;

/// The raised disposal warning, set in the artwork's glyph outlines on the rear face.
#[derive(Clone, Debug, PartialEq)]
pub struct Letters {
    pub outer: Bounds,
    pub lines: Vec<String>,
    pub family: String,
    pub artwork: Rc<Artwork>,
    pub cap_height: f64,
    pub depth: f64,
    pub embed: f64,
    pub line_gap: f64,
    pub bottom: f64,
}

#[derive(Clone, Debug, PartialEq)]
pub enum Op {
    Empty,
    /// The swept exterior silhouette, built from the piece's structure numbers.
    Silhouette,
    SeamBand {
        outer: Bounds,
        centre: f64,
        exterior: hsm_enclosure_numbers::exterior::Exterior,
    },
    Checkpoint(&'static str),
    Box(Bounds),
    RoundedBox {
        b: Bounds,
        radius: f64,
    },
    Cylinder {
        axis: usize,
        radius: f64,
        centre: P2,
        span: P2,
        stations: Option<P2>,
    },
    Cone {
        axis: usize,
        centre: P2,
        radii: P2,
        span: P2,
    },
    Prism {
        axis: usize,
        span: P2,
        section: Vec<P2>,
    },
    /// A prism with fillets at the named section vertices, its outline offset when asked.
    CornerPrism {
        axis: usize,
        span: P2,
        section: Vec<P2>,
        corners: Vec<usize>,
        radius: f64,
        offset: Option<f64>,
    },
    HandholdCutter {
        b: Bounds,
        radius: f64,
    },
    HandholdFinishAir(HandholdAir),
    /// The flank vent courses that clear the stock's interior, cut by their cutters.
    FlankVentCuts(FlankVents),
    BezierPrism {
        axis: usize,
        span: P2,
        segments: Vec<Seg>,
    },
    ArcPrism {
        axis: usize,
        span: P2,
        start: P2,
        segments: Vec<Step>,
    },
    /// Sections in corresponding order, ruled face to face; its faces name the recipe line.
    RuledStack {
        sections: Vec<Vec<P3>>,
        source: &'static Location<'static>,
    },
    InletFlange(Flange),
    TurnedRuns {
        centre: P2,
        profile: Vec<P3>,
    },
    RadialProfile {
        points: Vec<P2>,
    },
    StadiumX {
        y: f64,
        z: f64,
        radius: f64,
        fore: f64,
        aft: f64,
        span: P2,
    },
    StadiumProfileX {
        y: f64,
        z: f64,
        fore: f64,
        aft: f64,
        points: Vec<P2>,
    },
    NameplateStock(Rc<Snap>),
    NameplateCuts(Rc<Snap>),
    DisposalLetters(Rc<Letters>),
    Union,
    Cut,
    Intersect,
    Translate(P3),
    Rotate {
        origin: P3,
        end: P3,
        angle: f64,
    },
    Mirror(usize),
    /// A rigid frame: rotation rows and a translation.
    Placed {
        rotation: [P3; 3],
        translation: P3,
    },
}

#[derive(Clone, Debug, PartialEq)]
pub struct Node {
    pub op: Op,
    pub inputs: Vec<usize>,
}

/// A graph result and its conservative bounds; `None` means unbounded.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Shape {
    pub index: usize,
    pub bounds: Option<Bounds>,
}

impl Shape {
    pub fn bounds(&self) -> Bounds {
        self.bounds
            .expect("this feature has no conservative numeric bounds")
    }
}

#[derive(Default, Clone)]
pub struct Graph {
    pub nodes: Vec<Node>,
    shared: HashMap<String, usize>,
    additions: HashMap<usize, (Shape, Shape)>,
}

fn overlaps(a: &Bounds, b: &Bounds) -> bool {
    (0..3).all(|k| a[2 * k] < b[2 * k + 1] && b[2 * k] < a[2 * k + 1])
}

impl Graph {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn add(&mut self, op: Op, inputs: Vec<usize>, bounds: Option<Bounds>) -> Shape {
        let node = Node { op, inputs };
        let key = format!("{node:?}");
        let index = *self.shared.entry(key).or_insert_with(|| {
            self.nodes.push(node);
            self.nodes.len() - 1
        });
        Shape { index, bounds }
    }

    pub fn op(&self, shape: Shape) -> &Op {
        &self.nodes[shape.index].op
    }

    /// Retain the result at a construction boundary across edits to later features.
    pub fn checkpoint(&mut self, name: &'static str, shape: Shape) -> Shape {
        self.add(Op::Checkpoint(name), vec![shape.index], shape.bounds)
    }

    /// An authored addition stays separate while subsequent cuts and limits act on both branches.
    pub fn additive(&mut self, stock: Shape, feature: Shape) -> Shape {
        let result = self.boolean_plain(Op::Union, stock, &[feature]);
        self.additions.insert(result.index, (stock, feature));
        result
    }

    pub fn additive_parts(&self, shape: Shape) -> Option<(Shape, Shape)> {
        self.additions.get(&shape.index).copied()
    }

    /// The swept exterior every piece is trimmed to, bounded by the Box's outer bounds.
    pub fn silhouette(&mut self, outer: Bounds) -> Shape {
        self.add(Op::Silhouette, vec![], Some(outer))
    }

    pub fn empty(&mut self) -> Shape {
        self.add(Op::Empty, vec![], None)
    }

    pub fn box_(&mut self, b: Bounds) -> Shape {
        self.add(Op::Box(b), vec![], Some(b))
    }

    pub fn cylinder(
        &mut self,
        axis: usize,
        radius: f64,
        a: f64,
        b: f64,
        lo: f64,
        hi: f64,
    ) -> Shape {
        let span = if lo <= hi { [lo, hi] } else { [hi, lo] };
        let mut bounds = [0.0; 6];
        bounds[2 * axis] = span[0];
        bounds[2 * axis + 1] = span[1];
        let other: Vec<usize> = (0..3).filter(|&k| k != axis).collect();
        for (k, centre) in other.into_iter().zip([a, b]) {
            bounds[2 * k] = centre - radius;
            bounds[2 * k + 1] = centre + radius;
        }
        self.add(
            Op::Cylinder {
                axis,
                radius,
                centre: [a, b],
                span,
                stations: None,
            },
            vec![],
            Some(bounds),
        )
    }

    pub fn xcyl(&mut self, r: f64, y: f64, z: f64, x0: f64, x1: f64) -> Shape {
        self.cylinder(0, r, y, z, x0, x1)
    }
    pub fn ycyl(&mut self, r: f64, x: f64, z: f64, y0: f64, y1: f64) -> Shape {
        self.cylinder(1, r, x, z, y0, y1)
    }
    pub fn zcyl(&mut self, r: f64, x: f64, y: f64, z0: f64, z1: f64) -> Shape {
        self.cylinder(2, r, x, y, z0, z1)
    }

    /// A Y prism whose roof peaks at the teardrop's apex, for printing a horizontal bore.
    pub fn teardrop_y(
        &mut self,
        roof_angle: f64,
        radius: f64,
        x: f64,
        z: f64,
        y0: f64,
        y1: f64,
        up: f64,
    ) -> Shape {
        let angle = roof_angle.to_radians();
        let half = radius * angle.sin();
        let tangent = z + up * radius * angle.cos();
        let apex = z + up * radius / angle.cos();
        let pi2 = std::f64::consts::PI / 2.0;
        let circle = self.add(
            Op::Cylinder {
                axis: 1,
                radius,
                centre: [x, z],
                span: [y0, y1],
                stations: Some([up * pi2 - angle, up * pi2 + angle]),
            },
            vec![],
            Some([x - radius, x + radius, y0, y1, z - radius, z + radius]),
        );
        let roof = self.prism(
            1,
            y0,
            y1,
            vec![[x - half, tangent], [x + half, tangent], [x, apex]],
        );
        self.union(circle, &[roof])
    }

    /// A cylinder whose circle is broken at two stations, the angles its seams stand at.
    pub fn stationed_cylinder(
        &mut self,
        axis: usize,
        radius: f64,
        centre: P2,
        span: P2,
        stations: P2,
    ) -> Shape {
        let mut bounds = [0.0; 6];
        bounds[2 * axis] = span[0];
        bounds[2 * axis + 1] = span[1];
        let other: Vec<usize> = (0..3).filter(|&k| k != axis).collect();
        for (k, c) in other.into_iter().zip(centre) {
            bounds[2 * k] = c - radius;
            bounds[2 * k + 1] = c + radius;
        }
        self.add(
            Op::Cylinder {
                axis,
                radius,
                centre,
                span,
                stations: Some(stations),
            },
            vec![],
            Some(bounds),
        )
    }

    #[track_caller]
    pub fn ruled_stack(&mut self, sections: Vec<Vec<P3>>) -> Shape {
        let bounds = std::array::from_fn(|i| {
            let k = i / 2;
            let values = sections.iter().flatten().map(|p| p[k]);
            if i % 2 == 0 {
                values.fold(f64::INFINITY, f64::min)
            } else {
                values.fold(f64::NEG_INFINITY, f64::max)
            }
        });
        self.add(
            Op::RuledStack {
                sections,
                source: Location::caller(),
            },
            vec![],
            Some(bounds),
        )
    }

    /// A line-and-cubic outline in the plane across `axis`, extruded over `span`.
    pub fn bezier_prism(&mut self, axis: usize, span: P2, segments: Vec<Seg>) -> Shape {
        let points: Vec<P2> = segments
            .iter()
            .flat_map(|s| match s {
                Seg::Line(a, b) => vec![*a, *b],
                Seg::Cubic(a, b, c, d) => vec![*a, *b, *c, *d],
            })
            .collect();
        let bounds = Self::prism_bounds(axis, span, &points);
        self.add(
            Op::BezierPrism {
                axis,
                span,
                segments,
            },
            vec![],
            Some(bounds),
        )
    }

    pub fn prism(&mut self, axis: usize, lo: f64, hi: f64, section: Vec<P2>) -> Shape {
        let span = if lo <= hi { [lo, hi] } else { [hi, lo] };
        let bounds = Self::prism_bounds(axis, span, &section);
        self.add(
            Op::Prism {
                axis,
                span,
                section,
            },
            vec![],
            Some(bounds),
        )
    }
    pub fn yz_prism(&mut self, x0: f64, x1: f64, section: Vec<P2>) -> Shape {
        self.prism(0, x0, x1, section)
    }
    pub fn xz_prism(&mut self, y0: f64, y1: f64, section: Vec<P2>) -> Shape {
        self.prism(1, y0, y1, section)
    }
    pub fn xy_prism(&mut self, z0: f64, z1: f64, section: Vec<P2>) -> Shape {
        self.prism(2, z0, z1, section)
    }

    pub fn prism_bounds(axis: usize, span: P2, section: &[P2]) -> Bounds {
        let mut bounds = [0.0; 6];
        bounds[2 * axis] = span[0];
        bounds[2 * axis + 1] = span[1];
        let other: Vec<usize> = (0..3).filter(|&k| k != axis).collect();
        for (i, k) in other.into_iter().enumerate() {
            bounds[2 * k] = section.iter().map(|p| p[i]).fold(f64::INFINITY, f64::min);
            bounds[2 * k + 1] = section
                .iter()
                .map(|p| p[i])
                .fold(f64::NEG_INFINITY, f64::max);
        }
        bounds
    }

    /// The standing round of a rectangular stock; zero radius keeps the box.
    pub fn rounded(&mut self, shape: Shape, radius: f64) -> Shape {
        if radius <= 0.0 {
            return shape;
        }
        let Op::Box(_) = self.nodes[shape.index].op else {
            panic!("the enclosure standing round belongs to rectangular stock");
        };
        let b = shape.bounds();
        self.add(Op::RoundedBox { b, radius }, vec![], Some(b))
    }

    fn boolean(&mut self, op: Op, stock: Shape, others: &[Shape]) -> Shape {
        if let Some((core, feature)) = self.additive_parts(stock) {
            let core = self.boolean_plain(op.clone(), core, others);
            let feature = if matches!(op, Op::Union) {
                feature
            } else {
                self.boolean_plain(op, feature, others)
            };
            return self.additive(core, feature);
        }
        self.boolean_plain(op, stock, others)
    }

    fn boolean_plain(&mut self, op: Op, stock: Shape, others: &[Shape]) -> Shape {
        let mut nodes = vec![stock];
        match (&op, stock.bounds) {
            (Op::Cut, Some(b)) => nodes.extend(
                others
                    .iter()
                    .filter(|o| o.bounds.is_none_or(|ob| overlaps(&b, &ob))),
            ),
            _ => nodes.extend_from_slice(others),
        }
        if nodes.len() == 1 {
            return stock;
        }
        let all: Option<Vec<Bounds>> = nodes.iter().map(|n| n.bounds).collect();
        let bounds = match (&op, all) {
            (Op::Union, Some(all)) => Some(std::array::from_fn(|i| {
                let k = i / 2;
                if i % 2 == 0 {
                    all.iter().map(|b| b[2 * k]).fold(f64::INFINITY, f64::min)
                } else {
                    all.iter()
                        .map(|b| b[2 * k + 1])
                        .fold(f64::NEG_INFINITY, f64::max)
                }
            })),
            (Op::Union, None) => None,
            (Op::Intersect, Some(all)) => Some(std::array::from_fn(|i| {
                let k = i / 2;
                if i % 2 == 0 {
                    all.iter()
                        .map(|b| b[2 * k])
                        .fold(f64::NEG_INFINITY, f64::max)
                } else {
                    all.iter()
                        .map(|b| b[2 * k + 1])
                        .fold(f64::INFINITY, f64::min)
                }
            })),
            _ => stock.bounds,
        };
        self.add(op, nodes.iter().map(|n| n.index).collect(), bounds)
    }

    pub fn union(&mut self, stock: Shape, others: &[Shape]) -> Shape {
        self.boolean(Op::Union, stock, others)
    }
    pub fn cut(&mut self, stock: Shape, others: &[Shape]) -> Shape {
        self.boolean(Op::Cut, stock, others)
    }
    pub fn intersect(&mut self, stock: Shape, others: &[Shape]) -> Shape {
        self.boolean(Op::Intersect, stock, others)
    }
    /// Cut each air in turn, as a sequence of single cuts.
    pub fn cut_each(&mut self, mut stock: Shape, airs: &[Shape]) -> Shape {
        for air in airs {
            stock = self.cut(stock, &[*air]);
        }
        stock
    }
    /// Union each part in turn, as a sequence of single unions.
    pub fn union_each(&mut self, mut stock: Shape, parts: &[Shape]) -> Shape {
        for part in parts {
            stock = self.union(stock, &[*part]);
        }
        stock
    }

    pub fn translate(&mut self, shape: Shape, delta: P3) -> Shape {
        let bounds = shape
            .bounds
            .map(|b| std::array::from_fn(|i| b[i] + delta[i / 2]));
        self.add(Op::Translate(delta), vec![shape.index], bounds)
    }

    pub fn rotate(&mut self, shape: Shape, origin: P3, end: P3, angle: f64) -> Shape {
        let bounds = shape.bounds.map(|b| {
            let corners: Vec<P3> = (0..8)
                .map(|i| {
                    rotate_point(
                        [b[(i >> 2) & 1], b[2 + ((i >> 1) & 1)], b[4 + (i & 1)]],
                        origin,
                        end,
                        angle,
                    )
                })
                .collect();
            std::array::from_fn(|i| {
                let k = i / 2;
                if i % 2 == 0 {
                    corners.iter().map(|p| p[k]).fold(f64::INFINITY, f64::min)
                } else {
                    corners
                        .iter()
                        .map(|p| p[k])
                        .fold(f64::NEG_INFINITY, f64::max)
                }
            })
        });
        self.add(Op::Rotate { origin, end, angle }, vec![shape.index], bounds)
    }

    /// Mirror across a principal plane through the origin: 0 is YZ, 1 is XZ, 2 is XY.
    pub fn mirror(&mut self, shape: Shape, axis: usize) -> Shape {
        let bounds = shape.bounds.map(|mut b| {
            let (lo, hi) = (b[2 * axis], b[2 * axis + 1]);
            b[2 * axis] = -hi;
            b[2 * axis + 1] = -lo;
            b
        });
        self.add(Op::Mirror(axis), vec![shape.index], bounds)
    }

    pub fn placed(
        &mut self,
        shape: Shape,
        rotation: [P3; 3],
        translation: P3,
        bounds: Option<Bounds>,
    ) -> Shape {
        self.add(
            Op::Placed {
                rotation,
                translation,
            },
            vec![shape.index],
            bounds,
        )
    }

    /// The nodes reachable from the result (and the extras), renumbered in graph order.
    pub fn document(&self, result: Shape, extras: &[(&str, Shape)]) -> Value {
        let mut reachable = vec![false; self.nodes.len()];
        let mut stack = vec![result.index];
        stack.extend(extras.iter().map(|(_, s)| s.index));
        while let Some(i) = stack.pop() {
            if !reachable[i] {
                reachable[i] = true;
                stack.extend(&self.nodes[i].inputs);
            }
        }
        let order: Vec<usize> = (0..self.nodes.len()).filter(|&i| reachable[i]).collect();
        let mut remap = vec![usize::MAX; self.nodes.len()];
        for (new, &old) in order.iter().enumerate() {
            remap[old] = new;
        }
        let nodes: Vec<Value> = order
            .iter()
            .map(|&i| {
                let node = &self.nodes[i];
                let mut row = op_json(&node.op);
                row.insert(
                    "inputs".into(),
                    json!(node.inputs.iter().map(|&k| remap[k]).collect::<Vec<_>>()),
                );
                Value::Object(row)
            })
            .collect();
        let mut out = json!({"nodes": nodes, "result": remap[result.index]});
        if !extras.is_empty() {
            out["extras"] = Value::Object(
                extras
                    .iter()
                    .map(|(k, s)| (k.to_string(), json!(remap[s.index])))
                    .collect(),
            );
        }
        out
    }
}

pub fn rotate_point(p: P3, origin: P3, end: P3, angle: f64) -> P3 {
    let axis = [end[0] - origin[0], end[1] - origin[1], end[2] - origin[2]];
    let length = (axis[0] * axis[0] + axis[1] * axis[1] + axis[2] * axis[2]).sqrt();
    let axis = axis.map(|a| a / length);
    let (c, s) = (angle.to_radians().cos(), angle.to_radians().sin());
    let q = [p[0] - origin[0], p[1] - origin[1], p[2] - origin[2]];
    let cross = [
        axis[1] * q[2] - axis[2] * q[1],
        axis[2] * q[0] - axis[0] * q[2],
        axis[0] * q[1] - axis[1] * q[0],
    ];
    let dot = axis[0] * q[0] + axis[1] * q[1] + axis[2] * q[2];
    std::array::from_fn(|k| origin[k] + c * q[k] + s * cross[k] + (1.0 - c) * dot * axis[k])
}

pub(crate) fn op_json(op: &Op) -> Map<String, Value> {
    let (name, fields) = match op {
        Op::Empty => ("empty", json!({})),
        Op::Silhouette => ("silhouette", json!({})),
        Op::SeamBand {
            outer,
            centre,
            exterior,
        } => (
            "seam-band",
            json!({"outer":outer,"centre":centre,"exterior":exterior}),
        ),
        Op::Checkpoint(name) => ("checkpoint", json!({"name":name})),
        Op::Box(b) => ("box", json!({"box": b})),
        Op::RoundedBox { b, radius } => ("rounded-box", json!({"box": b, "radius": radius})),
        Op::Cylinder {
            axis,
            radius,
            centre,
            span,
            stations,
        } => {
            let mut v = json!({"axis": axis, "radius": radius, "centre": centre, "span": span});
            if let Some(s) = stations {
                v["stations"] = json!(s);
            }
            ("cylinder", v)
        }
        Op::Cone {
            axis,
            centre,
            radii,
            span,
        } => (
            "cone",
            json!({"axis": axis, "centre": centre, "radii": radii, "span": span}),
        ),
        Op::Prism {
            axis,
            span,
            section,
        } => (
            "prism",
            json!({"axis": axis, "span": span, "section": section}),
        ),
        Op::CornerPrism {
            axis,
            span,
            section,
            corners,
            radius,
            offset,
        } => {
            let mut v = json!({"axis": axis, "span": span, "section": section, "corners": corners, "radius": radius});
            if let Some(o) = offset {
                v["offset"] = json!(o);
            }
            ("corner-prism", v)
        }
        Op::HandholdCutter { b, radius } => {
            ("handhold-cutter", json!({"box": b, "radius": radius}))
        }
        Op::HandholdFinishAir(h) => (
            "handhold-finish-air",
            json!({
            "bed": h.bed, "roof": h.roof, "crown": h.crown, "y": h.y, "depth": h.depth, "corner": h.corner,
            "radius": h.radius, "end_stock": h.end_stock, "cutter_depth": h.cutter_depth, "slope": h.slope}),
        ),
        Op::FlankVentCuts(v) => (
            "flank-vents",
            json!({
            "columns": v.columns.iter().map(|c| json!({"cutters": c.cutters, "probe": c.probe, "side": c.side})).collect::<Vec<_>>(),
            "courses": v.courses, "clearance": v.clearance, "tolerance": v.tolerance, "island_min": v.island_min}),
        ),
        Op::BezierPrism {
            axis,
            span,
            segments,
        } => (
            "bezier-prism",
            json!({"axis": axis, "span": span,
            "segments": segments.iter().map(|s| match s {
                Seg::Line(a, b) => json!({"line": [a, b]}),
                Seg::Cubic(a, b, c, d) => json!({"cubic": [a, b, c, d]}),
            }).collect::<Vec<_>>()}),
        ),
        Op::ArcPrism {
            axis,
            span,
            start,
            segments,
        } => (
            "arc-prism",
            json!({"axis": axis, "span": span, "start": start,
            "segments": segments.iter().map(|s| match s {
                Step::Arc(m, e) => json!({"arc": [m, e]}),
                Step::Line(p) => json!({"line": p}),
            }).collect::<Vec<_>>()}),
        ),
        Op::RuledStack { sections, source } => (
            "ruled-stack",
            json!({"sections": sections,
            "source": {"path": source.file(), "line": source.line()}}),
        ),
        Op::InletFlange(f) => (
            "inlet-flange",
            json!({"clearance": f.clearance, "span": f.span, "landmarks": {
            "shoulder": f.shoulder, "round_mid": f.round_mid, "tangent_start": f.tangent_start,
            "ear_tangent": f.ear_tangent, "nose": f.nose, "taper_angle_deg": f.taper_angle_deg}}),
        ),
        Op::TurnedRuns { centre, profile } => {
            ("turned-runs", json!({"centre": centre, "profile": profile}))
        }
        Op::RadialProfile { points } => ("radial-profile", json!({"points": points})),
        Op::StadiumX {
            y,
            z,
            radius,
            fore,
            aft,
            span,
        } => (
            "stadium-x",
            json!({"y": y, "z": z, "radius": radius, "fore": fore, "aft": aft, "span": span}),
        ),
        Op::StadiumProfileX {
            y,
            z,
            fore,
            aft,
            points,
        } => (
            "stadium-profile-x",
            json!({"y": y, "z": z, "fore": fore, "aft": aft, "points": points}),
        ),
        Op::NameplateStock(s) => ("nameplate-stock", json!({"snap": snap_json(s)})),
        Op::NameplateCuts(s) => ("nameplate-cuts", json!({"snap": snap_json(s)})),
        Op::DisposalLetters(l) => (
            "disposal-letters",
            json!({"outer": l.outer, "lines": l.lines, "family": l.family,
            "artwork": l.artwork.source, "cap_height": l.cap_height, "depth": l.depth, "embed": l.embed,
            "line_gap": l.line_gap, "bottom": l.bottom}),
        ),
        Op::Union => ("union", json!({})),
        Op::Cut => ("cut", json!({})),
        Op::Intersect => ("intersect", json!({})),
        Op::Translate(d) => ("translate", json!({"delta": d})),
        Op::Rotate { origin, end, angle } => (
            "rotate",
            json!({"origin": origin, "end": end, "angle": angle}),
        ),
        Op::Mirror(axis) => ("mirror", json!({"axis": axis})),
        Op::Placed {
            rotation,
            translation,
        } => (
            "placed",
            json!({"frame": {"rotation": rotation, "translation_mm": translation}}),
        ),
    };
    let mut row = match fields {
        Value::Object(m) => m,
        _ => unreachable!(),
    };
    row.insert("op".into(), json!(name));
    row
}

pub fn snap_json(s: &Snap) -> Value {
    json!({"width": s.width, "height": s.height, "thick": s.thick, "corner": s.corner, "slip": s.slip,
        "supported": s.supported, "frame_width": s.frame_width, "frame_bottom": s.frame_bottom,
        "frame_top": s.frame_top, "frame_corner": s.frame_corner, "floor_rear": s.floor_rear,
        "floor_stock": s.floor_stock, "insert_stock_rear": s.insert_stock_rear,
        "insert_stock_radius": s.insert_stock_radius, "field_proud": s.field_proud, "crown_y": s.crown_y,
        "mouth_width": s.mouth_width, "mouth_height": s.mouth_height, "stations": s.stations,
        "clearance_diameter": s.clearance_diameter, "counterbore_diameter": s.counterbore_diameter,
        "counterbore_depth": s.counterbore_depth, "screw_length": s.screw_length,
        "screw_diameter": s.screw_diameter, "head_diameter": s.head_diameter, "head_height": s.head_height,
        "hex_key": s.hex_key, "insert_diameter": s.insert_diameter, "insert_length": s.insert_length,
        "pilot_diameter": s.pilot_diameter, "pilot_rear": s.pilot_rear})
}
