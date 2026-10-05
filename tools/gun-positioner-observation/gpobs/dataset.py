"""Append-only session directories.

    <root>/<UTC start>-<label>-<4 hex>/
        manifest.json      written once at creation (exclusive create)
        events.jsonl       every record, appended and flushed; never rewritten
        frames/<camera>/<seq>.<ext>   frame bytes, exclusive create
        closing.json       written once when the session closes

Nothing here deletes, renames or rewrites a file. A trial that failed stays in
the log with its outcome. A session that ends without `closing.json` is still
readable; `SessionReader.integrity()` reports it as unclosed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import secrets
import sys
import threading
import time

import numpy as np

from . import SCHEMA_VERSION, TOOL_VERSION
from .clock import Clock
from .schema import validate


def _jsonable(value):
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return [_jsonable(v) for v in value.tolist()]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        f = float(value)
        return f if np.isfinite(f) else None
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def dumps(record: dict) -> str:
    return json.dumps(_jsonable(record), separators=(",", ":"), allow_nan=False)


class SessionClosed(RuntimeError):
    pass


class SessionWriter:
    """Creates one new session directory and appends records to it.

    Thread-safe: capture threads, the move recorder and observers share one
    writer, so `rec` numbers are one global order.
    """

    def __init__(self, root: Path, label: str, clock: Clock | None = None,
                 config: dict | None = None, fsync_interval_s: float = 1.0):
        self.clock = clock or Clock()
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^A-Za-z0-9._-]+", "-", label).strip("-")[:48] or "session"
        stamp = datetime.fromtimestamp(self.clock.wall_ns() / 1e9, timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.session_id = f"{stamp}-{slug}-{secrets.token_hex(2)}"
        self.path = root / self.session_id
        self.path.mkdir(exist_ok=False)
        (self.path / "frames").mkdir()
        manifest = {
            "schema": SCHEMA_VERSION,
            "tool_version": TOOL_VERSION,
            "session_id": self.session_id,
            "label": label,
            "created_wall_utc": datetime.fromtimestamp(self.clock.wall_ns() / 1e9, timezone.utc).isoformat(),
            "created_mono_ns": self.clock.monotonic_ns(),
            "host": {
                "system": platform.system(),
                "machine": platform.machine(),
                "python": sys.version.split()[0],
                "numpy": np.__version__,
                "monotonic_clock": time.get_clock_info("monotonic").implementation,
            },
            "frame_storage": ("jpeg: compressed native sample as delivered; gray8/gray16: luma as PGM or PNG; "
                              "nv12: luma rows then CbCr rows as one PGM or PNG"),
            "config": config or {},
        }
        with open(self.path / "manifest.json", "x") as fh:
            fh.write(json.dumps(_jsonable(manifest), indent=2) + "\n")
        self._events = open(self.path / "events.jsonl", "x", buffering=1)
        self._lock = threading.Lock()
        self._rec = 0
        self._closed = False
        self._fsync_interval_ns = int(fsync_interval_s * 1e9)
        self._last_fsync = self.clock.monotonic_ns()
        self.counts: dict[str, int] = {}

    def append(self, kind: str, **fields) -> dict:
        with self._lock:
            if self._closed:
                raise SessionClosed(f"session {self.session_id} is closed")
            record = {"kind": kind, "rec": self._rec}
            if "mono_ns" not in fields:
                record["mono_ns"] = self.clock.monotonic_ns()
            if "wall_ns" not in fields:
                record["wall_ns"] = self.clock.wall_ns()
            record.update(_jsonable(fields))
            problems = validate(record)
            if problems:
                raise ValueError("; ".join(problems))
            self._events.write(dumps(record) + "\n")
            self._rec += 1
            self.counts[kind] = self.counts.get(kind, 0) + 1
            now = self.clock.monotonic_ns()
            if now - self._last_fsync >= self._fsync_interval_ns:
                self._events.flush()
                os.fsync(self._events.fileno())
                self._last_fsync = now
            return record

    def store_frame(self, camera_id: str, seq: int, data: bytes, ext: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", camera_id):
            raise ValueError("camera ids are letters, digits, '_' and '-'")
        folder = self.path / "frames" / camera_id
        folder.mkdir(exist_ok=True)
        rel = f"frames/{camera_id}/{seq:08d}.{ext}"
        with open(self.path / rel, "xb") as fh:
            fh.write(data)
        return rel

    def close(self, outcome: str = "closed", summary: dict | None = None) -> None:
        with self._lock:
            if self._closed:
                raise SessionClosed(f"session {self.session_id} is already closed")
            self._events.flush()
            os.fsync(self._events.fileno())
            self._events.close()
            self._closed = True
            closing = {
                "closed_wall_utc": datetime.fromtimestamp(self.clock.wall_ns() / 1e9, timezone.utc).isoformat(),
                "closed_mono_ns": self.clock.monotonic_ns(),
                "outcome": outcome,
                "records": self._rec,
                "counts": dict(sorted(self.counts.items())),
                "summary": summary or {},
            }
            with open(self.path / "closing.json", "x") as fh:
                fh.write(json.dumps(_jsonable(closing), indent=2) + "\n")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if not self._closed:
            self.close("closed" if exc_type is None else f"error: {exc_type.__name__}")
        return False


@dataclass
class IntegrityReport:
    ok: bool
    closed: bool
    problems: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


class SessionReader:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.manifest = json.loads((self.path / "manifest.json").read_text())
        closing = self.path / "closing.json"
        self.closing = json.loads(closing.read_text()) if closing.exists() else None
        self._records = None
        self.partial_tail = None

    @property
    def session_id(self) -> str:
        return self.manifest["session_id"]

    def records(self, kind: str | None = None) -> list[dict]:
        if self._records is None:
            out = []
            with open(self.path / "events.jsonl") as fh:
                lines = fh.read().split("\n")
            for i, line in enumerate(lines):
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    if i == len(lines) - 1:
                        self.partial_tail = line  # an interrupted final write
                        continue
                    raise
            self._records = out
        if kind is None:
            return list(self._records)
        return [r for r in self._records if r["kind"] == kind]

    def frame_path(self, frame_record: dict) -> Path:
        if not frame_record.get("file"):
            raise FileNotFoundError("frame was logged but not stored")
        return self.path / frame_record["file"]

    def load_frame(self, frame_record: dict) -> np.ndarray:
        from .imageio import load_frame
        return load_frame(self.frame_path(frame_record), frame_record["codec"], frame_record.get("height"))

    def integrity(self) -> IntegrityReport:
        problems = []
        records = self.records()
        if self.partial_tail is not None:
            problems.append("events.jsonl ends with a partial record")
        for expected, rec in enumerate(records):
            if rec.get("rec") != expected:
                problems.append(f"record numbering breaks at line {expected}: rec={rec.get('rec')}")
                break
        for rec in records:
            for p in validate(rec):
                problems.append(f"rec {rec.get('rec')}: {p}")
        stats = {"records": len(records), "frames": {}, "gaps": {}, "stored_missing": 0}
        last_seq: dict[str, int] = {}
        last_recv: dict[str, int] = {}
        for rec in records:
            if rec["kind"] == "frame":
                cam = rec["camera_id"]
                stats["frames"][cam] = stats["frames"].get(cam, 0) + 1
                if cam in last_seq and rec["seq"] != last_seq[cam] + 1:
                    problems.append(f"{cam}: frame seq {last_seq[cam]} -> {rec['seq']}")
                if cam in last_recv and rec["recv_mono_ns"] < last_recv[cam]:
                    problems.append(f"{cam}: receipt time went backwards at seq {rec['seq']}")
                last_seq[cam], last_recv[cam] = rec["seq"], rec["recv_mono_ns"]
                if rec["stored"] and not (self.path / rec["file"]).exists():
                    stats["stored_missing"] += 1
                    problems.append(f"{cam}: stored frame {rec['file']} is missing")
            elif rec["kind"] == "frame_gap":
                cam = rec["camera_id"]
                stats["gaps"][cam] = stats["gaps"].get(cam, 0) + rec["missing_estimate"]
        commands = {r["cmd_id"] for r in records if r["kind"] == "move_command"}
        completed = {r["cmd_id"] for r in records if r["kind"] == "move_complete"}
        stats["moves"] = len(commands)
        stats["moves_without_completion"] = sorted(commands - completed)
        started = {r["trial_id"] for r in records if r["kind"] == "trial_start"}
        ended = {r["trial_id"]: r["outcome"] for r in records if r["kind"] == "trial_end"}
        stats["trials"] = len(started)
        stats["trial_outcomes"] = {o: sum(1 for v in ended.values() if v == o) for o in sorted(set(ended.values()))}
        stats["trials_unterminated"] = sorted(started - set(ended))
        if self.closing is None:
            problems.append("session has no closing.json (interrupted or still open)")
        return IntegrityReport(ok=not problems, closed=self.closing is not None, problems=problems, stats=stats)
