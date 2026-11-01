//! `hsm render`: pictures of a payload, drawn by the daemon's resident renderer. The GPU
//! device, its pipelines and the scenes last drawn stay warm in the daemon, so a picture
//! costs its own draw. Each picture is its own request, so a long manifest never holds the
//! socket while other callers wait to measure.
use crate::{
    Client, published,
    service::{Query, Request},
};
use anyhow::{Context, Result, anyhow, bail, ensure};
use clap::Args;
use hsm_render::{
    Renderer,
    job::{self, Clip, Framing, Job, Orbit, Ray, Section},
};
use serde_json::{Value, json};
use std::{
    io::Read,
    panic::{self, AssertUnwindSafe},
    path::{Path, PathBuf},
    sync::Mutex,
};

#[derive(Args)]
pub struct RenderArgs {
    /// A STEP path under hardware/; what is drawn is its payload, `<step>.mesh`.
    step: Option<String>,
    /// The PNG written. Relative paths resolve against the checkout root.
    out: Option<PathBuf>,
    /// A JSON array of jobs, or `-` for standard input. A key a job leaves out takes the
    /// flag of the same name, else its default.
    #[arg(long, value_name = "FILE|-")]
    jobs: Option<String>,
    /// Every named body and its box, without drawing.
    #[arg(long)]
    list: bool,
    /// Join two frames side by side at one scale, unresized.
    #[arg(long, num_args = 3, value_names = ["OUT", "LEFT", "RIGHT"])]
    twin: Vec<PathBuf>,
    /// Each report as JSON, one array, instead of its text.
    #[arg(long)]
    json: bool,
    /// tools/look.sh's frame: annotated, framed on the solid set, a hue each, 1400x1100.
    #[arg(long)]
    look: bool,
    /// A payload file to draw instead of a step's.
    #[arg(long)]
    payload: Option<PathBuf>,

    /// right, left, front, back, top, bottom or iso (+Z up, -Y front).
    #[arg(long)]
    view: Option<String>,
    /// Several views, each written beside OUT as `<out>.<view>.png`.
    #[arg(long, value_delimiter = ',')]
    views: Vec<String>,
    /// `a:from,to,step[,elev]`: a sweep about x, y or z, a frame per step as `<out>.<a><deg>.png`.
    #[arg(long)]
    orbit: Vec<String>,
    /// Camera direction from the target, `x,y,z`. Default 1,-1,1, or the view's.
    #[arg(long, allow_hyphen_values = true)]
    cam: Option<String>,
    /// Camera up, `x,y,z`. Default 0,0,1, or the view's.
    #[arg(long, allow_hyphen_values = true)]
    up: Option<String>,
    /// Look-at point, `x,y,z` in mm. Default: the centre of the framed box.
    #[arg(long, allow_hyphen_values = true)]
    target: Option<String>,
    /// Camera distance in radii of the framed box.
    #[arg(long)]
    zoom: Option<f64>,
    /// Orthographic half-height in mm; implies --ortho.
    #[arg(long)]
    span: Option<f64>,
    /// Camera distance from the target in mm, overriding --zoom.
    #[arg(long)]
    distance: Option<f64>,
    #[arg(long)]
    ortho: bool,
    /// The orthographic frame's margin over the framed radius.
    #[arg(long)]
    margin: Option<f64>,

    /// `WxH` pixels. Default 1600x1200, or 1400x1100 with --look.
    #[arg(long)]
    size: Option<String>,
    /// Background. Default #1a1a2e.
    #[arg(long)]
    bg: Option<String>,
    #[arg(long)]
    transparent: bool,
    /// Trim to the background and fit the long side inside 1600 px.
    #[arg(long)]
    trim: bool,
    #[arg(long)]
    no_ground: bool,
    #[arg(long)]
    no_fog: bool,

    /// Explicit opaque surfaces, which are also the default.
    #[arg(long)]
    solid: bool,
    /// Bodies drawn solid; the rest take --context. Comma-separated `*` globs.
    #[arg(long, value_delimiter = ',')]
    only: Vec<String>,
    /// The viewer's x-ray: faint faces and feature edges. `*` is the whole model.
    #[arg(long, value_delimiter = ',')]
    xray: Vec<String>,
    /// Feature edges alone, faint.
    #[arg(long, value_delimiter = ',')]
    ghost: Vec<String>,
    /// A faint shell, no edges, left out of the framing.
    #[arg(long, value_delimiter = ',')]
    shell: Vec<String>,
    #[arg(long, value_delimiter = ',')]
    hide: Vec<String>,
    /// Drawn in the selection amber as a material.
    #[arg(long, value_delimiter = ',')]
    highlight: Vec<String>,
    /// The picker's amber over the frame, through everything.
    #[arg(long, value_delimiter = ',')]
    select: Vec<String>,
    /// What unnamed bodies become once --only names a subject: ghost, hide, solid, xray,
    /// shell or drop.
    #[arg(long)]
    context: Option<String>,
    /// A hue for each solid body; the default with --look.
    #[arg(long)]
    tint: bool,
    #[arg(long)]
    no_tint: bool,
    /// Feature edges on the solid bodies too.
    #[arg(long)]
    edges: bool,

    /// `a:lo,hi`: keep geometry with world a in [lo, hi], cut faces open. Repeatable.
    #[arg(long, allow_hyphen_values = true)]
    clip: Vec<String>,
    /// `x,y,z:nx,ny,nz`: cut away the side the normal points to, the cut filled flat.
    #[arg(long, allow_hyphen_values = true)]
    section: Option<String>,

    /// The legend and scale bar, and labels and grid where they default on.
    #[arg(long)]
    annotate: bool,
    #[arg(long)]
    label: bool,
    #[arg(long)]
    no_label: bool,
    #[arg(long)]
    grid: bool,
    #[arg(long)]
    no_grid: bool,
    #[arg(long)]
    title: Option<String>,
    /// A line in the legend. Repeatable.
    #[arg(long)]
    caption: Vec<String>,
    /// `x,y`: the pixel the viewer's picker clicks. Repeatable.
    #[arg(long)]
    pick: Vec<String>,
    /// `x,y,z:dx,dy,dz[,limit]`: the run to the first surface. Repeatable.
    #[arg(long, allow_hyphen_values = true)]
    ray: Vec<String>,
    /// `A,B`: the box gap between two bodies. Repeatable.
    #[arg(long)]
    gap: Vec<String>,
}

fn numbers(s: &str, what: &str) -> Result<Vec<f64>> {
    s.split(',')
        .map(|t| t.trim().parse::<f64>())
        .collect::<Result<Vec<_>, _>>()
        .map_err(|_| anyhow!("bad {what} {s:?}"))
}

fn triple(s: &str, what: &str) -> Result<[f64; 3]> {
    numbers(s, what)?
        .try_into()
        .map_err(|_| anyhow!("bad {what} {s:?}: want x,y,z"))
}

fn clip(s: &str) -> Result<Clip> {
    let bad = || anyhow!("bad --clip {s:?}: want a:lo,hi");
    let (axis, band) = s.split_once([':', '=']).ok_or_else(bad)?;
    let [lo, hi]: [f64; 2] = numbers(band, "--clip")?.try_into().map_err(|_| bad())?;
    Ok(Clip {
        axis: axis.trim().to_ascii_lowercase(),
        lo,
        hi,
    })
}

fn section(s: &str) -> Result<Section> {
    let (at, normal) = s
        .split_once(':')
        .ok_or_else(|| anyhow!("bad --section {s:?}: want x,y,z:nx,ny,nz"))?;
    Ok(Section {
        at: triple(at, "--section point")?,
        normal: triple(normal, "--section normal")?,
    })
}

fn ray(s: &str) -> Result<Ray> {
    let bad = || anyhow!("bad --ray {s:?}: want x,y,z:dx,dy,dz[,limit]");
    let (from, rest) = s.split_once(':').ok_or_else(bad)?;
    let rest = numbers(rest, "--ray")?;
    ensure!(rest.len() == 3 || rest.len() == 4, bad());
    Ok(Ray {
        from: triple(from, "--ray origin")?,
        dir: [rest[0], rest[1], rest[2]],
        limit: rest.get(3).copied().unwrap_or(400.0),
    })
}

/// The job the flags describe, before a manifest or a set of views fills it in.
fn flags(a: &RenderArgs) -> Result<Job> {
    let mut j = Job::default();
    if a.look {
        j.frame = Framing::Look;
        j.annotate = true;
        j.tint = true;
        j.size = "1400x1100".into();
    }
    j.step = a.step.clone();
    j.payload = a.payload.clone();
    j.out = a.out.clone();
    j.view = a.view.clone();
    j.cam = a.cam.as_deref().map(|s| triple(s, "--cam")).transpose()?;
    j.up = a.up.as_deref().map(|s| triple(s, "--up")).transpose()?;
    j.target = a.target.as_deref().map(|s| triple(s, "--target")).transpose()?;
    j.zoom = a.zoom;
    j.span = a.span;
    j.distance = a.distance;
    j.ortho = a.ortho;
    j.margin = a.margin;
    if let Some(s) = &a.size {
        j.size = s.clone();
    }
    if let Some(b) = &a.bg {
        j.bg = b.clone();
    }
    j.transparent = a.transparent;
    j.trim = a.trim;
    j.ground = !a.no_ground;
    j.fog = !a.no_fog;
    j.solid = a.solid;
    j.only = a.only.clone();
    j.xray = a.xray.clone();
    j.ghost = a.ghost.clone();
    j.shell = a.shell.clone();
    j.hide = a.hide.clone();
    j.highlight = a.highlight.clone();
    j.select = a.select.clone();
    j.context = a.context.clone();
    j.tint = (j.tint || a.tint) && !a.no_tint;
    j.edges = a.edges;
    j.clip = a.clip.iter().map(|s| clip(s)).collect::<Result<_>>()?;
    j.section = a.section.as_deref().map(section).transpose()?;
    j.annotate = j.annotate || a.annotate;
    j.labels = match (a.label, a.no_label) {
        (true, true) => bail!("--label and --no-label"),
        (true, _) => Some(true),
        (_, true) => Some(false),
        _ => None,
    };
    j.grid = match (a.grid, a.no_grid) {
        (true, true) => bail!("--grid and --no-grid"),
        (true, _) => Some(true),
        (_, true) => Some(false),
        _ => None,
    };
    j.title = a.title.clone();
    j.caption = a.caption.clone();
    j.pick = a
        .pick
        .iter()
        .map(|s| {
            numbers(s, "--pick")?
                .try_into()
                .map_err(|_| anyhow!("bad --pick {s:?}: want x,y"))
        })
        .collect::<Result<_>>()?;
    j.ray = a.ray.iter().map(|s| ray(s)).collect::<Result<_>>()?;
    j.gap = a
        .gap
        .iter()
        .map(|s| match s.split(',').map(str::trim).collect::<Vec<_>>()[..] {
            [x, y] if !x.is_empty() && !y.is_empty() => Ok([x.to_owned(), y.to_owned()]),
            _ => Err(anyhow!("bad --gap {s:?}: want A,B")),
        })
        .collect::<Result<_>>()?;
    Ok(j)
}

/// A manifest's jobs, each over the job the flags describe.
fn manifest(source: &str, base: &Job) -> Result<Vec<Job>> {
    let text = if source == "-" {
        let mut s = String::new();
        std::io::stdin().read_to_string(&mut s)?;
        s
    } else {
        std::fs::read_to_string(source).with_context(|| format!("read {source}"))?
    };
    let entries: Vec<Value> =
        serde_json::from_str(&text).with_context(|| format!("--jobs {source}: want a JSON array of jobs"))?;
    let base = serde_json::to_value(base)?;
    entries
        .into_iter()
        .enumerate()
        .map(|(i, entry)| {
            let Value::Object(keys) = entry else {
                bail!("--jobs[{i}]: want an object");
            };
            let mut job = base.clone();
            for (k, v) in keys {
                job[k] = v;
            }
            serde_json::from_value(job).with_context(|| format!("--jobs[{i}]"))
        })
        .collect()
}

fn rooted(root: &Path, p: &Path) -> PathBuf {
    if p.is_absolute() { p.to_path_buf() } else { root.join(p) }
}

fn print_text(report: &Value) {
    for line in report["text"].as_array().into_iter().flatten() {
        println!("{}", line.as_str().unwrap_or_default());
    }
}

pub fn run(client: &Client, a: RenderArgs) -> Result<bool> {
    if !a.twin.is_empty() {
        let _lease = hsm_run_slots::acquire("hsm:render-twin", hsm_run_slots::inherited()?, false)?;
        let [out, left, right] = [0, 1, 2].map(|i| rooted(&client.root, &a.twin[i]));
        let report = hsm_render::twin(&out, &left, &right)?;
        if a.json {
            println!("{}", serde_json::to_string_pretty(&report)?);
        } else {
            print_text(&report);
        }
        return Ok(true);
    }
    let base = flags(&a)?;
    let jobs = match &a.jobs {
        Some(source) => {
            ensure!(
                a.step.is_none() && a.out.is_none(),
                "--jobs takes the whole run; drop the step and the output path"
            );
            manifest(source, &base)?
        }
        None => vec![base],
    };
    let orbits: Vec<Orbit> = a.orbit.iter().map(|s| s.parse()).collect::<Result<_>>()?;
    let mut shots = Vec::new();
    for j in &jobs {
        if a.list {
            shots.push(j.clone());
        } else {
            shots.extend(job::shots(j, &a.views, &orbits)?);
        }
    }
    let mut reports = Vec::new();
    let mut failed = Vec::new();
    for j in shots {
        let what = j.out.as_ref().map_or_else(
            || j.step.clone().unwrap_or_default(),
            |o| o.display().to_string(),
        );
        let answer = (|| -> Result<Value> {
            published::ensure(&hsm_render::payload_path(&client.root, &j)?)?;
            let response = client.call(&Request {
                scene: PathBuf::new(),
                query: Query::Render {
                    root: client.root.clone(),
                    job: Box::new(j),
                    list: a.list,
                },
            })?;
            match response["ok"].as_bool() {
                Some(true) => Ok(response["result"].clone()),
                _ => bail!("{}", response["error"].as_str().unwrap_or("the daemon refused the picture")),
            }
        })();
        match answer {
            Ok(report) => {
                if !a.json {
                    if report["text"].as_array().is_some_and(|t| !t.is_empty()) {
                        print_text(&report);
                    } else {
                        println!(
                            "wrote {}  {}x{}  {} ms",
                            report["out"].as_str().unwrap_or_default(),
                            report["width"],
                            report["height"],
                            report["ms"]["total"]
                        );
                    }
                }
                reports.push(report);
            }
            Err(e) => {
                eprintln!("FAILED {what}: {e:#}");
                reports.push(json!({"out": what, "error": format!("{e:#}")}));
                failed.push(what);
            }
        }
    }
    if a.json {
        println!("{}", serde_json::to_string_pretty(&reports)?);
    }
    if !failed.is_empty() && reports.len() > 1 {
        eprintln!("{} of {} pictures failed: {}", failed.len(), reports.len(), failed.join(", "));
    }
    Ok(failed.is_empty())
}

/// The daemon's renderer, made on the first picture. A renderer that panics is let go, so the
/// next picture starts a fresh one and geometry queries carry on.
static RENDERER: Mutex<Option<Renderer>> = Mutex::new(None);

pub fn execute(root: &Path, job: &Job, list: bool) -> Result<Value> {
    let mut held = RENDERER.lock().unwrap_or_else(|p| p.into_inner());
    let renderer = held.get_or_insert_with(Renderer::new);
    let drawn = panic::catch_unwind(AssertUnwindSafe(|| {
        if list { renderer.list(root, job) } else { renderer.render(root, job) }
    }));
    drawn.unwrap_or_else(|p| {
        *held = None;
        let why = p
            .downcast_ref::<&str>()
            .map(|s| s.to_string())
            .or_else(|| p.downcast_ref::<String>().cloned())
            .unwrap_or_default();
        Err(anyhow!("the renderer panicked: {why}"))
    })
}

/// The renderer's warm state, for `hsm status`.
pub fn status() -> Value {
    let held = RENDERER.lock().unwrap_or_else(|p| p.into_inner());
    held.as_ref().map_or(Value::Null, Renderer::status)
}
