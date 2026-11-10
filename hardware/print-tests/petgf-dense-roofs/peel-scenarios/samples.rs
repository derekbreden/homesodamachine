// samples.rs makes D-process roofs with reduced anchoring and crops their enclosure counterparts.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Font, HAlign, Kind, Loop, Plane, Profile, Solid, VAlign, stl_bytes, v2, v3};
use serde_json::{Value, json};

fn point(v: &Value) -> Result<hsm_kernel::V3> {
    Ok(v3(v[0].as_f64().context("x")?,v[1].as_f64().context("y")?,v[2].as_f64().context("z")?))
}

fn main() -> Result<()> {
    let out = hsm_sandbox::out()?;
    let mut spec: Value = serde_json::from_slice(&std::fs::read(out.join("inputs/spec.json"))?)?;
    let ceiling = spec["ceiling_bottom_mm"].as_f64().context("ceiling")?;
    let thick = spec["roof_thickness_mm"].as_f64().context("roof thickness")?;
    let wall = spec["wall_thickness_mm"].as_f64().context("wall thickness")?;
    let label_height = spec["label_height_mm"].as_f64().context("label height")?;
    let font = Font::find("Helvetica Neue", Kind::Bold)?;
    let mut specimens = Vec::new();
    for family in spec["families"].as_array_mut().context("families")? {
        let id = family["id"].as_str().context("id")?.to_owned();
        let name = format!("{id}D");
        let (solid, label_at, z_shift) = if family["kind"] == "panel" {
            let (w,d) = (family["size_mm"][0].as_f64().unwrap(),family["size_mm"][1].as_f64().unwrap());
            let mut outline = Profile::rect(v2(0.,0.),w,d);
            let hole = family["hole_diameter_mm"].as_f64().unwrap();
            if hole > 0. { outline = outline.with_hole(Loop::circle(v2(0.,0.),hole/2.)); }
            let mut panel = Plane::XY.extrude(&outline,thick)?.translate(v3(0.,0.,ceiling));
            let anchor = match family["wall"].as_str().unwrap() {
                "west" => Some(Solid::cuboid(v3(-w/2.,-d/2.,0.),v3(-w/2.+wall,d/2.,ceiling+0.05))),
                "back" => Some(Solid::cuboid(v3(-w/2.,d/2.-wall,0.),v3(w/2.,d/2.,ceiling+0.05))),
                _ => None,
            };
            if let Some(anchor) = anchor { panel = panel.union(&anchor)?; }
            if family["wall"] == "none" {
                let witness = Solid::cuboid(v3(-2.,-d/2.-10.,0.),v3(2.,-d/2.-6.,ceiling));
                panel = panel.union(&witness)?;
            }
            (panel,v3(0.,6.,ceiling+thick),0.)
        } else {
            let imported = hsm_kernel::import::model(out.join("inputs").join(format!("{id}.npz")))?;
            let original = imported[0].solid.translate(v3(0.,0.,family["source_z_shift_mm"].as_f64().unwrap()));
            let crop = original.intersect(&Solid::cuboid(point(&family["crop_min_mm"])? ,point(&family["crop_max_mm"])?))?;
            let shift = -crop.bounds().min.z;
            let at = point(&family["label_center_world_mm"])? + v3(0.,0.,shift);
            (crop.translate(v3(0.,0.,shift)),at,shift)
        };
        let bodies = if family["wall"] == "none" {2} else {1};
        ensure!(solid.components().len()==bodies,"{name} retains its intended model bodies");
        let letters = Plane::XY.text(&font,&name,3.,label_height+0.05,HAlign::Center,VAlign::Center)?
            .translate(label_at-v3(0.,0.,0.05));
        let solid = solid.union(&letters)?;
        ensure!(solid.components().len()==bodies,"{name} label stays on the top surface");
        solid.check()?;
        std::fs::write(out.join(format!("{name}.stl")),stl_bytes(&[&solid])?)?;
        let b = solid.bounds();
        family["actual_crop_min_z_mm"] = json!(-z_shift);
        specimens.push(json!({"id":name,"family":id,"condition":"D",
            "bounds_mm":[[b.min.x,b.min.y,b.min.z],[b.max.x,b.max.y,b.max.z]],
            "volume_mm3":solid.volume(),"world_z_to_print_z_mm":z_shift,"watertight":true,"solids":bodies,
            "detached_witness_post":bodies==2}));
    }
    std::fs::write(out.join("geometry.json"),serde_json::to_vec_pretty(&json!({"spec":spec,"specimens":specimens}))?)?;
    println!("{}",out.join("geometry.json").display());
    Ok(())
}
