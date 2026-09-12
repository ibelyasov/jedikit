# Исследовательская база JediKit

Индекс источников и решений. Текущий продуктовый контракт —
[product-decisions.md](product-decisions.md); устройство модулей —
[skill-suite-architecture.md](skill-suite-architecture.md); команды разработки —
[README](../README.md#разработка-и-проверка).

## Навигация

| Направление              | Файл                                                                    | Что внутри                                                          |
| ------------------------ | ----------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Итоги grilling           | [product-decisions.md](product-decisions.md)                            | Согласованный продуктовый контракт v1 и закрытые границы            |
| Архитектура набора       | [skill-suite-architecture.md](skill-suite-architecture.md)              | Один пакет, узкие skills, адаптеры Codex/Claude/Hermes              |
| Нейминг                  | [naming-candidates.md](naming-candidates.md)                            | Финальное решение JediKit и история проверенных кандидатов          |
| Исследования habits      | [skills/jedikit-habits/references](../skills/jedikit-habits/references) | Академические основания, safety и Habitify MCP-контракт             |
| Habitify provider research | [habitify-provider-research.md](habitify-provider-research.md) | Датированный REST/OpenAPI срез, исключённый из runtime |
| Отложенные направления   | [../BACKLOG.md](../BACKLOG.md)                                          | Идеи, ожидания, напоминания и другие расширения                     |
| SingularityApp и MCP     | [singularity-mcp.md](singularity-mcp.md)                                | REST API v2, hosted MCP, OAuth/scopes, сущности и ограничения       |
| Live MCP probe           | [singularity-mcp-live-probe.md](singularity-mcp-live-probe.md)          | OAuth least privilege, версия сервера и scope-filtered `tools/list` |
| Полный каталог MCP tools | [singularity-mcp-tools.md](singularity-mcp-tools.md)                    | Live `tools/list`: 48 точных контрактов и capability matrix         |
| Встроенные MCP prompts   | [singularity-mcp-prompts.md](singularity-mcp-prompts.md)                | Четыре server-provided шаблона и расхождения с продуктом            |
| Авторская методология    | [jedi-method-primary.md](jedi-method-primary.md)                        | Decision trees, операционные карточки, правила и provenance         |
| Практики сообщества      | [jedi-community-practices.md](jedi-community-practices.md)              | Сценарии, примеры, decision tables и recovery playbooks             |
| Codex                    | [platform-codex.md](platform-codex.md)                                  | Agent Skills, plugins, MCP и Scheduled Tasks                        |
| Claude                   | [platform-claude.md](platform-claude.md)                                | Skills/plugins, marketplace, MCP и scheduling                       |
| Hermes                   | [platform-hermes.md](platform-hermes.md)                                | Skills Hub/taps, MCP, cron, delivery и permissions                  |
| Право и атрибуция        | [legal-and-attribution.md](legal-and-attribution.md)                    | Copyright, бренды, MIT и дисклеймер                                 |
| Тестирование             | [testing-strategy.md](testing-strategy.md)                              | Fake MCP, safety cases, smoke tests и acceptance matrix             |
| Архив Procoder           | [archive/procoder](archive/procoder)                                    | Исторические ответы и решения retired local workflow                |

Platform-файлы сохраняют датированные срезы первоначального task-only исследования. Их старые product-overlay формулировки считаются историческими; текущая двухskill-архитектура зафиксирована здесь и в [product-decisions.md](product-decisions.md).

Датированные platform research и grilling records сохраняют основания и историю
решений. Они не являются инструкцией установки текущего candidate или
доказательством его готовности. Исполняемые правила находятся в `skills/`;
вопросы текущей сборки и проверки решаются по README и исходникам инструментов.
