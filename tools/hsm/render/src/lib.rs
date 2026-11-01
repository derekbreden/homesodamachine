//! Pictures of the machine from its mesh payloads, drawn on this Mac's GPU the way the /3d
//! viewer draws them: its colours, finishes, lights, x-ray, contact shadow and fog, with the
//! feature edges along the payload's B-rep face boundaries. A `Renderer` lives in the hsm daemon,
//! so the device, the pipelines, the baked studio light and the last scenes drawn stay warm and a
//! picture costs its own draw.

pub mod annotate;
pub mod camera;
mod env;
mod gpu;
pub mod image;
pub mod job;
mod overlay;
pub mod payload;
pub mod pick;
pub mod plan;
pub mod scene;
mod shadow;

use crate::annotate::{Look, fixed, rounded};
use crate::camera::Camera;
use crate::gpu::{Frame, Gpu, SceneBuffers};
use crate::image::Image;
use crate::job::{Job, any_glob, parse_color, parse_size};
use crate::plan::{Finish, Plan, Role, collate};
use crate::scene::Scene;
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};
use std::time::{Instant, SystemTime};

/// The largest frame drawn: its multisampled colour and depth come to half a gigabyte.
const MAX_PIXELS: u64 = 4096 * 4096;
/// What the scenes kept warm may hold, CPU and GPU together, before the least recently drawn
/// one is let go. The scene being drawn is always kept.
const SCENE_BUDGET: u64 = 1 << 30;
/// A trim keeps the band this far off the background.
const TRIM_THRESHOLD: u8 = 10;
const TRIM_FIT: u32 = 1600;

const SOURCES: [&str; 18] = [
    include_str!("lib.rs"),
    include_str!("annotate.rs"),
    include_str!("camera.rs"),
    include_str!("env.rs"),
    include_str!("gpu.rs"),
    include_str!("image.rs"),
    include_str!("job.rs"),
    include_str!("overlay.rs"),
    include_str!("payload.rs"),
    include_str!("pick.rs"),
    include_str!("plan.rs"),
    include_str!("scene.rs"),
    include_str!("shadow.rs"),
    include_str!("shaders/common.wgsl"),
    include_str!("shaders/surface.wgsl"),
    include_str!("shaders/line.wgsl"),
    include_str!("shaders/shadow.wgsl"),
    include_str!("shaders/env.wgsl"),
];

/// A digest of everything that decides a picture's pixels, for the daemon's build identity.
pub fn source_digest() -> String {
    let mut h = Sha256::new();
    for s in SOURCES {
        h.update(s.as_bytes());
        h.update([0]);
    }
    h.finalize().iter().take(8).map(|b| format!("{b:02x}")).collect()
}

struct Loaded {
    scene: Scene,
    /// On the device once the scene is first drawn.
    buffers: Option<SceneBuffers>,
    bytes: u64,
    used: u64,
}

fn ms(since: Instant) -> f64 {
    (since.elapsed().as_secs_f64() * 1e5).round() / 100.0
}

/// The payload a job draws: `payload` when it names one, else the step's, beside it under hardware/.
pub fn payload_path(root: &Path, job: &Job) -> Result<PathBuf> {
    if let Some(p) = &job.payload {
        return Ok(if p.is_absolute() { p.clone() } else { root.join(p) });
    }
    let step = job.step.as_deref().context("a job names a `step` or a `payload`")?;
    let mesh = if step.ends_with(".mesh") { step.to_owned() } else { format!("{step}.mesh") };
    if Path::new(&mesh).is_absolute() {
        return Ok(PathBuf::from(mesh));
    }
    Ok(root.join("hardware").join(mesh.strip_prefix("hardware/").unwrap_or(&mesh)))
}

fn step_title(root: &Path, job: &Job) -> String {
    if let Some(t) = &job.title {
        return t.clone();
    }
    match (&job.step, &job.payload) {
        (Some(s), _) => format!("hardware/{}", s.strip_prefix("hardware/").unwrap_or(s)),
        (None, Some(p)) => p.strip_prefix(root).unwrap_or(p).display().to_string(),
        (None, None) => String::new(),
    }
}

#[derive(Default)]
pub struct Renderer {
    gpu: Option<Gpu>,
    scenes: Vec<Loaded>,
    finishes: Option<(PathBuf, SystemTime, Vec<Finish>)>,
    tick: u64,
}

impl Renderer {
    pub fn new() -> Renderer {
        Renderer::default()
    }

    /// The device and pipelines, made on the first picture; the milliseconds that took, if now.
    fn ensure_gpu(&mut self) -> Result<Option<f64>> {
        if self.gpu.is_some() {
            return Ok(None);
        }
        let t = Instant::now();
        self.gpu = Some(Gpu::new()?);
        Ok(Some(ms(t)))
    }

    pub fn adapter(&self) -> Option<&str> {
        self.gpu.as_ref().map(|g| g.adapter.as_str())
    }

    /// web/public/finishes.json, read again whenever it changes.
    fn finishes(&mut self, root: &Path) -> Result<Vec<Finish>> {
        let path = root.join("web/public/finishes.json");
        let modified = std::fs::metadata(&path).and_then(|m| m.modified()).ok();
        if let (Some((p, t, rows)), Some(m)) = (&self.finishes, modified)
            && *p == path
            && *t == m
        {
            return Ok(rows.clone());
        }
        let Some(m) = modified else {
            return Ok(Vec::new());
        };
        #[derive(serde::Deserialize)]
        struct File {
            finishes: Vec<Finish>,
        }
        let text = std::fs::read_to_string(&path).with_context(|| format!("read {}", path.display()))?;
        let rows = serde_json::from_str::<File>(&text)
            .with_context(|| format!("parse {}", path.display()))?
            .finishes;
        self.finishes = Some((path, m, rows.clone()));
        Ok(rows)
    }

    /// The scene at `path`, read again when the payload has changed; the milliseconds the read
    /// took, if it was read now.
    fn scene(&mut self, path: &Path) -> Result<(usize, Option<f64>)> {
        let stamp = scene::stamp(path)?;
        // A payload deleted since it was drawn, as a caller's scratch copy is, holds no budget.
        self.scenes.retain(|l| l.scene.path.exists());
        self.tick += 1;
        if let Some(i) = self.scenes.iter().position(|l| l.scene.path == path) {
            if self.scenes[i].scene.stamp == stamp {
                self.scenes[i].used = self.tick;
                return Ok((i, None));
            }
            self.scenes.remove(i);
        }
        let t = Instant::now();
        let scene = Scene::load(path)?;
        let bytes = (scene.positions.len() * 24 + scene.indices.len() * 4
            + scene.segments.len() * 32 + scene.attributes.len() * 32) as u64;
        self.scenes.push(Loaded {
            scene,
            buffers: None,
            bytes,
            used: self.tick,
        });
        let i = self.scenes.len() - 1;
        self.evict(i);
        let i = self.scenes.iter().position(|l| l.scene.path == path).unwrap_or(0);
        Ok((i, Some(ms(t))))
    }

    /// Let the least recently drawn scenes go until the rest fit the budget, keeping `keep`.
    fn evict(&mut self, keep: usize) {
        let keep_path = self.scenes[keep].scene.path.clone();
        loop {
            let total: u64 = self.scenes.iter().map(|l| l.bytes).sum();
            if total <= SCENE_BUDGET || self.scenes.len() <= 1 {
                return;
            }
            let Some(oldest) = (0..self.scenes.len())
                .filter(|&i| self.scenes[i].scene.path != keep_path)
                .min_by_key(|&i| self.scenes[i].used)
            else {
                return;
            };
            self.scenes.remove(oldest);
        }
    }

    /// The warm state, for `hsm status`.
    pub fn status(&self) -> Value {
        json!({
            "adapter": self.adapter(),
            "scenes": self.scenes.iter().map(|l| json!({
                "payload": l.scene.path.display().to_string(),
                "meshes": l.scene.meshes.len(),
                "bodies": l.scene.bodies.len(),
                "bytes": l.bytes,
                "on_gpu": l.buffers.is_some(),
            })).collect::<Vec<_>>(),
        })
    }

    /// Every named body and its box, as `--list` prints them.
    pub fn list(&mut self, root: &Path, job: &Job) -> Result<Value> {
        let path = payload_path(root, job)?;
        let (i, _) = self.scene(&path)?;
        let scene = &self.scenes[i].scene;
        let mut rows: Vec<(String, [f64; 3], [f64; 3])> = scene
            .bodies
            .iter()
            .map(|b| {
                let name = if b.name.is_empty() { "(unnamed)".to_owned() } else { b.name.clone() };
                (name, b.bbox.min.map(|v| rounded(v, 2)), b.bbox.max.map(|v| rounded(v, 2)))
            })
            .collect();
        rows.sort_by(|a, b| collate(&a.0, &b.0));
        let w = rows.iter().map(|r| r.0.chars().count()).max().unwrap_or(0).max(4);
        let label = job.step.clone().unwrap_or_else(|| path.display().to_string());
        let mut text = vec![format!("{} named bodies in {label}", rows.len())];
        for (name, lo, hi) in &rows {
            let f = |v: f64| format!("{:>9}", fixed(v, 2));
            text.push(format!(
                "{name:<w$}  x[{},{}] y[{},{}] z[{},{}]",
                f(lo[0]),
                f(hi[0]),
                f(lo[1]),
                f(hi[1]),
                f(lo[2]),
                f(hi[2])
            ));
        }
        Ok(json!({
            "payload": path.display().to_string(),
            "bodies": rows.iter().map(|(n, lo, hi)| json!({"name": n, "min": lo, "max": hi})).collect::<Vec<_>>(),
            "text": text,
        }))
    }

    /// Draw one job and write its PNG. The report says what was drawn, from where, and what the
    /// picture answers.
    pub fn render(&mut self, root: &Path, job: &Job) -> Result<Value> {
        let start = Instant::now();
        job.check()?;
        let (w, h) = parse_size(&job.size)?;
        ensure!(
            w as u64 * h as u64 <= MAX_PIXELS,
            "a {w}x{h} frame is past the {MAX_PIXELS}-pixel ceiling a frame's targets fit in"
        );
        let out = job.out.as_ref().map(|o| if o.is_absolute() { o.clone() } else { root.join(o) }).context("a job needs `out`")?;
        let path = payload_path(root, job)?;
        let gpu_ms = self.ensure_gpu()?;
        let finishes = self.finishes(root)?;
        let (i, load_ms) = self.scene(&path)?;
        let t_upload = Instant::now();
        let mut upload_ms = None;
        if self.scenes[i].buffers.is_none() {
            let gpu = self.gpu.as_ref().expect("made above");
            let loaded = &mut self.scenes[i];
            let buffers = gpu.upload(&loaded.scene);
            // What only the GPU reads is let go on this side once it is there.
            loaded.scene.normals = Vec::new();
            loaded.scene.segments = Vec::new();
            loaded.scene.attributes = Vec::new();
            loaded.bytes = (loaded.scene.positions.len() * 12 + loaded.scene.indices.len() * 4) as u64 + buffers.bytes;
            loaded.buffers = Some(buffers);
            upload_ms = Some(ms(t_upload));
            self.evict(i);
        }
        let i = self.scenes.iter().position(|l| l.scene.path == path).context("the scene left the cache")?;
        let gpu = self.gpu.as_ref().expect("made above");
        let loaded = &self.scenes[i];
        let scene = &loaded.scene;
        let buffers = loaded.buffers.as_ref().expect("uploaded above");

        let t_plan = Instant::now();
        let plan = Plan::new(scene, job);
        ensure!(!plan.whole.is_empty(), "nothing to draw in {}", path.display());
        let camera = Camera::frame(job, &plan.subject, &plan.whole, &plan.whole, w, h);
        let clips = plan::clip_planes(job)?;
        let picks: Vec<annotate::Pick> = job.pick.iter().map(|&px| annotate::pick(scene, &plan, &camera, &clips, px)).collect();
        let casts: Vec<annotate::Cast> = job.ray.iter().map(|r| annotate::cast(scene, &plan, r.from, r.dir, r.limit)).collect();
        let gaps: Vec<annotate::Gap> = job.gap.iter().map(|[a, b]| annotate::gap(scene, a, b)).collect();
        let mut lit = vec![false; scene.bodies.len()];
        for p in &picks {
            if let Some((b, _, _)) = p.hit {
                lit[b] = true;
            }
        }
        let mut selected = Vec::new();
        for (b, body) in scene.bodies.iter().enumerate() {
            if any_glob(&job.select, &body.name) && !matches!(plan.roles[b], Role::Hidden | Role::Dropped) {
                lit[b] = true;
                selected.push(body.name.clone());
            }
        }
        selected.sort();
        let plan_ms = ms(t_plan);
        let t_build = Instant::now();
        let built = plan::build(scene, job, &plan, &camera, &finishes, &lit)?;
        let textures: Vec<Image> = built.textures.iter().map(|path|
            image::read_png(&if path.is_absolute() { path.clone() } else { root.join(path) })
        ).collect::<Result<_>>()?;
        let build_ms = ms(t_build);

        let t_draw = Instant::now();
        let clear = if job.transparent {
            [0.0; 4]
        } else {
            let c = parse_color(&job.bg)?;
            [c[0], c[1], c[2], 1.0]
        };
        let rgba = gpu.draw(
            scene,
            buffers,
            &Frame {
                width: w,
                height: h,
                view: built.view,
                clear,
                materials: &built.materials,
                textures: &textures,
                edge_slot: &built.edge_slot,
                draws: &built.draws,
                shadow: built.shadow.as_deref(),
            },
        )?;
        let draw_ms = ms(t_draw);

        let t_post = Instant::now();
        let mut img = Image::from_frame(rgba, w, h, job.transparent);
        let out_text = out.display().to_string();
        let look = Look {
            scene,
            job,
            plan: &plan,
            camera: &camera,
            picks: &picks,
            casts: &casts,
            gaps: &gaps,
            selected: &selected,
            title: step_title(root, job),
            out: out_text.clone(),
        };
        let annotations = job.annotate.then(|| look.annotate());
        if let Some(a) = &annotations {
            overlay::draw(&mut img, a)?;
        }
        if job.trim {
            let bg = if job.transparent {
                [0, 0, 0]
            } else {
                parse_color(&job.bg)?.map(|c| (c * 255.0).round() as u8)
            };
            img = img.trim(bg, TRIM_THRESHOLD).fit_inside(TRIM_FIT);
        }
        let post_ms = ms(t_post);
        let t_encode = Instant::now();
        let png = img.png()?;
        if let Some(dir) = out.parent() {
            std::fs::create_dir_all(dir).with_context(|| format!("make {}", dir.display()))?;
        }
        std::fs::write(&out, &png).with_context(|| format!("write {}", out.display()))?;
        let encode_ms = ms(t_encode);

        let body = |b: usize| scene.bodies[b].name.clone();
        let count = |r: Role| plan.count(r);
        let mut text = annotations.as_ref().map(|a| a.text.clone()).unwrap_or_default();
        if job.annotate && !plan.unmatched.is_empty() {
            let mut names: Vec<&str> = scene.bodies.iter().map(|b| b.name.as_str()).collect();
            names.sort();
            text.push(String::new());
            text.push(format!("  !! matched no body: {}", plan.unmatched.join("  ")));
            for u in &plan.unmatched {
                let pat = u.rsplit(' ').next().unwrap_or("").replace('*', "");
                let stem = pat.split('-').next().unwrap_or("");
                let head: String = pat.chars().take(4).collect();
                let near: Vec<&str> = names.iter().copied().filter(|n| n.contains(stem) || n.starts_with(&head)).collect();
                text.push(format!(
                    "     {u} — nearest names present: {}",
                    if near.is_empty() { "(none)".into() } else { near.join(" ") }
                ));
            }
            text.push(format!("     all {} names in the mounted group:", names.len()));
            text.push(format!(
                "     {}",
                names.iter().map(|n| if n.is_empty() { "(unnamed)" } else { n }).collect::<Vec<_>>().join(" ")
            ));
        }
        Ok(json!({
            "out": out_text,
            "width": img.width,
            "height": img.height,
            "bytes": png.len(),
            "payload": path.display().to_string(),
            "scene": {
                "meshes": scene.meshes.len(),
                "bodies": scene.bodies.len(),
                "triangles": scene.indices.len() / 3,
                "segments": scene.segment_count(),
            },
            "camera": camera.report(),
            "mm_per_px": camera.mm_per_px(),
            "bodies": {
                "solid": count(Role::Solid),
                "highlight": count(Role::Highlight),
                "xray": count(Role::Xray),
                "ghost": count(Role::Ghost),
                "shell": count(Role::Shell),
                "hidden": count(Role::Hidden),
                "dropped": count(Role::Dropped),
            },
            "unmatched": plan.unmatched,
            "selected": selected,
            "picks": picks.iter().map(|p| json!({
                "px": p.px,
                "name": p.hit.map(|(b, _, _)| body(b)),
                "at": (p.hit.map(|(_, at, _)| [at.x, at.y, at.z].map(|v| rounded(v, 2)))),
                "mm": p.hit.map(|(_, _, mm)| rounded(mm, 2)),
            })).collect::<Vec<_>>(),
            "rays": casts.iter().map(|c| json!({
                "from": c.from,
                "dir": c.dir,
                "limit": c.limit,
                "name": c.hit.map(|(b, _)| body(b)),
                "mm": c.hit.map(|(_, mm)| rounded(mm, 2)),
                "at": ([c.end.x, c.end.y, c.end.z].map(|v| rounded(v, 2))),
            })).collect::<Vec<_>>(),
            "gaps": gaps.iter().map(|g| match g {
                annotate::Gap::Missing(a, b) => json!({"a": a, "b": b, "missing": true}),
                annotate::Gap::Overlap(a, b) => json!({"a": a, "b": b, "overlap": true}),
                annotate::Gap::Found { a, b, axis, mm, .. } => json!({"a": a, "b": b, "axis": (["x", "y", "z"][*axis]), "mm": mm}),
            }).collect::<Vec<_>>(),
            "legend": annotations.as_ref().map(|a| a.legend.clone()),
            "text": text,
            "ms": {
                "gpu_init": gpu_ms,
                "load": load_ms,
                "upload": upload_ms,
                "plan": plan_ms,
                "build": build_ms,
                "draw": draw_ms,
                "post": post_ms,
                "encode": encode_ms,
                "total": ms(start),
            },
        }))
    }
}

/// Two frames joined side by side at one scale, written to `out`.
pub fn twin(out: &Path, left: &Path, right: &Path) -> Result<Value> {
    let joined = Image::twin(&image::read_png(left)?, &image::read_png(right)?);
    if let Some(dir) = out.parent() {
        std::fs::create_dir_all(dir)?;
    }
    std::fs::write(out, joined.png()?).with_context(|| format!("write {}", out.display()))?;
    Ok(json!({
        "out": out.display().to_string(),
        "width": joined.width,
        "height": joined.height,
        "text": [format!("joined {}x{}  {}", joined.width, joined.height, out.display())],
    }))
}
