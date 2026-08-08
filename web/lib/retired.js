// The `.retired` marker — the single rule for what a directory is OUT of.
//
// A directory holding a `.retired` file, and everything under it, is source kept for reading
// and nothing else: its scripts are not runnables, its modules are not import targets, its
// `.step`s have no producer, and none of the files beside them are content the site serves.
// Nothing under it is built, watched, rebuilt or compared. The marker's own text says what
// the tree is kept for.
//
// Both readers import the rule from here so they cannot disagree about what is retired: the
// build graph (`dev-server/deps.js`), which decides what gets built, and the file walkers
// (`lib/walk.js`), which decide what the viewer browses and what the deploy diff notifies on.
// A tree one excludes and the other still lists is a model nothing can rebuild, served as if
// it were live.

export const RETIRED_MARKER = ".retired";

// True when a directory listing carries the marker. Takes the `withFileTypes` entries the
// callers have already read, so honouring the marker costs no extra syscall.
export function holdsRetiredMarker(entries) {
  return entries.some((e) => e.isFile() && e.name === RETIRED_MARKER);
}
