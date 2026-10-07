# JediKit

Два русскоязычных Agent Skill для личной продуктивности:

- **`jedikit-tasks`** ведёт задачи в [SingularityApp](https://singularity-app.com) по методу «Джедайских техник» Максима Дорофеева и исследованиям работы с задачами: Capture, Triage, следующий шаг проекта, Daily open, Daily close, Weekly и разбор Inbox debt. Фокус-лист составляется без календаря и проверки вместимости; разделы и теги поддерживаются, kanban — нет ([ADR 0007](docs/adr/0007-no-kanban.md)).
- **`jedikit-habits`** ведёт поведенческие эксперименты в [Habitify](https://habitify.me) на основе академических исследований: план эксперимента в заметке привычки, отметки, помощь при тяге и обзор эксперимента. Одна привычка за раз; при признаках клинического риска Safety-стоп направляет к специалисту.

Решение всегда остаётся за пользователем. Явная одиночная команда выполняется сразу; изменение, предложенное агентом, — только после Preview и подтверждения. Группа операций получает один Preview и одно подтверждение, выполняется последовательно и останавливается на первой ошибке с отчётом applied/unapplied. После каждой записи агент перечитывает результат (Read-back). Фоновые запуски по расписанию только читают, а память агента хранит только настройки. Термины — в [CONTEXT.md](CONTEXT.md), решения — в [docs/adr/](docs/adr/).

Проект в ранней версии: опубликованы prerelease-сборки, последняя — [`v0.3.0-alpha.2`](https://github.com/ibelyasov/jedikit/releases/tag/v0.3.0-alpha.2).

## Установка

| Хост | Что ставить |
| --- | --- |
| [Claude Code](#claude-code) | плагин из GitHub marketplace |
| [Codex](#codex) | плагин из GitHub marketplace |
| [Hermes](#hermes) | плагин из репозитория по commit SHA |
| [ChatGPT, Claude.ai](#chatgpt-и-claudeai) | ZIP нужного скилла из релиза |

Установка добавляет только инструкции. Доступ к SingularityApp и Habitify хост предоставляет отдельно — см. [«Что должен дать хост»](#что-должен-дать-хост).

### Claude Code

```sh
claude plugin marketplace add ibelyasov/jedikit
claude plugin install jedikit@jedikit
```

Явный вызов — `/jedikit:jedikit-tasks` и `/jedikit:jedikit-habits`. Подробности — [досье Claude Code](research/platforms/claude.md).

### Codex

```sh
codex plugin marketplace add ibelyasov/jedikit --ref v0.3.0-alpha.2
codex plugin add jedikit@jedikit
```

Codex устанавливает плагин в cache: после обновления проверьте установленную ревизию в новой сессии, а имена для явного вызова — в `/skills`. Подробности — [досье Codex](research/platforms/codex.md).

### Hermes

Hermes принимает только полный 40-символьный commit SHA; SHA каждой версии указан на её [странице релиза](https://github.com/ibelyasov/jedikit/releases).

```sh
hermes plugins install ibelyasov/jedikit --ref <FULL_JEDIKIT_COMMIT_SHA> --enable
```

Точное имя скилла для явного вызова дают `skills_list` и `skill_view`; загрузить скилл до начала чата — `hermes chat --skills '<EXACT_QUALIFIED_SKILL_NAME>'`. Подробности — [досье Hermes](research/platforms/hermes.md).

### ChatGPT и Claude.ai

1. Скачайте `jedikit-tasks.zip` или `jedikit-habits.zip` со [страницы релиза](https://github.com/ibelyasov/jedikit/releases/tag/v0.3.0-alpha.2).
2. ChatGPT: **Skills → Create → Upload from your computer** ([справка](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)). Claude.ai: **Settings → Capabilities → Skills → Upload skill** ([справка](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)).
3. Подключите MCP средствами веб-хоста.

`jedikit-habits` в веб-приложениях работает только при подключённом MCP с операциями из его `tools.json`. Работа скиллов в веб-приложениях не проверялась.

## Что должен дать хост

Ожидаемые операции перечислены в [`skills/jedikit-tasks/tools.json`](skills/jedikit-tasks/tools.json) (35 операций) и [`skills/jedikit-habits/tools.json`](skills/jedikit-habits/tools.json) (23 операции). У каждой операции указаны сервер, базовое имя без префикса хоста и доступ `read` или `write`; у Habitify ещё обязательные аргументы `required`.

- **SingularityApp** — официальный hosted MCP `https://mcp.singularity-app.com/mcp`, подключённый средствами хоста; OAuth проводит хост.
- **Habitify** — операции по официальному REST/OpenAPI v2, которые предоставляет доверенный адаптер хоста: чтения на сервере `habitify_read`, записи — на `habitify`. API-ключ хранится только у адаптера, агент его не видит. Официальный Habitify MCP не подходит: в нём нет создания и изменения привычек, заметок и архивации ([ADR 0001](docs/adr/0001-habitify-via-rest.md), [справка инструментов](skills/jedikit-habits/references/habitify-tools.md)).

Плагин не объявляет MCP-серверы и секреты ни для одного хоста ([ADR 0005](docs/adr/0005-one-source-host-connections.md)). Если нужных операций нет, скилл называет недостающие и предлагает подключить их средствами хоста; сам он ничего не устанавливает. Нужны также соответствующие права и тарифы провайдеров ([SingularityApp](research/providers/singularity.md), [Habitify](research/providers/habitify.md)).

## Устройство репозитория

| Путь | Что внутри |
| --- | --- |
| [`skills/`](skills/) | Единственный источник обоих скиллов: `SKILL.md`, справочные `references/` и `tools.json` |
| [`plugin.json`](plugin.json), [`.claude-plugin/`](.claude-plugin/), [`.agents/plugins/`](.agents/plugins/) | Manifests и каталоги для Hermes, Codex и Claude Code; все указывают на тот же `skills/` |
| [`CONTEXT.md`](CONTEXT.md), [`docs/adr/`](docs/adr/) | Словарь и принятые решения |
| [`research/`](research/README.md) | Основания: метод Дорофеева, исследования задач и привычек, контракты провайдеров и хостов, реестр источников |
| [`BACKLOG.md`](BACKLOG.md) | Отложенные возможности и явные исключения |

Репозиторий не содержит собственного кода: только инструкции, декларативные manifests, `tools.json` и документы ([ADR 0004](docs/adr/0004-no-custom-code.md)).

## Разработка

Правила для разработчиков и агентов — [AGENTS.md](AGENTS.md). Для локальной разработки: `claude --plugin-dir .` (после правок — `/reload-plugins`) или `codex plugin marketplace add .`.

Проверки из корня, без аккаунтов провайдеров:

```sh
claude plugin validate . --strict
claude plugin validate .claude-plugin/plugin.json --strict
hermes plugins validate . --json
hermes plugins doctor . --ci
git diff --check
```

[CI](.github/workflows/check.yml) выполняет те же статические проверки, кроме `hermes plugins doctor`, на закреплённых версиях инструментов. Валидаторы проверяют файлы и загрузку плагина; доступ к провайдерам, поведение модели и выполнение операций они не подтверждают.

## Лицензия и независимость

Оригинальные инструкции, manifests и документы — [MIT](LICENSE); сторонние материалы и названия — [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md). JediKit — независимый проект: он не связан и не одобрен Максимом Дорофеевым, SingularityApp, Habitify, Nous Research, Anthropic или OpenAI.
