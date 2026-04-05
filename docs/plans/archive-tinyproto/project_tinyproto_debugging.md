---
name: TinyProto debugging state
description: Detailed handoff for next agent — HDLC links connect but image uploads fail, RP2040 disconnects under load
type: project
---

# TinyProto Debugging Handoff

## Status as of 2026-03-20

The TinyProto migration (replacing SerialTransfer + UartLink) is code-complete but **not working end-to-end**. The most recent commit is `7ed7cfd` — a WIP commit with partially-tested fixes. The previous agent (me) made too many changes at once and lost the ability to isolate problems. This document is an honest accounting of what's known, what's uncertain, and what hasn't been tried.

## What Works

- **Both HDLC links connect and stay connected when idle.** ESP32 ↔ RP2040 and ESP32 ↔ S3 both complete SABM/UA handshake and maintain keepalives indefinitely with no disconnects — as long as no application data is sent.
- **Boot query (GET_CRCS, QUERY_COUNT) succeeds for S3.** The S3 responds to `queryS3ImageCount()` and reports its image count correctly.
- **Boot query sometimes succeeds for RP2040.** The RP2040 responded correctly in one test session (reported 5 images, answered CRC queries). In other sessions it fails.
- **S3 GET_CONFIG text command works.** The S3 successfully receives and responds to CONFIG text over HDLC.

## What Doesn't Work

1. **Image uploads to both devices fail.** The ESP32 sends `MSG_IMG_START` (upload start), the device should respond with `MSG_RESP_READY`, but the response never arrives (or arrives too late). ProtoQueue times out waiting for READY. Every upload attempt in the logs shows `FAIL op=2 slot=N offset=0/SIZE` — offset 0 means no data was ever sent, it failed at the START/READY handshake.

2. **RP2040 disconnects under load.** When boot sync starts pushing data (CRC queries, MAP commands, image uploads), the RP2040 HDLC link disconnects within ~1 second. It reconnects eventually (sometimes 90+ seconds later) but then boot sync has already given up.

3. **S3 CONFIG text send fails after uploads.** After all upload attempts time out, the final `sendText(CONFIG:...)` also fails with -2. This suggests the protocol state is degraded after the failed upload sequence.

## What I Changed (commit 7ed7cfd)

### Likely correct changes:

1. **Buffer-based service() in uart_proto.h** — The original code used `run_rx(readStatic)` and `run_tx(writeStatic)` callback APIs. These callbacks use a **4-byte internal buffer** (`uint8_t buf[4]` in TinyProtocolFd.cpp lines 102 and 117), meaning each call only processes 4 bytes. At 38400 baud, bytes arrive faster than 4-per-call can drain them. Replaced with buffer-based `run_rx(data, len)` and `run_tx(data, max_size)` using 256-byte buffers with loops. This is definitely the right approach — the library's own examples use buffer-based or set up background threads.

2. **Debug logging on all send methods** — Every `send()`, `sendText()`, `sendEmpty()`, `sendResponse()`, `sendChunk()` now logs failures with error code. This is pure instrumentation, no behavioral change.

3. **Pumping service() during boot waits** — The original code had `delay(3000)` before querying each device. During that delay, HDLC can't handshake because nobody calls `run_rx()`/`run_tx()`. Changed to a loop that calls `protoRP.service()` (and `protoS3.service()` for the second wait). This is clearly correct — HDLC needs continuous frame exchange to establish the link.

4. **isConnected() check before blocking query sends** — `queryImageCount()` and `queryS3ImageCount()` now wait up to 2s for connection before sending `MSG_QUERY_COUNT`. Previously they sent immediately regardless of link state, which with TinyProto returns -2 (TIMEOUT) if the link isn't established.

5. **isConnected() checks in ProtoQueue** — `startText()`, `startFileUpload()`, `startBufferUpload()`, and `startQuery()` all check `link->isConnected()` and fail fast with callback notification instead of sending into a disconnected link and timing out 5s later.

6. **isBusy() helper and GET_CONFIG flood prevention** — S3 `loop()` was queueing `GET_CONFIG` every 500ms during boot sync. With TinyProto's window, these queue up and flood the TX window. Added `isBusy()` check to skip if queue is already processing.

### Speculative changes that may need reverting:

7. **PROTOLINK_BUF_SIZE formula** — Changed from `4096 * PROTOLINK_WINDOW` (= 16384 bytes) to `tiny_fd_buffer_size_by_mtu(520, 4)` (= 2930 bytes). The formula is the library's own recommended calculation, used in its examples. The old value was a generous overestimate. Both should work — TinyProto auto-calculates MTU from buffer size. BUT: the old value gave more headroom and the new value hasn't been proven to work. The 2930-byte buffer might be too tight for some edge case. **This is untested** — if you're reverting things, this is a candidate. To revert: change line 25 of `lib/uart_proto/uart_proto.h` back to `#define PROTOLINK_BUF_SIZE (4096 * PROTOLINK_WINDOW)`.

8. **S3 sendResp/sendEmpty retry** — In `src_config/main.cpp`, wrapped `sendResponse()` and `sendEmpty()` in retry-once-after-service logic. This is a band-aid — if sends are failing, retrying once after one `service()` call is unlikely to fix the underlying issue. May be harmless but may also mask real problems.

## What I Did NOT Investigate

1. **RP2040 side of the disconnect.** I never looked at what the RP2040 is doing when it disconnects. The RP2040 firmware is in the same `lib/uart_proto/uart_proto.h` (shared library) but its main loop is in a separate source file. The RP2040 might not be calling `service()` fast enough, or its `onMessage` handler might be blocking too long (e.g., writing to LittleFS during an image receive).

2. **S3 side of the upload failure.** I never captured S3 logs during a failed upload attempt. The S3 should receive `MSG_IMG_START`, call `sendEmpty(MSG_RESP_READY)`, and wait for chunks. But maybe `sendEmpty()` is returning -2 on the S3 side too, meaning the READY response never makes it back. To check this, open a serial connection to the S3 and watch its debug output during a boot sync.

3. **Whether the RP2040 has the latest firmware.** The RP2040 was flashed with the buffer-based service() fix and the isConnected() checks. BUT it was flashed early in the debugging session. Many changes were made after that flash. The RP2040 currently does NOT have the `isBusy()` gating or the re-sync loop code. It also doesn't have the init logging. **The RP2040 needs reflashing.** Remember: disconnect UART first, then connect RP2040 via USB to flash.

4. **Whether the problem is app-layer or transport-layer.** I never ran a minimal test — just SABM/UA connection + one small text message, with no boot sync. The other reviewing agent suggested this and it's the right approach. A minimal test would be: disable boot sync entirely, wait for both links to connect, then send a single `sendText("hello")` and see if the other side receives it.

5. **Whether chunking is even needed.** The user pushed back on this and I kept insisting chunking was necessary. TinyProto's Fd protocol handles fragmentation internally — `tiny_fd_send_packet()` accepts packets up to MTU size and fragments them into HDLC frames. The app-layer 512-byte chunking in ProtoQueue's upload state machine may be unnecessary with TinyProto. However, the non-blocking send API (timeout=0) means a large send might return -2 if the window is full, so some form of flow control is still needed. This is worth understanding clearly before making changes.

## Key TinyProto Facts (verified by reading library source)

- `FdD` constructor takes buffer_size, allocates with `new uint8_t[size]`
- `IFd::begin()` does NOT set `init.mtu` — it stays 0, which triggers auto-calculation from buffer_size
- `IFd::write()` calls `tiny_fd_send_packet(m_handle, buf, size, m_sendTimeout)` — with timeout=0, returns TINY_ERR_TIMEOUT (-2) immediately if TX queue is full
- TINY_ERR_TIMEOUT (-2) means "no room in internal queue" — NOT "link is disconnected" (that's TINY_ERR_FAILED = -1)
- `run_rx(read_func)` and `run_tx(write_func)` callback versions use 4-byte internal buffers — do NOT use these
- `run_rx(const void *data, int len)` and `run_tx(void *data, int max_size)` buffer versions process full buffers — use THESE
- Default keepalive timeout: 5000ms, disconnect at 2x (10s)
- Default retry_timeout: 200ms, retries: 2
- ABM mode: both sides can initiate SABM
- `proto.getStatus()` returns `TINY_SUCCESS (0)` when connected, `-1` when not

## Recommended Approach for Next Agent

**Do not continue where I left off.** I was making too many changes at once and lost track of what was tested vs. speculative.

1. **Start with a minimal test.** Disable all boot sync. Flash all three boards. Verify both links connect and stay connected. Then manually trigger one small text send (e.g., via USB serial command) and verify it arrives. This isolates transport from application.

2. **If the minimal test works**, re-enable boot sync one piece at a time: first just the count query (no uploads), then one upload, then the full sync. Each step: flash, test, observe.

3. **If the minimal test fails**, the problem is in the TinyProto integration itself — buffer sizing, service() timing, or something fundamental. In that case, check baud rate consistency, check that both sides use the same PROTOLINK_BUF_SIZE and PROTOLINK_WINDOW, and consider reverting the buffer size formula change.

4. **Read the RP2040 and S3 firmware** (`src_config/main.cpp` for S3, find the RP2040 main). Understand how they handle incoming messages, especially image upload starts. Look for anything that might block the main loop long enough to cause HDLC keepalive timeout (5s default, disconnect at 10s).

5. **Consider whether ProtoQueue's upload state machine is compatible with TinyProto.** The old SerialTransfer was fire-and-forget — sends never failed. ProtoQueue was designed around that assumption. With TinyProto, sends CAN fail (-2), and the queue doesn't retry failed sends — it just transitions to a wait state that times out. This might need a fundamental rethink: either add retry logic to ProtoQueue, or increase the send timeout so sends block until the window has room.

## Files to Read

- `lib/uart_proto/uart_proto.h` — ProtoLink wrapper (the shared library all three boards use)
- `lib/uart_proto/uart_msg.h` — Message type constants and send helpers
- `lib/uart_queue/uart_queue.h` — ProtoQueue (ESP32 and S3 only, not RP2040)
- `src/main.cpp` — ESP32 main firmware (boot sync at ~line 2570, re-sync at ~line 2860)
- `src_config/main.cpp` — S3 firmware (upload handler, GET_CONFIG handler)
- RP2040 main source — search for it, I didn't look at it closely enough

## What's Currently Flashed on Each Board

- **ESP32**: commit 7ed7cfd (the WIP commit). Has all changes listed above. Boot sync IS enabled.
- **S3**: has buffer-based service(), isBusy() gate, sendResp/sendEmpty retry. Flashed earlier in the session.
- **RP2040**: has buffer-based service() and isConnected() checks, but NOT the latest isBusy() or re-sync changes. Was flashed early in the session. Needs reflashing.

## Hardware Setup

- ESP32 connects to USB via `/dev/cu.usbserial-*` — serial logger runs on this port
- S3 connects to USB via `/dev/cu.usbmodem*` — can flash while UART is connected
- RP2040 connects to USB via `/dev/cu.usbmodem*` — MUST disconnect UART before connecting USB
- Serial logger: `tools/serial_logger.py` — auto-restarts after flash, logs to `logs/esp32.log`
- Flash tool: `./tools/flash.sh <env>` — pauses serial logger, flashes, resumes
- Only one USB port available at a time for RP2040 (user swaps cables)
