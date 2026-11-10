// The native display reader draws SolidCraft's saved preview or its native mesh export without a CAD engine.
import * as THREE from 'three';
import {unzipSync} from 'three/addons/libs/fflate.module.js';
import {mergeGeometries,toCreasedNormals} from 'three/addons/utils/BufferGeometryUtils.js';

const decoder=new TextDecoder();
async function digest(bytes){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');}
function finish(parts){
  const shapes=parts.map(({geometry,color,matrix})=>{
    if(matrix)geometry.applyMatrix4(matrix);
    const smooth=toCreasedNormals(geometry,Math.PI/6);geometry.dispose();
    const values=new Float32Array(smooth.getAttribute('position').count*3);
    for(let i=0;i<values.length;i+=3){values[i]=color.r;values[i+1]=color.g;values[i+2]=color.b;}
    smooth.setAttribute('color',new THREE.BufferAttribute(values,3));return smooth;
  });
  if(!shapes.length)throw new Error('The native display contains no surfaces.');
  const result=mergeGeometries(shapes,false);for(const shape of shapes)shape.dispose();
  result.computeBoundingBox();return result;
}
export async function readNativeDisplay(bytes,kind,{onEmbedded=()=>{},colors}={}){
  if(kind==='assembly-preview'){
    const zip=unzipSync(new Uint8Array(bytes)),manifest=JSON.parse(decoder.decode(zip['assembly.json']));
    if(manifest.format!=='solidcraft-display-assembly/1')throw new Error('Unsupported native display assembly.');
    const cache=new Map(),parts=[];let bodyOffset=0;
    for(const occurrence of manifest.occurrences){
      const appearance=occurrence.colors?.map((color,i)=>colors?.[bodyOffset+i]||color);bodyOffset+=occurrence.colors?.length||0;
      const key=occurrence.file+JSON.stringify(appearance||[]);
      if(!cache.has(key)){
        const payload=zip[occurrence.file].slice().buffer;onEmbedded(occurrence.file.split('/').pop(),payload);
        cache.set(key,await readNativeDisplay(payload,occurrence.kind,{onEmbedded,colors:appearance}));
      }
      parts.push(cache.get(key).clone().applyMatrix4(new THREE.Matrix4().fromArray(occurrence.transform.flat())));
    }
    const result=mergeGeometries(parts,false);for(const part of parts)part.dispose();for(const part of cache.values())part.dispose();
    result.computeBoundingBox();return result;
  }
  if(kind==='native-export'){
    const {ThreeMFLoader}=await import('three/addons/loaders/3MFLoader.js');
    const scene=new ThreeMFLoader().parse(bytes),parts=[];
    scene.updateMatrixWorld(true);
    scene.traverse(node=>{
      if(!node.isMesh)return;
      const color=colors?.[parts.length]?new THREE.Color().setRGB(...colors[parts.length]).convertSRGBToLinear():node.material.color.clone();
      parts.push({geometry:node.geometry.clone(),color,matrix:node.matrixWorld.clone()});
      node.geometry.dispose();node.material.dispose();
    });
    return finish(parts);
  }
  const zip=unzipSync(new Uint8Array(bytes)),manifest=JSON.parse(decoder.decode(zip['cache/preview.json']));
  const payload=zip['cache/preview.bin'],document=zip['document.json'];
  if(manifest.format!=='solidcraft-preview/1'||!payload||!document
    ||await digest(payload)!==manifest.payload||await digest(document)!==manifest.document)throw new Error('The native saved display does not match its design.');
  const parts=[];
  for(const [bodyIndex,mesh] of manifest.meshes.entries()){
    const data=new DataView(payload.buffer,payload.byteOffset+mesh.offset,mesh.length);
    if(decoder.decode(new Uint8Array(data.buffer,data.byteOffset,8))!=='SCMESH01')throw new Error('Unsupported native display encoding.');
    const coordinates=Number(data.getBigUint64(8,true)),indices=Number(data.getBigUint64(16,true));
    if(coordinates%3||indices%3||24+coordinates*8+indices*4!==mesh.length)throw new Error('Incomplete native display surface.');
    const position=new Float32Array(coordinates),index=new Uint32Array(indices);
    for(let i=0;i<coordinates;i++)position[i]=data.getFloat64(24+i*8,true);
    for(let i=0;i<indices;i++)index[i]=data.getUint32(24+coordinates*8+i*4,true);
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(position,3));geometry.setIndex(new THREE.BufferAttribute(index,1));
    const color=new THREE.Color().setRGB(...(colors?.[bodyIndex]||mesh.color||[.7,.73,.77])).convertSRGBToLinear();
    parts.push({geometry,color});
  }
  return finish(parts);
}
