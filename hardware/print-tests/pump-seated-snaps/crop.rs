//! Cut the bare G-Ganen pump's complete receiver from the production lid in its original print frame.
use anyhow::{Context, Result, ensure};
use hsm_cold_core_layout::cap::{cap_face_z, cap_lid_pose, world_to_cap};
use hsm_foam_cap_numbers::air_holes;
use hsm_foam_cap_numbers::pump::{self, wing};
use hsm_kernel::{Solid, import, stl_bytes, v3};
use serde_json::json;
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const LID: &str = "hardware/printed-parts/cold-core/foam-cap/foam-cap-lid-top.step.npz";
const OUT: &str = "hardware/print-tests/pump-seated-snaps/parts";

fn main() -> Result<()> {
    let model = import::model(LID)?;
    let lid = import::body(&model, "foam-cap-lid-top")?;
    let c = pump::cradle();
    let [x, _, z] = c.centre;
    let y = c.frame.translation_mm[1];
    let half = c.station.outer + wing::TIP_RELEASE_ROOM + pump::FLANK_STOCK;
    let floor = cap_lid_pose().translation[2] + lid.bounds().min.z;
    let fore = c.selected.cover_channel_fore_native_x_mm - pump::FLANK_STOCK;
    let aft = c.selected.rail_stop_native_x_mm[1][1] + pump::FLANK_STOCK;
    let a = world_to_cap([x - half, y + fore, floor]);
    let b = world_to_cap([x + half, y + aft, z + pump::FLANK_STOCK]);
    let lo = v3(a[0].min(b[0]), a[1].min(b[1]), a[2]);
    let hi = v3(a[0].max(b[0]), a[1].max(b[1]), b[2]);
    let passage = air_holes().into_iter()
        .find(|h| (lo.x..hi.x).contains(&h.xy[0]) && (lo.y..hi.y).contains(&h.xy[1]))
        .context("the air passage beside the east release pocket")?;
    let border = passage.radius + pump::FLANK_STOCK;
    let air_lo = v3(passage.xy[0] - border, passage.xy[1] - border, lo.z);
    let air_hi = v3(passage.xy[0] + border, passage.xy[1] + border, cap_face_z() - cap_lid_pose().translation[2]);
    let crop = Solid::cuboid(lo, hi).union(&Solid::cuboid(air_lo, air_hi))?;
    let coupon = lid.intersect(&crop)?;
    coupon.check()?;
    ensure!(coupon.components().len() == 1, "the complete cradle and lid floor must stay joined");
    ensure!((coupon.bounds().min.z - lid.bounds().min.z).abs() < 1e-6, "retain the production bed datum");
    let bytes = stl_bytes(&[&coupon])?;
    let geometry = json!({
        "source": LID, "source_sha256": format!("{:x}", Sha256::digest(fs::read(LID)?)),
        "stl_sha256": format!("{:x}", Sha256::digest(&bytes)),
        "crop_bounds_lid_mm": [lo.to_array(), hi.to_array()],
        "air_passage_crop_bounds_lid_mm": [air_lo.to_array(), air_hi.to_array()],
        "print_up_lid": [0, 0, 1], "bed_z_mm": coupon.bounds().min.z,
        "connected_solids": 1, "volume_mm3": coupon.volume()
    });
    let out = Path::new(OUT);
    fs::create_dir_all(out)?;
    fs::write(out.join("pump-receiver.stl"), bytes)?;
    let mut data = serde_json::to_vec_pretty(&geometry)?;
    data.push(b'\n');
    fs::write(out.join("geometry.json"), data)?;
    Ok(())
}
