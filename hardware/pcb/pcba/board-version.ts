/**
 * board-version — the board's silk version string, mirroring the firmware's
 * scheme in `firmware/pre_build.py` so the carrier reads the same way the
 * displays and the iOS app do.
 *
 * Format: `YYYY.MM.DD <short-sha>[+]` — the date and short SHA of the last commit
 * to touch the board's DESIGN SOURCE (this directory, excluding the regenerated
 * out/ and *.circuit.json), with a trailing `+` when that source has uncommitted
 * edits on top. Off-repo, the build date + "unknown".
 *
 * The source's own commit, not HEAD. HEAD moves on every commit in the repo, and
 * this string is copper: stamping it would re-cut the silk — and with it every
 * gerber, plot and 3D view under out/ — because a marketing doc landed. Two runs
 * over an unchanged design would then disagree, which is the one thing
 * `build:check` exists to report, so it would report it forever and mean nothing.
 * Reading the design's own last commit makes the stamp change exactly when the
 * board does.
 *
 * Computed at render time (pcba.tsx calls boardVersionParts() for its identity silk),
 * the board analogue of pre_build.py generating fw_version.h before a firmware
 * build.
 */
import { execSync } from "node:child_process"

const pad = (n: number) => String(n).padStart(2, "0")
const buildDate = () => {
  const d = new Date()
  return `${d.getFullYear()}.${pad(d.getMonth() + 1)}.${pad(d.getDate())}`
}

// The design source: this directory, less what a render writes back into it.
// Spelled once, as a git pathspec for the log below and as a regex for the
// working-tree check, because they must agree on what "source" means.
const SOURCE_PATHSPEC = '. ":(exclude)out" ":(exclude)*.circuit.json"'
const REGENERATED = /(^|\/)out\/|\.circuit\.json$/

export function boardVersion(): string {
  const run = (args: string) =>
    execSync(`git ${args}`, { cwd: import.meta.dir, stdio: ["ignore", "pipe", "ignore"] })
      .toString()
      .trim()
  try {
    // One log call for both halves, so the date and the SHA are the same commit's.
    const stamp = run(
      `log -1 --format=%cd:%h --date=format:%Y.%m.%d -- ${SOURCE_PATHSPEC}`,
    )
    // No commit has touched the design yet (a fresh board, or a shallow clone
    // whose history does not reach one) — fall back to HEAD, then to the clock.
    const [date, rev] = stamp.includes(":")
      ? stamp.split(":")
      : [buildDate(), run("rev-parse --short HEAD")]
    if (!rev) return `${buildDate()} unknown`
    const sourceDirty = run("status --porcelain .")
      .split("\n")
      .map((l) => l.slice(3))
      .some((p) => p && !REGENERATED.test(p))
    return `${date} ${rev}${sourceDirty ? "+" : ""}`
  } catch {
    return `${buildDate()} unknown`
  }
}

/**
 * The version split into its two lines for the board's identity stamp: the
 * commit date and the (upper-cased) short SHA + its trailing `+`. The board nameplate
 * stacks them under "HOME SODA MACHINE"; upper-case to match the rest of the
 * board's silk and read clean at a glance.
 */
export function boardVersionParts(): { date: string; rev: string } {
  const v = boardVersion()
  const sp = v.indexOf(" ")
  return sp < 0
    ? { date: v.toUpperCase(), rev: "" }
    : { date: v.slice(0, sp), rev: v.slice(sp + 1).toUpperCase() }
}
