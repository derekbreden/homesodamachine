//! One picture: what to draw, from where, and how. A `--jobs` manifest is a JSON array of these,
//! and every key a job leaves out takes the default below.

use anyhow::{Result, bail, ensure};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// How the subject is framed when the job gives no camera distance of its own.
#[derive(Clone, Copy, Debug, Default, Deserialize, Serialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum Framing {
    /// Off the whole model's box: half its largest side is the radius, `zoom` radii away, and
    /// an orthographic frame of `radius × margin` (1.1). The installation art is drawn this way.
    #[default]
    Posed,
    /// Off the solid set's box, at least 1 mm: `zoom` 2.5, an orthographic frame of
    /// `radius × margin` (1.15) seen from eight radii out. `tools/look.sh` reads the pack this way.
    Look,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Clip {
    /// `x`, `y` or `z`.
    pub axis: String,
    pub lo: f64,
    pub hi: f64,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Section {
    /// A point on the cutting plane, in mm.
    pub at: [f64; 3],
    /// The side this points to is cut away.
    pub normal: [f64; 3],
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Ray {
    pub from: [f64; 3],
    pub dir: [f64; 3],
    #[serde(default = "default_ray_limit")]
    pub limit: f64,
}

fn default_ray_limit() -> f64 {
    400.0
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Sphere {
    pub center: [f64; 3],
    pub radius: f64,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(default, deny_unknown_fields)]
pub struct Job {
    /// A STEP path under hardware/: the model, and what the viewer keys its look off. What is
    /// drawn is its payload, `<step>.mesh`, unless `payload` names other bytes.
    pub step: Option<String>,
    /// A payload file to draw in place of the step's own: a model standing outside the tree, or
    /// another version of one.
    pub payload: Option<PathBuf>,
    /// Where the PNG goes. Relative paths resolve against the checkout root.
    pub out: Option<PathBuf>,

    /// A named camera: right, left, front, back, top, bottom or iso (+Z up, -Y front).
    pub view: Option<String>,
    /// Camera direction from the target; unnormalised is fine. Default 1,-1,1, or the view's.
    pub cam: Option<[f64; 3]>,
    /// Camera up. Default 0,0,1, or the view's.
    pub up: Option<[f64; 3]>,
    /// Look-at point. Default: the centre of the framed box.
    pub target: Option<[f64; 3]>,
    /// Distance in radii of the framed box.
    pub zoom: Option<f64>,
    /// Orthographic half-height in mm. Implies `ortho`.
    pub span: Option<f64>,
    /// Camera distance from the target in mm, overriding `zoom`.
    pub distance: Option<f64>,
    pub ortho: bool,
    pub frame: Framing,
    /// The orthographic frame's margin over the framed radius.
    pub margin: Option<f64>,
    /// The sphere the depth planes are fitted to, for pictures that must share them. Default:
    /// the model's.
    pub depth: Option<Sphere>,
    /// The orbit step this shot is, for the legend.
    pub orbit: Option<String>,

    /// `WxH` in pixels.
    pub size: String,
    pub bg: String,
    /// A real alpha channel instead of the background.
    pub transparent: bool,
    /// Trim to the background and fit the long side inside 1600 px.
    pub trim: bool,
    /// The contact shadow under the model.
    pub ground: bool,
    /// The distance fade toward the viewer's blue.
    pub fog: bool,

    /// Accepted from render-step-posed manifests; opaque surfaces are the default.
    pub solid: bool,
    /// Bodies drawn opaque. Unnamed bodies take `context`. Empty: every body.
    pub only: Vec<String>,
    /// The viewer's x-ray, for these bodies: faint faces and feature edges. `*` is the whole model.
    pub xray: Vec<String>,
    /// Feature edges alone, faint, no faces.
    pub ghost: Vec<String>,
    /// A faint shell, no edges, left out of the framing.
    pub shell: Vec<String>,
    /// Removed.
    pub hide: Vec<String>,
    /// Drawn in the selection amber as a material.
    pub highlight: Vec<String>,
    /// The picker's amber over the frame: bright edges and a faint shell, through everything.
    pub select: Vec<String>,
    /// What a body nobody named becomes once `only` names a subject: ghost, hide, solid, xray,
    /// shell, or drop (out of the scene, the framing and the shadow).
    pub context: Option<String>,
    /// A distinct hue for each solid body.
    pub tint: bool,
    /// Feature edges on the solid bodies too.
    pub edges: bool,

    /// Keep only geometry inside each band; cut faces are left open.
    pub clip: Vec<Clip>,
    /// Cut by a plane, the cut faces filled flat.
    pub section: Option<Section>,

    /// The legend, scale bar and (unless turned off) labels and grid of `tools/look.sh`.
    pub annotate: bool,
    pub labels: Option<bool>,
    pub grid: Option<bool>,
    pub title: Option<String>,
    pub caption: Vec<String>,
    /// Pixels to click, as the viewer's picker does.
    pub pick: Vec<[f64; 2]>,
    pub ray: Vec<Ray>,
    /// Box gaps between two bodies.
    pub gap: Vec<[String; 2]>,
}

impl Default for Job {
    fn default() -> Self {
        Job {
            step: None,
            payload: None,
            out: None,
            view: None,
            cam: None,
            up: None,
            target: None,
            zoom: None,
            span: None,
            distance: None,
            ortho: false,
            frame: Framing::Posed,
            margin: None,
            depth: None,
            orbit: None,
            size: "1600x1200".into(),
            bg: "#1a1a2e".into(),
            transparent: false,
            trim: false,
            ground: true,
            fog: true,
            solid: false,
            only: Vec::new(),
            xray: Vec::new(),
            ghost: Vec::new(),
            shell: Vec::new(),
            hide: Vec::new(),
            highlight: Vec::new(),
            select: Vec::new(),
            context: None,
            tint: false,
            edges: false,
            clip: Vec::new(),
            section: None,
            annotate: false,
            labels: None,
            grid: None,
            title: None,
            caption: Vec::new(),
            pick: Vec::new(),
            ray: Vec::new(),
            gap: Vec::new(),
        }
    }
}

/// Camera presets. Repo convention is +Z up, -Y front (the user's side), +X right; the two Z-axis
/// views lay up onto ∓Y, as the viewer's ViewCube does.
pub fn preset(name: &str) -> Option<([f64; 3], [f64; 3])> {
    Some(match name {
        "right" => ([1.0, 0.0, 0.0], [0.0, 0.0, 1.0]),
        "left" => ([-1.0, 0.0, 0.0], [0.0, 0.0, 1.0]),
        "front" => ([0.0, -1.0, 0.0], [0.0, 0.0, 1.0]),
        "back" => ([0.0, 1.0, 0.0], [0.0, 0.0, 1.0]),
        "top" => ([0.0, 0.0, 1.0], [0.0, -1.0, 0.0]),
        "bottom" => ([0.0, 0.0, -1.0], [0.0, 1.0, 0.0]),
        "iso" => ([1.0, -1.0, 1.0], [0.0, 0.0, 1.0]),
        _ => return None,
    })
}

pub const PRESETS: &str = "right, left, front, back, top, bottom, iso";

pub fn parse_size(s: &str) -> Result<(u32, u32)> {
    let Some((w, h)) = s.split_once('x') else {
        bail!("bad size {s:?}: want WxH")
    };
    let (w, h): (u32, u32) = (w.parse()?, h.parse()?);
    ensure!(
        (16..=8192).contains(&w) && (16..=8192).contains(&h),
        "size {s} is outside 16..8192 pixels"
    );
    Ok((w, h))
}

pub fn parse_color(s: &str) -> Result<[f64; 3]> {
    let hex = s.trim().trim_start_matches('#');
    let hex = if hex.len() == 3 {
        hex.chars().flat_map(|c| [c, c]).collect::<String>()
    } else {
        hex.to_owned()
    };
    ensure!(hex.len() == 6, "bad colour {s:?}: want #rrggbb");
    let v = u32::from_str_radix(&hex, 16)?;
    Ok([(v >> 16) & 255, (v >> 8) & 255, v & 255].map(|c| c as f64 / 255.0))
}

impl Job {
    pub fn check(&self) -> Result<()> {
        ensure!(self.step.is_some() || self.payload.is_some(), "a job names a `step` or a `payload`");
        ensure!(self.out.is_some(), "a job needs `out`");
        parse_size(&self.size)?;
        parse_color(&self.bg)?;
        for (name, v) in [("zoom", self.zoom), ("span", self.span), ("distance", self.distance), ("margin", self.margin)] {
            if let Some(v) = v {
                ensure!(v.is_finite() && v > 0.0, "bad {name}: {v}");
            }
        }
        if let Some(v) = &self.view {
            ensure!(preset(v).is_some(), "unknown view {v} (have {PRESETS})");
        }
        if let Some(c) = &self.context {
            ensure!(
                ["ghost", "hide", "solid", "xray", "shell", "drop"].contains(&c.as_str()),
                "bad context {c} (ghost, hide, solid, xray, shell or drop)"
            );
        }
        for c in &self.clip {
            ensure!(["x", "y", "z"].contains(&c.axis.as_str()), "bad clip axis {}", c.axis);
            ensure!(c.hi > c.lo, "clip {}[{},{}]: hi must exceed lo", c.axis, c.lo, c.hi);
        }
        for r in &self.ray {
            ensure!(r.dir.iter().any(|v| *v != 0.0), "a ray needs a direction");
        }
        if let Some(d) = &self.depth {
            ensure!(d.radius.is_finite() && d.radius > 0.0, "bad depth radius {}", d.radius);
        }
        Ok(())
    }

    pub fn cam_up(&self) -> ([f64; 3], [f64; 3]) {
        let (pc, pu) = self
            .view
            .as_deref()
            .and_then(preset)
            .unwrap_or(([1.0, -1.0, 1.0], [0.0, 0.0, 1.0]));
        (self.cam.unwrap_or(pc), self.up.unwrap_or(pu))
    }

    pub fn is_ortho(&self) -> bool {
        self.ortho || self.span.is_some()
    }
}

/// An `--orbit`: one axis swept from one angle to another in steps, `elev` degrees off the
/// equator of a turn about Z.
#[derive(Clone, Debug, PartialEq)]
pub struct Orbit {
    pub axis: char,
    pub from: f64,
    pub to: f64,
    pub step: f64,
    pub elev: f64,
}

impl std::str::FromStr for Orbit {
    type Err = anyhow::Error;

    /// `a:from,to,step[,elev]`, a one of x, y or z.
    fn from_str(s: &str) -> Result<Orbit> {
        let bad = || anyhow::anyhow!("bad --orbit {s} (want axis:from,to,step[,elev])");
        let (axis, rest) = s.split_once([':', '=']).ok_or_else(bad)?;
        let axis = match axis.trim().to_ascii_lowercase().as_str() {
            "x" => 'x',
            "y" => 'y',
            "z" => 'z',
            _ => return Err(bad()),
        };
        let v: Vec<f64> = rest.split(',').map(|t| t.trim().parse()).collect::<Result<_, _>>().map_err(|_| bad())?;
        ensure!(v.len() == 3 || v.len() == 4, bad());
        ensure!(v[2] > 0.0, "bad --orbit {s} (step must be positive)");
        Ok(Orbit {
            axis,
            from: v[0],
            to: v[1],
            step: v[2],
            elev: v.get(3).copied().unwrap_or(0.0),
        })
    }
}

/// One turn of an orbit as a camera direction and up. A turntable about Z keeps up at +Z; a
/// tumble about X or Y passes through the pole, so up rides the same circle a quarter turn ahead.
fn orbit_pose(axis: char, a: f64, elev: f64) -> ([f64; 3], [f64; 3]) {
    let (c, s) = (a.cos(), a.sin());
    match axis {
        'z' => ([c * elev.cos(), s * elev.cos(), elev.sin()], [0.0, 0.0, 1.0]),
        'x' => ([0.0, -c, s], [0.0, s, c]),
        _ => ([c, 0.0, s], [-s, 0.0, c]),
    }
}

/// The frame a shot of a set is written to: beside `out`, its label before the extension.
pub fn shot_path(out: &std::path::Path, label: &str) -> PathBuf {
    let s = out.to_string_lossy();
    match s.len().checked_sub(4).filter(|&i| s.is_char_boundary(i) && s[i..].eq_ignore_ascii_case(".png")) {
        Some(i) => PathBuf::from(format!("{}.{label}.png", &s[..i])),
        None => PathBuf::from(format!("{s}.{label}.png")),
    }
}

/// The shots a set asks for, in flight order: each named view, then each orbit's sweep, every
/// one its own camera and its own frame beside `job.out`. No set is the one job as asked.
pub fn shots(job: &Job, views: &[String], orbits: &[Orbit]) -> Result<Vec<Job>> {
    if views.is_empty() && orbits.is_empty() {
        return Ok(vec![job.clone()]);
    }
    let out = job.out.clone().unwrap_or_default();
    let mut planned = Vec::new();
    for v in views {
        let (cam, up) = preset(v).ok_or_else(|| anyhow::anyhow!("unknown view {v} (have {PRESETS})"))?;
        planned.push((v.clone(), Some(v.clone()), cam, up, None));
    }
    for o in orbits {
        let dir = if o.to >= o.from { 1.0 } else { -1.0 };
        let n = ((o.to - o.from).abs() / o.step + 1e-9).floor() as i64;
        for i in 0..=n {
            let deg = o.from + dir * i as f64 * o.step;
            // A full turn closes on its own start, and that frame is not taken twice.
            if i == n && n > 0 && ((deg - o.from) % 360.0).abs() < 1e-9 {
                break;
            }
            let (cam, up) = orbit_pose(o.axis, deg.to_radians(), o.elev.to_radians());
            let round = |v: [f64; 3]| v.map(|x| format!("{x:.6}").parse::<f64>().unwrap_or(x));
            let label = format!("{}{:03}", o.axis, (((deg % 360.0) + 360.0) % 360.0).round() as i64);
            let text = format!(
                "{} {:.0}°{}",
                o.axis,
                deg,
                if o.elev != 0.0 { format!(" elev {}°", o.elev) } else { String::new() }
            );
            planned.push((label, None, round(cam), round(up), Some(text)));
        }
    }
    Ok(planned
        .into_iter()
        .map(|(label, view, cam, up, orbit)| Job {
            out: Some(shot_path(&out, &label)),
            view,
            cam: Some(cam),
            up: Some(up),
            orbit,
            ..job.clone()
        })
        .collect())
}

/// `*` and `?` globs, matched against a whole body name.
pub fn glob(pattern: &str, name: &str) -> bool {
    fn go(p: &[u8], n: &[u8]) -> bool {
        match (p.first(), n.first()) {
            (None, None) => true,
            (Some(b'*'), _) => go(&p[1..], n) || (!n.is_empty() && go(p, &n[1..])),
            (Some(b'?'), Some(_)) => go(&p[1..], &n[1..]),
            (Some(a), Some(b)) if a == b => go(&p[1..], &n[1..]),
            _ => false,
        }
    }
    go(pattern.as_bytes(), name.as_bytes())
}

pub fn any_glob(patterns: &[String], name: &str) -> bool {
    patterns.iter().any(|p| glob(p, name))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn globs() {
        assert!(glob("enclosure-*", "enclosure-left"));
        assert!(!glob("enclosure-*", "an-enclosure-left"));
        assert!(glob("tee-?-a", "tee-y-a"));
        assert!(glob("*", ""));
        assert!(glob("a*b*c", "aXXbYYc"));
    }

    #[test]
    fn an_orbit_closes_without_a_duplicate_frame() {
        let mut job = Job::default();
        job.step = Some("a.step".into());
        job.out = Some("look/a.png".into());
        let o: Orbit = "z:0,360,90".parse().unwrap();
        let s = shots(&job, &[], &[o]).unwrap();
        let outs: Vec<String> = s.iter().map(|j| j.out.as_ref().unwrap().display().to_string()).collect();
        assert_eq!(outs, ["look/a.z000.png", "look/a.z090.png", "look/a.z180.png", "look/a.z270.png"]);
        assert_eq!(s[1].cam, Some([0.0, 1.0, 0.0]));
        assert_eq!(s[1].orbit.as_deref(), Some("z 90°"));
        let v = shots(&job, &["top".into()], &[]).unwrap();
        assert_eq!(v[0].out.as_ref().unwrap().display().to_string(), "look/a.top.png");
        assert_eq!(v[0].up, Some([0.0, -1.0, 0.0]));
    }

    #[test]
    fn manifest_defaults() {
        let j: Job = serde_json::from_str(r#"{"step": "a.step", "out": "a.png", "solid": true}"#).unwrap();
        assert_eq!(j.size, "1600x1200");
        assert!(j.ground && j.fog && !j.trim);
        assert_eq!(j.cam_up(), ([1.0, -1.0, 1.0], [0.0, 0.0, 1.0]));
        j.check().unwrap();
    }
}
