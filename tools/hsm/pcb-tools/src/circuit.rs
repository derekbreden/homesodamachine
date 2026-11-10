//! Circuit records retain tscircuit's authored nets, placements and manufacturing geometry.
use anyhow::{Context, Result, bail};
use serde::Deserialize;
use serde_json::Value;
use std::{collections::BTreeMap, fs, path::Path};

fn null_default<'de, D, T>(deserializer: D) -> std::result::Result<T, D::Error>
where
    D: serde::Deserializer<'de>,
    T: Deserialize<'de> + Default,
{
    Ok(Option::<T>::deserialize(deserializer)?.unwrap_or_default())
}

#[derive(Clone, Copy, Debug, Default, Deserialize)]
pub struct Point {
    #[serde(default)]
    pub x: f64,
    #[serde(default)]
    pub y: f64,
}
impl Point {
    pub fn distance(self, other: Self) -> f64 {
        (self.x - other.x).hypot(self.y - other.y)
    }
    pub fn mix(self, other: Self, t: f64) -> Self {
        Self {
            x: self.x + (other.x - self.x) * t,
            y: self.y + (other.y - self.y) * t,
        }
    }
}
#[derive(Clone, Copy, Debug, Default, Deserialize)]
pub struct Vector {
    #[serde(default)]
    pub x: f64,
    #[serde(default)]
    pub y: f64,
    #[serde(default)]
    pub z: f64,
}
impl Vector {
    pub fn array(self) -> [f64; 3] {
        [self.x, self.y, self.z]
    }
}

#[derive(Clone, Debug, Deserialize)]
#[serde(tag = "type")]
pub enum Element {
    #[serde(rename = "pcb_board")]
    Board(Board),
    #[serde(rename = "pcb_component")]
    Component(Component),
    #[serde(rename = "source_component")]
    SourceComponent(SourceComponent),
    #[serde(rename = "source_port")]
    SourcePort(SourcePort),
    #[serde(rename = "pcb_port")]
    Port(Port),
    #[serde(rename = "source_trace")]
    SourceTrace(SourceTrace),
    #[serde(rename = "pcb_trace")]
    Trace(Trace),
    #[serde(rename = "pcb_smtpad")]
    SmtPad(Pad),
    #[serde(rename = "pcb_plated_hole")]
    PlatedHole(Pad),
    #[serde(rename = "pcb_hole")]
    Hole(Pad),
    #[serde(rename = "pcb_via")]
    Via(Pad),
    #[serde(rename = "pcb_copper_pour")]
    Pour(Pour),
    #[serde(rename = "cad_component")]
    Cad(Cad),
    #[serde(rename = "pcb_courtyard_outline")]
    Courtyard(Courtyard),
    #[serde(rename = "pcb_silkscreen_text")]
    SilkText(SilkText),
    #[serde(rename = "pcb_silkscreen_path")]
    SilkPath(SilkPath),
    #[serde(other)]
    Other,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Board {
    pub width: f64,
    pub height: f64,
    #[serde(default)]
    pub center: Point,
    #[serde(default)]
    pub outline: Vec<Point>,
    #[serde(default = "thickness")]
    pub thickness: f64,
}
fn thickness() -> f64 {
    1.4
}
#[derive(Clone, Debug, Deserialize)]
pub struct Component {
    pub pcb_component_id: String,
    #[serde(default)]
    pub source_component_id: String,
    #[serde(default)]
    pub layer: String,
}
#[derive(Clone, Debug, Deserialize)]
pub struct SourceComponent {
    pub source_component_id: String,
    #[serde(default)]
    pub name: String,
}
#[derive(Clone, Debug, Deserialize)]
pub struct SourcePort {
    pub source_port_id: String,
    #[serde(default)]
    pub source_component_id: String,
    #[serde(default)]
    pub name: String,
    pub pin_number: Option<u32>,
    #[serde(default)]
    pub port_hints: Vec<String>,
}
#[derive(Clone, Debug, Deserialize)]
pub struct Port {
    pub pcb_port_id: String,
    pub source_port_id: String,
    #[serde(default)]
    pub x: f64,
    #[serde(default)]
    pub y: f64,
}
#[derive(Clone, Debug, Deserialize)]
pub struct SourceTrace {
    pub source_trace_id: String,
    #[serde(default)]
    pub display_name: String,
    pub subcircuit_connectivity_map_key: Option<String>,
    #[serde(default)]
    pub connected_source_port_ids: Vec<String>,
}
#[derive(Clone, Debug, Deserialize)]
pub struct Trace {
    #[serde(default)]
    pub source_trace_id: String,
    #[serde(default)]
    pub route: Vec<RoutePoint>,
}
#[derive(Clone, Debug, Deserialize)]
pub struct RoutePoint {
    pub x: Option<f64>,
    pub y: Option<f64>,
    pub layer: Option<String>,
    pub route_type: Option<String>,
    pub from_layer: Option<String>,
    pub to_layer: Option<String>,
    #[serde(default = "trace_width")]
    pub width: f64,
}
fn trace_width() -> f64 {
    0.2
}
impl RoutePoint {
    pub fn point(&self) -> Option<Point> {
        Some(Point {
            x: self.x?,
            y: self.y?,
        })
    }
}

#[derive(Clone, Debug, Deserialize)]
pub struct Pad {
    pub x: f64,
    pub y: f64,
    #[serde(default, deserialize_with = "null_default")]
    pub pcb_component_id: String,
    #[serde(default, deserialize_with = "null_default")]
    pub pcb_port_id: String,
    #[serde(default)]
    pub port_hints: Vec<String>,
    #[serde(default)]
    pub shape: String,
    #[serde(default)]
    pub hole_shape: String,
    pub width: Option<f64>,
    pub height: Option<f64>,
    pub radius: Option<f64>,
    pub outer_width: Option<f64>,
    pub outer_height: Option<f64>,
    pub outer_diameter: Option<f64>,
    pub hole_width: Option<f64>,
    pub hole_height: Option<f64>,
    pub hole_diameter: Option<f64>,
    #[serde(default)]
    pub ccw_rotation: Option<f64>,
    pub layer: Option<String>,
    #[serde(default)]
    pub layers: Vec<String>,
    pub subcircuit_connectivity_map_key: Option<String>,
}
impl Pad {
    pub fn point(&self) -> Point {
        Point {
            x: self.x,
            y: self.y,
        }
    }
}
#[derive(Clone, Debug, Deserialize)]
pub struct Pour {
    pub layer: String,
    #[serde(default)]
    pub polygons: Vec<Polygon>,
    #[serde(default)]
    pub outline: Vec<Point>,
}
#[derive(Clone, Debug, Deserialize)]
pub struct Polygon {
    #[serde(default)]
    pub points: Vec<Point>,
    #[serde(default)]
    pub vertices: Vec<Point>,
}
#[derive(Clone, Debug, Deserialize)]
pub struct Cad {
    #[serde(default)]
    pub cad_component_id: String,
    #[serde(default)]
    pub pcb_component_id: String,
    #[serde(default)]
    pub source_component_id: String,
    pub model_obj_url: Option<String>,
    pub model_step_url: Option<String>,
    #[serde(default)]
    pub position: Vector,
    #[serde(default)]
    pub rotation: Vector,
    #[serde(default)]
    pub model_origin_position: Vector,
}
#[derive(Clone, Debug, Deserialize)]
pub struct Courtyard {
    pub pcb_component_id: String,
    #[serde(default)]
    pub outline: Vec<Point>,
}
#[derive(Clone, Debug, Deserialize)]
pub struct SilkText {
    pub pcb_silkscreen_text_id: String,
    pub text: String,
    pub font_size: f64,
    pub anchor_position: Point,
    pub anchor_alignment: Option<String>,
    pub ccw_rotation: Option<f64>,
    pub is_mirrored: Option<bool>,
    pub layer: Option<String>,
}
#[derive(Clone, Debug, Deserialize)]
pub struct SilkPath {
    #[serde(default)]
    pub route: Vec<Point>,
    pub stroke_width: Option<f64>,
    pub pcb_component_id: Option<String>,
}

pub struct Circuit {
    pub elements: Vec<Element>,
}
impl Circuit {
    pub fn load(path: &Path) -> Result<Self> {
        let value: Value = serde_json::from_slice(
            &fs::read(path).with_context(|| format!("read {}", path.display()))?,
        )?;
        let elements = serde_json::from_value(if value.is_array() {
            value
        } else {
            value
                .get("circuitJson")
                .context("circuit JSON must contain an element array")?
                .clone()
        })?;
        Ok(Self { elements })
    }
    pub fn board(&self) -> Result<&Board> {
        self.elements
            .iter()
            .find_map(|e| {
                if let Element::Board(b) = e {
                    Some(b)
                } else {
                    None
                }
            })
            .context("circuit has no board")
    }
    pub fn names(&self) -> BTreeMap<String, String> {
        let source = self
            .elements
            .iter()
            .filter_map(|e| {
                if let Element::SourceComponent(c) = e {
                    Some((c.source_component_id.clone(), c.name.clone()))
                } else {
                    None
                }
            })
            .collect::<BTreeMap<_, _>>();
        self.elements
            .iter()
            .filter_map(|e| {
                if let Element::Component(c) = e {
                    Some((
                        c.pcb_component_id.clone(),
                        source
                            .get(&c.source_component_id)
                            .cloned()
                            .unwrap_or_else(|| "?".into()),
                    ))
                } else {
                    None
                }
            })
            .collect()
    }
    pub fn nets(&self) -> BTreeMap<String, String> {
        let mut source = BTreeMap::new();
        for e in &self.elements {
            if let Element::SourceTrace(t) = e {
                if let Some(key) = &t.subcircuit_connectivity_map_key {
                    for port in &t.connected_source_port_ids {
                        source.entry(port.clone()).or_insert_with(|| key.clone());
                    }
                }
            }
        }
        self.elements
            .iter()
            .filter_map(|e| {
                if let Element::Port(p) = e {
                    Some((
                        p.pcb_port_id.clone(),
                        source.get(&p.source_port_id)?.clone(),
                    ))
                } else {
                    None
                }
            })
            .collect()
    }
    pub fn named_pad(&self, anchor: &str) -> Result<usize> {
        let (component, pin) = anchor
            .split_once('.')
            .context("pad name must be Component.pin")?;
        let names = self.names();
        let source = self
            .elements
            .iter()
            .filter_map(|e| {
                if let Element::SourcePort(p) = e {
                    Some((p.source_port_id.as_str(), p))
                } else {
                    None
                }
            })
            .collect::<BTreeMap<_, _>>();
        let ports = self
            .elements
            .iter()
            .filter_map(|e| {
                if let Element::Port(p) = e {
                    Some((p.pcb_port_id.as_str(), p.source_port_id.as_str()))
                } else {
                    None
                }
            })
            .collect::<BTreeMap<_, _>>();
        for (index, e) in self.elements.iter().enumerate() {
            if let Element::SmtPad(p) | Element::PlatedHole(p) = e {
                if names
                    .get(&p.pcb_component_id)
                    .is_some_and(|v| v == component)
                    && (p.port_hints.iter().any(|v| v == pin)
                        || ports
                            .get(p.pcb_port_id.as_str())
                            .and_then(|s| source.get(s))
                            .is_some_and(|s| s.port_hints.iter().any(|v| v == pin)))
                {
                    return Ok(index);
                }
            }
        }
        bail!("pad {anchor} not found")
    }
}
