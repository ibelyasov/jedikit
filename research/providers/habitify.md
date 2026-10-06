# Habitify: досье официального hosted MCP

Дата проверки публичной документации: **2026-10-05**. Это исследование для пересборки JediKit с нуля, а не готовый runtime-контракт или подтверждение работоспособности. Документ не разрешает обращения к аккаунту или изменения данных.

## Решение проекта и границы доказательств

Согласовано владельцем для этой пересборки: acceptance host — **Hermes на Nix-сервере владельца**; поддержка **Claude Code и Codex** должна быть заявлена и проверена; provider access — только официальный hosted MCP; без custom code и Python; один исходный skill tree без generated copies. Это решения проекта, не обещания Habitify. Здесь реализовано только досье.

Уровни доказательств:

- **Первичная документация vendor:** публичные официальные страницы, прочитанные 2026-10-05. Они доказывают содержание опубликованных обещаний, но не выполнение операций. [Overview][overview], [Others][others], [Claude][claude], [ChatGPT][chatgpt].
- **Независимое от текста vendor наблюдение lead:** переданные исполнителю metadata и tool schemas из авторизованного Claude Code от 2026-10-05; endpoint `https://mcp.habitify.me/mcp`, ровно 12 tools. Только discovery: чтений данных и вызовов tools не было. Raw export исполнителю не предоставлен; исполнитель не делал probe и не может независимо воспроизвести snapshot. [Наблюдение lead][live].
- **Anecdotes:** не используются; независимых пользовательских свидетельств в исследовании нет.
- **Выводы и design options:** явно обозначены ниже; не подменяют provider contract.
- **Unknown:** то, что не установлено этими источниками. Отсутствие tool в одном snapshot означает отсутствие доступной capability в этом наблюдении, а не отсутствие функции во всём сервисе. [Наблюдение lead][live].

## Подключение и клиенты

Vendor указывает endpoint `https://mcp.habitify.me/mcp`, HTTP Streamable и OAuth 2.0 с dynamic client registration; API key для MCP не требуется. Это документированная конфигурация, не проверка подключения на Hermes или Codex. [Others][others]

Habitify публикует для Claude Code команду `claude mcp add habitify --transport http https://mcp.habitify.me/mcp`; guide также посвящён Claude Desktop и описывает авторизацию при первом подключении. Команда здесь приведена как текст источника, не выполнялась. [Claude][claude]

ChatGPT guide перечисляет Plus, Team и Enterprise и предлагает добавить тот же URL через настройки integration. Это заявление Habitify о ChatGPT, не подтверждение текущего UI OpenAI и не инструкция для Codex. [ChatGPT][chatgpt]

Guide Others заявляет совместимость с MCP-клиентами в целом. Именованных инструкций или результатов acceptance для Hermes и Codex в четырёх проверенных MCP-страницах нет. Совместимость конкретного host, OAuth lifecycle и доступный набор tools остаются непроверенными; обещание generic compatibility не заменяет acceptance. [Overview][overview] [Others][others] [Claude][claude] [ChatGPT][chatgpt]

## Документы против live discovery

Overview обещает чтение habits/status, измерения, status writes, streaks/progress, создание/изменение/archive и управление notes/areas. [Overview][overview]

Others дополнительно перечисляет delete habits, undo logs, add/update/delete notes, CRUD areas, statistics и journal, но не публикует точные tool names, JSON Schema или соответствие categories → tools. [Others][others]

Claude и ChatGPT guides дают примеры создания habit и просмотра statistics. Поэтому гипотеза «широкие функции доступны только ChatGPT, а Claude Code намеренно ограничен» не подтверждается текстом guides. [Claude][claude] [ChatGPT][chatgpt]

| Capability | Публичное обещание | Переданный snapshot и вывод |
| --- | --- | --- |
| Habits | List/create/update/archive/delete. [Others][others] | Есть только `list-habits-by-date`; create/update/archive/delete tools не перечислены. Нельзя обещать изменение структуры habits. [live] |
| Logging | Status writes, measured values, undo. [Others][others] | Есть individual, bulk, all status tools, add/remove log. Отдельного undo tool нет; `remove-habit-log` нельзя считать универсальным undo без проверки. [live] |
| Notes, areas | Notes: add/update/delete; areas: list/create/update/delete. [Others][others] | Tools не перечислены; нет notes/description write capability. [live] |
| Statistics, journal | Statistics/streaks и daily overview. [Others][others] | Именованных tools нет. Неизвестно, содержит ли результат `list-habits-by-date` часть этих данных. [live] |
| Reminders, Off Mode | В проверенных MCP-категориях не заявлены. [Overview][overview] [Others][others] | Tools не перечислены. Нельзя обещать управление reminders или паузой через MCP. [live] |
| Bulk и all writes | Точные bulk contracts в guides не опубликованы. [Others][others] | В snapshot есть шесть bulk/all tools; их schemas подтверждены discovery, execution semantics — нет. [live] |

Все `[live]` в таблицах относятся к [наблюдению lead от 2026-10-05][live].

**Причина расхождения неизвестна.** Проверенные guides не дают client-, Habitify plan- или scope-to-tool mapping и не объясняют урезанный набор. Упоминание платного Claude Custom Connectors относится к клиентской функции, а не доказательству Habitify plan gating. Snapshot не содержит переданных сведений о тарифе или scopes, поэтому нельзя выбирать одну из этих причин. [Claude][claude] [Others][others] [live]

## Инвентарь 12 tools

Имена и параметры в таблице — переданные schemas, не выведенные из REST. Колонки «смысл» различают документированную category и предположение по имени; guides не описывают каждый tool отдельно. Requiredness, output schemas и descriptions не переданы полностью, поэтому ниже не утверждается, что отсутствие `date` допустимо для всех tools. [live] [Others][others]

| Tool | Переданные inputs | Смысл и границы |
| --- | --- | --- |
| `add-habit-log` | `habitId`, `value >= 0`, `unit` enum ниже, default `rep`; `date` — `YYYY-MM-DD`, default today. [live] | Vendor заявляет measured logging. Неизвестно, значение добавляется к сумме или заменяет её, как связаны goal/unit, допустимы ли дубли. REST R3 ниже — только сравнение, с другими names inputs. [Others][others] [live] [OpenAPI][openapi] |
| `remove-habit-log` | `habitId`, `date`. [live] | По имени — удаление log для habit/date. Не установлено, удаляется один entry или все за день, сохраняется ли status и можно ли восстановить. REST R4 принимает `logId`, R6 — `targetDate`: ни один не доказанный mapping этого tool. Не объявлять undo. [live] [OpenAPI][openapi] |
| `complete-habit` | `habitId`, `date`. [live] | Соответствует документированной category completed; переходы состояния и связь с measurement не проверены. Goal-derived value у REST R5 не переносится в MCP. [Overview][overview] [live] [OpenAPI][openapi] |
| `fail-habit` | `habitId`, `date`. [live] | Соответствует category failed; влияние на прогресс/streak неизвестно. Failure log и errors REST R5 — не MCP contract. [Overview][overview] [live] [OpenAPI][openapi] |
| `skip-habit` | `habitId`, `date`. [live] | Соответствует category skipped; не доказывает Off Mode или отключение reminders. REST R5 не подтверждает MCP retry/idempotency. [Overview][overview] [live] [OpenAPI][openapi] |
| `complete-habits` | `bulks: [{habitId, date}]`. [live] | По имени — completed для перечисленных habits/dates. Предел batch, порядок, atomicity и результат каждого элемента неизвестны. [live] |
| `fail-habits` | `bulks: [{habitId, date}]`. [live] | По имени — failed для перечисленных элементов; partial failure/rollback неизвестны. [live] |
| `skip-habits` | `bulks: [{habitId, date}]`. [live] | По имени — skipped для перечисленных элементов; обработка повторов и смешанных дат неизвестна. [live] |
| `complete-all-habits` | `status: completed\|failed\|skipped`, `date`. [live] | Несмотря на имя schema допускает три status. Неизвестно, что означает all: scheduled, active, archived или иной набор. [live] |
| `fail-all-habits` | `date`. [live] | По имени — failed для all; состав затрагиваемого набора неизвестен. [live] |
| `skip-all-habits` | `date`. [live] | По имени — skipped для all; состав набора и влияние на reminders неизвестны. [live] |
| `list-habits-by-date` | `date`. [live] | Единственный перечисленный read tool. Имя предполагает список по дате; output, статус, ID, goals, archived/scheduled filtering, completeness и pagination не установлены. REST R1/R2 не доказывают output или pagination этого tool. [live] [OpenAPI][openapi] |

Точный переданный `unit` enum у `add-habit-log`:

`m`, `kM`, `ft`, `yd`, `mi`, `floor`, `L`, `mL`, `fl oz`, `cup`, `sec`, `min`, `hr`, `ms`, `kg`, `g`, `mg`, `oz`, `lb`, `mcg`, `J`, `kJ`, `kCal`, `cal`, `rep`, `step`. Регистр и пробелы значимы как часть schema strings; не нормализовать `kM` в `km`. Наличие enum не подтверждает конверсию units или допустимость любого unit для конкретной habit. [live]

## REST и Off Mode: только сравнение

Others направляет к API reference за поведением endpoints, но не задаёт mapping REST → MCP. Поэтому даже документированная REST operation не расширяет 12 tools и не подтверждает MCP semantics, undo или response format. [Others][others]

Текущий публичный **OpenAPI v2** получен lead через `curl` 2026-10-05, затем исполнитель прочитал тот же официальный документ вне sandbox. Это чтение документации без авторизации и данных аккаунта. Ниже — текущие REST claims, а не результаты REST calls. Исторический `research/habitify-provider-research.md` использован только как указатель на источники; старые product decisions не перенесены. [OpenAPI][openapi]

REST server — `https://api.habitify.me/v2`. Введение OpenAPI требует paid subscription для REST access и описывает `X-API-Key`; лимит 500/min/account с REST HTTP `429`. Это не доказательство Habitify plan gating tools или MCP error envelope. [OpenAPI][openapi]

| REST context | Документированное поведение, только REST |
| --- | --- |
| **R1: `GET /habits`** | Paginated list: query `archived`, `areaId`, `type`, `timeOfDay`, `limit` 1–100 (default 50), `offset` ≥0 (default 0). Description обещает scheduled-date filter, но соответствующего date parameter в этом schema block нет; не изобретать параметр. [OpenAPI][openapi] |
| **R2: `GET /habits/journal`** | Daily overview всех habits с completion/progress/current streak/log info. Optional query `date`: `YYYY-MM-DD`, default today based on your timezone. Это REST timezone claim, не установленная MCP timezone. [OpenAPI][openapi] |
| **R3: `POST /habits/{habitId}/logs`** | Новый measurable log: required `value`, `unitSymbol`, optional `targetDate` (`YYYY-MM-DD`, default today); responses `201`, `400`, `401`, `404`, `422`. MCP inputs называются `unit`/`date`; mapping отсутствует. [OpenAPI][openapi] [live] |
| **R4: `DELETE /habits/{habitId}/logs/{logId}`** | Permanent removal конкретного log по ID. MCP `remove-habit-log` получает дату, а не `logId`; equivalence не доказана. [OpenAPI][openapi] [live] |
| **R5: `POST /habits/{habitId}/logs/complete`, `POST /habits/{habitId}/logs/failed`, `POST /habits/{habitId}/logs/skipped`** | Complete вычисляет log value из goal/target; failed пишет failure log; skipped — intentional skip. У всех optional `targetDate` (`YYYY-MM-DD`, default today), responses `201`, `400`, `401`, `404`, `409` (log уже существует на дату). Это REST conflict behavior; MCP idempotency и status transitions остаются unknown. [OpenAPI][openapi] |
| **R6: `POST /habits/{habitId}/logs/undo`** | Удаляет **все** logs habit/date и сбрасывает status в in-progress. Optional `targetDate` (`YYYY-MM-DD`, default today); responses `200`, `400`, `401`, `404`. Date-shaped MCP input не доказывает, что `remove-habit-log` выполняет это REST undo. [OpenAPI][openapi] [live] |

В текущем inventory REST paths bulk/all log endpoints не найдены; это не описание batch execution у MCP. Для шести MCP bulk/all tools неизвестны atomicity, per-item errors и область all. В REST `targetDate`/journal `date` — calendar dates; `createdAt` — отдельное `date-time` поле. Не подменять MCP `date` полным timestamp или REST field name. [OpenAPI][openapi] [live]

Help Center описывает Off Mode как Time Off со start/end dates, отключением reminders и защитой streaks. Для одного дня vendor рекомендует ручной skip с тем же эффектом на progress; это не обещание равенства notifications, account-wide состояния или MCP-операций. В наблюдении Off Mode tool нет. Вывод проекта: не выдавать `skip-all-habits` за Off Mode. [Off Mode][offmode] [live]

## Что можно обещать coaching через MCP alone

**Вывод из доступного discovery, не доказательство исполнения:** возможен ограниченный цикл «получить habits для выбранной даты → обсудить с владельцем → по его запросу записать status или измерение». Какие факты можно показать, зависит от ещё неизвестного output read tool; нельзя обещать вычисленный streak, history, weekly statistics или полноту списка. [live]

**Вне наблюдаемого MCP:** создание нового habit, изменение цели/расписания/описания, archive/delete habit, запись coaching plan в notes, управление areas/reminders, native Off Mode. Coach может сформулировать предложение и попросить владельца применить его в приложении, но не сообщать о выполненном изменении. [live]

Coaching analysis может опираться на слова владельца и доступные результаты reads, явно различая их происхождение. Надёжность выводов о streaks и trends нельзя повысить простым перебором дат, пока неизвестны retention, completeness и output semantics. Это design constraint из отсутствия проверенного read contract. [live]

### Где может жить habit plan

Следующие варианты — **design options**, не функции Habitify и не реализованные механизмы:

| Вариант | Практический смысл | Ограничение |
| --- | --- | --- |
| Текст текущего разговора | Сформулировать cue, minimum action, frequency и review date без provider write | Нет гарантии сохранения между сессиями |
| Существующая owner-controlled memory/notes host | Хранить согласованный план и связь с habit ID, если host уже предлагает такую возможность | Нужно отдельно проверить persistence, доступ из Hermes/Claude Code/Codex и правила владения; не изобретать API |
| Пользователь вручную пишет план в Habitify UI | План остаётся рядом с habit, если приложение предоставляет подходящее поле | MCP не подтверждает ни чтение этого поля, ни возможность записать его |
| Один текстовый артефакт владельца | Общий переносимый план для нескольких hosts | Нужен отдельный выбор места и writer authority; досье не создаёт файл и не вводит вторую skill source tree |

Не выбирать persistence молча и не обещать синхронизацию. Отсутствие notes/description write tool в snapshot означает, что хранение плана в Habitify через этот MCP не подтверждено. [live]

## Открытые вопросы и безопасный способ проверки

Ни один пункт ниже не разрешает probe автоматически. Перед acceptance нужны отдельное owner approval на read-only доступ и отдельно disposable-data write tests; реальный пользовательский history не использовать как тестовый материал.

| Unknown | Что требуется установить | Тип проверки после разрешения |
| --- | --- | --- |
| Discovery на Hermes и Codex | Tool count/names/schemas, полнота discovery, сопоставимость с Claude Code, версии и дата snapshot | Авторизованный read-only discovery без data reads; сохранять только очищенный inventory |
| Read contract | Output IDs/status/goals, scheduled/archived filtering, completeness, pagination, пустой день | Owner-approved `list-habits-by-date`; вывод без персональных данных в evidence |
| Даты и timezone | Для каких tools format/default, timezone today, ограничения past/future, смена суток | Read-only schema/date comparison; write date boundaries — только disposable-data test |
| Measurement | Additive/replace semantics, conversion, goal compatibility, duplicate handling | Disposable habit, read-before/write/read-after; не предполагать retry safe |
| Undo/removal | Какой log удаляется, scope дневного удаления, отмена completed/failed/skipped, восстановление | Disposable-data test; tool name не доказательство обратимости |
| Status/idempotency | Повтор того же status, переходы status, взаимодействие с measured entries | Disposable-data test; повтор после timeout не выполнять автоматически |
| Batch/all | Размер batch, duplicates, mixed dates, atomicity, per-item failures, definition all | Изолированный disposable dataset; account-wide tools не тестировать на обычном аккаунте |
| Errors/rate limit | Error envelope, auth expiry, validation, timeout, retry-after, quota accounting | Публичная документация/естественный разрешённый error; не вызывать лимит намеренно |
| Причина docs/live gap | Client/plan/scopes/server version, rollout или устаревшая документация | Документированное пояснение vendor и согласованное сравнение metadata; не менять тариф/scopes/auth ради исследования |

Vendor публикует общий с REST лимит **500 requests/minute/account**; выполнение и конкретный error response не проверены. [Others][others]

MCP specification различает pagination у discovery `tools/list` и ошибки протокола/`isError` у tool results. Это требования/возможности протокола, не наблюдённая реализация Habitify. Cursor discovery ничего не доказывает о pagination результата `list-habits-by-date`; отсутствие details output нельзя компенсировать предположением по MCP spec. [MCP tools specification][mcp-spec] [live]

## Acceptance и текущий итог

Этот dossier подтверждает опубликованные обещания и фиксирует переданный ограниченный inventory. Runtime acceptance, reads, writes, восстановление после ошибок, host interoperability и OAuth lifecycle **не проверены**. Исторические результаты JediKit не являются acceptance пересборки.

Перед обещанием возможностей пользователю lead должен получить свежий очищенный discovery на acceptance host, разрешённый read contract и disposable-data evidence для каждого используемого write класса. Unsupported capability остаётся явным ограничением; REST fallback, custom server и helper code не входят в согласованную архитектуру.

## Источники

Ссылки `[live]` — сокращённое обозначение наблюдения lead; URL обозначает endpoint, а не доступный публичный snapshot. Все даты ниже — дата доступа/наблюдения **2026-10-05**.

[overview]: https://api-docs.habitify.me/mcp/ "Habitify MCP Overview; доступ 2026-10-05"
[others]: https://api-docs.habitify.me/mcp/others/ "Habitify Other MCP Clients; доступ 2026-10-05"
[claude]: https://api-docs.habitify.me/mcp/claude/ "Habitify Claude guide; доступ 2026-10-05"
[chatgpt]: https://api-docs.habitify.me/mcp/chatgpt/ "Habitify ChatGPT guide; доступ 2026-10-05"
[live]: https://mcp.habitify.me/mcp "Наблюдение lead: авторизованный Claude Code metadata/tool schemas 2026-10-05; без tools calls; raw export не предоставлен исполнителю"
[rest]: https://api-docs.habitify.me/api/ "Habitify API reference; попытка доступа 2026-10-05, web tool не отдал содержимое"
[openapi]: https://api-docs.habitify.me/openapi/v2/openapi-bundled.yaml "Habitify OpenAPI v2; доступ lead и исполнителя к публичному документу 2026-10-05"
[offmode]: https://intercom.help/habitify-app/en/articles/6178415-how-to-schedule-time-off-for-off-mode "Habitify Off Mode; доступ 2026-10-05"
[mcp-spec]: https://modelcontextprotocol.io/specification/2025-11-25/server/tools "MCP tools specification; доступ 2026-10-05"
