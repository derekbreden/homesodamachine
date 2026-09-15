// Where the objects live: Cloudflare R2, or a disk on this service, behind one shape.
//
// An object is a gzipped member of the pointer file, named `s-<sha256>.gz` after the bytes
// inside it. The store holds them and answers five questions: has, list, put, remove, and
// where a reader fetches one from. The routes in objects.js and the fill step in
// fetch-cad-artifacts.mjs speak only this shape, so which store stands behind the site is
// the environment's choice and nothing else changes.
//
// R2 IS THE STORE. Its public URL serves every object straight from Cloudflare: a deploy's
// 586 MB fetch and every adopt read from there, not through this service; the site's GET
// redirects a reader to that URL and its HEAD answers from the bucket. The disk store is what
// a laptop or a test runs against, and needs no account. With neither configured there is no
// store, and the site serves what its build fetched.

import { createReadStream } from "node:fs";
import { copyFile, mkdir, readdir, rm, stat } from "node:fs/promises";
import path from "node:path";

export const OBJECT_NAME = /^s-([0-9a-f]{64})\.gz$/;

export class DiskStore {
  constructor(dir) {
    this.dir = dir;
    this.kind = "disk";
  }

  pathOf(name) {
    return path.join(this.dir, name);
  }

  async has(name) {
    try {
      return (await stat(this.pathOf(name))).isFile();
    } catch {
      return false;
    }
  }

  /** `[{name, modified}]` for every object held, `modified` an epoch in ms. */
  async list() {
    let entries;
    try {
      entries = await readdir(this.dir);
    } catch {
      return [];
    }
    const out = [];
    for (const name of entries) {
      if (!OBJECT_NAME.test(name)) continue;
      try {
        const st = await stat(this.pathOf(name));
        if (st.isFile()) out.push({ name, modified: st.mtimeMs });
      } catch { /* gone between readdir and stat */ }
    }
    return out;
  }

  /** Keep the file at `src` as `name`; the disk is its own device. */
  async put(name, src) {
    await mkdir(this.dir, { recursive: true });
    const part = `${this.pathOf(name)}.${process.pid}.${Date.now()}.part`;
    await copyFile(src, part);
    const { rename } = await import("node:fs/promises");
    await rename(part, this.pathOf(name));
  }

  async remove(names) {
    for (const name of names) await rm(this.pathOf(name), { force: true });
  }

  /** A URL a reader is sent to, or null: a disk is read through this service. */
  redirectUrl() {
    return null;
  }

  readStream(name) {
    return createReadStream(this.pathOf(name));
  }
}

export class R2Store {
  /**
   * `client` is an S3 client for the bucket's endpoint; `publicUrl` the bucket's public
   * development URL or custom domain, with no trailing slash needed.
   */
  constructor({ client, bucket, publicUrl }) {
    this.client = client;
    this.bucket = bucket;
    this.publicUrl = publicUrl ? publicUrl.replace(/\/+$/, "") : null;
    this.kind = "r2";
  }

  async has(name) {
    const { HeadObjectCommand } = await import("@aws-sdk/client-s3");
    try {
      await this.client.send(new HeadObjectCommand({ Bucket: this.bucket, Key: name }));
      return true;
    } catch (err) {
      if (err?.$metadata?.httpStatusCode === 404 || err?.name === "NotFound") return false;
      throw err;
    }
  }

  async list() {
    const { ListObjectsV2Command } = await import("@aws-sdk/client-s3");
    const out = [];
    let token;
    do {
      const page = await this.client.send(new ListObjectsV2Command({
        Bucket: this.bucket, ContinuationToken: token, MaxKeys: 1000,
      }));
      for (const o of page.Contents ?? []) {
        if (OBJECT_NAME.test(o.Key)) out.push({ name: o.Key, modified: new Date(o.LastModified).getTime() });
      }
      token = page.IsTruncated ? page.NextContinuationToken : undefined;
    } while (token);
    return out;
  }

  async put(name, src) {
    const { PutObjectCommand } = await import("@aws-sdk/client-s3");
    const size = (await stat(src)).size;
    await this.client.send(new PutObjectCommand({
      Bucket: this.bucket, Key: name, Body: createReadStream(src), ContentLength: size,
      ContentType: "application/gzip", CacheControl: "public, max-age=31536000, immutable",
    }));
  }

  async remove(names) {
    if (!names.length) return;
    const { DeleteObjectsCommand } = await import("@aws-sdk/client-s3");
    for (let i = 0; i < names.length; i += 1000) {
      await this.client.send(new DeleteObjectsCommand({
        Bucket: this.bucket,
        Delete: { Objects: names.slice(i, i + 1000).map((Key) => ({ Key })), Quiet: true },
      }));
    }
  }

  redirectUrl(name) {
    return this.publicUrl ? `${this.publicUrl}/${name}` : null;
  }

  async readStream(name) {
    const { GetObjectCommand } = await import("@aws-sdk/client-s3");
    const got = await this.client.send(new GetObjectCommand({ Bucket: this.bucket, Key: name }));
    return got.Body;
  }
}

/** The store the environment names: R2 when its account and key pair are set, else the disk, else none. */
export async function storeFromEnv(env = process.env) {
  const { R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET, R2_PUBLIC_URL, OBJECTS_DIR } = env;
  if (R2_ACCOUNT_ID && R2_ACCESS_KEY_ID && R2_SECRET_ACCESS_KEY && R2_BUCKET) {
    const { S3Client } = await import("@aws-sdk/client-s3");
    const client = new S3Client({
      region: "auto",
      endpoint: `https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com`,
      credentials: { accessKeyId: R2_ACCESS_KEY_ID, secretAccessKey: R2_SECRET_ACCESS_KEY },
    });
    return new R2Store({ client, bucket: R2_BUCKET, publicUrl: R2_PUBLIC_URL || null });
  }
  if (OBJECTS_DIR) return new DiskStore(OBJECTS_DIR);
  return null;
}
