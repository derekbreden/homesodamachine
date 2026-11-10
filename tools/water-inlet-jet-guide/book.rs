//! The jet shop book combines authored operations with the issued jaw meshes and owning dimensions.
use crate::paper::{Drawing, Point};
use anyhow::{Result, ensure};
use hsm_cold_core_data::{JET_CAP_LIMITS as LIMITS, jet};
use hsm_water_inlet_jet_fixture_numbers as fixture;
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::path::Path;

const BLUE: &str = "#1749D1";
const INK: &str = "#202337";
const ICE: &str = "#EAF0FC";
const PAPER: &str = "#FCFCFA";
const STEEL: &str = "#E4E8EE";
const LIGHT_STEEL: &str = "#F1F4F7";
const ORANGE: &str = "#E95A2C";
type V3 = [f64; 3];
fn sub(a: V3, b: V3) -> V3 {
    std::array::from_fn(|i| a[i] - b[i])
}
fn dot(a: V3, b: V3) -> f64 {
    (0..3).map(|i| a[i] * b[i]).sum()
}
fn cross(a: V3, b: V3) -> V3 {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
fn unit(a: V3) -> V3 {
    let len = dot(a, a).sqrt();
    a.map(|v| v / len)
}

struct Mesh {
    vertices: Vec<V3>,
    faces: Vec<[usize; 3]>,
}
impl Mesh {
    fn read(path: &Path) -> Result<Self> {
        let bytes = std::fs::read(path)?;
        ensure!(bytes.len() >= 84, "truncated jaw STL");
        let count = u32::from_le_bytes(bytes[80..84].try_into()?) as usize;
        ensure!(bytes.len() == 84 + count * 50, "binary jaw STL length");
        let mut vertices = Vec::new();
        let mut faces = Vec::new();
        let mut index = BTreeMap::new();
        for face in bytes[84..].chunks_exact(50) {
            let mut triangle = [0; 3];
            for (corner, point) in face[12..48].chunks_exact(12).enumerate() {
                let key = std::array::from_fn::<_, 3, _>(|i| {
                    u32::from_le_bytes(point[i * 4..i * 4 + 4].try_into().unwrap())
                });
                triangle[corner] = *index.entry(key).or_insert_with(|| {
                    let i = vertices.len();
                    vertices.push(key.map(|v| f32::from_bits(v) as f64));
                    i
                });
            }
            faces.push(triangle);
        }
        Ok(Self { vertices, faces })
    }
    fn move_by(mut self, offset: V3, flip: bool) -> Self {
        for p in &mut self.vertices {
            for i in 0..3 {
                p[i] = p[i] * if flip && i < 2 { -1. } else { 1. } + offset[i];
            }
        }
        self
    }
    fn rod() -> Self {
        let sides = 48;
        let radius = jet::CAP_DIAMETER / 2.;
        let cy = fixture::GROOVE_RADIUS - radius;
        let mut vertices = Vec::new();
        let mut faces = Vec::new();
        for z in [fixture::BASE[2], fixture::BASE[2] + fixture::HANDLING_BLANK] {
            for i in 0..sides {
                let angle = i as f64 * std::f64::consts::TAU / sides as f64;
                vertices.push([radius * angle.cos(), cy + radius * angle.sin(), z]);
            }
        }
        vertices.push([0., cy, fixture::BASE[2]]);
        vertices.push([0., cy, fixture::BASE[2] + fixture::HANDLING_BLANK]);
        for i in 0..sides {
            let j = (i + 1) % sides;
            faces.extend([
                [i, j, j + sides],
                [i, j + sides, i + sides],
                [sides * 2, j, i],
                [sides * 2 + 1, i + sides, j + sides],
            ]);
        }
        Self { vertices, faces }
    }
}
#[derive(Clone, Copy)]
struct Iso {
    origin: [f64; 2],
    sx: f64,
    sy: f64,
    dx: f64,
    dy: f64,
    sz: f64,
}
impl Iso {
    fn p(self, p: V3) -> [f64; 2] {
        [
            self.origin[0] + self.sx * p[0] + self.sy * p[1],
            self.origin[1] + self.dx * p[0] + self.dy * p[1] - self.sz * p[2],
        ]
    }
}
fn line(out: &mut Vec<Drawing>, start: [f64; 2], end: [f64; 2], color: &str, width: f64) {
    out.push(Drawing::Line {
        start,
        end,
        color: color.into(),
        width,
        dash: vec![],
    });
}
fn arrow(out: &mut Vec<Drawing>, start: [f64; 2], end: [f64; 2], color: &str, width: f64) {
    out.push(Drawing::Arrow {
        start,
        end,
        color: color.into(),
        width,
        head: 6.,
    });
}
fn label(out: &mut Vec<Drawing>, value: &str, x: f64, y: f64, size: f64, align: &str) {
    out.push(Drawing::Label {
        value: value.into(),
        x,
        y,
        size,
        color: BLUE.into(),
        font: "PlexSemi".into(),
        align: align.into(),
    });
}
fn shape(
    out: &mut Vec<Drawing>,
    points: Vec<[f64; 2]>,
    fill: Option<&str>,
    stroke: Option<&str>,
    width: f64,
    close: bool,
) {
    out.push(Drawing::Shape {
        points: points.into_iter().map(Point::At).collect(),
        fill: fill.map(String::from),
        stroke: stroke.map(String::from),
        width,
        close,
    });
}
fn ellipse(out: &mut Vec<Drawing>, x: f64, y: f64, r: f64, fill: &str, width: f64) {
    out.push(Drawing::Ellipse {
        x: x - r,
        y: y - r,
        width: 2. * r,
        height: 2. * r,
        fill: Some(fill.into()),
        stroke: Some(INK.into()),
        line_width: width,
    });
}
fn paint(out: &mut Vec<Drawing>, iso: Iso, items: Vec<(Mesh, &str)>) {
    let view = unit(cross([iso.sx, iso.sy, 0.], [iso.dx, iso.dy, -iso.sz]).map(|v| -v));
    let light = unit([-0.15, -0.4, 1.]);
    let mut faces = Vec::new();
    for (mesh, fill) in items {
        let normals: Vec<_> = mesh
            .faces
            .iter()
            .map(|f| {
                unit(cross(
                    sub(mesh.vertices[f[1]], mesh.vertices[f[0]]),
                    sub(mesh.vertices[f[2]], mesh.vertices[f[0]]),
                ))
            })
            .collect();
        let visible: Vec<_> = normals.iter().map(|n| dot(*n, view) > 1e-8).collect();
        let mut adjacent: BTreeMap<(usize, usize), Vec<usize>> = BTreeMap::new();
        for (i, face) in mesh.faces.iter().enumerate() {
            for e in 0..3 {
                let (a, b) = (face[e], face[(e + 1) % 3]);
                adjacent.entry((a.min(b), a.max(b))).or_default().push(i);
            }
        }
        for (i, face) in mesh.faces.iter().enumerate().filter(|(i, _)| visible[*i]) {
            let xyz = face.map(|n| mesh.vertices[n]);
            let normal = normals[i];
            let gain = 0.76 + 0.24 * dot(normal, light).max(0.);
            let color = format!(
                "#{:02x}{:02x}{:02x}",
                (u8::from_str_radix(&fill[1..3], 16).unwrap() as f64 * gain).round_ties_even()
                    as u8,
                (u8::from_str_radix(&fill[3..5], 16).unwrap() as f64 * gain).round_ties_even()
                    as u8,
                (u8::from_str_radix(&fill[5..7], 16).unwrap() as f64 * gain).round_ties_even()
                    as u8
            );
            let mut edges = Vec::new();
            for e in 0..3 {
                let (a, b) = (face[e], face[(e + 1) % 3]);
                let pair = &adjacent[&(a.min(b), a.max(b))];
                if pair.len() != 2 || dot(normals[pair[0]], normals[pair[1]]) <= 0.94 {
                    edges.push((iso.p(mesh.vertices[a]), iso.p(mesh.vertices[b])));
                }
            }
            let depth = dot(
                std::array::from_fn(|k| xyz.iter().map(|p| p[k]).sum::<f64>() / 3.),
                view,
            );
            faces.push((depth, xyz.map(|p| iso.p(p)), color, edges));
        }
    }
    faces.sort_by(|a, b| a.0.total_cmp(&b.0));
    for (_, points, color, edges) in faces {
        shape(out, points.to_vec(), Some(&color), Some(&color), 0.15, true);
        for (start, end) in edges {
            line(out, start, end, INK, 0.75);
        }
    }
}
fn jaw(root: &Path, name: &str) -> Result<Mesh> {
    Mesh::read(&root.join(format!(
        "hardware/printed-parts/fixtures/water-inlet-jet/water-inlet-jet-fixture-{name}.stl"
    )))
}
fn print_parts(root: &Path) -> Result<Vec<Drawing>> {
    let mut out = vec![];
    label(&mut out, "1  FIXED JAW + BASE", 137., 22., 12., "center");
    label(&mut out, "2  LOOSE JAW", 415., 22., 12., "center");
    let left = Iso {
        origin: [139., 254.],
        sx: 1.55,
        sy: 0.7,
        dx: 0.43,
        dy: -0.36,
        sz: 2.,
    };
    let right = Iso {
        origin: [409., 239.],
        sx: 2.15,
        sy: 0.9,
        dx: 0.54,
        dy: -0.43,
        sz: 2.7,
    };
    paint(&mut out, left, vec![(jaw(root, "fixed")?, STEEL)]);
    paint(
        &mut out,
        right,
        vec![(jaw(root, "loose")?.move_by([0.; 3], true), ICE)],
    );
    label(&mut out, "half-round groove", 16., 65., 11., "left");
    arrow(&mut out, [119., 72.], left.p([0., 4.9, 28.]), BLUE, 1.);
    label(&mut out, "matching groove", 333., 64., 11., "left");
    arrow(&mut out, [433., 71.], right.p([0., 4.9, 23.]), BLUE, 1.);
    label(&mut out, "base stays attached", 138., 316., 11., "center");
    label(
        &mut out,
        "shown from groove side",
        415.,
        291.,
        10.5,
        "center",
    );
    label(
        &mut out,
        "flat bottom on print bed",
        270.,
        349.,
        11.,
        "center",
    );
    Ok(out)
}
fn load_jaws(root: &Path) -> Result<Vec<Drawing>> {
    let mut out = vec![];
    let i = Iso {
        origin: [300., 253.],
        sx: 2.,
        sy: 0.9,
        dx: 0.56,
        dy: -0.48,
        sz: 2.8,
    };
    let slip = fixture::GROOVE_RADIUS - jet::CAP_DIAMETER / 2.;
    paint(
        &mut out,
        i,
        vec![
            (jaw(root, "fixed")?, STEEL),
            (
                jaw(root, "loose")?.move_by([-65., -35., fixture::BASE[2]], false),
                ICE,
            ),
            (Mesh::rod(), LIGHT_STEEL),
        ],
    );
    arrow(&mut out, [230., 247.], [276., 255.], ORANGE, 2.);
    label(&mut out, "seat rod on the floor", 16., 40., 12., "left");
    arrow(
        &mut out,
        [154., 48.],
        i.p([-jet::CAP_DIAMETER / 2. - 0.25, slip, fixture::BASE[2]]),
        BLUE,
        1.,
    );
    label(&mut out, "fixed jaw stays on base", 300., 35., 11., "left");
    arrow(&mut out, [411., 43.], i.p([26., 17., 38.]), BLUE, 1.);
    label(&mut out, "set loose jaw on base", 15., 335., 11., "left");
    arrow(&mut out, [162., 323.], i.p([-85., -48., 29.]), BLUE, 1.);
    label(
        &mut out,
        "grooves face one another",
        335.,
        338.,
        11.,
        "center",
    );
    Ok(out)
}
fn jaw_plan() -> Vec<Drawing> {
    let mut out = vec![];
    let gap = fixture::GAP;
    let closure = 2. * fixture::GROOVE_RADIUS - jet::CAP_DIAMETER;
    let half = fixture::JAW[0] / 2.;
    let depth = fixture::JAW[1];
    let front = -gap / 2. - depth + closure;
    let back = -gap / 2. + closure;
    let p = |x: f64, y: f64| [270. + 2.5 * x, 169. - 2.5 * y];
    for (x0, x1, y0, y1, fill) in [
        (
            -fixture::BASE[0] / 2.,
            fixture::BASE[0] / 2.,
            -fixture::BASE[1] / 2.,
            fixture::BASE[1] / 2.,
            LIGHT_STEEL,
        ),
        (-half, half, gap / 2., gap / 2. + depth, STEEL),
        (-half, half, front, back, ICE),
    ] {
        let [x, y] = p(x0, y1);
        out.push(Drawing::Rect {
            x,
            y,
            width: 2.5 * (x1 - x0),
            height: 2.5 * (y1 - y0),
            fill: Some(fill.into()),
            stroke: Some(INK.into()),
        });
    }
    for (edge, centre, upper) in [(gap / 2., 0., true), (back, closure, false)] {
        let r = fixture::GROOVE_RADIUS;
        let angle = ((edge - centre) / r).asin();
        let (start, end) = if upper {
            (angle, std::f64::consts::PI - angle)
        } else {
            (std::f64::consts::PI - angle, std::f64::consts::TAU + angle)
        };
        let pts = (0..=256)
            .map(|n| {
                let a = start + (end - start) * n as f64 / 256.;
                p(r * a.cos(), centre + r * a.sin())
            })
            .collect();
        shape(&mut out, pts, Some(PAPER), Some(INK), 0.8, true);
    }
    let [x, y] = p(0., fixture::GROOVE_RADIUS - jet::CAP_DIAMETER / 2.);
    ellipse(&mut out, x, y, jet::CAP_DIAMETER * 2.5 / 2., STEEL, 1.);
    for sign in [-1., 1.] {
        let x = sign * fixture::JAW_CLAMP_X;
        let spine = sign * 42.;
        shape(
            &mut out,
            vec![p(x, 27.), p(spine, 27.), p(spine, -36.), p(x, -36.)],
            None,
            Some(BLUE),
            5.,
            false,
        );
        line(&mut out, p(x, -36.), p(x, front), INK, 2.);
        line(&mut out, p(x - 4., front), p(x + 4., front), BLUE, 4.);
        line(&mut out, p(x - 5., -41.), p(x + 5., -41.), INK, 2.);
        line(
            &mut out,
            p(x - 4., gap / 2. + depth),
            p(x + 4., gap / 2. + depth),
            BLUE,
            4.,
        );
        let [x, y] = p(spine, -9.);
        out.push(Drawing::Ellipse {
            x: x - 10.,
            y: y - 10.,
            width: 20.,
            height: 20.,
            fill: Some(BLUE.into()),
            stroke: Some(BLUE.into()),
            line_width: 1.5,
        });
        out.push(Drawing::Label {
            value: "A".into(),
            x,
            y: y + 3.7,
            size: 10.,
            color: PAPER.into(),
            font: "PlexBold".into(),
            align: "center".into(),
        });
    }
    label(&mut out, "TOP VIEW", 270., 25., 12., "center");
    label(&mut out, "fixed jaw / behind rod", 270., 92., 11., "center");
    label(&mut out, "loose jaw / in front", 270., 305., 11., "center");
    label(
        &mut out,
        "C-frames point outward",
        270.,
        347.,
        11.,
        "center",
    );
    out
}

pub fn build(root: &Path, output: Option<&Path>) -> Result<()> {
    let mut source =
        std::fs::read_to_string(root.join("hardware/water-inlet-jet-guide/pages.json"))?;
    for (key, value, spec) in [
        ("fixture_BASE_CLAMP_X_g", fixture::BASE_CLAMP_X, "g"),
        ("fixture_BASE_X_g", fixture::BASE[0], "g"),
        ("fixture_BASE_Y_g", fixture::BASE[1], "g"),
        ("fixture_GRIP_Z_g", fixture::JAW[2], "g"),
        ("fixture_JAW_CLAMP_X_g", fixture::JAW_CLAMP_X, "g"),
        ("jet_JET_CAP_T_p2f", jet::CAP_THICKNESS, ".2f"),
        (
            "limit_HOLE_EDGE_BREAK_MAX_p2f",
            LIMITS.hole_edge_break_max,
            ".2f",
        ),
        ("limit_THICKNESS_TOL_p2f", LIMITS.thickness_tolerance, ".2f"),
    ] {
        source = source.replace(
            &format!("{{{{{key}}}}}"),
            &hsm_documents::format_number(value, spec)?,
        );
    }
    ensure!(!source.contains("{{"), "unresolved jet-guide source value");
    let mut book: Value = serde_json::from_str(&source)?;
    book["drawings"] = json!({"jet-print_parts":print_parts(root)?,"jet-load_jaws":load_jaws(root)?,"jet-jaw_plan":jaw_plan()});
    book["extra"]["geometry_mm"] = json!({"JET_CAP_D":jet::CAP_DIAMETER,"JET_CAP_T":jet::CAP_THICKNESS,"JET_PASSAGE_D":jet::PASSAGE_DIAMETER});
    book["extra"]["finished_limits_mm"] = json!({"OD_TOL":LIMITS.od_tolerance,"THICKNESS_TOL":LIMITS.thickness_tolerance,"BORE_PLUS":LIMITS.bore_plus,"BORE_MINUS":LIMITS.bore_minus,"RADIAL_OFFSET_MAX":LIMITS.radial_offset_max,"AXIS_ANGLE_MAX":LIMITS.axis_angle_max,"FACE_GAP_MAX":LIMITS.face_gap_max,"THICKNESS_VARIATION_MAX":LIMITS.thickness_variation_max,"HOLE_EDGE_BREAK_MAX":LIMITS.hole_edge_break_max});
    book["extra"]["fixture_inputs_mm"] = json!({"BASE_X":fixture::BASE[0],"BASE_Y":fixture::BASE[1],"BASE_T":fixture::BASE[2],"JAW_X":fixture::JAW[0],"JAW_DEPTH":fixture::JAW[1],"GRIP_Z":fixture::JAW[2],"HANDLING_BLANK_L":fixture::HANDLING_BLANK,"MIN_HANDLING_BLANK_L":fixture::MINIMUM_BLANK,"OPEN_JAW_GAP":fixture::GAP,"GROOVE_R":fixture::GROOVE_RADIUS,"JAW_CLAMP_X":fixture::JAW_CLAMP_X,"BASE_CLAMP_X":fixture::BASE_CLAMP_X});
    crate::fixed_book::build(
        root,
        "water-inlet-jet-guide",
        &serde_json::to_string(&book)?,
        output,
    )
}
