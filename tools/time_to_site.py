#!/usr/bin/env python3
"""time_to_site.py — how long a change waits between being committed and being on the site.

    tools/cad-venv/bin/python tools/time_to_site.py            what is live, and what is not yet
    tools/cad-venv/bin/python tools/time_to_site.py --watch    sit until the site moves, and time it

THE NUMBER THIS TREE IS BUILT AROUND. A commit reaches homesodamachine.com by being pushed:
`render.yaml` sets autoDeploy and names the paths that trigger one, and Render serves the
commit it built. `/api/version` answers with that commit, so the distance between a change
existing and Derek being able to see it is measurable from outside and does not need CI's
account of itself.

WHICH PATHS COUNT IS READ FROM render.yaml, not restated here. A commit touching none of them
deploys nothing and is not late for anything, and counting it as unshipped would report a lag
that no push would ever clear.

--watch TIMES A REAL TRANSITION. It reads the live commit, waits for it to change, and reports
the wait against the new commit's own committer timestamp — so the figure spans the whole path,
push through build through serve, and not the part any one machine can see.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True).stdout.strip() or ".")
VERSION_URL = "https://homesodamachine.com/api/version"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(ROOT),
                          capture_output=True, text=True).stdout.strip()


def _yaml_list(text: str, key: str) -> list:
    """The `- ` entries under one key, comment lines and all skipped."""
    m = re.search(rf"\n\s*{key}:\s*\n((?:[ \t]*(?:#[^\n]*)?\n|[ \t]*-[ \t]*\S+[ \t]*\n)+)", text)
    if not m:
        return []
    return [ln.strip()[1:].strip() for ln in m.group(1).splitlines() if ln.strip().startswith("-")]


def deploy_filter() -> tuple:
    """The buildFilter, read off render.yaml so it cannot drift from what Render does.

    BOTH HALVES OF IT. Render builds on a changed file that is under `paths` and NOT under
    `ignoredPaths`, and the second half is not a footnote here: `web/public/checks.json` is
    pinned after every commit, so reading `paths` alone counts the most frequent commit in this
    tree as a deploy that will never happen. That is the lag no push would ever clear, which is
    the one reading this file exists to not report."""
    text = (ROOT / "render.yaml").read_text()
    body = text.split("buildFilter:", 1)
    if len(body) < 2:
        return ["web/**", "hardware/cad-artifacts.lock.json", "updates/**", "render.yaml"], []
    return (_yaml_list(body[1], "paths")
            or ["web/**", "hardware/cad-artifacts.lock.json", "updates/**", "render.yaml"],
            _yaml_list(body[1], "ignoredPaths"))


def under(f: str, patterns: list) -> bool:
    return any(fnmatch.fnmatch(f, p) or (p.endswith("/**") and f.startswith(p[:-2]))
               for p in patterns)


def deploys(sha: str, patterns: list, ignored: list) -> bool:
    files = git("show", "--name-only", "--format=", sha).splitlines()
    return any(under(f, patterns) and not under(f, ignored) for f in files)


def live() -> str:
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=20) as r:
            return json.load(r).get("commit", "")
    except Exception:
        return ""


def age(sha: str) -> float:
    when = git("show", "-s", "--format=%cI", sha)
    if not when:
        return 0.0
    return (datetime.now(timezone.utc)
            - datetime.fromisoformat(when).astimezone(timezone.utc)).total_seconds()


def human(sec: float) -> str:
    if sec < 90:
        return f"{sec:.0f}s"
    if sec < 5400:
        return f"{sec / 60:.1f} min"
    return f"{sec / 3600:.1f} h"


def report() -> int:
    git("fetch", "--quiet", "origin", "main")
    served = live()
    if not served:
        print(f"  {VERSION_URL} did not answer — nothing can be said about the lag")
        return 1
    known = git("cat-file", "-t", served) == "commit"
    print(f"  live   {served[:8]}  {'served ' + human(age(served)) + ' ago' if known else '(not in this checkout)'}")
    if not known:
        return 0

    patterns, ignored = deploy_filter()
    ahead = git("rev-list", f"{served}..origin/main").split()
    waiting = [s for s in ahead if deploys(s, patterns, ignored)]
    print(f"  origin {git('rev-parse', '--short', 'origin/main')}  "
          f"{len(ahead)} commit(s) past what is live, {len(waiting)} of them deploying")
    if not waiting:
        print("\n  nothing is waiting: every commit past the live one touches no deploying path")
        return 0
    oldest = waiting[-1]
    print(f"\n  oldest change not yet visible: {oldest[:8]}  committed {human(age(oldest))} ago")
    for s in waiting[-5:][::-1]:
        print(f"    {s[:8]}  {human(age(s)):>8} ago  {git('show', '-s', '--format=%s', s)[:56]}")
    return 0


def watch(timeout: float) -> int:
    start = live()
    print(f"  live now: {start[:8] or '(no answer)'} — waiting for it to move")
    began = time.time()
    while time.time() - began < timeout:
        time.sleep(15)
        now = live()
        if now and now != start:
            git("fetch", "--quiet", "origin", "main")
            known = git("cat-file", "-t", now) == "commit"
            print(f"  live moved to {now[:8]} after {human(time.time() - began)} of waiting")
            if known:
                print(f"  that commit was made {human(age(now))} ago — "
                      f"commit to visible, whole path")
            return 0
    print(f"  the site did not move within {human(timeout)}")
    return 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--watch", action="store_true", help="wait for the site to move and time it")
    ap.add_argument("--timeout", type=float, default=1800.0)
    args = ap.parse_args(argv)
    return watch(args.timeout) if args.watch else report()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
