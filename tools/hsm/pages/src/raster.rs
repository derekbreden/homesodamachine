//! A page drawn to pixels: shapes and text anti-aliased from their outlines, pictures resampled.
use crate::page::{Cap, Join, Op, Page, Pen, Seg};
use crate::Rgb;
use tiny_skia::{FillRule, FilterQuality, Paint, PathBuilder, Pixmap, PixmapPaint, Stroke, Transform};

fn paint(c: Rgb) -> Paint<'static> {
    let [r, g, b] = c.bytes();
    let mut p = Paint::default();
    p.set_color_rgba8(r, g, b, 255);
    p.anti_alias = true;
    p
}

fn build(segs: &[Seg]) -> Option<tiny_skia::Path> {
    let mut b = PathBuilder::new();
    for s in segs {
        match *s {
            Seg::Move(p) => b.move_to(p[0] as f32, p[1] as f32),
            Seg::Line(p) => b.line_to(p[0] as f32, p[1] as f32),
            Seg::Cubic(a, c, p) => b.cubic_to(a[0] as f32, a[1] as f32, c[0] as f32, c[1] as f32, p[0] as f32, p[1] as f32),
            Seg::Close => b.close(),
        }
    }
    b.finish()
}

fn stroke(p: &Pen) -> Stroke {
    Stroke {
        width: p.width as f32,
        miter_limit: 10.0,
        line_cap: if p.cap == Cap::Round { tiny_skia::LineCap::Round } else { tiny_skia::LineCap::Butt },
        line_join: if p.join == Join::Round { tiny_skia::LineJoin::Round } else { tiny_skia::LineJoin::Miter },
        dash: None,
    }
}

/// The transform that draws a `page_size` page into `pixels`, scaled to fit their width, with
/// its first row `rows_above` rows down the page: a band of the page when the pixmap is shorter.
pub fn fit(page_size: [f64; 2], width: u32, rows_above: u32) -> Transform {
    let s = width as f64 / page_size[0];
    Transform::from_row(s as f32, 0.0, 0.0, -s as f32, 0.0, (page_size[1] * s - rows_above as f64) as f32)
}

/// Draw `page` into `pixmap` through `transform`, from page points to pixels.
pub fn draw(pixmap: &mut Pixmap, page: &Page, transform: Transform) {
    for op in &page.ops {
        match op {
            Op::Shape { path, fill, pen } => {
                let Some(p) = build(&path.segs) else { continue };
                if let Some(f) = fill {
                    pixmap.fill_path(&p, &paint(*f), FillRule::Winding, transform, None);
                }
                if let Some(pen) = pen {
                    pixmap.stroke_path(&p, &paint(pen.color), &stroke(pen), transform, None);
                }
            }
            Op::Text(run) => {
                let mut b = PathBuilder::new();
                let mut x = run.at[0];
                for c in run.text.chars() {
                    let g = run.font.glyph(c);
                    run.font.outline(g, run.size, [x, run.at[1]], &mut b);
                    x += run.font.advance(g) * 0.001 * run.size + run.char_space;
                    if c == ' ' {
                        x += run.word_space;
                    }
                }
                if let Some(p) = b.finish() {
                    pixmap.fill_path(&p, &paint(run.color), FillRule::Winding, transform, None);
                }
            }
            Op::Picture { image, at, size } => {
                let Some(picture) = image.pixmap() else { continue };
                let place = Transform::from_row(
                    (size[0] / image.width as f64) as f32,
                    0.0,
                    0.0,
                    (-size[1] / image.height as f64) as f32,
                    at[0] as f32,
                    (at[1] + size[1]) as f32,
                );
                let paint = PixmapPaint { quality: FilterQuality::Bicubic, ..PixmapPaint::default() };
                pixmap.draw_pixmap(0, 0, picture.as_ref(), &paint, transform.pre_concat(place), None);
            }
        }
    }
}
