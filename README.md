# JediKit

Два русскоязычных Agent Skill для личной продуктивности. `jedikit-tasks` ведёт задачи в SingularityApp по методу «Джедайских техник» Максима Дорофеева и исследованиям задач; `jedikit-habits` ведёт поведенческие эксперименты в Habitify на основе академических исследований. Решение остаётся за пользователем.

- **`jedikit-tasks`**: Capture, Triage, следующий шаг проекта, Daily open, Daily close, Weekly и Inbox debt. Фокус-лист составляется без календаря и проверки вместимости. Разделы и теги поддерживаются; kanban исключён ([ADR 0007](docs/adr/0007-no-kanban.md)).
- **`jedikit-habits`**: план эксперимента в заметке привычки, отметка, помощь при тяге и обзор эксперимента. Работа идёт с одной привычкой за раз; Safety-стоп направляет к специалисту. Off Mode включается в приложении Habitify: в API его нет, команды `off` нет.

Явная одиночная команда выполняется сразу. Изменение, предложенное агентом, требует Preview и подтверждения. Группа операций получает один Preview и одно подтверждение, выполняется последовательно и останавливается на первой ошибке с отчётом applied/unapplied. После каждой записи — Read-back. Расписание хоста выполняет только read-only проверки и приглашения; память агента хранит только настройки ([глоссарий](CONTEXT.md), [ADR](docs/adr/)).

## Состояние

Последняя опубликованная версия — GitHub prerelease [`v0.3.0-alpha.2`](https://github.com/ibelyasov/jedikit/releases/tag/v0.3.0-alpha.2). Контракт: только скиллы, подключения даёт хост ([ADR 0005](docs/adr/0005-one-source-host-connections.md)). Владелец пользуется скиллами и сообщает о проблемах; обязательного ручного runtime-гейта нет. Публикация версии (тег и GitHub release) остаётся отдельным решением владельца.

Штатные валидаторы проверяют файлы и загрузку в пределах своего контракта. Они не подтверждают доступ к провайдерам, поведение модели, выполнение операций или Read-back.

## Установка

| Хост | Что ставить | Задачи | Привычки |
| --- | --- | --- | --- |
| Hermes | плагин из репозитория | с инструментами SingularityApp | с инструментами Habitify |
| Claude Code | плагин из GitHub marketplace | с инструментами SingularityApp | с инструментами Habitify |
| Codex | плагин из GitHub marketplace | с инструментами SingularityApp | с инструментами Habitify |
| ChatGPT, Claude.ai | ZIP нужного скилла из релиза | с MCP SingularityApp | только с MCP, предоставляющим контракт Habitify |

Установка добавляет инструкции. Инструменты провайдеров хост предоставляет отдельно, как описано ниже.

### ChatGPT и Claude.ai

1. Скачайте `jedikit-tasks.zip` или `jedikit-habits.zip` со [страницы релиза](https://github.com/ibelyasov/jedikit/releases/tag/v0.3.0-alpha.2).
2. ChatGPT: **Skills → Create → Upload from your computer** ([справка](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)). Claude.ai: **Settings → Capabilities → Skills → Upload skill** ([справка](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)).
3. Подключите MCP средствами веб-хоста согласно разделу «Что должен дать хост».

В ChatGPT и Claude.ai `jedikit-habits` работает только при подключённом MCP с инструментами из его `tools.json`. Работа скиллов в веб-приложениях не проверялась.

## Один источник скиллов

`skills/` — единственное редактируемое дерево. Корневой [plugin.json](plugin.json) использует Agent Plugins 1.0: Hermes и Codex находят `skills/` по фиксированному пути, поэтому portable schema не содержит поля `skills`. OpenAI presentation находится в `extensions.com.openai`. [Claude manifest](.claude-plugin/plugin.json) указывает на тот же `./skills/`. Генерации, копий и `agents/openai.yaml` нет. Плагин не объявляет MCP и секреты ни для одного хоста ([ADR 0005](docs/adr/0005-one-source-host-connections.md)).

`AGENTS.md` — единый контракт разработчиков. По уточнению владельца от 2026-10-06 адаптер `CLAUDE.md` исключён: Claude Code читает `AGENTS.md` напрямую при отсутствии project `CLAUDE.md`. Native discovery документирован начиная с 2.1.277 ([досье Claude Code](research/platforms/claude.md), [официальный контракт](https://code.claude.com/docs/en/memory)). Это инструкции разработки в checkout; установленный плагин передаёт пользовательские процедуры через `skills/`.

## Что должен дать хост

JediKit задаёт машиночитаемый контракт в [`skills/jedikit-tasks/tools.json`](skills/jedikit-tasks/tools.json) и [`skills/jedikit-habits/tools.json`](skills/jedikit-habits/tools.json). Каждая запись содержит сервер у каждой записи (`singularity`; для Habitify чтения — `habitify_read`, записи — `habitify`), базовое имя без префикса хоста и `access: read | write`; у Habitify дополнительно указаны обязательные аргументы `required`. Формат — `version: 2`. Для задач ожидаются 35 операций, для привычек — все 23. Имена — внешний контракт: они меняются вместе со скиллом и отмечаются в release notes.

- **SingularityApp:** официальный hosted MCP `https://mcp.singularity-app.com/mcp` подключается средствами хоста. OAuth проводит хост. Агент использует предоставленные tools и их runtime schemas.
- **Habitify:** хост поднимает OpenAPI→MCP-адаптер или эквивалент с теми же именами операций. Официальный REST/OpenAPI v2 остаётся бизнес-контрактом; ключ хранится только у доверенного адаптера, агент получает операции. Официальный Habitify MCP не используется из-за неполного набора возможностей ([ADR 0001](docs/adr/0001-habitify-via-rest.md), [справка инструментов](skills/jedikit-habits/references/habitify-tools.md)).

На Hermes владельца это делает clanwright. JediKit не содержит реализацию подключений. Если необходимых инструментов нет, скилл называет недостающие базовые имена из своего `tools.json` и рекомендует подключить их на хосте; сам ничего не устанавливает и не настраивает.

Нужны соответствующие права и тарифы провайдеров. Условия доступа и наличие необходимых операций хост проверяет отдельно ([SingularityApp](research/providers/singularity.md), [Habitify](research/providers/habitify.md)). Наличие инструкций или подписки само по себе не подтверждает выполнение операций.

## Hermes

Устанавливайте корневой пакет с GitHub, закрепляя полный **40-символьный commit SHA JediKit**. SHA каждой версии указан на её [странице релиза](https://github.com/ibelyasov/jedikit/releases). Branch, tag и сокращённый SHA не подходят исследованному exact-ref контракту.

```sh
hermes plugins install ibelyasov/jedikit --ref <FULL_JEDIKIT_COMMIT_SHA> --enable
```

Для явного вызова получите точное qualified name через `skills_list`, затем `skill_view`; namespace зависит от установленного пакета. Для загрузки до начала чата подтверждён синтаксис:

```sh
hermes chat --skills '<EXACT_QUALIFIED_SKILL_NAME>'
```

Автоматический `/jedikit:...` для portable Hermes не обещается. Основания команд и границы проверки — в [досье Hermes](research/platforms/hermes.md).

## Claude Code

Из GitHub:

```sh
claude plugin marketplace add ibelyasov/jedikit
claude plugin install jedikit@jedikit
```

Для разработки в локальном checkout — `claude --plugin-dir .` на одну сессию; после правок `/reload-plugins`. Явные вызовы — `/jedikit:jedikit-tasks` и `/jedikit:jedikit-habits`. Инструменты даёт хост; установка плагина не подключает провайдеры. Основания команд и границы проверки — в [досье Claude Code](research/platforms/claude.md).

## Codex

Каталог [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json) указывает на корневой пакет без копирования `skills/`. Из GitHub с закреплённой версией:

```sh
codex plugin marketplace add ibelyasov/jedikit --ref v0.3.0-alpha.2
codex plugin add jedikit@jedikit
```

Для разработки — `codex plugin marketplace add .` из checkout. Установка использует cache: после обновления проверьте установленную ревизию в новой сессии. В `/skills` проверьте обнаруженные имена для явного вызова. Инструменты даёт хост. Основания команд — [досье Codex](research/platforms/codex.md), упаковка — [официальная документация](https://developers.openai.com/plugins/build/plugins).

## Разработка и проверки

Контракт агентов — [AGENTS.md](AGENTS.md), исходный scope пересборки — [#1](https://github.com/ibelyasov/jedikit/issues/1), текущие решения — [CONTEXT.md](CONTEXT.md) и [ADR](docs/adr/). Репозиторий содержит инструкции скиллов, декларативные manifests, `tools.json` и документы. Собственного кода, scripts, generators, сборщика, fake MCP и generated copies нет. Правки выполняются непосредственно в единственном `skills/` и manifests.

Официальные проверки из корня, без подключения аккаунтов провайдеров:

```sh
claude plugin validate . --strict
claude plugin validate .claude-plugin/plugin.json --strict
hermes plugins validate . --json
hermes plugins doctor . --ci
git diff --check
```

Directory validation выбирает marketplace первым; исследованная Claude Code 2.1.289 при наличии рядом plugin manifest проверяет также его компоненты. Вторая команда отдельно адресует plugin для явного отчёта. Hermes validate проверяет admission/security; doctor — discovery/load в изолированной проверке. Просматривайте warnings и inventory: успешный exit не подтверждает runtime. Native validator Codex в исследованной 0.160.0 не найден. Проверка изменений включает независимое ревью агентом; модельных прогонов нет.

[CI](.github/workflows/check.yml) выполняет официальные статические проверки без модельных вызовов и аккаунтов провайдеров. Версии и SHA инструментов закреплены в workflow. Сохраняйте читаемый вывод локальных проверок, команду, exit status и длительность в `.work/`; результаты GitHub CI оценивайте отдельно от локальных.

По решению владельца официальный Hermes Action закреплён на полном нерелизном commit `781334eea4b9225a3e194faf0c241d9afe218634`: [Action последнего исследованного релиза](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/.github/actions/plugin-validate/action.yml) использует wheel-установку, запрещённую его [build guard](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/setup.py). После релиза с исправлением pin следует обновить. [Исправленный Action](https://github.com/NousResearch/hermes-agent/blob/781334eea4b9225a3e194faf0c241d9afe218634/.github/actions/plugin-validate/action.yml) не экспортирует CLI для следующего шага, поэтому `doctor` выполняется локально при доступном Hermes.

В Action и CLI нет штатного ignore для `.work/`: локальный [scanner](https://github.com/NousResearch/hermes-agent/blob/781334eea4b9225a3e194faf0c241d9afe218634/tools/plugin_guard.py) читает и её; `.gitignore` не является scanner policy. В CI каталог отсутствует в чистом Git checkout. Локальные warnings сохраняйте, не удаляя evidence ради зелёного результата. Источники этого ограничения прочитаны 2026-10-06.

Исследования — [research/](research/README.md); отложенные направления — [BACKLOG.md](BACKLOG.md).

## Лицензия и независимость

Оригинальные инструкции, manifests и документы — [MIT](LICENSE); сторонние материалы и названия — [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md). JediKit — независимый проект: он не связан и не одобрен Максимом Дорофеевым, SingularityApp, Habitify, Nous Research, Anthropic или OpenAI. Права и условия провайдеров применяются отдельно.
