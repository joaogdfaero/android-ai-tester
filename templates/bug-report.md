# Title

[<Área do app>] <Tela> - <Ação>: <resultado errado em poucas palavras>

# Description

**App / versão:** <nome> <versionName> (versionCode <N>) — build do ciclo: <link>
**Device:** <fabricante> <modelo> — Android <versão> (API <N>), build <ro.build.display.id>
**Conta:** <usuário de teste / customer ID, se o caso pedir>
**Idioma / região:** <pt-BR / BR>
**Rede:** <Wi-Fi / 4G / 5G>
**Data/hora (fuso):** <AAAA-MM-DD HH:MM:SS BRT (UTC-03)>
**Reprodutibilidade:** <3/3>

## Pré-condições

- <logado com conta X, item Y no carrinho, permissão Z concedida...>

## Actions Performed

1. Abrir o app <nome>.
2. ...
3. ...

## Expected Result

<o que deveria acontecer, citando a fonte se houver: passo do caso, padrão Android, comportamento em outra tela>

## Actual Result

<o que acontece; mensagens exatas entre aspas; para crash: "o app fecha e volta à tela inicial do Android">

## Isolamento

| Cenário | Resultado |
|---|---|
| <variação A> | OK |
| <variação B> | **Falha** |

## Logs

<trecho do logcat com stack trace / exceção, tokens mascarados — arquivo completo em evidence/bugs/BUG-N/bug-N-logcat.txt>

## Attachments

- `evidence/bugs/BUG-N/repro.mp4` (vídeo, sem áudio)
- `evidence/bugs/BUG-N/01-....png`
