//! Board datums, fab-model bounds and the shared heat-set tray recipe.
use crate::{num, opt};
use anyhow::{Context, Result, bail};
use serde_json::{Value, json};
use std::fs;

const FLOOR: f64 = 3.0;
const MARGIN: f64 = 8.0;
const STANDOFF: f64 = 5.0;
const OUTLINE_X: [f64; 2] = [-68.0, 17.0];
const OUTLINE_Y: [f64; 2] = [-36.3, 36.5];
const HOLES: [[f64; 2]; 4] = [[-64.5, 33.0], [13.5, 33.0], [13.5, -33.3], [-64.5, -33.3]];
const THICK: f64 = 1.6;
const HOLE_D: f64 = 3.2;
const PIN_DROP: f64 = 2.0;
const HOLE_REACH: f64 = 8.0;
const JOINTS: [(&str, [f64; 2], f64); 6] = [
    ("J1.1", [11.0, 26.48], 1.6),
    ("J8.4", [5.05, 31.0], 1.5),
    ("J7.1", [7.0, -30.3], 1.8),
    ("J11.1", [-62.0, -27.6], 1.5),
    ("J11.2", [-62.0, -25.1], 1.5),
    ("J3.4", [-56.0, -30.3], 1.5),
];

fn pair(v: &Value) -> Result<[f64; 2]> {
    Ok([
        v[0].as_f64().context("Missing X coordinate")?,
        v[1].as_f64().context("Missing Y coordinate")?,
    ])
}
fn width() -> f64 {
    OUTLINE_X[1] - OUTLINE_X[0]
}
fn depth() -> f64 {
    OUTLINE_Y[1] - OUTLINE_Y[0]
}
fn center() -> [f64; 2] {
    [
        (OUTLINE_X[0] + OUTLINE_X[1]) / 2.0,
        (OUTLINE_Y[0] + OUTLINE_Y[1]) / 2.0,
    ]
}
fn rotate(p: [f64; 2], degrees: f64) -> [f64; 2] {
    let r = degrees.to_radians();
    let (c, s) = (r.cos(), r.sin());
    [p[0] * c - p[1] * s, p[0] * s + p[1] * c]
}
fn corners(c: [f64; 2], w: f64, d: f64, r: f64) -> Vec<[f64; 2]> {
    [
        [-w / 2.0, -d / 2.0],
        [w / 2.0, -d / 2.0],
        [w / 2.0, d / 2.0],
        [-w / 2.0, d / 2.0],
    ]
    .into_iter()
    .map(|p| {
        let p = rotate(p, r);
        [c[0] + p[0], c[1] + p[1]]
    })
    .collect()
}
fn hull(mut points: Vec<[f64; 2]>) -> Vec<[f64; 2]> {
    points.sort_by(|a, b| a[0].total_cmp(&b[0]).then(a[1].total_cmp(&b[1])));
    points.dedup_by(|a, b| a[0] == b[0] && a[1] == b[1]);
    if points.len() <= 2 {
        return points;
    }
    fn cross(o: [f64; 2], a: [f64; 2], b: [f64; 2]) -> f64 {
        (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    }
    let mut lower: Vec<[f64; 2]> = vec![];
    for &p in &points {
        while lower.len() >= 2 && cross(lower[lower.len() - 2], lower[lower.len() - 1], p) <= 0.0 {
            lower.pop();
        }
        lower.push(p);
    }
    let mut upper: Vec<[f64; 2]> = vec![];
    for &p in points.iter().rev() {
        while upper.len() >= 2 && cross(upper[upper.len() - 2], upper[upper.len() - 1], p) <= 0.0 {
            upper.pop();
        }
        upper.push(p);
    }
    lower.pop();
    upper.pop();
    lower.extend(upper);
    lower
}
fn boss(d: f64) -> [f64; 3] {
    if d <= 2.6 {
        [5.8, 3.2, 5.0]
    } else {
        [7.2, 4.0, 5.0]
    }
}
fn posts(v: &Value) -> Result<Vec<[f64; 2]>> {
    let c = pair(&v["center"])?;
    let r = opt(v, "rotation", 0.0);
    v["holes"]
        .as_array()
        .context("Missing mounting holes")?
        .iter()
        .map(|p| {
            let p = rotate(pair(p)?, r);
            Ok([c[0] + p[0], c[1] + p[1]])
        })
        .collect()
}
fn module(v: &Value) -> Result<Value> {
    match v["method"].as_str().unwrap_or("state") {
        "rot" => Ok(json!(rotate(
            [num(v, "dx")?, num(v, "dy")?],
            num(v, "degrees")?
        ))),
        "corners" => Ok(json!(corners(
            pair(&v["center"])?,
            num(v, "width")?,
            num(v, "depth")?,
            num(v, "degrees")?
        ))),
        "hull" => Ok(json!(hull(
            v["points"]
                .as_array()
                .context("Missing hull points")?
                .iter()
                .map(pair)
                .collect::<Result<_>>()?
        ))),
        "boss" => Ok(json!(boss(num(v, "hole_dia")?))),
        "posts" => Ok(json!(posts(v)?)),
        _ => Ok(json!({"floor_t":FLOOR,"margin":MARGIN,"board_standoff":STANDOFF})),
    }
}

fn boxes(v: &Value) -> Result<Vec<[f64; 6]>> {
    let path = v["glb"]
        .as_str()
        .context("Missing populated-board GLB path")?;
    let raw = fs::read(path).with_context(|| format!("Reading {path}"))?;
    if raw.len() < 20 || &raw[..4] != b"glTF" {
        bail!("not a GLB")
    }
    let n = u32::from_le_bytes(raw[12..16].try_into()?) as usize;
    let doc: Value =
        serde_json::from_slice(raw.get(20..20 + n).context("Truncated GLB JSON chunk")?)?;
    let accessors = doc["accessors"]
        .as_array()
        .context("Missing GLB accessors")?;
    let meshes = doc["meshes"].as_array().context("Missing GLB meshes")?;
    let mut boxes = vec![];
    for node in doc["nodes"].as_array().map(Vec::as_slice).unwrap_or(&[]) {
        let Some(mesh) = node["mesh"].as_u64() else {
            continue;
        };
        let t = crate::point(node.get("translation").unwrap_or(&json!([0.0, 0.0, 0.0])))?;
        let s = crate::point(node.get("scale").unwrap_or(&json!([1.0, 1.0, 1.0])))?;
        let r = node.get("rotation");
        let mut lo = [f64::INFINITY; 3];
        let mut hi = [f64::NEG_INFINITY; 3];
        for primitive in meshes.get(mesh as usize).context("Missing GLB mesh")?["primitives"]
            .as_array()
            .context("Missing GLB primitives")?
        {
            let index = primitive["attributes"]["POSITION"]
                .as_u64()
                .context("Missing position accessor")? as usize;
            let a = accessors.get(index).context("Missing position bounds")?;
            let mn = crate::point(&a["min"])?;
            let mx = crate::point(&a["max"])?;
            for corner in 0..8 {
                let mut p = std::array::from_fn::<_, 3, _>(|i| {
                    if (corner >> i) & 1 != 0 {
                        mn[i] * s[i]
                    } else {
                        mx[i] * s[i]
                    }
                });
                if let Some(r) = r {
                    let q: Vec<f64> = r
                        .as_array()
                        .context("GLB quaternion")?
                        .iter()
                        .map(|v| v.as_f64().context("GLB quaternion number"))
                        .collect::<Result<_>>()?;
                    if q.len() != 4 {
                        bail!("GLB rotation needs four quaternion coordinates")
                    }
                    let [x, y, z] = p;
                    let (qx, qy, qz, qw) = (q[0], q[1], q[2], q[3]);
                    p = [
                        x * (1.0 - 2.0 * (qy * qy + qz * qz))
                            + y * 2.0 * (qx * qy - qz * qw)
                            + z * 2.0 * (qx * qz + qy * qw),
                        x * 2.0 * (qx * qy + qz * qw)
                            + y * (1.0 - 2.0 * (qx * qx + qz * qz))
                            + z * 2.0 * (qy * qz - qx * qw),
                        x * 2.0 * (qx * qz - qy * qw)
                            + y * 2.0 * (qy * qz + qx * qw)
                            + z * (1.0 - 2.0 * (qx * qx + qy * qy)),
                    ];
                }
                for i in 0..3 {
                    let p = p[i] + t[i];
                    lo[i] = lo[i].min(p);
                    hi[i] = hi[i].max(p);
                }
            }
        }
        boxes.push([
            1000.0 * lo[0],
            1000.0 * hi[0],
            1000.0 * lo[1],
            1000.0 * hi[1],
            1000.0 * lo[2],
            1000.0 * hi[2],
        ]);
    }
    Ok(boxes)
}
type Stock = Vec<([f64; 3], [f64; 3])>;
fn stock(v: &Value) -> Result<(Stock, Stock)> {
    let c = center();
    let (mut above, mut below) = (vec![], vec![]);
    let glb_top = 0.7;
    for [x0, x1, y0, y1, z0, z1] in boxes(v)? {
        let (w, d) = (x1 - x0, y1 - y0);
        if w < 0.2 || d < 0.2 || z1 - z0 < 0.2 {
            continue;
        }
        if w > width() * 0.95 && d > depth() * 0.95 {
            continue;
        }
        if z1 > glb_top + 0.05 {
            above.push(([x0 - c[0], y0 - c[1], THICK], [w, d, z1 - glb_top]));
        }
        if z0 < -glb_top - 0.05 {
            let zb = (-PIN_DROP).max(z0 + glb_top);
            below.push(([x0 - c[0], y0 - c[1], zb], [w, d, -zb]));
        }
    }
    Ok((above, below))
}
fn board_state() -> Result<Value> {
    let c = center();
    let holes = HOLES.map(|p| [p[0] - c[0], p[1] - c[1]]);
    let joints: Vec<_> = JOINTS
        .iter()
        .map(|(_, p, d)| [p[0] - c[0], p[1] - c[1], d / 2.0])
        .collect();
    Ok(
        json!({"values":{"_outline_x":OUTLINE_X,"_outline_y":OUTLINE_Y,"_holes_pcb":HOLES,
        "_centre":c,"_thickness":THICK,"_hole_dia":HOLE_D,"pin_drop":PIN_DROP,
        "_hole_reach":HOLE_REACH,"_hole_joints":JOINTS},
        "board":{"name":"pcba","length":width(),"width":depth(),"holes":holes,"joints":joints,
            "hole_dia":HOLE_D,"pin_drop":PIN_DROP},
        "variables":{"PCBA_SIZE":format!("{} × {} mm",hsm_documents::format_number(width(),".4g")?,hsm_documents::format_number(depth(),".4g")?)}}),
    )
}
fn assembly(v: &Value) -> Result<Value> {
    let (above, below) = stock(v)?;
    let c = center();
    let bores = HOLES.map(|p| [p[0] - c[0], p[1] - c[1], -0.5, HOLE_D / 2.0, THICK + 1.0]);
    let tail_keepouts = HOLES.map(|p| {
        (
            [
                p[0] - c[0] - HOLE_REACH,
                p[1] - c[1] - HOLE_REACH,
                -PIN_DROP - 0.5,
            ],
            [2.0 * HOLE_REACH, 2.0 * HOLE_REACH, PIN_DROP + 1.0],
        )
    });
    let joints: Vec<_> = JOINTS
        .iter()
        .map(|(_, p, d)| [p[0] - c[0], p[1] - c[1], -PIN_DROP, d / 2.0, PIN_DROP])
        .collect();
    let board = json!({"slab":[[-width()/2.0,-depth()/2.0,0.0],[width(),depth(),THICK]],"bores":bores,
        "above":above,"below":below,"tail_keepouts":tail_keepouts,"joints":joints,"pin_drop":PIN_DROP});
    let mut points = vec![];
    let mut bosses = vec![];
    let mut mounts = vec![];
    for (i, m) in v["mounts"]
        .as_array()
        .context("Missing tray mounts")?
        .iter()
        .enumerate()
    {
        let c = pair(&m["center"])?;
        let r = opt(m, "rotation", 0.0);
        points.extend(corners(c, num(m, "length")?, num(m, "width")?, r));
        let [boss_d, bore_d, depth] = boss(opt(m, "hole_dia", 3.2));
        let radius = boss_d / 2.0;
        for [px, py] in posts(m)? {
            points.extend([
                [px - radius, py - radius],
                [px + radius, py - radius],
                [px + radius, py + radius],
                [px - radius, py + radius],
            ]);
            bosses.push(json!({"stock":[px,py,FLOOR,radius,STANDOFF],
                "bore":[px,py,FLOOR+STANDOFF-depth,bore_d/2.0,depth+1.0]}));
        }
        mounts.push(
            json!({"name":format!("{}{i}",m["name"].as_str().context("Missing board name")?),
            "rotation":r,"translation":[c[0],c[1],FLOOR+STANDOFF]}),
        );
    }
    Ok(
        json!({"board":board,"tray":{"hull":hull(points),"floor_t":FLOOR,"bosses":bosses},
        "mounts":mounts,"board_color":v["board_color"],"tray_color":v["tray_color"]}),
    )
}

pub(super) fn request(v: &Value) -> Result<Value> {
    match v["part"].as_str().unwrap_or("") {
        "module-tray" => module(v),
        "pcba-assembly" => assembly(v),
        _ => match v["method"].as_str().unwrap_or("state") {
            "boxes" => Ok(json!(boxes(v)?)),
            "stock" => Ok(json!(stock(v)?)),
            "port" => {
                let c = center();
                Ok(json!([
                    [num(v, "px")? - c[0], num(v, "py")? - c[1], THICK],
                    [0.0, 0.0, 1.0]
                ]))
            }
            _ => board_state(),
        },
    }
}
