use super::*;
use model::{V, add, mul, v};
const PITCH: f64 = 1.85;
const J1: [&str; 7] = [
    "J1-COM", "J1-OUT3", "J1-OUT4", "J1-OUT5", "J1-OUT6", "J1-OUT7", "J1-OUT8",
];
const J2: [&str; 4] = ["J2-OUT1", "J2-OUT2", "J2-FAN", "J2-COM"];
fn p(at: &Value, id: &str) -> Result<V> {
    terminals::point(at, id)
}
fn text<'a>(c: &'a Value, key: &str) -> Result<&'a str> {
    string(&c[key])
}
fn has(value: &Value, key: &str) -> bool {
    value.get(key).is_some()
}
pub fn manifold_site() -> Result<Value> {
    let mut out = hsm_kernel::reads::json("tools/hsm/assembly-docs/src/wiring/manifold-bank.json")?;
    out["target_centers"] = json!({});
    for (x, z, wires) in [
        (
            74.1,
            263.05,
            vec![
                "J1-OUT8", "J1-OUT7", "J1-OUT6", "J1-OUT5", "J1-OUT4", "J1-OUT3", "J1-COM",
            ],
        ),
        (
            79.3,
            260.275,
            vec!["J2-COM", "J2-FAN", "J2-OUT2", "J2-OUT1"],
        ),
    ] {
        for (i, id) in wires.iter().enumerate() {
            out["target_centers"][*id] = json!([
                x,
                192.6,
                z + (i as f64 - (wires.len() as f64 - 1.) / 2.) * PITCH
            ]);
        }
    }
    Ok(out)
}
fn cable_sites() -> Result<Value> {
    hsm_kernel::reads::json("tools/hsm/assembly-docs/src/wiring/cable-sites.json")
}
pub fn pump_internal(at: &Value, x: f64, terminal_x: f64, lane: f64, n: f64) -> Result<Vec<V>> {
    let rear = v(&at["passages"]["front-top-electrical"]["points_mm"][0])?;
    let fore = v(&at["passages"]["front-top-electrical"]["points_mm"][1])?;
    let cross = v(&at["passages"]["front-top-pump-cross"]["points_mm"][1])?;
    Ok(vec![
        [x, rear[1] + 14.5, rear[2] - 2.7 + n * 1.9],
        [x, rear[1] + 5.5, rear[2] - 4.5],
        [x, fore[1] + 22., rear[2] - 4.5],
        [x, cross[1] + 8., cross[2]],
        [x, cross[1] + lane, cross[2]],
        [terminal_x, cross[1] + lane, cross[2]],
    ])
}
pub fn display_internal(at: &Value, n: f64) -> Result<Vec<V>> {
    let x = (n - 1.5) * PITCH;
    let rear = v(&at["passages"]["front-top-electrical"]["points_mm"][0])?;
    let low = v(&at["passages"]["front-top-display-chimney"]["points_mm"][0])?;
    let high = v(&at["passages"]["front-top-display-chimney"]["points_mm"][1])?;
    Ok(vec![
        [x, rear[1], rear[2] + 4.5],
        [x, low[1], rear[2] + 4.5],
        [x, high[1], high[2]],
    ])
}
fn pump_terminal(c: &Value, at: &Value, n: f64) -> Result<Vec<V>> {
    let end = text(c, "end")?;
    let tab = p(at, end)?;
    let bank = end.split('.').next().unwrap();
    let axis = (p(at, &format!("{bank}.1"))?[0] + p(at, &format!("{bank}.2"))?[0]) / 2.;
    let x = (1.5 - n) * PITCH;
    let lane = if tab[0].abs() > axis.abs() {
        PITCH / 2.
    } else {
        -PITCH / 2.
    };
    pump_internal(at, x, tab[0], lane, n)
}
fn pump_lead(c: &Value, at: &Value, n: f64) -> Result<Vec<V>> {
    let p = p(at, text(c, "start")?)?;
    let z = 277.3 + n * 1.9;
    let mut out = vec![[p[0], p[1], z], [-36., 157., z]];
    out.extend(pump_terminal(c, at, n)?);
    Ok(out)
}
fn station_rows(at: &Value, value: &Value) -> Result<Vec<V>> {
    rows(value)?
        .iter()
        .map(|s| terminals::station(at, s))
        .collect()
}
fn guide(
    c: &Value,
    at: &Value,
    groups: &BTreeMap<String, Vec<String>>,
    saved: &Value,
) -> Result<Vec<V>> {
    let (id, harness, start, end) = (
        text(c, "id")?,
        text(c, "harness")?,
        text(c, "start")?,
        text(c, "end")?,
    );
    let (a, b) = (p(at, start)?, p(at, end)?);
    let q = b;
    let p = a;
    let idx = groups
        .get(harness)
        .and_then(|g| g.iter().position(|v| v == id))
        .context("connection harness index")?;
    let lane = ((idx % 4) as f64 - 1.5) * 1.8;
    if harness == "J1" || harness == "J2" {
        let mut pts;
        if start.starts_with("J1.") || start.starts_with("J2.") {
            let labels = if harness == "J1" {
                vec![
                    "COM", "OUT1", "OUT2", "OUT3", "OUT4", "OUT5", "OUT6", "OUT7", "OUT8",
                ]
            } else {
                vec!["COM", "OUT1", "OUT2", "FAN", "OUT3"]
            };
            let n = labels
                .iter()
                .position(|&s| Some(s) == start.split('.').nth(1))
                .context("manifold pin")?;
            let bank = if harness == "J1" { 0 } else { 2 };
            let y = 179. + 2. * (bank + n / 5) as f64;
            let z = 282. + (n % 5) as f64 * PITCH;
            pts = vec![
                [p[0], p[1], 275.],
                [p[0], y, 275.],
                [p[0], y, z],
                [70. + n as f64 * PITCH, y, z],
            ];
            if end.starts_with("wago-") {
                pts.extend([[76., y, z], [76., q[1], q[2]]]);
                return Ok(pts);
            }
        } else {
            let n = idx % 9;
            let z = 281.5 + n as f64 * 1.4;
            let trunk = match id {
                "J1-positive-A" => 30.5,
                "J1-positive-B" => 32.3,
                _ => 24. + lane,
            };
            pts = vec![
                [p[0] - 6., p[1], p[2]],
                [75., p[1], p[2]],
                [75., 190., z],
                [trunk, 190., z],
            ];
        }
        let last = *pts.last().unwrap();
        if end.starts_with("V-") {
            let letter = end.chars().nth(2).context("valve letter")?;
            if has(saved, "tail_stations") {
                pts.extend(station_rows(at, &saved["tail_stations"])?);
                return Ok(pts);
            }
            if letter == 'B' {
                pts.extend([
                    [96., last[1], last[2]],
                    [96., q[1] + 8., last[2]],
                    [q[0], q[1] + 8., q[2]],
                ]);
                return Ok(pts);
            }
            if "AK".contains(letter) {
                let x = if letter == 'A' {
                    -62. + lane
                } else {
                    98. + lane
                };
                let z = 337. + (idx % 2) as f64 * 2.;
                pts.extend([
                    [x, 276., last[2]],
                    [x, 276., z],
                    [x, q[1], z],
                    [q[0], q[1], z],
                ]);
                return Ok(pts);
            }
            let x = 68. + (idx % 5) as f64 * 2.;
            if "GJ".contains(letter) {
                pts.extend([
                    [x, 190., last[2]],
                    [x, q[1] + 12., last[2]],
                    [x, q[1] + 12., q[2]],
                    [q[0], q[1] + 12., q[2]],
                ]);
                return Ok(pts);
            }
            let z = q[2] + v(&at["terminals"][end]["outward"])?[2] * (11. + (idx % 2) as f64 * 2.);
            pts.extend([
                [x, 190., last[2]],
                [x, q[1] + 12., last[2]],
                [x, q[1] + 12., z],
                [x, q[1], z],
                [q[0], q[1], z],
            ]);
            return Ok(pts);
        }
        pts.extend([
            [70. + lane, 190., 280.],
            [70. + lane, 80., 165. + lane],
            [q[0], 80., 165. + lane],
            [q[0], q[1] + 12., q[2]],
        ]);
        return Ok(pts);
    }
    match harness {
        "J13" => pump_lead(c, at, (idx % 4) as f64),
        "J9" => {
            let n = (idx % 4) as f64;
            let x = 4. + n * PITCH;
            let mut out = vec![
                [p[0], p[1], 298.],
                [x, p[1], 298.],
                [x, 208., 298.],
                [x, 184., 298.],
            ];
            out.extend(display_internal(at, n)?);
            Ok(out)
        }
        "J11" => {
            let x = -92. + lane;
            Ok(vec![
                [p[0], p[1], 283. + lane],
                [x, p[1], 283. + lane],
                [x, 178., 283. + lane],
                [x, 178., 30. + lane],
                [x, q[1] + 10., 30. + lane],
                [q[0] + 8., q[1] + 10., q[2]],
            ])
        }
        "J6" | "J7" => {
            if start.starts_with("reed-") {
                Ok(vec![
                    [p[0] + 4., p[1], p[2] - 8.],
                    [q[0] + 4., q[1], q[2] - 10.],
                ])
            } else if end.starts_with("wago-") {
                Ok(vec![
                    [p[0], p[1], 282. + lane],
                    [28. + lane, p[1], 282. + lane],
                    [28. + lane, q[1], 282. + lane],
                    [28. + lane, q[1], q[2]],
                ])
            } else {
                bail!("Reed lead missing its cap bundle: {id}")
            }
        }
        "J4" => {
            if end.starts_with("wago-") {
                return Ok(vec![
                    [p[0], p[1], 282. + lane],
                    [29. + lane, p[1], 282. + lane],
                    [29. + lane, q[1], 282. + lane],
                    [29. + lane, q[1], q[2]],
                ]);
            }
            if end.starts_with("flow.") {
                let n = match end {
                    "flow.V" => 0.,
                    "flow.PULSE" => 1.,
                    "flow.GND" => 2.,
                    _ => bail!("flow terminal"),
                };
                let x = 40. - n * 2.5;
                let fore = 278. + n * 2.5;
                let turn_y = 353. + n * 2.5;
                let east = 101.5 - n * PITCH;
                let meter = q[0] + 2.5 * n;
                let mut out = if start.starts_with("wago-") {
                    let departure = p[0] - 8.;
                    vec![
                        [departure, p[1], 274.],
                        [departure, fore, 274.],
                        [x, fore, 274.],
                    ]
                } else {
                    let departure = 5. - n * 2.5;
                    vec![
                        [p[0], p[1], 278.],
                        [departure, p[1], 278.],
                        [departure, fore, 278.],
                        [x, fore, 278.],
                    ]
                };
                out.extend([
                    [x, fore, 337.],
                    [east, fore, 337.],
                    [east, turn_y, 337.],
                    [east, turn_y, 268.],
                    [meter, turn_y, 268.],
                    [meter, q[1], 268.],
                    [q[0], q[1], 268.],
                ]);
                return Ok(out);
            }
            bail!("Sensor lead missing its cap bundle: {id}")
        }
        "J3" => {
            let z = 303. + lane;
            Ok(vec![
                [p[0], p[1], 282. + lane],
                [p[0], 280.5, 282. + lane],
                [-49. + lane, 280.5, 282. + lane],
                [-49. + lane, 280.5, z],
                [-49. + lane, 434., z],
                [q[0], 434., z],
                [q[0], q[1] - 6., q[2]],
            ])
        }
        "J5" => {
            if start.starts_with("relay-") {
                Ok(vec![[-70. + lane, p[1], p[2]], [-70. + lane, q[1], q[2]]])
            } else {
                Ok(vec![
                    [p[0], p[1], 283. + lane],
                    [p[0], 280.5, 283. + lane],
                    [-49. + lane, 280.5, 283. + lane],
                    [-49. + lane, 280.5, q[2]],
                    [-49. + lane, q[1], q[2]],
                ])
            }
        }
        "AC inlet" => {
            let y = 437. - (idx % 3) as f64 * 3.2;
            Ok(vec![
                [p[0], y, p[2]],
                [-44., y, p[2]],
                [-44., y, q[2]],
                [q[0], y, q[2]],
            ])
        }
        "PSU primary" => Ok(vec![
            [p[0], 437., p[2]],
            [-41.5, 437., p[2]],
            [-41.5, q[1] + 6., p[2]],
            [q[0], q[1] + 6., p[2]],
        ]),
        "12V power" => {
            if start.starts_with("psu.") {
                Ok(vec![
                    [p[0], 342., p[2]],
                    [-49. + lane, 342., p[2]],
                    [-49. + lane, 342., 282. + lane],
                    [-49. + lane, 280.5, 282. + lane],
                    [29. + lane, 280.5, 282. + lane],
                    [29. + lane, q[1], 282. + lane],
                    [29. + lane, q[1], q[2]],
                ])
            } else {
                Ok(vec![
                    [31. + lane, p[1], p[2]],
                    [31. + lane, p[1], 284. + lane],
                    [31. + lane, q[1] + 9., 284. + lane],
                    [q[0], q[1] + 9., 284. + lane],
                    [q[0], q[1] + 9., q[2]],
                ])
            }
        }
        "Diaphragm pump" => {
            if end.starts_with("relay-") {
                Ok(vec![
                    [31., p[1], p[2]],
                    [31., 280.5, 282.],
                    [-49., 280.5, 282.],
                    [-49., 280.5, 338.],
                    [-49., q[1], 338.],
                    [q[0] + 8., q[1], 338.],
                ])
            } else if start.starts_with("wago-") {
                Ok(vec![
                    [31., p[1], p[2]],
                    [31., p[1], 284.],
                    [31., 280.5, 284.],
                    [-49., 280.5, 284.],
                    [-49., 280.5, 300.],
                    [-49., 457., 300.],
                    [q[0], 457., 300.],
                    [q[0], 457., q[2]],
                ])
            } else {
                Ok(vec![
                    [p[0] + 8., p[1], p[2]],
                    [-49. + lane, p[1], p[2]],
                    [-49. + lane, 457., p[2]],
                    [q[0], 457., p[2]],
                    [q[0], 457., q[2]],
                ])
            }
        }
        "Compressor" => {
            if start.starts_with("fuse.") {
                Ok(vec![[p[0] + 7., p[1], p[2]], [q[0] + 7., q[1], q[2]]])
            } else {
                Ok(vec![
                    [p[0], 435., p[2]],
                    [-52., 435., p[2]],
                    [-52., q[1], p[2]],
                    [q[0] + 8., q[1], p[2]],
                    [q[0] + 8., q[1], q[2]],
                ])
            }
        }
        "Earth bonds" => Ok(vec![
            [p[0], 435., p[2]],
            [-49., 435., 340.],
            [-49., 280., 340.],
            [28., 280., 340.],
            [28., 240., 340.],
            [28., 240., 282.],
            [28., q[1], 282.],
            [q[0], q[1], 282.],
        ]),
        _ => bail!("No installed route family for {id}"),
    }
}
fn dress_bank(c: &Value, guides: &[V], at: &Value, saved: &mut Value) -> Result<Option<Vec<V>>> {
    let (id, end, start) = (text(c, "id")?, text(c, "end")?, text(c, "start")?);
    if id == "J2-positive-K" {
        saved["note"] = json!(
            "The V-K positive lead passes beside the manifold bank before rejoining its retained east-wall hook course; terminal positions and hook datums remain fixed."
        );
        let mut out = vec![[84.8, 185., 267.]];
        out.extend(guides);
        return Ok(Some(out));
    }
    let group = if J1.contains(&id) {
        &J1[..]
    } else if J2.contains(&id) {
        &J2[..]
    } else {
        return Ok(None);
    };
    saved["note"] = json!(
        "Front-going J1/J2 leads retain their terminal lands and pass through the two-channel lid bank using a shared board crossing and separated fore fanouts; physical dressing and packing remain unqualified."
    );
    let site = manifold_site()?;
    let [x, _, z] = v(&site["target_centers"][id])?;
    let index = group.iter().position(|&s| s == id).unwrap();
    let a = p(at, start)?;
    let b = p(at, end)?;
    let flat_y = 203. + index as f64 * PITCH;
    let flat_z = if J1.contains(&id) { 289.2 } else { 291.15 };
    let mut common = vec![
        [a[0], a[1], flat_z],
        [a[0], flat_y, flat_z],
        [x, flat_y, flat_z],
        [x, flat_y, z],
        [x, 178., z],
    ];
    match id {
        "J1-COM" => common.extend([[b[0] - 8., b[1], b[2]]]),
        "J2-COM" => common.extend([[76.5, b[1], b[2]]]),
        "J2-FAN" => common.extend([
            [x, 164., z],
            [92.5, 164., z],
            [92.5, 164., 150.],
            [92.5, 50., 150.],
            [b[0], 50., b[2]],
        ]),
        "J1-OUT6" => common.extend([
            [x, 163., b[2] + 6.],
            [b[0], 163., b[2] + 6.],
            [b[0], b[1], b[2] + 6.],
        ]),
        "J2-OUT1" => common.extend([
            [53., 180., z],
            [53., 180., 293.5],
            [53., 166.5, 293.5],
            [b[0], 166.5, 293.5],
            [b[0], b[1], 293.5],
        ]),
        _ => {
            let (lane, turn) = match id {
                "J1-OUT3" => (43.2, 135.),
                "J1-OUT4" => (45.05, 131.),
                "J1-OUT5" => (46.9, 144.),
                "J1-OUT7" => (48.75, 143.),
                "J1-OUT8" => (50.6, 140.),
                "J2-OUT2" => (52.45, 139.),
                _ => bail!("manifold bank member {id}"),
            };
            let h = if [
                "V-C.negative",
                "V-D.negative",
                "V-E.negative",
                "V-H.negative",
            ]
            .contains(&end)
            {
                b[2] - 6.
            } else {
                b[2]
            };
            common.extend([
                [lane, 168., z],
                [lane, 168., h],
                [lane, turn, h],
                [b[0], turn, h],
            ]);
        }
    }
    Ok(Some(common))
}
fn dress(c: &Value, mut guides: Vec<V>, at: &Value, saved: &mut Value) -> Result<Vec<V>> {
    if boolean(saved, "preserve_stations", false) && has(saved, "stations") {
        return Ok(guides);
    }
    if let Some(bank) = dress_bank(c, &guides, at, saved)? {
        guides = bank;
    }
    let id = text(c, "id")?;
    let sites = cable_sites()?;
    let target = rows(&sites)?
        .iter()
        .find_map(|s| s["target_centers"].get(id));
    let Some(target) = target else {
        return Ok(guides);
    };
    let [x, _, z] = v(target)?;
    if id.starts_with("J5-") {
        let a = p(at, text(c, "start")?)?;
        let b = p(at, text(c, "end")?)?;
        return Ok(vec![
            [-88.5, a[1], z - 4.],
            [x, 256.5, z],
            [x, 357., z],
            [-72., 357., z],
            [-72., b[1], z],
            [-72., b[1], b[2]],
        ]);
    }
    if id == "J2-positive-K" {
        if let Some(i) = guides
            .iter()
            .position(|p| p[0] > 93. && p[1] > 270. && p[1] < 280. && (p[2] - z).abs() < 0.01)
        {
            let mut out = guides[..i].to_vec();
            out.extend([[x, 266.5, z], [x, 281.5, z]]);
            out.extend(&guides[i + 1..]);
            return Ok(out);
        }
        return Ok(guides);
    }
    let lane = guides
        .iter()
        .enumerate()
        .filter(|(_, p)| p[0] < -92. && p[1] >= 308. && p[1] <= 335. && (p[2] - z).abs() < 0.01)
        .map(|(i, _)| i)
        .collect::<Vec<_>>();
    let Some(&first) = lane.first() else {
        return Ok(guides);
    };
    let last = *lane.last().unwrap();
    let mut out = guides[..first].to_vec();
    out.extend([[x, 331.5, z], [x, 305.5, z], [-80., guides[last][1], z]]);
    out.extend(&guides[last + 1..]);
    Ok(out)
}
pub fn routed(root: &Path, connections: &Value, at: &Value) -> Result<Value> {
    let mut overrides = load(root, "hardware/wiring/installed/route-overrides.json")?;
    let mut groups: BTreeMap<String, Vec<String>> = BTreeMap::new();
    for c in rows(connections)? {
        groups
            .entry(text(c, "harness")?.into())
            .or_default()
            .push(text(c, "id")?.into());
    }
    let stock = model::stock()?;
    let mut result = Vec::new();
    let mut bundle_context = bundles::Context::new(root, at)?;
    for c in rows(connections)? {
        if let Some(shared) = bundle_context.core_route(c)? {
            result.push(shared);
            continue;
        }
        let id = text(c, "id")?;
        let start = text(c, "start")?;
        let end = text(c, "end")?;
        let mut saved = overrides
            .get_mut(id)
            .map(|v| v.clone())
            .unwrap_or_else(|| json!({}));
        let mut guides = if has(&saved, "stations") {
            station_rows(at, &saved["stations"])?
        } else {
            guide(c, at, &groups, &saved)?
        };
        let index = groups[text(c, "harness")?]
            .iter()
            .position(|v| v == id)
            .unwrap() as f64;
        match saved.get("front_top_passage").and_then(Value::as_str) {
            Some("pump") => guides.extend(pump_terminal(c, at, index)?),
            Some("display") => guides.extend(display_internal(at, index)?),
            _ => {}
        }
        guides = dress(c, guides, at, &mut saved)?;
        let lead = if stock[text(c, "stock")?]["awg"] == 22 {
            6.
        } else {
            8.
        };
        let lands = saved.get("end_lands_mm");
        let mut start_lead = lands.map(|v| number(&v[0])).transpose()?.unwrap_or(lead);
        let mut end_lead = lands.map(|v| number(&v[1])).transpose()?.unwrap_or(lead);
        if lands.is_none() {
            if start.starts_with("psu.") {
                start_lead = 6.;
            }
            if end.starts_with("psu.") {
                end_lead = 6.;
            }
            if ["J9", "J13"].contains(&text(c, "harness")?) {
                end_lead = 3.;
            }
        }
        if start.starts_with("wago-mana.") || start.starts_with("wago-manb.") {
            start_lead = 4.;
        }
        if end.starts_with("wago-mana.") || end.starts_with("wago-manb.") {
            end_lead = 4.;
        }
        let a = p(at, start)?;
        let b = p(at, end)?;
        let mut points = vec![
            a,
            add(a, mul(v(&at["terminals"][start]["outward"])?, start_lead)),
        ];
        points.extend(guides);
        points.extend([
            add(b, mul(v(&at["terminals"][end]["outward"])?, end_lead)),
            b,
        ]);
        let mut input = json!({"connection":c,"points":points,"note":saved.get("note").and_then(Value::as_str).unwrap_or("Selected installed route between native terminal frames."),"endpoint_tangent_fraction":optional(&saved,"endpoint_tangent_fraction",0.44)});
        if let Some(radius) = saved.get("bend_radius_mm") {
            input["radius"] = radius.clone();
        }
        let mut route = model::finish(&input)?;
        route["status"] = saved
            .get("route_status")
            .cloned()
            .unwrap_or_else(|| json!("selected_layout"));
        result.push(route);
    }
    Ok(json!(result))
}
