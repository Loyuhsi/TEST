// Only public pairing requests and recipient-encrypted replies leave the two devices.
const encoder = new TextEncoder();
const keyParams = {name: "RSA-OAEP", hash: "SHA-256"};
const origin = "https://starforge-unified-v3-loyuhsi.pages.dev";
export const pairingPage = origin + "/unified/pair/";
export const inboxBase = "https://starforge-unified-bridge-v3.loyuhsi930821.workers.dev/api/pairing/replies/";
export async function inboxId(code) {
  const digest = await crypto.subtle.digest("SHA-256", encoder.encode(code));
  return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("");
}
export const requestLifetime = 24 * 60 * 60;
const replyLifetime = 30 * 60;
const seconds = () => Math.floor(Date.now() / 1000);

function encode(bytes) {
  return btoa(String.fromCharCode(...new Uint8Array(bytes))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function decode(text) {
  return Uint8Array.from(atob(text.replace(/-/g, "+").replace(/_/g, "/")), ch => ch.charCodeAt(0));
}

function parseRequest(code, now) {
  const match = /^SFPAIR1\.(\d{10})\.([A-Za-z0-9_-]{512})$/.exec(code);
  if (!match) throw Error("配對碼格式錯誤。請從 iPhone 重新複製完整的公開配對碼。");
  const created = Number(match[1]);
  if (created > now + 300 || created + requestLifetime <= now) throw Error("配對已逾時。請在 iPhone 建立新的配對。");
  const n = decode(match[2]);
  if (!(n[0] & 128) || !(n[n.length - 1] & 1)) throw Error("配對公鑰無效。");
  return {n: match[2], created};
}

function encryptionParams(code, expires) {
  return {name: "RSA-OAEP", label: encoder.encode([pairingPage, "WRITE", code, String(expires)].join("\n"))};
}

function checkWriteKey(value) {
  if (!/^[A-Za-z0-9_-]{64}$/.test(value)) throw Error("星海工坊寫入金鑰格式錯誤。");
}

export async function newRecipient(now = seconds()) {
  const pair = await crypto.subtle.generateKey({
    ...keyParams, modulusLength: 3072, publicExponent: new Uint8Array([1, 0, 1])
  }, false, ["encrypt", "decrypt"]);
  const {n} = await crypto.subtle.exportKey("jwk", pair.publicKey);
  return {code: "SFPAIR1." + now + "." + n, expires: now + requestLifetime, privateKey: pair.privateKey};
}

export async function sealWriteKey(code, value, now = seconds()) {
  const {n, created} = parseRequest(code, now);
  checkWriteKey(value);
  const key = await crypto.subtle.importKey("jwk", {kty: "RSA", n, e: "AQAB"}, keyParams, false, ["encrypt"]);
  const expires = Math.min(now + replyLifetime, created + requestLifetime);
  const ciphertext = await crypto.subtle.encrypt(encryptionParams(code, expires), key, encoder.encode(value));
  return "SFBOX1." + expires + "." + encode(ciphertext);
}

export async function openReply(recipient, reply, now = seconds()) {
  const {created} = parseRequest(recipient.code, now);
  const match = /^SFBOX1\.(\d{10})\.([A-Za-z0-9_-]{512})$/.exec(reply);
  if (!match) throw Error("領取連結不完整。請重新開啟原連結。");
  const expires = Number(match[1]);
  if (expires <= now) throw Error("領取連結已逾時。請重新送出這台手機的公開配對碼。");
  if (expires > created + requestLifetime || expires > now + replyLifetime + 300) throw Error("領取時間無效。請核對手機時間。");
  let plaintext;
  try {
    plaintext = await crypto.subtle.decrypt(encryptionParams(recipient.code, expires), recipient.privateKey, decode(match[2]));
  } catch {
    throw Error("無法解開這個連結。請用建立配對時的同一個 Safari 瀏覽器開啟完整連結。");
  }
  const token = new TextDecoder().decode(plaintext);
  new Uint8Array(plaintext).fill(0);
  checkWriteKey(token);
  return token;
}
