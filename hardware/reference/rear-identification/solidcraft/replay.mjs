// This manual replay builds the historical Rust recipe and publishes the isolated chip comparison.
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync,spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url)),repo=path.resolve(root,'../../../..');
const args=process.argv.slice(2),command=args[0],run=path.resolve(args[args.indexOf('--out')+1]||'');
if(!args.includes('--out'))throw new Error('--out requires a temporary run directory');
fs.mkdirSync(run,{recursive:true});
const inputs=JSON.parse(fs.readFileSync(path.join(root,'inputs.json'))),web=path.join(repo,'web/public/solidcraft-lab/identification');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const git=(...args)=>execFileSync('git',args,{cwd:repo,encoding:'utf8'});
function timed(program,args,log){const start=Date.now(),result=spawnSync(program,args,{cwd:repo,encoding:'utf8',env:{...process.env,CARGO_BUILD_JOBS:'2'},maxBuffer:16*1024*1024});fs.writeFileSync(path.join(run,log+'.log'),(result.stdout||'')+(result.stderr||''));if(result.status!==0)throw new Error(`${program} failed; see ${log}.log`);return {started_at:new Date(start).toISOString(),finished_at:new Date().toISOString(),wall_ms:Date.now()-start};}
function rust(variant){
  const dir=path.join(run,'rust-baseline');fs.mkdirSync(path.join(dir,'src'),{recursive:true});
  const layout=path.join(run,'above-core.json');if(!fs.existsSync(layout))fs.writeFileSync(layout,git('show',inputs.source_revision+':hardware/manifold-layout/above-core.json'));
  const words=git('show',inputs.source_revision+':hardware/printed-parts/enclosure/rear-identification/label-words.json');fs.writeFileSync(path.join(dir,'src/label-words.json'),words);
  const revision=variant==='before'?inputs.source_revision:inputs.change_revision;
  const source=git('show',revision+':hardware/printed-parts/enclosure/rear-identification/rear_identification.rs');
  const started=new Date().toISOString();fs.writeFileSync(path.join(dir,'src/main.rs'),source.replace('"hardware/manifold-layout/above-core.json"',JSON.stringify(layout)));
  const toml='[package]\nname="identification-rust-replay"\nversion="0.1.0"\nedition="2024"\n[workspace]\n[dependencies]\nanyhow="1"\nserde={version="1",features=["derive"]}\nserde_json={version="1.0.154",features=["float_roundtrip"]}\n'+Object.entries({'hsm-bulkhead-ring-numbers':'tools/hsm/bulkhead-ring-numbers','hsm-enclosure-components':'tools/hsm/enclosure-components','hsm-kernel':'tools/hsm/kernel'}).map(([name,dir])=>`${name}={path=${JSON.stringify(path.join(repo,dir))}}\n`).join('');
  fs.writeFileSync(path.join(dir,'Cargo.toml'),toml);
  const build=timed('python3',['tools/run.py','--','cargo','build','--release','--manifest-path',path.join(dir,'Cargo.toml'),'--target-dir','tools/hsm/target'],'rust-'+variant+'-compile');
  const generation=timed(path.join(repo,'tools/hsm/target/release/identification-rust-replay'),[path.join(run,'rust-'+variant)],'rust-'+variant+'-generate');
  const report={purpose:'This observation replays the historical recipe using frozen inputs and the current hsm kernel.',variant,recipe_revision:revision,recipe_sha256:sha(source),kernel_checkout:git('rev-parse','HEAD').trim(),source_edit_at:started,compile:build,generation,edit_to_outputs_ms:Date.now()-Date.parse(started),scope:variant==='before'?'Baseline setup; excluded from the edit comparison.':'Exact historical source change, compilation and complete printable/display outputs. Shared-host process times include waits.'};
  fs.writeFileSync(path.join(run,'rust-'+variant+'-timing.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}
function publish(){
  fs.mkdirSync(path.join(web,'assets'),{recursive:true});fs.mkdirSync(path.join(web,'designs'),{recursive:true});
  const before=JSON.parse(fs.readFileSync(path.join(root,'native/before.json')));
  const catalog={purpose:'Complete native and Rust chips replay the approved historical side clearance.',source_revision:inputs.source_revision,change_revision:inputs.change_revision,parts:inputs.parts.map((p,i)=>({key:p.key,label:p.key.startsWith('flavor')?p.key.toUpperCase():p.word,transform:before.occurrences[i].transform})),variants:{before:{width:inputs.nominal_width},after:{width:inputs.nominal_width-2*inputs.clearance_after}},models:{native:{},rust:{}}};
  for(const implementation of ['native','rust'])for(const variant of ['before','after']){
    const source=path.join(run,implementation+'-'+variant);if(!fs.existsSync(source))continue;
    const target=path.join(web,'assets',implementation+'-'+variant);fs.mkdirSync(target,{recursive:true});const parts={},downloads=[];
    for(const part of inputs.parts){
      const file=implementation==='native'?part.key+'.3mf':'rear-label-'+part.key+'.step.mesh';const bytes=fs.readFileSync(path.join(source,file));fs.writeFileSync(path.join(target,file),bytes);
      const url='/solidcraft-lab/identification/assets/'+implementation+'-'+variant+'/'+file;
      parts[part.key]={kind:implementation==='native'?'native-export':'rust-payload',label:implementation==='native'?'SolidCraft export':'Rust production payload',url:url+'?v='+sha(bytes).slice(0,16),sha256:sha(bytes),bytes:bytes.length};
      const stl=implementation==='native'?part.key+'.stl':'rear-label-'+part.key+'.stl';fs.copyFileSync(path.join(source,stl),path.join(target,stl));downloads.push({label:part.key.toUpperCase()+' · fused STL',url:'/solidcraft-lab/identification/assets/'+implementation+'-'+variant+'/'+stl});
    }
    const model={parts,downloads};
    if(implementation==='native'){
      const design=variant+'.json';fs.copyFileSync(path.join(root,'native',design),path.join(web,'designs',design));model.design='/solidcraft-lab/identification/designs/'+design;
      fs.copyFileSync(path.join(source,'complete-set.3mf'),path.join(target,'complete-set.3mf'));downloads.unshift({label:'Complete multicolor set · 3MF',url:'/solidcraft-lab/identification/assets/'+implementation+'-'+variant+'/complete-set.3mf'});
    }
    catalog.models[implementation][variant]=model;
  }
  fs.writeFileSync(path.join(web,'catalog.json'),JSON.stringify(catalog,null,2)+'\n');
  const files=['inputs.json',...fs.readdirSync(path.join(root,'lettering')).map(f=>'lettering/'+f),...['before','after'].flatMap(v=>['json','sc'].map(ext=>'native/'+v+'.'+ext)).filter(f=>fs.existsSync(path.join(root,f)))];
  if(fs.existsSync(path.join(root,'README.md')))files.push('README.md');
  const archive=path.join(web,'project.zip');if(fs.existsSync(archive))fs.unlinkSync(archive);execFileSync('zip',['-q',archive,...files],{cwd:root});
  console.log('Published isolated chip replay from the recorded outputs.');
}
if(command==='rust-before')rust('before');else if(command==='rust-after')rust('after');else if(command==='publish')publish();else throw new Error('rust-before | rust-after | publish --out RUN');
