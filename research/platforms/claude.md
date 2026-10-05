# Claude Code: актуальный контракт JediKit

Дата исследования: **2026-10-05**. Старый `research/platform-claude.md` — только исторический контекст. Решение владельца: Claude Code входит в заявленную поддержку; обязательный acceptance host — Hermes на Nix-сервере. Это исследование совместимости, а не runtime acceptance.

## Что является доказательством

- **Независимая проверка:** установленный Claude Code **2.1.289**, его `--version` и native help для `plugin`, `plugin validate`, `plugin eval`. Полный исходный код исполняемого файла не исследован: публичный репозиторий Anthropic не является открытой реализацией этого бинарника. Help подтверждает наличие команд, но не их выполнение с моделью. Официальный контекст версии и продукта: [C0].
- **Заявления vendor:** контракты ниже из текущей официальной документации [C1–C7]; они помечены отдельно от локальных запусков.
- **Anecdote:** пользовательские отзывы и старые успешные сессии не использованы как доказательство текущего контракта.

## Layout, manifest и invocation

Документированный manifest — `.claude-plugin/plugin.json`; он необязателен, а при наличии единственное обязательное поле — `name`. Без него имя определяется marketplace entry либо именем директории при `--plugin-dir`. `skills/`, `agents/`, commands и остальные компоненты находятся в plugin root, вне `.claude-plugin/`. Поле `skills` принимает строку или массив директорий и добавляет пути к стандартному `skills/`, не заменяя его. Пути компонентов должны существовать и оставаться внутри plugin root. Для JediKit достаточно одного настоящего `skills/jedikit-tasks/SKILL.md` и `skills/jedikit-habits/SKILL.md`; дополнительные пути и копии не нужны. [C1]

Claude namespace даёт explicit invocation `/jedikit:jedikit-tasks` и `/jedikit:jedikit-habits`; description используется для выбора skill моделью. Это документированный UX, а не выполненный smoke test. [C2]

`mcpServers` в Claude manifest допускает inline config либо путь к JSON; стандартный файл — `.mcp.json` в root. Официальный Claude transport для remote Streamable HTTP называется `http`, причём `streamable-http` принимается как alias в JSON configuration. Поэтому Claude adapter может явно указать `"mcpServers": "./mcp.json"`. [C1][C3][C8]

**Сосуществование manifests:** документация регулярной загрузки описывает `.claude-plugin/plugin.json`. Документация eval разрешает также root `plugin.json`, но это не гарантия одинакового приоритета manifest у всех loaders. Практический вариант — отдельный небольшой Claude manifest и общий root `skills/`; полный межплатформенный вывод находится в [hermes.md](hermes.md). [C1][C5]

## Local development

Локальная справка 2.1.289 подтверждает `claude --plugin-dir <path>`: флаг можно повторять, path может указывать на директорию или ZIP. Vendor описывает загрузку только в текущей сессии без установки/enabling в settings; изменения подхватываются `/reload-plugins`. Managed policy и конкурирующий одноимённый plugin могут влиять на загрузку. CLI invocation ниже — пример будущей проверки, в этой работе модель не запускалась. [C2][C4]

```sh
claude --plugin-dir .
```

## Статический validator и CI

Native command, подтверждённый help установленного CLI:

```sh
claude plugin validate . --strict --json
```

По официальному контракту validator проверяет manifest и соответствующие component files/configuration, `--strict` превращает warnings в errors, `--json` сохраняет те же exit codes: `0` success, `1` validation failure, `2` validator error. Directory discovery начинается с `.claude-plugin/marketplace.json`, затем `.claude-plugin/plugin.json`; состав реально проверенных компонентов виден в report. Symlinks не обходятся, а пропуск даёт warning: linked skills tree не подходит для чистого strict gate. Это проверка файлов, не модельного поведения или MCP authentication. [C6]

**Независимо выполнено 2026-10-05:**

```sh
env CLAUDE_CONFIG_DIR=/private/tmp/jedikit-platform-research-claude-static \
  claude plugin validate . --strict --json
```

Exit `0`, `success: true`, target — текущий `.claude-plugin/plugin.json`, errors/warnings пусты. В report `contents: []`; это не inventory проверенных файлов. Дополнительно проверена временная декларативная fixture с portable root `plugin.json`, Claude manifest с `skills: "./skills"`, `mcpServers: "./mcp.json"` и MCP-файлом с portable `$schema` + `type: streamable-http`: strict validation прошла. После удаления skill description и подстановки неизвестного MCP transport эта же fixture дала exit `1`, warning по frontmatter и error по MCP type. Тем самым проверено, что validator действительно проверяет компоненты, а portable MCP JSON принимается статически. Runtime loading этим не доказан. [C1][C6][C8]

Изолированная config directory не содержала аккаунта; модель и MCP не запускались. Исследованный validator пригоден для статического CI без пользовательского аккаунта; packet tracing отсутствия сети не выполнялся. Временная fixture использовала только `https://example.com/mcp`, без обращения к адресу или provider data. Команда и смысл report соответствуют [C6].

## Native eval: определение cases и mocks

Vendor предоставляет `claude plugin eval` начиная с 2.1.269; при установленном Git требуется >=2.31. Suite — `evals/`, case — `prompt.md` с frontmatter и graders, либо `case.yaml` с `schema_version: "1.1"` и `name`. Native graders: `regex`, `tool_used`, `tool_order`, `file_exists`, `llm`, `baseline`. Четыре первых не вызывают judge model; custom-code graders отсутствуют. [C5]

Native MCP mocks — Markdown `evals/mocks/<server>/<tool>.md`, с override в case. Тело задаёт result, `expect` проверяет inputs; нарушение прерывает run со score `0`. `_tools.json` позволяет сохранить настоящие descriptions и schemas; без него mock schema permissive. Fixed mocks заменяют сервис без своего MCP server. [C5]

Следующие flags независимо обнаружены в локальном help 2.1.289; официальный контракт — [C5]:

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

**Стоимость:** agent runs обращаются к модели с обычными credentials и расходуют plan usage/API budget; judge и `type: agent` mocks добавляют model calls. Fixed MCP mocks убирают обращения к provider, но не делают eval offline. Default comparison выполняет оба arms; стоимость не является фиксированной ценой case. Пример ниже предназначен для будущего отдельно разрешённого model CI, не выполнялся. [C5]

```sh
claude plugin eval . --trust-plugin --mocks record --no-publish \
  --ablation none --runs 1 --max-cost-usd 1 --concurrency 1
```

**Вывод для ограничения «no custom code»:** prompt/grader/mock files позволяют проверить invocation, tool arguments/order и текстовый результат штатными средствами. Создание workspace через `context.scaffold_script` уже требует авторского Bash script и не подходит принятому ограничению. Stateful fake-provider model и произвольные machine assertions не возникают автоматически из Markdown mocks. Eval на Claude не доказывает поведение Hermes. [C5]

## AGENTS.md и CLAUDE.md

В текущем vendor contract прямой `AGENTS.md` поддерживается с 2.1.277. Default mode `claude-md-or-agents-md`: наличие `CLAUDE.md`, `.claude/CLAUDE.md` либо `CLAUDE.local.md` в cwd/предках выбирает CLAUDE instructions вместо AGENTS; пользовательский `~/.claude/CLAUDE.md` не подавляет AGENTS. Если этих project CLAUDE files нет, при старте читаются `AGENTS.md` и `.claude/AGENTS.md` в cwd/предках, вложенные AGENTS — при чтении файлов соответствующей директории. [C7]

`.agents/`, `AGENTS.local.md`, `AGENTS.override.md` не входят в этот discovery. Другие modes: `claude-md-and-agents-md`, `claude-md`, `managed-only`; builtin `agents-md` можно отключить. Ограничения Bedrock/telemetry относились к версиям до 2.1.281. `@AGENTS.md` из `CLAUDE.md` остаётся совместимым импортом без копии текста. Это существенно отличается от старого вывода «Claude не читает AGENTS.md», но загрузка в реальной сессии здесь не проверялась. [C7]

## Открытые риски и граница проверки

Не выполнены `--plugin-dir` runtime, install, eval, OAuth или tool discovery hosted MCP. Не проверены фактическая загрузка AGENTS, runtime загрузка shared portable MCP config и runtime priority двух manifests. Наличие CLI и успешная статическая проверка не подтверждают эти слои. В rebuild следует использовать один настоящий `skills/`, декларативные adapters и разделить статический CI, model eval и будущую Hermes acceptance. [C1][C4][C5][C6][C7]

## Первичные источники

Для каждого source ниже **дата доступа — 2026-10-05**. Локальные наблюдения датированы отдельно; ссылки дают официальный контракт для сопоставления, а не независимое подтверждение состояния этого Mac.

- [C0] [Anthropic Claude Code: публичный repository и changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md), доступ 2026-10-05.
- [C1] [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference), доступ 2026-10-05.
- [C2] [Create a plugin](https://code.claude.com/docs/en/plugins/create), доступ 2026-10-05.
- [C3] [Add plugin components: MCP servers](https://code.claude.com/docs/en/plugins/components#mcp-servers), доступ 2026-10-05.
- [C4] [Plugin loading reference](https://code.claude.com/docs/en/plugins/loading), доступ 2026-10-05.
- [C5] [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals), доступ 2026-10-05.
- [C6] [Plugin CLI reference](https://code.claude.com/docs/en/plugins/cli-reference), доступ 2026-10-05.
- [C7] [Claude Code memory / instruction loading](https://code.claude.com/docs/en/memory), доступ 2026-10-05.
- [C8] [Claude Code MCP configuration](https://code.claude.com/docs/en/mcp), доступ 2026-10-05.
