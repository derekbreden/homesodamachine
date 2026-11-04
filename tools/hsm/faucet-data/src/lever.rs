//! Scan-derived lever stations and shape-preserving cubic slopes.

use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};

const PRINTED_OUTSIDE_WIDTH: f64 = 12.40;
const CHANNEL_PRINTED_WIDTH: f64 = 9.00;
const FLOOR_Z: f64 = 0.0;
const LEDGE_TOP: f64 = -5.55;
const LOWER_SLOT_HALF_WIDTH: f64 = 1.45;
const CUT_BELOW: f64 = -14.0;
const CUT_ABOVE: f64 = 7.0;
const CUT_FRONT: f64 = -3.0;
const CUT_REAR: f64 = 60.0;
const SHOW_PROFILE: &[[f64; 2]] = &[
    [0.8, 2.95],
    [5.0, 2.84],
    [15.0, 2.74],
    [25.0, 2.77],
    [35.0, 2.94],
    [37.0, 2.97],
    [38.5, 4.08],
    [40.0, 4.43],
    [41.5, 4.05],
    [43.0, 3.13],
    [46.0, 3.00],
    [49.5, 3.04],
    [50.5, 3.00],
];
const REAR_BOTTOM_PROFILE: &[[f64; 2]] = &[[51.0, -7.5], [50.2, -8.85], [49.3, -9.03]];
const RAIL_BOTTOM_PROFILE: &[[f64; 2]] = &[
    [35.0, -5.30],
    [30.0, -4.86],
    [20.0, -3.76],
    [10.0, -2.56],
    [5.0, -1.88],
    [1.1, -0.75],
];
const STOP_TAIL: &[[f64; 2]] = &[
    [3.80, 45.31],
    [3.50, 45.40],
    [3.00, 45.48],
    [2.70, 45.53],
    [2.50, 45.60],
    [2.30, 45.72],
    [2.20, 45.92],
];
const POCKET_START_Y: f64 = 1.2;
const POCKET_FRONT_RADIUS: f64 = 0.5;
const POCKET_STOP_JOIN_Y: f64 = 46.1;
const POCKET_CEILING: &[[f64; 2]] = &[
    [37.0, 0.12],
    [39.0, 0.12],
    [42.0, -0.38],
    [44.0, -0.52],
    [POCKET_STOP_JOIN_Y, -0.55],
];
const LEDGE_LIP_START: [f64; 2] = [36.70, -10.18];
const LEDGE_LIP_MID: [f64; 2] = [37.7, -7.25];
const LEDGE_LIP_END: [f64; 2] = [40.50, LEDGE_TOP];

fn edge_slope(h0: f64, h1: f64, m0: f64, m1: f64) -> f64 {
    let d = ((2.0 * h0 + h1) * m0 - h0 * m1) / (h0 + h1);
    let sign = |x: f64| if x == 0.0 { 0.0 } else { x.signum() };
    if sign(d) != sign(m0) {
        0.0
    } else if sign(m0) != sign(m1) && d.abs() > 3.0 * m0.abs() {
        3.0 * m0
    } else {
        d
    }
}

/// Fritsch-Butland interior harmonic slopes and one-sided shape-preserving
/// endpoint slopes, returned in the author's original station order.
pub fn pchip(points: &[[f64; 2]]) -> Result<Vec<[f64; 3]>> {
    ensure!(points.len() >= 2, "PCHIP needs at least two stations");
    let mut sorted = points.to_vec();
    sorted.sort_by(|a, b| a[0].total_cmp(&b[0]));
    let h: Vec<_> = sorted.windows(2).map(|w| w[1][0] - w[0][0]).collect();
    ensure!(
        h.iter().all(|v| v.is_finite() && *v > 0.0),
        "PCHIP station X must be finite and unique"
    );
    let m: Vec<_> = sorted
        .windows(2)
        .zip(&h)
        .map(|(w, h)| (w[1][1] - w[0][1]) / h)
        .collect();
    let mut slopes = vec![0.0; sorted.len()];
    if sorted.len() == 2 {
        slopes.fill(m[0]);
    } else {
        slopes[0] = edge_slope(h[0], h[1], m[0], m[1]);
        let n = h.len();
        slopes[n] = edge_slope(h[n - 1], h[n - 2], m[n - 1], m[n - 2]);
        for k in 1..n {
            if m[k - 1] == 0.0 || m[k] == 0.0 || m[k - 1].signum() != m[k].signum() {
                continue;
            }
            let w1 = 2.0 * h[k] + h[k - 1];
            let w2 = h[k] + 2.0 * h[k - 1];
            let mean = (w1 / m[k - 1] + w2 / m[k]) / (w1 + w2);
            slopes[k] = 1.0 / mean;
        }
    }
    Ok(points
        .iter()
        .map(|p| {
            let k = sorted
                .iter()
                .position(|q| q[0] == p[0])
                .expect("author station");
            [p[0], p[1], slopes[k]]
        })
        .collect())
}

pub fn pchip_request(request: &Value) -> Result<Value> {
    let points: Vec<[f64; 2]> = request["points"]
        .as_array()
        .context("PCHIP points")?
        .iter()
        .map(|v| {
            Ok([
                v[0].as_f64().context("PCHIP X")?,
                v[1].as_f64().context("PCHIP Y")?,
            ])
        })
        .collect::<Result<_>>()?;
    Ok(json!(pchip(&points)?))
}

/// Restore the lever's authored frame from its side-down printed STL.
/// Corners are read as f32, transformed in f64, and written as f32. The
/// face normals are read from the transformed corners, as the mesh reader does.
pub fn repack(request: &Value) -> Result<Value> {
    let source = std::path::Path::new(request["source"].as_str().context("lever print STL")?);
    let target = std::path::Path::new(request["target"].as_str().context("lever authored STL")?);
    let bytes = std::fs::read(source)?;
    ensure!(bytes.len() >= 84, "lever print STL header");
    let count = u32::from_le_bytes(bytes[80..84].try_into().unwrap()) as usize;
    ensure!(
        bytes.len() == 84 + count * 50,
        "lever print STL facet length"
    );
    let mut output = vec![0; 84 + count * 50];
    output[80..84].copy_from_slice(&(count as u32).to_le_bytes());
    let read = |row: &[u8], i: usize| f32::from_le_bytes(row[i..i + 4].try_into().unwrap()) as f64;
    let write = |row: &mut [u8], i: usize, v: f64| {
        let v = if v == 0.0 { 0.0 } else { v as f32 };
        row[i..i + 4].copy_from_slice(&v.to_le_bytes());
    };
    for (facet, out) in bytes[84..]
        .chunks_exact(50)
        .zip(output[84..].chunks_exact_mut(50))
    {
        let mut points = [[0.0; 3]; 3];
        for i in 0..3 {
            let base = 12 + i * 12;
            points[i] = [
                PRINTED_OUTSIDE_WIDTH / 2.0 - read(facet, base + 8),
                read(facet, base + 4),
                read(facet, base),
            ];
            for value in &mut points[i] {
                if *value == 0.0 {
                    *value = 0.0;
                }
            }
            write(
                out,
                base,
                PRINTED_OUTSIDE_WIDTH / 2.0 - read(facet, base + 8),
            );
            write(out, base + 4, read(facet, base + 4));
            write(out, base + 8, read(facet, base));
        }
        let a = [
            points[1][0] - points[0][0],
            points[1][1] - points[0][1],
            points[1][2] - points[0][2],
        ];
        let b = [
            points[2][0] - points[1][0],
            points[2][1] - points[1][1],
            points[2][2] - points[1][2],
        ];
        let cross = [
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        ];
        let norm = ((cross[0] * cross[0] + cross[1] * cross[1]) + cross[2] * cross[2]).sqrt();
        let normal = if norm > 1e-13 {
            cross.map(|v| v * (1.0 / norm))
        } else {
            [0.0; 3]
        };
        for i in 0..3 {
            out[i * 4..i * 4 + 4].copy_from_slice(&(normal[i] as f32).to_le_bytes());
        }
    }
    hsm_documents::write_if_changed(target, &output)?;
    Ok(json!({"facets":count,"source":source,"target":target}))
}

pub fn data(color: &Value) -> Result<Value> {
    let mut stop = vec![
        [CHANNEL_PRINTED_WIDTH / 2.0, 44.30],
        [4.20, 44.90],
        [4.00, 45.18],
    ];
    stop.extend_from_slice(STOP_TAIL);
    let lower_relief = vec![
        (
            -11.5,
            vec![
                [LOWER_SLOT_HALF_WIDTH, POCKET_START_Y],
                [LOWER_SLOT_HALF_WIDTH, 47.5],
                [2.1, 48.2],
                [4.4, 50.2],
                [5.4, 52.7],
            ],
        ),
        (
            LEDGE_TOP,
            vec![
                [1.65, POCKET_START_Y],
                [1.65, 47.5],
                [2.2, 48.2],
                [4.4, 50.2],
                [5.4, 52.7],
            ],
        ),
        (
            -0.55,
            vec![
                [2.20, POCKET_START_Y],
                [2.20, 47.5],
                [2.6, 48.25],
                [4.4, 50.2],
                [5.4, 52.7],
            ],
        ),
    ];
    let upper_relief = vec![
        (
            -0.56,
            vec![
                [0.25, 47.22],
                [2.2, 48.05],
                [3.5, 49.0],
                [4.4, 50.2],
                [5.4, 52.7],
            ],
        ),
        (
            2.75,
            vec![
                [2.20, 42.65],
                [3.35, 43.1],
                [3.90, 44.5],
                [4.50, 48.0],
                [5.4, 52.7],
            ],
        ),
        (
            5.20,
            vec![
                [5.30, 39.1],
                [5.80, 40.0],
                [6.40, 42.0],
                [7.00, 48.0],
                [8.0, 52.7],
            ],
        ),
    ];
    let lower_numbers: Vec<_> = lower_relief
        .iter()
        .map(|(z, p)| json!({"z":z,"right":p}))
        .collect();
    let upper_numbers: Vec<_> = upper_relief
        .iter()
        .map(|(z, p)| json!({"z":z,"right":p}))
        .collect();
    let mut rail = vec![[36.65, -5.55]];
    rail.extend_from_slice(RAIL_BOTTOM_PROFILE);
    Ok(json!({"datums":{
        "PRINTED_OUTSIDE_WIDTH":PRINTED_OUTSIDE_WIDTH,"CHANNEL_PRINTED_WIDTH":CHANNEL_PRINTED_WIDTH,
        "FLOOR_Z":FLOOR_Z,"LEDGE_TOP":LEDGE_TOP,"LOWER_SLOT_HALF_WIDTH":LOWER_SLOT_HALF_WIDTH,
        "CUT_BELOW":CUT_BELOW,"CUT_ABOVE":CUT_ABOVE,"CUT_FRONT":CUT_FRONT,"CUT_REAR":CUT_REAR,
        "STL_TOLERANCE":0.035,"STL_ANGLE_TOLERANCE":0.12,
        "SHOW_PROFILE":SHOW_PROFILE,"REAR_BOTTOM_PROFILE":REAR_BOTTOM_PROFILE,
        "RAIL_BOTTOM_PROFILE":RAIL_BOTTOM_PROFILE,"STOP_TAIL":STOP_TAIL,
        "PRINTED_STOP_PROFILE":stop,"POCKET_START_Y":POCKET_START_Y,
        "POCKET_FRONT_RADIUS":POCKET_FRONT_RADIUS,"POCKET_STOP_JOIN_Y":POCKET_STOP_JOIN_Y,
        "POCKET_CEILING":POCKET_CEILING,"LEDGE_LIP_START":LEDGE_LIP_START,
        "LEDGE_LIP_MID":LEDGE_LIP_MID,"LEDGE_LIP_END":LEDGE_LIP_END,
        "LOWER_RELIEF":lower_relief,"UPPER_RELIEF":upper_relief},
        "half_outer":PRINTED_OUTSIDE_WIDTH/2.0,"half_channel":CHANNEL_PRINTED_WIDTH/2.0,
        "numbers":{"name":"lever-replica","color":color,
            "outside_width":PRINTED_OUTSIDE_WIDTH,"channel_width":CHANNEL_PRINTED_WIDTH,
            "floor_z":FLOOR_Z,"ledge_top":LEDGE_TOP,"cut_below":CUT_BELOW,"cut_above":CUT_ABOVE,
            "cut_front":CUT_FRONT,"cut_rear":CUT_REAR,"outer_start":[0.0,0.8],
            "tip_arc":[[0.1,2.4],SHOW_PROFILE[0]],"show_pchip":pchip(SHOW_PROFILE)?,
            "rear_arc":[[52.65,0.2],[52.0,-4.0]],"rear_bottom":REAR_BOTTOM_PROFILE,
            "outer_corner":[[37.5,-10.15],[36.8,-10.05],[36.70,-9.5]],
            "rail_start":[36.65,-5.55],"rail_pchip":pchip(&rail)?,"tip_return_mid":[0.35,-0.2],
            "pocket_start":POCKET_START_Y,"pocket_front_radius":POCKET_FRONT_RADIUS,
            "pocket_stop_join":POCKET_STOP_JOIN_Y,"stop_profile":stop,
            "pocket_floor_end":[30.0,FLOOR_Z],"pocket_ceiling":POCKET_CEILING,
            "ledge_lip":[LEDGE_LIP_START,LEDGE_LIP_MID,LEDGE_LIP_END],
            "pocket_lower_corner":[36.0,CUT_BELOW],"lower_relief":lower_numbers,"upper_relief":upper_numbers}}))
}
