// The SolidCraft lab serves isolated native examples and streams its pinned browser runtime only on demand.
import path from 'node:path';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { Readable } from 'node:stream';
import { pipeline } from 'node:stream/promises';

const publicDir = fileURLToPath(new URL('../public/solidcraft-lab/', import.meta.url));
const runtime = JSON.parse(readFileSync(path.join(publicDir, 'runtime.json'), 'utf8'));
const base = '/labs/solidcraft/beduan';
const release = `https://github.com/derekbreden/homesodamachine/releases/download/${runtime.release}/`;

export function mountSolidcraftLab(app, {
  hardwareDir = fileURLToPath(new URL('../../hardware/', import.meta.url)), runtimeDirectory,
} = {}) {
  const carbonator = '/labs/solidcraft/carbonator';
  app.get([carbonator, `${carbonator}/`], (_req, res) => {
    res.set('Cache-Control', 'no-cache');
    res.sendFile(path.join(publicDir, 'carbonator/index.html'));
  });
  const nativeModels = {
    tube: 'parts/tube.json', endcap: 'parts/endcap.json', core: 'carbonator.json', parent: 'parent.json',
    representation: 'representation.json',
  };
  app.get(`${carbonator}/native/:model`, (req, res) => {
    const file = nativeModels[req.params.model];
    if (!file) return res.status(404).end();
    res.set('Cache-Control', 'no-cache');
    res.sendFile(path.join(hardwareDir, 'reference/carbonator-core/solidcraft', file));
  });
  app.get([base, `${base}/`], (_req, res) => {
    res.set('Cache-Control', 'no-cache');
    res.sendFile(path.join(publicDir, 'beduan.html'));
  });
  app.get(`${base}/editor`, (_req, res) => {
    res.set('Cache-Control', 'no-cache');
    res.sendFile(path.join(publicDir, 'editor.html'));
  });
  app.get(`${base}/model.json`, (_req, res) => {
    res.set('Cache-Control', 'no-cache');
    res.sendFile(path.join(hardwareDir, 'reference/beduan-solenoid/solidcraft/beduan-valve.json'));
  });
  app.get(`${base}/runtime/*file`, async (req, res) => {
    const file = req.params.file.join('/');
    const asset = runtime.assets[file];
    if (!asset) return res.status(404).end();
    res.set({
      'Content-Type': asset.contentType,
      'Cache-Control': 'public, max-age=31536000, immutable',
      'X-Content-Type-Options': 'nosniff',
      ...(asset.contentEncoding ? { 'Content-Encoding': asset.contentEncoding } : {}),
    });
    if (runtimeDirectory) return res.sendFile(path.join(runtimeDirectory, asset.asset), {dotfiles: 'allow'});
    const controller = new AbortController();
    const abort = () => { if (!res.writableEnded) controller.abort(); };
    res.once('close', abort);
    try {
      const upstream = await fetch(release + asset.asset, {
        method: req.method === 'HEAD' ? 'HEAD' : 'GET',
        signal: AbortSignal.any([controller.signal, AbortSignal.timeout(180000)]),
      });
      if (!upstream.ok) throw new Error(`Runtime download returned ${upstream.status}`);
      const length = upstream.headers.get('content-length');
      if (length) res.set('Content-Length', length);
      if (req.method === 'HEAD') return res.end();
      await pipeline(Readable.fromWeb(upstream.body), res);
    } catch (error) {
      if (controller.signal.aborted) return;
      if (res.headersSent) return res.destroy(error);
      res.removeHeader('Content-Encoding');
      res.removeHeader('Content-Length');
      res.set('Cache-Control', 'no-store');
      res.status(502).type('text/plain').send('The native browser runtime could not be downloaded. Please retry.');
    } finally {
      res.off('close', abort);
    }
  });
}
