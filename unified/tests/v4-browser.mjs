import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {dirname,join} from "node:path";
import {fileURLToPath} from "node:url";
const root=dirname(dirname(fileURLToPath(import.meta.url)));
const code=["data.js","exo-engine.js","app.js"].map(s=>readFileSync(join(root,s),"utf8")).join("\n");
const els=new Map(),listeners=new Map(),frames=[];
const ctx=new Proxy({}, {get(o,k){if(k==="createRadialGradient")return ()=>({addColorStop(){}});return o[k]||(()=>{})},set(o,k,v){o[k]=v;return true}});
function el(id){
 if(!els.has(id))els.set(id,{id,hidden:false,value:"",checked:true,disabled:false,textContent:"",innerHTML:"",style:{},dataset:{},
  children:[],classList:{add(){},remove(){},toggle(){}},
  addEventListener(t,f){listeners.set(id+":"+t,f)},appendChild(c){this.children.push(c)},
  getContext(){return ctx},getBoundingClientRect(){return {width:430,height:300,left:0,top:0}},
  setPointerCapture(){},click(){},remove(){},select(){}});
 return els.get(id);
}
const doc={getElementById:el,body:el("body"),execCommand(){return true},
 createElement:tag=>el("created:"+tag+":"+els.size),
 querySelectorAll(q){
 if(q==="#modes button")return ["galaxy","system","solar","deep","ssd","sync"].map(x=>Object.assign(el("nav"+x),{dataset:{mode:x}}));
 if(q===".pane")return ["galaxy","system","solar","deep","ssd","sync"].map(x=>el("pane-"+x));
 if(q==="#solar-scales button")return ["inner","outer","kuiper","oort","earth"].map(x=>Object.assign(el("scale"+x),{dataset:{scale:x}}));
 return [];
 }};
const win={devicePixelRatio:2,location:{hostname:"starforge-unified-v3-loyuhsi.pages.dev",pathname:"/unified/",search:""},
 addEventListener(){},history:{replaceState(){}}};
let api;
async function fakeFetch(url,options={}){
 if(String(url)==="https://worker-test.example/api/snapshot"&&options.method==="GET"){
  const s=api.getSnapshot();
  return{ok:true,json:async()=>({
   ...s,edit_revision:7,user_objects:[{id:"user:abc",kind:"planet",host_star_id:"hyg:70666",name:"AI 雲端行星",
    origin:"SIMULATED",source:"TYPINGMIND_MCP_WRITE",attributes:{orbit_au:.14,mass_earth:1.25}}],
   simulated_deep_positions:[{id:"NGC_UNKNOWN",source:"SIMULATED_DISTANCE",reality:"FICTIONAL_SCENARIO",
    raDeg:22,decDeg:8,distanceLy:3000,xPc:100,yPc:200,zPc:34,seed:"test"}]
  })};
 }
 throw Error("unexpected network "+String(url));
}
const ctor=new Function("window","document","requestAnimationFrame","localStorage","history","location","navigator","setTimeout","clearTimeout","Blob","URL","fetch",code);
ctor(win,doc,fn=>{frames.push(fn);return frames.length},{getItem(){return null},setItem(){}},win.history,win.location,
 {clipboard:{writeText:async()=>{}}},()=>1,()=>{},Blob,URL,fakeFetch);
api=win.SF_API;
assert.equal(api.getSnapshot().user_objects.length,0);
assert.equal(el("writeKey").disabled,false,"only trusted owned domain enables write key");
el("bridgeURL").value="https://worker-test.example";
el("writeKey").value="test-secret-not-real";
const cb=listeners.get("pullAI:click");assert(typeof cb==="function","mobile AI refresh must be wired");
await cb();
assert.equal(api.getSnapshot().user_objects.length,1);
assert.equal(api.getSnapshot().edit_revision,7);
assert(el("aiSystemObjects").innerHTML.includes("AI 雲端行星"));
assert(el("aiAllObjects").innerHTML.includes("AI 雲端行星"));
assert(el("remoteEdits").innerHTML.includes("revision 7"));
api.setMode("system");frames.shift()?.(100);
assert.equal(api.getSnapshot().stars.length,47,"real observations must remain intact");
assert.equal(api.getSnapshot().observed_planets.length,17);
console.log("PASS v4 iPhone frontend: trusted Worker refresh updates fictional planets, UI and revision, keeps all 47 observed stars / 17 NASA planets.");
