# Segurança

## Proteção SSRF

O validador rejeita:

- protocolos diferentes de HTTP e HTTPS;
- usuário e senha embutidos na URL;
- loopback;
- redes privadas;
- link-local;
- multicast;
- endereços reservados;
- endpoints conhecidos de metadados de nuvem.

Cada redirecionamento HTTP é validado antes da próxima requisição.

## Limites

- timeout padrão de 15 segundos;
- até 5 redirecionamentos;
- resposta limitada a 2 MB;
- somente conteúdo textual é processado;
- Playwright é opcional por monitor.

## Produção

- troque `SECRET_KEY`;
- use HTTPS;
- mantenha `ALLOW_PRIVATE_NETWORKS=false`;
- restrinja CORS ao domínio real;
- use segredos da plataforma;
- habilite backups do PostgreSQL;
- configure rate limiting no proxy ou gateway;
- não aceite URLs sem política de autorização.
