import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {join,dirname} from "node:path";
import {fileURLToPath} from "node:url";
const root=dirname(dirname(fileURLToPath(import.meta.url)));
const code=["data.js","exo-engine.js","app.js"].map(x=>readFileSync(join(root,x),"utf8")).join("\n");
const mocks=new Map(),handlers=new Map(),winListeners=new Map(),drawOps={};
const canvasCtx=new Proxy({}, {get(obj,key){if(key==="createRadialGradient")return ()=>({addColorStop(){}});if(key in obj)return obj[key];return (...args)=>{drawOps[key]=(drawOps[key]||0)+1}},set(obj,key,value){obj[key]=value;return true}});
function mock(id){
 if(!mocks.has(id)){
  const obj={id,style:{},dataset:{},hidden:false,textContent:"",innerHTML:"",value:"",checked:true,
   disabled:false,children:[],classList:{add(){},remove(){},toggle(){}},
   addEventListener(name,callback){handlers.set(id+":"+name,callback)},
   appendChild(child){this.children.push(child)},remove(){},setPointerCapture(){},
   select(){},click(){},getContext(){return canvasCtx},
   getBoundingClientRect(){return {left:0,top:0,width:430,height:280}}};
  mocks.set(id,obj);
 }
 return mocks.get(id)
}
const doc={getElementById:mock,body:mock("body"),execCommand(){return true},
 createElement(tag){const element=mock("created-"+tag+"-"+mocks.size);return element},
 querySelectorAll(q){
  if(q==="#modes button")return ["galaxy","system","solar","deep","ssd","sync"].map(m=>Object.assign(mock("tab-"+m),{dataset:{mode:m}}));
  if(q===".pane")return ["galaxy","system","solar","deep","ssd","sync"].map(m=>mock("pane-"+m));
  if(q==="#solar-scales button")return ["inner","outer","kuiper","oort","earth"].map(m=>Object.assign(mock("scale-"+m),{dataset:{scale:m}}));
  return [];
 }};
const win={devicePixelRatio:2,addEventListener(name,fn){winListeners.set(name,fn)},history:{replaceState(){}},location:{hostname:"raw.githack.com",pathname:"/unified/",search:""}};
const raf=[];const animate=(f)=>{raf.push(f);return raf.length};
const ls={getItem(){return null},setItem(){}};
const inst=new Function("window","document","requestAnimationFrame","localStorage","history","location","navigator","setTimeout","clearTimeout","Blob","URL",code);
inst(win,doc,animate,ls,win.history,win.location,{clipboard:{writeText:async()=>{}}},()=>1,()=>{},Blob,URL);
const api=win.SF_API;assert(api);
const start=api.getSnapshot();
assert.equal(start.stars.length,47);
assert.equal(start.observed_planets.length,17);
assert(start.generated_systems.length>=1);
assert(start.generated_systems[0].simulatedPlanets.length>=1);
assert(start.generated_systems[0].regions.every(x=>x.source==="SIMULATED"));
assert(mock("writeKey").disabled,"preview must block private write key");
const a=api.getSnapshot().generated_systems[0].seed;
const regenerate=handlers.get("generateEnvironment:click");assert(regenerate);
mock("exoSeed").value="another-story";
regenerate();
assert.notEqual(api.getSnapshot().generated_systems[0].seed,a);
api.setMode("system");raf.shift()?.(100);
api.setMode("solar");raf.shift()?.(150);
api.setMode("deep");raf.shift()?.(200);
api.setMode("galaxy");raf.shift()?.(250);
assert((drawOps.fillRect||0)>0,"star canvas painted");
assert(api.selectStarByName("Sirius"));
assert.equal(api.getSnapshot().selection.star_name,"Sirius");
const handler=winListeners.get("message");assert(handler);
handler({origin:"https://evil.test",data:{type:"STARFORGE_SSE_NATIVE",schema_version:"sse.starmap.v3.2",payload:{systems:[]}}});
assert.equal(api.getSnapshot().imported_sse,null,"spoofed origin must be ignored");
handler({origin:"https://starforge-sse-full-loyuhsi.pages.dev",data:{type:"STARFORGE_SSE_NATIVE",schema_version:"sse.starmap.v3.2",payload:{id:"native-sse-test",systems:[{id:"sample",nodes:[]}],gmNotes:"private user authorized"}}});
assert.equal(api.getSnapshot().imported_sse.systems.length,1);
console.log("PASS v3 browser: mobile Canvas2D, source-labelled environments, seed regeneration, full-mode navigation, private key suppression, origin-checked SSE handoff.");
