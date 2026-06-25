/**
 * Per-board single-flight lock for the board render: the newest run wins.
 *
 * On start a run SIGTERMs any older live run holding the same board's lock and
 * takes it over; a run that receives the signal kills its in-flight child and
 * exits (143), naming the run that superseded it. The lock is a pid file in the
 * OS temp dir keyed by board name; a stale file whose pid is dead is ignored.
 *
 * RENDER_SOURCE labels a run in the messages — "dev-server", "build-all", else
 * "manual".
 */
import { readFileSync, writeFileSync, rmSync, mkdirSync } from "node:fs"
import { tmpdir } from "node:os"
import path from "node:path"

type Holder = { pid: number; source: string; started: number }

const alive = (pid: number) => {
  try { process.kill(pid, 0); return true } catch { return false }
}
const read = (f: string): Holder | null => {
  try { return JSON.parse(readFileSync(f, "utf8")) } catch { return null }
}
// Portable synchronous sleep — wait on an Int32Array that never changes, so it
// always times out after `ms`. Lets us pause for a superseded run to die without
// a busy-spin or a bun-only API.
const sleepSync = (ms: number) => {
  try { Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms) } catch {}
}

export function singleflight(key: string, source: string) {
  const lockDir = path.join(tmpdir(), "hsm-render-lock")
  mkdirSync(lockDir, { recursive: true })
  const lockFile = path.join(lockDir, `${key}.json`)
  const byFile = path.join(lockDir, `${key}.by.json`) // who superseded the victim
  const me: Holder = { pid: process.pid, source, started: Date.now() }

  // Supersede an older live holder of this board's lock.
  const prev = read(lockFile)
  if (prev && prev.pid !== me.pid && alive(prev.pid)) {
    console.error(`[render:${key}] superseding the active run (pid ${prev.pid}, ${prev.source}) — sending SIGTERM`)
    writeFileSync(byFile, JSON.stringify(me))
    try { process.kill(prev.pid, "SIGTERM") } catch {}
    const until = Date.now() + 2000
    while (alive(prev.pid) && Date.now() < until) sleepSync(25)
  } else {
    try { rmSync(byFile, { force: true }) } catch {}
  }
  writeFileSync(lockFile, JSON.stringify(me))

  let killChild = () => {}
  let released = false
  const release = () => {
    if (released) return
    released = true
    const cur = read(lockFile)
    if (cur && cur.pid === me.pid) {
      try { rmSync(lockFile, { force: true }) } catch {}
      try { rmSync(byFile, { force: true }) } catch {}
    }
  }

  // We were SIGTERM'd (or Ctrl-C'd) — almost always by a newer run taking over.
  // Kill our in-flight build and exit now; the `exit` event still runs the
  // render's temp-file cleanup. exit(143) = terminated-by-SIGTERM convention.
  const onSignal = () => {
    const by = read(byFile)
    console.error(`[render:${key}] this run (${source}) was superseded by ${by ? by.source : "a newer run"} — stopping`)
    try { killChild() } catch {}
    process.exit(143)
  }
  process.on("SIGTERM", onSignal)
  process.on("SIGINT", onSignal)
  process.on("exit", release)

  return {
    /** Register how to kill the current child process when superseded. */
    setChildKiller(f: () => void) { killChild = f },
    /** Release the lock on normal completion. */
    release,
  }
}
