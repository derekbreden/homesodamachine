//! Manual shop books and their vector figures share typed page records and named illustrations.
use crate::paper::{self, Drawing, Point};
use anyhow::{Context, Result, bail, ensure};
use hsm_fabrication_guides::letter::{self, Canvas};
use hsm_pages::{Rgb, RgbaImage, Target};
use serde::Deserialize;
use serde_json::Value;
use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::Path;

#[derive(Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
enum Content {
    Box {
        x: f64,
        y: f64,
        width: f64,
        height: f64,
        fill: String,
        stroke: Option<String>,
        radius: f64,
    },
    Text {
        value: String,
        x: f64,
        y: f64,
        size: f64,
        font: String,
        color: String,
        align: String,
    },
    Paragraph {
        value: String,
        x: f64,
        y: f64,
        width: f64,
        size: f64,
        leading: f64,
        color: String,
        max_height: Option<f64>,
    },
    Picture {
        path: String,
        x: f64,
        y: f64,
        width: f64,
        height: f64,
    },
    Illustration {
        origin: [f64; 2],
        scale: f64,
        drawing: Vec<Drawing>,
    },
    PageLink {
        page: usize,
        rect: [f64; 4],
    },
    UriLink {
        url: String,
        rect: [f64; 4],
    },
}
#[derive(Deserialize)]
struct Page {
    title: String,
    subtitle: String,
    series: String,
    ops: Vec<Content>,
    source: String,
    url: String,
}
#[derive(Deserialize)]
struct SvgFigure {
    name: String,
    title: String,
    description: String,
    size: [u32; 2],
    view: [f64; 2],
}
#[derive(Deserialize)]
struct Book {
    title: String,
    subtitle: String,
    sources: Vec<String>,
    extra: Value,
    #[serde(default)]
    drawings: BTreeMap<String, Vec<Drawing>>,
    #[serde(default)]
    svg_figures: Vec<SvgFigure>,
    pages: Vec<Page>,
}

fn color(text: &str) -> Result<Rgb> {
    ensure!(
        text.len() == 7
            && text.starts_with('#')
            && text[1..].bytes().all(|v| v.is_ascii_hexdigit()),
        "faucet guide color {text}"
    );
    Ok(Rgb::hex(text))
}
fn text(text: &str) -> String {
    text.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}
fn paint(color: &Option<String>) -> &str {
    color.as_deref().unwrap_or("none")
}
fn general(value: f64) -> String {
    hsm_documents::format_number(value, "g").expect("general format")
}

fn svg(ops: &[Drawing], named: &BTreeMap<String, Vec<Drawing>>, out: &mut String) -> Result<()> {
    for op in ops {
        match op {
            Drawing::Shape {
                points,
                fill,
                stroke,
                width,
                close,
            } => {
                let mut path = String::new();
                for (i, point) in points.iter().enumerate() {
                    match point {
                        Point::At([x, y]) => write!(
                            path,
                            "{}{} {} ",
                            if i == 0 { "M" } else { "L" },
                            general(*x),
                            general(*y)
                        )?,
                        Point::Curve([a, b, c, d, x, y]) => write!(
                            path,
                            "C{} {} {} {} {} {} ",
                            general(*a),
                            general(*b),
                            general(*c),
                            general(*d),
                            general(*x),
                            general(*y)
                        )?,
                    }
                }
                if *close {
                    path.push('Z');
                }
                writeln!(
                    out,
                    "<path d=\"{path}\" fill=\"{}\" stroke=\"{}\" stroke-width=\"{}\"/>",
                    paint(fill),
                    paint(stroke),
                    general(*width)
                )?;
            }
            Drawing::Line {
                start,
                end,
                color,
                width,
                dash,
            } => {
                let d = if dash.is_empty() {
                    String::new()
                } else {
                    format!(
                        " stroke-dasharray=\"{}\"",
                        dash.iter()
                            .map(|v| general(*v))
                            .collect::<Vec<_>>()
                            .join(" ")
                    )
                };
                writeln!(
                    out,
                    "<line x1=\"{}\" y1=\"{}\" x2=\"{}\" y2=\"{}\" stroke=\"{color}\" stroke-width=\"{}\"{d}/>",
                    general(start[0]),
                    general(start[1]),
                    general(end[0]),
                    general(end[1]),
                    general(*width)
                )?;
            }
            Drawing::Rect {
                x,
                y,
                width,
                height,
                fill,
                stroke,
            } => writeln!(
                out,
                "<rect x=\"{}\" y=\"{}\" width=\"{}\" height=\"{}\" fill=\"{}\" stroke=\"{}\" stroke-width=\"1.5\"/>",
                general(*x),
                general(*y),
                general(*width),
                general(*height),
                paint(fill),
                paint(stroke)
            )?,
            Drawing::RoundRect {
                x,
                y,
                width,
                height,
                radius,
                fill,
                stroke,
                line_width,
            } => writeln!(
                out,
                "<rect x=\"{}\" y=\"{}\" width=\"{}\" height=\"{}\" rx=\"{}\" fill=\"{}\" stroke=\"{}\" stroke-width=\"{}\"/>",
                general(*x),
                general(*y),
                general(*width),
                general(*height),
                general(*radius),
                paint(fill),
                paint(stroke),
                general(*line_width)
            )?,
            Drawing::Ellipse {
                x,
                y,
                width,
                height,
                fill,
                stroke,
                line_width,
            } => writeln!(
                out,
                "<ellipse cx=\"{}\" cy=\"{}\" rx=\"{}\" ry=\"{}\" fill=\"{}\" stroke=\"{}\" stroke-width=\"{}\"/>",
                general(x + width / 2.),
                general(y + height / 2.),
                general(width / 2.),
                general(height / 2.),
                paint(fill),
                paint(stroke),
                general(*line_width)
            )?,
            Drawing::Label {
                value,
                x,
                y,
                size,
                color,
                font,
                align,
            } => {
                let anchor = match align.as_str() {
                    "center" => "middle",
                    "right" => "end",
                    _ => "start",
                };
                let weight = match font.as_str() {
                    "Plex" => "400",
                    "PlexBold" => "700",
                    _ => "600",
                };
                writeln!(
                    out,
                    "<text x=\"{}\" y=\"{}\" font-size=\"{}\" font-weight=\"{weight}\" text-anchor=\"{anchor}\" fill=\"{color}\">{}</text>",
                    general(*x),
                    general(*y),
                    general(*size),
                    text(value)
                )?;
            }
            Drawing::Arrow {
                start,
                end,
                color,
                width,
                head,
            } => {
                let angle = (end[1] - start[1]).atan2(end[0] - start[0]);
                let path = [
                    Point::At(*end),
                    Point::At([
                        end[0] - head * (angle - 0.5).cos(),
                        end[1] - head * (angle - 0.5).sin(),
                    ]),
                    Point::At([
                        end[0] - head * (angle + 0.5).cos(),
                        end[1] - head * (angle + 0.5).sin(),
                    ]),
                ];
                svg(
                    &[
                        Drawing::Line {
                            start: *start,
                            end: *end,
                            color: color.clone(),
                            width: *width,
                            dash: Vec::new(),
                        },
                        Drawing::Shape {
                            points: Vec::from(path),
                            fill: Some(color.clone()),
                            stroke: None,
                            width: 1.5,
                            close: true,
                        },
                    ],
                    named,
                    out,
                )?;
            }
            Drawing::Dimension { start, end, color } => {
                let mut lines = vec![Drawing::Line {
                    start: *start,
                    end: *end,
                    color: color.clone(),
                    width: 0.8,
                    dash: Vec::new(),
                }];
                for point in [*start, *end] {
                    let (a, b) = if start[0] == end[0] {
                        ([point[0] - 4., point[1]], [point[0] + 4., point[1]])
                    } else {
                        ([point[0], point[1] - 4.], [point[0], point[1] + 4.])
                    };
                    lines.push(Drawing::Line {
                        start: a,
                        end: b,
                        color: color.clone(),
                        width: 1.,
                        dash: Vec::new(),
                    });
                }
                svg(&lines, named, out)?;
            }
            Drawing::Reference { name } => svg(
                named
                    .get(name)
                    .with_context(|| format!("SVG illustration {name}"))?,
                named,
                out,
            )?,
            Drawing::Image { .. } => bail!("wiring vector figure contains a raster image"),
        }
    }
    Ok(())
}

pub fn build(root: &Path, id: &str, source: &str, output: Option<&Path>) -> Result<()> {
    let book: Book = serde_json::from_str(source)?;
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
        canvas.outline.push((page.title.replace('\n', " "), n));
        for op in &page.ops {
            match op {
                Content::Box {
                    x,
                    y,
                    width,
                    height,
                    fill,
                    stroke,
                    radius,
                } => canvas.box_(
                    *x,
                    *y,
                    *width,
                    *height,
                    color(fill)?,
                    stroke.as_deref().map(color).transpose()?,
                    *radius,
                ),
                Content::Text {
                    value,
                    x,
                    y,
                    size,
                    font,
                    color: c,
                    align,
                } => canvas.text(value, *x, *y, *size, font, color(c)?, align),
                Content::Paragraph {
                    value,
                    x,
                    y,
                    width,
                    size,
                    leading,
                    color: c,
                    max_height,
                } => {
                    canvas.paragraph(
                        value,
                        *x,
                        *y,
                        *width,
                        *size,
                        Some(*leading),
                        color(c)?,
                        *max_height,
                    );
                }
                Content::Picture {
                    path,
                    x,
                    y,
                    width,
                    height,
                } => {
                    let image = RgbaImage::read_png(&std::fs::read(root.join(path))?)?;
                    canvas.picture(&image, *x, *y, *width, *height, Rgb::WHITE);
                }
                Content::Illustration {
                    origin,
                    scale,
                    drawing,
                } => paper::drawing(root, &mut canvas, *origin, *scale, drawing, &book.drawings)?,
                Content::PageLink { page, rect } => {
                    let scale = letter::CONTENT_SCALE;
                    let at = |x: f64, y: f64| {
                        [
                            letter::W * (1. - scale) / 2. + x * scale,
                            letter::H * (1. - scale) / 2. + y * scale,
                        ]
                    };
                    let a = at(rect[0], rect[1]);
                    let b = at(rect[2], rect[3]);
                    canvas
                        .page
                        .link([a[0], a[1], b[0], b[1]], Target::Page(*page));
                }
                Content::UriLink { url, rect } => canvas.link(url, *rect),
            }
        }
        canvas.footer(n + 1, &page.source, &page.url);
        canvas.end_page();
    }
    let dest = output.unwrap_or(root);
    let relative_directory = format!("hardware/{id}");
    let directory = dest.join(&relative_directory);
    for figure in &book.svg_figures {
        let mut content = format!(
            "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{}\" height=\"{}\" viewBox=\"0 0 {} {}\" role=\"img\" aria-labelledby=\"title desc\">\n<title id=\"title\">{}</title>\n<desc id=\"desc\">{}</desc>\n<rect width=\"{}\" height=\"{}\" fill=\"#FFFFFF\"/>\n<g font-family=\"IBM Plex Sans, Arial, sans-serif\" stroke-linejoin=\"round\" stroke-linecap=\"round\">\n",
            figure.size[0],
            figure.size[1],
            general(figure.view[0]),
            general(figure.view[1]),
            text(&figure.title),
            text(&figure.description),
            general(figure.view[0]),
            general(figure.view[1])
        );
        svg(
            book.drawings
                .get(&figure.name)
                .context("named wiring drawing")?,
            &book.drawings,
            &mut content,
        )?;
        content.push_str("</g>\n</svg>\n");
        crate::write(
            &directory.join(format!("{}.svg", figure.name)),
            content.as_bytes(),
        )?;
    }
    let mut sources: Vec<_> = book
        .sources
        .iter()
        .filter(|p| root.join(p).is_file())
        .map(String::as_str)
        .collect();
    let record_path = format!("hardware/{id}/pages.json");
    let author_path = format!("tools/{id}/book.rs");
    sources.extend([
        record_path.as_str(),
        author_path.as_str(),
        "tools/assembly-guides/book.rs",
        "tools/assembly-guides/guide.rs",
        "tools/hsm/fabrication-guides/src/letter.rs",
        "tools/hsm/fabrication-guides/src/cuts.rs",
        "hardware/install-guide/fonts/Plex-Regular.ttf",
        "hardware/install-guide/fonts/Plex-Semibold.ttf",
        "hardware/install-guide/fonts/Plex-Bold.ttf",
        "hardware/guide-assets/fonts/PlexMono-Regular.ttf",
    ]);
    let receipt = letter::publish(
        root,
        dest,
        &canvas,
        letter::Publication {
            stem: id,
            directory: &relative_directory,
            title: &book.title,
            subtitle: &format!(
                "{}; {} illustrated Letter pages",
                book.subtitle,
                book.pages.len()
            ),
            subject: "Manual illustrated Letter shop instructions",
            sources: &sources,
        },
        book.extra,
    )?;
    if id == "water-inlet-jet-guide" {
        crate::write_json(&directory.join("guide-sources.json"), &receipt)?;
    }
    println!("{id}: {} pages", book.pages.len());
    Ok(())
}
