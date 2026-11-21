/* Starforge v4 editing core. All edits are FICTIONAL ONLY.
 * The durable object is authoritative for AI-originated changes; observational
 * catalogues in KV are never writable through MCP mutation tools.
 * License: MIT for Starforge-authored integration code; upstream SSE remains GPLv3.
 */
export const KINDS=Object.freeze(["planet","moon","asteroid_belt","trojan_cloud","kuiper_analogue","comet_cloud","deep_sky","civilization","station","ring","debris_disk","star","star_system"]);
const ALLOWED_FIELDS=new Set(["name","description","host_star_id","parent_id","orbit_au","eccentricity","inclination_deg","mass_earth","radius_earth","temperature_k","density","seed","notes","color","moon_count","age_gyr","metallicity","disk_mass","dynamical_history","semi_major_axis_au","ra_deg","dec_deg","distance_ly","x_pc","y_pc","z_pc","spectral_class","luminosity_solar"]);
const NUMERIC={orbit_au:[.00001,1000000],semi_major_axis_au:[.00001,1000000],eccentricity:[0,.98],inclination_deg:[0,180],mass_earth:[0,1000000],radius_earth:[0,100000],temperature_k:[0,100000],density:[0,1],moon_count:[0,200],age_gyr:[0,14],metallicity:[-3,1],disk_mass:[0,1],dynamical_history:[0,1],ra_deg:[0,360],dec_deg:[-90,90],distance_ly:[.00001,1000000000],x_pc:[-100000000,100000000],y_pc:[-100000000,100000000],z_pc:[-100000000,100000000],luminosity_solar:[0,100000000]};
const LIMIT_OBJECTS=500,MAX_JSON=1800000,MAX_HISTORY=20;
const fail=(status,message,extra={})=>Object.assign(new Error(message),{status,...extra});
const text=(value,name,limit=150)=>{if(typeof value!=="string"||!value.trim()||value.length>limit)throw fail(422,"Invalid "+name);return value.trim()};
function safeRecord(obj){if(!obj||typeof obj!=="object"||Array.isArray(obj))throw fail(422,"Expected object");if(Object.keys(obj).some(k=>["__proto__","constructor","prototype"].includes(k)))throw fail(422,"Unsafe property");return obj}
function cleanAttributes(raw){
 const obj=safeRecord(raw||{}),out={};
 if(Object.keys(obj).length>24)throw fail(422,"Too many properties");
 for(const [k,v] of Object.entries(obj)){
  if(!ALLOWED_FIELDS.has(k))throw fail(422,"Field not editable: "+k);
  if(v===null){out[k]=null;continue}
  if(NUMERIC[k]){
   if(typeof v!=="number"||!Number.isFinite(v)||v<NUMERIC[k][0]||v>NUMERIC[k][1])throw fail(422,"Invalid "+k);
   if(k==="moon_count"&&!Number.isInteger(v))throw fail(422,"moon_count must be an integer");
   out[k]=v;
  }else out[k]=text(v,k,k==="description"||k==="notes"?1000:160);
 }
 return out;
}
export function normalizeCreate(data){
 const a=safeRecord(data),kind=text(a.kind,"kind",60);
 if(!KINDS.includes(kind))throw fail(422,"Unsupported fictional kind");
 const name=text(a.name,"name",120);
 const attrs=cleanAttributes(a.attributes||{});
 let host=a.host_star_id==null?null:text(a.host_star_id,"host_star_id",150);
 if(!["deep_sky","civilization","star","star_system"].includes(kind)&&!host)throw fail(422,"Host star ID required");
 if(["deep_sky","star","star_system"].includes(kind)&&host)throw fail(422,"deep_sky cannot be disguised as a catalog star");
 return {id:"user:"+crypto.randomUUID(),kind,name,host_star_id:host,
   attributes:attrs,origin:"SIMULATED",source:"TYPINGMIND_MCP_WRITE",schema_version:"starforge.user_object.v1",
   created_at:new Date().toISOString(),updated_at:new Date().toISOString()};
}
export function normalizePatch(data){
 const x=safeRecord(data),p=safeRecord(x.patch);
 if(!Object.keys(p).length)throw fail(422,"Empty patch");
 const keys=new Set(["name","attributes"]);
 if(Object.keys(p).some(k=>!keys.has(k)))throw fail(422,"ID, kind, origin and provenance are immutable");
 const next={};
 if(p.name!==undefined)next.name=text(p.name,"name",120);
 if(p.attributes!==undefined)next.attributes=cleanAttributes(p.attributes);
 return next;
}
export function initialOverlay(){return{revision:0,user_objects:[],generated_systems:[],simulated_deep_positions:[],
  history:[],updated_at:null,last_action:null,request_ids:[]}}
function updateState(input,payload){
 const s=structuredClone(input||initialOverlay());
 s.user_objects??=[];s.generated_systems??=[];s.simulated_deep_positions??=[];s.history??=[];s.request_ids??=[];
 if(s.user_objects.length>LIMIT_OBJECTS)throw fail(422,"Too many objects");
 const p=safeRecord(payload),action=p.action,now=new Date().toISOString();
 let result={};
 if(action==="create"){
  const x=normalizeCreate(p.data);
  if(s.user_objects.length>=LIMIT_OBJECTS)throw fail(422,"User object limit reached");
  if(s.user_objects.some(v=>v.id===x.id))throw fail(409,"Duplicate ID");
  s.user_objects.push(x);result={object:x};
 }else if(action==="update"){
  const id=text(p.id,"id",180);
  if(!id.startsWith("user:"))throw fail(403,"Only user-created fictional objects are editable");
  const pos=s.user_objects.findIndex(x=>x.id===id);if(pos<0)throw fail(404,"Fictional object not found");
  const upd=normalizePatch(p.data);
  const old=s.user_objects[pos];
  const obj={...old,...upd,attributes:{...old.attributes,...(upd.attributes||{})},updated_at:now};
  s.user_objects[pos]=obj;result={object:obj,previous:old};
 }else if(action==="delete"){
  const id=text(p.id,"id",180);
  if(!id.startsWith("user:"))throw fail(403,"Cannot delete catalogue data");
  const pos=s.user_objects.findIndex(x=>x.id===id);if(pos<0)throw fail(404,"Fictional object not found");
  const removed=s.user_objects.splice(pos,1)[0];result={deleted:id,previous:removed};
 }else if(action==="generate"){
  const m=safeRecord(p.data);
  if(m.origin!=="CATALOG_STAR_WITH_SIMULATED_ENVIRONMENT"||m.schema_version!=="starforge.exosystem.v3"||!Array.isArray(m.realConfirmedPlanets)||!Array.isArray(m.simulatedPlanets)||!Array.isArray(m.regions))throw fail(422,"Invalid generator provenance");
  if(JSON.stringify(m).length>220000)throw fail(422,"System model too large");
  if(m.simulatedPlanets.some(x=>x.source!=="SIMULATED")||m.regions.some(x=>x.source!=="SIMULATED"))throw fail(422,"Generator attempted to modify observations");
  const at=s.generated_systems.findIndex(x=>x.starId===m.starId);
  if(at>=0)s.generated_systems[at]=m;else{if(s.generated_systems.length>=20)s.generated_systems.shift();s.generated_systems.push(m)}
  result={star_name:m.starName,planet_count:m.planetCount,regions:m.regions.length,seed:m.seed};
 }else if(action==="synthetic_position"){
  const d=safeRecord(p.data);
  if(d.source!=="SIMULATED_DISTANCE"||d.reality!=="FICTIONAL_SCENARIO"||
   ![d.raDeg,d.decDeg,d.distanceLy,d.xPc,d.yPc,d.zPc].every(x=>Number.isFinite(x))||
   d.raDeg<0||d.raDeg>=360||Math.abs(d.decDeg)>90||d.distanceLy<=0)throw fail(422,"Invalid fictional position");
  const obj={...d,updated_at:now};
  const at=s.simulated_deep_positions.findIndex(x=>x.id===d.id);
  if(at>=0)s.simulated_deep_positions[at]=obj;else{
   if(s.simulated_deep_positions.length>=1500)throw fail(422,"Too many fictional positions");
   s.simulated_deep_positions.push(obj);
  }result={id:d.id,distanceLy:d.distanceLy,source:d.source};
 }else if(action==="restore"){
  const past=safeRecord(p.data);
  if(!Array.isArray(past.user_objects)||!Array.isArray(past.generated_systems)||!Array.isArray(past.simulated_deep_positions))throw fail(422,"Invalid restoration");
  s.user_objects=structuredClone(past.user_objects);s.generated_systems=structuredClone(past.generated_systems);
  s.simulated_deep_positions=structuredClone(past.simulated_deep_positions);
  result={restored:true,objects:s.user_objects.length};
 }else throw fail(422,"Unsupported edit action");
 s.revision=(input?.revision||0)+1;
 s.updated_at=now;s.last_action=action;
 s.history=[...(input?.history||[]),{revision:s.revision,action,time:now,object_id:result.object?.id||result.deleted||result.star_name||result.id||null}].slice(-MAX_HISTORY);
 return {state:s,result:{...result,revision:s.revision,updated_at:now}};
}
function response(body,status=200){return new Response(JSON.stringify(body),{status,headers:{"content-type":"application/json","cache-control":"no-store"}})}
export class EditGate {
 constructor(ctx,env){this.ctx=ctx;this.env=env}
 async fetch(request){
  const url=new URL(request.url),path=url.pathname;
  try {
   if(path==="/state"&&request.method==="GET"){
    const state=await this.ctx.storage.get("current")||initialOverlay();
    return response(state);
   }
   if(path==="/mutate"&&request.method==="POST"){
    const p=await request.json();
    if(!p||typeof p!=="object"||typeof p.action!=="string")throw fail(400,"Invalid mutation");
    if(!Number.isInteger(p.expected_revision)||p.expected_revision<0)throw fail(422,"expected_revision must be a non-negative integer");
    const out=await this.ctx.storage.transaction(async tx=>{
      const old=await tx.get("current")||initialOverlay();
      if(old.revision!==p.expected_revision)throw fail(409,"Revision conflict",{current_revision:old.revision});
      const {state,result}=updateState(old,p);
      if(JSON.stringify(state).length>MAX_JSON)throw fail(413,"Edit overlay exceeds capacity");
      await tx.put("version:"+old.revision,{user_objects:old.user_objects,generated_systems:old.generated_systems,simulated_deep_positions:old.simulated_deep_positions});
      if(old.revision>=MAX_HISTORY)await tx.delete("version:"+(old.revision-MAX_HISTORY));
      await tx.put("current",state);
      return result;
    });
    return response({ok:true,...out});
   }
   if(path==="/version"&&request.method==="GET"){
    const i=Number(url.searchParams.get("revision"));
    if(!Number.isInteger(i)||i<0)throw fail(422,"Invalid revision");
    const current=await this.ctx.storage.get("current")||initialOverlay();
    if(i===current.revision)return response({revision:i,state:current});
    const past=await this.ctx.storage.get("version:"+i);
    return past?response({revision:i,state:past}):response({error:"Revision not retained"},404);
   }
   return response({error:"Not found"},404);
  }catch(e){return response({error:String(e.message||e),current_revision:e.current_revision},e.status||500)}
 }
}
export function mergeOverlay(snapshot,overlay){
 const base=snapshot&&typeof snapshot==="object"?structuredClone(snapshot):null;
 if(!base)return {available:false,...overlay};
 const o=overlay||initialOverlay();
 base.user_objects=structuredClone(o.user_objects||[]);
 const gen=new Map((base.generated_systems||[]).map(x=>[String(x.starId),x]));
 for(const x of o.generated_systems||[])gen.set(String(x.starId),structuredClone(x));
 base.generated_systems=[...gen.values()];
 const deep=new Map((base.simulated_deep_positions||[]).map(x=>[String(x.id),x]));
 for(const x of o.simulated_deep_positions||[])deep.set(String(x.id),structuredClone(x));
 base.simulated_deep_positions=[...deep.values()];
 base.edit_revision=o.revision||0;base.edit_updated_at=o.updated_at||null;
 return base;
}
