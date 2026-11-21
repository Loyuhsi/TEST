// Run locally with WRITE_TOKEN from the operator's existing credential vault.
import {inboxId, pairingPage, sealWriteKey} from "../pair/crypto.js";
import {execFileSync} from "node:child_process";
import {createRequire} from "node:module";
import {fileURLToPath} from "node:url";
import {dirname, join} from "node:path";

try {
  const [code, option, ...extra] = process.argv.slice(2);
  if (!code || extra.length || (option && option !== "--publish") || !process.env.WRITE_TOKEN) throw Error("需要手機的公開配對碼，以及本機安全載入的 WRITE_TOKEN。選項為 --publish。");
  const reply = await sealWriteKey(code, process.env.WRITE_TOKEN);
  if (option === "--publish") {
    const require = createRequire(import.meta.url);
    const cli = join(dirname(require.resolve("wrangler/package.json")), "bin", "wrangler.js");
    const id = await inboxId(code);
    const expiry = reply.split(".")[1];
    const env = {...process.env};
    delete env.WRITE_TOKEN;
    execFileSync(process.execPath, [cli, "kv", "key", "put", "pair:reply:v1:" + id, reply,
      "--binding", "STARFORGE_KV", "--remote", "--expiration", expiry],
      {cwd:fileURLToPath(new URL("../", import.meta.url)), env, stdio:"pipe"});
    console.log(JSON.stringify({published:true, id, expires:Number(expiry)}));
  } else console.log(pairingPage + "#" + reply);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
