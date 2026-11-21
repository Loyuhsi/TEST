import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import vm from "node:vm";
import worker from "../bridge/worker.js";
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
const html=readFileSync(join(root,"index.html"),"utf8");
assert(html.includes("./app.js")&&html.includes("./data.js"));
const storage=new Map();
const env={
 READ_TOKEN:"read-"+("r".repeat(45)),WRITE_TOKEN:"write-"+("w".repeat(45)),ALLOWED_ORIGINS:"https://atlas.example.com",
 STARFORGE_KV:{async get(k){return storage.get(k)||null},async put(k,v){storage.set(k,v)}}
};
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
assert.equal(t.length,10);assert(t.some(x=>x.name==="get_imported_sse_reference"));
const snapshot={schema_version:"starforge.unified.v2",version:"2-test",exported_at:new Date().toISOString(),selection:{mode:"system",star_name:"Proxima Centauri"},
 stars:C.stars.map(x=>({...x,id:"hyg:"+x.id})),observed_planets:C.exoplanets,solar_bodies:C.solar,
 solar_small_bodies:C.small,deep_sky:C.deep,simulated_planets:[],imported_sse:{nodes:[]}};
const upload=await call("/api/snapshot","POST",env.WRITE_TOKEN,snapshot);
assert.equal(upload.status,200);
assert.equal((await call("/api/snapshot","GET",env.WRITE_TOKEN)).status,401);
assert.equal((await call("/api/snapshot","GET",env.READ_TOKEN)).status,200);
let latest=await call("/mcp","POST",env.READ_TOKEN,{jsonrpc:"2.0",id:3,method:"tools/call",params:{name:"get_latest_universe",arguments:{}}});
let info=JSON.parse((await latest.json()).result.content[0].text);
assert.equal(info.counts.stars,47);assert.equal(info.counts.deep_sky,13);
let system=await call("/mcp","POST",env.READ_TOKEN,{jsonrpc:"2.0",id:4,method:"tools/call",params:{name:"get_star_system",arguments:{}}});
assert.equal(JSON.parse((await system.json()).result.content[0].text).confirmed_planets.length,2);
let imported=await call("/mcp","POST",env.READ_TOKEN,{jsonrpc:"2.0",id:5,method:"tools/call",params:{name:"get_imported_sse_reference",arguments:{}}});
assert.equal(JSON.parse((await imported.json()).result.content[0].text).available,true);
const deny=await call("/mcp","POST",env.WRITE_TOKEN,{jsonrpc:"2.0",id:6,method:"tools/list"});
assert.equal(deny.status,401);
console.log("PASS: 47 stars / 17 confirmed planets / 20 small bodies / 13 deep-sky objects, 10 MCP tools, protected read/write and original SSE import.");
