# Relatório de validação

## SitePulse 1.0.0 — 25 de julho de 2026

### Resultados executados neste checkpoint

| Verificação | Resultado |
|---|---|
| Estrutura obrigatória do repositório | Aprovada |
| Sintaxe Python | 42 arquivos válidos |
| Testes do backend | 25 aprovados |
| Cobertura do backend | 85,81% |
| Meta mínima de cobertura | 75% — aprovada |
| Testes do Demo Target | 2 aprovados |
| Sintaxe TypeScript/TSX | 8 arquivos válidos |
| YAML | 6 arquivos válidos |
| Procura básica por segredos | Aprovada |
| Scraping HTTP contra servidor real | Aprovado — HTTP 200, valor `2499.9` |
| E2E da API | Aprovado — login, seed, fila local, scraping e snapshot |
| Registro de tentativas | Aprovado — 1 tentativa no cenário saudável |
| Manifesto SHA-256 dos arquivos | Incluído no pacote |

### E2E validado

O teste iniciou o Demo Target e a API em processos reais, autenticou com a conta demonstrativa, carregou três monitores, criou uma execução, aguardou o processamento em segundo plano e confirmou:

```text
status: no_change
http_status: 200
value: 2499.9
attempts: 1
```

### Validações dependentes de ambiente externo

| Verificação | Situação |
|---|---|
| `npm install`, testes Vitest e build Vite | Não concluídos: o registro npm do ambiente retornou indisponibilidade/timeout |
| Build das imagens Docker | Não executado: Docker, Podman e Buildah não estão instalados no ambiente de geração |
| Playwright Chromium dentro do container | Configurado, mas depende do build Docker |

Esses itens estão automatizados no GitHub Actions e documentados para execução local. Não foram marcados como aprovados sem evidência.

## Comandos reproduzíveis

```bash
python scripts/validate_repository.py
cd backend && PYTHONPATH=. pytest --cov=app --cov-report=term-missing
cd ../demo-target && PYTHONPATH=. pytest -q
cd ../frontend && npm install && npm run test && npm run build
docker compose config
docker compose up --build
```

## Conclusão

O núcleo funcional, a persistência local de testes, a autenticação, o scraping HTTP, a detecção, a fila local de fallback, os snapshots e a interface em nível de sintaxe foram validados. O build completo do frontend e dos containers deve ser confirmado pelo CI ou por um computador com acesso ao npm e Docker Desktop.
