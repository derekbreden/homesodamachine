//! PNG artwork is packed directly into the display firmware's existing binary formats.
use crate::{Args, root, write};
use anyhow::{Context, Result, bail, ensure};
use hsm_display_assets::{
    self as assets, ANIMATION_FRAMES, ANIMATION_HEIGHT, ANIMATION_WIDTH, FACTORY_FLAVORS, Rendition,
};
use std::{
    fs,
    path::{Path, PathBuf},
};

const LOGO_HEADER: usize = 64;
const IMAGE_SLOT_MAGIC: usize = 0x494d4753;
const IMAGE_SLOT_FORMAT: usize = 2;
const IMAGE_MAX_SIZES: usize = 8;
const IMAGE_SLOT_PIXELS_AT: usize = 128;
const FIRST_FACTORY_SLOT: usize = 4;
fn u32le(out: &mut Vec<u8>, n: usize) {
    out.extend_from_slice(&(n as u32).to_le_bytes());
}
fn u16le(out: &mut Vec<u8>, n: usize) {
    out.extend_from_slice(&(n as u16).to_le_bytes());
}

pub fn make_art(mut args: Args) -> Result<()> {
    let out = args.take(&["-o", "--out"]);
    let quiet = args.flag("--quiet") | args.flag("-q");
    ensure!(
        args.positional(0)? == "enclosure",
        "board must be enclosure"
    );
    let image = assets::animation_frames(&root())?.concat();
    let crc = crc32fast::hash(&image);
    let mut blob = Vec::new();
    for n in [0x4d534148, 1, ANIMATION_FRAMES] {
        u32le(&mut blob, n);
    }
    u16le(&mut blob, ANIMATION_WIDTH);
    u16le(&mut blob, ANIMATION_HEIGHT);
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
    let bundles = (0..FACTORY_FLAVORS)
        .map(|face| assets::factory_bundle(&root(), face))
        .collect::<Result<Vec<_>>>()?;
    let per = bundles[0].len();
    let mut blob = Vec::new();
    let mut offset = None;
    if store {
        let slot_bytes = (IMAGE_SLOT_PIXELS_AT + per).div_ceil(4096) * 4096;
        let (base, size) = partition(&root().join(table))?;
        ensure!(
            (FIRST_FACTORY_SLOT + FACTORY_FLAVORS) * slot_bytes <= size,
            "factory slots exceed spiffs partition"
        );
        offset = Some(base + FIRST_FACTORY_SLOT * slot_bytes);
        for (face, bundle) in bundles.iter().enumerate() {
            let mut slot = Vec::new();
            for n in [
                IMAGE_SLOT_MAGIC,
                IMAGE_SLOT_FORMAT,
                per,
                crc32fast::hash(bundle) as usize,
                face,
            ] {
                u32le(&mut slot, n);
            }
            slot.push(Rendition::ALL.len() as u8);
            slot.resize(28, 0);
            let mut at = 0;
            for rendition in Rendition::ALL {
                let (w, h) = rendition.dimensions();
                u16le(&mut slot, w);
                u16le(&mut slot, h);
                u32le(&mut slot, at);
                at += w * h * 2;
            }
            slot.resize(28 + 8 * IMAGE_MAX_SIZES, 0);
            ensure!(
                slot.len() <= IMAGE_SLOT_PIXELS_AT,
                "slot header extends into pixels"
            );
            slot.resize(IMAGE_SLOT_PIXELS_AT, 255);
            slot.extend_from_slice(bundle);
            slot.resize(slot_bytes, 255);
            blob.extend_from_slice(&slot);
        }
    } else {
        for n in [0x53474f4c, 1, FACTORY_FLAVORS, per, Rendition::ALL.len()] {
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
