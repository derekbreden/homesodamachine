#!/usr/bin/env python3
"""Inspect and operate the two-axis PGFUN positioner."""
import argparse
import json
import math
import subprocess
import sys
import threading
import time
from pathlib import Path

from kinematics import AXES, COUNTS_PER_REV, SOFT_LIMIT, GEOMETRY_SHA, split_target, degrees_to_count
SOURCE = Path(__file__).resolve().parents[1]
MAX_JOG_COUNTS = 256
MIN_DURATION_US = 100_000
MAX_DURATION_US = 2_000_000
MAX_ACCELERATION = 4_000

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
        if (status.get('profile') != 'pgfun-50-64' or
                status.get('counts_per_rev') != COUNTS_PER_REV or
                status.get('geometry_sha256') != GEOMETRY_SHA or
                status.get('current_scales') != [13,13] or
                status.get('configured_vsense') != [0,0] or
                status.get('max_rate') != 1000 or
                (status.get('drivers_ok') and (status.get('vsense') != [0,0] or status.get('microsteps') != [64,64]))):
            raise RuntimeError('Controller/geometry does not match this package')

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
        if (len(delta) != 2 or any(isinstance(v, bool) or not isinstance(v, int) for v in delta) or
                any(abs(v) > MAX_JOG_COUNTS for v in delta) or not any(delta)):
            raise ValueError("Two signed nonzero total count deltas, ≤256 per axis, required")
        if not MIN_DURATION_US <= duration_us <= MAX_DURATION_US:
            raise ValueError("Duration must be100..2000ms")
        result = self.request("MOVE2", duration_us, *delta)
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

    def establish(self):
        """Operator has aligned both parking pins and removed them before calling."""
        self.recover()
        self.request("CLEAR")
        self.request("REF")
        self.request("ARM")
        self.start_heartbeat()

    def load_trajectory(self, trajectory):
        if trajectory['geometry_sha256'] != GEOMETRY_SHA:
            raise ValueError('Trajectory geometry mismatch')
        knots = trajectory['knots']
        self.request('LOAD2', trajectory['period_us'], len(knots))
        for i, (yaw, pitch) in enumerate(knots):
            self.request('KNOT', i, yaw, pitch)
        self.move_to_counts(knots[0])
        return self.request('PLAY')

    def drivers(self):
        with self.lock:
            self.serial.write(b"DRIVERS\n")
            deadline = time.monotonic() + 0.2
            rows = {}
            while len(rows) < 2:
                result = self.read(deadline)
                if result["type"] == "driver":
                    rows[result["axis"]] = result
            return [rows[i] for i in range(2)]

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
    print('clear; reference central; arm; jog yaw|pitch counts duration_ms; status; drivers; disarm; stop; quit')
    while True:
        f=input('pgfun> ').split()
        if not f: continue
        try:
            if f[0] in ('quit','exit'):return
            if f==['status']:r=client.status()
            elif f==['drivers']:r=client.drivers()
            elif f==['stop']:r=client.stop()
            elif f==['recover']:r=client.recover()
            elif f==['clear']:r=client.request('CLEAR')
            elif f==['reference','central']:r=client.request('REF')
            elif f==['arm']:
                r=client.request('ARM');client.start_heartbeat()
            elif f==['disarm']:r=client.request('DISARM')
            elif f[0]=='jog' and len(f)==4:
                d=[0,0];d[AXES.index(f[1])]=int(f[2]);r=client.move(d,int(float(f[3])*1000))
            else:raise ValueError('Unknown command or wrong argument count')
            print(json.dumps(r,indent=2))
        except (ValueError,RuntimeError,TimeoutError) as error:print(str(error),file=sys.stderr)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port');p.add_argument('--log');p.add_argument('--list',action='store_true');a=p.parse_args()
    if a.list:
        from serial.tools import list_ports
        for port in list_ports.comports():print(port.device,port.description)
    elif not a.port:p.error('--port required')
    else:
        c=Client(a.port,a.log)
        try:console(c)
        finally:c.close()
