//! The support-removal topology of a sliced plate: every connected support body, where it
//! starts, how far it climbs before its first model interface, and its separate interface
//! islands. These are measurements of one slice; removal effort and contact finish are
//! observations of the physical print.
//!
//! Support paths are marked on a grid in plan. Cells of one layer within a link distance are one
//! node; a node joins the nodes of the support layer below it within the same distance.

use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};

/// The plan grid's cell.
pub const GRID_MM: f64 = 0.4;
/// Support cells this close are one body.
pub const TREE_LINK_MM: f64 = 0.85;
/// Interface cells this close are one island.
pub const INTERFACE_LINK_MM: f64 = 1.25;

const SETTINGS: [&str; 11] = ["support_type", "support_style", "support_threshold_angle", "support_on_build_plate_only",
    "support_top_z_distance", "support_bottom_z_distance", "support_object_xy_distance", "support_interface_top_layers",
    "support_interface_bottom_layers", "support_interface_spacing", "layer_height"];

type Cell = (i64, i64);

/// Union by rank with path halving.
#[derive(Default)]
struct DisjointSet {
    parent: Vec<usize>,
    rank: Vec<u32>,
}

impl DisjointSet {
    fn add(&mut self) -> usize {
        self.parent.push(self.parent.len());
        self.rank.push(0);
        self.parent.len() - 1
    }

    fn find(&mut self, mut n: usize) -> usize {
        while self.parent[n] != n {
            self.parent[n] = self.parent[self.parent[n]];
            n = self.parent[n];
        }
        n
    }

    fn union(&mut self, a: usize, b: usize) {
        let (mut a, mut b) = (self.find(a), self.find(b));
        if a == b {
            return;
        }
        if self.rank[a] < self.rank[b] {
            std::mem::swap(&mut a, &mut b);
        }
        self.parent[b] = a;
        if self.rank[a] == self.rank[b] {
            self.rank[a] += 1;
        }
    }
}

fn q(v: f64) -> i64 {
    (v / GRID_MM + 0.5).floor() as i64
}

fn mark_line(cells: &mut HashSet<Cell>, a: (f64, f64), b: (f64, f64)) {
    let distance = (b.0 - a.0).hypot(b.1 - a.1);
    let count = ((distance / (GRID_MM * 0.45)).ceil() as usize).max(1);
    for i in 0..=count {
        let t = i as f64 / count as f64;
        cells.insert((q(a.0 + (b.0 - a.0) * t), q(a.1 + (b.1 - a.1) * t)));
    }
}

/// End points along one XY arc; an arc without centre offsets falls back to its chord.
pub fn arc_points(start: (f64, f64), end: (f64, f64), words: &[(u8, f64)], clockwise: bool) -> Vec<(f64, f64)> {
    let get = |k: u8| words.iter().find(|(c, _)| *c == k).map(|(_, v)| *v);
    let (Some(i), Some(j)) = (get(b'I'), get(b'J')) else { return vec![end] };
    let (cx, cy) = (start.0 + i, start.1 + j);
    let radius = (start.0 - cx).hypot(start.1 - cy);
    if radius <= 1e-9 {
        return vec![end];
    }
    let a0 = (start.1 - cy).atan2(start.0 - cx);
    let mut a1 = (end.1 - cy).atan2(end.0 - cx);
    if clockwise {
        while a1 >= a0 {
            a1 -= 2.0 * std::f64::consts::PI;
        }
    } else {
        while a1 <= a0 {
            a1 += 2.0 * std::f64::consts::PI;
        }
    }
    let turns = (get(b'P').unwrap_or(1.0).round() as i64).max(1);
    let sweep = (a1 - a0) + (2.0 * std::f64::consts::PI * (turns - 1) as f64).copysign(a1 - a0);
    let count = ((sweep.abs() * radius / (GRID_MM * 0.45)).ceil() as usize).max(1);
    (1..=count).map(|i| {
        let a = a0 + sweep * i as f64 / count as f64;
        (cx + radius * a.cos(), cy + radius * a.sin())
    }).collect()
}

fn offsets(link: f64, centre: bool) -> Vec<Cell> {
    let reach = ((link / GRID_MM).ceil() as i64).max(1);
    let mut out = Vec::new();
    for dx in -reach..=reach {
        for dy in -reach..=reach {
            if (centre || dx != 0 || dy != 0) && (dx as f64 * GRID_MM).hypot(dy as f64 * GRID_MM) <= link + 1e-9 {
                out.push((dx, dy));
            }
        }
    }
    out
}

fn components(cells: &HashSet<Cell>, link: f64) -> Vec<Vec<Cell>> {
    let steps = offsets(link, false);
    let mut sorted: Vec<Cell> = cells.iter().copied().collect();
    sorted.sort_unstable();
    let mut remaining: HashSet<Cell> = cells.clone();
    let mut answer = Vec::new();
    for seed in sorted {
        if !remaining.remove(&seed) {
            continue;
        }
        let (mut component, mut stack) = (vec![seed], vec![seed]);
        while let Some((x, y)) = stack.pop() {
            for (dx, dy) in &steps {
                let n = (x + dx, y + dy);
                if remaining.remove(&n) {
                    component.push(n);
                    stack.push(n);
                }
            }
        }
        answer.push(component);
    }
    answer
}

fn near_nodes(cells: &[Cell], previous: &HashMap<Cell, usize>, link: f64) -> BTreeSet<usize> {
    let steps = offsets(link, true);
    let mut out = BTreeSet::new();
    for (x, y) in cells {
        for (dx, dy) in &steps {
            if let Some(&node) = previous.get(&(x + dx, y + dy)) {
                out.insert(node);
            }
        }
    }
    out
}

fn r(v: f64, digits: i32) -> f64 {
    let s = 10f64.powi(digits);
    (v * s).round() / s
}

fn bbox(cells: &[Cell]) -> [f64; 4] {
    let (mut lo, mut hi) = ((i64::MAX, i64::MAX), (i64::MIN, i64::MIN));
    for &(x, y) in cells {
        lo = (lo.0.min(x), lo.1.min(y));
        hi = (hi.0.max(x), hi.1.max(y));
    }
    [r(lo.0 as f64 * GRID_MM, 2), r(lo.1 as f64 * GRID_MM, 2), r(hi.0 as f64 * GRID_MM, 2), r(hi.1 as f64 * GRID_MM, 2)]
}

fn merge(a: [f64; 4], b: [f64; 4]) -> [f64; 4] {
    [a[0].min(b[0]), a[1].min(b[1]), a[2].max(b[2]), a[3].max(b[3])]
}

/// A 3MF row-vector transform, `p · M + t`, as twelve values.
pub type Transform = [f64; 12];

pub fn apply(p: [f64; 3], t: &Transform) -> [f64; 3] {
    [0, 1, 2].map(|c| p[0] * t[c] + p[1] * t[3 + c] + p[2] * t[6 + c] + t[9 + c])
}

/// The transform applying `first`, then `second`.
pub fn compose(first: &Transform, second: &Transform) -> Transform {
    let mut out = [0.0; 12];
    for row in 0..3 {
        for col in 0..3 {
            out[row * 3 + col] = (0..3).map(|k| first[row * 3 + k] * second[k * 3 + col]).sum();
        }
    }
    let moved = apply([first[9], first[10], first[11]], second);
    out[9..12].copy_from_slice(&moved);
    out
}

pub fn inverse(t: &Transform) -> Option<Transform> {
    let [a, b, c, d, e, f, g, h, i] = [t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8]];
    let det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
    if det.abs() <= 1e-12 {
        return None;
    }
    let m = [(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det,
             (f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det,
             (d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det];
    let mut out = [0.0; 12];
    out[..9].copy_from_slice(&m);
    let moved = [0, 1, 2].map(|col| (0..3).map(|row| -t[9 + row] * m[row * 3 + col]).sum::<f64>());
    out[9..12].copy_from_slice(&moved);
    Some(out)
}

fn transform_bbox(b: [f64; 6], t: &Transform) -> Vec<f64> {
    let mut points = Vec::new();
    for x in [b[0], b[3]] {
        for y in [b[1], b[4]] {
            for z in [b[2], b[5]] {
                points.push(apply([x, y, z], t));
            }
        }
    }
    let lo = [0, 1, 2].map(|a| r(points.iter().map(|p| p[a]).fold(f64::INFINITY, f64::min), 3));
    let hi = [0, 1, 2].map(|a| r(points.iter().map(|p| p[a]).fold(f64::NEG_INFINITY, f64::max), 3));
    lo.into_iter().chain(hi).collect()
}

pub struct Options {
    pub piece: String,
    /// Only this object's support: other objects' feature labels read as another object's.
    pub object: Option<i64>,
    /// Retain support bodies without explicit interface feature labels.
    pub include_unlabelled: bool,
    /// Plate coordinates into the part's CAD frame.
    pub cad_transform: Option<Transform>,
    pub bed_reseat: Option<f64>,
    /// What the reading was taken from, as the caller names it.
    pub inputs: Value,
}

struct Node {
    z: f64,
    cells: Vec<Cell>,
}

/// Read the support topology of `gcode`.
pub fn audit(gcode: &[u8], options: &Options) -> Value {
    let (mut tree_set, mut island_set) = (DisjointSet::default(), DisjointSet::default());
    let (mut tree_nodes, mut island_nodes): (Vec<Node>, Vec<Node>) = (Vec::new(), Vec::new());
    let mut island_tree_nodes: HashMap<usize, BTreeSet<usize>> = HashMap::new();
    let (mut previous_tree, mut previous_island): (HashMap<Cell, usize>, HashMap<Cell, usize>) = (HashMap::new(), HashMap::new());
    let (mut previous_tree_z, mut previous_island_z): (Option<f64>, Option<f64>) = (None, None);
    let (mut extrusion_height, mut support_height, mut interface_height): (Option<f64>, Option<f64>, Option<f64>) = (None, None, None);
    let mut z: Option<f64> = None;
    let (mut layer_total, mut layer_interface): (HashSet<Cell>, HashSet<Cell>) = (HashSet::new(), HashSet::new());
    let mut first_layer_z: Option<f64> = None;
    let (mut x, mut y, mut e) = (0.0, 0.0, 0.0);
    let (mut absolute, mut relative_e) = (true, true);
    let mut feature = String::new();
    let mut settings = Map::new();
    let mut slicer_version: Option<String> = None;
    let mut current_object: Option<i64> = None;
    let mut settings_seen = 0usize;

    let mut finish_layer = |z: Option<f64>, layer_total: &HashSet<Cell>, layer_interface: &HashSet<Cell>,
                            support_height: Option<f64>, interface_height: Option<f64>,
                            first_layer_z: &mut Option<f64>, previous_tree: &mut HashMap<Cell, usize>,
                            previous_island: &mut HashMap<Cell, usize>, previous_tree_z: &mut Option<f64>,
                            previous_island_z: &mut Option<f64>| {
        let Some(z) = z else { return };
        // The bed datum is the print's first layer, including model-only layers.
        if first_layer_z.is_none() {
            *first_layer_z = Some(z);
        }
        // Independent support layers can span several intervening model layers.
        if layer_total.is_empty() {
            return;
        }
        if let (Some(h), Some(pz)) = (support_height, *previous_tree_z) {
            if z - pz > h + 0.002 {
                previous_tree.clear();
            }
        }
        if let (Some(h), Some(pz)) = (interface_height, *previous_island_z) {
            if z - pz > h + 0.002 {
                previous_island.clear();
            }
        }
        let mut tree_lookup: HashMap<Cell, usize> = HashMap::new();
        for cells in components(layer_total, TREE_LINK_MM) {
            let node = tree_set.add();
            for old in near_nodes(&cells, previous_tree, TREE_LINK_MM) {
                tree_set.union(node, old);
            }
            for cell in &cells {
                tree_lookup.insert(*cell, node);
            }
            tree_nodes.push(Node { z, cells });
        }
        let mut island_lookup: HashMap<Cell, usize> = HashMap::new();
        for cells in components(layer_interface, INTERFACE_LINK_MM) {
            let node = island_set.add();
            for old in near_nodes(&cells, previous_island, INTERFACE_LINK_MM) {
                island_set.union(node, old);
            }
            let owners: BTreeSet<usize> = cells.iter().filter_map(|c| tree_lookup.get(c).copied()).collect();
            island_tree_nodes.entry(node).or_default().extend(owners);
            for cell in &cells {
                island_lookup.insert(*cell, node);
            }
            island_nodes.push(Node { z, cells });
        }
        *previous_tree = tree_lookup;
        *previous_island = island_lookup;
        *previous_tree_z = Some(z);
        *previous_island_z = if layer_interface.is_empty() { None } else { Some(z) };
    };

    for raw in gcode.split(|b| *b == b'\n') {
        let text = String::from_utf8_lossy(raw);
        let line = text.trim();
        if let Some(rest) = line.strip_prefix("; ") {
            if line.starts_with("; BambuStudio ") {
                slicer_version = Some(rest.trim().to_string());
            }
        }
        if options.object.is_some() {
            if let Some(v) = line.strip_prefix("; OBJECT_ID:") {
                current_object = v.trim().parse().ok();
            } else if line.starts_with("; start printing object, unique label id:") {
                current_object = line.rsplit(':').next().and_then(|v| v.trim().parse().ok());
            } else if line.starts_with("; stop printing object") {
                current_object = None;
            }
        }
        if let Some(v) = line.strip_prefix("; Z_HEIGHT:") {
            finish_layer(z, &layer_total, &layer_interface, support_height, interface_height, &mut first_layer_z,
                         &mut previous_tree, &mut previous_island, &mut previous_tree_z, &mut previous_island_z);
            z = v.trim().parse().ok();
            layer_total.clear();
            layer_interface.clear();
            support_height = None;
            interface_height = None;
            continue;
        }
        if let Some(v) = line.strip_prefix("; LAYER_HEIGHT:") {
            extrusion_height = v.trim().parse().ok();
            continue;
        }
        if let Some(v) = line.strip_prefix("; FEATURE:") {
            feature = if options.object.is_some_and(|o| current_object != Some(o)) { "Other object".into() } else { v.trim().to_string() };
            continue;
        }
        if let Some(rest) = line.strip_prefix("; ") {
            if let Some((key, value)) = rest.split_once(" = ") {
                if settings_seen < 800 {
                    if SETTINGS.contains(&key) {
                        settings.insert(key.to_string(), json!(value.trim()));
                    }
                    settings_seen = settings.len();
                }
                continue;
            }
        }
        let code = line.split(';').next().unwrap_or("").trim();
        let Some(command) = code.split_whitespace().next() else { continue };
        let words = crate::gcode::words(code);
        let get = |k: u8| words.iter().find(|(c, _)| *c == k).map(|(_, v)| *v);
        match command {
            "G90" => { absolute = true; continue; }
            "G91" => { absolute = false; continue; }
            "M82" => { relative_e = false; continue; }
            "M83" => { relative_e = true; continue; }
            "G92" => {
                x = get(b'X').unwrap_or(x);
                y = get(b'Y').unwrap_or(y);
                e = get(b'E').unwrap_or(e);
                continue;
            }
            "G0" | "G1" | "G2" | "G3" => {}
            _ => continue,
        }
        let nx = if absolute { get(b'X').unwrap_or(x) } else { x + get(b'X').unwrap_or(0.0) };
        let ny = if absolute { get(b'Y').unwrap_or(y) } else { y + get(b'Y').unwrap_or(0.0) };
        let de = if relative_e { get(b'E').unwrap_or(0.0) } else { get(b'E').unwrap_or(e) - e };
        let support = matches!(feature.as_str(), "Support" | "Support transition" | "Support interface");
        if z.is_some() && support && de > 1e-9 && ((nx - x).abs() > 1e-9 || (ny - y).abs() > 1e-9) {
            let interface = feature == "Support interface";
            if let Some(h) = extrusion_height {
                support_height = Some(support_height.unwrap_or(0.0).max(h));
                if interface {
                    interface_height = Some(interface_height.unwrap_or(0.0).max(h));
                }
            }
            let points = if command == "G0" || command == "G1" { vec![(nx, ny)] } else { arc_points((x, y), (nx, ny), &words, command == "G2") };
            let mut start = (x, y);
            for &p in &points {
                mark_line(if interface { &mut layer_interface } else { &mut layer_total }, start, p);
                start = p;
            }
            if interface {
                // Interface material is part of the removable support body too.
                let mut start = (x, y);
                for &p in &points {
                    mark_line(&mut layer_total, start, p);
                    start = p;
                }
            }
        }
        x = nx;
        y = ny;
        if let Some(v) = get(b'E') {
            e = if relative_e { e + v } else { v };
        }
    }
    finish_layer(z, &layer_total, &layer_interface, support_height, interface_height, &mut first_layer_z,
                 &mut previous_tree, &mut previous_island, &mut previous_tree_z, &mut previous_island_z);

    struct Tree { base: f64, top: f64, bbox: [f64; 4] }
    let mut trees_by_root: BTreeMap<usize, Tree> = BTreeMap::new();
    for (node, reading) in tree_nodes.iter().enumerate() {
        let root = tree_set.find(node);
        let b = bbox(&reading.cells);
        let row = trees_by_root.entry(root).or_insert(Tree { base: reading.z, top: reading.z, bbox: b });
        row.base = row.base.min(reading.z);
        row.top = row.top.max(reading.z);
        row.bbox = merge(row.bbox, b);
    }
    struct Island { first: f64, last: f64, bbox: [f64; 4], roots: BTreeSet<usize>, first_by_tree: BTreeMap<usize, f64>, order: usize }
    let mut islands: HashMap<usize, Island> = HashMap::new();
    for (node, reading) in island_nodes.iter().enumerate() {
        let root = island_set.find(node);
        let b = bbox(&reading.cells);
        let order = islands.len();
        let row = islands.entry(root).or_insert(Island { first: reading.z, last: reading.z, bbox: b, roots: BTreeSet::new(), first_by_tree: BTreeMap::new(), order });
        row.first = row.first.min(reading.z);
        row.last = row.last.max(reading.z);
        row.bbox = merge(row.bbox, b);
        for &t in island_tree_nodes.get(&node).into_iter().flatten() {
            let tree_root = tree_set.find(t);
            row.roots.insert(tree_root);
            let first = row.first_by_tree.entry(tree_root).or_insert(reading.z);
            *first = first.min(reading.z);
        }
    }
    let reaching: Vec<usize> = if options.include_unlabelled {
        trees_by_root.keys().copied().collect()
    } else {
        islands.values().flat_map(|i| i.roots.iter().copied()).collect::<BTreeSet<_>>().into_iter().collect()
    };
    let mut numbered = reaching.clone();
    numbered.sort_by(|a, b| {
        let (ta, tb) = (&trees_by_root[a], &trees_by_root[b]);
        ta.bbox.partial_cmp(&tb.bbox).unwrap().then(ta.base.partial_cmp(&tb.base).unwrap())
    });
    let number: HashMap<usize, usize> = numbered.iter().enumerate().map(|(i, root)| (*root, i + 1)).collect();

    let mut island_rows: Vec<&Island> = islands.values().collect();
    island_rows.sort_by(|a, b| a.first.partial_cmp(&b.first).unwrap().then(a.bbox.partial_cmp(&b.bbox).unwrap()).then(a.order.cmp(&b.order)));
    let mut interfaces: Vec<Value> = Vec::new();
    let mut by_tree: HashMap<usize, Vec<usize>> = HashMap::new();
    for row in island_rows {
        let mut owners: Vec<usize> = row.roots.iter().copied().filter(|r| number.contains_key(r)).collect();
        if owners.is_empty() {
            continue;
        }
        owners.sort_by_key(|r| number[r]);
        let ids: Vec<String> = owners.iter().map(|r| format!("tree-{}", number[r])).collect();
        let mut interface = json!({"id": format!("interface-{}", interfaces.len() + 1), "first_z_mm": r(row.first, 3),
                                   "last_z_mm": r(row.last, 3), "bbox_xy_mm": row.bbox});
        if owners.len() == 1 {
            interface["tree"] = json!(ids[0]);
            interface["build_up_mm"] = json!(r(row.first - trees_by_root[&owners[0]].base, 3));
        } else {
            // An interface island is a contact-region reading, not necessarily one support body:
            // independently removable trees can reach different passes of the same surface island.
            interface["trees"] = json!(ids);
            interface["first_z_by_tree_mm"] = Value::Object(owners.iter().zip(&ids).map(|(root, id)| (id.clone(), json!(r(row.first_by_tree[root], 3)))).collect());
            interface["build_up_by_tree_mm"] = Value::Object(owners.iter().zip(&ids).map(|(root, id)| (id.clone(), json!(r(row.first_by_tree[root] - trees_by_root[root].base, 3)))).collect());
        }
        if let Some(t) = &options.cad_transform {
            interface["bbox_cad_xyz_mm"] = json!(transform_bbox([row.bbox[0], row.bbox[1], row.first, row.bbox[2], row.bbox[3], row.last], t));
        }
        for root in &owners {
            by_tree.entry(number[root]).or_default().push(interfaces.len());
        }
        interfaces.push(interface);
    }
    let mut trees: Vec<Value> = Vec::new();
    for root in &reaching {
        let n = number[root];
        let row = &trees_by_root[root];
        let contacts = by_tree.get(&n).cloned().unwrap_or_default();
        let first = contacts.iter().map(|&i| {
            let c = &interfaces[i];
            c.get("first_z_by_tree_mm").and_then(|m| m.get(format!("tree-{n}"))).and_then(Value::as_f64).unwrap_or_else(|| c["first_z_mm"].as_f64().unwrap())
        }).fold(None, |m: Option<f64>, v| Some(m.map_or(v, |m| m.min(v))));
        let build = first.map(|f| f - row.base);
        let bed = first_layer_z.is_some_and(|f| row.base <= f + 1e-6);
        let mut tree = json!({"id": format!("tree-{n}"), "root": if bed { "bed" } else { "model" }, "base_z_mm": r(row.base, 3),
            "first_interface_z_mm": first.map(|f| r(f, 3)), "shortest_build_up_mm": build.map(|b| r(b, 3)),
            "top_z_mm": r(row.top, 3), "bbox_xy_mm": row.bbox,
            "interfaces": contacts.iter().map(|&i| interfaces[i]["id"].clone()).collect::<Vec<_>>()});
        if options.include_unlabelled {
            tree["interface_reading"] = json!(if contacts.is_empty() { "unlabelled" } else { "explicit_feature" });
        }
        if let Some(t) = &options.cad_transform {
            tree["bbox_cad_xyz_mm"] = json!(transform_bbox([row.bbox[0], row.bbox[1], row.base, row.bbox[2], row.bbox[3], row.top], t));
        }
        trees.push(tree);
    }
    trees.sort_by_key(|t| t["id"].as_str().and_then(|s| s.split('-').nth(1)).and_then(|s| s.parse::<usize>().ok()).unwrap_or(0));

    let coordinate_frame = options.cad_transform.map(|t| {
        let mut frame = json!({"plate_to_cad_transform": t.iter().map(|v| r(*v, 9)).collect::<Vec<_>>()});
        let identity = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0];
        if (0..9).all(|i| (t[i] - identity[i]).abs() <= 1e-7) {
            frame["plate_to_cad_translation_mm"] = json!(t[9..12].iter().map(|v| r(*v, 6)).collect::<Vec<_>>());
        }
        if let Some(b) = options.bed_reseat {
            frame["replacement_mesh_bed_reseat_mm"] = json!(r(b, 6));
        }
        frame
    });
    let builds: Vec<f64> = trees.iter().filter_map(|t| t["shortest_build_up_mm"].as_f64()).collect();
    let shortest = builds.iter().copied().fold(None, |m: Option<f64>, v| Some(m.map_or(v, |m| m.min(v))));
    let mut result = json!({
        "schema": 1, "piece": options.piece, "inputs": options.inputs, "slicer": slicer_version,
        "first_layer_z_mm": first_layer_z, "coordinate_frame": coordinate_frame, "slicer_settings": settings,
        "summary": {"support_bodies": trees.len(), "interface_islands": interfaces.len(),
                    "bed_rooted_bodies": trees.iter().filter(|t| t["root"] == "bed").count(),
                    "model_rooted_bodies": trees.iter().filter(|t| t["root"] == "model").count(),
                    "shortest_build_up_mm": shortest},
        "trees": trees, "interfaces": interfaces,
    });
    if options.include_unlabelled {
        result["interface_feature_policy"] = json!("All support bodies are retained; unlabelled interfaces have unknown contact count and build-up.");
        let missing = result["trees"].as_array().unwrap().iter().filter(|t| t["interfaces"].as_array().is_some_and(Vec::is_empty)).count();
        let explicit = interfaces_len(&result);
        let summary = result["summary"].as_object_mut().unwrap();
        summary.insert("bodies_without_interface_labels".into(), json!(missing));
        summary.insert("explicit_interface_islands".into(), json!(explicit));
        let s = result["summary"]["shortest_build_up_mm"].clone();
        result["summary"]["shortest_labelled_build_up_mm"] = s;
        if missing > 0 {
            result["summary"]["interface_islands"] = Value::Null;
            result["summary"]["shortest_build_up_mm"] = Value::Null;
        }
    }
    result
}

fn interfaces_len(result: &Value) -> usize {
    result["interfaces"].as_array().map_or(0, Vec::len)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn read(text: &str, include: bool) -> Value {
        audit(text.as_bytes(), &Options { piece: "fixture".into(), object: None, include_unlabelled: include, cad_transform: None, bed_reseat: None, inputs: Value::Null })
    }

    const FIXTURE: &str = "; support_type = tree(auto)\nG90\nM83\n; Z_HEIGHT: 0.2\n; FEATURE: Support\nG1 X0 Y0\nG1 X1 Y0 E1\n; Z_HEIGHT: 0.4\n; FEATURE: Support\nG1 X0 Y0\nG1 X1 Y0 E1\n; FEATURE: Support interface\nG1 X0 Y0\nG1 X1 Y0 E1\n; Z_HEIGHT: 2.0\n; FEATURE: Support\nG1 X10 Y0\nG1 X11 Y0 E1\n; Z_HEIGHT: 8.0\n; FEATURE: Support interface\nG1 X10 Y0\nG1 X11 Y0 E1\n";

    #[test]
    fn bed_and_model_rooted_bodies() {
        let result = read(FIXTURE, false);
        assert_eq!(result["summary"]["support_bodies"], 2);
        assert_eq!(result["summary"]["bed_rooted_bodies"], 1);
        assert_eq!(result["summary"]["model_rooted_bodies"], 1);
        let mut builds: Vec<f64> = result["trees"].as_array().unwrap().iter().map(|t| t["shortest_build_up_mm"].as_f64().unwrap()).collect();
        builds.sort_by(|a, b| a.partial_cmp(b).unwrap());
        assert_eq!(builds, vec![0.2, 6.0]);
        let unlabelled = read(&FIXTURE.replace("; FEATURE: Support interface", "; FEATURE: Support"), true);
        assert_eq!(unlabelled["summary"]["support_bodies"], 2);
        assert_eq!(unlabelled["summary"]["bodies_without_interface_labels"], 2);
        assert_eq!(unlabelled["summary"]["explicit_interface_islands"], 0);
        assert!(unlabelled["summary"]["interface_islands"].is_null());
        assert!(unlabelled["summary"]["shortest_build_up_mm"].is_null());
    }

    #[test]
    fn a_model_rooted_tree_climbs_from_its_first_support() {
        let result = read("G90\nM83\n; Z_HEIGHT: 0.2\n; FEATURE: Outer wall\nG1 X0 Y0\nG1 X4 Y0 E1\n; Z_HEIGHT: 10.2\n; FEATURE: Support\nG1 X0 Y0\nG1 X1 Y0 E1\n; Z_HEIGHT: 18.2\n; FEATURE: Support interface\nG1 X0 Y0\nG1 X1 Y0 E1\n", false);
        assert_eq!(result["first_layer_z_mm"], 0.2);
        assert_eq!(result["summary"]["bed_rooted_bodies"], 0);
        assert_eq!(result["summary"]["model_rooted_bodies"], 1);
        assert_eq!(result["trees"][0]["shortest_build_up_mm"], 8.0);
    }

    #[test]
    fn trees_share_one_interface_island() {
        let shared = read("G90\nM83\n; Z_HEIGHT: 0.2\n; FEATURE: Support\nG1 X20 Y0\nG1 X21 Y0 E1\nG1 X22.5 Y0\nG1 X23.5 Y0 E1\n; Z_HEIGHT: 0.4\n; FEATURE: Support\nG1 X20 Y0\nG1 X21 Y0 E1\nG1 X22.5 Y0\nG1 X23.5 Y0 E1\n; FEATURE: Support interface\nG1 X20 Y0\nG1 X21 Y0 E1\nG1 X22.5 Y0\nG1 X23.5 Y0 E1\n", false);
        assert_eq!(shared["summary"]["support_bodies"], 2);
        assert_eq!(shared["summary"]["interface_islands"], 1);
        assert_eq!(shared["interfaces"][0]["trees"], json!(["tree-1", "tree-2"]));
        let delayed = read("G90\nM83\n; Z_HEIGHT: 0.2\n; FEATURE: Support\nG1 X20 Y0\nG1 X21 Y0 E1\n; Z_HEIGHT: 0.4\n; FEATURE: Support interface\nG1 X20 Y0\nG1 X21 Y0 E1\n; Z_HEIGHT: 0.6\n; FEATURE: Support interface\nG1 X20 Y0\nG1 X21 Y0 E1\nG1 X22.5 Y0\nG1 X23.5 Y0 E1\n", false);
        assert_eq!(delayed["summary"]["support_bodies"], 2);
        assert_eq!(delayed["summary"]["interface_islands"], 1);
        assert_eq!(delayed["interfaces"][0]["first_z_by_tree_mm"], json!({"tree-1": 0.4, "tree-2": 0.6}));
        assert_eq!(delayed["interfaces"][0]["build_up_by_tree_mm"], json!({"tree-1": 0.2, "tree-2": 0.0}));
    }

    #[test]
    fn independent_support_layers_keep_their_bodies() {
        let text = "G90\nM83\n; Z_HEIGHT: 0.4\n; LAYER_HEIGHT: 0.4\n; FEATURE: Support\nG1 X0 Y0\nG1 X2 Y0 E1\n; Z_HEIGHT: 0.56\n; LAYER_HEIGHT: 0.16\n; FEATURE: Outer wall\nG1 X10 Y0\nG1 X12 Y0 E1\n; Z_HEIGHT: 0.9\n; LAYER_HEIGHT: 0.5\n; FEATURE: Support transition\nG1 X0 Y0\nG1 X2 Y0 E1\n; Z_HEIGHT: 1.06\n; LAYER_HEIGHT: 0.16\n; FEATURE: Support interface\nG1 X0 Y0\nG1 X2 Y0 E1\n; Z_HEIGHT: 2.0\n; LAYER_HEIGHT: 0.4\n; FEATURE: Outer wall\nG1 X0 Y0\nG1 X2 Y0 E1\n; Z_HEIGHT: 2.4\n; LAYER_HEIGHT: 0.4\n; FEATURE: Support\nG1 X0 Y0\nG1 X2 Y0 E1\n; Z_HEIGHT: 2.56\n; LAYER_HEIGHT: 0.16\n; FEATURE: Support interface\nG1 X0 Y0\nG1 X2 Y0 E1\n";
        let result = read(text, false);
        assert_eq!(result["summary"]["support_bodies"], 2);
        let mut builds: Vec<f64> = result["trees"].as_array().unwrap().iter().map(|t| t["shortest_build_up_mm"].as_f64().unwrap()).collect();
        builds.sort_by(|a, b| a.partial_cmp(b).unwrap());
        assert_eq!(builds, vec![0.16, 0.66]);
    }

    #[test]
    fn transforms_invert_and_carry_boxes() {
        let forward = [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 10.0, 20.0, 30.0];
        let back = apply(apply([4.0, 5.0, 6.0], &forward), &inverse(&forward).unwrap());
        assert!((back[0] - 4.0).abs() < 1e-9 && (back[1] - 5.0).abs() < 1e-9 && (back[2] - 6.0).abs() < 1e-9);
        assert_eq!(transform_bbox([0.0, 0.0, 0.0, 2.0, 3.0, 4.0], &forward), vec![7.0, 20.0, 30.0, 10.0, 22.0, 34.0]);
    }
}
