/* Starforge Exosystem Ecology v3
 * Distinct from SSE v3.2: a seeded, explicitly approximate environmental-layer model.
 * No claim of observed bodies unless present in NASA Exoplanet Archive input.
 * Designed for mobile, no external libraries, deterministic by seed.
 */
(function (root) {
  "use strict";
  const TAU=Math.PI*2, EARTH_PER_SOLAR=3.0034896149156e-6, AU_KM=149597870.7, EARTH_RADIUS_KM=6371;
  const fnv1a=s=>{let h=2166136261>>>0;for(let i=0;i<String(s).length;i++){h^=String(s).charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0};
  function rng(seed){let a=typeof seed==="number"?seed>>>0:fnv1a(seed);return ()=>{a=(a+0x6D2B79F5)>>>0;let t=Math.imul(a^(a>>>15),1|a);t^=t+Math.imul(t^(t>>>7),61|t);return ((t^(t>>>14))>>>0)/4294967296}}
  const clamp=(x,min,max)=>Math.min(max,Math.max(min,x)),lin=(r,a,b)=>a+(b-a)*r(),log=(r,a,b)=>Math.exp(lin(r,Math.log(a),Math.log(b)));
  const choose=(r,a)=>a[Math.min(a.length-1,Math.floor(r()*a.length))];
  const coin=(r,p)=>r()<clamp(p,0,1);
  const finite=v=>v!==null&&v!==undefined&&v!==""&&Number.isFinite(Number(v))?Number(v):null;
  const spectralMass={
    O:[18,60],B:[2.2,17],A:[1.45,2.2],F:[1.1,1.45],
    G:[.83,1.10],K:[.55,.84],M:[.09,.55],L:[.03,.08],T:[.016,.06],Y:[.004,.03]
  };
  function starPhysical(star,r){
    const spectral=String(star.s||star.spect||"").trim().toUpperCase(),type=spectral.charAt(0);
    const lu=finite(star.lum);
    const base=spectralMass[type]||[.65,1.5];
    // A luminosity-derived stellar mass is only a main-sequence proxy.
    const giant=/I{1,3}|IV|GIANT|SUPERGIANT/.test(spectral);
    const fromL=lu>0?Math.pow(lu,1/(giant?5.3:3.5)):null;
    const nominal=fromL&&Number.isFinite(fromL)?clamp(fromL,base[0],base[1]):(base[0]+base[1])*.5;
    const mass=clamp(nominal*lin(r,.94,1.06),.018,55);
    const massSource=finite(star.massSolar)>0?(star.origin==="SIMULATED"?"SIMULATED_INPUT":"OBSERVED"):fromL?"DERIVED_FROM_LUMINOSITY":"SPECTRAL_PRIOR";
    const M=finite(star.massSolar)>0?finite(star.massSolar):mass;
    const L=lu>0?lu:clamp(Math.pow(M,3.5),.00005,200000);
    const luminositySource=lu>0?(star.origin==="SIMULATED"?"SIMULATED_INPUT":"CATALOG_VALUE"):"INFERRED_MASS_LUMINOSITY";
    const life=clamp(10*Math.pow(M,-2.5),.04,100);
    return {massSolar:+M.toFixed(4),luminositySolar:+L.toPrecision(5),spectralType:spectral||"UNKNOWN",
      metallicityMeasured:finite(star.feh),massSource,luminositySource,agePriorGyr:[.1,Math.min(13.6,life)],
      provenance:star.origin==="SIMULATED"?"SIMULATED_STAR":"STAR_OBSERVED_WITH_INFERRED_PHYSICS",uncertainty:massSource==="OBSERVED"?"other parameters may remain estimated":"stellar mass not measured; broad prior"};
  }
  function planetMassEarth(p){
    const m=finite(p.m??p.massEarth);
    if(m>0)return {mass:m,method:"INPUT_REPORTED"};
    const rad=finite(p.r??p.radiusEarth);
    if(rad>0){
      const estimated=rad<1.5?Math.pow(rad,3.2):rad<4?2.7*Math.pow(rad,1.4):rad<10?17*Math.pow(rad/4,1.55):318*Math.pow(rad/11.2,1.4);
      return {mass:clamp(estimated,.001,4500),method:"DERIVED_FROM_RADIUS_NONUNIQUE"};
    }
    return {mass:null,method:"UNKNOWN"};
  }
  function keplerDays(a,mSun,planetEarth=0){return 365.2568983*Math.sqrt(a*a*a/Math.max(.001,mSun+planetEarth*EARTH_PER_SOLAR))}
  function fromPeriod(period,mSun){return Math.cbrt(Math.pow(period/365.2568983,2)*mSun)}
  function hillMutual(a1,a2,m1,m2,ms){return ((a1+a2)/2)*Math.cbrt(((m1||1)+(m2||1))*EARTH_PER_SOLAR/Math.max(.001,ms*3))}
  function allowed(slots,candidate,mass,ms,dynamism){
    for(const p of slots){
      if(!Number.isFinite(p.a))continue;
      const diff=Math.abs(p.a-candidate);
      const safety=hillMutual(p.a,candidate,p.massEarth||1,mass||1,ms)*(7+5*dynamism);
      if(diff<Math.max(safety,Math.min(candidate,p.a)*.12))return false
    }
    return true
  }
  const phase=r=>+(r()*TAU).toFixed(5);
  function environmentPlanet(p,phys,dynamism){
    const a=p.a;const L=phys.luminositySolar;
    const temp=278.4*Math.pow(L,.25)/Math.sqrt(Math.max(.001,a));
    const mass=p.massEarth;
    const g=mass&&p.radiusEarth?9.80665*mass/(p.radiusEarth*p.radiusEarth):null;
    const escape=mass&&p.radiusEarth?11.186*Math.sqrt(mass/p.radiusEarth):null;
    const vol=mass===null?"UNKNOWN":mass>30?"HIGH_GASEOUS":mass>5?"VOLATILES_LIKELY":temp>430?"HOT_DRY":temp<145?"ICE_POSSIBLE":"UNDETERMINED";
    return {temperatureEquilibriumK:+temp.toFixed(1),temperatureSource:"SIMPLE_BLACKBODY_APPROX",surfaceTemperatureK:null,
      surfaceGravityMs2:g===null?null:+g.toFixed(2),escapeVelocityKmS:escape===null?null:+escape.toFixed(2),
      atmosphereModel:vol,habitability:"NOT_ESTABLISHED",tidalLock:"NOT_EVALUATED",orbitalInstabilityRisk:dynamism>.7&&p.eccentricity>.18?"ELEVATED":"NOT_CHECKED"};
  }
  function generate(star,observed=[],options={}){
    if(!star||typeof star!=="object")throw Error("star required");
    const id=String(star.id||star.n||star.name||"star");
    const seed=String(options.seed??("exo:"+id)),r=rng(seed),phys=starPhysical(star,r);
    const metallicity=clamp(finite(options.metallicity)??((phys.metallicityMeasured??0)+lin(r,-.18,.18)), -1.5,.6);
    const diskMass=clamp(finite(options.diskMass)??lin(r,.2,.9),.05,1);
    const dynamic=clamp(finite(options.dynamicalHistory)??lin(r,.08,.7),.01,1);
    const age=clamp(finite(options.ageGyr)??lin(r,...phys.agePriorGyr),.01,13.6);
    const luminosity=phys.luminositySolar,mass=phys.massSolar;
    const snowLine=2.7*Math.sqrt(luminosity);
    const habitableZone=[Math.sqrt(luminosity/.95),Math.sqrt(luminosity/.35)];
    const diskOuter=clamp((18+mass*18)*(.65+diskMass*1.25),4,180);
    const target=clamp(Math.round((1+7*diskMass+2.4*Math.max(-.6,metallicity))*(.8+mass*.1)),1,14);
    const maxBodies=clamp(finite(options.maxBodies)??target,1,24);
    const output=[],reported=[];
    let rindex=0;
    for(const p of observed){
      const inputA=finite(p.a??p.semiMajorAxisAU),period=finite(p.p??p.periodDays),knownMass=planetMassEarth(p);
      const a=inputA>0?inputA:period>0?fromPeriod(period,mass):null;
      reported.push({id:"real:"+(p.n||p.name||rindex++),name:String(p.n||p.name||"confirmed exoplanet"),
        source:"NASA_CONFIRMED",a:a>0?+a.toPrecision(6):null,aSource:inputA>0?"NASA_REPORTED":a?"KEPLER_DERIVED_FROM_OBSERVED_PERIOD":"UNKNOWN",
        periodDays:period>0?period:a?keplerDays(a,mass,knownMass.mass||0):null,
        periodSource:period>0?"NASA_REPORTED":a?"KEPLER_DERIVED":"UNKNOWN",massEarth:knownMass.mass,massSource:knownMass.method,
        radiusEarth:finite(p.r??p.radiusEarth),eccentricity:finite(p.eccentricity),inclinationDeg:finite(p.inclinationDeg),
        positionPhase:phase(r),estimate:false,observational:"MEASURED_OR_DERIVED_FIELDS_LABELLED",kind:"confirmed_exoplanet"});
    }
    const occupied=reported.filter(x=>x.a).map(x=>({a:x.a,massEarth:x.massEarth||3}));const used=occupied.slice();
    const inner=clamp(.035*Math.sqrt(luminosity),.006,.65),outer=Math.max(diskOuter,Math.max(1,...occupied.map(x=>x.a))*1.9);
    const attempts=maxBodies*24;
    let placed=0;
    for(let attempt=0;attempt<attempts&&placed<maxBodies;attempt++){
      const a=log(r,inner,outer);
      const cold=a>snowLine;
      const giantChance=clamp(diskMass*(cold?.35:.045)*(mass>.35?1:.17)*Math.pow(10,metallicity*.42),.008,.55);
      const isGiant=coin(r,giantChance);
      const kind=isGiant?(coin(r,.7)?"gas_giant":"ice_giant"):
        cold?(coin(r,.44)?"icy_dwarf":coin(r,.5)?"ice_planet":"sub_neptune"):
        (coin(r,.44)?"rocky":coin(r,.42)?"super_earth":"sub_neptune");
      const pe=kind==="gas_giant"?log(r,35,2500):kind==="ice_giant"?log(r,8,85):
        kind==="sub_neptune"?log(r,2,18):kind==="super_earth"?log(r,1.4,8):
        kind==="icy_dwarf"?log(r,.0007,.05):log(r,.07,4.5);
      if(!allowed(used,a,pe,mass,dynamic))continue;
      const ecc=clamp(-Math.log(Math.max(1e-7,1-r()))*(.012+dynamic*.095),.002,.62);
      const inclination=clamp(-Math.log(Math.max(1e-7,1-r()))*(.3+dynamic*2),.05,33);
      const radius=kind==="gas_giant"?clamp(8+Math.log10(pe)*1.1,7,16):kind==="ice_giant"?clamp(2+Math.sqrt(pe)*.52,2,6.5):Math.pow(pe,1/(kind==="icy_dwarf"?3.3:2.6));
      const body={id:"sim:"+id+":"+placed,name:(star.n||star.name||"star")+" • "+(placed+1),kind,source:"SIMULATED",
        a:+a.toPrecision(6),aSource:"SEEDED_DISK_MODEL",massEarth:+pe.toPrecision(5),massSource:"STOCHASTIC_FORMATION_PRIOR",
        radiusEarth:+radius.toFixed(3),radiusSource:"MASS_RADIUS_APPROX",eccentricity:+ecc.toFixed(4),
        inclinationDeg:+inclination.toFixed(3),periodDays:+keplerDays(a,mass,pe).toFixed(3),periodSource:"KEPLER_ESTIMATE",positionPhase:phase(r),
        estimate:true,observational:"NONE",moons:[],rings:null};
      body.environment=environmentPlanet(body,phys,dynamic);
      if(["gas_giant","ice_giant"].includes(kind)||coin(r,cold?.33:.12)){
        const hill=a*Math.cbrt(pe*EARTH_PER_SOLAR/(3*mass));
        const rkm=body.radiusEarth*EARTH_RADIUS_KM,innerMoon=Math.max(rkm*2.8/AU_KM,1e-6);
        const outerMoon=hill*.36;
        const n=outerMoon>innerMoon?Math.floor(r()*Math.min(15,2+Math.sqrt(pe)*.35)):0;
        for(let j=0;j<n;j++){let orbit=log(r,innerMoon,outerMoon),m=clamp(log(r,1e-5,kind==="gas_giant"?.05:.004),1e-6,.15);
          body.moons.push({id:body.id+":moon:"+j,name:body.name+" m"+(j+1),source:"SIMULATED",aAU:+orbit.toPrecision(5),
            periodDays:+keplerDays(orbit,pe*EARTH_PER_SOLAR,m).toPrecision(5),massEarth:+m.toPrecision(5),model:"Hill_fraction_with_Roche_floor"});
        }
        if(kind==="gas_giant"&&coin(r,.65))body.rings={source:"SIMULATED",type:choose(r,["icy_rings","dusty_ringlets","broad_rings","diffuse_torus"]),opticalDepth:+lin(r,.05,.9).toFixed(2)}
      }
      used.push({a,massEarth:pe});output.push(body);placed++;
    }
    output.sort((a,b)=>a.a-b.a);
    const allPlanets=[...reported,...output].filter(x=>x.a).sort((a,b)=>a.a-b.a);
    const giants=allPlanets.filter(x=>x.massEarth>50&&x.a>1.15), outerGiant=giants.slice().sort((a,b)=>b.a-a.a)[0];
    const belts=[];
    const occupiedInterval=allPlanets.filter(x=>x.massEarth>15).map(x=>[x.a*.75,x.a*1.34]);
    function belt(name,type,start,end,density,why,extra={}){
      if(!Number.isFinite(start)||!Number.isFinite(end)||start<0||end<=start)return;
      const overlaps=occupiedInterval.filter(([a,b])=>start<b&&end>a);
      belts.push({id:"region:"+type+":"+belts.length,name,type,startAU:+start.toPrecision(5),endAU:+end.toPrecision(5),
       source:"SIMULATED",densityRelative:+clamp(density,0,.99).toFixed(3),formationRationale:why,
       uncertainties:"Idealized reservoir distribution, not resolved orbits",giantOverlapCount:overlaps.length,...extra})
    }
    const preSnow=Math.max(inner*1.3,snowLine*.65),postSnow=snowLine*1.32;
    belt("inner_debris_belt","INNER_DEBRIS",Math.max(inner*.8,.02),preSnow*.72,lin(r,.05,.38)*diskMass,
         "metallic and silicate planetesimal remnants");
    if(coin(r,.25+diskMass*.5))belt("frost_line_asteroid_reservoir","ASTEROID_BELT",
      preSnow,postSnow,lin(r,.2,.85)*diskMass,"volatile condensation transition and giant perturbations",
      {snowLineAU:+snowLine.toFixed(3)});
    for(const planet of giants){if(planet.eccentricity!==null&&planet.eccentricity>.18)continue;if(coin(r,.2+.45*(1-dynamic))){
      const width=planet.a*(.015+lin(r,.004,.08));
      belt("trojan_"+planet.name,"TROJAN_CLOUD",planet.a-width,planet.a+width,lin(r,.08,.66),
       "co-orbital L4/L5 reservoirs; not a complete circular belt",
       {hostPlanetId:planet.id,librationCenterDeg:[60,300]});
    }}
    const kuiperStart=Math.max(outerGiant?outerGiant.a*1.25:snowLine*2.7,postSnow*1.7,2.5);
    const kuiperEnd=clamp(kuiperStart*lin(r,1.4,3.2),kuiperStart*1.1,300);
    if(coin(r,.35+diskMass*.45)){
      belt("outer_icy_planetesimals","KUIPER_ANALOGUE",kuiperStart,kuiperEnd,lin(r,.2,.82)*diskMass,
      "ice-rich planetesimal reservoir beyond giant planets",
      {architecture:"smooth_or_resonant",resonances:outerGiant?["3:2","2:1","5:2"]:[]})
    }
    if(outerGiant&&coin(r,.25+.6*dynamic))belt("scattered_disc","SCATTERED_DISC",kuiperStart*.9,kuiperEnd*lin(r,2,6),lin(r,.04,.25),
    "scattering by exterior giant planet");
    const cloudChance=clamp(.35+.5*(1-dynamic)+.12*Math.log1p(mass)-.2*(age<.1),0,1);
    let cloud=null;
    if(coin(r,cloudChance)){
      const innerCloud=clamp(kuiperEnd*lin(r,12,45),150,15000),
        outerCloud=clamp(50000*Math.pow(mass,.55)*lin(r,.25,1.5),2000,180000);
      cloud={id:"cloud:"+id,kind:"COMET_RESERVOIR",source:"SIMULATED",name:choose(r,["distant_isotropic_cloud","flattened_comet_halo","weak_outer_cloud","asymmetric_comet_reservoir"]),
        innerAU:+Math.min(innerCloud,outerCloud*.28).toFixed(1),outerAU:+outerCloud.toFixed(1),
        densityFalloffPower:+lin(r,2.5,4.7).toFixed(3),anisotropy:+lin(r,.3,1).toFixed(2),
        survivalProbability:+cloudChance.toFixed(3),uncertainty:"Not directly observed for any external star; galactic tides and encounters not simulated"};
    }
    const resonance=giants.map(g=>({host:g.name,possibleGaps:["1:2","2:3","3:5"],note:"potential resonance zones, not numerically integrated"}));
    return {schema_version:"starforge.exosystem.v3",generator:"StarforgeExoEnvironment",generatorVersion:"3.0.0",seed,starId:id,starName:String(star.n||star.name||id),
      origin:star.origin==="SIMULATED"?"SIMULATED_STAR_WITH_SIMULATED_ENVIRONMENT":"CATALOG_STAR_WITH_SIMULATED_ENVIRONMENT",physicalStar:phys,
      priors:{metallicity,diskMass,dynamicalHistory:dynamic,ageGyr:age,habitableZoneAU:habitableZone.map(v=>+v.toFixed(4)),
        snowLineAU:+snowLine.toFixed(4),diskOuterAU:+diskOuter.toFixed(3),dataQuality:"star/planet measurements mixed with parameter priors"},
      realConfirmedPlanets:reported,simulatedPlanets:output,regions:belts,outerCometCloud:cloud,
      resonanceAnnotations:resonance,backgroundBelts:belts.length,planetCount:output.length,knownCount:reported.length,
      limitations:["not full SSE physics","not N-body integrated","no absolute orbital ephemeris","debris density is procedural",
        "star mass and age may be estimated","cloud dimensions are theoretical","do not conflate simulated and observed"]};
  }
  function positionAt(planet,day=0){
    if(!(planet&&planet.a>0&&planet.periodDays>0))return null;
    const e=clamp(finite(planet.eccentricity)??0,0,.95);
    const M=(finite(planet.positionPhase)||0)+TAU*(day/planet.periodDays);
    let E=M;for(let i=0;i<12;i++){const f=E-e*Math.sin(E)-M,df=1-e*Math.cos(E);E-=f/df}
    const x=planet.a*(Math.cos(E)-e),y=planet.a*Math.sqrt(1-e*e)*Math.sin(E);
    return {xAU:x,yAU:y,rAU:Math.hypot(x,y),source:"ESTIMATED_KEPLER_PHASE_NOT_REAL_EPHEMERIS"};
  }
  function imaginedDeepPosition(object,opts={}){
    const id=String(object?.id||object?.n||"deep"),seed=String(opts.seed??"milkyway-unknown-v3");
    const r=rng(seed+"|"+id),type=String(object?.type||"NEBULA").toUpperCase(),ra=finite(object?.ra),dec=finite(object?.dec);
    if(ra===null||dec===null)throw Error("Deep sky RA and Dec required");
    // Stable catalogue direction is retained. We sample the *radial distance* only.
    // Values below are broad storytelling priors, NOT object-specific measured distances.
    const ranges={NEBULA:[150,20000],PLANETARY_NEBULA:[250,12000],SNR:[700,35000],OPEN_CLUSTER:[100,11000],
      GLOBULAR_CLUSTER:[5000,160000],PULSAR:[1500,85000],BLACK_HOLE:[1600,100000],BROWN_DWARF:[1.5,350],
      MOLECULAR_CLOUD:[120,22000],UNKNOWN:[500,90000]};
    const base=ranges[type]||ranges.UNKNOWN;
    const distLy=clamp(log(r,base[0],base[1]),base[0],base[1]),d=distLy/3.261563777;
    const a=ra*Math.PI/180,b=dec*Math.PI/180;
    return {id,raDeg:ra,decDeg:dec,distanceLy:+distLy.toFixed(2),xPc:+(d*Math.cos(a)*Math.cos(b)).toFixed(5),
      yPc:+(d*Math.sin(a)*Math.cos(b)).toFixed(5),zPc:+(d*Math.sin(b)).toFixed(5),source:"SIMULATED_DISTANCE",
      skyDirectionSource:object?.source||"CATALOG_RA_DEC",seed,priorRangeLy:base,
      reality:"FICTIONAL_SCENARIO",notes:"Not a measured 3D coordinate. Real sky direction with synthetic radial distance."};
  }
  root.StarforgeExoV3=Object.freeze({generate,positionAt,imaginedDeepPosition,fnv1a,rng,version:"3.0.0"});
})(typeof window!=="undefined"?window:globalThis);
