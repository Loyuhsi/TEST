import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {dirname,join} from "node:path";
import {fileURLToPath} from "node:url";
import {webcrypto} from "node:crypto";
import worker,{EditGate} from "../bridge/worker.js";
import vm from "node:vm";
if(!globalThis.crypto)globalThis.crypto=webcrypto;
const root=dirname(dirname(fileURLToPath(import.meta.url)));
const data={window:{}};vm.runInNewContext(readFileSync(join(root,"data.js"),"utf8"),data);
const C=data.window.SF_DATA;
const storageMap=new Map();
const storage={
 async get(k){return structuredClone(storageMap.get(k))},
 async put(k,v){storageMap.set(k,structuredClone(v))},
 async delete(k){storageMap.delete(k)},
 async transaction(fn){return await fn(this)}
};
const edit=new EditGate({storage},{});
const stub={fetch:(url,opts)=>edit.fetch(url instanceof Request?url:new Request(url,opts))};
const kvMap=new Map();
const env={
 READ_TOKEN:"read-"+("r".repeat(45)),WRITE_TOKEN:"write-"+("w".repeat(45)),ADMIN_TOKEN:"admin-"+("a".repeat(45)),
 ALLOWED_ORIGINS:"https://starforge-unified-v3-loyuhsi.pages.dev",
 STARFORGE_KV:{async get(k){return kvMap.get(k)||null},async put(k,v){kvMap.set(k,v)}},
 EDIT_GATE:{idFromName:n=>n,get:id=>stub},
 SSD_GATE:{idFromName:n=>n,get:id=>{throw Error("JPL not tested")}}
};
const uri="https://starforge-worker.test";
function request(path,method="GET",token,body){
 const headers={"Content-Type":"application/json"};if(token)headers.Authorization="Bearer "+token;
 return new Request(uri+path,{method,headers,body:body===undefined?undefined:JSON.stringify(body)});
}
async function raw(path,method,token,payload){return worker.fetch(request(path,method,token,payload),env)}
let n=0;async function call(token,name,args={}){
 const out=await raw("/mcp","POST",token,{jsonrpc:"2.0",id:++n,method:"tools/call",params:{name,arguments:args}});
 const j=await out.json();
 return {http:out.status,raw:j,answer:j.result?.content?.[0]?.text?JSON.parse(j.result.content[0].text):null,error:j.result?.isError||!!j.error};
}
async function listed(token){
 const out=await raw("/mcp","POST",token,{jsonrpc:"2.0",id:++n,method:"tools/list"});
 return (await out.json()).result.tools;
}
const snapshot={schema_version:"starforge.unified.v2",version:"4-test",
 exported_at:new Date().toISOString(),selection:{mode:"system",star_name:"Proxima Centauri"},
 stars:C.stars.map(x=>({...x,id:"hyg:"+x.id})),observed_planets:C.exoplanets,
 solar_bodies:C.solar,solar_small_bodies:C.small,
 deep_sky:[...C.deep,{id:"UNKNOWN_CLUSTER",n:"未定距離星團",en:"Unknown Cluster",type:"OPEN_CLUSTER",ra:120,dec:23,ly:null,source:"MOCK_CATALOG",precision:"none"}],
 simulated_planets:[],generated_systems:[],simulated_deep_positions:[],user_objects:[]};
assert.equal((await raw("/api/snapshot","POST",env.WRITE_TOKEN,snapshot)).status,200);
const roles=[
 [env.READ_TOKEN,16,false,false],
 [env.WRITE_TOKEN,20,true,false],
 [env.ADMIN_TOKEN,23,true,true]
];
for(const [token,count,writable,admin] of roles){
 const defs=await listed(token);assert.equal(defs.length,count);
 assert.equal(defs.some(d=>d.name==="create_simulated_object"),writable);
 assert.equal(defs.some(d=>d.name==="delete_simulated_object"),admin);
}
assert.equal((await raw("/mcp","POST",null,{jsonrpc:"2.0",id:3,method:"tools/list"})).status,401);
const a0=await call(env.READ_TOKEN,"get_edit_state");
assert.equal(a0.answer.revision,0);
assert.equal(a0.answer.permissions.write,false);
let hidden=await call(env.READ_TOKEN,"create_simulated_object",{expected_revision:0,kind:"planet",name:"應拒絕"});
assert(hidden.error&&!hidden.answer,"READ_TOKEN must never create");
let created=await call(env.WRITE_TOKEN,"create_simulated_object",{
 expected_revision:0,kind:"planet",name:"AI 創建的晨星",host_star_id:"hyg:70666",
 attributes:{orbit_au:.125,eccentricity:.03,mass_earth:1.4,radius_earth:1.1,description:"虛構宜居行星"}
});
assert.equal(created.error,false);assert(created.answer.object.id.startsWith("user:"));
assert.equal(created.answer.object.origin,"SIMULATED");
assert.equal(created.answer.revision,1);
const id=created.answer.object.id;
let clash=await call(env.WRITE_TOKEN,"update_simulated_object",{
 expected_revision:0,id,patch:{name:"舊版本覆寫"}
});
assert(clash.error&&/conflict/i.test(clash.answer.error),"stale write must fail");
const invalid=await call(env.WRITE_TOKEN,"update_simulated_object",{
 expected_revision:1,id,patch:{source:"NASA_CONFIRMED"}
});
assert(invalid.error,"provenance must be immutable");
const updated=await call(env.WRITE_TOKEN,"update_simulated_object",{
 expected_revision:1,id,patch:{name:"AI 新晨星",attributes:{orbit_au:.14,temperature_k:290}}
});
assert.equal(updated.answer.revision,2);
assert.equal(updated.answer.object.attributes.orbit_au,.14);
const catalogMutation=await call(env.WRITE_TOKEN,"update_simulated_object",{
 expected_revision:2,id:"hyg:70666",patch:{name:"偽造"}
});
assert(catalogMutation.error,"observational HYG star must not be editable");
const fakeHost=await call(env.WRITE_TOKEN,"create_simulated_object",{
 expected_revision:2,kind:"planet",name:"未知母星",host_star_id:"hyg:nonexistent",attributes:{}
});
assert(fakeHost.error,"host star must exist");
const generated=await call(env.WRITE_TOKEN,"generate_system_environment",{
 expected_revision:2,star_name:"Proxima Centauri",seed:"typingmind-original-v4",disk_mass:.77,dynamical_history:.22,max_bodies:5
});
assert.equal(generated.error,false);
assert.equal(generated.answer.revision,3);
assert(generated.answer.planet_count>0);
const fictional=await call(env.WRITE_TOKEN,"create_fictional_deep_position",{
 expected_revision:3,object_id:"UNKNOWN_CLUSTER",seed:"nebula-fiction-v4"
});
assert.equal(fictional.error,false);
assert.equal(fictional.answer.revision,4);
const badDistance=await call(env.WRITE_TOKEN,"create_fictional_deep_position",{
 expected_revision:4,object_id:"M42",seed:"not-allowed"
});
assert(badDistance.error,"measured deep-sky position must stay unchanged");
const mergedResp=await raw("/api/snapshot","GET",env.WRITE_TOKEN);
assert.equal(mergedResp.status,200);const merged=await mergedResp.json();
assert.equal(merged.stars.length,47);
assert.equal(merged.observed_planets.length,17);
assert.equal(merged.user_objects.length,1);
assert.equal(merged.generated_systems.length,1);
assert.equal(merged.simulated_deep_positions.length,1);
assert.equal(merged.edit_revision,4);
const userList=await call(env.READ_TOKEN,"list_user_objects",{kind:"planet"});
assert.equal(userList.answer.results[0].name,"AI 新晨星");
const system=await call(env.READ_TOKEN,"get_star_system",{name:"Proxima Centauri"});
assert.equal(system.answer.user_objects.length,1);
const writeCanDelete=await call(env.WRITE_TOKEN,"delete_simulated_object",{id,expected_revision:4});
assert(writeCanDelete.error,"ADMIN_TOKEN required for delete");
const pre=await call(env.ADMIN_TOKEN,"prepare_destructive_change",{action:"delete",target_id:id,expected_revision:4});
assert.equal(pre.error,false);
assert(pre.answer.confirmation_token.length===64);
const noPhrase=await call(env.ADMIN_TOKEN,"delete_simulated_object",{
 id,expected_revision:4,expires_at:pre.answer.expires_at,confirmation_token:pre.answer.confirmation_token,
 confirmation_phrase:"yes"
});
assert(noPhrase.error,"strong confirmation phrase required");
const deleted=await call(env.ADMIN_TOKEN,"delete_simulated_object",{
 id,expected_revision:4,expires_at:pre.answer.expires_at,confirmation_token:pre.answer.confirmation_token,
 confirmation_phrase:pre.answer.confirmation_phrase
});
assert.equal(deleted.error,false);assert.equal(deleted.answer.revision,5);
const preRestore=await call(env.ADMIN_TOKEN,"prepare_destructive_change",{
 action:"restore",target_revision:4,expected_revision:5
});
assert.equal(preRestore.error,false);
const restored=await call(env.ADMIN_TOKEN,"restore_edit_revision",{
 target_revision:4,expected_revision:5,expires_at:preRestore.answer.expires_at,
 confirmation_token:preRestore.answer.confirmation_token,confirmation_phrase:preRestore.answer.confirmation_phrase
});
assert.equal(restored.error,false);assert.equal(restored.answer.revision,6);
assert.equal((await call(env.READ_TOKEN,"list_user_objects")).answer.results.length,1);
const history=await call(env.READ_TOKEN,"get_change_history",{limit:20});
assert(history.answer.history.length>=6);
const health=await (await raw("/api/health")).json();
assert.equal(health.editing,true);
console.log("PASS v4 bidirectional MCP: 16 READ / 20 WRITE / 23 ADMIN tools; 6 edits + restore, strict observational immutability, optimistic revision, HMAC deletion approval, merged UI snapshot.");
