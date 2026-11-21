// Starforge Secure Bridge v4 — Cloudflare Worker + KV + two Durable Objects.
import {EditGate,mergeOverlay} from "./edit-engine.js";
import "../exo-engine.js";
export {EditGate};
// Deploy with Wrangler; NEVER place READ_TOKEN or WRITE_TOKEN in GitHub.
// Single global Durable Object serializes JPL requests. JPL fair use:
// https://ssd-api.jpl.nasa.gov/doc/
const MAX_BYTES=3000000;
function okJSON(obj,status=200,extra={}){return new Response(JSON.stringify(obj),{status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store",...extra}})}
function no(method){return okJSON({error:"Method not allowed"},405,{"allow":method})}
const testAuth=(request,token)=>{
 if(!token||token.length<24)return false;
 const h=request.headers.get("authorization")||"";
 const provided=h.startsWith("Bearer ")?h.slice(7):(request.headers.get("x-starforge-key")||"");
 return provided.length===token.length&&provided===token;
};
function CORS(request,env){
 const o=request.headers.get("Origin");
 if(!o)return {};
 const allowed=(env.ALLOWED_ORIGINS||"").split(",").map(x=>x.trim()).filter(Boolean);
 if(!allowed.includes(o))return {};
 return {"access-control-allow-origin":o,"vary":"Origin","access-control-allow-methods":"GET,POST,OPTIONS","access-control-allow-headers":"Authorization,Content-Type,X-Starforge-Key,Mcp-Protocol-Version,Mcp-Session-Id","access-control-max-age":"600"};
}
function pack(r,request,env){
 const headers=new Headers(r.headers);
 for(const [k,v] of Object.entries(CORS(request,env)))headers.set(k,v);
 headers.set("x-content-type-options","nosniff");
 return new Response(r.body,{status:r.status,statusText:r.statusText,headers});
}
function err(status,detail){return okJSON({error:String(detail)},status)}
function bounds(s,n=80){const v=String(s||"").trim();if(!v||v.length>n)throw Error("Invalid input");return v}
function asInt(v,lo,hi,def){let n=Number(v);return Number.isInteger(n)&&n>=lo&&n<=hi?n:def}
async function getBaseSnapshot(env){const raw=await env.STARFORGE_KV.get("snapshot:latest");return raw?JSON.parse(raw):null}
async function getOverlay(env){
 if(!env.EDIT_GATE)throw Error("EDIT_GATE Durable Object binding required for bidirectional editing");
 const stub=env.EDIT_GATE.get(env.EDIT_GATE.idFromName("starforge-v4-user-edits"));
 const res=await stub.fetch("https://starforge-edit.internal/state");
 if(!res.ok)throw Error("Edit state not available");
 return res.json();
}
async function getSnapshot(env){
 const base=await getBaseSnapshot(env);
 if(!env.EDIT_GATE)return base;
 return mergeOverlay(base,await getOverlay(env));
}
function authorizationRole(request,env){
 if(testAuth(request,env.ADMIN_TOKEN))return "admin";
 if(testAuth(request,env.WRITE_TOKEN))return "write";
 if(testAuth(request,env.READ_TOKEN))return "read";
 return null;
}
const canWrite=role=>role==="write"||role==="admin";
async function mutateEdit(env,action,expected_revision,payload){
 if(!Number.isInteger(expected_revision)||expected_revision<0)throw Error("expected_revision must be an integer ≥ 0; call get_edit_state first");
 if(!env.EDIT_GATE)throw Error("EDIT_GATE Durable Object is not deployed");
 const stub=env.EDIT_GATE.get(env.EDIT_GATE.idFromName("starforge-v4-user-edits"));
 const response=await stub.fetch("https://starforge-edit.internal/mutate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({action,expected_revision,...payload})});
 const result=await response.json();
 if(!response.ok)throw Error("Edit rejected (HTTP "+response.status+"): "+result.error+(result.current_revision===undefined?"":"; latest revision="+result.current_revision));
 return result;
}
async function loadVersion(env,revision){
 const stub=env.EDIT_GATE.get(env.EDIT_GATE.idFromName("starforge-v4-user-edits"));
 const resp=await stub.fetch("https://starforge-edit.internal/version?revision="+encodeURIComponent(revision));
 const j=await resp.json();if(!resp.ok)throw Error(j.error||"Revision not retained");return j;
}
function toolsForRole(role){
 return tools.filter(t=>!t._role||t._role==="read"||t._role==="write"&&canWrite(role)||t._role==="admin"&&role==="admin")
   .map(({_role,...tool})=>tool);
}
const EDIT_WRITE_NAMES=new Set(["create_simulated_object","update_simulated_object","generate_system_environment","create_fictional_deep_position"]);
const EDIT_ADMIN_NAMES=new Set(["prepare_destructive_change","delete_simulated_object","restore_edit_revision"]);
function safeString(v,limit=120){if(typeof v!=="string"||!v.trim()||v.length>limit)throw Error("Invalid string argument");return v.trim();}
function boundedNumber(v,min,max,defaultValue){if(v===undefined||v===null)return defaultValue;const n=Number(v);if(!Number.isFinite(n)||n<min||n>max)throw Error("Number outside allowed range");return n}
async function signApproval(env,action,target,revision,expiry){
 const key=await crypto.subtle.importKey("raw",new TextEncoder().encode(env.ADMIN_TOKEN),{name:"HMAC",hash:"SHA-256"},false,["sign"]);
 const data=new TextEncoder().encode("starforge-v4|"+action+"|"+target+"|"+revision+"|"+expiry);
 const bytes=new Uint8Array(await crypto.subtle.sign("HMAC",key,data));
 return [...bytes].map(x=>x.toString(16).padStart(2,"0")).join("");
}
async function verifyApproval(env,action,target,revision,expiry,token){
 if(!env.ADMIN_TOKEN||Date.now()>expiry||expiry>Date.now()+180000||!Number.isSafeInteger(expiry))throw Error("Approval expired or invalid");
 const expected=await signApproval(env,action,target,revision,expiry);
 if(typeof token!=="string"||token.length!==expected.length)throw Error("Invalid approval token");
 let mismatch=0;for(let i=0;i<token.length;i++)mismatch|=token.charCodeAt(i)^expected.charCodeAt(i);
 if(mismatch!==0)throw Error("Approval token mismatch");
}
function publicSummary(s){
 if(!s||s.available===false)return {available:false,message:"No snapshot has been synced yet"};
 const sel=s.selection||{};
 return {available:true,schema_version:s.schema_version,exported_at:s.exported_at,selection:sel,counts:{stars:s.stars?.length||0,confirmed_exoplanets:s.observed_planets?.length||0,solar_bodies:s.solar_bodies?.length||0,small_bodies:s.solar_small_bodies?.length||0,deep_sky:s.deep_sky?.length||0,simulated_planets:s.simulated_planets?.length||0,user_objects:s.user_objects?.length||0,generated_systems:s.generated_systems?.length||0,simulated_deep_positions:s.simulated_deep_positions?.length||0},source_note:s.note}
}
function byQuery(list,key,q){
 q=String(q||"").trim().toLowerCase();
 if(!q)return list.slice(0,25);
 return list.filter(x=>String(x[key]||x.name||x.n||x.id||"").toLowerCase().includes(q)).slice(0,50)
}
const tools=[
 {name:"get_latest_universe",description:"讀取星海工坊最新同步快照摘要，或返回所選天體與計數。",inputSchema:{type:"object",properties:{include_full:{type:"boolean",description:"是否回傳完整快照（最大 1.5 MB）"}},additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"search_stars",description:"在已同步 HYG/NASA 恆星中搜尋名稱或 HIP ID。",inputSchema:{type:"object",properties:{query:{type:"string"},limit:{type:"integer",minimum:1,maximum:50}},required:["query"],additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"get_star_system",description:"讀取恆星及已確認、虛構的系外行星，真實與模擬明確區分。",inputSchema:{type:"object",properties:{name:{type:"string",description:"恆星名稱，預設選取的恆星"}},additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"list_solar_small_bodies",description:"列出太陽系小天體與分類。JPL 快照與近似示意資料明確區分。",inputSchema:{type:"object",properties:{group:{type:"string",description:"MBA/TNO/COMET/NEO/CENTAUR/TROJAN/DETACHED"},limit:{type:"integer",minimum:1,maximum:200}},additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"get_small_body",description:"取得已同步的小天體詳細參數、資料曆元與精度。",inputSchema:{type:"object",properties:{name:{type:"string"}},required:["name"],additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"list_deep_sky_objects",description:"列出銀河內的非恆星天體，如星雲、星團、脈衝星及黑洞。",inputSchema:{type:"object",properties:{type:{type:"string"},limit:{type:"integer",minimum:1,maximum:200}},additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"get_deep_sky_object",description:"查詢深空天體的估計距離、天球座標、來源。",inputSchema:{type:"object",properties:{name:{type:"string"}},required:["name"],additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"list_generated_systems",description:"取得依恆星物理先驗生成的系外環境清單。",inputSchema:{type:"object",properties:{limit:{type:"integer",minimum:1,maximum:20}},additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"get_generated_system",description:"讀取指定恆星的種子、已確認行星、虛構行星、衛星、環、小天體帶和遠距彗星雲。",inputSchema:{type:"object",properties:{star_name:{type:"string"}},additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"list_simulated_deep_positions",description:"取得有資料來源與虛構標籤的深空天體 3D 場景座標。",inputSchema:{type:"object",properties:{limit:{type:"integer",minimum:1,maximum:200}},additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"get_imported_sse_reference",description:"讀取使用者匯入的原版 SSE JSON 摘要；資料保持原樣，不會與真實星表混淆。",inputSchema:{type:"object",properties:{include_raw:{type:"boolean"}},additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"lookup_jpl_sbdb",description:"透過具節流的 JPL SSD Bridge 查單一已知小天體真實資料，不會直接從聊天調用 NASA。",inputSchema:{type:"object",properties:{name:{type:"string",maxLength:64}},required:["name"],additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"get_horizons_vector",description:"取得指定太陽系天體的 Horizons 日心狀態向量文字資料，限有限白名單。",inputSchema:{type:"object",properties:{body:{type:"string",description:"例如 399=地球、499=火星"},date:{type:"string",description:"YYYY-MM-DD"}},required:["body","date"],additionalProperties:false},annotations:{readOnlyHint:true}},
 {_role:"read",name:"get_edit_state",description:"讀取雙向 AI 編輯版本與物件數量；每次修改前先取得 revision。",inputSchema:{type:"object",properties:{},additionalProperties:false},annotations:{readOnlyHint:true}},
 {_role:"read",name:"list_user_objects",description:"列出由 TypingMind/星海工坊建立的虛構天體，支援按種類、母星篩選；含 user: ID 供更新使用。",inputSchema:{type:"object",properties:{kind:{type:"string"},host_star_id:{type:"string"},limit:{type:"integer",minimum:1,maximum:100}},additionalProperties:false},annotations:{readOnlyHint:true}},
 {_role:"read",name:"get_change_history",description:"取得最近的 AI 編輯版本和動作紀錄，含可供版本復原的 revision。",inputSchema:{type:"object",properties:{limit:{type:"integer",minimum:1,maximum:20}},additionalProperties:false},annotations:{readOnlyHint:true}},
 {_role:"write",name:"create_simulated_object",description:"【寫入】建立虛構行星、衛星、行星環、小天體帶、特洛伊群、類柯伊伯帶、彗星雲、文明、基地或深空虛構天體。僅寫入 user_objects，不修改 NASA/HYG/JPL 觀測值。先執行 get_edit_state。",inputSchema:{type:"object",properties:{expected_revision:{type:"integer",minimum:0},kind:{type:"string",enum:["planet","moon","asteroid_belt","trojan_cloud","kuiper_analogue","comet_cloud","deep_sky","civilization","station","ring","debris_disk"]},name:{type:"string",minLength:1,maxLength:120},host_star_id:{type:"string",description:"例如 hyg:70666；deep_sky 可省略"},attributes:{type:"object",description:"只允許物理/描述欄位，例 {orbit_au:2.4,eccentricity:0.08,mass_earth:1,description:'...'}"}},required:["expected_revision","kind","name"],additionalProperties:false},annotations:{readOnlyHint:false,destructiveHint:false,idempotentHint:false}},
 {_role:"write",name:"update_simulated_object",description:"【寫入】只修改先前建立的 user: 虛構天體的名稱或許可物理參數，無法更動 ID/來源/真實觀測值。先執行 get_edit_state。",inputSchema:{type:"object",properties:{expected_revision:{type:"integer",minimum:0},id:{type:"string"},patch:{type:"object",properties:{name:{type:"string"},attributes:{type:"object"}},additionalProperties:false}},required:["expected_revision","id","patch"],additionalProperties:false},annotations:{readOnlyHint:false,destructiveHint:false,idempotentHint:false}},
 {_role:"write",name:"generate_system_environment",description:"【寫入】依所選真實恆星的 HYG/NASA 資料與種子重建多樣化虛構行星、衛星、環、原行星盤及彗星雲。真實行星保持 NASA 來源，不會覆寫。",inputSchema:{type:"object",properties:{expected_revision:{type:"integer",minimum:0},star_name:{type:"string"},seed:{type:"string",maxLength:100},disk_mass:{type:"number",minimum:0.05,maximum:1},metallicity:{type:"number",minimum:-1.5,maximum:0.6},dynamical_history:{type:"number",minimum:0.01,maximum:1},max_bodies:{type:"integer",minimum:1,maximum:20}},required:["expected_revision","star_name","seed"],additionalProperties:false},annotations:{readOnlyHint:false,destructiveHint:false,idempotentHint:false}},
 {_role:"write",name:"create_fictional_deep_position",description:"【寫入】在保留真實赤經赤緯的前提下，對無可信距離的深空天體創建可重現的虛構 3D XYZ 座標，標示 SIMULATED_DISTANCE。",inputSchema:{type:"object",properties:{expected_revision:{type:"integer",minimum:0},object_id:{type:"string"},seed:{type:"string",maxLength:100}},required:["expected_revision","object_id","seed"],additionalProperties:false},annotations:{readOnlyHint:false,destructiveHint:false,idempotentHint:false}},
 {_role:"admin",name:"prepare_destructive_change",description:"【管理員確認第一步】預覽刪除虛構物件或還原歷史版本，產生 2 分鐘有效的帶簽章確認碼。沒有 ADMIN_TOKEN 無法使用。",inputSchema:{type:"object",properties:{action:{type:"string",enum:["delete","restore"]},target_id:{type:"string"},target_revision:{type:"integer",minimum:0},expected_revision:{type:"integer",minimum:0}},required:["action","expected_revision"],additionalProperties:false},annotations:{readOnlyHint:true}},
 {_role:"admin",name:"delete_simulated_object",description:"【危險操作】只刪除 user: 自訂虛構天體，必須提供當前版本、prepare_destructive_change 確認碼與明確 DELETE <id> 字句；不可刪觀測天體。",inputSchema:{type:"object",properties:{id:{type:"string"},expected_revision:{type:"integer",minimum:0},expires_at:{type:"integer"},confirmation_token:{type:"string"},confirmation_phrase:{type:"string"}},required:["id","expected_revision","expires_at","confirmation_token","confirmation_phrase"],additionalProperties:false},annotations:{readOnlyHint:false,destructiveHint:true,idempotentHint:false}},
 {_role:"admin",name:"restore_edit_revision",description:"【危險操作】還原最近的 AI 編輯 overlay（保留真實星表）；需管理員限時確認碼與目前版本，復原操作也保留歷史。",inputSchema:{type:"object",properties:{target_revision:{type:"integer",minimum:0},expected_revision:{type:"integer",minimum:0},expires_at:{type:"integer"},confirmation_token:{type:"string"},confirmation_phrase:{type:"string"}},required:["target_revision","expected_revision","expires_at","confirmation_token","confirmation_phrase"],additionalProperties:false},annotations:{readOnlyHint:false,destructiveHint:true,idempotentHint:false}}
];
function cleanName(name){return bounds(name,64).replace(/[^\w \-+.'()/]/g,"").slice(0,64)}
async function requestJPL(env,kind,params,cacheKey){
 const cached=await env.STARFORGE_KV.get(cacheKey);
 if(cached)return JSON.parse(cached);
 if(!env.SSD_GATE)throw Error("JPL Durable Object binding is missing. Configure wrangler first.");
 const id=env.SSD_GATE.idFromName("jpl-ssd-serialized-global");
 const stub=env.SSD_GATE.get(id);
 const resp=await stub.fetch(new Request("https://ssd-gate.internal/query",{method:"POST",body:JSON.stringify({kind,params})}));
 const result=await resp.json();
 if(!resp.ok||result.error)throw Error(result.error||"JPL returned "+resp.status);
 await env.STARFORGE_KV.put(cacheKey,JSON.stringify(result),{expirationTtl:kind==="horizons"?21600:86400});
 return result;
}
async function SBDB(env,name){
 const value=cleanName(name);if(!value)throw Error("Invalid body");
 return await requestJPL(env,"sbdb",{name:value},"ssd:body:"+value.toLowerCase());
}
const ALLOWED_HORIZONS=new Set(["10","199","299","301","399","499","599","699","799","899"]);
async function Horizons(env,body,date){
 if(!ALLOWED_HORIZONS.has(String(body)))throw Error("Body not in safe ID allowlist");
 if(!/^\d{4}-\d{2}-\d{2}$/.test(String(date)))throw Error("Date must be YYYY-MM-DD");
 const d=new Date(date+"T00:00:00Z");if(Number.isNaN(d.getTime())||d.toISOString().slice(0,10)!==date)throw Error("Invalid date");
 if(d.getUTCFullYear()<1800||d.getUTCFullYear()>2200)throw Error("Date out of allowed range");
 return await requestJPL(env,"horizons",{body:String(body),date},"ssd:horizons:"+body+":"+date);
}
async function callTool(env,name,args){
 const s=await getSnapshot(env),selection=s?.selection||{};
 switch(name){
 case "get_latest_universe":return args.include_full?s?JSON.stringify(s).length<1500000?s:{...publicSummary(s),warning:"Too large for full response"}:{available:false}:publicSummary(s);
 case "search_stars":if(!s)return {available:false};{const q=String(args.query||"").toLowerCase(),limit=asInt(args.limit,1,50,20);return {query:q,results:(s.stars||[]).filter(x=>String(x.n||"").toLowerCase().includes(q)||String(x.h||"").toLowerCase().includes(q)||String(x.zh||"").includes(q)).slice(0,limit)}} 
 case "get_star_system":if(!s)return {available:false};{const q=String(args.name||selection.star_name||"").toLowerCase();const st=(s.stars||[]).find(x=>String(x.n||"").toLowerCase()===q)||null;const norm=v=>String(v||"").toLowerCase().replace(/[^a-z0-9]/g,"");const k=norm(q)==="proximacentauri"?"proximacen":norm(q)==="pollux"?"hd62509":norm(q);const planets=(s.observed_planets||[]).filter(p=>norm(p.h)===k);const sim=(s.simulated_planets||[]).filter(p=>p.hostId===st?.id);const user=(s.user_objects||[]).filter(o=>o.host_star_id===st?.id);return {star:st,confirmed_planets:planets,simulated_planets:sim,user_objects:user,note:"Confirmed planets from NASA; simulated planets are creative."}}
 case "list_solar_small_bodies":if(!s)return {available:false};return{results:(s.solar_small_bodies||[]).filter(x=>!args.group||x.group===args.group).slice(0,asInt(args.limit,1,200,50))};
 case "get_small_body":if(!s)return{available:false};return(s.solar_small_bodies||[]).find(x=>String(x.name||"").toLowerCase()===String(args.name||"").toLowerCase()||x.zh===args.name||x.id===args.name)||{found:false};
 case "list_deep_sky_objects":if(!s)return{available:false};return{results:(s.deep_sky||[]).filter(x=>!args.type||x.type===args.type).slice(0,asInt(args.limit,1,200,50))};
 case "get_deep_sky_object":if(!s)return{available:false};return(s.deep_sky||[]).find(x=>x.id===args.name||x.n===args.name||String(x.en||"").toLowerCase()===String(args.name||"").toLowerCase())||{found:false};
 case "list_generated_systems":if(!s)return{available:false};return (s.generated_systems||[]).slice(0,asInt(args.limit,1,20,18)).map(g=>({starName:g.starName,starId:g.starId,seed:g.seed,observedCount:g.knownCount,simulatedCount:g.planetCount,regionCount:g.regions?.length||0,outerCloud:!!g.outerCometCloud,source:g.origin}));
 case "get_generated_system":if(!s)return{available:false};{const q=String(args.star_name||selection.star_name||"").toLowerCase();return(s.generated_systems||[]).find(g=>String(g.starName||"").toLowerCase()===q)||{found:false,starName:q}}
 case "list_simulated_deep_positions":if(!s)return{available:false};return{source:"SIMULATED_DISTANCE",warning:"Not observed or scientifically measured 3D positions",results:(s.simulated_deep_positions||[]).slice(0,asInt(args.limit,1,200,100))};
 case "get_imported_sse_reference":if(!s)return{available:false};{const j=s.imported_sse||null;if(!j)return{available:false};const text=JSON.stringify(j);return args.include_raw&&text.length<=150000?{available:true,data:j}:{available:true,topLevelKeys:Object.keys(j),bytes:text.length,raw_available:text.length<=150000,note:"Unmodified original SSE import; not validated as HYG or NASA observations."}}
 case "lookup_jpl_sbdb":return SBDB(env,args.name);
 case "get_horizons_vector":return Horizons(env,args.body,args.date);
 default:throw Error("Unknown tool "+name);
 }
}
async function callEditTool(env,name,args,role){
 if(!role)throw Error("Authentication required");
 if(name==="get_edit_state"){
  const state=await getOverlay(env);
  return {revision:state.revision,updated_at:state.updated_at,last_action:state.last_action,
    fictional_objects:state.user_objects?.length||0,generated_systems:state.generated_systems?.length||0,
    fictional_deep_positions:state.simulated_deep_positions?.length||0,
    permissions:{read:true,write:canWrite(role),admin:role==="admin"},
    note:"Observation records remain immutable through MCP. Supply expected_revision for every mutation."};
 }
 if(name==="list_user_objects"){
  const state=await getOverlay(env),limit=asInt(args.limit,1,100,50);
  return {revision:state.revision,results:(state.user_objects||[]).filter(x=>(!args.kind||x.kind===args.kind)&&(!args.host_star_id||x.host_star_id===args.host_star_id)).slice(0,limit)};
 }
 if(name==="get_change_history"){
  const state=await getOverlay(env);
  return {revision:state.revision,history:(state.history||[]).slice(-asInt(args.limit,1,20,15))};
 }
 if(EDIT_WRITE_NAMES.has(name)&&!canWrite(role))throw Error("WRITE_TOKEN (or ADMIN_TOKEN) required");
 if(EDIT_ADMIN_NAMES.has(name)&&role!=="admin")throw Error("ADMIN_TOKEN required; destructive operation unavailable");
 const s=await getBaseSnapshot(env);
 if(!s)throw Error("No baseline star catalogue yet. Use trusted Starforge frontend to sync an initial snapshot first.");
 const revision=args.expected_revision;
 if(!Number.isInteger(revision)||revision<0)throw Error("Call get_edit_state first; expected_revision is required");
 if(name==="create_simulated_object"){
  const kind=safeString(args.kind,60),host=args.host_star_id;
  if(kind!=="deep_sky"&&kind!=="civilization"){
   if(typeof host!=="string"||!(s.stars||[]).some(x=>String(x.id)===host)||(s.stars||[]).filter(x=>String(x.id)===host).length!==1){
    // NASA exoplanet host records may be stored only as planet host names in the base snapshot.
    if(!String(host||"").startsWith("nasa:")||!(s.observed_planets||[]).some(x=>"nasa:"+x.h===host))throw Error("Host star must exist in HYG/NASA catalogue; inspect search_stars or get_latest_universe");
   }
  }
  return mutateEdit(env,"create",revision,{data:{kind,name:args.name,host_star_id:host,attributes:args.attributes||{}}});
 }
 if(name==="update_simulated_object")return mutateEdit(env,"update",revision,{id:args.id,data:{patch:args.patch}});
 if(name==="generate_system_environment"){
  const name=safeString(args.star_name,150),seed=safeString(args.seed,100);
  let star=(s.stars||[]).find(x=>x.n?.toLowerCase()===name.toLowerCase()||String(x.id)===name);
  if(!star){
   const p=(s.observed_planets||[]).find(x=>x.h?.toLowerCase()===name.toLowerCase());
   if(p)star={id:"nasa:"+p.h,n:p.h,s:"",lum:null};
  }
  if(!star)throw Error("Star absent from synced HYG/NASA catalogue. Cannot invent a star's observed properties.");
  const norm=x=>String(x||"").toLowerCase().replace(/[^a-z0-9]/g,"");
  const match=norm(star.n)==="proximacentauri"?"proximacen":norm(star.n)==="pollux"?"hd62509":norm(star.n);
  const real=(s.observed_planets||[]).filter(p=>norm(p.h)===match);
  const engine=globalThis.StarforgeExoV3;
  if(!engine?.generate)throw Error("Starforge exosystem generator was not bundled");
  const model=engine.generate(star,real,{seed,diskMass:boundedNumber(args.disk_mass,.05,1,.5),
    metallicity:boundedNumber(args.metallicity,-1.5,.6,0),
    dynamicalHistory:boundedNumber(args.dynamical_history,.01,1,.35),
    maxBodies:boundedNumber(args.max_bodies,1,20,8)});
  return mutateEdit(env,"generate",revision,{data:model});
 }
 if(name==="create_fictional_deep_position"){
  const id=safeString(args.object_id,180),seed=safeString(args.seed,100);
  const obj=(s.deep_sky||[]).find(x=>String(x.id)===id||String(x.n)===id);
  if(!obj)throw Error("Deep-sky catalogue object not found");
  if(obj.ly!==null&&obj.ly!==undefined&&Number(obj.ly)>0)throw Error("Real distance exists; simulated distance creation is blocked for this object");
  const engine=globalThis.StarforgeExoV3;
  if(!engine?.imaginedDeepPosition)throw Error("Deep-sky generator was not bundled");
  const fictional=engine.imaginedDeepPosition(obj,{seed});
  return mutateEdit(env,"synthetic_position",revision,{data:fictional});
 }
 const overlay=await getOverlay(env);
 if(overlay.revision!==revision)throw Error("Revision changed; use get_edit_state and retry");
 if(name==="prepare_destructive_change"){
  const action=safeString(args.action,20);
  if(!["delete","restore"].includes(action))throw Error("Only delete/restore can be prepared");
  const target=action==="delete"?safeString(args.target_id,180):String(args.target_revision);
  let description;
  if(action==="delete"){
   if(!target.startsWith("user:"))throw Error("Cannot delete catalog objects");
   const obj=(overlay.user_objects||[]).find(x=>x.id===target);
   if(!obj)throw Error("Fictional object not found");
   description="Delete fictional object: "+obj.name+" ("+obj.kind+").";
  }else{
   if(!Number.isInteger(args.target_revision)||args.target_revision<0)throw Error("Invalid target revision");
   const old=await loadVersion(env,args.target_revision);
   description="Restore simulated overlay from revision "+old.revision+"; current simulated edits may be replaced.";
  }
  const expiry=Date.now()+120000,token=await signApproval(env,action,target,revision,expiry);
  const phrase=action==="delete"?"DELETE "+target:"RESTORE "+target;
  return {action,target,expected_revision:revision,expires_at:expiry,confirmation_token:token,
    confirmation_phrase:phrase,description,warning:"Requires explicit user approval before calling destructive tool. Expires in 2 minutes. Observed catalogue is never deleted."};
 }
 if(name==="delete_simulated_object"){
  const id=safeString(args.id,180);
  if(args.confirmation_phrase!=="DELETE "+id)throw Error("Explicit DELETE <id> confirmation required");
  await verifyApproval(env,"delete",id,revision,args.expires_at,args.confirmation_token);
  return mutateEdit(env,"delete",revision,{id});
 }
 if(name==="restore_edit_revision"){
  if(!Number.isInteger(args.target_revision)||args.target_revision<0)throw Error("Invalid target revision");
  const id=String(args.target_revision);
  if(args.confirmation_phrase!=="RESTORE "+id)throw Error("Explicit RESTORE <revision> confirmation required");
  await verifyApproval(env,"restore",id,revision,args.expires_at,args.confirmation_token);
  const saved=await loadVersion(env,args.target_revision);
  return mutateEdit(env,"restore",revision,{data:saved.state});
 }
 throw Error("Unknown edit tool");
}
async function handleMCP(request,env){
 const role=authorizationRole(request,env);
 if(!role)return err(401,"Valid READ_TOKEN, WRITE_TOKEN or ADMIN_TOKEN required");
 if(request.method==="GET")return no("POST, OPTIONS");
 if(request.method!=="POST")return no("POST, OPTIONS");
 let body;try{body=await request.json()}catch{return err(400,"Invalid JSON")};
 if(Array.isArray(body))return err(400,"MCP batch requests are not supported");
 const {id,method,params={}}=body;
 if(method==="notifications/initialized"||method?.startsWith("notifications/"))return new Response(null,{status:202});
 const success=result=>okJSON({jsonrpc:"2.0",id,result},200,{"mcp-protocol-version":"2025-06-18"});
 const failure=(code,message)=>okJSON({jsonrpc:"2.0",id,error:{code,message}},200);
 if(method==="initialize"){return success({protocolVersion:"2025-06-18",capabilities:{tools:{listChanged:false}},serverInfo:{name:"Starforge Unified Atlas MCP",version:"4.0.0"}})}
 if(method==="ping")return success({});
 if(method==="tools/list")return success({tools:toolsForRole(role)});
 if(method==="tools/call"){
  const name=params.name;try{
  if(!toolsForRole(role).some(t=>t.name===name))return failure(-32601,"Unknown or unauthorized tool");
  const ans=name==="get_edit_state"||name==="get_change_history"||EDIT_WRITE_NAMES.has(name)||EDIT_ADMIN_NAMES.has(name)?await callEditTool(env,name,params.arguments||{},role):await callTool(env,name,params.arguments||{});
  return success({content:[{type:"text",text:JSON.stringify(ans)}],isError:false});
  }catch(e){return success({content:[{type:"text",text:JSON.stringify({error:String(e.message||e)})}],isError:true})}
 }
 return failure(-32601,"Method not found");
}
async function route(request,env){
 const u=new URL(request.url),path=u.pathname;
 if(request.method==="OPTIONS"){
  const c=CORS(request,env);
  return Object.keys(c).length?new Response(null,{status:204,headers:c}):new Response(null,{status:403});
 }
 if(path==="/api/health")return okJSON({service:"Starforge Secure Bridge v4",status:"ok",mcp:"/mcp",ssd:!!env.SSD_GATE,editing:!!env.EDIT_GATE,write_configured:!!env.WRITE_TOKEN,admin_configured:!!env.ADMIN_TOKEN});
 if(path==="/mcp"||path==="/api/mcp")return handleMCP(request,env);
 if(path==="/api/snapshot"){
  if(request.method==="GET"){if(!authorizationRole(request,env))return err(401,"Read token required");return okJSON(await getSnapshot(env)||{available:false})}
  if(request.method!=="POST")return no("GET, POST, OPTIONS");
  if(!canWrite(authorizationRole(request,env)))return err(401,"Write token required");
  if(Number(request.headers.get("content-length"))>MAX_BYTES)return err(413,"Snapshot exceeds 3 MB");
  const raw=await request.text();if(raw.length>MAX_BYTES)return err(413,"Snapshot exceeds 3 MB");
  let data;try{data=JSON.parse(raw)}catch{return err(400,"Invalid JSON snapshot")};
  if(data.schema_version!=="starforge.unified.v2")return err(422,"Unsupported schema");
  for(const [k,max] of Object.entries({stars:8000,observed_planets:3000,solar_bodies:30,solar_small_bodies:500,deep_sky:1500,simulated_planets:500,generated_systems:20,simulated_deep_positions:1500})){if(!Array.isArray(data[k])||data[k].length>max)return err(422,"Invalid size "+k)}
  if((data.simulated_planets||[]).some(p=>p.origin!=="SIMULATED"))return err(422,"Invalid simulation label");
  if((data.simulated_deep_positions||[]).some(p=>p.source!=="SIMULATED_DISTANCE"||p.reality!=="FICTIONAL_SCENARIO"))return err(422,"Invalid fictional distance labels");
  if((data.generated_systems||[]).some(p=>p.origin!=="CATALOG_STAR_WITH_SIMULATED_ENVIRONMENT"||p.schema_version!=="starforge.exosystem.v3"))return err(422,"Invalid exosystem provenance");
  const updated_at=new Date().toISOString();
  await env.STARFORGE_KV.put("snapshot:latest",raw);
  await env.STARFORGE_KV.put("snapshot:meta",JSON.stringify({updated_at,version:data.version,bytes:raw.length}));
  return okJSON({ok:true,updated_at,version:data.version});
 }
 if(path==="/api/ssd/body"){
  if(!authorizationRole(request,env))return err(401,"Bridge key required");
  if(request.method!=="GET")return no("GET, OPTIONS");
  try{return okJSON(await SBDB(env,u.searchParams.get("name")))}catch(e){return err(502,e.message)}
 }
 if(path==="/api/ssd/horizons"){
  if(!testAuth(request,env.READ_TOKEN)&&!testAuth(request,env.WRITE_TOKEN))return err(401,"Bridge key required");
  try{return okJSON(await Horizons(env,u.searchParams.get("body"),u.searchParams.get("date")))}catch(e){return err(502,e.message)}
 }
 return err(404,"Not found");
}
export default {
 async fetch(request,env){try{return pack(await route(request,env),request,env)}catch(e){return pack(err(500,"Bridge internal error"),request,env)}}
};
// Single globally addressed Durable Object: serialized requests and 1600ms spacing.
export class SSDGate {
 constructor(ctx,env){this.ctx=ctx;this.env=env;this.queue=Promise.resolve();this.lastSent=0}
 async fetch(request){
  if(request.method!=="POST")return err(405,"POST only");
  let resolveNext;const next=new Promise(r=>{resolveNext=r}),prior=this.queue;this.queue=next;
  await prior.catch(()=>{});
  try{
   const item=await request.json();const now=Date.now();const delay=Math.max(0,1600-(now-this.lastSent));if(delay)await new Promise(r=>setTimeout(r,delay));
   let u;if(item.kind==="sbdb"){u=new URL("https://ssd-api.jpl.nasa.gov/sbdb.api");u.searchParams.set("sstr",cleanName(item.params.name));}
   else if(item.kind==="horizons"){
    const body=item.params.body,date=item.params.date,nextDate=new Date(Date.parse(date+"T00:00:00Z")+86400000).toISOString().slice(0,10);
    u=new URL("https://ssd.jpl.nasa.gov/api/horizons.api");
    const params={format:"json",COMMAND:"'"+body+"'",MAKE_EPHEM:"'YES'",EPHEM_TYPE:"'VECTORS'",CENTER:"'500@0'",START_TIME:"'"+date+"'",STOP_TIME:"'"+nextDate+"'",STEP_SIZE:"'1 d'",OUT_UNITS:"'AU-D'",REF_PLANE:"'ECLIPTIC'",VEC_TABLE:"'2'"};
    for(const [k,v] of Object.entries(params))u.searchParams.set(k,v);
   }else{return err(400,"Unknown kind")}
   this.lastSent=Date.now();
   const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),13000);
   if(!this.env.JPL_CONTACT||String(this.env.JPL_CONTACT).length<5){clearTimeout(timeout);return err(503,"JPL_CONTACT is required for a compliant identifiable User-Agent")}
   const agent="StarforgeUnifiedAtlas/3.0 (+contact: "+String(this.env.JPL_CONTACT).slice(0,160)+")";
   try{const response=await fetch(u.toString(),{headers:{Accept:"application/json","User-Agent":agent},signal:controller.signal});const raw=await response.text();if(!response.ok)return err(502,"JPL "+response.status);if(raw.length>1200000)return err(502,"JPL response too large");
    let result;try{result=JSON.parse(raw)}catch{return err(502,"Invalid JPL payload")}
    if(item.kind==="horizons"){if(typeof result.result!=="string"||!result.result.includes("$$SOE"))return err(502,"Horizons did not return vector data");const part=result.result.split("$$SOE")[1].split("$$EOE")[0].trim();result={source:"JPL Horizons",kind:"VECTORS",body:item.params.body,date:item.params.date,frame:"ECLIPTIC",center:"solar-system barycenter",units:"AU-D",vector_table_excerpt:part.slice(0,2500),not_for_navigation:true}}
    return okJSON(result);
   }finally{clearTimeout(timeout)}
  }catch(e){return err(502,"SSD backend temporarily unavailable: "+String(e.message||e))}
  finally{resolveNext()}
 }
}
