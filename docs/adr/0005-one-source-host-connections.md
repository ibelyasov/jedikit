# Один источник скиллов, подключения настраиваются на хосте

`skills/` в корне — единственный источник для Hermes, Claude Code и Codex: корневой portable `plugin.json` читают Hermes и Codex, `.claude-plugin/plugin.json` — Claude Code. Генерации и копий нет. Плагин не объявляет MCP-серверы и секреты: SingularityApp (OAuth) и ключ Habitify настраиваются на хосте по инструкции из README. Так Hermes не создаёт namespaced MCP-дубли без OAuth, из-за которых раньше понадобился отдельный пакет `packages/jedikit`.

Исключение — `.mcp.json` в корне: его читает только Claude Code, а Hermes и Codex — нет. Там объявлен только публичный endpoint SingularityApp без секретов, потому что Claude Code проводит OAuth сам и дублей не создаёт.

## Consequences

Установка плагина в Hermes и Codex не подключает провайдеры: это отдельный шаг на каждом хосте. Обязательная приёмка — только Hermes; поддержка Claude Code и Codex заявлена без runtime-гейта.
