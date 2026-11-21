import assert from "node:assert/strict";
import {randomBytes} from "node:crypto";
import {newRecipient, openReply, requestLifetime, sealWriteKey} from "../pair/crypto.js";

const now = Math.floor(Date.now() / 1000);
const [phone, other] = await Promise.all([newRecipient(now), newRecipient(now)]);
const testKey = randomBytes(48).toString("base64url");
assert.equal(phone.privateKey.extractable, false);
await assert.rejects(crypto.subtle.exportKey("jwk", phone.privateKey));
const sealed = await sealWriteKey(phone.code, testKey, now);
assert(!sealed.includes(testKey));
assert.equal(await openReply(phone, sealed, now), testKey);
await assert.rejects(openReply(other, sealed, now));
await assert.rejects(openReply(phone, sealed.replace(String(now + 1800), String(now + 1750)), now));
await assert.rejects(openReply(phone, sealed, now + 1800));
await assert.rejects(sealWriteKey(phone.code, testKey, now + requestLifetime));
await assert.rejects(sealWriteKey("not a pairing request", testKey, now));
await assert.rejects(sealWriteKey(phone.code, "", now));
console.log("Phone pairing: recipient-only decryption, non-exportable key, expiry and tamper checks passed.");
