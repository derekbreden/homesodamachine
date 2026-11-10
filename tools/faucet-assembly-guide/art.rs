//! Faucet guide pictures section the current component outputs and preserve the observed assembly frame.
use crate::artwork::{self, Scene, color, component};
use crate::tube_fixture as jig;
use anyhow::{Result, bail};
use hsm_kernel::{Solid, V3, v3};
use std::path::Path;

pub const NAMES: &[&str] = &[
    "accepted-lever",
    "sleeve-on-tube",
    "sleeved-tube-to-donor",
    "shell-base-section",
    "shared-tip-section",
];
fn accent() -> [f64; 3] {
    color([0.91, 0.34, 0.18])
}
fn stock() -> [f64; 3] {
    color([0.17, 0.18, 0.20])
}
fn steel() -> [f64; 3] {
    color([0.56, 0.59, 0.63])
}
fn section(shape: &Solid) -> Result<Solid> {
    shape.cut(&jig::block(0., 500., -500., 500., -500., 500.))
}
fn tube(z: f64, length: f64, y: f64) -> Result<Solid> {
    Solid::cylinder(v3(0., y, z), V3::Z, jig::numbers::TUBE_OD / 2., length)?.cut(&Solid::cylinder(
        v3(0., y, z),
        V3::Z,
        jig::numbers::TUBE_ID / 2.,
        length,
    )?)
}

pub fn render(root: &Path, output: &Path, names: &[String]) -> Result<()> {
    let chosen: Vec<_> = if names.is_empty() {
        NAMES.iter().map(|v| v.to_string()).collect()
    } else {
        names.to_vec()
    };
    let mut scenes = Vec::new();
    for name in chosen {
        let (mut up, mut camera) = ([0., 0., 1.], [1., -0.8, 0.3]);
        let bodies = match name.as_str() {
            "accepted-lever" => {
                camera = [0.8, -1., -0.8];
                up = [0., 1., 0.];
                vec![component(
                    "accepted-lever",
                    artwork::read(
                        root,
                        "hardware/printed-parts/faucet/lever-replica/lever-replica.step",
                    )?,
                    accent(),
                )]
            }
            "sleeve-on-tube" => {
                camera = [1., -0.75, 0.25];
                let sleeve = artwork::read(
                    root,
                    "hardware/printed-parts/faucet/tpu-o-ring/tpu-o-ring.step",
                )?;
                vec![
                    component("thimble", section(&sleeve)?, accent()),
                    component("tube", section(&tube(23.6, 25., 0.)?)?, stock()),
                ]
            }
            "sleeved-tube-to-donor" => {
                let sleeve = artwork::read(
                    root,
                    "hardware/printed-parts/faucet/tpu-o-ring/tpu-o-ring.step",
                )?
                .translate(v3(0., 8.75, 51.));
                let donor = artwork::read(
                    root,
                    "hardware/reference/touch-flo-faucet/westbrass-reference/westbrass-reference.step",
                )?;
                vec![
                    component("donor", section(&donor)?, steel()),
                    component("thimble", section(&sleeve)?, accent()),
                    component(
                        "tube",
                        section(&tube(53.1, 38., 8.75)?.cut(&sleeve)?)?,
                        stock(),
                    ),
                ]
            }
            "shell-base-section" => {
                camera = [1., -0.3, 0.18];
                vec![component(
                    "shell-base",
                    section(&artwork::read(
                        root,
                        "hardware/printed-parts/faucet/faucet-shell/faucet-shell-base.step",
                    )?)?,
                    stock(),
                )]
            }
            "shared-tip-section" => {
                camera = [1., -0.5, 0.45];
                vec![component(
                    "shell-tip",
                    section(&artwork::read(
                        root,
                        "hardware/printed-parts/faucet/faucet-shell/faucet-shell-tip.step",
                    )?)?,
                    stock(),
                )]
            }
            _ => bail!("unknown faucet guide illustration {name}"),
        };
        scenes.push(Scene {
            name,
            bodies,
            camera,
            up,
            size: "1500x1500".into(),
            target: None,
            span: None,
        });
    }
    artwork::render(root, output, scenes)
}
