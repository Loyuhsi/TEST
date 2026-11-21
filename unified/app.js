(function(){
"use strict";
const DATA=window.SF_DATA;
const Exo=window.StarforgeExoV3;
const $=id=>document.getElementById(id);
const list=s=>Array.from(document.querySelectorAll(s));
const allowedModes=["galaxy","system","solar","deep","ssd","sync"];
const num=v=>v===null||v===undefined||v===""?null:(Number.isFinite(Number(v))?Number(v):null);
const fmt=(v,n=2)=>v===null||v===undefined||!Number.isFinite(Number(v))?"未知":Number(v).toLocaleString("zh-TW",{maximumFractionDigits:n});
const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const pc=ly=>ly/3.26156,ly=pc=>pc*3.26156;
const PI=Math.PI,rad=d=>d*PI/180;
const hash=n=>{let x=Math.sin(n*127.135)*43758.5453;return x-Math.floor(x)};
let stars=DATA.stars.map(x=>({...x,id:"hyg:"+x.id,origin:"HYG"}));
let planets=DATA.exoplanets.map(x=>({...x,origin:"NASA_EXOPLANET"}));
let small=DATA.small.map(x=>({...x}));
const deep=DATA.deep.map(x=>({...x}));
const solar=DATA.solar.map(x=>({...x}));
const solarMap=Object.fromEntries(solar.map(x=>[x.id,x]));
let mode="galaxy",starRadius=15,showHosts=true,showDeep=true,selectedStar=null,selectedPlanet=null,selectedSolar="earth",selectedSmall="ssd:1",selectedDeep="M42",solarScale="inner",smallFilter="ALL",deepFilter="ALL",deepProjection="sky";
let importedSSE=null;let generatedSystems=new Map(),syntheticDeepMap=new Map(),deepSynthetic=true,deepSeed="fictional-mw-v1";let simulated=[];try{let x=JSON.parse(localStorage.getItem("sf_v2_simulated")||"[]");if(Array.isArray(x))simulated=x.slice(0,500)}catch{}
let yaw=.35,pitch=.45,zoom=1,paused=false,day=0,speed=8,last=0,frame=0,hit=[],pointers=new Map(),moved=false,firstPointer=null,pinchStart=0;
let bridge="",writeKey="",autoSync=false,syncTimer=null,nasaRetrieved="2026-11-21",currentSSD=null;
const canvas=$("sky"),ctx=canvas.getContext("2d",{alpha:false});let W=1,H=1,dpr=1;
if(!DATA||!ctx){$("health").textContent="未能初始化";return}
let toastTimer=0;const toast=m=>{const e=$("toast");e.textContent=m;e.classList.add("show");clearTimeout(toastTimer);toastTimer=setTimeout(()=>e.classList.remove("show"),3600)};
function on(id,type,fn){const e=$(id);if(e)e.addEventListener(type,fn)}
function normalizeName(s){return String(s||"").toLowerCase().replace(/[^a-z0-9]/g,"")}
const aliases={"proximacentauri":"proximacen","pollux":"hd62509","ran":"eps eri","rigilkentaurus":"alphacen","toliman":"alphacen","sirius":"sirius"};
function relatedPlanets(star){if(!star)return[];const raw=normalizeName(star.n),k=aliases[raw]||raw;return planets.filter(p=>normalizeName(p.h)===k || normalizeName(p.h)===raw)}

function generateEnvironment(force=false){
 if(!selectedStar||!Exo)return null;
 const id=String(selectedStar.id||selectedStar.n),found=generatedSystems.get(id);
 if(found&&!force)return found;
 const known=relatedPlanets(selectedStar);
 const opts={seed:($("exoSeed")?.value||"story-01")+"|"+id,diskMass:Number($("exoDisk")?.value||.5),
   metallicity:Number($("exoMet")?.value||0),dynamicalHistory:Number($("exoDyn")?.value||.35)};
 const model=Exo.generate(selectedStar,known,opts);
 generatedSystems.set(id,model);
 // Limit persisted per-star models; original NASA data is never modified.
 if(generatedSystems.size>18){const oldest=generatedSystems.keys().next().value;generatedSystems.delete(oldest)}
 return model;
}
function renderEnvironment(){
 const model=generateEnvironment(),box=$("exoStats"),out=$("exoRegions");
 if(!model||!box||!out)return;
 const p=model.priors,giants=model.simulatedPlanets.filter(p=>["gas_giant","ice_giant"].includes(p.kind)).length;
 const moons=model.simulatedPlanets.reduce((n,p)=>n+(p.moons?.length||0),0);
 box.innerHTML='<div class="griddata"><div>恆星質量：<b>'+fmt(model.physicalStar.massSolar,3)+' M☉</b><small>'+esc(model.physicalStar.massSource)+'</small></div>'+
 '<div>宜居帶先驗：<b>'+p.habitableZoneAU.map(x=>fmt(x,3)).join("～")+' AU</b></div>'+
 '<div>雪線估計：<b>'+fmt(p.snowLineAU,3)+' AU</b></div>'+
 '<div>星系年齡先驗：<b>'+fmt(p.ageGyr,2)+' Gyr</b></div>'+
 '<div>本次模擬：<b>'+model.planetCount+' 行星 / '+moons+' 衛星</b></div>'+
 '<div>外圍環境：<b>'+model.regions.length+' 帶狀區 + '+(model.outerCometCloud?"雲層":"無雲層")+'</b></div></div>'+
 '<p class="hint">依序列種子 '+esc(model.seed)+'，金屬量 '+fmt(p.metallicity,2)+'，盤質量 '+fmt(p.diskMass,2)+'，巨行星 '+giants+'；結果可重現。並非完整 SSE 物理模擬。</p>';
 const regions=model.regions.map(r=>'<div class="detailbox"><b>◌ '+esc(r.name)+'</b>　<span class="tag sim">SIMULATED</span>'+
 '<p>'+esc(r.type)+' · '+fmt(r.startAU,3)+'～'+fmt(r.endAU,2)+' AU</p>'+
 '<small>'+esc(r.formationRationale)+'</small></div>').join("");
 const cloud=model.outerCometCloud;
 out.innerHTML=regions+(cloud?'<div class="detailbox"><b>☄ '+esc(cloud.name)+'</b> <span class="tag sim">虛構彗星雲</span><p>'+
 fmt(cloud.innerAU,0)+'～'+fmt(cloud.outerAU,0)+' AU，非直接觀測</p><small>'+esc(cloud.uncertainty)+'</small></div>':
 '<div class="detailbox">本次模型沒有產生類歐特雲；不代表恆星系必然缺乏遠距彗星天體。</div>');
}
function imaginedDeep(o){
 if(o?.ly!==null&&o?.ly!==undefined&&Number(o.ly)>0)return null;
 if(!deepSynthetic||!Exo)return null;
 const key=deepSeed+"|"+String(o?.id);
 let found=syntheticDeepMap.get(key);
 if(!found){found=Exo.imaginedDeepPosition(o,{seed:deepSeed});syntheticDeepMap.set(key,found)}
 return found;
}
function allHosts(){const m=new Map();for(const p of planets){if(m.has(p.h)||!(p.d>0)||!Number.isFinite(p.ra)||!Number.isFinite(p.dec))continue;
const a=rad(p.ra),b=rad(p.dec),d=p.d;m.set(p.h,{id:"nasa:"+p.h,n:p.h,h:"",d,x:d*Math.cos(b)*Math.cos(a),y:d*Math.cos(b)*Math.sin(a),z:d*Math.sin(b),lum:null,m:null,s:"",origin:"NASA_HOST"})}return [...m.values()].filter(h=>!stars.some(s=>normalizeName(s.n)===normalizeName(h.n)))}
function allStars(){return [...stars,...allHosts()]}
function findStar(q){const v=normalizeName(q);let pool=allStars();let found=pool.find(s=>normalizeName(s.n)===v || String(s.h||"")===String(q).replace(/HIP\s*/i,""));if(!found)found=pool.find(s=>normalizeName(s.n).includes(v)||normalizeName(s.zh).includes(v));if(!found){let p=planets.find(p=>normalizeName(p.n).includes(v));if(p)found=pool.find(s=>normalizeName(s.n)===normalizeName(p.h))}return found}
function selectStar(star,goSystem=true){if(!star)return;selectedStar=star;selectedPlanet=null;if(star.d>starRadius){starRadius=[6,15,50,150,500,1000,10000].find(v=>v>=star.d)||10000;$("starRadius").value=String(Math.min(1000,starRadius))}updateSystem();renderStarChips();if(goSystem)switchMode("system");changed()}
function setText(id,value){const e=$(id);if(e)e.textContent=value}
function resize(){const r=canvas.getBoundingClientRect();W=Math.max(1,r.width);H=Math.max(1,r.height);dpr=Math.min(2,window.devicePixelRatio||1);canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0)}
window.addEventListener("resize",resize);if(window.ResizeObserver)new ResizeObserver(resize).observe(canvas);
function switchMode(next){if(!allowedModes.includes(next))return;mode=next;list("#modes button").forEach(b=>b.classList.toggle("active",b.dataset.mode===next));list(".pane").forEach(p=>{p.classList.toggle("active",p.id==="pane-"+next);p.hidden=p.id!=="pane-"+next});const heads={galaxy:["真實銀河局部星圖","恆星相對太陽位置（pc） · 2D 投影 3D 旋轉"],system:[(selectedStar?.n||"恆星系")+" 系統","真實行星優先；缺失數值絕不補成觀測值"],solar:["太陽系與小天體環境","主帶、柯伊伯帶、散射盤、日球層與推定歐特雲"],deep:["銀河非恆星天體","星團、星雲、脈衝星、棕矮星及黑洞"],ssd:["JPL SSD 軌道數據","離線 SBDB 快照；即時查詢需自有後端"],sync:["TypingMind / MCP 資料交換","本地匯出可用；遠端安全同步需部署 Bridge"]};setText("viz-title",heads[next][0]);setText("viz-sub",heads[next][1]);
setText("scale-label",next==="galaxy"?"HYG 赤道直角座標 pc · J2000":next==="deep"?"RA / Dec 或近似距離（各天體誤差不同）":next==="system"?"AU 示意／尺寸不等比例":next==="solar"?"日心 AU 壓縮尺度 · 非即時曆表":"資料探索示意");
if(next==="solar")updateSolar();if(next==="deep")updateDeep();if(next==="ssd")updateSSD();if(next==="system")updateSystem();if(next==="sync")renderSyncStatus();try{history.replaceState(null,"",location.pathname+"?mode="+encodeURIComponent(next)+(selectedStar?"&star="+encodeURIComponent(selectedStar.n):""))}catch{}}
function drawBg(){ctx.fillStyle="#06101c";ctx.fillRect(0,0,W,H);let g=ctx.createRadialGradient(W*.45,H*.4,5,W*.46,H*.54,Math.max(W,H)*.75);g.addColorStop(0,"#172e46");g.addColorStop(1,"#05101b");ctx.fillStyle=g;ctx.fillRect(0,0,W,H);for(let i=0;i<125;i++){const x=hash(i+21)*W,y=hash(i+121)*H;ctx.globalAlpha=.13+hash(i+127)*.48;ctx.fillStyle="#bcd7f7";ctx.fillRect(x,y,i%23===0?1.5:.85,i%23===0?1.5:.85)}ctx.globalAlpha=1}
function circ(x,y,r,c,glow=0){ctx.beginPath();ctx.fillStyle=c;ctx.shadowColor=c;ctx.shadowBlur=glow;ctx.arc(x,y,r,0,2*PI);ctx.fill();ctx.shadowBlur=0}
function textAt(s,x,y,color="#cbdff0"){ctx.font="11px system-ui";ctx.fillStyle=color;ctx.fillText(String(s),x,y)}
function project(v,R){const y0=v.y*Math.cos(yaw)-v.x*Math.sin(yaw),x0=v.y*Math.sin(yaw)+v.x*Math.cos(yaw);const h=v.z*Math.cos(pitch)-y0*Math.sin(pitch),depth=v.z*Math.sin(pitch)+y0*Math.cos(pitch);const perspective=Math.max(.45,Math.min(1.5,2.5/(2.5+depth/Math.max(R,1))));const s=Math.min(W,H)*.42/Math.max(R,1)*zoom*perspective;return{x:W/2+x0*s,y:H/2-h*s,z:depth}}
function colorStar(s){const t=(s.s||"").toUpperCase();return t.startsWith("O")?"#89b4ff":t.startsWith("B")?"#a3c3ff":t.startsWith("A")?"#d5e6ff":t.startsWith("F")?"#e8f6ff":t.startsWith("G")?"#ffe5b7":t.startsWith("K")?"#ffd19e":t.startsWith("M")?"#fc977b":"#cde4ed"}
function drawGalaxy(){const R=starRadius;hit=[];ctx.strokeStyle="#345f7655";ctx.lineWidth=1;
for(let rr=R/3;rr<=R;rr+=R/3){ctx.beginPath();for(let i=0;i<=80;i++){const a=i/80*2*PI,p=project({x:rr*Math.cos(a),y:rr*Math.sin(a),z:0},R);if(i)ctx.lineTo(p.x,p.y);else ctx.moveTo(p.x,p.y)}ctx.stroke()}
const sun=project({x:0,y:0,z:0},R);circ(sun.x,sun.y,4,"#ffd492",12);textAt("☀ 太陽（點此進入）",sun.x+8,sun.y-7,"#ffe4ad");hit.push({kind:"sun",x:sun.x,y:sun.y,r:20});
const pool=(showHosts?allStars():stars).filter(s=>s.d<=R&&Number.isFinite(s.x));pool.sort((a,b)=>(a.m??20)-(b.m??20));const limited=pool.slice(0,3600);let count=0;
for(const s of limited){const p=project(s,R);if(p.x<0||p.x>W||p.y<0||p.y>H)continue;count++;const selected=selectedStar?.id===s.id,col=s.origin==="NASA_HOST"?"#7ce7e0":colorStar(s);circ(p.x,p.y,selected?5:Math.max(1.2,3.7-(s.m??9)*.2),col,selected?15:1);if(selected||s.m!=null&&s.m<1.1)textAt(s.zh||s.n,p.x+7,p.y-7);hit.push({kind:"star",ref:s,x:p.x,y:p.y,r:Math.max(9,Math.min(16,4+(s.m??7)))});}
if(showDeep){for(const o of deep){if(!o.ly || pc(o.ly)>R)continue;const d=pc(o.ly),ra=rad(o.ra),dec=rad(o.dec),p=project({x:d*Math.cos(dec)*Math.cos(ra),y:d*Math.cos(dec)*Math.sin(ra),z:d*Math.sin(dec)},R);if(p.x<0||p.x>W||p.y<0||p.y>H)continue;drawDeepGlyph(p.x,p.y,o);hit.push({kind:"deep",ref:o,x:p.x,y:p.y,r:12});count++}}
setText("draw-count",fmt(count,0)+" 個可見節點");}
function drawDeepGlyph(x,y,o){const col=o.type==="BLACK_HOLE"?"#d6a0ff":o.type==="PULSAR"?"#7deded":o.type==="BROWN_DWARF"?"#ec9e7e":o.type.includes("CLUSTER")?"#b6c2ff":"#f8acde";ctx.beginPath();ctx.strokeStyle=col;ctx.lineWidth=1.8;ctx.arc(x,y,6,0,2*PI);ctx.stroke();if(o.type==="BLACK_HOLE")circ(x,y,2.7,"#080d19");else circ(x,y,2.3,col,8);if(o.id===selectedDeep)textAt(o.n,x+9,y-7,col)}
function visibleDeep(){
 const q=String($("deepQuery")?.value||"").trim().toLowerCase();
 return deep.filter(o=>(deepFilter==="ALL"||o.type===deepFilter)&&(!q||[o.id,o.n,o.en,o.type].some(v=>String(v||"").toLowerCase().includes(q))))
}
function drawDeep(){
 hit=[];let count=0;const total=visibleDeep(),objects=total.slice(0,1200);
 for(const o of objects){
 const knownDistance=Number.isFinite(Number(o.ly))&&Number(o.ly)>0;
 const fake=knownDistance?null:imaginedDeep(o);
 if(deepProjection==="distance"&&!knownDistance&&!fake)continue;
 const a=rad(o.ra),b=rad(o.dec),dist=knownDistance?pc(o.ly):fake?fake.distanceLy/3.26156:null;
 const coord=deepProjection==="sky"?{x:10+(o.ra/360)*(W-20),y:10+((90-o.dec)/180)*(H-20)}:(()=>{
 const radius=Math.log10(1+dist),r=Math.log10(1+20000);
 return project({x:Math.cos(b)*Math.cos(a)*radius,y:Math.cos(b)*Math.sin(a)*radius,z:Math.sin(b)*radius},r)
 })();
 if(!Number.isFinite(coord.x)||!Number.isFinite(coord.y))continue;
 count++;
 drawDeepGlyph(coord.x,coord.y,o);
 if(fake){ctx.beginPath();ctx.strokeStyle="#d2a4fa";ctx.lineWidth=1.3;ctx.arc(coord.x,coord.y,9,0,2*PI);ctx.stroke()}
 hit.push({kind:"deep",ref:o,x:coord.x,y:coord.y,r:19});
 if(o.id===selectedDeep||o.id==="M42"||o.id==="SgrA*")textAt(o.n+(fake?" ✧":""),coord.x+10,coord.y-8);
 }
 setText("draw-count",count+" 個天體節點"+(total.length>objects.length?"（取樣顯示）":"")+
  (deepProjection==="distance"?(deepSynthetic?" · 紫環為虛構 3D 位置":" · 未知距離已隱藏"):""));
}

function groupSolar(){return small.filter(b=>smallFilter==="ALL"||b.group===smallFilter)}
function radial(a){const min=Math.min(W,H)*.09,range=Math.min(W,H)*.36*zoom;
if(solarScale==="earth")return 0;
if(solarScale==="inner")return min+range*Math.pow(Math.min(a,3.6)/3.6,.75);
if(solarScale==="outer")return min+range*Math.log1p(Math.min(a,35))/Math.log1p(35);
if(solarScale==="kuiper")return min+range*Math.log1p(Math.min(a,100))/Math.log1p(100);
return min+range*Math.log1p(Math.min(a,100000))/Math.log1p(100000)}
function ring(r,color,width=1){ctx.beginPath();ctx.strokeStyle=color;ctx.lineWidth=width;ctx.ellipse(W/2,H*.54,r,r*Math.max(.26,.72*Math.cos(pitch)*.7+.34),yaw,0,2*PI);ctx.stroke()}
function orbitPosition(a,phase){const r=radial(a),angle=phase+yaw;return{x:W/2+Math.cos(angle)*r,y:H*.54+Math.sin(angle)*r*Math.max(.27,.65*Math.cos(pitch)+.32)}}
function drawBand(lo,hi,n,col,seed=1){for(let i=0;i<n;i++){const f=hash(i*3.3+seed),a=lo+(hi-lo)*f,angle=i*2.39996+seed*2,p=orbitPosition(a,angle);ctx.globalAlpha=.2+.55*hash(i+seed*11);circ(p.x,p.y,.4+hash(i+4)*.7,col)}ctx.globalAlpha=1}
function drawSolar(){hit=[];const center={x:W/2,y:H*.54};const inc=solarScale==="inner"?solar.filter(s=>s.a<=4):solarScale==="outer"?solar.filter(s=>s.a>3.5&&s.a<=31):solarScale==="kuiper"?solar.filter(s=>s.a>=19):solarScale==="oort"?[]:solar.filter(s=>["sun","earth","moon"].includes(s.id));
circ(center.x,center.y,solarScale==="earth"?5:9,"#ffd28f",18);hit.push({kind:"solar",ref:solarMap.sun,x:center.x,y:center.y,r:16});
if(solarScale==="earth"){const earth=solarMap.earth;const r=Math.min(W,H)*.095*zoom;circ(center.x,center.y,r,"#3188cc",16);circ(center.x-r*.15,center.y-r*.19,r*.43,"#3bbd85");ring(Math.min(W,H)*.33*zoom,"#91bfe366");hit.push({kind:"solar",ref:earth,x:center.x,y:center.y,r:r+12});
const m=solarMap.moon,p={x:center.x+Math.cos(day/27.322*2*PI+yaw)*Math.min(W,H)*.33*zoom,y:center.y+Math.sin(day/27.322*2*PI+yaw)*Math.min(W,H)*.22*zoom};circ(p.x,p.y,7,"#bcc0c7",7);textAt("月球",p.x+9,p.y);hit.push({kind:"solar",ref:m,x:p.x,y:p.y,r:17});textAt("地球 · 磁層／大氣示意",center.x-r-15,center.y+r+18);setText("draw-count","地月兩個主要節點");return}
if(solarScale==="inner"){ring(radial(2.1),"#a2a2a040");ring(radial(3.4),"#a2a2a040");if($("showSmall").checked)drawBand(2.1,3.4,175,"#d3c09b",11)}
if(solarScale==="outer"){if($("showSmall").checked)drawBand(5.0,5.5,125,"#a9b9df",5)}
if(solarScale==="kuiper"){ring(radial(30),"#7a9cca59",2);ring(radial(50),"#7a9cca59",2);if($("showSmall").checked)drawBand(30,50,220,"#98b6dd",24);textAt("柯伊伯帶 30–50 AU",10,H-37)}
if(solarScale==="oort"){const layers=[[120,"日球層頂約百餘 AU","#6bc8ca"],[3000,"內歐特雲（理論）","#9c9cbe"],[100000,"外歐特雲（理論）","#b6a2d9"]];for(const [a,label,col] of layers){ring(radial(a),col+"55",1.5);const p=orbitPosition(a,.8);textAt(label,Math.max(6,Math.min(W-180,p.x)),p.y,col)}if($("showSmall").checked)drawBand(3000,100000,210,"#b3a2dc",13)}
let count=0;for(const b of inc){if(b.id==="sun"||b.id==="moon")continue;const p=orbitPosition(b.a,(b.phase||0)+day*2*PI/Math.max(1,b.period));ring(radial(b.a),"#6685a044");const r=b.id==="jupiter"?8:b.id==="saturn"?7:b.id==="earth"?6:4;circ(p.x,p.y,r,b.color,b.id===selectedSolar?13:4);hit.push({kind:"solar",ref:b,x:p.x,y:p.y,r:17});if(b.id===selectedSolar||r>5)textAt(b.n,p.x+8,p.y-8);count++}
if($("showSmall").checked){for(const s of groupSolar()){if(s.a===null||s.a===undefined)continue;if(solarScale==="inner"&&s.a>4||solarScale==="outer"&&(s.a<3||s.a>32)||solarScale==="kuiper"&&(s.a<28||s.a>110)||solarScale==="oort"&&s.a<200)continue;const p=orbitPosition(s.a,(s.ma??hash(s.a)*360)*PI/180+day*2*PI/(s.period||Math.max(300,s.a**1.5*365)));circ(p.x,p.y,2.4,s.source==="JPL_SBDB_SNAPSHOT"?"#9be3d7":"#b6a4d9",4);hit.push({kind:"small",ref:s,x:p.x,y:p.y,r:12});count++}}
setText("draw-count",count+" 個天體節點（示意）")}
function drawSystem(){
 hit=[];const model=generateEnvironment(),legacy=simulated.filter(p=>p.hostId===selectedStar?.id);
 const arr=[...(model?.realConfirmedPlanets||[]).map(p=>({...p,sim:false,name:p.name,period:p.periodDays})),
           ...(model?.simulatedPlanets||[]).map(p=>({...p,sim:true,name:p.name,period:p.periodDays})),
           ...legacy.map(p=>({...p,sim:true,name:p.name,period:p.period}))].filter(p=>p.a&&p.a>0);
 const cx=W/2,cy=H*.54;
 const cloud=model?.outerCometCloud,regions=model?.regions||[];
 const maxA=Math.max(.12,...arr.map(p=>p.a||.12),...regions.map(r=>r.endAU||0));
 const maxR=Math.min(W,H)*.42*zoom;
 const screenR=a=>maxR*(.14+.80*Math.log1p(Math.min(a,maxA)*12)/Math.log1p(maxA*12));
 // Belt positions are region models, not copies of Solar System belts.
 for(const reg of regions){
 const start=screenR(reg.startAU),end=screenR(reg.endAU),color=reg.type.includes("TROJAN")?"#a5d4dd":reg.type.includes("KUIPER")?"#9f9ee5":"#c3a989";
 if(reg.type==="TROJAN_CLOUD"){
   const host=arr.find(x=>x.id===reg.hostPlanetId);
   const phase=host?host.positionPhase||.4:1.1;
   for(let k=0;k<30;k++){const p=(k%2?phase+PI/3:phase-PI/3)+hash(k*10.93+reg.startAU)*.3;
      const rad0=screenR((reg.startAU+reg.endAU)*.5);
      circ(cx+Math.cos(p+yaw)*rad0,cy+Math.sin(p+yaw)*rad0*.55,.7,color);}
 }else{
   for(let k=0;k<90;k++){
    const rr=start+(end-start)*hash(k*1.711+reg.startAU),theta=k*2.399+hash(k*23)*.12;
    ctx.globalAlpha=.1+.58*hash(k+reg.startAU);circ(cx+Math.cos(theta+yaw)*rr,cy+Math.sin(theta+yaw)*rr*.55,.7,color)
   }
   ctx.globalAlpha=1
 }
 }
 circ(cx,cy,10,selectedStar?colorStar(selectedStar):"#ffd58e",18);
 hit.push({kind:"selectedStar",x:cx,y:cy,r:20});
 textAt(selectedStar?.n||"恆星",cx+14,cy-10);
 let count=0;for(const [i,p] of arr.entries()){
 const rr=screenR(p.a);
 ring(rr,p.sim?"#b48ac04e":"#6bcbd14b");
 const xy=Exo?.positionAt(p,day);const theta=xy?Math.atan2(xy.yAU,xy.xAU):day*2*PI/Math.max(1,p.period||600)+(i*2.3);
 const pos={x:cx+Math.cos(theta+yaw)*rr,y:cy+Math.sin(theta+yaw)*rr*Math.max(.26,.8*Math.cos(pitch)+.3)};
 const color=p.sim?(p.kind==="gas_giant"?"#ddc09e":p.kind==="ice_giant"?"#93d9e5":"#c6a6ec"):(p.radiusEarth!=null&&p.radiusEarth>7?"#d8aa92":"#7ee0cb");
 circ(pos.x,pos.y,p.id===selectedPlanet?6:4,color,p.id===selectedPlanet?13:5);
 if(p.rings){ctx.beginPath();ctx.strokeStyle="#9dc5e4ba";ctx.ellipse(pos.x,pos.y,8,3,.35,0,2*PI);ctx.stroke()}
 hit.push({kind:"planet",ref:p,x:pos.x,y:pos.y,r:18});
 if(p.id===selectedPlanet||arr.length<5)textAt(p.name,pos.x+6,pos.y-5);
 count++;
 }
 if(cloud)textAt("☄ "+cloud.name+" • "+fmt(cloud.innerAU,0)+"～"+fmt(cloud.outerAU,0)+" AU（虛構）",8,H-28,"#cfb0e7");
 setText("draw-count",count+" 顆行星 / "+regions.length+" 種帶狀環境 · 非即時軌道");
}

function draw(ts){requestAnimationFrame(draw);if(!last)last=ts;const dt=Math.min(.1,Math.max(0,(ts-last)/1000));last=ts;if(!paused)day+=dt*speed;if(ts-frame<36)return;frame=ts;drawBg();if(mode==="galaxy")drawGalaxy();else if(mode==="deep")drawDeep();else if(mode==="solar")drawSolar();else if(mode==="system")drawSystem();else{ctx.fillStyle="#a9c6d7";ctx.font="15px system-ui";ctx.fillText(mode==="ssd"?"JPL SSD · 選取右側資料查詢":"TypingMind · 安全資料匯出 / MCP",Math.max(15,W/2-160),H/2)}}
function starInfo(star){if(!star)return"<p>請選擇恆星。</p>";return '<div class="griddata"><div>來源：<b>'+esc(star.origin)+'</b></div><div>距離：<b>'+fmt(star.d,3)+' pc</b></div><div>光譜：<b>'+esc(star.s||"未測")+'</b></div><div>光度：<b>'+fmt(star.lum,3)+' L☉</b></div></div><p class="muted">恆星在星圖中使用 HYG / NASA 的赤道座標，行星軌道另以 AU 顯示。</p>'}
function updateSystem(){if(!selectedStar)return;const generated=generateEnvironment();setText("systemHeading",(selectedStar.zh?selectedStar.zh+" · ":"")+selectedStar.n);setText("systemOrigin",selectedStar.origin==="NASA_HOST"?"NASA Exoplanet Archive 母恆星":"HYG 衍生恆星資料");$("systemStar").innerHTML=starInfo(selectedStar);let known=relatedPlanets(selectedStar),fiction=simulated.filter(p=>p.hostId===selectedStar.id);
$("systemPlanets").innerHTML=known.length+fiction.length?known.map(p=>'<div class="detailbox"><span class="tag real">NASA 已確認</span><b>'+esc(p.n)+'</b><div class="griddata"><div>週期 '+fmt(p.p,3)+' 日</div><div>半長軸 '+fmt(p.a,4)+' AU</div><div>半徑 '+fmt(p.r,3)+' 地球半徑</div><div>質量 '+fmt(p.m,3)+' 地球質量</div></div></div>').join("")+fiction.map(p=>'<div class="detailbox"><span class="tag sim">虛構生成</span><b>'+esc(p.name)+'</b><p>半長軸 '+fmt(p.a,3)+' AU · Kepler 近似週期 '+fmt(p.period,1)+' 日</p></div>').join(""):'<div class="detailbox">目前載入的 NASA 樣本中沒有這顆恆星的已確認行星；不等於實際不存在行星。</div>';
if(generated&&generated.simulatedPlanets.length){
 $("systemPlanets").innerHTML+=generated.simulatedPlanets.map(p=>
  '<div class="detailbox"><span class="tag sim">SIMULATED · '+esc(p.kind)+'</span><b>'+esc(p.name)+'</b>'+
  '<div class="griddata"><div>a：'+fmt(p.a,4)+' AU</div><div>e：'+fmt(p.eccentricity,3)+'</div>'+
  '<div>週期：'+fmt(p.periodDays,2)+' 日</div><div>大小：'+fmt(p.radiusEarth,2)+' R⊕</div>'+
  '<div>溫度估計：'+fmt(p.environment?.temperatureEquilibriumK,0)+' K</div>'+
  '<div>表面重力：'+fmt(p.environment?.surfaceGravityMs2,2)+' m/s²</div></div>'+
  '<p>☾ 衛星：'+(p.moons?.length||0)+'，行星環：'+(p.rings?esc(p.rings.type):'無')+'</p></div>'
 ).join("");
}
renderEnvironment()}
function updateSolar(){const b=solarMap[selectedSolar]||solarMap.earth;setText("solarSelName",b.n);let html='<b>'+esc(b.n)+' · '+esc(b.en)+'</b><p>'+esc(b.descr)+'</p><div class="griddata"><div>軌道半長軸：<b>'+fmt(b.a,3)+' AU</b></div><div>公轉週期：<b>'+fmt(b.period,1)+' 日</b></div><div>赤道直徑：<b>'+fmt(b.diameter,0)+' km</b></div><div>參考重力：<b>'+fmt(b.g,2)+' m/s²</b></div></div><p>環境：'+esc(b.temp)+" · "+esc(b.atm)+"</p>";
if(selectedSolar==="earth")html+='<div class="hint">大氣：氮約 78%、氧約 21%；海洋覆蓋約 71%；地軸傾角約 23.4°；月球平均距離約 384,400 km。磁層與太陽風相互作用會隨太陽活動改變。</div>';
$("solarDetails").innerHTML=html;
const bands={inner:"主小行星帶約 2.1–3.4 AU；木星的重力共振造成柯克伍德空隙。點選已載入的小天體可查看 JPL 參數。",outer:"木星特洛伊群分布在 L4／L5 附近，並非固定同心環；行星軌道點為示意。",kuiper:"柯伊伯帶主體約 30–50 AU；冥王星 3:2 共振、散射盤與分離天體分布不同。",oort:"歐特雲的內外界線高度不確定，推定分布可延伸至數萬甚至約十萬 AU；沒有完整直接觀測的雲內物件清單。此圖僅表示假說區域。",earth:"地球磁層、范艾倫輻射帶、月球軌道及太陽風的比例皆經過示意化處理。"};setText("bandsInfo",bands[solarScale]);list("#solar-scales button").forEach(b=>b.classList.toggle("active",b.dataset.scale===solarScale));updateSmallList();}
function updateSmallList(){let arr=groupSolar(),c=$("smallList");c.innerHTML="";for(const b of arr){const btn=document.createElement("button");btn.className=b.id===selectedSmall?"selected":"";btn.innerHTML="<b>"+esc(b.zh||b.name)+"</b><small>"+esc(b.name)+" · "+esc(b.group)+" · "+fmt(b.a,2)+" AU · "+(b.source==="JPL_SBDB_SNAPSHOT"?"JPL 軌道快照":"近似示意")+"</small>";btn.onclick=()=>{selectedSmall=b.id;showSmallBody(b);updateSmallList();changed()};c.appendChild(btn)}}
function showSmallBody(b){if(!b)return;currentSSD=b;switchMode("ssd");updateSSD()}
function updateSSD(){const b=currentSSD||small.find(x=>x.id===selectedSmall)||small[0];if(!b)return;const real=b.source==="JPL_SBDB_SNAPSHOT";$("ssdOutput").innerHTML='<div><span class="tag '+(real?"real":"approx")+'">'+(real?"JPL SBDB 核對快照":"僅代表性近似值")+'</span><h3>'+esc(b.zh||b.name)+' · '+esc(b.name)+'</h3><div class="griddata"><div>a：'+fmt(b.a,4)+' AU</div><div>e：'+fmt(b.e,5)+'</div><div>i：'+fmt(b.i,3)+'°</div><div>M：'+fmt(b.ma,2)+'°</div><div>週期：'+fmt(b.period,1)+' 日</div><div>軌道曆元 JD：'+fmt(b.epoch,1)+'</div></div><p class="muted">來源：'+esc(b.source)+'。'+(real?"不同小天體軌道曆元不一定相同，不能直接當成同一天的精確相對位置。":"目前沒有核對完整軌道要素，不應把環形點當成預報軌道。")+'</p></div>';}
function updateDeep(){
 const c=$("deepList");c.innerHTML="";
 const matches=visibleDeep();
 for(const o of matches.slice(0,150)){
 const fake=imaginedDeep(o),known=Number(o.ly)>0;
 const b=document.createElement("button");b.className=o.id===selectedDeep?"selected":"";
 b.innerHTML="<b>"+esc(o.n)+"</b><small>"+esc(o.en)+" · "+esc(o.type)+" · "+
    (known?"約 "+fmt(o.ly,0)+" 光年（參考距離）":fake?"✧ 虛構 "+fmt(fake.distanceLy,0)+" 光年":"僅天球方向")+"</small>";
 b.onclick=()=>{selectedDeep=o.id;updateDeep();changed()};c.appendChild(b)
 }
 const o=deep.find(x=>x.id===selectedDeep),sim=imaginedDeep(o),known=o&&Number(o.ly)>0;
 $("deepDetails").innerHTML=o?'<b>'+esc(o.n)+' / '+esc(o.en)+'</b><div class="griddata"><div>類型：<b>'+esc(o.type)+'</b></div>'+
  '<div>實測／參考距離：<b>'+(known?"約 "+fmt(o.ly,0)+" 光年":"未提供")+'</b></div>'+
  '<div>赤經：<b>'+fmt(o.ra,4)+'°</b></div><div>赤緯：<b>'+fmt(o.dec,4)+'°</b></div></div>'+
  (sim?'<p><span class="tag sim">SIMULATED_DISTANCE</span> 虛構徑向距離 '+fmt(sim.distanceLy,1)+' 光年<br>衍生 XYZ（pc）：'+fmt(sim.xPc,3)+", "+fmt(sim.yPc,3)+", "+fmt(sim.zPc,3)+
  '<br>種子：'+esc(sim.seed)+'；類型先驗範圍 '+sim.priorRangeLy.join("～")+' 光年。不可引用為真實天文測量。</p>':
  '<p class="muted">未使用虛構距離；僅保留原始目錄資訊。</p>')+
  '<p class="muted">原始來源：'+esc(o.source)+' / '+esc(o.precision)+'</p><a href="'+esc(o.link)+'" rel="noopener" target="_blank">原始資料來源</a>':"尚未選取深空天體";
 const m=deep.filter(o=>o.source==="OpenNGC CC BY-SA 4.0").length;
 setText("deepCatalogStatus","已載入 "+deep.length+" 筆深空資料"+(m?"（OpenNGC "+m+" 筆）":"（內建 13 筆）")+
 "；最多顯示 150 筆。紫色標記代表虛構距離；實際測量值保持原樣。");
}

function renderStarChips(){const container=$("quick-stars");container.innerHTML="";const names=["Proxima Centauri","Sirius","Vega","Pollux","TRAPPIST-1","GJ 876","51 Peg"];for(const name of names){const b=document.createElement("button");b.textContent=name;b.onclick=()=>{const s=findStar(name);if(s)selectStar(s,true);else toast("目前樣本未包含此恆星")};container.appendChild(b)}}
function download(name,str,type){const obj=new Blob([str],{type:type||"application/json"}),url=URL.createObjectURL(obj),a=document.createElement("a");a.href=url;a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{a.remove();URL.revokeObjectURL(url)},2000)}
function snapshot(){return{schema_version:"starforge.unified.v2",exported_at:new Date().toISOString(),data_kind:"observations_plus_simulation",version:DATA.version,selection:{mode,star_id:selectedStar?.id,star_name:selectedStar?.n,solar:selectedSolar,small_body:selectedSmall,deep:selectedDeep,solar_view:solarScale},sources:DATA.metadata,stars,observed_planets:planets,solar_bodies:solar,solar_small_bodies:small,deep_sky:deep,simulated_planets:simulated,generated_systems:[...generatedSystems.values()],simulated_deep_positions:[...syntheticDeepMap.values()].filter(x=>x.seed===deepSeed),imported_sse:importedSSE,note:"CATALOG fields are observational/reference. SIMULATED are creative; orbit animations are illustrative and not Horizons ephemerides."}}
function changed(){if(autoSync&&bridge&&writeKey){clearTimeout(syncTimer);syncTimer=setTimeout(()=>sendSnapshot(true),1600)}}
function saveFiction(){try{localStorage.setItem("sf_v2_simulated",JSON.stringify(simulated))}catch{}}
function simulatePlanet(){if(!selectedStar)return;const i=simulated.filter(p=>p.hostId===selectedStar.id).length+1;if(i>30){toast("單顆恆星最多加入 30 顆示意行星");return}const a=Math.round((.15+hash(i+selectedStar.n.length)*6)*1000)/1000;const L=selectedStar.lum??1,M=Math.min(30,Math.max(.08,L**(1/3.5)));const p=365.25*Math.sqrt(a*a*a/M);simulated.push({id:"sf:sim:"+Date.now()+":"+i,hostId:selectedStar.id,name:selectedStar.n+" · 虛構行星 "+i,origin:"SIMULATED",a,period:p,estimatedMassSolar:M,method:"Kepler two-body approximate, stellar mass estimated from luminosity",created_at:new Date().toISOString()});saveFiction();updateSystem();changed();toast("已產生明確標示的虛構行星")}
function summary(){const p=relatedPlanets(selectedStar),b=solarMap[selectedSolar],o=deep.find(x=>x.id===selectedDeep),f=simulated.filter(x=>x.hostId===selectedStar?.id);return"【星海工坊 v2｜"+new Date().toISOString()+"】\n目前模式："+mode+"\n恆星："+(selectedStar?.n||"未選")+", 距離 "+fmt(selectedStar?.d,3)+" pc, HYG / NASA 來源 "+(selectedStar?.origin||"")+"\n已確認行星："+(p.map(x=>x.n+"（週期 "+fmt(x.p,3)+" 日，a "+fmt(x.a,3)+" AU）").join("；")||"載入資料中未發現")+"\n虛構行星："+(f.map(x=>x.name).join("、")||"無")+"\n太陽系選取："+(b?.n||"")+", 小天體："+(small.find(x=>x.id===selectedSmall)?.name||"")+"\n深空："+(o?.n||"")+", 約 "+fmt(o?.ly,0)+" 光年\n資料來源：HYG / NASA Exoplanet Archive / JPL SBDB 快照 / NASA Hubble / OpenNGC。示意軌道不是即時 NASA Horizons 星曆；區分已觀測與模擬資料。"}
async function copy(str){try{await navigator.clipboard.writeText(str);toast("已複製到剪貼簿")}catch{const el=document.createElement("textarea");el.value=str;document.body.appendChild(el);el.select();const ok=document.execCommand("copy");el.remove();toast(ok?"已複製":"請改用匯出 JSON")}}
function renderSyncStatus(msg){if(msg)setText("syncStatus",msg);else setText("syncStatus",bridge?"已設定 Bridge URL，尚未驗證服務。":"尚未配置 Bridge；離線匯出與複製摘要可用。")}
function normalizedBridge(){const raw=$("bridgeURL").value.trim().replace(/\/+$/,"");if(!raw)return"";try{const u=new URL(raw);if(u.protocol!=="https:")return"";return u.origin+(u.pathname==="/"? "":u.pathname)}catch{return""}}
async function testBridge(){bridge=normalizedBridge();if(!bridge){toast("請先填寫有效的 HTTPS Bridge 網址");return}try{let r=await fetch(bridge+"/api/health",{cache:"no-store",mode:"cors"});if(!r.ok)throw Error("HTTP "+r.status);let data=await r.json();renderSyncStatus("Bridge 已回應："+(data.service||"Starforge")+". 若要同步請填寫寫入金鑰。");toast("Bridge 連線成功")}catch(e){renderSyncStatus("Bridge 未連線："+String(e.message||e));toast("Bridge 無法連線，離線資料仍可使用")}}
async function sendSnapshot(silent=false){bridge=normalizedBridge();writeKey=$("writeKey").value.trim();if(!bridge||!writeKey){if(!silent)toast("需要 Bridge HTTPS URL 和獨立寫入金鑰");return}try{const r=await fetch(bridge+"/api/snapshot",{method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+writeKey},body:JSON.stringify(snapshot()),mode:"cors"});if(!r.ok)throw Error("HTTP "+r.status);const d=await r.json();renderSyncStatus("已同步到 Bridge，時間："+(d.updated_at||new Date().toLocaleString("zh-TW"))+"，版本："+(d.version||"2"));if(!silent)toast("成功同步，可由 TypingMind MCP 讀取")}catch(e){renderSyncStatus("同步失敗："+String(e.message||e));if(!silent)toast("同步失敗；本地資料仍保留")}}
async function requestSSD(){const q=$("ssdSearch").value.trim().slice(0,60);if(!q){toast("請輸入小天體名稱或編號");return}const cached=small.find(s=>s.name.toLowerCase()===q.toLowerCase()||s.zh===q||s.id==="ssd:"+q);if(cached){selectedSmall=cached.id;currentSSD=cached;updateSSD()}const base=normalizedBridge(),key=$("writeKey").value.trim();if(!base||!key){toast("已顯示離線快照；即時 JPL 查詢需設定 Bridge");return}try{setText("syncStatus","正在由 Bridge 依 JPL 限速查詢……");let r=await fetch(base+"/api/ssd/body?name="+encodeURIComponent(q),{headers:{"Authorization":"Bearer "+key}});if(!r.ok)throw Error("HTTP "+r.status);let j=await r.json();if(!j.object||!j.orbit)throw Error("不是有效 SBDB 物件");const parts=Object.fromEntries((j.orbit.elements||[]).map(v=>[v.name,num(v.value)]));currentSSD={id:"ssd:"+j.object.des,name:j.object.shortname||q,zh:q,group:j.object.orbit_class?.code||"OTHER",a:parts.a,e:parts.e,i:parts.i,ma:parts.ma,period:parts.per,epoch:num(j.orbit.epoch),source:"JPL_SBDB_LIVE_VIA_BRIDGE",precision:"JPL supplied",date:new Date().toISOString().slice(0,10)};updateSSD();toast("已透過 Bridge 取得 SBDB")}catch(e){toast("SSD 即時查詢失敗："+String(e.message||e))}}
function findSolar(q){const s=solar.find(b=>b.n===q||b.en.toLowerCase()===q.toLowerCase());if(s){selectedSolar=s.id;switchMode("solar");changed()}}
function clickSearch(id){const e=$(id),s=findStar(e.value.trim());if(s)selectStar(s,true);else{if(e.value.includes("太陽")||e.value.includes("地球")){selectedSolar=e.value.includes("地球")?"earth":"sun";switchMode("solar")}else toast("樣本中沒有找到該恆星；可嘗試下載命名星表")}}
function bindUI(){list("#modes button").forEach(b=>b.onclick=()=>switchMode(b.dataset.mode));
on("starGo","click",()=>clickSearch("starSearch"));on("systemGo","click",()=>clickSearch("systemSearch"));on("starSearch","keydown",e=>{if(e.key==="Enter")clickSearch("starSearch")});on("systemSearch","keydown",e=>{if(e.key==="Enter")clickSearch("systemSearch")});
on("starRadius","change",e=>{starRadius=Number(e.target.value);changed()});on("showHosts","change",e=>{showHosts=e.target.checked;changed()});on("showDeep","change",e=>{showDeep=e.target.checked;changed()});
on("deepFilter","change",e=>{deepFilter=e.target.value;updateDeep()});on("deepProjection","change",e=>{deepProjection=e.target.value;changed()});on("deepGo","click",updateDeep);on("deepQuery","keydown",e=>{if(e.key==="Enter")updateDeep()});on("loadOpenNGC","click",loadOpenNGC);
on("deepSynthetic","change",e=>{deepSynthetic=!!e.target.checked;updateDeep();changed()});
on("deepRegenerate","click",()=>{deepSeed=String($("deepSeed").value||"fictional-mw-v1").slice(0,80);syntheticDeepMap.clear();updateDeep();changed();toast("已根據新種子生成虛構距離；原始座標未修改")});
on("generateEnvironment","click",()=>{if(!selectedStar)return;generatedSystems.delete(String(selectedStar.id||selectedStar.n));generateEnvironment(true);updateSystem();changed();toast("已重新生成完整環境，可重現")});
on("exportExo","click",()=>{const x=generateEnvironment();if(!x){toast("請先選擇恆星");return}download("Starforge_Exosystem_"+String(selectedStar.n).replace(/[^\w-]/g,"_")+".json",JSON.stringify(x,null,2));toast("環境 JSON 已下載")});
list("#solar-scales button").forEach(b=>b.onclick=()=>{solarScale=b.dataset.scale;updateSolar();changed()});on("timeSpeed","input",e=>speed=Number(e.target.value));on("smallGroup","change",e=>{smallFilter=e.target.value;updateSolar()});on("showSmall","change",()=>changed());
on("solarBodySelect","change",e=>{selectedSolar=e.target.value;updateSolar();changed()});on("addFiction","click",simulatePlanet);on("removeFiction","click",()=>{if(!selectedStar)return;simulated=simulated.filter(p=>p.hostId!==selectedStar.id);saveFiction();updateSystem();changed();toast("已清除此恆星的虛構行星")});
on("ssdGo","click",requestSSD);on("ssdSearch","keydown",e=>{if(e.key==="Enter")requestSSD()});on("ssdCached","click",()=>{currentSSD=small.find(x=>x.id===selectedSmall)||small[0];updateSSD();toast("顯示本地 SBDB 快照")});
on("bridgeURL","change",e=>{bridge=normalizedBridge();try{localStorage.setItem("sf_v2_bridge_url",bridge)}catch{}});
on("writeKey","input",e=>{writeKey=e.target.value.trim()});on("autoSync","change",e=>{autoSync=e.target.checked;if(autoSync)changed()});on("syncNow","click",()=>sendSnapshot());on("testBridge","click",testBridge);on("copyMCP","click",()=>{let b=normalizedBridge();if(!b){toast("請先填入 Bridge 基址");return}copy(b+"/mcp")});on("exportJSON","click",()=>{download("Starforge_Unified_Atlas_v2_"+new Date().toISOString().slice(0,10)+".json",JSON.stringify(snapshot(),null,2));toast("JSON 已啟動下載")});on("copySummary","click",()=>copy(summary()));on("importJSON","click",()=>$("importFile").click());on("importFile","change",async e=>{const file=e.target.files?.[0];if(!file)return;try{if(file.size>12e6)throw Error("請先使用小於 12MB 的 JSON");const data=JSON.parse(await file.text());if(data.schema_version!=="starforge.unified.v2"&&data.schema_version!=="starforge.real_milky_way.v1"){if(data&&typeof data==="object"&&("nodes" in data||"starSystems" in data||"system" in data||Array.isArray(data.systems))){importedSSE=data;changed();toast("已安全保留原始 SSE JSON；不會當作真實觀測資料");e.target.value="";return}throw Error("不支援的資料 schema")}if(Array.isArray(data.stars)&&data.stars.length<=8000)stars=data.stars.map(s=>({...s,origin:s.origin||"HYG"})).filter(s=>Number.isFinite(s.x)&&Number.isFinite(s.y)&&Number.isFinite(s.z));if(Array.isArray(data.observed_planets))planets=data.observed_planets.slice(0,1000);if(Array.isArray(data.simulated_planets))simulated=data.simulated_planets.filter(s=>s.origin==="SIMULATED").slice(0,500);if(data.imported_sse&&typeof data.imported_sse==="object")importedSSE=data.imported_sse;saveFiction();setText("starTotal",stars.length);setText("exoTotal",planets.length);updateSystem();toast("星圖 JSON 匯入成功；未替你上傳到遠端");changed()}catch(err){toast("匯入失敗："+String(err.message||err))}e.target.value=""});
on("zoomin","click",()=>zoom=Math.min(3.2,zoom*1.22));on("zoomout","click",()=>zoom=Math.max(.3,zoom/1.22));on("reset","click",()=>{yaw=.35;pitch=.45;zoom=1;day=0});on("run","click",()=>{paused=!paused;$("run").textContent=paused?"▶":"Ⅱ"});
canvas.addEventListener("pointerdown",e=>{canvas.setPointerCapture(e.pointerId);const p=point(e);pointers.set(e.pointerId,p);firstPointer=p;moved=false;if(pointers.size===2){const a=[...pointers.values()];pinchStart=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y)}});
canvas.addEventListener("pointermove",e=>{if(!pointers.has(e.pointerId))return;const old=pointers.get(e.pointerId),p=point(e);pointers.set(e.pointerId,p);if(pointers.size>=2){const a=[...pointers.values()],d=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);if(pinchStart>0)zoom=Math.max(.3,Math.min(3.2,zoom*d/pinchStart));pinchStart=d;moved=true}else{yaw+=(p.x-old.x)*.008;pitch=Math.max(-1.2,Math.min(1.2,pitch-(p.y-old.y)*.005));if(firstPointer&&Math.hypot(firstPointer.x-p.x,firstPointer.y-p.y)>5)moved=true}});
canvas.addEventListener("pointerup",e=>{if(!moved&&pointers.size===1){const p=point(e),best=hit.map(x=>({...x,dist:Math.hypot(p.x-x.x,p.y-x.y)})).sort((a,b)=>a.dist-b.dist)[0];if(best&&best.dist<(best.r||16))handleHit(best)}pointers.delete(e.pointerId);if(!pointers.size){firstPointer=null;pinchStart=0}});
canvas.addEventListener("pointercancel",e=>pointers.delete(e.pointerId));canvas.addEventListener("wheel",e=>{e.preventDefault();zoom=Math.max(.3,Math.min(3.2,zoom*(e.deltaY>0?.9:1.12)))},{passive:false});
on("loadNamed","click",loadNamed);on("loadNASA","click",loadNASA);
}
function point(e){const r=canvas.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top}}
function handleHit(h){if(h.kind==="sun"){selectedSolar="earth";solarScale="inner";switchMode("solar")}else if(h.kind==="star"||h.kind==="selectedStar")selectStar(h.ref||selectedStar,true);else if(h.kind==="deep"){selectedDeep=h.ref.id;switchMode("deep")}else if(h.kind==="planet"){selectedPlanet=h.ref.id;toast(h.ref.name+": "+(h.ref.sim?"虛構行星":"NASA 已確認"))}else if(h.kind==="solar"){selectedSolar=h.ref.id;updateSolar();changed()}else if(h.kind==="small"){selectedSmall=h.ref.id;showSmallBody(h.ref);changed()}}
function parseNGCLine(row,sep){
 const a=[];let out="",q=false;
 for(let i=0;i<row.length;i++){const c=row[i];
 if(c==='"'){if(q&&row[i+1]==='"'){out+='"';i++}else q=!q}
 else if(c===sep&&!q){a.push(out);out=""}
 else out+=c}
 a.push(out);return a;
}
function ngcRA(s){
 const v=String(s||"").trim(),p=v.split(":");
 if(p.length!==3)return NaN;
 const a=p.map(Number);
 return a.every(Number.isFinite)?15*(a[0]+a[1]/60+a[2]/3600):NaN
}
function ngcDec(s){
 const v=String(s||"").trim(),p=v.replace(/^[+-]/,"").split(":");
 if(p.length!==3)return NaN;
 const a=p.map(Number);
 return a.every(Number.isFinite)?(v[0]==="-"?-1:1)*(a[0]+a[1]/60+a[2]/3600):NaN
}
async function loadOpenNGC(){
 const btn=$("loadOpenNGC");btn.disabled=true;
 setText("deepCatalogStatus","正在讀取 OpenNGC（約 4MB），請勿關閉此頁。");
 const types={"OCl":"OPEN_CLUSTER","GCl":"GLOBULAR_CLUSTER","Cl+N":"NEBULA","HII":"NEBULA","EmN":"NEBULA","DrkN":"NEBULA","RfN":"NEBULA","Neb":"NEBULA","PN":"PLANETARY_NEBULA","SNR":"SNR","*Ass":"OPEN_CLUSTER"};
 try{
 const resp=await fetch("https://raw.githubusercontent.com/mattiaverga/OpenNGC/master/database_files/NGC.csv",{cache:"force-cache"});
 if(!resp.ok)throw Error("HTTP "+resp.status);
 const csv=await resp.text();
 if(csv.length<100000||csv.length>10000000)throw Error("原始資料大小不符預期");
 const rows=csv.split(/\r?\n/).filter(Boolean),head=rows.shift()||"";
 const sep=(head.match(/;/g)||[]).length>(head.match(/,/g)||[]).length?";":",";
 const cols=parseNGCLine(head,sep);
 const pos=Object.fromEntries(cols.map((v,i)=>[v.trim().replace(/^\uFEFF/,""),i]));
 if(["Name","Type","RA","Dec"].some(k=>pos[k]===undefined))throw Error("OpenNGC 目前欄位格式與預期不同");
 let imported=0;
 const existing=new Set(deep.map(x=>String(x.id).toUpperCase().replace(/\s+/g,"")));
 for(const row of rows){
 if(imported>=1200)break;
 const x=parseNGCLine(row,sep),type=types[(x[pos.Type]||"").trim()];
 if(!type)continue;
 const ra=ngcRA(x[pos.RA]),dec=ngcDec(x[pos.Dec]);
 if(!Number.isFinite(ra)||!Number.isFinite(dec)||ra<0||ra>=360||Math.abs(dec)>90)continue;
 const id=(x[pos.Name]||"").trim();
 if(!id||existing.has(id.toUpperCase().replace(/\s+/g,"")))continue;
 const name=(x[pos["Common names"]]||"").trim();
 deep.push({id,n:id,en:name||id,type,ra,dec,ly:null,source:"OpenNGC CC BY-SA 4.0",precision:"J2000 sky position only; no reliable distance",link:"https://github.com/mattiaverga/OpenNGC"});
 existing.add(id.toUpperCase().replace(/\s+/g,""));imported++;
 }
 if(imported<50)throw Error("沒有成功解析足夠的銀河深空物件");
 deepProjection="sky";$("deepProjection").value="sky";
 updateDeep();changed();toast("已從 OpenNGC 載入 "+imported+" 個深空天體（只提供 RA／Dec）");
 }catch(e){setText("deepCatalogStatus","載入失敗，仍可使用離線 13 筆樣本："+String(e.message||e));toast("OpenNGC 連線或格式錯誤")}
 finally{btn.disabled=false}
}
async function loadNamed(){const btn=$("loadNamed");btn.disabled=true;toast("從 GitHub 下載約 3,151 顆命名恆星…");try{const r=await fetch("https://raw.githubusercontent.com/RDFZ-AI-Challenge-2026/project-star-map-3d/main/data/processed/named_stars.json");if(!r.ok)throw Error("HTTP "+r.status);const arr=await r.json();if(arr.length<1500)throw Error("資料不完整");stars=arr.filter(x=>Number.isFinite(x.x)&&Number.isFinite(x.y)&&Number.isFinite(x.z)&&x.dist_pc>0).map(x=>({id:"hyg:"+x.id,n:x.proper||x.en||x.zh||"HYG "+x.id,zh:x.zh||"",h:x.hip,d:x.dist_pc,x:x.x,y:x.y,z:x.z,s:x.spect,m:num(x.mag),lum:num(x.lum),origin:"HYG"}));setText("starTotal",fmt(stars.length,0));toast("已載入 "+fmt(stars.length,0)+" 顆命名恆星");}catch(e){toast("下載失敗；仍可使用離線樣本："+String(e.message||e))}finally{btn.disabled=false}}
async function loadNASA(){const btn=$("loadNASA");btn.disabled=true;const sql="select top 250 pl_name,hostname,sy_dist,ra,dec,pl_orbper,pl_rade,pl_orbsmax,pl_bmasse from pscomppars where sy_dist is not null and sy_dist<100 order by sy_dist asc";const url="https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query="+encodeURIComponent(sql)+"&format=json";try{const r=await fetch(url);if(!r.ok)throw Error("HTTP "+r.status);const a=await r.json();if(!Array.isArray(a)||a.length<1)throw Error("Empty NASA result");planets=a.map(p=>({n:p.pl_name,h:p.hostname,d:num(p.sy_dist),ra:num(p.ra),dec:num(p.dec),p:num(p.pl_orbper),r:num(p.pl_rade),a:num(p.pl_orbsmax),m:num(p.pl_bmasse),origin:"NASA_EXOPLANET"}));nasaRetrieved=new Date().toISOString().slice(0,10);setText("exoTotal",fmt(planets.length,0));updateSystem();toast("NASA 資料已更新，共 "+planets.length+" 筆");}catch(e){toast("NASA 瀏覽器查詢失敗（網路或 CORS）；離線樣本仍保留")}finally{btn.disabled=false}}
function installSSEBridge(){
 const trustedSSE="https://starforge-sse-full-loyuhsi.pages.dev";
 window.addEventListener("message",event=>{
   if(event.origin!==trustedSSE)return;
   const m=event.data;
   if(m?.type!=="STARFORGE_SSE_NATIVE"||m.schema_version!=="sse.starmap.v3.2")return;
   if(!m.payload||!Array.isArray(m.payload.systems))return;
   try{
     const serialized=JSON.stringify(m.payload);
     if(serialized.length>2200000){toast("SSE 原始星圖太大，請改用原生匯入");return}
     importedSSE={...m.payload,starforge_handoff:{source:"SSE_3.2_NATIVE",received_at:new Date().toISOString(),from:trustedSSE}};
     changed();
     toast("已接收 SSE 原版星圖（含 "+m.payload.systems.length+" 個恆星系）。若已啟用安全同步，將更新 TypingMind 資料。");
   }catch(e){toast("SSE 星圖接收失敗："+String(e))}
 });
}
function initialize(){for(const b of solar){const op=document.createElement("option");op.value=b.id;op.textContent=b.n;$("solarBodySelect").appendChild(op)}$("solarBodySelect").value="earth";try{$("bridgeURL").value=localStorage.getItem("sf_v2_bridge_url")||""}catch{}bridge=normalizedBridge();selectedStar=stars.find(x=>x.n==="Proxima Centauri")||stars[0];installSSEBridge();bindUI();renderStarChips();updateDeep();updateSolar();updateSSD();updateSystem();resize();deepSynthetic=$("deepSynthetic").checked;deepSeed=$("deepSeed").value;const qp=new URLSearchParams(location.search),requestedMode=qp.get("mode"),name=qp.get("star");if(name){const s=findStar(name);if(s)selectedStar=s}switchMode(allowedModes.includes(requestedMode)?requestedMode:"galaxy");if(location.hostname==="raw.githack.com"){const key=$("writeKey"),t=$("autoSync"),btn=$("syncNow");key.disabled=true;t.disabled=true;btn.disabled=true;renderSyncStatus("安全預覽限制：目前使用第三方 raw.githack.com 網頁，禁止輸入與傳送私人寫入金鑰。需要自動同步時，請先部署到自己控制的 HTTPS 網域。");}window.SF_API=Object.freeze({getSnapshot:snapshot,getSummary:summary,selectStarByName:name=>{const s=findStar(name);if(s){selectStar(s);return true}return false},setMode:switchMode,version:"3.0.0-beta"});requestAnimationFrame(draw);setText("health","● 資料已載入")}
initialize();
})();