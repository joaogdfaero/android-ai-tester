#!/usr/bin/env bash
# Setup do android-ai-tester. Rode da raiz do projeto: bash scripts/setup.sh
set -u
cd "$(dirname "$0")/.."
ok(){ echo "✓ $*"; }; warn(){ echo "! $*"; }; bad(){ echo "✗ $*"; }

echo "== Ferramentas"
command -v adb >/dev/null && ok "adb: $(adb version | head -1)" || { bad "adb ausente: sudo apt install android-tools-adb (ou platform-tools do Google)"; exit 1; }
command -v python3 >/dev/null && ok "python3: $(python3 --version)" || bad "python3 ausente"
if command -v node >/dev/null; then
  NV=$(node -p 'process.versions.node.split(".")[0]')
  if [ "$NV" -ge 20 ]; then ok "node $(node -v)"; else warn "node $(node -v) < 20: o .mcp.json usa npx com node@22 automaticamente (sem mexer no sistema)."; fi
else bad "node/npx ausente: necessário para o mobile-mcp"; fi
command -v scrcpy >/dev/null && ok "scrcpy (opcional) presente" || warn "scrcpy (opcional) ausente: útil para espelhar a tela e gravar vídeo COM áudio (sudo apt install scrcpy)"
command -v claude >/dev/null && ok "claude code presente" || warn "Claude Code não encontrado no PATH"

echo "== Config"
[ -f config/device.env ] || { cp config/device.env.example config/device.env; warn "config/device.env criado a partir do exemplo: edite TARGET_PACKAGES."; }
chmod +x tools/droid .claude/hooks/guard_device.py

echo "== Pré-baixando mobile-mcp (primeira vez demora)"
if [ "${NV:-0}" -ge 20 ]; then CMD=(npx -y @mobilenext/mobile-mcp@1.0.16); else CMD=(npx -y -p node@22 -p @mobilenext/mobile-mcp@1.0.16 mobile-mcp); fi
timeout 300 "${CMD[@]}" </dev/null >/dev/null 2>&1 || true
ok "cache do npx aquecido"

echo "== Device"
tools/droid doctor
