// Guards the browser side of the web/contracts/ single-sourcing.
//
// The server imports these contracts directly (events.js -> ws-frames.js), so
// a normal node:test exercises its half. The viewer runs in a browser and
// pulls three.js + touches document/window, so it can't be loaded here the
// same way — instead we assert at the source level that the browser modules
// IMPORT the shared constants from /contracts and never re-inline the wire
// strings. Without this, boot.js could drift to new CustomEvent("hsm:...")
// again and silently disagree with the server that broadcasts the frame — the
// exact class of bug the homing was meant to kill.
//
// Pair with smoke.test.js, which asserts /contracts/*.js is actually served
// (the runtime other half: the import above resolves over HTTP).

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { HSM_EVENTS } from "../contracts/client-events.js";
import { WS } from "../contracts/ws-frames.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PUBLIC = path.resolve(__dirname, "..", "public");
const read = (rel) => fs.readFileSync(path.join(PUBLIC, rel), "utf8");

// Every browser module that dispatches or listens for an hsm:* CustomEvent.
const EVENT_MODULES = [
  "boot.js",
  "js/viewer/live.js",
  "js/viewer/pcb-pick.js",
  "js/viewer/pcb-edit.js",
];

const IMPORTS_HSM_EVENTS =
  /import\s*\{[^}]*\bHSM_EVENTS\b[^}]*\}\s*from\s*["']\/contracts\/client-events\.js["']/;

// A dispatch/listen call built from a raw "hsm:" literal — the pattern the
// refactor removed. Anchored on the call so the "hsm:pcb-tool" that appears
// inside a comment (pcb-edit.js) is not mistaken for a live call site.
const RAW_EVENT_CALL = /(?:CustomEvent|addEventListener)\(\s*["']hsm:/;

test("every hsm:* consumer imports HSM_EVENTS from the served contract", () => {
  for (const rel of EVENT_MODULES) {
    assert.match(read(rel), IMPORTS_HSM_EVENTS,
      `${rel} must import HSM_EVENTS from /contracts/client-events.js`);
  }
});

test("no hsm:* CustomEvent is dispatched or listened for by raw literal", () => {
  for (const rel of EVENT_MODULES) {
    assert.doesNotMatch(read(rel), RAW_EVENT_CALL,
      `${rel} builds a CustomEvent/addEventListener from a raw "hsm:" string ` +
      `instead of HSM_EVENTS`);
  }
});

// boot.js is the sole WebSocket client; it must match frame types via the WS
// contract, never a bare string (which the server could rename out from under).
test("boot.js imports WS and matches frames by constant", () => {
  const src = read("boot.js");
  assert.match(src,
    /import\s*\{[^}]*\bWS\b[^}]*\}\s*from\s*["']\/contracts\/ws-frames\.js["']/,
    "boot.js must import WS from /contracts/ws-frames.js");
  for (const type of Object.values(WS)) {
    assert.doesNotMatch(src, new RegExp(`msg\\.type\\s*===\\s*["']${type}["']`),
      `boot.js matches the "${type}" frame by literal instead of WS`);
  }
});

// The imported constants must carry the exact strings the whole system already
// agreed on — the single source is only "single" if it holds the real values.
// (The server sends WS.* frames in events.js; the pickers key off HSM_EVENTS.)
test("contract constants hold the agreed wire strings", () => {
  assert.equal(HSM_EVENTS.FILES_CHANGED, "hsm:files-changed");
  assert.equal(HSM_EVENTS.POSTS_CHANGED, "hsm:posts-changed");
  assert.equal(HSM_EVENTS.DEPLOY, "hsm:deploy");
  assert.equal(HSM_EVENTS.NOTIFICATIONS_UPDATED, "hsm:notifications-updated");
  assert.equal(HSM_EVENTS.PCB_TOOL, "hsm:pcb-tool");
  assert.equal(WS.HELLO, "hello");
  assert.equal(WS.PING, "ping");
  assert.equal(WS.FILES_CHANGED, "files-changed");
  assert.equal(WS.POSTS_CHANGED, "posts-changed");
});
