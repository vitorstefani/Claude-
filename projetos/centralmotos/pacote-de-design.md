# Pacote de design: Central Motos Multimarcas (Nível 1)

## 1. Premissa
A faixa. A faixa laranja tracejada da pista é o fio da marca: leva do céu até o asfalto no hero, corre pela lateral da página ligando as seções, e termina no WhatsApp. Cada seção é um trecho da mesma estrada até a moto nova.

## 2. Paleta
```css
:root{
  --canvas:#17181B;      /* asfalto tingido, nunca preto puro */
  --panel:#212226;
  --accent:#FF6A13;      /* laranja Central, só CTA, foco e a faixa */
  --accent-hover:#FF8A3D;
  --accent-muted:rgba(255,106,19,.18);
  --text-secondary:#B7B8BD;
  --text-primary:#F4F2EE;
}
```

## 3. Fontes
Big Shoulders Display 800/900 (títulos, letreiro de estrada), Archivo 400/600 (texto), Martian Mono 500 (rótulos e placas).

## 4. Mapa de faixas (pontos de partida, 400vh)
| Faixa | Intervalo | Filmagem | Texto | Entrada |
|---|---|---|---|---|
| 1 | 0.00 a 0.30 | vista aérea, morros e estrada | "Central Motos" / "Multimarcas em Itatiba" | deriva para baixo |
| 2 | 0.36 a 0.64 | câmera descendo | "Vendas. Trocas. Financiamento." / "E a gente compra a sua moto." | alinhamento em grade, como tracejado |
| 3 | 0.72 a 1.00 | rente ao asfalto, faixa até o pôr do sol | "Potência, confiança e atitude." + CTA | subida palavra por palavra |

## 5. Hero estático
"Central Motos" / "Multimarcas em Itatiba. Vendas, trocas, financiamento, e a gente compra a sua moto." / CTA WhatsApp.

## 6. Abaixo da dobra
Serviços, Estoque (fichas com placa), Negócio claro (FAQ das objeções: documentação, financiamento, troca), Como pagar (momento interativo: segurar para acelerar o conta-giros), Avaliações (reais do Google), Visite, CTA final sobre o quadro final.

## 7. Camada vetorial
Faixa tracejada lateral que se traça com o scroll (assinatura), conta-giros SVG, partículas de poeira em nível de sussurro, grão de fundo.

## 8. Engenharia
Blob simples (vídeo < 8 MB), rAF normalizado por dt, seeks travados, escritas por delta, cinco portões vivos, completo sem vídeo, movimento reduzido nas duas direções.

## 9. Gate de texto
Zero travessões, zero palavras de estoque.
