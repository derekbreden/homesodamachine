---
name: Use existing libraries instead of writing protocol code
description: When user says "use a library," search for and evaluate existing libraries before writing custom implementations
type: feedback
---

When the user asks to use a library for something, actually search for and evaluate existing libraries. Do not write custom implementations of protocol-level functionality (framing, reliable delivery, flow control, ack/retry) — these are solved problems with battle-tested libraries.

**Why:** User explicitly asked for library-based approach for UART protocol reliability. Instead, UartLink was written from scratch (~850 lines) reimplementing what TinyProto (HDLC, RFC 1662) already provides — with worse results (stale packet timeout bugs, no flow control, hours of debugging). The user had to find TinyProto themselves.

**How to apply:** Before writing any infrastructure/protocol code, search for existing libraries first. Evaluate at least 2-3 options. Present findings to the user. Only write custom code if no suitable library exists or the user explicitly chooses to.
