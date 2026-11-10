//! Existing toolpath page templates show requested seam and speed readings in a scratch file.
use super::{
    OUTER_WALLS, Placement, Run, Seam, add, enforcer_triangles, layer_range, measure, measure_runs,
    object_in, probe_runs, read_runs, rounded, scale, slice_text, sub, zones,
};
use anyhow::{Context, Result, ensure};
use clap::{Args, Subcommand};
use serde_json::{Value, json};
use std::{
    fs,
    path::{Path, PathBuf},
};

const PAGE_LIMIT: usize = 16_000_000;
const SEAM_TEMPLATE: &str = include_str!("../../../gcode/seam-page.html");
const SPEED_TEMPLATE: &str = include_str!("../../../gcode/speed-page.html");

#[derive(Args)]
pub struct Options {
    #[command(subcommand)]
    mode: Mode,
}
#[derive(Subcommand)]
enum Mode {
    Seams(Seams),
    Speed(Speeds),
}
#[derive(Args)]
struct Page {
    #[arg(long)]
    title: String,
    #[arg(long)]
    lede: Option<String>,
    #[arg(long)]
    out: PathBuf,
}
#[derive(Args)]
struct Seams {
    slice: PathBuf,
    print_json: PathBuf,
    #[arg(long)]
    part: String,
    #[arg(long)]
    project: Option<PathBuf>,
    #[arg(long)]
    compare: Vec<String>,
    #[arg(long, allow_hyphen_values = true)]
    frame_z: Option<String>,
    #[command(flatten)]
    page: Page,
}
#[derive(Args)]
struct Speeds {
    #[arg(required=true,num_args=1..)]
    slices: Vec<String>,
    #[arg(long)]
    object: Option<i64>,
    #[arg(long)]
    mark_layers: Option<String>,
    #[arg(long, default_value = "leftmost", allow_hyphen_values = true)]
    at: String,
    #[arg(long,default_value="iso",value_parser=["left","right","front","back","iso"])]
    view: String,
    #[arg(long)]
    elevation: Option<f64>,
    #[arg(long, default_value = "10-30", allow_hyphen_values = true)]
    scale: String,
    #[command(flatten)]
    page: Page,
}

fn base64(bytes: &[u8]) -> String {
    const TABLE: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let mut text = String::with_capacity(bytes.len().div_ceil(3) * 4);
    for group in bytes.chunks(3) {
        let word = (u32::from(group[0]) << 16)
            | (u32::from(*group.get(1).unwrap_or(&0)) << 8)
            | u32::from(*group.get(2).unwrap_or(&0));
        text.push(TABLE[((word >> 18) & 63) as usize] as char);
        text.push(TABLE[((word >> 12) & 63) as usize] as char);
        text.push(if group.len() > 1 {
            TABLE[((word >> 6) & 63) as usize] as char
        } else {
            '='
        });
        text.push(if group.len() > 2 {
            TABLE[(word & 63) as usize] as char
        } else {
            '='
        });
    }
    text
}
fn floats(points: impl IntoIterator<Item = f64>) -> Result<String> {
    let mut bytes = Vec::new();
    for value in points {
        let value = value as f32;
        ensure!(
            value.is_finite(),
            "toolpath page contains a non-finite coordinate"
        );
        bytes.extend_from_slice(&value.to_le_bytes());
    }
    Ok(base64(&bytes))
}
pub fn walls(runs: &[Run], origin: [f64; 3], with_speed: bool) -> Result<Value> {
    ensure!(
        !runs.is_empty(),
        "the selected slice has no continuous outer-wall runs"
    );
    let mut points = Vec::new();
    let mut offsets = Vec::new();
    let mut heights = Vec::new();
    let mut speeds = Vec::new();
    let mut count = 0usize;
    offsets.extend_from_slice(&0u32.to_le_bytes());
    for run in runs {
        ensure!(
            !run.feed.is_empty() && run.feed.len() + 1 == run.pts.len(),
            "wall run has no complete move metadata"
        );
        for point in &run.pts {
            for (coordinate, base) in point.iter().zip(origin) {
                let value = coordinate - base;
                ensure!(
                    value.is_finite() && value.abs() <= 327.,
                    "the selected toolpaths exceed the page's coordinate range"
                );
                points.extend_from_slice(&((value * 100.).round_ties_even() as i16).to_le_bytes());
            }
        }
        count += run.pts.len();
        offsets.extend_from_slice(
            &u32::try_from(count)
                .context("too many page toolpath points")?
                .to_le_bytes(),
        );
        let height = run.h.filter(|v| *v != 0.).unwrap_or(0.2);
        ensure!(height.is_finite(), "wall run has a non-finite layer height");
        heights.push((height * 100.).round_ties_even() as u8);
        if with_speed {
            for feed in run.feed.iter().chain(run.feed.last()) {
                ensure!(feed.is_finite(), "wall run has a non-finite feed");
                speeds.extend_from_slice(&((feed * 100.).round_ties_even() as u16).to_le_bytes());
            }
        }
    }
    let mut out = json!({"paths":base64(&points),"offsets":base64(&offsets),"heights":base64(&heights),"runs":runs.len(),"points":count});
    if with_speed {
        out["speeds"] = json!(base64(&speeds));
    }
    Ok(out)
}
fn dots(rows: &[Seam], placement: &Placement, main: &Placement, origin: [f64; 3]) -> Vec<[f64; 3]> {
    rows.iter()
        .map(|row| {
            sub(
                main.to_plate(placement.to_cad(add(row.start_plate, scale(row.start_normal, 0.5)))),
                origin,
            )
        })
        .collect()
}
fn escape(text: &str) -> String {
    text.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#x27;")
}
fn render(template: &str, title: &str, lede: &str, data: &Value) -> Result<String> {
    let payload = serde_json::to_string(data)?;
    ensure!(
        !payload.contains("</"),
        "page data would close its script element"
    );
    let page = template
        .replace("{{TITLE}}", &escape(title))
        .replace("{{LEDE}}", &escape(lede))
        .replace("/*DATA*/", &payload);
    ensure!(
        page.len() <= PAGE_LIMIT,
        "toolpath page exceeds the artifact size limit"
    );
    Ok(page)
}
fn save(template: &str, title: &str, lede: &str, data: &Value, out: &Path) -> Result<()> {
    let page = render(template, title, lede, data)?;
    fs::write(out, &page).with_context(|| format!("writing {}", out.display()))?;
    println!("{}  {:.1} MB", out.display(), page.len() as f64 / 1e6);
    Ok(())
}
fn range(text: &str) -> Result<[f64; 2]> {
    let (low, high) = text.split_once('-').context("expected a low-high range")?;
    let (low, high) = (low.parse::<f64>()?, high.parse::<f64>()?);
    ensure!(
        low.is_finite() && high.is_finite() && low < high,
        "range must have finite increasing endpoints"
    );
    Ok([low, high])
}
fn bounds(runs: &[Run]) -> Result<([f64; 3], [f64; 3])> {
    let mut low = [f64::INFINITY; 3];
    let mut high = [f64::NEG_INFINITY; 3];
    for point in runs.iter().flat_map(|run| &run.pts) {
        for i in 0..3 {
            low[i] = low[i].min(point[i]);
            high[i] = high[i].max(point[i]);
        }
    }
    ensure!(
        low.iter().chain(&high).all(|v| v.is_finite()),
        "the selected slice has no wall points"
    );
    Ok((low, high))
}
fn seams(args: Seams) -> Result<i32> {
    let main = Placement::read(&args.print_json, &args.part)?;
    let text = slice_text(&args.slice, 1)?;
    let runs = read_runs(&text, object_in(&text, main.identify_id), &OUTER_WALLS)?;
    let (low, high) = bounds(&runs)?;
    let origin = [main.t[0], (low[1] + high[1]) / 2., 0.];
    let paint = args
        .project
        .as_deref()
        .map(|project| enforcer_triangles(project, &main))
        .transpose()?
        .unwrap_or_default();
    let rows = measure_runs(&runs, &main, [0., 1., 0.], &paint);
    ensure!(!rows.is_empty(), "the selected part has no exterior loops");
    let starts = dots(&rows, &main, &main, origin);
    let mut peaks = Vec::new();
    for zone in zones(&rows, 1.) {
        let i = rows
            .iter()
            .position(|row| row.print_z == zone.peak_print_z_mm)
            .context("peak seam layer")?;
        peaks.push(json!({"at":starts[i].map(|v|rounded(v,3)),"lateral":zone.peak_lateral_mm,"from_z":zone.print_z_mm[0],"to_z":zone.print_z_mm[1],"z":zone.peak_print_z_mm}));
    }
    let toward: [f64; 3] = std::array::from_fn(|i| main.m[1][i]);
    let rear = rows.iter().map(|row| {
        add(
            sub(row.target_plate, origin),
            [0.35 * toward[0], 0.35 * toward[1], 0.],
        )
    });
    let mut data = json!({"source":args.slice,"walls":walls(&runs,origin,false)?,"layers":rows.len(),"seams":{"dots":floats(starts.iter().flatten().copied())?,"lateral":floats(rows.iter().map(|row|row.lateral_mm))?},"rear":floats(rear.flatten())?,"peaks":peaks,"view_azimuth":toward[1].atan2(toward[0]).to_degrees(),"frame_z":args.frame_z.as_deref().map(range).transpose()?,"compare":[]});
    if !paint.is_empty() {
        data["enforcers"] = json!(floats(
            paint.iter().flatten().flat_map(|p| sub(*p, origin))
        )?);
        data["enforcer_triangles"] = json!(paint.len());
    }
    let palette = ["#ff7ad9", "#7fe3ff", "#c7f464", "#ffd166"];
    let mut compare = Vec::new();
    for (i, spec) in args.compare.iter().enumerate() {
        let (label, paths) = spec
            .split_once('=')
            .context("comparison must be label=SLICE:PRINT.json")?;
        let (slice, report) = paths
            .split_once(':')
            .context("comparison must provide a slice and print report")?;
        let other = Placement::read(Path::new(report), &args.part)?;
        let rows = measure(Path::new(slice), &other, None, [0., 1., 0.])?;
        ensure!(
            !rows.is_empty(),
            "comparison {label:?} has no exterior loops"
        );
        let starts = dots(&rows, &other, &main, origin);
        compare.push(json!({"label":label,"color":palette[i%palette.len()],"dots":floats(starts.into_iter().flatten())?,"max_abs_lateral":rounded(rows.iter().map(|row|row.lateral_mm.abs()).fold(0.,f64::max),2)}));
    }
    data["compare"] = json!(compare);
    let lede=args.page.lede.unwrap_or_else(||format!("Every outer wall of {} in {}, drawn from the G-code. Each dot marks the start of a layer's outer loop and is coloured by its distance from the part's centerline.",main.name,args.slice.file_name().unwrap_or_default().to_string_lossy()));
    save(
        SEAM_TEMPLATE,
        &args.page.title,
        &lede,
        &data,
        &args.page.out,
    )?;
    Ok(0)
}
fn speeds(args: Speeds) -> Result<i32> {
    let mut panels = Vec::new();
    let mut origin = None;
    let layers = args.mark_layers.as_deref().map(layer_range).transpose()?;
    for (i, spec) in args.slices.iter().enumerate() {
        let (label, path) = spec.rsplit_once('=').unwrap_or(("", spec));
        let path = Path::new(path);
        let runs = read_runs(&slice_text(path, 1)?, args.object, &OUTER_WALLS)?;
        let (low, high) = bounds(&runs)?;
        let origin = *origin.get_or_insert([(low[0] + high[0]) / 2., (low[1] + high[1]) / 2., 0.]);
        let mut panel = walls(&runs, origin, true)?;
        panel["letter"] = json!(
            char::from_u32(65 + u32::try_from(i)?)
                .context("too many comparison panels")?
                .to_string()
        );
        panel["name"] = json!(if label.is_empty() {
            path.file_name()
                .unwrap_or_default()
                .to_string_lossy()
                .into_owned()
        } else {
            label.into()
        });
        panel["source"] = json!(path);
        if let Some(layers) = &layers {
            let rows = probe_runs(&runs, &args.at, Some(layers))?;
            ensure!(
                !rows.is_empty(),
                "no exterior loops in the marked layers of {}",
                path.display()
            );
            let mid = &rows[rows.len() / 2];
            panel["mark"] = json!({"at":sub(mid.point_plate,origin).map(|v|rounded(v,3)),"layers":[rows[0].layer,rows.last().unwrap().layer],"place":args.at,"speeds":rows.iter().map(|row|row.arriving_mm_s).collect::<Vec<_>>()});
        }
        panels.push(panel);
    }
    ensure!(
        args.elevation.is_none_or(f64::is_finite),
        "view elevation must be finite"
    );
    let lede=args.page.lede.unwrap_or_else(||"Outer walls coloured by the speed each move commands; feed-only lines carry the speed forward.".into());
    let data = json!({"panels":panels,"view":args.view,"elevation":args.elevation,"scale_mm_s":range(&args.scale)?});
    save(
        SPEED_TEMPLATE,
        &args.page.title,
        &lede,
        &data,
        &args.page.out,
    )?;
    Ok(0)
}
pub fn run(options: Options) -> Result<i32> {
    match options.mode {
        Mode::Seams(args) => seams(args),
        Mode::Speed(args) => speeds(args),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn base64_packs_finite_typed_arrays_without_a_runtime() {
        for (bytes, text) in [
            (b"".as_slice(), ""),
            (b"f".as_slice(), "Zg=="),
            (b"fo".as_slice(), "Zm8="),
            (b"foo".as_slice(), "Zm9v"),
            (b"foobar".as_slice(), "Zm9vYmFy"),
        ] {
            assert_eq!(base64(bytes), text);
        }
        assert!(floats([f64::NAN]).is_err());
        assert_eq!(floats([1.]).unwrap(), "AACAPw==");
    }
    #[test]
    fn page_serialization_keeps_point_and_run_alignment() -> Result<()> {
        let run = Run {
            layer: 0,
            z: 0.2,
            h: Some(0.2),
            object: Some(7),
            line: 1,
            end_line: 2,
            pts: vec![[0., 0., 0.], [1., 0., 0.], [1., 1., 0.]],
            feed: vec![10., 20.],
            overhang: vec![false, true],
            lines: vec![1, 2],
        };
        let data = walls(&[run], [0.; 3], true)?;
        assert_eq!(data["runs"], 1);
        assert_eq!(data["points"], 3);
        assert_eq!(data["offsets"], "AAAAAAMAAAA=");
        assert_eq!(data["heights"], "FA==");
        assert_eq!(data["speeds"], "6APQB9AH");
        Ok(())
    }
    #[test]
    fn html_reuses_the_current_templates_and_escapes_prose() -> Result<()> {
        let page = render(
            "<h1>{{TITLE}}</h1><p>{{LEDE}}</p><script>/*DATA*/</script>",
            "<&>\"'",
            "A&B",
            &json!({"x":1}),
        )?;
        assert!(page.contains("&lt;&amp;&gt;&quot;&#x27;"));
        assert!(page.contains("A&amp;B"));
        assert!(page.contains("{\"x\":1}"));
        assert!(render(SEAM_TEMPLATE, "title", "lede", &json!({"path":"</script>"})).is_err());
        assert!(SEAM_TEMPLATE.contains("/*DATA*/") && SPEED_TEMPLATE.contains("/*DATA*/"));
        Ok(())
    }
}
