//! Reference-only NPZ access: identities and exact transformed vertex bounds.
//!
//! Geometry is left in its source archive. Triangles and face records are decoded only by
//! the construction paths which actually cut a solid.
use anyhow::{ensure, Context, Result};
use hsm_kernel::{v3, Affine, Bounds, V3};
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeMap,
    fs::File,
    io::{BufReader, Read, Seek},
    path::Path,
};
use zip::ZipArchive;

type Key = (usize, [[u64; 4]; 3]);
pub struct References {
    pub names: Vec<String>,
    archive: ZipArchive<BufReader<File>>,
    bounds: BTreeMap<Key, Bounds>,
}
impl References {
    pub fn open(path: &str) -> Result<Self> {
        let mut file = File::open(path).with_context(|| format!("reference model {path}"))?;
        if std::env::var_os("HSM_READS").is_some() {
            let mut hash = Sha256::new();
            let mut block = [0_u8; 65536];
            loop {
                let n = file.read(&mut block)?;
                if n == 0 {
                    break;
                }
                hash.update(&block[..n]);
            }
            hsm_kernel::reads::digest(Path::new(path), &format!("{:x}", hash.finalize()));
            file.rewind()?;
        }
        let mut archive = ZipArchive::new(BufReader::new(file))?;
        let names = {
            let mut member = archive.by_name("names.npy")?;
            let (_head, _offset) = header(&mut member)?;
            let mut bytes = Vec::new();
            member.read_to_end(&mut bytes)?;
            serde_json::from_slice(&bytes)?
        };
        Ok(Self {
            names,
            archive,
            bounds: BTreeMap::new(),
        })
    }
    pub fn bounds(&mut self, index: usize, frame: &Affine) -> Result<Bounds> {
        ensure!(index < self.names.len(), "selected reference entry");
        let key = (index, frame.m.map(|row| row.map(f64::to_bits)));
        if let Some(b) = self.bounds.get(&key) {
            return Ok(*b);
        }
        let mut member = self.archive.by_name(&format!("V{index}.npy"))?;
        let (head, offset) = header(&mut member)?;
        let dtype = value(&head, "descr")?;
        let dtype = dtype.trim_matches(['\'', '"']);
        ensure!(
            ["<f8", ">f8", "=f8", "f8"].contains(&dtype),
            "reference vertices are f64"
        );
        ensure!(
            value(&head, "fortran_order")? == "False",
            "reference vertices are C ordered"
        );
        let shape = value(&head, "shape")?;
        let shape: Vec<usize> = shape
            .trim_matches(['(', ')'])
            .split(',')
            .filter(|v| !v.trim().is_empty())
            .map(|v| v.trim().parse())
            .collect::<std::result::Result<_, _>>()?;
        ensure!(
            shape.len() == 2 && shape[1] == 3,
            "reference vertices are N by 3"
        );
        ensure!(
            member.size() == offset as u64 + shape[0] as u64 * 24,
            "reference vertex bytes"
        );
        let big = dtype.starts_with('>') || (dtype.starts_with('=') && cfg!(target_endian = "big"));
        let mut lo = v3(f64::INFINITY, f64::INFINITY, f64::INFINITY);
        let mut hi = -lo;
        let mut block = [0_u8; 24 * 1024];
        let mut left = shape[0];
        while left > 0 {
            let n = left.min(1024);
            member.read_exact(&mut block[..n * 24])?;
            for xyz in block[..n * 24].chunks_exact(24) {
                let values: [f64; 3] = std::array::from_fn(|i| {
                    let bytes: [u8; 8] = xyz[i * 8..i * 8 + 8].try_into().unwrap();
                    if big {
                        f64::from_be_bytes(bytes)
                    } else {
                        f64::from_le_bytes(bytes)
                    }
                });
                let vertex = V3::from(values);
                ensure!(vertex.is_finite(), "reference vertex is finite");
                let point = frame.point(vertex);
                lo = lo.min(point);
                hi = hi.max(point);
            }
            left -= n;
        }
        ensure!(
            lo.is_finite() && hi.is_finite(),
            "empty reference has no seating bounds"
        );
        let result = Bounds { min: lo, max: hi };
        self.bounds.insert(key, result);
        Ok(result)
    }
}
fn header(reader: &mut impl Read) -> Result<(String, usize)> {
    let mut prefix = [0_u8; 8];
    reader.read_exact(&mut prefix)?;
    ensure!(&prefix[..6] == b"\x93NUMPY", "reference NPY header");
    let (size, start) = if prefix[6] == 1 {
        let mut len = [0; 2];
        reader.read_exact(&mut len)?;
        (u16::from_le_bytes(len) as usize, 10)
    } else {
        ensure!([2, 3].contains(&prefix[6]), "reference NPY version");
        let mut len = [0; 4];
        reader.read_exact(&mut len)?;
        (u32::from_le_bytes(len) as usize, 12)
    };
    let mut bytes = vec![0; size];
    reader.read_exact(&mut bytes)?;
    Ok((String::from_utf8(bytes)?, start + size))
}
fn value<'a>(head: &'a str, key: &str) -> Result<&'a str> {
    let at = head
        .find(&format!("'{key}'"))
        .or_else(|| head.find(&format!("\"{key}\"")))
        .with_context(|| format!("NPY field {key}"))?;
    let text = head[at..]
        .split_once(':')
        .context("NPY field value")?
        .1
        .trim_start();
    let stop = if text.starts_with('(') {
        text.find(')').map(|i| i + 1)
    } else {
        text.find(',')
    }
    .context("NPY field terminator")?;
    Ok(text[..stop].trim())
}
