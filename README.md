# Alessa Effects Sounds Prophetic

Complemento gratuito e de código aberto para o leitor de telas **NVDA** que acrescenta efeitos sonoros originais, com piano, pads e bateria suave, enquanto você navega pelo computador.

## Conjuntos de sons

Na janela de configurações há uma caixa combinada **Conjunto de sons** com cinco opções, todas com sons originais criados para este projeto:

- **Profético:** piano e pads com eco, com bateria suave ao digitar (padrão).
- **Somente pads:** só texturas suaves de pad, sem piano.
- **Piano com reverb intenso:** notas de piano com eco longo.
- **Celular clássico:** bipes e cliques eletrônicos curtos, no estilo de celulares antigos.
- **Smartphone moderno:** toques suaves e cristalinos, no estilo de celulares atuais.

Os sons deste projeto são originais e inspirados apenas no estilo. Não são cópias de sons de nenhum sistema ou fabricante.

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

Os sons do conjunto profético ficam na pasta `sons`, e os dos outros conjuntos em subpastas de `sons`, em formato WAV. Para criar um conjunto novo, crie uma subpasta com os mesmos nomes de arquivo e acrescente a pasta na lista `TEMAS` do arquivo do plugin. Para usar um som seu, substitua o arquivo com o mesmo nome. Os scripts `gerar_sons.py` e `gerar_temas.py` mostram como os sons foram sintetizados (Python com NumPy).

## Limitações conhecidas

- Os sons por tipo de elemento tocam quando o foco muda de verdade (Tab, setas em listas e menus). Ao navegar pela página com as setas no modo de navegação do NVDA, o foco não muda e esses sons não tocam.
- O som de carregamento de páginas depende de um evento que nem todas as páginas disparam.

## Licença

GNU General Public License, versão 2 (GPL v2). Veja o arquivo LICENSE.

## Autoria

Idealizado por Alessandra Acessibilidade Já.
