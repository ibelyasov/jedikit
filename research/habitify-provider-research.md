# Habitify provider research: REST/OpenAPI snapshot

Статус: исторический research, **не runtime-контракт JediKit**. Проверено
2026-08-29 без авторизации и без записи пользовательских данных. JediKit runtime
использует только официальный MCP и текущий `tools/list`; описанные ниже REST
paths, поля и enums нельзя переносить в MCP-вызовы или использовать как fallback.

Публичные источники повторно проверены **2026-09-13** без OAuth, токена и данных
аккаунта. Точный MCP `tools/list` и JSON Schema публично по-прежнему не
опубликованы; перечисленные ниже MCP capabilities подтверждены только на уровне
официальных категорий, а точные REST операции остаются snapshot 2026-08-29.

## Вопрос, маршрут чтения и уровни доказательства

**Вопрос:** что официальные публичные источники подтверждают для Habitify REST
v2 и hosted MCP, особенно для delete, undo, archive, batch и Off Mode, и какие
точные MCP contracts остаются недоступны без runtime discovery?

Сначала читайте источники/auth и текущие публичные MCP categories, затем
исторический REST snapshot, его schema traps и итоговую MCP capability table.
Канонический runtime scope JediKit находится в
[`skills/jedikit-habits/references/habitify-mcp.md`](../skills/jedikit-habits/references/habitify-mcp.md)
и [product decisions](product-decisions.md); этот research не подменяет их.

REST paths, fields и enums ниже — **official OpenAPI snapshot 2026-08-29**.
Публичные MCP categories, OAuth metadata и Off Mode Help Center — **current docs
evidence 2026-09-13**. Авторизованного Habitify `tools/list` или observed runtime
schema в этом исследовании нет. Продуктовые запреты на REST fallback и эмуляцию
capabilities приходят из JediKit decisions, а не из provider docs.

## Источники и подключения

Источники: [официальная API-документация](https://api-docs.habitify.me/), её
[OpenAPI v2](https://api-docs.habitify.me/openapi/v2/openapi-bundled.yaml),
[официальная MCP-документация](https://api-docs.habitify.me/mcp/) и Help Center
Habitify. На дату проверки OpenAPI отдавался с `Last-Modified: 2026-05-18` и
`info.version: 2.0.0`.

REST v2 описывался как `https://api.habitify.me/v2` с `X-API-Key`. Ключ
создавался в мобильном приложении (`Settings → API Credentials`), показывался
один раз, а генерация нового отзывала старый. Документация указывала платный
план и 500 запросов/минуту на аккаунт. Старые URL и ключи не следовало смешивать
с v2; см. [официальное пояснение 403](https://intercom.help/habitify-app/en/articles/14075422-troubleshooting-403-forbidden-error-with-the-habitify-api).

Официальный MCP по-прежнему указан как `https://mcp.habitify.me/mcp`, OAuth 2.0
с dynamic client registration и HTTP Streamable. Read-only public discovery
2026-09-13 показал protected resource `https://mcp.habitify.me`, authorization
server `https://account.habitify.me` и resource scopes `profile`, `openid`;
authorization-server metadata дополнительно перечисляет `openid`, `profile`,
`email`, `offline_access`, `all`. Эти scopes не раскрывают scope-to-tool mapping
и не разрешают запрашивать `all` без необходимости. Help Center от 2026-03-10
называл тот же URL SSE в [старой инструкции](https://intercom.help/habitify-app/en/articles/13843791-use-habitify-with-ai-apps-tools),
тогда как MCP-документация указывала HTTP Streamable. Это датированный drift,
а не основание угадывать transport или scopes.

Исторический анонимный preflight 2026-08-29 без token вернул `401`. Это
наблюдение подтверждало требование auth для того запроса в тот момент; оно не
является новым runtime probe, не раскрывает tool schemas и не доказывает текущий
status endpoint.

Текущая официальная [страница для MCP-клиентов](https://api-docs.habitify.me/mcp/others/)
публично заявляет следующие категории: habits list/create/update/archive/delete;
logs complete/fail/skip/measurement и native undo; notes add/update/delete; areas
list/create/update/delete; statistics и journal. Она также заявляет общий с REST
лимит 500 requests/minute/account. Страница **не публикует** tool names,
`inputSchema`, required fields, enums, read-back tool pairing, batch/transaction
semantics или OAuth scope для каждой операции. Поэтому нельзя переносить в MCP
точные REST paths/поля или считать одноимённую capability доказанным tool schema.

## Снимок REST v2

| Сущность | Документированные REST operations | Поля и ограничения на дату проверки |
| --- | --- | --- |
| Habit | `GET/POST /habits`; `GET/PUT/DELETE /habits/{habitId}`; `POST /habits/{habitId}/archive`; journal; statistics | `good\|bad`, description, startDate, archive, log method, occurrence, areas/time-of-day, nested goals/reminders/stacks/end condition |
| Log | create; complete/failed/skipped; undo; delete by log ID | `YYYY-MM-DD`; measurement с value и unit; statuses `completed`, `skipped`, `failed`, `inprogress` |
| Note | list/create/update/delete under habit | content, mood, photo URIs; create требовал хотя бы одно поле |
| Area | list/create/get/update/delete | удаление area снимало привязку и не удаляло habits |
| Goals/reminders/stacks/end conditions/time-of-day | nested Habit fields on create/update | отдельного CRUD в OpenAPI не было; безопасное очищение nested field не документировалось |

Список habits описывал `archived`, `areaId`, `type`, `timeOfDay`, `limit` 1–100 и
`offset`. Journal принимал `date` и иначе использовал «сегодня» в timezone
аккаунта. Statistics включал агрегаты logs/skips/fails/completions/avg и daily
progress. Эти сведения описывают REST snapshot и не доказывают MCP capability.

## Наблюдавшиеся gaps и traps

- OpenAPI не документировал webhook/events, bulk log/write, export/import,
  user-timezone read/set, time-of-day CRUD, отдельный CRUD для goals/reminders/
  stacks/end conditions или raw logs range query. Statistics был агрегатом.
- Documented `unarchive` отсутствовал. REST archive нельзя было считать
  обратимым, а habit/log/note delete был permanent в REST-модели.
- Habit occurrence использовал weekdays `0 = Sunday … 6 = Saturday`, reminder
  filter — `1 = Sunday … 7 = Saturday`; status писался `inprogress`.
- Описание `GET /habits` обещало scheduled-date filter без соответствующего
  query parameter. Notes назывались paginated без `limit/offset`. Area response
  требовал отсутствующее в properties поле `description`. End-condition input
  и response расходились по `periodType`.
- OpenAPI перечислял bearer `AccessTokenAuth`/`IdTokenAuth`, но не описывал
  OAuth flow. Это не разрешало изобретать token exchange.

## Граница MCP capability на 2026-09-13

| Capability | Публично подтверждено | Не подтверждено без runtime `tools/list` |
| --- | --- | --- |
| Delete | MCP docs заявляют delete для habits, notes и areas | Tool names/schemas, permanence, confirmations и read-back; log delete указан только в REST snapshot |
| Undo | MCP docs заявляют native undo logs | Какой именно log можно отменить, окно/ID/schema и post-undo read-back |
| Archive | MCP docs заявляют archive habits; Help Center описывает ручной Unarchive в приложении | MCP unarchive tool/schema; archive нельзя подменять delete или Off Mode |
| Batch | Публичная MCP-страница не заявляет batch | Batch tool, предел, atomicity, rollback и idempotency |
| Off Mode | [Help Center](https://intercom.help/habitify-app/en/articles/6178415-how-to-schedule-time-off-for-off-mode) подтверждает account-wide Time Off: даты, отключение reminders и защиту streaks | Off Mode отсутствует в публичном списке MCP capability; MCP tool/schema не подтверждены. Не эмулировать через skip/archive/delete |
| Exact tools | Нет публичного `tools/list` или JSON Schema | Любые tool names, counts, required fields, enums и scope-to-tool mapping |

Сторонние MCP-серверы, legacy paths и REST API-key access не входят в текущую
архитектуру JediKit. Актуальный runtime contract находится в
`skills/jedikit-habits/references/habitify-mcp.md`.
