// A model's bytes, from the store when it has a public address and from this site otherwise.
//
// THE URL IS THE HASH OF THE BYTES. `/api/objects` hands the page one URL per member, built
// from the hash the pointer file names, so a URL that has not changed names bytes that have
// not changed: the browser serves a repeat open out of its own cache, the edge serves a first
// open from wherever the reader is, and this container is not in the path. That is also what
// makes freshness free — `loaded` below compares URLs where the site path compares ETags.
//
// THE OBJECT IS A GZIP OF THE MEMBER, which is what its name says and what every publisher
// puts there. Nothing about the store has to be arranged for a browser: the bytes arrive
// compressed and this decompresses them.
//
// A STORE THAT ANSWERS NOTHING IS NOT AN OUTAGE. Every caller falls back to the site's own
// route, which reads the same member off the container's disk.

import { state } from "./state.js";

/** `{ url }` for a member, or null when the store has no public address or no line for it. */
export function memberUrl(file) {
  return state.memberUrls.get(file) || null;
}

/** Whether this exact member was the last one loaded for `file`. */
export function memberLoaded(file, url) {
  return state.memberLoaded.get(file) === url;
}

export function rememberMember(file, url) {
  state.memberLoaded.set(file, url);
}

// Every caller reads the site when this throws, so a store that answers nothing looks the same
// to a reader as one that answers everything. One line, once a page, says which it is.
let said = false;

/**
 * The member's bytes from `url`, decompressed when they arrive gzipped.
 * Throws when the store does not answer, which is the caller's cue to read the site.
 */
export async function fetchMember(url) {
  let resp;
  try {
    resp = await fetch(url);
  } catch (err) {
    if (!said) { said = true; console.warn("store unreachable, serving from the site:", err); }
    throw err;
  }
  if (!resp.ok) {
    if (!said) { said = true; console.warn(`store answered ${resp.status}, serving from the site:`, url); }
    throw new Error(`${url} — ${resp.status}`);
  }
  const bytes = new Uint8Array(await resp.arrayBuffer());
  if (bytes[0] !== 0x1f || bytes[1] !== 0x8b) return bytes;
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}
