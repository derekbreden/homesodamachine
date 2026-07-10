/**
 * board-version — the board's silk version string, mirroring the firmware's
 * scheme in `firmware/pre_build.py` so the carrier reads the same way the
 * displays and the iOS app do.
 *
 * Format: `YYYY.MM.DD <short-sha>[+]` — HEAD's commit date and short SHA, with
 * a trailing `+` when the board's design source (this directory, excluding the
 * regenerated out/ and *.circuit.json) has uncommitted edits. The date is the
 * commit's own date; `+` is that commit plus uncommitted source edits. Off-repo,
 * the build date + "unknown".
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

export function boardVersion(): string {
  const run = (args: string) =>
    execSync(`git ${args}`, { cwd: import.meta.dir, stdio: ["ignore", "pipe", "ignore"] })
      .toString()
      .trim()
  try {
    const rev = run("rev-parse --short HEAD")
    if (!rev) return `${buildDate()} unknown`
    let date: string
    try {
      date = run("show -s --format=%cd --date=format:%Y.%m.%d HEAD")
    } catch {
      date = buildDate()
    }
    const regenerated = /(^|\/)out\/|\.circuit\.json$/ // out/ renders + circuit-json caches
    const sourceDirty = run("status --porcelain .")
      .split("\n")
      .map((l) => l.slice(3))
      .some((p) => p && !regenerated.test(p))
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
