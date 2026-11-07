# android-ai-tester

Projeto para a IA executar **testes scriptados (test cases da uTest)** e **testes exploratórios** em um app Android rodando no **celular pessoal** do usuário, conectado por adb (USB ou Wi-Fi).

Converse em pt-BR. O usuário é testador da uTest: quem submete resultados e bugs é sempre ele.

## Como trabalhar

- Test case da uTest (colado no chat ou em `test-cases/`) → skill **`utest-android-test-case`**.
- "Explore o app", "procure bugs", ciclo exploratório → skill **`android-exploratory`**.
- Qualquer interação com o device → skill **`android-device`** primeiro (as outras duas pedem isso).

Ferramentas:
- **mobile-mcp** (`mcp__mobile-mcp__*`, definido em `.mcp.json`): ver a tela, listar elementos, tocar, deslizar, digitar, abrir apps.
- **`tools/droid`** (Python + adb): run, prep/restore, screenshot, vídeo, logcat, crashes, About Device, simulações (rotação, tema, fonte, bateria, permissões, morte de processo). `tools/droid --help`.

## Regras inegociáveis (device pessoal)

1. Só opere os apps de `TARGET_PACKAGES` (`config/device.env`). Configurações do Android só para consulta.
2. Nada irreversível: sem reboot/reset/root, sem apagar arquivos, sem desinstalar ou limpar outros apps. O hook `.claude/hooks/guard_device.py` bloqueia o grosso disso; não tente contorná-lo.
3. Sem dinheiro e sem contato com terceiros: compras, assinaturas, trials, ligações, SMS, e-mails, mensagens e compartilhamentos para fora do app exigem pergunta explícita (AskUserQuestion).
4. Privacidade: rode `tools/droid prep` (Não perturbe) antes de gravar e confira cada evidência antes de salvar. Nada de notificações, contatos, fotos ou outros apps pessoais nas evidências. Não leia `config/accounts.env` e não grave senhas nos arquivos da run.
5. Sempre `tools/droid log stop` e `tools/droid restore` no fim da sessão, mesmo se ela for interrompida ou falhar.

## Estrutura

```
.claude/skills/        skills (android-device, utest-android-test-case, android-exploratory)
.claude/hooks/         guard do device pessoal (PreToolUse)
config/                device.env (serial, pacotes-alvo, prep), accounts.env (fora do git)
tools/droid            CLI de apoio
templates/             bug report, README da run, FINAL-REPORT, charter, notas de sessão
test-cases/            test cases colados da uTest
charters/              charters de sessões exploratórias
runs/AAAA-MM-DD_slug/  uma pasta por execução (evidence/, bug-reports/, logs/, snap/)
```
