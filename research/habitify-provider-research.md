# Habitify provider research: REST/OpenAPI snapshot

Статус: исторический research, **не runtime-контракт JediKit**. Проверено
2026-08-29 без авторизации и без записи пользовательских данных. JediKit runtime
использует только официальный MCP и текущий `tools/list`; описанные ниже REST
paths, поля и enums нельзя переносить в MCP-вызовы или использовать как fallback.

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

Официальный MCP был указан как `https://mcp.habitify.me/mcp`, OAuth 2.0 и HTTP
Streamable. Read-only preflight без токена возвращал `401`; protected-resource
metadata указывал `https://account.habitify.me`. Help Center от 2026-03-10
называл тот же URL SSE в [старой инструкции](https://intercom.help/habitify-app/en/articles/13843791-use-habitify-with-ai-apps-tools),
тогда как MCP-документация указывала HTTP Streamable. Это датированный drift,
а не основание угадывать transport или scopes.

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

Сторонние MCP-серверы, legacy paths и REST API-key access не входят в текущую
архитектуру JediKit. Актуальный runtime contract находится в
`skills/jedikit-habits/references/habitify-mcp.md`.
