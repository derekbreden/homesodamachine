#!/bin/bash
# cloud_session.sh prepares native build and publication tools in a cloud checkout.

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1

BAZELISK=https://github.com/bazelbuild/bazelisk/releases/download/v1.25.0/bazelisk-linux-amd64

say() { printf '  %s\n' "$*"; }
missing=0
need() { missing=1; say "missing: $*"; }

node_major() { node --version 2>/dev/null | sed 's/^v//; s/\..*//'; }
if [ "$(node_major)" -ge 22 ] 2>/dev/null; then
  say "node: $(node --version)"
elif [ "$CHECK" = 1 ]; then
  need "node 22 ($(node --version 2>/dev/null || echo none) on PATH)"
elif [ -x /opt/node22/bin/node ] && [ -w /usr/local/bin ]; then
  for tool in node npm npx; do
    if [ -x "/opt/node22/bin/$tool" ] && { [ -L "/usr/local/bin/$tool" ] || [ ! -e "/usr/local/bin/$tool" ]; }; then
      ln -sfn "/opt/node22/bin/$tool" "/usr/local/bin/$tool"
    fi
  done
  hash -r
  say "node: $(node --version), linked from /opt/node22"
elif [ "$(id -u)" = 0 ] && command -v apt-get >/dev/null; then
  say "node: installing 22 ($(node --version 2>/dev/null || echo none) here)"
  curl -fsSL https://deb.nodesource.com/setup_22.x | bash - >/dev/null 2>&1
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq nodejs >/dev/null
  hash -r
  say "node: $(node --version)"
else
  say "node: $(node --version 2>/dev/null || echo none), and no way to put 22 on PATH here"
fi

if [ -d web/node_modules ]; then
  say "web/node_modules: present"
elif [ "$CHECK" = 1 ]; then
  need "web/node_modules"
else
  say "web/node_modules: installing"
  npm --prefix web install --no-audit --no-fund
fi

if [ "$CHECK" = 1 ]; then
  NODE_USE_ENV_PROXY=1 node web/scripts/fetch-cad-artifacts.mjs --for-build --check >/dev/null 2>&1 \
    && say "pointed-at solids: in place" || need "pointed-at solids"
else
  NODE_USE_ENV_PROXY=1 node web/scripts/fetch-cad-artifacts.mjs --for-build
fi

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
  say "gh: not installed (no root apt here); hsm-pack cannot upload without it"
fi

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
if [ "$CHECK" = 0 ]; then
  mkdir -p .cache
  for d in /opt/homebrew/bin /usr/local/bin; do
    [ -d "$d" ] || mkdir -p "$d" 2>/dev/null || sudo mkdir -p "$d" 2>/dev/null || true
  done
fi

if [ "$CHECK" = 1 ]; then
  for tool in hsm-run hsm hsm-build-plan hsm-print-build hsm-publish hsm-pack hsm-land hsm-merge-pointers; do
    [ -x "tools/hsm/target/release/$tool" ] && say "$tool: built" || need "$tool"
  done
else
  command -v cargo >/dev/null || { echo "Install the Rust toolchain before running this setup" >&2; exit 1; }
  command -v cmake >/dev/null || { echo "Install CMake before running this setup" >&2; exit 1; }
  if [ ! -x tools/hsm/target/release/hsm-run ]; then
    cargo build --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-run-slots --bin hsm-run
  fi
  tools/run -- cargo build --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml \
    -p hsm -p hsm-build-plan -p hsm-print-build \
    -p hsm-publication -p hsm-git-tools -p hsm-cargo-config
  tools/hsm/target/release/hsm-run --install-hsm "$ROOT" tools/hsm/target/release/hsm
  tools/hsm/target/release/hsm-run --install-tools "$ROOT" \
    tools/hsm/target/release/hsm-build-plan tools/hsm/target/release/hsm-print-build \
    tools/hsm/target/release/hsm-cargo-config tools/hsm/target/release/hsm-publish \
    tools/hsm/target/release/hsm-pack tools/hsm/target/release/hsm-land \
    tools/hsm/target/release/hsm-merge-pointers tools/hsm/target/release/hsm-build-times \
    tools/hsm/target/release/hsm-cut-vs-pointers
  export PATH="$HOME/.local/bin:$PATH"
fi

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

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)
if [ "$branch" = "main" ]; then
  say "branch: main"
elif [ "$CHECK" = 1 ]; then
  need "the checkout on main (on $branch)"
else
  git checkout -q -B main
  git branch -q --set-upstream-to=origin/main main 2>/dev/null || true
  say "branch: main (was $branch)"
fi

if [ "$(git config --get core.hooksPath || true)" = ".githooks" ]; then
  say "hooks: .githooks"
elif [ "$CHECK" = 1 ]; then
  need "hooks (core.hooksPath)"
else
  git config core.hooksPath .githooks
  say "hooks: .githooks"
fi
if [[ "$(git config --get merge.cadpointers.driver || true)" == *hsm-merge-pointers* ]]; then
  say "merge driver: cadpointers"
elif [ "$CHECK" = 1 ]; then
  need "merge driver (merge.cadpointers.driver)"
else
  printf -v driver '%q %%O %%A %%B' "$ROOT/tools/hsm/target/release/hsm-merge-pointers"
  git config merge.cadpointers.driver "$driver"
  git config merge.cadpointers.name "the CAD pointer file, merged by member"
  say "merge driver: cadpointers"
fi

if [ "$CHECK" = 1 ]; then
  [ -f .bazelrc.paths ] && say ".bazelrc.paths: written" || need ".bazelrc.paths"
else
  tools/hsm/target/release/hsm-build-plan write
fi

if [ "$CHECK" = 1 ]; then
  [ "$missing" = 0 ] && say "--check: this machine can run the tree" || exit 1
fi
