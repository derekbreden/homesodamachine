"""Cut tube stock from the Rust cold-core scalar recipe."""

from _cold_core_data import read as _read

globals().update(_read("stock"))
