# Contrato visual — PCM Authenticator v1.2.0

Referência aprovada pelo responsável do Projeto PCM em 16/08/2026.

## Objetivo
Migrar o PCM Authenticator do padrão visual inspirado na Oliven para o padrão visual oficial do Projeto PCM, preservando integralmente a lógica funcional já validada na v1.1.1.

## Resolução de referência
- Base móvel vertical: aproximadamente 690 × 1536 px nos testes reais do aparelho.
- Conteúdo sempre respeita status bar e navigation bar por system insets.
- Nenhum elemento pode ficar por baixo das barras do Android.

## Paleta
- Fundo principal: #FAFAFA / branco quente muito claro.
- Cards e modais: #FFFFFF.
- Texto principal: #111111.
- Texto secundário: #666666.
- Bordas e divisores: #E5E5E5 / #D9D9D9.
- Preto institucional: #111111 para ações primárias, código e elemento ativo.
- Vermelho destrutivo: #E53935.
- Alerta de renovação: fundo #FFF1D6 e texto #9A6200.
- Cinza inativo: #B7B7B7.

## Tipografia
- Família: sans-serif do sistema, equivalente visual a Inter.
- Título de app: 20–22sp, bold/semibold.
- Título de card/modal: 18–21sp, bold.
- Texto: 12–14sp.
- Código TOTP: 38–42sp, bold, espaçamento entre grupos.

## Estrutura principal
1. Cabeçalho compacto com marca PCM em preto, texto “PCM Authenticator” e contador circular/oval à direita.
2. Área central rolável com estado vazio ou cards de instalações.
3. Botão primário preto “+ Adicionar instalação”.
4. Navegação inferior com quatro itens: Instalações, Histórico, Configurações e Sobre.
5. Item Instalações ativo em preto; demais em cinza.

## Card de instalação
- Fundo branco.
- Borda fina cinza clara.
- Raio aproximado: 18–20dp.
- Sombra muito discreta.
- Nome da instalação e identificador no topo.
- Chip “Renova hoje” em amarelo suave.
- Próxima renovação logo abaixo.
- Divisor horizontal.
- Rótulo “CÓDIGO ATUAL”.
- Código TOTP em preto.
- Barra de progresso preta sobre trilha cinza clara.
- Ações: Copiar código com contorno preto; Remover com contorno e texto vermelhos.

## Estado vazio
- Card branco com borda leve.
- Ícone de segurança neutro/cinza.
- Texto centralizado.
- Botão primário preto.

## Modal de cadastro
- Bottom-sheet/modal branco com cantos superiores arredondados.
- Campos brancos, borda cinza clara, altura aproximada de 50dp.
- Próxima renovação somente por seleção de calendário; não permitir digitação manual.
- Aviso de proteção do segredo em bloco cinza muito claro.
- Cancelar: botão secundário branco com borda preta/cinza.
- Salvar instalação: botão preto com texto branco.

## Calendário
- A seleção de data deve continuar por calendário nativo.
- Tema deve acompanhar branco/preto do PCM tanto quanto permitido pelo componente do sistema.
- Data selecionada destacada em preto.

## Confirmação de remoção
- Modal branco.
- Ícone/ênfase vermelha somente para ação destrutiva.
- Cancelar neutro.
- Remover com fundo vermelho e texto branco.

## Navegação inferior
- Altura visual aproximada: 62–68dp.
- Separador superior cinza claro.
- Fundo branco.
- Quatro itens igualmente distribuídos.
- Rótulos pequenos e ícones simples.
- Nesta versão, apenas Instalações precisa ser funcional; demais podem exibir aviso de funcionalidade futura sem alterar a tela atual.

## Preservações obrigatórias
- TOTP de 6 dígitos.
- Janela de 60 segundos.
- Contagem regressiva.
- Barra de progresso.
- Cópia do código.
- Remoção com confirmação.
- Múltiplas instalações.
- Persistência local.
- Segredo cifrado e protegido pelo Android Keystore.
- Calendário para próxima renovação.
- System insets já corrigidos na v1.1.1.

## Critério de aceite
A versão deve manter a funcionalidade da v1.1.1 e visualmente migrar de verde/Oliven para branco/preto/PCM, com vermelho somente em ações destrutivas e amarelo suave em alertas de renovação.