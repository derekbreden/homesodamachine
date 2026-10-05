"""VISCA encoding and decoding against the FoMaKo manual's tables (section 5)."""

import unittest

import support  # noqa: F401  (path setup)

from gpobs import optics, visca
from gpobs.clock import FakeClock


def hx(s: str) -> bytes:
    return bytes.fromhex(s.replace(" ", ""))


class Packets(unittest.TestCase):
    def test_control_commands_match_manual(self):
        a = 1
        table = [  # manual 5.2, with x = 1
            (visca.cam_power(a, True), "81 01 04 00 02 FF"),
            (visca.cam_power(a, False), "81 01 04 00 03 FF"),
            (visca.zoom_stop(a), "81 01 04 07 00 FF"),
            (visca.zoom_tele(a), "81 01 04 07 02 FF"),
            (visca.zoom_wide(a), "81 01 04 07 03 FF"),
            (visca.zoom_tele_variable(a, 0x5), "81 01 04 07 25 FF"),
            (visca.zoom_wide_variable(a, 0xF), "81 01 04 07 3F FF"),
            (visca.zoom_direct(a, 0x1A2B), "81 01 04 47 01 0A 02 0B FF"),
            (visca.focus_stop(a), "81 01 04 08 00 FF"),
            (visca.focus_far(a), "81 01 04 08 02 FF"),
            (visca.focus_near(a), "81 01 04 08 03 FF"),
            (visca.focus_direct(a, 0x0F00), "81 01 04 48 00 0F 00 00 FF"),
            (visca.focus_auto(a), "81 01 04 38 02 FF"),
            (visca.focus_manual(a), "81 01 04 38 03 FF"),
            (visca.focus_one_push_mode(a), "81 01 04 38 04 FF"),
            (visca.zoom_focus_direct(a, 0x1234, 0xABCD), "81 01 04 47 01 02 03 04 0A 0B 0C 0D FF"),
            (visca.ae_mode(a, "full_auto"), "81 01 04 39 00 FF"),
            (visca.ae_mode(a, "manual"), "81 01 04 39 03 FF"),
            (visca.ae_mode(a, "shutter_priority"), "81 01 04 39 0A FF"),
            (visca.ae_mode(a, "iris_priority"), "81 01 04 39 0B FF"),
            (visca.ae_mode(a, "bright"), "81 01 04 39 0D FF"),
            (visca.shutter_direct(a, 0x15), "81 01 04 4A 00 00 01 05 FF"),
            (visca.iris_direct(a, 0x0C), "81 01 04 4B 00 00 00 0C FF"),
            (visca.bright_direct(a, 0x2F), "81 01 04 4D 00 00 02 0F FF"),
            (visca.exp_comp(a, True), "81 01 04 3E 02 FF"),
            (visca.exp_comp_direct(a, 0x07), "81 01 04 4E 00 00 00 07 FF"),
            (visca.backlight(a, False), "81 01 04 33 03 FF"),
            (visca.gain_limit(a, 0x9), "81 01 04 2C 09 FF"),
            (visca.wb_mode(a, 0x06), "81 01 04 35 06 FF"),
            (visca.tracking(1, False), "81 0A 01 32 00 00 03 00 FF"),
            (visca.tracking(1, True), "81 0A 01 32 00 00 02 00 FF"),
            (visca.if_clear_broadcast(), "88 01 00 01 FF"),
            (visca.address_set_broadcast(1), "88 30 01 FF"),
        ]
        for got, want in table:
            self.assertEqual(got, hx(want), want)

    def test_inquiries_match_manual(self):
        table = {  # manual 5.3, with x = 1
            "power": "81 09 04 00 FF", "zoom_position": "81 09 04 47 FF", "focus_mode": "81 09 04 38 FF",
            "focus_position": "81 09 04 48 FF", "ae_mode": "81 09 04 39 FF", "shutter_position": "81 09 04 4A FF",
            "iris_position": "81 09 04 4B FF", "gain_limit": "81 09 04 2C FF", "bright_position": "81 09 04 4D FF",
            "wb_mode": "81 09 04 35 FF", "pan_tilt_position": "81 09 06 12 FF", "video_system": "81 09 06 23 FF",
            "version": "81 09 00 02 FF", "pan_tilt_speed": "81 09 01 01 FF", "flip": "81 09 04 A4 FF",
        }
        for name, want in table.items():
            self.assertEqual(visca.inquiry(1, name), hx(want), name)
        self.assertEqual(visca.inquiry(3, "zoom_position"), hx("83 09 04 47 FF"))

    def test_bounds(self):
        with self.assertRaises(ValueError):
            visca.zoom_direct(0, 1)
        with self.assertRaises(ValueError):
            visca.zoom_direct(8, 1)
        with self.assertRaises(ValueError):
            visca.zoom_direct(1, 0x10000)
        with self.assertRaises(ValueError):
            visca.wb_mode(1, 0x0C)
        with self.assertRaises(ValueError):
            visca.tracking(2, False)      # the manual prints these packets only for address 1
        self.assertEqual(visca.from_nibbles(bytes([1, 0xA, 2, 0xB])), 0x1A2B)
        with self.assertRaises(visca.ViscaError):
            visca.from_nibbles(bytes([0x10]))

    def test_ports_named_in_manual(self):
        self.assertEqual((visca.IP_VISCA_PORT, visca.SONY_VISCA_PORT), (1259, 52381))
        self.assertEqual(visca.SERIAL_BAUDS, (2400, 4800, 9600, 38400, 115200))


class Replies(unittest.TestCase):
    def test_return_messages(self):
        r = visca.parse_reply(hx("90 41 FF"))
        self.assertEqual((r.kind, r.address, r.socket), ("ack", 1, 1))
        r = visca.parse_reply(hx("90 51 FF"))
        self.assertEqual((r.kind, r.socket), ("completion", 1))
        self.assertEqual(visca.parse_reply(hx("90 60 02 FF")).error, "syntax_error")
        self.assertEqual(visca.parse_reply(hx("90 61 41 FF")).error, "command_not_executable")
        self.assertEqual(visca.parse_reply(hx("90 60 03 FF")).error, "undocumented_error_0x03")
        self.assertEqual(visca.parse_reply(hx("A0 41 FF")).address, 2)
        self.assertEqual(visca.parse_reply(hx("90 07 7D 01 04 00 FF")).kind, "ir_receive_return")
        self.assertEqual(visca.parse_reply(hx("12 34 FF")).kind, "unknown")

    def test_inquiry_decoders(self):
        dec = {name: d for name, (_, d) in visca.INQUIRIES.items()}
        self.assertEqual(dec["zoom_position"](hx("01 0A 02 0B")), 0x1A2B)
        self.assertEqual(dec["focus_mode"](hx("02")), "auto")
        self.assertEqual(dec["focus_mode"](hx("03")), "manual")
        self.assertEqual(dec["focus_mode"](hx("04")), "one_push")
        self.assertEqual(dec["ae_mode"](hx("0A")), "shutter_priority")
        self.assertEqual(dec["ae_mode"](hx("03")), "manual")
        self.assertEqual(dec["wb_mode"](hx("06")), "6500K")
        self.assertEqual(dec["wb_mode"](hx("0C")), "undocumented:0x0c")
        self.assertEqual(dec["shutter_position"](hx("00 00 01 05")), 0x15)
        self.assertEqual(dec["gain_limit"](hx("09")), 9)
        self.assertEqual(dec["video_system"](hx("0D")), "1080P29.97")
        self.assertEqual(dec["pan_tilt_position"](hx("00 01 02 03 0F 0E 0D 0C")), {"pan": 0x0123, "tilt": 0xFEDC})
        self.assertEqual(dec["version"](hx("02 20 05 11 01 02 00")),
                         {"vendor_id": "0220", "model_id": "0511", "arm_version": "0102", "reserve": "00"})
        with self.assertRaises(visca.ViscaError):
            dec["shutter_position"](hx("01 00 01 05"))

    def test_split_messages(self):
        buf = bytearray(hx("90 41 FF 90 51 FF 90 50 03"))
        self.assertEqual(visca.split_messages(buf), [hx("90 41 FF"), hx("90 51 FF")])
        self.assertEqual(bytes(buf), hx("90 50 03"))


class FakeCamera:
    """Answers per the manual's tables; advances a fake clock by its reply delay."""

    def __init__(self, clock, address=1, state=None, ack_delay_ns=3_000_000, done_delay_ns=40_000_000,
                 silent=False, refuse=None, chunked=False):
        self.clock, self.address = clock, address
        self.y = (address + 8) << 4
        self.state = {"focus_mode": 0x02, "ae_mode": 0x00, "zoom": 0x1A2B, "focus": 0x0300, "pan": 0x10,
                      "tilt": 0x20, "shutter": 0x0B, "iris": 0x08, "gain": 0x4, "bright": 0x10, "wb": 0x06,
                      **(state or {})}
        self.ack_delay_ns, self.done_delay_ns = ack_delay_ns, done_delay_ns
        self.silent, self.refuse, self.chunked = silent, refuse, chunked
        self.queue = []
        self.sent = []

    def write(self, data):
        self.sent.append(bytes(data))
        if self.silent:
            return
        body = data[1:-1]
        now = self.clock.monotonic_ns()
        if body[0] == 0x01 or body[0] == 0x0A:
            if self.refuse and body == self.refuse:
                self.queue.append((now + self.ack_delay_ns, bytes([self.y, 0x61, 0x41, 0xFF])))
                return
            self.queue.append((now + self.ack_delay_ns, bytes([self.y, 0x41, 0xFF])))
            self.queue.append((now + self.done_delay_ns, bytes([self.y, 0x51, 0xFF])))
            if body[:3] == bytes([0x01, 0x04, 0x38]):
                self.state["focus_mode"] = body[3]
            if body[:3] == bytes([0x01, 0x04, 0x39]):
                self.state["ae_mode"] = body[3]
            if body[:3] == bytes([0x01, 0x04, 0x47]):
                self.state["zoom"] = visca.from_nibbles(body[3:7])
            return
        n = visca.nibbles
        replies = {
            (0x09, 0x04, 0x00): [0x02], (0x09, 0x04, 0x47): n(self.state["zoom"]),
            (0x09, 0x04, 0x38): [self.state["focus_mode"]], (0x09, 0x04, 0x48): n(self.state["focus"]),
            (0x09, 0x04, 0x39): [self.state["ae_mode"]], (0x09, 0x04, 0x4A): [0, 0, *n(self.state["shutter"], 2)],
            (0x09, 0x04, 0x4B): [0, 0, *n(self.state["iris"], 2)], (0x09, 0x04, 0x2C): [self.state["gain"]],
            (0x09, 0x04, 0x4D): [0, 0, *n(self.state["bright"], 2)], (0x09, 0x04, 0x35): [self.state["wb"]],
            (0x09, 0x06, 0x12): [*n(self.state["pan"]), *n(self.state["tilt"])], (0x09, 0x06, 0x23): [0x06],
            (0x09, 0x00, 0x02): [0x02, 0x20, 0x05, 0x11, 0x01, 0x02, 0x00],
        }
        data = replies.get(tuple(body))
        msg = bytes([self.y, 0x50, *data, 0xFF]) if data is not None else bytes([self.y, 0x60, 0x02, 0xFF])
        self.queue.append((now + self.ack_delay_ns, msg))

    def read(self, timeout_s):
        if not self.queue:
            self.clock.advance_ns(int(timeout_s * 1e9))
            return b""
        self.queue.sort()
        t, msg = self.queue.pop(0)
        if t > self.clock.monotonic_ns():
            self.clock.advance_ns(t - self.clock.monotonic_ns())
        if self.chunked and len(msg) > 2:
            self.queue.insert(0, (t, msg[2:]))
            return msg[:2]
        return msg

    def close(self):
        pass


class Client(unittest.TestCase):
    def test_command_ack_then_completion_with_times(self):
        clock = FakeClock()
        cam = FakeCamera(clock, chunked=True)
        client = visca.ViscaClient(cam, 1, clock)
        ex = client.command(visca.focus_manual(1), "focus_manual")
        self.assertEqual(ex.status, "completed")
        self.assertEqual(ex.ack_ns - ex.send_ns, 3_000_000)
        self.assertEqual(ex.done_ns - ex.send_ns, 40_000_000)
        self.assertEqual([r[2] for r in ex.replies], ["ack", "completion"])

    def test_errors_and_timeouts(self):
        clock = FakeClock()
        cam = FakeCamera(clock, refuse=visca.focus_direct(1, 5)[1:-1])
        client = visca.ViscaClient(cam, 1, clock)
        self.assertEqual(client.command(visca.focus_direct(1, 5)).status, "error:command_not_executable")
        silent = visca.ViscaClient(FakeCamera(clock, silent=True), 1, clock, ack_timeout_s=0.5)
        t0 = clock.monotonic_ns()
        self.assertEqual(silent.command(visca.focus_manual(1)).status, "timeout_ack")
        self.assertGreaterEqual(clock.monotonic_ns() - t0, 500_000_000)
        self.assertEqual(silent.inquire("zoom_position").status, "timeout_reply")

    def test_read_optics_and_gate(self):
        clock = FakeClock()
        cam = FakeCamera(clock)
        client = visca.ViscaClient(cam, 1, clock)
        state, exchanges = visca.read_optics(client, "cam_a")
        self.assertEqual((state.focus_mode, state.exposure_mode, state.tracking), ("auto", "full_auto", "unknown"))
        self.assertEqual((state.zoom_position, state.pan_position, state.tilt_position), (0x1A2B, 0x10, 0x20))
        self.assertEqual(state.white_balance, "6500K")
        self.assertEqual(state.extra["version"]["vendor_id"], "0220")
        verdict = optics.gate(state, clock.monotonic_ns())
        self.assertFalse(verdict.ok)
        self.assertIn("focus_mode_auto", verdict.reasons)
        self.assertIn("tracking_state_unknown", verdict.reasons)
        locked = visca.lock_optics(client, zoom=0x2000)
        self.assertEqual([e.name for e in locked], ["tracking_off", "focus_manual", "ae_manual", "zoom_direct"])
        self.assertTrue(all(e.status == "completed" for e in locked))
        state, _ = visca.read_optics(client, "cam_a")
        self.assertEqual((state.focus_mode, state.exposure_mode, state.tracking, state.zoom_position),
                         ("manual", "manual", "off_commanded", 0x2000))
        self.assertTrue(optics.gate(state, clock.monotonic_ns()).ok)

    def test_lock_stops_at_first_failure(self):
        clock = FakeClock()
        cam = FakeCamera(clock, refuse=visca.focus_manual(1)[1:-1])
        locked = visca.lock_optics(visca.ViscaClient(cam, 1, clock), zoom=1)
        self.assertEqual([e.status for e in locked], ["completed", "error:command_not_executable"])
        self.assertNotIn(visca.zoom_direct(1, 1), cam.sent)


if __name__ == "__main__":
    unittest.main()
