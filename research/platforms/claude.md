# Claude Code: актуальный контракт JediKit

Дата исходного исследования: **2026-10-05**, консолидация — **2026-10-06**. По [issue #1](https://github.com/ibelyasov/jedikit/issues/1) и [ADR 0005](../../docs/adr/0005-one-source-host-connections.md) Claude Code поддерживается без обязательного runtime-гейта; acceptance host — Hermes на Nix-сервере владельца. Это исследование совместимости, а не runtime acceptance.

## Что является доказательством

- **Наблюдение 2026-10-05:** установленный Claude Code **2.1.289**, его `--version` и native help для `plugin`, `plugin validate`, `plugin eval`. Полный исходный код исполняемого файла не исследован: публичный репозиторий Anthropic не является открытой реализацией этого бинарника. Help подтверждает наличие команд, но не их выполнение с моделью. Официальный контекст версии и продукта: [PL-C-0](../sources.md).
- **Заявления vendor:** контракты ниже из официальной документации [PL-C-1](../sources.md), [PL-C-5](../sources.md), [PL-C-6](../sources.md), [PL-C-7](../sources.md); они помечены отдельно от локальных запусков.
- **Anecdote:** пользовательские отзывы и старые успешные сессии не использованы как доказательство текущего контракта.

## Layout, manifest и invocation

Документированный manifest — `.claude-plugin/plugin.json`; он необязателен, а при наличии единственное обязательное поле — `name`. Без него имя определяется marketplace entry либо именем директории при `--plugin-dir`. `skills/`, `agents/`, commands и остальные компоненты находятся в plugin root, вне `.claude-plugin/`. Поле `skills` принимает строку или массив директорий и добавляет пути к стандартному `skills/`, не заменяя его. Пути компонентов должны существовать и оставаться внутри plugin root. Для JediKit достаточно одного настоящего `skills/jedikit-tasks/SKILL.md` и `skills/jedikit-habits/SKILL.md`; дополнительные пути и копии не нужны. [PL-C-1](../sources.md)

Claude namespace даёт explicit invocation `/jedikit:jedikit-tasks` и `/jedikit:jedikit-habits`; description используется для выбора skill моделью. Это документированный UX, а не выполненный smoke test. [PL-C-2](../sources.md)

Платформа допускает `mcpServers` inline либо путь к JSON, стандартный `.mcp.json` в root; remote transport называется `http`, а `streamable-http` принимается как alias. По уточнённому [ADR 0005](../../docs/adr/0005-one-source-host-connections.md) JediKit сохраняет специальное исключение: корневой `.mcp.json` читает только Claude Code; в нём объявлен только публичный endpoint SingularityApp без секретов, а OAuth проводит Claude Code. Hermes и Codex этот файл не читают. Habitify остаётся REST v2 с ключом на хосте по [ADR 0001](../../docs/adr/0001-habitify-via-rest.md). Уточнение ADR взято из локального commit `149ce0d`, не из runtime-проверки или опубликованного релиза. [JEDIKIT-ADR0005-149CE0D](../sources.md), [PL-C-1](../sources.md), [PL-C-3](../sources.md), [PL-C-8](../sources.md)

**Сосуществование manifests:** документация регулярной загрузки описывает `.claude-plugin/plugin.json`. Документация eval разрешает также root `plugin.json`, но это не гарантия одинакового приоритета manifest у всех loaders. Практический вариант — отдельный небольшой Claude manifest и общий root `skills/`; полный межплатформенный вывод находится в [hermes.md](hermes.md). [PL-C-1](../sources.md), [PL-C-5](../sources.md)

## Local development

Локальная справка 2.1.289 подтверждает `claude --plugin-dir <path>`: флаг можно повторять, path может указывать на директорию или ZIP. Vendor описывает загрузку только в текущей сессии без установки/enabling в settings; изменения подхватываются `/reload-plugins`. Managed policy и конкурирующий одноимённый plugin могут влиять на загрузку. CLI invocation ниже — пример будущей проверки, в этой работе модель не запускалась. [PL-C-2](../sources.md), [PL-C-4](../sources.md)

```sh
claude --plugin-dir .
```

## Статический validator и CI

Native command, подтверждённый help установленного CLI:

```sh
claude plugin validate . --strict --json
```

По официальному контракту validator проверяет manifest и соответствующие component files/configuration, `--strict` превращает warnings в errors, `--json` сохраняет те же exit codes: `0` success, `1` validation failure, `2` validator error. Directory discovery начинается с `.claude-plugin/marketplace.json`, затем `.claude-plugin/plugin.json`; состав реально проверенных компонентов виден в report. Symlinks не обходятся, а пропуск даёт warning: linked skills tree не подходит для чистого strict gate. Это проверка файлов, не модельного поведения или MCP authentication. [PL-C-6](../sources.md)

**Независимо выполнено 2026-10-05:**

```sh
env CLAUDE_CONFIG_DIR=/private/tmp/jedikit-platform-research-claude-static \
  claude plugin validate . --strict --json
```

Exit `0`, `success: true`, target — текущий `.claude-plugin/plugin.json`, errors/warnings пусты. В report `contents: []`; это не inventory проверенных файлов. Дополнительно проверена временная декларативная fixture с portable root `plugin.json`, Claude manifest с `skills: "./skills"`, `mcpServers: "./mcp.json"` и MCP-файлом с portable `$schema` + `type: streamable-http`: strict validation прошла. После удаления skill description и подстановки неизвестного MCP transport эта же fixture дала exit `1`, warning по frontmatter и error по MCP type. Тем самым проверено, что validator действительно проверяет компоненты, а portable MCP JSON принимается статически. Runtime loading этим не доказан. [PL-C-1](../sources.md), [PL-C-6](../sources.md), [PL-C-8](../sources.md)

Изолированная config directory не содержала аккаунта; модель и MCP не запускались. Исследованный validator пригоден для статического CI без пользовательского аккаунта; packet tracing отсутствия сети не выполнялся. Временная fixture использовала только `https://example.com/mcp`, без обращения к адресу или provider data. Команда и смысл report соответствуют [PL-C-6](../sources.md).

## Native eval: определение cases и mocks

Vendor предоставляет `claude plugin eval` начиная с 2.1.269; при установленном Git требуется >=2.31. Suite — `evals/`, case — `prompt.md` с frontmatter и graders, либо `case.yaml` с `schema_version: "1.1"` и `name`. Native graders: `regex`, `tool_used`, `tool_order`, `file_exists`, `llm`, `baseline`. Четыре первых не вызывают judge model; custom-code graders отсутствуют. [PL-C-5](../sources.md)

Native MCP mocks — Markdown `evals/mocks/<server>/<tool>.md`, с override в case. Тело задаёт result, `expect` проверяет inputs; нарушение прерывает run со score `0`. `_tools.json` позволяет сохранить настоящие descriptions и schemas; без него mock schema permissive. Fixed mocks заменяют сервис без своего MCP server. [PL-C-5](../sources.md)

Следующие flags независимо обнаружены в локальном help 2.1.289; официальный контракт — [PL-C-5](../sources.md):

| Возможность | Точный смысл |
| --- | --- |
| `--mocks record` | Default; server без mock не запускается |
| `--allow-real-servers` | Разрешает реальные servers без mocks |
| `--mocks off` | Запускает реальные servers вместо mocks |
| `--scaffold` | Отдельно разрешает author-supplied Bash; default off |
| `--trust-plugin` | Убирает trust prompt для CI; не включает scaffold, gated tools или real servers |
| `--runs` | Default case.runs либо 3 |
| `--ablation` | При найденном plugin default `with-without` |
| `--threshold` | Default `1.0`; ниже него exit `1` |
| `--no-publish` | Сохраняет report локально |
| `--max-cost-usd` | Проверяется перед стартом run; уже запущенные runs могут превысить ceiling |
| `--concurrency` | 1–8 model runs |

**Стоимость:** agent runs обращаются к модели с обычными credentials и расходуют plan usage/API budget; judge и `type: agent` mocks добавляют model calls. Fixed MCP mocks убирают обращения к provider, но не делают eval offline. Default comparison выполняет оба arms; стоимость не является фиксированной ценой case. Пример ниже предназначен для будущего отдельно разрешённого model CI, не выполнялся. [PL-C-5](../sources.md)

```sh
claude plugin eval . --trust-plugin --mocks record --no-publish \
  --ablation none --runs 1 --max-cost-usd 1 --concurrency 1
```

**Вывод для ограничения «no custom code»:** prompt/grader/mock files позволяют проверить invocation, tool arguments/order и текстовый результат штатными средствами. Создание workspace через `context.scaffold_script` уже требует авторского Bash script и не подходит принятому ограничению. Stateful fake-provider model и произвольные machine assertions не возникают автоматически из Markdown mocks. Eval на Claude не доказывает поведение Hermes. [PL-C-5](../sources.md)

## AGENTS.md и CLAUDE.md

В текущем vendor contract прямой `AGENTS.md` поддерживается с 2.1.277. Default mode `claude-md-or-agents-md`: наличие `CLAUDE.md`, `.claude/CLAUDE.md` либо `CLAUDE.local.md` в cwd/предках выбирает CLAUDE instructions вместо AGENTS; пользовательский `~/.claude/CLAUDE.md` не подавляет AGENTS. Если этих project CLAUDE files нет, при старте читаются `AGENTS.md` и `.claude/AGENTS.md` в cwd/предках, вложенные AGENTS — при чтении файлов соответствующей директории. [PL-C-7](../sources.md)

`.agents/`, `AGENTS.local.md`, `AGENTS.override.md` не входят в этот discovery. Другие modes: `claude-md-and-agents-md`, `claude-md`, `managed-only`; builtin `agents-md` можно отключить. Ограничения Bedrock/telemetry относились к версиям до 2.1.281. `@AGENTS.md` из `CLAUDE.md` остаётся совместимым импортом без копии текста. Это существенно отличается от старого вывода «Claude не читает AGENTS.md», но загрузка в реальной сессии здесь не проверялась. [PL-C-7](../sources.md)

## Открытые риски и граница проверки

Не выполнены `--plugin-dir` runtime, install, eval, OAuth или tool discovery hosted MCP. Не проверены фактическая загрузка AGENTS и runtime priority двух manifests. Наличие CLI и успешная статическая проверка не подтверждают эти слои. Приняты один настоящий `skills/`, небольшие manifests и раздельные статический CI, model eval и Hermes acceptance. [PL-C-1](../sources.md), [PL-C-4](../sources.md), [PL-C-5](../sources.md), [PL-C-6](../sources.md), [PL-C-7](../sources.md)

**Открытый вопрос native mocks:** документация eval связывает MCP mocks с server names, объявленными тестируемым plugin. Уточнённый [ADR 0005](../../docs/adr/0005-one-source-host-connections.md) допускает Claude-only `.mcp.json` с публичным SingularityApp endpoint; эта декларация может предоставить требуемое имя сервера для native mocks. Фактическая mock inventory и выполнение eval с ней здесь не проверены. Habitify использует REST, и его покрытие штатными mocks остаётся неподтверждённым. Выбранное направление из [ADR 0004](../../docs/adr/0004-no-custom-code.md) сохраняется: нужно проверить штатный механизм, без собственного fake server, изменения host credentials или расширения утверждённого MCP-исключения. [JEDIKIT-ADR0005-149CE0D](../sources.md), [PL-C-5](../sources.md)

## Источники

Полные citations и объём доступа — в [реестре источников](../sources.md).

## Scheduling и различия поверхностей

Историческое исследование **2026-09-13** различало session-bound `/loop`/CronCreate, fresh remote Cloud tasks и Desktop local tasks. Текущая документация session scheduling описывает повтор до истечения срока (7 дней для recurring task) либо окончания сессии; это не долговечный daemon scheduler. Для remote/local scheduled surfaces отдельно проверяются место исполнения, доступный context, lifecycle, permissions и destination. Такие jobs здесь не создавались. [PL-C-9](../sources.md)

Claude Code plugin, Claude.ai upload и Skills API — разные deployment surfaces. В API skills используют Code Execution sandbox с его runtime/network restrictions; plugin install не подтверждает доступ к локальному диску, API deployment или аккаунтам другой поверхности. Ни API wrapper, ни отдельная generated package не входят в согласованный scope. [PL-C-10](../sources.md), [PL-C-13](../sources.md)

Marketplace регистрирует источник plugins, установка выбирает конкретный plugin. Claude host-specific dependencies/bundle не образуют universal skill-to-skill dependency contract. Для JediKit два независимых skills имеют одну package identity без router; каждый содержит необходимые operational references. Mixed request разделяется на workflows. [PL-C-11](../sources.md), [PL-C-14](../sources.md)

Для диагностики проверяются source/revision, manifest, inventory обоих namespaced skills, новая session и host MCP/tool schemas, затем поведение. Project trust, tool permission и согласие пользователя на запись различаются. Пользовательский OAuth не переносится при копировании repo. Unattended permission bypass не служит доказательством корректного preview/approval/read-back. По [ADR 0003](../../docs/adr/0003-no-unattended-writes.md) фоновые обзоры только читают. `disable-model-invocation: true` на платформе отключает автоматическую активацию; его нельзя добавлять как универсальную safety policy для skills с scheduled invocation. [PL-C-12](../sources.md)

Native memory не является общим хранилищем трёх hosts. По [ADR 0006](../../docs/adr/0006-memory-holds-settings-only.md) там только настройки; состояние обзоров не сохраняется. Не проверены Cloud/Desktop delivery и фактическая загрузка skills в каждой поверхности. Заявленная поддержка Claude Code остаётся без runtime-гейта; Claude behavioral eval не заменяет обязательную Hermes acceptance.
