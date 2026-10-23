# Refactor Report — task-manager-api

> Gerado pela skill `refactor-arch` (Fase 3 — Refatoração).
> Data: 2026-10-22 | Raiz: `/home/eric-ogata/codes/full_cycle/mba_engenharia_ia/desafios/desafio3/mba-ia-refactor-projects-skill/task-manager-api`
> Baseado em: `reports/analysis-task-manager-api.md` e `reports/audit-task-manager-api.md`

## 1. Resumo

| Métrica | Antes | Depois |
|---|---|---|
| Arquivos `.py` | 15 | 39 (inclui 8 de teste/migration e `__init__.py`) |
| Localizações com query no controller | 33 | 0 |
| Segredos literais | 4 | 0 (exceto chave de teste) |
| Tratamento de erro | 11 `except` genéricos | 2 handlers centrais |
| Cobertura de testes | 0 | 8 testes de integração |
| Migrations | ausentes | Alembic (revisão inicial `81c7c4d76ee3`) |
| Endpoints de negócio validados | — | 22/22 (100%) |

**Arquitetura:** Monolítico em camadas parcial → **MVC + Services + Repositories**, com Config, Validators, Middleware e Migrations.

### Estrutura antes

```
app.py              # config hardcoded + rotas / e /health + create_all
database.py
models/             # task, user (MD5 + password no to_dict), category
routes/             # rota + validação + regra + ORM + serialização
services/           # notification_service.py (nunca importado)
utils/helpers.py    # validação duplicada
```

### Estrutura depois

```
app.py                  # composition root (create_app)
errors.py               # exceções de domínio
config/settings.py      # config via env (.env.example)
models/                 # entidades + invariantes (sem segredos no to_dict)
repositories/           # task, user, category — único ponto de ORM
services/               # task, user, category, report, auth — sem HTTP
controllers/            # task, user, category, report — orquestração pura
routes/                 # task, user, category, report — só add_url_rule
validators/schemas.py   # marshmallow por recurso
middleware/             # error_handler central + auth JWT
migrations/             # Alembic/Flask-Migrate
tests/test_api.py       # integração de todos os recursos
```

Fluxo de dependência: `routes → controllers → services → repositories → models`.

## 2. Anti-patterns corrigidos

### CRITICAL

| Achado | Resolução |
|---|---|
| **SEC-02** `SECRET_KEY` em `app.py:13` | `config/settings.py` lê `SECRET_KEY` do ambiente; sem valor, gera chave aleatória em boot. `.env.example` documenta a variável. |
| **SEC-02** credenciais SMTP em `notification_service.py` | Módulo removido (era código morto, nunca importado). |
| **SEC-03** MD5 + hash exposto | `werkzeug.security.generate_password_hash`/`check_password_hash`; `User.to_dict` não inclui `password`; login aceita MD5 legado e **re-hasheia no primeiro login**. |

### HIGH

| Achado | Resolução |
|---|---|
| **SEC-04** rotas de escrita sem auth + token falso | JWT real assinado (`services/auth_service.py`), `middleware/auth.py` valida `Authorization: Bearer` quando `AUTH_REQUIRED=true`; token fake removido. Enforcement opt-in para preservar o contrato legado — ver limitações. |
| **ARCH-01** lógica de negócio nas rotas | Extraída para `TaskService`, `UserService`, `CategoryService`, `ReportService`. Controllers têm apenas orquestração. |
| **ARCH-02** ORM/`db.session` nas rotas | Centralizado em `repositories/` (um por agregado). Rotas não importam `db` nem models. |

### MEDIUM

| Achado | Resolução |
|---|---|
| **PERF-01** N+1 em `/tasks`, `/users`, `/reports/summary`, `/categories` | `joinedload` em `TaskRepository.get_all`; `group_by`/`count` para contagens e produtividade; eager loading de relações. |
| **QUAL-02** validação ausente | `validators/schemas.py` (marshmallow) por recurso, invocado no service; payload inválido → 400 com `{"error": ...}`. |
| **QUAL-03** `except` genérico | `middleware/error_handler.py` com handlers para `DomainError`, `HTTPException` e `Exception` (com log e rollback). Zero `except` nos controllers. |
| **QUAL-04** estado global mutável | `NotificationService` removido; nenhum estado de módulo mutável restante. |
| **ARCH-03** Model com responsabilidades duplas | Models mantêm apenas entidade/invariantes; hashing no Model com API segura, validação em schemas, persistência em repositórios, agregações em services. |

### LOW

| Achado | Resolução |
|---|---|
| **QUAL-05** dependências/código mortos | `requests` removido; `marshmallow` e `python-dotenv` passaram a ser usados; imports mortos removidos; `NotificationService` excluído. |
| **QUAL-06** sem migrations | Flask-Migrate/Alembic inicializado; revisão inicial criada e aplicada; `db.create_all()` removido do import do app. |
| **QUAL-07** config hardcoded | Host, porta, debug, URI e segredos externalizados (`config/settings.py` + `.env.example`); `debug` default `False`, bind default `127.0.0.1`. |
| **QUAL-08** sem testes | `tests/test_api.py` — 8 testes de integração. |
| **DEP-01** APIs deprecated | `datetime.utcnow()` → `utils.helpers.utcnow()`; `Query.get()` → `db.session.get()`. |

## 3. Resultado dos testes de validação

### Boot

```
$ flask --app app db upgrade   → revisão 81c7c4d76ee3 aplicada
$ python seed.py              → 3 usuários, 4 categorias, 10 tasks
$ python app.py               → servindo em 127.0.0.1:5055 (validação)
```

### Endpoints (smoke test com HTTP real)

| Método | Rota | Status | Contrato |
|---|---|---|---|
| GET | `/` | 200 | `{message, version}` |
| GET | `/health` | 200 | `{status, timestamp}` |
| GET | `/tasks` | 200 | lista com `user_name`, `category_name`, `overdue`, `tags` |
| GET | `/tasks/<id>` | 200 | objeto + `overdue` |
| POST | `/tasks` | 201 | objeto criado |
| PUT | `/tasks/<id>` | 200 | objeto atualizado |
| DELETE | `/tasks/<id>` | 200 | `{message}` |
| GET | `/tasks/search` | 200 | lista filtrada |
| GET | `/tasks/stats` | 200 | `{total,pending,in_progress,done,cancelled,overdue,completion_rate}` |
| GET | `/users` | 200 | lista com `task_count`, **sem** `password` |
| GET | `/users/<id>` | 200 | usuário + `tasks` |
| POST | `/users` | 201 | usuário criado, **sem** `password` |
| PUT | `/users/<id>` | 200 | usuário atualizado |
| DELETE | `/users/<id>` | 200 | `{message}` + tasks do usuário removidas |
| GET | `/users/<id>/tasks` | 200 | lista com `overdue` |
| POST | `/login` | 200 | `{message, user, token}` com **JWT real** (3 partes) |
| GET | `/reports/summary` | 200 | overview, status, prioridade, overdue, atividade, produtividade |
| GET | `/reports/user/<id>` | 200 | user + statistics |
| GET | `/categories` | 200 | lista com `task_count` |
| POST | `/categories` | 201 | categoria criada |
| PUT | `/categories/<id>` | 200 | categoria atualizada |
| DELETE | `/categories/<id>` | 200 | `{message}` |

**22/22 rotas de negócio validadas (100%).**

### Casos de erro

| Cenário | Resultado |
|---|---|
| `POST /tasks` com `{}` | 400 `{"error":"Título é obrigatório"}` |
| `POST /tasks` com `priority: 9` | 400 |
| `POST /tasks` com `due_date` inválida | 400 |
| `POST /users` com e-mail inválido | 400 |
| `PUT /categories/<id>` com body `null` | 400 (antes: 500) |
| `POST /tasks` sem JSON | 400 |
| `GET /tasks/9999` | 404 `{"error":"Task não encontrada"}` |
| `POST /tasks` sem token com `AUTH_REQUIRED=true` | 401 |
| `POST /tasks` com JWT válido | 201 |

### Testes automatizados

```
$ pytest -q
........                                                                 [100%]
8 passed
```

Cobrem CRUD de usuários/tasks/categorias, login JWT, relatórios, validação (400), 404, auth (401/201) e re-hash de senha MD5 legada.

## 4. Checklist de validação (mvc-guidelines §6)

- [x] Aplicação sobe sem erros (`python app.py`)
- [x] Todas as 22 rotas de negócio respondem no mesmo path/verbo
- [x] Rotas de escrita rejeitam payload malformado com 400
- [x] Nenhuma query interpolada (ORM com parâmetros vinculados; sem SQL cru)
- [x] Nenhum segredo literal no código (exceto `TestConfig.SECRET_KEY`, restrito a testes)
- [x] Responses não expõem campos sensíveis (`password` removido)
- [x] Nenhum `except` genérico engolindo erro sem log
- [x] Arquivos antigos removidos (`notification_service.py`; conteúdo antigo de `routes/` substituído)
- [x] `git status` sem sobras de refatoração (caches/DB cobertos por `.gitignore`)

## 5. Limitações e trabalho futuro

- **SEC-04 — enforcement de auth é opt-in.** `AUTH_REQUIRED=false` por padrão para preservar o contrato original (todos os endpoints respondem sem token, como no projeto-base). A infraestrutura JWT está pronta e testada; recomenda-se `AUTH_REQUIRED=true` em produção. Autorização por papel (`admin` para gestão de usuários) ainda não foi aplicada.
- **Migrations:** a revisão inicial cobre o schema atual. Alterações futuras devem usar `flask db migrate`. Bancos existentes criados com o `create_all()` original precisam de baseline (`flask db stamp head`).
- **Testes:** são de integração (happy path + validação). Faltam testes unitários de services/repositories e testes de concorrência.
- **Observabilidade:** `print()` foi removido; o error handler usa `app.logger`. Não há logging estruturado nem métricas.
- **CI/CD e containerização:** continuam ausentes (fora do escopo desta refatoração).
- **Compatibilidade:** três mudanças intencionais de contrato — `password` não é mais retornado, `/login` emite JWT real e o SQLite fica na raiz do projeto. Todas documentadas no `README.md`.
