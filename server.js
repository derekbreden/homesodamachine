import express from "express";
import path from "path";
import fs from "fs";
import { fileURLToPath, pathToFileURL } from "url";
import pg from "pg";

import { mountViewerRoutes } from "./lib/viewer-routes.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HARDWARE_DIR = path.join(__dirname, "hardware");
const LANDING_PUBLIC = path.join(__dirname, "public");
const VIEWER_PUBLIC = path.join(__dirname, "tools", "step-viewer", "public");

function attachSubscribe(app) {
  const pool = process.env.DATABASE_URL
    ? new pg.Pool({
        connectionString: process.env.DATABASE_URL,
        ssl: { rejectUnauthorized: false },
      })
    : null;

  if (pool) {
    (async () => {
      for (let attempt = 1; attempt <= 30; attempt++) {
        try {
          await pool.query(`
            CREATE TABLE IF NOT EXISTS subscribers (
              id SERIAL PRIMARY KEY,
              email TEXT NOT NULL UNIQUE,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
          `);
          console.log("schema ready");
          return;
        } catch (e) {
          console.log(`schema init attempt ${attempt} failed: ${e.code || e.message}`);
          await new Promise((r) => setTimeout(r, 2000));
        }
      }
      console.error("schema init giving up after 30 attempts");
    })();
  }

  app.post("/api/subscribe", async (req, res) => {
    const email = String(req.body?.email || "").trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 254) {
      return res.status(400).json({ error: "Invalid email" });
    }
    if (!pool) return res.status(503).json({ error: "Database unavailable" });
    try {
      await pool.query(
        "INSERT INTO subscribers (email) VALUES ($1) ON CONFLICT (email) DO NOTHING",
        [email],
      );
      res.json({ ok: true });
    } catch (e) {
      console.error("subscribe error:", e);
      res.status(500).json({ error: "Server error" });
    }
  });
}

export async function start({ dev = false, port } = {}) {
  const app = express();
  app.use(express.json());

  mountViewerRoutes(app, { hardwareDir: HARDWARE_DIR });

  let server;

  if (dev) {
    // Dev mode: viewer is the front page. Watcher + Python + WebSocket are
    // attached by the dev wrapper after start() returns.
    app.use(express.static(VIEWER_PUBLIC));
    server = app.listen(port ?? process.env.PORT ?? 3000, () => {
      console.log(`Dev viewer: http://localhost:${server.address().port}`);
    });
  } else {
    // Production: landing page at /, dev viewer behind /dev/, signup endpoint.
    app.use(express.static(LANDING_PUBLIC));
    app.get("/dev", (_req, res) => res.sendFile(path.join(VIEWER_PUBLIC, "index.html")));
    app.get("/dev/mermaid", (_req, res) => res.sendFile(path.join(VIEWER_PUBLIC, "mermaid.html")));
    app.use("/dev", express.static(VIEWER_PUBLIC));
    attachSubscribe(app);
    server = app.listen(port ?? process.env.PORT ?? 3001, () => {
      console.log(`Listening on :${server.address().port}`);
    });
  }

  return { app, server, hardwareDir: HARDWARE_DIR };
}

// If run directly (i.e. by Render as `node server.js`), boot in production mode.
const isMain = import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  start({ dev: false });
}
