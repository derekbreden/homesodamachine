//! Transfer the hand-selected three-dot spring and fixed cheek to the three full fitted bench mounts.
#[allow(dead_code)]
#[path = "../../../tools/hsm/print-prep/src/mesh.rs"]
mod mesh;

use super::{HERE, sha, write_json};
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Affine, Face, Plane, Profile, Solid, V3, import, reads, stl_bytes, v2, v3};
use serde_json::{Value, json};
use std::{fs, path::Path};

const DONOR: &str = "hardware/print-tests/open-snap-section/parts/easy-entry";
const CAPS: &str =
    "hardware/printed-parts/enclosure/rear-equipment-caps/rear-equipment-caps-installed.step.npz";
const BACK: f64 = -5.40; // A cut inside the old neck, in solid backing outside the hardware passages.
const LAP: f64 = 0.15;

#[derive(Clone, Copy, PartialEq)]
enum Mount {
    Asse,
    Meter,
    Water,
}

impl Mount {
    fn names(self) -> (&'static str, &'static str) {
        match self {
            Self::Asse => ("asse-snap-cap", "asse-receiver"),
            Self::Meter => ("meter-snap-cap", "meter-receiver"),
            Self::Water => ("regulator-snap-cap", "water-regulator-receiver"),
        }
    }

    /// In the working frame X crosses the two wings, Y runs along each catch, and +Z closes the cover.
    fn to_machine(self) -> Affine {
        match self {
            Self::Asse => Affine::IDENTITY,
            Self::Meter => Affine::from_columns(-V3::Z, V3::Y, V3::X, V3::ZERO),
            Self::Water => Affine::from_columns(V3::Y, -V3::X, V3::Z, V3::ZERO),
        }
    }

    fn print_axis(self) -> V3 {
        if self == Self::Water { V3::Y } else { V3::X }
    }
}

fn inverse_rigid(pose: &Affine) -> Affine {
    let m = pose.m;
    let mut inv = Affine::IDENTITY;
    for i in 0..3 {
        for j in 0..3 {
            inv.m[i][j] = m[j][i];
        }
        inv.m[i][3] = -(0..3).map(|j| m[j][i] * m[j][3]).sum::<f64>();
    }
    inv
}

fn box3(x: [f64; 2], y: [f64; 2], z: [f64; 2]) -> Solid {
    Solid::cuboid(v3(x[0], y[0], z[0]), v3(x[1], y[1], z[1]))
}

fn facet_solid(vertices: &[V3], faces: &[[u32; 3]]) -> Result<Solid> {
    Solid::from_mesh(
        vertices,
        faces,
        &vec![0; faces.len()],
        &[Face::from_json(&Value::Null)?],
    )
}

/// Read a bench STL in the specimen's native machine coordinates before copying a working face.
fn coupon(dir: &Path, data: &Value, name: &str, origin: V3) -> Result<Solid> {
    let row = &data["parts"][name];
    let transform = Affine {
        m: serde_json::from_value(row["assembly_to_print_matrix_mm"].clone())?,
    };
    let revert = inverse_rigid(&transform);
    let mesh = mesh::Mesh::read_stl(&dir.join(row["stl"].as_str().context("coupon STL")?))?;
    let vertices: Vec<_> = mesh
        .vertices
        .into_iter()
        .map(|p| {
            let mut p = revert.point(p.into()) - origin;
            for x in [0., -2.] {
                if (p.x - x).abs() < 2e-6 {
                    p.x = x;
                }
            }
            if p.z.abs() < 2e-6 {
                p.z = 0.;
            }
            p
        })
        .collect();
    facet_solid(
        &vertices,
        &mesh
            .faces
            .into_iter()
            .map(|f| f.map(|i| i as u32))
            .collect::<Vec<_>>(),
    )
}

struct Donor {
    wing: Solid,
    cheek: Solid,
    join: f64,
    rim: f64,
    pilot: f64,
    lip: f64,
    lip_height: f64,
    deep: f64,
}

impl Donor {
    fn read() -> Result<Self> {
        let dir = Path::new(DONOR);
        let data = reads::json(dir.join("geometry.json"))?;
        let number = |k: &str| {
            data[k]
                .as_f64()
                .with_context(|| format!("donor dimension {k}"))
        };
        let source = &data["parts"]["cover-3"];
        let cover_bounds: [[f64; 3]; 2] =
            serde_json::from_value(source["nominal_machine_bounds_mm"].clone())?;
        let edge = cover_bounds[1][0];
        let axis = number("axis_x_mm")?;
        let y = number("axis_y_mm")?;
        let roof_h = number("roof_h_mm")?;
        let stop = number("back_face_z_mm")? - roof_h;
        let travel = number("cover_seating_travel_mm")?;
        let join = roof_h - number("join_h_mm")?;
        let cover = coupon(dir, &data, "cover-3", v3(edge, y, stop - travel))?;
        let entire_side = cover.intersect(&box3([-6.0, 1.0], [-8., 8.], [join - LAP, 1.]))?;
        let wing = entire_side
            .components()
            .into_iter()
            .max_by(|a, b| a.bounds().max.z.total_cmp(&b.bounds().max.z))
            .context("donor spring")?;
        let receiver = coupon(dir, &data, "receiver-3", v3(edge, y, stop))?;
        let spec = &data["pairs"][2];
        ensure!(spec["number"] == 3, "three-dot working faces");
        let entrance: [[f64; 2]; 3] =
            serde_json::from_value(spec["receiver_entrance_r_h_mm"].clone())?;
        let rim = roof_h - entrance[2][1];
        let pilot = entrance[2][0] - (edge - axis);
        let lip = entrance[0][0] - (edge - axis);
        let lip_height = roof_h - entrance[0][1];
        let guide: Vec<[f64; 2]> = serde_json::from_value(spec["receiver_guide_r_h_mm"].clone())?;
        let local = |[r, h]: [f64; 2]| v2(r - (edge - axis), roof_h - h);
        let end = local(*guide.last().context("end of receiver guide")?);
        let neck = receiver
            .verts()
            .iter()
            .filter(|p| p.z < end.y - 0.02 && p.z > lip_height + 0.02 && p.x > BACK && p.x < end.x)
            .min_by(|a, b| a.x.total_cmp(&b.x))
            .context("neck of the donor's 45-degree retaining shoulder")?;
        let deep = neck.x;
        let mut profile = vec![v2(BACK - LAP, 0.)];
        profile.extend(guide.into_iter().map(local));
        profile.push(v2(neck.x, neck.z));
        profile.extend(entrance.into_iter().map(local));
        // The mouth continues into pre-existing solid below the bevel on mounts with deeper seats.
        profile.extend([v2(pilot, rim - LAP), v2(BACK - LAP, rim - LAP)]);
        let cheek = Plane::XZ
            .at(v3(0., -1., 0.))
            .extrude(&Profile::polygon(&profile), -2.)?;
        Ok(Self {
            wing,
            cheek,
            join,
            rim,
            pilot,
            lip,
            lip_height,
            deep,
        })
    }
}

struct Side {
    sign: f64,
    edge: f64,
    span: [f64; 2],
    lane: [f64; 2],
    join: f64,
    crest: f64,
    roof: f64,
}

impl Side {
    fn measure(cap: &Solid, receiver: &Solid, sign: f64) -> Result<Self> {
        let b = cap.bounds();
        let edge = if sign > 0. { b.max.x } else { b.min.x };
        let crest = b.max.z;
        let at_edge: Vec<_> = cap
            .verts()
            .iter()
            .filter(|p| (p.x - edge).abs() < 1e-5 && (p.z - crest).abs() < 1e-5)
            .collect();
        let span = [
            at_edge
                .iter()
                .map(|p| p.y)
                .reduce(f64::min)
                .context("spring fore end")?,
            at_edge
                .iter()
                .map(|p| p.y)
                .reduce(f64::max)
                .context("spring aft end")?,
        ];
        let inner = edge - sign * 2.;
        let join = cap
            .verts()
            .iter()
            .filter(|p| (p.x - inner).abs() < 1e-5)
            .map(|p| p.z)
            .reduce(f64::min)
            .context("end of spring root radius")?
            + 0.35;
        let y = (span[0] + span[1]) * 0.5;
        let probe = edge - sign * 0.45;
        let roof = receiver.intersect(&box3(
            [probe - 0.01, probe + 0.01],
            [y - 0.01, y + 0.01],
            [crest - 0.01, crest + 3.],
        ))?;
        ensure!(
            !roof.is_empty(),
            "fixed receiver must stop the original crest"
        );
        let lane = [span[0] - 0.25, span[1] + 0.25];
        Ok(Self {
            sign,
            edge,
            span,
            lane,
            join,
            crest,
            roof: roof.bounds().min.z,
        })
    }

    fn box_at(&self, r: [f64; 2], span: [f64; 2], height: [f64; 2]) -> Solid {
        let [a, b] = r.map(|v| self.edge + self.sign * v);
        box3([a.min(b), a.max(b)], span, height)
    }

    fn project(
        &self,
        stock: &Solid,
        span: [f64; 2],
        base: f64,
        shift: impl Fn(f64) -> f64,
    ) -> Result<Solid> {
        let b = stock.bounds();
        let k = (span[1] - span[0]) / b.size().y;
        let points: Vec<_> = stock
            .verts()
            .iter()
            .map(|p| {
                v3(
                    self.edge + self.sign * p.x,
                    span[0] + k * (p.y - b.min.y),
                    base + p.z + shift(p.z),
                )
            })
            .collect();
        let mut faces = stock.tris().to_vec();
        if self.sign < 0. {
            for f in &mut faces {
                f.swap(1, 2);
            }
        }
        facet_solid(&points, &faces)
    }

    fn fit(
        &self,
        donor: &Donor,
        cap: &Solid,
        receiver: &Solid,
        mount: Mount,
    ) -> Result<(Solid, Solid)> {
        let crest = self.crest;
        let roof = self.roof;
        let seam = self.join;
        let delta = seam - (crest + donor.join);
        let (span, cut_z) = if delta.abs() < 1e-6 {
            (self.span, seam)
        } else {
            // The adjusted shank joins in its straight stock and clears the old wing's end faces.
            ([self.span[0] - 0.02, self.span[1] + 0.02], seam - 0.10)
        };
        let cap = cap.cut_all(&[
            self.box_at([-2.70, 1.], span, [cut_z, crest + 1.]),
            self.box_at([BACK, 1.], span, [crest - 13., crest + 1.]),
        ])?;
        // The root transition absorbs the station's shank length. The outer 19 mm use the unscaled coupon.
        let wing = self.project(&donor.wing, self.span, crest, |z| {
            let t = ((z - donor.join) / 9.).clamp(0., 1.);
            delta * (1. - t * t * (3. - 2. * t))
        })?;
        let cap = cap.union(&wing)?;
        let bottom = receiver.bounds().min.z - 1.;
        let receiver = receiver.cut_all(&[
            self.box_at([BACK, 5.5], self.lane, [roof + donor.rim, roof]),
            self.box_at([donor.pilot, 5.5], self.lane, [bottom, roof + donor.rim]),
        ])?;
        // The turned water fixture's full end walls carry both ends of each cheek.
        let seat_y = if mount == Mount::Water {
            [self.lane[0] - LAP, self.lane[1] + LAP]
        } else {
            self.lane
        };
        let cheek = self.project(&donor.cheek, seat_y, roof, |_| 0.)?;
        Ok((cap, receiver.union(&cheek)?))
    }
}

fn write_part(dir: &Path, name: &str, native: &Solid, transform: &Affine) -> Result<Value> {
    native.check()?;
    ensure!(
        native.components().len() == 1,
        "{name} must be one connected solid"
    );
    let bytes = stl_bytes(&[&native.transformed(transform)])?;
    mesh::Mesh::from_corners(&mesh::stl_corners(&bytes)?).check_closed_single_body(name)?;
    fs::write(dir.join(format!("{name}.stl")), &bytes)?;
    let b = native.bounds();
    Ok(
        json!({"sha256":sha(&bytes),"volume_mm3":native.volume(),"connected_solids":1,
        "installed_bounds_mm":[b.min.to_array(),b.max.to_array()],"assembly_to_stl_matrix_mm":transform.m}),
    )
}

fn bounds(stock: &Solid, to_machine: &Affine) -> [f64; 6] {
    let b = stock.transformed(to_machine).bounds();
    [b.min.x, b.max.x, b.min.y, b.max.y, b.min.z, b.max.z]
}

fn print_features(
    dir: &Path,
    mount: Mount,
    donor: &Donor,
    sides: &[Side],
    digest: &Value,
) -> Result<()> {
    let name = mount.names().1;
    let mut features =
        reads::json(Path::new(HERE).join(format!("parts/{name}.print-features.json")))?;
    features["producer"] = json!("equipment-snap-receivers --three-dot");
    features["source_stl_sha256"] = digest.clone();
    let pose = mount.to_machine();
    for row in features["support_free_regions"]
        .as_array_mut()
        .context("receiver support exclusions")?
    {
        let label = row["name"].as_str().unwrap_or("");
        if !label.contains("catch pocket") && !label.contains("upper cap pocket") {
            continue;
        }
        let sign = if label.contains("west") || label.contains("fore") || label.contains("upper") {
            -1.
        } else {
            1.
        };
        let side = sides
            .iter()
            .find(|s| s.sign == sign)
            .context("wing on the named side of the receiver")?;
        let keep = side.box_at(
            [donor.deep - 0.25, 0.05],
            side.lane,
            [side.roof + donor.lip_height, side.roof],
        );
        let bound = bounds(&keep, &pose);
        for k in ["bounds_source_mm", "blocking_bounds_source_mm"] {
            let mut b: [f64; 6] = serde_json::from_value(row[k].clone())?;
            if mount == Mount::Meter {
                b = bound;
                if k == "blocking_bounds_source_mm" {
                    // The printed tree crown spreads beyond its contact box toward the pocket.
                    b[0] -= 1.3;
                }
            } else {
                for i in 0..3 {
                    b[2 * i] = b[2 * i].min(bound[2 * i]);
                    b[2 * i + 1] = b[2 * i + 1].max(bound[2 * i + 1]);
                }
            }
            row[k] = json!(b);
        }
    }
    if mount == Mount::Meter {
        let side = &sides[0];
        let row = features["support_regions"]
            .as_array_mut()
            .context("meter targets")?
            .iter_mut()
            .find(|r| r["name"] == "Accessible flow meter front lip")
            .context("meter entrance support")?;
        let west = row["bounds_source_mm"][0]
            .as_f64()
            .context("meter west face")?;
        let target = side.box_at(
            [donor.pilot - 0.25, donor.lip + 0.25],
            side.lane,
            [west, side.roof + donor.lip_height - 2.4],
        );
        row["bounds_source_mm"] = json!(bounds(&target, &pose));
    }
    write_json(&dir.join(format!("{name}.print-features.json")), &features)
}

pub(super) fn write() -> Result<()> {
    let dir = Path::new(HERE).join("parts/three-dot");
    fs::create_dir_all(&dir)?;
    let donor = Donor::read()?;
    let spec = reads::json(Path::new(HERE).join("inputs.json"))?;
    let shell_file = spec["source_model"].as_str().context("enclosure source")?;
    let shell = import::model(shell_file)?;
    let shell = import::body(&shell, "enclosure-back-top")?;
    let caps = import::model(CAPS)?;
    let mut stations = Vec::new();
    for mount in [Mount::Asse, Mount::Meter, Mount::Water] {
        let (cap_name, seat_name) = mount.names();
        let fixture = spec["receivers"]
            .as_array()
            .context("equipment receiver specifications")?
            .iter()
            .find(|r| r["name"] == seat_name)
            .context("complete receiver crop")?;
        let lo: [f64; 3] = serde_json::from_value(fixture["min_mm"].clone())?;
        let hi: [f64; 3] = serde_json::from_value(fixture["max_mm"].clone())?;
        let seat = shell
            .intersect(&Solid::cuboid(lo.into(), hi.into()))?
            .components()
            .into_iter()
            .find(|b| (b.bounds().max.z - hi[2]).abs() < 1e-5)
            .context("rooted receiver")?;
        let native = import::body(&caps, cap_name)?;
        let world = mount.to_machine();
        let local = inverse_rigid(&world);
        let original = native.transformed(&local);
        let mut cap = original.clone();
        let mut seat = seat.transformed(&local);
        let sides: Vec<_> = [-1., 1.]
            .into_iter()
            .map(|sign| Side::measure(&original, &seat, sign))
            .collect::<Result<_>>()?;
        for side in &sides {
            (cap, seat) = side.fit(&donor, &cap, &seat, mount)?;
        }
        if mount == Mount::Asse {
            // The solid inlet-adapter stock overlaps the last 3 mm of the springs below the ASSE axis.
            let b = original.bounds();
            let inner_root = sides[0].join - 0.35 - 1.5;
            let bridge = box3(
                [b.min.x - 1., b.max.x + 1.],
                [sides[0].span[1] - 3., b.max.y + 1.],
                [b.min.z - 1., inner_root + 10.],
            );
            cap = cap.union(&original.intersect(&bridge)?)?;
        }
        let turn = Affine::rotation(V3::ZERO, mount.print_axis(), 90.);
        let b = native.transformed(&turn).bounds();
        let print =
            Affine::translation(v3(-b.center().x, -b.center().y, -b.min.z)).then_after(&turn);
        let cap_data = write_part(&dir, cap_name, &cap.transformed(&world), &print)?;
        let seat_data = write_part(
            &dir,
            seat_name,
            &seat.transformed(&world),
            &Affine::IDENTITY,
        )?;
        print_features(&dir, mount, &donor, &sides, &seat_data["sha256"])?;
        let wings: Vec<_> = sides.iter().map(|s|json!({"sign":s.sign,"outer_wall_x":s.edge,"spring_join_z":s.join,
            "cover_reference_z":s.crest,"receiver_stop_z":s.roof,"spring_y":s.span,"receiver_y":s.lane,
            "pilot_x":s.edge+s.sign*donor.pilot,"pilot_z":s.roof+donor.rim,
            "lip_x":s.edge+s.sign*donor.lip,"lip_z":s.roof+donor.lip_height})).collect();
        stations.push(
            json!({"cover":cap_name,"receiver":seat_name,"working_to_machine":world.m,"wings":wings,
            "meshes":{cap_name:cap_data,seat_name:seat_data}}),
        );
        println!("{cap_name} + {seat_name}");
    }
    write_json(
        &dir.join("geometry.json"),
        &json!({"purpose":"Register the full hardware-specific three-dot covers, their matched receiver fixtures and the exact coupon they reproduce.",
        "donor":DONOR,"cover_donor_sha256":sha(&fs::read(Path::new(DONOR).join("cover-3.stl"))?),"receiver_donor_sha256":sha(&fs::read(Path::new(DONOR).join("receiver-3.stl"))?),
        "source_installed_caps":CAPS,"source_caps_sha256":sha(&fs::read(CAPS)?),"source_receiver":shell_file,
        "source_receiver_sha256":sha(&fs::read(shell_file)?),"working_frame":"X across wings, Y along hooks, +Z closing. Receiver STLs retain machine coordinates and print -Z up. Covers retain their production slicer frames.","stations":stations}),
    )
}
