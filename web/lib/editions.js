// The editions the viewer serves. An edition is one machine: a content root
// holding its own generators, assemblies and outputs, built and browsed
// independently of the others.
//
// This list is the single source of truth. It feeds:
//   - dev-server/deps.js  contentRoots()  — what the watcher walks and rebuilds
//   - server.js                           — the dirs handed to the viewer routes
//   - lib/viewer-routes.js                — which root a request resolves against
//   - lib/shell.js                        — the pre-paint cookie mirror
//   - lib/settings.js + public/settings.js — the Edition selector
//
// so adding one is this array plus the directory. `id` is the cookie /
// localStorage value and must stay stable; `dir` is path segments from the
// repo root.
//
// `shares` is what an edition reaches for outside its own root, and it is
// checked: tools/check_editions.py resolves every anchored path in an
// edition's Python and fails on one that leaves the tree without being
// declared here. (`tools/` is shared by all of them and needs no entry.) An
// empty list is the strong claim — this edition is self-contained, and a path
// into another machine's tree is a bug, not a shortcut.
export const EDITIONS = [
  {
    id: "kitchen",
    label: "Kitchen",
    help: "The counter appliance. hardware/",
    dir: ["hardware"],
    shares: [],
  },
  {
    id: "lite",
    label: "Lite",
    help: "The stripped build. pie-in-the-sky/lite/",
    dir: ["pie-in-the-sky", "lite"],
    // Lite carries its own enclosure and trays but no tooling or purchased-part
    // models: it builds with the kitchen's hardware/scripts and loads reference
    // STEPs (the display) out of hardware/reference.
    shares: ["hardware"],
  },
  {
    id: "thin",
    label: "Thin",
    help: "The tall, narrow machine. thin/hardware/",
    dir: ["thin", "hardware"],
    shares: [],
  },
];

// The edition a request falls back to when the cookie is absent or names one
// that no longer exists.
export const DEFAULT_EDITION = "kitchen";

export const EDITION_IDS = EDITIONS.map((e) => e.id);

// Each edition's content root as one repo-root-relative path. This is the prefix a
// pick blob's `file:` line carries, and the viewer's own paths are what is left after
// it. Mirrored into the page pre-paint by lib/shell.js, because the edge picker has to
// name the machine it is looking at — the trees mirror each other's filenames, so a
// blob prefixed with the wrong root reads as a real path into another machine.
export const EDITION_DIRS = Object.fromEntries(EDITIONS.map((e) => [e.id, e.dir.join("/")]));

export function editionById(id) {
  return EDITIONS.find((e) => e.id === id) || null;
}
