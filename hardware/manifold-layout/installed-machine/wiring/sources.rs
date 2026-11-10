//! The values the installed wiring's routing asks its host for, each read from where it is
//! owned: the above-core layout, the plan's placements, the parts' own reference files and
//! published numbers, the cold core's typed interface and the materials catalog.
//!
//! A value no typed crate or published file holds yet comes from the plan's
//! `metadata.wiring_context`, and its absence is an error that names the value and its owner.
use super::{Request, corridors, measure, readers, terminals};
use crate::design;
use anyhow::{Context, Result, bail, ensure};
use hsm_cold_core_interface as cci;
use hsm_enclosure_numbers::{catalog, structure};
use serde_json::{Value, json};
use std::cell::RefCell;
use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::rc::Rc;

/// What a turn names for a part that the layout or the plan places by its own native pose: the
/// pose decides, and a turn read in its place fails as a list of turns.
const PLACED: &str = "placed by its native pose";

/// The final connections' WAGOs stand with their ports fore: a half turn about Z from the
/// reference's own frame.
const PORTS_FORE: [[f64; 3]; 3] = [[-1., 0., 0.], [0., -1., 0.], [0., 0., 1.]];

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

    /// One of the included code's provider queries, by its kind.
    pub fn answer(&self, query: &Value) -> Result<Value> {
        match query["kind"].as_str().context("a provider query names its kind")? {
            "measure" => self.measure(query),
            "reference_bounds" => self.reference_bounds(query),
            "valve_reference" => self.valve_reference(),
            "fixed_wiring_passages" => self.context(
                "fixed_passages",
                "the front top's fixed cable passages, which the enclosure's fixed pump mount owns",
            ),
            "step" => self.checkout_name(query["path"].as_str().context("a STEP's path")?),
            "get" => self.value(
                query["base"].as_str().context("a query's module")?,
                query["path"].as_str().context("a query's attribute")?,
                query.get("args"),
            ),
            kind => bail!("the installed wiring has no source for a {kind} query"),
        }
    }

    /// The value the included code names `base`.`path`, given `args` where it is a function.
    pub fn value(&self, base: &str, path: &str, args: Option<&Value>) -> Result<Value> {
        let arg = |i: usize| -> Result<&Value> {
            args.and_then(|a| a.get(i)).with_context(|| format!("{base}.{path} takes an argument"))
        };
        match (base, path) {
            ("ea", "PCBA_STEP") => self.reference_step("pcba"),
            ("ea", "PSU_STEP") => self.reference_step("psu"),
            ("ea", "RELAY_STEP") => self.shared_reference(&["relay-1", "relay-2"]),
            ("ea", "C14_STEP") => self.reference_step("c14-inlet"),
            ("ea", "MQ6_STEP") => self.reference_step("mq6-sensor"),
            ("ea", "DIGITEN_STEP") => self.reference_step("digiten-flow"),
            ("ea", "PCBA_TURN") => self.placed("pcba"),
            ("ea", "PSU_TURN") => self.placed("psu"),
            ("ea", "RELAY_TURN") => self.placed("relay-1"),
            ("ea", "RELAY2_TURN") => self.placed("relay-2"),
            ("ea", "DIGITEN_TURN") => self.placed("digiten-flow"),
            ("ea", "MQ6_TURN") => self.placed("mq6-sensor"),
            ("ea", "FUSE_TURN") => self.placed("thermal-fuse"),
            ("ea", "WAGO_TURN" | "WAGO_TURN_WEST") => {
                ensure!(self.placements()?.as_object().is_some_and(|m| !m.is_empty()), "the plan places no WAGO");
                Ok(json!(PLACED))
            }
            // The display reference's screen faces −Y, upright; the display plane tilts back from
            // upright by the facet's tilt from level less a quarter turn.
            ("ea", "DISPLAY_TILT") => Ok(json!([[1., 0., 0.], structure::ANGLE - 90.])),
            ("ea", "wago_step") => Ok(json!(self.wago_reference(string(arg(0)?)?)?)),
            ("ea", "_pcba._centre") => self.pcba_centre(),
            ("ea", "_pcba._thickness") => self.pcba_thickness(),
            ("ea", "_fuse.BODY_L") => Ok(json!(self.fuse_case()?.0)),
            ("ea", "_fuse.AXIS_Z") => Ok(json!(self.fuse_case()?.1 / 2.)),
            ("ea", "_fuse.LEAD_STUB") => self.fuse_lead_stub(),
            ("ea", "_fuse.LEAD_D") => self.context(
                "fuse_lead_diameter_mm",
                "the thermal fuse's lead diameter, which the SF76E reference owns",
            ),
            // How much lead the fuse comes with reaches only the wiring's review, which this
            // request leaves out.
            ("ea", "_fuse.LEAD_LONG" | "_fuse.LEAD_SHORT") => Ok(Value::Null),
            ("ea", "_digiten.wire_exit") => self.digiten_wire_exit(),
            ("ea", "_cca._V.top_plate_z") => Ok(self.cold_core()?["carbonator"]["top_plate_z"].clone()),
            ("ea", "_cca._V._bond.datums") => self.bond(arg(0)?),
            ("ea", "_cci.foam_shell_outer_height") => Ok(json!(cci::FOAM_SHELL_OUTER_HEIGHT)),
            ("ea", "_cci.cap_cable_conduits") => self.cable_conduits(),
            ("ea", "_cci.cap_conduit_bore_radius") => Ok(json!(cci::CAP_CONDUIT_BORE_RADIUS)),
            ("ea", "_foam.lid_total_height") => Ok(json!(cci::foam_cap_lid_height(&self.fits))),
            ("above_core_wiring", "frame") => self.native_frame(string(arg(0)?)?),
            ("above_core_wiring", "placements") => self.placements(),
            ("above_core_wiring", "PORTS_FORE") => Ok(json!(PORTS_FORE)),
            ("above_core_wiring", "REFERENCES") => self.wago_references(),
            ("above_core_wiring", "C_AC_HUB") => Ok(json!({"$linear": design::material("C_AC_HUB")?})),
            ("above_core", "specification") => Ok((*self.above_core()?).clone()),
            ("above_core", "cap_lid_pose") => Ok(self.above_core()?["cap_lid_pose"].clone()),
            ("_foam_cap", "top_cap_height") => Ok(json!(self.top_cap_height())),
            ("_above_core_mounts", "cable_guide_points") => self.cable_guide(string(arg(0)?)?),
            ("_internal_routes", "route_segments") => {
                let points = arg(0)?.as_array().context("a corridor's points")?
                    .iter().map(xyz).collect::<Result<Vec<_>>>()?;
                corridors::route_segments(&points, arg(1)?.as_f64().context("a corridor's bend radius")?)
            }
            ("_payload_rules", "LINEAR_DEFLECTION_RATIO") => self.context(
                "presentation_deflection_ratio",
                "the viewer payload's linear deflection ratio, which the payload rule owns",
            ),
            ("_mesh_payload", "ANGULAR_DEFLECTION") => self.context(
                "presentation_angular_deflection_rad",
                "the viewer payload's angular deflection, which the payload rule owns",
            ),
            _ => bail!("nothing owns {base}.{path} for the installed wiring"),
        }
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
    fn above_core(&self) -> Result<Rc<Value>> {
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
    fn placements(&self) -> Result<Value> {
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
    fn native_frame(&self, name: &str) -> Result<Value> {
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
    fn placed(&self, name: &str) -> Result<Value> {
        let written = !self.above_core()?["parts"][name].is_null();
        ensure!(
            written || !self.native_frame(name)?.is_null(),
            "{name} has no written-down pose, and nothing owns turns for it"
        );
        Ok(json!(PLACED))
    }

    /// The reference STEP part `name` is drawn from: the one the above-core layout names for it,
    /// or the one the plan's native instance of it was cut from.
    fn reference_step(&self, name: &str) -> Result<Value> {
        if let Some(reference) = self.above_core()?["parts"][name]["reference"].as_str() {
            return Ok(json!(self.root.join(reference)));
        }
        let (_, step) = self.native_instance(name)?.with_context(|| format!("{name} names no reference STEP"))?;
        Ok(json!(step))
    }

    /// The reference STEP the parts `names` are all drawn from.
    fn shared_reference(&self, names: &[&str]) -> Result<Value> {
        let mut found = BTreeSet::new();
        for name in names {
            found.insert(self.reference_step(name)?.as_str().context("a reference's path")?.to_owned());
        }
        ensure!(found.len() == 1, "{names:?} are drawn from different references: {found:?}");
        Ok(json!(found.pop_first()))
    }

    /// The reference the solenoid valves are drawn from where their tabs are not modelled.
    fn valve_reference(&self) -> Result<Value> {
        self.shared_reference(&["valve-v-a", "valve-v-b", "vk-solenoid"])
    }

    /// The WAGO reference of `size` poles, as the reference family names its STEPs.
    fn wago_reference(&self, size: &str) -> Result<PathBuf> {
        let file = format!("wago-221-{size}.step");
        let queries = self.document(&format!("{WAGO_REFERENCE}/native-queries.json"))?;
        ensure!(queries["references"].get(&file).is_some(), "the WAGO reference family has no {file}");
        Ok(self.root.join(WAGO_REFERENCE).join(file))
    }

    /// Every WAGO reference of the family, by its size.
    fn wago_references(&self) -> Result<Value> {
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
    fn pcba_centre(&self) -> Result<Value> {
        let assembly = self.document("hardware/printed-parts/electronics/pcba-tray/pcba-assembly.numbers.json")?;
        let mounts = assembly["mounts"].as_array().context("the board's mounts")?;
        ensure!(mounts.len() == 1, "the board tray mounts {} boards", mounts.len());
        let at = mounts[0]["translation"].as_array().context("the board's mount")?;
        Ok(json!([at[0], at[1]]))
    }

    /// The main board's thickness: the height of its slab.
    fn pcba_thickness(&self) -> Result<Value> {
        let assembly = self.document("hardware/printed-parts/electronics/pcba-tray/pcba-assembly.numbers.json")?;
        let thickness = &assembly["board"]["slab"][1][2];
        ensure!(thickness.is_number(), "the board's slab states no thickness");
        Ok(thickness.clone())
    }

    /// The thermal fuse's case length and diameter, as its clamp is cut to them.
    fn fuse_case(&self) -> Result<(f64, f64)> {
        let clamp = self.document("hardware/printed-parts/refrigeration/fuse-clamp/fuse-clamp.numbers.json")?;
        Ok((
            clamp["case_l"].as_f64().context("the fuse clamp's case length")?,
            clamp["case_d"].as_f64().context("the fuse clamp's case diameter")?,
        ))
    }

    /// The straight lead stub the fuse's reference models each side of its case: the reference
    /// reaches the stub's tip along its own axis.
    fn fuse_lead_stub(&self) -> Result<Value> {
        let queries = self.document("hardware/reference/sf76e-thermal-fuse/native-queries.json")?;
        let bounds = &queries["references"]["sf76e-thermal-fuse.step"]["bounds_mm"];
        let (low, high) = (number(&bounds[0][0])?, number(&bounds[1][0])?);
        ensure!((low + high).abs() < 1e-9, "the fuse reference is not centred on its case");
        Ok(json!(high - self.fuse_case()?.0 / 2.))
    }

    /// The flow meter's wire exit in its own frame: the wire root its model check records, and
    /// the outward normal of the reference's envelope face it lies on.
    fn digiten_wire_exit(&self) -> Result<Value> {
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
        Ok(json!([root, faces[0]]))
    }

    /// The carbonator's earth bond datums in the cold core's frame, for the top plate at `plate`.
    fn bond(&self, plate: &Value) -> Result<Value> {
        let core = self.cold_core()?;
        ensure!(
            core["carbonator"]["top_plate_z"][1] == *plate,
            "the cold core publishes its bond datums for the top plate, not for {plate}"
        );
        let bond = core["bond"].clone();
        ensure!(bond.is_object(), "the cold core publishes no bond datums");
        Ok(bond)
    }

    /// The foam cap's height above the shell top to the lid's underside.
    fn top_cap_height(&self) -> f64 {
        cci::FOAM_CAP_HEIGHT - cci::head_pad_height(&self.fits)
    }

    /// The cap conduits the wiring's cables pass through, in the cap's frame, as the foam cap is
    /// cut with them.
    fn cable_conduits(&self) -> Result<Value> {
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
    fn cable_guide(&self, name: &str) -> Result<Value> {
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

    /// The bounds of a reference turned by `rotation`, from its native queries or its fine model.
    fn reference_bounds(&self, query: &Value) -> Result<Value> {
        let result = readers::request(&Request {
            op: "model_reference_bounds".into(),
            data: json!({"path": query["path"], "rotation": query["rotation"]}),
            root: self.root.clone(),
        })?;
        Ok(result["bounds"].clone())
    }

    /// The bodies of the models a measurement query names, as the fine model reader states them.
    fn measure(&self, query: &Value) -> Result<Value> {
        let components: BTreeSet<String> = query["component_names"].as_array().into_iter().flatten()
            .filter_map(Value::as_str).map(str::to_owned).collect();
        let mut bodies = Vec::new();
        for instance in query["instances"].as_array().context("a measurement's models")? {
            let path = Path::new(instance["model"].as_str().context("a measured model's path")?);
            bodies.extend(measure::summaries(path, measure::frame(instance.get("transform"))?.as_ref(), &components)?);
        }
        Ok(json!({"bodies": bodies}))
    }

    /// The name the installed-wires program imports the STEP at `path` by: its checkout path.
    fn checkout_name(&self, path: &str) -> Result<Value> {
        let relative = Path::new(path).strip_prefix(&self.root)
            .with_context(|| format!("{path} is outside the checkout"))?;
        Ok(json!(relative.to_string_lossy()))
    }
}

/// A text of a query's arguments.
fn string(value: &Value) -> Result<&str> {
    value.as_str().context("a query's text argument")
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
