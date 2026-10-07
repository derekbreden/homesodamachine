// Execute the exact canonical pin helper and connector JSX declarations.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');
const root = process.cwd();
const ts = require(require.resolve('typescript', {paths:[path.join(root,'hardware/pcb/pcba')]}));
const parts = fs.readFileSync('hardware/pcb/pcba/parts.tsx','utf8');
const pcba = fs.readFileSync('hardware/pcb/pcba/pcba.tsx','utf8');
const names=['J1','J2','J3','J4','J5','J6','J7','J8','J9','J11','J13'];
const declarations=['ulnOUT','WAFER_PITCH','WAFER_OPEN','WAFER_PIN1_WEST'].map(name=>{
  const line=parts.split('\n').find(s=>new RegExp(`^(export )?const ${name}\\b`).test(s));
  if(!line)throw new Error(`Missing canonical declaration ${name}`);
  return line;
});
const start=parts.indexOf('export const jstPins =');
const end=parts.indexOf('\n}\n',start);
if(start<0||end<0)throw new Error('Missing canonical jstPins');
const elements=names.map(name=>{
  const line=pcba.split('\n').find(s=>new RegExp(`^const ${name}El\\b`).test(s));
  if(!line)throw new Error(`Missing canonical placement ${name}`);
  return line;
});
const source=[...declarations,parts.slice(start,end+2),...elements,
  `export const connectors=Object.fromEntries([${names.map(n=>`${n}El`).join(',')}].map(el=>[el.name,{...el,...jstPins(el)}]));`].join('\n');
const compiled=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,
  target:ts.ScriptTarget.ES2020,jsx:ts.JsxEmit.React,jsxFactory:'jsx'},fileName:'canonical-pins.tsx'}).outputText;
const context={exports:{},Math,Jst:'Jst',jsx:(_,props)=>props};vm.runInNewContext(compiled,context);
process.stdout.write(JSON.stringify({connectors:context.exports.connectors,
  extracted_source_sha256:crypto.createHash('sha256').update(source).digest('hex'),
  source_sha256:{'hardware/pcb/pcba/parts.tsx':crypto.createHash('sha256').update(parts).digest('hex'),
    'hardware/pcb/pcba/pcba.tsx':crypto.createHash('sha256').update(pcba).digest('hex')},
  method:'Execute exact canonical TypeScript declarations, jstPins helper and J1–J9/J11/J13 JSX props after TypeScript transpilation, without board build.'}));
