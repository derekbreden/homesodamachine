"""The controls contract: constants, profiles, Client signatures, receipt mapping. No serial port."""

import inspect
import json
import math
import unittest

from support import FakeClient, FakeDevice, tmpdir

from gpobs import controls, learn
from gpobs.clock import FakeClock
from gpobs.controls import (AXES, CONSERVATIVE_MAX_RATE, COUNTS_PER_MM, MAX_JOG_COUNTS, SOFT_MAX, SOFT_MIN,
                            ControlsClientBackend, ReceiptError, driver_profile_header, firmware_constants,
                            host_modules, minimum_duration_us, nominal_rms_current_a, profile_problems,
                            profile_summary, receipt_from_client_move)
from gpobs.dataset import SessionReader, SessionWriter
from gpobs.moves import MoveCommand, MoveRecorder, PositionerBackend, RecordOnlyBackend
from gpobs.simulation import PROFILES, SimulatedMechanism, SimulatedPositioner, default_truth
from gpobs.timeline import frames_in_supply_cycles, supply_cycles


class FirmwareConstants(unittest.TestCase):
    def test_parser_reads_real_headers(self):
        fw = firmware_constants()
        self.assertEqual(fw["kCountsPerMm"], COUNTS_PER_MM)
        self.assertEqual(fw["kCountsPerMm"], 6400)
        self.assertEqual(fw["kMinCount"], list(SOFT_MIN))
        self.assertEqual(fw["kMaxCount"], list(SOFT_MAX))
        self.assertEqual(fw["kMaxJogCounts"], 640)
        self.assertEqual((fw["kMinDurationUs"], fw["kMaxDurationUs"]), (100_000, 2_000_000))
        self.assertEqual(fw["kMaxAcceleration"], 12_000)
        # kMaxRate is defined through the build-profile macro; its in-header default resolves.
        self.assertIn("kMaxRate", fw)
        self.assertEqual(fw["macro_defaults"]["kMaxRate"]["macro"], "POSITIONER_MAX_RATE")
        self.assertIn(fw["kMaxRate"], [p["max_rate"] for p in PROFILES.values()])

    def test_parser_handles_macro_and_literal_forms(self):
        d = tmpdir("headers")
        geometry = d / "geometry_generated.h"
        geometry.write_text("constexpr int32_t kCountsPerMm = 6400;\n"
                            "constexpr std::array<int32_t, 6> kMinCount = {-1, -2, -3, -4, -5, -6};\n"
                            "constexpr std::array<int32_t, 6> kMaxCount = {1, 2, 3, 4, 5, 6};\n")
        macro = d / "macro.h"
        macro.write_text("#ifndef POSITIONER_MAX_RATE\n#define POSITIONER_MAX_RATE 1000\n#endif\n"
                         "constexpr uint32_t kMaxRate = POSITIONER_MAX_RATE; // peak\n")
        literal = d / "literal.h"
        literal.write_text("constexpr uint32_t kMaxRate = 2000; // peak\n")
        self.assertEqual(firmware_constants(macro, geometry)["kMaxRate"], 1000)
        self.assertEqual(firmware_constants(literal, geometry)["kMaxRate"], 2000)
        self.assertEqual(firmware_constants(literal, geometry)["kMinCount"], [-1, -2, -3, -4, -5, -6])

    def test_canonical_geometry_and_angular_bounds(self):
        """Soft bounds recomputed here from the canonical geometry file and the clevis law."""
        import json
        import math
        k = host_modules().kinematics
        g = json.loads(k.GEOMETRY_PATH.read_text())
        self.assertEqual(AXES, ("X", "Y", "Z", "U", "V", "W"))
        r, l0 = g["angular_actuator"]["r_mm"], g["angular_actuator"]["L0_mm"]
        self.assertEqual((l0, r), (180.0, 150.0))
        per_mm = g["nominal_motion"]["sixteen_microstep_command_pulses_per_mm"]
        lo_mm, hi_mm = g["linear_limits_mm"]["soft"]
        self.assertEqual(list(SOFT_MIN[:3]), [math.ceil(lo_mm * per_mm)] * 3)
        self.assertEqual(list(SOFT_MAX[:3]), [math.floor(hi_mm * per_mm)] * 3)
        soft = g["angular_limits_deg"]

        def extension(deg):
            a = math.radians(deg)
            return math.sqrt(l0**2 + 2 * l0 * r * math.sin(a) + 2 * r**2 * (1 - math.cos(a))) - l0

        for i, name in enumerate(("yaw", "pitch", "roll")):
            lo, hi = soft.get("soft_by_axis", {}).get(name, soft["soft"])
            self.assertEqual(SOFT_MIN[3 + i], math.ceil(extension(lo) * per_mm), name)
            self.assertEqual(SOFT_MAX[3 + i], math.floor(extension(hi) * per_mm), name)
        fw = firmware_constants()
        self.assertEqual((fw["kMinCount"], fw["kMaxCount"]), (list(SOFT_MIN), list(SOFT_MAX)))


class RateProfiles(unittest.TestCase):
    def test_duration_never_shorter_than_counts_over_rate(self):
        for rate in (1000, 2000):
            for n in (1, 7, 40, 160, 333, 640):
                d = minimum_duration_us([n, 0, 0, 0, 0, -n // 2], rate)
                self.assertGreaterEqual(d, n / rate * 1e6)
                self.assertGreaterEqual(d, 100_000)

    def test_unreported_rate_assumes_the_slowest_profile(self):
        self.assertEqual(CONSERVATIVE_MAX_RATE, min(p["max_rate"] for p in PROFILES.values()))

    def test_both_profiles_accept_their_own_durations(self):
        for profile, spec in PROFILES.items():
            rate = spec["max_rate"]
            sim = SimulatedPositioner(SimulatedMechanism(default_truth()), FakeClock(), profile=profile)
            self.assertEqual(sim.max_rate, rate)
            for n in range(1, MAX_JOG_COUNTS + 1, 7):
                counts = [n, -n, n // 2, 0, 0, 1]
                self.assertIsNone(sim.firmware_check(counts, minimum_duration_us(counts, rate)), (profile, n))

    def test_bench_durations_are_too_short_for_loaded_profile(self):
        loaded = SimulatedPositioner(SimulatedMechanism(default_truth()), FakeClock(), profile="loaded-development")
        bench_duration = minimum_duration_us([640, 0, 0, 0, 0, 0], PROFILES["bench"]["max_rate"])
        self.assertEqual(loaded.firmware_check([640, 0, 0, 0, 0, 0], bench_duration), "rate")

    def test_recorder_uses_backend_rate_and_refuses_short_durations(self):
        for profile in PROFILES:
            clock = FakeClock()
            backend = SimulatedPositioner(SimulatedMechanism(default_truth()), clock, profile=profile)
            with SessionWriter(tmpdir(f"rate-{profile}"), "rate", clock) as w:
                rec = MoveRecorder(backend, w, clock)
                cmd, out = rec.execute([640, 0, -640, 0, 320, 0], "probe_jog")
                self.assertEqual(out.status, "done")
                self.assertGreaterEqual(cmd.duration_us, 1.5 * 640 / backend.max_rate * 1e6)
                with self.assertRaises(ValueError):
                    rec.execute([640, 0, 0, 0, 0, 0], "probe_jog", duration_us=cmd.duration_us - 1000)
                self.assertEqual(backend.rejected, [])

    def test_unreported_rate_is_conservative(self):
        clock = FakeClock()
        device = FakeDevice(clock, max_rate=1000, report_max_rate=False)
        client = FakeClient.with_device(device)
        # The controls Client refuses such a controller at connection; the adapter's own fallback stays slow.
        with self.assertRaises(RuntimeError):
            host_modules().positioner.Client.check_profile(device.status())
        backend = ControlsClientBackend(client, None, clock, read_drivers=False)
        self.assertEqual(backend.max_rate, CONSERVATIVE_MAX_RATE)
        self.assertEqual(backend.max_rate_source, "conservative_default")
        with SessionWriter(tmpdir("conservative"), "c", clock) as w:
            rec = MoveRecorder(backend, w, clock, allow_hardware=True)
            _, out = rec.execute([640, 0, 0, 0, 0, 0], "probe_jog")
            self.assertEqual(out.status, "done")

    def test_split_move_uses_controls_split_target(self):
        for profile in PROFILES:
            clock = FakeClock()
            backend = SimulatedPositioner(SimulatedMechanism(default_truth()), clock, profile=profile)
            with SessionWriter(tmpdir(f"split-{profile}"), "split", clock) as w:
                rec = MoveRecorder(backend, w, clock)
                done = rec.execute_split([2000, -1300, 0, 641, 0, -5], "return")
                self.assertTrue(all(out.status == "done" for _, out in done))
                self.assertTrue(all(max(map(abs, cmd.counts)) <= MAX_JOG_COUNTS for cmd, _ in done))
                self.assertEqual(backend.counts, [2000, -1300, 0, 641, 0, -5])
                for cmd, _ in done:
                    self.assertGreaterEqual(cmd.duration_us, max(map(abs, cmd.counts)) / backend.max_rate * 1e6)


def _changed(values, axis, new):
    out = list(values)
    out[AXES.index(axis)] = new
    return out


class DriverProfile(unittest.TestCase):
    """Per-axis current scales and VSENSE: the toolkit expects exactly what the controls package exports."""

    def test_profiles_are_the_controls_host_export(self):
        pos = host_modules().positioner
        self.assertEqual(sorted(PROFILES), sorted(pos.PROFILES))
        self.assertEqual(sorted(pos.VSENSE_PROFILES), sorted(pos.PROFILES))
        for name, (scales, rate) in pos.PROFILES.items():
            self.assertEqual(PROFILES[name]["current_scales"], list(scales), name)
            self.assertEqual(PROFILES[name]["vsense"], list(pos.VSENSE_PROFILES[name]), name)
            self.assertEqual(PROFILES[name]["max_rate"], rate, name)
            self.assertEqual(len(scales), len(AXES))

    def test_host_export_matches_the_firmware_header(self):
        """driver_profile.h's kCurrentScales and kVsense, per POSITIONER_LOADED_PROFILE, equal the host export."""
        header = driver_profile_header()["profiles"]
        self.assertEqual(sorted(header), sorted(PROFILES))
        for name, spec in header.items():
            self.assertEqual(spec["current_scales"], PROFILES[name]["current_scales"], name)
            self.assertEqual(spec["vsense"], PROFILES[name]["vsense"], name)

    def test_build_manifest_matches(self):
        """The controls build manifest states the same profiles, sense resistance and nominal currents."""
        manifest = json.loads(controls.BUILD_MANIFEST.read_text())
        built = {p["name"]: p for p in manifest["profiles"]}
        self.assertEqual(sorted(built), sorted(PROFILES))
        scope = manifest["current_estimate_scope"]
        self.assertEqual(scope["sense_resistor_nominal_ohm"], controls.RSENSE_OHM)
        self.assertEqual(scope["internal_sense_resistance_ohm"], controls.INTERNAL_SENSE_OHM)
        for name, spec in PROFILES.items():
            b = built[name]
            self.assertEqual(b["current_scales"], spec["current_scales"], name)
            self.assertEqual(b["configured_vsense"], spec["vsense"], name)
            self.assertEqual(b["max_rate_count_s"], spec["max_rate"], name)
            self.assertEqual(b["microsteps"], 16, name)            # the microstep setting the gates require
            self.assertEqual(b["nominal_VFS_V"], [controls.VFS_V[v] for v in spec["vsense"]], name)
            for ours, theirs in zip(spec["nominal_rms_current_a"], b["nominal_R110_current_rms_A"]):
                self.assertAlmostEqual(ours, theirs, delta=1e-4, msg=name)

    def test_nominal_rms_current_includes_vsense(self):
        for cs in (0, 10, 14, 22, 31):
            for vsense, vfs in ((0, 0.325), (1, 0.18)):
                self.assertAlmostEqual(nominal_rms_current_a(cs, vsense),
                                       (cs + 1) / 32 * vfs / (0.110 + 0.02) / math.sqrt(2), places=12)
        with self.assertRaises(ValueError):
            nominal_rms_current_a(10, 2)
        stated = driver_profile_header()["stated_nominal_rms"]
        used = {(c, v) for p in PROFILES.values() for c, v in zip(p["current_scales"], p["vsense"])}
        self.assertEqual({(c, v) for c, v, _ in stated}, used, "driver_profile.h states every pair in use")
        for cs, vsense, amps in stated:           # the header states three decimals
            self.assertAlmostEqual(nominal_rms_current_a(cs, vsense), amps, delta=0.0005, msg=(cs, vsense))
        for name, spec in PROFILES.items():
            self.assertEqual(spec["nominal_rms_current_a"],
                             [round(nominal_rms_current_a(c, v), 4) for c, v in zip(spec["current_scales"],
                                                                                    spec["vsense"])], name)
        summary = profile_summary(FakeDevice(FakeClock(), max_rate=1000).status())
        self.assertTrue(summary["matches_controls_export"])
        self.assertIn("nominal", summary["basis"])
        self.assertIn("not calibrated", summary["basis"])

    def test_fixtures_report_the_exported_profile(self):
        check = host_modules().positioner.Client.check_profile
        for name, spec in PROFILES.items():
            device = FakeDevice(FakeClock(), max_rate=spec["max_rate"])
            sim = SimulatedPositioner(SimulatedMechanism(default_truth()), FakeClock(), profile=name)
            for status in (device.status(), sim.status()):
                check(status)
                self.assertEqual(profile_problems(status), [], name)
                self.assertEqual(learn.controller_refusals(status), [], name)
                self.assertEqual((status["current_scales"], status["configured_vsense"], status["vsense"]),
                                 (spec["current_scales"], spec["vsense"], spec["vsense"]), name)
            rows = device.command("DRIVERS")
            self.assertEqual([r["configured_cs"] for r in rows], spec["current_scales"])
            self.assertEqual([r["cs_actual"] for r in rows], spec["current_scales"])
            self.assertEqual([r["configured_vsense"] for r in rows], spec["vsense"])
            self.assertEqual([r["vsense"] for r in rows], spec["vsense"])
            device.drivers_ok = False
            self.assertEqual(device.status()["vsense"], [None] * 6)    # unverified readings are null

    def test_profile_check_agrees_with_the_controls_client(self):
        """profile_problems() accepts exactly the STATUS lines Client.check_profile accepts."""
        check = host_modules().positioner.Client.check_profile
        loaded, bench = PROFILES["loaded-development"], PROFILES["bench"]
        base = FakeDevice(FakeClock(), max_rate=loaded["max_rate"]).status()
        flipped_z = _changed(loaded["vsense"], "Z", 1 - loaded["vsense"][AXES.index("Z")])
        cases = {
            "as exported": ({}, True),
            "pitch scale differs": ({"current_scales": _changed(loaded["current_scales"], "V",
                                                                 loaded["current_scales"][AXES.index("V")] + 1)},
                                    False),
            "Z scale differs": ({"current_scales": _changed(loaded["current_scales"], "Z",
                                                             loaded["current_scales"][AXES.index("Z")] - 1)}, False),
            "Z configured VSENSE differs": ({"configured_vsense": flipped_z}, False),
            "decoded Z VSENSE differs while drivers_ok": ({"vsense": flipped_z}, False),
            "decoded VSENSE unverified while drivers_ok": ({"vsense": [None] * 6}, False),
            "decoded VSENSE differs, drivers not ok": ({"drivers_ok": False, "vsense": flipped_z}, True),
            "decoded VSENSE null, drivers not ok": ({"drivers_ok": False, "vsense": [None] * 6}, True),
            "no configured VSENSE": ({"configured_vsense": None}, False),
            "other profile's rate": ({"max_rate": bench["max_rate"]}, False),
            "other profile's currents": ({"current_scales": bench["current_scales"],
                                          "configured_vsense": bench["vsense"], "vsense": bench["vsense"]}, False),
            "unknown profile": ({"profile": "custom"}, False),
        }
        for name, (change, accepted) in cases.items():
            with self.subTest(name):
                status = {**base, **change}
                try:
                    check(status)
                    client_accepts = True
                except RuntimeError:
                    client_accepts = False
                self.assertEqual(client_accepts, accepted)
                self.assertEqual(profile_problems(status) == [], accepted, profile_problems(status))
                refusals = learn.controller_refusals(status)
                self.assertEqual(any(r.startswith("driver profile: ") for r in refusals), not accepted, refusals)
                self.assertEqual(profile_summary(status)["matches_controls_export"], accepted)


class ClientContract(unittest.TestCase):
    def test_fake_client_matches_real_signatures(self):
        real = host_modules().positioner.Client
        for name in ("__init__", "status", "request", "stop", "start_heartbeat", "move", "move_to_counts",
                     "drivers", "close"):
            self.assertTrue(hasattr(real, name), f"controls Client lost {name}")
            self.assertEqual(inspect.signature(getattr(real, name)), inspect.signature(getattr(FakeClient, name)),
                             f"controls Client.{name} signature changed; update the adapter and FakeClient")

    def test_move_command_bounds_match_client_move(self):
        real_move = host_modules().positioner.Client.move

        class Sent(Exception):
            pass

        class Stub:
            def request(self, *args):
                raise Sent(args)

        cases = [([640, 0, 0, 0, 0, 0], 1_000_000), ([641, 0, 0, 0, 0, 0], 1_000_000),
                 ([0, 0, 0, 0, 0, -640], 100_000), ([1, 0, 0, 0, 0, 0], 99_999), ([1, 0, 0, 0, 0, 0], 2_000_001),
                 ([0] * 6, 1_000_000), ([1, 2, 3, 4, 5, -640], 2_000_000)]
        for counts, duration in cases:
            try:
                real_move(Stub(), counts, duration)
                client_ok = None
            except Sent:
                client_ok = True
            except ValueError:
                client_ok = False
            try:
                MoveCommand("c", tuple(counts), duration, "probe_jog")
                ours = True
            except ValueError:
                ours = False
            self.assertEqual(ours, client_ok, (counts, duration))

    def test_interfaces_have_no_laser_vocabulary(self):
        banned = ("laser", "fire", "emission", "emit", "trigger", "weld", "power")
        for cls in (PositionerBackend, RecordOnlyBackend, ControlsClientBackend, SimulatedPositioner, MoveRecorder):
            for name in dir(cls):
                if not name.startswith("__"):
                    self.assertFalse(any(b in name.lower() for b in banned), f"{cls.__name__}.{name}")
        real = host_modules().positioner.Client
        for name in dir(real):
            if not name.startswith("__"):
                self.assertFalse(any(b in name.lower() for b in ("laser", "fire", "emission")), name)


class ReceiptMapping(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock(start_ns=5_000_000_000)
        self.device = FakeDevice(self.clock, max_rate=1000)
        self.log = tmpdir("receipts") / f"client-{id(self)}.jsonl"
        self.client = FakeClient.with_device(self.device, self.log)
        self.backend = ControlsClientBackend(self.client, self.log, self.clock)
        self.writer = SessionWriter(tmpdir("receipt-sessions"), "receipt", self.clock)

    def tearDown(self):
        self.writer.close()
        self.client.close()

    def test_hardware_backend_needs_explicit_permission(self):
        with self.assertRaises(PermissionError):
            MoveRecorder(self.backend, self.writer, self.clock)
        with self.assertRaises(PermissionError):
            self.backend.prepare(datum_established=False)

    def test_move_maps_onto_one_timeline(self):
        rec = MoveRecorder(self.backend, self.writer, self.clock, allow_hardware=True)
        for _ in range(4):   # pings build the clock map, as the heartbeat does
            self.client.request("PING")
        cmd, out = rec.execute([320, -160, 0, 64, 0, 0], "probe_jog", "t1")
        self.assertEqual(out.status, "done")
        self.assertEqual(self.backend.max_rate, 1000)
        self.assertGreaterEqual(cmd.duration_us, 1.5 * 320 / 1000 * 1e6)
        records = SessionReader(self.writer.path).records()
        command = next(r for r in records if r["kind"] == "move_command")
        ack = next(r for r in records if r["kind"] == "move_ack")
        done = next(r for r in records if r["kind"] == "move_complete")
        log = [json.loads(line) for line in self.log.read_text().splitlines()]
        seq = int(next(r for r in log if r.get("command", "").startswith("MOVE6"))["command"].split()[2])
        ack_log = next(r for r in log if r["type"] == "device_reply" and r["device"]["type"] == "ack"
                       and r["device"]["seq"] == seq)
        self.assertEqual(ack_log["device"]["op"], "MOVE6")
        done_log = next(r for r in log if r["type"] == "device_reply" and r["device"].get("completed_seq") == seq)
        self.assertEqual(ack["ack_mono_ns"], ack_log["host_receive_ns"])
        self.assertEqual(done["complete_mono_ns"], done_log["host_receive_ns"])
        self.assertLessEqual(command["issued_mono_ns"], ack["ack_mono_ns"])
        self.assertLessEqual(ack["ack_mono_ns"], done["complete_mono_ns"])
        self.assertEqual(done["seq"], seq)
        self.assertEqual(done["controller_time_us"], done_log["device"]["completed_us"])
        self.assertEqual(done["reported_counts"], [320, -160, 0, 64, 0, 0])
        self.assertEqual(done["controller"]["max_rate"], 1000)
        self.assertEqual([d["cs_actual"] for d in done["driver_state"]],
                         PROFILES["loaded-development"]["current_scales"])
        self.assertEqual([d["vsense"] for d in done["driver_state"]], PROFILES["loaded-development"]["vsense"])
        self.assertTrue(all("sample_us" in d for d in done["driver_state"]))
        true_completion = self.device.completion_host_ns[seq]
        self.assertLessEqual(abs(done["completion_mapped_mono_ns"] - true_completion),
                             done["completion_mapping_uncertainty_ns"] + 1000)
        self.assertLessEqual(true_completion, done["complete_mono_ns"])
        exchanges = [r for r in records if r["kind"] == "clock_exchange"]
        self.assertTrue(exchanges and all(r["boot"] == self.device.boot for r in exchanges))
        self.assertEqual(rec.direction, [1, -1, 0, 1, 0, 0])

    def test_only_the_move6_ack_is_the_moves_acceptance(self):
        """A late PING ack carrying the move's sequence is never taken for the MOVE6 ack."""
        boot, seq, counts, duration = "0badc0de", 12, [64, 0, 0, 0, 0, 0], 200_000
        command = {"type": "host_command", "host_send_ns": 1_000,
                   "command": f"MOVE6 {boot} {seq} {duration} " + " ".join(map(str, counts))}

        def reply(ns, **device):
            return {"type": "device_reply", "host_receive_ns": ns, "device": {"boot": boot, **device}}

        early_ping = reply(500, type="ack", op="PING", seq=seq, time_us=40, vm_epoch=0, completed_seq=seq)
        ping = reply(1_100, type="ack", op="PING", seq=seq, time_us=50, vm_epoch=0, completed_seq=seq)
        ack = reply(1_200, type="ack", op="MOVE6", seq=seq, time_us=60, vm_epoch=2, completed_seq=seq - 1)
        done = reply(5_000, type="status", seq=0, time_us=300, vm_epoch=2, completed_seq=seq, completed_us=290,
                     count=counts)
        for records in ([command, ping, ack, done], [early_ping, command, ping, ack, done]):
            out = receipt_from_client_move(counts, duration, 900, 5_100, done["device"], None, records, None)
            self.assertEqual((out.status, out.seq), ("done", seq))
            self.assertEqual((out.ack_mono_ns, out.ack_controller_us, out.ack_vm_epoch), (1_200, 60, 2))
            self.assertEqual(out.complete_mono_ns, 5_000)
        with self.assertRaises(ReceiptError) as refused:
            receipt_from_client_move(counts, duration, 900, 5_100, done["device"], None, [command, ping, done], None)
        self.assertIn(f"no MOVE6 ack with sequence {seq}", str(refused.exception))
        self.assertIn("PING", str(refused.exception))
        with self.assertRaises(ReceiptError) as refused:
            receipt_from_client_move(counts, duration, 900, 5_100, done["device"], None, [ping, ack, done], None)
        self.assertIn("no MOVE6 command", str(refused.exception))
        with self.assertRaises(ReceiptError) as refused:
            receipt_from_client_move(counts, duration, 900, 5_100, done["device"], None, [command, ping, ack], None)
        self.assertIn(f"completed_seq {seq}", str(refused.exception))
        # Without a Client log nothing is associated and nothing is refused.
        bare = receipt_from_client_move(counts, duration, 900, 5_100, done["device"], None, [], None,
                                        log_expected=False)
        self.assertEqual((bare.status, bare.ack_mono_ns, bare.complete_mono_ns), ("done", None, 5_100))

    def test_late_ping_ack_with_the_moves_sequence_is_ignored(self):
        rec = MoveRecorder(self.backend, self.writer, self.clock, allow_hardware=True)
        rec.execute([64, 0, 0, 0, 0, 0], "probe_jog")
        self.device.stale_before_next_ack = {"op": "PING", "vm_epoch": 0, "time_us": 5}
        _, out = rec.execute([0, 64, 0, 0, 0, 0], "probe_jog")
        self.assertEqual(out.status, "done")
        log = [json.loads(line) for line in self.log.read_text().splitlines()]
        acks = [r["device"] for r in log if r["type"] == "device_reply" and r["device"]["type"] == "ack"
                and r["device"]["seq"] == out.seq]
        self.assertEqual([a["op"] for a in acks], ["PING", "MOVE6"])
        self.assertEqual((out.ack_vm_epoch, out.ack_controller_us), (1, acks[1]["time_us"]))
        notes = [r["text"] for r in SessionReader(self.writer.path).records("session_note")]
        self.assertFalse(any("vm_epoch" in t for t in notes), notes)       # no false supply cycle
        self.assertEqual(rec.direction[:2], [1, 1])

    def test_move_missing_from_the_client_log_is_unverified_and_halts(self):
        elsewhere = tmpdir("receipts") / f"elsewhere-{id(self)}.jsonl"
        elsewhere.write_text("")
        gate = learn.GatedBackend(ControlsClientBackend(self.client, elsewhere, self.clock), 64, self.clock)
        rec = MoveRecorder(gate, self.writer, self.clock, allow_hardware=True)
        _, out = rec.execute([64, 0, 0, 0, 0, 0], "probe_jog")
        self.assertEqual(out.status, "unverified")
        self.assertIn("ReceiptError: the controls Client log holds no MOVE6 command", out.error)
        self.assertIsNone(out.ack_mono_ns)
        self.assertEqual(out.reported_counts, [64, 0, 0, 0, 0, 0])
        self.assertEqual(rec.direction[0], 0)
        self.assertTrue(gate.halted)
        moves = self.device.moves
        _, again = rec.execute([64, 0, 0, 0, 0, 0], "probe_jog")
        self.assertEqual(again.status, "rejected")
        self.assertEqual(self.device.moves, moves)
        records = SessionReader(self.writer.path).records()
        self.assertEqual([r["status"] for r in records if r["kind"] == "move_complete"], ["unverified", "rejected"])
        self.assertFalse(any(r["kind"] == "move_ack" for r in records))

    def test_rejected_and_faulted_moves(self):
        rec = MoveRecorder(self.backend, self.writer, self.clock, allow_hardware=True)
        rec.execute([100, 0, 0, 0, 0, 0], "engage")
        self.backend.max_rate = 2000           # pretend the controller reported the bench profile
        _, out = rec.execute([640, 0, 0, 0, 0, 0], "probe_jog")
        self.assertEqual(out.status, "rejected")
        self.assertEqual(rec.direction[0], 1)          # nothing was issued
        self.device.fault_on_move = self.device.moves + 1
        self.backend.max_rate = 1000
        _, out = rec.execute([0, 50, 0, 0, 0, 0], "probe_jog")
        self.assertEqual(out.status, "fault")
        self.assertEqual(out.fault, "driver")
        self.assertEqual(rec.direction[1], 0)
        statuses = [r["status"] for r in SessionReader(self.writer.path).records("move_complete")]
        self.assertEqual(statuses, ["done", "rejected", "fault"])

    def test_for_session_logs_inside_session_directory(self):
        from unittest import mock
        positioner = host_modules().positioner
        clock = FakeClock()
        device = FakeDevice(clock, max_rate=1000)
        with mock.patch.object(positioner, "Client", lambda port, log: FakeClient.with_device(device, log)):
            backend = ControlsClientBackend.for_session("fake-port", self.writer, clock)
        rec = MoveRecorder(backend, self.writer, clock, allow_hardware=True)
        _, out = rec.execute([64, 0, 0, 0, 0, 0], "probe_jog")
        backend.client.close()
        self.assertEqual(out.status, "done")
        log = self.writer.path / "controller-client.jsonl"
        self.assertTrue(log.exists())
        self.assertIn("MOVE6", log.read_text())
        self.assertIsNotNone(out.ack_mono_ns)

    def test_prepare_mirrors_console_sequence(self):
        self.device.state = "unreferenced"
        sent = []
        original = self.device.command

        def spy(line):
            sent.append(line.split()[0])
            return original(line)

        self.device.command = spy
        self.backend.prepare(datum_established=True)
        self.assertEqual([s for s in sent if s in ("CLEAR", "REF", "ARM")], ["CLEAR", "REF", "ARM"])
        self.assertEqual(self.device.state, "armed")
        self.assertEqual(self.client.heartbeat, "fake")


class StatusFields(unittest.TestCase):
    """STATUS and DRIVERS as main.cpp prints them: profile, per-axis currents and microsteps, vm_epoch."""

    def run_moves(self, epochs, name):
        clock = FakeClock()
        device = FakeDevice(clock, max_rate=1000)
        log = tmpdir("fields") / f"{name}.jsonl"
        client = FakeClient.with_device(device, log)
        backend = ControlsClientBackend(client, log, clock)
        writer = SessionWriter(tmpdir("fields-sessions"), name, clock)
        rec = MoveRecorder(backend, writer, clock, allow_hardware=True)
        for epoch in epochs:
            device.vm_epoch = epoch
            rec.execute([100, -100, 0, 0, 50, 0], "probe_jog")
            clock.advance_ns(200_000_000)
        writer.close()
        client.close()
        return rec, SessionReader(writer.path).records()

    def test_receipts_carry_vm_epoch_and_every_status_field(self):
        rec, records = self.run_moves([3, 3], "fields")
        done = [r for r in records if r["kind"] == "move_complete"]
        acks = [r for r in records if r["kind"] == "move_ack"]
        self.assertEqual([r["vm_epoch"] for r in done], [3, 3])
        self.assertEqual([r["vm_epoch"] for r in acks], [3, 3])
        for key in ("profile", "current_scales", "configured_vsense", "vsense", "microsteps", "timer_ticks",
                    "drivers_ok", "max_rate", "counts_per_mm", "state", "fault", "boot", "vm_epoch"):
            self.assertIn(key, done[-1]["controller"], key)
        self.assertNotIn("count", done[-1]["controller"])
        self.assertEqual(done[-1]["controller"]["profile"], "loaded-development")
        loaded = PROFILES["loaded-development"]
        self.assertEqual(done[-1]["controller"]["current_scales"], loaded["current_scales"])
        self.assertEqual(done[-1]["controller"]["configured_vsense"], loaded["vsense"])
        self.assertEqual(done[-1]["controller"]["vsense"], loaded["vsense"])
        self.assertTrue(all(d["sample_valid"] and d["configured_cs"] == d["cs_actual"]
                            for d in done[-1]["driver_state"]))
        self.assertEqual(rec.direction, [1, -1, 0, 0, 1, 0])
        self.assertEqual(supply_cycles(records), [])

    def test_supply_cycle_is_detected_and_resets_takeup(self):
        rec, records = self.run_moves([1, 1, 2], "cycle")
        cycles = supply_cycles(records)
        self.assertEqual(len(cycles), 1)
        self.assertEqual((cycles[0]["from_epoch"], cycles[0]["to_epoch"]), (1, 2))
        self.assertEqual(rec.direction, [0] * 6)   # the cycle may have happened during this move
        notes = [r["text"] for r in records if r["kind"] == "session_note"]
        self.assertTrue(any("vm_epoch 1 -> 2" in t for t in notes))
        inside = {"camera_id": "cam_a", "seq": 7, "device_pts_ns": (cycles[0]["after_ns"] + cycles[0]["before_ns"]) // 2,
                  "recv_mono_ns": cycles[0]["before_ns"]}
        outside = {**inside, "seq": 8, "device_pts_ns": cycles[0]["after_ns"] - 1}
        self.assertEqual(frames_in_supply_cycles([inside, outside], cycles), [("cam_a", 7)])

    def test_recorder_controller_status_comes_from_receipts(self):
        rec, _ = self.run_moves([5], "status")
        status = rec.controller_status()
        self.assertTrue(status["drivers_ok"])
        self.assertEqual(status["microsteps"], [16] * 6)
        self.assertEqual(status["vm_epoch"], 5)

    def test_command_rejected_class_maps_to_rejected(self):
        rejected = host_modules().positioner.CommandRejected
        status, fault = controls._classify_error(rejected("Controller rejected command: rate"))
        self.assertEqual((status, fault), ("rejected", None))
        self.assertEqual(controls._classify_error(RuntimeError("Motion fault: driver")), ("fault", "driver"))
        self.assertEqual(controls._classify_error(TimeoutError("x"))[0], "timeout")


if __name__ == "__main__":
    unittest.main()
