#!/usr/bin/env node
// sheet.mjs — lay the renders out as contact sheets.
//
//   node sheet.mjs                      # one sheet per screen, plus one per direction
//
// A per-screen sheet puts every direction's take on the same screen side by side, which is how
// a direction is chosen. A per-direction sheet puts one direction's five screens together,
// which is how it is checked for holding up across the whole interface.
import { chromium } from 'playwright';
import path from 'path';
import fs from 'fs';
import { pathToFileURL } from 'url';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const RENDERS = path.join(HERE, 'renders');
const SHEETS = path.join(HERE, 'sheets');
const TMP = path.join(HERE, '.sheet-tmp');
const SCREENS = ['choose', 'flavor', 'pick', 'lock', 'settings'];
const SCREEN_TITLE = {
  choose: 'Choose',
  flavor: "A flavor's own page",
  pick: 'Fill a flavor',
  lock: 'The operation lock',
  settings: 'Settings',
};

const meta = JSON.parse(fs.readFileSync(path.join(HERE, 'directions.json'), 'utf8'));
const keys = meta.directions.map((d) => d.key).filter((k) => fs.existsSync(path.join(RENDERS, `${k}-choose.png`)));
fs.mkdirSync(SHEETS, { recursive: true });
fs.mkdirSync(TMP, { recursive: true });

const name = (k) => meta.directions.find((d) => d.key === k)?.name ?? k;
const thesis = (k) => meta.directions.find((d) => d.key === k)?.thesis ?? '';

const head = (title) => `<!doctype html><meta charset=utf-8>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel=stylesheet>
<style>
  :root { color-scheme: dark; }
  html, body { margin: 0; background: #0b0b10; color: #e9e9f2;
    font-family: Inter, system-ui, sans-serif; -webkit-font-smoothing: antialiased; }
  .sheet { padding: 44px 44px 52px; }
  h1 { margin: 0 0 4px; font-size: 30px; font-weight: 800; letter-spacing: -0.02em; }
  .sub { margin: 0 0 34px; font-size: 15px; color: #8b8ba3; }
  .grid { display: grid; grid-template-columns: repeat(var(--cols), 800px); gap: 40px 36px; }
  figure { margin: 0; }
  figcaption { padding: 12px 2px 0; }
  .k { font-size: 19px; font-weight: 700; letter-spacing: -0.01em; }
  .t { font-size: 14px; color: #8b8ba3; line-height: 1.45; margin-top: 3px;
       display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  img { display: block; width: 800px; height: 480px; border-radius: 10px;
        box-shadow: 0 0 0 1px #24243a, 0 18px 44px rgba(0,0,0,.55); }
</style>
<title>${title}</title>`;

const pages = [];

for (const s of SCREENS) {
  const shown = keys.filter((k) => fs.existsSync(path.join(RENDERS, `${k}-${s}.png`)));
  if (!shown.length) continue;
  const cols = Math.min(3, shown.length);
  const html = `${head(SCREEN_TITLE[s])}
<div class=sheet>
  <h1>${SCREEN_TITLE[s]}</h1>
  <p class=sub>Every direction's take on one screen. 800 &times; 480, the panel's own grid.</p>
  <div class=grid style="--cols:${cols}">
    ${shown.map((k) => `<figure><img src="${path.join(RENDERS, `${k}-${s}.png`)}">
      <figcaption><div class=k>${name(k)}</div><div class=t>${thesis(k)}</div></figcaption></figure>`).join('\n')}
  </div>
</div>`;
  const f = path.join(TMP, `screen-${s}.html`);
  fs.writeFileSync(f, html);
  pages.push({ f, out: path.join(SHEETS, `screen-${s}.png`), cols, rows: Math.ceil(shown.length / cols) });
}

for (const k of keys) {
  const shown = SCREENS.filter((s) => fs.existsSync(path.join(RENDERS, `${k}-${s}.png`)));
  const cols = Math.min(2, shown.length);
  const html = `${head(name(k))}
<div class=sheet>
  <h1>${name(k)}</h1>
  <p class=sub>${thesis(k)}</p>
  <div class=grid style="--cols:${cols}">
    ${shown.map((s) => `<figure><img src="${path.join(RENDERS, `${k}-${s}.png`)}">
      <figcaption><div class=k>${SCREEN_TITLE[s]}</div></figcaption></figure>`).join('\n')}
  </div>
</div>`;
  const f = path.join(TMP, `dir-${k}.html`);
  fs.writeFileSync(f, html);
  pages.push({ f, out: path.join(SHEETS, `direction-${k}.png`), cols, rows: Math.ceil(shown.length / cols) });
}

const exe = process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium';
const browser = await chromium.launch({
  executablePath: fs.existsSync(exe) ? exe : undefined,
  args: ['--no-sandbox', '--font-render-hinting=none'],
});
for (const p of pages) {
  const width = 88 + p.cols * 800 + (p.cols - 1) * 36;
  const ctx = await browser.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  await page.goto(pathToFileURL(p.f).href, { waitUntil: 'networkidle', timeout: 90000 });
  try { await page.evaluate(() => document.fonts.ready); } catch {}
  await page.screenshot({ path: p.out, fullPage: true });
  await ctx.close();
  console.log(`wrote ${p.out}`);
}
await browser.close();
fs.rmSync(TMP, { recursive: true, force: true });
