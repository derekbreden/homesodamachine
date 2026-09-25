#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { start } from "../../../web/server.js";
import { launchBrowser, closeBrowser, closeServer, frameBuffer, finish } from "../../../tools/render/browser.js";

const root = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(root, "out");
const timeline = JSON.parse(fs.readFileSync(path.join(out, "timeline.json"), "utf8"));
const stills = process.argv.includes("--stills");
let server, browser, encoder;
try {
  const running = await start({ port: 0 });
  server = running.server;
  running.app.get("/video/composition.js", (_req, res) => res.sendFile(path.join(root, "composition.js")));
  if (!server.listening) await once(server, "listening");
  browser = await launchBrowser({ protocolTimeout: 180000 });
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await page.goto(`http://localhost:${server.address().port}/tour?paused=1&renderAlpha=1`,
    { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForFunction(() => window.__tour?.state.phase === "dwell", { timeout: 180000 });
  await page.evaluate(async (timeline) => {
    const { prepare } = await import("/video/composition.js");
    window.__movie = await prepare(timeline);
  }, timeline);
  if (errors.length) throw new Error(errors.join("\n"));
  console.log(`Machine loaded; rendering ${stills ? "review frames" : `${timeline.frames} frames`}.`);
  if (stills) {
    for (const second of [3, 10, 15.5, 19, 22, 25.5, 30, 35, 39]) {
      const frame = await page.evaluate((time) => window.__movie.draw(time), second);
      fs.writeFileSync(path.join(out, `review-${second}.jpg`), frameBuffer(frame));
    }
  } else {
    encoder = spawn("ffmpeg", ["-hide_banner", "-loglevel", "warning", "-y",
      "-f", "image2pipe", "-framerate", String(timeline.fps), "-vcodec", "mjpeg", "-i", "pipe:0",
      "-i", path.join(out, "voice-master.wav"), "-map", "0:v", "-map", "1:a",
      "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
      "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", String(timeline.duration),
      path.join(out, "opening.mp4")], { stdio: ["pipe", "ignore", "inherit"] });
    const completed = new Promise((resolve, reject) => {
      encoder.once("error", reject);
      encoder.once("close", (code) => code === 0 ? resolve() : reject(new Error(`ffmpeg exited ${code}`)));
    });
    encoder.stdin.on("error", (error) => console.error(error.message));
    for (let frame = 0; frame < timeline.frames; frame++) {
      const data = await page.evaluate((time) => window.__movie.draw(time), frame / timeline.fps);
      if (frame === timeline.fps * 3) fs.writeFileSync(path.join(out, "poster.jpg"), frameBuffer(data));
      if (!encoder.stdin.write(frameBuffer(data))) await once(encoder.stdin, "drain");
      if (frame % 150 === 0) console.log(`${frame}/${timeline.frames} frames`);
      if (errors.length) throw new Error(errors.join("\n"));
    }
    encoder.stdin.end();
    await completed;
    fs.copyFileSync(path.join(root, "preview.html"), path.join(out, "index.html"));
    console.log(path.join(out, "opening.mp4"));
  }
} catch (error) {
  console.error(error.message);
  encoder?.kill();
  process.exitCode = 1;
} finally {
  await closeBrowser(browser);
  await closeServer(server);
  finish(process.exitCode || 0);
}
