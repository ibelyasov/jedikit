# SingularityApp и MCP для `singularity-jedi`

Дата первоначальной проверки: **2026-08-08**. Authenticated metadata probes дополнены **2026-08-09** (Europe/Moscow).

Первоначальная проверка была read-only: открыты официальная Wiki, публичная OpenAPI-схема и OAuth/MCP discovery; к пользовательскому аккаунту, токену и данным доступа не было. В Context7 `SingularityApp` не разрешился как библиотека; для самого протокола использован официальный `/modelcontextprotocol/modelcontextprotocol` (схема Tool и transport). Контракт MCP требует у каждого инструмента `name`, `description` и JSON Schema `inputSchema` ([MCP tools](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/server/tools.mdx)); стандарт описывает stdio и Streamable HTTP ([transports](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/basic/transports.mdx)). Последующие probes не вызывали tools и не читали пользовательские данные: least-privilege опыт записан в [singularity-mcp-live-probe.md](singularity-mcp-live-probe.md), полный каталог 48 tools — в [singularity-mcp-tools.md](singularity-mcp-tools.md), четыре server prompts — в [singularity-mcp-prompts.md](singularity-mcp-prompts.md).

## Краткий вывод

1. У SingularityApp есть официальные REST API v2 и hosted MCP. Для обычного v1 собственного MCP не требуется: можно подключить официальный remote endpoint и поверх него держать skill с правилами формулировок, подтверждений и маппингом сущностей.
2. API v2 уже покрывает нужные CRUD, даты, завершение, архив/разархивирование, чек-листы, канбан и batch. У API есть 64 опубликованные операции в OpenAPI 3.0; вызовы требуют Bearer token.
3. Публичная документация MCP не показывает фактический `tools/list`, но authenticated metadata probes его сняли: 1 tool с одним `mcp:read`, 35 с entity scopes без habits/kanban и 48 в full-scope Hermes-сессии. Полный snapshot подтверждает CRUD/lifecycle/views/habits/kanban и отсутствие явных MCP delete/batch tools.
4. Отдельного публичного sandbox/demo/test tenant или sample token не найдено. Новый аккаунт получает 14-дневный trial, но документация не подтверждает, что в trial доступна именно MCP-конфигурация.

## 1. Официальная модель данных и функции

Официальный glossary определяет Task, Checklist, Project, Section, Notebook, Note и Tag; системные папки включают Archive и Trash ([Glossary](https://singularity-app.com/wiki/glossary/), [Wiki index](https://singularity-app.com/wiki/)). Модель, релевантная skill, выглядит так:

| Сущность/сценарий | Подтверждённая модель | API/MCP значение для v1 |
|---|---|---|
| Задача | Task — основная единица планирования; есть title/note/priority/start/deadline/project/parent/group/tags и checked/complete. REST: `/v2/task`. | Основной объект skill: capture, выбор следующего действия, даты и статусы. [API Wiki](https://singularity-app.com/wiki/api/) · [OpenAPI](https://api.singularity-app.com/v2/api-json) |
| Проект | Project — контейнер общей цели; Section — `task-group` внутри проекта; есть вложенные проекты, kanban statuses. | Структурирование планов и декомпозиция. REST: `/v2/project`, `/v2/task-group`, `/v2/kanban-status`. [Glossary](https://singularity-app.com/wiki/glossary/) · [OpenAPI](https://api.singularity-app.com/v2/api-json) |
| Чек-лист | Checklist — пункты внутри Task, каждый можно отметить отдельно. | Подходит для еженедельного/вечернего обзора; REST CRUD + check/uncheck. [API Wiki](https://singularity-app.com/wiki/api/) · [OpenAPI](https://api.singularity-app.com/v2/api-json) |
| Note/Notebook | В публичной OpenAPI нет `/v2/note` или `/v2/notebook`: note — Task с `isNote=true`, notebook — Project с `isNotebook=true`; оба флага есть в DTO/response. В dashboard Note всё же отображается как отдельная permission-сущность. | Не смешивать «заметку» и обычную задачу в skill; точную MCP-модель считать не подтверждённой. [OpenAPI](https://api.singularity-app.com/v2/api-json) · [Dashboard permissions](https://singularity-app.com/wiki/account-dashboard/) |
| Теги | Tag — метка для группировки/фильтрации; поддерживается вложенный `parent`, hotkey, color. REST: `/v2/tag`. | Сохранить только рабочие теги; не создавать декоративные автоматически. [Glossary](https://singularity-app.com/wiki/glossary/) · [API Wiki](https://singularity-app.com/wiki/api/) |
| Даты и время | Task `start`, `deadline`, notifications, duration; Project `start/end`; списки фильтруются ISO date/datetime и `modifiedSince`; time-stat хранит интервалы. | Skill должен различать жёсткий deadline и плановую дату; timezone/date-only требуется нормализовать до вызова. [OpenAPI](https://api.singularity-app.com/v2/api-json) |
| Завершение/отмена | Есть отдельные task actions `complete`, `uncomplete`, `cancel`, `complete-today`; чек-лист — `check`, `uncheck`. | Не имитировать completion через произвольный PATCH, пока доступен action endpoint. [OpenAPI](https://api.singularity-app.com/v2/api-json) |
| Привычки | Habit и daily progress — отдельные сущности; progress `0/1/2` (empty/skip/full). | Не нужно для минимального task/project v1, но официальный MCP toolset `habits` его покрывает. [API Wiki](https://singularity-app.com/wiki/api/) |

## 2. REST API v2: точный публичный ground truth

Публичный [Swagger UI](https://api.singularity-app.com/v2/api) и машинный [OpenAPI JSON](https://api.singularity-app.com/v2/api-json) — источники точных operation IDs и DTO. Вызовы используют Bearer `rest-token`; сам токен создаётся в личном кабинете, права выбираются по сущностям и Read/Write ([Account Dashboard](https://singularity-app.com/wiki/account-dashboard/)).

### Операции и схемы, которые покрывают `singularity-jedi`

Ниже перечислены **точные REST operation IDs**, а не придуманные имена MCP tools. Они подтверждены OpenAPI и являются тем, что hosted MCP должен в итоге вызвать или обернуть:

```text
task:
  TaskController_list, TaskController_create, TaskController_getById,
  TaskController_update, TaskController_delete,
  TaskController_complete, TaskController_uncomplete, TaskController_cancel,
  TaskController_completeToday, TaskController_archive, TaskController_unarchive,
  TaskController_move, TaskController_changeColumn

project / sections / kanban:
  ProjectController_list, ProjectController_create, ProjectController_getById,
  ProjectController_update, ProjectController_delete,
  ProjectController_archive, ProjectController_unarchive
  TaskGroupController_list, TaskGroupController_create,
  TaskGroupController_getById, TaskGroupController_update, TaskGroupController_delete
  KanbanStatusController_list, KanbanStatusController_create,
  KanbanStatusController_getById, KanbanStatusController_update, KanbanStatusController_delete
  KanbanTaskStatusController_list, KanbanTaskStatusController_create,
  KanbanTaskStatusController_getById, KanbanTaskStatusController_update,
  KanbanTaskStatusController_delete

checklist:
  ChecklistItemController_list, ChecklistItemController_create,
  ChecklistItemController_getById, ChecklistItemController_update,
  ChecklistItemController_delete, ChecklistItemController_check,
  ChecklistItemController_uncheck

tag:
  TagController_list, TagController_create, TagController_getById,
  TagController_update, TagController_delete

habit / progress:
  HabitController_list, HabitController_create, HabitController_getById,
  HabitController_update, HabitController_delete
  HabitDailyProgressController_list, HabitDailyProgressController_create,
  HabitDailyProgressController_getById, HabitDailyProgressController_update,
  HabitDailyProgressController_delete

time / batch:
  TimeStatController_list, TimeStatController_create,
  TimeStatController_getById, TimeStatController_update,
  TimeStatController_delete, TimeStatController_deleteBulk
  BatchController_execute
```

Ключевые публичные JSON schemas:

- `TaskCreateDto`: обязательно `title`; опционально `note`, `priority` (`0/1/2`), `start`, `deadline`, `projectId`, `parent`, `group`, `tags[]`, `isNote`, notifications и duration. `TaskUpdateDto` позволяет менять те же поля, а также `checked`, `complete`, `deleteDate`, `kanbanStatusId`.
- `ProjectCreateDto`: обязательно `title`; `note`, `start/end`, `parent`, `journalDate/deleteDate`, `isNotebook` и display fields. `ProjectUpdateDto` — partial update; archive DTO содержит `journalDate`.
- `ChecklistItemCreateDto`: обязательны `parent` (Task ID) и `title`; `done` и `parentOrder` опциональны. Update меняет title/done/parent/order; отдельные action endpoints check/uncheck.
- `TagCreateDto`: обязательно `title`; `parent`, `parentOrder`, `hotkey`, `color`; update в текущем JSON также помечен обязательным `title`.
- `BatchRequestDto`: `operations[]`, каждая операция имеет обязательные `method` (`POST|PATCH|DELETE`) и `path` (начинается с `/v2/`), опционально `body`, `uuid` (idempotency) и `tempId`. Response возвращает `results[]` и `tempIdMap`. GET внутри batch схемой не разрешён.

### Что реально возможно через REST

| Действие | Подтверждение | Ограничение/нюанс |
|---|---|---|
| Читать | GET list/get для всех перечисленных сущностей; pagination `maxCount` до 1000, `offset`, `modifiedSince`, sparse `fields`. | Данные аккаунта не публичны; нужен token. [OpenAPI](https://api.singularity-app.com/v2/api-json) |
| Создавать | POST task/project/task-group/checklist/tag/habit/kanban/time и batch POST. | Recurring task API Wiki всё ещё не разрешает создавать через API; обычная задача поддерживается. [API Wiki](https://singularity-app.com/wiki/api/) |
| Редактировать | PATCH по ID для task/project/section/checklist/tag/habit/kanban/time. | PATCH partial, но конкретная обязательность поля зависит от DTO. [OpenAPI](https://api.singularity-app.com/v2/api-json) |
| Завершать | Task complete/uncomplete/cancel/complete-today; checklist check/uncheck; habit progress. | MCP wiki не публикует отдельные имена этих tools, только сущности/«add and edit». [MCP Wiki](https://singularity-app.com/wiki/mcp/) |
| Архивировать | Task и Project имеют `/archive` и `/unarchive`; PATCH также содержит `journalDate`; списки умеют `includeArchived`. | Не считать архив тем же, что permanent delete. [OpenAPI](https://api.singularity-app.com/v2/api-json) |
| Удалять | DELETE по ID для task/project/section/checklist/tag/habit/kanban/time; wiki прямо называет удаление task через DELETE irreversible. | До destructive DELETE skill должен запросить подтверждение; для task/project есть мягкий `deleteDate`/Trash. [API Wiki](https://singularity-app.com/wiki/api/) |
| Batch | REST `/v2/batch` подтверждён, включая `uuid` и `tempId`; отдельные POST/PATCH/DELETE можно выполнить одним запросом. | Не опубликован отдельный MCP toolset `batch`; MCP batch не подтверждён без `tools/list`. |
| Webhooks/events | Не поддерживаются: Wiki прямо говорит, что API не имеет webhooks, event streams или subscriptions. | Для реактивного агента нужен polling или собственный event layer. [API Wiki](https://singularity-app.com/wiki/api/) |

Замечена документационная рассинхронизация: Wiki описывает bulk-delete time records как `POST /v2/time-stat/delete-bulk`, но актуальный OpenAPI JSON публикует `DELETE /v2/time-stat` с operation ID `TimeStatController_deleteBulk` и фильтрами `dateFrom/dateTo/relatedTaskId`; для реализации брать текущий Swagger/OpenAPI и делать live smoke-test. [Wiki](https://singularity-app.com/wiki/api/) · [OpenAPI](https://api.singularity-app.com/v2/api-json)

## 3. Официальный hosted MCP

### Установка и auth

Официальная инструкция — [MCP Wiki](https://singularity-app.com/wiki/mcp/):

```json
{
  "mcpServers": {
    "singularity": {
      "url": "https://mcp.singularity-app.com/mcp"
    }
  }
}
```

Можно ограничить URL query `toolsets`:

```text
https://mcp.singularity-app.com/mcp?toolsets=tasks,projects,meta,habits,kanban,tags,time,system
```

Опубликованные toolsets: `tasks`, `projects`, `meta`, `habits`, `kanban`, `tags`, `time`, `system`. Отдельного публичного `checklists` или `batch` toolset в инструкции нет; это не доказывает, что таких tools нет внутри другого набора.

Для статического доступа создаётся token в [Account Dashboard](https://singularity-app.com/wiki/account-dashboard/): один token привязан к одному account, права выбираются по entities (Project, Task Group, Task, Note, Checklist, Tag, Habit, Kanban Board, Time Statistics) и Read/Write; token используется и для REST, и для MCP. Документация MCP требует Pro/Elite; dashboard сообщает, что API usage currently free.

Анонимные read-only probes 2026-08-08:

| Probe | Наблюдение | Вывод |
|---|---|---|
| `GET https://mcp.singularity-app.com/mcp` | HTTP 405, JSON `POST is the only supported method on /mcp`. | Это hosted HTTPS endpoint с POST-only route; не предполагать локальный stdio или GET/SSE без auth smoke-test. [endpoint](https://mcp.singularity-app.com/mcp) |
| `POST /mcp` с обычным MCP `initialize` без Authorization | HTTP 401, `WWW-Authenticate: Bearer`, scopes перечислены сервером. | Auth обязателен до `initialize`/`tools/list`; тест не менял данные. [endpoint](https://mcp.singularity-app.com/mcp) |
| Protected-resource metadata | `resource=https://mcp.singularity-app.com/mcp`, auth server `https://me.singularity-app.com`, bearer header; scopes: `tasks:read/write/check`, `projects:read/write`, `habits:read/write`, `tags:read/write`, `kanban:read/write`, `time_stat:read/write`, `checklists:read/write`, `mcp:read/write`. | Точные machine-readable scopes подтверждены. [metadata](https://mcp.singularity-app.com/.well-known/oauth-protected-resource/mcp) |
| OAuth discovery | `authorization_endpoint=/oauth/authorize`, `token_endpoint=/oauth/token`, `registration_endpoint=/oauth/register`, `introspection/revocation`; code + refresh_token grants; PKCE `S256`; dynamic client metadata supported. | Remote clients могут идти через OAuth; не хранить пароль в skill. [OAuth metadata](https://me.singularity-app.com/.well-known/oauth-authorization-server) |
| Metadata `resource_documentation` | Указывает `https://mcp.singularity-app.com/docs`, но анонимный GET этой ссылки в проверке вернул 404. | Не использовать `/docs` как подтверждение tool contract; опираться на Wiki/OpenAPI и authenticated `tools/list`. [docs URL](https://mcp.singularity-app.com/docs) |

### Точные MCP tool names и schemas: что подтверждено

**Подтверждено live:** server `singularity-mcp ^2.0.1`, protocol `2025-11-25`, 48 точных Tool objects с names, titles, descriptions, `inputSchema` и annotations. Полный JSONL snapshot находится в [singularity-mcp-tools.md](singularity-mcp-tools.md). Он содержит 35 core tools и 13 full-scope additions: habits, habit progress, kanban statuses и `task_change_column`.

**Не подтверждено:** причинное соответствие каждого OAuth scope конкретному tool без A/B probe; output/side-effect semantics; rate limits; фактическая idempotency; наличие транзакций. В 48 именах нет явных permanent-delete и batch tools. Следующий live acceptance требует уже не discovery, а отдельные disposable create/update/archive/check smokes с ручным подтверждением; permanent delete через hosted MCP не обещать.

### Сторонние MCP

- Exact поиск `SingularityApp` в [официальном MCP Registry](https://registry.modelcontextprotocol.io/v0.1/servers?search=SingularityApp) на 2026-08-08 вернул `count: 0`.
- Публичный GitHub repository search по `SingularityApp MCP` также вернул 0 результатов ([поиск](https://github.com/search?q=SingularityApp+MCP&type=repositories)); открытый сторонний сервер для SingularityApp не подтверждён.
- В выдаче Registry по `singularity` есть `io.github.ivaavimusic/singularity`, но это **Singularity Layer/Marketplace**, не SingularityApp task manager; не использовать как интеграцию. [Registry search](https://registry.modelcontextprotocol.io/v0.1/servers?search=singularity) · [его docs](https://studio.x402layer.cc/docs/agentic-access/mcp-server)

## 4. Sandbox/demo/test account

| Вопрос | Подтверждено | Статус для проверки |
|---|---|---|
| Отдельный официальный sandbox/demo tenant или sample token | Нет публичного упоминания в Wiki/MCP/API discovery; публичные endpoints требуют account token. | **Не подтверждено / считать отсутствующим** до ответа поддержки. |
| Бесплатный доступ для пробы | Новый account получает 14-day trial с большинством paid features; MCP docs требуют Pro/Elite. | Trial существует, но MCP token/endpoint в trial отдельно не обещаны — **нужно проверить на disposable account**. [Trial](https://singularity-app.com/wiki/subscription-activation-and-renewal/) |
| Публичные fixtures/тестовые данные | Не найдены в официальной документации/OpenAPI. | Для automated tests нужен свой account/fixture layer или mock, не production account. |

## 5. Пробелы и необходимость собственного MCP

Собственный MCP оправдан только если нужен хотя бы один из пунктов ниже:

1. **Стабильный versioned tool contract.** Hosted MCP публикует names/schemas только после auth и может менять их при `listChanged:false`; свой thin wrapper может оставить 6–10 безопасных intent-level tools (read task, create task, update task, complete, checklist, project) с зафиксированным JSON Schema.
2. **Детерминированный batch/idempotency.** REST batch есть, но в полном MCP `tools/list` отдельного batch tool нет; wrapper может явно принимать план операций, `uuid`, preview и подтверждение.
3. **Sandbox/local stdio.** Официально найден только hosted URL; нет опубликованного local package/fixture server. Собственный mock нужен для CI и demo без production data.
4. **Event-driven workflow.** Vendor API прямо не даёт webhooks/events/subscriptions; собственный poller/event layer нужен для «изменилось → агент реагирует».
5. **First-class notes/notebooks.** REST моделирует Note/Notebook через task/project flags, а dashboard permissions называет Note отдельной entity; wrapper может стабилизировать эту семантику.
6. **Policy/audit.** Нужны read-only profile, explicit confirmation для archive/delete, redaction, idempotency и audit log поверх vendor API.

Для обычного `singularity-jedi` v1 этих причин недостаточно: thin skill + официальный MCP URL проще и безопаснее; собственный сервер отложить до реального сценария, который подтверждённый hosted contract не покрывает.

## 6. Подтверждено / не подтверждено / вывод для v1

| Предмет | Подтверждено | Не подтверждено | Вывод для v1 |
|---|---|---|---|
| Официальный API | API v2, OpenAPI JSON/Swagger, Bearer token, CRUD; 64 операции. [OpenAPI](https://api.singularity-app.com/v2/api-json) | Rate limits, SLA и стабильность operation IDs | Ссылаться на OpenAPI; не кодировать undocumented limits. |
| Официальный MCP | Hosted endpoint, full-scope live snapshot из 48 tools; CRUD/lifecycle/archive/views/habits/kanban. [MCP Wiki](https://singularity-app.com/wiki/mcp/) · [snapshot](singularity-mcp-tools.md) | MCP batch/permanent delete, output/side effects и точный scope→tool mapping | Делать capability discovery; не обещать отсутствующие delete/batch tools. |
| Auth | Bearer header + OAuth discovery, PKCE S256, scopes. [resource metadata](https://mcp.singularity-app.com/.well-known/oauth-protected-resource/mcp) · [OAuth metadata](https://me.singularity-app.com/.well-known/oauth-authorization-server) | Scope-to-tool mapping и consent UI каждого MCP client | Least privilege; не просить пароль/API token в чате; использовать client OAuth/secret store. |
| Tasks/projects/checklists/tags/dates | REST DTO и точные MCP list/get/create/update/lifecycle schemas. [OpenAPI](https://api.singularity-app.com/v2/api-json) · [snapshot](singularity-mcp-tools.md) | Результаты и side effects tool calls | Skill mapping на domain intents; smoke-test с disposable data. |
| Notes/notebooks | `isNote`/`isNotebook` в REST DTO; dashboard permission labels. [Dashboard](https://singularity-app.com/wiki/account-dashboard/) | First-class MCP note tools и поведение archive/delete для notes | Обозначить как vendor-specific flags; не обещать отдельную note API. |
| Batch | `/v2/batch`, POST/PATCH/DELETE operations, UUID/tempId. [OpenAPI](https://api.singularity-app.com/v2/api-json) | В полном MCP snapshot batch tool отсутствует | Не строить batch-dependent v1 на hosted MCP. |
| Events | API explicitly lacks webhooks/events/subscriptions. [API Wiki](https://singularity-app.com/wiki/api/) | Internal polling guarantees | В v1 только explicit pull; реактивность — отдельный backlog. |
| Sandbox | 14-day trial documented. [Trial](https://singularity-app.com/wiki/subscription-activation-and-renewal/) | MCP availability during trial; dedicated demo account/fixtures | Не обещать test account; тестировать на отдельном user account или mock. |
| Third-party implementation | Registry/GitHub exact searches empty; unrelated Singularity Layer excluded. | Private/unindexed repos | Не добавлять dependency; official hosted MCP — единственный подтверждённый интеграционный путь. |

## Рекомендация для `singularity-jedi` v1

Сделать skill-only инструкцию: объяснять сущности и подтверждения, предлагать официальный URL MCP, требовать least-privilege OAuth и всегда сверять фактические capabilities через authenticated `tools/list`. Использовать зафиксированный snapshot для fake MCP, но не считать его вечным контрактом. Собственный MCP и webhook/poller добавлять только после конкретного провала hosted MCP; mock остаётся тестовой обвязкой.
