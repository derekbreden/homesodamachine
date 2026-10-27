// Manually package native captures for review. Uses the repository's existing
// Sharp dependency. No HTML approximation of the app is drawn here.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const sharp = require('../../tools/render/node_modules/sharp');
const here = import.meta.dirname;
const inlineAt = process.argv.indexOf('--inline-dir');
const inlineDirectory = inlineAt >= 0 ? path.resolve(process.argv[inlineAt + 1]) : null;
const manifest = JSON.parse(await fs.readFile(path.join(here, 'renders/manifest.json'), 'utf8'));
const preview = path.join(here, 'preview');
await fs.mkdir(preview, {recursive: true});

const labels = {
  home: 'Machine', flavor: 'Flavor image and ratio', images: 'Image library', crop: 'Crop a photo',
  uploading: 'Image upload', care: 'Care', fill: 'Prepare to fill', filling: 'Filling',
  clean: 'Prepare to clean', cleaning: 'Cleaning · round 2', cleanFunnel: 'Cleaning · funnel path',
  prime: 'Prepare to prime', priming: 'Prime · on the machine', settings: 'Settings', sound: 'Sound and quiet hours',
  update: 'Update available', updating: 'Update · sending', current: 'Software current', machines: 'Your machines',
  rename: 'Machine name', add: 'First run', offline: 'Out of range', bluetooth: 'Bluetooth off',
  unread: 'No readings yet', alarm: 'Gas alarm', busy: 'Machine busy', stopped: 'Cleaning stopped',
  complete: 'Cleaning complete', lost: 'Connection lost during cleaning', clock: 'Clock unavailable',
  imageError: 'Image transfer failed', fillStopped: 'Filling stopped', fillFull: 'Reservoir full',
  stopping: 'Stop awaiting confirmation', updateError: 'Update check failed', restarting: 'Update · restarting',
  verifying: 'Update · verifying'
};
const focusedGroups = [
  {id: 'soda-polished-phone', title: 'Refined appliance app', routes: ['home', 'flavor', 'care', 'settings', 'sound'], sizes: ['phone'], initialRoute: 'home', initialViewport: 'phone'},
  {id: 'soda-polished-layouts', title: 'Refined adaptive layouts', routes: ['home'], sizes: ['cover', 'duo', 'ipad-portrait', 'ipad', 'landscape'], initialRoute: 'home', initialViewport: 'duo'}
];
const images = [];
for (const item of manifest) {
  const source = path.join(here, 'renders', item.file);
  const file = item.file.replace(/\.png$/, '.webp');
  await sharp(source).resize({width: item.width}).webp({quality: 90, effort: 5}).toFile(path.join(preview, file));
  images.push({...item, file, label: labels[item.route]});
}
const detailDirectory = path.join(preview, 'detail');
await fs.mkdir(detailDirectory, {recursive: true});
const detailImages = new Map();
for (const item of images) {
  if (!focusedGroups.some(group => group.routes.includes(item.route) && group.sizes.includes(item.viewport))) continue;
  // Keep every captured pixel. These review copies supply two image pixels per
  // displayed SwiftUI point and preserve text edges without lossy compression.
  const buffer = await sharp(path.join(here, 'renders', item.file.replace(/\.webp$/, '.png')))
    .webp({lossless: true, effort: 6}).toBuffer();
  const detailFile = `detail/${item.file}`;
  await fs.writeFile(path.join(preview, detailFile), buffer);
  item.detailFile = detailFile;
  detailImages.set(item.file, buffer);
}
await fs.writeFile(path.join(preview, 'manifest.json'), JSON.stringify(images, null, 2) + '\n');

const viewports = [...new Set(images.map(item => item.viewport))];
const routes = [...new Set(images.map(item => item.route))];
let index = '# Native app renders\n\nEach image is a native SwiftUI content render with sample data. Dimensions are layout canvases in points; system chrome and device safe-area masks are omitted. Source captures are 2× PNGs in the local `renders/` directory. Focused detail copies retain that 2× resolution with lossless WebP encoding; the complete matrix uses compact 1× WebP copies.\n\n';
index += '## Detail review · 2× lossless\n\n| Screen | Window | Native detail |\n| --- | --- | --- |\n';
for (const item of images.filter(item => item.detailFile)) index += `| ${item.label} | ${item.title} · ${item.width} × ${item.height} pt | [View 2× lossless](${item.detailFile}) |\n`;
index += '\n## Complete screen matrix · 1×\n\n';
index += '| Screen | ' + viewports.join(' | ') + ' |\n| --- | ' + viewports.map(() => '---').join(' | ') + ' |\n';
for (const route of routes) index += `| ${labels[route]} | ` + viewports.map(v => `[View](${v}-${route}.webp)`).join(' | ') + ' |\n';
await fs.writeFile(path.join(preview, 'README.md'), index);

// A compact visual index for opening the proposal from the repository.
const boardRoutes = ['home', 'flavor', 'images', 'care', 'clean', 'sound', 'update', 'machines'];
const cellWidth = 268, gap = 22, captionHeight = 38;
const cellHeight = Math.round(874 * cellWidth / 402);
const boardWidth = gap + 4 * (cellWidth + gap);
const boardHeight = gap + 2 * (cellHeight + captionHeight + gap);
const layers = [];
for (const [i, route] of boardRoutes.entries()) {
  const x = gap + (i % 4) * (cellWidth + gap);
  const y = gap + Math.floor(i / 4) * (cellHeight + captionHeight + gap);
  const input = await sharp(path.join(here, 'renders', `phone-${route}.png`)).resize({width: cellWidth}).png().toBuffer();
  layers.push({input, left: x, top: y + captionHeight});
  const text = labels[route].replaceAll('&', '&amp;');
  layers.push({input: Buffer.from(`<svg width="${cellWidth}" height="${captionHeight}"><text x="0" y="24" font-family="Arial" font-size="16" fill="#DCE6FF">${text}</text></svg>`), left: x, top: y});
}
await sharp({create: {width: boardWidth, height: boardHeight, channels: 3, background: '#10319C'}})
  .composite(layers).png().toFile(path.join(preview, 'overview.png'));

if (inlineDirectory) {
  await fs.mkdir(inlineDirectory, {recursive: true});
  const template = await fs.readFile(path.join(here, 'review-template.html'), 'utf8');
  const helper = await fs.readFile(path.join(here, '../../tools/viz/inline-mobile/assets/theme.js'), 'utf8');
  for (const group of focusedGroups) {
    const selected = images.filter(item => group.routes.includes(item.route) && group.sizes.includes(item.viewport));
    const encoded = selected.map(item => ({...item,
      data: `data:image/webp;base64,${detailImages.get(item.file).toString('base64')}`}));
    function fragment(items, id) {
      const initial = items.find(item => item.route === group.initialRoute && item.viewport === group.initialViewport) ?? items[0];
      // The initial image lives in the data once; render() assigns its src before
      // the first useful frame, avoiding a second full base64 copy in the file.
      return template.replaceAll('__ROOT_ID__', id).replaceAll('__REVIEW_TITLE__', group.title)
        .replace('__INITIAL_ALT__', initial.label)
        .replace('__THEME_HELPER__', helper)
        .replace('__RENDER_DATA__', JSON.stringify({images: items, initialRoute: initial.route, initialViewport: initial.viewport}));
    }
    // A larger future screen may require another fragment. Split the review
    // rather than reducing its native resolution or introducing lossy encoding.
    const batches = [];
    let batch = [];
    for (const item of encoded) {
      const candidate = [...batch, item];
      if (batch.length && Buffer.byteLength(fragment(candidate, group.id)) >= 1_000_000) {
        batches.push(batch);
        batch = [item];
      } else {
        batch = candidate;
      }
    }
    if (batch.length) batches.push(batch);
    for (const [index, items] of batches.entries()) {
      const id = index ? `${group.id}-${index + 1}` : group.id;
      const html = fragment(items, id);
      if (Buffer.byteLength(html) >= 1_000_000) throw new Error(`${id} has one native render larger than the inline size limit`);
      const destination = path.join(inlineDirectory, `${id}.html`);
      await fs.writeFile(destination, html);
      console.log(`${group.title}: ${items.length} renders, 2× lossless, ${Buffer.byteLength(html)} bytes, ${destination}`);
    }
  }
}
console.log(`Review index: ${path.join(preview, 'README.md')}`);
