import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import vm from "node:vm";
const root=dirname(dirname(fileURLToPath(import.meta.url)));
const code=readFileSync(join(root,"exo-engine.js"),"utf8");
const scope={window:{}};vm.runInNewContext(code,scope);
const engine=scope.window.StarforgeExoV3;assert(engine);
const stars=[
 {id:"sirius",n:"Sirius",s:"A0V",lum:22.82},
 {id:"proxima",n:"Proxima Centauri",s:"M5Ve",lum:.00006},
 {id:"pollux",n:"Pollux",s:"K0III",lum:32.09},
 {id:"trappist1",n:"TRAPPIST-1",s:"M8V",lum:.0005}
];
const confirmed=[{n:"Proxima Cen b",a:.04848,p:11.18465,m:1.055,r:1.02},{n:"Proxima Cen d",a:.02881,p:5.12338,m:.26,r:.692}];
for(const star of stars){
 const a=engine.generate(star,confirmed,{seed:"fixed-seed",diskMass:.68,metallicity:.1,dynamicalHistory:.3});
 const b=engine.generate(star,confirmed,{seed:"fixed-seed",diskMass:.68,metallicity:.1,dynamicalHistory:.3});
 assert.equal(JSON.stringify(a),JSON.stringify(b),"identical seed must reproduce");
 assert(a.simulatedPlanets.every(p=>p.source==="SIMULATED"));
 assert(a.realConfirmedPlanets.every(p=>p.source==="NASA_CONFIRMED"));
 assert.equal(a.realConfirmedPlanets.length,confirmed.length);
 assert.equal(a.realConfirmedPlanets[0].a,.04848,"preserve catalog semimajor axis");
 assert(a.simulatedPlanets.every(p=>Number.isFinite(p.a)&&p.a>0&&p.periodDays>0));
 assert(a.simulatedPlanets.every(p=>p.environment.temperatureEquilibriumK>0));
 assert(a.regions.every(r=>r.startAU>0&&r.endAU>r.startAU&&r.source==="SIMULATED"));
 assert(!a.outerCometCloud||a.outerCometCloud.source==="SIMULATED");
 assert.equal(a.schema_version,"starforge.exosystem.v3");
}
const a=engine.generate(stars[0],[],{seed:"a"}),b=engine.generate(stars[1],[],{seed:"a"});
assert.notEqual(a.priors.snowLineAU,b.priors.snowLineAU,"snow line depends on star luminosity");
assert.notEqual(JSON.stringify(a.simulatedPlanets),JSON.stringify(b.simulatedPlanets),"no copy/paste system architecture");
let diff=0;for(let i=0;i<25;i++){let x=engine.generate(stars[2],[],{seed:String(i)});let y=engine.generate(stars[2],[],{seed:String(i+1)});if(JSON.stringify(x.regions)!==JSON.stringify(y.regions))diff++}assert(diff>10,"different seeds should lead to diverse structures");
const neb={id:"NGC42",ra:83.8,dec:-5.4,type:"NEBULA",source:"OpenNGC"};
const sim=engine.imaginedDeepPosition(neb,{seed:"test"});
assert.equal(sim.source,"SIMULATED_DISTANCE");assert.equal(sim.reality,"FICTIONAL_SCENARIO");
assert.equal(JSON.stringify(sim),JSON.stringify(engine.imaginedDeepPosition(neb,{seed:"test"})));
assert.notEqual(sim.distanceLy,engine.imaginedDeepPosition(neb,{seed:"another"}).distanceLy);
assert.equal(sim.raDeg,83.8);assert.equal(sim.decDeg,-5.4);
assert(Math.abs(Math.hypot(sim.xPc,sim.yPc,sim.zPc)*3.261563777-sim.distanceLy)<.1);
const p=engine.positionAt(a.simulatedPlanets[0],12);
assert(Number.isFinite(p.xAU)&&Number.isFinite(p.yAU));
assert.equal(p.source,"ESTIMATED_KEPLER_PHASE_NOT_REAL_EPHEMERIS");
console.log("PASS Starforge Exosystem v3: reproducibility, stellar diversity, known planets, moons/regions, provenance, 3D fictional distances.");
