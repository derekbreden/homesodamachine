#!/usr/bin/env node
// uvc.js — read and set the panelcam's focus and exposure, over the wire it actually answers on.
//
//   node uvc.js show                 # what this camera implements, and where each value sits
//   node uvc.js get absolute_focus
//   node uvc.js set absolute_focus 170
//   node uvc.js set auto_focus 0
//   node uvc.js hold "auto_focus=0,gain=0" 120   # rewrite them every 120 ms until terminated
//
// THE UNIT IDS ARE READ, NOT ASSUMED. A UVC control request is addressed to a unit inside the
// camera, and a request sent to the wrong unit is answered with a STALL that looks exactly like
// "this camera cannot do that". `uvcc` guesses those ids and every control on this camera stalls;
// the ids are in the device's own VideoControl descriptors, where this reads them. On the ELP
// they are CameraTerminal 1 and ProcessingUnit 2.
//
// bmControls IS THE CAMERA'S OWN ANSWER about what it supports — one bit per control, published
// in the same descriptors. `show` prints what the bits say and then reads each one, because a
// bit that is set and a value that comes back are two different claims.
//
// This talks to the control interface only. It never opens the video stream, so it needs no
// camera permission from macOS and does not disturb a capture in flight.

import { getDeviceList } from "usb";

const VENDOR = 0x32e4; // ELP / Ailipu

// UVC 1.5 §4.2: control selectors, and their bmControls bit positions.
const CAMERA = {
  scanning_mode:          { bit: 0,  cs: 0x01, len: 1 },
  auto_exposure_mode:     { bit: 1,  cs: 0x02, len: 1 },
  auto_exposure_priority: { bit: 2,  cs: 0x03, len: 1 },
  absolute_exposure_time: { bit: 3,  cs: 0x04, len: 4 },
  absolute_focus:         { bit: 5,  cs: 0x06, len: 2 },
  absolute_zoom:          { bit: 9,  cs: 0x0b, len: 2 },
  absolute_pan_tilt:      { bit: 11, cs: 0x0d, len: 8, signed: true },
  auto_focus:             { bit: 17, cs: 0x08, len: 1 },
};
const PROCESSING = {
  brightness:                    { bit: 0,  cs: 0x02, len: 2, signed: true },
  contrast:                      { bit: 1,  cs: 0x03, len: 2 },
  hue:                           { bit: 2,  cs: 0x06, len: 2, signed: true },
  saturation:                    { bit: 3,  cs: 0x07, len: 2 },
  sharpness:                     { bit: 4,  cs: 0x08, len: 2 },
  gamma:                         { bit: 5,  cs: 0x09, len: 2 },
  white_balance_temperature:     { bit: 6,  cs: 0x0a, len: 2 },
  backlight_compensation:        { bit: 8,  cs: 0x01, len: 2 },
  gain:                          { bit: 9,  cs: 0x04, len: 2 },
  power_line_frequency:          { bit: 10, cs: 0x05, len: 1 },
  white_balance_temperature_auto:{ bit: 12, cs: 0x0b, len: 1 },
};

const GET_CUR = 0x81, GET_MIN = 0x82, GET_MAX = 0x83, SET_CUR = 0x01;

function openCamera() {
  const dev = getDeviceList().find((d) => d.deviceDescriptor.idVendor === VENDOR);
  if (!dev) throw new Error(`no UVC camera with vendor 0x${VENDOR.toString(16)} attached`);
  dev.open();
  const vc = dev.configDescriptor.interfaces[0][0]; // VideoControl is always interface 0
  return { dev, iface: vc.bInterfaceNumber, units: parseUnits(vc.extra) };
}

// Walk the class-specific VideoControl descriptors for the two units that carry controls.
function parseUnits(extra) {
  const units = {};
  for (let i = 0; i < extra.length; ) {
    const len = extra[i] || 1, type = extra[i + 1], sub = extra[i + 2];
    if (type === 0x24 && sub === 0x02 && (extra[i + 4] | (extra[i + 5] << 8)) === 0x0201) {
      units.camera = { id: extra[i + 3], bm: readBitmap(extra, i + 15, extra[i + 14]), map: CAMERA };
    } else if (type === 0x24 && sub === 0x05) {
      units.processing = { id: extra[i + 3], bm: readBitmap(extra, i + 8, extra[i + 7]), map: PROCESSING };
    }
    i += len;
  }
  return units;
}

const readBitmap = (buf, off, n) => {
  let bm = 0n;
  for (let k = 0; k < n; k++) bm |= BigInt(buf[off + k]) << BigInt(8 * k);
  return bm;
};

const unitFor = (units, name) =>
  Object.values(units).find((u) => name in u.map);

const transfer = (dev, req, unit, spec, iface, dataOrLen) =>
  new Promise((resolve, reject) =>
    dev.controlTransfer(
      req === SET_CUR ? 0x21 : 0xa1, req,
      spec.cs << 8, (unit.id << 8) | iface, dataOrLen,
      (err, data) => (err ? reject(err) : resolve(data)),
    ));

// UVC mixes signed and unsigned controls of the same width, and no descriptor says which is
// which — the spec does, per control. Read brightness as unsigned and its floor comes back as
// 65472 rather than -64.
const decode = (buf, spec) => {
  let v = 0;
  for (let i = buf.length - 1; i >= 0; i--) v = v * 256 + buf[i];
  if (spec?.signed) {
    const span = 2 ** (8 * buf.length);
    if (v >= span / 2) v -= span;
  }
  return v;
};

const encode = (value, len) => {
  const b = Buffer.alloc(len);
  let v = value < 0 ? value + 2 ** (8 * len) : value;
  for (let i = 0; i < len; i++) { b[i] = v & 0xff; v = Math.floor(v / 256); }
  return b;
};

async function cmdShow({ dev, iface, units }) {
  for (const [kind, unit] of Object.entries(units)) {
    console.log(`\n${kind} unit id=${unit.id}`);
    for (const [name, spec] of Object.entries(unit.map)) {
      if (!(unit.bm & (1n << BigInt(spec.bit)))) continue;
      let line;
      try {
        const cur = decode(await transfer(dev, GET_CUR, unit, spec, iface, spec.len), spec);
        let range = "";
        try {
          const lo = decode(await transfer(dev, GET_MIN, unit, spec, iface, spec.len), spec);
          const hi = decode(await transfer(dev, GET_MAX, unit, spec, iface, spec.len), spec);
          range = `  [${lo}..${hi}]`;
        } catch { /* a control may publish no range; the value still stands */ }
        line = `${cur}${range}`;
      } catch (e) {
        line = `unreadable (${e.message})`;
      }
      console.log(`  ${name.padEnd(32)} ${line}`);
    }
  }
}

// While the stream is open this camera walks its own lens: auto_focus reads back 0 and
// absolute_focus still climbs 340, 370, 400. Written again every few hundred milliseconds, the
// value stays where it is put. Runs until terminated.
async function cmdHold({ dev, iface, units }, spec, intervalMs) {
  const pairs = String(spec).split(",")
    .map((s) => s.split("="))
    .filter((a) => a.length === 2)
    .map(([name, value]) => {
      const unit = unitFor(units, name);
      if (!unit) throw new Error(`unknown control '${name}'`);
      return { unit, spec: unit.map[name], value: Number(value), name };
    });
  let running = true;
  const stop = () => { running = false; };
  process.on("SIGTERM", stop);
  process.on("SIGINT", stop);
  while (running) {
    for (const p of pairs) {
      if (!(p.unit.bm & (1n << BigInt(p.spec.bit)))) continue;
      try {
        await transfer(dev, SET_CUR, p.unit, p.spec, iface, encode(p.value, p.spec.len));
      } catch { /* a write lost to a busy device is retried on the next pass */ }
    }
    await new Promise((r) => setTimeout(r, intervalMs));
  }
}

async function main() {
  const [action, name, value] = process.argv.slice(2);
  const cam = openCamera();
  try {
    if (action === "show" || !action) return await cmdShow(cam);
    if (action === "hold") return await cmdHold(cam, name, Number(value) || 350);
    const unit = unitFor(cam.units, name);
    if (!unit) throw new Error(`unknown control '${name}' — run 'show' for the list`);
    const spec = unit.map[name];
    if (!(unit.bm & (1n << BigInt(spec.bit))))
      throw new Error(`this camera does not implement '${name}'`);

    if (action === "get") {
      console.log(decode(await transfer(cam.dev, GET_CUR, unit, spec, cam.iface, spec.len), spec));
    } else if (action === "set") {
      if (value === undefined) throw new Error(`set needs a value`);
      await transfer(cam.dev, SET_CUR, unit, spec, cam.iface, encode(Number(value), spec.len));
      console.log(decode(await transfer(cam.dev, GET_CUR, unit, spec, cam.iface, spec.len), spec));
    } else {
      throw new Error(`usage: uvc.js show | get <control> | set <control> <value> | hold <k=v,…> <ms>`);
    }
  } finally {
    cam.dev.close();
  }
}

main().catch((e) => { console.error(`panelcam-uvc: ${e.message}`); process.exit(1); });
