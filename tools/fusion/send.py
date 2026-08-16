"""Run a `session.py` call inside Fusion, from a shell.

    python3 tools/fusion/send.py "sync()"
    python3 tools/fusion/send.py "opened()" "look('front')"
    python3 tools/fusion/send.py --raw "print(adsk.core.Application.get().version)"

Fusion's MCP server speaks streamable HTTP on 127.0.0.1:27182, and `fusion_mcp_execute` takes a
script whose `run(_context)` it calls. Each call here sends `session.py` whole and appends a
`run` that evaluates the arguments in order, printing what each returns.

Stdlib only — this runs on the host, not in `tools/cad-venv` and not in Fusion.

`sync()` takes longer than the MCP client Claude uses will wait, so `--timeout` defaults past it.
"""

import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
URL = "http://127.0.0.1:27182/mcp"
HEADERS = {"Content-Type": "application/json",
           "Accept": "application/json, text/event-stream"}


def _post(body, session=None, timeout=60):
    headers = dict(HEADERS)
    if session:
        headers["mcp-session-id"] = session
    request = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                     headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as reply:
        return reply.headers.get("mcp-session-id"), reply.read().decode()


def _unwrap(text):
    """One JSON-RPC frame, whether it arrived bare or under an SSE `data:` line."""
    for line in text.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:])
    return json.loads(text) if text.strip() else {}


def connect(timeout=60):
    session, text = _post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                           "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                                      "clientInfo": {"name": "hsm-send", "version": "1"}}},
                          timeout=timeout)
    _unwrap(text)
    _post({"jsonrpc": "2.0", "method": "notifications/initialized"}, session, timeout)
    return session


def execute(script, timeout=600):
    session = connect()
    _, text = _post({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                     "params": {"name": "fusion_mcp_execute",
                                "arguments": {"featureType": "script",
                                              "object": {"script": script}}}},
                    session, timeout)
    frame = _unwrap(text)
    if "error" in frame:
        return False, json.dumps(frame["error"], indent=1)
    content = frame.get("result", {}).get("content", [])
    said = "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
    try:
        parsed = json.loads(said)
    except (ValueError, TypeError):
        return True, said
    if isinstance(parsed, dict) and parsed.get("success") is False:
        return False, parsed.get("error", said)
    if isinstance(parsed, dict) and "message" in parsed:
        return True, parsed["message"]
    return True, said


def payload(calls, raw=False):
    if raw:
        body = "\n".join("    " + line for line in "\n".join(calls).splitlines())
        return ("import adsk.core, adsk.fusion\n\n"
                "def run(_context):\n" + (body or "    pass") + "\n")
    lines = ["", "", "def run(_context):"]
    for call in calls:
        lines.append(f"    said = {call}")
        lines.append(f"    print({call!r}, '->', said)")
    return (HERE / "session.py").read_text() + "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("calls", nargs="+", help="session.py expressions, run in order")
    parser.add_argument("--raw", action="store_true",
                        help="send the arguments as a bare script body, without session.py")
    parser.add_argument("--timeout", type=float, default=600.0)
    args = parser.parse_args()

    try:
        ok, said = execute(payload(args.calls, args.raw), args.timeout)
    except urllib.error.URLError as exc:
        sys.exit(f"nothing answered on {URL} ({exc.reason}) — Fusion has to be running with "
                 f"Preferences > General > API > Fusion MCP Server on")
    print(said.rstrip())
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
