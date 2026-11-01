/** One board render at a time. A new render waits; signals cancel only this run. */
import { spawn } from "node:child_process"
import { existsSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { ensureRunLease } from "../../../tools/run-slots.mjs"

export async function singleflight(key: string, source: string) {
  ensureRunLease()
  const here = path.dirname(fileURLToPath(import.meta.url))
  const root = path.resolve(here, "../../..")
  const localPython = path.join(process.env.HSM_WORKSPACE || root, "tools/cad-venv/bin/python")
  const python = existsSync(localPython) ? localPython : "python3"
  const holder = spawn(python, [path.join(here, "run-lock.py"), key], {
    stdio: ["pipe", "pipe", "inherit"],
  })
  await new Promise<void>((resolve, reject) => {
    holder.once("error", reject)
    holder.once("exit", (code) => reject(new Error(`board mutex exited ${code}`)))
    holder.stdout.once("data", () => resolve())
  })
  let killChild = () => {}
  let released = false
  const release = () => {
    if (released) return
    released = true
    holder.stdin.end()
  }
  const onSignal = (signal: NodeJS.Signals) => {
    console.error(`[render:${key}] ${source} received ${signal} — stopping this run`)
    try { killChild() } catch {}
    release()
    process.exit(signal === "SIGINT" ? 130 : 143)
  }
  process.on("SIGTERM", () => onSignal("SIGTERM"))
  process.on("SIGINT", () => onSignal("SIGINT"))
  process.on("exit", release)
  return { setChildKiller(f: () => void) { killChild = f }, release }
}
