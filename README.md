# JediKit

Два русскоязычных Agent Skill для личной продуктивности. `jedikit-tasks` ведёт задачи в SingularityApp по методу «Джедайских техник» Максима Дорофеева и исследованиям задач; `jedikit-habits` ведёт поведенческие эксперименты в Habitify на основе академических исследований. Решение остаётся за пользователем.

- **`jedikit-tasks`**: Capture, Triage, следующий шаг проекта, Daily open, Daily close, Weekly и Inbox debt. Фокус-лист составляется без календаря и проверки вместимости. Разделы и теги поддерживаются; kanban исключён ([ADR 0007](docs/adr/0007-no-kanban.md)).
- **`jedikit-habits`**: план эксперимента в заметке привычки, отметка, помощь при тяге и обзор эксперимента. Работа идёт с одной привычкой за раз; Safety-стоп направляет к специалисту. Off Mode включается в приложении Habitify: в API его нет, команды `off` нет.

Явная одиночная команда выполняется сразу. Изменение, предложенное агентом, требует Preview и подтверждения. Группа операций получает один Preview и одно подтверждение, выполняется последовательно и останавливается на первой ошибке с отчётом applied/unapplied. После записи — Read-back. Расписание хоста выполняет только read-only проверки и приглашения; память агента хранит только настройки ([спецификация #1](https://github.com/ibelyasov/jedikit/issues/1), [глоссарий](CONTEXT.md)).

## Состояние 0.3.0-alpha.1

Версия опубликована как GitHub prerelease [`v0.3.0-alpha.1`](https://github.com/ibelyasov/jedikit/releases/tag/v0.3.0-alpha.1): её можно ставить, но **обязательная приёмка — Hermes на Nix-сервере владельца** по [чек-листу](docs/acceptance.md) — ещё не пройдена. Claude Code и Codex входят в заявленную поддержку без runtime-гейта. Статические валидаторы проверяют файлы; они не подтверждают загрузку в сессии, доступ к провайдерам, выполнение операций или Read-back.

## Установка

| Хост | Что ставить | Задачи | Привычки |
| --- | --- | --- | --- |
| Hermes | плагин из репозитория | да | да |
| Claude Code | плагин из GitHub marketplace | да | да |
| Codex | плагин из GitHub marketplace | да | да |
| ChatGPT, Claude.ai | ZIP скилла из релиза | да, с коннектором SingularityApp | нет |

`jedikit-habits` вызывает Habitify REST через `curl` и ключ из secret-окружения. В веб-приложениях ChatGPT и Claude.ai нет места для такого секрета, поэтому там поддерживается только `jedikit-tasks`. Команды для каждого хоста — ниже.

### ChatGPT и Claude.ai

1. Скачайте `jedikit-tasks.zip` со [страницы релиза](https://github.com/ibelyasov/jedikit/releases/tag/v0.3.0-alpha.1).
2. ChatGPT: **Skills → Create → Upload from your computer** ([справка](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)). Claude.ai: **Settings → Capabilities → Skills → Upload skill** ([справка](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)).
3. Подключите SingularityApp как коннектор приложения с адресом `https://mcp.singularity-app.com/mcp` и пройдите OAuth.

Работа скилла в веб-приложениях не проверялась.

`AGENTS.md` — единый контракт разработчиков. По уточнению владельца от 2026-10-06 адаптер `CLAUDE.md` исключён: Claude Code читает `AGENTS.md` напрямую при отсутствии project `CLAUDE.md`. Native discovery документирован начиная с 2.1.277; проверка этой работы использует 2.1.289 ([досье Claude Code](research/platforms/claude.md), [официальный контракт](https://code.claude.com/docs/en/memory)). Это инструкции разработки в checkout; установленный плагин передаёт пользовательские процедуры через `skills/`.

Основания команд: досье [Hermes](research/platforms/hermes.md), [Claude Code](research/platforms/claude.md), [Codex](research/platforms/codex.md) от 2026-10-05. Они исследуют Hermes 0.21.5, Claude Code 2.1.289 и Codex CLI 0.160.0. Справки установленных Claude/Codex и первичные документы сверены 2026-10-06. Установка нового JediKit, OAuth и работа провайдеров на этих хостах **не проверены**.

## Один источник, отдельные подключения

`skills/` — единственное редактируемое дерево. Корневой [plugin.json](plugin.json) использует Agent Plugins 1.0: Hermes и Codex находят `skills/` по фиксированному пути, поэтому portable schema не содержит поля `skills`. OpenAI presentation находится в `extensions.com.openai`. [Claude manifest](.claude-plugin/plugin.json) указывает на тот же `./skills/`. Генерации, копий и `agents/openai.yaml` нет.

**Почему остаётся `.mcp.json`:** это декларация только для Claude Code — официальный endpoint SingularityApp, transport `http`, без секретов. Она позволяет Claude загрузить plugin MCP и использовать его имя в штатных eval mocks. Hermes и portable Codex читают только `mcp.json`, которого здесь нет; `.mcp.json` не служит им fallback. Так пакет не объявляет MCP и секреты для Hermes/Codex и не создаёт в Hermes дубли без OAuth. Это явное Claude-исключение к общему правилу подключений на хосте ([ADR 0005](docs/adr/0005-one-source-host-connections.md), [досье Hermes](research/platforms/hermes.md)). Декларация endpoint не авторизует аккаунт.

`jedikit-tasks` использует только официальный hosted MCP SingularityApp: `https://mcp.singularity-app.com/mcp`. `jedikit-habits` использует только официальный REST API v2 Habitify: `https://api.habitify.me/v2`, заголовок `X-API-Key` из `HABITIFY_API_KEY` ([ADR 0001](docs/adr/0001-habitify-via-rest.md)). Habitify MCP не подключается. Нужны соответствующие права и тарифы провайдеров: SingularityApp заявляет Pro/Elite, для Habitify REST ADR указывает Pro. Точные условия доступа проверяются владельцем ([SingularityApp](research/providers/singularity.md), [Habitify](research/providers/habitify.md)).

На каждом хосте владелец передаёт `HABITIFY_API_KEY` через своё secret-окружение процессу агента и его штатному средству HTTP-запросов. Значение ключа не помещается в prompt, manifests, `config.toml`, коммиты, историю команд или вывод. Способ доставки секрета и доступность штатного HTTP-инструмента проверяются на конкретном хосте; собственного wrapper, MCP-сервера или runtime у JediKit нет.

## Контракт инструментов хоста

[`skills/jedikit-tasks/tools.json`](skills/jedikit-tasks/tools.json) и [`skills/jedikit-habits/tools.json`](skills/jedikit-habits/tools.json) — машиночитаемый список инструментов, которые скилл ожидает от хоста. Каждая запись содержит ID сервера (`singularity`, `habitify`), базовое имя без префикса хоста и `access: read | write`; у Habitify дополнительно указаны обязательные аргументы API (`required`). Подключения реализует хост. На Hermes владельца это делает clanwright и сверяет `tools.include` с файлами закреплённого релиза: расхождение даёт красную проверку.

В 0.3.0-alpha.1 добавлены только эти списки. Скиллы не изменились с 0.2.1: `jedikit-habits` пока вызывает REST через `curl`, переход на инструменты из списка будет в следующем релизе.

## Hermes на сервере владельца

Устанавливайте корневой пакет с GitHub, закрепляя полный **40-символьный commit SHA JediKit**. SHA каждой версии указан на её [странице релиза](https://github.com/ibelyasov/jedikit/releases). Branch, tag и сокращённый SHA не подходят проверенному exact-ref контракту.

```sh
hermes plugins install ibelyasov/jedikit --ref <FULL_JEDIKIT_COMMIT_SHA> --enable
```

SingularityApp настраивается отдельно на хосте. Эти команды выполняет владелец; `add` запускает OAuth и записывает host configuration:

```sh
hermes mcp add singularity --url https://mcp.singularity-app.com/mcp --auth oauth
hermes mcp test singularity
```

Syntax `--url` подтверждён [CLI parser Hermes 0.21.5](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/subcommands/mcp.py#L23). `test` проверяет соединение/discovery, а действия с данными требуют отдельной приёмки. Передайте `HABITIFY_API_KEY` в secret-окружение службы Hermes по правилам выше; конфигурация Nix-сервера и подключение аккаунтов находятся вне этого репозитория.

Минимальные toolsets для задач — `tasks,projects,meta,tags`. Их полноту и исключение `habits`, `kanban`, `time_stat` нужно подтвердить discovery на Hermes; текущие данные не позволяют обещать точное соответствие семейств URL-фильтру `?toolsets=`. Batch не используется. Root install scanner ещё требуется проверить на финальном составе репозитория; обход scanner не предлагается.

Для явного вызова получите точное qualified name через `skills_list`, затем `skill_view`; namespace зависит от установленного пакета. Для загрузки до начала чата подтверждён синтаксис:

```sh
hermes chat --skills '<EXACT_QUALIFIED_SKILL_NAME>'
```

Автоматический `/jedikit:...` для portable Hermes не обещается.

## Claude Code

Из GitHub:

```sh
claude plugin marketplace add ibelyasov/jedikit
claude plugin install jedikit@jedikit
```

Для разработки в локальном checkout — `claude --plugin-dir .` на одну сессию; после правок `/reload-plugins`. Явные вызовы — `/jedikit:jedikit-tasks` и `/jedikit:jedikit-habits`.

При загрузке плагина `.mcp.json` объявляет сервер `plugin:jedikit:singularity`. Авторизуйте именно его через `/mcp` в сессии Claude Code; имя проверьте в списке. [Официальная MCP-документация](https://code.claude.com/docs/en/mcp#plugin-provided-mcp-servers) описывает scoped names. Установка плагина сама по себе не завершает OAuth.

При запуске из корня checkout тот же `.mcp.json` может также предложить project-scoped `singularity`. Для plugin-пути отклоните подключение project server или отключите его через `/mcp`; оставьте только `plugin:jedikit:singularity`. Не рассчитывайте на автоматическое объединение этих имён: риск двух соединений следует из [project scope](https://code.claude.com/docs/en/mcp#project-scope) и plugin scope, runtime deduplication здесь не проверялась.

Альтернатива — native подключение на хосте через `claude mcp`. В этом случае отключите plugin server через `/mcp`, чтобы использовать одно соединение:

```sh
claude mcp add --transport http singularity https://mcp.singularity-app.com/mcp
claude mcp login singularity
```

Форма подтверждена справкой 2.1.289 и [MCP-документацией](https://code.claude.com/docs/en/mcp). Ключ Habitify передайте в окружение Claude и его HTTP-инструмента. OAuth, implicit routing и REST-действия этой версии JediKit в Claude Code не проверены.

## Codex

Каталог [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json) указывает на корневой пакет без копирования `skills/`. Из GitHub с закреплённой версией:

```sh
codex plugin marketplace add ibelyasov/jedikit --ref v0.3.0-alpha.1
codex plugin add jedikit@jedikit
```

Для разработки — `codex plugin marketplace add .` из checkout. Команды подтверждены досье Codex и справкой 0.160.0. Установка использует cache: после обновления проверьте установленную ревизию в новой сессии. Порядок marketplace и OpenAI extension описан в [официальной документации](https://developers.openai.com/plugins/build/plugins).

SingularityApp добавляется в личный `~/.codex/config.toml` или trusted project `.codex/config.toml`, без токенов:

```toml
[mcp_servers.singularity]
url = "https://mcp.singularity-app.com/mcp"
```

Затем владелец выполняет OAuth:

```sh
codex mcp login singularity
```

Форма подтверждена справкой 0.160.0 и [официальной MCP-документацией](https://developers.openai.com/codex/mcp). Передайте ключ Habitify через окружение процесса Codex и его HTTP-инструмента; если environment policy фильтрует переменные, разрешите `HABITIFY_API_KEY` на хосте. Не задавайте его как bearer token SingularityApp. В `/skills` проверьте обнаруженные имена для явного вызова. Загрузка плагина, OAuth и доступность ключа из HTTP-инструмента в Codex пока не проверены.

## Разработка и проверки

Контракт агентов — [AGENTS.md](AGENTS.md), решения — [#1](https://github.com/ibelyasov/jedikit/issues/1), [CONTEXT.md](CONTEXT.md), [ADR](docs/adr/). Репозиторий содержит инструкции скиллов, manifests и документы. Собственного кода, scripts, generators, сборщика, fake MCP и generated copies нет. Правки выполняются непосредственно в единственном `skills/` и небольших manifests.

Официальные проверки из корня, без подключения аккаунтов провайдеров:

```sh
claude plugin validate . --strict
claude plugin validate .claude-plugin/plugin.json --strict
hermes plugins validate . --json
hermes plugins doctor . --ci
git diff --check
```

Directory validation выбирает marketplace первым; в Claude Code 2.1.289 при наличии рядом plugin manifest проверяются также его компоненты. Вторая команда отдельно адресует plugin для явного отчёта. Hermes validate проверяет admission/security; doctor — discovery/load в изолированной проверке. Просматривайте warnings и inventory: успешный exit не подтверждает runtime. Native validator Codex в исследованной 0.160.0 не найден.

[CI](.github/workflows/check.yml) выполняет официальные статические проверки без модельных вызовов и аккаунтов провайдеров. Версии и SHA инструментов закреплены в workflow. Сохраняйте читаемый вывод локальных проверок, команду, exit status и длительность в `.work/`; результаты GitHub CI оценивайте отдельно от локальных.

По решению владельца официальный Hermes Action закреплён на полном нерелизном commit `781334eea4b9225a3e194faf0c241d9afe218634`: [Action последнего проверенного релиза](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/.github/actions/plugin-validate/action.yml) использует wheel-установку, запрещённую его [build guard](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/setup.py). После релиза с исправлением pin следует обновить. [Исправленный Action](https://github.com/NousResearch/hermes-agent/blob/781334eea4b9225a3e194faf0c241d9afe218634/.github/actions/plugin-validate/action.yml) не экспортирует CLI для следующего шага, поэтому `doctor` выполняется локально.

В Action и CLI нет штатного ignore для `.work/`: локальный [scanner](https://github.com/NousResearch/hermes-agent/blob/781334eea4b9225a3e194faf0c241d9afe218634/tools/plugin_guard.py) читает и её; `.gitignore` не является scanner policy. В CI каталог отсутствует в чистом Git checkout. Локальные caution/warnings сохраняйте, не удаляя evidence ради зелёного результата. Перечисленные первичные источники прочитаны 2026-10-06.

Перед релизом используйте [поведенческие evals](evals/README.md): документированный формат `claude plugin eval`, фиксированные Markdown MCP mocks SingularityApp и штатные graders. Habitify REST через `curl` не имеет документированного native mock: его cases проверяют ответы и безопасность без HTTP-записей. Проверку записи и Read-back обеспечивает [чек-лист Hermes](docs/acceptance.md). Отдельной проверки формата evals без модели в справке Claude Code 2.1.289 нет; `plugin validate` не подтверждает формат suite.

Модельный запуск требует разрешённого account/budget: mocks исключают обращения к провайдерам, но agent и LLM graders расходуют usage. Команда с ограничением числа запусков и cost ceiling находится в `evals/README.md`; ceiling может быть превышен уже начатым run. Не меняйте аккаунт ради проверки и не включайте реальные MCP servers или scaffold. Приёмку на Nix-сервере выполняет владелец по `docs/acceptance.md`, фиксируя наблюдаемые результаты в [#6](https://github.com/ibelyasov/jedikit/issues/6).

Исследования — [research/](research/README.md); отложенные направления — [BACKLOG.md](BACKLOG.md). Старые alpha-проверки не доказывают приёмку 0.2.0.

## Лицензия и независимость

Оригинальные инструкции, manifests и документы — [MIT](LICENSE); сторонние материалы и названия — [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md). JediKit — независимый проект: он не связан и не одобрен Максимом Дорофеевым, SingularityApp, Habitify, Nous Research, Anthropic или OpenAI. Права и условия провайдеров применяются отдельно.
