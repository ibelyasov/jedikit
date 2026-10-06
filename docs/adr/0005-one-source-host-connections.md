# Один источник скиллов, подключения настраиваются на хосте

`skills/` в корне — единственный источник для Hermes, Claude Code и Codex: корневой portable `plugin.json` читают Hermes и Codex, `.claude-plugin/plugin.json` — Claude Code. Генерации и копий нет. Плагин не объявляет MCP-серверы и секреты: SingularityApp (OAuth) и ключ Habitify настраиваются на хосте по инструкции из README. Так Hermes не создаёт namespaced MCP-дубли без OAuth, из-за которых раньше понадобился отдельный пакет `packages/jedikit`.

## Consequences

Установка плагина не подключает провайдеры: это отдельный шаг на каждом хосте. Обязательная приёмка — только Hermes; поддержка Claude Code и Codex заявлена без runtime-гейта.
