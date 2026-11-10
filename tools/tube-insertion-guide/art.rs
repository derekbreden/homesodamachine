//! Tube insertion illustrations place the retained prints, native stock proxies and current donor surfaces.
use crate::artwork::{self, Scene, color, component};
use crate::tube_fixture::{self as jig, Component, numbers::*};
use anyhow::{Context as _, Result, bail};
use hsm_kernel::{Plane, Profile, Solid, V3, v2, v3};
use serde::Deserialize;
use std::collections::BTreeMap;
use std::path::Path;

const GRIP: &[&str] = &[
    "carrier",
    "lower-jaw",
    "upper-jaw",
    "lower-liner",
    "upper-liner",
    "clamp-front-m5x50",
    "clamp-rear-m5x50",
    "clamp-front-washer",
    "clamp-rear-washer",
    "clamp-front-nut",
    "clamp-rear-nut",
    "carrier-front-m5x20",
    "carrier-rear-m5x20",
    "carrier-front-nut",
    "carrier-rear-nut",
];
pub const NAMES: &[&str] = &[
    "hero",
    "load-path",
    "faucet-lever",
    "plate-rigid",
    "plate-liners",
    "hardware",
    "clean-base",
    "carrier-joint",
    "carrier",
    "liners",
    "jaws",
    "puck",
    "preset-travel",
    "handles-clear",
    "depth",
    "marks",
    "sleeve-fit",
    "grip-mark",
    "donor-in",
    "engage",
    "press",
    "release",
    "workpiece",
    "sleeved-tube",
];
fn accent() -> [f64; 3] {
    color([0.84, 0.25, 0.31])
}
fn brass() -> [f64; 3] {
    color([0.78, 0.60, 0.22])
}
fn gauge() -> [f64; 3] {
    color([0.23, 0.41, 0.68])
}
fn tube_color() -> [f64; 3] {
    color([0.86, 0.88, 0.90])
}
fn tube(length: f64) -> Result<Solid> {
    Solid::cylinder(V3::ZERO, V3::Z, TUBE_OD / 2., length)?.cut(&Solid::cylinder(
        V3::ZERO,
        V3::Z,
        TUBE_ID / 2.,
        length,
    )?)
}
fn section(shape: &Solid) -> Result<Solid> {
    shape.cut(&jig::block(-50., 50., -100., 0., -10., 140.))
}
fn arrow(x: f64, y: f64, z: f64, length: f64) -> Result<Solid> {
    Solid::extrude(
        &Profile::polygon(&[
            v2(0., 0.),
            v2(8., 5.),
            v2(8., 2.),
            v2(length, 2.),
            v2(length, -2.),
            v2(8., -2.),
            v2(8., -5.),
        ])
        .place(&Plane::XY),
        V3::Z,
        v3(0., 0., 0.4),
    )
    .map(|s| s.translate(v3(x, y, z)))
}
fn move_named(parts: &mut [Component], name: &str, delta: V3) {
    if let Some(part) = parts.iter_mut().find(|p| p.name == name) {
        part.solid = part.solid.translate(delta);
    }
}
fn replace(parts: &mut [Component], name: &str, solid: Solid) {
    if let Some(part) = parts.iter_mut().find(|p| p.name == name) {
        part.solid = solid;
    }
}

struct Context<'a> {
    root: &'a Path,
    parts: BTreeMap<String, Solid>,
}
impl<'a> Context<'a> {
    fn part(&self, name: &str, print: bool) -> Result<Solid> {
        let solid = self
            .parts
            .get(name)
            .with_context(|| format!("tube fixture part {name}"))?;
        Ok(if print {
            jig::print_pose(name, solid)
        } else {
            solid.clone()
        })
    }
    fn thimble(&self) -> Result<Solid> {
        artwork::read(
            self.root,
            "hardware/printed-parts/faucet/tpu-o-ring/tpu-o-ring.step",
        )
    }
    fn assembly(&self, stroke: f64, workpiece: bool, hardware: bool) -> Result<Vec<Component>> {
        jig::assembly(
            self.root,
            &self.parts,
            stroke,
            workpiece,
            hardware,
            false,
            DONOR_PORT_DEPTH_MIN,
        )
    }
    fn detail(
        &self,
        names: &[&str],
        accents: &[&str],
        stroke: f64,
        workpiece: bool,
        hardware: bool,
        offsets: &[(&str, [f64; 3])],
    ) -> Result<Vec<Component>> {
        let mut parts = self.assembly(stroke, workpiece, hardware)?;
        parts.retain(|p| names.contains(&p.name.as_str()));
        for part in &mut parts {
            if let Some((_, offset)) = offsets.iter().find(|(name, _)| *name == part.name) {
                part.solid = part.solid.translate(V3::from(*offset));
            }
            if accents.contains(&part.name.as_str()) {
                part.color = accent();
            } else if part.name.contains("nut") {
                part.color = brass();
            } else if part.name == "lldpe-tube" {
                part.color = tube_color();
            }
        }
        Ok(parts)
    }
    fn clamps(
        &self,
        parts: &mut Vec<Component>,
        stroke: f64,
        accents: &[&str],
        backoff: f64,
        contacts: bool,
    ) -> Result<()> {
        for (side, label) in [(-1, "C1"), (1, "C2")] {
            for mut part in jig::build_clamp_reference(side, stroke)? {
                if backoff != 0.
                    && [
                        "moving-pad-envelope",
                        "spindle-schematic",
                        "wood-handle-envelope",
                    ]
                    .contains(&part.name.as_str())
                {
                    part.solid = part.solid.translate(v3(backoff, 0., 0.));
                }
                if accents.contains(&part.name.as_str()) {
                    part.color = accent();
                }
                if contacts
                    && ["fixed-pad-envelope", "moving-pad-envelope"].contains(&part.name.as_str())
                {
                    part.color = gauge();
                }
                part.name = format!("{label}-{}", part.name);
                parts.push(part);
            }
        }
        Ok(())
    }
    fn whole(
        &self,
        stroke: f64,
        accents: &[&str],
        workpiece: bool,
        clamps: bool,
        clamp_accents: &[&str],
        backoff: f64,
    ) -> Result<Vec<Component>> {
        let mut parts = self.assembly(stroke, workpiece, true)?;
        for part in &mut parts {
            if accents.contains(&part.name.as_str()) {
                part.color = accent();
            } else if part.name.contains("nut") {
                part.color = brass();
            } else if part.name == "lldpe-tube" {
                part.color = tube_color();
            }
        }
        if clamps {
            self.clamps(&mut parts, stroke, clamp_accents, backoff, false)?;
        }
        Ok(parts)
    }
    fn scene(&self, name: &str) -> Result<Scene> {
        let cam;
        let mut up = [0., 0., 1.];
        let mut size = "2200x1800";
        let (mut target, mut span) = (None, None);
        let bodies = match name {
            "hero" => {
                cam = [0.25, -0.85, 1.15];
                size = "2400x1700";
                self.whole(PRESS_TRAVEL, &[], true, true, &[], 0.)?
            }
            "load-path" => {
                cam = [0., 0., 1.];
                up = [0., 1., 0.];
                size = "2400x1650";
                let mut parts =
                    self.whole(10., &["lower-jaw", "upper-jaw"], true, false, &[], 0.)?;
                self.clamps(&mut parts, 10., &[], 0., true)?;
                let end = parts
                    .iter()
                    .find(|p| p.name == "lldpe-tube")
                    .unwrap()
                    .solid
                    .bounds()
                    .max
                    .x;
                parts.push(component(
                    "tube-axis-reference",
                    jig::block(DONOR_PORT_X, end, TUBE_Y - 0.22, TUBE_Y + 0.22, 59., 59.25),
                    gauge(),
                ));
                let font = hsm_kernel::text::Font::open(
                    self.root
                        .join("hardware/install-guide/fonts/Plex-Regular.ttf"),
                    0,
                )?;
                for station in jig::clamp_stations(10.) {
                    let [x, y, _] = station.moving_center_mm;
                    parts.push(component(
                        format!("{}-advance", station.name),
                        arrow(x + 15., y, 58., 24.)?,
                        gauge(),
                    ));
                    let letters = Plane::XY
                        .text(
                            &font,
                            station.name,
                            10.,
                            0.3,
                            hsm_kernel::text::HAlign::Center,
                            hsm_kernel::text::VAlign::Center,
                        )?
                        .translate(v3(
                            30.,
                            y + station.side as f64 * (FACTORY_CLAMP_THROAT + 12.),
                            42.,
                        ));
                    parts.push(component(
                        format!("label-{}", station.name),
                        letters,
                        gauge(),
                    ));
                }
                parts
            }
            "faucet-lever" => {
                cam = [0.65, -0.9, 0.7];
                size = "1900x1300";
                vec![component(
                    "accepted-faucet-lever",
                    artwork::read(
                        self.root,
                        "hardware/printed-parts/faucet/lever-replica/lever-replica.step",
                    )?,
                    accent(),
                )]
            }
            "plate-rigid" => {
                cam = [0.4, -0.75, 1.2];
                #[derive(Deserialize)]
                struct Entry {
                    source: String,
                    offset_mm: [f64; 2],
                }
                #[derive(Deserialize)]
                struct Plate {
                    id: String,
                    parts: Vec<Entry>,
                }
                #[derive(Deserialize)]
                struct Layout {
                    plates: Vec<Plate>,
                }
                let layout: Layout = serde_json::from_slice(&std::fs::read(
                    self.root.join(jig::DIRECTORY).join("print-layout.json"),
                )?)?;
                let plate = layout
                    .plates
                    .into_iter()
                    .find(|p| p.id == "centered-grip-mark2")
                    .context("current grip print plate")?;
                let mut parts = Vec::new();
                for entry in plate.parts {
                    let name = entry
                        .source
                        .trim_start_matches("tube-insertion-")
                        .trim_end_matches("-print.stl");
                    let shape = self.part(name, true)?;
                    let bounds = shape.bounds();
                    let [x, y] = entry.offset_mm;
                    parts.push(component(
                        name,
                        shape.translate(v3(
                            x - bounds.center().x,
                            y - bounds.center().y,
                            -bounds.min.z,
                        )),
                        jig::rigid_color(),
                    ));
                }
                parts
            }
            "plate-liners" => {
                cam = [-0.9, -1., 0.6];
                size = "1900x1500";
                let shape = self.part("liner", true)?;
                let b = shape.bounds();
                [-5.5, 5.5]
                    .into_iter()
                    .enumerate()
                    .map(|(i, x)| {
                        component(
                            format!("F-liner-{}", i + 1),
                            shape.translate(v3(x - b.center().x, -b.center().y, -b.min.z)),
                            accent(),
                        )
                    })
                    .collect()
            }
            "hardware" => {
                cam = [0.3, -0.8, 1.2];
                size = "2200x1700";
                let mut parts = Vec::new();
                self.clamps(&mut parts, 0., &[], 0., false)?;
                for i in 0..2 {
                    let i = i as f64;
                    parts.push(component(
                        format!("M5x50-{i}"),
                        jig::bolt_shape(-3. + i * 23., -4., 5., 50.)?,
                        jig::steel_color(),
                    ));
                    parts.push(component(
                        format!("M5x20-countersunk-{i}"),
                        jig::countersunk_bolt_shape(48. + i * 20., -4., 0., 20.)?,
                        jig::steel_color(),
                    ));
                    parts.push(component(
                        format!("washer-{i}"),
                        jig::washer_shape(12. + i * 33., 28., 0.)?,
                        jig::steel_color(),
                    ));
                }
                for i in 0..4 {
                    parts.push(component(
                        format!("square-nut-{i}"),
                        jig::square_nut_shape(-4. + i as f64 * 18., 52., 0.)?,
                        brass(),
                    ));
                }
                parts
            }
            "clean-base" => {
                cam = [-0.7, -0.85, 0.9];
                size = "2200x1700";
                let mut parts = vec![component(
                    "A-base",
                    self.part("base", true)?,
                    jig::rigid_color(),
                )];
                for station in jig::clamp_stations(0.) {
                    let [x, y, z] = station.fixed_center_mm;
                    parts.push(component(
                        format!("{}-fixed-centre-ink", station.name),
                        jig::cylinder_x(x - 0.25, x - 0.02, y, z, 1.8)?,
                        gauge(),
                    ));
                }
                parts
            }
            "carrier-joint" => {
                cam = [0.6, -0.9, 0.7];
                self.detail(
                    &[
                        "carrier",
                        "lower-jaw",
                        "lower-liner",
                        "carrier-front-m5x20",
                        "carrier-rear-m5x20",
                        "carrier-front-nut",
                        "carrier-rear-nut",
                    ],
                    &["carrier-front-m5x20", "carrier-rear-m5x20"],
                    0.,
                    false,
                    true,
                    &[
                        ("lower-jaw", [0., 0., 28.]),
                        ("lower-liner", [0., 0., 28.]),
                        ("carrier-front-m5x20", [0., 0., -16.]),
                        ("carrier-rear-m5x20", [0., 0., -16.]),
                        ("carrier-front-nut", [0., -16., 28.]),
                        ("carrier-rear-nut", [0., 16., 28.]),
                    ],
                )?
            }
            "carrier" => {
                cam = [0.45, -0.85, 0.9];
                size = "2200x1700";
                let mut names = vec!["base"];
                names.extend(GRIP);
                let offsets: Vec<_> = GRIP.iter().map(|&name| (name, [0., 0., 34.])).collect();
                self.detail(&names, &["carrier"], 0., false, true, &offsets)?
            }
            "liners" => {
                cam = [0.55, -0.8, 0.8];
                size = "1900x1600";
                let mut parts = vec![
                    component(
                        "D-lower-jaw",
                        self.part("lower-jaw", true)?.translate(v3(0., -62., 0.)),
                        jig::rigid_color(),
                    ),
                    component(
                        "E-upper-jaw",
                        self.part("upper-jaw", true)?.translate(v3(0., 62., 0.)),
                        jig::rigid_color(),
                    ),
                ];
                for (i, y) in [-62., 62.].into_iter().enumerate() {
                    parts.push(component(
                        format!("F-liner-{}", i + 1),
                        self.part("liner", false)?.translate(v3(
                            LINER_START_X,
                            y,
                            JAW_HALF_H - LINER_POCKET_H + 18.,
                        )),
                        accent(),
                    ));
                }
                parts
            }
            "jaws" => {
                cam = [0.65, -0.9, 0.7];
                self.detail(
                    GRIP,
                    &["upper-jaw", "clamp-front-m5x50", "clamp-rear-m5x50"],
                    0.,
                    false,
                    true,
                    &[
                        ("upper-jaw", [0., 0., 28.]),
                        ("upper-liner", [0., 0., 28.]),
                        ("clamp-front-m5x50", [0., 0., -18.]),
                        ("clamp-rear-m5x50", [0., 0., -18.]),
                        ("clamp-front-washer", [0., 0., 40.]),
                        ("clamp-rear-washer", [0., 0., 40.]),
                        ("clamp-front-nut", [0., 0., 49.]),
                        ("clamp-rear-nut", [0., 0., 49.]),
                    ],
                )?
            }
            "puck" => {
                cam = [0.6, -0.8, 0.9];
                size = "1800x1600";
                span = Some(42.);
                vec![
                    component(
                        "G-cap-support-puck",
                        self.part("cap-support-puck", false)?,
                        accent(),
                    ),
                    component(
                        "thimble",
                        self.thimble()?.translate(v3(0., 0., PUCK_H + 12.)),
                        jig::tpu_color(),
                    ),
                ]
            }
            "preset-travel" => {
                cam = [0.25, -0.85, 1.2];
                size = "2200x1700";
                let mut parts = self.whole(
                    PRESS_TRAVEL,
                    &[],
                    false,
                    true,
                    &["spindle-schematic", "wood-handle-envelope"],
                    0.,
                )?;
                for station in jig::clamp_stations(PRESS_TRAVEL) {
                    let [x, y, _] = station.moving_center_mm;
                    parts.push(component(
                        format!("{}-travel-direction", station.name),
                        arrow(x - PRESS_TRAVEL, y, 57., PRESS_TRAVEL)?,
                        gauge(),
                    ));
                }
                parts
            }
            "handles-clear" => {
                cam = [0.15, -0.8, 1.35];
                size = "2200x1700";
                let mut parts =
                    self.whole(PRESS_TRAVEL, &[], true, true, &["wood-handle-envelope"], 0.)?;
                for (i, (x, y)) in [(12., 112.), (170., 112.)].into_iter().enumerate() {
                    let ring = jig::vertical_hole(x, y, BASE_H + 0.05, BASE_H + 0.35, 14.)?
                        .cut(&jig::vertical_hole(x, y, BASE_H, BASE_H + 1., 6.)?)?;
                    parts.push(component(
                        format!("mounting-location-{}", i + 1),
                        ring,
                        gauge(),
                    ));
                }
                parts
            }
            "depth" => {
                cam = [-1., 0.2, 0.35];
                target = Some([0., TUBE_Y, 32.]);
                span = Some(24.);
                size = "1800x1400";
                let donor=artwork::read(self.root,"hardware/reference/touch-flo-faucet/westbrass-reference/westbrass-reference.step")?.cut(&jig::block(-100.,0.,-50.,50.,-55.,95.))?;
                let beam = jig::block(
                    3.,
                    6.,
                    TUBE_Y - 15.,
                    TUBE_Y + 15.,
                    DONOR_PORT_X,
                    DONOR_PORT_X + 3.,
                )
                .union(&jig::block(
                    3.7,
                    4.4,
                    TUBE_Y - 1.2,
                    TUBE_Y + 1.2,
                    DONOR_PORT_X - DONOR_PORT_DEPTH_MIN,
                    DONOR_PORT_X,
                ))?;
                vec![
                    component("donor-section", donor, jig::steel_color()),
                    component("depth-blade-reference", beam, gauge()),
                ]
            }
            "marks" => {
                cam = [0.5, -0.9, 0.3];
                size = "1600x1900";
                let mut parts = vec![component("tube", tube(58.)?, tube_color())];
                let witness = DONOR_PORT_DEPTH_MIN - SLEEVE_CAP_H;
                for (i, z) in [witness, witness + CLAMP_FINAL_X - DONOR_PORT_X]
                    .into_iter()
                    .enumerate()
                {
                    let mark = Solid::cylinder(v3(0., 0., z), V3::Z, TUBE_OD / 2. + 0.15, 0.6)?
                        .cut(&Solid::cylinder(v3(0., 0., z), V3::Z, TUBE_OD / 2., 0.6)?)?;
                    parts.push(component(format!("witness-{}", i + 1), mark, gauge()));
                }
                parts
            }
            "sleeve-fit" => {
                cam = [-0.65, -0.85, 0.45];
                size = "1900x1900";
                let cap = PUCK_H - PUCK_CAP_RECESS_H;
                let mut parts = vec![
                    component(
                        "puck",
                        self.part("cap-support-puck", false)?,
                        jig::rigid_color(),
                    ),
                    component(
                        "thimble",
                        self.thimble()?.translate(v3(0., 0., cap)),
                        accent(),
                    ),
                    component(
                        "tube",
                        tube(130.)?.translate(v3(0., 0., cap + SLEEVE_CAP_H + 5.)),
                        tube_color(),
                    ),
                ];
                for mut part in self
                    .assembly(0., false, true)?
                    .into_iter()
                    .filter(|p| GRIP.contains(&p.name.as_str()))
                {
                    part.solid = part
                        .solid
                        .translate(v3(-CLAMP_FINAL_X, -TUBE_Y, -TUBE_Z))
                        .rotate(V3::ZERO, V3::Y, -90.)
                        .translate(v3(0., 0., 65.));
                    if part.name.contains("nut") {
                        part.color = brass();
                    }
                    parts.push(part);
                }
                parts
            }
            "grip-mark" => {
                cam = [0.55, -0.9, 0.55];
                size = "2200x1500";
                let mut names = GRIP.to_vec();
                names.extend(["lldpe-tube", "tpu-sealing-thimble"]);
                let mut parts = self.detail(&names, &[], 0., true, true, &[])?;
                replace(
                    &mut parts,
                    "lldpe-tube",
                    jig::tube_shape(DONOR_PORT_DEPTH_MIN, 0., 220.)?,
                );
                for (i, x) in [DONOR_PORT_X, CLAMP_FINAL_X].into_iter().enumerate() {
                    let mark =
                        jig::cylinder_x(x, x + 0.7, TUBE_Y, TUBE_Z, TUBE_OD / 2. + 0.15)?.cut(
                            &jig::cylinder_x(x - 1., x + 2., TUBE_Y, TUBE_Z, TUBE_OD / 2.)?,
                        )?;
                    parts.push(component(format!("tube-mark-{}", i + 1), mark, gauge()));
                }
                for station in jig::clamp_stations(0.) {
                    let [x, y, z] = station.moving_center_mm;
                    parts.push(component(
                        format!("{}-moving-centre-ink", station.name),
                        jig::cylinder_x(x + 0.02, x + 0.25, y, z, 1.8)?,
                        gauge(),
                    ));
                }
                parts
            }
            "donor-in" => {
                cam = [0.4, -0.95, 0.85];
                size = "2200x1700";
                let mut parts = self.detail(&["base"], &[], 0., false, false, &[])?;
                parts.push(component(
                    "donor",
                    jig::donor_shape(self.root)?.translate(v3(0., 0., 24.)),
                    accent(),
                ));
                parts
            }
            "engage" => {
                cam = [0.3, -0.9, 1.];
                size = "2200x1600";
                self.whole(
                    PRESS_TRAVEL,
                    &["lower-jaw", "upper-jaw"],
                    true,
                    true,
                    &[],
                    0.,
                )?
            }
            "press" => {
                cam = [0.2, -0.8, 1.15];
                size = "2200x1700";
                self.whole(
                    8.,
                    &[],
                    true,
                    true,
                    &[
                        "spindle-schematic",
                        "wood-handle-envelope",
                        "moving-pad-envelope",
                    ],
                    0.,
                )?
            }
            "release" => {
                cam = [0.35, -0.9, 1.];
                size = "2200x1600";
                let mut parts = self.whole(0., &["upper-jaw"], true, true, &[], 6.)?;
                for name in ["upper-jaw", "upper-liner"] {
                    move_named(&mut parts, name, v3(0., 0., 28.));
                }
                for name in [
                    "clamp-front-nut",
                    "clamp-rear-nut",
                    "clamp-front-washer",
                    "clamp-rear-washer",
                ] {
                    move_named(&mut parts, name, v3(0., 0., 49.));
                }
                for part in &mut parts {
                    if part.name.starts_with("C1-") || part.name.starts_with("C2-") {
                        let side = if part.name.starts_with("C1-") {
                            -1.
                        } else {
                            1.
                        };
                        part.solid = part.solid.translate(v3(0., side * 12., 40.));
                    }
                }
                parts
            }
            "workpiece" => {
                cam = [0.4, -1., 0.65];
                size = "2100x1300";
                let mut parts = self.detail(
                    &["touch-flo-donor", "lldpe-tube", "tpu-sealing-thimble"],
                    &[],
                    0.,
                    true,
                    false,
                    &[],
                )?;
                replace(
                    &mut parts,
                    "lldpe-tube",
                    jig::tube_shape(DONOR_PORT_DEPTH_MIN, 0., 100.)?,
                );
                parts
            }
            "sleeved-tube" => {
                cam = [0.35, -1., 0.28];
                size = "1500x1800";
                vec![
                    component("thimble-section", section(&self.thimble()?)?, accent()),
                    component(
                        "tube-section",
                        section(&tube(35.)?.translate(v3(0., 0., SLEEVE_CAP_H)))?,
                        tube_color(),
                    ),
                ]
            }
            _ => bail!("unknown tube insertion illustration {name}"),
        };
        Ok(Scene {
            name: name.into(),
            bodies,
            camera: cam,
            up,
            size: size.into(),
            target,
            span,
        })
    }
}

pub fn render(root: &Path, output: &Path, names: &[String]) -> Result<()> {
    let context = Context {
        root,
        parts: jig::retained_parts(root, false)?,
    };
    let chosen: Vec<_> = if names.is_empty() {
        NAMES.iter().map(|s| s.to_string()).collect()
    } else {
        names.to_vec()
    };
    let scenes = chosen
        .iter()
        .map(|name| context.scene(name))
        .collect::<Result<Vec<_>>>()?;
    artwork::render(root, output, scenes)
}
