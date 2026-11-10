//! One fixed camera measures the wire endpoint and aiming dot relative to the seam in the same frame.
use crate::{
    client::{Clock, HostClock},
    policy::{FRAME_MAX_AGE_NS, MAX_SIGMA_MM},
};
use anyhow::{Context, Result, bail, ensure};
use hsm_pgfun_observation::{
    capture::{Codec, RawFrame, SourceItem},
    features::{self, DotConfig, FeatureResult, LineValues, PointValues, SeamConfig, WireConfig},
    helper_stream::{CaptureOptions, HelperPaths, HelperSource},
    imageio::{self, Image},
    monotonic_ns,
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeMap,
    fs::OpenOptions,
    io::Write,
    path::{Path, PathBuf},
    sync::mpsc::RecvTimeoutError,
    time::Duration,
};

#[derive(Clone, Debug, Default, Deserialize, Serialize)]
pub struct Observation {
    #[serde(default)]
    pub valid: bool,
    #[serde(default)]
    pub physical: bool,
    #[serde(default)]
    pub noise_qualified: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub values_mm: Option<[f64; 4]>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sigma_mm: Option<[f64; 4]>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sample_ns: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub receive_ns: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub frame_seq: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub camera_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub optics_config_sha256: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reason: Option<String>,
    #[serde(flatten)]
    pub fields: BTreeMap<String, Value>,
}
impl Observation {
    pub fn values(&self) -> Result<[f64; 4]> {
        self.values_mm.context("observation coordinates")
    }
    pub fn sigma(&self) -> Result<[f64; 4]> {
        self.sigma_mm.context("observation uncertainties")
    }
    pub fn stamp(&self) -> Result<u64> {
        self.sample_ns.context("observation timestamp")
    }
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(default)]
pub struct OpticsConfig {
    pub manual_focus: bool,
    pub manual_exposure: bool,
    pub auto_tracking: bool,
    pub mm_per_pixel: [Option<f64>; 2],
    pub stationary_sigma_px: Option<f64>,
    pub noise_qualified: bool,
    pub dot: DotConfig,
    pub wire: WireConfig,
    pub seam: SeamConfig,
    #[serde(flatten)]
    pub fields: BTreeMap<String, Value>,
}
impl Default for OpticsConfig {
    fn default() -> Self {
        Self {
            manual_focus: false,
            manual_exposure: false,
            auto_tracking: true,
            mm_per_pixel: [None, None],
            stationary_sigma_px: None,
            noise_qualified: false,
            dot: DotConfig::default(),
            wire: WireConfig::default(),
            seam: SeamConfig::default(),
            fields: BTreeMap::new(),
        }
    }
}
impl OpticsConfig {
    pub fn scales(&self) -> Result<[f64; 2]> {
        let values = [
            self.mm_per_pixel[0].context("calibrated tangent scale")?,
            self.mm_per_pixel[1].context("calibrated normal scale")?,
        ];
        ensure!(
            values.iter().all(|v| v.is_finite() && *v > 0.),
            "calibrated tangent and normal scales required"
        );
        Ok(values)
    }
    pub fn check_live(&self) -> Result<()> {
        ensure!(
            self.manual_focus && self.manual_exposure && !self.auto_tracking,
            "lock focus, exposure, pan and tracking before measuring"
        );
        ensure!(
            self.dot.roi.is_some() && self.wire.roi.is_some() && self.seam.roi.is_some(),
            "measured dot, wire and seam regions are required"
        );
        Ok(())
    }
}
fn summary<V: Serialize>(feature: &FeatureResult<V>) -> Value {
    json!({"valid":feature.valid,"reason":feature.reason,"confidence":feature.confidence,"details":feature.diagnostics})
}
fn measured<V: Serialize>(feature: &FeatureResult<V>) -> Result<Value> {
    let all = serde_json::to_value(feature)?;
    Ok(json!({"values":all["values"],"sigma":all["sigma"]}))
}
pub fn extract(image: &Image, config: &OpticsConfig) -> Result<Observation> {
    let dot = features::aiming_dot(image, &config.dot)?;
    let wire = features::wire_tip(image, &config.wire)?;
    let seam = features::seam_line(image, &config.seam)?;
    extract_features(image, config, &dot, &wire, &seam)
}
pub fn extract_features(
    image: &Image,
    config: &OpticsConfig,
    dot: &FeatureResult<PointValues>,
    wire: &FeatureResult<PointValues>,
    seam: &FeatureResult<LineValues>,
) -> Result<Observation> {
    let mut out = Observation::default();
    out.fields.insert(
        "diagnostics".into(),
        json!({"dot":summary(dot),"wire":summary(wire),"seam":summary(seam)}),
    );
    out.fields.insert(
        "features".into(),
        json!({"dot":measured(dot)?,"wire":measured(wire)?,"seam":measured(seam)?}),
    );
    if !dot.valid
        || !wire.valid
        || !seam.valid
        || dot.confidence < 0.5
        || wire.confidence < 0.5
        || seam.confidence < 0.5
        || dot.saturated_pixels > 0
    {
        return Ok(out);
    }
    let line = seam.values.as_ref().context("valid seam values")?;
    let line_sigma = seam.sigma.as_ref().context("valid seam uncertainty")?;
    let theta = line.theta_deg.to_radians();
    let normal = [theta.cos(), theta.sin()];
    let tangent = [normal[1], -normal[0]];
    let center = features::roi_center(config.seam.roi, [image.width, image.height]);
    let scale = config.scales()?;
    let floor = config
        .stationary_sigma_px
        .context("stationary pixel jitter floor")?;
    let mut values = [0.; 4];
    let mut sigma = [0.; 4];
    for (index, feature) in [dot, wire].into_iter().enumerate() {
        let point = feature.values.as_ref().context("valid endpoint values")?;
        let uncertainty = feature
            .sigma
            .as_ref()
            .context("valid endpoint uncertainty")?;
        let point = [point.u - center[0], point.v - center[1]];
        let pn = point[0] * normal[0] + point[1] * normal[1];
        let pt = point[0] * tangent[0] + point[1] * tangent[1];
        values[2 * index] = pt * scale[0];
        values[2 * index + 1] = (pn - line.rho) * scale[1];
        let angular = line_sigma.theta_deg.to_radians();
        let st = ((tangent[0] * uncertainty.u).powi(2)
            + (tangent[1] * uncertainty.v).powi(2)
            + (pn * angular).powi(2))
        .sqrt();
        let sn = ((normal[0] * uncertainty.u).powi(2)
            + (normal[1] * uncertainty.v).powi(2)
            + line_sigma.rho.powi(2)
            + (pt * angular).powi(2))
        .sqrt();
        sigma[2 * index] = floor.max(st) * scale[0];
        sigma[2 * index + 1] = floor.max(sn) * scale[1];
    }
    out.valid = true;
    out.values_mm = Some(values);
    out.sigma_mm = Some(sigma);
    out.noise_qualified = config.noise_qualified;
    Ok(out)
}
pub fn frame_image(frame: &RawFrame) -> Result<Image> {
    let width = frame.width.context("frame width")?;
    let height = frame.height.context("frame height")?;
    let image = match &frame.codec {
        Codec::Jpeg => imageio::decode_jpeg(&frame.payload, true),
        Codec::Gray8 => Image::gray8(width, height, frame.payload.clone()),
        Codec::Nv12 => {
            let length = width.checked_mul(height).context("frame dimensions")?;
            ensure!(frame.payload.len() >= length, "short NV12 luma plane");
            imageio::nv12_to_rgb(
                width,
                height,
                &frame.payload[..length],
                &frame.payload[length..],
                true,
            )
        }
        _ => bail!("unsupported observation frame codec"),
    }?;
    ensure!(
        (image.width, image.height) == (width, height),
        "decoded frame dimensions disagree with capture metadata"
    );
    Ok(image)
}
pub fn process_frame(
    frame: &RawFrame,
    config: &OpticsConfig,
    now: u64,
    last_seq: Option<u64>,
    camera: &str,
    config_sha: &str,
) -> Result<Observation> {
    let stamp = frame
        .device_pts_ns
        .filter(|&v| v != 0)
        .or(frame.source_host_ns);
    let mut record = if (frame.width, frame.height) != (Some(3840), Some(2160)) {
        Observation {
            reason: Some("requires_native_3840x2160".into()),
            ..Observation::default()
        }
    } else if !stamp
        .is_some_and(|stamp| stamp > 0 && stamp <= now && now - stamp <= FRAME_MAX_AGE_NS)
    {
        Observation {
            reason: Some("stale_frame".into()),
            ..Observation::default()
        }
    } else if !matches!(frame.codec, Codec::Jpeg | Codec::Gray8 | Codec::Nv12) {
        Observation {
            reason: Some("unsupported_codec".into()),
            ..Observation::default()
        }
    } else {
        extract(&frame_image(frame)?, config)?
    };
    if last_seq.is_some_and(|last| {
        last.checked_add(1)
            .is_none_or(|expected| frame.source_seq != Some(expected))
    }) {
        record.valid = false;
        record.reason = Some("frame_gap".into());
    }
    record.physical = true;
    record.sample_ns = stamp;
    record.receive_ns = Some(now);
    record.frame_seq = frame.source_seq;
    record.camera_id = Some(camera.into());
    record.optics_config_sha256 = Some(config_sha.into());
    Ok(record)
}
pub fn latest(
    path: &Path,
    after_ns: u64,
    timeout: Duration,
    clock: &dyn Clock,
) -> Result<Observation> {
    let deadline = clock.now_ns() + timeout.as_nanos() as u64;
    while clock.now_ns() < deadline {
        ensure!(!crate::interrupted(), "host interrupted");
        let bytes = match std::fs::read(path) {
            Ok(bytes) => Some(bytes),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => None,
            Err(error) => return Err(error.into()),
        };
        if let Some(bytes) = bytes {
            let json = match serde_json::from_slice::<Value>(&bytes) {
                Ok(value) => Some(value),
                Err(error) if error.is_eof() || error.is_syntax() => None,
                Err(error) => return Err(error.into()),
            };
            if let Some(json) = json {
                let sample: Observation = serde_json::from_value(json)?;
                let stamp = sample.stamp()?;
                let now = clock.now_ns();
                ensure!(sample.physical && sample.valid, "features are invalid");
                ensure!(
                    sample.noise_qualified,
                    "stationary camera noise has not been qualified"
                );
                if stamp <= after_ns || stamp > now || now - stamp > FRAME_MAX_AGE_NS {
                    clock.sleep(Duration::from_millis(20));
                    continue;
                }
                let values = sample.values()?;
                let sigma = sample.sigma()?;
                ensure!(
                    values.iter().all(|v| v.is_finite())
                        && sigma.iter().all(|v| v.is_finite() && *v >= 0.),
                    "malformed observation"
                );
                ensure!(
                    sigma.iter().all(|&v| v <= MAX_SIGMA_MM),
                    "feature uncertainty exceeds the optical limit"
                );
                return Ok(sample);
            }
        }
        clock.sleep(Duration::from_millis(20));
    }
    bail!("no fresh valid camera observation")
}

pub struct ObserveOptions {
    pub camera_id: String,
    pub config: PathBuf,
    pub latest: PathBuf,
    pub log: PathBuf,
    pub seconds: f64,
}
pub fn run(root: &Path, options: &ObserveOptions) -> Result<()> {
    let bytes = std::fs::read(&options.config)?;
    let config: OpticsConfig = serde_json::from_slice(&bytes)?;
    config.check_live()?;
    let config_sha = format!("{:x}", Sha256::digest(&bytes));
    let mut source = HelperSource::capture(
        HelperPaths::in_root(root),
        "weld-view",
        &options.camera_id,
        CaptureOptions {
            chroma: true,
            ..CaptureOptions::default()
        },
    );
    source.start()?;
    let clock = HostClock;
    ensure!(
        options.seconds.is_finite() && options.seconds >= 0.,
        "finite capture duration required"
    );
    let deadline = monotonic_ns() + (options.seconds * 1e9) as u64;
    let mut log = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&options.log)?;
    let mut last_seq = None;
    while clock.now_ns() < deadline && !crate::interrupted() {
        let item = match source.read(Duration::from_millis(200)) {
            Ok(Some(item)) => item,
            Ok(None) | Err(RecvTimeoutError::Disconnected) => break,
            Err(RecvTimeoutError::Timeout) => continue,
        };
        let SourceItem::Frame(frame) = item else {
            continue;
        };
        let record = process_frame(
            &frame,
            &config,
            clock.now_ns(),
            last_seq,
            &options.camera_id,
            &config_sha,
        )?;
        last_seq = frame.source_seq;
        serde_json::to_writer(&mut log, &record)?;
        log.write_all(b"\n")?;
        log.flush()?;
        let temporary = options.latest.with_extension("new");
        std::fs::write(&temporary, serde_json::to_vec(&record)?)?;
        std::fs::rename(temporary, &options.latest)?;
    }
    source.stop()?;
    ensure!(!crate::interrupted(), "host interrupted");
    Ok(())
}
