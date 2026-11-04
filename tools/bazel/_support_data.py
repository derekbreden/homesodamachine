"""Standard parser/tokenizer object marshalling for native build support."""
import ast
import io
from pathlib import Path
import sys
import tokenize

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "hardware/scripts"))
from _build_data import request as _request


def _provider(query):
    raw = bytes(query["bytes"])
    if query["op"] == "parse-source":
        try:
            return {"dump": ast.dump(ast.parse(raw))}
        except (SyntaxError, ValueError):
            return {"dump": None}
    if query["op"] == "tokenize-source":
        try:
            encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
        except SyntaxError:
            return {"encoding": None, "tokens": []}
        if encoding != "utf-8":
            return {"encoding": encoding, "tokens": []}
        return {"encoding": encoding,
                "tokens": [(tokenize.tok_name[token.type], token.start, token.end)
                           for token in tokenize.tokenize(io.BytesIO(raw).readline)]}
    raise ValueError(query["op"])


def request(op, **fields):
    return _request(op, callback=_provider, **fields)
