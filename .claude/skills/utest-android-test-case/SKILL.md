---
name: utest-android-test-case
description: Executa um caso de teste scriptado da uTest (crowdtesting) em um app Android no device pessoal do usuário, salvando evidências por passo (screenshots, vídeos, logcat, notes) e rascunhos de bug no formato uTest, com README e FINAL-REPORT.md. Use quando o usuário colar ou apontar um test case/escopo de ciclo da uTest ("Step 1 - ...", "Expected Results", "Result Attachments", "In scope / Out of scope", "Known Issues") para um app Android, ou disser "execute este caso de teste" / "roda o test case".
---

# Executar um test case da uTest no Android

Carregue primeiro a skill `android-device` e siga as regras dela (segurança, ciclo observar→agir→verificar, evidências). **Quem submete na uTest é sempre o usuário.** Você entrega status sugeridos, evidências prontas e bugs redigidos.

Regras fixas:
- **Anexos só na quantidade pedida pelo passo** ("Minimum 3 – screenshots" → exatamente 3 na pasta do passo; passo sem "Result Attachments" → só `notes.md`). Capturas intermediárias ficam em `snap/` e não são entregues. A exceção são as evidências de bug (seção 3).
- **O foco é achar bugs**, não só marcar Pass. Em cada função, teste também bordas e combinações: toque rápido repetido, voltar (BACK) no meio de um fluxo, rotação no meio de um formulário, ir para background e voltar, matar o processo e reabrir, campos vazios/longos/com acentos e emoji, fonte grande, tema escuro, sem permissão. Use o passo exploratório (se houver) para aprofundar.

## 0. Ler o caso antes de agir

O caso pode vir colado no chat ou em `test-cases/<arquivo>.md`. Extraia e registre no `README.md` da run:
- **App** (nome, pacote, versão/build exigida, link de instalação: Play Store, Firebase App Distribution, TestFlight não se aplica), **conta/credenciais**, **plataformas em escopo** (versão mínima do Android, fabricantes), **conteúdo exigido**.
- **Passos:** instruções, resultados esperados e anexos mínimos.
- **Fora de escopo**, **campos obrigatórios do bug report** e o link de **Known Issues**.

Confira o app instalado: `tools/droid info` mostra a versão. Se a versão/build for diferente da exigida, **pare e avise** (bug em build errado é rejeitado). Se o pacote não está em `TARGET_PACKAGES`, peça para o usuário ajustar `config/device.env`.

Avise cedo sobre lacunas do ambiente: Android do device fora do escopo, passo que precisa de um 2º device, SIM/ligação, NFC, rede específica, compra real. Não trave: execute o que der e marque o resto como N/A ou Blocked com ressalva.

Links de docs da uTest (`platform.utest.com/...`) exigem login. Não tente abrir; peça ao usuário para conferir os Known Issues.

## 1. Estrutura da run

`tools/droid run new <app>-<tema>` cria:
```
runs/<AAAA-MM-DD>_<slug>/
  README.md                         # resumo, status por passo, rascunhos de bug
  FINAL-REPORT.md                   # consolidação final (templates/final-report.md)
  evidence/about-device/            # about-device.md/json + screenshot de Configurações > Sobre o telefone
  evidence/step-1-<slug>/ ...       # NN-descricao.png|.mp4, notes.md, *.txt
  evidence/step-N-<slug>/_invalid-<motivo>/   # descartados (artefato de ambiente) — nunca apagar
  evidence/bugs/BUG-N/              # vídeo/screenshot + bug-N-logcat.txt
  bug-reports/BUG-N.md              # bug no formato uTest (templates/bug-report.md)
  logs/                             # logcat completo da sessão
  snap/                             # capturas de trabalho, não entregues
```
Numere arquivos na ordem (`01-`, `02a-`) com nomes que digam o que mostram.

## 2. Preparação

1. `tools/droid doctor`, `tools/droid prep`, `tools/droid log start`.
2. About Device: `tools/droid info --out <run>/evidence/about-device`. Se o caso pedir screenshot de "About device", abra Configurações > Sobre o telefone (`mobile_launch_app com.android.settings`) e tire o print **sem** número de telefone/IMEI/nome pessoal visível (role a tela ou corte). Também a tela de informações do app com a versão, se pedida.
3. Estado inicial do app conforme o caso (logado/deslogado, primeira execução). "Primeira execução" exige `tools/droid clear`: **pergunte antes**, pois apaga o login e os dados do app.

## 3. Executar os passos

- Siga a ordem do caso. Para cada passo: crie `evidence/step-N-<slug>/`, anote o início (`droid note`), execute com o ciclo observar→agir→verificar, grave o vídeo/screenshot pedido **enquanto** faz a ação (não refaça só para filmar, a menos que necessário).
- Compare o resultado real com o esperado item por item e anote PASS / FAIL / BLOCKED / N/A com o motivo.
- Listas de funções ("Test ALL features of X"): teste uma a uma e monte uma matriz função × resultado. Não invente função que a UI não tem: marque N/A.
- Passos longos (esperar 1 h, download grande): comece cedo, registre o horário e continue os outros passos se o caso permitir.
- **Ações com dinheiro ou irreversíveis** (assinar, comprar, iniciar trial, excluir conta, enviar algo para terceiros): **nunca** sem perguntar. Use AskUserQuestion: pular e marcar Blocked / o usuário faz manualmente / prosseguir.
- Depois de cada passo, confira o logcat (`tools/droid crashes`) para pegar crash silencioso ou ANR.

## 4. Antes de chamar de bug

1. **Reproduza** pelo menos 2 vezes e registre a taxa (3/3, 1/3).
2. **Isole a variável:** caminho de entrada, logado × deslogado, retrato × paisagem, tema, rede, primeira execução × uso normal, dado específico.
3. Descarte **artefatos do ambiente**: toque duplicado pela automação, animação incompleta, tela que bloqueou, Não perturbe suprimindo notificação que o caso testa (desligue o DND nesse passo se o teste for de notificação), volume zerado em teste de áudio (o `prep` zera o volume de mídia: para testar som, ajuste e avise). Mova a evidência para `_invalid-<motivo>/`.
4. Confira o **escopo**: só reporte o que está em escopo. Crash e ANR sempre ficam.
5. Lembre o usuário de checar os **Known Issues**.

Para cada bug confirmado: `evidence/bugs/BUG-N/` com 1 vídeo curto da reprodução (do estado inicial até o erro) e/ou screenshot, mais `bug-N-logcat.txt` com o trecho relevante (stack trace de crash, exceção, horário). Mascare tokens, e-mails e IDs pessoais nos logs (`sed -E 's/(token|auth|Bearer)[=: ]+[^ ,"]+/\1=<redacted>/Ig'`).

## 5. Entrega

`README.md` (progresso por passo) com:
- Tabela de metadados: app + versão (versionName/versionCode), device, Android/API/build, idioma, fuso, conta (sem senha), janela de execução.
- Avisos: Known Issues não conferidos, Android fora do escopo, vídeos sem áudio.
- **Status sugerido por passo** (Pass / Fail / Blocked / N/A) com resumo e pasta de evidência.
- Matriz de funções, quando o caso pede várias.
- Rascunhos de bug com os campos exigidos pelo caso.

`FINAL-REPORT.md` na raiz da run (use `templates/final-report.md`), consolidando **todos** os bugs: tabela-resumo (ID, título, passo, severidade sugerida, reprodutibilidade, pronto para submeter ✅/⚠️), uma seção completa por bug (formato `templates/bug-report.md`), observações de menor prioridade, descartados com motivo e checklist pré-submissão. IDs BUG-N idênticos ao README.

Ao final: `tools/droid log stop`, `tools/droid restore` (sempre). No chat, em pt-BR e curto: caminho da run e do `FINAL-REPORT.md`, status por passo, bugs e o que o usuário precisa fazer antes de submeter.
