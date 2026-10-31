#!/usr/bin/env python3
"""Missing tools: what the code agents wrote for themselves read in the repo, and the longest waits.

    python3 tools/missing_tools.py                       # the last 7 days
    python3 tools/missing_tools.py --days 14
    python3 tools/missing_tools.py --show '*.step.mesh'  # the code behind one row

It reads this repo's Claude Code transcripts and Codex rollouts from the window,
offloaded ones included, and takes from each session the code it wrote and ran
for itself: a heredoc fed to an interpreter, a `-c` or `-e` string, or a code
file written to a scratchpad or /tmp. Each row of the first table is a file in
the repo, or a kind of file, that such code opened or imported, with how many
sessions' code did and what a few of them said it was for; `--show` prints that
code. The second table is the tool runs that held a session two minutes or
more, counting the calls that ran each and the calls that waited on it, longest
first, with what each ran.

Reading an offloaded transcript downloads it from iCloud Drive, sixteen at a
time; the hourly transcript offload evicts it again. `--show` reads the last
run's findings from .cache/missing_tools.json while they are under twelve
hours old.
"""
import argparse
import ast
import glob
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import warnings
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

HOME = os.path.expanduser("~")
MAIN = os.path.dirname(subprocess.run(
    ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
    cwd=os.path.dirname(os.path.abspath(__file__)), capture_output=True, text=True, check=True).stdout.strip())
CLAUDE_PROJECTS = os.path.join(HOME, ".claude", "projects")
CLAUDE_META = os.path.join(HOME, "Library", "Application Support", "Claude", "claude-code-sessions")
CODEX = os.path.join(HOME, ".codex")
SF_DATALESS = 0x40000000  # st_flags bit of a file whose data lives only in iCloud
WORKERS = 16
warnings.filterwarnings("ignore", category=SyntaxWarning)  # escapes JS allows and Python doesn't
warnings.filterwarnings("ignore", category=DeprecationWarning)

FILES = [p for p in subprocess.run(["git", "-C", MAIN, "ls-files"], capture_output=True, text=True,
                                   check=True).stdout.split("\n") if p]
TOPS = sorted({p.split("/", 1)[0] for p in FILES if "/" in p and not p.startswith(".")})
STOP = {"__init__", "build", "common", "main", "test", "tests", "conftest", "setup", "config", "util", "utils",
        "helpers", "app", "index", "run", "cli"}
_by_name = defaultdict(list)
for _p in FILES:
    if _p.endswith(".py"):
        _by_name[os.path.basename(_p)[:-3]].append(_p)
MODULES = {name: paths[0] if len(paths) == 1 else f"{name}.py" for name, paths in _by_name.items()
           if len(paths) <= 2 and name not in STOP and name not in sys.stdlib_module_names}
# Files of these kinds are many and built; a row counts them together.
KINDS = (".step.mesh", ".facts.json", ".step", ".stp", ".stl", ".3mf", ".glb", ".gcode",
         ".png", ".jpg", ".jpeg", ".webp", ".svg", ".pdf")
CODE_EXT = (".py", ".mjs", ".cjs", ".js", ".ts", ".swift")

PATH = re.compile(r"(?<![\w.\-])(?:" + "|".join(map(re.escape, TOPS)) + r")/[\w.\-/*{}@+]+")
IMPORT = re.compile(r"^[ \t]*(?:from[ \t]+([\w.]+)[ \t]+import[ \t]+\(?([\w \t,*]+)|import[ \t]+([\w. \t,]+))", re.M)
RUNNER = re.compile(r"\b(?:python3?(?:\.\d+)?|node|ruby|perl|osascript|swift)\b")
CODE_FILE = re.compile(r">\s*\S+\.(?:py|mjs|cjs|js|ts|swift)\b")
HEREDOC = re.compile(r"(?P<lead>[^\n]*?)<<-?[ \t]*(?P<q>['\"]?)(?P<tag>[A-Za-z_]\w*)(?P=q)(?P<tail>[^\n]*)\n"
                     r"(?P<body>.*?)\n[ \t]*(?P=tag)[ \t]*(?=\n|$)", re.S)
DASH_C = re.compile(r"\b(?:python3?(?:\.\d+)?|node|osascript)\b[^\n|;&]*?\s-[ce]\s+"
                    r"(?P<code>\"(?:[^\"\\]|\\.)*\"|'[^']*')", re.S)
JS_CMD = re.compile(r"\bcmd\s*:\s*(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)", re.S)
CELL = re.compile(r"Script running with cell ID (\w+)")
STILL = re.compile(r'"session_id":\s*(\d+)|Process running with session ID (\d+)')
POLL = re.compile(r"session_id\s*:\s*(\d+)")


def stamp(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def gist(desc, code):
    """What a script said it was for: its call's description, its docstring or first comment, or its first line."""
    if desc:
        return " ".join(desc.split())
    m = (re.search(r"^\s*(?:\"\"\"|''')\s*(\S[^\n]*?)\s*(?:\"\"\"|''')?\s*$", code, re.M)
         or re.search(r"^\s*(?:#|//)\s*(\S[^\n]*)$", code, re.M))
    if m and not m.group(1).startswith("!"):
        return m.group(1).strip()
    for line in code.splitlines():
        s = line.strip()
        if s and not s.startswith(("import ", "from ", "#!", "cd ", "set ", "const ", "let ")):
            return s
    return ""


def inline_code(cmd):
    """The code a shell command runs from its own text: heredoc bodies fed to an interpreter or written to a
    code file, and -c or -e strings."""
    out = [m.group("body") for m in HEREDOC.finditer(cmd)
           if RUNNER.search(m.group("lead") + m.group("tail")) or CODE_FILE.search(m.group("lead") + m.group("tail"))]
    for m in DASH_C.finditer(cmd):
        s = m.group("code")[1:-1]
        out.append(s.replace('\\"', '"').replace("\\$", "$").replace("\\\\", "\\") if m.group("code")[0] == '"' else s)
    return out


def js_string(s):
    if s[0] == "`":
        return s[1:-1].replace("\\`", "`").replace("\\\\", "\\")
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return s[1:-1]


def scratch(path):
    """A code file written outside the repo's own work: a scratchpad, /tmp, or the repo's .cache."""
    if not path.endswith(CODE_EXT):
        return False
    if path.startswith(os.path.join(MAIN, ".cache") + "/"):
        return True
    parts = path.split("/")
    return ("scratchpad" in parts or path.startswith(("/tmp/", "/private/tmp/", "/var/folders/"))) \
        and not set(parts) & set(TOPS)


def reads(code):
    """The repo files, and kinds of file, a script opens or imports."""
    out = set()
    for m in PATH.finditer(code):
        p = m.group(0).rstrip(".,:;)]}'\"`")
        base = p.rsplit("/", 1)[-1].lower()
        kind = next((k for k in KINDS if base.endswith(k)), None)
        if kind:
            out.add("*" + kind)
        elif "*" not in p and "{" not in p and "." in base and not base.endswith(".md") \
                and os.path.exists(os.path.join(MAIN, p)):
            out.add(p)
    for m in IMPORT.finditer(code):
        names = [m.group(1).rsplit(".", 1)[-1]] + (m.group(2) or "").split(",") if m.group(1) \
            else (m.group(3) or "").split(",")
        for name in names:
            name = name.split(" as ")[0].strip().rsplit(".", 1)[-1]
            if name in MODULES:
                out.add(MODULES[name])
    return out


class Session:
    def __init__(self, agent, sid, path, title=""):
        self.agent, self.sid, self.path, self.title = agent, sid, path, title
        self.scripts, self.waits, self.downloaded = [], [], 0

    def script(self, key, ts, desc, code):
        if code.strip():
            self.scripts.append({"key": key, "ts": ts, "gist": gist(desc, code), "code": code, "reads": reads(code)})


def claude_scan(s, since):
    calls = {}
    for raw in open(s.path, "rb"):
        if b'"tool_use"' in raw or b'"tool_result"' in raw:
            try:
                d = json.loads(raw)
            except ValueError:
                continue
            ts, content = d.get("timestamp") or "", (d.get("message") or {}).get("content")
            for b in content if isinstance(content, list) else []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use" and ts >= since:
                    name, inp = b.get("name"), b.get("input") or {}
                    if name == "Bash":
                        cmd = str(inp.get("command") or "")
                        for i, code in enumerate(inline_code(cmd)):
                            s.script(f"{b.get('id')}:{i}", ts, inp.get("description"), code)
                        if not inp.get("run_in_background"):
                            calls[b.get("id")] = (ts, inp.get("description") or cmd.split("\n")[0])
                    elif name in ("Write", "Edit") and scratch(str(inp.get("file_path") or "")):
                        code = str(inp.get("content") or inp.get("new_string") or "")
                        s.script(b.get("id"), ts, os.path.basename(inp["file_path"]) if name == "Edit" else None, code)
                elif b.get("type") == "tool_result" and b.get("tool_use_id") in calls and ts:
                    t0, what = calls.pop(b["tool_use_id"])
                    s.waits.append((stamp(ts) - stamp(t0), t0, what, b["tool_use_id"]))
        elif b'"custom-title"' in raw:
            try:
                s.title = json.loads(raw).get("customTitle") or s.title
            except ValueError:
                pass


def codex_text(out):
    if isinstance(out, str):
        return out
    if isinstance(out, list):
        return "".join(x.get("text", "") for x in out if isinstance(x, dict))
    return "" if out is None else json.dumps(out)


def codex_scan(s, since):
    # A run's wait is the time the calls that ran it and polled it kept the session blocked: a cell that
    # yields counts again in each `wait` on it, a command still running when its cell ends in each poll.
    pending, cells, running = {}, {}, {}
    for raw in open(s.path, "rb"):
        if b'_call' not in raw[:200]:
            continue
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        ts, pl = d.get("timestamp") or "", d.get("payload") or {}
        kind, name, cid = pl.get("type"), pl.get("name"), pl.get("call_id")
        if ts < since:
            continue
        if kind == "custom_tool_call" and name == "exec":
            code = pl.get("input") or ""
            cmds = [js_string(m.group(1)) for m in JS_CMD.finditer(code)]
            for i, cmd in enumerate(cmds):
                for j, body in enumerate(inline_code(cmd)):
                    s.script(f"{cid}:{i}:{j}", ts, None, body)
            polls = {n for n in POLL.findall(code) if n in running}
            if cmds or polls:
                pending[cid] = (ts, {"t0": ts, "what": cmds[0].split("\n")[0] if cmds else None, "polls": polls,
                                     "id": cid, "held": 0.0})
        elif kind == "function_call" and name in ("exec_command", "shell", "shell_command", "local_shell"):
            try:
                args = json.loads(pl.get("arguments") or "{}")
            except ValueError:
                continue
            cmd = args.get("cmd") or args.get("command") or ""
            cmd = cmd[-1] if isinstance(cmd, list) and cmd else str(cmd)
            for j, body in enumerate(inline_code(cmd)):
                s.script(f"{cid}:{j}", ts, None, body)
            pending[cid] = (ts, {"t0": ts, "what": cmd.split("\n")[0], "polls": set(), "id": cid, "held": 0.0})
        elif kind == "function_call" and name in ("wait", "write_stdin"):
            try:
                args = json.loads(pl.get("arguments") or "{}")
            except ValueError:
                continue
            if str(args.get("cell_id")) in cells:
                pending[cid] = (ts, cells.pop(str(args["cell_id"])))
            elif str(args.get("session_id")) in running:
                pending[cid] = (ts, {"t0": ts, "what": None, "polls": {str(args["session_id"])}, "id": cid,
                                     "held": 0.0})
        elif kind == "custom_tool_call" and name == "apply_patch":
            for path, body in re.findall(r"^\*\*\* Add File: (\S+)\n((?:\+.*\n?)*)", pl.get("input") or "", re.M):
                if scratch(path):
                    s.script(f"{cid}:{path}", ts, None, "\n".join(l[1:] for l in body.splitlines()))
        elif kind in ("custom_tool_call_output", "function_call_output") and cid in pending:
            t_call, e = pending.pop(cid)
            e["held"] += stamp(ts) - stamp(t_call)
            text = codex_text(pl.get("output"))
            cell = CELL.match(text)
            if cell:
                cells[cell.group(1)] = e
                continue
            still = {a or b for a, b in STILL.findall(text)}
            for n in e["polls"] & running.keys():
                running[n]["held"] += e["held"]
                if n not in still:
                    r = running.pop(n)
                    s.waits.append((r["held"], r["t0"], r["what"], r["id"]))
            if e["what"]:
                for n in still - e["polls"]:
                    running.setdefault(n, dict(e, polls=set()))
                if not still - e["polls"]:
                    s.waits.append((e["held"], e["t0"], e["what"], e["id"]))


def claude_sessions():
    prefix = MAIN.replace("/", "-").replace(".", "-")
    for d in glob.glob(os.path.join(CLAUDE_PROJECTS, glob.escape(prefix) + "*")):
        for p in glob.glob(os.path.join(glob.escape(d), "**", "*.jsonl"), recursive=True):
            yield "claude", os.path.relpath(p, d).split("/")[0].removesuffix(".jsonl"), p


def codex_sessions():
    dbs = glob.glob(os.path.join(CODEX, "state_*.sqlite"))
    if not dbs:
        return {}
    db = max(dbs, key=lambda p: int(re.search(r"_(\d+)\.sqlite$", p).group(1)))
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = con.execute("SELECT id, rollout_path, coalesce(nullif(name, ''), nullif(title, ''), agent_nickname, '') "
                       "FROM threads WHERE cwd LIKE ?", (f"%/{os.path.basename(MAIN)}%",)).fetchall()
    return {sid: (path, title) for sid, path, title in rows if path}


def claude_titles():
    """Each Claude Code session id's title in the desktop app, and the ids of sessions forked from another."""
    titles, forks = {}, set()
    for p in glob.glob(os.path.join(glob.escape(CLAUDE_META), "*", "*", "local_*.json")):
        try:
            m = json.load(open(p))
        except (OSError, ValueError):
            continue
        for sid in [m.get("cliSessionId")] + (m.get("priorCliSessionIds") or []):
            if sid:
                titles[sid] = m.get("title") or ""
                if m.get("forkedFromSessionId"):
                    forks.add(sid)
    return titles, forks


def scan(s, since):
    try:
        st = os.stat(s.path)
        if st.st_flags & SF_DATALESS:
            s.downloaded = st.st_size
        (claude_scan if s.agent == "claude" else codex_scan)(s, since)
    except OSError as e:
        print(f"  could not read {s.path}: {e}", file=sys.stderr)
    return s



CACHE = os.path.join(MAIN, ".cache", "missing_tools.json")


def gather(days):
    """Every session's scripts and waits in the window, each call counted once, saved for `--show`."""
    t_start = time.time()
    since_t = t_start - days * 86400
    since = datetime.fromtimestamp(since_t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    titles, forks = claude_titles()
    codex = codex_sessions()
    titles.update({sid: title for sid, (_, title) in codex.items()})
    sessions = [Session(agent, sid, p) for agent, sid, p in claude_sessions()]
    sessions += [Session("codex", sid, p) for sid, (p, _) in codex.items()]
    sessions = [s for s in sessions if os.path.exists(s.path) and os.stat(s.path).st_mtime >= since_t]
    offloaded = sum(os.stat(s.path).st_size for s in sessions if os.stat(s.path).st_flags & SF_DATALESS)
    print(f"reading {len(sessions)} transcripts, {offloaded / 1e9:.1f} GB of them from iCloud", file=sys.stderr)
    with ThreadPoolExecutor(WORKERS) as ex:
        sessions = list(ex.map(lambda s: scan(s, since), sessions))
    # A fork's transcript repeats its parent's calls under the same ids; each call counts once, in the parent.
    sessions.sort(key=lambda s: (s.sid in forks, s.path))
    scripts, waits, seen = [], [], set()
    for s in sessions:
        for x in s.scripts:
            if x["key"] not in seen:
                seen.add(x["key"])
                scripts.append(dict(x, agent=s.agent, sid=s.sid, reads=sorted(x["reads"])))
        for w, t0, what, wid in s.waits:
            if ("wait", wid) not in seen:
                seen.add(("wait", wid))
                waits.append({"agent": s.agent, "sid": s.sid, "seconds": w, "t0": t0,
                              "what": " ".join(str(what).split())})
    run = {"days": days, "since": since_t, "made": time.time(), "seconds": time.time() - t_start,
           "sessions": len({(s.agent, s.sid) for s in sessions}), "downloaded": sum(s.downloaded for s in sessions),
           "titles": {s.sid: titles.get(s.sid) or s.title for s in sessions}, "scripts": scripts, "waits": waits}
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w") as f:
        json.dump(run, f)
    return run


def cached(days):
    """The last run's findings, when they cover the same days and are under twelve hours old."""
    try:
        run = json.load(open(CACHE))
    except (OSError, ValueError):
        return None
    return run if run.get("days") == days and time.time() - run.get("made", 0) < 12 * 3600 else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--days", type=float, default=7, help="the window, ending now (default 7)")
    ap.add_argument("--show", metavar="ROW", help="print the code behind one row of the first table")
    ap.add_argument("--top", type=int, default=15, help="rows in each table (default 15)")
    ap.add_argument("--min-wait", type=float, default=120, help="seconds a wait must reach to be listed (default 120)")
    a = ap.parse_args()

    run = (a.show and cached(a.days)) or gather(a.days)
    titles, scripts = run["titles"], run["scripts"]

    def label(agent, sid):
        return f"{titles.get(sid) or '(untitled)'} [{agent} {sid[:8]}]"

    if a.show:
        hits = sorted((x for x in scripts if a.show in x["reads"]), key=lambda x: x["ts"])
        codes = set()
        for x in hits:
            if x["code"] in codes:
                continue
            codes.add(x["code"])
            lines = x["code"].strip("\n").split("\n")
            print(f"\n== {x['ts'][:16].replace('T', ' ')}  {label(x['agent'], x['sid'])}\n   {x['gist'][:110]}")
            print("\n".join("   | " + l for l in lines[:80]) + (f"\n   | ... {len(lines) - 80} more lines" if len(lines) > 80 else ""))
        print(f"\n{len(hits)} scripts read {a.show}, {len(codes)} of them different, "
              f"in {len({(x['agent'], x['sid']) for x in hits})} sessions")
        return

    day = lambda t: datetime.fromtimestamp(t).strftime("%b %-d")
    print(f"Code agents wrote for themselves, {day(run['since'])} to {day(run['made'])}: {len(scripts)} scripts in "
          f"{len({(x['agent'], x['sid']) for x in scripts})} of {run['sessions']} sessions "
          f"({run['downloaded'] / 1e9:.1f} GB downloaded, {run['seconds']:.0f} s)")
    rows = defaultdict(lambda: {"sessions": {}, "scripts": 0})
    for x in scripts:
        for k in x["reads"]:
            rows[k]["scripts"] += 1
            rows[k]["sessions"].setdefault((x["agent"], x["sid"]), x)
    shared = sorted(((k, r) for k, r in rows.items() if len(r["sessions"]) > 1),
                    key=lambda kr: (-len(kr[1]["sessions"]), -kr[1]["scripts"], kr[0]))
    print(f"\nWhat that code read, shared by more than one session\n  sessions  scripts  read")
    for k, r in shared[:a.top]:
        print(f"  {len(r['sessions']):8}  {r['scripts']:7}  {k}")
        for (agent, sid), x in list(r["sessions"].items())[:2]:
            print(f"                     {x['gist'][:64]:64}  {label(agent, sid)[:48]}")

    long_waits = sorted((w for w in run["waits"] if w["seconds"] >= a.min_wait), key=lambda w: -w["seconds"])
    held, spans = 0.0, defaultdict(list)
    for w in long_waits:
        spans[(w["agent"], w["sid"])].append((stamp(w["t0"]), stamp(w["t0"]) + w["seconds"]))
    for session in spans.values():
        end = -1.0
        for lo, hi in sorted(session):  # a session's time held, with waits that overlap counted once
            held += max(0.0, hi - max(lo, end))
            end = max(end, hi)
    print(f"\nWaits of {a.min_wait / 60:g} min or more: {len(long_waits)}, holding their sessions "
          f"{held / 3600:.1f} h in all")
    for w in long_waits[:a.top]:
        print(f"  {w['seconds'] / 60:6.1f} min  {w['t0'][:10]}  {w['what'][:64]:64}  {label(w['agent'], w['sid'])[:48]}")


if __name__ == "__main__":
    main()
