//! Native manual guides draw authored operation records and schematic illustrations as Letter pages.
use anyhow::{Context, Result, bail, ensure};
use hsm_fabrication_guides::letter::{self, Art, BLUE, Canvas, ICE, INK, curve, p};
use hsm_pages::Rgb;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::path::Path;

#[derive(Deserialize, Serialize)]
#[serde(untagged)]
pub enum Point {
    At([f64; 2]),
    Curve([f64; 6]),
}
#[derive(Deserialize, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum Drawing {
    Shape {
        points: Vec<Point>,
        fill: Option<String>,
        stroke: Option<String>,
        width: f64,
        close: bool,
    },
    Line {
        start: [f64; 2],
        end: [f64; 2],
        color: String,
        width: f64,
        dash: Vec<f64>,
    },
    Rect {
        x: f64,
        y: f64,
        width: f64,
        height: f64,
        fill: Option<String>,
        stroke: Option<String>,
    },
    RoundRect {
        x: f64,
        y: f64,
        width: f64,
        height: f64,
        radius: f64,
        fill: Option<String>,
        stroke: Option<String>,
        line_width: f64,
    },
    Ellipse {
        x: f64,
        y: f64,
        width: f64,
        height: f64,
        fill: Option<String>,
        stroke: Option<String>,
        line_width: f64,
    },
    Label {
        value: String,
        x: f64,
        y: f64,
        size: f64,
        color: String,
        font: String,
        align: String,
    },
    Arrow {
        start: [f64; 2],
        end: [f64; 2],
        color: String,
        width: f64,
        head: f64,
    },
    Dimension {
        start: [f64; 2],
        end: [f64; 2],
        color: String,
    },
    Image {
        path: String,
        x: f64,
        y: f64,
        width: f64,
        height: f64,
    },
    Reference {
        name: String,
    },
}
#[derive(Deserialize)]
struct Illustration {
    origin: [f64; 2],
    scale: f64,
    panel: [f64; 4],
    drawing: Vec<Drawing>,
}
#[derive(Deserialize)]
struct Action {
    title: String,
    body: String,
}
#[derive(Deserialize)]
struct Outcome {
    title: String,
    body: String,
    y: f64,
    tone: String,
}
#[derive(Deserialize)]
struct Page {
    title: String,
    subtitle: String,
    series: String,
    illustration: Illustration,
    actions: Vec<Action>,
    actions_y: f64,
    result: Outcome,
    source: String,
    url: String,
}
#[derive(Deserialize)]
#[serde(rename_all = "lowercase")]
enum Layout {
    Refrigeration,
    Mold,
}
#[derive(Deserialize)]
struct Book {
    layout: Layout,
    title: String,
    subtitle: String,
    sources: Vec<String>,
    extra: Value,
    pages: Vec<Page>,
}

fn color(value: &str) -> Result<Rgb> {
    ensure!(
        value.len() == 7
            && value.starts_with('#')
            && value[1..].bytes().all(|b| b.is_ascii_hexdigit()),
        "guide color {value:?}"
    );
    Ok(Rgb::hex(value))
}
fn optional(value: &Option<String>) -> Result<Option<Rgb>> {
    value.as_deref().map(color).transpose()
}
impl Drawing {
    fn draw(&self, art: &mut Art<'_>) -> Result<()> {
        match self {
            Self::Shape {
                points,
                fill,
                stroke,
                width,
                close,
            } => {
                let points: Vec<_> = points
                    .iter()
                    .map(|point| match point {
                        Point::At([x, y]) => p(*x, *y),
                        Point::Curve([a, b, c, d, x, y]) => curve(*a, *b, *c, *d, *x, *y),
                    })
                    .collect();
                art.shape(&points, optional(fill)?, optional(stroke)?, *width, *close);
            }
            Self::Line {
                start,
                end,
                color: c,
                width,
                dash,
            } => art.line(start[0], start[1], end[0], end[1], color(c)?, *width, dash),
            Self::Rect {
                x,
                y,
                width,
                height,
                fill,
                stroke,
            } => art.shape(
                &[
                    p(*x, *y),
                    p(x + width, *y),
                    p(x + width, y + height),
                    p(*x, y + height),
                ],
                optional(fill)?,
                optional(stroke)?,
                1.5,
                true,
            ),
            Self::RoundRect {
                x,
                y,
                width,
                height,
                radius,
                fill,
                stroke,
                line_width,
            } => {
                let (x0, x1, y0, y1) = (*x, x + width, *y, y + height);
                let r = *radius;
                let t = 0.4472 * r;
                art.shape(
                    &[
                        p(x0 + r, y0),
                        p(x1 - r, y0),
                        curve(x1 - t, y0, x1, y0 + t, x1, y0 + r),
                        p(x1, y1 - r),
                        curve(x1, y1 - t, x1 - t, y1, x1 - r, y1),
                        p(x0 + r, y1),
                        curve(x0 + t, y1, x0, y1 - t, x0, y1 - r),
                        p(x0, y0 + r),
                        curve(x0, y0 + t, x0 + t, y0, x0 + r, y0),
                    ],
                    optional(fill)?,
                    optional(stroke)?,
                    *line_width,
                    true,
                );
            }
            Self::Ellipse {
                x,
                y,
                width,
                height,
                fill,
                stroke,
                line_width,
            } => art.ellipse(
                *x,
                *y,
                *width,
                *height,
                optional(fill)?,
                optional(stroke)?,
                *line_width,
            ),
            Self::Label {
                value,
                x,
                y,
                size,
                color: c,
                font,
                align,
            } => art.label(value, *x, *y, *size, color(c)?, font, align),
            Self::Arrow {
                start,
                end,
                color: c,
                width,
                head,
            } => art.arrow(start[0], start[1], end[0], end[1], color(c)?, *width, *head),
            Self::Dimension {
                start,
                end,
                color: c,
            } => art.dim(start[0], start[1], end[0], end[1], color(c)?),
            Self::Image { .. } | Self::Reference { .. } => {
                bail!("draw image/reference through the guide illustration composer")
            }
        }
        Ok(())
    }
}

pub fn drawing(
    root: &Path,
    canvas: &mut Canvas,
    origin: [f64; 2],
    scale: f64,
    ops: &[Drawing],
    named: &std::collections::BTreeMap<String, Vec<Drawing>>,
) -> Result<()> {
    for op in ops {
        match op {
            Drawing::Image {
                path,
                x,
                y,
                width,
                height,
            } => {
                let image = hsm_pages::RgbaImage::read_png(&std::fs::read(root.join(path))?)?;
                canvas.picture(
                    &image,
                    origin[0] + x * scale,
                    origin[1] + y * scale,
                    width * scale,
                    height * scale,
                    hsm_pages::Rgb::WHITE,
                );
            }
            Drawing::Reference { name } => drawing(
                root,
                canvas,
                origin,
                scale,
                named
                    .get(name)
                    .with_context(|| format!("named guide illustration {name}"))?,
                named,
            )?,
            _ => {
                let mut art = Art::new(canvas, origin[0], origin[1], scale);
                op.draw(&mut art)?;
            }
        }
    }
    Ok(())
}

#[derive(Deserialize)]
struct Rod {
    diameter_mm: f64,
    length_mm: f64,
}
#[derive(Deserialize)]
struct Support {
    guide_diameter_mm: f64,
    guide_open: bool,
}
#[derive(Deserialize)]
struct Socket {
    diameter_mm: f64,
    depth_mm: f64,
}
#[derive(Deserialize)]
struct Volume {
    funnel: f64,
}
#[derive(Deserialize)]
struct MoldDesign {
    finish_allowance_mm: f64,
    rod: Rod,
    rod_support: Support,
    rod_socket: Socket,
    volume_ml: Volume,
}

fn source(root: &Path, id: &str) -> Result<String> {
    let path = root.join("hardware").join(id).join("pages.json");
    let mut text = std::fs::read_to_string(&path)?;
    if id == "mold-guide" {
        let design: MoldDesign = serde_json::from_slice(&std::fs::read(
            root.join("hardware/printed-parts/zone-c/funnel-mold/design.json"),
        )?)?;
        ensure!(
            design.finish_allowance_mm == 0.30
                && design.rod.diameter_mm == 6.
                && design.rod.length_mm == 25.
                && design.rod_support.guide_diameter_mm == 6.4
                && design.rod_socket.diameter_mm == 6.4
                && design.rod_socket.depth_mm == 1.5
                && design.rod_support.guide_open,
            "review mold illustrations against the current finishing allowance and rod datums"
        );
        text = text
            .replace(
                "{{funnel_volume_ml}}",
                &format!("{:.1}", design.volume_ml.funnel),
            )
            .replace(
                "{{silicone_mass_g}}",
                &format!("{:.0}", design.volume_ml.funnel * 1.13),
            );
    }
    if id == "refrigeration-guide" {
        let policy =
            std::fs::read_to_string(root.join("firmware/lib/machine_policy/cold_policy.h"))?;
        for (name, expected) in [
            ("kTankTargetC", 2.),
            ("kHysteresisC", 2.),
            ("kFreezeCutoffC", -8.),
            ("kFreezeRecoverC", -5.),
            ("kMinOffMs", 180000.),
            ("kMinOnMs", 60000.),
            ("kReadingStaleMs", 30000.),
        ] {
            let line = policy
                .lines()
                .find(|line| {
                    line.trim_start().starts_with("constexpr ")
                        && line
                            .split_once('=')
                            .is_some_and(|(left, _)| left.split_whitespace().last() == Some(name))
                })
                .with_context(|| format!("cold policy {name}"))?;
            let actual = line
                .split_once('=')
                .context("cold-policy assignment")?
                .1
                .split(';')
                .next()
                .context("cold-policy literal")?
                .trim()
                .trim_end_matches('f')
                .parse::<f64>()?;
            ensure!(
                actual == expected,
                "review refrigeration guide against cold policy {name}"
            );
        }
    }
    ensure!(
        !text.contains("{{"),
        "unresolved manual guide field: {}",
        path.display()
    );
    Ok(text)
}

pub fn build(root: &Path, id: &str, output: Option<&Path>) -> Result<()> {
    ensure!(
        matches!(id, "refrigeration-guide" | "mold-guide"),
        "unknown operation-record guide {id}"
    );
    let book: Book = serde_json::from_str(&source(root, id)?)?;
    let mut canvas = Canvas::new(root)?;
    for (n, page) in book.pages.iter().enumerate() {
        canvas.begin_page();
        canvas.header(
            n + 1,
            &page.title,
            &page.subtitle,
            book.pages.len(),
            &page.series,
        );
        canvas.outline.push((page.title.clone(), n));
        let illustration = &page.illustration;
        let [x, y, w, h] = illustration.panel;
        canvas.panel(x, y, w, h);
        drawing(
            root,
            &mut canvas,
            illustration.origin,
            illustration.scale,
            &illustration.drawing,
            &Default::default(),
        )?;
        let mut y = page.actions_y;
        for (i, action) in page.actions.iter().enumerate() {
            match book.layout {
                Layout::Refrigeration => {
                    canvas.badge(i + 1, 32., y, &action.title, BLUE, 13.);
                    canvas.paragraph(
                        &action.body,
                        63.,
                        y + 25.,
                        510.,
                        11.25,
                        Some(13.5),
                        INK,
                        Some(41.),
                    );
                    y += 63.;
                }
                Layout::Mold => {
                    canvas.badge(i + 1, 34., y, &action.title, BLUE, 13.);
                    canvas.paragraph(
                        &action.body,
                        65.,
                        y + 26.,
                        493.,
                        11.2,
                        Some(13.6),
                        INK,
                        Some(28.),
                    );
                    y += 59.;
                }
            }
        }
        let result = &page.result;
        let tone = color(&result.tone)?;
        match book.layout {
            Layout::Refrigeration => {
                canvas.box_(
                    32.,
                    result.y,
                    548.,
                    41.,
                    if result.title == "HOLD" {
                        Rgb::hex("#FBEDE5")
                    } else {
                        ICE
                    },
                    None,
                    5.,
                );
                canvas.text(
                    &result.title,
                    43.,
                    result.y + 15.,
                    8.5,
                    "PlexBold",
                    tone,
                    "left",
                );
                canvas.paragraph(
                    &result.body,
                    43.,
                    result.y + 20.,
                    522.,
                    9.7,
                    Some(11.2),
                    INK,
                    Some(22.),
                );
            }
            Layout::Mold => {
                canvas.box_(
                    32.,
                    result.y,
                    547.,
                    61.,
                    if tone == BLUE {
                        ICE
                    } else {
                        Rgb::hex("#FFF0E7")
                    },
                    None,
                    7.,
                );
                canvas.box_(32., result.y, 5., 61., tone, None, 0.);
                canvas.text(
                    &result.title,
                    45.,
                    result.y + 17.,
                    10.4,
                    "PlexBold",
                    tone,
                    "left",
                );
                canvas.paragraph(
                    &result.body,
                    45.,
                    result.y + 25.,
                    518.,
                    10.6,
                    Some(12.6),
                    INK,
                    Some(34.),
                );
            }
        }
        canvas.footer(n + 1, &page.source, &page.url);
        canvas.end_page();
    }
    let mut source_paths: Vec<_> = book
        .sources
        .iter()
        .filter(|p| root.join(p).is_file())
        .map(String::as_str)
        .collect();
    let record_path = format!("hardware/{id}/pages.json");
    source_paths.extend([
        &record_path,
        "tools/assembly-guides/guide.rs",
        "tools/hsm/fabrication-guides/src/letter.rs",
        "hardware/guide-assets/fonts/PlexMono-Regular.ttf",
        "hardware/install-guide/fonts/Plex-Regular.ttf",
        "hardware/install-guide/fonts/Plex-Semibold.ttf",
        "hardware/install-guide/fonts/Plex-Bold.ttf",
    ]);
    let dest = output.unwrap_or(root);
    let directory = format!("hardware/{id}");
    letter::publish(
        root,
        dest,
        &canvas,
        letter::Publication {
            stem: id,
            directory: &directory,
            title: &book.title,
            subtitle: &format!(
                "{} - {} illustrated Letter pages",
                book.subtitle,
                book.pages.len()
            ),
            subject: "Manual illustrated Letter shop instructions",
            sources: &source_paths,
        },
        book.extra,
    )?;
    println!("{id}: {} pages", canvas.pages.len());
    Ok(())
}
