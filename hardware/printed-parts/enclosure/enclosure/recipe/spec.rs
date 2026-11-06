//! The declared Box the enclosure is cut from: the layout's bounds and the pack it holds.
use crate::plan::Bounds;
use anyhow::{Context, Result, ensure};
use serde::Deserialize;
use serde_json::{Map, Value};
use std::collections::BTreeMap;
use std::path::Path;

/// One body's relief through a column, by the corner it stands at.
#[derive(Clone, Debug, Deserialize)]
pub struct ColumnRelief(pub f64, pub f64, pub String, pub Bounds);

#[derive(Clone, Debug, Deserialize)]
pub struct Port {
    pub axis: [f64; 3],
    pub point: [f64; 3],
    pub valve: String,
}

/// The collet plate the pump bay closes on, and the valve tubes that pass it.
#[derive(Clone, Debug, Deserialize)]
pub struct ColletPlate {
    pub aft_y: f64,
    pub fore_y: f64,
    pub hole_d: f64,
    pub holes: Vec<[f64; 2]>,
    pub pump_tube_cut: f64,
    pub return_ports: BTreeMap<String, Port>,
    pub upper_ports: BTreeMap<String, Port>,
    pub seat_z: f64,
    pub seated_tube_bottom_y: f64,
    pub tee_axis_y: f64,
    pub tube_bottom_y: f64,
    pub valve_trays: Vec<(f64, f64, Vec<[f64; 2]>)>,
    pub wall_aft_y: f64,
    pub x0: f64,
    pub x1: f64,
    pub z0: f64,
    pub z1: f64,
    pub fixture_print_bed_z: f64,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Pack {
    pub funnel: [f64; 2],
    pub floor_bosses: Vec<[f64; 4]>,
    pub west_cradle: Vec<[f64; 3]>,
    pub cond_cradle: Vec<[f64; 6]>,
    pub cond_mount: (f64, f64, f64, Vec<[f64; 3]>),
    pub cond_airway: [f64; 4],
    pub ceiling_reliefs: Vec<(String, f64, f64, f64, f64, f64)>,
    pub valve_trays: Vec<(f64, f64, Vec<[f64; 2]>)>,
    pub pump_trays: Vec<[f64; 3]>,
    pub core_stops: Vec<[f64; 3]>,
    pub core_holds: Vec<[f64; 4]>,
    pub vent_chase: Vec<[f64; 3]>,
    pub collet_plate: ColletPlate,
    pub front_flank_reliefs: Vec<(String, f64, f64, f64, f64, f64, f64)>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Box {
    pub pack: Pack,
    pub inner: Bounds,
    pub outer: Bounds,
    pub y_joint: f64,
    pub splits: [f64; 2],
    pub z_seam_passes: [bool; 2],
    pub column_reliefs: Vec<ColumnRelief>,
    pub pump_bay: [f64; 3],
}

/// The layout writes Python's records in tagged form; this reads them back as plain JSON.
fn plain(v: Value) -> Value {
    match v {
        Value::Object(mut m) => {
            if let Some(Value::Array(rows)) = m.remove("__hsm_dict__") {
                let mut out = Map::new();
                for row in rows {
                    if let Value::Array(mut pair) = row {
                        let value = pair.pop().unwrap_or(Value::Null);
                        let key = match pair.pop() {
                            Some(Value::String(s)) => s,
                            Some(other) => other.to_string(),
                            None => String::new(),
                        };
                        out.insert(key, plain(value));
                    }
                }
                return Value::Object(out);
            }
            if m.contains_key("__hsm_namedtuple__") {
                let fields = m.remove("fields").unwrap_or(Value::Null);
                let values = m.remove("values").unwrap_or(Value::Null);
                let mut out = Map::new();
                if let (Value::Array(f), Value::Array(v)) = (fields, values) {
                    for (k, x) in f.into_iter().zip(v) {
                        out.insert(k.as_str().unwrap_or_default().to_owned(), plain(x));
                    }
                }
                return Value::Object(out);
            }
            if let Some(rows) = m.remove("__hsm_list__") {
                return plain(rows);
            }
            Value::Object(m.into_iter().map(|(k, x)| (k, plain(x))).collect())
        }
        Value::Array(rows) => Value::Array(rows.into_iter().map(plain).collect()),
        other => other,
    }
}

/// Pack features this recipe set has no construction for. The layout declares none of them;
/// one that appears is a recipe to write, not something to drop.
const UNBUILT: [&str; 17] = [
    "placed", "front_ports", "back_ports", "east_ports", "west_ports", "c14", "east_bosses",
    "east_mount_fills", "side_wells", "asse_cradle", "flow_meter_anchors", "tube_anchors",
    "flank_reliefs", "port_field", "nameplate", "keystone", "ports",
];

impl Box {
    pub fn read(path: &Path) -> Result<Box> {
        let text = std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?;
        let document: Value = serde_json::from_str(&text).with_context(|| format!("parsing {}", path.display()))?;
        Self::from_document(document).with_context(|| format!("reading the Box in {}", path.display()))
    }

    pub fn from_document(document: Value) -> Result<Box> {
        let document = plain(document);
        let pack = &document["box"]["pack"];
        for name in UNBUILT {
            let declared = match &pack[name] {
                Value::Null => false,
                Value::Array(a) => !a.is_empty(),
                Value::Object(m) => !m.is_empty(),
                _ => true,
            };
            ensure!(!declared, "the Box declares `{name}`, which no enclosure recipe builds");
        }
        Ok(serde_json::from_value(document["box"].clone())?)
    }
}
