//! Exact STL digests bind emitted facet indices to their native construction records.
use super::*;
use std::io::{Cursor, Read};

struct Body {
    first: usize,
    faces: Vec<usize>,
    records: Vec<Value>,
}
pub struct Sources {
    pub status: String,
    bodies: Vec<Body>,
}

fn array_bytes(archive: &mut zip::ZipArchive<std::fs::File>, name: &str) -> Result<Vec<u8>> {
    let mut bytes = Vec::new();
    archive.by_name(name)?.read_to_end(&mut bytes)?;
    Ok(bytes)
}
fn json_array(archive: &mut zip::ZipArchive<std::fs::File>, name: &str) -> Result<Value> {
    let bytes = array_bytes(archive, name)?;
    let npy = npyz::NpyFile::new(Cursor::new(bytes))?;
    Ok(serde_json::from_slice(&npy.into_vec::<u8>()?)?)
}
fn indices(bytes: &[u8]) -> Result<Vec<usize>> {
    let npy = npyz::NpyFile::new(Cursor::new(bytes))?;
    ensure!(npy.shape().len() == 1, "facet indices are not a vector");
    if let Ok(values) = npy.into_vec::<u32>() {
        return Ok(values.into_iter().map(|v| v as usize).collect());
    }
    if let Ok(values) = npyz::NpyFile::new(Cursor::new(bytes))?.into_vec::<u64>() {
        return values
            .into_iter()
            .map(|v| usize::try_from(v).context("facet index overflow"))
            .collect();
    }
    let values = npyz::NpyFile::new(Cursor::new(bytes))?.into_vec::<i64>()?;
    values
        .into_iter()
        .map(|v| usize::try_from(v).context("negative facet index"))
        .collect()
}
impl Sources {
    pub fn load(model: Option<&Path>, hash: &str, facets: usize) -> Self {
        let Some(model) = model else {
            return Self {
                status: "not requested".into(),
                bodies: Vec::new(),
            };
        };
        match Self::read(model, hash, facets) {
            Ok(read) => read,
            Err(error) => Self {
                status: format!("unknown ({error})"),
                bodies: Vec::new(),
            },
        }
    }
    fn read(model: &Path, hash: &str, facets: usize) -> Result<Self> {
        let mut archive =
            zip::ZipArchive::new(std::fs::File::open(model).context("unreadable STL binding")?)
                .context("unreadable STL binding")?;
        let document = json_array(&mut archive, "document.npy").context("no STL binding")?;
        let trace = &document["printed"];
        ensure!(trace["v"] == 1, "no STL binding");
        ensure!(trace["sha256"] == hash, "stale STL binding");
        let records = json_array(
            &mut archive,
            trace["records"]
                .as_str()
                .context("incomplete STL binding")?,
        )?;
        let mut bodies = Vec::new();
        let mut first = 0;
        for (i, body) in trace["bodies"]
            .as_array()
            .context("incomplete STL binding")?
            .iter()
            .enumerate()
        {
            ensure!(
                body["body"].as_u64() == Some(i as u64)
                    && body["first"].as_u64() == Some(first as u64),
                "incomplete STL binding"
            );
            let rows = records[i]
                .as_array()
                .context("incomplete STL binding")?
                .clone();
            let ids = indices(&array_bytes(
                &mut archive,
                body["faces"].as_str().context("incomplete STL binding")?,
            )?)?;
            ensure!(
                body["count"].as_u64() == Some(ids.len() as u64)
                    && ids.iter().all(|&i| i < rows.len()),
                "incomplete STL binding"
            );
            let count = ids.len();
            bodies.push(Body {
                first,
                faces: ids,
                records: rows,
            });
            first += count;
        }
        ensure!(first == facets, "incomplete STL binding");
        Ok(Self {
            status: format!("bound STL · sha256 {}", &hash[..8]),
            bodies,
        })
    }
    pub fn for_facets(&self, facets: &[usize]) -> Vec<Value> {
        if self.bodies.is_empty() {
            return vec![Value::Null];
        }
        let mut seen = BTreeMap::new();
        for body in &self.bodies {
            let selected = facets
                .iter()
                .filter_map(|&i| {
                    i.checked_sub(body.first)
                        .and_then(|j| body.faces.get(j))
                        .copied()
                })
                .collect::<BTreeSet<_>>();
            for i in selected {
                for source in hsm_build_data::payload::record_sources(&body.records[i])
                    .as_array()
                    .unwrap()
                {
                    seen.entry(serde_json::to_string(source).unwrap())
                        .or_insert_with(|| source.clone());
                }
            }
        }
        if seen.is_empty() {
            vec![Value::Null]
        } else {
            seen.into_values().collect()
        }
    }
}
