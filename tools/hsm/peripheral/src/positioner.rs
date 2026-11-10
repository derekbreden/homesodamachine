//! Positioner release tools bind motion geometry and pack or verify the RP2040 flash image.
use crate::{flag, read_json, sha, validate_args, write};
use anyhow::{bail, ensure, Context, Result};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{collections::BTreeMap, fs, path::Path, process::Command};

const FIRMWARE: &str = "firmware/src_pgfun_positioner";
const MECHANICAL: &str = "hardware/printed-parts/fixtures/pgfun-positioner";
const BLOCK: usize = 512;
const PAYLOAD: usize = 256;
const UF2_MAGIC: [u32; 3] = [0x0A324655, 0x9E5D5157, 0x0AB16F30];
const FAMILY: u32 = 0xE48BFF56;
const FLASH: u32 = 0x10000000;

#[derive(Deserialize)]
struct Geometry {
    motion: Value,
    sha256: String,
}

fn expected(root: &Path) -> Result<String> {
    let record: Geometry = serde_json::from_value(read_json(
        &root.join(MECHANICAL).join("motion-geometry.json"),
    )?)?;
    let canonical = serde_json::to_vec(&record.motion)?;
    let digest = sha(&canonical);
    let design = read_json(&root.join(MECHANICAL).join("design.json"))?;
    ensure!(
        digest == record.sha256,
        "motion geometry digest differs; rebuild mechanical outputs before generating firmware"
    );
    for (key, value) in design
        .as_object()
        .context("mechanical design is not an object")?
    {
        ensure!(
            record.motion.get(key) == Some(value),
            "motion geometry {key} differs; rebuild mechanical outputs before generating firmware"
        );
    }
    let sources = record.motion["mechanical_sources"]
        .as_object()
        .context("motion geometry has no mechanical sources")?;
    ensure!(
        !sources.is_empty(),
        "motion geometry has no mechanical sources"
    );
    for (path, expected) in sources {
        ensure!(
            sha(&fs::read(root.join(path))?)
                == expected
                    .as_str()
                    .context("mechanical source digest is not a string")?,
            "mechanical source changed: {path}"
        );
    }
    let g = &record.motion;
    let integer = |key: &str| {
        g[key]
            .as_i64()
            .with_context(|| format!("motion geometry {key} is not an integer"))
    };
    let counts = integer("reduction")?
        .checked_mul(integer("motor_full_steps")?)
        .and_then(|v| v.checked_mul(integer("external_microsteps").ok()?))
        .context("count geometry overflows")?;
    let limit = (counts as f64
        * g["soft_limit_deg"]
            .as_f64()
            .context("soft limit is not numeric")?
        / 360.0) as i64;
    Ok(format!(
        "#pragma once\n#include <array>\n#include <cstdint>\nnamespace pgfun_positioner {{\nconstexpr int32_t kCountsPerRev = {counts};\nconstexpr std::array<int32_t, 2> kMinCount = {{-{limit}, -{limit}}};\nconstexpr std::array<int32_t, 2> kMaxCount = {{{limit}, {limit}}};\nconstexpr const char *kGeometrySha256 = \"{digest}\";\n}}\n"
    ))
}

pub fn geometry(root: &Path, args: &[String]) -> Result<()> {
    ensure!(
        validate_args(args, &["--check"], &[])?.is_empty(),
        "positioner-geometry accepts --check"
    );
    let expected = expected(root)?;
    let path = root.join(FIRMWARE).join("geometry_generated.h");
    if flag(args, "--check") {
        ensure!(
            fs::read(&path).is_ok_and(|v| v == expected.as_bytes()),
            "generated geometry is stale"
        );
    } else {
        write(&path, expected.as_bytes())?;
    }
    Ok(())
}

pub fn uf2(args: &[String]) -> Result<()> {
    ensure!(args.len() == 2, "uf2 SOURCE.bin DESTINATION.uf2");
    let data = fs::read(&args[0])?;
    let packed = pack(&data)?;
    write(Path::new(&args[1]), &packed)?;
    println!(
        "{}",
        json!({"binary_bytes": data.len(), "uf2_blocks": packed.len()/BLOCK, "uf2_bytes": packed.len()})
    );
    Ok(())
}

pub fn pico_pad_checksum(args: &[String]) -> Result<()> {
    use std::fmt::Write as _;
    let mut positional = Vec::new();
    let (mut pad, mut seed) = (256_usize, 0_u32);
    let integer = |text: &str| -> Result<u32> {
        Ok(if let Some(hex) = text.strip_prefix("0x") {
            u32::from_str_radix(hex, 16)?
        } else {
            text.parse()?
        })
    };
    let mut index = 0;
    while index < args.len() {
        match args[index].as_str() {
            "-s" | "--seed" => {
                seed = integer(args.get(index + 1).context("seed requires an integer")?)?;
                index += 2;
            }
            "-p" | "--pad" => {
                pad = integer(args.get(index + 1).context("pad requires an integer")?)? as usize;
                index += 2;
            }
            arg if !arg.starts_with('-') => {
                positional.push(arg);
                index += 1;
            }
            arg => bail!("unknown boot checksum option {arg}"),
        }
    }
    ensure!(
        positional.len() == 2 && pad >= 4,
        "pico-pad-checksum [-s SEED] [-p PAD] SOURCE.bin DESTINATION.S"
    );
    let mut bytes = fs::read(positional[0])?;
    ensure!(bytes.len() <= pad - 4, "boot input exceeds padded size");
    bytes.resize(pad - 4, 0);
    let mut crc = seed;
    for byte in &bytes {
        crc ^= u32::from(byte.reverse_bits());
        for _ in 0..8 {
            crc = if crc & 1 != 0 {
                (crc >> 1) ^ 0xedb88320
            } else {
                crc >> 1
            };
        }
    }
    bytes.extend_from_slice(&crc.reverse_bits().to_le_bytes());
    let mut output = format!("// Padded and checksummed version of: {}\n\n.cpu cortex-m0plus\n.thumb\n\n.section .boot2, \"ax\"\n\n", positional[0]);
    for chunk in bytes.chunks(16) {
        writeln!(
            output,
            ".byte {}",
            chunk
                .iter()
                .map(|byte| format!("0x{byte:02x}"))
                .collect::<Vec<_>>()
                .join(", ")
        )?;
    }
    write(Path::new(positional[1]), output.as_bytes())
}

fn pack(data: &[u8]) -> Result<Vec<u8>> {
    ensure!(
        !data.is_empty() && data.len() <= 2 * 1024 * 1024,
        "expected a nonempty RP2040 flash image within its flash capacity"
    );
    let count = data.len().div_ceil(PAYLOAD);
    let mut packed = vec![0; count * BLOCK];
    for (index, payload) in data.chunks(PAYLOAD).enumerate() {
        let block = &mut packed[index * BLOCK..(index + 1) * BLOCK];
        for (offset, word) in [
            UF2_MAGIC[0],
            UF2_MAGIC[1],
            0x2000,
            FLASH + (PAYLOAD * index) as u32,
            PAYLOAD as u32,
            index as u32,
            count as u32,
            FAMILY,
        ]
        .iter()
        .enumerate()
        {
            block[offset * 4..offset * 4 + 4].copy_from_slice(&word.to_le_bytes());
        }
        block[32..32 + payload.len()].copy_from_slice(payload);
        block[BLOCK - 4..].copy_from_slice(&UF2_MAGIC[2].to_le_bytes());
    }
    Ok(packed)
}

fn decode(data: &[u8]) -> Result<Vec<u8>> {
    ensure!(
        !data.is_empty() && data.len() % BLOCK == 0,
        "invalid UF2 block length"
    );
    let count = data.len() / BLOCK;
    let mut binary = Vec::with_capacity(count * PAYLOAD);
    for (index, block) in data.chunks_exact(BLOCK).enumerate() {
        let word = |offset| u32::from_le_bytes(block[offset..offset + 4].try_into().unwrap());
        let expected = [
            UF2_MAGIC[0],
            UF2_MAGIC[1],
            0x2000,
            FLASH + (PAYLOAD * index) as u32,
            PAYLOAD as u32,
            index as u32,
            count as u32,
            FAMILY,
        ];
        ensure!(
            expected.iter().enumerate().all(|(i, v)| word(i * 4) == *v)
                && word(BLOCK - 4) == UF2_MAGIC[2],
            "invalid UF2 header at block {index}"
        );
        binary.extend_from_slice(&block[32..32 + PAYLOAD]);
    }
    Ok(binary)
}

#[derive(Deserialize, Serialize)]
struct Receipt {
    #[serde(default)]
    source_revision: Option<String>,
    sources: BTreeMap<String, String>,
    uf2_sha256: String,
    binary_bytes: usize,
    binary_sha256: String,
    geometry_sha256: String,
}

pub fn verify(root: &Path, args: &[String]) -> Result<()> {
    ensure!(args.is_empty(), "positioner-verify takes no arguments");
    geometry(root, &["--check".to_owned()])?;
    let receipt: Receipt = serde_json::from_value(read_json(
        &root.join(FIRMWARE).join("assets/build-receipt.json"),
    )?)?;
    for (path, digest) in &receipt.sources {
        let bytes = if let Some(revision) = &receipt.source_revision {
            ensure!(
                revision.len() == 40 && revision.bytes().all(|v| v.is_ascii_hexdigit()),
                "receipt revision must be a full Git SHA"
            );
            crate::output(
                Command::new("git")
                    .current_dir(root)
                    .args(["show", &format!("{revision}:{path}")]),
            )?
            .stdout
        } else {
            fs::read(root.join(path))?
        };
        ensure!(sha(&bytes) == *digest, "released source differs: {path}");
        if !path.ends_with("/geometry_generated.h")
            && matches!(
                Path::new(path).extension().and_then(|s| s.to_str()),
                Some("cpp" | "h")
            )
        {
            ensure!(
                sha(&fs::read(root.join(path))?) == *digest,
                "current firmware source differs from the released image: {path}"
            );
        }
    }
    let image = fs::read(root.join(FIRMWARE).join("assets/pgfun-positioner-r1.uf2"))?;
    ensure!(sha(&image) == receipt.uf2_sha256, "UF2 digest mismatch");
    let binary = decode(&image)?;
    ensure!(
        receipt.binary_bytes <= binary.len(),
        "binary receipt exceeds UF2 payload"
    );
    ensure!(
        sha(&binary[..receipt.binary_bytes]) == receipt.binary_sha256
            && binary[receipt.binary_bytes..].iter().all(|v| *v == 0),
        "UF2 payload mismatch"
    );
    let motion = if let Some(revision) = &receipt.source_revision {
        serde_json::from_slice(
            &crate::output(Command::new("git").current_dir(root).args([
                "show",
                &format!("{revision}:{MECHANICAL}/motion-geometry.json"),
            ]))?
            .stdout,
        )?
    } else {
        read_json(&root.join(MECHANICAL).join("motion-geometry.json"))?
    };
    ensure!(
        motion["sha256"] == receipt.geometry_sha256,
        "geometry mismatch"
    );
    println!("UF2 payload, source hashes and motion geometry match their receipt; current motion header is current");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn released_uf2_header_and_payload_are_preserved() {
        let binary = (0..257).map(|v| v as u8).collect::<Vec<_>>();
        let packed = pack(&binary).unwrap();
        assert_eq!(packed.len(), 1024);
        assert_eq!(
            &packed[..8],
            &[0x55, 0x46, 0x32, 0x0a, 0x57, 0x51, 0x5d, 0x9e]
        );
        assert_eq!(&packed[512 + 12..512 + 16], &[0, 1, 0, 0x10]);
        let decoded = decode(&packed).unwrap();
        assert_eq!(&decoded[..257], binary);
        assert!(decoded[257..].iter().all(|v| *v == 0));
        let mut corrupt = packed;
        corrupt[512 + 20] ^= 1;
        assert!(decode(&corrupt).is_err());
        assert!(pack(&[]).is_err());
        assert!(decode(&[0; 511]).is_err());
    }
}
