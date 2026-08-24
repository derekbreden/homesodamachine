// WHERE WE ARE COMING FROM, AND WHERE WE ARE GOING TO — written on the two
// places themselves, while the camera is between them.
//
// The wide shot in the middle of a flight holds both subjects, which is what
// makes the move legible; these are what make it unambiguous. Two chips pinned
// to the two subjects in screen space: the one being left, fading out as the
// move ends, and the one being arrived at, fading in as it begins. Between
// them the reader has the answer without having to recognise a fitting.
//
// They exist only during a move. A held beat has the card for its name and
// everything lit is its subject, so a pin there would be a third label saying
// what two already say.

import * as THREE from "three";

const OUT = "←"; // from here
const IN = "→";  // to there

const _v = new THREE.Vector3();

function chip(cls) {
  const n = document.createElement("div");
  n.className = `tour-tag ${cls}`;
  n.innerHTML = '<span class="tour-tag-arrow"></span><span class="tour-tag-text"></span>';
  return n;
}

export function mountTags(host) {
  const from = chip("tour-tag-from");
  const to = chip("tour-tag-to");
  host.append(from, to);

  function place(node, box, camera, rect, alpha, arrow, text) {
    if (!box || box.isEmpty() || alpha <= 0.02) { node.style.opacity = "0"; return; }
    box.getCenter(_v);
    _v.project(camera);
    // Behind the camera: the projection wraps and the chip would land on the
    // opposite side of the frame from the thing it names.
    if (_v.z > 1) { node.style.opacity = "0"; return; }
    const x = THREE.MathUtils.clamp((_v.x * 0.5 + 0.5) * rect.width, 70, rect.width - 70);
    const y = THREE.MathUtils.clamp((-_v.y * 0.5 + 0.5) * rect.height, 40, rect.height - 120);
    node.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px)`;
    node.style.opacity = String(alpha);
    node.querySelector(".tour-tag-arrow").textContent = arrow;
    const t = node.querySelector(".tour-tag-text");
    if (t.textContent !== text) t.textContent = text;
  }

  return {
    /** `mix` is the move's own 0→1. Both chips are up through the middle of it,
     *  which is where the wide shot is. */
    update({ camera, rect, mix, fromBox, fromText, toBox, toText, active }) {
      if (!active) { from.style.opacity = "0"; to.style.opacity = "0"; return; }
      camera.updateMatrixWorld();
      place(from, fromBox, camera, rect, Math.min(1, (1 - mix) * 1.9), OUT, fromText || "");
      place(to, toBox, camera, rect, Math.min(1, mix * 1.9), IN, toText || "");
    },
    hide() { from.style.opacity = "0"; to.style.opacity = "0"; },
  };
}
