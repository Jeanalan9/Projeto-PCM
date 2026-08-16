# PCM Authenticator v1.3.0 — contrato visual

Referências aprovadas: visual branco/preto do PCM Authenticator v1.2.x e padrão de barra inferior do aplicativo Oficina PCM enviado em 16/08/2026.

## Estrutura
- Tela vertical Android, ocupando toda a área útil entre status bar e navigation bar.
- Fundo #FAFAFA, cartões #FFFFFF, texto principal #111111, secundário #666666, borda #E2E2E2.
- Vermelho #E53935 somente para ações destrutivas.
- Amarelo suave somente para estado “Renova hoje”.
- Cabeçalho PCM Authenticator preservado.
- Conteúdo principal rolável apenas quando necessário.
- Botão primário “Adicionar instalação” acima da barra interna.
- Barra inferior imediatamente acima da navigation bar do Android e sempre respeitando system insets.

## Barra inferior
- 4 itens: Instalações, Histórico, Configurações e Sobre.
- Ícone e rótulo separados verticalmente.
- Ícones em aproximadamente 24sp, rótulos em 11sp.
- Área útil de cada item: aproximadamente 66dp de altura.
- Altura total da barra: aproximadamente 74dp.
- Aba ativa com fundo cinza suave e texto/ícone preto.
- Abas inativas em cinza médio.
- Nenhum item pode ficar encoberto pela navigation bar do Android.

## Histórico
- Título e descrição no topo.
- Cards brancos para cada evento.
- Exibir tipo, instalação/identificador quando aplicável e data/hora.
- Nunca exibir ou armazenar segredo Base32 ou código TOTP no histórico.
- Botão Limpar histórico com tratamento destrutivo em vermelho.
- Estado vazio com ícone, título e texto explicativo.

## Configurações
- Card “Segurança e privacidade” com switches funcionais.
- Card “Parâmetros do autenticador” com valores somente leitura.
- Switches: permitir cópia de códigos; registrar ações no histórico.
- Informações: janela TOTP, formato, funcionamento offline, Android Keystore e quantidade de instalações.

## Sobre
- Card principal com identidade PCM Authenticator e versão.
- Cards explicativos para finalidade, TOTP, funcionamento offline e Android Keystore.
- Rodapé discreto “Projeto PCM · Autenticação das instalações”.

## Estados
- Light mode é o contrato visual desta versão.
- Dialogs continuam com fundo branco, cantos arredondados e ação destrutiva vermelha.
- Conteúdo deve permanecer legível em telas similares ao Motorola Edge 50 Pro apresentado nos testes.
