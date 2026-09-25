#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { once } from "node:events";
import { start } from "../../../web/server.js";
import { launchBrowser, closeBrowser, closeServer, frameBuffer, finish } from "../../../tools/render/browser.js";

const root = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(new URL("../../../web/package.json", import.meta.url));
const express = require("express");
const palette = JSON.parse(fs.readFileSync(path.join(root, "../../../brand/palette.json"), "utf8"));
let server, browser;
try {
  const running = await start({ port: 0 });
  server = running.server;
  running.app.use("/errand", express.static(root));
  if (!server.listening) await once(server, "listening");
  browser = await launchBrowser({ protocolTimeout: 180000 });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  // stage.html carries the import map and Montserrat.
  await page.goto(`http://localhost:${server.address().port}/errand/stage.html`,
    { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForFunction(() => window.__film, { timeout: 180000 });
  const image = await page.evaluate(async (palette) => {
    const THREE = await import("three");
    const { createProductScenes } = await import("/errand/product-scenes.js");
    const product = await createProductScenes({ THREE, width: 3840, height: 2160, palette });
    const logo = new Image();
    logo.src = "/brand/wordmark-reverse.svg";
    await logo.decode();
    await document.fonts.load("600 150px Montserrat");
    await document.fonts.load("500 26px Montserrat");
    const canvas = document.createElement("canvas");
    canvas.width = 3840;
    canvas.height = 2160;
    const ctx = canvas.getContext("2d", { alpha: false });
    ctx.scale(2, 2);
    ctx.fillStyle = palette.cobalt;
    ctx.fillRect(0, 0, 1920, 1080);
    // Mid-pour: the stream still running, the glass most of the way full.
    ctx.drawImage(product.draw(6.5, "pour", { cobalt: true }), 60, 0, 1920, 1080);
    ctx.drawImage(logo, 87, 65, 320, 320 * 80.5 / 270);
    ctx.fillStyle = palette.ice;
    ctx.font = "500 26px Montserrat, sans-serif";
    ctx.fillText("COLD SODA, ON TAP", 104, 350);
    ctx.fillStyle = palette.white;
    ctx.font = "600 150px Montserrat, sans-serif";
    ctx.fillText("ONE LESS", 94, 520);
    ctx.fillText("ERRAND", 94, 688);
    ctx.fillStyle = palette.orange;
    ctx.beginPath(); ctx.roundRect(104, 755, 100, 9, 4.5); ctx.fill();
    product.dispose();
    return canvas.toDataURL("image/jpeg", 0.95);
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
