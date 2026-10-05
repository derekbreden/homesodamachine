#!/usr/bin/env python3
"""Gun-positioner observation: cameras, optics, capture, dry learning, fit, validation, proposals.

    observe.py cameras [--save F] [--new-since F]   video devices and their AVFoundation unique IDs
    observe.py clock-check [--out F]                helper clocks against time.monotonic_ns()
    observe.py optics check RECEIPT --camera-id A   check an optics receipt
    observe.py optics inquire --camera-id A --serial /dev/cu.X --baud 9600 --out F --recorded-by NAME
    observe.py optics lock --camera-id A --tcp 192.168.5.163:1259 --apply --zoom 16384 --out F
    observe.py validate-config cameras.json [--measurement]
    observe.py capture --config cameras.json --root ~/gpo-sessions --seconds 10 [--measure]
    observe.py format-report SESSION_DIR
    observe.py simulate --root /tmp/gpo --out /tmp/gpo-analysis
    observe.py fit SESSION_DIR... --out ANALYSIS_DIR
    observe.py propose --model M --report R --observation O --target T
    observe.py check SESSION_DIR
    observe.py export-frame SESSION_DIR --camera cam_a --out frame.png
    observe.py schema [--write]
    observe.py learn check | plan | record | jog | fit | validate | propose | execute ...

No subcommand fires, enables or otherwise commands a laser. `simulate` moves
only a simulated mechanism. Session directories belong outside the repository.
`capture --measure` refuses a configuration that still holds template
placeholders or fails `validate-config --measurement`. `learn record`, `jog` and
`execute` default to the simulator; real motion needs `--backend controller`,
the --i-understand-this-moves-hardware flag, validated files, a passing clock
check, and the operator arming the controller at the tool's prompt.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402

from gpobs import config as gconfig  # noqa: E402
from gpobs import learn  # noqa: E402
from gpobs import helper_stream, optics, response, schema, validation, visca  # noqa: E402
from gpobs.controls import AXES as AXES_CHOICES  # noqa: E402
from gpobs.controls import PROFILES  # noqa: E402
from gpobs.clock import Clock, FakeClock  # noqa: E402
from gpobs.dataset import SessionReader, SessionWriter  # noqa: E402

SCHEMA_PATH = HERE / "observation-schema.json"


def _dump(obj, path: Path | None):
    text = json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    if path:
        Path(path).write_text(text + "\n")
        print(path)
    else:
        print(text)


def _transport(args):
    if args.serial:
        return visca.SerialTransport(args.serial, args.baud)
    spec = args.tcp or args.udp
    host, _, port = spec.partition(":")
    port = int(port or visca.IP_VISCA_PORT)
    return visca.TcpTransport(host, port) if args.tcp else visca.UdpTransport(host, port)


def cmd_cameras(args):
    listing = helper_stream.list_cameras()
    if args.save:
        Path(args.save).expanduser().write_text(json.dumps(listing, indent=1) + "\n")
    if args.new_since:
        before = json.loads(Path(args.new_since).expanduser().read_text())
        known = {d["unique_id"] for d in before.get("devices", [])}
        new = [{k: d.get(k) for k in ("unique_id", "name", "model_id")} for d in listing["devices"]
               if d["unique_id"] not in known]
        _dump({"source": listing["source"], "new_devices": new}, None)
        return 0 if len(new) == 1 else 1
    _dump(listing, None)
    return 0


def cmd_clock_check(args):
    check = helper_stream.clock_check()
    receipt = gconfig.clock_receipt(check, helper_stream.BINARY, Clock().wall_ns())
    _dump(receipt, Path(args.out).expanduser() if args.out else None)
    return 0 if receipt["passed"] else 1


def cmd_optics(args):
    if args.action == "check":
        if not args.file:
            raise SystemExit("optics check needs the receipt file")
        receipt = gconfig.load_receipt(Path(args.file).expanduser(), args.camera_id,
                                       max_age_s=args.max_age_hours * 3600)
        verdict = optics.gate(receipt.state, Clock().monotonic_ns(), receipt_max_age_s=args.max_age_hours * 3600)
        problems = receipt.problems + ([f"measurement gate: {r}" for r in verdict.reasons] if receipt.state else [])
        _dump({"receipt": str(receipt.path), "ok": not problems, "problems": problems,
               "warnings": verdict.warnings if receipt.state else [],
               "state": receipt.state.as_dict() if receipt.state else None}, None)
        return 0 if not problems else 1
    if not (args.serial or args.tcp or args.udp):
        raise SystemExit("choose --serial PORT --baud N, --tcp HOST[:PORT] or --udp HOST[:PORT]")
    client = visca.ViscaClient(_transport(args), args.address, ack_timeout_s=args.ack_timeout,
                               completion_timeout_s=args.completion_timeout, inquiry_timeout_s=args.inquiry_timeout)
    try:
        locked = []
        if args.action == "lock":
            if not args.apply:
                raise SystemExit("lock sends commands that move the camera's lens; pass --apply")
            locked = visca.lock_optics(client, args.zoom, args.focus, args.shutter, args.iris, args.gain,
                                       args.bright, args.wb)
        state, exchanges = visca.read_optics(client, args.camera_id)
        verdict = optics.gate(state, client.clock.monotonic_ns())
        result = {"state": state.as_dict(), "gate": verdict.__dict__,
                  "lock_exchanges": [e.as_dict() for e in locked],
                  "inquiry_exchanges": [e.as_dict() for e in exchanges], "unsolicited": client.unsolicited}
        if args.out:
            tracking = "off" if client.tracking_off_confirmed else "unknown"
            receipt = gconfig.receipt_from_state(state, args.recorded_by, Clock().wall_ns(), tracking,
                                                 result["lock_exchanges"] + result["inquiry_exchanges"])
            _dump(receipt, Path(args.out).expanduser())
            print("fill lens_attachment in the receipt, then check it with: observe.py optics check", args.out)
        else:
            _dump(result, None)
        return 0 if verdict.ok else 1
    finally:
        client.transport.close()


def cmd_validate_config(args):
    purpose = "measurement" if args.measurement else "dry"
    cfg = gconfig.load_config(Path(args.config).expanduser())
    problems = cfg.problems(purpose)
    _dump({"config": str(cfg.path), "purpose": purpose, "ok": not problems, "problems": problems,
           "also_needed_for_measurement": [] if args.measurement else cfg.measurement_problems}, None)
    return 0 if not problems else 1


def _optics_provider(cfg: gconfig.CaptureConfig, clock: Clock) -> optics.OpticsProvider:
    return learn.optics_provider(cfg, clock)


def cmd_capture(args):
    from gpobs.capture import CameraCapture, CameraSpec, CaptureSession, StorePolicy
    purpose = "measurement" if args.measure else "dry"
    try:
        cfg = gconfig.validate(Path(args.config).expanduser(), purpose)
    except gconfig.ConfigError as exc:
        print(f"capture refused: {exc}", file=sys.stderr)
        return 2
    clock = Clock()
    clock_receipt = json.loads(cfg.clock_receipt.read_text()) if cfg.clock_receipt and cfg.clock_receipt.exists() else None
    writer = SessionWriter(Path(args.root).expanduser(), args.label, clock,
                           config={"capture_config": cfg.data, "config_path": str(cfg.path), "purpose": purpose,
                                   "clock_check": clock_receipt,
                                   "not_ready_for_measurement": cfg.measurement_problems})
    captures = []
    for cam in cfg.cameras:
        if purpose == "measurement":
            vf = cam.verified_format
            width, height, fps, subtypes, chroma = (vf["width"], vf["height"], vf["fps"], vf["pixel_format"],
                                                    vf["chroma"])
        else:
            width, height, fps, subtypes, chroma = (args.request_width, args.request_height, args.request_fps,
                                                    args.request_subtypes, args.request_chroma)
        spec = CameraSpec(cam.camera_id, cam.unique_id, cam.name or "", cam.position or "", width, height,
                          cam.codec or "requested", fps, cam.require_native_4k)
        source = helper_stream.HelperSource(cam.camera_id, cam.unique_id, width, height, fps, subtypes=subtypes,
                                            chroma=chroma, mode=args.launch, name=cam.name or "",
                                            log_path=writer.path / f"helper-{cam.camera_id}.log")
        captures.append(CameraCapture(spec, source, writer, clock,
                                      StorePolicy(args.store, args.every_n, args.pixel_format)))
    session = CaptureSession(writer, captures, _optics_provider(cfg, clock), clock, on_unknown="refuse",
                             receipt_max_age_s=cfg.receipt_max_age_s)
    outcome = "closed"
    try:
        session.start()
        if args.measure:
            with session.measurement("capture"):
                time.sleep(args.seconds)
        else:
            time.sleep(args.seconds)
    except KeyboardInterrupt:
        outcome = "interrupted"
    finally:
        session.stop()
        writer.close(outcome)
    print(writer.path)
    report = SessionReader(writer.path).integrity()
    _dump({"ok": report.ok, "stats": report.stats, "problems": report.problems[:20]}, None)
    return 0 if report.ok else 1


def cmd_format_report(args):
    reader = SessionReader(Path(args.session).expanduser())
    report = gconfig.measured_format(reader)
    _dump(report, None)
    return 0 if report and all(r["consistent"] for r in report.values()) else 1


def _groups(readers) -> tuple[dict, dict]:
    groups, purposes = {}, {}
    for r in readers:
        for rec in r.records("trial_start"):
            groups[rec["trial_id"]] = rec["plan"].get("group", rec["purpose"])
            purposes[rec["trial_id"]] = rec["purpose"]
    return groups, purposes


def analyse(session_dirs, out: Path, holdout_fraction: float, seed: int, max_deadband: float,
            min_skill: float) -> tuple[response.ResponseModel, validation.ValidationReport]:
    readers = [SessionReader(Path(d)) for d in session_dirs]
    data = response.assemble(readers)
    groups, purposes = _groups(readers)
    splittable = [t for t in data.trials() if purposes.get(t) in ("probe", "closed_loop")]
    train, hold = validation.split_trials(splittable, holdout_fraction, seed, groups)
    train += [t for t in data.trials() if t not in set(splittable)]
    model = response.fit(data, train, max_deadband=max_deadband)
    report = validation.validate(model, data, hold, min_skill=min_skill)
    out.mkdir(parents=True, exist_ok=True)
    (out / "model.json").write_text(model.to_json() + "\n")
    (out / "validation.json").write_text(report.to_json() + "\n")
    return model, report


def _summary(model, report) -> dict:
    return {"model_id": model.model_id, "deadband_counts": np.round(model.deadband, 1).tolist(),
            "deadband_identified": model.deadband_identified.tolist(), "training_rows": model.n_rows,
            "training_outliers": len(model.outliers), "validation_passed": report.passed,
            "validation_reasons": report.reasons, "validated_axis_directions": report.validated_axis_directions,
            "held_out_trials": len(report.holdout_trials), "held_out_steps": report.n_steps,
            "held_out_outliers": report.n_outliers,
            "held_out_rms": {k: round(v["rms"], 4) for k, v in report.per_feature.items()},
            "baseline_visual_servo_rms": {k: round(v["rms"], 4) for k, v in
                                          report.baseline_visual_servo.get("per_feature", {}).items()}}


def cmd_fit(args):
    model, report = analyse(args.sessions, Path(args.out), args.holdout_fraction, args.seed, args.max_deadband,
                            args.min_skill)
    _dump(_summary(model, report), None)
    return 0 if report.passed else 1


def cmd_simulate(args):
    from gpobs.experiment import Runner, SimulatedObserver
    from gpobs.moves import MoveRecorder
    from gpobs.proposal import CorrectionController, ProposalConfig
    from gpobs.simulation import SimulatedMechanism, SimulatedPositioner, default_truth
    clock = FakeClock()
    truth = default_truth(seed=args.seed, outlier_prob=args.outlier_prob)
    mech = SimulatedMechanism(truth, seed=args.seed + 4)
    writer = SessionWriter(Path(args.root).expanduser(), "simulated-dry-learning", clock,
                           config={"simulation": {"seed": args.seed, "profile": args.profile,
                                                  "outlier_prob": args.outlier_prob,
                                                  "true_deadband_counts": truth.backlash.tolist()}})
    backend = SimulatedPositioner(mech, clock, profile=args.profile)
    recorder = MoveRecorder(backend, writer, clock)
    runner = Runner(recorder, SimulatedObserver(mech, writer, clock), writer, clock)
    runner.engage()
    runner.identify(sizes=tuple(args.sizes), trials_per_size=args.trials_per_size)
    writer.append("session_note", author="simulate", text="identification complete; fitting on logged steps")
    out = Path(args.out)
    model, report = analyse([writer.path], out, args.holdout_fraction, args.seed, args.max_deadband, args.min_skill)
    result = {"session": str(writer.path), "analysis": str(out), **_summary(model, report),
              "true_deadband_counts": truth.backlash.tolist(),
              "j_plus_relative_error": float(np.linalg.norm(model.j_plus - truth.j_plus) / np.linalg.norm(truth.j_plus)),
              "j_minus_relative_error": float(np.linalg.norm(model.j_minus - truth.j_minus) / np.linalg.norm(truth.j_minus))}
    if args.closed_loop and report.passed:
        offset = np.array(args.closed_loop_offset, dtype=float)
        start = mech.true_features()
        goal = start + truth.j_plus @ np.maximum(offset, 0) + truth.j_minus @ np.minimum(offset, 0)
        target = {n: float(v) for n, v in zip(truth.feature_names, goal)}
        cfg = ProposalConfig(max_step_counts=(args.max_step,) * 6, tolerance=args.tolerance)
        loop = runner.closed_loop(CorrectionController(model, report, cfg), target, max_iters=100)
        result["closed_loop"] = {"outcome": loop.outcome, "reason": loop.reason, "moves": len(loop.commands),
                                 "final_true_error_px": np.round(mech.true_features() - goal, 4).tolist()}
    writer.close("closed")
    _dump(result, None)
    return 0 if report.passed else 1


def cmd_propose(args):
    from gpobs.proposal import Observation, ProposalConfig, propose
    model = response.ResponseModel.from_dict(json.loads(Path(args.model).read_text()))
    report = validation.ValidationReport.from_dict(json.loads(Path(args.report).read_text()))
    o = json.loads(Path(args.observation).read_text())
    obs = Observation(o["obs_id"], o["t_start_ns"], o["t_end_ns"], o["values"], o.get("sigma", {}),
                      o.get("confidence", {}), o.get("trial_id"))
    cfg = ProposalConfig(**json.loads(Path(args.config).read_text())) if args.config else ProposalConfig()
    now = args.now_ns if args.now_ns is not None else Clock().monotonic_ns()
    p = propose(model, report, obs, json.loads(Path(args.target).read_text()), cfg, now, args.last_complete_ns,
                args.counts, args.direction)
    _dump(p.as_dict(), None)
    return 0


def cmd_check(args):
    report = SessionReader(Path(args.session)).integrity()
    _dump({"ok": report.ok, "closed": report.closed, "problems": report.problems, "stats": report.stats}, None)
    return 0 if report.ok else 1


def cmd_export_frame(args):
    from gpobs.imageio import encode_png
    reader = SessionReader(Path(args.session).expanduser())
    frames = [f for f in reader.records("frame") if f["camera_id"] == args.camera and f["stored"]
              and (args.seq is None or f["seq"] == args.seq)]
    if not frames:
        raise SystemExit(f"no stored frame for {args.camera}" + (f" with seq {args.seq}" if args.seq is not None else ""))
    image = reader.load_frame(frames[0])
    Path(args.out).expanduser().write_bytes(encode_png(image))
    print(f"{args.out}: camera {args.camera} seq {frames[0]['seq']}, {image.shape[1]} x {image.shape[0]} px; "
          "ROI x and y are column and row from the top-left corner")


def cmd_schema(args):
    text = json.dumps(schema.json_schema(), indent=1) + "\n"
    if args.write:
        SCHEMA_PATH.write_text(text)
        print(SCHEMA_PATH)
    else:
        print(text, end="")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    cm = sub.add_parser("cameras")
    cm.add_argument("--save", help="also write the listing to this file")
    cm.add_argument("--new-since", help="print only devices absent from this earlier --save listing")
    cm.set_defaults(func=cmd_cameras)
    ck = sub.add_parser("clock-check")
    ck.add_argument("--out", help="write the clock-check receipt here")
    ck.set_defaults(func=cmd_clock_check)
    vc = sub.add_parser("validate-config")
    vc.add_argument("config")
    vc.add_argument("--measurement", action="store_true", help="check readiness for measurement capture")
    vc.set_defaults(func=cmd_validate_config)
    fr = sub.add_parser("format-report")
    fr.add_argument("session")
    fr.set_defaults(func=cmd_format_report)

    o = sub.add_parser("optics")
    o.add_argument("action", choices=("inquire", "lock", "check"))
    o.add_argument("file", nargs="?", help="optics receipt (check)")
    o.add_argument("--camera-id", required=True)
    o.add_argument("--max-age-hours", type=float, default=12.0, help="check: receipt age limit")
    o.add_argument("--recorded-by", default="observe.py optics", help="inquire/lock --out: who made the receipt")
    o.add_argument("--serial")
    o.add_argument("--baud", type=int, default=9600)
    o.add_argument("--tcp", help="HOST[:PORT]; bare VISCA, framing unverified")
    o.add_argument("--udp", help="HOST[:PORT]; bare VISCA, framing unverified")
    o.add_argument("--address", type=int, default=1)
    o.add_argument("--ack-timeout", type=float, default=1.0)
    o.add_argument("--completion-timeout", type=float, default=10.0)
    o.add_argument("--inquiry-timeout", type=float, default=1.0)
    o.add_argument("--apply", action="store_true", help="lock: actually send the lens commands")
    for name in ("zoom", "focus", "shutter", "iris", "gain", "bright", "wb"):
        o.add_argument(f"--{name}", type=lambda v: int(v, 0))
    o.add_argument("--out")
    o.set_defaults(func=cmd_optics)

    c = sub.add_parser("capture")
    c.add_argument("--config", required=True)
    c.add_argument("--root", required=True, help="session root, outside the repository")
    c.add_argument("--label", default="capture")
    c.add_argument("--seconds", type=float, default=10.0)
    c.add_argument("--measure", action="store_true",
                   help="record the run as one measurement window; needs validate-config --measurement to pass")
    c.add_argument("--request-width", type=int, default=3840, help="dry capture: size to request")
    c.add_argument("--request-height", type=int, default=2160, help="dry capture: size to request")
    c.add_argument("--request-fps", type=float, default=30.0, help="dry capture: frame rate to request")
    c.add_argument("--request-subtypes", default="dmb1,jpeg,420v,420f,yuvs,2vuy",
                   help="dry capture: AVFoundation subtypes in order of preference")
    c.add_argument("--request-chroma", action="store_true", help="dry capture: keep chroma (nv12)")
    c.add_argument("--store", choices=("measurement", "all", "none"), default="measurement")
    c.add_argument("--every-n", type=int, default=0)
    c.add_argument("--pixel-format", choices=("pgm", "png"), default="pgm")
    c.add_argument("--launch", choices=("open", "exec"), default="open")
    c.set_defaults(func=cmd_capture)

    s = sub.add_parser("simulate")
    s.add_argument("--root", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--seed", type=int, default=7)
    s.add_argument("--profile", choices=sorted(PROFILES), default="loaded-development")
    s.add_argument("--outlier-prob", type=float, default=0.03)
    s.add_argument("--sizes", type=int, nargs="+", default=[16, 32, 64, 256])
    s.add_argument("--trials-per-size", type=int, default=3)
    s.add_argument("--holdout-fraction", type=float, default=0.34)
    s.add_argument("--max-deadband", type=float, default=400.0)
    s.add_argument("--min-skill", type=float, default=0.8)
    s.add_argument("--closed-loop", action="store_true")
    s.add_argument("--closed-loop-offset", type=float, nargs=6, default=[150, -120, 60, -40, 90, -70])
    s.add_argument("--max-step", type=int, default=64, help="per-axis bound; 64 counts is 0.01 mm")
    s.add_argument("--tolerance", type=float, default=0.5)
    s.set_defaults(func=cmd_simulate)

    f = sub.add_parser("fit")
    f.add_argument("sessions", nargs="+")
    f.add_argument("--out", required=True)
    f.add_argument("--holdout-fraction", type=float, default=0.3)
    f.add_argument("--seed", type=int, default=0)
    f.add_argument("--max-deadband", type=float, default=400.0)
    f.add_argument("--min-skill", type=float, default=0.8)
    f.set_defaults(func=cmd_fit)

    p = sub.add_parser("propose")
    p.add_argument("--model", required=True)
    p.add_argument("--report", required=True)
    p.add_argument("--observation", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--config")
    p.add_argument("--now-ns", type=int)
    p.add_argument("--last-complete-ns", type=int)
    p.add_argument("--counts", type=int, nargs=6)
    p.add_argument("--direction", type=int, nargs=6)
    p.set_defaults(func=cmd_propose)

    k = sub.add_parser("check")
    k.add_argument("session")
    k.set_defaults(func=cmd_check)

    sc = sub.add_parser("schema")
    sc.add_argument("--write", action="store_true")
    sc.set_defaults(func=cmd_schema)

    ex = sub.add_parser("export-frame")
    ex.add_argument("session")
    ex.add_argument("--camera", required=True)
    ex.add_argument("--seq", type=int, help="frame sequence number; the first stored frame by default")
    ex.add_argument("--out", required=True, help="PNG to write, for reading pixel coordinates of ROIs")
    ex.set_defaults(func=cmd_export_frame)

    lp = sub.add_parser("learn", help="dry-session learning: check, plan, record, jog, fit, validate, propose, execute")
    ls = lp.add_subparsers(dest="step", required=True)

    def hardware_args(a, backends, default):
        a.add_argument("--backend", choices=backends, default=default)
        a.add_argument("--world", help="simulator state file (default ROOT/simulated-world.json)")
        a.add_argument("--seed", type=int, default=7, help="simulator seed for a new world")
        a.add_argument("--cameras", help="camera configuration (real cameras)")
        a.add_argument("--port", help="controller USB serial device (controller backend)")
        a.add_argument("--launch", choices=("open", "exec"), default="open")
        a.add_argument("--store-frames", choices=("window_first", "measurement", "none"), default="window_first")
        a.add_argument(learn.HARDWARE_FLAG, action="store_true",
                       help="required, with everything else, before any real move")

    a = ls.add_parser("check")
    a.add_argument("--features", required=True)
    a.add_argument("--target")
    a.add_argument("--plan")
    a.add_argument("--cameras")
    a.set_defaults(func=learn.run_check)

    a = ls.add_parser("plan")
    a.add_argument("--out", required=True)
    a.add_argument("--axes", nargs="+", choices=AXES_CHOICES, default=list(AXES_CHOICES))
    a.add_argument("--sizes", type=int, nargs="+", default=[16, 32, 64, 256])
    a.add_argument("--repeats", type=int, default=3)
    a.add_argument("--trials-per-size", type=int, default=2)
    a.add_argument("--max-step", type=int, default=256)
    a.add_argument("--engage-counts", type=int, default=256)
    a.add_argument("--min-motion-z", type=float, default=8.0)
    a.set_defaults(func=learn.run_plan)

    a = ls.add_parser("record")
    a.add_argument("--features", required=True)
    a.add_argument("--root", required=True)
    a.add_argument("--label", default="record")
    a.add_argument("--observations", type=int, default=5)
    a.add_argument("--interval-s", type=float, default=0.5)
    a.add_argument("--target", help="also print the target quantities")
    hardware_args(a, ("simulator", "cameras"), "simulator")
    a.set_defaults(func=learn.run_record)

    a = ls.add_parser("jog")
    a.add_argument("--plan", required=True)
    a.add_argument("--features", required=True)
    a.add_argument("--root", required=True)
    a.add_argument("--label", default="jog")
    hardware_args(a, ("simulator", "controller"), "simulator")
    a.set_defaults(func=learn.run_jog)

    a = ls.add_parser("fit")
    a.add_argument("sessions", nargs="+")
    a.add_argument("--features", required=True)
    a.add_argument("--out", required=True)
    a.add_argument("--holdout-fraction", type=float, default=0.3)
    a.add_argument("--seed", type=int, default=0)
    a.add_argument("--max-deadband", type=float, default=400.0)
    a.set_defaults(func=learn.run_fit)

    a = ls.add_parser("validate")
    a.add_argument("sessions", nargs="+")
    a.add_argument("--model", required=True)
    a.add_argument("--split", help="split.json from learn fit; otherwise every probe trial not used in training")
    a.add_argument("--out", required=True)
    a.add_argument("--min-skill", type=float, default=0.8)
    a.set_defaults(func=learn.run_validate)

    a = ls.add_parser("propose")
    a.add_argument("--model", required=True)
    a.add_argument("--validation", required=True)
    a.add_argument("--features", required=True)
    a.add_argument("--target", required=True)
    src = a.add_mutually_exclusive_group(required=True)
    src.add_argument("--session", help="use this session's last observation and move state")
    src.add_argument("--observation", help="an observation record (JSON)")
    a.add_argument("--out", required=True)
    a.add_argument("--max-step", type=int, default=64)
    a.set_defaults(func=learn.run_propose)

    a = ls.add_parser("execute")
    a.add_argument("--model", required=True)
    a.add_argument("--validation", required=True)
    a.add_argument("--features", required=True)
    a.add_argument("--target", required=True)
    a.add_argument("--root", required=True)
    a.add_argument("--label", default="execute")
    a.add_argument("--max-moves", type=int, default=20)
    a.add_argument("--max-step", type=int, default=64, help="per-axis bound per move (64 counts = 0.01 mm)")
    hardware_args(a, ("simulator", "controller"), "simulator")
    a.set_defaults(func=learn.run_execute)

    args = ap.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
