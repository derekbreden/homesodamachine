#!/usr/bin/env node
// node tools/shot-page.mjs <file-or-url> <out.png> [--size=1440x900] [--click=selector] [--full]
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";
const a = process.argv.slice(2);
const pos = a.filter(x => !x.startsWith("--")); const opt = Object.fromEntries(a.filter(x => x.startsWith("--")).map(x => { const i = x.indexOf("="); return i < 0 ? [x.slice(2), ""] : [x.slice(2, i), x.slice(i + 1)]; }));
const [w, h] = (opt.size ?? "1440x900").split("x").map(Number);
const url = /^https?:|^file:/.test(pos[0]) ? pos[0] : pathToFileURL(path.resolve(pos[0])).href;
const require = createRequire("/Users/derekbredensteiner/Developer/homesodamachine/tools/render/");
const puppeteer = require("puppeteer");
const browser = await puppeteer.launch({ headless: true, pipe: true, args: ["--no-sandbox", "--allow-file-access-from-files", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
try {
  const page = await browser.newPage(); await page.setViewport({ width: w, height: h });
  const errs = []; page.on("pageerror", e => errs.push(String(e))); page.on("console", m => { if (m.type() === "error") errs.push(m.text()); });
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 120000 }); await new Promise(r => setTimeout(r, 1200));
  if (opt.click) { await page.click(opt.click); await new Promise(r => setTimeout(r, 1500)); }
  await page.screenshot({ path: pos[1], fullPage: opt.full !== undefined });
  console.log(pos[1], errs.length ? "ERRORS:\n" + errs.join("\n") : "no errors");
} finally { await browser.close(); }
