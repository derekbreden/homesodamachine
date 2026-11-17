// Release ZIPs store each original print file verbatim. The index addresses that file's byte range.
import { readFileSync } from "node:fs";
import path from "node:path";
import { Readable } from "node:stream";
import { pipeline } from "node:stream/promises";

const DOWNLOADS = "https://github.com/derekbreden/homesodamachine/releases/download/print-projects/";
export const BLOB_ID = /^[a-f0-9]{40}$/;

export function readPrintArchive(hardwareDir) {
  try {
    return JSON.parse(readFileSync(path.join(hardwareDir, "print-archive.json"), "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") return { blobs: {}, checkout: {} };
    throw error;
  }
}

export async function printArchiveStream(entry, signal) {
  const range = `${entry.offset}-${entry.offset + entry.bytes - 1}`;
  const response = await fetch(DOWNLOADS + encodeURIComponent(entry.archive), {
    headers: { Range: `bytes=${range}` }, signal,
  });
  const contentRange = response.headers.get("content-range") ?? "";
  if (response.status !== 206 || !contentRange.startsWith(`bytes ${range}/`)
      || Number(response.headers.get("content-length")) !== entry.bytes) {
    await response.body?.cancel();
    throw new Error(`Release asset ${entry.archive} did not return bytes ${range}`);
  }
  return Readable.fromWeb(response.body);
}

export function mountPrintArchive(app, hardwareDir) {
  const { blobs } = readPrintArchive(hardwareDir);
  app.get("/print-archive/:blob/:filename", async (req, res) => {
    const { blob, filename } = req.params;
    const entry = BLOB_ID.test(blob) && blobs[blob];
    if (!entry || !/\.(3mf|zip)$/i.test(filename) || /[/\\\u0000-\u001f\u007f]/.test(filename)) {
      return res.status(404).send("Print archive not found");
    }
    const abort = new AbortController();
    res.once("close", () => abort.abort());
    try {
      const stream = req.method === "HEAD" ? null : await printArchiveStream(entry, abort.signal);
      res.attachment(filename).set({
        "Content-Length": String(entry.bytes),
        "Cache-Control": "public, max-age=31536000, immutable",
      });
      if (!stream) return res.end();
      await pipeline(stream, res);
    } catch (error) {
      if (res.destroyed) return;
      if (res.headersSent) return res.destroy(error);
      res.removeHeader("Content-Length");
      res.removeHeader("Content-Disposition");
      res.status(502).send("Print archive temporarily unavailable");
    }
  });
}
