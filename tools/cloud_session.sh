#!/bin/bash
# cloud_session.sh — the machine a cloud session starts on, stood up to run this tree.
#
#     tools/cloud_session.sh            # install what is missing, fetch what the pointer file names
#     tools/cloud_session.sh --check    # say what is missing and install nothing
#
# A cloud session (Claude Code on the web, CLAUDE_CODE_REMOTE=true) starts from a fresh,
# shallow clone on a Linux x86_64 box with python and node and nothing this tree builds with:
# no CadQuery, no bazel, no gh, no solids, and fifty commits of history. The
# Mac has all of it by hand and `tools/ci-image/Dockerfile` bakes it for the runner; this is
# the third machine, assembled on session start. Every step is idempotent and skips what is
# already there, so a second run costs a few seconds.
#
# THE KERNEL HERE IS THE RUNNER'S, NOT THE MAC'S. `cadquery-ocp` at the pin resolves to the
# manylinux_2_31_x86_64 wheel, the same one `derive` runs in, so what this machine cuts is
# byte-identical to what the runner cuts and NOT to what the Mac writes into the pointer file
# (`publish.yml` says why: 95 of 124 members differ across the two wheels). A session here can
# build, check, derive, compare and publish: like any machine, it moves the lines for what it cut.
#
# WHAT EACH STEP BUYS:
#   web/node_modules            `npm test`, and `check_web_tests.py` reads red without it
#   tools/cad-venv              every generator and every check that imports one
#   the pointed-at solids           `check_paths`, `check_step_colours`, the parts-tree tests
#   gh                          `pack.py` uploads with it; `check_release_room` reads through it
#   bazel                       `bazel build <target>`, `sync_tree.py`, `affected.py`
#   .cache                      `.bazelrc.paths` mounts it and bazel refuses an absent mount
#   the whole history           `check_release_room` refuses a shallow clone, `check_paths`
#                               resolves the archive tags, `check_print_profile` reads
#                               `git:<sha>:<path>`, and `git log` reaches past fifty commits
#   .bazelrc.paths              `gen_build.py` writes this checkout's own paths
#
# NOT HERE: tools/render's puppeteer and its Chromium (the card deck and the posed renders),
# blender, rsvg-convert. `derive` has them from the image; a session that needs them installs
# them the way the Dockerfile does.

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1

PY=tools/cad-venv/bin/python
BAZELISK=https://github.com/bazelbuild/bazelisk/releases/download/v1.25.0/bazelisk-linux-amd64

say() { printf '  %s\n' "$*"; }
missing=0
need() { missing=1; say "missing: $*"; }

# --- web's node modules -----------------------------------------------------------------
if [ -d web/node_modules ]; then
  say "web/node_modules: present"
elif [ "$CHECK" = 1 ]; then
  need "web/node_modules"
else
  say "web/node_modules: installing"
  npm --prefix web install --no-audit --no-fund
fi

# --- the CAD venv at the tree's pin ---------------------------------------------------------
# `uv` when it is there (seconds), else the venv module and pip (minutes). Python 3.13 either
# way: `cad-requirements.txt` pins wheels that exist for cp313, and `publish.yml` asserts it.
if "$PY" -c "import cadquery" 2>/dev/null; then
  say "tools/cad-venv: cadquery $("$PY" -c 'import cadquery; print(cadquery.__version__)')"
elif [ "$CHECK" = 1 ]; then
  need "tools/cad-venv"
else
  say "tools/cad-venv: installing"
  PY313=$(command -v python3.13 || true)
  [ -n "$PY313" ] || { echo "python3.13 is not on PATH and the CAD pin needs it" >&2; exit 1; }
  UV=$(command -v uv || { [ -x "$HOME/.local/bin/uv" ] && echo "$HOME/.local/bin/uv"; } || true)
  if [ -n "$UV" ]; then
    "$UV" venv --quiet --python "$PY313" --seed tools/cad-venv
    "$UV" pip install --quiet --python "$PY" -r tools/cad-requirements.txt
  else
    "$PY313" -m venv tools/cad-venv
    "$PY" -m pip install --quiet --upgrade pip
    "$PY" -m pip install --quiet -r tools/cad-requirements.txt
  fi
fi
if [ "$CHECK" = 0 ]; then
  "$PY" tools/cad-venv-site/install.py >/dev/null
  "$PY" tools/cad-venv-site/install.py --check
fi

# --- the solids the pointer file names ---------------------------------------------------------------
# Node's own fetch does not read HTTPS_PROXY unless told to; the variable is harmless elsewhere.
if [ "$CHECK" = 1 ]; then
  NODE_USE_ENV_PROXY=1 node web/scripts/fetch-cad-artifacts.mjs --check >/dev/null 2>&1 \
    && say "pointed-at solids: in place" || need "pointed-at solids"
else
  NODE_USE_ENV_PROXY=1 node web/scripts/fetch-cad-artifacts.mjs
fi

# --- gh, which pack.py uploads with and check_release_room reads through -----------------------
# The token the session runs under is on the proxy, so a bare `gh` reaches the release.
if command -v gh >/dev/null; then
  say "gh: $(gh --version | head -1)"
elif [ "$CHECK" = 1 ]; then
  need "gh"
elif [ "$(id -u)" = 0 ] && command -v apt-get >/dev/null; then
  say "gh: installing"
  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    -o /usr/share/keyrings/githubcli-archive-keyring.gpg
  chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    > /etc/apt/sources.list.d/github-cli.list
  apt-get update -qq >/dev/null && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq gh >/dev/null
else
  say "gh: not installed (no root apt here); check_release_room takes no reading without it"
fi

# --- bazel at .bazelversion --------------------------------------------------------------------
if command -v bazel >/dev/null; then
  say "bazel: $(command -v bazel)"
elif [ "$CHECK" = 1 ]; then
  need "bazel"
else
  say "bazel: installing bazelisk"
  dest=/usr/local/bin/bazel
  [ -w /usr/local/bin ] || { mkdir -p "$HOME/.local/bin"; dest="$HOME/.local/bin/bazel"; }
  curl -fsSL -o "$dest" "$BAZELISK" && chmod +x "$dest"
  case ":$PATH:" in *":$(dirname "$dest"):"*) ;; *) export PATH="$(dirname "$dest"):$PATH" ;; esac
  [ -n "${CLAUDE_ENV_FILE:-}" ] && echo "export PATH=\"$(dirname "$dest"):\$PATH\"" >> "$CLAUDE_ENV_FILE"
fi
# `.bazelrc` names two mount pairs and `.bazelrc.paths` a third; bazel refuses an absent one.
if [ "$CHECK" = 0 ]; then
  mkdir -p .cache
  for d in /opt/homebrew/bin /usr/local/bin; do
    [ -d "$d" ] || mkdir -p "$d" 2>/dev/null || sudo mkdir -p "$d" 2>/dev/null || true
  done
fi

# --- the history the checks read -----------------------------------------------------------------
# The whole of it: 8078 commits and 2.3 GB of .git, fetched in 1m48s here. `check_release_room`
# reads reachability off history and refuses a shallow clone; `check_paths` holds every
# archive tag a doc names; `check_print_profile` reads a 3MF at the commit a print log
# cites; and `git log` answers past the clone's fifty commits, which is where this tree keeps
# its history. When the full fetch does not answer, the tags and the cited commits are fetched
# on their own, which is what those three checks need and `git log` does without.
if [ "$(git rev-parse --is-shallow-repository)" = "true" ]; then
  if [ "$CHECK" = 1 ]; then
    need "full history (shallow clone, $(git rev-list --count HEAD) commits)"
  elif git fetch --quiet --unshallow --tags origin; then
    say "history: whole, $(git rev-list --count HEAD) commits and $(git tag | wc -l | tr -d ' ') tags"
  else
    say "history: the full fetch did not answer — taking the tags and the cited commits"
    git fetch --quiet origin --tags --depth=1 || say "tags: the fetch did not answer"
    grep -rhoE "git:[0-9a-f]{40}" hardware tools web --include=*.md --include=*.py --include=*.js \
      2>/dev/null | sort -u | sed 's/^git://' | while read -r sha; do
        git cat-file -e "$sha^{commit}" 2>/dev/null || git fetch --quiet origin "$sha" \
          || say "commit $sha: the fetch did not answer"
      done
  fi
elif [ "$CHECK" = 1 ]; then
  say "history: whole, $(git rev-list --count HEAD) commits"
fi

# --- this checkout's own paths --------------------------------------------------------------------
if [ "$CHECK" = 1 ]; then
  [ -f .bazelrc.paths ] && say ".bazelrc.paths: written" || need ".bazelrc.paths"
else
  "$PY" tools/bazel/gen_build.py
fi

if [ "$CHECK" = 1 ]; then
  [ "$missing" = 0 ] && say "--check: this machine can run the tree" || exit 1
fi
