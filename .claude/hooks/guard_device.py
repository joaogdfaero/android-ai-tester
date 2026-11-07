#!/usr/bin/env python3
"""PreToolUse hook: protege o device Android PESSOAL do usuário.

- Bloqueia (deny) comandos adb destrutivos ou irreversíveis.
- Pede confirmação (ask) para ações que mexem em rede/estado global ou em apps fora do alvo.
- Vale para Bash (adb / tools/droid) e para as ferramentas do mobile-mcp.
Pacotes-alvo vêm de TARGET_PACKAGES em config/device.env.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2]))


def targets():
    f = ROOT / "config" / "device.env"
    if not f.exists():
        return []
    for line in f.read_text().splitlines():
        if line.strip().startswith("TARGET_PACKAGES="):
            v = line.split("=", 1)[1].strip().strip('"').strip("'")
            return [p.strip() for p in v.split(",") if p.strip()]
    return []


def decide(decision, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


DENY = [
    (r"\badb\b.*\b(reboot|root|unroot|remount|disable-verity|enable-verity|sideload|restore)\b", "reboot/root/remount/restore do device"),
    (r"\b(wipe|recovery|bootloader|fastboot)\b", "wipe/recovery/bootloader"),
    (r"MASTER_CLEAR|FACTORY_RESET|factory[_ ]?reset", "factory reset"),
    (r"\brm\s+(-\w*\s+)*(/sdcard|/storage|/data)(/|\s|$)(?!.*droid_)", "apagar arquivos do armazenamento do usuário"),
    (r"\bcontent\s+(delete|update)\b", "apagar/alterar dados de content providers (contatos, SMS...)"),
    (r"\bsettings\s+put\s+secure\b", "alterar configurações secure"),
    (r"\bpm\s+(disable|disable-user|hide|suspend|set-installer|reset-permissions)\b", "desativar/ocultar apps ou resetar permissões"),
    (r"\bdpm\b|\bcmd\s+(lock_settings|account)\b|\block_settings\b", "senha/conta/admin do device"),
    (r"\bam\s+start\b.*\b(CALL|SENDTO|SEND)\b|\b(tel|sms|smsto|mailto):", "ligar ou enviar mensagem/e-mail"),
    (r"\bservice\s+call\s+(phone|isms)\b", "ligação/SMS via service call"),
    (r"\badb\b.*\bbackup\b", "adb backup"),
]

ASK = [
    (r"\bsvc\s+(wifi|data|bluetooth|nfc)\b|\bcmd\s+(wifi|connectivity)\b|airplane_mode", "alterar rede (Wi-Fi/dados/modo avião) no seu celular pessoal"),
    (r"\bsettings\s+put\s+global\s+(?!(stay_on_while_plugged_in|window_animation_scale|transition_animation_scale|animator_duration_scale)\b)", "alterar configuração global"),
    (r"\badb\b.*\b(install|install-multiple)\b", "instalar APK no device"),
    (r"\bcmd\s+locale\b|persist\.sys\.locale|\bsetprop\b", "alterar idioma/propriedades do sistema"),
    (r"\badb\b.*\bpull\b.*(/sdcard/(DCIM|Pictures|Download|Documents|WhatsApp|Android/media))", "copiar arquivos pessoais do device"),
]


def check_target_pkg_ops(cmd, tg):
    # pm uninstall / pm clear / am force-stop em pacote que não é alvo
    for m in re.finditer(r"\b(?:pm\s+(uninstall|clear)|adb\b[^|;&]*\buninstall)\s+(?:-\S+\s+)*([\w.]+)", cmd):
        op, pkg = m.group(1) or "uninstall", m.group(2)
        if pkg not in tg:
            decide("deny", f"`{op}` em `{pkg}` bloqueado: não está em TARGET_PACKAGES (config/device.env).")
        if op == "uninstall":
            decide("ask", f"Desinstalar o app-alvo `{pkg}` apaga os dados dele. Confirmar?")
    for m in re.finditer(r"\bpm\s+(grant|revoke)\s+([\w.]+)", cmd):
        if m.group(2) not in tg:
            decide("deny", f"Alterar permissões de `{m.group(2)}` (fora do alvo) bloqueado.")


def check_bash(cmd):
    tg = targets()
    is_device = re.search(r"\badb\b|tools/droid|\bdroid\b", cmd)
    if not is_device:
        return
    for pat, why in DENY:
        if re.search(pat, cmd, re.I):
            decide("deny", f"Bloqueado pelo guard do device pessoal: {why}. Se for mesmo necessário, o usuário deve executar manualmente.")
    check_target_pkg_ops(cmd, tg)
    for pat, why in ASK:
        if re.search(pat, cmd, re.I):
            decide("ask", f"Ação sensível no device pessoal: {why}.")


def check_mcp(name, inp):
    tg = targets()
    short = name.split("__")[-1]
    pkg = inp.get("packageName") or inp.get("package") or inp.get("bundleId") or ""
    if "uninstall" in short:
        decide("deny", "Desinstalar apps pelo MCP está bloqueado no device pessoal.")
    if "install" in short:
        decide("ask", "Instalar app no device pessoal. Confirmar?")
    if short.endswith("launch_app") and pkg and tg and pkg not in tg and not pkg.startswith("com.android.settings"):
        decide("ask", f"Abrir app fora do alvo (`{pkg}`) no seu celular pessoal. Confirmar?")
    url = str(inp.get("url", ""))
    if re.match(r"(tel|sms|smsto|mailto|intent):", url, re.I):
        decide("deny", "Abrir URL de ligação/mensagem/intent bloqueado.")


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    name = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}
    if name == "Bash":
        check_bash(inp.get("command", ""))
    elif name.startswith("mcp__mobile"):
        check_mcp(name, inp)
    sys.exit(0)


if __name__ == "__main__":
    main()
