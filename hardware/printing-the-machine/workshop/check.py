"""Checks the built leaves against the record: every quoted passage appears word for word in a commit
message or a repository file, and every evidence link names a file that exists at its revision."""
import html
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

RUN = Path(__file__).parent
ROOT = RUN.parents[2]
DIST = RUN / "dist"


def norm(s):
    s = html.unescape(s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("‑", "-").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, errors="replace").stdout


def main():
    leaves = sorted(DIST.glob("[0-9][0-9]-*.html"))
    log = norm(git("log", "--format=%B"))
    # ---- quotes
    misses, checked = [], 0
    for leaf in leaves:
        text = leaf.read_text()
        for m in re.finditer(r"<blockquote[^>]*>(.*?)</blockquote>", text, re.S):
            inner = m.group(1)
            body = re.split(r"<footer", inner)[0]
            body = re.sub(r"<[^>]+>", "", body)
            body = norm(body).strip('"').strip()
            for frag in re.split(r"…|\.\.\.", body):
                frag = frag.strip(' "')
                if len(frag) < 18:
                    continue
                checked += 1
                if frag in log:
                    continue
                # a file in the tree?
                key = max(re.split(r"['\"]", frag), key=len)[:70]
                hit = git("grep", "-l", "-F", "--untracked", key, "--", "hardware", "future", "tools", "calibration", "changes").strip()
                if hit:
                    continue
                misses.append((leaf.name, frag))
    # ---- links
    bad, nlinks = [], 0
    for leaf in leaves:
        for m in re.finditer(r'href="https://github\.com/derekbreden/homesodamachine/(blob|tree|commit)/([^"#]+)(#[^"]*)?"', leaf.read_text()):
            kind, rest = m.group(1), unquote(m.group(2))
            nlinks += 1
            if kind == "commit":
                ok = subprocess.run(["git", "cat-file", "-e", rest + "^{commit}"], cwd=ROOT, capture_output=True).returncode == 0
            else:
                rev, _, path = rest.partition("/")
                rev = "HEAD" if rev == "main" else rev
                ok = subprocess.run(["git", "cat-file", "-e", f"{rev}:{path}"], cwd=ROOT, capture_output=True).returncode == 0
            if not ok:
                bad.append((leaf.name, kind, rest))
    print(f"{len(leaves)} leaves; {checked} quoted passages checked, {len(misses)} not found; {nlinks} links checked, {len(bad)} broken")
    for name, frag in misses:
        print("  QUOTE?", name, "::", frag[:150])
    for name, kind, rest in bad:
        print("  LINK? ", name, "::", kind, rest[:150])
    return 1 if (misses or bad) else 0


if __name__ == "__main__":
    sys.exit(main())
