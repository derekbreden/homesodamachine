//! Manual explainer exports read current native CAD payloads, pressure sections and forming datums.
use super::{explainer, sound};
use crate::scene::{V3, add, mul, sub};
use crate::{Args, json, root, write};
use anyhow::{Context, Result, ensure};
use hsm_carbonator_numbers as carbonator;
use hsm_coil_numbers as coil;
use hsm_kernel::{Body, Plane};
use hsm_render::payload::RawMesh;
use serde_json::{Value, json};
use std::{
    fs,
    io::Write,
    path::{Path, PathBuf},
};

fn mapped(p: V3, floor: f64) -> V3 {
    [-p[1], p[2] - floor, -p[0]]
}
fn bounds(points: &[V3]) -> [V3; 2] {
    let mut lo = [f64::INFINITY; 3];
    let mut hi = [f64::NEG_INFINITY; 3];
    for point in points {
        for i in 0..3 {
            lo[i] = lo[i].min(point[i]);
            hi[i] = hi[i].max(point[i]);
        }
    }
    [lo, hi]
}
fn group(name: &str) -> &str {
    if name.starts_with("foam-") {
        "insulation"
    } else if name.starts_with("evap-") {
        "evaporator"
    } else if name.starts_with("reservoir-")
        || ["float-a", "float-b", "reed-a", "reed-b"]
            .iter()
            .any(|p| name.starts_with(p))
    {
        "flavor-reservoirs"
    } else if [
        "carbonator",
        "endcap-",
        "float-rod-carb",
        "float-carb",
        "water-inlet-jet",
        "collet-",
        "prv-",
        "reed-carb",
        "reed-bridge",
    ]
    .iter()
    .any(|p| name.starts_with(p))
    {
        "carbonator"
    } else if name.starts_with("display") {
        "display"
    } else if name.starts_with("funnel") {
        "funnel"
    } else {
        "mechanical-context"
    }
}
fn role(name: &str) -> &str {
    if name == "carbonator-tube" {
        "pressure-shell"
    } else if name.starts_with("endcap") {
        "endcap"
    } else if name.starts_with("carbonator-elbow") {
        "port"
    } else if name.starts_with("collet") {
        "collet"
    } else if name.starts_with("prv") {
        "prv"
    } else if name == "water-inlet-jet-cap-nominal" {
        "jet-cap"
    } else if name == "float-rod-carb" {
        "float-guide"
    } else {
        "sensor"
    }
}
fn compressed(path: &Path, value: &Value) -> Result<Value> {
    let bytes = serde_json::to_vec(value)?;
    write(path, &bytes)?;
    let mut encoder = flate2::GzBuilder::new()
        .mtime(0)
        .write(Vec::new(), flate2::Compression::best());
    encoder.write_all(&bytes)?;
    let data = encoder.finish()?;
    let gzip = path.with_extension("json.gz");
    write(&gzip, &data)?;
    let meshes = value["meshes"].as_array().context("bundle meshes")?;
    Ok(
        json!({"file":path.file_name().unwrap().to_string_lossy(),"compressedFile":gzip.file_name().unwrap().to_string_lossy(),"meshes":meshes.len(),"triangles":meshes.iter().filter_map(|m|m["triangles"].as_u64()).sum::<u64>(),"bytes":bytes.len(),"compressedBytes":data.len(),"source":value["source"],"sourceSha256":value["sourceSha256"]}),
    )
}
fn mesh(raw: &RawMesh, frame: &str, clip: Option<f64>, floor: f64) -> Option<Value> {
    let points: Vec<V3> = raw.positions.iter().map(|p| p.map(|x| x as f64)).collect();
    let native = bounds(&points);
    let positions: Vec<V3> = points
        .iter()
        .map(|&p| match frame {
            "cold" => [-p[1], p[0] + 323.8, p[2] + 20.],
            "carbonator" => mapped(p, floor),
            "float" => mapped(p, 14.),
            _ => p,
        })
        .collect();
    let normals: Vec<_> = raw
        .normals
        .iter()
        .map(|p| {
            let p = p.map(|x| x as f64);
            match frame {
                "cold" => [-p[1], p[0], p[2]],
                "carbonator" | "float" => [-p[1], p[2], -p[0]],
                _ => p,
            }
        })
        .flatten()
        .collect();
    let indices: Vec<_> = raw
        .indices
        .chunks_exact(3)
        .filter(|tri| clip.is_none_or(|floor| tri.iter().all(|&i| points[i as usize][2] >= floor)))
        .flatten()
        .copied()
        .collect();
    if indices.is_empty() {
        return None;
    }
    let section: Vec<_> = indices
        .chunks_exact(3)
        .enumerate()
        .filter(|(_, tri)| tri.iter().all(|&i| positions[i as usize][2].abs() < 1e-5))
        .map(|(i, _)| i)
        .collect();
    let cut: Vec<_> = section
        .iter()
        .flat_map(|&i| indices[i * 3..i * 3 + 3].iter().copied())
        .collect();
    Some(
        json!({"name":raw.name,"group":match frame{"faucet"=>"faucet","carbonator"=>"carbonator-hardware","float"=>"magnetic-float",_=>group(&raw.name)},"role":if frame=="float"{if raw.name=="float-aero"{"float-body"}else{"float-magnet"}}else{role(&raw.name)},"color":raw.color.unwrap_or([0.4;3]),"positions":positions.iter().flatten().copied().collect::<Vec<_>>(),"normals":normals,"indices":indices,"bounds":bounds(&positions),"nativeBounds":native,"sourceTriangles":raw.indices.len()/3,"triangles":indices.len()/3,"sectionTriangleOrdinals":section,"sectionFaceIndices":cut,"sectionTriangles":section.len()}),
    )
}
fn bundle(
    out: &Path,
    source: &str,
    target: &str,
    frame: &str,
    selected: impl Fn(&str) -> bool,
    clip: Option<f64>,
) -> Result<Value> {
    let path = root().join(source);
    let data = crate::scene::read_payload(source, &selected)?;
    let floor = carbonator::INTERIOR_Z[0];
    let meshes: Vec<_> = data
        .iter()
        .filter(|m| selected(&m.name))
        .filter_map(|m| mesh(m, frame, clip, floor))
        .collect();
    ensure!(!meshes.is_empty(), "selected native bundle has meshes");
    compressed(
        &out.join(target),
        &json!({"version":1,"units":"mm","frame":match frame{"faucet"=>"faucet-z-up","carbonator"=>"carbonator-local-y-up","float"=>"float-magnet-centered-y-up",_=>"enclosure-z-up"},"colorSpace":"linear-srgb","source":source,"sourceSha256":sound::hash(&path)?,"meshes":meshes}),
    )
}
fn coil_path(out: &Path) -> Result<()> {
    let floor = carbonator::INTERIOR_Z[0];
    let wrap: Vec<_> = coil::wrap_points()
        .into_iter()
        .map(|p| mapped(p, floor))
        .collect();
    let tail = |which: coil::Tail| {
        let form = coil::tail_form(which, false);
        let mut points = vec![form.segments[0].start()];
        for segment in &form.segments {
            let n = (segment.length() / 1.5).ceil().max(1.) as usize;
            for i in 1..=n {
                let t = i as f64 / n as f64;
                let p = match segment {
                    coil::Segment::Straight { start, end, .. } => {
                        add(*start, mul(sub(*end, *start), t))
                    }
                    coil::Segment::Bend {
                        start,
                        tangent,
                        normal,
                        radius,
                        degrees,
                        ..
                    } => {
                        let a = degrees.to_radians() * t;
                        add(
                            add(*start, mul(*tangent, radius * a.sin())),
                            mul(*normal, radius * (1. - a.cos())),
                        )
                    }
                };
                points.push(p);
            }
        }
        points
            .into_iter()
            .map(|p| mapped(p, floor))
            .collect::<Vec<_>>()
    };
    let mut inlet = tail(coil::Tail::Inlet);
    inlet.reverse();
    let outlet = tail(coil::Tail::Outlet);
    let flow: Vec<_> = inlet
        .iter()
        .copied()
        .chain(wrap.iter().skip(1).copied())
        .chain(outlet.iter().skip(1).copied())
        .collect();
    write(
        out.join("coil-path.json"),
        serde_json::to_vec(
            &json!({"units":"mm","frame":"three-y-up, radial center at origin, internal floor y=0","wraps":coil::WRAPS,"nominalRadius":coil::WIND_RADIUS,"tubeRadius":coil::TUBE_RADIUS,"nativeFloorZ":floor,"lowY":coil::LOW_Z-floor,"highY":coil::HIGH_Z-floor,"source":"hardware/cold-core-layout/coil/numbers.rs","sourceSha256":sound::hash(&root().join("hardware/cold-core-layout/coil/numbers.rs"))?,"wrapPoints":wrap,"inletPoints":inlet,"outletPoints":outlet,"flowPoints":flow,"flowDirection":"inlet through lower coil end and winding to outlet"}),
        )?,
    )
}
fn lumen(name: &str, incoming: bool) -> (Vec<V3>, Value) {
    let p = carbonator::port(name);
    let collet = if carbonator::COLLET_PORTS.contains(&name) {
        add(p.mouth, mul(p.out, carbonator::collet::STANDOFF))
    } else {
        p.mouth
    };
    let tip = p.male_tip();
    let radius = 1.5;
    let mut points = vec![collet, p.mouth, add(p.corner, mul(p.out, radius))];
    let center = add(p.corner, mul(add(p.out, p.up), radius));
    for i in 1..=12 {
        let a = std::f64::consts::FRAC_PI_2 * i as f64 / 12.;
        points.push(sub(
            sub(center, mul(p.up, radius * a.cos())),
            mul(p.out, radius * a.sin()),
        ));
    }
    points.push(tip);
    if !incoming {
        points.reverse();
    }
    let floor = carbonator::INTERIOR_Z[0];
    (
        points.into_iter().map(|p| mapped(p, floor)).collect(),
        json!({"corner":mapped(p.corner,floor),"maleTip":mapped(tip,floor),"elbowMouth":mapped(p.mouth,floor),"colletMouth":mapped(collet,floor),"up":mapped(p.up,0.),"out":mapped(p.out,0.)}),
    )
}
fn pressure(out: &Path) -> Result<Vec<Value>> {
    let source = "hardware/cold-core-layout/cold-core-assembly.step.mesh";
    let floor = carbonator::INTERIOR_Z[0];
    let selected = |n: &str| {
        n == "carbonator-tube"
            || n.starts_with("endcap-")
            || n == "float-rod-carb"
            || n == "float-stop-carb-top"
            || n.starts_with("carbonator-elbow-")
            || n == "water-inlet-jet-cap-nominal"
            || n.starts_with("collet-")
            || n.starts_with("prv-")
            || n == "reed-bridge"
            || n.starts_with("reed-carb-")
            || n == "probe-carbonator-ds18b20"
    };
    let mut bundles = vec![bundle(
        out,
        source,
        "carbonator-hardware-full.json",
        "carbonator",
        selected,
        None,
    )?];
    let bodies =
        hsm_kernel::import::bodies(&crate::scene::payload_bytes(source, &selected)?, source)?;
    let mut meshes = Vec::new();
    for body in bodies.iter().filter(|b| selected(&b.name)) {
        if body.solid.bounds().max.x < 0. {
            continue;
        }
        let solid = body.solid.trim(&Plane::YZ)?;
        if solid.is_empty() {
            continue;
        }
        let bytes = hsm_kernel::write::payload_bytes(
            &[Body {
                name: &body.name,
                color: body.color,
                solid: &solid,
            }],
            None,
            None,
        );
        for raw in hsm_render::payload::decode(&bytes)? {
            if let Some(mesh) = mesh(&raw, "carbonator", None, floor) {
                meshes.push(mesh);
            }
        }
    }
    bundles.push(compressed(&out.join("carbonator-hardware-section.json"),&json!({"version":1,"units":"mm","frame":"carbonator-local-y-up","colorSpace":"linear-srgb","source":source,"sourceSha256":sound::hash(&root().join(source))?,"section":{"keptHalfSpace":"local z <= 0","plane":[0,0,-1,0],"cutFacesAreGeometry":true},"meshes":meshes}))?);
    let float_source =
        "hardware/printed-parts/cold-core/magnetic-float/all-aero/assembly.step.mesh";
    bundles.push(bundle(
        out,
        float_source,
        "magnetic-float-cad.json",
        "float",
        |n| n == "float-aero" || n == "RC62",
        None,
    )?);
    let (water, wp) = lumen("water-in", true);
    let (gas, gp) = lumen("co2-in", true);
    let (outlet, op) = lumen("carb-water-out", false);
    let p = carbonator::port("water-in");
    let tip = p.male_tip();
    let jet = mapped(add(tip, mul(p.up, carbonator::jet::CAP_THICKNESS)), floor);
    let axis = carbonator::rod_xy();
    use hsm_aero_float_numbers as f;
    let immersion = -f::magnet_above_waterline(f::design_mass_g(), f::WATER_DENSITY);
    let data = json!({"units":"mm","frame":"carbonator-local-y-up; inner floor y=0; axis x=z=0","nativeColdCoreMapping":["-cc.y",format!("cc.z-{floor}"),"-cc.x"],"jetExit":jet,"jetEntrance":mapped(tip,floor),"jetDiameter":carbonator::jet::PASSAGE_DIAMETER,"jetCapThickness":carbonator::jet::CAP_THICKNESS,"waterLumen":water,"gasLumen":gas,"outletLumen":outlet,"waterJetPassage":[mapped(tip,floor),jet],"lumenDiameter":carbonator::street_elbow::BORE,"recommendedFluidRadius":2.7,"gasExit":gp["maleTip"],"waterOutlet":op["maleTip"],"ports":{"water-in":wp,"co2-in":gp,"carb-water-out":op},"vessel":{"outerRadius":carbonator::PLATE_DIAMETER/2.,"innerRadius":carbonator::PLATE_DIAMETER/2.-3.175,"insideHeight":carbonator::INTERIOR_Z[1]-floor,"tubeY":[carbonator::BOTTOM_Z-floor,carbonator::BOTTOM_Z+carbonator::HEIGHT-floor],"bottomPlateY":carbonator::BOTTOM_PLATE_Z.map(|x|x-floor),"topPlateY":carbonator::TOP_PLATE_Z.map(|x|x-floor)},"guide":{"axisXZ":[-axis[1],-axis[0]],"diameter":carbonator::ROD_DIAMETER,"rangeY":carbonator::ROD_Z.map(|x|x-floor)},"float":{"asset":"magnetic-float-cad.json","diameter":f::DIAMETER,"height":f::height(),"guideBoreDiameter":f::BORE_DIAMETER,"pocketDepth":f::POCKET_DEPTH,"localY":[-f::height()/2.,f::height()/2.],"magnetCenter":[0,0,0],"magnetCenterBelowWater":immersion,"position":[-axis[1],format!("level-{immersion}"),-axis[0]],"freeboardAtSizingDensity":f::height()/2.-immersion,"material":{"bodyColor":"#d8d6cf","bodyRoughness":0.78,"bodyMetalness":0,"magnetColor":"#737d88","magnetRoughness":0.35,"magnetMetalness":0.65}},"bundles":bundles});
    write(
        out.join("carbonator-datums.json"),
        serde_json::to_vec_pretty(&data)?,
    )?;
    Ok(bundles)
}
pub fn main(mut args: Args) -> Result<()> {
    let out = args
        .take(&["--out"])
        .map(PathBuf::from)
        .unwrap_or_else(|| explainer::here().join("assets"));
    fs::create_dir_all(&out)?;
    let selected = args.take(&["--bundle"]).unwrap_or_else(|| "all".into());
    let mut manifest = json(explainer::here().join("assets/cad-manifest.json"))?;
    let mut bundles = Vec::new();
    if ["all", "enclosure"].contains(&selected.as_str()) {
        let exterior = [
            "enclosure-front-bottom",
            "enclosure-front-top",
            "enclosure-back-bottom",
            "enclosure-back-top",
            "display/1",
            "display/2",
            "display-cover",
            "display-gasket",
            "funnel",
            "funnel-cover",
            "funnel-frame",
            "compressor/1",
            "compressor/2",
            "condenser+fan",
            "psu",
            "pump-a-head",
            "pump-a-boss",
            "pump-a-motor",
            "pump-b-head",
            "pump-b-boss",
            "pump-b-motor",
            "c14-inlet",
            "pcba",
        ];
        bundles.push(bundle(
            &out,
            "hardware/manifold-layout/enclosure-assembly.step.mesh",
            "enclosure-cad.json",
            "enclosure",
            |n| exterior.contains(&n),
            None,
        )?);
    }
    if ["all", "cold-core"].contains(&selected.as_str()) {
        bundles.push(bundle(
            &out,
            "hardware/cold-core-layout/cold-core-assembly.step.mesh",
            "cold-core-cad.json",
            "cold",
            |n| {
                [
                    "foam-",
                    "carbonator-",
                    "endcap-",
                    "float-rod-",
                    "float-",
                    "reservoir-",
                    "evap-",
                    "collet-",
                    "prv-",
                    "reed-",
                ]
                .iter()
                .any(|p| n.starts_with(p))
                    || [
                        "water-inlet-jet-cap-nominal",
                        "probe-carbonator-ds18b20",
                        "probe-coil-ds18s20",
                    ]
                    .contains(&n)
            },
            None,
        )?);
    }
    if ["all", "faucet"].contains(&selected.as_str()) {
        let names = [
            "westbrass",
            "soda_faucet_tube",
            "flavor_tube_pos_x",
            "flavor_tube_neg_x",
            "lever",
            "above_counter_plate",
            "above_counter_gasket",
            "shell_base",
            "shell_tip",
            "faucet-display-cover-seated",
            "faucet_display",
            "faucet_display_screen",
        ];
        bundles.push(bundle(
            &out,
            "hardware/faucet-layout/faucet-assembly.step.mesh",
            "faucet-cad.json",
            "faucet",
            |n| names.contains(&n),
            Some(-0.2),
        )?);
        let image = crate::kitchen::texture(1, &out)?;
        fs::rename(image, out.join("faucet-display-flavor1.png"))?;
        let mut datums = json(explainer::here().join("assets/faucet-datums.json"))?;
        datums["source"] = json!("tools/hsm/marketing/src/film/beverage.rs");
        write(
            out.join("faucet-datums.json"),
            serde_json::to_vec_pretty(&datums)?,
        )?;
    }
    if ["all", "coil"].contains(&selected.as_str()) {
        coil_path(&out)?;
    }
    if ["all", "carbonator"].contains(&selected.as_str()) {
        let pressure = pressure(&out)?;
        manifest["carbonatorAnimation"] =
            json!({"datums":"carbonator-datums.json","bundles":pressure});
    }
    if !bundles.is_empty() {
        let previous = manifest["bundles"]
            .as_array_mut()
            .context("bundle manifest")?;
        for bundle in bundles {
            if let Some(existing) = previous.iter_mut().find(|b| b["file"] == bundle["file"]) {
                *existing = bundle;
            } else {
                previous.push(bundle);
            }
        }
    }
    for name in [
        "wordmark.svg",
        "wordmark-reverse.svg",
        "wordmark-stacked.svg",
        "mark.svg",
        "mark-white.svg",
        "mark-blue.svg",
    ] {
        fs::copy(root().join("web/public/brand").join(name), out.join(name))?;
    }
    fs::copy(root().join("brand/palette.json"), out.join("palette.json"))?;
    manifest["faucetSurfaceNormals"] = json!("Current source payload normals");
    manifest["notes"] = json!([
        "Current payload arrays preserve their native solid placements and linear-sRGB colors.",
        "Compressed bundles are the saved film inputs; plain JSON files are local working copies."
    ]);
    write(
        out.join("cad-manifest.json"),
        serde_json::to_vec_pretty(&manifest)?,
    )?;
    println!("{}", out.display());
    Ok(())
}
