// Manual scene tests exercise progressive loading, failed parts and shared-object placement.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { resolveScene } from '../public/js/viewer/shared-scene.js';

function encoded(head, blob = new Uint8Array()) {
  const text = new TextEncoder().encode(JSON.stringify(head));
  const n = Math.ceil(text.length / 4) * 4;
  const bytes = new Uint8Array(4+n+blob.length);
  new DataView(bytes.buffer).setUint32(0,n,true);bytes.fill(32,4,4+n);bytes.set(text,4);bytes.set(blob,4+n);
  return bytes;
}
function object(x) {
  const bytes = new Uint8Array(92), view = new DataView(bytes.buffer);
  const pos = [x,0,0,x+1,0,0,x,1,0], nrm = [0,0,1,0,0,1,0,0,1];
  [...pos,...nrm].forEach((v,i)=>view.setFloat32(i*4,v,true));
  [0,1,2,0,0].forEach((v,i)=>view.setUint32(72+i*4,v,true));
  return encoded({v:3,meshes:[{name:'0',color:null,pos:[0,9],nrm:[36,9],idx:[72,3],fac:[84,2],face_sources:[[{op:'source',src:'part.rs'}]]}]},bytes);
}
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const node = (name, bytes, transform) => ({name,asset:hash(bytes),entries:[{name,color:[.2,.3,.4]}],transform});

test('completed parts arrive while a neighboring object is pending or unavailable', async () => {
  const a=object(3),b=object(7);let release;
  const slow=new Promise(resolve=>{release=resolve;});
  const original=globalThis.fetch;
  globalThis.fetch=async url=>{if(String(url).includes(hash(a)))return new Response(a);await slow;return new Response('unavailable',{status:503});};
  try {
    const arrived=[];let finished=false;
    const pending=resolveScene(encoded({v:4,meshes:[node('left',a),node('right',b)]}),{onPart:(n)=>arrived.push(n.name)}).then(value=>{finished=true;return value;});
    await new Promise(resolve=>setImmediate(resolve));
    assert.deepEqual(arrived,['left']);assert.equal(finished,false);
    release();const result=await pending;
    assert.deepEqual(result.meshes.map(m=>m.name),['left']);assert.equal(result.errors.length,1);
    assert.equal(result.meshes[0].brep_faces[0].sources[0].src,'part.rs');
  } finally {globalThis.fetch=original;}
});

test('instances reuse downloaded geometry and place reflected triangles consistently',async()=>{
  const a=object(11);let calls=0;const original=globalThis.fetch;
  globalThis.fetch=async()=>{calls++;return new Response(a);};
  try {
    const first=node('first',a),second=node('second',a,[[-1,0,0,5],[0,1,0,3],[0,0,1,2]]);
    const result=await resolveScene(encoded({v:4,meshes:[first,second]}));
    assert.equal(calls,1);assert.equal(result.meshes[0].attributes.position.array[0],11);
    assert.deepEqual([...result.meshes[1].attributes.position.array.slice(0,3)],[-6,3,2]);
    assert.deepEqual([...result.meshes[1].index.array],[0,2,1]);
    const again=await resolveScene(encoded({v:4,meshes:[second]}));assert.equal(calls,1);
    assert.equal(again.meshes[0].name,'second');
    assert.equal(again.meshes[0],result.meshes[1]);
  } finally {globalThis.fetch=original;}
});
