{
  // Exposure for the Fill illustrations on a white page.
  renderer.toneMappingExposure = .6;
  const textureLoader = new THREE.TextureLoader();
  const fillScreenTexture = await textureLoader.loadAsync(o.fillScreen);
  fillScreenTexture.colorSpace = THREE.SRGBColorSpace;
  fillScreenTexture.anisotropy = renderer.capabilities.getMaxAnisotropy();
  const fillScreen = new THREE.Mesh(new THREE.PlaneGeometry(o.screen.width, o.screen.height),
    new THREE.MeshBasicMaterial({map: fillScreenTexture, toneMapped: false}));
  fillScreen.name = "guide-fill-screen";
  fillScreen.rotation.x = o.screen.angle_deg * Math.PI/180;
  fillScreen.position.set(...o.screen.origin);
  currentGroup.add(fillScreen);

  const enclosure = currentGroup.children.find(part => part.name === "enclosure-back-top");
  const cover = currentGroup.children.find(part => part.name === "display-cover");
  if (!enclosure?.isMesh || !cover?.isMesh)
    throw new Error("The Fill scene must contain the enclosure and display cover");
  cover.material = enclosure.material;

  for (const part of currentGroup.children) {
    if (!part.isMesh) continue;
    if (o.view === "frame") {
      part.visible = part.name === "display" || part.name.startsWith("display/") ||
        part.name === "display-cover" || part.name === "display-gasket" ||
        part.name === "guide-fill-screen";
    } else if (o.view === "bottle") {
      part.visible = part.name.startsWith("bottle-");
    } else if (o.view === "closed") {
      // The fill done: the bottle set down and the cover pressed back onto the brim.
      part.visible = !part.name.startsWith("bottle-");
    } else {
      part.visible = part.name.split("/")[0] !== "funnel-cover";
    }
    if (part.name === "bottle-pet") {
      part.material = new THREE.MeshPhysicalMaterial({
        color: "#dce9ee", transparent: true, opacity: .065, depthWrite: false,
        roughness: .18, metalness: .02, clearcoat: .5, clearcoatRoughness: .18,
        side: THREE.FrontSide,
      });
      part.renderOrder = 5;
    } else if (part.name === "bottle-concentrate") {
      part.material = new THREE.MeshStandardMaterial({color: "#361b0d", roughness: .62});
    } else if (part.name.startsWith("bottle-ring-")) {
      part.material = new THREE.MeshPhysicalMaterial({
        color: "#9daeb4", transparent: true, opacity: .63,
        roughness: .18, metalness: .08, depthWrite: false,
      });
      part.renderOrder = 6;
    } else if (part.name.startsWith("bottle-grip-") || part.name === "bottle-collar") {
      part.material = new THREE.MeshStandardMaterial({color: "#17191a", roughness: .42});
    } else if (part.name === "display" || part.name === "display/2") {
      part.material = new THREE.MeshBasicMaterial({color: "#11151a"});
    }
  }

  if (o.view === "fill" || o.view === "bottle") {
    const labelTexture = await textureLoader.loadAsync(o.labelUrl);
    labelTexture.colorSpace = THREE.SRGBColorSpace;
    labelTexture.anisotropy = renderer.capabilities.getMaxAnisotropy();
    // Wrapped in the bottle's own frame, mouth at the origin and base up +Z, then tipped with it.
    // Its middle faces the camera.
    const positions = [], normals = [], uvs = [], indices = [];
    const tilt = (90-o.tip)*Math.PI/180;
    const count = 160, angle = Math.atan2(o.cam[1]*Math.cos(tilt)+o.cam[2]*Math.sin(tilt), o.cam[0]);
    for (let j = 0; j < 2; j++) {
      const z = 72+j*106, radius = 32.25+j*.43;
      for (let i = 0; i <= count; i++) {
        const u = i/count, theta = angle+2*Math.PI*(u-.5);
        positions.push(radius*Math.cos(theta), radius*Math.sin(theta), z);
        normals.push(Math.cos(theta), Math.sin(theta), 0);
        uvs.push(1-u, 1-j);
      }
    }
    for (let i = 0; i < count; i++) {
      indices.push(i, i+1, count+1+i, i+1, count+2+i, count+1+i);
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
    geometry.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
    geometry.setIndex(indices);
    const bottleLabel = new THREE.Mesh(geometry,
      new THREE.MeshStandardMaterial({map: labelTexture, roughness: .62, metalness: .015}));
    bottleLabel.name = "bottle-label";
    bottleLabel.rotation.x = tilt;
    bottleLabel.position.set(...o.mouth);
    currentGroup.add(bottleLabel);
  }
}
