"""Protocol regressions using an in-memory serial device; no ports are opened."""
import json
import sys
import threading
import types
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "host"))
from positioner import Client, CommandRejected

class FakeSerial:
    def __init__(self):
        self.pending = bytearray()
        self.commands = []
        self.last_seq = 0
        self.boot = "00000001"
        self.behavior = "normal"
        self.closed = False

    @property
    def in_waiting(self):
        return len(self.pending)

    def emit(self, kind, **kwargs):
        status = dict(type=kind, boot=self.boot, seq=0, last_seq=self.last_seq, time_us=1000,
                      profile="bench", current_scales=[10] * 6, max_rate=2000, counts_per_mm=6400,
                      microsteps=[16] * 6, configured_vsense=[1] * 6, vsense=[1] * 6,
                      count=[0] * 6, state="fault", referenced=False,
                      completed_seq=0, fault="user_stop")
        status.update(kwargs)
        self.pending.extend((json.dumps(status) + "\n").encode())

    def write(self, data):
        command = data.decode().strip()
        self.commands.append(command)
        tokens = command.split()
        op = tokens[0]
        if op == "STATUS": self.emit("status")
        elif op == "STOP": self.emit("stopped", op="STOP")
        else:
            seq = int(tokens[2])
            self.last_seq = seq
            if self.behavior == "lost_move_ack" and op == "MOVE6": return len(data)
            if self.behavior == "late_ping_ack" and op == "MOVE6": self.emit("ack", seq=seq, op="PING")
            if self.behavior == "reject_move" and op == "MOVE6":
                self.emit("ack", seq=seq, op="PING")
                self.emit("error", seq=seq, op=op, error="sequence")
            else: self.emit("ack", seq=seq, op=op)
        return len(data)

    def read(self, size):
        result = self.pending[:size]
        del self.pending[:size]
        return bytes(result)

    def close(self): self.closed = True

class ClientTests(unittest.TestCase):
    def setUp(self):
        self.device = FakeSerial()
        self.serial_patch = patch.dict(sys.modules, {"serial": types.SimpleNamespace(Serial=lambda *a, **k: self.device)})
        self.serial_patch.start()
        self.client = Client("FAKE_NO_PORT")

    def tearDown(self):
        self.client.close(False)
        self.serial_patch.stop()

    def test_late_ping_ack_never_acknowledges_move(self):
        self.device.behavior = "late_ping_ack"
        reply = self.client.request("MOVE6", 1000000, 16, 0, 0, 0, 0, 0)
        self.assertEqual(reply["op"], "MOVE6")
        self.device.behavior = "reject_move"
        with self.assertRaises(CommandRejected): self.client.request("MOVE6", 1000000, 16, 0, 0, 0, 0, 0)

    def test_unknown_move_acceptance_stops_resyncs_and_never_retries(self):
        self.device.behavior = "lost_move_ack"
        elapsed = [0.0]
        def advance():
            elapsed[0] += 0.01
            return elapsed[0]
        with patch("positioner.time.monotonic", advance):
            with self.assertRaises(TimeoutError): self.client.request("MOVE6", 1000000, 16, 0, 0, 0, 0, 0)
        self.assertEqual(sum(c.startswith("MOVE6 ") for c in self.device.commands), 1)
        self.assertIn("STOP", self.device.commands)
        self.assertEqual(self.client.seq, 1)
        self.assertIsNotNone(self.client.failure)
        with self.assertRaises(RuntimeError): self.client.request("CLEAR")
        self.client.recover()
        self.assertIsNone(self.client.failure)
        self.assertFalse(self.client.last["referenced"])
        self.assertEqual(self.client.request("CLEAR")["seq"], 2)

    def test_boot_change_requires_explicit_recovery(self):
        self.device.boot = "00000002"
        self.device.last_seq = 0
        with self.assertRaisesRegex(RuntimeError, "reset"): self.client.status()
        self.assertEqual(self.client.boot, "00000002")
        self.assertIsNotNone(self.client.failure)
        with self.assertRaises(RuntimeError): self.client.request("CLEAR")
        self.client.recover()
        self.assertEqual(self.client.seq, 0)
        self.assertFalse(self.client.last["referenced"])

    def test_failed_heartbeat_stops_and_restarts_only_after_recovery(self):
        real_request = self.client.request
        def failed(*args): raise TimeoutError("injected heartbeat failure")
        self.client.request = failed
        self.client.start_heartbeat()
        self.client.heartbeat.join(1)
        self.assertFalse(self.client.heartbeat.is_alive())
        self.assertIn("STOP", self.device.commands)
        with self.assertRaises(RuntimeError): self.client.start_heartbeat()
        self.client.request = real_request
        self.client.recover()
        self.client.start_heartbeat()
        self.assertTrue(self.client.heartbeat.is_alive())

    def test_profile_and_scaling_mismatch_refuses_connection(self):
        original = self.device.emit
        def mismatch(kind, **kwargs): original(kind, counts_per_mm=1234, **kwargs)
        self.device.emit = mismatch
        with self.assertRaisesRegex(RuntimeError, "profile/scaling"): Client("FAKE_NO_PORT")

    def test_reset_to_incompatible_controller_cannot_recover(self):
        self.device.boot = "00000002"
        original = self.device.emit
        def mismatch(kind, **kwargs): original(kind, counts_per_mm=1234, **kwargs)
        self.device.emit = mismatch
        with self.assertRaisesRegex(RuntimeError, "reset"): self.client.status()
        with self.assertRaisesRegex(RuntimeError, "profile/scaling"): self.client.recover()
        self.assertIsNotNone(self.client.failure)
        with self.assertRaises(RuntimeError): self.client.request("CLEAR")
        self.assertFalse(any(c.startswith("CLEAR ") for c in self.device.commands))

    def test_loaded_profile_requires_axis_specific_sense_voltage(self):
        status = dict(profile="loaded-development", current_scales=[10,10,22,10,14,10],
                      counts_per_mm=6400, max_rate=1000, configured_vsense=[1,1,0,1,1,1],
                      drivers_ok=True, vsense=[1,1,0,1,1,1])
        Client.check_profile(status)
        status["vsense"][2] = 1
        with self.assertRaisesRegex(RuntimeError, "profile/scaling"): Client.check_profile(status)
        status["drivers_ok"] = False
        status["vsense"] = [None] * 6
        Client.check_profile(status) # Cold, unverified driver readings can be inspected.
        status["configured_vsense"] = [1] * 6
        with self.assertRaisesRegex(RuntimeError, "profile/scaling"): Client.check_profile(status)

if __name__ == "__main__": unittest.main()
