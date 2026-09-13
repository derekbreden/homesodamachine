import fs from 'node:fs';
import { pathToFileURL } from 'node:url';
import { launchBrowser, closeBrowser } from '../render/browser.js';

const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
let browser;
try {
  browser = await launchBrowser({ protocolTimeout: 120000 });
  const page = await browser.newPage();
  page.on('pageerror', error => { throw error; });
  for (const job of jobs) {
    await page.setViewport({ width: job.size[0], height: job.size[1], deviceScaleFactor: 1 });
    await page.goto(pathToFileURL(job.html).href, { waitUntil: 'load' });
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    await page.screenshot({ path: job.out, omitBackground: true });
  }
  console.log(`Rendered ${jobs.length} illustrations with page-space contours.`);
} finally {
  await closeBrowser(browser);
}
