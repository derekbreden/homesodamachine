---
name: UART reliability — resolved via TinyProto migration
description: SerialTransfer+UartLink replaced with TinyProto (HDLC)+ProtoQueue — acks, retries, flow control now handled by protocol layer
type: project
---

Resolved. SerialTransfer (COBS framing) + UartLink (~930-line hand-rolled reliability layer) replaced with TinyProto (HDLC, RFC 1662) + ProtoQueue (~430 lines, queue only). TinyProto provides built-in acks, retransmission, CRC-16, and flow control via HDLC I-frame sequencing with a 4-frame sliding window.

Key changes: per-chunk acks eliminated (fire-and-forget 512-byte chunks), `#seq:` text ack protocol removed, upload state machine simplified from 5 to 4 states, all constants renamed PKT_* → MSG_*. RP2040 required pre_build.py patching for TinyProto compatibility.

**Why:** UartLink reimplemented what TinyProto provides out of the box, poorly — stale packet timeout races, no flow control, fragile text ack parsing. Bugs were growing with each new feature sharing the serial links.

**How to apply:** UART reliability is no longer a concern. ProtoQueue handles application-level queueing and state machines; TinyProto handles transport reliability. No need to flag reliability risks when touching UART code.
