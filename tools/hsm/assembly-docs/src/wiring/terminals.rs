use super::*;
use model::{V, add, dot, mul, sub, unit, v};
use serde::{Deserialize, Serialize};
use sources::{PORTS_FORE, Sources};

/// A rotation and translation that carry a part's own frame into the installed frame.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Pose {
    pub rotation: [V; 3],
    pub translation_mm: V,
}

impl Pose {
    /// `p` turned into the installed frame.
    pub fn rotate(&self, p: V) -> V {
        rotate(&self.rotation, p)
    }

    /// `p` carried into the installed frame.
    pub fn carry(&self, p: V) -> V {
        add(self.rotate(p), self.translation_mm)
    }
}

/// `p` turned by the rows of `matrix`.
pub fn rotate(matrix: &[V; 3], p: V) -> V {
    [dot(matrix[0], p), dot(matrix[1], p), dot(matrix[2], p)]
}

/// One turn of a part from its reference's frame: an axis and the degrees about it.
pub type Turn = (V, f64);

/// The rotation `list` makes, each turn applied after the ones before it.
pub fn turns(list: &[Turn]) -> [V; 3] {
    let mut rotation = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]];
    for &(axis, degrees) in list {
        let [x, y, z] = unit(axis);
        let angle = degrees.to_radians();
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
    rotation
}

/// One separate solid of an installed body: its bounds and, where it is measured, its volume.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Solid {
    pub lower: V,
    pub upper: V,
    pub volume_mm3: Option<f64>,
}

impl Solid {
    fn centre(&self) -> V {
        mul(add(self.lower, self.upper), 0.5)
    }
}

/// An installed body as the terminals read it: its separate solids.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Body {
    pub solids: Vec<Solid>,
}

impl Body {
    /// The bounds over the body's solids.
    pub fn bounds(&self) -> Result<(V, V)> {
        let mut lo = [f64::INFINITY; 3];
        let mut hi = [f64::NEG_INFINITY; 3];
        for s in &self.solids {
            for i in 0..3 {
                lo[i] = lo[i].min(s.lower[i]);
                hi[i] = hi[i].max(s.upper[i]);
            }
        }
        ensure!(!self.solids.is_empty(), "body has no solid bounds");
        Ok((lo, hi))
    }

    fn centre(&self) -> Result<V> {
        let (a, b) = self.bounds()?;
        Ok(mul(add(a, b), 0.5))
    }
}

/// One terminal of the wiring: where a conductor lands on a part and which way it leaves.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Terminal {
    pub id: String,
    pub part: String,
    pub point: V,
    pub outward: V,
    pub kind: String,
    pub basis: String,
    pub status: String,
    pub pin: String,
}

/// How a part's reference frame was resolved onto its installed body, for the review.
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(untagged)]
pub enum FrameCheck {
    /// The pose is written down; the reference is checked against the body it places.
    Explicit {
        reference: String,
        basis: String,
        rotation: [V; 3],
        translation_mm: V,
        maximum_extent_residual_mm: f64,
        maximum_bounds_residual_mm: f64,
    },
    /// The reference is turned and centred on the body.
    Fitted {
        reference: String,
        turns: Vec<Turn>,
        translation_mm: V,
        maximum_extent_residual_mm: f64,
    },
}

/// A thermal-fuse lead as its bundle route dresses it.
#[derive(Clone, Debug, Deserialize)]
struct FuseDressing {
    offsets_mm: Vec<V>,
    bend_radius_mm: f64,
}

/// A thermal-fuse lead from its native stub to its splice.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FuseLead {
    pub offsets_mm: Vec<V>,
    pub bend_radius_mm: f64,
    pub points_mm: Vec<V>,
    pub native_stub_tip_mm: V,
    pub lead_diameter_mm: f64,
    pub native_straight_mm: f64,
    pub available_lead_mm: Option<f64>,
}

/// A cable passage through the cap lid or the front top.
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(untagged)]
pub enum Passage {
    /// A cap conduit, carried into the installed frame.
    Cap {
        points_mm: Vec<V>,
        upper_mouth_mm: V,
        lower_entry_mm: V,
        corridor_points_mm: Vec<V>,
        corridor_bend_radius_mm: f64,
        bore_diameter_mm: f64,
        basis: String,
    },
    /// A passage the front top is cut with, as its file writes it.
    Fixed {
        points_mm: Vec<V>,
        #[serde(flatten)]
        detail: BTreeMap<String, Value>,
    },
}

impl Passage {
    /// The stations a conductor passes through, in order.
    pub fn points(&self) -> &[V] {
        match self {
            Passage::Cap { points_mm, .. } | Passage::Fixed { points_mm, .. } => points_mm,
        }
    }
}

/// What the wiring is routed from: the installed bodies, every terminal resolved onto them, the
/// frames that placed the references, the dressed fuse leads and the cable passages.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct State {
    pub scene: BTreeMap<String, Body>,
    pub terminals: BTreeMap<String, Terminal>,
    pub frames_data: BTreeMap<String, Pose>,
    pub frame_checks: BTreeMap<String, FrameCheck>,
    pub fuse_leads: BTreeMap<String, FuseLead>,
    pub passages: BTreeMap<String, Passage>,
    pub pcb_reference: Value,
}

impl State {
    /// The installed body `name`, in the enclosure or in the cold core.
    pub fn part(&self, name: &str) -> Result<&Body> {
        self.scene
            .get(name)
            .or_else(|| self.scene.get(&format!("cold-core/{name}")))
            .with_context(|| format!("installed body {name}"))
    }

    /// The terminal `id`.
    pub fn terminal(&self, id: &str) -> Result<&Terminal> {
        self.terminals
            .get(id)
            .with_context(|| format!("wiring terminal {id}"))
    }

    /// Where the terminal `id` lands.
    pub fn point(&self, id: &str) -> Result<V> {
        Ok(self.terminal(id)?.point)
    }

    /// The station `index` of the cable passage `name`.
    pub fn passage_point(&self, name: &str, index: usize) -> Result<V> {
        self.passages
            .get(name)
            .and_then(|passage| passage.points().get(index))
            .copied()
            .with_context(|| format!("cable passage {name} station {index}"))
    }

    /// The point a route station names: a written point, a passage's end, a terminal, or a
    /// fraction of a body's bounds, moved by its offset.
    pub fn station(&self, spec: &Value) -> Result<V> {
        let p = if let Some(value) = spec.get("point_mm") {
            v(value)?
        } else if let Some(passage) = spec.get("passage") {
            self.passage_point(
                string(passage)?,
                spec.get("end").and_then(Value::as_u64).unwrap_or(0) as usize,
            )?
        } else if let Some(id) = spec.get("terminal") {
            self.point(string(id)?)?
        } else {
            let (lo, hi) = self.part(string(&spec["part"])?)?.bounds()?;
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
}

/// A pin as a source document numbers or labels it.
fn pin_text(pin: &Value) -> String {
    match pin {
        Value::String(text) => text.clone(),
        Value::Null => String::new(),
        other => other.to_string(),
    }
}
fn put(
    at: &mut State,
    id: &str,
    part: &str,
    p: V,
    outward: V,
    kind: &str,
    basis: &str,
    status: &str,
    pin: &str,
) {
    at.terminals.insert(
        id.to_owned(),
        Terminal {
            id: id.to_owned(),
            part: part.to_owned(),
            point: p,
            outward: unit(outward),
            kind: kind.to_owned(),
            basis: basis.to_owned(),
            status: status.to_owned(),
            pin: pin.to_owned(),
        },
    );
}
/// The pose that carries the reference at `reference` onto the installed body `name`: the
/// written-down pose where there is one, else the reference turned by `turned` and centred on
/// the body.
fn frame(
    src: &Sources,
    at: &mut State,
    root: &Path,
    name: &str,
    reference: &str,
    turned: Option<&[Turn]>,
) -> Result<Pose> {
    if let Some(pose) = at.frames_data.get(name) {
        return Ok(pose.clone());
    }
    let explicit = src.written_pose(name)?;
    let rotation = match (&explicit, turned) {
        (Some(pose), _) => pose.rotation,
        (None, Some(list)) => turns(list),
        (None, None) => bail!("{name} is placed by a native pose that nothing writes down"),
    };
    let (mut a, mut b) = src.reference_bounds(reference, &rotation)?;
    let (c, d) = at.part(name)?.bounds()?;
    let reference = Path::new(reference)
        .strip_prefix(root)
        .unwrap_or(Path::new(reference))
        .to_string_lossy()
        .into_owned();
    let translation = match &explicit {
        None => sub(at.part(name)?.centre()?, mul(add(a, b), 0.5)),
        Some(pose) => pose.translation_mm,
    };
    let residual = (0..3)
        .map(|i| ((b[i] - a[i]) - (d[i] - c[i])).abs())
        .fold(0., f64::max);
    let record = match &explicit {
        None => FrameCheck::Fitted {
            reference,
            turns: turned.unwrap_or_default().to_vec(),
            translation_mm: translation,
            maximum_extent_residual_mm: residual,
        },
        Some(_) => {
            a = add(a, translation);
            b = add(b, translation);
            FrameCheck::Explicit {
                reference,
                basis: "Explicit production native frame".into(),
                rotation,
                translation_mm: translation,
                maximum_extent_residual_mm: residual,
                maximum_bounds_residual_mm: (0..3)
                    .flat_map(|i| [(a[i] - c[i]).abs(), (b[i] - d[i]).abs()])
                    .fold(0., f64::max),
            }
        }
    };
    at.frame_checks.insert(name.to_owned(), record);
    let pose = Pose {
        rotation,
        translation_mm: translation,
    };
    at.frames_data.insert(name.to_owned(), pose.clone());
    Ok(pose)
}
/// The frame of a part the layout or the plan places by its native pose.
fn frame_placed(
    src: &Sources,
    at: &mut State,
    root: &Path,
    name: &str,
    reference: &Path,
) -> Result<Pose> {
    src.placed(name)?;
    frame(src, at, root, name, &reference.to_string_lossy(), None)
}
fn apply(
    at: &mut State,
    id: &str,
    part: &str,
    pose: &Pose,
    p: V,
    a: V,
    kind: &str,
    basis: &str,
    status: &str,
    pin: &str,
) {
    put(
        at,
        id,
        part,
        pose.carry(p),
        pose.rotate(a),
        kind,
        basis,
        status,
        pin,
    );
}
fn board(src: &Sources, at: &mut State, root: &Path) -> Result<()> {
    let data = load(root, "hardware/wiring/installed/connector-map.json")?;
    at.pcb_reference = data["source_sha256"].clone();
    let pose = frame_placed(src, at, root, "pcba", &src.reference_step("pcba")?)?;
    let centre = src.pcba_centre()?;
    let top = src.pcba_thickness()?;
    for (owner, entry) in data["connectors"].as_object().context("board connectors")? {
        if owner == "J8" {
            continue;
        }
        for pin in rows(&entry["pins"])? {
            let x = number(&pin["xy_mm"][0])?;
            let y = number(&pin["xy_mm"][1])?;
            let label = string(&pin["label"])?;
            let mut local = [x - centre[0], y - centre[1], top + 9.8];
            let mut direction = [0., 0., 1.];
            let mut basis = "connector-map.json fabricated physical pad and native board pose; JST XH nominal 9.8 mm assembled height";
            if owner == "J10" {
                let b = &entry["component_glb_bounds_mm"];
                local = [
                    number(&b[1])? - centre[0],
                    y - centre[1],
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
                &pin_text(&pin["number"]),
            );
        }
    }
    Ok(())
}
fn valves(src: &Sources, at: &mut State, root: &Path) -> Result<()> {
    for letter in "ABCDEFGHIJK".chars() {
        let name = if letter == 'K' {
            "vk-solenoid".into()
        } else if "AB".contains(letter) {
            format!("valve-v-{}", letter.to_lowercase())
        } else {
            format!("coil-v-{}", letter.to_lowercase())
        };
        let body = at.part(&name)?.clone();
        let solids = &body.solids;
        let mut tabs = Vec::new();
        for solid in solids {
            let (lo, hi) = (solid.lower, solid.upper);
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
                    a.volume_mm3
                        .unwrap_or(0.)
                        .total_cmp(&b.volume_mm3.unwrap_or(0.))
                })
                .context("valve main body")?;
            let root = bulk.centre();
            let mut ends = Vec::new();
            for tab in tabs {
                let (lo, hi) = (tab.lower, tab.upper);
                let c = tab.centre();
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
                    "",
                );
            }
        } else if "ABK".contains(letter) {
            let reference = src.valve_reference()?;
            let pose = frame(src, at, root, &name, &reference.to_string_lossy(), Some(&[]))?;
            let mut entries = Vec::new();
            for sx in [-1., 1.] {
                entries.push((
                    pose.carry([sx * 7.45, 27.1, 52.2]),
                    pose.rotate([0., 1., 0.]),
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
                    "",
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
fn wagos(src: &Sources, at: &mut State, root: &Path) -> Result<()> {
    let interfaces = hsm_kernel::reads::json(
        root.join("hardware/reference/wago-221/terminal-interfaces.json"),
    )?;
    let pitch = number(&interfaces["pole_pitch_mm"])?;
    let entry_z = number(&interfaces["entry_center_z_mm"])?;
    let placements = src.placements()?;
    for (name, row) in &placements {
        if !name.starts_with("wago-") {
            continue;
        }
        let size = row.size.as_str();
        let reference = src.wago_reference(size)?;
        let pose = frame(src, at, root, name, &reference.to_string_lossy(), None)?;
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
                &(i + 1).to_string(),
            );
        }
    }
    for (name, point) in FINAL_JOINS {
        let pose = Pose {
            rotation: PORTS_FORE,
            translation_mm: point,
        };
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
                &(i + 1).to_string(),
            );
        }
    }
    Ok(())
}

/// Where each final connection's WAGO stands, by the join it makes.
pub const FINAL_JOINS: [(&str, V); 3] = [
    ("compressor-h", [-65., 247., 290.5]),
    ("compressor-n", [-85., 247., 290.5]),
    ("pump-positive", [-45., 255., 278.]),
];
fn power(src: &Sources, at: &mut State, root: &Path) -> Result<()> {
    let supply = hsm_kernel::reads::json(
        root.join("hardware/reference/meanwell-irm90/replica-parameters.json"),
    )?;
    let pose = frame_placed(src, at, root, "psu", &src.reference_step("psu")?)?;
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
                "",
            );
        }
    }
    let relay = hsm_kernel::reads::json(
        root.join("hardware/reference/teyleten-relay/scan-datums.json"),
    )?;
    let offsets = rows(&relay["replica_geometry"]["terminal_shape"]["terminal_y_mm"])?
        .iter()
        .map(number)
        .collect::<Result<Vec<_>>>()?;
    for index in [1, 2] {
        let name = format!("relay-{index}");
        let pose = frame_placed(src, at, root, &name, &src.relay_reference()?)?;
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
                    "",
                );
            }
        }
    }
    let reference = src.reference_step("c14-inlet")?;
    let pose = frame(src, at, root, "c14-inlet", &reference.to_string_lossy(), Some(&[]))?;
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
            "",
        );
    }
    let pose = frame_placed(
        src,
        at,
        root,
        "thermal-fuse",
        &root.join("hardware/reference/sf76e-thermal-fuse/sf76e-thermal-fuse.step"),
    )?;
    let bundles = load(root, "hardware/wiring/installed/bundle-routes.json")?;
    let leads = &bundles["compressor-cord"]["fuse_leads"];
    let (body_l, case_d) = src.fuse_case()?;
    let stub = src.fuse_lead_stub()?;
    let z = case_d / 2.;
    for (label, sign) in [("in", -1.), ("out", 1.)] {
        let p = pose.carry([sign * (body_l / 2. + stub), 0., z]);
        let dressing: FuseDressing = serde_json::from_value(leads[label].clone())
            .with_context(|| format!("the {label} fuse lead's dressing"))?;
        let points = dressing
            .offsets_mm
            .iter()
            .map(|&v| add(p, v))
            .collect::<Vec<_>>();
        let end = *points.last().context("fuse lead offsets")?;
        at.fuse_leads.insert(
            label.to_owned(),
            FuseLead {
                offsets_mm: dressing.offsets_mm,
                bend_radius_mm: dressing.bend_radius_mm,
                points_mm: points,
                native_stub_tip_mm: p,
                lead_diameter_mm: src.fuse_lead_diameter()?,
                native_straight_mm: stub,
                available_lead_mm: None,
            },
        );
        put(
            at,
            &format!("fuse.{label}"),
            "thermal-fuse",
            end,
            [1., 0., 0.],
            "insulated-splice",
            "Proposed splice beyond dressed SF76E lead; native first 3 mm remain straight",
            "nominal",
            "",
        );
    }
    Ok(())
}
fn pump_motors(at: &mut State) -> Result<()> {
    for bank in ["a", "b"] {
        let name = format!("pump-{bank}-motor");
        let (_, hi) = at.part(&name)?.bounds()?;
        let c = at.part(&name)?.centre()?;
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
                &i.to_string(),
            );
        }
    }
    Ok(())
}
fn sensors(src: &Sources, at: &mut State, root: &Path) -> Result<()> {
    let pose = frame_placed(src, at, root, "mq6-sensor", &src.reference_step("mq6-sensor")?)?;
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
            &(i + 1).to_string(),
        );
    }
    let pose = frame_placed(src, at, root, "digiten-flow", &src.reference_step("digiten-flow")?)?;
    let (local, outward) = src.digiten_wire_exit()?;
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
            "",
        );
    }
    for (label, name) in [
        ("carbonator", "probe-carbonator-ds18b20"),
        ("coil", "probe-coil-ds18s20"),
    ] {
        let (lo, _) = at.part(name)?.bounds()?;
        let c = at.part(name)?.centre()?;
        let tank = at.part("carbonator-tube")?.centre()?;
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
                "",
            );
        }
    }
    for (bank, count) in [("a", 4), ("b", 4), ("carb", 2)] {
        for i in 1..=count {
            let name = format!("reed-{bank}-{i}");
            let (lo, hi) = at.part(&name)?.bounds()?;
            let c = at.part(&name)?.centre()?;
            for (label, z, mut axis) in [
                ("signal", hi[2], [0., 0., 1.]),
                ("GND", lo[2], [0., 0., -1.]),
            ] {
                let mut p = [c[0], c[1], z];
                let mut basis = "Reed capture-envelope ends; soldered lead extensions and insulation are proposed";
                if bank == "carb" {
                    let tank = at.part("carbonator-tube")?.centre()?;
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
                    "",
                );
            }
        }
    }
    let pose = frame(
        src,
        at,
        root,
        "display",
        &root
            .join("hardware/reference/waveshare-43b-display/waveshare-43b-display.step")
            .to_string_lossy(),
        Some(&[src.display_tilt()]),
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
            &pin_text(&port["board_label"]),
        );
    }
    let (lo, _) = at.part("keystone-jack")?.bounds()?;
    let c = at.part("keystone-jack")?.centre()?;
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
            &i.to_string(),
        );
    }
    Ok(())
}
/// The carbonator's earth bond, carried from the cold core's frame into the installed frame.
pub fn bond(src: &Sources) -> Result<sources::Bond> {
    let mut d = src.bond()?;
    let pose = src.cap_lid_pose()?;
    let offset = src.foam_shell_outer_height() + src.top_cap_height();
    for point in [&mut d.contact_point_mm, &mut d.wire_exit_mm] {
        let [x, y, z] = *point;
        *point = pose.carry([-x, -y, z - offset]);
    }
    for axis in [&mut d.contact_outward, &mut d.wire_outward] {
        let [x, y, z] = *axis;
        *axis = pose.rotate([-x, -y, z]);
    }
    Ok(d)
}
fn boundaries(src: &Sources, at: &mut State) -> Result<()> {
    let body = at.part("compressor")?;
    let mut found = None;
    for s in &body.solids {
        let (lo, hi) = (s.lower, s.upper);
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
    let hi = power.upper;
    let c = power.centre();
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
            "",
        );
    }
    let (lo, hi) = at.part("condenser+fan")?.bounds()?;
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
            "",
        );
    }
    let (_, hi) = at.part("g-ganen-pump")?.bounds()?;
    let c = at.part("g-ganen-pump")?.centre()?;
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
            "",
        );
    }
    let d = bond(src)?;
    put(
        at,
        "carbonator.PE",
        &format!("cold-core/{}", d.body),
        d.wire_exit_mm,
        d.wire_outward,
        "ring-barrel",
        "M3 closed ring on the tapped upper tube rim; shared rim/fastener and ring-barrel datums",
        "modeled",
        "",
    );
    Ok(())
}
fn passages(src: &Sources, at: &mut State) -> Result<()> {
    let face = number(&src.above_core()?["cap_face_z_mm"])?;
    let pose = src.cap_lid_pose()?;
    let conduits = src.cable_conduits()?;
    let height = src.lid_total_height();
    let bore = src.cap_conduit_bore();
    for (name, xy) in &conduits {
        let corridor = src.cable_guide(name)?;
        let lower = *corridor.points_mm.first().context("a cable guide's points")?;
        let floor = [lower[0], lower[1], lower[2] + 1.];
        let upper = pose.carry([xy[0], xy[1], height]);
        at.passages.insert(
            name.clone(),
            Passage::Cap {
                points_mm: vec![
                    [upper[0], upper[1], face + 1.6],
                    [floor[0], floor[1], floor[2] - 1.6],
                ],
                upper_mouth_mm: upper,
                lower_entry_mm: floor,
                corridor_points_mm: corridor.points_mm,
                corridor_bend_radius_mm: corridor.bend_radius_mm,
                bore_diameter_mm: bore,
                basis: "Native top-cap cable conduit, carried into the installed frame".into(),
            },
        );
    }
    at.passages.extend(src.fixed_passages()?);
    Ok(())
}
/// The state before any terminal is resolved: the installed bodies under their hyphenated
/// names, without the wiring's own.
pub fn init(scene: BTreeMap<String, Body>) -> State {
    State {
        scene: scene
            .into_iter()
            .filter(|(name, _)| {
                !["wire-", "wiring-", "terminal-"]
                    .iter()
                    .any(|p| name.starts_with(p))
            })
            .map(|(name, body)| (name.replace('_', "-"), body))
            .collect(),
        terminals: BTreeMap::new(),
        frames_data: BTreeMap::new(),
        frame_checks: BTreeMap::new(),
        fuse_leads: BTreeMap::new(),
        passages: BTreeMap::new(),
        pcb_reference: Value::Null,
    }
}
/// Every terminal, reference frame, fuse lead and cable passage, resolved onto the scene `at`.
pub fn resolve(src: &Sources, mut at: State, root: &Path) -> Result<State> {
    board(src, &mut at, root)?;
    valves(src, &mut at, root)?;
    wagos(src, &mut at, root)?;
    power(src, &mut at, root)?;
    pump_motors(&mut at)?;
    sensors(src, &mut at, root)?;
    boundaries(src, &mut at)?;
    passages(src, &mut at)?;
    Ok(at)
}
