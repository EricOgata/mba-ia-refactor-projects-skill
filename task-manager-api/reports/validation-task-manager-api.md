# Validation Report — task-manager-api

> Gerado pela skill `refactor-arch` (Fase 4 — Validação Pós-Refatoração).
> Data: 2026-10-22 | Raiz: `/home/eric-ogata/codes/full_cycle/mba_engenharia_ia/desafios/desafio3/mba-ia-refactor-projects-skill/task-manager-api`
> Baseado em: `reports/analysis-task-manager-api.md`, `reports/audit-task-manager-api.md`, `reports/refactor-task-manager-api.md`

## 1. Resumo

| Métrica | Resultado |
|---|---|
| Status geral | **PASS** (com ressalvas não bloqueantes) |
| Rotas de negócio testadas | 22/22 |
| Rotas aprovadas | 22 (100%) |
| CRITICAL resolvidos | 3/3 |
| HIGH resolvidos | 2/3 (1 parcial) |
| Verificações estáticas | OK (2 WARN) |
| Testes automatizados | 8/8 passed |

**Status:** `VALIDATED WITH RESERVES`
**Recomendação:** `APPROVED WITH RESERVES`

## 2. Contrato original vs atual

Inventário extraído da Fase 1 (22 rotas de negócio; a rota `/static` do Flask não conta).

| Recurso | Rotas no contrato original | Rotas hoje | Preservado |
|---|---|---|---|
| Aplicação | `GET /`, `GET /health` | 2 | ✅ |
| Tasks | `GET/POST /tasks`, `GET/PUT/DELETE /tasks/<id>`, `GET /tasks/search`, `GET /tasks/stats` | 7 | ✅ |
| Users | `GET/POST /users`, `GET/PUT/DELETE /users/<id>`, `GET /users/<id>/tasks` | 6 | ✅ |
| Auth | `POST /login` | 1 | ✅ |
| Reports | `GET /reports/summary`, `GET /reports/user/<id>` | 2 | ✅ |
| Categories | `GET/POST /categories`, `PUT/DELETE /categories/<id>` | 4 | ✅ |
| **Total** | **22** | **22** | **100%** |

Rotas registradas no Flask (`app.url_map`): 22 de negócio + `/static` = 23 regras.

## 3. Smoke test por endpoint

Servidor real: `PORT=5056 python app.py` (boot sem erros). Banco migrado (`flask db upgrade`) e populado (`seed.py`).

| # | Método | Path | Status esperado | Obtido | Resultado | Observação |
|---|---|---|---|---|---|---|
| 1 | GET | `/` | 200 | 200 | PASS | `{message, version}` |
| 2 | GET | `/health` | 200 | 200 | PASS | `{status, timestamp}` |
| 3 | GET | `/tasks` | 200 | 200 | PASS | inclui `user_name`, `category_name`, `overdue` |
| 4 | GET | `/tasks/search?q=login` | 200 | 200 | PASS | filtro aplicado |
| 5 | GET | `/tasks/stats` | 200 | 200 | PASS | 7 chaves preservadas |
| 6 | GET | `/tasks/1` | 200 | 200 | PASS | `to_dict` + `overdue` |
| 7 | POST | `/tasks` | 201 | 201 | PASS | task criada |
| 8 | PUT | `/tasks/11` | 200 | 200 | PASS | status atualizado |
| 9 | DELETE | `/tasks/11` | 200 | 200 | PASS | `{message}` |
| 10 | GET | `/users` | 200 | 200 | PASS | `task_count`; **sem** `password` |
| 11 | GET | `/users/1` | 200 | 200 | PASS | usuário + `tasks` |
| 12 | GET | `/users/1/tasks` | 200 | 200 | PASS | campos originais + `overdue` |
| 13 | POST | `/users` | 201 | 201 | PASS | **sem** `password` na resposta |
| 14 | PUT | `/users/4` | 200 | 200 | PASS | nome atualizado |
| 15 | DELETE | `/users/4` | 200 | 200 | PASS | `{message}` |
| 16 | POST | `/login` | 200 | 200 | PASS | JWT real (3 partes) |
| 17 | GET | `/reports/summary` | 200 | 200 | PASS | 7 seções preservadas |
| 18 | GET | `/reports/user/1` | 200 | 200 | PASS | `user` + `statistics` |
| 19 | GET | `/categories` | 200 | 200 | PASS | `task_count` |
| 20 | POST | `/categories` | 201 | 201 | PASS | categoria criada |
| 21 | PUT | `/categories/5` | 200 | 200 | PASS | descrição atualizada |
| 22 | DELETE | `/categories/5` | 200 | 200 | PASS | `{message}` |

### Comportamento de erro (regressão)

| Cenário | Antes | Agora | Resultado |
|---|---|---|---|
| `POST /tasks` com `{}` | 400 | 400 `Título é obrigatório` | PASS |
| `PUT /categories/1` com `null` | **500** (TypeError) | 400 `Dados inválidos` | PASS (melhoria) |
| `GET /tasks/99999` | 404 | 404 `Task não encontrada` | PASS |
| `POST /tasks` sem token (`AUTH_REQUIRED=true`) | n/a | 401 | PASS |
| `POST /tasks` com JWT válido | n/a | 201 | PASS |

**Nenhum erro 500 inesperado** durante o smoke test.

## 4. Verificação estática

| Item | Resultado | Evidência |
|---|---|---|
| Estrutura alvo presente | OK | `config/`, `controllers/`, `services/`, `repositories/`, `models/`, `routes/`, `middleware/`, `validators/`, `migrations/`, `tests/` |
| Rotas separadas do entrypoint | WARN | 22 rotas de negócio em `routes/*.py`; `app.py:29,33` mantém `/` e `/health` inline (rotas de infraestrutura) |
| Controllers só orquestram | OK | `grep` não encontra `db`, models ou `.query` em `controllers/` |
| Services sem HTTP/request | WARN | `services/` não usa `request`/`response`; `services/auth_service.py:4` usa `current_app` apenas para `SECRET_KEY`/expiração |
| Repositories sem HTTP | OK | `grep` não encontra Flask em `repositories/` |
| Queries parametrizadas | OK | ORM com parâmetros vinculados; único SQL é gerado pelo Alembic em `migrations/env.py` |
| Segredos hardcoded | OK | `grep` por `super-secret-key-123`, `senha123`, `smtp.gmail` → nenhum resultado |
| Arquivos órfãos | OK | `services/notification_service.py` removido; nenhum import remanescente; `import app` funciona |
| Config centralizada | OK | `config/settings.py` lê env; `.env.example` presente |
| APIs deprecated | OK | sem `datetime.utcnow()` nem `Query.get()` no código (só menção em docstring) |
| Error handling central | OK | `middleware/error_handler.py`; zero `except:` nu no projeto |

## 5. Cruzamento com auditoria (CRITICAL/HIGH)

### CRITICAL

| ID | Achado | Status | Evidência |
|---|---|---|---|
| SEC-02 | `SECRET_KEY` hardcoded (`app.py:13`) | **RESOLVIDO** | `config/settings.py:29` lê `SECRET_KEY` do ambiente; sem valor, `secrets.token_hex(32)`. Nenhum literal no código de produção. |
| SEC-02 | Credenciais SMTP hardcoded | **RESOLVIDO** | `services/notification_service.py` removido (código morto); nenhum `smtp`/`senha123` no projeto. |
| SEC-03 | MD5 + hash exposto | **RESOLVIDO** | `models/user.py:34-47` usa `generate_password_hash`/`check_password_hash`; `to_dict` (`:16-25`) não inclui `password`; login re-hasheia MD5 legado (`tests/test_api.py::test_legacy_md5_password_is_rehashed_on_login`). |

### HIGH

| ID | Achado | Status | Evidência |
|---|---|---|---|
| SEC-04 | Rotas de escrita sem auth + token falso | **PARCIAL** | JWT real emitido em `services/auth_service.py` e validado por `middleware/auth.py`; token fake removido. Porém `AUTH_REQUIRED=false` por default para preservar o contrato original — o enforcement é opt-in. Testado: 401 sem token e 201 com token quando habilitado (`test_auth_guard_blocks_writes_when_enabled`). |
| ARCH-01 | Lógica de negócio nas rotas | **RESOLVIDO** | Regras em `services/task_service.py`, `user_service.py`, `category_service.py`, `report_service.py`; controllers com 1-6 linhas por handler. |
| ARCH-02 | Acesso a dados nas rotas | **RESOLVIDO** | Todo ORM em `repositories/` (3 arquivos); `grep` de `db`/`.query` em `controllers/` e `routes/` não retorna nada. |

**Resumo:** CRITICAL 3/3 resolvidos; HIGH 2/3 resolvidos, 1 parcial (SEC-04, por decisão de compatibilidade documentada).

### MEDIUM/LOW (não bloqueantes)

| ID | Status | Evidência |
|---|---|---|
| PERF-01 N+1 | RESOLVIDO | `joinedload` em `TaskRepository.get_all`; agregações com `group_by`/`count` em `TaskRepository`/`UserRepository`. |
| QUAL-02 validação | RESOLVIDO | `validators/schemas.py`; payloads inválidos → 400 (validado dinamicamente). |
| QUAL-03 erro genérico | RESOLVIDO | `middleware/error_handler.py`; zero `except:` nu. |
| QUAL-04 estado global | RESOLVIDO | `NotificationService` removido; nenhuma lista/dict mutável de módulo. |
| ARCH-03 models duplos | RESOLVIDO | Models só entidade/invariantes; persistência e regras extraídas. |
| QUAL-05 deps/código morto | RESOLVIDO | `requests` removido; `marshmallow`/`dotenv` em uso; imports limpos. |
| QUAL-06 migrations | RESOLVIDO | `migrations/versions/81c7c4d76ee3_initial_schema.py`; `db.create_all()` fora do import. |
| QUAL-07 config hardcoded | RESOLVIDO | `config/settings.py` + `.env.example`. |
| QUAL-08 testes | RESOLVIDO | 8 testes de integração, todos passando. |
| DEP-01 APIs deprecated | RESOLVIDO | `utils/helpers.py:utcnow()`; `db.session.get()`. |

## 6. Riscos e ressalvas

1. **SEC-04 (PARCIAL):** o guard JWT existe e funciona, mas só é exigido com `AUTH_REQUIRED=true`. Em produção, habilitar a variável. Não há autorização por papel (ex.: apenas `admin` gerencia usuários).
2. **`/` e `/health` inline em `app.py`:** são rotas de infraestrutura; a separação das 22 rotas de negócio foi cumprida. Baixo impacto.
3. **`auth_service` usa `current_app`:** dependência do contexto de aplicação Flask (não de HTTP request/response). Aceitável, mas poderia migrar para `middleware/security.py` em uma iteração futura.
4. **Mudanças de contrato intencionais:** `password` não é mais retornado; `/login` emite JWT real; SQLite na raiz do projeto. Documentadas no `README.md`.
5. **Baseline de banco legado:** bancos criados com o `create_all()` original precisam de `flask db stamp head` antes de novas migrations.
6. **Fora de escopo:** CI/CD, containerização, logging estruturado e testes unitários de services/repositories.

## 7. Recomendação final

**APROVADO COM RESSALVAS**

A refatoração preservou 100% das 22 rotas de negócio (path, verbo e formato), eliminou todos os achados CRITICAL e todos os HIGH com exceção parcial de SEC-04 (infraestrutura pronta, enforcement opt-in). Não há falha funcional, erro 500 inesperado ou regressão de contrato.

**Ações recomendadas (não bloqueantes):**
1. Definir `AUTH_REQUIRED=true` em produção.
2. Implementar autorização por papel para rotas administrativas.
3. Adicionar baseline de migrations em bancos legados (`flask db stamp head`).
4. (Opcional) Mover `/` e `/health` para `routes/` e `auth_service` para `middleware/`.

## 8. Notas e evidências

Comandos executados:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/flask --app app db upgrade        # 81c7c4d76ee3 aplicada
.venv/bin/python seed.py                    # 3 usuários, 4 categorias, 10 tasks
PORT=5056 .venv/bin/python app.py           # boot OK
.venv/bin/python -m pytest -q               # 8 passed
```

Smoke test HTTP: 22/22 PASS, 0 FAIL. Erros esperados: `{}` → 400, `null` → 400, id inexistente → 404. Payloads de `/users` e `/login` não contêm `password`; token com 3 partes (JWT).

Contagem de artefatos: `app.url_map` = 22 rotas de negócio + `/static`; `git status` restrito a mudanças da refatoração (caches e `tasks.db` cobertos por `.gitignore`).
