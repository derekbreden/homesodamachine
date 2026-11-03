import { ensureRunLease } from "../render/browser.js";
ensureRunLease();
import fs from 'node:fs';
import { pathToFileURL } from 'node:url';
import { launchBrowser, closeBrowser } from '../render/browser.js';

const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
let browser;
try {
  browser = await launchBrowser({ protocolTimeout: 120000 });
  for (const job of jobs) {
    console.log(`Rendering illustration ${job.html} (${job.size[0]} x ${job.size[1]}).`);
    // Each image gets a clean SVG filter surface at its own viewport size.
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error));
    try {
      await page.setViewport({ width: job.size[0], height: job.size[1], deviceScaleFactor: 1 });
      await page.goto(pathToFileURL(job.html).href, { waitUntil: 'load' });
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      if (errors.length) throw errors[0];
      // The SVG occupies this viewport; no offscreen page surface is needed.
      await page.screenshot({ path: job.out, omitBackground: true,
        captureBeyondViewport: false });
    } finally {
      await page.close();
    }
  }
  console.log(`Rendered ${jobs.length} illustrations with page-space contours.`);
} finally {
  await closeBrowser(browser);
}
