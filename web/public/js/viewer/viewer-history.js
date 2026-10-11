import { state } from "./state.js";

// Dismissal ends the viewer walk. Browser Back during a walk still follows its
// material/model entries; Back caused by the close button must not reopen one.
export function dismissViewerHistory(depth = 0) {
  if (!location.hash) return;
  if (depth > 0) {
    state.dismissViewerRoute = true;
    history.go(-depth);
  } else history.replaceState(null, "", location.pathname + location.search);
}
