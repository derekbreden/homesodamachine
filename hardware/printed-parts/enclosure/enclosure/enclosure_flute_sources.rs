//! Conservative lineage for the unchanged fluted print triangles.
//!
//! The boolean's own run IDs identify the authored flute tool. Structural and repaired
//! facets inherit records only through exact f32 triangle matches. Everything else is
//! explicitly unknown; no spatial proximity assigns a source.
use hsm_kernel::{Solid, write::face_json};
use manifold_csg::Manifold;
use serde_json::{Value, json};
use std::collections::{BTreeMap, HashMap, HashSet};

type Triangle = [[u32; 3]; 3];

fn key(mut corners: Triangle) -> Triangle {
    let start = (0..3).min_by_key(|&i| corners[i]).unwrap();
    corners.rotate_left(start);
    corners
}

fn sources(record: Value) -> Vec<Value> {
    let mut records = record.get("contributors").and_then(Value::as_array)
        .cloned().unwrap_or_else(|| vec![record.clone()]);
    for source in &mut records {
        if let Some(fields) = source.as_object_mut() {
            fields.retain(|key, _| matches!(key.as_str(), "src" | "op" | "via"));
            if let Some(via) = record.get("via") {
                let via = via.as_str().and_then(|text| text.split_once(" at "))
                    .map(|(op, src)| json!({"op":op,"src":src})).unwrap_or_else(|| via.clone());
                fields.insert("via".into(), via);
            }
        }
    }
    records
}

fn join(into: &mut Vec<Value>, sources: &[Value]) {
    for source in sources {
        if !into.contains(source) { into.push(source.clone()); }
    }
    into.sort_by_cached_key(Value::to_string);
}

fn triangles(shape: &Manifold) -> (Vec<Triangle>, Vec<u32>, Vec<u32>) {
    let mesh = shape.to_meshgl();
    let vertices = mesh.vert_properties();
    let stride = mesh.num_prop();
    let triangles = mesh.tri_verts().chunks_exact(3).map(|indices| {
        key(std::array::from_fn(|k| {
            std::array::from_fn(|j| vertices[indices[k] as usize * stride + j].to_bits())
        }))
    }).collect();
    (triangles, mesh.run_index(), mesh.run_original_id())
}

pub(crate) struct Sources {
    base: HashMap<Triangle, Vec<Value>>,
    base_ids: HashSet<u32>,
    tools: HashMap<u32, Value>,
    cut: HashMap<Triangle, Vec<Value>>,
    records: Vec<Vec<Value>>,
    faces: Vec<u32>,
}

impl Sources {
    pub(crate) fn new(solid: &Solid) -> Self {
        let mut base = HashMap::<Triangle, Vec<Value>>::new();
        for (i, triangle) in solid.tris().iter().enumerate() {
            let corners = key(triangle.map(|v| solid.verts()[v as usize]
                .to_array().map(|x| (x as f32).to_bits())));
            join(base.entry(corners).or_default(), &sources(face_json(solid.face_at(i))));
        }
        Self { base, base_ids: HashSet::new(), tools: HashMap::new(), cut: HashMap::new(),
            records: vec![vec![Value::Null]], faces: vec![] }
    }

    pub(crate) fn document(&self) -> Value {
        json!({"v":1, "records":self.records, "triangles":self.faces,
            "lineage":"Boolean run IDs and exact oriented f32 triangle correspondence; unmatched facets are unknown."})
    }
}

impl super::skin::FluteObserver for Sources {
    fn base(&mut self, shape: &Manifold) {
        self.base_ids.extend(shape.to_meshgl().run_original_id());
    }

    fn cutter(&mut self, shape: &Manifold, source: Value) {
        for id in shape.to_meshgl().run_original_id() {
            self.tools.insert(id, source.clone());
        }
    }

    fn cut(&mut self, shape: &Manifold) {
        let (triangles, runs, ids) = triangles(shape);
        let mut run = 0;
        for (i, triangle) in triangles.into_iter().enumerate() {
            while run + 1 < ids.len() && runs[run + 1] as usize <= 3 * i { run += 1; }
            let source = match ids.get(run) {
                Some(id) if self.tools.contains_key(id) => vec![self.tools[id].clone()],
                Some(id) if self.base_ids.contains(id) =>
                    self.base.get(&triangle).cloned().unwrap_or_else(|| vec![Value::Null]),
                _ => vec![Value::Null],
            };
            join(self.cut.entry(triangle).or_default(), &source);
        }
        self.base.clear();
    }

    fn finished(&mut self, shape: &Manifold) {
        let (triangles, _, _) = triangles(shape);
        let mut groups = BTreeMap::from([(Value::Array(vec![Value::Null]).to_string(), 0)]);
        for triangle in triangles {
            let sources = self.cut.get(&triangle).cloned().unwrap_or_else(|| vec![Value::Null]);
            let key = Value::Array(sources.clone()).to_string();
            let group = *groups.entry(key).or_insert_with(|| {
                self.records.push(sources);
                self.records.len() as u32 - 1
            });
            self.faces.push(group);
        }
        self.cut.clear();
    }
}
