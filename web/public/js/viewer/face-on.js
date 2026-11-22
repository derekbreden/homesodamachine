// Face on turns around a picked point and remembers the exact camera and orbit target it came from.
import * as THREE from "three";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { camera, controls, turnCamera } from "./scene.js";
import { state } from "./state.js";
import { makeToolButton } from "./tool-rail.js";

function currentPose() {
  return {
    position: camera.position.clone(), target: controls.target.clone(),
    up: camera.up.clone(), rotation: camera.quaternion.clone(), zoom: camera.zoom,
  };
}

function facingPose(start, point, normal) {
  const eye = start.position.clone().sub(point);
  const outward = normal.clone().normalize();
  if (outward.dot(eye) < 0) outward.negate();

  // Keep the machine's height legible. At a pole the current screen supplies the in-plane up.
  const oldBack = new THREE.Vector3(0, 0, 1).applyQuaternion(start.rotation);
  const shortest = new THREE.Quaternion().setFromUnitVectors(oldBack, outward);
  const transportedUp = new THREE.Vector3(0, 1, 0).applyQuaternion(start.rotation).applyQuaternion(shortest);
  const up = new THREE.Vector3(0, 0, 1).projectOnPlane(outward);
  if (up.lengthSq() < 0.01) up.copy(transportedUp);
  else if (up.dot(transportedUp) < 0) up.negate();
  const basis = new THREE.Matrix4().lookAt(outward, new THREE.Vector3(), up);
  const rotation = new THREE.Quaternion().setFromRotationMatrix(basis);
  const turn = rotation.clone().multiply(start.rotation.clone().invert());
  return {
    position: eye.applyQuaternion(turn).add(point),
    target: start.target.clone().sub(point).applyQuaternion(turn).add(point),
    up: start.up.clone().applyQuaternion(turn), rotation, zoom: start.zoom,
  };
}

function moveTo(pose, pivot, finished) {
  const start = currentPose();
  // In camera coordinates the picked point stays still during a face turn. Returning
  // after a manual pan or zoom also interpolates the new distance and in-plane offset.
  function relative(view) {
    const inverse = view.rotation.clone().invert();
    return {
      eye: view.position.clone().sub(pivot).applyQuaternion(inverse),
      up: view.up.clone().applyQuaternion(inverse), distance: view.position.distanceTo(view.target),
    };
  }
  const from = relative(start), to = relative(pose);
  const rotation = new THREE.Quaternion();
  return turnCamera(t => {
    if (t < 1) {
      rotation.slerpQuaternions(start.rotation, pose.rotation, t);
      camera.position.lerpVectors(from.eye, to.eye, t).applyQuaternion(rotation).add(pivot);
      const distance = THREE.MathUtils.lerp(from.distance, to.distance, t);
      controls.target.set(0, 0, -distance).applyQuaternion(rotation).add(camera.position);
      camera.up.lerpVectors(from.up, to.up, t).applyQuaternion(rotation);
    } else {
      camera.position.copy(pose.position);
      controls.target.copy(pose.target);
      camera.up.copy(pose.up);
    }
    const zoom = THREE.MathUtils.lerp(start.zoom, pose.zoom, t);
    if (zoom !== camera.zoom) { camera.zoom = zoom; camera.updateProjectionMatrix(); }
  }, finished);
}

function pickedNormal(pick) {
  const face = pick?.face;
  return face?.kind === "plane" ? face.n : pick?.kind === "plane" ? pick.normal : null;
}

export function createFaceOn({ wrapper }) {
  let previous = null, cancelTurn;
  const rail = wrapper.querySelector(".tool-rail") || wrapper;
  const button = makeToolButton({
    className: "previous-view", label: "Previous view", title: "Return to the view before Face on",
    onClick: () => {
      if (!previous) return;
      const { pose, pivot, trigger } = previous;
      cancelTurn = moveTo(pose, pivot, () => {
        if (document.activeElement === button && trigger?.isConnected) trigger.focus({ preventScroll: true });
        forget();
      });
    },
  });
  function forget() {
    cancelTurn?.();
    previous = null;
    button.remove();
  }
  function onMount({ detail }) {
    if (previous && previous.file !== detail.file) forget();
  }
  window.addEventListener(HSM_EVENTS.STEP_MOUNTED, onMount);
  function canUse(pick) {
    const normal = pickedNormal(pick);
    return !!(pick?.point?.isVector3 && normal?.isVector3 && normal.lengthSq() > 0);
  }
  function start(pick) {
    if (!canUse(pick)) return false;
    const pose = currentPose(), pivot = pick.point.clone();
    const destination = facingPose(pose, pivot, pickedNormal(pick));
    if (pose.rotation.angleTo(destination.rotation) < 1e-7) return false;
    if (previous?.pick !== pick) {
      previous = { pick, pose, pivot, file: state.mountedDetail?.file, trigger: document.activeElement };
    }
    rail.append(button);
    cancelTurn = moveTo(destination, pivot);
    return true;
  }
  return {
    canUse, start,
    dispose() { forget(); window.removeEventListener(HSM_EVENTS.STEP_MOUNTED, onMount); },
  };
}
