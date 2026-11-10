//! Display partition packagers lay the source RGB565 words out in the firmware's binary formats.
use crate::{Args, root, write};
use anyhow::{Context, Result, bail, ensure};
use std::{
    fs,
    path::{Path, PathBuf},
};

const RENDITIONS: [(&str, usize, usize); 3] =
    [("anchor", 172, 320), ("card", 129, 240), ("tile", 86, 160)];
const FACES: usize = 4;
const LOGO_HEADER: usize = 64;
fn u32le(out: &mut Vec<u8>, n: usize) {
    out.extend_from_slice(&(n as u32).to_le_bytes());
}
fn u16le(out: &mut Vec<u8>, n: usize) {
    out.extend_from_slice(&(n as u16).to_le_bytes());
}

pub fn pixels(path: &Path) -> Result<Vec<u8>> {
    let text = fs::read_to_string(path).with_context(|| format!("read {}", path.display()))?;
    let start = text.find('{').context("image initializer")?;
    let end = text.rfind('}').context("image initializer end")?;
    let raw = text[start + 1..end].as_bytes();
    let mut out = Vec::new();
    let mut i = 0;
    while i + 2 < raw.len() {
        if raw[i] == b'0' && matches!(raw[i + 1], b'x' | b'X') {
            let first = i + 2;
            i = first;
            while i < raw.len() && raw[i].is_ascii_hexdigit() {
                i += 1;
            }
            let value = u16::from_str_radix(std::str::from_utf8(&raw[first..i])?, 16)?;
            out.extend_from_slice(&value.to_le_bytes());
        } else {
            i += 1;
        }
    }
    Ok(out)
}

pub fn make_art(mut args: Args) -> Result<()> {
    let out = args.take(&["-o", "--out"]);
    let quiet = args.flag("--quiet") | args.flag("-q");
    ensure!(
        args.positional(0)? == "enclosure",
        "board must be enclosure"
    );
    let mut image = Vec::new();
    for i in 0..16 {
        let name = format!("anim_{i:02}");
        let data = pixels(&root().join(format!("firmware/src_front/images/{name}.h")))?;
        ensure!(
            data.len() == 360 * 360 * 2,
            "{name}: unexpected pixel count"
        );
        if !quiet {
            println!("{name}: {} bytes", data.len());
        }
        image.extend_from_slice(&data);
    }
    let crc = crc32fast::hash(&image);
    let mut blob = Vec::new();
    for n in [0x4d534148, 1, 16] {
        u32le(&mut blob, n);
    }
    u16le(&mut blob, 360);
    u16le(&mut blob, 360);
    blob.extend_from_slice(&crc.to_le_bytes());
    blob.resize(32, 0);
    blob.extend_from_slice(&image);
    let out = out
        .map(PathBuf::from)
        .unwrap_or_else(|| root().join(".pio/build/esp32s3_front/art.bin"));
    write(&out, &blob)?;
    if !quiet {
        println!(
            "{}: {} bytes, pixel CRC {crc:#010x}",
            out.display(),
            blob.len()
        );
    }
    Ok(())
}

fn constant(path: &Path, name: &str) -> Result<usize> {
    let text = fs::read_to_string(path)?;
    for line in text.lines() {
        if let Some((left, right)) = line.split_once('=') {
            if left.split_whitespace().last() == Some(name) {
                return number(right.split(';').next().unwrap_or(right).trim());
            }
        }
    }
    bail!("no {name} in {}", path.display())
}
fn number(value: &str) -> Result<usize> {
    if let Some(hex) = value
        .strip_prefix("0x")
        .or_else(|| value.strip_prefix("0X"))
    {
        Ok(usize::from_str_radix(hex, 16)?)
    } else {
        Ok(value.parse()?)
    }
}
fn partition(path: &Path) -> Result<(usize, usize)> {
    for line in fs::read_to_string(path)?.lines() {
        let cols: Vec<_> = line
            .split('#')
            .next()
            .unwrap_or("")
            .split(',')
            .map(str::trim)
            .collect();
        if cols.len() >= 5 && cols[0] == "spiffs" {
            return Ok((number(cols[3])?, number(cols[4])?));
        }
    }
    bail!("no spiffs partition in {}", path.display())
}

pub fn make_logos(mut args: Args) -> Result<()> {
    let out = PathBuf::from(args.take(&["-o", "--out"]).context("--out is required")?);
    let store = args.flag("--store");
    let quiet = args.flag("--quiet") | args.flag("-q");
    let table = args
        .take(&["--partitions"])
        .unwrap_or_else(|| "firmware/partitions_s3_faucet.csv".into());
    let mut bundles = Vec::new();
    for face in 0..FACES {
        let mut bundle = Vec::new();
        for (name, w, h) in RENDITIONS {
            let path = root().join(format!("firmware/src_front/images/flavor{face}_{name}.h"));
            let data = pixels(&path)?;
            ensure!(
                data.len() == w * h * 2,
                "{}: unexpected pixel count",
                path.display()
            );
            bundle.extend_from_slice(&data);
        }
        bundles.push(bundle);
    }
    let per = bundles[0].len();
    let mut blob = Vec::new();
    let mut offset = None;
    if store {
        let header = root().join("firmware/lib/image_store/image_store.h");
        let magic = constant(&header, "IMAGE_SLOT_MAGIC")?;
        let format = constant(&header, "IMAGE_SLOT_FORMAT")?;
        let pixels_at = constant(&header, "IMAGE_SLOT_PIXELS_AT")?;
        let sizes = constant(&header, "IMAGE_MAX_SIZES")?;
        let first = constant(
            &root().join("firmware/lib/proto_link/proto_msg.h"),
            "FLAVOR_ART_CUSTOM",
        )?;
        let slot_bytes = (pixels_at + per).div_ceil(4096) * 4096;
        let (base, size) = partition(&root().join(table))?;
        ensure!(
            (first + FACES) * slot_bytes <= size,
            "factory slots exceed spiffs partition"
        );
        offset = Some(base + first * slot_bytes);
        ensure!(
            sizes >= RENDITIONS.len(),
            "renditions exceed the firmware table"
        );
        for (face, bundle) in bundles.iter().enumerate() {
            let mut slot = Vec::new();
            for n in [magic, format, per, crc32fast::hash(bundle) as usize, face] {
                u32le(&mut slot, n);
            }
            slot.push(RENDITIONS.len() as u8);
            slot.resize(28, 0);
            let mut at = 0;
            for (_, w, h) in RENDITIONS {
                u16le(&mut slot, w);
                u16le(&mut slot, h);
                u32le(&mut slot, at);
                at += w * h * 2;
            }
            slot.resize(28 + 8 * sizes, 0);
            ensure!(slot.len() <= pixels_at, "slot header extends into pixels");
            slot.resize(pixels_at, 255);
            slot.extend_from_slice(bundle);
            slot.resize(slot_bytes, 255);
            blob.extend_from_slice(&slot);
        }
    } else {
        for n in [0x53474f4c, 1, FACES, per, RENDITIONS.len()] {
            u32le(&mut blob, n);
        }
        for bundle in &bundles {
            blob.extend_from_slice(&crc32fast::hash(bundle).to_le_bytes());
        }
        blob.resize(LOGO_HEADER, 0);
        for bundle in &bundles {
            blob.extend_from_slice(bundle);
        }
    }
    write(&out, &blob)?;
    if !quiet {
        println!("{}: {} bytes", out.display(), blob.len());
        if let Some(at) = offset {
            println!(
                "esptool --chip esp32s3 --port <port> write-flash {at:#x} {}",
                out.display()
            );
        }
    }
    Ok(())
}
