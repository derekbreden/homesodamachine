#!/usr/bin/env node
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(new URL("../../../web/package.json", import.meta.url));
const express = require("express");
const app = express();
app.get("/favicon.ico", (_req, res) => res.sendStatus(204));
app.use(express.static(fileURLToPath(new URL("./out/", import.meta.url))));
const server = app.listen(Number(process.argv[2] || 0), "127.0.0.1", () => {
  console.log(`Tour video preview: http://127.0.0.1:${server.address().port}/`);
});
