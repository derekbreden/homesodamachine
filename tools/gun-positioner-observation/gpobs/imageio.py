"""Frame files: camera JPEG as delivered, 8/16-bit PGM, and JPEG header parsing.

A UVC Motion-JPEG frame often omits its Huffman tables (DHT); a standalone JPEG
decoder then refuses it. Frames are stored exactly as the camera delivered
them. `decode_jpeg` inserts the standard tables of ITU-T T.81 Annex K.3 when a
frame carries none, as Motion-JPEG decoders do, and decodes with Pillow.
"""

from __future__ import annotations

from pathlib import Path
import io
import struct

import numpy as np

SOF_MARKERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


class JpegError(ValueError):
    pass


def jpeg_segments(data: bytes):
    """Yield (marker, offset, payload) up to and including SOS."""
    if len(data) < 4 or data[0] != 0xFF or data[1] != 0xD8:
        raise JpegError("not a JPEG: missing SOI")
    i = 2
    n = len(data)
    while i < n:
        if data[i] != 0xFF:
            raise JpegError(f"expected a marker at byte {i}")
        while i < n and data[i] == 0xFF:
            i += 1
        if i >= n:
            break
        marker = data[i]
        i += 1
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            continue
        if marker == 0xD9:
            return
        if i + 2 > n:
            raise JpegError("truncated segment length")
        length = struct.unpack(">H", data[i:i + 2])[0]
        if length < 2 or i + length > n:
            raise JpegError("segment runs past the end of the frame")
        yield marker, i - 2, data[i + 2:i + length]
        if marker == 0xDA:
            return
        i += length


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    """(width, height) from the frame's SOF header, without decoding pixels."""
    for marker, _, payload in jpeg_segments(data):
        if marker in SOF_MARKERS:
            if len(payload) < 5:
                raise JpegError("short SOF segment")
            height, width = struct.unpack(">HH", payload[1:5])
            return width, height
    raise JpegError("no SOF segment before scan data")


def _dht(table_class: int, table_id: int, bits: list[int], vals: list[int]) -> bytes:
    assert len(bits) == 16 and sum(bits) == len(vals)
    return bytes([(table_class << 4) | table_id]) + bytes(bits) + bytes(vals)


_DC_LUM_BITS = [0, 1, 5, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
_DC_CHR_BITS = [0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
_DC_VALS = list(range(12))
_AC_LUM_BITS = [0, 2, 1, 3, 3, 2, 4, 3, 5, 5, 4, 4, 0, 0, 1, 0x7D]
_AC_LUM_VALS = bytes.fromhex("".join((
    "0102030004110512", "2131410613516107", "227114328191a108", "2342b1c11552d1f0",
    "2433627282090a16", "1718191a25262728", "292a343536373839", "3a43444546474849",
    "4a53545556575859", "5a63646566676869", "6a73747576777879", "7a83848586878889",
    "8a92939495969798", "999aa2a3a4a5a6a7", "a8a9aab2b3b4b5b6", "b7b8b9bac2c3c4c5",
    "c6c7c8c9cad2d3d4", "d5d6d7d8d9dae1e2", "e3e4e5e6e7e8e9ea", "f1f2f3f4f5f6f7f8",
    "f9fa")))
_AC_CHR_BITS = [0, 2, 1, 2, 4, 4, 3, 4, 7, 5, 4, 4, 0, 1, 2, 0x77]
_AC_CHR_VALS = bytes.fromhex("".join((
    "0001020311040521", "3106124151076171", "1322328108144291", "a1b1c109233352f0",
    "156272d10a162434", "e125f11718191a26", "2728292a35363738", "393a434445464748",
    "494a535455565758", "595a636465666768", "696a737475767778", "797a828384858687",
    "88898a9293949596", "9798999aa2a3a4a5", "a6a7a8a9aab2b3b4", "b5b6b7b8b9bac2c3",
    "c4c5c6c7c8c9cad2", "d3d4d5d6d7d8d9da", "e2e3e4e5e6e7e8e9", "eaf2f3f4f5f6f7f8",
    "f9fa")))

_STANDARD_DHT_PAYLOAD = (
    _dht(0, 0, _DC_LUM_BITS, _DC_VALS) + _dht(1, 0, _AC_LUM_BITS, list(_AC_LUM_VALS))
    + _dht(0, 1, _DC_CHR_BITS, _DC_VALS) + _dht(1, 1, _AC_CHR_BITS, list(_AC_CHR_VALS)))
STANDARD_DHT_SEGMENT = b"\xff\xc4" + struct.pack(">H", len(_STANDARD_DHT_PAYLOAD) + 2) + _STANDARD_DHT_PAYLOAD


def has_huffman_tables(data: bytes) -> bool:
    return any(marker == 0xC4 for marker, _, _ in jpeg_segments(data))


def with_standard_huffman_tables(data: bytes) -> bytes:
    """The frame with Annex K.3 tables inserted before its scan, if it has no DHT."""
    sos_offset = None
    for marker, offset, _ in jpeg_segments(data):
        if marker == 0xC4:
            return data
        if marker == 0xDA:
            sos_offset = offset
    if sos_offset is None:
        raise JpegError("no scan segment")
    return data[:sos_offset] + STANDARD_DHT_SEGMENT + data[sos_offset:]


def decode_jpeg(data: bytes, gray: bool = True) -> np.ndarray:
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("decoding camera JPEG frames requires Pillow (see requirements.txt)") from exc
    with Image.open(io.BytesIO(with_standard_huffman_tables(data))) as img:
        img = img.convert("L" if gray else "RGB")
        return np.asarray(img)


def encode_pgm(image: np.ndarray) -> bytes:
    """Binary PGM, 8- or 16-bit."""
    img = np.asarray(image)
    if img.ndim != 2:
        raise ValueError("PGM holds one channel")
    if img.dtype == np.uint8:
        maxval, body = 255, img.tobytes()
    elif img.dtype == np.uint16:
        maxval, body = 65535, img.astype(">u2").tobytes()
    else:
        raise ValueError("PGM frames are uint8 or uint16")
    return f"P5\n{img.shape[1]} {img.shape[0]}\n{maxval}\n".encode() + body


def decode_pgm(data: bytes) -> np.ndarray:
    tokens = []
    i = 0
    while len(tokens) < 4:
        while data[i:i + 1].isspace():
            i += 1
        if data[i:i + 1] == b"#":
            while data[i:i + 1] not in (b"\n", b""):
                i += 1
            continue
        j = i
        while not data[j:j + 1].isspace():
            j += 1
        tokens.append(data[i:j])
        i = j
    i += 1  # exactly one whitespace byte after maxval
    if tokens[0] != b"P5":
        raise ValueError("only binary PGM (P5) frames are read")
    w, h, maxval = int(tokens[1]), int(tokens[2]), int(tokens[3])
    dtype = np.uint8 if maxval < 256 else np.dtype(">u2")
    arr = np.frombuffer(data, dtype=dtype, count=w * h, offset=i).reshape(h, w)
    return arr.astype(np.uint16) if maxval >= 256 else arr.copy()


def nv12_to_rgb(y: np.ndarray, uv: np.ndarray, video_range: bool = True) -> np.ndarray:
    """BT.709 conversion of a 4:2:0 frame (luma plane, interleaved CbCr plane) to RGB uint8."""
    yf = y.astype(float)
    cb = np.repeat(np.repeat(uv[:, 0::2].astype(float), 2, axis=0), 2, axis=1)[:y.shape[0], :y.shape[1]] - 128
    cr = np.repeat(np.repeat(uv[:, 1::2].astype(float), 2, axis=0), 2, axis=1)[:y.shape[0], :y.shape[1]] - 128
    if video_range:
        yf = (yf - 16) * 255 / 219
        cb, cr = cb * 255 / 224, cr * 255 / 224
    r = yf + 1.5748 * cr
    g = yf - 0.1873 * cb - 0.4681 * cr
    b = yf + 1.8556 * cb
    return np.clip(np.round(np.stack([r, g, b], axis=2)), 0, 255).astype(np.uint8)


def split_nv12(stacked: np.ndarray, height: int) -> tuple[np.ndarray, np.ndarray]:
    """Luma rows then CbCr rows, as stored for codec "nv12"."""
    return stacked[:height], stacked[height:]


def encode_png(image: np.ndarray) -> bytes:
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("PNG frame storage requires Pillow (see requirements.txt)") from exc
    img = np.asarray(image)
    buf = io.BytesIO()
    pil = Image.fromarray(img) if img.dtype == np.uint8 else Image.fromarray(img.astype(np.uint16))
    pil.save(buf, format="PNG", compress_level=1)
    return buf.getvalue()


def decode_png(data: bytes) -> np.ndarray:
    from PIL import Image
    with Image.open(io.BytesIO(data)) as img:
        return np.asarray(img)


def load_frame(path: Path, codec: str, height: int | None = None, video_range: bool = True) -> np.ndarray:
    """Pixels of a stored frame: gray (H x W) for gray8/gray16, RGB for nv12 and jpeg colour."""
    path = Path(path)
    data = path.read_bytes()
    if codec == "jpeg":
        return decode_jpeg(data)
    raw = decode_png(data) if path.suffix == ".png" else decode_pgm(data)
    if codec in ("gray8", "gray16"):
        return raw
    if codec == "nv12":
        h = height if height is not None else raw.shape[0] * 2 // 3
        return nv12_to_rgb(*split_nv12(raw, h), video_range=video_range)
    raise ValueError(f"no reader for codec {codec}")
