# Heurísticas de teste exploratório mobile (Android)

Comandos entre crases são do `tools/droid`; todos os ajustes são desfeitos por `droid restore`.

## Interrupções e ciclo de vida
- HOME no meio de um fluxo e voltar pelos Recentes (`key HOME`, `key APP_SWITCH`).
- Morte de processo em background (`kill-bg`): o app deve voltar à mesma tela com os dados do formulário.
- BACK em cada tela: fecha diálogo/teclado/bottom sheet antes de navegar? Sai do app sem confirmação no meio de algo importante?
- Bloquear/desbloquear a tela durante carregamento ou reprodução de mídia (`key POWER`, peça ao usuário para desbloquear).
- Notificação ou ligação chegando (peça ao usuário ou desligue o DND naquele teste).
- Trocar de app e voltar durante upload/download/pagamento simulado.

## Configuração do device
- Rotação em cada tela relevante (`set rotate 1` / `0`): perde estado? layout quebra? diálogo some?
- Fonte grande (`set font 1.3` e `2.0`): texto cortado, botões fora da tela, sobreposição.
- Tema escuro (`set dark on`): contraste, ícones invisíveis, imagens com fundo branco.
- Modo multitarefa/tela dividida e janela flutuante (peça ao usuário se o gesto for difícil).
- Idioma/região: formatos de data, moeda, separador decimal (pergunte antes de mudar o idioma do sistema).
- Bateria baixa simulada (`set battery 5`): o app muda comportamento? economia de energia.

## Input
- Campos: vazio, só espaços, muito longo (500+ caracteres), acentos `ção`, emoji `👍🏽`, RTL `مرحبا`, colar texto, caracteres especiais `<script>`, `' OR 1=1`, números negativos/decimais com vírgula.
- Teclado cobrindo o campo/botão; ENTER/“próximo” do teclado avança ou envia?
- Toques rápidos repetidos em botão de enviar/salvar (duplicação de pedido/registro).
- Gestos: long press, double tap, swipe para atualizar, scroll até o fim (paginação), pinch zoom em imagens.

## Estado e dados
- Criar → editar → excluir → desfazer; o item some/volta corretamente em todas as listas?
- Logout/login: dados de outra sessão aparecem? cache antigo?
- Primeira execução vs. reaberta (pergunte antes de `clear`).
- Permissões negadas e depois concedidas (`perm revoke ...`), "não perguntar novamente".
- Deep links / compartilhamento para dentro do app (`mobile_open_url` com URL do próprio app).

## Rede
- Conexão lenta ou queda no meio de uma ação (peça ao usuário para trocar a rede/modo avião; avise se o adb for por Wi-Fi).
- Voltar a ficar online: tenta de novo sozinho? mensagem de erro clara? dado duplicado?
- Offline ao abrir o app: tela vazia ou mensagem adequada?

## Conteúdo, UI e acessibilidade
- Textos com erro, idioma misturado, placeholders tipo `%s`/`{name}`, truncamento sem reticências.
- Imagens quebradas, carregamento infinito, skeleton que não some.
- Elementos clicáveis sem `content-desc` (veja `droid ui`: botões só com ícone sem `desc`), alvos de toque < 48dp, contraste.
- Consistência entre telas (mesmo dado com valores diferentes).

## Mídia (se o app tiver)
- Play/pause, seek no início e no fim, velocidade, fila, background playback, fone/BT desconectando, rotação durante vídeo em tela cheia, PiP.
- Lembre: o `prep` zera o volume de mídia; para checar áudio, ajuste (`key VOLUME_UP`) e informe o usuário.
