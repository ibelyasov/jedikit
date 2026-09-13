# SingularityApp и MCP для `singularity-jedi`

Дата первоначальной проверки: **2026-08-08**. Authenticated metadata probes дополнены **2026-08-09** (Europe/Moscow). Публичные официальные источники повторно проверены **2026-09-13**; авторизованный `tools/list` не повторялся.

Первоначальная проверка была read-only: открыты официальная Wiki, публичная OpenAPI-схема и OAuth/MCP discovery; к пользовательскому аккаунту, токену и данным доступа не было. В Context7 `SingularityApp` не разрешился как библиотека; для самого протокола использован официальный `/modelcontextprotocol/modelcontextprotocol` (схема Tool и transport). Контракт MCP требует у каждого Tool `name` и валидный JSON Schema object `inputSchema`; `description` опционален ([MCP Tool schema](https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/schema/2025-11-25/schema.json), [MCP tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)). Стандарт описывает stdio и Streamable HTTP ([transports](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/basic/transports.mdx)). Последующие probes не вызывали tools и не читали пользовательские данные: least-privilege опыт записан в [singularity-mcp-live-probe.md](singularity-mcp-live-probe.md), исторический каталог 48 tools — в [singularity-mcp-tools.md](singularity-mcp-tools.md), четыре исторических server prompts — в [singularity-mcp-prompts.md](singularity-mcp-prompts.md).

## Вопрос, маршрут чтения и уровни доказательства

**Вопрос:** какие возможности официально предоставляет SingularityApp через REST
и hosted MCP, какие точные MCP contracts действительно наблюдались, и какие
ограничения должен учитывать JediKit, не смешивая provider evidence с
продуктовыми решениями?

Маршрут чтения: этот файл даёт публичную модель, REST ground truth, auth и общий
MCP capability boundary. Затем [least-privilege probe](singularity-mcp-live-probe.md)
фиксирует первый `mcp:read` опыт, [tool snapshot](singularity-mcp-tools.md) — полный
исторический `tools/list`, а [prompt snapshot](singularity-mcp-prompts.md) —
исторические server prompts и их анализ. Канонический scope и правила JediKit
берутся только из [product decisions](product-decisions.md).

В тексте используются три уровня доказательства:

- **Текущая официальная документация:** публичные Wiki, OpenAPI и OAuth metadata,
  повторно прочитанные 2026-09-13; они подтверждают опубликованные возможности,
  но не внутреннюю реализацию MCP.
- **Наблюдавшийся runtime snapshot:** авторизованные metadata-only probes
  2026-08-09. Они подтверждают только ответ той сессии и не выдаются за текущий
  каталог или проверку side effects.
- **Продуктовое решение:** локальный журнал JediKit. Оно определяет разрешённый
  runtime scope, но не используется как источник фактов о provider.

## Краткий вывод

1. У SingularityApp есть независимые публичные интерфейсы: REST API v2 и hosted MCP. Текущий продуктовый выбор JediKit — использовать hosted MCP без REST fallback или собственного MCP; это решение проекта, а не вывод о внутренней реализации provider ([product decisions](product-decisions.md)).
2. REST API v2 публикует CRUD, даты, завершение, архив/разархивирование, чек-листы, канбан и batch. У API есть 64 операции в OpenAPI 3.0; вызовы требуют Bearer token. Наличие REST operation не доказывает одноимённую MCP capability.
3. Публичная документация MCP не показывает фактические tool names или JSON Schema. Она теперь отдельно документирует `system` как Batch toolset: он выключен по умолчанию и допускает до 20 операций в одном запросе. Это публичное описание capability, а не точный tool contract. Authenticated probes 2026-08-09 сняли исторические snapshots: 1 tool с одним `mcp:read`, 35 с entity scopes без habits/kanban и 48 в full-scope Hermes-сессии; в том 48-tool snapshot явных delete/batch tools не было.
4. В повторно просмотренных официальных страницах не найден отдельный sandbox/demo/test tenant или sample token. Текущая subscription Wiki 2026-09-13 подтверждает 14-дневный trial для нового аккаунта, но не обещает доступность MCP в trial.

## 1. Официальная модель данных и функции

Официальный glossary определяет Task, Checklist, Project, Section, Notebook, Note и Tag; системные папки включают Archive и Trash ([Glossary](https://singularity-app.com/wiki/glossary/), [Wiki index](https://singularity-app.com/wiki/)). Таблица разделяет возможности REST от текущего runtime scope JediKit:

| Сущность/сценарий | Подтверждённая модель | Граница REST, MCP и продукта |
|---|---|---|
| Задача | Task — основная единица планирования; есть title/note/priority/start/deadline/project/parent/group/tags и checked/complete. REST: `/v2/task`. | REST fields подтверждены текущей OpenAPI. Точный MCP input contract подтверждён только историческим snapshot; task является runtime scope `jedikit-tasks` по [product decisions](product-decisions.md). |
| Проект | Project — контейнер общей цели; Section — `task-group` внутри проекта; есть вложенные проекты, kanban statuses. | REST публикует `/v2/project`, `/v2/task-group`, `/v2/kanban-status`. JediKit использует projects, но исключает kanban из v1 scope по product decisions. [Glossary](https://singularity-app.com/wiki/glossary/) · [OpenAPI](https://api.singularity-app.com/v2/api-json) |
| Чек-лист | Checklist — пункты внутри Task, каждый можно отметить отдельно. | REST публикует CRUD + check/uncheck. Это не доказывает текущую MCP schema и само по себе не назначает checklist роль в daily/weekly workflow. [API Wiki](https://singularity-app.com/wiki/api/) · [OpenAPI](https://api.singularity-app.com/v2/api-json) |
| Note/Notebook | В публичной OpenAPI нет `/v2/note` или `/v2/notebook`: note — Task с `isNote=true`, notebook — Project с `isNotebook=true`; оба флага есть в DTO/response. В dashboard Note всё же отображается как отдельная permission-сущность. | Это REST/dashboard representation; first-class MCP note/notebook tools и их semantics публично не подтверждены. [OpenAPI](https://api.singularity-app.com/v2/api-json) · [Dashboard permissions](https://singularity-app.com/wiki/account-dashboard/) |
| Теги | Tag — метка для группировки/фильтрации; поддерживается вложенный `parent`, hotkey, color. REST: `/v2/tag`. | REST capability не задаёт продуктовую политику создания или хранения тегов; текущие правила находятся в product decisions. [Glossary](https://singularity-app.com/wiki/glossary/) · [API Wiki](https://singularity-app.com/wiki/api/) |
| Даты и время | Task `start`, `deadline`, notifications, duration; Project `start/end`; списки фильтруются ISO date/datetime и `modifiedSince`; time-stat хранит интервалы. | REST fields и filters подтверждены; семантика `start`/`deadline` и отсутствие time-stat в JediKit задаются product decisions, а не API. [OpenAPI](https://api.singularity-app.com/v2/api-json) |
| Завершение/отмена | Есть отдельные REST task actions `complete`, `uncomplete`, `cancel`, `complete-today`; чек-лист — `check`, `uncheck`. | REST action endpoints не доказывают текущие MCP tool names. Специализированные MCP lifecycle tools видны только в snapshot 2026-08-09. [OpenAPI](https://api.singularity-app.com/v2/api-json) |
| Привычки | Habit и daily progress — отдельные REST сущности; progress `0/1/2` (empty/skip/full). | Публичный Singularity MCP toolset `habits` существует, но JediKit habits использует только Habitify MCP; Singularity habits не входят в runtime scope. [API Wiki](https://singularity-app.com/wiki/api/) · [product decisions](product-decisions.md) |

## 2. REST API v2: точный публичный ground truth

Публичный [Swagger UI](https://api.singularity-app.com/v2/api) и машинный [OpenAPI JSON](https://api.singularity-app.com/v2/api-json) — источники точных operation IDs и DTO. Вызовы используют Bearer `rest-token`; сам токен создаётся в личном кабинете, права выбираются по сущностям и Read/Write ([Account Dashboard](https://singularity-app.com/wiki/account-dashboard/)).

### Релевантные REST операции и схемы

Ниже перечислены **точные REST operation IDs**, подтверждённые текущей OpenAPI. Это отдельный REST contract; официальные источники не раскрывают, использует ли hosted MCP эти endpoints или общий backend.

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
| Завершать | REST Task complete/uncomplete/cancel/complete-today; checklist check/uncheck; habit progress. | MCP Wiki не публикует отдельные имена или schemas этих tools. [MCP Wiki](https://singularity-app.com/wiki/mcp/) |
| Архивировать | Task и Project имеют `/archive` и `/unarchive`; PATCH также содержит `journalDate`; списки умеют `includeArchived`. | Не считать архив тем же, что permanent delete. [OpenAPI](https://api.singularity-app.com/v2/api-json) |
| Удалять | REST DELETE по ID для task/project/section/checklist/tag/habit/kanban/time; Wiki прямо называет task DELETE irreversible. | Эти REST endpoints не доказывают MCP delete tool; JediKit confirmation policy задана отдельно в product decisions. [API Wiki](https://singularity-app.com/wiki/api/) |
| Batch | REST `/v2/batch` подтверждён, включая `uuid` и `tempId`; отдельные POST/PATCH/DELETE можно выполнить одним запросом. | MCP Wiki документирует toolset `system`, но имя/schema tool и соответствие REST Batch не опубликованы. |
| Webhooks/events | Не поддерживаются: Wiki прямо говорит, что API не имеет webhooks, event streams или subscriptions. | Для реактивного агента нужен polling или собственный event layer. [API Wiki](https://singularity-app.com/wiki/api/) |

Замечена документационная рассинхронизация: Wiki описывает bulk-delete time records как `POST /v2/time-stat/delete-bulk`, но актуальный OpenAPI JSON публикует `DELETE /v2/time-stat` с operation ID `TimeStatController_deleteBulk` и фильтрами `dateFrom/dateTo/relatedTaskId`. Это REST-only drift; JediKit не использует REST fallback или time-stat. [Wiki](https://singularity-app.com/wiki/api/) · [OpenAPI](https://api.singularity-app.com/v2/api-json)

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
https://mcp.singularity-app.com/mcp?toolsets=tasks,projects,meta,habits,kanban,tags,system
```

На 2026-09-13 публично перечислены toolsets `tasks`, `projects`, `meta`, `habits`, `kanban`, `tags` и `system`; `tasks` включает задачи и checklists, а `system` включает Batch. `system` выключен по умолчанию, его рекомендуют включать только при необходимости, и документация заявляет предел до 20 операций на один запрос. Страница не публикует точное имя Batch tool, его `inputSchema`, атомарность, rollback или idempotency. Ранее указанного здесь `time` нет в текущем публичном списке toolsets, хотя OAuth metadata продолжает объявлять `time_stat:read/write`; нельзя из scope выводить наличие отдельного toolset или tool. [MCP Wiki](https://singularity-app.com/wiki/mcp/)

Текущая публичная MCP-инструкция описывает OAuth: клиент открывает страницу SingularityApp, пользователь входит и подтверждает доступ, а приложение затем видно в Connected Apps. REST API отдельно использует account token из [Account Dashboard](https://singularity-app.com/wiki/account-dashboard/). Не следует переносить REST-token в MCP-конфигурацию или считать его текущим рекомендуемым MCP auth. MCP и REST помечены как Pro/Elite features. [MCP Wiki](https://singularity-app.com/wiki/mcp/) · [API Wiki](https://singularity-app.com/wiki/api/)

Анонимные read-only probes 2026-08-08:

| Probe | Наблюдение | Вывод |
|---|---|---|
| `GET https://mcp.singularity-app.com/mcp` | HTTP 405, JSON `POST is the only supported method on /mcp`. | Это hosted HTTPS endpoint с POST-only route; не предполагать локальный stdio или GET/SSE без auth smoke-test. [endpoint](https://mcp.singularity-app.com/mcp) |
| `POST /mcp` с обычным MCP `initialize` без Authorization | HTTP 401, `WWW-Authenticate: Bearer`, scopes перечислены сервером. | Auth обязателен до `initialize`/`tools/list`; тест не менял данные. [endpoint](https://mcp.singularity-app.com/mcp) |
| Protected-resource metadata | `resource=https://mcp.singularity-app.com/mcp`, auth server `https://me.singularity-app.com`, bearer header; scopes: `tasks:read/write/check`, `projects:read/write`, `habits:read/write`, `tags:read/write`, `kanban:read/write`, `time_stat:read/write`, `checklists:read/write`, `mcp:read/write`. | Точные machine-readable scopes подтверждены. [metadata](https://mcp.singularity-app.com/.well-known/oauth-protected-resource/mcp) |
| OAuth discovery | `authorization_endpoint=/oauth/authorize`, `token_endpoint=/oauth/token`, `registration_endpoint=/oauth/register`, `introspection/revocation`; code + refresh_token grants; PKCE `S256`; dynamic client metadata supported. | Remote clients могут идти через OAuth; не хранить пароль в skill. [OAuth metadata](https://me.singularity-app.com/.well-known/oauth-authorization-server) |
| Metadata `resource_documentation` | Указывает `https://mcp.singularity-app.com/docs`, но анонимный GET этой ссылки в проверке вернул 404. | Не использовать `/docs` как подтверждение tool contract; опираться на Wiki/OpenAPI и authenticated `tools/list`. [docs URL](https://mcp.singularity-app.com/docs) |

### Точные MCP tool names и schemas: историческое подтверждение

**Подтверждено live только 2026-08-09:** server `singularity-mcp ^2.0.1`, protocol `2025-11-25`, 48 точных Tool objects с names, titles, descriptions, `inputSchema` и annotations. Полный JSONL snapshot находится в [singularity-mcp-tools.md](singularity-mcp-tools.md). Он содержит 35 core tools и 13 full-scope additions: habits, habit progress, kanban statuses и `task_change_column`. Публичные источники 2026-09-13 не позволяют подтвердить, что этот count, version и schemas остаются текущими.

**Текущими публичными источниками подтверждено:** hosted OAuth endpoint, toolset categories и Batch через `system` до 20 операций. **Не подтверждено:** точное имя/schema Batch tool; актуальный полный `tools/list`; причинное соответствие каждого OAuth scope конкретному tool; output/side-effect semantics; rate limits; фактическая idempotency; транзакции/rollback. В исторических 48 именах нет явных permanent-delete и batch tools. Публичная MCP-страница приводит delete как возможное пользовательское действие и рекомендует approval для delete, но не публикует delete tool name/schema; permanent delete через hosted MCP всё ещё нельзя обещать без runtime discovery.

Отдельный будущий acceptance contract, **не выполненный в этом research**:
сначала текущий authenticated `tools/list`, затем только на отдельном disposable
account/data — минимальные create → read-back → update → read-back → archive →
read-back и check → read-back smokes. Каждая запись требует ручного подтверждения;
permanent delete в этот набор не входит. Такой probe проверит outputs и side
effects, которых metadata discovery не доказывает.

### Сторонние MCP

- Exact поиск `SingularityApp` в [официальном MCP Registry](https://registry.modelcontextprotocol.io/v0.1/servers?search=SingularityApp) на 2026-08-08 вернул `count: 0`.
- Публичный GitHub repository search по `SingularityApp MCP` также вернул 0 результатов ([поиск](https://github.com/search?q=SingularityApp+MCP&type=repositories)); открытый сторонний сервер для SingularityApp не подтверждён.
- В выдаче Registry по `singularity` есть `io.github.ivaavimusic/singularity`, но это **Singularity Layer/Marketplace**, не SingularityApp task manager; не использовать как интеграцию. [Registry search](https://registry.modelcontextprotocol.io/v0.1/servers?search=singularity) · [его docs](https://studio.x402layer.cc/docs/agentic-access/mcp-server)

## 4. Sandbox/demo/test account

| Вопрос | Подтверждено | Статус для проверки |
|---|---|---|
| Отдельный официальный sandbox/demo tenant или sample token | В просмотренных Wiki/MCP/API discovery страницах не найдено публичного упоминания; REST требует account token, MCP — OAuth. | **Не подтверждено**; отсутствие в просмотренных источниках не доказывает отсутствие предложения provider. |
| Бесплатный доступ для пробы | Subscription Wiki повторно проверена 2026-09-13: новый account получает 14-day trial с большинством paid features; MCP docs требуют Pro/Elite. | Trial существует, но MCP availability в trial отдельно не обещана; проверять можно только на отдельном disposable account после решения владельца. [Trial](https://singularity-app.com/wiki/subscription-activation-and-renewal/) |
| Публичные fixtures/тестовые данные | Не найдены в просмотренной официальной документации/OpenAPI. | Public fixture contract не подтверждён. Для automated tests нужен отдельный test account/fixture layer или mock; production account/data не использовать. |

## 5. Пробелы и необходимость собственного MCP

Собственный MCP оправдан только если нужен хотя бы один из пунктов ниже:

1. **Стабильный versioned tool contract.** Hosted MCP публикует names/schemas только после auth и может менять их при `listChanged:false`; свой thin wrapper может оставить 6–10 безопасных intent-level tools (read task, create task, update task, complete, checklist, project) с зафиксированным JSON Schema.
2. **Детерминированный batch/idempotency.** REST batch и публичный MCP `system` Batch есть, но публичного MCP tool schema и гарантий atomicity/rollback/idempotency нет; исторический 48-tool snapshot был снят до появления этого публичного описания и не содержал batch tool. Wrapper может явно принимать план операций, `uuid`, preview и подтверждение.
3. **Sandbox/local stdio.** Официально найден только hosted URL; нет опубликованного local package/fixture server. Собственный mock нужен для CI и demo без production data.
4. **Event-driven workflow.** Vendor API прямо не даёт webhooks/events/subscriptions; собственный poller/event layer нужен для «изменилось → агент реагирует».
5. **First-class notes/notebooks.** REST моделирует Note/Notebook через task/project flags, а dashboard permissions называет Note отдельной entity; wrapper может стабилизировать эту семантику.
6. **Policy/audit.** Нужны read-only profile, explicit confirmation для archive/delete, redaction, idempotency и audit log поверх vendor API.

Текущий [product decision](product-decisions.md) уже выбирает официальный hosted MCP без собственного MCP и без REST fallback. Перечень выше фиксирует возможные будущие причины пересмотра, но не меняет это решение.

## 6. Подтверждено / не подтверждено / вывод для v1

| Предмет | Подтверждено | Не подтверждено | Вывод для v1 |
|---|---|---|---|
| Официальный API | API v2, OpenAPI JSON/Swagger, Bearer token, CRUD; 64 операции. [OpenAPI](https://api.singularity-app.com/v2/api-json) | Rate limits, SLA и стабильность operation IDs | Ссылаться на OpenAPI; не кодировать undocumented limits. |
| Официальный MCP | Hosted endpoint и OAuth; публичные toolset categories; `system` Batch до 20 операций; исторический full-scope snapshot из 48 tools с CRUD/lifecycle/archive/views/habits/kanban. [MCP Wiki](https://singularity-app.com/wiki/mcp/) · [snapshot](singularity-mcp-tools.md) | Текущий полный `tools/list`, точные Batch/delete schemas, atomicity/rollback, output/side effects и точный scope→tool mapping | Делать runtime capability discovery; Batch не включать по умолчанию и не обещать schema/transaction semantics. |
| Auth | Bearer header + OAuth discovery, PKCE S256, scopes. [resource metadata](https://mcp.singularity-app.com/.well-known/oauth-protected-resource/mcp) · [OAuth metadata](https://me.singularity-app.com/.well-known/oauth-authorization-server) | Scope-to-tool mapping и consent UI каждого MCP client | Least privilege; не просить пароль/API token в чате; использовать client OAuth/secret store. |
| Tasks/projects/checklists/tags/dates | REST DTO и исторические MCP list/get/create/update/lifecycle schemas. [OpenAPI](https://api.singularity-app.com/v2/api-json) · [snapshot](singularity-mcp-tools.md) | Текущие MCP schemas, результаты и side effects tool calls | Runtime discovery обязателен; REST contract не переносится в MCP. |
| Notes/notebooks | `isNote`/`isNotebook` в REST DTO; dashboard permission labels. [Dashboard](https://singularity-app.com/wiki/account-dashboard/) | First-class MCP note tools и поведение archive/delete для notes | Обозначить как vendor-specific flags; не обещать отдельную note API. |
| Batch | REST `/v2/batch` с POST/PATCH/DELETE operations и UUID/tempId; MCP Wiki теперь документирует `system` Batch до 20 операций. [OpenAPI](https://api.singularity-app.com/v2/api-json) · [MCP Wiki](https://singularity-app.com/wiki/mcp/) | Публичного имени/schema MCP Batch tool и гарантий атомарности/rollback нет; исторический 48-tool snapshot его не содержал | Не строить batch-dependent v1 без текущего runtime discovery; по умолчанию выполнять последовательно. |
| Events | API explicitly lacks webhooks/events/subscriptions. [API Wiki](https://singularity-app.com/wiki/api/) | Internal polling guarantees | В v1 только explicit pull; реактивность — отдельный backlog. |
| Sandbox | 14-day trial повторно подтверждён 2026-09-13. [Trial](https://singularity-app.com/wiki/subscription-activation-and-renewal/) | MCP availability during trial; dedicated demo account/fixtures | Trial не считать MCP sandbox; provider data tests требуют отдельного решения. |
| Third-party implementation | Registry/GitHub exact searches empty; unrelated Singularity Layer excluded. | Private/unindexed repos | Не добавлять dependency; official hosted MCP — единственный подтверждённый интеграционный путь. |

## Связь с текущим решением JediKit

Канонические требования находятся в [product decisions](product-decisions.md): `jedikit-tasks` использует только официальный hosted MCP, без REST/third-party fallback, собственного MCP, kanban и time statistics. Исторический snapshot пригоден как research evidence и fake-provider fixture, но не как текущий provider contract; runtime должен сверять capabilities через текущий `tools/list`. Пересмотр собственного MCP имеет смысл только после конкретного, воспроизводимого провала требуемой capability hosted contract, а не из-за расхождения REST и MCP inventories само по себе.
