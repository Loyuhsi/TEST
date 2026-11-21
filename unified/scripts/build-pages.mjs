import {mkdirSync,copyFileSync,writeFileSync,readFileSync} from "node:fs";
import {resolve,join} from "node:path";
const root=process.cwd(),out=resolve(root,"site-dist");
for(const path of ["unified","solar-system","real-milky-way"])mkdirSync(join(out,path),{recursive:true});
for(const file of ["index.html","offline.html","style.css","data.js","exo-engine.js","app.js","TYPINGMIND-v4.md"])copyFileSync(join(root,"unified",file),join(out,"unified",file));
for(const kind of ["solar-system","real-milky-way"])copyFileSync(join(root,kind,"index.html"),join(out,kind,"index.html"));
copyFileSync(join(out,"unified","offline.html"),join(out,"index.html"));
writeFileSync(join(out,"_headers"),"/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n");
console.log("Starforge mobile frontend ready:",out);
