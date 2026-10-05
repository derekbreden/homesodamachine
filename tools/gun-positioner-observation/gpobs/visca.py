"""VISCA messages as tabulated in the FoMaKo PTZ camera manual.

Source: FoMaKo "NDI/HDMI/USB IP PTZ Camera User Manual" V1.0
(https://www.fomako.net/uploads/20250529/ce40713967c8ae0e137cabdd8a72ff1d.pdf),
section 5: serial parameters (8 data bits, 1 stop bit, no parity), 5.1 return
messages, 5.2 control commands, 5.3 inquiry commands. `x` is the camera address,
`y = x + 8`. Every packet and decoder table below is transcribed from those
tables; the tests check them byte for byte.

Not established by the manual, and therefore not assumed here:
  * Network framing. The quick start names "IP Visca port: 1259" and "Sony Visca
    port: 52381" without stating TCP or UDP or any header. `TcpTransport` and
    `UdpTransport` send bare VISCA messages to a chosen port; whether the camera
    accepts either is unverified. No header for port 52381 is encoded.
  * Latency. The manual states that a command returns an ACK when accepted and a
    Completion when executed, but gives no times. Timeouts are parameters, and
    every exchange records its send, ACK and Completion stamps so the real
    latency can be measured.
  * Auto-tracking. The manual gives Tracking OFF/ON packets only in their
    address-1 form (81 ...) and no tracking inquiry.
  * Signedness and units of positions (zoom, focus, pan, tilt): returned raw.
No camera has been connected to this code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import socket

from .clock import Clock
from .optics import OpticsState

IP_VISCA_PORT = 1259
SONY_VISCA_PORT = 52381  # named in the manual; its framing is not documented there
SERIAL_BAUDS = (2400, 4800, 9600, 38400, 115200)  # section 5 and the 2.4 parameter table
TERMINATOR = 0xFF


class ViscaError(Exception):
    pass


def _x(address: int) -> int:
    if not 1 <= address <= 7:
        raise ValueError("VISCA camera address is 1..7")
    return 0x80 | address


def nibbles(value: int, count: int = 4) -> list[int]:
    """0p 0q 0r 0s form: one value spread over `count` low nibbles."""
    if not 0 <= value < 16 ** count:
        raise ValueError(f"{value} does not fit in {count} nibbles")
    return [(value >> (4 * (count - 1 - i))) & 0x0F for i in range(count)]


def from_nibbles(data: bytes | list[int]) -> int:
    value = 0
    for b in data:
        if b > 0x0F:
            raise ViscaError(f"byte 0x{b:02x} is not a 0p nibble")
        value = (value << 4) | b
    return value


def _cmd(address: int, *body: int) -> bytes:
    return bytes([_x(address), *body, TERMINATOR])


# ---- 5.2 control commands -------------------------------------------------------------------

def cam_power(address: int, on: bool) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x00, 0x02 if on else 0x03)


def zoom_stop(address: int) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x07, 0x00)


def zoom_tele(address: int) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x07, 0x02)


def zoom_wide(address: int) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x07, 0x03)


def zoom_tele_variable(address: int, speed: int) -> bytes:
    if not 0 <= speed <= 0xF:
        raise ValueError("p = 0 (low) .. F (high)")
    return _cmd(address, 0x01, 0x04, 0x07, 0x20 | speed)


def zoom_wide_variable(address: int, speed: int) -> bytes:
    if not 0 <= speed <= 0xF:
        raise ValueError("p = 0 (low) .. F (high)")
    return _cmd(address, 0x01, 0x04, 0x07, 0x30 | speed)


def zoom_direct(address: int, position: int) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x47, *nibbles(position))


def focus_stop(address: int) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x08, 0x00)


def focus_far(address: int) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x08, 0x02)


def focus_near(address: int) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x08, 0x03)


def focus_direct(address: int, position: int) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x48, *nibbles(position))


def focus_auto(address: int) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x38, 0x02)


def focus_manual(address: int) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x38, 0x03)


def focus_one_push_mode(address: int) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x38, 0x04)


def zoom_focus_direct(address: int, zoom: int, focus: int) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x47, *nibbles(zoom), *nibbles(focus))


AE_MODES = {"full_auto": 0x00, "manual": 0x03, "shutter_priority": 0x0A,
            "iris_priority": 0x0B, "bright": 0x0D}


def ae_mode(address: int, mode: str) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x39, AE_MODES[mode])


def _pq_direct(address: int, selector: int, value: int) -> bytes:
    return _cmd(address, 0x01, 0x04, selector, 0x00, 0x00, *nibbles(value, 2))


def shutter_direct(address: int, position: int) -> bytes:
    return _pq_direct(address, 0x4A, position)


def iris_direct(address: int, position: int) -> bytes:
    return _pq_direct(address, 0x4B, position)


def bright_direct(address: int, position: int) -> bytes:
    return _pq_direct(address, 0x4D, position)


def exp_comp_direct(address: int, position: int) -> bytes:
    return _pq_direct(address, 0x4E, position)


def exp_comp(address: int, on: bool) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x3E, 0x02 if on else 0x03)


def backlight(address: int, on: bool) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x33, 0x02 if on else 0x03)


def gain_limit(address: int, position: int) -> bytes:
    return _cmd(address, 0x01, 0x04, 0x2C, *nibbles(position, 1))


def wb_mode(address: int, mode: int) -> bytes:
    if not 0x00 <= mode <= 0x0B:
        raise ValueError("WB mode pq = 00..0B")
    return _cmd(address, 0x01, 0x04, 0x35, mode)


def tracking(address: int, on: bool) -> bytes:
    """The manual's Tracking OFF/ON packets, printed only for address 1."""
    if address != 1:
        raise ValueError("the manual documents the tracking packets only as 81 0A 01 32 ... (address 1)")
    return bytes([0x81, 0x0A, 0x01, 0x32, 0x00, 0x00, 0x02 if on else 0x03, 0x00, TERMINATOR])


def if_clear_broadcast() -> bytes:
    return bytes([0x88, 0x01, 0x00, 0x01, TERMINATOR])


def address_set_broadcast(first_address: int = 1) -> bytes:
    return bytes([0x88, 0x30, *nibbles(first_address, 1), TERMINATOR])


# ---- 5.3 inquiry commands ---------------------------------------------------------------------

def _enum(table: dict[int, str]):
    def decode(data: bytes):
        if len(data) != 1:
            raise ViscaError(f"expected one data byte, got {data.hex()}")
        return table.get(data[0], f"undocumented:0x{data[0]:02x}")
    return decode


def _nib(count: int):
    def decode(data: bytes):
        if len(data) != count:
            raise ViscaError(f"expected {count} nibble bytes, got {data.hex()}")
        return from_nibbles(data)
    return decode


def _zero_pq(data: bytes):
    if len(data) != 4 or data[0] != 0 or data[1] != 0:
        raise ViscaError(f"expected 00 00 0p 0q, got {data.hex()}")
    return from_nibbles(data[2:])


def _pan_tilt(data: bytes):
    if len(data) != 8:
        raise ViscaError(f"expected 0w0w0w0w 0z0z0z0z, got {data.hex()}")
    return {"pan": from_nibbles(data[:4]), "tilt": from_nibbles(data[4:])}


def _version(data: bytes):
    if len(data) != 7:
        raise ViscaError(f"expected ab cd mn pq rs tu vw, got {data.hex()}")
    return {"vendor_id": data[0:2].hex(), "model_id": data[2:4].hex(),
            "arm_version": data[4:6].hex(), "reserve": data[6:7].hex()}


def _max_speed(data: bytes):
    if len(data) != 2:
        raise ViscaError(f"expected ww zz, got {data.hex()}")
    return {"pan_max_speed": data[0], "tilt_max_speed": data[1]}


ON_OFF = {0x02: "on", 0x03: "off"}
VIDEO_SYSTEMS = {0x0: "1080P60", 0x1: "1080P50", 0x4: "720P60", 0x5: "720P50", 0x6: "1080P30",
                 0x7: "1080P25", 0xA: "1080P59.94", 0xC: "720P59.94", 0xD: "1080P29.97"}
WB_MODES = {0x00: "auto", 0x01: "3000K", 0x02: "4000K", 0x03: "one_push", 0x04: "5000K",
            0x05: "manual", 0x06: "6500K", 0x07: "3500K", 0x08: "4500K", 0x09: "5500K",
            0x0A: "6000K", 0x0B: "7000K"}
FOCUS_MODE_REPLY = {0x02: "auto", 0x03: "manual", 0x04: "one_push"}
AE_MODE_REPLY = {0x00: "full_auto", 0x03: "manual", 0x0A: "shutter_priority",
                 0x0B: "iris_priority", 0x0D: "bright"}

# name: (packet bytes after the address byte, without FF; decoder of the reply's data bytes)
INQUIRIES = {
    "power": ((0x09, 0x04, 0x00), _enum({0x02: "on", 0x03: "off_standby"})),
    "zoom_position": ((0x09, 0x04, 0x47), _nib(4)),
    "focus_mode": ((0x09, 0x04, 0x38), _enum(FOCUS_MODE_REPLY)),
    "focus_position": ((0x09, 0x04, 0x48), _nib(4)),
    "af_sensitivity": ((0x09, 0x04, 0x58), _enum({0x01: "high", 0x02: "normal", 0x03: "low"})),
    "wb_mode": ((0x09, 0x04, 0x35), _enum(WB_MODES)),
    "r_gain": ((0x09, 0x04, 0x43), _zero_pq),
    "b_gain": ((0x09, 0x04, 0x44), _zero_pq),
    "ae_mode": ((0x09, 0x04, 0x39), _enum(AE_MODE_REPLY)),
    "shutter_position": ((0x09, 0x04, 0x4A), _zero_pq),
    "iris_position": ((0x09, 0x04, 0x4B), _zero_pq),
    "gain_limit": ((0x09, 0x04, 0x2C), _nib(1)),
    "bright_position": ((0x09, 0x04, 0x4D), _zero_pq),
    "exp_comp_mode": ((0x09, 0x04, 0x3E), _enum(ON_OFF)),
    "exp_comp_position": ((0x09, 0x04, 0x4E), _zero_pq),
    "backlight_mode": ((0x09, 0x04, 0x33), _enum(ON_OFF)),
    "wdr_strength": ((0x09, 0x04, 0x51), _nib(1)),
    "nr_2d": ((0x09, 0x04, 0x53), _nib(1)),
    "nr_3d": ((0x09, 0x04, 0x54), _nib(1)),
    "flicker": ((0x09, 0x04, 0x55), _enum({0x00: "off", 0x01: "50Hz", 0x02: "60Hz"})),
    "aperture": ((0x09, 0x04, 0x42), _zero_pq),
    "picture_effect": ((0x09, 0x04, 0x63), _enum({0x00: "off", 0x04: "b_and_w"})),
    "memory": ((0x09, 0x04, 0x3F), _nib(1)),
    "pan_tilt_speed": ((0x09, 0x01, 0x01), _nib(1)),
    "menu_mode": ((0x09, 0x06, 0x06), _enum(ON_OFF)),
    "lr_reverse": ((0x09, 0x04, 0x61), _enum(ON_OFF)),
    "picture_flip": ((0x09, 0x04, 0x66), _enum(ON_OFF)),
    "ir_receive": ((0x09, 0x06, 0x08), _enum(ON_OFF)),
    "brightness": ((0x09, 0x04, 0xA1), _zero_pq),
    "contrast": ((0x09, 0x04, 0xA2), _zero_pq),
    "flip": ((0x09, 0x04, 0xA4), _enum({0x00: "off", 0x01: "flip_h", 0x02: "flip_v", 0x03: "flip_hv"})),
    "gamma": ((0x09, 0x04, 0x5B), _nib(1)),
    "low_light": ((0x09, 0x04, 0x2D), _enum({0x00: "off", 0x01: "on"})),
    "version": ((0x09, 0x00, 0x02), _version),
    "video_system": ((0x09, 0x06, 0x23), _enum(VIDEO_SYSTEMS)),
    "pan_tilt_max_speed": ((0x09, 0x06, 0x11), _max_speed),
    "pan_tilt_position": ((0x09, 0x06, 0x12), _pan_tilt),
}


def inquiry(address: int, name: str) -> bytes:
    body, _ = INQUIRIES[name]
    return _cmd(address, *body)


# ---- 5.1 return messages ----------------------------------------------------------------------

@dataclass(frozen=True)
class Reply:
    raw: bytes
    kind: str              # ack | completion | inquiry_reply | error | ir_receive_return | unknown
    address: int | None
    socket: int | None = None
    error: str | None = None
    data: bytes = b""


ERRORS = {0x02: "syntax_error", 0x41: "command_not_executable"}


def parse_reply(raw: bytes) -> Reply:
    if len(raw) < 3 or raw[-1] != TERMINATOR:
        return Reply(raw, "unknown", None)
    head = raw[0]
    address = (head >> 4) - 8 if head & 0x0F == 0 else None
    if address is None or not 1 <= address <= 7:
        return Reply(raw, "unknown", None)
    second = raw[1]
    if 0x40 <= second <= 0x4F and len(raw) == 3:
        return Reply(raw, "ack", address, socket=second & 0x0F)
    if 0x50 <= second <= 0x5F:
        if len(raw) == 3:
            return Reply(raw, "completion", address, socket=second & 0x0F)
        if second == 0x50:
            return Reply(raw, "inquiry_reply", address, data=bytes(raw[2:-1]))
    if 0x60 <= second <= 0x6F and len(raw) == 4:
        code = raw[2]
        return Reply(raw, "error", address, socket=second & 0x0F,
                     error=ERRORS.get(code, f"undocumented_error_0x{code:02x}"))
    if second == 0x07 and len(raw) >= 4 and raw[2] == 0x7D:
        return Reply(raw, "ir_receive_return", address, data=bytes(raw[3:-1]))
    return Reply(raw, "unknown", address)


def split_messages(buffer: bytearray) -> list[bytes]:
    """Remove and return every complete FF-terminated message in `buffer`."""
    out = []
    while True:
        try:
            end = buffer.index(TERMINATOR)
        except ValueError:
            return out
        out.append(bytes(buffer[:end + 1]))
        del buffer[:end + 1]


# ---- transports -------------------------------------------------------------------------------

class SerialTransport:
    """RS-232/RS-485 per manual section 5: 8 data bits, 1 stop bit, no parity."""

    def __init__(self, port: str, baud: int):
        if baud not in SERIAL_BAUDS:
            raise ValueError(f"baud {baud} is not one the manual lists: {SERIAL_BAUDS}")
        import serial  # pyserial
        self._s = serial.Serial()
        self._s.port, self._s.baudrate = port, baud
        self._s.bytesize, self._s.parity, self._s.stopbits = 8, "N", 1
        self._s.xonxoff = self._s.rtscts = self._s.dsrdtr = False
        self._s.dtr = self._s.rts = False
        self._s.timeout = 0.05
        self._s.open()
        self.description = f"serial {port} {baud} 8N1"

    def write(self, data: bytes) -> None:
        self._s.write(data)
        self._s.flush()

    def read(self, timeout_s: float) -> bytes:
        self._s.timeout = max(0.0, timeout_s)
        first = self._s.read(1)
        return first + self._s.read(self._s.in_waiting) if first else b""

    def close(self) -> None:
        self._s.close()


class TcpTransport:
    """Bare VISCA bytes over TCP (default port 1259). Framing unverified on the camera."""

    def __init__(self, host: str, port: int = IP_VISCA_PORT, connect_timeout_s: float = 3.0):
        self._sock = socket.create_connection((host, port), timeout=connect_timeout_s)
        self.description = f"tcp {host}:{port} bare VISCA (unverified framing)"

    def write(self, data: bytes) -> None:
        self._sock.sendall(data)

    def read(self, timeout_s: float) -> bytes:
        self._sock.settimeout(max(0.001, timeout_s))
        try:
            data = self._sock.recv(4096)
        except socket.timeout:
            return b""
        if not data:
            raise ConnectionError("camera closed the TCP connection")
        return data

    def close(self) -> None:
        self._sock.close()


class UdpTransport:
    """Bare VISCA bytes over UDP (default port 1259). Framing unverified on the camera."""

    def __init__(self, host: str, port: int = IP_VISCA_PORT):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.connect((host, port))
        self.description = f"udp {host}:{port} bare VISCA (unverified framing)"

    def write(self, data: bytes) -> None:
        self._sock.send(data)

    def read(self, timeout_s: float) -> bytes:
        self._sock.settimeout(max(0.001, timeout_s))
        try:
            return self._sock.recv(4096)
        except socket.timeout:
            return b""

    def close(self) -> None:
        self._sock.close()


# ---- client -----------------------------------------------------------------------------------

@dataclass
class Exchange:
    name: str
    sent: str
    send_ns: int
    status: str = "pending"   # completed | reply | error:<code> | timeout_ack | timeout_completion | timeout_reply | bad_reply
    ack_ns: int | None = None
    done_ns: int | None = None
    replies: list = field(default_factory=list)   # [ns, hex, kind]
    value: object = None

    def as_dict(self) -> dict:
        return {"name": self.name, "sent": self.sent, "send_ns": self.send_ns, "status": self.status,
                "ack_ns": self.ack_ns, "done_ns": self.done_ns, "replies": self.replies,
                "value": self.value}


class ViscaClient:
    def __init__(self, transport, address: int = 1, clock: Clock | None = None,
                 ack_timeout_s: float = 1.0, completion_timeout_s: float = 10.0,
                 inquiry_timeout_s: float = 1.0):
        _x(address)
        self.transport = transport
        self.address = address
        self.clock = clock or Clock()
        self.ack_timeout_s = ack_timeout_s
        self.completion_timeout_s = completion_timeout_s
        self.inquiry_timeout_s = inquiry_timeout_s
        self._buffer = bytearray()
        self.tracking_off_confirmed = False
        self.history: list[Exchange] = []
        self.unsolicited: list[tuple[int, str, str]] = []

    def _next_reply(self, deadline_ns: int) -> tuple[int, Reply] | None:
        while True:
            for raw in split_messages(self._buffer):
                reply = parse_reply(raw)
                now = self.clock.monotonic_ns()
                if reply.kind in ("ir_receive_return", "unknown") or reply.address != self.address:
                    self.unsolicited.append((now, raw.hex(), reply.kind))
                    continue
                return now, reply
            remaining = (deadline_ns - self.clock.monotonic_ns()) / 1e9
            if remaining <= 0:
                return None
            self._buffer.extend(self.transport.read(remaining))

    def command(self, packet: bytes, name: str = "command") -> Exchange:
        if packet[0] & 0xF0 != 0x80 or packet[-1] != TERMINATOR:
            raise ValueError("not a VISCA command packet")
        self._buffer.clear()
        ex = Exchange(name, packet.hex(), self.clock.monotonic_ns())
        self.transport.write(packet)
        deadline = ex.send_ns + int(self.ack_timeout_s * 1e9)
        while ex.status == "pending":
            got = self._next_reply(deadline)
            if got is None:
                ex.status = "timeout_ack" if ex.ack_ns is None else "timeout_completion"
                break
            now, reply = got
            ex.replies.append([now, reply.raw.hex(), reply.kind])
            if reply.kind == "ack" and ex.ack_ns is None:
                ex.ack_ns = now
                deadline = now + int(self.completion_timeout_s * 1e9)
            elif reply.kind == "completion":
                ex.done_ns = now
                ex.status = "completed"
            elif reply.kind == "error":
                ex.status = f"error:{reply.error}"
            else:
                ex.status = "bad_reply"
        self.history.append(ex)
        if name == "tracking_off":
            self.tracking_off_confirmed = ex.status == "completed"
        return ex

    def inquire(self, name: str) -> Exchange:
        _, decode = INQUIRIES[name]
        packet = inquiry(self.address, name)
        self._buffer.clear()
        ex = Exchange(name, packet.hex(), self.clock.monotonic_ns())
        self.transport.write(packet)
        got = self._next_reply(ex.send_ns + int(self.inquiry_timeout_s * 1e9))
        if got is None:
            ex.status = "timeout_reply"
        else:
            now, reply = got
            ex.replies.append([now, reply.raw.hex(), reply.kind])
            ex.done_ns = now
            if reply.kind == "inquiry_reply":
                try:
                    ex.value = decode(reply.data)
                    ex.status = "reply"
                except ViscaError as exc:
                    ex.status = "bad_reply"
                    ex.value = str(exc)
            elif reply.kind == "error":
                ex.status = f"error:{reply.error}"
            else:
                ex.status = "bad_reply"
        self.history.append(ex)
        return ex


OPTICS_INQUIRIES = ("power", "zoom_position", "focus_mode", "focus_position", "ae_mode",
                    "shutter_position", "iris_position", "gain_limit", "bright_position",
                    "wb_mode", "pan_tilt_position", "video_system", "version")


def read_optics(client: ViscaClient, camera_id: str) -> tuple[OpticsState, list[Exchange]]:
    """Inquire the optics-relevant state. A failed inquiry leaves its field unknown."""
    exchanges = [client.inquire(name) for name in OPTICS_INQUIRIES]
    got = {ex.name: ex.value for ex in exchanges if ex.status == "reply"}
    failures = {ex.name: ex.status for ex in exchanges if ex.status != "reply"}
    focus = got.get("focus_mode", "unknown")
    exposure = got.get("ae_mode", "unknown")
    pan_tilt = got.get("pan_tilt_position") or {}
    state = OpticsState(
        camera_id=camera_id, source="visca_inquiry", taken_mono_ns=client.clock.monotonic_ns(),
        focus_mode=focus if focus in ("auto", "manual", "one_push") else "unknown",
        exposure_mode=exposure if exposure in AE_MODES else "unknown",
        tracking="off_commanded" if client.tracking_off_confirmed else "unknown",
        zoom_position=got.get("zoom_position"), focus_position=got.get("focus_position"),
        shutter_position=got.get("shutter_position"), iris_position=got.get("iris_position"),
        gain_limit=got.get("gain_limit"), bright_position=got.get("bright_position"),
        white_balance=got.get("wb_mode"), pan_position=pan_tilt.get("pan"),
        tilt_position=pan_tilt.get("tilt"), power=got.get("power"),
        video_system=got.get("video_system"),
        extra={"version": got.get("version"), "inquiry_failures": failures,
               "transport": getattr(client.transport, "description", type(client.transport).__name__),
               "address": client.address})
    return state, exchanges


def lock_optics(client: ViscaClient, zoom: int | None = None, focus: int | None = None,
                shutter: int | None = None, iris: int | None = None, gain: int | None = None,
                bright: int | None = None, white_balance: int | None = None) -> list[Exchange]:
    """Fix tracking off, manual focus and manual exposure, then any direct values.

    Stops at the first exchange that does not complete. Moves only the camera's
    lens settings; no pan/tilt command is sent.
    """
    a = client.address
    plan = []
    if a == 1:
        plan.append(("tracking_off", tracking(a, False)))
    plan += [("focus_manual", focus_manual(a)), ("ae_manual", ae_mode(a, "manual"))]
    if zoom is not None:
        plan.append(("zoom_direct", zoom_direct(a, zoom)))
    if focus is not None:
        plan.append(("focus_direct", focus_direct(a, focus)))
    if shutter is not None:
        plan.append(("shutter_direct", shutter_direct(a, shutter)))
    if iris is not None:
        plan.append(("iris_direct", iris_direct(a, iris)))
    if gain is not None:
        plan.append(("gain_limit", gain_limit(a, gain)))
    if bright is not None:
        plan.append(("bright_direct", bright_direct(a, bright)))
    if white_balance is not None:
        plan.append(("wb_mode", wb_mode(a, white_balance)))
    done = []
    for name, packet in plan:
        ex = client.command(packet, name)
        done.append(ex)
        if ex.status != "completed":
            break
    return done
