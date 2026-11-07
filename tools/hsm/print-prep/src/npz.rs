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
