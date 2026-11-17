// Open and refresh the board viewer with the deployed code. The PCB modal
// keeps its view and pan/zoom in shared state across a module reload.

import { state } from "./state.js";
import * as pcbMod from "./pcb.js";

const cache = new Map();

async function currentPcbModule() {
  const version = state.codeVersion;
  if (!version) return pcbMod;
  try {
    if (!cache.has(version)) cache.set(version, await import(`./pcb.js?v=${encodeURIComponent(version)}`));
    return cache.get(version);
  } catch {
    return pcbMod;
  }
}

export async function openPcbDetail(file, push = true) { return (await currentPcbModule()).openPcbDetail(file, push); }
export async function refetchOpenPcb(file) { return (await currentPcbModule()).refetchOpenPcb(file); }

// Browser history uses synchronous teardown before opening the next view.
export const closePcbDetail = pcbMod.closePcbDetail;
