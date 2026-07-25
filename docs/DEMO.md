# Guia de demonstração

## Cenário 1 — mudança de preço

1. Abra o dashboard.
2. Entre em Demo Lab.
3. Altere o preço de R$ 2.499,90 para R$ 2.199,90.
4. Execute o monitor de preço.
5. Veja a execução marcada como alteração.
6. Confira o alerta e o Mailpit.

## Cenário 2 — disponibilidade

1. Desmarque “Produto disponível”.
2. Execute o monitor de disponibilidade.
3. Compare “Em estoque” com “Indisponível”.

## Cenário 3 — JavaScript

1. Ative o monitor de página dinâmica.
2. Execute-o.
3. O worker abrirá Chromium pelo Playwright.

## Cenário 4 — falha

Use `http://demo-target:8080/unstable?fail=true` e extração por status HTTP para demonstrar erro, retry e registro de falha.
