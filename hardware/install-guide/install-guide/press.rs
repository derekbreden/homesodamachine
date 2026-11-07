//! The booklet's editions. The reading copy is every page at trim size, with its links, outline
//! and page labels. A print order also takes Lulu's two upload files, the full-bleed interior and
//! the outside cover spread flattened to pixels, and the bundle the order is placed from.
use super::book::{BLEED, BLUE, Book, H, W};
use anyhow::{Context, Result, ensure};
use hsm_pages::pdf::{self, Document, Label, Sheet};
use hsm_pages::raster;
use hsm_pages::{Page, RgbImage};
use sha2::{Digest, Sha256};
use std::io::Write;
use std::path::Path;
use std::sync::Arc;
use tiny_skia::{Color, Pixmap, Transform};

const INTERIOR_PAGES: usize = 32;
const AUTHOR: &str = "Derek Bredensteiner";
const SUBJECT: &str = "Home Soda Machine install guide - 9 x 7 inch landscape, 32 interior pages";
/// The resolution the outside cover is flattened at.
const COVER_PPI: f64 = 600.0;
/// The width the site's cover picture is drawn at.
const THUMBNAIL: u32 = 1200;

/// Lulu's perfect-bound spine: interior pages over 444, plus six hundredths of an inch.
fn spine() -> f64 {
    (INTERIOR_PAGES as f64 / 444.0 + 0.06) * 72.0
}

fn cover_size() -> [f64; 2] {
    [2.0 * W + spine() + 2.0 * BLEED, H + 2.0 * BLEED]
}

/// Every page at trim size, front cover to back.
pub fn reading(book: &Book) -> Result<Vec<u8>> {
    ensure!(book.pages.len() == INTERIOR_PAGES + 2, "the booklet has {} pages", book.pages.len());
    let last = book.pages.len() - 1;
    pdf::write(&Document {
        sheets: book
            .pages
            .iter()
            .map(|page| Sheet { page, size: [W, H], trim_inset: 0.0, offset: [0.0, 0.0], links: true })
            .collect(),
        outline: book.outline.clone(),
        labels: vec![
            Label { page: 0, prefix: Some("Cover".into()), decimal_from: None },
            Label { page: 1, prefix: None, decimal_from: Some(1) },
            Label { page: last, prefix: Some("Back cover".into()), decimal_from: None },
        ],
        title: "Home Soda Machine - Install guide".into(),
        author: AUTHOR.into(),
        subject: SUBJECT.into(),
    })
}

/// The site's picture of the front cover.
pub fn thumbnail(front: &Page) -> RgbImage {
    let height = (H * THUMBNAIL as f64 / W).ceil() as u32;
    let mut pixmap = Pixmap::new(THUMBNAIL, height).expect("a cover picture's size");
    pixmap.fill(Color::WHITE);
    raster::draw(&mut pixmap, front, raster::fit([W, H], THUMBNAIL, 0));
    RgbImage::from_pixmap(&pixmap)
}

/// The numbered interior pages, each on a sheet with its bleed.
fn interior(book: &Book) -> Result<Vec<u8>> {
    pdf::write(&Document {
        sheets: book.pages[1..=INTERIOR_PAGES]
            .iter()
            .map(|page| Sheet {
                page,
                size: [W + 2.0 * BLEED, H + 2.0 * BLEED],
                trim_inset: BLEED,
                offset: [BLEED, BLEED],
                links: false,
            })
            .collect(),
        title: "Home Soda Machine - Lulu Small Landscape interior".into(),
        author: AUTHOR.into(),
        subject: SUBJECT.into(),
        ..Document::default()
    })
}

/// The outside cover: back cover, plain spine and front cover on one cobalt ground, in pixels.
fn cover(book: &Book) -> Result<Vec<u8>> {
    let size = cover_size();
    let k = COVER_PPI / 72.0;
    let (cols, rows) = ((size[0] * k).ceil() as u32, (size[1] * k).ceil() as u32);
    let panels = [(book.pages.last().context("a back cover")?, BLEED), (&book.pages[0], W + spine() + BLEED)];
    let [r, g, b] = BLUE.bytes();
    let mut data = Vec::with_capacity((cols * rows * 3) as usize);
    // A band of rows at a time, so the spread is never held at four bytes a pixel.
    let band = 256;
    let mut top = 0;
    while top < rows {
        let h = band.min(rows - top);
        let mut pixmap = Pixmap::new(cols, h).context("a cover band")?;
        pixmap.fill(Color::from_rgba8(r, g, b, 255));
        for (page, x) in panels {
            let place = Transform::from_row(k as f32, 0.0, 0.0, -k as f32, (x * k) as f32, ((size[1] - BLEED) * k - top as f64) as f32);
            raster::draw(&mut pixmap, page, place);
        }
        data.extend(pixmap.data().chunks_exact(4).flat_map(|p| [p[0], p[1], p[2]]));
        top += h;
    }
    let mut sheet = Page::default();
    sheet.picture(Arc::new(RgbImage { width: cols, height: rows, data }), [0.0, 0.0], size);
    pdf::write(&Document {
        sheets: vec![Sheet { page: &sheet, size, trim_inset: BLEED, offset: [0.0, 0.0], links: false }],
        title: "Home Soda Machine - Lulu Small Landscape cover".into(),
        author: AUTHOR.into(),
        subject: SUBJECT.into(),
        ..Document::default()
    })
}

fn write(path: &Path, bytes: &[u8]) -> Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::write(path, bytes).with_context(|| format!("writing {}", path.display()))
}

/// Lulu's upload files beside the booklet, the copies an order is placed from, their checksums
/// and the bundle that carries them with the order instructions.
pub fn order(book: &Book, reading: &[u8], out: &Path) -> Result<()> {
    let interior = interior(book)?;
    let cover = cover(book)?;
    let press = out.join("hardware/install-guide/press");
    write(&press.join("interior.pdf"), &interior)?;
    write(&press.join("cover.pdf"), &cover)?;
    let output = out.join("output/pdf");
    let instructions = std::fs::read(book.root.join("hardware/install-guide/press/ORDER.md"))?;
    let files: [(&str, &[u8]); 4] = [
        ("install-guide-lulu-order.md", &instructions),
        ("install-guide-lulu-interior.pdf", &interior),
        ("install-guide-lulu-cover.pdf", &cover),
        ("install-guide.pdf", reading),
    ];
    let mut sums = String::new();
    for (name, bytes) in files {
        write(&output.join(name), bytes)?;
        sums += &format!("{:x}  {name}\n", Sha256::digest(bytes));
    }
    write(&output.join("install-guide-lulu-SHA256SUMS.txt"), sums.as_bytes())?;
    let mut zip = zip::ZipWriter::new(std::io::Cursor::new(Vec::new()));
    let options = zip::write::SimpleFileOptions::default()
        .compression_method(zip::CompressionMethod::Deflated)
        .last_modified_time(zip::DateTime::from_date_and_time(2000, 1, 1, 0, 0, 0).expect("a fixed date"))
        .unix_permissions(0o644);
    for (name, bytes) in files.into_iter().chain([("install-guide-lulu-SHA256SUMS.txt", sums.as_bytes())]) {
        zip.start_file(name, options)?;
        zip.write_all(bytes)?;
    }
    write(&output.join("install-guide-lulu-order.zip"), &zip.finish()?.into_inner())?;
    Ok(())
}
