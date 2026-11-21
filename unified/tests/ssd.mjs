import assert from 'node:assert/strict';
import {SSDGate} from '../bridge/worker.js';
const durable=new Map(),cache=new Map(),requests=[];
const ctx={storage:{async get(k){return durable.get(k)},async put(k,v){durable.set(k,v)}}};
const env={JPL_CONTACT:'https://example.com/maintenance',STARFORGE_KV:{async get(k){return cache.get(k)},async put(k,v){cache.set(k,v)}}};
let active=0,maxActive=0;
const originalFetch=globalThis.fetch;
globalThis.fetch=async(url,options)=>{
 const u=new URL(url);requests.push({url:u,at:Date.now(),headers:options.headers});maxActive=Math.max(maxActive,++active);
 await new Promise(r=>setTimeout(r,8));active--;
 const result=u.pathname.endsWith('sbdb.api')?{signature:{source:'NASA/JPL SBDB',version:'1.3'},object:{des:'1',fullname:'1 Ceres'},orbit:{epoch:'2461200.5',elements:[]}}:{signature:{source:'NASA/JPL Horizons API'},result:'header\n$$SOE\n2461365.5 = 2026-Nov-21 TDB\n X=1 Y=2 Z=3\n$$EOE'};
 return new Response(JSON.stringify(result));
};
function query(gate,kind,params){return gate.fetch(new Request('https://ssd.internal/query',{method:'POST',body:JSON.stringify({kind,params})})).then(async r=>({status:r.status,body:await r.json()}))}
try{
 const gate=new SSDGate(ctx,env);
 const [first,second]=await Promise.all([query(gate,'sbdb',{name:'Ceres'}),query(gate,'sbdb',{name:'Ceres'})]);
 assert.equal(first.status,200);assert.equal(first.body.starforge_jpl.cache,'MISS');
 assert.equal(second.body.starforge_jpl.cache,'HIT');assert.equal(requests.length,1,'duplicate queries must be coalesced after the serialized cache check');
 assert.equal(first.body.orbit.epoch,'2461200.5');
 const vector=await query(gate,'horizons',{body:'399',date:'2026-11-21'});
 assert.equal(vector.status,200);assert.equal(vector.body.timescale,'TDB');assert.equal(vector.body.center,'solar-system barycenter');
 assert.equal(vector.body.reference_epoch,'J2000');assert(vector.body.not_for_navigation);
 assert.equal(maxActive,1);assert(requests[1].at-requests[0].at>=1550);
 assert(requests[0].headers['User-Agent'].includes(env.JPL_CONTACT));
 const rebooted=new SSDGate(ctx,env);
 assert.equal((await query(rebooted,'sbdb',{name:'Ceres'})).body.starforge_jpl.cache,'HIT');
 assert.equal(requests.length,2,'KV cache persists across a DO restart');
 await query(rebooted,'horizons',{body:'499',date:'2026-11-21'});
 assert(requests[2].at-requests[1].at>=1550,'rate spacing persists across restarts');
 assert.equal((await query(gate,'unknown',{})).status,400);
 console.log('PASS JPL gate: serialized and deduplicated requests, durable spacing, KV cache, identifiable User-Agent, explicit TDB/J2000/barycentric vectors.');
}finally{globalThis.fetch=originalFetch}
