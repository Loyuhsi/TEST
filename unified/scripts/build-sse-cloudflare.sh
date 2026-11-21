#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(pwd)"
git clone --depth 1 https://github.com/FrunkQ/star-system-generator.git sse-upstream
cd sse-upstream
git fetch --depth 1 origin f2459feb3a275ce0f7d5f8ad8115c1231eb6a9dd
git checkout --detach f2459feb3a275ce0f7d5f8ad8115c1231eb6a9dd
npm ci
npm install --save-dev --legacy-peer-deps --no-audit @sveltejs/adapter-cloudflare@^7 wrangler@^4
cp LICENSE COPYING-GPL-3.0
sed -i 's|@sveltejs/adapter-auto|@sveltejs/adapter-cloudflare|' svelte.config.js
node "$ROOT/unified/sse-interop-patch.mjs"
CF_PAGES=1 npm run build
echo 'SSE full Cloudflare build complete.'
