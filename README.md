# JediKit

Пять русскоязычных Agent Skill для личной продуктивности:

- **`jedikit-tasks`** ведёт задачи в [SingularityApp](https://singularity-app.com) по методу «Джедайских техник» Максима Дорофеева и исследованиям работы с задачами: Capture, Triage, следующий шаг проекта, Daily open, Daily close, Weekly и разбор Inbox debt. Фокус-лист составляется без календаря и проверки вместимости; разделы и теги поддерживаются, kanban — нет ([ADR 0007](docs/adr/0007-no-kanban.md)).
- **`jedikit-habits`** ведёт поведенческие эксперименты и ритуалы в [Habitify](https://habitify.me): план эксперимента в заметке привычки, отметки, помощь при тяге и обзоры. Ритуал объединяет привычки в Области Habitify; новое поведение проверяется одним экспериментом за раз. При признаках клинического риска Safety-стоп направляет к специалисту.
- **`jedikit-calendar`** ведёт личный Google Calendar: показывает день и неделю, создаёт, переносит и удаляет События, ведёт Распорядок по просьбе пользователя. Читает выбранные календари, пишет в один; рабочий Outlook не управляется.
- **`jedikit-planning`** составляет План дня поверх Фокус-листа: проверяет вместимость по свободным окнам и предлагает Брони для важных задач. Бронь ссылается на задачу, не закрывает её. Daily open остаётся в `jedikit-tasks`; План дня — следующая команда.
- **`jedikit`** по запросу объясняет возможности, словарь и карту команд, помогает выбрать скилл и следующий шаг. Навигатор только читает и не выполняет сценарии других скиллов.

Решение всегда остаётся за пользователем. Полная явная команда выполняется сразу, включая несколько названных записей на разных провайдерах. Одиночное предложение агента — одна строка и «да»; собранный агентом набор — один общий Preview и подтверждение. Безвозвратная потеря данных Habitify (удаление привычки, области, удаление/отмена отметок) всегда требует однострочного подтверждения. Однозначное удаление События выполняется сразу: оно остаётся 30 дней в корзине Google, восстановление доступно только в интерфейсе Google. Группа выполняется последовательно, останавливается на первой ошибке с отчётом applied/unapplied и не откатывается автоматически. После каждой записи — Read-back ([ADR 0014](docs/adr/0014-confirmations.md)). Фоновые запуски только читают, память агента хранит только настройки. Термины — в [CONTEXT.md](CONTEXT.md), решения — в [docs/adr/](docs/adr/).

Проект в ранней версии. Доступные сборки — на [странице релизов](https://github.com/ibelyasov/jedikit/releases); публикация версии — отдельное решение владельца.

## Установка

| Хост | Что ставить |
| --- | --- |
| [Claude Code](#claude-code) | плагин из GitHub marketplace |
| [Codex](#codex) | плагин из GitHub marketplace |
| [Hermes](#hermes) | плагин из репозитория по commit SHA |
| [ChatGPT, Claude.ai](#chatgpt-и-claudeai) | ZIP нужного скилла из релиза |

Установка добавляет только инструкции. Выберите опубликованную ревизию с нужным набором скиллов; локальный checkout подключается по [инструкции для разработки](#разработка). Доступ к SingularityApp, Habitify и Google Calendar, а также внешний скилл `grill-me` хост предоставляет отдельно — см. [«Что должен дать хост»](#что-должен-дать-хост).

### Claude Code

```sh
claude plugin marketplace add ibelyasov/jedikit
claude plugin install jedikit@jedikit
```

Явные вызовы: `/jedikit:jedikit-tasks`, `/jedikit:jedikit-habits`, `/jedikit:jedikit-calendar`, `/jedikit:jedikit-planning`, `/jedikit:jedikit`. Подробности — [досье Claude Code](research/platforms/claude.md).

### Codex

```sh
codex plugin marketplace add ibelyasov/jedikit --ref <JEDIKIT_REF>
codex plugin add jedikit@jedikit
```

Замените `<JEDIKIT_REF>` опубликованным тегом или commit SHA. Codex устанавливает плагин в cache: после обновления проверьте установленную ревизию в новой сессии, а имена для явного вызова — в `/skills`. Подробности — [досье Codex](research/platforms/codex.md).

### Hermes

Hermes принимает только полный 40-символьный commit SHA; SHA каждой версии указан на её [странице релиза](https://github.com/ibelyasov/jedikit/releases).

```sh
hermes plugins install ibelyasov/jedikit --ref <FULL_JEDIKIT_COMMIT_SHA> --enable
```

Точное имя скилла для явного вызова дают `skills_list` и `skill_view`; загрузить скилл до начала чата — `hermes chat --skills '<EXACT_QUALIFIED_SKILL_NAME>'`. Подробности — [досье Hermes](research/platforms/hermes.md).

### ChatGPT и Claude.ai

1. Подготовьте ZIP каталога нужного скилла из `skills/` с `SKILL.md`, `references/` и `tools.json` при наличии; готовые архивы доступны на [странице релизов](https://github.com/ibelyasov/jedikit/releases). Для `jedikit-planning` нужны также три провайдерных скилла, для `jedikit` — остальные скиллы JediKit.
2. ChatGPT: **Skills → Create → Upload from your computer** ([справка](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)). Claude.ai: **Settings → Capabilities → Skills → Upload skill** ([справка](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)).
3. Подключите MCP средствами веб-хоста.

Провайдерным скиллам в веб-приложениях нужны операции хоста из их `tools.json`. Работа скиллов в веб-приложениях не проверялась.

## Что должен дать хост

Ожидаемые операции перечислены в [`skills/jedikit-tasks/tools.json`](skills/jedikit-tasks/tools.json) (35 операций), [`skills/jedikit-habits/tools.json`](skills/jedikit-habits/tools.json) (23 операции) и [`skills/jedikit-calendar/tools.json`](skills/jedikit-calendar/tools.json) (7 операций). У каждой операции указаны сервер, базовое имя без префикса хоста и доступ `read` или `write`; у Habitify и Google Calendar ещё обязательные аргументы `required`.

- **SingularityApp** — официальный hosted MCP `https://mcp.singularity-app.com/mcp`, подключённый средствами хоста; OAuth проводит хост.
- **Habitify** — операции по официальному REST/OpenAPI v2, которые предоставляет доверенный адаптер хоста: чтения на сервере `habitify_read`, записи — на `habitify`. API-ключ хранится только у адаптера, агент его не видит. Официальный Habitify MCP не подходит: в нём нет создания и изменения привычек, заметок и архивации ([ADR 0001](docs/adr/0001-habitify-via-rest.md), [справка инструментов](skills/jedikit-habits/references/habitify-tools.md)).
- **Google Calendar** — сервер хоста `google_calendar` с базовыми именами `list-calendars`, `list-events`, `get-event`, `get-current-time`, `create-event`, `update-event`, `delete-event`. На Hermes владельца clanwright подключает `nspady/google-calendar-mcp` `v2.7.0`; авторизация остаётся у хоста ([ADR 0009](docs/adr/0009-separate-calendar-skill.md), [контракт инструментов](skills/jedikit-calendar/tools.json)).
- **`grill-me`** — внешний скилл хоста для редкого глубокого уточнения намерения. Если его нет, JediKit называет требование и рекомендует установить его средствами хоста; своё интервью не проводит ([ADR 0013](docs/adr/0013-clarification.md)).

`jedikit-planning` использует `jedikit-tasks`, `jedikit-calendar`, `jedikit-habits` и их инструменты; своего провайдера и `tools.json` у него нет. `jedikit` требует остальные скиллы JediKit, работает только по запросу и своего `tools.json` не имеет.

Плагин не объявляет MCP-серверы и секреты ни для одного хоста ([ADR 0005](docs/adr/0005-one-source-host-connections.md)). Если нужных операций нет, скилл называет недостающие базовые имена и рекомендует подключить их средствами хоста. Ни один скилл ничего не устанавливает и не настраивает подключения. Нужны также соответствующие права и тарифы провайдеров ([SingularityApp](research/providers/singularity.md), [Habitify](research/providers/habitify.md), [Google Calendar](research/providers/google-calendar.md)).

## Устройство репозитория

| Путь | Что внутри |
| --- | --- |
| [`skills/`](skills/) | Единственный источник пяти скиллов: `SKILL.md`, справочные `references/`; `tools.json` только у провайдерных скиллов |
| [`plugin.json`](plugin.json), [`.claude-plugin/`](.claude-plugin/), [`.agents/plugins/`](.agents/plugins/) | Manifests и каталоги для Hermes, Codex и Claude Code; все указывают на тот же `skills/` |
| [`CONTEXT.md`](CONTEXT.md), [`docs/adr/`](docs/adr/) | Словарь и принятые решения |
| [`research/`](research/README.md) | Основания: метод Дорофеева, исследования задач, привычек и календаря, уточнение намерения и композиция скиллов, контракты провайдеров и хостов, реестр источников |
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

Оригинальные инструкции, manifests и документы — [MIT](LICENSE); сторонние материалы и названия — [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md). JediKit — независимый проект: он не связан и не одобрен Максимом Дорофеевым, SingularityApp, Habitify, Google, Nous Research, Anthropic или OpenAI.
