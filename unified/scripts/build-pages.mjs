import {mkdirSync,copyFileSync,writeFileSync,readFileSync} from "node:fs";
import {resolve,join} from "node:path";
const root=process.cwd(),out=resolve(root,"site-dist");
let offline=readFileSync(join(root,"unified/index.html"),"utf8");
offline=offline.replace('<link rel="stylesheet" href="./style.css">',()=>'<style>'+readFileSync(join(root,"unified/style.css"),"utf8")+'</style>');
for(const script of ["data.js","exo-engine.js","app.js"])offline=offline.replace('<script src="./'+script+'"></script>',()=>'<script>'+readFileSync(join(root,"unified",script),"utf8").replace(/<\/script/gi,"<\\/script")+'</script>');
writeFileSync(join(root,"unified/offline.html"),offline);
for(const path of ["unified","solar-system","real-milky-way"])mkdirSync(join(out,path),{recursive:true});
for(const file of ["index.html","offline.html","style.css","data.js","exo-engine.js","app.js","TYPINGMIND-v4.md"])copyFileSync(join(root,"unified",file),join(out,"unified",file));
const pairDir = join(out, "unified", "pair");
mkdirSync(pairDir, {recursive:true});
for (const asset of ["index.html", "pair.css", "page.js", "crypto.js"]) {
  copyFileSync(join(root, "unified", "pair", asset), join(pairDir, asset));
}
for(const kind of ["solar-system","real-milky-way"])copyFileSync(join(root,kind,"index.html"),join(out,kind,"index.html"));
copyFileSync(join(out,"unified","offline.html"),join(out,"index.html"));
writeFileSync(join(out,"_headers"),"/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n\n/unified/pair/*\n  Cache-Control: no-store\n  X-Frame-Options: DENY\n  Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; connect-src https://starforge-unified-bridge-v3.loyuhsi930821.workers.dev/api/pairing/replies/; frame-ancestors 'none'; form-action 'none'; base-uri 'none'\n");
writeFileSync(join(out,"404.html"),'<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>找不到頁面</title><p>找不到頁面。<a href="/unified/">返回星海工坊</a></p></html>');
console.log("Starforge mobile frontend ready:",out);
