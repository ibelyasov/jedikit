# JediKit

Русскоязычные Agent Skill для Hermes Agent: что и как Hermes делает в личной жизни и работе владельца по методологии каждой темы. Сейчас это личная продуктивность — пять скиллов:

- **`jedikit-tasks`** ведёт задачи в [SingularityApp](https://singularity-app.com) по методу «Джедайских техник» Максима Дорофеева и исследованиям работы с задачами: Capture, Triage, следующий шаг проекта, Daily open, Daily close, Weekly и разбор Inbox debt. Фокус-лист составляется без календаря и проверки вместимости; разделы и теги поддерживаются, kanban — нет ([ADR 0007](docs/adr/0007-no-kanban.md)).
- **`jedikit-habits`** ведёт поведенческие эксперименты и ритуалы в [Habitify](https://habitify.me): план эксперимента в заметке привычки, отметки, помощь при тяге и обзоры. Ритуал объединяет привычки в Области Habitify; новое поведение проверяется одним экспериментом за раз. При признаках клинического риска Safety-стоп направляет к специалисту.
- **`jedikit-calendar`** ведёт личный Google Calendar: показывает день и неделю, создаёт, переносит и удаляет События, ведёт Распорядок по просьбе пользователя. Читает выбранные календари, пишет в один; рабочий Outlook не управляется.
- **`jedikit-planning`** составляет План дня поверх Фокус-листа: проверяет вместимость по свободным окнам и предлагает Брони для важных задач. Бронь ссылается на задачу, не закрывает её. Daily open остаётся в `jedikit-tasks`; План дня — следующая команда.
- **`jedikit`** по запросу объясняет возможности, словарь и карту команд, помогает выбрать скилл и следующий шаг. Навигатор только читает и не выполняет сценарии других скиллов.

Решение всегда остаётся за пользователем. Полная явная команда выполняется сразу, включая несколько названных записей на разных провайдерах. Одиночное предложение агента — одна строка и «да»; собранный агентом набор — один общий Preview и подтверждение. Безвозвратная потеря данных Habitify (удаление привычки, области, удаление/отмена отметок) всегда требует однострочного подтверждения. Однозначное удаление События выполняется сразу: оно остаётся 30 дней в корзине Google, восстановление доступно только в интерфейсе Google. Группа выполняется последовательно, останавливается на первой ошибке с отчётом applied/unverified/unapplied и не откатывается автоматически. После каждой записи — Read-back ([ADR 0014](docs/adr/0014-confirmations.md)). Фоновые запуски только читают, память агента хранит только настройки. Термины — в [CONTEXT.md](CONTEXT.md), решения — в [docs/adr/](docs/adr/).

Проект в ранней версии. Версии — теги и commit SHA на [странице релизов](https://github.com/ibelyasov/jedikit/releases); публикация версии — отдельное решение владельца.

## Установка

JediKit работает в [Hermes Agent](https://hermes-agent.nousresearch.com/). Установка добавляет только инструкции пяти скиллов; доступ к SingularityApp, Habitify и Google Calendar, а также внешний скилл `grill-me` настраиваются в Hermes отдельно — см. [«Что нужно от Hermes»](#что-нужно-от-hermes). Ставьте закреплённую ревизию: полный 40-символьный commit SHA каждой версии указан на её [странице релиза](https://github.com/ibelyasov/jedikit/releases).

### Каталог скиллов в `skills.external_dirs`

Основной способ: каталог `skills/` закреплённой ревизии JediKit подключается в конфигурации Hermes. Ревизию закрепляет источник каталога — checkout на нужном commit SHA или Nix input с этим SHA; у владельца так подключает clanwright.

```yaml
skills:
  external_dirs:
    - /path/to/jedikit/skills
```

Скиллы становятся обычными скиллами Hermes: имена `jedikit`, `jedikit-tasks`, `jedikit-habits`, `jedikit-calendar`, `jedikit-planning`; имя и начало описания каждого видны модели в индексе скиллов, явный вызов — `/jedikit-tasks` и т. д. Hermes не защищает внешний каталог от записи: держите его неизменяемым средствами системы, например в Nix store.

### Plugin install

```sh
hermes plugins install ibelyasov/jedikit --ref <FULL_JEDIKIT_COMMIT_SHA> --enable
```

`--ref` принимает только полный commit SHA. Скиллы получают имена вида `agent-plugin-jedikit-805a716c:jedikit-tasks` и не попадают в индекс скиллов system prompt, поэтому сами по запросу не подхватываются надёжно. Попросите Hermes найти JediKit через `skills_list` и загрузить нужный скилл через `skill_view` или загрузите скилл до начала чата: `hermes chat --skills '<точное имя>'`. Автоматические slash-команды для plugin-скиллов не гарантируются.

В обоих способах скиллы JediKit находят друг друга сами: соседний скилл загружается тем же видом имени, что и текущий. Подробности — [досье Hermes](research/platforms/hermes.md).

## Что нужно от Hermes

JediKit задаёт поведение скиллов и ожидания к инструментам. Hermes Agent загружает скиллы и вызывает инструменты. Всё остальное для Hermes обеспечивает потребитель — репозиторий, который подключает JediKit к Hermes (у владельца это clanwright): выбирает, подключает и реализует инструменты и MCP по этому контракту, отвечает за окружение и песочницу, доступы, расписания и доставку, кроме приглашений, которые скилл создаёт по просьбе пользователя, характер и самообучение агента, всё, что работает без модели, включение скиллов и развёртывание. Если сценарию нужен инструмент, которого у Hermes нет, JediKit добавляет ожидание в `tools.json` или в этот раздел. Новую потребность потребитель передаёт issue в этот репозиторий — рамкой задачи, а не спецификацией скилла ([ADR 0016](docs/adr/0016-consumer-boundary.md)).

Ожидаемые операции перечислены в [`skills/jedikit-tasks/tools.json`](skills/jedikit-tasks/tools.json) (35 операций), [`skills/jedikit-habits/tools.json`](skills/jedikit-habits/tools.json) (23 операции) и [`skills/jedikit-calendar/tools.json`](skills/jedikit-calendar/tools.json) (7 операций). У каждой операции указаны MCP-сервер, базовое имя и доступ `read` или `write`; у Habitify и Google Calendar ещё обязательные аргументы `required`. Агент вызывает их как `mcp__<server>__<base_name>`, где `-` и другие символы вне `[A-Za-z0-9_]` заменены на `_`.

**MCP-серверы:**

- **`singularity`** — официальный hosted MCP SingularityApp `https://mcp.singularity-app.com/mcp`; OAuth проводит Hermes.
- **`habitify_read`** и **`habitify`** — чтения и записи Habitify по официальному REST/OpenAPI v2 через доверенный адаптер. API-ключ хранится только у адаптера, агент его не видит. Скилл рассчитывает на такую форму ответа: ошибка — `isError: true` и HTTP-код в тексте как `status code NNN`; успех — без `isError`, тело ответа Habitify как JSON в тексте, пустой текст — успех без тела (`204`). Официальный Habitify MCP не подходит: в нём нет создания и изменения привычек, заметок и архивации ([ADR 0001](docs/adr/0001-habitify-via-rest.md), [справка инструментов](skills/jedikit-habits/references/tools.md)).
- **`google_calendar`** — Google Calendar с базовыми именами `list-calendars`, `list-events`, `get-event`, `get-current-time`, `create-event`, `update-event`, `delete-event`; у владельца это `nspady/google-calendar-mcp` `v2.7.0` ([ADR 0009](docs/adr/0009-separate-calendar-skill.md), [контракт инструментов](skills/jedikit-calendar/tools.json)).

**Toolsets и скиллы Hermes:**

- `skills` — `skills_list` и `skill_view` для загрузки скиллов и их `references/`.
- `clarify` — вопросы о недостающих полях и карточки согласия «Да»/«Нет» ([ADR 0013](docs/adr/0013-clarification.md), [ADR 0014](docs/adr/0014-confirmations.md)).
- `memory` — настройки скиллов, одна запись на скилл ([ADR 0006](docs/adr/0006-memory-holds-settings-only.md)).
- `cronjob` — только если нужны приглашения по расписанию ([ADR 0003](docs/adr/0003-no-unattended-writes.md)). Время задания считается по timezone профиля Hermes.
- Tool Search не обязателен: видимый MCP-инструмент скилл вызывает по имени, а при включённом Tool Search находит отложенные schemas через `tool_search` и `tool_describe` и вызывает через `tool_call`.
- Задание утренней сводки заводит потребитель, скиллы его не создают; toolsets cron должны включать чтения SingularityApp и Google Calendar. Фоновые запуски только читают.
- **`grill-me`** — внешний скилл для редкого глубокого уточнения намерения (есть среди официальных optional skills Hermes). Если его нет, JediKit называет требование и рекомендует установить его; своё интервью не проводит.

`jedikit-planning` использует `jedikit-tasks`, `jedikit-calendar`, `jedikit-habits` и их инструменты; своего провайдера и `tools.json` у него нет. `jedikit` требует остальные скиллы JediKit, работает только по запросу и своего `tools.json` не имеет.

Пакет не объявляет MCP-серверы и секреты ([ADR 0005](docs/adr/0005-hermes-plugin-host-connections.md)). Если нужных операций нет, скилл называет недостающие базовые имена и рекомендует подключить их в Hermes. Ни один скилл ничего не устанавливает и не настраивает подключения. Нужны также соответствующие права и тарифы провайдеров ([SingularityApp](research/providers/singularity.md), [Habitify](research/providers/habitify.md), [Google Calendar](research/providers/google-calendar.md)).

## Устройство репозитория

| Путь | Что внутри |
| --- | --- |
| [`skills/`](skills/) | Единственный источник пяти скиллов: `SKILL.md`, справочные `references/`; `tools.json` только у провайдерных скиллов |
| [`plugin.json`](plugin.json) | Portable manifest для `hermes plugins install`; указывает на тот же `skills/` |
| [`CONTEXT.md`](CONTEXT.md), [`docs/adr/`](docs/adr/) | Словарь и принятые решения |
| [`research/`](research/README.md) | Основания: метод Дорофеева, исследования задач, привычек и календаря, уточнение намерения и композиция скиллов, контракты провайдеров и Hermes, реестр источников |
| [`BACKLOG.md`](BACKLOG.md) | Отложенные возможности и явные исключения |

Репозиторий не содержит собственного кода: только инструкции, `plugin.json`, `tools.json` и документы ([ADR 0004](docs/adr/0004-no-custom-code.md)).

## Разработка

Правила для разработчиков и агентов — [AGENTS.md](AGENTS.md). Для локальной проверки скиллов укажите в `skills.external_dirs` каталог `skills/` своего checkout; изменения подхватываются в новой сессии Hermes.

Проверки из корня, без аккаунтов провайдеров:

```sh
hermes plugins validate . --json
hermes plugins doctor . --ci
git diff --check "$(git hash-object -t tree /dev/null)" HEAD  # всё дерево HEAD, как в CI
git diff --check HEAD                                         # незакоммиченные правки
```

[CI](.github/workflows/check.yml) проверяет пробелы во всём дереве HEAD против пустого дерева и выполняет `hermes plugins validate` официальным Action Hermes на закреплённой ревизии; `doctor` запускается локально. Валидаторы проверяют `skills/` как portable plugin: файлы, scanner и загрузку. Exit `0` не доказывает точный состав пяти скиллов — читайте отчёты и warnings. Доступ к провайдерам, поведение модели и выполнение операций они не подтверждают.

## Лицензия и независимость

Оригинальные инструкции, manifests и документы — [MIT](LICENSE); сторонние материалы и названия — [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md). JediKit — независимый проект: он не связан и не одобрен Максимом Дорофеевым, SingularityApp, Habitify, Google или Nous Research.
