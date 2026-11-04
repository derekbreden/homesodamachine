//! Reproducible GNU tar/gzip publication objects and content-addressed adoption.
use super::zlib::Gzip;
use anyhow::{Context, Result, ensure};
use flate2::read::MultiGzDecoder;
use sha2::{Digest, Sha256};
use std::{
    fs::{self, File},
    io::{Read, Write},
    path::Path,
};

fn number(value: u64, width: usize) -> Vec<u8> {
    let octal = format!("{value:0w$o}\0", w = width - 1);
    if octal.len() == width {
        return octal.into_bytes();
    }
    let mut bytes = vec![0; width];
    let raw = value.to_be_bytes();
    bytes[width - 8..].copy_from_slice(&raw);
    bytes[0] = 0x80;
    bytes
}
fn header(name: &str, size: u64, mode: u64, kind: u8) -> [u8; 512] {
    let mut bytes = [0u8; 512];
    let name = name.as_bytes();
    let n = name.len().min(100);
    bytes[..n].copy_from_slice(&name[..n]);
    for (start, width, value) in [
        (100, 8, mode),
        (108, 8, 0),
        (116, 8, 0),
        (124, 12, size),
        (136, 12, 0),
    ] {
        bytes[start..start + width].copy_from_slice(&number(value, width));
    }
    bytes[148..156].fill(b' ');
    bytes[156] = kind;
    bytes[257..265].copy_from_slice(b"ustar  \0");
    let checksum: u64 = bytes.iter().map(|&b| u64::from(b)).sum();
    let checksum = format!("{checksum:06o}\0");
    bytes[148..155].copy_from_slice(checksum.as_bytes());
    bytes
}
fn zeros(out: &mut impl Write, count: u64) -> Result<()> {
    let bytes = [0; 10240];
    let mut left = count;
    while left > 0 {
        let n = left.min(bytes.len() as u64) as usize;
        out.write_all(&bytes[..n])?;
        left -= n as u64;
    }
    Ok(())
}
pub fn bundle(root: &Path, rels: &[String], target: &Path) -> Result<String> {
    let mut output = Gzip::new(target, 6)?;
    let mut offset = 0u64;
    for relative in rels {
        let path = root.join(relative);
        let size = path.metadata()?.len();
        if relative.len() > 100 {
            let bytes = relative.as_bytes();
            let size = bytes.len() as u64 + 1;
            output.write_all(&header("././@LongLink", size, 0, b'L'))?;
            output.write_all(bytes)?;
            output.write_all(&[0])?;
            let padding = (512 - size % 512) % 512;
            zeros(&mut output, padding)?;
            offset += 512 + size + padding;
        }
        output.write_all(&header(relative, size, 0o644, b'0'))?;
        let copied = std::io::copy(&mut File::open(&path)?.take(size), &mut output)?;
        ensure!(copied == size, "unexpected end of data: {}", path.display());
        let padding = (512 - size % 512) % 512;
        zeros(&mut output, padding)?;
        offset += 512 + size + padding;
    }
    zeros(&mut output, 1024)?;
    offset += 1024;
    zeros(&mut output, (10240 - offset % 10240) % 10240)?;
    output.finish()?;
    crate::payload::digest(target)
}
pub fn gzip(source: &Path, target: &Path, level: u32) -> Result<()> {
    let mut output = Gzip::new(target, level)?;
    std::io::copy(&mut File::open(source)?, &mut output)?;
    output.finish()?;
    Ok(())
}
pub fn decompress(bytes: &[u8]) -> Result<Vec<u8>> {
    let mut output = Vec::new();
    MultiGzDecoder::new(bytes).read_to_end(&mut output)?;
    Ok(output)
}
pub fn adopt(root: &Path, relative: &str, digest: &str, bytes: &[u8]) -> Result<bool> {
    if format!("{:x}", Sha256::digest(bytes)) != digest {
        return Ok(false);
    }
    let target = root.join(relative);
    let name = target
        .file_name()
        .context("adopted filename")?
        .to_string_lossy();
    let temporary = target.with_file_name(format!("{name}.adopt"));
    fs::write(&temporary, bytes)?;
    fs::rename(temporary, target)?;
    Ok(true)
}
pub fn facets(path: &Path) -> Result<i64> {
    if path.extension().is_none_or(|e| e != "stl") {
        return Ok(-1);
    }
    let mut file = File::open(path)?;
    let mut bytes = [0; 84];
    let mut count = 0;
    while count < 84 {
        let n = file.read(&mut bytes[count..])?;
        if n == 0 {
            return Ok(-1);
        }
        count += n;
    }
    if bytes.starts_with(b"solid") {
        return Ok(-1);
    }
    Ok(i64::from(u32::from_le_bytes(bytes[80..84].try_into()?)))
}
