#!/usr/bin/env python3
"""Inspect/console an RP2040 dry-development positioner. No laser commands exist."""
import argparse
import json
import math
import subprocess
import sys
import threading
import time
from pathlib import Path

from kinematics import AXES, COUNTS_PER_MM, NEUTRAL_LENGTH_MM, SOFT_MIN, SOFT_MAX, actuator_length, mm_to_count, split_target

SOURCE = Path(__file__).resolve().parents[1]
MAX_JOG_COUNTS = 640
MIN_DURATION_US = 100_000
MAX_DURATION_US = 2_000_000
MAX_ACCELERATION = 12_000 # counts/s²; firmware applies the cubic-profile check.
PROFILES = {
    "bench": ([10] * 6, 2000),
    "loaded-development": ([10, 10, 22, 10, 14, 10], 1000),
}
VSENSE_PROFILES = {"bench": [1] * 6, "loaded-development": [1, 1, 0, 1, 1, 1]}

class CommandRejected(RuntimeError):
    pass

class Client:
    def __init__(self, port, log_path=None):
        import serial
        self.serial = serial.Serial(port, 115200, timeout=0.02, write_timeout=0.1)
        self.lock = threading.RLock()
        self.shutdown = threading.Event()
        self.heartbeat = None
        self.failure = None
        self.buffer = bytearray()
        self.boot = None
        self.seq = 0
        self.last = {}
        self.log = open(log_path, "a") if log_path else None
        try:
            self.status()
            self.seq = self.last["last_seq"]
            self.check_profile(self.last)
        except Exception:
            self.serial.close()
            if self.log: self.log.close()
            raise

    @staticmethod
    def check_profile(status):
        profile = status.get("profile")
        if (status.get("counts_per_mm") != COUNTS_PER_MM or profile not in PROFILES or
                status.get("current_scales") != PROFILES[profile][0] or status.get("max_rate") != PROFILES[profile][1] or
                status.get("configured_vsense") != VSENSE_PROFILES[profile] or
                (status.get("drivers_ok") and status.get("vsense") != VSENSE_PROFILES[profile])):
            raise RuntimeError("Controller profile/scaling does not match this host package")

    def record(self, record):
        if self.log:
            self.log.write(json.dumps(record, separators=(",", ":")) + "\n")
            self.log.flush()

    def read(self, deadline):
        while time.monotonic() < deadline:
            if b"\n" in self.buffer:
                line, _, tail = self.buffer.partition(b"\n")
                self.buffer = bytearray(tail)
                if not line.strip():
                    continue
                result = json.loads(line)
                received = time.monotonic_ns()
                self.record({"type": "device_reply", "host_receive_ns": received, "device": result})
                if "boot" in result:
                    changed = self.boot and result["boot"] != self.boot
                    self.boot = result["boot"]
                    self.last = result
                    if changed:
                        self.failure = RuntimeError("Controller reset: reference invalid, recover and re-establish datum")
                        raise self.failure
                return result
            chunk = self.serial.read(max(1, min(4096, self.serial.in_waiting)))
            self.buffer.extend(chunk)
            if len(self.buffer) > 8192:
                raise RuntimeError("Malformed/overlong device response")
        raise TimeoutError("No complete device reply within 200ms")

    def exchange(self, command, desired_type, seq=None, op=None):
        sent = time.monotonic_ns()
        self.record({"type": "host_command", "host_send_ns": sent, "command": command})
        self.serial.write((command + "\n").encode("ascii"))
        deadline = time.monotonic() + 0.2
        while True:
            result = self.read(deadline)
            matches_op = op is None or result.get("op") == op
            if result["type"] == "error" and matches_op and (seq is None or result.get("seq") in (0, seq)):
                raise CommandRejected("Controller rejected command: " + result.get("error", "unknown"))
            if result["type"] == desired_type and matches_op and (seq is None or result.get("seq") == seq):
                received = time.monotonic_ns()
                if "time_us" in result:
                    self.record({"type": "clock_bracket", "host_send_ns": sent,
                                 "host_receive_ns": received, "device_time_us": result["time_us"],
                                 "boot": result["boot"]})
                return result

    def request(self, operation, *args):
        with self.lock:
            if self.failure:
                raise RuntimeError("Host heartbeat failed; stop and re-reference") from self.failure
            seq = self.seq + 1
            try:
                result = self.exchange(" ".join(map(str, (operation, self.boot, seq, *args))), "ack", seq, operation)
            except CommandRejected:
                raise
            except Exception as error:
                # Acceptance is unknown. Never retry the command or assume a late
                # heartbeat ACK means a MOVE was accepted. STOP, resync and latch.
                self.failure = error
                try: self.stop()
                except Exception: pass
                try: self.seq = self.status()["last_seq"]
                except Exception: pass
                raise
            self.seq = seq
            return result

    def status(self):
        with self.lock:
            return self.exchange("STATUS", "status")

    def stop(self):
        with self.lock:
            return self.exchange("STOP", "stopped", op="STOP")

    def recover(self):
        """Explicit operator recovery stops first; it never restores a reference."""
        self.shutdown.set()
        if self.heartbeat:
            self.heartbeat.join(timeout=1)
            if self.heartbeat.is_alive():
                self.failure = RuntimeError("Heartbeat thread did not stop; reconnect the console")
                raise self.failure
        with self.lock:
            try:
                self.stop()
                result = self.status()
                self.check_profile(result)
            except Exception as error:
                self.failure = error
                raise
            self.seq = result["last_seq"]
            self.failure = None
            self.heartbeat = None
            self.shutdown.clear()
            return result

    def start_heartbeat(self):
        if self.failure:
            raise RuntimeError("Use explicit recover before restarting heartbeat")
        if self.heartbeat and self.heartbeat.is_alive():
            return
        def loop():
            while not self.shutdown.wait(0.1):
                try:
                    self.request("PING")
                except Exception as error:
                    self.failure = error
                    try:
                        with self.lock:
                            self.serial.write(b"STOP\n")
                    except Exception:
                        pass
                    return
        self.heartbeat = threading.Thread(target=loop, daemon=True)
        self.heartbeat.start()

    def move(self, delta, duration_us=1000000):
        if (len(delta) != 6 or any(isinstance(v, bool) or not isinstance(v, int) for v in delta) or
                any(abs(v) > MAX_JOG_COUNTS for v in delta) or not any(delta)):
            raise ValueError("Six signed nonzero total count deltas, ≤640 per axis, required")
        if not MIN_DURATION_US <= duration_us <= MAX_DURATION_US:
            raise ValueError("Duration must be100..2000ms")
        result = self.request("MOVE6", duration_us, *delta)
        move_seq = result["seq"]
        deadline = time.monotonic() + duration_us / 1e6 + 0.5
        try:
            while time.monotonic() < deadline:
                result = self.status()
                if result["state"] == "fault":
                    raise RuntimeError("Motion fault: " + result["fault"])
                if result["completed_seq"] == move_seq:
                    return result
                time.sleep(0.03)
        except Exception:
            try: self.stop()
            except Exception: pass
            raise
        self.stop()
        raise TimeoutError("Move completion absent; reference invalidated")

    def move_to_counts(self, target, duration_us=1000000):
        current = self.status()
        if current["state"] != "armed" or not current["referenced"]:
            raise RuntimeError("A healthy armed physical reference is required")
        result = current
        for segment in split_target(current["count"], target):
            result = self.move(segment, duration_us)
        return result

    def drivers(self):
        with self.lock:
            self.serial.write(b"DRIVERS\n")
            deadline = time.monotonic() + 0.2
            rows = {}
            while len(rows) < 6:
                result = self.read(deadline)
                if result["type"] == "driver":
                    rows[result["axis"]] = result
            return [rows[i] for i in range(6)]

    def close(self, stop_motion=True):
        # Exiting a motion session always inhibits pulses and invalidates datum.
        self.shutdown.set()
        if self.heartbeat:
            self.heartbeat.join(timeout=0.3)
        if stop_motion:
            try:
                self.stop()
            except Exception:
                pass
        self.serial.close()
        if self.log:
            self.log.close()

def console(client):
    print("Dry controller console. clear; reference central; arm; jog X 0.0025 250;")
    print("move6 dx_mm dy_mm dz_mm du_mm dv_mm dw_mm duration_ms; status; drivers; disarm; stop; quit")
    print("Coarse no-tube tests: target X 5 1000; angle U 5 1000. Targets split into≤0.1mm segments.")
    print("U/V/W are screw extension in mm. Reference central requires all six physical central datums.")
    while True:
        try:
            fields = input("positioner> ").split()
            if not fields:
                continue
            operation = fields[0]
            if operation in ("quit", "exit"):
                return
            if operation == "status" and len(fields) == 1:
                result = client.status()
            elif operation == "drivers" and len(fields) == 1:
                result = client.drivers()
            elif operation == "stop" and len(fields) == 1:
                result = client.stop()
            elif operation == "recover" and len(fields) == 1:
                result = client.recover()
            elif operation == "clear" and len(fields) == 1:
                result = client.request("CLEAR")
            elif fields == ["reference", "central"]:
                result = client.request("REF")
            elif operation == "arm" and len(fields) == 1:
                result = client.request("ARM"); client.start_heartbeat()
            elif operation == "disarm" and len(fields) == 1:
                result = client.request("DISARM")
            elif operation == "jog" and len(fields) == 4:
                delta = [0] * 6
                delta[AXES.index(fields[1].upper())] = mm_to_count(float(fields[2]))
                result = client.move(delta, round(float(fields[3]) * 1000))
            elif operation == "move6" and len(fields) == 8:
                delta = [mm_to_count(float(v)) for v in fields[1:7]]
                result = client.move(delta, round(float(fields[7]) * 1000))
            elif operation in ("target", "angle") and len(fields) == 4:
                axis = AXES.index(fields[1].upper())
                value = float(fields[2])
                if operation == "angle":
                    if axis < 3:
                        raise ValueError("angle acceptsU/V/W only; XYZ use target inmm")
                    value = actuator_length(value, axis=AXES[axis]) - NEUTRAL_LENGTH_MM
                target = client.status()["count"].copy()
                target[axis] = mm_to_count(value)
                if operation == "angle": target[axis] = max(SOFT_MIN[axis], min(SOFT_MAX[axis], target[axis]))
                result = client.move_to_counts(target, round(float(fields[3]) * 1000))
            else:
                raise ValueError("Unknown command or wrong argument count")
            print(json.dumps(result, indent=2))
        except (ValueError, RuntimeError, TimeoutError) as error:
            print(str(error), file=sys.stderr)
        except (KeyboardInterrupt, EOFError):
            return

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("simulate", "inspect", "console"))
    parser.add_argument("--port", help="Explicit Pico USB port; never auto-discovered or auto-selected")
    parser.add_argument("--log", type=Path, help="Append timestamped command/reply JSONL")
    parser.add_argument("--output", type=Path, help="Simulation JSONL output")
    args = parser.parse_args()
    if args.action == "simulate":
        import tempfile
        with tempfile.TemporaryDirectory(prefix="gun-positioner-sim-") as directory:
            binary = Path(directory) / "simulator"
            subprocess.run(["c++", "-std=c++17", "-O2", str(SOURCE / "tests/simulator.cpp"), "-o", str(binary)], check=True)
            result = subprocess.run([str(binary)], capture_output=True, text=True, check=True)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(result.stdout)
            else:
                print(result.stdout, end="")
        return
    if not args.port:
        parser.error("inspect/console require an explicit --port; simulate opens no serial port")
    client = Client(args.port, args.log)
    try:
        if args.action == "inspect":
            print(json.dumps(client.last, indent=2))
        else:
            console(client)
    finally:
        client.close(stop_motion=args.action == "console")

if __name__ == "__main__":
    main()
