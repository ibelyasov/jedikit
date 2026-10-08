# Один каталог скиллов для Hermes Agent, подключения настраиваются в Hermes

JediKit работает на одном хосте — Hermes Agent. `skills/` в корне — единственный источник пяти скиллов; корневой portable `plugin.json` (Agent Plugins 1.0.0) описывает пакет без кода, `extensions`, MCP и секретов. Генерации, копий и других manifests нет.

Hermes подключает тот же `skills/` закреплённой ревизии одним из двух штатных способов:

- **Каталог в `skills.external_dirs`** — основной способ; так JediKit подключён у владельца через clanwright. Скиллы обычные: голые имена (`jedikit-tasks`), имя и начало `description` в индексе скиллов system prompt, slash `/jedikit-tasks`.
- **`hermes plugins install ibelyasov/jedikit --ref <FULL_SHA> --enable`**. Скиллы получают имена `agent-plugin-jedikit-805a716c:<скилл>` и в индекс system prompt не попадают: их находят через `skills_list`, загружают через `skill_view`, заранее подключают `hermes chat --skills '<имя>'`.

Инструкции одинаковы для обоих способов: соседний скилл JediKit загружается `skill_view(name=…)` с тем же префиксом, что у текущего скилла, — голым именем или тем же `agent-plugin-…:`. Frontmatter скилла содержит только `name` и `description`: вложенный `metadata.hermes` portable loader не принимает и отбрасывает скилл.

Провайдерные скиллы объявляют ожидания в [`skills/jedikit-tasks/tools.json`](../../skills/jedikit-tasks/tools.json), [`skills/jedikit-habits/tools.json`](../../skills/jedikit-habits/tools.json) и [`skills/jedikit-calendar/tools.json`](../../skills/jedikit-calendar/tools.json): сервер у каждой операции, базовое имя без префикса, `read`/`write`; у Habitify и Google Calendar ещё `required`. Чтения Habitify объявлены на сервере `habitify_read`, записи — на `habitify`: это отдельные экземпляры с разным уровнем доверия. Google Calendar объявлен на сервере `google_calendar`. Агент вызывает их как `mcp__<server>__<base_name>`. Это декларативный внешний контракт, задаваемый JediKit; изменение имён выполняется вместе со скиллом и отмечается в release notes. У `jedikit-planning` и навигатора `jedikit` своих провайдеров и `tools.json` нет.

MCP-серверы настраиваются в Hermes. SingularityApp — официальный hosted MCP на сервере `singularity`, OAuth проводит Hermes. Habitify предоставляет доверенный адаптер по REST/OpenAPI v2 с ключом только у адаптера ([ADR 0001](0001-habitify-via-rest.md)). Google Calendar — сервер `google_calendar` ([ADR 0009](0009-separate-calendar-skill.md)). У владельца серверы, toolsets и cron настраивает clanwright. Для глубокого уточнения намерения нужен внешний скилл `grill-me` ([ADR 0013](0013-clarification.md)); JediKit не реализует собственное интервью.

## Considered Options

- Native `plugin.yaml`: требует Python-модуля с `register()`, то есть кода ([ADR 0004](0004-no-custom-code.md)), и не подключает MCP или toolsets.
- Только Skills Hub (`hermes skills install`): ставит скиллы по одному с default branch без выбора ревизии, копия изменяема.
- `metadata.hermes` (`tags`, `related_skills`, `requires_*`): несовместимо с plugin install; `requires_*` при включённом Tool Search может скрыть исправный скилл из индекса.

## Consequences

Установка JediKit не подключает провайдеров. Если нужных инструментов нет, скилл называет недостающие базовые имена из своего `tools.json` и рекомендует подключить их в Hermes; сам ничего не устанавливает и не настраивает. После каждой записи — Read-back. Владелец пользуется скиллами и сообщает о проблемах, обязательного ручного runtime-гейта нет. Публикация версии (тег и GitHub release) остаётся отдельным решением владельца. Основания — [досье Hermes](../../research/platforms/hermes.md).
