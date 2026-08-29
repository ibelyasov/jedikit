# Habitify: runtime-контракт для jedikit-habits

Проверено **2026-08-29** без авторизации и без записи пользовательских данных. Источники — [официальная API-документация](https://api-docs.habitify.me/), её [OpenAPI v2](https://api-docs.habitify.me/openapi/v2/openapi-bundled.yaml), [официальная MCP-документация](https://api-docs.habitify.me/mcp/) и Help Center Habitify. OpenAPI-файл отдаётся с `Last-Modified: 2026-05-18`, `info.version: 2.0.0`.

## 1. Официальные точки подключения

### REST v2

```text
Base URL: https://api.habitify.me/v2
Auth:    X-API-Key: <key>
```

Ключ создаётся только в мобильном приложении (`Settings → API Credentials`), показывается один раз и не восстанавливается. В аккаунте активен только один ключ: генерация нового немедленно отзывает старый. API доступен на платном плане; лимит — **500 запросов/минуту на аккаунт**, превышение даёт `429`. Старые URL/ключи legacy не смешивать с v2 ([официальное пояснение 403](https://intercom.help/habitify-app/en/articles/14075422-troubleshooting-403-forbidden-error-with-the-habitify-api)).

### Официальный MCP

```text
Endpoint:   https://mcp.habitify.me/mcp
Transport:  HTTP Streamable (по текущей MCP-документации)
Auth:       OAuth 2.0, dynamic client registration; API key не нужен
```

На `2026-08-29` read-only preflight: `GET`/`POST` без токена возвращают `401`; `WWW-Authenticate` указывает на [protected-resource metadata](https://mcp.habitify.me/.well-known/oauth-protected-resource), а `OPTIONS` разрешает `GET, POST, DELETE` и заголовки `mcp-protocol-version`, `mcp-session-id`. Metadata указывает authorization server `https://account.habitify.me` и scopes `profile`, `openid`; его [OIDC metadata](https://account.habitify.me/.well-known/openid-configuration) дополнительно рекламирует `/reg`, `/auth`, `/token`, `refresh_token` и scopes `email`, `offline_access`, `all`. Это не доказывает, какие scopes выдаются конкретному клиенту.

Официальная страница [для других MCP-клиентов](https://api-docs.habitify.me/mcp/others/) перечисляет категории tools, но не фиксирует имена и JSON-схемы. Поэтому после OAuth сначала выполнить только `initialize` и `tools/list`, сохранить обнаруженные имена/required fields в runtime и **fail closed** при несовместимости. Не угадывать tool names, batch-возможности или scopes; не использовать REST как скрытый fallback MCP.

Есть официальный drift: Help Center от 2026-03-10 называет тот же URL `SSE` ([страница интеграции](https://intercom.help/habitify-app/en/articles/13843791-use-habitify-with-ai-apps-tools)), тогда как актуальная MCP-документация говорит `HTTP Streamable`. Выбирать транспорт по успешному handshake, а не по старой статье.

## 2. Нативные сущности и операции

| Сущность                                                    | Подтверждённые операции v2                                                                                                                          | Важные поля/ограничения                                                                                                                                                                                                          |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Habit`                                                     | `GET/POST /habits`; `GET/PUT/DELETE /habits/{habitId}`; `POST /habits/{habitId}/archive`; `GET /habits/journal`; `GET /habits/{habitId}/statistics` | `type: good\|bad`; описание, цвет/icon, `startDate`, `isArchived`, `logMethod: manual\|auto`; расписание `daily`, `weekDays`, `monthDays`, `intervalDays`; areas/time-of-day IDs; вложенные goals/reminders/stacks/end condition |
| `Log`                                                       | `POST /habits/{id}/logs`; `POST .../complete\|failed\|skipped`; `POST .../undo`; `DELETE .../logs/{logId}`                                          | Дата `YYYY-MM-DD`; measured log требует `value` + `unitSymbol`; статусы `completed`, `skipped`, `failed`, `inprogress`                                                                                                           |
| `Note`                                                      | `GET/POST/PUT/DELETE /habits/{id}/notes[/noteId]`                                                                                                   | `content`, `moodLevel` (`veryLow`…`veryHigh`), URI `photos`; создание требует хотя бы одно поле                                                                                                                                  |
| `Area`                                                      | `GET/POST /areas`; `GET/PUT/DELETE /areas/{areaId}`                                                                                                 | Удаление area только снимает привязку, привычки не удаляет                                                                                                                                                                       |
| Goals, reminders, habit stacks, end conditions, time-of-day | Возвращаются/задаются как вложенные поля Habit при `POST/PUT /habits`                                                                               | Отдельных CRUD endpoint в OpenAPI нет; `PUT` не документирует безопасное очищение поля                                                                                                                                           |

Для списка привычек есть `archived`, `areaId`, `type`, `timeOfDay`, `limit` (1–100, default 50), `offset` (≥0). Journal принимает `date` и по умолчанию использует «сегодня» в timezone аккаунта. Statistics возвращает `totalLogs`, `skips`, `fails`, `completions`, `avg`, unit/periodicity и `dailyProgress` (`date`, `totalLog`, `status`).

## 3. Нормализованный узкий contract skill

Skill может иметь provider-independent операции:

```text
habits.list(filters?)       habits.get(id)
habits.create(input)        habits.update(id, patch)
habits.archive(id)          habits.delete(id)       # irreversible
journal.get(date?)          statistics.get(id, startDate?, endDate?)
logs.complete|failed|skipped(id, targetDate?)
logs.measure(id, value, unitSymbol, targetDate?)
logs.undo(id, targetDate?)  logs.delete(id, logId)  # irreversible
notes.list|create|update|delete(habitId, ...)
areas.list|create|update|delete(...)
```

Имена выше — внутренняя абстракция, не обещание официальных MCP tool names. Для `tools/list` сохранять только реальные схемы; unknown/несовместимый provider capability отключать локально.

## 4. Provider-specific ограничения

Общий read/write workflow, подтверждения и partial-failure report определяет
[coaching.md](coaching.md). Здесь остаются только факты, зависящие от Habitify.

- `archive` обратим только средствами, которые API сейчас не документирует; `DELETE habit` удаляет habit, logs, notes, goals и reminders навсегда. `logs.delete`, `notes.delete`, `areas.delete` также permanent. Не подменять delete архивом и не выполнять массовые writes.
- Не помещать API key/OAuth token в prompt, skill, memory, git или обычные логи. API key хранить в env/secret store и помнить, что ротация ломает все старые интеграции. OAuth ведёт host. Не логировать содержимое notes/photos и персональные данные.
- Habitify заявляет [prompt-controlled request/response, без background streaming и с минимальной передачей данных](https://intercom.help/habitify-app/en/articles/14074824-how-data-flows-between-habitify-and-ai-agents-mcp); это эксплуатационное заявление поставщика, а не основание ослаблять локальные границы доступа.

## 5. Точные пробелы и traps

- В v2 OpenAPI нет документированных webhook/events, bulk log/write, export/import, user-timezone read/set, time-of-day CRUD, отдельного goal/reminder/stack/end-condition CRUD или GET raw logs по диапазону. Statistics — агрегат, не замена полной истории. Для фонового refresh нужен внешний scheduler и явное окно дат.
- Нет documented `unarchive`; permanent delete нельзя считать обратимым.
- Даты везде `YYYY-MM-DD`; timezone endpoint отсутствует, а journal «today» зависит от timezone аккаунта. Не вычислять локальную дату молча — принимать её от host/user и явно показывать.
- Расписание `occurrence.weekDays`: **0 = Sunday … 6 = Saturday**. У reminder `occurrenceFilter.weekDays`: **1 = Sunday … 7 = Saturday**.
- Journal/status enum — **`inprogress`** (без подчёркивания). Не принимать legacy-вариант `in_progress` без явного provider mapping.
- Описание `GET /habits` обещает фильтр scheduled date, но такого query parameter в OpenAPI нет. `GET notes` называется paginated, но `limit/offset` не описаны. У Area response `required` содержит `description`, которого нет среди properties. Input end conditions для `streak`/`successPeriods` не принимают `periodType`, хотя response его требует. Эти места покрыть contract tests и при неоднозначности fail closed.
- REST OpenAPI также перечисляет bearer `AccessTokenAuth`/`IdTokenAuth`, но не описывает OAuth flow; для jedikit использовать официальный MCP OAuth или API-key REST, не изобретать обмен токенов.

**Не использовать сторонние MCP-серверы как fallback.** Их provenance, legacy-пути, заголовки и схемы не являются официальным контрактом Habitify v2; при недоступности официального MCP остановить только текущую habit-операцию и сообщить конкретный capability/auth gap.

Safety/privacy policy и ограничения клинических выводов находятся в
[evidence-and-safety.md](evidence-and-safety.md).
