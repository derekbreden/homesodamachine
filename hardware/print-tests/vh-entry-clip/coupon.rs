//! Crop the V-H saddle from the production print mesh and give the upright wall a stable bench foot.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Face, Solid, Surface, V3, file_src, stl_bytes, v3};
use hsm_print_prep::mesh::Mesh;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const ENC: &str = "hardware/printed-parts/enclosure/enclosure";
const NAME: &str = "vh-entry-clip";
const EDGE: f64 = 3.;
const FOOT: f64 = 2.4;

fn digest(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn main() -> Result<()> {
    let source = Path::new(ENC).join("enclosure-front-top.stl");
    let out = Path::new("hardware/print-tests/vh-entry-clip/parts");
    let features_path = source.with_extension("print-features.json");
    let regions_path = Path::new(ENC).join("heat-set-review/print-regions.json");
    let features: Value = serde_json::from_slice(&fs::read(&features_path)?)?;
    let regions: Value = serde_json::from_slice(&fs::read(&regions_path)?)?;
    let sha = digest(&fs::read(&source)?);
    ensure!(
        features["source_stl_sha256"] == sha
            && regions["native_artifact_sha256"]["front-top"][".stl"] == sha,
        "the clip and reinforcement records must describe the current production mesh"
    );

    let guide = features["support_free_regions"]
        .as_array()
        .context("support regions")?
        .iter()
        .find(|r| r["name"] == "V-H upright entry clip")
        .context("upright saddle")?;
    let [x0, x1, y0, y1, z0, z1]: [f64; 6] =
        serde_json::from_value(guide["bounds_source_mm"].clone())?;
    let mesh = Mesh::read_stl(&source)?;
    let (source_min, _) = mesh.bounds();
    let layer = 0.24;
    let base = source_min[2] + layer * ((z0 - EDGE - FOOT - source_min[2]) / layer).floor();
    let low = v3(x0 - EDGE, y0 - 3. * EDGE, base);
    let high = v3(x1 + EDGE, y1 + EDGE, z1 + EDGE);
    let vertices: Vec<_> = mesh.vertices.iter().copied().map(V3::from).collect();
    let tris: Vec<_> = mesh.faces.iter().map(|f| f.map(|i| i as u32)).collect();
    let face = Face::new(
        Surface::Free { kind: "STL" },
        "coupon",
        file_src(source.to_str().context("source STL path")?),
    );
    let quadrant = Solid::from_mesh(&vertices, &tris, &vec![0; tris.len()], &[face])?;
    let wall = quadrant.intersect(&Solid::cuboid(low, high))?;
    ensure!(
        wall.components().len() == 1,
        "crop must retain the saddle attached to the wall"
    );
    let foot = Solid::cuboid(low, v3(high.x, high.y, base + FOOT));
    let coupon = wall.union(&foot)?;
    coupon.check()?;
    ensure!(
        coupon.components().len() == 1,
        "the printed coupon must be a single body"
    );
    let bytes = stl_bytes(&[&coupon])?;
    let coupon_sha = digest(&bytes);
    fs::create_dir_all(out)?;
    fs::write(out.join(format!("{NAME}.stl")), bytes)?;
    let save = |name: &str, record: Value| -> Result<()> {
        fs::write(out.join(name), serde_json::to_vec_pretty(&record)?)?;
        Ok(())
    };
    let mut modifiers = vec![];
    for row in regions["pieces"]["front-top"]
        .as_array()
        .context("front-top infill regions")?
    {
        let [a, b, c, d, e, f]: [f64; 6] =
            serde_json::from_value(row["applied_source_bounds_mm"].clone())?;
        let bound = [
            a.max(low.x),
            b.min(high.x),
            c.max(low.y),
            d.min(high.y),
            e.max(low.z + FOOT),
            f.min(high.z),
        ];
        if bound.chunks_exact(2).all(|p| p[0] < p[1]) {
            let mut copy = row.clone();
            copy["machine_bounds_mm"] = json!(bound);
            copy["applied_source_bounds_mm"] = json!(bound);
            modifiers.push(copy);
        }
    }
    ensure!(!modifiers.is_empty(), "retain production reinforcement");
    save(
        "vh-entry-clip.print-regions.json",
        json!({
            "native_artifact_sha256": {NAME:{".stl":coupon_sha}}, "pieces": {NAME:modifiers}, "source":regions_path
        }),
    )?;
    save(
        "vh-entry-clip.print-features.json",
        json!({
            "producer":NAME,"source_stl_sha256":coupon_sha,"boundary_overlap_mm":features["boundary_overlap_mm"],
            "support_free_regions":[guide]
        }),
    )?;
    save(
        "geometry.json",
        json!({
            "source":source,"source_stl_sha256":sha,"coupon_stl_sha256":coupon_sha,
            "production_crop_bounds_mm":[low.to_array(),high.to_array()],
            "coupon_foot_top_z_mm":base+FOOT,"coupon_foot_to_lowest_guide_mm":z0-base-FOOT,
            "bounds_mm":[coupon.bounds().min.to_array(),coupon.bounds().max.to_array()],
            "volume_mm3":coupon.volume(),"watertight":true,"connected_solids":1
        }),
    )
}
