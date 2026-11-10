//! Stationary observations qualify the camera's projected jitter floor without commanding hardware.
use crate::policy::{HOLDOUT_MAX_MM, HOLDOUT_P95_MM, MAX_SIGMA_MM};
use anyhow::{Context, Result, ensure};
use hsm_pgfun_observation::{median, quantile};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeMap;

#[derive(Clone, Debug, Deserialize)]
pub struct NoiseSample {
    #[serde(default)]
    pub physical: bool,
    #[serde(default)]
    pub valid: bool,
    pub sample_ns: Option<u64>,
    pub values_mm: Option<[f64; 4]>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct NoiseConfig {
    pub mm_per_pixel: [f64; 2],
    pub stationary_sigma_px: Option<f64>,
    #[serde(default)]
    pub noise_qualified: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub noise_receipt_sha256: Option<String>,
    #[serde(flatten)]
    pub fields: BTreeMap<String, Value>,
}
#[derive(Clone, Debug, Serialize)]
pub struct NoiseReceipt {
    pub frame_count: usize,
    pub sigma_mm: [f64; 4],
    pub p95_mm: f64,
    pub maximum_mm: f64,
    pub stationary_sigma_px: f64,
    pub scope: &'static str,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_sha256: Option<String>,
}

pub fn qualify(rows: &[NoiseSample], config: &NoiseConfig) -> Result<(NoiseConfig, NoiseReceipt)> {
    let good: Vec<_> = rows.iter().filter(|r| r.physical && r.valid).collect();
    ensure!(
        good.len() >= 300 && good.len() as f64 >= 0.98 * rows.len() as f64,
        "insufficient valid physical stationary coverage"
    );
    let stamps: Vec<_> = good
        .iter()
        .map(|r| r.sample_ns.context("stationary observation timestamp"))
        .collect::<Result<_>>()?;
    ensure!(
        stamps.iter().max().unwrap() - stamps.iter().min().unwrap() >= 15_000_000_000,
        "stationary observation duration is too short"
    );
    let values: Vec<_> = good
        .iter()
        .map(|r| {
            r.values_mm
                .context("four stationary observation coordinates")
        })
        .collect::<Result<_>>()?;
    ensure!(
        values.iter().flatten().all(|v| v.is_finite()),
        "four finite observation coordinates required"
    );
    let center: [f64; 4] =
        std::array::from_fn(|axis| median(&values.iter().map(|v| v[axis]).collect::<Vec<_>>()));
    let sigma: [f64; 4] = std::array::from_fn(|axis| {
        let mean = values.iter().map(|v| v[axis]).sum::<f64>() / values.len() as f64;
        (values.iter().map(|v| (v[axis] - mean).powi(2)).sum::<f64>() / (values.len() - 1) as f64)
            .sqrt()
    });
    let error: Vec<_> = values
        .iter()
        .flat_map(|v| std::array::from_fn::<_, 4, _>(|axis| (v[axis] - center[axis]).abs()))
        .collect();
    let p95 = quantile(&error, 0.95);
    let maximum = error.iter().copied().fold(0., f64::max);
    ensure!(
        sigma.iter().all(|&v| v <= MAX_SIGMA_MM)
            && p95 <= HOLDOUT_P95_MM
            && maximum <= HOLDOUT_MAX_MM,
        "stationary jitter exceeds the optical qualification limits"
    );
    let floor = sigma
        .iter()
        .enumerate()
        .map(|(axis, &v)| v / config.mm_per_pixel[axis % 2])
        .fold(0.1, f64::max);
    let mut out = config.clone();
    out.stationary_sigma_px = Some(floor);
    out.noise_qualified = true;
    Ok((
        out,
        NoiseReceipt {
            frame_count: good.len(),
            sigma_mm: sigma,
            p95_mm: p95,
            maximum_mm: maximum,
            stationary_sigma_px: floor,
            scope: "Stationary projected image-plane jitter; does not certify scale bias or absolute endpoint accuracy",
            source_sha256: None,
        },
    ))
}
