// Fit the visible render inside a Parts tile with even padding around its limiting axis.
import path from "node:path";
import { pathToFileURL } from "node:url";
import sharp from "sharp";

const tileAspect = 1.23;
const tileFill = 0.88;

export async function writeCatalogThumbnail(source, destination) {
  const image = sharp(source);
  const { data, info } = await image.clone().ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  const { width, height, channels } = info;
  let left = width;
  let top = height;
  let right = -1;
  let bottom = -1;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const alpha = data[(y * width + x) * channels + channels - 1];
      if (alpha === 0) continue;
      left = Math.min(left, x);
      top = Math.min(top, y);
      right = Math.max(right, x);
      bottom = Math.max(bottom, y);
    }
  }
  if (right < left) throw new Error(`Empty thumbnail render: ${source}`);

  const crop = { left, top, width: right - left + 1, height: bottom - top + 1 };
  const paddedWidth = Math.max(crop.width, crop.height * tileAspect) / tileFill;
  const canvasWidth = Math.round(paddedWidth);
  const canvasHeight = Math.round(paddedWidth / tileAspect);
  const padX = Math.floor((canvasWidth - crop.width) / 2);
  const padY = Math.floor((canvasHeight - crop.height) / 2);
  await image.extract(crop).extend({
    left: padX,
    top: padY,
    right: canvasWidth - crop.width - padX,
    bottom: canvasHeight - crop.height - padY,
    background: { r: 0, g: 0, b: 0, alpha: 0 },
  }).webp({ quality: 84 }).toFile(destination);
}

// `node tools/render/catalog-thumbnail.mjs SOURCE.png DESTINATION.webp ...` fits each pair.
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const files = process.argv.slice(2);
  if (!files.length || files.length % 2) {
    throw new Error("Usage: node tools/render/catalog-thumbnail.mjs SOURCE.png DESTINATION.webp ...");
  }
  for (let i = 0; i < files.length; i += 2) await writeCatalogThumbnail(files[i], files[i + 1]);
}
