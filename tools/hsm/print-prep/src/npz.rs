//! NumPy's `.npz` archive of float64 triangle arrays, the form `np.load` reads the show faces in.

use anyhow::Result;
use std::io::Write;
use std::path::Path;

/// Each array is (count, 3, 3) float64, under its name, deflated as `np.savez_compressed` writes.
pub fn write_triangles(path: &Path, arrays: &[(String, Vec<[[f64; 3]; 3]>)]) -> Result<()> {
    let mut archive = zip::ZipWriter::new(std::fs::File::create(path)?);
    let options = zip::write::SimpleFileOptions::default().compression_method(zip::CompressionMethod::Deflated);
    for (name, triangles) in arrays {
        archive.start_file(format!("{name}.npy"), options)?;
        let mut header = format!("{{'descr': '<f8', 'fortran_order': False, 'shape': ({}, 3, 3), }}", triangles.len());
        // Magic, version, length, then the dictionary padded so data starts on 64 bytes.
        while (10 + header.len() + 1) % 64 != 0 {
            header.push(' ');
        }
        header.push('\n');
        let mut bytes = b"\x93NUMPY\x01\x00".to_vec();
        bytes.extend_from_slice(&(header.len() as u16).to_le_bytes());
        bytes.extend_from_slice(header.as_bytes());
        for t in triangles {
            for p in t {
                for v in p {
                    bytes.extend_from_slice(&v.to_le_bytes());
                }
            }
        }
        archive.write_all(&bytes)?;
    }
    archive.finish()?;
    Ok(())
}

/// One array of a NumPy archive, as little-endian numbers in C order.
pub struct Array {
    pub shape: Vec<usize>,
    pub data: Data,
}

pub enum Data {
    F64(Vec<f64>),
    U32(Vec<u32>),
    I64(Vec<i64>),
    U8(Vec<u8>),
}

impl Array {
    pub fn f64(&self) -> Option<&[f64]> {
        match &self.data { Data::F64(v) => Some(v), _ => None }
    }

    /// Rows of three, as an index or a count list: unsigned or signed integers alike.
    pub fn indices(&self) -> Option<Vec<usize>> {
        match &self.data {
            Data::U32(v) => Some(v.iter().map(|&x| x as usize).collect()),
            Data::I64(v) => Some(v.iter().map(|&x| x as usize).collect()),
            Data::U8(v) => Some(v.iter().map(|&x| x as usize).collect()),
            Data::F64(_) => None,
        }
    }

    pub fn bytes(&self) -> Option<&[u8]> {
        match &self.data { Data::U8(v) => Some(v), _ => None }
    }
}

/// Every array of an `.npz` archive, by name.
pub fn read_arrays(path: &Path) -> Result<std::collections::BTreeMap<String, Array>> {
    use anyhow::{bail, Context};
    use std::io::Read;
    let mut archive = zip::ZipArchive::new(std::fs::File::open(path).with_context(|| format!("opening {}", path.display()))?)?;
    let mut out = std::collections::BTreeMap::new();
    for i in 0..archive.len() {
        let mut entry = archive.by_index(i)?;
        let name = entry.name()?.to_string();
        let mut bytes = Vec::new();
        entry.read_to_end(&mut bytes)?;
        if !bytes.starts_with(b"\x93NUMPY") {
            bail!("{name} in {} is not a NumPy array", path.display());
        }
        let (length, start) = if bytes[6] == 1 {
            (u16::from_le_bytes([bytes[8], bytes[9]]) as usize, 10)
        } else {
            (u32::from_le_bytes([bytes[8], bytes[9], bytes[10], bytes[11]]) as usize, 12)
        };
        let header = std::str::from_utf8(&bytes[start..start + length])?;
        let field = |key: &str| -> Option<&str> {
            let at = header.find(&format!("'{key}':"))? + key.len() + 3;
            Some(header[at..].trim_start())
        };
        let descr = field("descr").and_then(|s| s.strip_prefix('\'')).and_then(|s| s.split('\'').next()).context("array type")?;
        if field("fortran_order").is_some_and(|s| s.starts_with("True")) {
            bail!("{name} is stored in Fortran order");
        }
        let shape_text = field("shape").and_then(|s| s.strip_prefix('(')).and_then(|s| s.split(')').next()).context("array shape")?;
        let shape: Vec<usize> = shape_text.split(',').map(str::trim).filter(|s| !s.is_empty()).map(str::parse).collect::<Result<_, _>>()?;
        let body = &bytes[start + length..];
        let data = match descr {
            "<f8" => Data::F64(body.chunks_exact(8).map(|c| f64::from_le_bytes(c.try_into().unwrap())).collect()),
            "<u4" => Data::U32(body.chunks_exact(4).map(|c| u32::from_le_bytes(c.try_into().unwrap())).collect()),
            "<i8" => Data::I64(body.chunks_exact(8).map(|c| i64::from_le_bytes(c.try_into().unwrap())).collect()),
            "|u1" | "<u1" => Data::U8(body.to_vec()),
            other => bail!("{name} has type {other}, which this reader does not read"),
        };
        out.insert(name.trim_end_matches(".npy").to_string(), Array { shape, data });
    }
    Ok(out)
}
