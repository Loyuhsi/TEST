import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import vm from "node:vm";
import worker,{EditGate} from "../bridge/worker.js";
const root=dirname(dirname(fileURLToPath(import.meta.url)));
const source=readFileSync(join(root,"data.js"),"utf8");
const sandbox={window:{}};vm.runInNewContext(source,sandbox);
const C=sandbox.window.SF_DATA;
assert.equal(C.stars.length,47);
assert.equal(C.exoplanets.length,17);
assert.equal(C.solar.length,12);
assert.equal(C.small.length,20);
assert.equal(C.deep.length,13);
assert.equal(C.small.filter(x=>x.source==="JPL_SBDB_SNAPSHOT").length,6);
assert(C.deep.some(x=>x.type==="BLACK_HOLE"));
assert(C.deep.some(x=>x.type==="PULSAR"));
const app=readFileSync(join(root,"app.js"),"utf8");
new Function(app);
const importerFunctions=app.slice(app.indexOf("function parseNGCLine("),app.indexOf("async function loadOpenNGC(){"));
assert(importerFunctions.startsWith("function parseNGCLine("));
const funcs=new Function(importerFunctions+"\nreturn {parseNGCLine,ngcRA,ngcDec};")();
const sample="NGC0197;OCl;00:39:13.4;+08:47:24;Psc";
const values=funcs.parseNGCLine(sample,";");
assert.equal(values.length,5);
assert.equal(values[0],"NGC0197");
assert.equal(values[1],"OCl");
assert(Math.abs(funcs.ngcRA("00:39:13.4")-9.80583)<0.01);
assert(Math.abs(funcs.ngcDec("-05:23:30")+5.391667)<0.01);
assert(app.includes("ly:null,source:\"OpenNGC CC BY-SA 4.0\""),"Do not synthesize 3D distances from sky coordinates");
assert(app.includes("if(deepProjection===\"distance\"&&!knownDistance&&!fake)continue"),"Unknown distances must either remain hidden or be separately labelled as simulated");

const engineScope={window:{}};vm.runInNewContext(readFileSync(join(root,"exo-engine.js"),"utf8"),engineScope);
const model=engineScope.window.StarforgeExoV3.generate({...C.stars[0],id:"hyg:"+C.stars[0].id},[],{seed:"test-v3"});
const samplePosition=engineScope.window.StarforgeExoV3.imaginedDeepPosition({id:"NoDistance",ra:83.822,dec:-5.39,type:"NEBULA",source:"OpenNGC"},{seed:"test"});
const html=readFileSync(join(root,"index.html"),"utf8");
assert(html.includes("./app.js")&&html.includes("./data.js"));
const storage=new Map();
const env={
 READ_TOKEN:"read-"+("r".repeat(45)),WRITE_TOKEN:"write-"+("w".repeat(45)),ALLOWED_ORIGINS:"https://atlas.example.com",
 STARFORGE_KV:{async get(k){return storage.get(k)||null},async put(k,v){storage.set(k,v)}}
};
const editStorage=new Map();
const edit=new EditGate({storage:{async get(k){return structuredClone(editStorage.get(k))},async put(k,v){editStorage.set(k,structuredClone(v))},async transaction(fn){return fn(this)}}},env);
env.EDIT_GATE={idFromName:x=>x,get:()=>({fetch:(url,opts)=>edit.fetch(new Request(url,opts))})};
const uri="https://worker.example.com";
const request=(path,method="GET",token=null,payload=null)=>{
 const headers={"content-type":"application/json"};if(token)headers.authorization="Bearer "+token;
 return new Request(uri+path,{method,headers,body:payload?JSON.stringify(payload):undefined});
};
async function call(path,method,token,payload){return worker.fetch(request(path,method,token,payload),env)}
assert.equal((await call("/api/health","GET")).status,200);
assert.equal((await call("/api/snapshot","GET")).status,401);
let init=await call("/mcp","POST",env.READ_TOKEN,{jsonrpc:"2.0",id:1,method:"initialize",params:{protocolVersion:"2025-06-18"}});
assert.equal(init.status,200);
assert.equal((await init.json()).result.serverInfo.name,"Starforge Unified Atlas MCP");
let tools=await call("/mcp","POST",env.READ_TOKEN,{jsonrpc:"2.0",id:2,method:"tools/list"});
let t=(await tools.json()).result.tools;
assert.equal(t.length,16);assert(t.every(x=>x.annotations?.readOnlyHint!==false),"READ tools must not mutate data");assert(t.some(x=>x.name==="get_generated_system"));assert(t.some(x=>x.name==="list_simulated_deep_positions"));assert(t.some(x=>x.name==="get_imported_sse_reference"));
const snapshot={schema_version:"starforge.unified.v2",version:"2-test",exported_at:new Date().toISOString(),selection:{mode:"system",star_name:"Proxima Centauri"},
 stars:C.stars.map(x=>({...x,id:"hyg:"+x.id})),observed_planets:C.exoplanets,solar_bodies:C.solar,
 solar_small_bodies:C.small,deep_sky:C.deep,simulated_planets:[],generated_systems:[model],simulated_deep_positions:[samplePosition],imported_sse:{nodes:[]}};
const upload=await call("/api/snapshot","POST",env.WRITE_TOKEN,snapshot);
assert.equal(upload.status,200);
assert.equal((await call("/api/snapshot","GET",env.WRITE_TOKEN)).status,200);
assert.equal((await call("/api/snapshot","GET",env.READ_TOKEN)).status,200);
let latest=await call("/mcp","POST",env.READ_TOKEN,{jsonrpc:"2.0",id:3,method:"tools/call",params:{name:"get_latest_universe",arguments:{}}});
let info=JSON.parse((await latest.json()).result.content[0].text);
assert.equal(info.counts.stars,47);assert.equal(info.counts.deep_sky,13);assert.equal(info.counts.generated_systems,1);assert.equal(info.counts.simulated_deep_positions,1);
let system=await call("/mcp","POST",env.READ_TOKEN,{jsonrpc:"2.0",id:4,method:"tools/call",params:{name:"get_star_system",arguments:{}}});
assert.equal(JSON.parse((await system.json()).result.content[0].text).confirmed_planets.length,2);
let imported=await call("/mcp","POST",env.READ_TOKEN,{jsonrpc:"2.0",id:5,method:"tools/call",params:{name:"get_imported_sse_reference",arguments:{}}});
assert.equal(JSON.parse((await imported.json()).result.content[0].text).available,true);
const generated=await call("/mcp","POST",env.READ_TOKEN,{jsonrpc:"2.0",id:7,method:"tools/call",params:{name:"get_generated_system",arguments:{star_name:model.starName}}});
assert.equal(JSON.parse((await generated.json()).result.content[0].text).schema_version,"starforge.exosystem.v3");
const simulatedDistance=await call("/mcp","POST",env.READ_TOKEN,{jsonrpc:"2.0",id:8,method:"tools/call",params:{name:"list_simulated_deep_positions",arguments:{}}});
assert.equal(JSON.parse((await simulatedDistance.json()).result.content[0].text).results[0].source,"SIMULATED_DISTANCE");
const deny=await call("/mcp","POST",env.WRITE_TOKEN,{jsonrpc:"2.0",id:6,method:"tools/list"});
assert.equal(deny.status,200);assert.equal((await deny.json()).result.tools.length,20);
console.log("PASS: 47 stars / 17 confirmed planets / 20 small bodies / 13 deep-sky objects, 16 READ MCP tools, 20 WRITE MCP tools, protected data and original SSE import.");
