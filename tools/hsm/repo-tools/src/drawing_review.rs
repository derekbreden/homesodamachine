//! Drawing review renders selected PDF pages and contextual crops with Poppler and records their source hash.
use anyhow::{Context, Result, bail, ensure};
use regex::Regex;
use serde::Serialize;
use std::{
    collections::{BTreeMap, BTreeSet},
    path::{Path, PathBuf},
    process::Command,
};
#[derive(Clone, Debug)]
pub struct Region {
    page: u32,
    name: String,
    box_pt: [f64; 4],
}
impl Region {
    fn parse(value: &str) -> Result<Self> {
        let fields = value.split(',').collect::<Vec<_>>();
        let usage = "use PAGE,NAME,X0,Y0,X1,Y1 with a lowercase name and a positive-area box";
        ensure!(fields.len() == 6, "{usage}");
        let page = fields[0].parse::<u32>().context(usage)?;
        let name = fields[1];
        let values = fields[2..]
            .iter()
            .map(|v| v.parse::<f64>())
            .collect::<std::result::Result<Vec<_>, _>>()
            .context(usage)?;
        let box_pt: [f64; 4] = values.try_into().expect("four coordinates");
        ensure!(
            page > 0
                && Regex::new(r"^[a-z0-9][a-z0-9_-]*$")?.is_match(name)
                && box_pt.iter().all(|v| v.is_finite())
                && box_pt[0] >= 0.
                && box_pt[1] >= 0.
                && box_pt[2] > box_pt[0]
                && box_pt[3] > box_pt[1],
            "{usage}"
        );
        Ok(Self {
            page,
            name: name.into(),
            box_pt,
        })
    }
}
#[derive(Serialize, Debug)]
pub struct Overview {
    page: u32,
    dpi: u32,
    size_pt: [f64; 2],
    image: PathBuf,
}
#[derive(Serialize, Debug)]
pub struct Detail {
    page: u32,
    name: String,
    box_pt: [f64; 4],
    dpi: u32,
    image: PathBuf,
}
#[derive(Serialize, Debug)]
pub struct Review {
    source_pdf: PathBuf,
    source_sha256: String,
    overview: Vec<Overview>,
    details: Vec<Detail>,
}
fn run(command: &str, args: &[String]) -> Result<String> {
    let output = Command::new(command)
        .args(args)
        .output()
        .with_context(|| format!("Poppler command is unavailable: {command}"))?;
    ensure!(
        output.status.success(),
        "{command}: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    Ok(String::from_utf8(output.stdout)?)
}
fn page_count(info: &str) -> Result<u32> {
    let pattern = Regex::new(r"(?m)^Pages:\s+(\d+)")?;
    Ok(pattern
        .captures(info)
        .context("pdfinfo did not return the page count")?[1]
        .parse()?)
}
fn page_sizes(info: &str) -> Result<BTreeMap<u32, [f64; 2]>> {
    let number = r"(-?\d+(?:\.\d+)?)";
    let boxes = Regex::new(&format!(
        r"(?m)^Page\s+(\d+)\s+CropBox:\s+{number}\s+{number}\s+{number}\s+{number}"
    ))?;
    let mut sizes = BTreeMap::new();
    for m in boxes.captures_iter(info) {
        let n = m[1].parse::<u32>()?;
        let c = (2..=5)
            .map(|i| m[i].parse::<f64>())
            .collect::<std::result::Result<Vec<_>, _>>()?;
        sizes.insert(n, [c[2] - c[0], c[3] - c[1]]);
    }
    for m in Regex::new(r"(?m)^Page\s+(\d+)\s+rot:\s+(-?\d+)")?.captures_iter(info) {
        if m[2].parse::<i32>()?.rem_euclid(180) == 90 {
            if let Some(size) = sizes.get_mut(&m[1].parse::<u32>()?) {
                size.swap(0, 1);
            }
        }
    }
    Ok(sizes)
}
fn pixel_crop(box_pt: [f64; 4], height: f64, dpi: u32) -> [i64; 4] {
    let scale = dpi as f64 / 72.;
    let [x0, y0, x1, y1] = box_pt;
    let left = (x0 * scale).floor() as i64;
    let top = ((height - y1) * scale).floor() as i64;
    [
        left,
        top,
        (x1 * scale).ceil() as i64 - left,
        ((height - y0) * scale).ceil() as i64 - top,
    ]
}
fn render(
    pdf: &Path,
    page: u32,
    dpi: u32,
    prefix: &Path,
    crop: Option<[i64; 4]>,
) -> Result<PathBuf> {
    let mut args = vec![
        "-f".into(),
        page.to_string(),
        "-l".into(),
        page.to_string(),
        "-cropbox".into(),
        "-r".into(),
        dpi.to_string(),
        "-png".into(),
        "-singlefile".into(),
    ];
    if let Some(crop) = crop {
        for (flag, value) in ["-x", "-y", "-W", "-H"].into_iter().zip(crop) {
            args.push(flag.into());
            args.push(value.to_string());
        }
    }
    args.push(pdf.to_string_lossy().into_owned());
    args.push(prefix.to_string_lossy().into_owned());
    run("pdftoppm", &args)?;
    Ok(prefix.with_extension("png"))
}
pub fn review(
    pdf: &Path,
    output: &Path,
    pages: &BTreeSet<u32>,
    regions: &[Region],
    overview_dpi: u32,
    detail_dpi: u32,
) -> Result<Review> {
    ensure!(
        overview_dpi > 0 && detail_dpi > 0,
        "rendering DPI must be positive"
    );
    let pdf = std::fs::canonicalize(pdf)
        .with_context(|| format!("PDF does not exist: {}", pdf.display()))?;
    ensure!(pdf.is_file(), "PDF does not exist: {}", pdf.display());
    let count = page_count(&run("pdfinfo", &[pdf.to_string_lossy().into_owned()])?)?;
    let pages = if pages.is_empty() {
        (1..=count).collect()
    } else {
        pages.clone()
    };
    ensure!(
        pages.iter().all(|p| *p > 0 && *p <= count),
        "pages must be between 1 and {count}"
    );
    let sizes = page_sizes(&run(
        "pdfinfo",
        &[
            "-f".into(),
            "1".into(),
            "-l".into(),
            count.to_string(),
            "-box".into(),
            pdf.to_string_lossy().into_owned(),
        ],
    )?)?;
    ensure!(
        pages.iter().all(|p| sizes.contains_key(p)),
        "pdfinfo did not return the selected pages' crop boxes"
    );
    let mut names = BTreeSet::new();
    for region in regions {
        ensure!(
            pages.contains(&region.page),
            "region {} belongs to an unselected page: {}",
            region.name,
            region.page
        );
        ensure!(
            names.insert((region.page, &region.name)),
            "duplicate region name on page {}: {}",
            region.page,
            region.name
        );
        let [width, height] = sizes[&region.page];
        ensure!(
            region.box_pt[2] <= width && region.box_pt[3] <= height,
            "region {} exceeds page {} ({width} x {height} pt)",
            region.name,
            region.page
        );
    }
    std::fs::create_dir_all(output)?;
    let output = std::fs::canonicalize(output)?;
    let mut review = Review {
        source_sha256: hsm_build_data::payload::digest(&pdf)?,
        source_pdf: pdf.clone(),
        overview: Vec::new(),
        details: Vec::new(),
    };
    for page in pages {
        let image = render(
            &pdf,
            page,
            overview_dpi,
            &output.join(format!("page-{page:02}-overview")),
            None,
        )?;
        review.overview.push(Overview {
            page,
            dpi: overview_dpi,
            size_pt: sizes[&page],
            image,
        });
    }
    for region in regions {
        let crop = pixel_crop(region.box_pt, sizes[&region.page][1], detail_dpi);
        let image = render(
            &pdf,
            region.page,
            detail_dpi,
            &output.join(format!("page-{:02}-{}", region.page, region.name)),
            Some(crop),
        )?;
        review.details.push(Detail {
            page: region.page,
            name: region.name.clone(),
            box_pt: region.box_pt,
            dpi: detail_dpi,
            image,
        });
    }
    crate::write_json(&output.join("review-images.json"), &review)?;
    Ok(review)
}
pub fn cli(_root: &Path, args: &[String]) -> Result<i32> {
    let (mut pdf, mut output) = (None, None);
    let mut pages = BTreeSet::new();
    let mut regions = Vec::new();
    let (mut overview_dpi, mut detail_dpi) = (150, 240);
    let mut it = args.iter();
    while let Some(arg) = it.next() {
        match arg.as_str() {
            "--output-dir" => {
                output = Some(PathBuf::from(
                    it.next().context("--output-dir needs a path")?,
                ))
            }
            "--page" => {
                pages.insert(
                    it.next()
                        .context("--page needs a page number")?
                        .parse::<u32>()?,
                );
            }
            "--region" => regions.push(Region::parse(
                it.next().context("--region needs PAGE,NAME,X0,Y0,X1,Y1")?,
            )?),
            "--overview-dpi" => {
                overview_dpi = it
                    .next()
                    .context("--overview-dpi needs a resolution")?
                    .parse()?
            }
            "--detail-dpi" => {
                detail_dpi = it
                    .next()
                    .context("--detail-dpi needs a resolution")?
                    .parse()?
            }
            "--help" | "-h" => {
                println!(
                    "repo-tools drawing-review PDF --output-dir PATH [--page N]... [--region PAGE,NAME,X0,Y0,X1,Y1]... [--overview-dpi DPI] [--detail-dpi DPI]\nRenders overviews and contextual crops with Poppler and writes review-images.json. Region points start at the bottom-left of the displayed CropBox after rotation. The source PDF is read only."
                );
                return Ok(0);
            }
            other if !other.starts_with('-') && pdf.is_none() => pdf = Some(PathBuf::from(other)),
            other => bail!("unknown drawing-review argument {other}"),
        }
    }
    let review = review(
        &pdf.context("drawing-review needs a PDF")?,
        &output.context("--output-dir is required")?,
        &pages,
        &regions,
        overview_dpi,
        detail_dpi,
    )?;
    println!("{}", serde_json::to_string_pretty(&review)?);
    Ok(0)
}
#[cfg(test)]
mod tests {
    use super::*;
    fn dimensions(path: &Path) -> [u32; 2] {
        let bytes = std::fs::read(path).unwrap();
        [
            u32::from_be_bytes(bytes[16..20].try_into().unwrap()),
            u32::from_be_bytes(bytes[20..24].try_into().unwrap()),
        ]
    }
    #[test]
    fn poppler_cropbox_rotation_and_fractional_pixel_edges() {
        let root = std::env::temp_dir().join(format!(
            "hsm-drawing-review-{}-{}",
            std::process::id(),
            crate::now().to_bits()
        ));
        std::fs::create_dir_all(&root).unwrap();
        let pdf = root.join("fixture.pdf");
        std::fs::write(&pdf, include_bytes!("../tests/fixtures/drawing-review.pdf")).unwrap();
        let before = std::fs::read(&pdf).unwrap();
        let regions = (1..=4)
            .map(|n| Region::parse(&format!("{n},context,8.25,12.75,48.5,60.5")).unwrap())
            .collect::<Vec<_>>();
        let review = review(
            &pdf,
            &root.join("images"),
            &BTreeSet::new(),
            &regions,
            72,
            144,
        )
        .unwrap();
        for (page, size) in
            review
                .overview
                .iter()
                .zip([[200., 100.], [100., 200.], [200., 100.], [100., 200.]])
        {
            assert_eq!(page.size_pt, size);
            assert_eq!(dimensions(&page.image), size.map(|v| v as u32));
        }
        assert_eq!(pixel_crop(regions[0].box_pt, 100., 144), [16, 79, 81, 96]);
        assert_eq!(pixel_crop(regions[0].box_pt, 200., 144), [16, 279, 81, 96]);
        for detail in &review.details {
            assert_eq!(dimensions(&detail.image), [81, 96]);
        }
        assert_eq!(std::fs::read(pdf).unwrap(), before);
        std::fs::remove_dir_all(root).unwrap();
    }
}
