---
name: android-device
description: Como controlar o device Android pessoal do usuário (via mobile-mcp e tools/droid/adb) e coletar evidências (screenshot, vídeo, logcat, crashes, About Device) com segurança. Carregue antes de qualquer interação com o celular, inclusive dentro das skills utest-android-test-case e android-exploratory.
---

# Controlar o device Android

O device é o **celular pessoal** do usuário. Trate-o como produção: nada irreversível, nada fora do app-alvo sem perguntar, nada de dados pessoais nas evidências.

## 0. Antes de começar (toda sessão)

1. `tools/droid doctor`: precisa mostrar exatamente 1 device `device` (não `unauthorized`/`offline`) e o app-alvo instalado com versão. Se falhar, peça ao usuário para desbloquear o celular, aceitar a chave RSA ou reconectar (USB ou `adb connect`).
2. `tools/droid run new <app>-<tema>`: cria `runs/AAAA-MM-DD_<slug>/` e define a run atual.
3. `tools/droid prep`: liga Não perturbe, mantém a tela acesa, mostra toques, zera o volume de mídia. **Sempre** rode `tools/droid restore` no fim (também se a sessão for interrompida).
4. `tools/droid log start`: logcat da sessão em `runs/<run>/logs/`. `tools/droid log stop` no fim lista crash/ANR/exceções.
5. `tools/droid info --out runs/<run>/evidence/about-device`: dados do device e versão do app.

## 1. Duas camadas de controle

| Use | Para |
|---|---|
| **mobile-mcp** (`mcp__mobile-mcp__*`) | navegar: `mobile_list_elements_on_screen` (árvore de acessibilidade com coordenadas), `mobile_take_screenshot` (você **vê** a tela), `mobile_click_on_screen_at_coordinates`, `mobile_swipe_on_screen`, `mobile_type_keys` (aceita acentos), `mobile_press_button` (BACK/HOME/ENTER/VOLUME), `mobile_launch_app`, `mobile_set_orientation`. Na 1ª chamada, `mobile_list_available_devices` + `mobile_use_device` se pedir. |
| **tools/droid** | evidências e estado: `shot`, `rec start/stop`, `log`, `crashes`, `info`, `note`, `ui` (lista compacta com índice), `tap-el N`, `kill-bg`, `set dark/font/battery/rotate/anim`, `perm grant/revoke`, `restore`. Funciona mesmo se o MCP cair. |

Ciclo de cada ação: **observar → agir → verificar**.
- Observar: prefira a lista de elementos (`mobile_list_elements_on_screen` ou `tools/droid ui`), que é barata e precisa. Use screenshot quando precisar avaliar visual (layout, corte de texto, sobreposição, cores, imagem quebrada) ou quando a árvore vier vazia (WebView, Flutter, jogos, Compose sem semântica).
- Agir: toque no **centro** do elemento. Para texto, toque no campo antes de digitar.
- Verificar: depois de cada ação, observe de novo e confirme que a tela mudou como esperado. Nunca assuma sucesso. Se nada mudou, espere 1–2 s e observe novamente antes de repetir o toque (toque duplo acidental gera falso bug).

Coordenadas são em pixels físicos do device (`adb shell wm size`). Se usar screenshot redimensionada, converta.

## 2. Evidências

- Screenshot: `tools/droid shot <pasta>/NN-descricao.png`.
- Vídeo: `tools/droid rec start <pasta>/NN-descricao.mp4` → executa os passos → `tools/droid rec stop`. Limite de 180 s por vídeo (`screenrecord`); **sem áudio**. O vídeo mostra toques (por causa do `prep`) e data/hora (`--bugreport`). Se o caso exigir áudio, avise o usuário para gravar com `scrcpy --record arquivo.mp4` (Android 11+) ou pelo gravador do próprio celular.
- Logs: para bug, recorte do logcat com o trecho relevante (`grep` pelo pacote/PID e horário) em `bug-N-logcat.txt`. Crash/ANR: `tools/droid crashes`.
- Notas: `tools/droid note "..." --step <pasta>` (data/hora com fuso).
- **Privacidade antes de salvar:** olhe cada screenshot/vídeo. Se aparecer notificação pessoal, nome/telefone/e-mail que não seja da conta de teste, foto pessoal ou outro app, descarte e refaça. Telas com `FLAG_SECURE` (banco, senha) saem pretas: isso é comportamento do app, não bug.

## 3. Regras de segurança (o hook `.claude/hooks/guard_device.py` reforça)

- Só opere o(s) app(s) em `TARGET_PACKAGES` (config/device.env). Abrir Configurações do Android para ver versão/permissões é ok. Outros apps: pergunte.
- **Nunca**: reboot, factory reset, root, apagar arquivos do usuário, desinstalar/limpar outro app, mexer em senha/conta Google, ligar, mandar SMS/e-mail/mensagem para contatos reais, compras, assinaturas, pagamentos, aceitar termos em nome do usuário.
- **Pergunte antes** (AskUserQuestion): desligar Wi-Fi/dados/modo avião (pode derrubar o próprio adb por Wi-Fi), instalar APK, mudar idioma do sistema, `droid clear` (apaga login do app), compartilhar conteúdo para fora do app, qualquer ação com dinheiro.
- Credenciais da conta de teste: não grave em arquivos da run. Se precisar logar, peça ao usuário para digitar no device, ou peça que ele cole a senha no chat só para aquela sessão.
- Teclado: o texto digitado aparece no vídeo. Não digite nada pessoal.

## 4. Simulações úteis (todas desfeitas por `droid restore`)

- Interrupção/background: `droid key HOME` → `droid key APP_SWITCH` → voltar ao app. Morte de processo: `droid kill-bg` e reabrir pelos Recentes (estado deve ser restaurado).
- Rotação: `droid set rotate 1` (paisagem), `0` (retrato), `auto`.
- Tema escuro: `droid set dark on|off`. Fonte grande: `droid set font 1.3` (ou `2.0`).
- Bateria baixa (simulada): `droid set battery 5` / `reset`.
- Animações desligadas (vídeos e toques mais estáveis): `droid set anim off`.
- Permissões do app-alvo: `droid perm revoke android.permission.CAMERA` (o app deve pedir de novo e não quebrar).
- Rede ruim: sem root não há throttle real. Peça ao usuário para usar Configurações > Rede, um hotspot lento ou modo avião manualmente, e registre o horário.

## 5. Problemas comuns

- `unauthorized` / sem device: desbloquear, aceitar RSA, `adb kill-server && adb start-server`.
- Árvore vazia ou genérica: WebView/Flutter. Use screenshot + coordenadas e registre isso nas notas.
- `uiautomator dump` falha com tela em animação/vídeo: tente de novo ou pause o vídeo.
- `input text` não aceita acentos: use `mobile_type_keys`.
- Tela apagou/bloqueou: `droid key WAKEUP`; se houver senha, peça ao usuário para desbloquear (nunca tente digitar o PIN dele).
