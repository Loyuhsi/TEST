// Starforge Secure Bridge v2 — Cloudflare Worker + KV + Durable Object.
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
async function getSnapshot(env){const raw=await env.STARFORGE_KV.get("snapshot:latest");return raw?JSON.parse(raw):null}
function publicSummary(s){
 if(!s)return {available:false,message:"No snapshot has been synced yet"};
 const sel=s.selection||{};
 return {available:true,schema_version:s.schema_version,exported_at:s.exported_at,selection:sel,counts:{stars:s.stars?.length||0,confirmed_exoplanets:s.observed_planets?.length||0,solar_bodies:s.solar_bodies?.length||0,small_bodies:s.solar_small_bodies?.length||0,deep_sky:s.deep_sky?.length||0,simulated_planets:s.simulated_planets?.length||0},source_note:s.note}
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
 {name:"get_imported_sse_reference",description:"讀取使用者匯入的原版 SSE JSON 摘要；資料保持原樣，不會與真實星表混淆。",inputSchema:{type:"object",properties:{include_raw:{type:"boolean"}},additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"lookup_jpl_sbdb",description:"透過具節流的 JPL SSD Bridge 查單一已知小天體真實資料，不會直接從聊天調用 NASA。",inputSchema:{type:"object",properties:{name:{type:"string",maxLength:64}},required:["name"],additionalProperties:false},annotations:{readOnlyHint:true}},
 {name:"get_horizons_vector",description:"取得指定太陽系天體的 Horizons 日心狀態向量文字資料，限有限白名單。",inputSchema:{type:"object",properties:{body:{type:"string",description:"例如 399=地球、499=火星"},date:{type:"string",description:"YYYY-MM-DD"}},required:["body","date"],additionalProperties:false},annotations:{readOnlyHint:true}}
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
 case "get_star_system":if(!s)return {available:false};{const q=String(args.name||selection.star_name||"").toLowerCase();const st=(s.stars||[]).find(x=>String(x.n||"").toLowerCase()===q)||null;const norm=v=>String(v||"").toLowerCase().replace(/[^a-z0-9]/g,"");const k=norm(q)==="proximacentauri"?"proximacen":norm(q)==="pollux"?"hd62509":norm(q);const planets=(s.observed_planets||[]).filter(p=>norm(p.h)===k);const sim=(s.simulated_planets||[]).filter(p=>p.hostId===st?.id);return {star:st,confirmed_planets:planets,simulated_planets:sim,note:"Confirmed planets from NASA; simulated planets are creative."}}
 case "list_solar_small_bodies":if(!s)return {available:false};return{results:(s.solar_small_bodies||[]).filter(x=>!args.group||x.group===args.group).slice(0,asInt(args.limit,1,200,50))};
 case "get_small_body":if(!s)return{available:false};return(s.solar_small_bodies||[]).find(x=>String(x.name||"").toLowerCase()===String(args.name||"").toLowerCase()||x.zh===args.name||x.id===args.name)||{found:false};
 case "list_deep_sky_objects":if(!s)return{available:false};return{results:(s.deep_sky||[]).filter(x=>!args.type||x.type===args.type).slice(0,asInt(args.limit,1,200,50))};
 case "get_deep_sky_object":if(!s)return{available:false};return(s.deep_sky||[]).find(x=>x.id===args.name||x.n===args.name||String(x.en||"").toLowerCase()===String(args.name||"").toLowerCase())||{found:false};
 case "get_imported_sse_reference":if(!s)return{available:false};{const j=s.imported_sse||null;if(!j)return{available:false};const text=JSON.stringify(j);return args.include_raw&&text.length<=150000?{available:true,data:j}:{available:true,topLevelKeys:Object.keys(j),bytes:text.length,raw_available:text.length<=150000,note:"Unmodified original SSE import; not validated as HYG or NASA observations."}}
 case "lookup_jpl_sbdb":return SBDB(env,args.name);
 case "get_horizons_vector":return Horizons(env,args.body,args.date);
 default:throw Error("Unknown tool "+name);
 }
}
async function handleMCP(request,env){
 if(!testAuth(request,env.READ_TOKEN))return err(401,"Invalid read token");
 if(request.method==="GET")return no("POST, OPTIONS");
 if(request.method!=="POST")return no("POST, OPTIONS");
 let body;try{body=await request.json()}catch{return err(400,"Invalid JSON")};
 if(Array.isArray(body))return err(400,"MCP batch requests are not supported");
 const {id,method,params={}}=body;
 if(method==="notifications/initialized"||method?.startsWith("notifications/"))return new Response(null,{status:202});
 const success=result=>okJSON({jsonrpc:"2.0",id,result},200,{"mcp-protocol-version":"2025-06-18"});
 const failure=(code,message)=>okJSON({jsonrpc:"2.0",id,error:{code,message}},200);
 if(method==="initialize"){return success({protocolVersion:"2025-06-18",capabilities:{tools:{listChanged:false}},serverInfo:{name:"Starforge Unified Atlas MCP",version:"2.0.0"}})}
 if(method==="ping")return success({});
 if(method==="tools/list")return success({tools});
 if(method==="tools/call"){
  const name=params.name;try{
  if(!tools.some(t=>t.name===name))return failure(-32601,"Unknown tool");
  const ans=await callTool(env,name,params.arguments||{});
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
 if(path==="/api/health")return okJSON({service:"Starforge Secure Bridge v2",status:"ok",mcp:"/mcp",ssd:!!env.SSD_GATE});
 if(path==="/mcp"||path==="/api/mcp")return handleMCP(request,env);
 if(path==="/api/snapshot"){
  if(request.method==="GET"){if(!testAuth(request,env.READ_TOKEN))return err(401,"Read token required");return okJSON(await getSnapshot(env)||{available:false})}
  if(request.method!=="POST")return no("GET, POST, OPTIONS");
  if(!testAuth(request,env.WRITE_TOKEN))return err(401,"Write token required");
  if(Number(request.headers.get("content-length"))>MAX_BYTES)return err(413,"Snapshot exceeds 3 MB");
  const raw=await request.text();if(raw.length>MAX_BYTES)return err(413,"Snapshot exceeds 3 MB");
  let data;try{data=JSON.parse(raw)}catch{return err(400,"Invalid JSON snapshot")};
  if(data.schema_version!=="starforge.unified.v2")return err(422,"Unsupported schema");
  for(const [k,max] of Object.entries({stars:8000,observed_planets:3000,solar_bodies:30,solar_small_bodies:500,deep_sky:300,simulated_planets:500})){if(!Array.isArray(data[k])||data[k].length>max)return err(422,"Invalid size "+k)}
  if((data.simulated_planets||[]).some(p=>p.origin!=="SIMULATED"))return err(422,"Invalid simulation label");
  const updated_at=new Date().toISOString();
  await env.STARFORGE_KV.put("snapshot:latest",raw);
  await env.STARFORGE_KV.put("snapshot:meta",JSON.stringify({updated_at,version:data.version,bytes:raw.length}));
  return okJSON({ok:true,updated_at,version:data.version});
 }
 if(path==="/api/ssd/body"){
  if(!testAuth(request,env.READ_TOKEN)&&!testAuth(request,env.WRITE_TOKEN))return err(401,"Bridge key required");
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
   try{const response=await fetch(u.toString(),{headers:{Accept:"application/json"},signal:controller.signal});const raw=await response.text();if(!response.ok)return err(502,"JPL "+response.status);if(raw.length>1200000)return err(502,"JPL response too large");
    let result;try{result=JSON.parse(raw)}catch{return err(502,"Invalid JPL payload")}
    if(item.kind==="horizons"){if(typeof result.result!=="string"||!result.result.includes("$$SOE"))return err(502,"Horizons did not return vector data");const part=result.result.split("$$SOE")[1].split("$$EOE")[0].trim();result={source:"JPL Horizons",kind:"VECTORS",body:item.params.body,date:item.params.date,frame:"ECLIPTIC",center:"solar-system barycenter",units:"AU-D",vector_table_excerpt:part.slice(0,2500),not_for_navigation:true}}
    return okJSON(result);
   }finally{clearTimeout(timeout)}
  }catch(e){return err(502,"SSD backend temporarily unavailable: "+String(e.message||e))}
  finally{resolveNext()}
 }
}
