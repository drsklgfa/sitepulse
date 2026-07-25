# Deploy

O repositório é local-first, mas os serviços foram separados para implantação futura.

## Serviços de produção

1. `frontend`: build estático React.
2. `api`: FastAPI.
3. `worker`: Celery Worker.
4. `scheduler`: Celery Beat, uma única réplica.
5. `postgres`: banco gerenciado.
6. `redis`: serviço gerenciado.

## Variáveis principais

```text
APP_ENV=production
SECRET_KEY=<segredo-forte>
DATABASE_URL=postgresql+psycopg://...
REDIS_URL=redis://...
CORS_ORIGINS=https://seu-dominio
ALLOW_PRIVATE_NETWORKS=false
SEED_DEMO_DATA=false
SMTP_ENABLED=true
SMTP_HOST=...
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
SMTP_USE_TLS=true
```

## Ordem de inicialização

1. Banco e Redis disponíveis.
2. `alembic upgrade head`.
3. API.
4. Workers.
5. Scheduler.
6. Frontend.

## Observação

O scheduler deve ter somente uma instância para evitar enfileiramento duplicado. Em escala, use uma estratégia de lock distribuído ou um scheduler persistente.
