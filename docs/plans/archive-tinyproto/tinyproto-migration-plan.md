---
name: TinyProto migration plan
description: Completed plan for SerialTransfer+UartLink → TinyProto+ProtoQueue migration
type: reference
---

COMPLETED. See git history (commits around 2026-03-20) for implementation details.

Migration replaced SerialTransfer (COBS) + UartLink (~930 lines) with TinyProto (HDLC) + ProtoQueue (~430 lines) across all three MCUs. Key files: `lib/uart_msg/uart_msg.h`, `lib/uart_proto/uart_proto.h`, `lib/uart_queue/uart_queue.h`, plus updates to `src/main.cpp`, `src_display/main.cpp`, `src_config/main.cpp`, and `pre_build.py` (RP2040 TinyProto patching).
