# Один источник скиллов, подключения настраиваются на хосте

`skills/` в корне — единственный источник для Hermes, Claude Code и Codex: корневой portable `plugin.json` читают Hermes и Codex, `.claude-plugin/plugin.json` — Claude Code. Генерации и копий нет. Плагин не объявляет MCP и секреты ни для одного хоста. Подключения и их реализация принадлежат хосту.

Провайдерные скиллы объявляют ожидания в [`skills/jedikit-tasks/tools.json`](../../skills/jedikit-tasks/tools.json), [`skills/jedikit-habits/tools.json`](../../skills/jedikit-habits/tools.json) и [`skills/jedikit-calendar/tools.json`](../../skills/jedikit-calendar/tools.json): сервер у каждой операции, базовое имя без префикса хоста, `read`/`write`; у Habitify и Google Calendar ещё `required`. Чтения Habitify объявлены на сервере `habitify_read`, записи — на `habitify`: хост держит их в отдельных экземплярах с разным уровнем доверия. Google Calendar объявлен на сервере `google_calendar`. Это декларативный внешний контракт, задаваемый JediKit. Изменение имён выполняется вместе со скиллом и отмечается в release notes. У `jedikit-planning` и навигатора `jedikit` своих провайдеров и `tools.json` нет.

SingularityApp подключается через официальный hosted MCP, OAuth проводит хост. Habitify предоставляется инструментами хоста по REST/OpenAPI v2, с ключом только у доверенного адаптера ([ADR 0001](0001-habitify-via-rest.md)). Google Calendar предоставляется инструментами хоста ([ADR 0009](0009-separate-calendar-skill.md)). На Hermes владельца подключения настраивает clanwright. Для глубокого уточнения намерения хост предоставляет внешний скилл `grill-me` ([ADR 0013](0013-clarification.md)); JediKit не реализует собственное интервью.

## Consequences

Установка плагина не подключает провайдеры ни на одном хосте. Если нужных инструментов нет, скилл называет недостающие базовые имена из своего `tools.json` и рекомендует подключить их средствами хоста; сам ничего не устанавливает и не настраивает. После каждой записи — Read-back. Владелец пользуется скиллами и сообщает о проблемах, обязательного ручного runtime-гейта нет. Публикация версии (тег и GitHub release) остаётся отдельным решением владельца.
