import {inboxBase, inboxId, newRecipient, openReply} from "./crypto.js";

const element = id => document.getElementById(id);
const now = () => Math.floor(Date.now() / 1000);
const setStatus = message => { element("status").textContent = message; };
let db;
let recipient;
let writeKey = "";
let replyExpires = 0;
// Keep the encrypted fragment until the matching browser has saved it.
const incoming = location.hash.slice(1);

function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("starforge-phone-pair-v1", 1);
    request.onupgradeneeded = () => request.result.createObjectStore("device");
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

// Read and conditionally update the one device slot in a single transaction.
function deviceSlot(update) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction("device", update ? "readwrite" : "readonly");
    const store = tx.objectStore("device");
    const read = store.get("active");
    let result;
    read.onsuccess = () => {
      result = read.result;
      if (!update) return;
      const next = update(result);
      if (next === result) return;
      if (next) store.put(next, "active");
      else store.delete("active");
      result = next;
    };
    tx.oncomplete = () => resolve(result);
    tx.onabort = () => reject(tx.error || Error("裝置儲存空間無法使用。"));
  });
}

function clearSecret() {
  writeKey = "";
  element("password").value = "";
  element("manual-key").hidden = true;
  element("received").hidden = true;
}

function showCode() {
  element("public-code").value = recipient.code;
  element("request").hidden = false;
}

async function acceptReply(device, envelope) {
  const secret = await openReply(device, envelope);
  const saved = await deviceSlot(current => {
    if (current?.code !== device.code || current.envelope === envelope) return current;
    return {...current, envelope};
  });
  if (saved?.code !== device.code || recipient?.code !== device.code) throw Error("本機配對已更換。請重新開啟配對首頁。");
  if (location.hash) history.replaceState(null, "", location.pathname);
  writeKey = secret;
  replyExpires = Number(envelope.split(".")[1]);
  element("request").hidden = true;
  element("received").hidden = false;
  setStatus("金鑰已在這支手機解開。請先存入「密碼」。");
}

async function checkInbox() {
  const device = recipient;
  const button = element("check-inbox");
  if (!device || button.disabled) return;
  button.disabled = true;
  setStatus("正在查詢這個配對碼的加密回覆…");
  try {
    const id = await inboxId(device.code);
    const response = await fetch(inboxBase + id, {credentials:"omit", cache:"no-store", referrerPolicy:"no-referrer", redirect:"error"});
    if (recipient?.code !== device.code) return;
    if (response.status === 404) {
      setStatus("配對碼末八碼 " + device.code.slice(-8) + " 暫無可領取的回覆。可稍候再按「領取寫入金鑰」。");
      return;
    }
    if (!response.ok) throw Error("暫時無法連線至領取服務，請稍後再試。");
    const {envelope} = await response.json();
    await acceptReply(device, envelope);
  } catch (error) {
    if (recipient?.code === device.code) setStatus(error.name === "Error" ? error.message : "領取服務連線中斷。請再按一次「領取寫入金鑰」。");
  } finally { button.disabled = false; }
}

async function start() {
  if (!db) db = await openDatabase();
  recipient = await deviceSlot();
  const existing = recipient && recipient.expires > now();
  if (!existing) {
    if (incoming) throw Error("這個 Safari 找不到有效的配對。請在建立配對時使用的 Safari 開啟領取連結，或返回配對首頁重新開始。");
    const candidate = await newRecipient();
    recipient = await deviceSlot(current => current?.expires > now() ? current : candidate);
  }
  element("forget").hidden = false;
  const envelope = incoming || recipient.envelope;
  if (envelope) {
    try { await acceptReply(recipient, envelope); return; }
    catch (error) {
      clearSecret();
      if (incoming) { showCode(); setStatus(error.message); return; }
    }
  }
  showCode();
  if (existing) await checkInbox();
  else setStatus("這支手機的配對碼已備妥，有效 24 小時。");
}

element("check-inbox").onclick = checkInbox;
element("copy-code").onclick = async () => {
  try {
    await navigator.clipboard.writeText(recipient.code);
    setStatus("公開配對碼已複製。請貼回原來的對話。");
  } catch {
    document.querySelector("details").open = true;
    element("public-code").select();
    setStatus("請按住已選取的公開配對碼，點「拷貝」。");
  }
};

function stillAvailable() {
  if (writeKey && now() < replyExpires) return true;
  clearSecret();
  showCode();
  setStatus("領取連結已逾時。請重新送出公開配對碼。");
  return false;
}

element("copy-key").onclick = async () => {
  if (!stillAvailable()) return;
  try {
    await navigator.clipboard.writeText(writeKey);
    setStatus("WRITE 金鑰已複製。現在可貼入 iPhone 的「密碼」。");
  } catch {
    if (!stillAvailable()) return;
    element("manual-key").hidden = false;
    element("password").value = writeKey;
    element("password").select();
    setStatus("Safari 未允許自動拷貝。請使用下方的密碼欄。");
  }
};

element("forget").onclick = async () => {
  if (!confirm("清除後，這支手機無法再次開啟本次領取連結。結束配對？")) return;
  try {
    await deviceSlot(current => current?.code === recipient.code ? undefined : current);
    clearSecret();
    recipient = undefined;
    element("public-code").value = "";
    element("request").hidden = element("forget").hidden = true;
    setStatus("本機配對資料已清除。");
  } catch { setStatus("無法清除配對資料，請重試。"); }
};

window.addEventListener("pagehide", clearSecret);
window.addEventListener("hashchange", () => { if (location.hash) location.reload(); });
window.addEventListener("pageshow", event => { if (event.persisted) location.reload(); });
document.addEventListener("visibilitychange", () => {
  if (!document.hidden && writeKey) stillAvailable();
});
start().catch(error => {
  setStatus(error.name === "Error" ? error.message : "Safari 無法儲存配對資料。請用一般 Safari 分頁開啟並允許網站儲存資料。");
  element("restart").hidden = false;
});
