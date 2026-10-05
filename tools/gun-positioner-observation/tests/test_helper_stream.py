"""The capture helper's stream protocol (no camera, no helper process)."""

import io
import unittest

import numpy as np

import support  # noqa: F401

from gpobs.capture import RawFrame, SourceDrop, SourceEvent
from gpobs.helper_stream import ProtocolError, encode_message, read_message, to_item


class Protocol(unittest.TestCase):
    def test_roundtrip_and_items(self):
        luma = bytes(range(12))
        stream = io.BytesIO(
            encode_message({"type": "hello", "mode": "capture", "unique_id": "0x13000032e41298"})
            + encode_message({"type": "frame", "seq": 1, "pts_ns": 10, "host_ns": 12, "duration_ns": 33,
                              "codec": "gray8", "width": 4, "height": 3, "subtype": "420v"}, luma)
            + encode_message({"type": "frame", "seq": 2, "codec": "jpeg", "width": 3840, "height": 2160}, b"\xff\xd8")
            + encode_message({"type": "drop", "pts_ns": 99, "reason": "OutOfBuffers"})
            + encode_message({"type": "bye", "frames": 2, "drops": 1}))
        items = []
        while (msg := read_message(stream)) is not None:
            items.append(to_item(*msg))
        self.assertIsInstance(items[0], SourceEvent)
        self.assertEqual(items[0].detail["unique_id"], "0x13000032e41298")
        frame = items[1]
        self.assertIsInstance(frame, RawFrame)
        self.assertEqual((frame.codec, frame.source_seq, frame.device_pts_ns, frame.source_host_ns),
                         ("gray8", 1, 10, 12))
        self.assertEqual(frame.payload.shape, (3, 4))
        self.assertTrue(np.array_equal(frame.payload.ravel(), np.arange(12)))
        self.assertEqual(items[2].codec, "jpeg")
        self.assertIsInstance(items[3], SourceDrop)
        self.assertEqual(items[3].reason, "OutOfBuffers")
        self.assertEqual(items[4].event, "bye")

    def test_truncation_and_corruption(self):
        good = encode_message({"type": "frame", "seq": 1, "codec": "jpeg"}, b"abcdef")
        with self.assertRaises(ProtocolError):
            read_message(io.BytesIO(good[:-2]))
        with self.assertRaises(ProtocolError):
            read_message(io.BytesIO(good[:7]))
        with self.assertRaises(ProtocolError):
            read_message(io.BytesIO(b"XXXX" + good[4:]))
        self.assertIsNone(read_message(io.BytesIO(b"")))


if __name__ == "__main__":
    unittest.main()
