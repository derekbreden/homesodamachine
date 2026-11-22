"""Time-stamp each USB command and receipt from the appliance used for the cup experiment."""
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import serial


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class Journal:
    def __init__(self, path):
        self.stream = Path(path).open("a", buffering=1)

    def append(self, event, **values):
        row = dict(utc=utc(), mono_ns=time.monotonic_ns(), event=event, **values)
        self.stream.write(json.dumps(row, separators=(",", ":"), allow_nan=False) + "\n")
        return row


class Board:
    def __init__(self, path, journal):
        self.events = journal
        self.port = serial.Serial(port=None, baudrate=115200, timeout=0.10, write_timeout=0.5, exclusive=True)
        self.port.dtr = False
        self.port.rts = False
        self.port.port = path
        self.port.open()
        time.sleep(1.45)
        self.port.reset_input_buffer()
        self.status()

    def send(self, command):
        data = self.events.append("tx", command=command)
        self.port.write((command + "\n").encode("ascii"))
        self.port.flush()
        return data["mono_ns"]

    def line(self):
        raw = self.port.readline()
        if not raw:
            return ""
        line = raw.decode("utf8", errors="replace").strip()
        if line:
            self.events.append("rx", line=line)
        return line

    def status(self):
        self.send("status")
        seen = []
        deadline = time.monotonic() + 2.4
        while time.monotonic() < deadline:
            line = self.line()
            if line:
                seen.append(line)
            if re.match(r"volume\s+", line):
                break
        if not any("d6e49a5f6" in s for s in seen) or not any(re.search(r"state\s+idle",s) for s in seen) or not any(re.search(r"valves\s+all closed",s) for s in seen):
            raise RuntimeError("Controller identity or parked state was not confirmed")

    def gate(self, channel, duration_ms):
        if channel not in ("A", "B") or not 15 <= duration_ms <= 4000:
            raise ValueError((channel, duration_ms))
        tx = self.send(f"pump {channel.lower()} {duration_ms}")
        deadline = time.monotonic() + duration_ms / 1000 + 1.4
        started_ns = None
        while time.monotonic() < deadline:
            line = self.line()
            if f"pump {channel} at full for {duration_ms} ms" in line:
                started_ns = time.monotonic_ns()
            match = re.search(r"pump ([AB]) done after (\d+) ms", line)
            if match:
                if match[1] != channel or abs(int(match[2]) - duration_ms) > 3 or started_ns is None:
                    raise RuntimeError("Unexpected acknowledged gate: " + line)
                return dict(tx_ns=tx,start_ack_ns=started_ns,done_ack_ns=time.monotonic_ns(),board_ms=int(match[2]))
            if "refused" in line or "stopped after" in line:
                raise RuntimeError(line)
        raise TimeoutError(f"Missing {channel} completion for {duration_ms} ms")

    def close(self):
        try:
            self.status()
        finally:
            self.port.close()
