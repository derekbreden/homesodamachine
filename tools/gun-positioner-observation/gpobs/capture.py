"""The frames, drop notices and events a camera source delivers.

A `FrameSource` delivers `RawFrame`s with the source's own sequence numbers and
stamps, `SourceDrop` notices of frames the source reports lost (AVFoundation's
didDrop), and `SourceEvent`s for everything else it reports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RawFrame:
    payload: object                    # bytes (jpeg, nv12) or ndarray (gray8/gray16)
    codec: str                         # jpeg | gray8 | gray16 | nv12
    width: int | None = None
    height: int | None = None
    source_seq: int | None = None
    device_pts_ns: int | None = None   # presentation time on the host clock, where the source has one
    source_host_ns: int | None = None  # the source process's own receipt stamp
    duration_ns: int | None = None
    subtype: str | None = None         # AVFoundation format subtype the frame arrived in


@dataclass
class SourceDrop:
    device_pts_ns: int | None
    reason: str


@dataclass
class SourceEvent:
    event: str
    detail: dict


class FrameSource(ABC):
    camera_id: str
    unique_id: str
    name: str

    @abstractmethod
    def start(self) -> dict:
        """Begin delivery; returns what the source reports about itself."""

    @abstractmethod
    def read(self, timeout_s: float):
        """Next RawFrame, SourceDrop or SourceEvent; None at end of stream; raises queue.Empty on timeout."""

    def stop(self) -> None:
        pass
