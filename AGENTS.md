# Контракт разработки JediKit

JediKit содержит два русскоязычных Agent Skill: `jedikit-tasks` для SingularityApp и `jedikit-habits` для Habitify. Пользовательские инструкции, обсуждения, коммиты и PR пишем по-русски; identifiers, команды и API сохраняем оригинальными.

Claude Code читает этот `AGENTS.md` напрямую при отсутствии project `CLAUDE.md` (native discovery с 2.1.277, default mode `claude-md-or-agents-md`). По уточнению владельца от 2026-10-06 адаптер `CLAUDE.md` исключён; не создавай его. Контракт и ограничения parent instructions — в `research/platforms/claude.md`.

## Источники истины и карта репозитория

Перед изменением прочитай [утверждённую пересборку #1](https://github.com/ibelyasov/jedikit/issues/1), [CONTEXT.md](CONTEXT.md) и относящиеся к задаче [ADR](docs/adr/). #1 задаёт согласованный scope, CONTEXT — термины и модель, ADR — принятые решения. Не переоткрывай согласованные решения по собственной инициативе. Настоящее противоречие между ними: останови затронутую работу и сообщи владельцу с точными ссылками; рутинные детали решай самостоятельно.

| Путь | Назначение |
| --- | --- |
| `skills/jedikit-tasks/`, `skills/jedikit-habits/` | Единственный источник инструкций и справочных материалов скиллов |
| `plugin.json`, `.claude-plugin/plugin.json` | Portable manifest для Hermes/Codex и manifest Claude Code |
| `README.md` | Установка, подключения провайдеров на хосте и приёмка |
| `research/{tasks,habits,providers,platforms}/`, `research/sources.md` | Основания, контракты и происхождение источников |
| `docs/adr/`, `CONTEXT.md` | Решения и единый словарь |
| `BACKLOG.md` | Отложенные возможности, без обещания реализации |
| `.github/workflows/check.yml` | Статические проверки |
| `LICENSE`, `THIRD-PARTY-NOTICES.md` | MIT оригинальных материалов и права третьих лиц |
| `.work/` | Игнорируемые временные планы и читаемые результаты проверок |

Текущий контракт описывай в канонических документах, временный план — в `.work/`. Не создавай параллельную постоянную спецификацию. Используй термины CONTEXT в предложениях, исследованиях, тикетах и сценариях проверки.

## Авторинг и границы

- В каждом `SKILL.md` обязателен YAML frontmatter с `name` (kebab-case, совпадает с каталогом) и `description` (когда выбирать скилл, без пересказа процедуры). Основной текст даёт наблюдаемый результат; подробности выносятся в локальные `references/`.
- Один корневой `skills/` для всех хостов; без generated copies, `packages/jedikit` и `agents/openai.yaml` (ADR 0005, #1).
- Только инструкции, декларативные manifests и документы. Не добавляй собственный код, скрипты, генераторы, MCP/proxy/runtime, custom graders или scaffold scripts. Пробел в штатной проверке сообщай владельцу; новый код требует отдельного решения (ADR 0004).
- SingularityApp работает через официальный hosted MCP; Habitify — только через официальный REST API v2, без MCP/fallback (ADR 0001). Для Hermes/Codex плагин не объявляет MCP и секреты (ADR 0005). Явное исключение задачи #7 — Claude-only `.mcp.json` с публичным endpoint SingularityApp для загрузки и native mocks; OAuth и ключ Habitify настраивает владелец на хосте по README.
- Записи следуют #1: явная одиночная команда — сразу; предложение агента — после Preview и подтверждения; группа операций — последовательно, стоп на первой ошибке, отчёт applied/unapplied, без автоматического отката; после записи Read-back. Фоновые запуски только читают (ADR 0003).
- Native memory хранит только настройки по ADR 0006. Kanban исключён (ADR 0007). После ручного переноса идеи, справки или встречи исходный Inbox item отменяется через `task_cancel` с подтверждением (ADR 0008). Off Mode отсутствует в API Habitify: только инструкция для приложения, команды `off` нет.
- Сохраняй чужие изменения. Не включай в файлы или логи секреты и личные данные провайдеров. Provider, DNS, ACME, deploy, backup-writer, restore, prune, credential и secret mutations требуют явного разрешения владельца.

## Проверки и доказательства

Релевантные штатные проверки:

```sh
claude plugin validate . --strict
claude plugin validate .claude-plugin/plugin.json --strict
hermes plugins validate . --json
hermes plugins doctor . --ci
git diff --check
```

Claude strict проверяет декларации, не поведение. Directory validation выбирает marketplace первым; версия 2.1.289 при соседнем plugin manifest проверяет и его компоненты. Direct command даёт отдельный отчёт plugin. Hermes validate включает scanner; doctor проверяет discovery/load/registration. Прочитай reports и warnings: exit `0` Hermes сам по себе не доказывает точный inventory обоих скиллов или отсутствие component diagnostics. Замена CI на официальный Hermes Action с pinned revision принадлежит тикету #6. Отдельный native validator/eval Codex в исследованной версии не найден; не заменяй его Python helper или собственной assertion logic.

Поведенческие проверки — штатный `claude plugin eval` с native fixed mock-ответами провайдеров и native graders, локально перед релизом. Mocks исключают provider calls, но модель всё равно расходует account/budget: запуск требует отдельного разрешения на модель и бюджет. Не включай реальные серверы, scaffold или agent mocks без соответствующего разрешения.

Сохраняй читаемый вывод каждой проверки, команду, exit status и длительность в согласованном каталоге `.work/`. Отчёт завершения: изменённые пути, выполненные проверки и ссылки на вывод, непроверенные слои и риски. Статика, загрузка, поведение модели, авторизация провайдеров, запись/Read-back и приёмка — разные результаты. Обязательную runtime-приёмку Hermes на Nix-сервере проводит владелец; Claude Code и Codex заявлены без runtime-гейта. Тег и prerelease — отдельное решение после приёмки, не следствие зелёного CI.

## Исследования

Для вопросов о синтаксисе, настройке, версиях и поведении CLI/API сначала проверь установленную версию, локальную справку/source и исследования репозитория; затем текущую официальную документацию или официальный `llms.txt`. Для обычного рефакторинга и редактирования документов внешний поиск не нужен.

Каждый проверяемый тезис сопровождай первичной ссылкой и датой доступа; для реализации сохраняй version/commit pin. Различай заявления vendor, независимое чтение source, локально выполненную проверку и anecdote. Недоступный источник и непроверенный runtime явно оставляй неопределёнными. Авторские положения Дорофеева отделяй от академических выводов и продуктовых решений; расхождение с автором выноси владельцу. Сохраняй provenance в `research/sources.md`, формулируй самостоятельно, не копируй книги и чужие ассеты. Правовые основания — `research/legal-and-attribution.md`.

## GitHub Issues и triage

Трекер — GitHub Issues [ibelyasov/jedikit](https://github.com/ibelyasov/jedikit/issues), через `gh` из checkout. Спецификации и тикеты публикуй как issues в разрешённом scope; PR не является поверхностью запросов. Читай body, labels и comments; фильтруй по state/labels, сохраняй историю в comments. Для многострочных bodies/comments используй временный файл и `--body-file`. GitHub mutations выполняй только в пределах разрешения владельца.

| Каноническая роль и label | Значение |
| --- | --- |
| `needs-triage` | Требуется оценка сопровождающего |
| `needs-info` | Ожидается информация от автора запроса |
| `ready-for-agent` | Полностью определено для автономного агента |
| `ready-for-human` | Требуется реализация человеком |
| `wontfix` | Запрос не будет реализован |

Для wayfinding: один map issue с `wayfinder:map` и разделами Notes, Decisions-so-far, Fog; дочерние sub-issues типов `wayfinder:research`, `wayfinder:prototype`, `wayfinder:grilling`, `wayfinder:task`. Если sub-issues недоступны, используй task list карты и `Part of #<map>` в дочернем тикете. Блокировки — native dependencies либо `Blocked by: #<number>`. Frontier — первый открытый неназначенный тикет в порядке карты с закрытыми блокерами. Перед работой назначь driving developer; по завершении сохрани результат в comment, закрой разрешённый тикет и добавь ссылку/решение в Decisions-so-far.

`gh` использует существующую macOS Keychain-аутентификацию. Sandbox failure не доказывает expiry: запроси исполнение вне sandbox через штатный approval, без `gh auth login`, извлечения токена или браузерного обхода. Git transport — SSH, проверяемый отдельно. Коммит содержит обязательную атрибуцию `Co-Authored-By: Codex <noreply@openai.com>`.
