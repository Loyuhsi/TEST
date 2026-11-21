// Run locally with WRITE_TOKEN from the operator's existing credential vault.
import {pairingPage, sealWriteKey} from "../pair/crypto.js";

try {
  if (process.argv.length !== 3 || !process.env.WRITE_TOKEN) throw Error("需要手機的公開配對碼，以及本機安全載入的 WRITE_TOKEN。");
  const reply = await sealWriteKey(process.argv[2], process.env.WRITE_TOKEN);
  console.log(pairingPage + "#" + reply);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
