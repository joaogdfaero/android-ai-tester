---
name: android-exploratory
description: Conduz uma sessão de teste exploratório (charter + timebox, estilo SBTM) em um app Android no device pessoal do usuário, procurando bugs com heurísticas mobile e entregando notas de sessão, evidências e bugs no formato uTest. Use quando o usuário pedir "teste exploratório", "explore o app", "procure bugs no app X", "faça uma sessão de ET", ou colar um escopo de ciclo exploratório da uTest.
---

# Teste exploratório em app Android

Carregue primeiro a skill `android-device`. A meta é **achar bugs reais e reportáveis** dentro do escopo, com evidência forte, não percorrer o app inteiro.

## 1. Charter

Antes de tocar no device, escreva `charters/<AAAA-MM-DD>_<app>-<tema>.md` (modelo em `templates/charter.md`) e mostre ao usuário em 5 linhas:
- **Missão:** "Explorar <área> com <recursos/técnica> para descobrir <tipo de risco>".
- **Escopo / fora de escopo** (copiado do ciclo uTest, se houver), **tipos de bug aceitos** (funcional, UI, conteúdo, usabilidade, crash), **ações proibidas**.
- **Timebox** (padrão 45–60 min de interação) e **orçamento de passos** (ex.: 150 ações). Ao estourar, pare e entregue.
- **Áreas priorizadas** por risco: o que é novo nesta build, fluxos de dinheiro/dados, telas com muito input, integrações (câmera, mídia, mapas, notificações, deep links).

Se o usuário só disse "explore o app", proponha o charter e siga sem esperar, a não ser que o escopo esteja ambíguo de verdade.

## 2. Sessão

`tools/droid run new <app>-et-<tema>`, `tools/droid prep`, `tools/droid log start`, `tools/droid info --out <run>/evidence/about-device`.

Ritmo: alterne **tours** (passar pela área para montar o mapa) e **ataques** (aprofundar onde algo pareceu frágil). Registre em `<run>/session-notes.md` (modelo `templates/session-notes.md`) à medida que anda:
- mapa de telas visitadas, hipóteses de risco, perguntas para o usuário, bugs, observações, **ideias não exploradas**.
- tempo gasto em Setup / Teste / Investigação de bug (%).

Heurísticas: veja `references/mobile-heuristics.md`. Use pelo menos 4 categorias diferentes por sessão (ex.: interrupções, input, rotação/configuração, estado/ciclo de vida, rede, acessibilidade, conteúdo/localização).

Oráculos (como saber que é bug): consistência com o próprio app, com o padrão Android (BACK fecha o diálogo antes de sair da tela, estado preservado na rotação, teclado não cobre o campo ativo), com a descrição do produto/loja, com versões anteriores, com o que o usuário espera; e mensagens no logcat (exceção, crash, ANR).

Sinais para investigar imediatamente: spinner infinito, toque sem resposta, dado que some/duplica após voltar, texto cortado ou sobreposto, tela em branco, idioma misturado, valor/total errado, app reinicia ao voltar do background, exceção no logcat junto com a ação.

## 3. Bug

Ao suspeitar: pare o tour, `droid note`, reproduza ≥ 2 vezes do estado limpo, isole a variável, grave vídeo curto (`droid rec start evidence/bugs/BUG-N/repro.mp4`) do estado inicial até o erro, extraia o logcat do horário. Siga a seção 4 da skill `utest-android-test-case` para validar e `templates/bug-report.md` para redigir em `bug-reports/BUG-N.md` (título no padrão `[Área] Tela - Ação: resultado errado`).

Severidade sugerida: **Critical** crash/perda de dados/bloqueio do fluxo principal; **High** função principal quebrada sem contorno; **Medium** função quebrada com contorno ou secundária; **Low** visual/texto/usabilidade.

## 4. Entrega

- `session-notes.md` completo (charter, duração real, cobertura, bugs, observações, ideias para próximas sessões, % de tempo).
- `bug-reports/BUG-N.md` + `evidence/bugs/BUG-N/`.
- `FINAL-REPORT.md` (`templates/final-report.md`).
- `tools/droid log stop` e `tools/droid restore`.

No chat (pt-BR, curto): caminho da run, bugs com severidade e reprodutibilidade, o que validar antes de submeter (Known Issues, duplicados), e 2–3 sugestões de próximos charters.
