//! Saved-image features estimate pixel positions, uncertainty and explicit target refusals.
use crate::imageio::Image;
use crate::median;
use serde::{Deserialize, Serialize, Serializer, de::DeserializeOwned};
use serde_json::{Value, json};
use std::collections::BTreeMap;

pub const DOT_LIMITS: &str = "An intensity-weighted centroid needs one compact spot above the noise threshold. Comparable reflections, an oversized spot and clipping limit it. A surface spot alone does not determine standoff or gun orientation.";
pub const WIRE_LIMITS: &str = "An elongated region and its half-contrast endpoint require the configured approach and polarity. Joined shadows or features, defocus and a curved endpoint change the estimate.";
pub const SEAM_LIMITS: &str = "A straight intensity edge is fitted about the ROI center. Lighting, reflections, scratches and curvature can change the visible edge; a recessed fillet is a spatial corner.";

#[derive(Clone, Copy, Debug, Default, Serialize, Deserialize, PartialEq)]
pub struct PointValues {
    pub u: f64,
    pub v: f64,
}

#[derive(Clone, Copy, Debug, Default, Serialize, Deserialize, PartialEq)]
pub struct LineValues {
    pub theta_deg: f64,
    pub rho: f64,
}

fn serialize_values<V: Serialize, S: Serializer>(
    value: &Option<V>,
    serializer: S,
) -> Result<S::Ok, S::Error> {
    match value {
        Some(value) => value.serialize(serializer),
        None => BTreeMap::<String, Value>::new().serialize(serializer),
    }
}
fn deserialize_values<'de, V: DeserializeOwned, D: serde::Deserializer<'de>>(
    decoder: D,
) -> Result<Option<V>, D::Error> {
    let value = Value::deserialize(decoder)?;
    if value.is_null() || value.as_object().is_some_and(|m| m.is_empty()) {
        Ok(None)
    } else {
        serde_json::from_value(value)
            .map(Some)
            .map_err(serde::de::Error::custom)
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(bound(serialize = "V: Serialize", deserialize = "V: DeserializeOwned"))]
pub struct FeatureResult<V> {
    pub extractor: String,
    pub version: String,
    pub valid: bool,
    #[serde(
        default,
        serialize_with = "serialize_values",
        deserialize_with = "deserialize_values"
    )]
    pub values: Option<V>,
    #[serde(
        default,
        serialize_with = "serialize_values",
        deserialize_with = "deserialize_values"
    )]
    pub sigma: Option<V>,
    pub confidence: f64,
    pub reason: Option<String>,
    pub diagnostics: BTreeMap<String, Value>,
    #[serde(skip)]
    pub saturated_pixels: usize,
}

impl<V> FeatureResult<V> {
    fn invalid(
        name: &str,
        version: &str,
        reason: &str,
        diagnostics: BTreeMap<String, Value>,
    ) -> Self {
        Self {
            extractor: name.into(),
            version: version.into(),
            valid: false,
            values: None,
            sigma: None,
            confidence: 0.,
            reason: Some(reason.into()),
            diagnostics,
            saturated_pixels: 0,
        }
    }
}

fn deserialize_roi<'de, D: serde::Deserializer<'de>>(
    decoder: D,
) -> Result<Option<[i32; 4]>, D::Error> {
    let values = Option::<[f64; 4]>::deserialize(decoder)?;
    Ok(values.map(|values| values.map(|v| v as i32)))
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct DotConfig {
    #[serde(deserialize_with = "deserialize_roi")]
    pub roi: Option<[i32; 4]>,
    pub channel: Option<String>,
    pub label: Option<String>,
    pub threshold_sigma: f64,
    pub min_pixels: usize,
    pub max_pixels: usize,
    pub saturation: Option<f64>,
}
impl Default for DotConfig {
    fn default() -> Self {
        Self {
            roi: None,
            channel: Some("red".into()),
            label: None,
            threshold_sigma: 6.,
            min_pixels: 3,
            max_pixels: 20000,
            saturation: None,
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct WireConfig {
    #[serde(deserialize_with = "deserialize_roi")]
    pub roi: Option<[i32; 4]>,
    pub channel: Option<String>,
    pub label: Option<String>,
    pub approach_deg: f64,
    pub polarity: String,
    pub threshold_sigma: f64,
    pub min_pixels: usize,
    pub min_elongation: f64,
}
impl Default for WireConfig {
    fn default() -> Self {
        Self {
            roi: None,
            channel: None,
            label: None,
            approach_deg: 180.,
            polarity: "dark".into(),
            threshold_sigma: 5.,
            min_pixels: 30,
            min_elongation: 3.,
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct SeamConfig {
    #[serde(deserialize_with = "deserialize_roi")]
    pub roi: Option<[i32; 4]>,
    pub channel: Option<String>,
    pub label: Option<String>,
    pub orientation: String,
    pub inlier_px: f64,
    pub iterations: usize,
    pub min_inlier_fraction: f64,
    pub min_edge_sigma: f64,
    pub seed: u64,
}
impl Default for SeamConfig {
    fn default() -> Self {
        Self {
            roi: None,
            channel: None,
            label: None,
            orientation: "horizontal".into(),
            inlier_px: 1.,
            iterations: 200,
            min_inlier_fraction: 0.6,
            min_edge_sigma: 5.,
            seed: 0,
        }
    }
}

struct Crop {
    width: usize,
    height: usize,
    pixels: Vec<f64>,
    offset: [f64; 2],
}
fn prepare(
    image: &Image,
    roi: Option<[i32; 4]>,
    channel: Option<&str>,
) -> Result<Crop, &'static str> {
    let selected = match channel {
        Some("red") => Some(0),
        Some("green") => Some(1),
        Some("blue") => Some(2),
        _ => None,
    };
    if image.channels > 1 && selected.is_some_and(|c| c >= image.channels) {
        return Err("missing_channel");
    }
    let index = |value: i64, size: usize| -> usize {
        let value = if value < 0 {
            size as i64 + value
        } else {
            value
        };
        value.clamp(0, size as i64) as usize
    };
    let (x, y, w, h, offset) = if let Some([x, y, w, h]) = roi {
        let xa = index(x as i64, image.width);
        let xb = index(x as i64 + w as i64, image.width);
        let ya = index(y as i64, image.height);
        let yb = index(y as i64 + h as i64, image.height);
        (
            xa,
            ya,
            xb.saturating_sub(xa),
            yb.saturating_sub(ya),
            [x as f64, y as f64],
        )
    } else {
        (0, 0, image.width, image.height, [0., 0.])
    };
    if w == 0 || h == 0 {
        return Err("empty_roi");
    }
    let mut pixels = Vec::with_capacity(w * h);
    for row in y..y + h {
        for col in x..x + w {
            let start = (row * image.width + col) * image.channels;
            let value = if image.channels == 1 {
                image.pixels[start] as f64
            } else if let Some(c) = selected {
                image.pixels[start + c] as f64
            } else {
                let count = image.channels.min(3);
                image.pixels[start..start + count]
                    .iter()
                    .map(|&p| p as f64)
                    .sum::<f64>()
                    / count as f64
            };
            pixels.push(value);
        }
    }
    Ok(Crop {
        width: w,
        height: h,
        pixels,
        offset,
    })
}

fn background(values: &[f64]) -> (f64, f64) {
    let level = median(values);
    let noise = 1.4826 * median(&values.iter().map(|v| (v - level).abs()).collect::<Vec<_>>());
    (level, noise.max(0.5))
}
fn components(mask: &[bool], width: usize, height: usize) -> Vec<Vec<usize>> {
    let mut seen = vec![false; mask.len()];
    let mut out = Vec::new();
    for start in 0..mask.len() {
        if !mask[start] || seen[start] {
            continue;
        }
        seen[start] = true;
        let mut points = vec![start];
        let mut head = 0;
        while head < points.len() {
            let at = points[head];
            head += 1;
            let x = at % width;
            let y = at / width;
            for row in y.saturating_sub(1)..=(y + 1).min(height - 1) {
                for col in x.saturating_sub(1)..=(x + 1).min(width - 1) {
                    let next = row * width + col;
                    if mask[next] && !seen[next] {
                        seen[next] = true;
                        points.push(next);
                    }
                }
            }
        }
        points.sort_unstable();
        out.push(points);
    }
    out
}
fn diagnostics(values: Value) -> BTreeMap<String, Value> {
    values
        .as_object()
        .unwrap()
        .iter()
        .map(|(key, value)| (key.clone(), value.clone()))
        .collect()
}

fn validate_input(image: &Image, channel: Option<&str>) -> anyhow::Result<()> {
    image.validate()?;
    if image.channels > 1 {
        let selected = match channel {
            Some("red") => Some(0),
            Some("green") => Some(1),
            Some("blue") => Some(2),
            _ => None,
        };
        anyhow::ensure!(
            selected.is_none_or(|c| c < image.channels),
            "selected image channel is absent"
        );
    }
    Ok(())
}

pub fn aiming_dot(image: &Image, config: &DotConfig) -> anyhow::Result<FeatureResult<PointValues>> {
    validate_input(image, config.channel.as_deref())?;
    Ok(extract_dot(image, config))
}

pub fn wire_tip(image: &Image, config: &WireConfig) -> anyhow::Result<FeatureResult<PointValues>> {
    validate_input(image, config.channel.as_deref())?;
    anyhow::ensure!(
        matches!(config.polarity.as_str(), "dark" | "bright"),
        "wire polarity is dark or bright"
    );
    Ok(extract_wire(image, config))
}

pub fn seam_line(image: &Image, config: &SeamConfig) -> anyhow::Result<FeatureResult<LineValues>> {
    validate_input(image, config.channel.as_deref())?;
    anyhow::ensure!(
        matches!(config.orientation.as_str(), "horizontal" | "vertical"),
        "seam orientation is horizontal or vertical"
    );
    Ok(extract_seam(image, config))
}

fn extract_dot(image: &Image, config: &DotConfig) -> FeatureResult<PointValues> {
    let crop = match prepare(image, config.roi, config.channel.as_deref()) {
        Ok(crop) => crop,
        Err(reason) => return FeatureResult::invalid("dot", "1", reason, BTreeMap::new()),
    };
    let (bg, noise) = background(&crop.pixels);
    let peak = crop
        .pixels
        .iter()
        .copied()
        .fold(f64::NEG_INFINITY, f64::max);
    let snr = (peak - bg) / noise;
    let mut diag = diagnostics(json!({"background":bg,"noise":noise,"peak":peak,"snr":snr}));
    if snr < config.threshold_sigma {
        return FeatureResult::invalid("dot", "1", "no_spot", diag);
    }
    let threshold = bg + config.threshold_sigma * noise;
    let comps = components(
        &crop
            .pixels
            .iter()
            .map(|&p| p > threshold)
            .collect::<Vec<_>>(),
        crop.width,
        crop.height,
    );
    if comps.is_empty() {
        return FeatureResult::invalid("dot", "1", "no_spot", diag);
    }
    let peaks: Vec<_> = comps
        .iter()
        .map(|c| {
            c.iter()
                .map(|&i| crop.pixels[i])
                .fold(f64::NEG_INFINITY, f64::max)
        })
        .collect();
    let mut main = 0;
    for i in 1..peaks.len() {
        if peaks[i] > peaks[main] {
            main = i;
        }
    }
    diag.insert("spots".into(), json!(comps.len()));
    if (0..comps.len()).any(|i| {
        i != main && comps[i].len() >= config.min_pixels && peaks[i] - bg > 0.5 * (peaks[main] - bg)
    }) {
        return FeatureResult::invalid("dot", "1", "multiple_spots", diag);
    }
    let points = &comps[main];
    if points.len() < config.min_pixels {
        return FeatureResult::invalid("dot", "1", "spot_too_small", diag);
    }
    if points.len() > config.max_pixels {
        return FeatureResult::invalid("dot", "1", "spot_too_large", diag);
    }
    let weight: f64 = points.iter().map(|&i| crop.pixels[i] - threshold).sum();
    let u = points
        .iter()
        .map(|&i| (crop.pixels[i] - threshold) * (i % crop.width) as f64)
        .sum::<f64>()
        / weight;
    let v = points
        .iter()
        .map(|&i| (crop.pixels[i] - threshold) * (i / crop.width) as f64)
        .sum::<f64>()
        / weight;
    let su = noise
        * points
            .iter()
            .map(|&i| ((i % crop.width) as f64 - u).powi(2))
            .sum::<f64>()
            .sqrt()
        / weight;
    let sv = noise
        * points
            .iter()
            .map(|&i| ((i / crop.width) as f64 - v).powi(2))
            .sum::<f64>()
            .sqrt()
        / weight;
    let saturation = config
        .saturation
        .unwrap_or(if peak <= 255. { 255. } else { 65535. });
    let saturated_pixels = points
        .iter()
        .filter(|&&i| crop.pixels[i] >= saturation)
        .count();
    diag.insert("pixels".into(), json!(points.len()));
    diag.insert("saturated_pixels".into(), json!(saturated_pixels));
    let mut confidence =
        ((snr - config.threshold_sigma) / (3. * config.threshold_sigma)).clamp(0., 1.);
    if saturated_pixels >= 2 {
        confidence *= 0.5;
    }
    FeatureResult {
        extractor: "dot".into(),
        version: "1".into(),
        valid: true,
        values: Some(PointValues {
            u: u + crop.offset[0],
            v: v + crop.offset[1],
        }),
        sigma: Some(PointValues { u: su, v: sv }),
        confidence,
        reason: None,
        diagnostics: diag,
        saturated_pixels,
    }
}

fn covariance(points: &[[f64; 2]]) -> ([f64; 2], [f64; 3]) {
    let n = points.len() as f64;
    let mean = [
        points.iter().map(|p| p[0]).sum::<f64>() / n,
        points.iter().map(|p| p[1]).sum::<f64>() / n,
    ];
    let mut covariance = [0.; 3];
    for point in points {
        let x = point[0] - mean[0];
        let y = point[1] - mean[1];
        covariance[0] += x * x;
        covariance[1] += x * y;
        covariance[2] += y * y;
    }
    (mean, covariance.map(|v| v / (n - 1.)))
}
fn eigen(cov: [f64; 3]) -> ([f64; 2], [[f64; 2]; 2]) {
    let [a, b, d] = cov;
    let middle = (a + d) / 2.;
    let gap = ((a - d) / 2.).hypot(b);
    let angle = 0.5 * (2. * b).atan2(a - d);
    let large = [angle.cos(), angle.sin()];
    ([middle - gap, middle + gap], [[-large[1], large[0]], large])
}
fn bilinear(pixels: &[f64], width: usize, height: usize, x: f64, y: f64) -> f64 {
    let x = x.clamp(0., (width as f64 - 1.000001).max(0.));
    let y = y.clamp(0., (height as f64 - 1.000001).max(0.));
    let x0 = x.floor() as usize;
    let y0 = y.floor() as usize;
    let x1 = (x0 + 1).min(width - 1);
    let y1 = (y0 + 1).min(height - 1);
    let fx = x - x0 as f64;
    let fy = y - y0 as f64;
    pixels[y0 * width + x0] * (1. - fx) * (1. - fy)
        + pixels[y0 * width + x1] * fx * (1. - fy)
        + pixels[y1 * width + x0] * (1. - fx) * fy
        + pixels[y1 * width + x1] * fx * fy
}

fn extract_wire(image: &Image, config: &WireConfig) -> FeatureResult<PointValues> {
    let crop = match prepare(image, config.roi, config.channel.as_deref()) {
        Ok(crop) => crop,
        Err(reason) => return FeatureResult::invalid("wire", "1", reason, BTreeMap::new()),
    };
    let (bg, noise) = background(&crop.pixels);
    let contrast: Vec<_> = crop
        .pixels
        .iter()
        .map(|p| {
            if config.polarity == "dark" {
                bg - p
            } else {
                p - bg
            }
        })
        .collect();
    let comps = components(
        &contrast
            .iter()
            .map(|&p| p > config.threshold_sigma * noise)
            .collect::<Vec<_>>(),
        crop.width,
        crop.height,
    );
    let mut largest = None;
    for component in &comps {
        if largest.is_none_or(|c: &Vec<usize>| component.len() > c.len()) {
            largest = Some(component);
        }
    }
    let Some(component) = largest.filter(|c| c.len() >= config.min_pixels && c.len() > 1) else {
        return FeatureResult::invalid("wire", "1", "no_wire", BTreeMap::new());
    };
    let points: Vec<_> = component
        .iter()
        .map(|&i| [(i % crop.width) as f64, (i / crop.width) as f64])
        .collect();
    let (mean, cov) = covariance(&points);
    let (values, vectors) = eigen(cov);
    let mut axis = vectors[1];
    let approach = config.approach_deg.to_radians();
    if axis[0] * -approach.cos() + axis[1] * -approach.sin() < 0. {
        axis = axis.map(|v| -v);
    }
    let normal = [-axis[1], axis[0]];
    let elongation = (values[1] / values[0].max(1e-9)).sqrt();
    let projections: Vec<_> = points
        .iter()
        .map(|p| (p[0] - mean[0]) * axis[0] + (p[1] - mean[1]) * axis[1])
        .collect();
    let tip_p = projections
        .iter()
        .copied()
        .fold(f64::NEG_INFINITY, f64::max);
    let near: Vec<_> = points
        .iter()
        .zip(&projections)
        .filter(|(_, p)| **p > tip_p - 8. && **p < tip_p - 2.)
        .map(|(p, _)| (p[0] - mean[0]) * normal[0] + (p[1] - mean[1]) * normal[1])
        .collect();
    let lateral = if near.is_empty() {
        0.
    } else {
        near.iter().sum::<f64>() / near.len() as f64
    };
    let start = tip_p - 10.;
    let step = (start + 0.05) - start;
    let samples: Vec<_> = (0..320).map(|i| start + i as f64 * step).collect();
    let profile: Vec<_> = samples
        .iter()
        .map(|s| {
            [-1., 0., 1.]
                .iter()
                .map(|offset| {
                    let x = mean[0] + s * axis[0] + (lateral + offset) * normal[0];
                    let y = mean[1] + s * axis[1] + (lateral + offset) * normal[1];
                    bilinear(&contrast, crop.width, crop.height, x, y)
                })
                .sum::<f64>()
                / 3.
        })
        .collect();
    let body: Vec<_> = samples
        .iter()
        .zip(&profile)
        .filter(|(s, _)| **s < tip_p - 3.)
        .map(|(_, p)| *p)
        .collect();
    let level = if body.is_empty() { 0. } else { median(&body) };
    let diag = diagnostics(
        json!({"elongation":elongation,"pixels":component.len(),"level":level,"noise":noise}),
    );
    if level < config.threshold_sigma * noise {
        return FeatureResult::invalid("wire", "1", "low_contrast", diag);
    }
    let half = level / 2.;
    let Some(i) = (0..profile.len() - 1)
        .rev()
        .find(|&i| profile[i] >= half && profile[i + 1] < half)
    else {
        return FeatureResult::invalid("wire", "1", "no_tip_edge", diag);
    };
    let fraction = (profile[i] - half) / (profile[i] - profile[i + 1]).max(1e-9);
    let s_tip = samples[i] + fraction * (samples[i + 1] - samples[i]);
    let tip = [
        mean[0] + s_tip * axis[0] + lateral * normal[0],
        mean[1] + s_tip * axis[1] + lateral * normal[1],
    ];
    let slope = (profile[i] - profile[i + 1]).abs() / (samples[i + 1] - samples[i]);
    let sigma = noise / 3_f64.sqrt() / slope.max(1e-9);
    let confidence = ((level / noise - config.threshold_sigma) / (2. * config.threshold_sigma))
        .clamp(0., 1.)
        * ((elongation - config.min_elongation) / config.min_elongation).clamp(0., 1.);
    let valid = elongation >= config.min_elongation;
    FeatureResult {
        extractor: "wire".into(),
        version: "1".into(),
        valid,
        values: Some(PointValues {
            u: tip[0] + crop.offset[0],
            v: tip[1] + crop.offset[1],
        }),
        sigma: Some(PointValues { u: sigma, v: sigma }),
        confidence,
        reason: if valid {
            None
        } else {
            Some("not_elongated".into())
        },
        diagnostics: diag,
        saturated_pixels: 0,
    }
}

fn extract_seam(image: &Image, config: &SeamConfig) -> FeatureResult<LineValues> {
    let crop = match prepare(image, config.roi, config.channel.as_deref()) {
        Ok(crop) => crop,
        Err(reason) => return FeatureResult::invalid("seam", "2", reason, BTreeMap::new()),
    };
    let vertical = config.orientation == "vertical";
    let (width, height) = if vertical {
        (crop.height, crop.width)
    } else {
        (crop.width, crop.height)
    };
    if height < 3 || width == 0 {
        return FeatureResult::invalid(
            "seam",
            "2",
            "no_edge",
            diagnostics(json!({"edge_columns":0,"gradient_noise":0.001})),
        );
    }
    let pixel = |x: usize, y: usize| {
        if vertical {
            crop.pixels[x * crop.width + y]
        } else {
            crop.pixels[y * crop.width + x]
        }
    };
    let mut smooth = vec![0.; width * height];
    for y in 0..height {
        for x in 0..width {
            smooth[y * width + x] = 0.5 * pixel(x, y)
                + if x > 0 { 0.25 * pixel(x - 1, y) } else { 0. }
                + if x + 1 < width {
                    0.25 * pixel(x + 1, y)
                } else {
                    0.
                };
        }
    }
    let mut gradient = Vec::with_capacity((height - 2) * width);
    for y in 1..height - 1 {
        for x in 0..width {
            gradient.push((smooth[(y + 1) * width + x] - smooth[(y - 1) * width + x]) / 2.);
        }
    }
    let mid = median(&gradient);
    let mut noise = 1.4826 * median(&gradient.iter().map(|g| (g - mid).abs()).collect::<Vec<_>>());
    if noise == 0. {
        noise = 0.001;
    }
    let rows = height - 2;
    let mut points = Vec::new();
    for col in 0..width {
        let mut row = 0;
        let mut strength = gradient[col].abs();
        for r in 1..rows {
            let value = gradient[r * width + col].abs();
            if value > strength {
                row = r;
                strength = value;
            }
        }
        let mut offset = 0.;
        if row > 0 && row + 1 < rows {
            let a = gradient[(row - 1) * width + col].abs();
            let b = gradient[row * width + col].abs();
            let c = gradient[(row + 1) * width + col].abs();
            let den = a - 2. * b + c;
            if den.abs() > 1e-12 {
                offset = 0.5 * (a - c) / den;
            }
        }
        if strength > config.min_edge_sigma * noise {
            points.push([col as f64, row as f64 + 1. + offset]);
        }
    }
    let mut diag = diagnostics(json!({"edge_columns":points.len(),"gradient_noise":noise}));
    if points.len() < 5 {
        return FeatureResult::invalid("seam", "2", "no_edge", diag);
    }
    let mut rng = fastrand::Rng::with_seed(config.seed);
    let mut best = vec![false; points.len()];
    let mut best_count = 0;
    for _ in 0..config.iterations {
        let i = rng.usize(..points.len());
        let j = rng.usize(..points.len() - 1);
        let j = if j >= i { j + 1 } else { j };
        let d = [points[j][0] - points[i][0], points[j][1] - points[i][1]];
        let length = d[0].hypot(d[1]);
        if length < 1e-9 {
            continue;
        }
        let normal = [-d[1] / length, d[0] / length];
        let inliers: Vec<_> = points
            .iter()
            .map(|p| {
                ((p[0] - points[i][0]) * normal[0] + (p[1] - points[i][1]) * normal[1]).abs()
                    < config.inlier_px
            })
            .collect();
        let count = inliers.iter().filter(|&&v| v).count();
        if count > best_count {
            best = inliers;
            best_count = count;
        }
        if best_count == points.len() {
            break;
        }
    }
    if best_count < 2 {
        return FeatureResult::invalid("seam", "2", "few_inliers", diag);
    }
    let selected: Vec<_> = points
        .iter()
        .zip(&best)
        .filter(|(_, inside)| **inside)
        .map(|(p, _)| *p)
        .collect();
    let (mut mean, cov) = covariance(&selected);
    let (eigenvalues, vectors) = eigen(cov);
    let mut normal = vectors[0];
    if vertical {
        normal.swap(0, 1);
        mean.swap(0, 1);
    }
    if normal[1] < 0. || (normal[1].abs() < 1e-12 && normal[0] < 0.) {
        normal = normal.map(|v| -v);
    }
    let theta_deg = normal[1].atan2(normal[0]).to_degrees();
    let center = [
        (crop.width as f64 - 1.) / 2.,
        (crop.height as f64 - 1.) / 2.,
    ];
    let rho = (mean[0] - center[0]) * normal[0] + (mean[1] - center[1]) * normal[1];
    let residual = eigenvalues[0].max(0.).sqrt();
    let fraction = best_count as f64 / points.len() as f64;
    diag.insert("inlier_fraction".into(), json!(fraction));
    diag.insert("rms_residual".into(), json!(residual));
    diag.insert("center_in_roi".into(), json!(center));
    let min_x = selected.iter().map(|p| p[0]).fold(f64::INFINITY, f64::min);
    let max_x = selected
        .iter()
        .map(|p| p[0])
        .fold(f64::NEG_INFINITY, f64::max);
    let sigma_theta = residual / (max_x - min_x).max(1.);
    let lever = ((mean[0] - center[0]) * -normal[1] + (mean[1] - center[1]) * normal[0]).abs();
    let sigma_rho = (residual / (best_count as f64).sqrt()).hypot(lever * sigma_theta);
    let confidence =
        ((fraction - config.min_inlier_fraction) / (1. - config.min_inlier_fraction)).clamp(0., 1.);
    let valid = fraction >= config.min_inlier_fraction;
    FeatureResult {
        extractor: "seam".into(),
        version: "2".into(),
        valid,
        values: Some(LineValues { theta_deg, rho }),
        sigma: Some(LineValues {
            theta_deg: sigma_theta.to_degrees(),
            rho: sigma_rho,
        }),
        confidence,
        reason: if valid {
            None
        } else {
            Some("few_inliers".into())
        },
        diagnostics: diag,
        saturated_pixels: 0,
    }
}

pub fn roi_center(roi: Option<[i32; 4]>, image_shape: [usize; 2]) -> [f64; 2] {
    if let Some([x, y, w, h]) = roi {
        [
            x as f64 + (w as f64 - 1.) / 2.,
            y as f64 + (h as f64 - 1.) / 2.,
        ]
    } else {
        [
            (image_shape[0] as f64 - 1.) / 2.,
            (image_shape[1] as f64 - 1.) / 2.,
        ]
    }
}
pub fn signed_distance(point: [f64; 2], line: &LineValues, reference: [f64; 2]) -> f64 {
    let theta = line.theta_deg.to_radians();
    (point[0] - reference[0]) * theta.cos() + (point[1] - reference[1]) * theta.sin() - line.rho
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::imageio::{Depth, decode_pgm};
    use std::{fs, path::PathBuf};

    fn aiming_dot(image: &Image, config: &DotConfig) -> FeatureResult<PointValues> {
        super::aiming_dot(image, config).unwrap()
    }
    fn wire_tip(image: &Image, config: &WireConfig) -> FeatureResult<PointValues> {
        super::wire_tip(image, config).unwrap()
    }
    fn seam_line(image: &Image, config: &SeamConfig) -> FeatureResult<LineValues> {
        super::seam_line(image, config).unwrap()
    }

    #[test]
    fn malformed_frames_and_configuration_are_errors_without_hiding_no_target_results() {
        let image = Image::gray8(4, 4, vec![60; 16]).unwrap();
        assert!(
            super::wire_tip(
                &image,
                &WireConfig {
                    polarity: "sideways".into(),
                    ..Default::default()
                }
            )
            .is_err()
        );
        assert!(
            super::seam_line(
                &image,
                &SeamConfig {
                    orientation: "diagonal".into(),
                    ..Default::default()
                }
            )
            .is_err()
        );
        let mut invalid = image.clone();
        invalid.pixels.pop();
        assert!(super::aiming_dot(&invalid, &DotConfig::default()).is_err());
        assert!(
            !super::aiming_dot(&image, &DotConfig::default())
                .unwrap()
                .valid
        );
    }

    #[test]
    fn point_offsets_channel_selection_and_empty_results_keep_the_frame_contract() {
        let mut image = Image {
            width: 7,
            height: 7,
            channels: 3,
            depth: Depth::U16,
            pixels: vec![1000; 7 * 7 * 3],
        };
        for x in 3..=5 {
            image.pixels[(3 * 7 + x) * 3] = 50000;
        }
        let a = aiming_dot(
            &image,
            &DotConfig {
                roi: Some([2, 2, 4, 4]),
                ..Default::default()
            },
        );
        assert_eq!(a.values, Some(PointValues { u: 4., v: 3. }));
        assert_eq!(a.saturated_pixels, 0);
        let b = aiming_dot(
            &image,
            &DotConfig {
                roi: Some([-5, -5, 4, 4]),
                ..Default::default()
            },
        );
        assert_eq!(b.values, Some(PointValues { u: -3., v: -4. }));
        let empty = aiming_dot(
            &image,
            &DotConfig {
                roi: Some([30, 20, 5, 5]),
                ..Default::default()
            },
        );
        assert_eq!(empty.reason.as_deref(), Some("empty_roi"));
        assert_eq!(serde_json::to_value(empty).unwrap()["values"], json!({}));
        assert_eq!(
            aiming_dot(
                &image,
                &DotConfig {
                    channel: Some("green".into()),
                    ..Default::default()
                }
            )
            .reason
            .as_deref(),
            Some("no_spot")
        );
    }

    #[test]
    fn dot_refuses_component_size_and_reports_clipping_to_the_observer() {
        let mut image = Image::gray8(9, 9, vec![0; 81]).unwrap();
        image.pixels[40] = 255;
        assert_eq!(
            aiming_dot(&image, &DotConfig::default()).reason.as_deref(),
            Some("spot_too_small")
        );
        image.pixels[39] = 255;
        image.pixels[41] = 255;
        let result = aiming_dot(&image, &DotConfig::default());
        assert_eq!(result.saturated_pixels, 3);
        assert_eq!(result.confidence, 0.5);
        assert_eq!(
            aiming_dot(
                &image,
                &DotConfig {
                    max_pixels: 2,
                    ..Default::default()
                }
            )
            .reason
            .as_deref(),
            Some("spot_too_large")
        );
        let serialized = serde_json::to_value(result).unwrap();
        assert!(serialized.get("saturated_pixels").is_none());
        assert_eq!(serialized["diagnostics"]["saturated_pixels"], 3);
    }

    #[test]
    fn seam_reference_and_small_regions_have_explicit_outcomes() {
        let line = LineValues {
            theta_deg: 90.,
            rho: -1.1,
        };
        let center = roi_center(Some([10, 15, 70, 40]), [96, 72]);
        assert_eq!(center, [44.5, 34.5]);
        assert!((signed_distance([10., 40.], &line, center) - 6.6).abs() < 1e-12);
        let image = Image::gray8(4, 2, vec![80; 8]).unwrap();
        assert_eq!(
            seam_line(&image, &SeamConfig::default()).reason.as_deref(),
            Some("no_edge")
        );
        assert_eq!(
            wire_tip(&image, &WireConfig::default()).reason.as_deref(),
            Some("no_wire")
        );
    }

    fn compare(expected: &Value, actual: &Value, path: &str) {
        match (expected, actual) {
            (Value::Number(a), Value::Number(b)) => {
                let (a, b) = (a.as_f64().unwrap(), b.as_f64().unwrap());
                assert!((a - b).abs() < 1e-8, "{path}: expected {a}, got {b}");
            }
            (Value::Object(a), Value::Object(b)) => {
                assert_eq!(a.len(), b.len(), "{path}: field count");
                for (key, value) in a {
                    compare(value, &b[key], &format!("{path}/{key}"));
                }
            }
            (Value::Array(a), Value::Array(b)) => {
                assert_eq!(a.len(), b.len(), "{path}: array length");
                for (i, (a, b)) in a.iter().zip(b).enumerate() {
                    compare(a, b, &format!("{path}/{i}"));
                }
            }
            _ => assert_eq!(expected, actual, "{path}"),
        }
    }

    #[test]
    #[ignore = "on-demand saved-image comparison; set PGFUN_SAVED_FEATURE_BASELINE"]
    fn saved_feature_baseline() {
        let root = PathBuf::from(
            std::env::var_os("PGFUN_SAVED_FEATURE_BASELINE")
                .expect("saved-image baseline directory"),
        );
        let baseline: Value =
            serde_json::from_slice(&fs::read(root.join("features.json")).unwrap()).unwrap();
        for case in baseline["cases"].as_array().unwrap() {
            let image =
                decode_pgm(&fs::read(root.join(case["file"].as_str().unwrap())).unwrap()).unwrap();
            let actual = match case["kind"].as_str().unwrap() {
                "dot" => serde_json::to_value(aiming_dot(
                    &image,
                    &serde_json::from_value(case["config"].clone()).unwrap(),
                ))
                .unwrap(),
                "wire" => serde_json::to_value(wire_tip(
                    &image,
                    &serde_json::from_value(case["config"].clone()).unwrap(),
                ))
                .unwrap(),
                "seam" => serde_json::to_value(seam_line(
                    &image,
                    &serde_json::from_value(case["config"].clone()).unwrap(),
                ))
                .unwrap(),
                _ => panic!("unknown saved feature kind"),
            };
            compare(&case["expected"], &actual, case["name"].as_str().unwrap());
            println!("{}: saved feature fields match", case["name"]);
        }
    }
}
