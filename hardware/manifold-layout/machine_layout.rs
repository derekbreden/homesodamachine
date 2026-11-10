//! The installed machine: ordered source models, authored datums and rigid frames.
//!
//! Layout reads fine part geometry to seat it; it does not reconstruct those parts in an
//! interpreter. Geometry authored by the layout itself (the condenser, mounting envelopes
//! and fixed-return elbows) is cut here on the same kernel as the part generators.
use anyhow::{ensure, Context, Result};
use hsm_kernel::{step, v2, v3, Affine, Body, Bounds, Imported, Plane, Profile, Solid, V3};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

#[path = "../assembly/scenes/model_export/component_order.rs"]
mod component_order;
mod machine_layout_refs;

fn f(v: &Value, k: &str) -> Result<f64> {
    v.get(k)
        .and_then(Value::as_f64)
        .with_context(|| format!("missing number {k}"))
}
fn p(v: &Value) -> Result<V3> {
    let a = v.as_array().context("point is an array")?;
    ensure!(a.len() == 3, "point has three coordinates");
    Ok(v3(
        a[0].as_f64().context("point X")?,
        a[1].as_f64().context("point Y")?,
        a[2].as_f64().context("point Z")?,
    ))
}
fn frame(v: &Value) -> Result<Affine> {
    if v.is_null() {
        return Ok(Affine::IDENTITY);
    }
    let mut m = [[0.; 4]; 3];
    if v.get("rotation").is_some() {
        let t = p(&v["translation_mm"])?;
        for (i, row) in m.iter_mut().enumerate() {
            for (j, cell) in row.iter_mut().take(3).enumerate() {
                *cell = v["rotation"][i][j]
                    .as_f64()
                    .context("rotation coordinate")?;
            }
            row[3] = t.to_array()[i];
        }
    } else {
        for (i, row) in m.iter_mut().enumerate() {
            for (j, cell) in row.iter_mut().enumerate() {
                *cell = v[i][j].as_f64().context("frame coordinate")?;
            }
        }
    }
    Ok(Affine { m })
}
fn bounds(parts: &[Imported], transform: &Affine) -> Result<Bounds> {
    let mut lo = v3(f64::INFINITY, f64::INFINITY, f64::INFINITY);
    let mut hi = -lo;
    for part in parts {
        for &vertex in part.solid.verts() {
            let point = transform.point(vertex);
            lo = lo.min(point);
            hi = hi.max(point);
        }
    }
    ensure!(
        lo.is_finite() && hi.is_finite(),
        "empty model has no seating bounds"
    );
    Ok(Bounds { min: lo, max: hi })
}
fn merged(a: Bounds, b: Bounds) -> Bounds {
    Bounds {
        min: a.min.min(b.min),
        max: a.max.max(b.max),
    }
}
fn values(b: Bounds) -> Value {
    json!([b.min.to_array(), b.max.to_array()])
}
fn packed_box(b: Bounds) -> Value {
    json!([b.min.x, b.max.x, b.min.y, b.max.y, b.min.z, b.max.z])
}
fn logical(name: &str) -> &str {
    name.rsplit_once('/')
        .filter(|(_, tail)| !tail.is_empty() && tail.chars().all(|c| c.is_ascii_digit()))
        .map_or(name, |(head, _)| head)
}
fn rounded(x: f64) -> f64 {
    (x * 1e6).round() / 1e6
}

fn payload_entries(path: &str) -> Result<Vec<Imported>> {
    // The importer normally groups /1,/2 meshes into one purchased body. A placement plan
    // retains the fine export's entry boundary as well as the logical component boundary.
    let bytes = std::fs::read(path)?;
    hsm_kernel::reads::read(Path::new(path), &bytes);
    ensure!(bytes.len() >= 4, "payload header");
    let n = u32::from_le_bytes(bytes[..4].try_into().unwrap()) as usize;
    let header: Value = serde_json::from_slice(&bytes[4..4 + n])?;
    let mut out = vec![];
    for entry in header["meshes"].as_array().context("payload entries")? {
        let mut one = header.clone();
        one["meshes"] = json!([entry]);
        let mut head = serde_json::to_vec(&one)?;
        while head.len() % 4 != 0 {
            head.push(b' ');
        }
        let mut payload = (head.len() as u32).to_le_bytes().to_vec();
        payload.extend(head);
        payload.extend_from_slice(&bytes[4 + n..]);
        for mut body in hsm_kernel::import::bodies(&payload, path)? {
            body.name = entry["name"]
                .as_str()
                .context("payload entry name")?
                .to_owned();
            out.push(body);
        }
    }
    Ok(out)
}

struct Layout {
    sources: BTreeMap<String, Vec<Imported>>,
    references: BTreeMap<String, machine_layout_refs::References>,
    instances: Vec<Value>,
    presentation: Vec<Value>,
    generated: Vec<Imported>,
    bounds: BTreeMap<String, Bounds>,
    frames: BTreeMap<String, Value>,
    seats: BTreeMap<String, Value>,
    order: Vec<String>,
    generated_path: String,
}
impl Layout {
    fn new(path: &Path) -> Self {
        Self {
            sources: BTreeMap::new(),
            references: BTreeMap::new(),
            instances: vec![],
            presentation: vec![],
            generated: vec![],
            bounds: BTreeMap::new(),
            frames: BTreeMap::new(),
            seats: BTreeMap::new(),
            order: vec![],
            generated_path: path.to_string_lossy().into_owned(),
        }
    }
    fn load(&mut self, path: &str) -> Result<&[Imported]> {
        if !self.sources.contains_key(path) {
            let rows = if path.ends_with(".npz") {
                hsm_kernel::import::model(path)?
            } else if path.ends_with(".mesh") {
                payload_entries(path)?
            } else {
                hsm_kernel::import::step(path)?
            };
            self.sources.insert(path.to_owned(), rows);
        }
        Ok(&self.sources[path])
    }
    fn reference(&mut self, model: &str) -> Result<&mut machine_layout_refs::References> {
        if !self.references.contains_key(model) {
            self.references.insert(
                model.to_owned(),
                machine_layout_refs::References::open(model)?,
            );
        }
        Ok(self.references.get_mut(model).unwrap())
    }
    fn identities(&mut self, model: &str) -> Result<Vec<String>> {
        if model == self.generated_path {
            return Ok(self.generated.iter().map(|b| b.name.clone()).collect());
        }
        if let Some(parts) = self.sources.get(model) {
            return Ok(parts.iter().map(|b| b.name.clone()).collect());
        }
        if model.ends_with(".npz") {
            return Ok(self.reference(model)?.names.clone());
        }
        Ok(self.load(model)?.iter().map(|b| b.name.clone()).collect())
    }
    fn entry_bounds(&mut self, model: &str, index: usize, transform: &Affine) -> Result<Bounds> {
        if model.ends_with(".npz") && !self.sources.contains_key(model) {
            return self.reference(model)?.bounds(index, transform);
        }
        bounds(
            std::slice::from_ref(
                self.load(model)?
                    .get(index)
                    .context("selected source entry")?,
            ),
            transform,
        )
    }
    fn model_bounds(&mut self, model: &str, transform: &Affine) -> Result<Bounds> {
        let n = self.identities(model)?.len();
        let mut result = None;
        for i in 0..n {
            let b = self.entry_bounds(model, i, transform)?;
            result = Some(result.map_or(b, |old| merged(old, b)));
        }
        result.context("empty model has no seating bounds")
    }
    fn add(
        &mut self,
        model: &str,
        name: Option<&str>,
        prefix: &str,
        selected: Option<Vec<usize>>,
        transform: Affine,
        color: Option<Value>,
    ) -> Result<Vec<String>> {
        let source_names = self.identities(model)?;
        let selected = selected.unwrap_or_else(|| (0..source_names.len()).collect());
        let mut name_counts: BTreeMap<String, usize> = BTreeMap::new();
        for &index in &selected {
            *name_counts
                .entry(
                    source_names
                        .get(index)
                        .context("selected source entry")?
                        .clone(),
                )
                .or_default() += 1;
        }
        let duplicate_names = name.is_none() && name_counts.values().any(|&count| count > 1);
        let mut by_name: BTreeMap<String, Bounds> = BTreeMap::new();
        let mut ordered = vec![];
        for &i in &selected {
            let body_name = name
                .map(|name| logical(name).to_owned())
                .unwrap_or_else(|| format!("{prefix}{}", logical(&source_names[i])));
            let b = self.entry_bounds(model, i, &transform)?;
            if let Some(before) = by_name.get_mut(&body_name) {
                *before = merged(*before, b);
            } else {
                ordered.push(body_name.clone());
                by_name.insert(body_name, b);
            }
        }
        self.bounds.extend(by_name);
        for name in &ordered {
            if !self.order.contains(name) {
                self.order.push(name.clone());
            }
        }
        if !model.ends_with(".npz") {
            let parts = self.sources[model].clone();
            let override_color = color.as_ref().map(|value| {
                if value.is_null() {
                    None
                } else {
                    Some([
                        value[0].as_f64().unwrap(),
                        value[1].as_f64().unwrap(),
                        value[2].as_f64().unwrap(),
                    ])
                }
            });
            let count = selected.len();
            let mut targets = vec![];
            for (ordinal, &index) in selected.iter().enumerate() {
                let body = &parts[index];
                let target = match name {
                    Some(name) if count > 1 => format!("{name}/{}", ordinal + 1),
                    Some(name) => name.to_owned(),
                    None => format!("{prefix}{}", body.name),
                };
                self.generated(
                    &target,
                    body.solid.transformed(&transform),
                    override_color.unwrap_or(body.color),
                )?;
                targets.push(target);
            }
            self.presentation
                .push(json!({"payload":model,"transform":transform.m,"targets":targets}));
        } else if duplicate_names {
            let mut seen: BTreeMap<String, usize> = BTreeMap::new();
            for &index in &selected {
                let native = source_names[index].clone();
                let ordinal = seen.entry(native.clone()).or_default();
                *ordinal += 1;
                let target = if name_counts[&native] > 1 {
                    format!("{prefix}{native}/{ordinal}")
                } else {
                    format!("{prefix}{native}")
                };
                let mut row =
                    json!({"model":model,"indices":[index],"transform":transform.m,"name":target});
                if let Some(color) = &color {
                    row["color"] = color.clone();
                }
                self.instances.push(row);
            }
        } else if let Some(name) = name.filter(|_| selected.len() > 1) {
            for (ordinal, index) in selected.iter().enumerate() {
                let mut row = json!({"model":model,"indices":[index],"transform":transform.m,
                    "name":format!("{name}/{}",ordinal+1)});
                if let Some(color) = &color {
                    row["color"] = color.clone();
                }
                self.instances.push(row);
            }
        } else {
            let mut row = json!({"model":model,"indices":selected,"transform":transform.m});
            if let Some(name) = name {
                row["name"] = json!(name);
            } else if !prefix.is_empty() {
                row["prefix"] = json!(prefix);
            }
            if let Some(color) = color {
                row["color"] = color;
            }
            self.instances.push(row);
        }
        Ok(ordered)
    }
    fn generated(&mut self, name: &str, solid: Solid, color: Option<[f64; 3]>) -> Result<()> {
        let b = solid.bounds();
        let index = self.generated.len();
        self.generated.push(Imported {
            name: name.to_owned(),
            color,
            solid,
        });
        let logical = logical(name).to_owned();
        self.bounds
            .entry(logical.clone())
            .and_modify(|old| *old = merged(*old, b))
            .or_insert(b);
        if !self.order.contains(&logical) {
            self.order.push(logical);
        }
        self.instances
            .push(json!({"model":self.generated_path,"indices":[index]}));
        Ok(())
    }
    fn ports(&mut self, name: &str, transform: Affine, native: &Value) -> Result<()> {
        let mut ports = serde_json::Map::new();
        for (key, row) in native.as_object().context("named ports")? {
            let (position, axis, diameter) = if row.is_array() {
                (
                    p(&row[0])?,
                    p(&row[1])?,
                    row[2].as_f64().context("port diameter")?,
                )
            } else {
                (p(&row["pos"])?, p(&row["axis"])?, f(row, "diam")?)
            };
            ports.insert(
                key.to_owned(),
                json!({"pos":transform.point(position).to_array(),
                "axis":transform.vector(axis).to_array(),"diam":diameter}),
            );
        }
        let mut value = json!({"transform":transform.m,"ports":ports});
        if let Some(b) = self.bounds.get(name) {
            value["bb"] = packed_box(*b);
        }
        self.frames.insert(name.to_owned(), value);
        Ok(())
    }
    fn station_seat(&mut self, name: &str, at: V3) {
        let station = json!({"station":at.to_array()});
        self.seats.insert(
            name.to_owned(),
            json!({"members":[name],"turns":[],"rule":station,
            "got":station,"room":[]}),
        );
    }
    fn plane_seat(&mut self, name: &str, rule: Value, members: Vec<String>, b: Bounds) {
        let mut got = serde_json::Map::new();
        for (key, _) in rule.as_object().unwrap() {
            let value = match key.as_str() {
                "x0" => b.min.x,
                "x1" => b.max.x,
                "cx" => (b.min.x + b.max.x) / 2.,
                "y0" => b.min.y,
                "y1" => b.max.y,
                "cy" => (b.min.y + b.max.y) / 2.,
                "z0" => b.min.z,
                _ => continue,
            };
            got.insert(key.clone(), json!(value));
        }
        self.seats.insert(
            name.to_owned(),
            json!({"members":members,"turns":[],"rule":rule,
            "got":got,"room":[]}),
        );
    }
    fn write_generated(&self) -> Result<()> {
        if let Some(parent) = Path::new(&self.generated_path).parent() {
            std::fs::create_dir_all(parent)?;
        }
        let bodies = self
            .generated
            .iter()
            .map(|body| Body {
                name: &body.name,
                color: body.color,
                solid: &body.solid,
            })
            .collect::<Vec<_>>();
        step::write_model(&self.generated_path, &bodies)?;
        Ok(())
    }
}

fn color(v: &Value, name: &str) -> Result<Option<[f64; 3]>> {
    let value = &v["colors"][name];
    if value.is_null() {
        return Ok(None);
    }
    Ok(Some([
        value[0].as_f64().context("color R")?,
        value[1].as_f64().context("color G")?,
        value[2].as_f64().context("color B")?,
    ]))
}
fn source<'a>(v: &'a Value, name: &str) -> Result<&'a str> {
    v["sources"][name]
        .as_str()
        .with_context(|| format!("missing model source {name}"))
}
fn translated(transform: Affine, step: V3) -> Affine {
    transform.then(&Affine::translation(step))
}
fn seated(parts: &[Imported], turn: Affine, planes: &Value) -> Result<Affine> {
    let b = bounds(parts, &turn)?;
    let cx = planes
        .get("cx")
        .and_then(Value::as_f64)
        .map_or(0., |n| n - (b.min.x + b.max.x) / 2.);
    let cy = planes
        .get("cy")
        .and_then(Value::as_f64)
        .map_or(0., |n| n - (b.min.y + b.max.y) / 2.);
    let at = |key: &str, current: f64| {
        planes
            .get(key)
            .and_then(Value::as_f64)
            .map_or(0., |n| n - current)
    };
    Ok(translated(
        turn,
        v3(
            cx + at("x0", b.min.x) + at("x1", b.max.x),
            cy + at("y0", b.min.y) + at("y1", b.max.y),
            at("z0", b.min.z),
        ),
    ))
}

fn condenser(v: &Value) -> Result<Solid> {
    let c = &v["datums"]["condenser"];
    let (x, y, z) = (f(c, "airflow")?, f(c, "face_a")?, f(c, "face_b")?);
    let t = f(c, "plate_t")?;
    let r = f(c, "recess_y")?;
    let mut shape = Solid::cuboid(V3::ZERO, v3(x, y, z));
    for y0 in [0., y - r] {
        shape = shape.cut(&Solid::cuboid(v3(0., y0, t), v3(x, y0 + r, z - t)))?;
    }
    shape.cut(&Solid::cylinder(
        v3(f(c, "mount_x")?, f(c, "mount_y")?, 0.),
        V3::Z,
        f(c, "mount_d")? / 2.,
        z,
    )?)
}
fn base(layout: &mut Layout, v: &Value) -> Result<()> {
    let d = &v["datums"];
    let r = Affine::rotation(V3::ZERO, V3::Z, 90.);
    let comp_source = source(v, "compressor")?;
    let comp0 = seated(
        layout.load(comp_source)?,
        r,
        &json!({"cx":0.,"y0":0.,"z0":0.}),
    )?;
    let compb = bounds(layout.load(comp_source)?, &comp0)?;
    let cond = condenser(v)?;
    let raw = Imported {
        name: "condenser+fan".into(),
        color: color(v, "condenser")?,
        solid: cond,
    };
    let cond0 = seated(
        std::slice::from_ref(&raw),
        r,
        &json!({"cx":0.,"y0":compb.max.y,"z0":f(d,"cond_bore_depth")?}),
    )?;
    let condb = bounds(std::slice::from_ref(&raw), &cond0)?;
    let combined = merged(compb, condb);
    let turn = Affine::rotation(
        v3(combined.center().x, combined.center().y, 0.),
        V3::Z,
        -90.,
    );
    let turned = comp0.then(&turn);
    let comp_turn = bounds(layout.load(comp_source)?, &turned)?;
    let move_pair = Affine::translation(v3(
        f(d, "suction_lane_x")? - comp_turn.min.x,
        f(d, "compressor_front")? - comp_turn.min.y,
        0.,
    ));
    let comp = turned.then(&move_pair);
    let cond = cond0.then(&turn).then(&move_pair);
    let b = bounds(std::slice::from_ref(&raw), &cond)?;
    let cond = translated(
        cond,
        v3(
            f(d, "front_bottom_east")? - f(d, "cond_mount_clear")? - b.max.x,
            0.,
            0.,
        ),
    );
    layout.add(
        comp_source,
        Some("compressor"),
        "",
        None,
        comp,
        Some(v["colors"]["compressor"].clone()),
    )?;
    layout.generated("condenser+fan", raw.solid.transformed(&cond), raw.color)?;
    let cb = layout.bounds["compressor"];
    let db = layout.bounds["condenser+fan"];
    layout.plane_seat(
        "refrigeration-base",
        json!({"x0":f(d,"suction_lane_x")?,"z0":0.}),
        vec!["compressor".into(), "condenser+fan".into()],
        cb,
    );
    layout.plane_seat(
        "refrigeration-base depth",
        json!({"y0":f(d,"compressor_front")?}),
        vec!["compressor".into()],
        cb,
    );
    layout.ports("compressor", comp, &d["compressor"]["ports"])?;
    layout.ports("condenser+fan", cond, &d["condenser"]["ports"])?;
    let sensor = source(v, "mq6")?;
    let sensor_turn = Affine::rotation(V3::ZERO, V3::X, -90.).then(&r);
    let sensor_plane = json!({"x0":f(d,"front_bottom_west")?+f(d,"clearance_floor")?,
        "y0":f(d,"mq6_y0")?,"z0":cb.min.z+f(d,"mq6_rail_wall")?});
    let sensor_frame = seated(layout.load(sensor)?, sensor_turn, &sensor_plane)?;
    layout.add(
        sensor,
        Some("mq6-sensor"),
        "",
        None,
        sensor_frame,
        None,
    )?;
    layout.plane_seat(
        "mq6-sensor",
        sensor_plane,
        vec!["mq6-sensor".into()],
        layout.bounds["mq6-sensor"],
    );
    let face = comp.point(p(&d["compressor"]["power_face"])?);
    let fuse_frame = translated(Affine::rotation(V3::ZERO, V3::X, 90.).then(&r), face);
    for (key, name) in [("fuse", "thermal-fuse"), ("fuse_clamp", "fuse-clamp")] {
        layout.add(
            source(v, key)?,
            Some(name),
            "",
            None,
            fuse_frame,
            Some(v["colors"][key].clone()),
        )?;
        layout.station_seat(name, face);
    }
    layout.seats.get_mut("thermal-fuse").unwrap()["room"] = json!([
        [
            "cover either side of the case",
            0.,
            (f(&d["compressor"], "power_y")? - f(&d["fuse"], "length")?) / 2.
        ],
        [
            "cover above and below the case",
            0.,
            (f(&d["compressor"], "power_z")? - f(&d["fuse"], "diameter")?) / 2.
        ]
    ]);
    let mut floor = vec![];
    for xy in d["compressor"]["mount_xy"]
        .as_array()
        .context("compressor mounts")?
    {
        let point = comp.point(v3(
            xy[0].as_f64().unwrap(),
            xy[1].as_f64().unwrap(),
            f(&d["compressor"], "base_z")?,
        ));
        floor.push(json!([
            point.x,
            point.y,
            point.z - f(d, "floor_grommet_squeeze")?,
            f(&d["compressor"], "mount_d")? - 2. * f(d, "floor_boss_slip")?
        ]));
    }
    let mut rows = vec![];
    let c = &d["condenser"];
    let height = f(c, "face_b")?;
    let t = f(c, "plate_t")?;
    for (i, (z0, z1)) in [(0., t), (height - t, height)].iter().enumerate() {
        let point = cond.point(v3(0., 0., *z0));
        let high = cond.point(v3(0., 0., *z1)).z;
        let half = f(d, "cond_slot_press")?;
        let root = if i == 0 {
            cb.min.z
        } else {
            point.z - half - f(d, "cond_rail_wall")?
        };
        rows.push(json!([point.y, db.min.x, db.max.x, point.z, high, root]));
    }
    let band0 = cond
        .point(v3(
            0.,
            f(c, "face_a")? - f(c, "recess_y")? + f(d, "cond_mount_clear")?,
            0.,
        ))
        .y;
    let band1 = cond
        .point(v3(
            0.,
            f(c, "face_a")? - f(d, "cond_slot_grip")? - f(d, "cond_mount_clear")?,
            0.,
        ))
        .y;
    let mut seats = vec![];
    for z in [0., height - t] {
        seats.push(
            cond.point(v3(f(c, "mount_x")?, f(c, "mount_y")?, z))
                .to_array(),
        );
    }
    let ay0 = cond.point(v3(0., f(c, "recess_y")?, 0.)).y;
    let ay1 = cond
        .point(v3(0., f(c, "face_a")? - f(c, "recess_y")?, 0.))
        .y;
    layout.frames.insert("__pack_base".into(),json!({"floor_bosses":floor,
        "west_cradle":[sensor_frame.point(p(&d["mq6_card_plane"])?).to_array()],
        "cond_cradle":rows,"cond_mount":[db.max.x+f(d,"cond_mount_clear")?,band0.min(band1),band0.max(band1),seats],
        "cond_airway":[ay0.min(ay1),ay0.max(ay1),db.min.z,db.max.z]}));
    Ok(())
}

fn manifold(layout: &mut Layout, v: &Value) -> Result<Vec<String>> {
    let model = source(v, "manifold")?;
    let excluded = v["datums"]["manifold_exclude"]
        .as_array()
        .context("manifold omitted bodies")?
        .iter()
        .filter_map(Value::as_str)
        .collect::<BTreeSet<_>>();
    let indices = layout
        .load(model)?
        .iter()
        .enumerate()
        .filter(|(_, b)| !excluded.contains(logical(&b.name)))
        .map(|(i, _)| i)
        .collect::<Vec<_>>();
    let d = &v["datums"];
    // These are the two actual authored turns. Their f64 coefficients also carry analytic
    // face records, and intentionally retain the quarter-turn's floating coefficients.
    let transform = Affine::rotation(V3::ZERO, V3::X, 90.)
        .then(&Affine::rotation(V3::ZERO, V3::Z, 180.))
        .then(&Affine::translation(v3(
            0.,
            f(d, "pack_y")?,
            f(d, "world_lift")?,
        )));
    let names = layout.add(model, None, "", Some(indices), transform, None)?;
    let inputs = &v["manifold_numbers"]["bodies"];
    let mut source_frames = BTreeMap::new();
    for row in inputs.as_array().context("manifold construction rows")? {
        let Some(name) = row["name"].as_str() else {
            continue;
        };
        if row["kind"] == "reference" {
            source_frames.insert(name.to_owned(), frame(&row["transform"])?);
        }
    }
    for (name, native) in d["manifold_ports"]
        .as_object()
        .context("manifold port datums")?
    {
        if let Some(local) = source_frames.get(name) {
            layout.ports(name, local.then(&transform), native)?;
        }
    }
    let pump_head = layout.bounds["pump-a-head"];
    layout.plane_seat(
        "manifold-layout",
        json!({"z0":f(d,"world_lift")?+f(d,"pump_face_z")?}),
        names.clone(),
        pump_head,
    );
    Ok(names)
}

fn core(layout: &mut Layout, v: &Value) -> Result<(Vec<String>, Affine)> {
    let d = &v["datums"];
    let cd = &v["core_datums"];
    let casing = source(v, "casing")?;
    let rotation = Affine::rotation(V3::ZERO, V3::Z, 90.);
    let local = p(&cd["source_seat"])?;
    let no_front = translated(rotation, -rotation.point(local));
    let native_bounds = bounds(layout.load(casing)?, &no_front)?;
    let front = f(d, "rear_plane_y")?
        - f(d, "rear_seam_clear")?
        - (native_bounds.max.y - native_bounds.min.y + 2. * f(cd, "casing_foil_allowance")?);
    let transform = translated(no_front, v3(0., front, 0.));
    let envelope = bounds(layout.load(casing)?, &transform)?;
    layout.bounds.insert("foam-assembly".into(), envelope);
    layout.station_seat("foam-assembly", v3(0., front, 0.));
    layout.ports("foam-assembly", transform, &cd["ports"])?;
    let before = layout.instances.len();
    let names = layout.add(
        source(v, "core")?,
        None,
        "cold-core/",
        None,
        transform,
        None,
    )?;
    layout.frames.insert(
        "__core".into(),
        json!({"transform":transform.m,
        "envelope":{"model":casing,"transform":transform.m,"color":v["colors"]["fuse_clamp"]},"front_y":front,
        "instance_count":layout.instances.len()-before,
        "cap_face":envelope.min.z+f(cd,"cap_face_over_floor")?}),
    );
    Ok((names, transform))
}

fn valve_trays(layout: &Layout) -> Result<Value> {
    let mut groups: BTreeMap<(usize, i8, i64), Vec<(String, V3)>> = BTreeMap::new();
    for (name, b) in &layout.bounds {
        if !name.starts_with("valve-v-") || ["valve-v-a", "valve-v-b"].contains(&name.as_str()) {
            continue;
        }
        let coil = name.replacen("valve-", "coil-", 1);
        let Some(cb) = layout.bounds.get(&coil) else {
            continue;
        };
        let delta = cb.center() - b.center();
        let ds = delta.to_array();
        let axis = (0..3)
            .max_by(|&a, &b| ds[a].abs().total_cmp(&ds[b].abs()))
            .unwrap();
        let sign = if ds[axis] > 0. { 1 } else { -1 };
        let plane = if sign > 0 {
            b.min.to_array()[axis]
        } else {
            b.max.to_array()[axis]
        };
        groups
            .entry((axis, sign, (plane * 1e6).round() as i64))
            .or_default()
            .push((name.clone(), b.center()));
    }
    let mut out = vec![];
    // Existing tray names sort aft before fore, independently of numeric plane order.
    let mut decks = groups
        .into_iter()
        .map(|((axis, sign, plane), members)| {
            let where_ = match (axis, sign) {
                (0, 1) => "west",
                (0, -1) => "east",
                (1, 1) => "fore",
                (1, -1) => "aft",
                (2, 1) => "bottom",
                _ => "top",
            };
            (format!("valve-tray-{where_}"), axis, sign, plane, members)
        })
        .collect::<Vec<_>>();
    decks.sort_by(|a, b| a.0.cmp(&b.0));
    for (_, axis, sign, plane, members) in decks {
        ensure!(axis == 1, "valve tray is installed on Y");
        out.push(json!([
            plane as f64 / 1e6,
            sign,
            members
                .iter()
                .map(|(_, c)| [rounded(c.x), rounded(c.z)])
                .collect::<Vec<_>>()
        ]));
    }
    Ok(json!(out))
}

fn pack(
    layout: &mut Layout,
    v: &Value,
    manifold_names: &[String],
    core_frame: Affine,
) -> Result<Value> {
    let d = &v["datums"];
    let mut pack = serde_json::Map::new();
    for key in [
        "front_ports",
        "back_ports",
        "east_ports",
        "west_ports",
        "c14",
        "east_bosses",
        "east_mount_fills",
        "side_wells",
        "asse_cradle",
        "flow_meter_anchors",
        "tube_anchors",
        "flank_reliefs",
    ] {
        pack.insert(key.into(), json!([]));
    }
    for key in ["funnel", "port_field", "nameplate", "keystone"] {
        pack.insert(key.into(), Value::Null);
    }
    if let Some(base) = layout.frames.remove("__pack_base") {
        for (key, value) in base.as_object().unwrap() {
            pack.insert(key.clone(), value.clone());
        }
    }
    let trays = valve_trays(layout)?;
    pack.insert("valve_trays".into(), trays.clone());
    // Bracket datums are authored by the current manifold producer, separate from its skirt's
    // tessellation. The scalar input retains that distinction.
    pack.insert("pump_trays".into(), d["pump_trays"].clone());
    let mut plate = d["collet_plate"].clone();
    plate["valve_trays"] = trays;
    pack.insert("collet_plate".into(), plate);
    pack.insert(
        "ceiling_reliefs".into(),
        json!(v["above_core"]["ceiling_pockets"]["pockets"]
            .as_array()
            .context("roof pockets")?
            .iter()
            .map(|p| json!([p["name"], p["xmin"], p["xmax"], p["ymin"], p["ymax"], p["zmax"]]))
            .collect::<Vec<_>>()),
    );
    let core = layout.bounds["foam-assembly"];
    let cd = &v["core_datums"];
    let floor0 = core.min.z;
    let floor1 = floor0 + f(d, "core_stop_rise")?;
    let casing = source(v, "casing")?;
    let mut course = vec![];
    for body in layout.load(casing)? {
        let s = body.solid.transformed(&core_frame);
        let clipped = s.intersect(&Solid::cuboid(
            v3(core.min.x - 1., core.min.y - 1., floor0),
            v3(core.max.x + 1., core.max.y + 1., floor1),
        ))?;
        if !clipped.is_empty() {
            course.push(Imported {
                name: String::new(),
                color: None,
                solid: clipped,
            });
        }
    }
    let foot = bounds(&course, &Affine::IDENTITY)?;
    let radius = f(cd, "corner_round_radius")?;
    let foil = f(cd, "casing_foil_allowance")?;
    pack.insert(
        "core_stops".into(),
        json!([-1., 1.]
            .iter()
            .map(|s| [
                s * (foot.max.x - radius),
                foot.min.y + radius,
                radius + foil
            ])
            .collect::<Vec<_>>()),
    );
    let cap = core.min.z + f(cd, "cap_face_over_floor")?;
    let east = f(
        &v["above_core"]["rear_wall"]["interior_panel_relief"],
        "xmin",
    )?;
    pack.insert(
        "core_holds".into(),
        json!([
            [-43.6, -37.5, core.max.y + foil, cap],
            [east - 9., east, core.max.y + foil, cap]
        ]),
    );
    let tip = core_frame.point(p(&cd["prv_vent_tip"])?);
    pack.insert(
        "vent_chase".into(),
        json!([[core.min.x - foil, tip.y, tip.z]]),
    );
    // The two flank pockets use fine coil/valve geometry, not expanded Python Shapes.
    let model = source(v, "manifold")?;
    let transform = Affine::rotation(V3::ZERO, V3::X, 90.)
        .then(&Affine::rotation(V3::ZERO, V3::Z, 180.))
        .then(&Affine::translation(v3(
            0.,
            f(d, "pack_y")?,
            f(d, "world_lift")?,
        )));
    let mut pockets = vec![];
    for (name, valve) in [("coil-v-f", "valve-v-f"), ("coil-v-i", "valve-v-i")] {
        let b = layout.bounds[name];
        let side = if b.center().x > 0. { 1. } else { -1. };
        let face = if side > 0. {
            f(d, "front_top_east")?
        } else {
            f(d, "front_top_west")?
        };
        let air = f(d, "clearance_floor")?;
        let mut hits = vec![];
        let query_bounds = [layout.bounds[name], layout.bounds[valve]];
        let items = layout.load(model)?;
        for (index, (which, entry)) in [
            (name, if side > 0. { face - air } else { face + air }),
            (valve, face),
        ]
        .into_iter()
        .enumerate()
        {
            let b = query_bounds[index];
            let (lo, hi) = if side > 0. {
                (entry, b.max.x + 1.)
            } else {
                (b.min.x - 1., entry)
            };
            if hi <= lo {
                continue;
            }
            let tool = Solid::cuboid(
                v3(lo, b.min.y - 1., b.min.z - 1.),
                v3(hi, b.max.y + 1., b.max.z + 1.),
            );
            for part in items.iter().filter(|part| logical(&part.name) == which) {
                let hit = part.solid.transformed(&transform).intersect(&tool)?;
                if !hit.is_empty() {
                    hits.push(Imported {
                        name: String::new(),
                        color: None,
                        solid: hit,
                    });
                }
            }
            if which == name && hits.is_empty() {
                break;
            }
        }
        if hits.is_empty() {
            continue;
        }
        let b = bounds(&hits, &Affine::IDENTITY)?;
        let floor = if side > 0. {
            b.max.x + air
        } else {
            b.min.x - air
        };
        pockets.push(json!([
            name,
            face.min(floor),
            face.max(floor),
            b.min.y - air,
            b.max.y + air,
            b.min.z - air,
            b.max.z + air
        ]));
    }
    pack.insert("front_flank_reliefs".into(), json!(pockets));
    let outside = d["through_wall"]
        .as_array()
        .unwrap()
        .iter()
        .filter_map(Value::as_str)
        .collect::<BTreeSet<_>>();
    let placed = layout
        .bounds
        .iter()
        .filter(|(name, _)| !name.starts_with("cold-core/") && !outside.contains(name.as_str()))
        .map(|(name, b)| (name.clone(), values(*b)))
        .collect::<BTreeMap<_, _>>();
    pack.insert("placed".into(), json!(placed));
    pack.insert("manifold_names".into(), json!(manifold_names));
    Ok(Value::Object(pack))
}

fn append(layout: &mut Layout, plan: &Value) -> Result<()> {
    for row in plan["instances"]
        .as_array()
        .map(Vec::as_slice)
        .unwrap_or(&[])
    {
        let model = row["model"].as_str().context("equipment model")?;
        let indices = row
            .get("indices")
            .and_then(Value::as_array)
            .map(|a| a.iter().map(|i| i.as_u64().unwrap() as usize).collect());
        if row["split_components"].as_bool() == Some(true) {
            let pose = frame(&row["transform"])?;
            let parts = layout.load(model)?.to_vec();
            let indices: Vec<usize> = indices.unwrap_or_else(|| (0..parts.len()).collect());
            let name = row["name"].as_str().context("split component name")?;
            let mut components = vec![];
            for index in indices {
                let body = &parts[index];
                for solid in component_order::in_frame(&body.solid, &pose.m)? {
                    components.push((solid.transformed(&pose), body.color));
                }
            }
            let count = components.len();
            for (i, (solid, source_color)) in components.into_iter().enumerate() {
                let target = if count == 1 {
                    name.to_owned()
                } else {
                    format!("{name}/{}", i + 1)
                };
                let color = row
                    .get("color")
                    .map(|value| {
                        if value.is_null() {
                            None
                        } else {
                            Some([
                                value[0].as_f64().unwrap(),
                                value[1].as_f64().unwrap(),
                                value[2].as_f64().unwrap(),
                            ])
                        }
                    })
                    .unwrap_or(source_color);
                layout.generated(&target, solid, color)?;
            }
            continue;
        }
        layout.add(
            model,
            row.get("name").and_then(Value::as_str),
            row.get("prefix").and_then(Value::as_str).unwrap_or(""),
            indices,
            frame(&row["transform"])?,
            row.get("color").cloned(),
        )?;
    }
    for row in plan["presentation"]
        .as_array()
        .map(Vec::as_slice)
        .unwrap_or(&[])
    {
        layout.presentation.push(row.clone());
    }
    for (name, value) in plan["frames"].as_object().into_iter().flatten() {
        let mut value = value.clone();
        if let Some(b) = layout.bounds.get(name) {
            value["bb"] = packed_box(*b);
        }
        if !layout.seats.contains_key(name) {
            if let Ok(pose) = frame(&value["transform"]) {
                layout.station_seat(name, pose.point(V3::ZERO));
            }
        }
        layout.frames.insert(name.clone(), value);
    }
    for (name, value) in plan["seats"].as_object().into_iter().flatten() {
        layout.seats.insert(name.clone(), value.clone());
    }
    Ok(())
}

fn dock(layout: &mut Layout, v: &Value) -> Result<()> {
    let tee = source(v, "tee")?;
    let stem = source(v, "stem_elbow")?;
    for row in v["dock_rows"].as_array().context("dock station rows")? {
        let name = row["tee"].as_str().context("dock tee name")?;
        let pose = Affine::from_columns(
            -V3::X,
            -V3::Y,
            V3::Z,
            v3(f(row, "x")?, f(row, "tee_y")?, f(row, "z")?),
        );
        layout.add(
            tee,
            Some(name),
            "",
            None,
            pose,
            Some(v["colors"]["tee"].clone()),
        )?;
        layout.station_seat(name, pose.point(V3::ZERO));
        for elbow in row["elbows"]
            .as_array()
            .context("two fixed return elbows")?
        {
            let name = elbow["name"].as_str().context("elbow name")?;
            let socket = p(&elbow["socket"])?;
            let x = -V3::Z;
            let z = v3(socket.y, -socket.x, 0.);
            let y = z.cross(x);
            let pose = Affine::from_columns(x, y, z, p(&elbow["crossing"])?);
            let keep = f(v, "hub_back_reach")? + f(elbow, "stem")?;
            let cutter = Solid::cuboid(v3(-keep - 40., -20., -20.), v3(-keep, 20., 20.));
            let native = layout.load(stem)?.to_vec();
            let count = native.len();
            for (i, body) in native.into_iter().enumerate() {
                // The collet is disjoint from the shortened stem cutter. Applying the same
                // exact cut to both retains the source order without centroid heuristics.
                let solid = if body.solid.bounds().min.x < -keep {
                    body.solid.cut(&cutter)?
                } else {
                    body.solid
                };
                let physical = if count == 1 {
                    name.to_owned()
                } else {
                    format!("{name}/{}", i + 1)
                };
                layout.generated(&physical, solid.transformed(&pose), color(v, "elbow")?)?;
            }
            layout.station_seat(name, pose.point(V3::ZERO));
        }
    }
    Ok(())
}

fn zcylinder(x: f64, y: f64, r: f64, z0: f64, z1: f64) -> Result<Solid> {
    Solid::cylinder(v3(x, y, z0), V3::Z, r, z1 - z0)
}
fn hexagon(x: f64, y: f64, across_flats: f64, z0: f64, z1: f64) -> Result<Solid> {
    let radius = across_flats / (2. * (std::f64::consts::PI / 6.).cos());
    let points = (0..6)
        .map(|i| {
            let a = i as f64 * std::f64::consts::TAU / 6.;
            v2(x + radius * a.cos(), y + radius * a.sin())
        })
        .collect::<Vec<_>>();
    Plane::XY
        .at(v3(0., 0., z0))
        .extrude(&Profile::polygon(&points), z1 - z0)
}
fn installed(layout: &mut Layout, v: &Value) -> Result<()> {
    let d = &v["installed_datums"];
    let cx = f(d, "cx")?;
    let cy = f(d, "cy")?;
    let seat = f(d, "funnel_seat_z")?;
    let funnel = Affine::translation(v3(cx, cy, seat));
    layout.add(
        source(v, "funnel")?,
        Some("funnel"),
        "",
        None,
        funnel,
        Some(v["colors"]["funnel"].clone()),
    )?;
    layout.station_seat("funnel", v3(cx, cy, seat));
    let lid = Affine::translation(v3(cx, cy, f(d, "cover_z")?));
    layout.add(
        source(v, "funnel_cover")?,
        Some("funnel-cover"),
        "",
        None,
        lid,
        Some(v["colors"]["funnel_cover"].clone()),
    )?;
    layout.station_seat("funnel-cover", lid.point(V3::ZERO));
    // Explicitly authored shell extras and panels are supplied by the enclosure producer.
    // Their positions are already world coordinates; their source models retain their exact
    // fine face records and any deliberate full-triangle spring presentation.
    let extras = &v["installed"];
    for row in extras["instances"]
        .as_array()
        .map(Vec::as_slice)
        .unwrap_or(&[])
    {
        let name = row["name"].as_str().unwrap_or("");
        if name.starts_with("enclosure-") {
            continue;
        }
        append(layout, &json!({"instances":[row]}))?;
    }
    for row in d["funnel_fasteners"]
        .as_array()
        .context("funnel fasteners")?
    {
        let name = format!(
            "funnel-frame-{}",
            row["name"].as_str().context("fastener name")?
        );
        let (x, y, head, insert) = (
            f(row, "x")?,
            f(row, "y")?,
            f(row, "head_seat_z")?,
            f(row, "insert_top_z")?,
        );
        let screw = zcylinder(x, y, 1.5, head - 12., head)?
            .union(&zcylinder(x, y, 2.75, head, head + 3.)?)?
            .cut(&hexagon(x, y, 2.5, head + 1.5, head + 3.1)?)?;
        let sleeve = zcylinder(x, y, 2.3, insert - 5.7, insert)?.cut(&zcylinder(
            x,
            y,
            1.25,
            insert - 5.8,
            insert + 0.1,
        )?)?;
        layout.generated(&format!("{name}-screw"), screw, color(v, "screw")?)?;
        layout.generated(&format!("{name}-insert"), sleeve, color(v, "insert")?)?;
    }
    let hole = v3(
        cx + f(d, "neck_dx")?,
        cy + f(d, "neck_dy")?,
        f(d, "frame_floor")? - f(d, "cradle_catch_gap")?,
    );
    let cradle = Affine::translation(hole + v3(0., 0., f(d, "cradle_source_z0")?));
    layout.add(
        source(v, "cradle")?,
        Some("elbow-cradle"),
        "",
        None,
        cradle,
        Some(v["colors"]["display_cover"].clone()),
    )?;
    layout.station_seat("elbow-cradle", hole);
    let turn = Affine::rotation(V3::ZERO, V3::Y, 90.);
    let target = v3(
        cx + f(d, "neck_dx")?,
        cy + f(d, "neck_dy")?,
        seat + f(d, "spout_land_z")?,
    );
    let elbow = translated(turn, target - turn.point(p(&d["drain_stem_tip"])?));
    layout.add(
        source(v, "stem_elbow")?,
        Some("funnel-drain-union"),
        "",
        None,
        elbow,
        Some(v["colors"]["elbow"].clone()),
    )?;
    layout.station_seat("funnel-drain-union", target);
    layout.ports("funnel-drain-union", elbow, &d["drain_ports"])?;
    layout.ports("funnel", funnel, &d["funnel_ports"])?;
    let a = f(d, "display_angle_deg")?.to_radians();
    let origin = p(&d["display_origin"])?;
    let normal = p(&d["display_normal"])?;
    let glass = v3(f(d, "display_centre_x")?, origin.y, origin.z)
        - normal * (f(d, "display_bezel_depth")? - f(d, "display_native_bezel_depth")?);
    let at = glass
        + V3::X * f(d, "display_body_offset_x")?
        + v3(0., a.cos(), a.sin()) * f(d, "display_body_offset_slope")?;
    let display = translated(
        Affine::rotation(V3::ZERO, V3::X, f(d, "display_angle_deg")? - 90.),
        at,
    );
    let display_source = source(v, "display")?;
    let display_bodies = layout.load(display_source)?;
    let mut display_indices = (0..display_bodies.len()).collect::<Vec<_>>();
    // The immutable display payload lists bezel before body. Its physical STEP's historical
    // leaves list the body first; the names identify that boundary without changing geometry.
    display_indices.sort_by_key(|&index| match display_bodies[index].name.as_str() {
        "body" => 0,
        "bezel" => 1,
        _ => 2,
    });
    layout.add(
        display_source,
        Some("display"),
        "",
        Some(display_indices),
        display,
        None,
    )?;
    layout.station_seat("display", at);
    let cover = translated(
        Affine::rotation(V3::ZERO, V3::X, f(d, "display_angle_deg")?),
        p(&d["display_cover_origin"])?,
    );
    for (key, name) in [
        ("display_cover", "display-cover"),
        ("display_gasket", "display-gasket"),
    ] {
        layout.add(
            source(v, key)?,
            Some(name),
            "",
            None,
            cover,
            Some(v["colors"][key].clone()),
        )?;
        layout.station_seat(name, cover.point(V3::ZERO));
    }
    let display_fasteners = Path::new(source(v, "display_cover")?)
        .with_file_name("display-cover-fasteners.step.npz");
    layout.add(
        display_fasteners.to_str().context("display fastener model path")?,
        Some("display-cover-fasteners"), "", None, cover, None,
    )?;
    // The status plate, its screws, inserts and LED are drawn in the cover's own frame beside it,
    // so the cover's transform places them.
    for (file, name) in [
        ("status-plate.step.npz", "status-plate"),
        ("status-plate-fasteners.step.npz", "status-plate-fasteners"),
    ] {
        let model = Path::new(source(v, "display_cover")?).with_file_name(file);
        layout.add(model.to_str().context("status plate model path")?, Some(name), "", None, cover, None)?;
    }
    for row in extras["instances"]
        .as_array()
        .map(Vec::as_slice)
        .unwrap_or(&[])
    {
        if row["name"].as_str().unwrap_or("").starts_with("enclosure-") {
            append(layout, &json!({"instances":[row]}))?;
        }
    }
    for row in d["y_seam"].as_array().context("y-seam hardware")? {
        let name = row["name"].as_str().context("seam screw name")?;
        let (x, y, seat, tip) = (f(row, "x")?, f(row, "y")?, f(row, "seat")?, f(row, "tip")?);
        let up = row["upward"].as_bool().unwrap();
        let (h0, h1) = if up {
            (seat - 5., seat)
        } else {
            (seat, seat + 5.)
        };
        let (s0, s1) = if up {
            (h0 - 0.1, h0 + 2.5)
        } else {
            (h1 - 2.5, h1 + 0.1)
        };
        let screw = zcylinder(x, y, 2.5, seat.min(tip), seat.max(tip))?
            .union(&zcylinder(x, y, 4.25, h0, h1)?)?
            .cut(&hexagon(x, y, 4., s0, s1)?)?;
        let (i0, i1) = (f(row, "insert0")?, f(row, "insert1")?);
        let insert =
            zcylinder(x, y, 3.55, i0, i1)?.cut(&zcylinder(x, y, 2.5, i0 - 0.1, i1 + 0.1)?)?;
        layout.generated(&format!("{name}-screw"), screw, color(v, "seam_screw")?)?;
        layout.generated(&format!("{name}-insert"), insert, color(v, "insert")?)?;
    }
    append(layout, &v["dock"])?;
    for skin in extras["presentation"]
        .as_array()
        .map(Vec::as_slice)
        .unwrap_or(&[])
    {
        layout.presentation.push(skin.clone());
    }
    Ok(())
}

fn hydrate(layout: &mut Layout, plan: &Value) -> Result<()> {
    let rows = plan["instances"].as_array().context("prepared instances")?;
    let normalized = plan["metadata"]["raw_bounds"].is_object()
        && plan["metadata"]["frames"].is_object()
        && plan["metadata"]["seats"].is_object()
        && rows.iter().all(|row| {
            row["model"].as_str().is_some_and(|m| m.ends_with(".npz"))
                && row["split_components"] != true
                && row["indices"].is_array()
                && (row.get("name").is_none() || row["indices"].as_array().unwrap().len() <= 1)
        });
    if normalized {
        for row in rows {
            let names = layout.identities(row["model"].as_str().unwrap())?;
            for index in row["indices"].as_array().unwrap() {
                let index = index.as_u64().context("prepared index")? as usize;
                let native = names.get(index).context("prepared source entry")?;
                let name = row["name"]
                    .as_str()
                    .map(|n| logical(n).to_owned())
                    .unwrap_or_else(|| {
                        format!(
                            "{}{}",
                            row["prefix"].as_str().unwrap_or(""),
                            logical(native)
                        )
                    });
                if !layout.order.contains(&name) {
                    layout.order.push(name);
                }
            }
            let mut instance = row.clone();
            instance["transform"] = json!(frame(&row["transform"])?.m);
            layout.instances.push(instance);
        }
        layout.presentation.extend(
            plan["presentation"]
                .as_array()
                .into_iter()
                .flatten()
                .cloned(),
        );
    } else {
        append(layout, plan)?;
    }
    // The casing is a measuring envelope, deliberately absent from the exported assembly.
    for (name, b) in plan["metadata"]["raw_bounds"]
        .as_object()
        .into_iter()
        .flatten()
    {
        layout.bounds.insert(
            name.clone(),
            Bounds {
                min: p(&b[0])?,
                max: p(&b[1])?,
            },
        );
    }
    for (name, row) in plan["metadata"]["frames"].as_object().into_iter().flatten() {
        layout.frames.insert(name.clone(), row.clone());
    }
    for (name, row) in plan["metadata"]["seats"].as_object().into_iter().flatten() {
        layout.seats.insert(name.clone(), row.clone());
    }
    Ok(())
}

fn placed_equipment(v: &Value) -> (Value, Vec<String>) {
    let equipment = &v["equipment"];
    let core = equipment["core_equipment"]
        .as_array()
        .map(Vec::as_slice)
        .unwrap_or(&[])
        .iter()
        .filter_map(Value::as_str)
        .collect::<BTreeSet<_>>();
    let mut regular = vec![];
    let mut flavor = vec![];
    let mut tubes = vec![];
    let mut internal = vec![];
    let mut aliases = vec![];
    let mut insulation = None;
    for row in equipment["instances"]
        .as_array()
        .map(Vec::as_slice)
        .unwrap_or(&[])
    {
        let name = row["name"].as_str().unwrap_or("");
        let base = logical(name);
        if base == "soda-continuous-insulation" {
            insulation = Some(row.clone());
            continue;
        }
        if base.starts_with("tube-") {
            tubes.push(row.clone());
        } else if core.contains(base) {
            let mut row = row.clone();
            row["name"] = json!(format!("cold-core/{name}"));
            internal.push((base.to_owned(), row));
            aliases.push(base.to_owned());
        } else if base.starts_with("flavor-reducer-") {
            flavor.push(row.clone());
        } else {
            regular.push(row.clone());
        }
    }
    let mut rows = flavor;
    for row in regular {
        let holder = row["name"].as_str() == Some("soda-bend-holder");
        rows.push(row);
        if holder {
            if let Some(insulation) = insulation.take() {
                rows.push(insulation);
            }
        }
    }
    if let Some(insulation) = insulation {
        rows.push(insulation);
    }
    let mut core_junctions = vec![];
    for row in equipment["junctions"]
        .as_array()
        .map(Vec::as_slice)
        .unwrap_or(&[])
    {
        if row["owner"] == "cold-core" {
            let name = row["name"].as_str().unwrap();
            aliases.push(name.to_owned());
            let mut row = row.clone();
            row["name"] = json!(format!("cold-core/{name}"));
            core_junctions.push(row);
        } else {
            rows.push(row.clone());
        }
    }
    let mut core_tubes = vec![];
    for row in tubes {
        let name = logical(row["name"].as_str().unwrap());
        let id = name.strip_prefix("tube-").unwrap_or(name);
        let spec = &equipment["route_specs"][id];
        let owners = spec["owners"].as_array().map(Vec::as_slice).unwrap_or(&[]);
        let on_core = !owners.is_empty()
            && owners
                .iter()
                .filter_map(Value::as_str)
                .all(|name| name == "foam-assembly" || core.contains(name));
        if on_core {
            aliases.push(name.to_owned());
            let mut row = row.clone();
            row["name"] = json!(format!("cold-core/{}", row["name"].as_str().unwrap()));
            core_tubes.push(row);
        } else {
            rows.push(row);
        }
    }
    internal.sort_by(|a, b| a.0.cmp(&b.0));
    let internal = internal
        .into_iter()
        .map(|(_, row)| row)
        .chain(core_junctions)
        .chain(core_tubes)
        .collect::<Vec<_>>();
    let mut plan = equipment.clone();
    plan["instances"] = json!(rows);
    plan["core_instances"] = json!(internal);
    if let Some(skins) = plan["presentation"].as_array_mut() {
        for skin in skins {
            if let Some(targets) = skin["targets"].as_array_mut() {
                for target in targets {
                    if let Some(name) = target.as_str() {
                        if aliases.iter().any(|alias| alias == logical(name)) {
                            *target = json!(format!("cold-core/{name}"));
                        }
                    }
                }
            }
        }
    }
    (plan, aliases)
}

pub fn run(v: &Value, out: &Path) -> Result<Value> {
    let generated = out.with_extension("parts.npz");
    let mut layout = Layout::new(&generated);
    if v["stage"] == "dock" {
        dock(&mut layout, v)?;
        layout.write_generated()?;
        return Ok(
            json!({"name":"pump-dock-equipment","generated_model":layout.generated_path,"instances":layout.instances,
            "seats":layout.seats,"metadata":{"raw_bounds":layout.bounds.iter()
                .map(|(name,b)|(name.clone(),values(*b))).collect::<BTreeMap<_,_>>()}}),
        );
    }
    let prepared = v.get("prepared").filter(|value| value.is_object());
    let (manifold_names, mut core_names, core_frame, core_meta) = if let Some(plan) = prepared {
        hydrate(&mut layout, plan)?;
        let meta = &plan["metadata"];
        (
            serde_json::from_value::<Vec<String>>(meta["manifold_names"].clone())?,
            serde_json::from_value::<Vec<String>>(meta["core_body_names"].clone())?,
            frame(&meta["core_carry"])?,
            json!({"envelope":plan["envelope"],"instance_count":meta["core_instance_count"]}),
        )
    } else {
        base(&mut layout, v)?;
        let manifold_names = manifold(&mut layout, v)?;
        let (core_names, core_frame) = core(&mut layout, v)?;
        let core_meta = layout.frames.remove("__core").unwrap();
        (manifold_names, core_names, core_frame, core_meta)
    };
    let core_instance_count = core_meta["instance_count"].as_u64().unwrap_or(1) as usize;
    let core_instances = layout
        .instances
        .split_off(layout.instances.len() - core_instance_count);
    let (equipment, core_external) = placed_equipment(v);
    append(&mut layout, &equipment)?;
    layout.instances.extend(core_instances);
    append(
        &mut layout,
        &json!({"instances":equipment["core_instances"]}),
    )?;
    let mut aliases = serde_json::Map::new();
    for name in &core_external {
        let physical = format!("cold-core/{name}");
        core_names.push(physical.clone());
        aliases.insert(physical.clone(), json!(name));
        if let Some(b) = layout.bounds.get(&physical).copied() {
            layout.bounds.insert(name.clone(), b);
        }
    }
    let mut packed = if let Some(prepared) = prepared {
        prepared["metadata"]["pack"].clone()
    } else {
        pack(&mut layout, v, &manifold_names, core_frame)?
    };
    let outside = v["datums"]["through_wall"]
        .as_array()
        .unwrap()
        .iter()
        .filter_map(Value::as_str)
        .collect::<BTreeSet<_>>();
    packed["placed"] = json!(layout
        .bounds
        .iter()
        .filter(|(name, _)| !name.starts_with("cold-core/") && !outside.contains(name.as_str()))
        .map(|(name, b)| (name.clone(), values(*b)))
        .collect::<BTreeMap<_, _>>());
    if v["stage"] == "installed" {
        installed(&mut layout, v)?;
    }
    let mut metadata = v["equipment"]["metadata"].clone();
    if !metadata.is_object() {
        metadata = json!({});
    }
    metadata["pack"] = packed.clone();
    metadata["frames"] = json!(layout.frames);
    metadata["seats"] = json!(layout.seats);
    metadata["core_body_names"] = json!(core_names);
    metadata["core_instance_count"] = json!(core_instance_count);
    metadata["core_external_names"] = json!(core_external);
    metadata["core_carry"] = json!(core_frame.m);
    metadata["envelope"] = core_meta["envelope"].clone();
    metadata["raw_bounds"] = json!(layout
        .bounds
        .iter()
        .map(|(name, b)| (name.clone(), values(*b)))
        .collect::<BTreeMap<_, _>>());
    metadata["manifold_names"] = json!(manifold_names);
    metadata["box"] = v["box"].clone();
    if let Some(models) = v["piece_models"].as_object() {
        let mut pieces = serde_json::Map::new();
        for (name, path) in models {
            let b =
                layout.model_bounds(path.as_str().context("piece model")?, &Affine::IDENTITY)?;
            pieces.insert(
                name.clone(),
                json!([b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z]),
            );
        }
        metadata["piece_bounds"] = Value::Object(pieces);
    }
    if let Some(datums) = v["installed"]["datums"].as_object() {
        metadata["enclosure_datums"] = json!(datums);
        if let Some(pieces) = datums.get("piece_bounds") {
            metadata["piece_bounds"] = pieces.clone();
        }
    }
    metadata["pack_body_names"] = json!(packed["placed"]
        .as_object()
        .unwrap()
        .keys()
        .collect::<Vec<_>>());
    let order = layout
        .order
        .iter()
        .map(|name| {
            aliases
                .get(name)
                .and_then(Value::as_str)
                .unwrap_or(name)
                .to_owned()
        })
        .filter(|name| name != "foam-assembly" && packed["placed"].get(name).is_some())
        .chain(std::iter::once("foam-assembly".to_owned()))
        .collect::<Vec<_>>();
    metadata["pack_order"] = json!(order);
    let mut pack_references: BTreeMap<String, Vec<Value>> = BTreeMap::new();
    for ordinal in 0..layout.instances.len() {
        let instance = layout.instances[ordinal].clone();
        let model = instance["model"].as_str().unwrap();
        let named = instance.get("name").and_then(Value::as_str);
        let prefix = instance.get("prefix").and_then(Value::as_str).unwrap_or("");
        if prefix == "cold-core/" {
            continue;
        }
        // Metadata needs names/indices only; reading source identities here avoids creating
        // another placed model solely to rediscover its groups in Python.
        let body_names = layout.identities(model)?;
        let indices = instance["indices"]
            .as_array()
            .map(|a| {
                a.iter()
                    .map(|i| i.as_u64().unwrap() as usize)
                    .collect::<Vec<_>>()
            })
            .unwrap_or_else(|| (0..body_names.len()).collect());
        let mut groups: BTreeMap<String, Vec<usize>> = BTreeMap::new();
        for i in indices {
            let name = named
                .map(|name| logical(name).to_owned())
                .unwrap_or_else(|| format!("{prefix}{}", logical(&body_names[i])));
            let name = aliases
                .get(&name)
                .and_then(Value::as_str)
                .unwrap_or(&name)
                .to_owned();
            if packed["placed"].get(&name).is_some() {
                groups.entry(name).or_default().push(i);
            }
        }
        for (name, indices) in groups {
            let mut row = instance.clone();
            row["indices"] = json!(indices);
            pack_references.entry(name).or_default().push(row);
        }
    }
    metadata["pack_references"] = json!(pack_references);
    metadata["pack_references"]["foam-assembly"] = json!([{"model":source(v,"casing")?,
        "transform":core_frame.m,"name":"foam-assembly"}]);
    layout.write_generated()?;
    Ok(
        json!({"name":"enclosure-assembly","generated_model":layout.generated_path,"instances":layout.instances,"aliases":aliases,
        "presentation":layout.presentation,"metadata":metadata,"envelope":core_meta["envelope"]}),
    )
}
fn main() -> Result<()> {
    let (numbers, directory) = hsm_kernel::part::args()?;
    std::fs::create_dir_all(&directory)?;
    let output = directory.join("machine-layout.json");
    let value = run(numbers.get("request")?, &output)?;
    if let Some(parent) = output.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::write(&output, serde_json::to_vec(&value)?)?;
    println!(
        "{}",
        json!({"files":["machine-layout.json","machine-layout.parts.npz"],"bodies":[],
        "plan":output,"components":value["instances"].as_array().unwrap().len()})
    );
    Ok(())
}
