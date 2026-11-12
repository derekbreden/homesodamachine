//! What the installed wiring's routing is cut from, each value read from where it is owned: the
//! above-core layout, the plan's placements, the parts' own reference files and published
//! numbers, the cold core's typed interface and the materials catalog.
//!
//! A value no typed crate or published file holds yet comes from the plan's
//! `metadata.wiring_context`, and its absence is an error that names the value and its owner.
use super::{measure, readers, terminals};
use crate::design;
use anyhow::{Context, Result, ensure};
use hsm_cold_core_interface as cci;
use hsm_enclosure_numbers::{catalog, structure};
use serde_json::{Value, json};
use std::cell::RefCell;
use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::rc::Rc;

/// What a turn names for a part that the layout or the plan places by its own native pose: the
/// pose decides, and a turn read in its place fails as a list of turns.
pub const PLACED: &str = "placed by its native pose";

/// The final connections' WAGOs stand with their ports fore: a half turn about Z from the
/// reference's own frame.
pub const PORTS_FORE: [[f64; 3]; 3] = [[-1., 0., 0.], [0., -1., 0.], [0., 0., 1.]];

/// The reference family every WAGO lever connector of the wiring is drawn from.
const WAGO_REFERENCE: &str = "hardware/reference/wago-221";

/// The plan, the checkout and the documents read from it for one wiring request.
pub struct Sources {
    root: PathBuf,
    plan: Value,
    fits: cci::Fits,
    documents: RefCell<BTreeMap<String, Rc<Value>>>,
}

impl Sources {
    /// The sources of the wiring for the plan `plan`, with files read under `root`.
    pub fn read(root: &Path, plan: &Value) -> Result<Self> {
        let fits = cci::Fits {
            slip: catalog::slip(),
            running: catalog::running(),
            supported_surface: catalog::supported(),
            m5_thread_pass_dia: catalog::m5_thread_pass_dia(),
        };
        Ok(Self { root: root.to_owned(), plan: plan.clone(), fits, documents: RefCell::new(BTreeMap::new()) })
    }

    /// The display reference's screen faces −Y, upright; the display plane tilts back from
    /// upright by the facet's tilt from level less a quarter turn.
    pub fn display_tilt(&self) -> Value {
        json!([[1., 0., 0.], structure::ANGLE - 90.])
    }

    /// The colour of the hub the final connections' WAGOs are drawn in, as linear RGB.
    pub fn ac_hub_colour(&self) -> Result<Value> {
        Ok(json!({"$linear": design::material("C_AC_HUB")?}))
    }

    /// The foam shell's outer height, which the cap lid's frame stands above.
    pub fn foam_shell_outer_height(&self) -> f64 {
        cci::FOAM_SHELL_OUTER_HEIGHT
    }

    /// The bore of a cap cable conduit.
    pub fn cap_conduit_bore(&self) -> f64 {
        2. * cci::CAP_CONDUIT_BORE_RADIUS
    }

    /// The foam cap lid's height.
    pub fn lid_total_height(&self) -> f64 {
        cci::foam_cap_lid_height(&self.fits)
    }

    /// The front top's fixed cable passages.
    pub fn fixed_passages(&self) -> Result<Value> {
        self.context(
            "fixed_passages",
            "the front top's fixed cable passages, which the enclosure's fixed pump mount owns",
        )
    }

    /// The thermal fuse's lead diameter.
    pub fn fuse_lead_diameter(&self) -> Result<Value> {
        self.context(
            "fuse_lead_diameter_mm",
            "the thermal fuse's lead diameter, which the SF76E reference owns",
        )
    }

    /// The viewer payload's linear deflection ratio.
    pub fn presentation_deflection_ratio(&self) -> Result<Value> {
        self.context(
            "presentation_deflection_ratio",
            "the viewer payload's linear deflection ratio, which the payload rule owns",
        )
    }

    /// The viewer payload's angular deflection.
    pub fn presentation_angular_deflection(&self) -> Result<Value> {
        self.context(
            "presentation_angular_deflection_rad",
            "the viewer payload's angular deflection, which the payload rule owns",
        )
    }

    /// The JSON file at `path` under the root, read once per request.
    fn document(&self, path: &str) -> Result<Rc<Value>> {
        if let Some(found) = self.documents.borrow().get(path) {
            return Ok(found.clone());
        }
        let read = Rc::new(design::plain(&design::read(self.root.join(path))?));
        self.documents.borrow_mut().insert(path.to_owned(), read.clone());
        Ok(read)
    }

    /// The above-core layout as written down: its parts' poses, the cap lid's pose, the guides.
    pub fn above_core(&self) -> Result<Rc<Value>> {
        self.document("hardware/manifold-layout/above-core.json")
    }

    /// The cold core's own published numbers: its carbonator and its earth bond's datums.
    fn cold_core(&self) -> Result<Rc<Value>> {
        self.document("hardware/cold-core-layout/cold-core-assembly.numbers.json")
    }

    /// A value the plan hands the wiring because nothing typed or published holds it yet.
    fn context(&self, key: &str, what: &str) -> Result<Value> {
        self.plan["metadata"]["wiring_context"].get(key).cloned().with_context(|| {
            format!("the plan's metadata.wiring_context gives no `{key}`: {what}, and no typed crate or published file holds it yet")
        })
    }

    /// The WAGO lever connectors the plan places, by name: size, parent and native pose.
    pub fn placements(&self) -> Result<Value> {
        let placements = &self.plan["metadata"]["wiring_placements"];
        ensure!(placements.is_object(), "the plan's metadata has no wiring_placements");
        Ok(placements.clone())
    }

    /// The plan's instance `name`, when it places its frozen reference's own fine model, with
    /// the STEP that model was cut from.
    fn native_instance(&self, name: &str) -> Result<Option<(&Value, PathBuf)>> {
        let children = format!("{name}/");
        for instance in self.plan["instances"].as_array().into_iter().flatten() {
            let Some(alias) = instance["name"].as_str() else { continue };
            if alias != name && !alias.strip_prefix(children.as_str())
                .is_some_and(|suffix| suffix.parse::<usize>().is_ok()) {
                continue;
            }
            let Some(model) = instance["model"].as_str().map(Path::new) else { continue };
            let manifest = model.parent().context("a model's directory")?.join("frozen-asset.json");
            if !manifest.is_file() {
                continue;
            }
            let asset = design::read(&manifest)?;
            let file = model.file_name().map(|n| n.to_string_lossy().into_owned());
            let named = asset["fine_models"].as_object().into_iter().flatten()
                .find(|(_, row)| row["path"].as_str() == file.as_deref())
                .map(|(step, _)| step.clone());
            let single = || {
                let steps: Vec<&String> = asset["members"].as_object().into_iter().flatten()
                    .map(|(member, _)| member).filter(|member| member.ends_with(".step")).collect();
                (asset["fine_model"]["path"].as_str() == file.as_deref() && steps.len() == 1)
                    .then(|| steps[0].clone())
            };
            if let Some(step) = named.or_else(single) {
                return Ok(Some((instance, model.with_file_name(step))));
            }
        }
        Ok(None)
    }

    /// The native pose a part is placed by: its WAGO placement, or the plan's placement of its
    /// reference's own fine model. A part placed any other way has none here.
    pub fn native_frame(&self, name: &str) -> Result<Value> {
        if let Some(row) = self.placements()?.get(name) {
            return Ok(row.clone());
        }
        let Some((instance, _)) = self.native_instance(name)? else { return Ok(Value::Null) };
        let placed = measure::frame(instance.get("transform"))?.context("a native instance's placement")?;
        let m = placed.m;
        Ok(json!({"rotation": [[m[0][0], m[0][1], m[0][2]], [m[1][0], m[1][1], m[1][2]], [m[2][0], m[2][1], m[2][2]]],
                  "translation_mm": [m[0][3], m[1][3], m[2][3]]}))
    }

    /// The turns of a part that the above-core layout or the plan places by its native pose.
    pub fn placed(&self, name: &str) -> Result<Value> {
        let written = !self.above_core()?["parts"][name].is_null();
        ensure!(
            written || !self.native_frame(name)?.is_null(),
            "{name} has no written-down pose, and nothing owns turns for it"
        );
        Ok(json!(PLACED))
    }

    /// The cap lid's pose in the installed frame.
    pub fn cap_lid_pose(&self) -> Result<Value> {
        Ok(self.above_core()?["cap_lid_pose"].clone())
    }

    /// The reference STEP part `name` is drawn from: the one the above-core layout names for it,
    /// or the one the plan's native instance of it was cut from.
    pub fn reference_step(&self, name: &str) -> Result<PathBuf> {
        if let Some(reference) = self.above_core()?["parts"][name]["reference"].as_str() {
            return Ok(self.root.join(reference));
        }
        let (_, step) = self.native_instance(name)?.with_context(|| format!("{name} names no reference STEP"))?;
        Ok(step)
    }

    /// The reference STEP the parts `names` are all drawn from.
    fn shared_reference(&self, names: &[&str]) -> Result<PathBuf> {
        let mut found = BTreeSet::new();
        for name in names {
            found.insert(self.reference_step(name)?);
        }
        ensure!(found.len() == 1, "{names:?} are drawn from different references: {found:?}");
        found.pop_first().context("a shared reference")
    }

    /// The reference both relays are drawn from.
    pub fn relay_reference(&self) -> Result<PathBuf> {
        self.shared_reference(&["relay-1", "relay-2"])
    }

    /// The reference the solenoid valves are drawn from where their tabs are not modelled.
    pub fn valve_reference(&self) -> Result<PathBuf> {
        self.shared_reference(&["valve-v-a", "valve-v-b", "vk-solenoid"])
    }

    /// The WAGO reference of `size` poles, as the reference family names its STEPs.
    pub fn wago_reference(&self, size: &str) -> Result<PathBuf> {
        let file = format!("wago-221-{size}.step");
        let queries = self.document(&format!("{WAGO_REFERENCE}/native-queries.json"))?;
        ensure!(queries["references"].get(&file).is_some(), "the WAGO reference family has no {file}");
        Ok(self.root.join(WAGO_REFERENCE).join(file))
    }

    /// Every WAGO reference of the family, by its size.
    pub fn wago_references(&self) -> Result<Value> {
        let queries = self.document(&format!("{WAGO_REFERENCE}/native-queries.json"))?;
        let mut out = json!({});
        for file in queries["references"].as_object().context("the WAGO references")?.keys() {
            if let Some(size) = file.strip_prefix("wago-221-").and_then(|f| f.strip_suffix(".step")) {
                out[size] = json!(self.wago_reference(size)?);
            }
        }
        Ok(out)
    }

    /// The main board's outline centre in its own PCB frame, where its tray mounts it.
    pub fn pcba_centre(&self) -> Result<[f64; 2]> {
        let assembly = self.document("hardware/printed-parts/electronics/pcba-tray/pcba-assembly.numbers.json")?;
        let mounts = assembly["mounts"].as_array().context("the board's mounts")?;
        ensure!(mounts.len() == 1, "the board tray mounts {} boards", mounts.len());
        let at = mounts[0]["translation"].as_array().context("the board's mount")?;
        Ok([number(&at[0])?, number(&at[1])?])
    }

    /// The main board's thickness: the height of its slab.
    pub fn pcba_thickness(&self) -> Result<f64> {
        let assembly = self.document("hardware/printed-parts/electronics/pcba-tray/pcba-assembly.numbers.json")?;
        assembly["board"]["slab"][1][2].as_f64().context("the board's slab states no thickness")
    }

    /// The thermal fuse's case length and diameter, as its clamp is cut to them.
    pub fn fuse_case(&self) -> Result<(f64, f64)> {
        let clamp = self.document("hardware/printed-parts/refrigeration/fuse-clamp/fuse-clamp.numbers.json")?;
        Ok((
            clamp["case_l"].as_f64().context("the fuse clamp's case length")?,
            clamp["case_d"].as_f64().context("the fuse clamp's case diameter")?,
        ))
    }

    /// The straight lead stub the fuse's reference models each side of its case: the reference
    /// reaches the stub's tip along its own axis.
    pub fn fuse_lead_stub(&self) -> Result<f64> {
        let queries = self.document("hardware/reference/sf76e-thermal-fuse/native-queries.json")?;
        let bounds = &queries["references"]["sf76e-thermal-fuse.step"]["bounds_mm"];
        let (low, high) = (number(&bounds[0][0])?, number(&bounds[1][0])?);
        ensure!((low + high).abs() < 1e-9, "the fuse reference is not centred on its case");
        Ok(high - self.fuse_case()?.0 / 2.)
    }

    /// The flow meter's wire exit in its own frame: the wire root its model check records, and
    /// the outward normal of the reference's envelope face it lies on.
    pub fn digiten_wire_exit(&self) -> Result<([f64; 3], [f64; 3])> {
        let check = self.document("hardware/reference/digiten-flow-sensor/model-check.json")?;
        let root = xyz(&check["wire_root_mm"])?;
        let queries = self.document("hardware/reference/digiten-flow-sensor/native-queries.json")?;
        let bounds = &queries["references"]["digiten-flow-sensor.step"]["bounds_mm"];
        let (low, high) = (xyz(&bounds[0])?, xyz(&bounds[1])?);
        let mut faces = Vec::new();
        for axis in 0..3 {
            for (side, plane) in [(-1., low[axis]), (1., high[axis])] {
                if (root[axis] - plane).abs() < 1e-9 {
                    let mut outward = [0.; 3];
                    outward[axis] = side;
                    faces.push(outward);
                }
            }
        }
        ensure!(faces.len() == 1, "the flow meter's wire root lies on {} envelope faces", faces.len());
        Ok((root, faces[0]))
    }

    /// The carbonator's earth bond datums in the cold core's frame, at its top plate.
    pub fn bond(&self) -> Result<Value> {
        let bond = self.cold_core()?["bond"].clone();
        ensure!(bond.is_object(), "the cold core publishes no bond datums");
        Ok(bond)
    }

    /// The foam cap's height above the shell top to the lid's underside.
    pub fn top_cap_height(&self) -> f64 {
        cci::FOAM_CAP_HEIGHT - cci::head_pad_height(&self.fits)
    }

    /// The cap conduits the wiring's cables pass through, in the cap's frame, as the foam cap is
    /// cut with them.
    pub fn cable_conduits(&self) -> Result<Value> {
        let cap = self.document("hardware/printed-parts/cold-core/foam-cap/foam-cap.numbers.json")?;
        let mut out = json!({});
        for name in self.cable_passages()? {
            out[&name] = cap["conduits"].get(&name).cloned()
                .with_context(|| format!("the foam cap cuts no conduit {name}"))?;
        }
        Ok(out)
    }

    /// The cap passages the wiring's bundles run through, as its bundle routes name them.
    fn cable_passages(&self) -> Result<BTreeSet<String>> {
        /// Collects every passage named anywhere under `value`.
        fn walk(value: &Value, out: &mut BTreeSet<String>) {
            match value {
                Value::Object(map) => {
                    if let Some(name) = map.get("passage").and_then(Value::as_str) {
                        out.insert(name.to_owned());
                    }
                    map.values().for_each(|v| walk(v, out));
                }
                Value::Array(rows) => rows.iter().for_each(|v| walk(v, out)),
                _ => {}
            }
        }
        let mut out = BTreeSet::new();
        walk(&*self.document("hardware/wiring/installed/bundle-routes.json")?, &mut out);
        Ok(out)
    }

    /// A cable conduit's corridor in world XYZ and the bend its guide is printed to: the foam
    /// assembly's own probe of that guide, carried off the shell the way the cap lid sits on it.
    pub fn cable_guide(&self, name: &str) -> Result<Value> {
        let assembly = self.document("hardware/printed-parts/cold-core/foam-assembly/foam-assembly.numbers.json")?;
        let probe = assembly["report"]["probes"].as_array().context("the foam assembly's probes")?
            .iter().find(|p| p["name"] == name && p["points"].is_array())
            .with_context(|| format!("the foam assembly probes no guide {name}"))?;
        let pose = self.above_core()?["cap_lid_pose"].clone();
        let offset = cci::FOAM_SHELL_OUTER_HEIGHT + self.top_cap_height();
        let points = probe["points"].as_array().unwrap().iter().map(|p| {
            let [x, y, z] = xyz(p)?;
            terminals::carry(&pose, [-x, -y, z - offset])
        }).collect::<Result<Vec<_>>>()?;
        Ok(json!({"points_mm": points, "bend_radius_mm": probe["bend"]}))
    }

    /// The bounds of the reference at `path` turned by `rotation`, from its native queries or
    /// its fine model.
    pub fn reference_bounds(&self, path: &str, rotation: &Value) -> Result<Value> {
        Ok(readers::reference(Path::new(path), rotation)?["bounds"].clone())
    }

    /// The name the installed-wires program imports the STEP at `path` by: its checkout path.
    pub fn checkout_name(&self, path: &str) -> Result<Value> {
        let relative = Path::new(path).strip_prefix(&self.root)
            .with_context(|| format!("{path} is outside the checkout"))?;
        Ok(json!(relative.to_string_lossy()))
    }
}

/// A number of a source document.
fn number(value: &Value) -> Result<f64> {
    value.as_f64().context("a source's number")
}

/// A point of a source document.
fn xyz(value: &Value) -> Result<[f64; 3]> {
    let row = value.as_array().filter(|r| r.len() == 3).context("a point is three coordinates")?;
    Ok([number(&row[0])?, number(&row[1])?, number(&row[2])?])
}
