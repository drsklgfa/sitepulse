# API e regras de domínio

Base local: `http://localhost:8000/api/v1`

## Autenticação

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

## Monitores

- `GET /monitors`
- `POST /monitors`
- `GET /monitors/{id}`
- `PATCH /monitors/{id}`
- `DELETE /monitors/{id}`
- `POST /monitors/{id}/run`
- `GET /monitors/{id}/runs`

## Histórico e painel

- `GET /dashboard`
- `GET /runs`
- `GET /runs/{id}`
- `GET /notifications`
- `GET /health`
- `GET /demo-info`

## Tipos de extração

| Tipo | Resultado |
|---|---|
| `text` | Texto normalizado |
| `price` | Decimal canônico |
| `number` | Decimal canônico |
| `status` | Código HTTP |
| `html` | HTML do elemento |
| `attribute` | Valor de atributo |

## Condições

| Condição | Regra |
|---|---|
| `any_change` | Hash atual diferente do anterior |
| `price_drop` | Valor atual menor que o anterior |
| `price_below` | Valor atual menor que o limite |
| `contains` | Palavra presente |
| `not_contains` | Palavra ausente |
| `status_not_ok` | Código HTTP maior ou igual a 400 |
