# Prompts официального MCP SingularityApp

**Отчётный срез:** 2026-08-08. **Фактический live metadata probe:** 2026-08-09 (Europe/Moscow). **Статус:** исследование шаблонов, без исполнения полученных сообщений и без чтения данных аккаунта.

## Короткий вывод

Официальный сервер вернул ровно четыре MCP prompts: `plan_my_day`, `triage_inbox`, `weekly_review` и `summarize_project`. Они являются готовыми текстовыми макросами, а не отдельными безопасными операциями: каждый результат `prompts/get` — одно сообщение с ролью `user`, в тексте которого перечислены будущие вызовы Singularity tools. MCP определяет prompts как выбираемые пользователем шаблоны, поэтому получение шаблона не равно его выполнению ([MCP Prompts, 2025-11-25](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/server/prompts.mdx)).

Для `singularity-jedi` это полезные заготовки для обнаружения данных и структуры отчёта, но не каноническая методология. Наиболее существенные конфликты — жёсткие часы дня, лимит **6 часов** фокусной работы и фиксированные группы **3–5/2–3/2–3**, автоматическая установка даты `09:00`, а также упрощение triage до трёх веток. В v1 prompts можно использовать только как опциональные read/preview-шаблоны, обёрнутые правилами Jedi: следующий физический шаг, календарь и ресурс, разделение сущностей, явное подтверждение изменения обязательств и отсутствие универсальных числовых рецептов ([`jedi-method-primary.md`](jedi-method-primary.md), разделы «Приоритеты для Agent Skill» и DT-1—DT-9).

## Граница и воспроизводимость probe

Проверялся официальный MCP endpoint [`https://mcp.singularity-app.com/mcp`](https://mcp.singularity-app.com/mcp). Использована уже существовавшая авторизованная Hermes-сессия; новый OAuth не запускался, OAuth URL, client ID и токены в отчёт не попадают.

| Поле | Наблюдение |
| --- | --- |
| Клиент | `singularity-jedi-prompts-probe` `0.1.0`, Python MCP SDK из уже установленного Hermes Agent (`0.20.0`, сборка 2026.8.3) |
| MCP protocol | `2025-11-25` (из `initialize`) |
| Server | `name: singularity-mcp`, `version: ^2.0.1` |
| Разрешения сессии | `mcp:read`, `mcp:write`; `tasks:read/write/check`, `projects:read/write`, `tags:read/write`, `checklists:read/write`, `habits:read/write`, `kanban:read/write`, `time_stat:read/write` (сами scopes не являются секретами) |
| MCP capabilities | `prompts: {listChanged:false}`; также объявлены `tools` и `resources`, но они в этом probe не вызывались; notifications о смене списка prompts не обещаны |
| Разрешённые RPC | только `initialize`, `prompts/list`, `prompts/get` |
| Запрещённые/не выполнявшиеся действия | `tools/list`, `tools/call`, `resources/list`, `resources/read`, любые task/project/tag/checklist reads и любые записи/архивирование/удаление |
| Песочница/demo/test account | отдельная не подтверждена и не создавалась; использована существующая сессия только для metadata |

Полный предыдущий контекстный probe (без prompts и без чтения задач) находится в [`research/singularity-mcp-live-probe.md`](singularity-mcp-live-probe.md). Его результат не подменяет текущий prompts probe.

## Что именно требует MCP

Официальная спецификация описывает prompts как **user-controlled** шаблоны, которые клиент показывает пользователю для явного выбора. `prompts/list` принимает необязательный `cursor` и возвращает `prompts` с полями `name`, `title`, `description`, необязательным `arguments` и, при необходимости, `icons`; `nextCursor` используется для следующей страницы. Capability `prompts.listChanged` сообщает, будут ли уведомления об изменении списка ([спецификация prompts/list](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/server/prompts.mdx#listing-prompts)).

`prompts/get` принимает обязательный `name` и необязательную map `arguments`, а возвращает `description` и массив `messages`. У сообщения есть `role` и `content`; content может быть текстом либо embedded resource ([спецификация prompts/get](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/server/prompts.mdx#getting-a-prompt)). Сервер не исполняет инструкции из текста сам: это материал, который клиент решает, добавлять ли в контекст модели. Tools имеют отдельный `tools/call` и могут приводить к операциям, resources — отдельные `resources/read` для данных/контекста ([MCP tools](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/server/tools.mdx), [MCP resources](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/server/resources.mdx)).

## `prompts/list`: live-ответ

Сервер [`https://mcp.singularity-app.com/mcp`](https://mcp.singularity-app.com/mcp) вернул одну страницу без `nextCursor` (SDK обернул результат с `meta: null`):

| `name` | `title` | `description` | `arguments` |
| --- | --- | --- | --- |
| `plan_my_day` | `Plan my day` | `Plan today using today and overdue tasks with energy-aware scheduling.` | `[]` |
| `triage_inbox` | `Triage inbox` | `Sort inbox tasks into user's project structure with concrete next actions.` | `[]` |
| `weekly_review` | `Weekly review` | `Summarize the last 7 days of completed, cancelled, pending, and overdue work.` | `[]` |
| `summarize_project` | `Summarize project` | `Summarize one project: open vs completed tasks, blockers, and checklist progress.` | `[ { "name": "projectId", "description": "Project ID to summarize.", "required": true } ]` |

Иконок и серверных prompt metadata в элементах не было; `listChanged:false` означает только отсутствие обещания push-уведомлений, а не неизменность списка навсегда.

## `prompts/get`: live-ответы

Для трёх prompt без аргументов правильный вызов потребовал явно передать `arguments: {}`. Первая попытка с отсутствующим полем `arguments` дала подтверждённую ошибку SDK: `McpError: Invalid arguments for prompt <name>: Invalid input: expected object, received undefined`. Это не HTTP 400 и не вызов инструмента. Для `summarize_project` передан синтетический, заведомо не использовавшийся ID `P-00000000-0000-0000-0000-000000000000`; поэтому реальный проект не читался.

Общая форма каждого live-ответа с [`https://mcp.singularity-app.com/mcp`](https://mcp.singularity-app.com/mcp): `meta: null`, `description: null`, ровно одно `messages[0]`, `role: "user"`, `content.type: "text"`, `content.annotations: null`, `content.meta: null`. Схематично (поле `text` полностью приведено в подразделе prompt):

```json
{
  "meta": null,
  "description": null,
  "messages": [
    {
      "role": "user",
      "content": {
        "type": "text",
        "text": "<полный live-текст ниже>",
        "annotations": null,
        "meta": null
      }
    }
  ]
}
```

Ни один текст ниже не исполнялся.

### `plan_my_day`

Вызов: `prompts/get({"name":"plan_my_day","arguments":{}})`.

```text
You are a personal time-management coach. Plan the user's day.

Step 1 — gather data:
- task_list_overdue({ timezone: "<user_timezone>" }) — tasks with start date before today, still open
- task_list_today({ timezone: "<user_timezone>" }) — tasks scheduled for today, still open
- For each task, also call task_get(id) to see priority (0=HIGH, 1=NORMAL, 2=LOW), tags, and notes (Quill Delta format).

<user_timezone> is an IANA name (e.g. "Europe/Moscow") or an integer offset in minutes (e.g. -180).
If unknown, call get_my_context({ include: ["glossary"] }) first — it documents how to ask the user, or check the most recent task timestamps as a hint.

Step 2 — produce a tactical plan with energy management:
- **Morning (09:00–12:00) is peak focus time.** High priority + complex tasks go first.
- **After lunch (14:00–16:00)** is lower energy — schedule meetings, routine, or simple tasks.
- **17:00–18:00** — admin/email/inbox triage.
- **Lunch 12:00–13:00 is protected** — do NOT schedule.
- Group similar tasks (same project or tag) into blocks to reduce context-switching.
- If total time > 6h of focus work, warn the user and suggest rescheduling low-priority items to the next day via task_update(id, { start: "YYYY-MM-DDT09:00:00.000Z" }).

Step 3 — output the plan in the user's language. Use the format:
- **Morning**: 3-5 specific tasks with start times
- **Midday**: 2-3 tasks
- **Afternoon**: 2-3 tasks
- **Follow-ups**: any overdue items to address first thing tomorrow

Be specific and actionable. Avoid generic advice like "stay focused".
```

### `triage_inbox`

Вызов: `prompts/get({"name":"triage_inbox","arguments":{}})`.

```text
You are helping the user clear their inbox. Inbox = tasks without a project and without a start date.

Step 1 — gather data:
- task_list_inbox() — list all inbox tasks
- project_list({ "journalDate.isSet": false, "deleteDate.isSet": false, "removed.isSet": false, maxCount: 30 }) — list active projects to suggest grouping

Step 2 — for each inbox task, propose one of three actions in the user's language:
- **Assign to a project** (call task_update(id, { projectId, start: "YYYY-MM-DDT09:00:00.000Z" }) if a start date is needed) — preferred for tasks that clearly belong somewhere
- **Schedule for today** (task_update with start = today) — for tasks the user should do today
- **Archive** — for tasks that are no longer relevant - do NOT call any delete tool, just archive them (after user explisit confirmation by user).

Step 3 — group suggestions:
- Multiple similar tasks (same tag or same topic) — suggest creating a project or grouping under one existing project
- Tasks with no obvious home — ask the user which project to assign

Output a structured triage list: each inbox task with proposed action. Wait for user confirmation before applying any task_update.
```

В live-тексте сохранена опечатка `explisit`; это часть серверного шаблона, а не редакторская правка отчёта.

### `weekly_review`

Вызов: `prompts/get({"name":"weekly_review","arguments":{}})`.

```text
You are helping the user run a weekly review. Use ISO 8601 datetime for all date filters.

Step 1 — gather last-7-days data with explicit date ranges:
- task_list({ "checked.eq": 1, "completeLast.gte": "<7_days_ago_iso>", "completeLast.lte": "<now_iso>", "maxCount": 50 }) — tasks completed in the last week
- task_list({ "checked.eq": 2, "modificatedDate.gte": "<7_days_ago_iso>", "maxCount": 50 }) — tasks cancelled in the last week (use modificatedDate as proxy for cancellation time)
- task_list({ "checked.eq": 0, "maxCount": 50 }) — open tasks (pending work); `truncated: true` in response means there may be more, refine filter
- task_list_overdue({ timezone: "<user_timezone>" }) — currently overdue
- project_list({ "journalDate.isSet": false, maxCount: 30 }) — active projects for context

Compute "<7_days_ago_iso>" as today's date at 00:00:00 minus 7 days. Compute "<now_iso>" as current datetime in ISO 8601 UTC format.
<user_timezone> is an IANA name (e.g. "Europe/Moscow") or integer offset in minutes; if unknown, ask the user or infer from recent task timestamps.

Step 2 — produce the weekly review in the user's language with these sections:
- **Completed this week** — count + 3-5 highlights (by project or by tag)
- **Cancelled this week** — count + reason pattern if visible from titles
- **Still pending** — total open count + overdue count + any projects with many open tasks
- **Patterns spotted** — e.g. "5 of 7 cancellations were project X — consider trimming it"
- **Next week focus** — top 3 follow-up actions: which overdue to tackle first, which project to clear out, what to schedule

Be specific with counts and project names. Avoid generic motivational language.
```

### `summarize_project`

Вызов: `prompts/get({"name":"summarize_project","arguments":{"projectId":"P-00000000-0000-0000-0000-000000000000"}})`; ID синтетический, вызов не обращался к проекту.

```text
Summarize project "P-00000000-0000-0000-0000-000000000000". Run these calls:
- project_get({ id: "P-00000000-0000-0000-0000-000000000000" }) — project metadata, journalDate, deadline
- task_list({ projectId: "P-00000000-0000-0000-0000-000000000000", "maxCount": 50 }) — project tasks (any state); widen maxCount or refine filter if response shows truncated:true
- For each task with non-empty checklist: don't list items individually, just count how many tasks have checklists

Then produce in the user's language:
- **Open tasks**: count, grouped by priority (HIGH/NORMAL/LOW)
- **Completed this week**: filtered count from above ("checked.eq": 1, "completeLast.gte": 7_days_ago)
- **Overdue**: tasks with start < today and checked.eq=0
- **Blockers**: tasks overdue by 7+ days, or with priority HIGH and start already passed
- **Recommendation**: which 1-3 tasks to focus on next, or whether to archive the project if it has no recent activity
```

## Сопоставление с `jedi-method-primary.md`

Ниже используется именно операционализация в [`jedi-method-primary.md`](jedi-method-primary.md): безопасный контур «захват → triage → тип сущности → физический следующий шаг → выбор по календарю/ресурсу → выполнение → замыкание → ежедневный/еженедельный обзор» (ядро, строки 20–31), запрет универсальных часов/приоритетов и обязательное подтверждение изменения обязательств (строки 199–205).

### `plan_my_day`

- **Совпадает:** собирает открытые задачи на сегодня и просроченные; учитывает приоритеты, теги, заметки и часовой пояс; группирует похожие задачи; выдаёт конкретный план на языке пользователя. Это совместимо с идеей уменьшать переключения и выбирать наблюдаемый следующий шаг.
- **Расходится:** берёт только Today/overdue, а Jedi требует смотреть неделю и календарь, спросить `must/could`, ресурс и резерв (DT-5). Шаблон навязывает `09:00–12:00` как пик, `14:00–16:00` как низкую энергию, `17:00–18:00` как admin, защищённый обед `12:00–13:00`; это не подтверждённый универсальный рецепт. Он вводит порог **>6 часов** фокусной работы, фиксирует **3–5** утренних, **2–3** дневных и **2–3** послеобеденных задач и предлагает `task_update` на следующий день. В Jedi нет универсального лимита часов; при перегрузе нужно уменьшить обязательства/«Сегодня», а не автоматически проталкивать перенос (DT-8).
- **Переиспользовать:** timezone-нормализацию, read-only сбор Today/overdue, показ причин и группировку.
- **Заменить в skill:** запросить реальный календарь/окна/энергию, разделить `due`/`planned`/`target`, выбрать небольшой `must/could`-список и показать проектный следующий шаг. Любой перенос/изменение даты — только как preview с подтверждением; убрать фиксированные часы, 6h и квоты 3–5/2–3/2–3.

### `triage_inbox`

- **Совпадает:** начинается с входящих и предлагает разобрать их, а не считать прочтение обработкой; связывает задачу с проектом и просит подтверждение перед `task_update`; архивирует вместо безвозвратного удаления.
- **Расходится:** определяет inbox как «нет проекта **и** нет start date», хотя в Jedi это состояние необработанности, а дата — отдельная семантика. Три ветки (`assign`, `schedule today`, `archive`) не покрывают `idea`, `reference`, `meeting`, `waiting`, делегирование, уточнение, отказ или «оставить в inbox» (DT-1/DT-2). Жёстко прошит `maxCount:30` и старт `09:00` при назначении проекта; архив предлагается при субъективной нерелевантности. В тексте есть опечатка `explisit`.
- **Переиспользовать:** `task_list_inbox`, список активных проектов как подсказку, структурированный preview и ожидание явного подтверждения.
- **Заменить в skill:** сначала сохранить/показать исходный `raw_text`, спросить «это действие, проект, идея, справка, встреча или чужая просьба?», сформулировать один физический шаг; дату не проставлять по умолчанию. Архив/отмена/делегирование — отдельные ветви с причиной и подтверждением, а не три фиксированных действия.

### `weekly_review`

- **Совпадает:** выделяет недельный обзор, completed/cancelled/pending/overdue, активные проекты, паттерны и следующий фокус; использует явные ISO-диапазоны и предупреждает о `truncated:true`; избегает общей мотивационной риторики.
- **Расходится:** ровно **7 дней**, `maxCount:50` для задач и `30` для проектов, top **3** follow-ups; `checked.eq:2` + `modificatedDate` — лишь прокси отмены, а не подтверждённая дата/причина; UTC `now` и догадка о часовом поясе из последних timestamps. Не требует собрать все inbox-источники, просмотреть календарь на 1–2 недели, выбрать ближайший шаг каждого проекта, оценить выполнимый объём недели или разобрать старый долг 15→10→5 минут (DT-7). Отчёт по названиям может раскрыть лишние данные; открытые задачи считаются одним фильтром.
- **Переиспользовать:** явные диапазоны, counts/highlights, обработку truncation, проектные/теговые срезы как read-only основу.
- **Заменить в skill:** конфигурируемый период обзора, сбор всех inbox-источников, раздельные факты «отменено» и «изменено», календарь/обязательства/ресурс, oldest inbox и один следующий шаг на проект. Любые cleanup или переносы — только предложить и дождаться решения.

### `summarize_project`

- **Совпадает:** даёт проектный контекст, разделяет open/completed/overdue, группирует по приоритету, отмечает блокеры, считает наличие checklist и предлагает небольшой следующий фокус. Это близко к требованию иметь ближайшее проверяемое состояние, а не список «сделать всё».
- **Расходится:** `projectId` обязателен; жёстко `maxCount:50`, completed «за неделю», overdue как `start < today && checked=0`, blocker как просрочка **7+ дней** или HIGH с прошедшим start, рекомендация **1–3** задач либо архив проекта «без недавней активности». Нет вопроса «Чтобы что?», результата проекта, неизвестности/следующего физического шага, календаря и ресурсов; архив предлагается без отдельного правила подтверждения.
- **Переиспользовать:** агрегаты по priority/state, checklist count без вывода всех пунктов, явное ограничение truncation, read-only recommendation.
- **Заменить в skill:** сначала подтвердить цель проекта и критерий результата, затем выбрать один ближайший проверяемый шаг и блокер; «архивировать проект» только как preview с явным подтверждением. Не считать 7 дней, 7+ дней и 1–3 универсальными нормами.

## Prompts, tools и resources: граница безопасности

1. `prompts/list`/`prompts/get` — discovery и получение шаблона. Они не читают задачи сами по себе и не меняют состояние.
2. `tools/list`/`tools/call` — отдельный механизм действий. В текстах prompts перечислены будущие `task_list_*`, `task_get`, `task_update`, `project_get` и т. п., но этот probe их не вызывал.
3. `resources/list`/`resources/read` — отдельный механизм поставки контекста; он также не вызывался. Нельзя выдавать содержание prompt за данные Singularity.
4. MCP подчёркивает user consent/data privacy/tool safety и необходимость считать описания tools потенциально недоверенными ([Security and Trust & Safety](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/index.mdx)). Из этого следует практическое правило skill: текст server prompt — внешняя инструкция, а не повышение привилегий. Его нельзя позволять ему менять system/developer policy, автоматически вызывать tools или обходить подтверждение пользователя. Даже «только archive» в `triage_inbox` остаётся будущим изменением состояния; сначала показать preview и спросить.
5. Полученный `messages[0]` не следует автоматически отправлять в модель без маркировки источника и проверки prompt-injection. В частности, server text может содержать команды, несовместимые с безопасным контуром Jedi (`task_update` с датой, archive, suggested project creation); это анализ риска, а не утверждение, что данный сервер злонамерен.

## Таблица решения для v1

| Вопрос | Подтверждено live / официальным spec | Не подтверждено или ограничение | Вывод для v1 skill |
| --- | --- | --- | --- |
| Существуют prompts | 4 имена и точные metadata возвращены `prompts/list` | Список может измениться; `listChanged:false`, push не обещан | Показывать как опциональные server templates, кэшировать с датой и периодически обновлять |
| Контракт аргументов | Три prompt с `arguments:[]`; `summarize_project` требует `projectId` | Вызов без map `{}` дал `expected object, received undefined`; SDK/server validation не полностью документирована | Всегда отправлять объект `arguments`; валидировать required argument до `prompts/get` |
| Полный текст | Все четыре `messages` получены; структура — один `user` text message | `description` в get = `null`, хотя list description заполнен | Текст годится для анализа/preview, но не считается политикой skill |
| Чтение/запись данных | Этот probe не читал задачи/проекты/теги/checklists | Наличие перечисленных в тексте tools не доказывает их schema/доступ | Передать реальные операции отдельному least-privilege tool probe; prompts-only режим остаётся безопасным |
| Batch | В prompt нет MCP batch API; лишь циклы «для каждого task» в тексте | Ни batching, ни idempotency, ни transaction semantics не проверялись | Не обещать batch; в v1 делать поштучный preview и подтверждение |
| Sandbox/demo/test account | Не найден и не создавался | Проверена существующая Hermes OAuth-сессия, без новых внешних изменений | Для автономных тестов нужен отдельный согласованный аккаунт или mock MCP |
| Ошибки | Подтверждена ошибка отсутствующего `arguments`; исправлена `{}` | Известный HTTP 400 `get_my_context` в этом probe не воспроизводился и поэтому не утверждается | Не включать эту ошибку в диагностику prompts; повторять только с согласованными scopes |
| Нужен собственный MCP | Prompts дают четыре полезных read-oriented сценария | Нет доказанного покрытия Jedi capture/entity/next-step/consent и нет sandbox | Собственный MCP не нужен только ради prompt discovery; собственный safety/method wrapper нужен для соответствия Jedi |

## Итоговое решение

Серверные prompts стоит оставить **опциональным источником шаблонов**, доступным после явного выбора пользователя и с маркировкой «server-provided». Для v1 skill их нельзя принимать как готовый decision policy: `plan_my_day` требует заменить часы/6h/квоты календарно-ресурсным выбором; `triage_inbox` — расширить классификацию и убрать автоматическую дату; `weekly_review` — добавить все входящие источники, календарь, проекты и выполнимый объём; `summarize_project` — добавить цель/следующий физический шаг и подтверждение архива. Получение prompts само по себе не требует собственного MCP, но для безопасного поведения нужен слой skill, который фильтрует и переписывает эти допущения до любого `tools/call`.
