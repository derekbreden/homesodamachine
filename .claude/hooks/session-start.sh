#!/bin/bash
# The SessionStart hook: a cloud session stands the tree up before its first turn.
#
# Registered in .claude/settings.json. On Derek's Mac (no CLAUDE_CODE_REMOTE) it exits at once;
# on Anthropic's machines it asks tools/cloud_session.sh --check, which takes seconds on a
# container that already holds the toolchain, and runs the install only when something is
# missing, which takes minutes on a fresh one. Synchronous, so the first turn finds the
# toolchain in place.
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
tools/cloud_session.sh --check || tools/cloud_session.sh
[ -n "${CLAUDE_ENV_FILE:-}" ] && echo 'export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"' >> "$CLAUDE_ENV_FILE"
exit 0
