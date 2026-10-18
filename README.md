# Alessa Effects Sounds Prophetic

Complemento gratuito e de código aberto para o leitor de telas **NVDA** que acrescenta efeitos sonoros originais, com piano, pads e bateria suave, enquanto você navega pelo computador.

## O que ele faz

- **Abrir programas e janelas:** nota de piano com eco.
- **Terminar de carregar páginas:** pad suave que cresce devagar.
- **Mover o foco (Tab e setas):** um som para cada tipo de elemento: botão, link, caixa de texto, caixa de seleção (sobe ao marcar, desce ao desmarcar), menu, lista, título, aba e controle deslizante.
- **Digitar:** bateria suave nas letras, bumbo no espaço, caixa no Backspace.
- **Enter:** acorde de piano.

## Instalação

1. Baixe o arquivo `.nvda-addon` na página de [Releases](https://github.com/alemartinsvha-pixel/alessa-efects-sonds-prophects/releases).
2. Aperte Enter no arquivo baixado e confirme a instalação.
3. Reinicie o NVDA.

## Configuração

Abra o menu do NVDA (NVDA+N), vá em Preferências, Configurações, e escolha a categoria **Alessa Effects Sounds Prophetic**. Lá você ajusta o volume e liga ou desliga cada grupo de sons. O botão **Ouvir exemplo** toca três sons para testar o volume.

Atalhos:

- **NVDA+Shift+E:** liga ou desliga todos os efeitos.
- **NVDA+Shift+D:** liga ou desliga só os sons de digitação.

Você pode mudar os atalhos em Preferências, Comandos de entrada, categoria "Alessa Effects Sounds Prophetic".

## Trocar um som

Os sons ficam na pasta `sons`, em formato WAV. Para usar um som seu, substitua o arquivo com o mesmo nome. O script `gerar_sons.py` mostra como os sons originais foram sintetizados (Python com NumPy).

## Limitações conhecidas

- Os sons por tipo de elemento tocam quando o foco muda de verdade (Tab, setas em listas e menus). Ao navegar pela página com as setas no modo de navegação do NVDA, o foco não muda e esses sons não tocam.
- O som de carregamento de páginas depende de um evento que nem todas as páginas disparam.

## Licença

GNU General Public License, versão 2 (GPL v2). Veja o arquivo LICENSE.

## Autoria

Idealizado por Alessandra Acessibilidade Já.
