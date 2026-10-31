//! What each body becomes in a picture, and the draws that make it: the role a job gives a body,
//! the viewer's material for that role, and the order three.js draws its lists in.

use crate::camera::Camera;
use crate::gpu::{Draw, Layer, MAX_CLIPS, Material, ViewUniform, flag};
use crate::job::{Framing, Job, any_glob};
use crate::scene::{Aabb, Scene};
use crate::shadow::{self, ShadowMap};
use anyhow::{Result, ensure};
use glam::DVec3;
use serde::Deserialize;
use std::collections::HashMap;
use std::sync::Arc;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Role {
    /// Opaque faces in the body's own finish, or its tint.
    Solid,
    /// The viewer's x-ray: faint faces and feature edges.
    Xray,
    /// Feature edges alone, faint.
    Ghost,
    /// A faint shell, no edges.
    Shell,
    /// Opaque, in the selection amber.
    Highlight,
    /// Not drawn, but still part of the model the frame and the shadow are fitted to.
    Hidden,
    /// Out of the picture altogether.
    Dropped,
}

/// One row of web/public/finishes.json: a colour the tree draws and how that stock takes light.
#[derive(Clone, Debug, Deserialize)]
pub struct Finish {
    pub rgb: [f64; 3],
    pub roughness: f64,
    pub metalness: f64,
}

/// step.js DEFAULT_FINISH and DEFAULT_FRONT.
const DEFAULT_FINISH: (f64, f64) = (0.6, 0.1);
const DEFAULT_COLOR: u32 = 0x8899aa;
/// step.js FINISH_TOL2: a body this close to a row is that row.
const FINISH_TOL2: f64 = 4e-4 * 4e-4;
/// A look's tints, a hue per solid body, handed out in name order.
pub const TINTS: [u32; 12] = [
    0x7fb3ff, 0xffb454, 0x6fd6a6, 0xff8fa3, 0xc79bff, 0xffe066, 0x5fd4d6, 0xff9d6f, 0x9fd356, 0xf58fd8, 0x8fa8ff,
    0xd6c48f,
];
/// component-picker.js SEL.
pub const AMBER: u32 = 0xffa733;
const GHOST_EDGE: u32 = 0x8fa3bd;
/// change.mjs: a cut face is the solid's colour most of the way to a steel blue-grey, and a
/// highlighted solid cuts a darker amber.
const SECTION_TINT: u32 = 0x8fa6bd;
const SECTION_MIX: f64 = 0.7;
const SECTION_AMBER: u32 = 0xb8700f;
/// scene.js BG_COLOR: what distance fades toward.
const FOG_COLOR: u32 = 0x10319c;
const BACK_DARKEN: f32 = 0.75;
const EDGE_WIDTH: f32 = 1.4;
const SELECT_EDGE_WIDTH: f32 = 1.0;
const XRAY_OPACITY: f32 = 0.14;
const SHELL_OPACITY: f32 = 0.16;
const GHOST_OPACITY: f32 = 0.34;
const SELECT_EDGE_OPACITY: f32 = 0.95;
const SELECT_SHELL_OPACITY: f32 = 0.18;
/// A tinted body's edges are its tint at this fraction, in linear light.
const TINT_EDGE: f64 = 0.42;

/// web/contracts/faucet-options.js: a faucet style's finish bodies are drawn in the faucet finish
/// whatever colour the payload gives them, in its assembly the bodies named here and in one of its
/// parts drawn alone the whole part. The finish is PETGF_BLACK (web/contracts/material-finishes.js),
/// the one a page nobody has switched to white shows.
const FAUCET_ASSEMBLIES: [&str; 2] = ["faucet-layout/faucet-assembly.step", "faucet-layout/faucet-industrial-assembly.step"];
const FAUCET_FINISH_BODIES: [&str; 7] = [
    "shell_base",
    "shell_tip",
    "faucet-display-cover-seated",
    "above_counter_plate",
    "above_counter_gasket",
    "lever",
    "soda_faucet_tube",
];
const FAUCET_PARTS: [&str; 10] = [
    "printed-parts/faucet/lever-replica/lever-replica.step",
    "printed-parts/faucet/faucet-shell/faucet-shell-base.step",
    "printed-parts/faucet/faucet-shell/faucet-shell-tip.step",
    "printed-parts/faucet/faucet-display-cover/faucet-display-cover.step",
    "printed-parts/faucet/above-counter-plate/above-counter-plate.step",
    "printed-parts/faucet/above-counter-gasket/above-counter-gasket.step",
    "printed-parts/faucet/industrial/industrial-shell-base.step",
    "printed-parts/faucet/industrial/industrial-display-cover.step",
    "printed-parts/faucet/industrial/industrial-above-counter-plate.step",
    "printed-parts/faucet/industrial/industrial-above-counter-gasket.step",
];
const FAUCET_BLACK: [f64; 3] = [0.03310476616024971, 0.03310476616024971, 0.036306485533714294];
const FAUCET_FINISH: (f64, f64) = (0.85, 0.0);

/// Whether the viewer draws `body` of the model at `step` in the faucet finish.
pub fn faucet_finish(step: Option<&str>, body: &str) -> bool {
    let Some(step) = step.map(|s| s.strip_prefix("hardware/").unwrap_or(s)) else {
        return false;
    };
    if FAUCET_ASSEMBLIES.contains(&step) {
        return FAUCET_FINISH_BODIES.contains(&body);
    }
    FAUCET_PARTS.contains(&step)
}

pub fn srgb_to_linear(c: f64) -> f64 {
    if c <= 0.04045 { c / 12.92 } else { ((c + 0.055) / 1.055).powf(2.4) }
}

pub fn hex_srgb(hex: u32) -> [f64; 3] {
    [(hex >> 16) & 255, (hex >> 8) & 255, hex & 255].map(|c| c as f64 / 255.0)
}

pub fn hex_linear(hex: u32) -> [f64; 3] {
    hex_srgb(hex).map(srgb_to_linear)
}

pub fn hex_css(hex: u32) -> String {
    format!("#{hex:06x}")
}

pub struct Plan {
    /// One per body.
    pub roles: Vec<Role>,
    /// The TINTS entry a solid body is drawn in.
    pub tints: Vec<Option<u32>>,
    /// Patterns that named no body, as `--flag pattern`.
    pub unmatched: Vec<String>,
    /// Every body still in the model: what fog, shadow and depth are fitted to.
    pub whole: Aabb,
    /// What the frame is fitted to.
    pub subject: Aabb,
}

impl Plan {
    pub fn new(scene: &Scene, job: &Job) -> Plan {
        let context = match job.context.as_deref().unwrap_or("ghost") {
            "hide" => Role::Hidden,
            "solid" => Role::Solid,
            "xray" => Role::Xray,
            "shell" => Role::Shell,
            "drop" => Role::Dropped,
            _ => Role::Ghost,
        };
        let roles: Vec<Role> = scene
            .bodies
            .iter()
            .map(|b| {
                let n = b.name.as_str();
                if any_glob(&job.hide, n) {
                    Role::Hidden
                } else if any_glob(&job.highlight, n) {
                    Role::Highlight
                } else if any_glob(&job.ghost, n) {
                    Role::Ghost
                } else if any_glob(&job.shell, n) {
                    Role::Shell
                } else if any_glob(&job.xray, n) {
                    Role::Xray
                } else if job.only.is_empty() || any_glob(&job.only, n) {
                    Role::Solid
                } else {
                    context
                }
            })
            .collect();

        let mut tints = vec![None; scene.bodies.len()];
        if job.tint {
            let mut solid: Vec<usize> = (0..scene.bodies.len()).filter(|&b| roles[b] == Role::Solid).collect();
            // Name order as JavaScript's default sort has it, so a body keeps its hue.
            solid.sort_by(|&a, &b| scene.bodies[a].name.cmp(&scene.bodies[b].name));
            for (i, b) in solid.into_iter().enumerate() {
                tints[b] = Some(TINTS[i % TINTS.len()]);
            }
        }

        let mut unmatched = Vec::new();
        for (flag, patterns) in [
            ("only", &job.only),
            ("xray", &job.xray),
            ("ghost", &job.ghost),
            ("shell", &job.shell),
            ("hide", &job.hide),
            ("highlight", &job.highlight),
            ("select", &job.select),
        ] {
            for p in patterns {
                if !scene.bodies.iter().any(|b| crate::job::glob(p, &b.name)) {
                    unmatched.push(format!("--{flag} {p}"));
                }
            }
        }

        let mut whole = Aabb::EMPTY;
        let mut solid = Aabb::EMPTY;
        for (b, body) in scene.bodies.iter().enumerate() {
            if roles[b] != Role::Dropped {
                whole.union(&body.bbox);
            }
            if matches!(roles[b], Role::Solid | Role::Highlight) {
                solid.union(&body.bbox);
            }
        }
        let subject = match job.frame {
            crate::job::Framing::Look if !solid.is_empty() => solid,
            _ => whole,
        };
        Plan {
            roles,
            tints,
            unmatched,
            whole,
            subject,
        }
    }

    pub fn count(&self, role: Role) -> usize {
        self.roles.iter().filter(|&&r| r == role).count()
    }
}

/// Names in the order JavaScript's `localeCompare` puts them (ICU's root collation): spaces and
/// punctuation in ICU's own order, then digits, then letters without regard to case, and case
/// only to break a tie, lower first.
pub fn collate(a: &str, b: &str) -> std::cmp::Ordering {
    const PUNCTUATION: &str = " _-,;:!?.'\"()[]{}@*/\\&#%`^+<=>|~$";
    let key = |s: &str| -> Vec<(u8, u32)> {
        s.chars()
            .map(|c| {
                if let Some(i) = PUNCTUATION.find(c) {
                    (0, i as u32)
                } else if c.is_ascii_digit() {
                    (1, c as u32)
                } else if c.is_alphabetic() {
                    (2, c.to_lowercase().next().unwrap_or(c) as u32)
                } else {
                    (0, 0x100 + c as u32)
                }
            })
            .collect()
    };
    key(a).cmp(&key(b)).then_with(|| {
        let flip = |s: &str| {
            s.chars()
                .map(|c| if c.is_ascii_uppercase() { c.to_ascii_lowercase() } else { c.to_ascii_uppercase() })
                .collect::<String>()
        };
        flip(a).cmp(&flip(b))
    })
}

pub fn finish_for(finishes: &[Finish], color: Option<[f64; 3]>) -> (f64, f64) {
    let Some(c) = color else { return DEFAULT_FINISH };
    let mut best = DEFAULT_FINISH;
    let mut best_d = FINISH_TOL2;
    for f in finishes {
        let d: f64 = (0..3).map(|i| (f.rgb[i] - c[i]).powi(2)).sum();
        if d <= best_d {
            best_d = d;
            best = (f.roughness, f.metalness);
        }
    }
    best
}

/// One frame's materials, each distinct one once, in the order they were first asked for: the
/// order three.js would have created them in, which is the first key of its opaque sort.
#[derive(Default)]
struct Materials {
    list: Vec<Material>,
    index: HashMap<[u32; 12], u32>,
}

impl Materials {
    fn slot(&mut self, m: Material) -> u32 {
        let key: [u32; 12] = bytemuck::cast(m);
        *self.index.entry(key).or_insert_with(|| {
            self.list.push(m);
            self.list.len() as u32 - 1
        })
    }
}

fn surface(color: [f64; 3], opacity: f32, (roughness, metalness): (f64, f64), darken: f32, flags: u32) -> Material {
    Material {
        color: [color[0] as f32, color[1] as f32, color[2] as f32, opacity],
        params: [roughness as f32, metalness as f32, 0.0, darken],
        flags: [flags, 0, 0, 0],
    }
}

fn line(color: [f64; 3], opacity: f32, width: f32, flags: u32) -> Material {
    Material {
        color: [color[0] as f32, color[1] as f32, color[2] as f32, opacity],
        params: [0.0, 0.0, width, 1.0],
        flags: [flags, 0, 0, 0],
    }
}

pub struct Built {
    pub materials: Vec<Material>,
    pub edge_slot: Vec<u32>,
    pub draws: Vec<(Layer, Draw)>,
    pub view: ViewUniform,
    pub shadow: Option<Arc<ShadowMap>>,
    /// Keep where dot(xyz, p) + w >= 0.
    pub clips: Vec<[f64; 4]>,
}

/// The planes a job cuts by: each clip band's two faces, and the section's.
pub fn clip_planes(job: &Job) -> Result<Vec<[f64; 4]>> {
    let mut planes = Vec::new();
    for c in &job.clip {
        let a = match c.axis.as_str() {
            "x" => 0,
            "y" => 1,
            _ => 2,
        };
        let mut n = [0.0; 3];
        n[a] = 1.0;
        planes.push([n[0], n[1], n[2], -c.lo]);
        planes.push([-n[0], -n[1], -n[2], c.hi]);
    }
    if let Some(s) = &job.section {
        // change.mjs: Plane(-n, n·at), which keeps the side the normal points away from.
        let n = s.normal;
        let d = n[0] * s.at[0] + n[1] * s.at[1] + n[2] * s.at[2];
        planes.push([-n[0], -n[1], -n[2], d]);
    }
    ensure!(planes.len() <= MAX_CLIPS, "at most {} cutting planes", MAX_CLIPS);
    Ok(planes)
}

pub fn kept(planes: &[[f64; 4]], p: DVec3) -> bool {
    planes.iter().all(|c| c[0] * p.x + c[1] * p.y + c[2] * p.z + c[3] >= 0.0)
}

/// Every draw of the frame, in three.js's order: the opaque list by material and then front to
/// back, then the transparent list back to front with the contact shadow first, then the
/// selection overlay, its edges before its shells.
pub fn build(
    scene: &Scene,
    job: &Job,
    plan: &Plan,
    camera: &Camera,
    finishes: &[Finish],
    lit: &[bool],
) -> Result<Built> {
    let clips = clip_planes(job)?;
    let section = job.section.is_some();
    let n = scene.meshes.len();
    let total = scene.segment_count();
    let mut materials = Materials::default();
    let mut edge_slot = vec![0u32; 2 * n];
    let mut opaque: Vec<(u8, u32, f64, usize, Draw)> = Vec::new();
    let mut blend: Vec<(f64, u8, usize, Draw)> = Vec::new();
    let mut overlay: Vec<(u8, f64, usize, Draw)> = Vec::new();
    let default_color = hex_linear(DEFAULT_COLOR);
    let amber = hex_linear(AMBER);

    for (mi, mesh) in scene.meshes.iter().enumerate() {
        let body = mesh.body;
        let role = plan.roles[body];
        if matches!(role, Role::Hidden | Role::Dropped) {
            continue;
        }
        let z = camera.to_screen(DVec3::from(mesh.bbox.center())).2;
        let (base, finish) = if faucet_finish(job.step.as_deref(), &scene.bodies[body].name) {
            (FAUCET_BLACK, FAUCET_FINISH)
        } else {
            (mesh.color.unwrap_or(default_color), finish_for(finishes, mesh.color))
        };
        let edges = |materials: &mut Materials, edge_slot: &mut [u32], color: [f64; 3]| {
            edge_slot[mi] = materials.slot(line(color, 1.0, EDGE_WIDTH, flag::NO_FOG));
            Draw::Lines {
                instances: mesh.segments.clone(),
            }
        };
        let cut = if section { flag::FRONT_ONLY } else { 0 };
        match role {
            Role::Solid | Role::Highlight => {
                let (material, cap) = if role == Role::Highlight {
                    (surface(amber, 1.0, (0.5, 0.05), 1.0, cut), hex_linear(SECTION_AMBER))
                } else if let Some(t) = plan.tints[body] {
                    (surface(hex_linear(t), 1.0, DEFAULT_FINISH, BACK_DARKEN, cut), lerp(hex_linear(t), hex_linear(SECTION_TINT), SECTION_MIX))
                } else {
                    (surface(base, 1.0, finish, BACK_DARKEN, cut), lerp(base, hex_linear(SECTION_TINT), SECTION_MIX))
                };
                let slot = materials.slot(material);
                opaque.push((0, slot, z, mi, Draw::Surface { mesh: mi, slot }));
                if section {
                    let slot = materials.slot(surface(cap, 1.0, DEFAULT_FINISH, 1.0, flag::UNLIT | flag::BACK_ONLY));
                    opaque.push((1, slot, z, mi, Draw::Cap { mesh: mi, slot }));
                }
                // A look draws its solid set with the feature edges the viewer's x-ray gives it.
                let edged = job.edges
                    || (role == Role::Solid && job.frame == Framing::Look)
                    || (role == Role::Highlight && any_glob(&job.xray, &scene.bodies[body].name));
                if edged {
                    let color = match plan.tints[body] {
                        Some(t) if role == Role::Solid => hex_linear(t).map(|c| c * TINT_EDGE),
                        _ => base,
                    };
                    let draw = edges(&mut materials, &mut edge_slot, color);
                    opaque.push((2, edge_slot[mi], z, mi, draw));
                }
            }
            Role::Xray => {
                let slot = materials.slot(surface(base, XRAY_OPACITY, finish, BACK_DARKEN, 0));
                blend.push((z, 0, mi, Draw::Surface { mesh: mi, slot }));
                let draw = edges(&mut materials, &mut edge_slot, base);
                opaque.push((2, edge_slot[mi], z, mi, draw));
            }
            Role::Shell => {
                let slot = materials.slot(surface(base, SHELL_OPACITY, finish, BACK_DARKEN, 0));
                blend.push((z, 0, mi, Draw::Surface { mesh: mi, slot }));
            }
            Role::Ghost => {
                edge_slot[mi] = materials.slot(line(hex_linear(GHOST_EDGE), GHOST_OPACITY, EDGE_WIDTH, flag::NO_FOG));
                blend.push((z, 1, mi, Draw::Lines { instances: mesh.segments.clone() }));
            }
            Role::Hidden | Role::Dropped => unreachable!(),
        }
        if lit[body] {
            edge_slot[n + mi] = materials.slot(line(amber, SELECT_EDGE_OPACITY, SELECT_EDGE_WIDTH, 0));
            let s = mesh.segments.clone();
            overlay.push((0, z, mi, Draw::Lines { instances: total + s.start..total + s.end }));
            let slot = materials.slot(surface(amber, SELECT_SHELL_OPACITY, DEFAULT_FINISH, 1.0, flag::UNLIT));
            overlay.push((1, z, mi, Draw::Surface { mesh: mi, slot }));
        }
    }

    opaque.sort_by(|a, b| (a.0, a.1).cmp(&(b.0, b.1)).then(a.2.total_cmp(&b.2)).then(a.3.cmp(&b.3)));
    blend.sort_by(|a, b| b.0.total_cmp(&a.0).then(a.1.cmp(&b.1)).then(a.2.cmp(&b.2)));
    overlay.sort_by(|a, b| a.0.cmp(&b.0).then(b.1.total_cmp(&a.1)).then(a.2.cmp(&b.2)));

    let size = plan.whole.size();
    let shadow = (job.ground && !plan.whole.is_empty() && size[0] > 0.0 && size[1] > 0.0)
        .then(|| shadow::falloff(size[1] / size[0]));
    let mut draws: Vec<(Layer, Draw)> = Vec::new();
    draws.extend(opaque.into_iter().map(|d| (Layer::Opaque, d.4)));
    if shadow.is_some() {
        draws.push((Layer::Blend, Draw::Shadow));
    }
    draws.extend(blend.into_iter().map(|d| (Layer::Blend, d.3)));
    draws.extend(overlay.into_iter().map(|d| (Layer::Overlay, d.3)));

    let view = view_uniform(camera, job, scene, plan, &clips);
    Ok(Built {
        materials: materials.list,
        edge_slot,
        draws,
        view,
        shadow,
        clips,
    })
}

fn lerp(a: [f64; 3], b: [f64; 3], t: f64) -> [f64; 3] {
    std::array::from_fn(|i| a[i] + (b[i] - a[i]) * t)
}

fn view_uniform(camera: &Camera, job: &Job, scene: &Scene, plan: &Plan, clips: &[[f64; 4]]) -> ViewUniform {
    let f = |v: DVec3, w: f32| [v.x as f32, v.y as f32, v.z as f32, w];
    let mut clip = [[0f32; 4]; MAX_CLIPS];
    for (i, c) in clips.iter().enumerate() {
        clip[i] = c.map(|v| v as f32);
    }
    let fog = if job.fog {
        [camera.fog.0 as f32, camera.fog.1 as f32, 1.0, 0.0]
    } else {
        [0.0; 4]
    };
    let fog_color = hex_srgb(FOG_COLOR);
    let whole = &plan.whole;
    let size = whole.size();
    let center = whole.center();
    let over = shadow::QUAD_OVER_FOOTPRINT;
    ViewUniform {
        view_proj: camera.view_proj().as_mat4().to_cols_array_2d(),
        view: camera.view().as_mat4().to_cols_array_2d(),
        proj: camera.proj().as_mat4().to_cols_array_2d(),
        eye: f(camera.eye, if camera.ortho { 0.0 } else { 1.0 }),
        back: f(camera.back(), 0.0),
        screen: [camera.width as f32, camera.height as f32, camera.near as f32, camera.far as f32],
        fog,
        fog_color: [fog_color[0] as f32, fog_color[1] as f32, fog_color[2] as f32, 1.0],
        shadow_center: [
            center[0] as f32,
            center[1] as f32,
            (whole.min[2] - size[2].max(1.0) * 0.001) as f32,
            0.0,
        ],
        shadow_half: [(size[0] * over / 2.0) as f32, (size[1] * over / 2.0) as f32, 0.0, 0.0],
        clip,
        // clip_planes puts the bands first; the shadow is cut by those and not by a section.
        counts: [
            clips.len() as u32,
            scene.segment_count().max(1),
            scene.meshes.len() as u32,
            2 * job.clip.len() as u32,
        ],
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn names_sort_as_locale_compare_does() {
        let mut v = vec!["tee_b", "Tee-a", "tee-a", "tee10", "tee2", "tee-b"];
        v.sort_by(|a, b| collate(a, b));
        assert_eq!(v, ["tee_b", "tee-a", "Tee-a", "tee-b", "tee10", "tee2"]);
    }

    #[test]
    fn colours_decode_to_linear() {
        let c = hex_linear(0xffffff);
        assert!(c.iter().all(|v| (v - 1.0).abs() < 1e-12));
        assert!((hex_linear(0x808080)[0] - 0.2158605).abs() < 1e-6);
    }
}
