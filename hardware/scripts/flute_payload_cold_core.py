"""The cold-core shell's printed viewer surface. The cap producer writes its own payloads."""

import flute_payload


if __name__ == "__main__":
    raise SystemExit(flute_payload.rust_main(flute_payload.COLD_CORE_DIRS[:1]))
