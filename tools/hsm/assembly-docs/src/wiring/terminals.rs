use super::*;
use model::{V, add, dot, mul, points, sub, unit, v};
fn ea(path: &str) -> Result<Value> {
    get("ea", path)
}
fn module(name: &str, path: &str, args: Value) -> Result<Value> {
    call(name, path, args)
}
pub fn rotate(matrix: &Value, p: V) -> Result<V> {
    let mut out = [0.; 3];
    for (i, row) in rows(matrix)?.iter().enumerate() {
        out[i] = dot(v(row)?, p);
    }
    Ok(out)
}
pub fn carry(pose: &Value, p: V) -> Result<V> {
    Ok(add(
        rotate(&pose["rotation"], p)?,
        v(&pose["translation_mm"])?,
    ))
}
pub fn turns(value: &Value) -> Result<Value> {
    let mut rotation = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]];
    for turn in rows(value)? {
        let [x, y, z] = unit(v(&turn[0])?);
        let angle = number(&turn[1])?.to_radians();
        let (c, s) = (angle.cos(), angle.sin());
        let q = 1. - c;
        let t = [
            [c + x * x * q, x * y * q - z * s, x * z * q + y * s],
            [y * x * q + z * s, c + y * y * q, y * z * q - x * s],
            [z * x * q - y * s, z * y * q + x * s, c + z * z * q],
        ];
        let mut next = [[0.; 3]; 3];
        for i in 0..3 {
            for j in 0..3 {
                next[i][j] = (0..3).map(|k| t[i][k] * rotation[k][j]).sum();
            }
        }
        rotation = next;
    }
    Ok(json!(rotation))
}
pub fn bounds(body: &Value) -> Result<(V, V)> {
    let solids = body.get("solids").map(rows).transpose()?;
    if let Some(solids) = solids {
        let mut lo = [f64::INFINITY; 3];
        let mut hi = [f64::NEG_INFINITY; 3];
        for s in solids {
            let (a, b) = (v(&s["lower"])?, v(&s["upper"])?);
            for i in 0..3 {
                lo[i] = lo[i].min(a[i]);
                hi[i] = hi[i].max(b[i]);
            }
        }
        ensure!(!solids.is_empty(), "body has no solid bounds");
        Ok((lo, hi))
    } else {
        Ok((v(&body["lower"])?, v(&body["upper"])?))
    }
}
fn centre(body: &Value) -> Result<V> {
    let (a, b) = bounds(body)?;
    Ok(mul(add(a, b), 0.5))
}
pub fn part<'a>(at: &'a Value, name: &str) -> Result<&'a Value> {
    at["scene"]
        .get(name)
        .or_else(|| at["scene"].get(format!("cold-core/{name}")))
        .with_context(|| format!("installed body {name}"))
}
pub fn point(at: &Value, id: &str) -> Result<V> {
    v(&at["terminals"][id]["point"])
}
pub fn station(at: &Value, spec: &Value) -> Result<V> {
    let p = if let Some(value) = spec.get("point_mm") {
        v(value)?
    } else if let Some(passage) = spec.get("passage") {
        v(&at["passages"][string(passage)?]["points_mm"]
            [spec.get("end").and_then(Value::as_u64).unwrap_or(0) as usize])?
    } else if let Some(id) = spec.get("terminal") {
        point(at, string(id)?)?
    } else {
        let (lo, hi) = bounds(part(at, string(&spec["part"])?)?)?;
        let f = spec.get("fraction").map(v).transpose()?.unwrap_or([0.5; 3]);
        [
            lo[0] + (hi[0] - lo[0]) * f[0],
            lo[1] + (hi[1] - lo[1]) * f[1],
            lo[2] + (hi[2] - lo[2]) * f[2],
        ]
    };
    Ok(add(
        p,
        spec.get("offset").map(v).transpose()?.unwrap_or([0.; 3]),
    ))
}
fn put(
    at: &mut Value,
    id: &str,
    part: &str,
    p: V,
    outward: V,
    kind: &str,
    basis: &str,
    status: &str,
    pin: Value,
) {
    let pin = pin.as_str().map(str::to_owned).unwrap_or_else(|| {
        if pin.is_null() {
            String::new()
        } else {
            pin.to_string()
        }
    });
    at["terminals"][id] = json!({"id":id,"part":part,"point":p,"outward":unit(outward),"kind":kind,"basis":basis,"status":status,"pin":pin});
}
fn frame(
    at: &mut Value,
    root: &Path,
    name: &str,
    reference: &str,
    turn_input: &Value,
) -> Result<Value> {
    if let Some(pose) = at["frames_data"].get(name) {
        return Ok(pose.clone());
    }
    let mut explicit = module("above_core_wiring", "frame", json!([name]))?;
    if explicit.is_null() {
        explicit = module("above_core", "specification", json!([]))?["parts"]
            .get(name)
            .cloned()
            .unwrap_or(Value::Null);
    }
    let rotation = if explicit.is_null() {
        turns(turn_input)?
    } else {
        explicit["rotation"].clone()
    };
    let source = provider(json!({"kind":"reference_bounds","path":reference,"rotation":rotation}))?;
    let (mut a, mut b) = (v(&source[0])?, v(&source[1])?);
    let (c, d) = bounds(part(at, name)?)?;
    let reference = Path::new(reference)
        .strip_prefix(root)
        .unwrap_or(Path::new(reference))
        .to_string_lossy()
        .into_owned();
    let translation = if explicit.is_null() {
        sub(centre(part(at, name)?)?, mul(add(a, b), 0.5))
    } else {
        v(&explicit["translation_mm"])?
    };
    let residual = (0..3)
        .map(|i| ((b[i] - a[i]) - (d[i] - c[i])).abs())
        .fold(0., f64::max);
    let record = if explicit.is_null() {
        json!({"reference":reference,"turns":turn_input,"translation_mm":translation,"maximum_extent_residual_mm":residual})
    } else {
        a = add(a, translation);
        b = add(b, translation);
        json!({"reference":reference,"basis":"Explicit production native frame","rotation":rotation,"translation_mm":translation,"maximum_extent_residual_mm":residual,"maximum_bounds_residual_mm":(0..3).flat_map(|i|[(a[i]-c[i]).abs(),(b[i]-d[i]).abs()]).fold(0.,f64::max)})
    };
    at["frame_checks"][name] = record;
    let pose = json!({"rotation":rotation,"translation_mm":translation});
    at["frames_data"][name] = pose.clone();
    Ok(pose)
}
fn frame_ea(
    at: &mut Value,
    root: &Path,
    name: &str,
    reference: &str,
    turns: &str,
) -> Result<Value> {
    let reference = ea(reference)?;
    let turns = ea(turns)?;
    frame(at, root, name, string(&reference)?, &turns)
}
fn apply(
    at: &mut Value,
    id: &str,
    part: &str,
    pose: &Value,
    p: V,
    a: V,
    kind: &str,
    basis: &str,
    status: &str,
    pin: Value,
) -> Result<()> {
    put(
        at,
        id,
        part,
        carry(pose, p)?,
        rotate(&pose["rotation"], a)?,
        kind,
        basis,
        status,
        pin,
    );
    Ok(())
}
fn board(at: &mut Value, root: &Path) -> Result<()> {
    let data = load(root, "hardware/wiring/installed/connector-map.json")?;
    at["pcb_reference"] = data["source_sha256"].clone();
    let pose = frame_ea(at, root, "pcba", "PCBA_STEP", "PCBA_TURN")?;
    let centre = ea("_pcba._centre")?;
    let top = number(&ea("_pcba._thickness")?)?;
    for (owner, entry) in data["connectors"].as_object().context("board connectors")? {
        if owner == "J8" {
            continue;
        }
        for pin in rows(&entry["pins"])? {
            let x = number(&pin["xy_mm"][0])?;
            let y = number(&pin["xy_mm"][1])?;
            let label = string(&pin["label"])?;
            let mut local = [x - number(&centre[0])?, y - number(&centre[1])?, top + 9.8];
            let mut direction = [0., 0., 1.];
            let mut basis = "connector-map.json fabricated physical pad and native board pose; JST XH nominal 9.8 mm assembled height";
            if owner == "J10" {
                let b = &entry["component_glb_bounds_mm"];
                local = [
                    number(&b[1])? - number(&centre[0])?,
                    y - number(&centre[1])?,
                    top + (number(&b[5])? - 0.7) * 0.4,
                ];
                direction = [1., 0., 0.];
                basis = "KF301 native component envelope, +X side wire entry; mouth height nominal, separate from screw axis";
            }
            apply(
                at,
                &format!("{owner}.{label}"),
                "pcba",
                &pose,
                local,
                direction,
                if owner == "J10" { "screw" } else { "JST-XH" },
                basis,
                "nominal",
                pin["number"].clone(),
            )?;
        }
    }
    Ok(())
}
fn valves(at: &mut Value, root: &Path) -> Result<()> {
    for letter in "ABCDEFGHIJK".chars() {
        let name = if letter == 'K' {
            "vk-solenoid".into()
        } else if "AB".contains(letter) {
            format!("valve-v-{}", letter.to_lowercase())
        } else {
            format!("coil-v-{}", letter.to_lowercase())
        };
        let body = part(at, &name)?.clone();
        let solids = rows(&body["solids"])?;
        let mut tabs = Vec::new();
        for solid in solids {
            let (lo, hi) = bounds(solid)?;
            let mut dims = (0..3).map(|i| hi[i] - lo[i]).collect::<Vec<_>>();
            dims.sort_by(f64::total_cmp);
            if (dims[0] - 0.8).abs() < 0.02
                && (dims[1] - 6.3).abs() < 0.05
                && (dims[2] - 8.6).abs() < 0.05
            {
                tabs.push(solid);
            }
        }
        if tabs.len() == 2 {
            let bulk = solids
                .iter()
                .max_by(|a, b| {
                    a["volume_mm3"]
                        .as_f64()
                        .unwrap_or(0.)
                        .total_cmp(&b["volume_mm3"].as_f64().unwrap_or(0.))
                })
                .context("valve main body")?;
            let root = centre(bulk)?;
            let mut ends = Vec::new();
            for tab in tabs {
                let (lo, hi) = bounds(tab)?;
                let c = centre(tab)?;
                let axis = (0..3)
                    .max_by(|&i, &j| (hi[i] - lo[i]).total_cmp(&(hi[j] - lo[j])))
                    .unwrap();
                let sign = if c[axis] > root[axis] { 1. } else { -1. };
                let mut p = c;
                p[axis] = if sign > 0. { hi[axis] } else { lo[axis] };
                let mut a = [0.; 3];
                a[axis] = sign;
                ends.push((p, a));
            }
            ends.sort_by(|a, b| a.0[0].abs().total_cmp(&b.0[0].abs()));
            for (label, (mut p, mut axis)) in ["positive", "negative"].into_iter().zip(ends) {
                let aft = "CDGJ".contains(letter);
                if aft {
                    p = sub(p, mul(axis, 4.3));
                    axis = [0., 1., 0.];
                }
                put(
                    at,
                    &format!("V-{letter}.{label}"),
                    &name,
                    p,
                    axis,
                    "female-disconnect",
                    if aft {
                        "Native tab engagement region; aft wire exit with flexible tab/disconnect"
                    } else {
                        "Actual native 6.3 × 0.8 mm metal tab, tip on its long axis; inboard tab assigned positive"
                    },
                    if aft { "nominal" } else { "modeled" },
                    Value::Null,
                );
            }
        } else if "ABK".contains(letter) {
            let reference = provider(json!({"kind":"valve_reference"}))?;
            let pose = frame(at, root, &name, string(&reference)?, &json!([]))?;
            let mut entries = Vec::new();
            for sx in [-1., 1.] {
                entries.push((
                    carry(&pose, [sx * 7.45, 27.1, 52.2])?,
                    rotate(&pose["rotation"], [0., 1., 0.])?,
                ));
            }
            entries.sort_by(|a, b| a.0[0].abs().total_cmp(&b.0[0].abs()));
            for (label, (p, a)) in ["positive", "negative"].into_iter().zip(entries) {
                put(
                    at,
                    &format!("V-{letter}.{label}"),
                    &name,
                    p,
                    a,
                    "female-disconnect",
                    "Native reference tab through explicit production valve pose",
                    "modeled",
                    Value::Null,
                );
            }
        } else {
            bail!(
                "{name}: expected two separate metal spades, found {}",
                tabs.len()
            );
        }
    }
    Ok(())
}
fn wagos(at: &mut Value, root: &Path) -> Result<()> {
    let interfaces = hsm_kernel::reads::json(
        root.join("hardware/reference/wago-221/terminal-interfaces.json"),
    )?;
    let pitch = number(&interfaces["pole_pitch_mm"])?;
    let entry_z = number(&interfaces["entry_center_z_mm"])?;
    let placements = module("above_core_wiring", "placements", json!([]))?;
    for (name, row) in placements.as_object().context("junction placements")? {
        if !name.starts_with("wago-") {
            continue;
        }
        let size = string(&row["size"])?;
        let reference = call("ea", "wago_step", json!([size]))?;
        let turns = ea(if name.contains("reeds-") || name == "wago-sensors" {
            "WAGO_TURN_WEST"
        } else {
            "WAGO_TURN"
        })?;
        let pose = frame(at, root, name, string(&reference)?, &turns)?;
        let (d, h, n, rows) = match size {
            "413" => (18.6, 8.4, 3, 1),
            "415" => (18.6, 8.4, 5, 1),
            "420" => (18.3, 15.8, 10, 2),
            _ => bail!("WAGO size {size}"),
        };
        let cols = n / rows;
        for i in 0..n {
            let p = [
                ((i % cols) as f64 - (cols - 1) as f64 / 2.) * pitch,
                d / 2.,
                if i / cols == 0 { entry_z } else { h - entry_z },
            ];
            apply(
                at,
                &format!("{name}.{}", i + 1),
                name,
                &pose,
                p,
                [0., 1., 0.],
                "WAGO-port",
                "Modeled wire mouths through the native connector pose with nominal electrical pole order",
                "nominal",
                json!(i + 1),
            )?;
        }
    }
    let rotation = get("above_core_wiring", "PORTS_FORE")?;
    for (name, point) in final_joins().as_object().unwrap() {
        let pose = json!({"rotation":rotation,"translation_mm":point});
        for i in 0..3 {
            apply(
                at,
                &format!("join-{name}.{}", i + 1),
                &format!("wiring-junction-{name}"),
                &pose,
                [
                    (i as f64 - 1.) * pitch,
                    18.6 / 2.,
                    entry_z,
                ],
                [0., 1., 0.],
                "WAGO-port",
                "Modeled wire mouth through the final connector pose",
                "nominal",
                json!(i + 1),
            )?;
        }
    }
    Ok(())
}
pub fn final_joins() -> Value {
    json!({"compressor-h":[-65.,247.,290.5],"compressor-n":[-85.,247.,290.5],"pump-positive":[-45.,255.,278.]})
}
fn power(at: &mut Value, root: &Path) -> Result<()> {
    let supply = hsm_kernel::reads::json(
        root.join("hardware/reference/meanwell-irm90/replica-parameters.json"),
    )?;
    let pose = frame_ea(at, root, "psu", "PSU_STEP", "PSU_TURN")?;
    for (row_name, side) in [("ac", 1.), ("dc", -1.)] {
        let row = rows(&supply["terminals"])?
            .iter()
            .find(|row| row["side"].as_f64() == Some(side))
            .with_context(|| format!("supply {row_name} terminal row"))?;
        let count = row["poles"].as_u64().context("supply terminal count")? as usize;
        let pitch = number(&row["pitch"])?;
        let interface = &supply["terminal_interfaces"][row_name];
        let center = v(&interface["wire_center"])?;
        let outward = v(&interface["wire_axis"])?;
        for label in ["L", "N", "V12", "GND"] {
            let port = &supply["electrical_ports"][label];
            if port["row"] != row_name {
                continue;
            }
            let pole = port["pole"].as_u64().context("supply electrical pole")? as usize;
            let mut point = center;
            point[0] += (pole as f64 - (count - 1) as f64 / 2.) * pitch;
            apply(
                at,
                &format!("psu.{label}"),
                "psu",
                &pose,
                point,
                outward,
                "screw",
                "Manufacturer wire mouths, pitch and ST top-view terminal labels",
                "nominal",
                Value::Null,
            )?;
        }
    }
    let relay = hsm_kernel::reads::json(
        root.join("hardware/reference/teyleten-relay/scan-datums.json"),
    )?;
    let offsets = rows(&relay["replica_geometry"]["terminal_shape"]["terminal_y_mm"])?
        .iter()
        .map(number)
        .collect::<Result<Vec<_>>>()?;
    for (index, turn) in [(1, "RELAY_TURN"), (2, "RELAY2_TURN")] {
        let name = format!("relay-{index}");
        let pose = frame_ea(at, root, &name, "RELAY_STEP", turn)?;
        for (group, labels) in [
            ("contacts", ["COM", "NO", "NC"]),
            ("logic", ["V5", "GND", "IN"]),
        ] {
            let interface = &relay["ports"][group];
            let center = v(&interface["point_mm"])?;
            let outward = v(&interface["outward_axis"])?;
            let across = [-outward[1], outward[0], 0.];
            let mut mouths = offsets
                .iter()
                .map(|&offset| add(center, mul(across, offset)))
                .collect::<Vec<_>>();
            mouths.sort_by(|a, b| a[1].total_cmp(&b[1]));
            for (ordinal, label) in labels.into_iter().enumerate() {
                apply(
                    at,
                    &format!("{name}.{label}"),
                    &name,
                    &pose,
                    *mouths.get(ordinal).context("relay terminal mouth")?,
                    outward,
                    "screw",
                    "Fitted terminal wire mouths with nominal electrical pole order",
                    "nominal",
                    Value::Null,
                )?;
            }
        }
    }
    let reference = ea("C14_STEP")?;
    let pose = frame(at, root, "c14-inlet", string(&reference)?, &json!([]))?;
    for (label, x, z) in [("L", -6.7, 2.45), ("PE", 0.35, -2.6), ("N", 7.1, 2.65)] {
        apply(
            at,
            &format!("c14.{label}"),
            "c14-inlet",
            &pose,
            [x, -25., z],
            [0., -1., 0.],
            "solder-tab",
            "Scanned tab positions; L/N assignment awaits physical moulded marks",
            "nominal",
            Value::Null,
        )?;
    }
    let pose = frame(
        at,
        root,
        "thermal-fuse",
        &root
            .join("hardware/reference/sf76e-thermal-fuse/sf76e-thermal-fuse.step")
            .to_string_lossy(),
        &ea("FUSE_TURN")?,
    )?;
    let bundles = load(root, "hardware/wiring/installed/bundle-routes.json")?;
    let leads = &bundles["compressor-cord"]["fuse_leads"];
    let body_l = number(&ea("_fuse.BODY_L")?)?;
    let stub = number(&ea("_fuse.LEAD_STUB")?)?;
    let z = number(&ea("_fuse.AXIS_Z")?)?;
    for (label, sign) in [("in", -1.), ("out", 1.)] {
        let p = carry(&pose, [sign * (body_l / 2. + stub), 0., z])?;
        let mut lead = leads[label].clone();
        let points = points(&lead["offsets_mm"])?
            .into_iter()
            .map(|v| add(p, v))
            .collect::<Vec<_>>();
        lead["points_mm"] = json!(points);
        lead["native_stub_tip_mm"] = json!(p);
        lead["lead_diameter_mm"] = ea("_fuse.LEAD_D")?;
        lead["native_straight_mm"] = json!(stub);
        lead["available_lead_mm"] = ea(if label == "in" {
            "_fuse.LEAD_LONG"
        } else {
            "_fuse.LEAD_SHORT"
        })?;
        at["fuse_leads"][label] = lead;
        put(
            at,
            &format!("fuse.{label}"),
            "thermal-fuse",
            *points.last().context("fuse lead offsets")?,
            [1., 0., 0.],
            "insulated-splice",
            "Proposed splice beyond dressed SF76E lead; native first 3 mm remain straight",
            "nominal",
            Value::Null,
        );
    }
    Ok(())
}
fn pump_motors(at: &mut Value) -> Result<()> {
    for bank in ["a", "b"] {
        let name = format!("pump-{bank}-motor");
        let (_, hi) = bounds(part(at, &name)?)?;
        let c = centre(part(at, &name)?)?;
        for (i, dx) in [(1, -4.), (2, 4.)] {
            put(
                at,
                &format!("pump-{bank}.{i}"),
                &name,
                [c[0] + dx, c[1], hi[2]],
                [0., 0., 1.],
                "female-disconnect",
                "Faston receptacle on the motor tab, at the native rear-cap plane inside the integral mount terminal room; actual motor tabs unlocated",
                "unlocated",
                json!(i),
            );
        }
    }
    Ok(())
}
fn sensors(at: &mut Value, root: &Path) -> Result<()> {
    let pose = frame_ea(at, root, "mq6-sensor", "MQ6_STEP", "MQ6_TURN")?;
    for i in 0..4 {
        apply(
            at,
            &format!("mq6.{}", i + 1),
            "mq6-sensor",
            &pose,
            [-13., (i as f64 - 1.5) * 2.54, 0.],
            [0., 0., -1.],
            "pin-header",
            "Native header tips; VCC/GND/DO/AO assignment follows module description",
            "nominal",
            json!(i + 1),
        )?;
    }
    let pose = frame_ea(at, root, "digiten-flow", "DIGITEN_STEP", "DIGITEN_TURN")?;
    let exit = call("ea", "_digiten.wire_exit", json!([]))?;
    let local = v(&exit[0])?;
    let outward = v(&exit[1])?;
    for (i, label) in ["V", "PULSE", "GND"].into_iter().enumerate() {
        apply(
            at,
            &format!("flow.{label}"),
            "digiten-flow",
            &pose,
            [local[0] + (i as f64 - 1.) * 1.8, local[1], local[2]],
            outward,
            "factory-lead",
            "Observed wire-exit boss; individual lead spacing nominal",
            "nominal",
            Value::Null,
        )?;
    }
    for (label, name) in [
        ("carbonator", "probe-carbonator-ds18b20"),
        ("coil", "probe-coil-ds18s20"),
    ] {
        let (lo, _) = bounds(part(at, name)?)?;
        let c = centre(part(at, name)?)?;
        let tank = centre(part(at, "carbonator-tube")?)?;
        let radial = unit([c[0] - tank[0], c[1] - tank[1], 0.]);
        let joint = add([c[0], c[1], lo[2]], mul(radial, 7.));
        let tangent = [-radial[1], radial[0], 0.];
        for (i, pin) in ["V", "DATA", "GND"].into_iter().enumerate() {
            let sign = if label == "coil" { -1. } else { 1. };
            put(
                at,
                &format!("temp-{label}.{pin}"),
                &format!("cold-core/{name}"),
                add(joint, mul(tangent, sign * (i as f64 - 1.) * 1.85)),
                radial,
                "TO-92-lead",
                "Proposed insulated solder joints 7 mm radially outside the probe, with a tangential 1.85 mm lead row; bare lead dressing and pin assignment nominal",
                "nominal",
                Value::Null,
            );
        }
    }
    for (bank, count) in [("a", 4), ("b", 4), ("carb", 2)] {
        for i in 1..=count {
            let name = format!("reed-{bank}-{i}");
            let (lo, hi) = bounds(part(at, &name)?)?;
            let c = centre(part(at, &name)?)?;
            for (label, z, mut axis) in [
                ("signal", hi[2], [0., 0., 1.]),
                ("GND", lo[2], [0., 0., -1.]),
            ] {
                let mut p = [c[0], c[1], z];
                let mut basis = "Reed capture-envelope ends; soldered lead extensions and insulation are proposed";
                if bank == "carb" {
                    let tank = centre(part(at, "carbonator-tube")?)?;
                    let radial = unit([c[0] - tank[0], c[1] - tank[1], 0.]);
                    let tangent = [-radial[1], radial[0], 0.];
                    p = add(p, mul(radial, 8.));
                    axis = radial;
                    basis = "Proposed insulated splice outside the coil; the 14 mm reed capture envelope includes lead/tape room, not measured glass ends";
                    if label == "GND" {
                        p = add(
                            add([c[0], c[1], z - 3.], mul(radial, 8.)),
                            mul(tangent, 2.8),
                        );
                        axis = [0., 0., 1.];
                        basis = "Proposed insulated tap on the continuous carbonator-reed common, 2.8 mm beside the signal splice row and 3 mm below its capture envelope; local bare lead dressing nominal";
                    }
                } else if label == "GND" {
                    p = [c[0] - 2.8, c[1], z - 3.];
                    axis = [0., 0., 1.];
                    basis = "Proposed insulated tap on the continuous common spine, 2.8 mm along the channel width beside the reed axis and 3 mm below its capture envelope; local bare lead dressing nominal";
                }
                put(
                    at,
                    &format!("{name}.{label}"),
                    &format!("cold-core/{name}"),
                    p,
                    axis,
                    if label == "GND" {
                        "insulated-splice"
                    } else {
                        "reed-lead"
                    },
                    basis,
                    "nominal",
                    Value::Null,
                );
            }
        }
    }
    let pose = frame(
        at,
        root,
        "display",
        &root
            .join("hardware/reference/waveshare-43b-display/waveshare-43b-display.step")
            .to_string_lossy(),
        &json!([ea("DISPLAY_TILT")?]),
    )?;
    let interfaces = hsm_kernel::reads::json(
        root.join("hardware/reference/waveshare-43b-display/terminal-interfaces.json"),
    )?;
    let row = &interfaces["row"];
    let mouth_y = number(&row["mouth_y_mm"])?;
    let inner_y = number(&row["entry_inner"]["y_mm"])?;
    let inner_z = number(&row["entry_inner"]["z_mm"])?;
    let outer_y = number(&row["entry_outer"]["y_mm"])?;
    let outer_z = number(&row["entry_outer"]["z_mm"])?;
    let mouth_z = inner_z + (mouth_y - inner_y) / (outer_y - inner_y) * (outer_z - inner_z);
    let first_x = number(&row["first_x_mm"])?;
    let pitch = number(&row["pitch_mm"])?;
    for label in ["B", "A", "GND", "V12"] {
        let port = &interfaces["ports"][label];
        let pole = number(&port["pole_index"])?;
        apply(
            at,
            &format!("display.{label}"),
            "display",
            &pose,
            [first_x + pole * pitch, mouth_y, mouth_z],
            v(&row["outward_axis"])?,
            "display-terminal",
            "Supplier-derived connector mouth and printed pole label; received-part net assignment and conductor continuity unqualified",
            "nominal",
            port["board_label"].clone(),
        )?;
    }
    let (lo, _) = bounds(part(at, "keystone-jack")?)?;
    let c = centre(part(at, "keystone-jack")?)?;
    for i in 2..=5 {
        put(
            at,
            &format!("keystone.{i}"),
            "keystone-jack",
            [c[0] + (i as f64 - 3.5) * 2.54, lo[1], c[2]],
            [0., -1., 0.],
            "IDC",
            "Native jack envelope; individual IDC locations nominal, electrical pin map from cable schedule",
            "nominal",
            json!(i),
        );
    }
    Ok(())
}
pub fn bond() -> Result<Value> {
    let plates = ea("_cca._V.top_plate_z")?;
    let mut d = call("ea", "_cca._V._bond.datums", json!([plates[1]]))?;
    let pose = module("above_core", "cap_lid_pose", json!([]))?;
    let offset = number(&ea("_cci.foam_shell_outer_height")?)?
        + number(&get("_foam_cap", "top_cap_height")?)?;
    for key in ["contact_point_mm", "wire_exit_mm"] {
        let [x, y, z] = v(&d[key])?;
        d[key] = json!(carry(&pose, [-x, -y, z - offset])?);
    }
    for key in ["contact_outward", "wire_outward"] {
        let [x, y, z] = v(&d[key])?;
        d[key] = json!(rotate(&pose["rotation"], [-x, -y, z])?);
    }
    Ok(d)
}
fn boundaries(at: &mut Value) -> Result<()> {
    let body = part(at, "compressor")?;
    let mut found = None;
    for s in rows(&body["solids"])? {
        let (lo, hi) = bounds(s)?;
        let mut dims = (0..3).map(|i| hi[i] - lo[i]).collect::<Vec<_>>();
        dims.sort_by(f64::total_cmp);
        if dims
            .iter()
            .zip([27.5, 45., 45.])
            .all(|(a, b)| (a - b).abs() < 0.1)
        {
            found = Some(s.clone());
            break;
        }
    }
    let power = found.context("compressor power cover")?;
    let (_, hi) = bounds(&power)?;
    let c = centre(&power)?;
    for (i, label) in ["H", "N", "PE"].into_iter().enumerate() {
        put(
            at,
            &format!("compressor.{label}"),
            "compressor",
            [hi[0], c[1] + (i as f64 - 1.) * 5., hi[2] - 7.],
            [1., 0., 0.],
            "donor-interface",
            "Proposed external landing region beside retained native power box; exact Unit B lead and earth contacts unlocated",
            "unlocated",
            Value::Null,
        );
    }
    let (lo, hi) = bounds(part(at, "condenser+fan")?)?;
    for (i, label) in ["positive", "negative"].into_iter().enumerate() {
        put(
            at,
            &format!("fan.{label}"),
            "condenser+fan",
            [hi[0] - 6. - i as f64 * 2., lo[1] + 30., hi[2] + 4.],
            [0., 1., 0.],
            "donor-lead",
            "Condenser crown approach; donor lead and terminal unlocated",
            "unlocated",
            Value::Null,
        );
    }
    let (_, hi) = bounds(part(at, "g-ganen-pump")?)?;
    let c = centre(part(at, "g-ganen-pump")?)?;
    for (i, label) in ["positive", "negative"].into_iter().enumerate() {
        put(
            at,
            &format!("diaphragm.{label}"),
            "g-ganen-pump",
            [c[0] + (i as f64 - 0.5) * 4., hi[1], c[2]],
            [0., 1., 0.],
            "factory-lead",
            "Proposed motor-lead approach; scan records casing/lead transition regions, not terminal polarity",
            "unlocated",
            Value::Null,
        );
    }
    let d = bond()?;
    put(
        at,
        "carbonator.PE",
        &format!("cold-core/{}", string(&d["body"])?),
        v(&d["wire_exit_mm"])?,
        v(&d["wire_outward"])?,
        "ring-barrel",
        "M3 closed ring on the tapped upper tube rim; shared rim/fastener and ring-barrel datums",
        "modeled",
        Value::Null,
    );
    Ok(())
}
fn passages(at: &mut Value) -> Result<()> {
    let spec = module("above_core", "specification", json!([]))?;
    let face = number(&spec["cap_face_z_mm"])?;
    let pose = module("above_core", "cap_lid_pose", json!([]))?;
    let conduits = ea("_cci.cap_cable_conduits")?;
    let height = number(&ea("_foam.lid_total_height")?)?;
    let bore = 2. * number(&ea("_cci.cap_conduit_bore_radius")?)?;
    for (name, xy) in conduits.as_object().context("cable conduits")? {
        let corridor = module("_above_core_mounts", "cable_guide_points", json!([name]))?;
        let lower = v(&corridor["points_mm"][0])?;
        let floor = [lower[0], lower[1], lower[2] + 1.];
        let upper = carry(&pose, [number(&xy[0])?, number(&xy[1])?, height])?;
        at["passages"][name] = json!({"points_mm":[[upper[0],upper[1],face+1.6],[floor[0],floor[1],floor[2]-1.6]],"upper_mouth_mm":upper,"lower_entry_mm":floor,"corridor_points_mm":corridor["points_mm"],"corridor_bend_radius_mm":corridor["bend_radius_mm"],"bore_diameter_mm":bore,"basis":"Native top-cap cable conduit, carried into the installed frame"});
    }
    let fixed = provider(json!({"kind":"fixed_wiring_passages"}))?;
    at["passages"].as_object_mut().unwrap().extend(
        fixed
            .as_object()
            .context("fixed pump wiring passages")?
            .clone(),
    );
    Ok(())
}
pub fn init(scene: &Value) -> Result<Value> {
    let mut filtered = serde_json::Map::new();
    let mut source_names = serde_json::Map::new();
    for (name, body) in scene.as_object().context("physical scene bodies")? {
        if !["wire-", "wiring-", "terminal-"]
            .iter()
            .any(|p| name.starts_with(p))
        {
            filtered.insert(name.replace('_', "-"), body.clone());
            source_names.insert(name.replace('_', "-"), json!(name));
        }
    }
    Ok(
        json!({"scene":filtered,"source_names":source_names,"terminals":{},"frames_data":{},"frame_checks":{},"parts":{},"fuse_leads":{},"passages":{},"pcb_reference":null}),
    )
}
/// Every terminal, reference frame, fuse lead and cable passage, resolved onto the scene `at`.
pub fn resolve(mut at: Value, root: &Path) -> Result<Value> {
    board(&mut at, root)?;
    valves(&mut at, root)?;
    wagos(&mut at, root)?;
    power(&mut at, root)?;
    pump_motors(&mut at)?;
    sensors(&mut at, root)?;
    boundaries(&mut at)?;
    passages(&mut at)?;
    Ok(at)
}
