#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { once } from "node:events";
import { start } from "../../../web/server.js";
import { launchBrowser, closeBrowser, closeServer, frameBuffer, finish } from "../../../tools/render/browser.js";

const root = path.dirname(fileURLToPath(import.meta.url));
const palette = JSON.parse(fs.readFileSync(path.join(root, "../../../brand/palette.json"), "utf8"));
let server, browser;
try {
  const running = await start({ port: 0 });
  server = running.server;
  for (const file of ["composition.js", "film-scenes.js"]) {
    running.app.get(`/video/${file}`, (_req, res) => res.sendFile(path.join(root, file)));
  }
  if (!server.listening) await once(server, "listening");
  browser = await launchBrowser({ protocolTimeout: 180000 });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await page.goto(`http://localhost:${server.address().port}/tour?paused=1&renderAlpha=1`,
    { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForFunction(() => window.__tour?.state.phase === "dwell", { timeout: 180000 });
  const image = await page.evaluate(async (palette) => {
    const { prepare } = await import("/video/composition.js");
    const movie = await prepare({ width: 1920, height: 1080, captions: [], duration: 42 }, palette);
    const logo = new Image();
    logo.src = "/brand/wordmark-reverse.svg";
    await logo.decode();
    await document.fonts.load("600 164px Montserrat");
    const canvas = document.createElement("canvas");
    canvas.width = 3840;
    canvas.height = 2160;
    const ctx = canvas.getContext("2d", { alpha: false });
    ctx.scale(2, 2);
    ctx.fillStyle = palette.cobalt;
    ctx.fillRect(0, 0, 1920, 1080);
    const glow = ctx.createRadialGradient(1330, 450, 100, 1330, 450, 900);
    glow.addColorStop(0, `${palette.ice}18`);
    glow.addColorStop(1, `${palette.ice}00`);
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, 1920, 1080);
    movie.draw(19);
    const { renderer, scene, camera } = window.__tour;
    renderer.setPixelRatio(3);
    renderer.render(scene, camera);
    ctx.drawImage(renderer.domElement, 540, -55, 1760, 1760 * 840 / 1360);
    ctx.drawImage(logo, 87, 65, 320, 320 * 80.5 / 270);
    ctx.fillStyle = palette.ice;
    ctx.font = "500 26px Montserrat, sans-serif";
    ctx.fillText("INSIDE THE MACHINE", 104, 350);
    ctx.fillStyle = palette.white;
    ctx.font = "600 164px Montserrat, sans-serif";
    ctx.fillText("SODA", 94, 526);
    ctx.font = "600 150px Montserrat, sans-serif";
    ctx.fillText("ON TAP", 94, 698);
    ctx.fillStyle = palette.orange;
    ctx.beginPath(); ctx.roundRect(104, 765, 100, 9, 4.5); ctx.fill();
    return canvas.toDataURL("image/jpeg", 0.97);
  }, palette);
  const filename = path.join(root, "thumbnail.jpg");
  fs.writeFileSync(filename, frameBuffer(image));
  console.log(filename);
} catch (error) {
  console.error(error);
  process.exitCode = 1;
} finally {
  await closeBrowser(browser);
  await closeServer(server);
  finish(process.exitCode || 0);
}
