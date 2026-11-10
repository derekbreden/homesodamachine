//! Saved numerical examples and fixture transports exercise the host without touching hardware.
use crate::{kinematics::Geometry, noise, servo, trajectory};
use serde_json::Value;
use std::collections::BTreeMap;

fn corpus() -> Value {
    serde_json::from_str(include_str!("../tests/fixtures/host.json")).unwrap()
}
fn geometry() -> Geometry {
    serde_json::from_value(corpus()["geometry"].clone()).unwrap()
}
fn parsed<T: serde::de::DeserializeOwned>(key: &str) -> T {
    serde_json::from_value(corpus()[key].clone()).unwrap()
}

#[test]
fn target_segments_preserve_exact_counts_and_the_mechanical_envelope() {
    let geometry = geometry();
    let segments = geometry.split_target([12, -10], [1000, -700]).unwrap();
    assert!(segments.iter().flatten().all(|&value| value.abs() <= 256));
    assert_eq!(
        segments
            .iter()
            .fold([0, 0], |a, b| [a[0] + b[0], a[1] + b[1]]),
        [988, -690]
    );
    assert!(
        geometry
            .split_target([0, 0], [geometry.soft_limit().unwrap() + 1, 0])
            .is_err()
    );
    let a = geometry.aim_point([1, 0]).unwrap();
    let b = geometry.aim_point([0, 0]).unwrap();
    let distance = (0..3).map(|i| (a[i] - b[i]).powi(2)).sum::<f64>().sqrt();
    assert!((distance - geometry.nominal_mm_per_count().unwrap()).abs() < 1e-9);
}
#[test]
fn directional_fit_and_holdouts_match_the_saved_response() {
    let geometry = geometry();
    let rows: Vec<servo::ResponseRow> = parsed("response_rows");
    let model = servo::fit(&geometry, &rows).unwrap();
    let expected: servo::Model = parsed("response_model");
    assert!(!model.qualified);
    for (name, branch) in &model.branches {
        assert_eq!(
            branch.reversal_deadband_counts,
            expected.branches[name].reversal_deadband_counts
        );
        for i in 0..4 {
            for j in 0..2 {
                assert!(
                    (branch.jacobian[i][j] - expected.branches[name].jacobian[i][j]).abs() < 1e-12
                );
            }
        }
    }
    let qualified = servo::qualify(&model, &parsed::<Vec<_>>("response_holdouts")).unwrap();
    assert!(qualified.qualified);
    assert!(servo::qualify(&model, &rows).is_err());
    let delta = servo::correction(
        &geometry,
        &qualified,
        [0.03, 0.02, 0.034, 0.023],
        [1, 1],
        0.010,
    )
    .unwrap()
    .0;
    let expected: [i32; 2] = serde_json::from_value(corpus()["correction"][0].clone()).unwrap();
    assert_eq!(delta, expected);
    assert!(servo::correction(&geometry, &qualified, [0., 0., 1., 0.], [1, 1], 0.010).is_err());
}
#[test]
fn reversal_intervals_are_fitted_and_the_search_boundary_is_refused() {
    let rows = parsed::<Vec<servo::ResponseRow>>("lost_rows");
    let model = servo::fit(&geometry(), &rows).unwrap();
    assert!(
        model
            .branches
            .values()
            .all(|b| b.reversal_deadband_counts == [10, 7])
    );
    assert!(
        servo::qualify(&model, &parsed::<Vec<_>>("lost_holdouts"))
            .unwrap()
            .qualified
    );
    let mut boundary = rows;
    for row in &mut boundary {
        let effective = std::array::from_fn(|i| {
            f64::from(row.delta[i].signum())
                * (f64::from(row.delta[i]).abs() - [32., 7.][i]).max(0.)
        });
        row.change_mm = servo::apply(
            &[[0.001, 0.], [0., 0.001], [0.001, 0.0002], [0.0001, 0.001]],
            effective,
        );
    }
    assert!(
        servo::fit(&geometry(), &boundary)
            .unwrap_err()
            .to_string()
            .contains("search boundary")
    );
}
#[test]
fn periodic_cubic_values_and_envelopes_match_the_saved_examples() {
    let geometry = geometry();
    let mut profile: trajectory::Profile = parsed("profile");
    trajectory::check(&geometry, &profile).unwrap();
    let phases: Vec<f64> = parsed("phases");
    let expected: Vec<[f64; 2]> = parsed("evaluated");
    for (phase, expected) in phases.into_iter().zip(expected) {
        let actual = trajectory::evaluate(&profile, phase).unwrap();
        for i in 0..2 {
            assert!((actual[i] - expected[i]).abs() < 1e-10);
        }
    }
    for speed in [5, 8, 10, 15] {
        assert_eq!(
            trajectory::period_for_speed(speed as f64).unwrap(),
            corpus()["period_for_speed"][speed.to_string()]
                .as_u64()
                .unwrap()
        );
    }
    profile.knots[1][0] = geometry.soft_limit().unwrap();
    assert!(trajectory::check(&geometry, &profile).is_err());
}
fn dry_capture(profile: &trajectory::Profile, offset: u64) -> trajectory::DryCapture {
    let rows = (0..1800)
        .map(|i| {
            let phase = (((i + 1) as f64) / 600.).rem_euclid(1.);
            let elapsed = (i + 1) as f64 * profile.period_us as f64 / 1e6 / 600.;
            let disturbance = [
                8. * (phase * 2. * std::f64::consts::PI).sin(),
                5. * (phase * 2. * std::f64::consts::PI).cos(),
            ];
            let command = trajectory::evaluate(profile, phase).unwrap();
            let change = servo::apply(
                &[[0.001, 0.], [0., 0.001], [0.001, 0.0002], [0.0001, 0.001]],
                [disturbance[0] + command[0], disturbance[1] + command[1]],
            );
            let goal = [0., 0., 0.1, 0.2];
            trajectory::DryRow {
                physical: true,
                valid: true,
                phase,
                elapsed_s: elapsed,
                sigma_mm: [0.001; 4],
                clock_uncertainty_ms: 1.,
                values_mm: std::array::from_fn(|i| goal[i] + change[i]),
                sample_ns: offset + i as u64,
                optics_config_sha256: "0".repeat(64),
                command_counts: None,
                fields: BTreeMap::new(),
            }
        })
        .collect();
    trajectory::DryCapture {
        physical: true,
        profile: profile.clone(),
        rows,
        optics_config_sha256: Some("0".repeat(64)),
        speed_mm_s: 8.,
        direction: "cw".into(),
        index_label: "tube-zero".into(),
        geometry_sha256: None,
    }
}
#[test]
fn periodic_fit_requires_independent_replay_evidence() {
    let geometry = geometry();
    let model = servo::qualify(
        &servo::fit(&geometry, &parsed::<Vec<_>>("response_rows")).unwrap(),
        &parsed::<Vec<_>>("response_holdouts"),
    )
    .unwrap();
    let profile =
        trajectory::Profile::centered(&geometry, trajectory::period_for_speed(8.).unwrap());
    let target = trajectory::Target {
        physical: true,
        values_mm: [0., 0., 0.1, 0.2],
        optics_config_sha256: Some("0".repeat(64)),
        fields: BTreeMap::new(),
    };
    let candidate =
        trajectory::fit(&geometry, &dry_capture(&profile, 10000), &model, &target, 3).unwrap();
    assert!(!candidate.qualified);
    let qualified = trajectory::qualify(
        &geometry,
        &candidate,
        &[
            dry_capture(&candidate, 20000),
            dry_capture(&candidate, 30000),
        ],
    )
    .unwrap();
    assert!(qualified.qualified);
    assert!(qualified.holdout_max_mm.unwrap() <= 0.010);
    assert!(
        trajectory::qualify(
            &geometry,
            &candidate,
            &[
                dry_capture(&candidate, 20000),
                dry_capture(&candidate, 20000)
            ]
        )
        .is_err()
    );
}
#[test]
fn stationary_noise_preserves_the_saved_floor_and_refuses_drift() {
    let mut rows: Vec<noise::NoiseSample> = parsed("stationary");
    let config: noise::NoiseConfig = parsed("noise_config");
    let (out, receipt) = noise::qualify(&rows, &config).unwrap();
    let data = corpus();
    let expected = &data["noise_receipt"];
    assert!(out.noise_qualified);
    for i in 0..4 {
        assert!((receipt.sigma_mm[i] - expected["sigma_mm"][i].as_f64().unwrap()).abs() < 1e-15);
    }
    assert!(noise::qualify(&rows[..100], &config).is_err());
    rows.last_mut().unwrap().values_mm = Some([0.05; 4]);
    assert!(noise::qualify(&rows, &config).is_err());
}

use crate::{
    client::{Client, Clock, HostClock, SessionConfig, Snapshot, Transport},
    observe,
};
use hsm_pgfun_observation::{
    capture::{Codec, RawFrame},
    features::{FeatureResult, LineValues, PointValues},
    imageio::Image,
};
use serde_json::json;
use std::{
    collections::VecDeque,
    io,
    sync::{
        Arc, Mutex,
        atomic::{AtomicU64, Ordering},
    },
    time::Duration,
};

struct TestClock(AtomicU64);
impl TestClock {
    fn new() -> Self {
        Self(AtomicU64::new(2_000_000_000))
    }
}
impl Clock for TestClock {
    fn now_ns(&self) -> u64 {
        self.0.load(Ordering::SeqCst)
    }
    fn sleep(&self, duration: Duration) {
        self.0
            .fetch_add(duration.as_nanos() as u64, Ordering::SeqCst);
    }
}
#[derive(Clone, Copy, PartialEq)]
enum Behavior {
    Normal,
    LostMove,
    LatePing,
    RejectOnce,
    ResetOnMove,
}
#[derive(Default)]
struct WireEvidence {
    commands: Vec<String>,
    closed: bool,
    overlap: bool,
}
struct FixtureTransport {
    evidence: Arc<Mutex<WireEvidence>>,
    queued: VecDeque<u8>,
    snapshot: Snapshot,
    behavior: Behavior,
    delay: bool,
    slow_move: bool,
}
impl FixtureTransport {
    fn new(behavior: Behavior) -> (Self, Arc<Mutex<WireEvidence>>) {
        let geometry = geometry();
        let evidence = Arc::new(Mutex::new(WireEvidence::default()));
        let snapshot=serde_json::from_value(json!({"boot":"abcde001","seq":0,"last_seq":0,"time_us":1,"state":"armed","fault":"none","referenced":true,"count":[0,0],"completed_seq":0,"completed_us":0,"stop_closed":true,"open_limit_mask":0,"supply_adc":1200,"drivers_ok":true,"profile":"pgfun-50-64","counts_per_rev":geometry.counts_per_rev().unwrap(),"max_rate":1000,"geometry_sha256":geometry.sha256,"current_scales":[13,13],"configured_vsense":[0,0],"vsense":[0,0],"microsteps":[64,64]})).unwrap();
        (
            Self {
                evidence: Arc::clone(&evidence),
                queued: VecDeque::new(),
                snapshot,
                behavior,
                delay: false,
                slow_move: false,
            },
            evidence,
        )
    }
    fn reply(&mut self, kind: &str, op: Option<&str>, seq: u32) {
        let mut value = serde_json::to_value(&self.snapshot).unwrap();
        value["type"] = json!(kind);
        value["op"] = json!(op);
        value["seq"] = json!(seq);
        self.queued.extend(serde_json::to_vec(&value).unwrap());
        self.queued.push_back(b'\n');
    }
}
impl Transport for FixtureTransport {
    fn write_all(&mut self, bytes: &[u8]) -> io::Result<()> {
        let command = std::str::from_utf8(bytes).unwrap().trim().to_owned();
        {
            let mut evidence = self.evidence.lock().unwrap();
            evidence.overlap |= !self.queued.is_empty();
            evidence.commands.push(command.clone());
        }
        let fields: Vec<_> = command.split_whitespace().collect();
        match fields[0] {
            "STATUS" => self.reply("status", None, 0),
            "STOP" => {
                self.snapshot.state = crate::client::State::Unreferenced;
                self.snapshot.referenced = false;
                self.reply("stopped", Some("STOP"), 0);
            }
            operation => {
                let seq = fields[2].parse().unwrap();
                if operation == "MOVE2" {
                    if self.slow_move {
                        self.delay = true;
                    }
                    match self.behavior {
                        Behavior::LostMove => {
                            self.snapshot.last_seq = seq;
                            return Ok(());
                        }
                        Behavior::LatePing => {
                            self.snapshot.last_seq = seq;
                            self.reply("ack", Some("PING"), seq);
                            return Ok(());
                        }
                        Behavior::RejectOnce => {
                            self.behavior = Behavior::Normal;
                            self.snapshot.error = Some("out_of_range".into());
                            self.reply("error", Some(operation), seq);
                            self.snapshot.error = None;
                            return Ok(());
                        }
                        Behavior::ResetOnMove => {
                            self.snapshot.boot = "abcde002".into();
                        }
                        Behavior::Normal => {}
                    }
                    self.snapshot.completed_seq = seq;
                    for i in 0..2 {
                        self.snapshot.count[i] += fields[4 + i].parse::<i32>().unwrap();
                    }
                }
                self.snapshot.last_seq = seq;
                self.reply("ack", Some(operation), seq);
            }
        }
        Ok(())
    }
    fn read(&mut self, out: &mut [u8]) -> io::Result<usize> {
        if self.delay && !self.queued.is_empty() {
            self.delay = false;
            std::thread::sleep(Duration::from_millis(5));
        }
        if self.queued.is_empty() {
            return Err(io::ErrorKind::WouldBlock.into());
        }
        let length = out.len().min(17).min(self.queued.len());
        for byte in &mut out[..length] {
            *byte = self.queued.pop_front().unwrap();
        }
        Ok(length)
    }
    fn close(&mut self) -> io::Result<()> {
        self.evidence.lock().unwrap().closed = true;
        Ok(())
    }
}
fn fixture(behavior: Behavior) -> (Client<FixtureTransport>, Arc<Mutex<WireEvidence>>) {
    let (transport, evidence) = FixtureTransport::new(behavior);
    (
        Client::with_transport(
            transport,
            geometry(),
            Arc::new(TestClock::new()),
            SessionConfig {
                reply_timeout: Duration::from_millis(20),
                heartbeat_interval: Duration::from_millis(2),
            },
            None,
        )
        .unwrap(),
        evidence,
    )
}
#[test]
fn uncertain_move_acceptance_stops_resynchronizes_and_never_retries_motion() {
    for behavior in [Behavior::LostMove, Behavior::LatePing] {
        let (mut client, evidence) = fixture(behavior);
        assert!(client.move_counts([3, -2], 100_000).is_err());
        assert!(client.failure().unwrap().is_some());
        let before = evidence.lock().unwrap().commands.clone();
        assert_eq!(before.iter().filter(|c| c.starts_with("MOVE2 ")).count(), 1);
        assert_eq!(&before[before.len() - 2..], ["STOP", "STATUS"]);
        assert!(
            client
                .request("MOVE2", &["100000".into(), "3".into(), "-2".into()])
                .is_err()
        );
        assert_eq!(evidence.lock().unwrap().commands, before);
        client.recover().unwrap();
        assert!(client.failure().unwrap().is_none());
        assert!(!client.status().unwrap().referenced);
        assert!(
            !evidence
                .lock()
                .unwrap()
                .commands
                .iter()
                .any(|c| c.starts_with("REF "))
        );
        client.close().unwrap();
        assert!(evidence.lock().unwrap().closed);
    }
}
#[test]
fn known_rejection_keeps_the_sequence_and_a_reset_invalidates_the_session() {
    let (mut client, evidence) = fixture(Behavior::RejectOnce);
    assert!(client.move_counts([3, 0], 100_000).is_err());
    assert!(client.failure().unwrap().is_none());
    let completed = client.move_counts([3, 0], 100_000).unwrap();
    assert_eq!(completed.count, [3, 0]);
    let moves: Vec<_> = evidence
        .lock()
        .unwrap()
        .commands
        .iter()
        .filter(|c| c.starts_with("MOVE2 "))
        .cloned()
        .collect();
    assert_eq!(moves.len(), 2);
    assert_eq!(moves[0], moves[1]);
    client.close().unwrap();
    let (client, _) = fixture(Behavior::ResetOnMove);
    assert!(client.move_counts([3, 0], 100_000).is_err());
    assert!(client.failure().unwrap().unwrap().contains("reset"));
}
#[test]
fn heartbeat_and_motion_share_the_request_lock_and_close_stops_motion() {
    let (mut transport, evidence) = FixtureTransport::new(Behavior::Normal);
    transport.slow_move = true;
    let mut client = Client::with_transport(
        transport,
        geometry(),
        Arc::new(HostClock),
        SessionConfig {
            reply_timeout: Duration::from_millis(200),
            heartbeat_interval: Duration::from_millis(1),
        },
        None,
    )
    .unwrap();
    client.start_heartbeat().unwrap();
    client
        .request("MOVE2", &["100000".into(), "3".into(), "-2".into()])
        .unwrap();
    let deadline = std::time::Instant::now() + Duration::from_millis(250);
    while !evidence
        .lock()
        .unwrap()
        .commands
        .iter()
        .any(|c| c.starts_with("PING "))
        && std::time::Instant::now() < deadline
    {
        std::thread::sleep(Duration::from_millis(1));
    }
    client.close().unwrap();
    let evidence = evidence.lock().unwrap();
    assert!(!evidence.overlap);
    assert!(evidence.commands.iter().any(|c| c.starts_with("PING ")));
    assert_eq!(evidence.commands.last().unwrap(), "STOP");
    assert!(evidence.closed);
}
#[test]
fn controller_profile_and_motion_arguments_are_checked_before_motion() {
    let (mut transport, evidence) = FixtureTransport::new(Behavior::Normal);
    transport.snapshot.current_scales = [12, 13];
    assert!(
        Client::with_transport(
            transport,
            geometry(),
            Arc::new(TestClock::new()),
            SessionConfig::default(),
            None
        )
        .is_err()
    );
    assert!(evidence.lock().unwrap().closed);
    let (client, evidence) = fixture(Behavior::Normal);
    let before = evidence.lock().unwrap().commands.len();
    assert!(client.move_counts([257, 0], 100_000).is_err());
    assert!(client.move_counts([0, 0], 100_000).is_err());
    assert!(client.move_counts([1, 0], 99_999).is_err());
    assert_eq!(evidence.lock().unwrap().commands.len(), before);
}
#[test]
fn stale_or_unqualified_camera_records_never_enter_control() {
    let path =
        std::env::temp_dir().join(format!("hsm-pgfun-observation-{}.json", std::process::id()));
    let clock = TestClock::new();
    let mut record = json!({"physical":true,"valid":true,"noise_qualified":true,"sample_ns":1_000_000_000_u64,"values_mm":[0.,0.,0.,0.],"sigma_mm":[0.001,0.001,0.001,0.001]});
    std::fs::write(&path, serde_json::to_vec(&record).unwrap()).unwrap();
    assert!(observe::latest(&path, 0, Duration::from_millis(30), &clock).is_err());
    record["sample_ns"] = json!(clock.now_ns());
    std::fs::write(&path, serde_json::to_vec(&record).unwrap()).unwrap();
    assert!(observe::latest(&path, 0, Duration::from_millis(30), &clock).is_ok());
    record["noise_qualified"] = json!(false);
    std::fs::write(&path, serde_json::to_vec(&record).unwrap()).unwrap();
    assert!(observe::latest(&path, 0, Duration::from_millis(30), &clock).is_err());
    std::fs::remove_file(path).unwrap();
}
#[test]
fn seam_angle_uncertainty_grows_at_the_endpoint_and_clipped_dots_are_refused() {
    let mut point = FeatureResult {
        extractor: "dot".into(),
        version: "1".into(),
        valid: true,
        values: Some(PointValues { u: 1050., v: 50. }),
        sigma: Some(PointValues { u: 0.1, v: 0.1 }),
        confidence: 1.,
        reason: None,
        diagnostics: BTreeMap::new(),
        saturated_pixels: 0,
    };
    let seam = FeatureResult {
        extractor: "seam".into(),
        version: "1".into(),
        valid: true,
        values: Some(LineValues {
            theta_deg: 90.,
            rho: 0.,
        }),
        sigma: Some(LineValues {
            theta_deg: 1.,
            rho: 0.1,
        }),
        confidence: 1.,
        reason: None,
        diagnostics: BTreeMap::new(),
        saturated_pixels: 0,
    };
    let mut config = observe::OpticsConfig::default();
    config.seam.roi = Some([0, 0, 100, 100]);
    config.mm_per_pixel = [Some(0.001); 2];
    config.stationary_sigma_px = Some(0.1);
    config.noise_qualified = true;
    let image = Image::gray8(1100, 100, vec![0; 1100 * 100]).unwrap();
    let result = observe::extract_features(&image, &config, &point, &point, &seam).unwrap();
    assert!(result.valid);
    assert!(result.sigma().unwrap()[1] > 0.017);
    point.saturated_pixels = 1;
    assert!(
        !observe::extract_features(&image, &config, &point, &point, &seam)
            .unwrap()
            .valid
    );
}
#[test]
fn frame_size_timestamp_and_sequence_guards_precede_feature_work() {
    let config = observe::OpticsConfig::default();
    let mut frame = RawFrame {
        payload: vec![],
        codec: Codec::Gray8,
        width: Some(3840),
        height: Some(2160),
        source_seq: Some(1),
        device_pts_ns: Some(1_000_000_000),
        source_host_ns: None,
        duration_ns: None,
        subtype: None,
    };
    let stale =
        observe::process_frame(&frame, &config, 2_000_000_000, None, "fixed", "hash").unwrap();
    assert_eq!(stale.reason.as_deref(), Some("stale_frame"));
    frame.width = Some(1920);
    frame.device_pts_ns = Some(2_000_000_000);
    let size =
        observe::process_frame(&frame, &config, 2_000_000_000, None, "fixed", "hash").unwrap();
    assert_eq!(size.reason.as_deref(), Some("requires_native_3840x2160"));
    let gap =
        observe::process_frame(&frame, &config, 2_000_000_000, Some(1), "fixed", "hash").unwrap();
    assert_eq!(gap.reason.as_deref(), Some("frame_gap"));
    assert!(gap.physical);
    assert!(!gap.valid);
}
