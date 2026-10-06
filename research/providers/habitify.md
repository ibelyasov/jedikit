# Habitify: инструменты хоста и официальный REST API v2

Исходное исследование: **2026-10-05**. Перепроверка **2026-10-06**: официальный OpenAPI v2 (`info.version: 2.0.0`), MCP Others, Off Mode Help Center и официальное пояснение REST `403`. Читались только публичные документы, без ключа, OAuth и данных аккаунта. OpenAPI просмотрен по введению/auth, schemas Habit/Log/Note/Area и paths; ответ провайдера с данными не проверен. При прежнем чтении API reference через web не отдал содержание, OpenAPI получен публичным HTTP-клиентом; `/llms.txt` вернул HTML оболочку, а не пригодный индекс документации. Для перехода на инструменты хоста повторно прочитаны [MCP Others](https://api-docs.habitify.me/mcp/others/), [Off Mode](https://intercom.help/habitify-app/en/articles/6178415-how-to-schedule-time-off-for-off-mode) и [пояснение 403](https://intercom.help/habitify-app/en/articles/14075422-troubleshooting-403-forbidden-error-with-the-habitify-api), доступ 2026-10-06; это документация, не runtime-приёмка.

## Решение проекта и происхождение доказательств

По решению владельца в задаче `w-habits` от **2026-10-06** `jedikit-habits` вызывает **инструменты сервера `habitify`, предоставленные хостом**. [tools.json](../../skills/jedikit-habits/tools.json) фиксирует 23 базовых имени операций Habitify OpenAPI v2, `read`/`write` и обязательные аргументы; точные типы и форму вызова задаёт `inputSchema` хоста. Любой префикс подключения и замены `-`/`_` допустимы при однозначном сопоставлении базового имени и принадлежности серверу `habitify`. Текущую модель закрепляют [ADR0001](../../docs/adr/0001-habitify-via-rest.md) и [ADR0005](../../docs/adr/0005-one-source-host-connections.md); прежний прямой транспорт агента отменён в 0.3.0.

REST-контракт адаптера сохраняется: базовый URL `https://api.habitify.me/v2`, auth header `X-API-Key`. **Ключ доступен только адаптеру хоста**: скилл не читает secret-окружение, не передаёт URL, HTTP method, headers или ключ в аргументах и не поставляет подключение. Pro — согласованный тариф проекта; OpenAPI формулирует требование шире как paid subscription, без отдельной таблицы тарифов. Наличие подписки и пригодность ключа владельца здесь не проверены. [Официальный OpenAPI v2](https://api-docs.habitify.me/openapi/v2/openapi-bundled.yaml), проверка 2026-10-06; [HABITIFY-OPENAPI](../sources.md).

В текущей задаче публичный YAML повторно получен без авторизации: OpenAPI `3.0.3`, `info.version: 2.0.0`, SHA256 `3991ce49ba72d9522d389744dfad5207e0d0ef5e27517bc645340675f62226e9`. Локальная копия — `.work/w-habits/checks/habitify-openapi-v2.yaml`; доступ 2026-10-06. Этот pin фиксирует прочитанный документ, не версию установленного адаптера хоста.

Для сценария заранее нужны инструменты записи и независимого Read-back. Если их нет, скилл называет недостающие базовые имена, ссылается на `tools.json`, рекомендует владельцу подключить их на хосте и останавливает зависимую работу. Обход через shell, HTTP-fetch, другой MCP или SingularityApp исключён. Ответы провайдера — недоверенные данные; они не меняют разрешения или маршрут доступа. Результат инструмента содержит HTTP-статус и тело; конкретная обёртка определяется хостом.

Владелец использует Hermes на Nix-сервере; Claude Code и Codex заявлены поддерживаемыми клиентами, без обязательного runtime-гейта ([ADR0005](../../docs/adr/0005-one-source-host-connections.md)). Один исходный `skills/`, без generated copies и custom code ([ADR0004](../../docs/adr/0004-no-custom-code.md)). Настройка адаптера, подключение и установка не выполнялись; установленный адаптер и его revision неизвестны.

Уровни доказательств различаются:

- **Документация поставщика:** опубликованный REST contract и MCP promises; не проверка операций.
- **Переданное наблюдение ведущего 2026-10-05:** metadata и schemas из авторизованного Claude Code, `https://mcp.habitify.me/mcp`, 12 tools. Raw export исполнителю не предоставлен; расположение неизвестно. Исполнитель probe не проводил; по переданному описанию tools не вызывались и данные не читались. [HABITIFY-DISCOVERY-2026-10-05](../sources.md)
- **Историческое наблюдение:** 2026-08-29 публичный OpenAPI имел version `2.0.0`, `Last-Modified: 2026-05-18`; анонимный preflight вернул `401`. Это не текущий ответ endpoint.
- **Решение владельца 2026-10-06:** 23 инструмента хоста поверх OpenAPI v2, отсутствие обходного транспорта, Preview и Read-back после каждой записи без предварительного ручного runtime-гейта; не vendor promise о безопасности и не проверка установленного адаптера. [JEDIKIT-W-HABITS-2026-10-06](../sources.md)

Независимых испытаний надёжности, coaching efficacy или пользовательских anecdotes в досье нет.

## REST: точные операции и семантические ловушки

Все paths ниже относительны к `/v2`. API key создаётся в приложении `Settings > API`; одновременно активен один ключ, новый отзывает старый. Здесь ключи не создавались. OpenAPI также перечисляет bearer `AccessTokenAuth`/`IdTokenAuth`, но не задаёт OAuth flow; JediKit их не использует и не выдумывает token exchange. Документированный предел — 500 requests/minute/account и HTTP `429`; это опубликованный лимит, не результат нагрузки. [HABITIFY-OPENAPI](../sources.md)

Не смешивать legacy URL/инструкции/ключи с REST v2. Официальная статья от 2026-03-20, прочитанная в прежнем исследовании 2026-09-13 и повторно 2026-10-06, объясняет частую причину `403`: **новый V2 key отправлен на legacy endpoints**, где он не распознаётся. Статья направляет к актуальной API v2 документации; OpenAPI задаёт базовый `/v2` URL. Это документированная диагностика, а не ответ аккаунта владельца; из `403` нельзя автоматически заключать, что ключ истёк, или генерировать новый ключ, отзывающий существующий. Совместимость любого старого ключа с v2 здесь не доказана. [HABITIFY-API-403](../sources.md), [HABITIFY-OPENAPI](../sources.md)

| Сценарий | Публичный REST contract | Граница для JediKit |
| --- | --- | --- |
| Habit CRUD | `GET/POST /habits`; `GET/PUT/DELETE /habits/{habitId}` | Модель различает `good`/`bad`; create/update покрывают name, description, startDate, occurrence, goal, reminders/stacks/endCondition и связи. DELETE permanent, уничтожает связанные logs/notes/goals/reminders; не обычный способ завершить эксперимент. |
| Список привычек | Query `archived`, `areaId`, `type`, `timeOfDay`, `limit` 1–100 (default 50), `offset` ≥0 (default 0) | Description обещает scheduled-date filter, но date parameter в schema нет. Не изобретать его и не считать одну страницу полным списком. |
| Journal | `GET /habits/journal`, optional `date` `YYYY-MM-DD` | Default today по timezone аккаунта. Отдельного user-timezone read/set в просмотренном OpenAPI нет; согласованный день лучше указывать явно. Journal включает status/progress/current streak/log info. |
| Statistics | `GET /habits/{habitId}/statistics` | Агрегаты logs/skips/fails/completions/average и daily progress; не raw log range query и не доказательство эффекта эксперимента. |
| Measurable log | `POST /habits/{habitId}/logs`, required `value`, `unitSymbol`; optional `targetDate` `YYYY-MM-DD` | Создаёт entry; `createdAt` — отдельное date-time. Unit и goal должны соответствовать выбранному habit, не переносить MCP `unit`/`date` в REST. |
| Complete/fail/skip | `POST /habits/{habitId}/logs/complete`, `/failed`, `/skipped`; optional `targetDate` | Complete вычисляет value из goal, failed пишет failure, skipped — intentional skip. Ответ `409` описан как уже существующий log на дату; не считать повтор идемпотентным. |
| Undo | `POST /habits/{habitId}/logs/undo`, optional `targetDate` | Удаляет **все** logs habit/date и возвращает status в in-progress; preview должен назвать именно эту область потери записей. Не универсальное undo всех provider changes. |
| Delete log | `DELETE /habits/{habitId}/logs/{logId}` | Permanent removal конкретного entry по ID, не эквивалент дневного undo. |
| План в Note | `GET/POST /habits/{habitId}/notes`; `PUT/DELETE /habits/{habitId}/notes/{noteId}` | Create требует минимум одно из content/moodLevel/photos; update меняет переданные поля. DELETE permanent. План связывается с habit ID и note ID; успешный write требует отдельного read-back. |
| Archive | `POST /habits/{habitId}/archive` | Скрывает habit из active list и сохраняет данные; `409` — уже archived. Документированного unarchive path или `archived` input у PUT не найдено. Archive не обозначать как обратимую pause. |
| Areas | list/create/get/update/delete `/areas` и `/areas/{areaId}` | Delete снимает привязку habits, а не удаляет их. Не входит в автоматическую гигиену экспериментов. |

Источник таблицы: [HABITIFY-OPENAPI](../sources.md), публичная проверка 2026-10-06. GET habit возвращает description, но это другое поле, чем отдельные Note: план в заметке не считать записанным после обновления description.

Историческая запись досье 2026-09-13 отдельно сообщала, что Help Center описывает **ручной Unarchive в приложении**. Точный URL и текст первичной страницы в этой записи не сохранены, UI-действие не проверено повторно. Это квалифицированное историческое сведение о ручном восстановлении, не доказательство текущего REST/MCP unarchive или автоматической pause/resume. Отсутствие unarchive path в просмотренном OpenAPI не отменяет того исторического UI-сведения. [HABITIFY-UI-UNARCHIVE-HISTORICAL](../sources.md)

### Schema traps, сохранённые из проверки 2026-08-29 и сверенные 2026-10-06

- Habit occurrence weekdays: `0 = Sunday … 6 = Saturday`; reminder occurrenceFilter weekdays: `1 = Sunday … 7 = Saturday`. Не переносить числовой enum из одного поля в другое.
- Log status string — `inprogress`, а не `in-progress`; календарные `date`/`targetDate` — `YYYY-MM-DD`, не timestamp с offset.
- Notes называются paginated, но `limit`/`offset` в GET notes не описаны. Полнота списка не гарантирована схемой; отсутствие заметки в неполном чтении не доказывает отсутствие плана или успех удаления. Запись подтверждается Read-back точного ID и текста.
- Area response включает required `description`, отсутствующее в properties. Streak/successPeriods endCondition response содержит `periodType`, input этого поля не описывает. Это рассинхронизация схемы, не разрешение изобретать input.
- Goals/reminders/stacks/endCondition — nested Habit fields; отдельного CRUD и безопасного очищения nested field не описано. Описание Habit PUT в повторно прочитанном YAML заявляет, что пропущенные поля остаются неизменными; это vendor statement, не локально проверенное поведение. По решению владельца сохраняется guard полной writable-конфигурации и полного Read-back. Не считать omission, null и пустой объект взаимозаменяемыми.
- В просмотренном OpenAPI не найдены webhook/events, bulk/all logs, export/import, pause, Off Mode или unarchive. Отсутствие в этом документе не доказывает отсутствие функции во всём сервисе.

Источник: [HABITIFY-OPENAPI](../sources.md). Исторические даты наблюдения и HTTP headers не обновляются сегодняшней датой.

## Исторический официальный hosted MCP: обещания против переданного inventory

Официальный MCP endpoint — `https://mcp.habitify.me/mcp`; Others описывает Streamable HTTP, OAuth 2.0 с dynamic client registration и общий с REST лимит. MCP guides обещают create/update/archive/delete habits, notes/areas, statistics/journal и undo. Они не дают точных per-tool schemas или объяснения ограниченного набора Claude Code. Snapshot 2026-10-05 содержит лишь список habits по дате и logs/status; создать habit, изменить его, записать план в Note или архивировать через тот наблюдавшийся набор нельзя. Причина расхождения (plan/scopes/client/rollout/version) не установлена. Этот hosted MCP snapshot не описывает нынешний контракт адаптера хоста с 23 операциями и не служит fallback. [MCP Others](https://api-docs.habitify.me/mcp/others/), доступ 2026-10-06; [HABITIFY-MCP-OTHERS](../sources.md), [HABITIFY-DISCOVERY-2026-10-05](../sources.md).

Claude/ChatGPT guides также приводили create/statistics, поэтому гипотеза «CRUD только у ChatGPT» не подтверждалась. Именованных инструкций/acceptance Hermes и Codex в просмотренных четырёх MCP guides 2026-10-05 не было. Generic MCP compatibility не доказывает конкретный host. [HABITIFY-MCP-OVERVIEW](../sources.md), [HABITIFY-MCP-CLAUDE](../sources.md), [HABITIFY-MCP-CHATGPT](../sources.md)

Исторический public discovery 2026-09-13: protected resource `https://mcp.habitify.me`, auth server `https://account.habitify.me`, resource scopes `profile`, `openid`; authorization metadata также `email`, `offline_access`, `all`. Tool mapping из них не следует. Help Center от 2026-03-10 называл URL SSE, MCP docs — Streamable HTTP: датированный drift, не текущий probe. [HABITIFY-OAUTH-RESOURCE](../sources.md), [HABITIFY-OAUTH-SERVER](../sources.md), [HABITIFY-MCP-HELP](../sources.md)

### Переданный inventory 2026-10-05: 12 tools, без исполнения

Это сохранённое свидетельство, не REST contract и не нынешний независимый discovery. Requiredness, outputs, annotations и параметры сессии не переданы полностью. `add-habit-log` имеет `value >= 0`, default unit `rep`, default date today; это не разрешает перенос defaults на остальные tools.

| Tool | Переданные inputs | Что не доказано |
| --- | --- | --- |
| `add-habit-log` | `habitId`, `value`, `unit`, `date` | Additive/replace, duplicates, совместимость goal/unit |
| `remove-habit-log` | `habitId`, `date` | Один или все entries, status effect, undo; REST delete требует logId |
| `complete-habit`, `fail-habit`, `skip-habit` | `habitId`, `date` | Idempotency, status transitions, goal-derived values, streak/reminders |
| `complete-habits`, `fail-habits`, `skip-habits` | `bulks: [{habitId, date}]` | Предел, порядок, mixed dates, atomicity/rollback, per-item errors |
| `complete-all-habits` | `status: completed\|failed\|skipped`, `date` | Несмотря на имя доступны три status; что означает all, неизвестно |
| `fail-all-habits`, `skip-all-habits` | `date` | Состав all: active/scheduled/archived, effects |
| `list-habits-by-date` | `date` | Output IDs/goals/history, filtering, completeness/pagination |

Переданный unit enum: `m`, `kM`, `ft`, `yd`, `mi`, `floor`, `L`, `mL`, `fl oz`, `cup`, `sec`, `min`, `hr`, `ms`, `kg`, `g`, `mg`, `oz`, `lb`, `mcg`, `J`, `kJ`, `kCal`, `cal`, `rep`, `step`. Регистр и пробелы — часть schema strings, не нормализовать `kM` в `km`. [HABITIFY-DISCOVERY-2026-10-05](../sources.md)

## Pause, Off Mode и хранение плана

Help Center описывает account-wide Time Off со start/end dates, отключением reminders и защитой streaks. Для одного дня рекомендует manual skip с тем же эффектом на progress; это не равенство notifications и состояния всего аккаунта. Нативной Off Mode операции в просмотренном REST OpenAPI и переданном MCP наборе нет. У JediKit нет команды `off`, и он не эмулирует её skip/archive/delete. [HABITIFY-OFF-MODE](../sources.md), [HABITIFY-OPENAPI](../sources.md)

Для **pause** нет native API-операции: остаются разговорный план с условием возврата и инструкция для приложения. Archive, skip и изменение occurrence не подменяют паузу. [Off Mode](https://intercom.help/habitify-app/en/articles/6178415-how-to-schedule-time-off-for-off-mode), доступ 2026-10-06, описывает ручной путь `Settings → Data → Off Mode → Plan new Time Off`; account-wide эффект следует объяснить пользователю. Archive сохраняет историю, но не имеет публичного unarchive contract.

План эксперимента по CONTEXT.md — человекочитаемый текст в Note Habitify: цель, поведение, триггер, минимум/замена, if–then, дата обзора, stop-rule. `create-habit-note` и `update-habit-note` выполняют согласованную запись; `list-habit-notes` подтверждает точный `id` и полный `content` у выбранного `habitId`. При неизвестном исходе создания сначала читается список: дублирующая запись не разрешена. Если точный ID и полный текст не подтверждены либо текст расходится, результат `unverified`, без повторной записи. Найденные точный ID и полный `content` подтверждают запись даже в неполном списке; отсутствие в таком списке не доказывает, что заметки нет. Native memory хранит только настройки и выбранные IDs, а не альтернативную копию состояния эксперимента ([ADR0006](../../docs/adr/0006-memory-holds-settings-only.md)).

`update-habit` сохраняет guard Habit PUT: по `get-habit` восстанавливается **вся текущая writable-конфигурация**, меняется только согласованное; невосстановимое поле останавливает запись с инструкцией ручного изменения. Read-back сравнивает всю конфигурацию, в том числе неизменяемые в этом сценарии поля. `reminders` разрешены по явной просьбе с Preview и проверкой через `get-habit`; безопасное очищение не выводится из omission/null/empty, доставка не обещается. Несоответствие или нехватка данных после любой записи означает `unverified`, а не разрешение повторить её. Технические ветки — [habitify-tools.md](../../skills/jedikit-habits/references/habitify-tools.md).

## Открытые вопросы и непроверенные слои

Фактических REST reads/writes, авторизации и provider mutations в этой работе нет. Исторические alpha artifacts не доказывают поведение текущих инструментов хоста. В 0.3.0 обязательного ручного runtime-гейта нет ([ADR0005](../../docs/adr/0005-one-source-host-connections.md)); Read-back проверяет результат каждой реальной разрешённой записи и не требует отдельного тестового прогона.

| Вопрос | Что остаётся непроверенным и как ограничен текущий сценарий |
| --- | --- |
| Доступ и read contract | Paid account/key без раскрытия секрета, выбранные habit IDs, pagination, journal/date/timezone и полнота notes |
| Note binding | Реальная запись плана требует Read-back habit ID/note ID и полного content; после неизвестного результата сначала чтение, без дубля |
| Reminders и pause | Согласованная конфигурация reminders и Read-back через get-habit; доставку оценивать отдельно. Native pause недоступна, ожидается разговорный план/инструкция приложения |
| Log/status/undo | Measurement units, goal-derived values, transitions, 409, day-boundary; дневной undo проверять отдельно от delete log |
| Ошибки | 400/422 без догадки о значении; 401/403 — доступ хоста не подтверждён, подключение проверяет владелец без передачи ключа скиллу; 404/409 — адресное чтение; 429 — стоп; 5xx/timeout/outcome_uncertain после записи — сначала адресное чтение, без слепого повтора |
| Archive | Active/archived visibility и сохранность данных; не обещать автоматическое unarchive |
| Удаления и host approval | Habit/note/area только по явной просьбе с Preview и подтверждением необратимой потери; delete-habit-log только при известном logId. Отказ кнопки хоста — unapplied, без повтора до новой просьбы |

Явную одиночную команду пользователя можно выполнить сразу, кроме `delete-habit`, `delete-habit-note` и `delete-area`: они необратимы и всегда требуют Preview и подтверждения. Для удаления привычки Preview называет потерю истории, отметок, заметок, целей и напоминаний; удаление области снимает связи, сохраняя привычки. Завершение эксперимента сначала предполагает предложение архива. Предложенное агентом изменение выполняется после точного Preview и подтверждения. Группа операций требует единого Preview и подтверждения, выполняется последовательно и останавливается на первой ошибке. После каждой записи нужен независимый Read-back; отчёт различает `applied`, `unverified`, `unapplied`. Фоновые проверки только читают ([ADR0003](../../docs/adr/0003-no-unattended-writes.md)).

По контракту хоста, переданному владельцем для этой задачи, Hermes при `trust = "untrusted"` отдельно запрашивает кнопку для инструмента без `readOnlyHint`. Эта кнопка не заменяет согласие скилла; отказ означает `unapplied` с причиной и запрещает повтор без новой просьбы пользователя. `outcome_uncertain` после оборванной записи означает неизвестный исход: сначала адресное чтение. Это требование интеграции хоста, не факт официального Habitify OpenAPI и не проверенный здесь Hermes runtime. Cleanup тоже mutation, permanent delete не является default. Нельзя нагрузочно вызывать 429 или менять auth/scopes/тариф ради исследования.
