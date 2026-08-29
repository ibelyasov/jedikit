# Исследовательская база JediKit

Проверено: **2026-08-29**. Исследования собраны до проектирования и реализации; повторный audit/grilling 2026-08-29 зафиксирован в каноническом журнале решений. Финальный бренд — **JediKit**; канонический package/repo slug — `jedikit`, первый skill — `jedikit-tasks`. Текущий GitHub-репозиторий ещё не переименован.

## Навигация

| Направление              | Файл                                                           | Что внутри                                                          |
| ------------------------ | -------------------------------------------------------------- | ------------------------------------------------------------------- |
| Итоги grilling           | [product-decisions.md](product-decisions.md)                   | Согласованный продуктовый контракт v1 и закрытые границы            |
| Архитектура набора       | [skill-suite-architecture.md](skill-suite-architecture.md)     | Один пакет, узкие skills, адаптеры Codex/Claude/Hermes              |
| Нейминг                  | [naming-candidates.md](naming-candidates.md)                   | Финальное решение JediKit и история проверенных кандидатов          |
| Отложенные направления   | [../BACKLOG.md](../BACKLOG.md)                                 | Идеи, ожидания, напоминания, привычки и другие расширения           |
| SingularityApp и MCP     | [singularity-mcp.md](singularity-mcp.md)                       | REST API v2, hosted MCP, OAuth/scopes, сущности и ограничения       |
| Live MCP probe           | [singularity-mcp-live-probe.md](singularity-mcp-live-probe.md) | OAuth least privilege, версия сервера и scope-filtered `tools/list` |
| Полный каталог MCP tools | [singularity-mcp-tools.md](singularity-mcp-tools.md)           | Live `tools/list`: 48 точных контрактов и capability matrix         |
| Встроенные MCP prompts   | [singularity-mcp-prompts.md](singularity-mcp-prompts.md)       | Четыре server-provided шаблона и расхождения с продуктом            |
| Авторская методология    | [jedi-method-primary.md](jedi-method-primary.md)               | Decision trees, операционные карточки, правила и provenance         |
| Практики сообщества      | [jedi-community-practices.md](jedi-community-practices.md)     | Сценарии, примеры, decision tables и recovery playbooks             |
| Codex                    | [platform-codex.md](platform-codex.md)                         | Agent Skills, plugins, MCP и Scheduled Tasks                        |
| Claude                   | [platform-claude.md](platform-claude.md)                       | Skills/plugins, marketplace, MCP и scheduling                       |
| Hermes                   | [platform-hermes.md](platform-hermes.md)                       | Skills Hub/taps, MCP, cron, delivery и permissions                  |
| Право и атрибуция        | [legal-and-attribution.md](legal-and-attribution.md)           | Copyright, бренды, MIT и дисклеймер                                 |
| Тестирование             | [testing-strategy.md](testing-strategy.md)                     | Fake MCP, safety cases, smoke tests и acceptance matrix             |

## Согласованный v1

### Продукт и архитектура

- Публичный неофициальный русскоязычный Agent Skill под MIT для оригинальных материалов проекта.
- Официальный hosted MCP SingularityApp используется напрямую; собственный MCP и REST fallback не нужны.
- Один зонтичный пакет `jedikit` с одним рабочим skill `jedikit-tasks`. Идеи, ожидания, напоминания, привычки и расширенное управление проектами остаются в backlog.
- Каноническое portable-ядро и тонкие адаптеры Codex, Claude и Hermes. Широкого router skill в v1 нет.
- Финальное имя — **JediKit**; tagline — «Разгрузи голову. Действуй ясно.» Наблюдаемая нишевая коллизия со старым Star Wars-модом принята пользователем осознанно.

### Модель данных и структура

- Верхнеуровневые области `Работа` и `Личное`, плюс выбранные пользователем области. Внутри основных областей — контейнеры `Общее` для одиночных задач.
- Области и `Общее` — контейнеры, а не проекты с обязательным следующим действием.
- Только явный capture («запиши/сохрани, чтобы не забыть») сохраняет исходную фразу во Inbox. Во время triage task/project исходный item переиспользуется: он переименовывается и перемещается, а task-дубликат не создаётся. История и служебный `raw_text` не сохраняются.
- Для idea/reference/meeting skill даёт инструкцию ручного переноса и не создаёт prep/follow-up task. После отдельного подтверждения переноса cleanup требует собственного delete-preview и второго подтверждения; текущий hosted MCP не имеет подтверждённого delete-tool, поэтому item сохраняется без archive/cancel fallback.

### Задачи, даты и подтверждения

- Каноническая задача содержит конкретный глагол, объект и наблюдаемый критерий завершения.
- Deadline — только внешняя жёсткая дата; start — только выбранная пользователем плановая дата. Capture и triage не ставят дату автоматически.
- Одиночная обратимая запись допустима сразу в явно понятном контексте. Групповые изменения и существенная перепланировка требуют preview и подтверждения.
- Hosted MCP не предоставляет подтверждённого permanent delete или настоящего batch. Желаемый manual-transfer cleanup поэтому сейчас блокируется capability gap; archive не называется и не используется как delete. Согласованная группа выполняется последовательными наблюдаемыми операциями.
- Завершение задачи не запускает unsolicited push и не предлагает следующую задачу. Следующий шаг проекта проверяется только по запросу пользователя, в daily close или weekly review.

### Регулярные практики

- `daily open` формирует **focus list for today**, а не календарный план. Он учитывает тип дня и ресурс, но не читает календарь и прямо сообщает об этом ограничении.
- `daily close` проверяет только проекты, затронутые сегодня. Если вчерашний close пропущен, следующий open автоматически сначала выполняет полный catch-up.
- `weekly` проходит все активные реальные проекты и входящие. Календарь не проверяется; ограничение называется явно.
- Прерванный daily/weekly в следующий раз начинается с нуля. Timestamp меняется только после полного прохождения и явного подтверждения пользователя.
- Scheduled run всегда read-only и присылает короткое приглашение к обзору. Если нативный scheduler недоступен, skill только объясняет ограничение — без OS cron/launchd fallback.

### Память и приватность

- Только native memory агента; никаких служебных файлов, тегов, проектов, notebook или заметок в SingularityApp.
- Автоматически сохраняются только timezone, рабочие дни, окна обзоров, IDs/режимы корневых областей и timestamps завершённых обзоров.
- Содержимое задач, названия проектов, история обзоров и старые формулировки не копируются.
- Если memory недоступна, skill один раз объясняет ограничение и продолжает без fallback-хранилища.

### Команды

`setup`, `capture`, `triage`, `daily open`, `daily close`, `weekly`, `project`, `status`, `help`, `memory show`, `memory forget`, `memory reset` — и эквивалентные запросы на естественном русском.

## Подтверждённые ограничения платформ

- Hosted MCP: `singularity-mcp ^2.0.1`, protocol `2025-11-25`; full-scope Hermes probe вернул 48 tools. Явных permanent-delete и batch tools нет.
- Четыре встроенных MCP prompts исследованы, но core v1 их не использует: они навязывают часы/квоты и расходятся с согласованными review/triage правилами.
- Codex и Claude могут установить plugin с несколькими skills. Hermes tap регистрирует источник, но официальная документация показывает установку отдельных skills; bundle — runtime alias уже установленных skills.
- Marketplace-релизы не симметричны и отложены до стабильного GitHub prerelease.

## Статус

Повторный grilling завершён. Источник истины — [product-decisions.md](product-decisions.md); отложенные направления — [BACKLOG.md](../BACKLOG.md). Текущий tree прошёл fail-closed release gate и остаётся `unreleased candidate` до отдельного решения о version/tag и публикации.
