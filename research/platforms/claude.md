# Claude Code: актуальный контракт JediKit

Дата исходного исследования: **2026-10-05**, консолидация — **2026-10-06**. Модель изменена в 0.3.0: плагин не объявляет подключения и секреты ни для одного хоста ([ADR 0005](../../docs/adr/0005-one-source-host-connections.md)). Это исследование совместимости, а не подтверждение runtime.

## Что является доказательством

- **Наблюдение 2026-10-05:** установленный Claude Code **2.1.289**, его `--version` и native help для `plugin`, `plugin validate`. Полный исходный код исполняемого файла не исследован: публичный репозиторий Anthropic не является открытой реализацией этого бинарника. Help подтверждает наличие команд, но не их выполнение с моделью. Официальный контекст версии и продукта: [PL-C-0](../sources.md).
- **Заявления vendor:** контракты ниже из официальной документации [PL-C-1](../sources.md), [PL-C-6](../sources.md), [PL-C-7](../sources.md); они помечены отдельно от локальных запусков.
- **Anecdote:** пользовательские отзывы и старые успешные сессии не использованы как доказательство текущего контракта.

## Layout, manifest и invocation

Документированный manifest — `.claude-plugin/plugin.json`; он необязателен, а при наличии единственное обязательное поле — `name`. Без него имя определяется marketplace entry либо именем директории при `--plugin-dir`. `skills/`, `agents/`, commands и остальные компоненты находятся в plugin root, вне `.claude-plugin/`. Поле `skills` принимает строку или массив директорий и добавляет пути к стандартному `skills/`, не заменяя его. Пути компонентов должны существовать и оставаться внутри plugin root. Для JediKit достаточно одного настоящего `skills/jedikit-tasks/SKILL.md` и `skills/jedikit-habits/SKILL.md`; дополнительные пути и копии не нужны. [PL-C-1](../sources.md)

Claude namespace даёт explicit invocation `/jedikit:jedikit-tasks` и `/jedikit:jedikit-habits`; description используется для выбора skill моделью. Это документированный UX, а не выполненный smoke test. [PL-C-2](../sources.md)

Платформа поддерживает plugin MCP declarations, но JediKit ими не пользуется. SingularityApp и Habitify подключает хост. Habitify сохраняет официальный REST/OpenAPI v2 как бизнес-контракт; операции предоставляет OpenAPI→MCP-адаптер или эквивалент с теми же именами, ключ остаётся только у адаптера ([ADR 0001](../../docs/adr/0001-habitify-via-rest.md), [ADR 0005](../../docs/adr/0005-one-source-host-connections.md)). Официальный Habitify MCP отвергнут из-за неполноты операций. `tools.json` задаёт базовые имена без host prefix, серверы `singularity`/`habitify`, доступ `read`/`write` и `required` у Habitify. При отсутствии tools агент называет недостающие операции и рекомендует подключить их на хосте; ничего не устанавливает. [PL-C-1](../sources.md), [PL-C-3](../sources.md)

**Сосуществование manifests:** документация регулярной загрузки описывает `.claude-plugin/plugin.json`. JediKit использует небольшой Claude manifest и общий root `skills/`; межплатформенные границы изложены в [hermes.md](hermes.md). [PL-C-1](../sources.md)

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

Exit `0`, `success: true`, target — текущий `.claude-plugin/plugin.json`, errors/warnings пусты. В report `contents: []`; это не inventory проверенных файлов. Исторически, до изменения модели в 0.3.0 ([ADR 0005](../../docs/adr/0005-one-source-host-connections.md)), проверена временная декларативная fixture с portable root `plugin.json`, Claude manifest с `skills: "./skills"`, `mcpServers: "./mcp.json"` и MCP-файлом с portable `$schema` + `type: streamable-http`: strict validation прошла. После удаления skill description и подстановки неизвестного MCP transport эта же fixture дала exit `1`, warning по frontmatter и error по MCP type. Тем самым проверено, что validator действительно проверяет компоненты, а portable MCP JSON принимается статически. Runtime loading этим не доказан. [PL-C-1](../sources.md), [PL-C-6](../sources.md), [PL-C-8](../sources.md)

Изолированная config directory не содержала аккаунта; модель и MCP не запускались. Исследованный validator пригоден для статического CI без пользовательского аккаунта; packet tracing отсутствия сети не выполнялся. Временная fixture использовала только `https://example.com/mcp`, без обращения к адресу или provider data. Команда и смысл report соответствуют [PL-C-6](../sources.md).

## AGENTS.md и CLAUDE.md

В текущем vendor contract прямой `AGENTS.md` поддерживается с 2.1.277. Default mode `claude-md-or-agents-md`: наличие `CLAUDE.md`, `.claude/CLAUDE.md` либо `CLAUDE.local.md` в cwd/предках выбирает CLAUDE instructions вместо AGENTS; пользовательский `~/.claude/CLAUDE.md` не подавляет AGENTS. Если этих project CLAUDE files нет, при старте читаются `AGENTS.md` и `.claude/AGENTS.md` в cwd/предках, вложенные AGENTS — при чтении файлов соответствующей директории. [PL-C-7](../sources.md)

`.agents/`, `AGENTS.local.md`, `AGENTS.override.md` не входят в этот discovery. Другие modes: `claude-md-and-agents-md`, `claude-md`, `managed-only`; builtin `agents-md` можно отключить. Ограничения Bedrock/telemetry относились к версиям до 2.1.281. `@AGENTS.md` из `CLAUDE.md` остаётся совместимым импортом без копии текста. Это существенно отличается от старого вывода «Claude не читает AGENTS.md», но загрузка в реальной сессии здесь не проверялась. [PL-C-7](../sources.md)

## Открытые риски и граница проверки

Не выполнены `--plugin-dir` runtime, install, OAuth или tool discovery. Не проверены фактическая загрузка AGENTS и runtime priority manifests. Наличие CLI и успешная статическая проверка не подтверждают эти слои. Проверки проекта — штатные Claude/Hermes validators, `git diff --check` и независимое агентное ревью; модельные прогоны не входят в текущую проверку. [PL-C-1](../sources.md), [PL-C-4](../sources.md), [PL-C-6](../sources.md), [PL-C-7](../sources.md)

## Источники

Полные citations и объём доступа — в [реестре источников](../sources.md).

## Scheduling и различия поверхностей

Историческое исследование **2026-09-13** различало session-bound `/loop`/CronCreate, fresh remote Cloud tasks и Desktop local tasks. Текущая документация session scheduling описывает повтор до истечения срока (7 дней для recurring task) либо окончания сессии; это не долговечный daemon scheduler. Для remote/local scheduled surfaces отдельно проверяются место исполнения, доступный context, lifecycle, permissions и destination. Такие jobs здесь не создавались. [PL-C-9](../sources.md)

Claude Code plugin, Claude.ai upload и Skills API — разные deployment surfaces. В API skills используют Code Execution sandbox с его runtime/network restrictions; plugin install не подтверждает доступ к локальному диску, API deployment или аккаунтам другой поверхности. Ни API wrapper, ни отдельная generated package не входят в согласованный scope. [PL-C-10](../sources.md), [PL-C-13](../sources.md)

Marketplace регистрирует источник plugins, установка выбирает конкретный plugin. Claude host-specific dependencies/bundle не образуют universal skill-to-skill dependency contract. Для JediKit два независимых skills имеют одну package identity без router; каждый содержит необходимые operational references. Mixed request разделяется на workflows. [PL-C-11](../sources.md), [PL-C-14](../sources.md)

Для диагностики проверяются source/revision, manifest, inventory обоих namespaced skills, новая session и host MCP/tool schemas, затем поведение. Project trust, tool permission и согласие пользователя на запись различаются. Пользовательский OAuth не переносится при копировании repo. Unattended permission bypass не служит доказательством корректного preview/approval/read-back. По [ADR 0003](../../docs/adr/0003-no-unattended-writes.md) фоновые обзоры только читают. `disable-model-invocation: true` на платформе отключает автоматическую активацию; его нельзя добавлять как универсальную safety policy для skills с scheduled invocation. [PL-C-12](../sources.md)

Native memory не является общим хранилищем трёх hosts. По [ADR 0006](../../docs/adr/0006-memory-holds-settings-only.md) там только настройки; состояние обзоров не сохраняется. Не проверены Cloud/Desktop delivery и фактическая загрузка skills в каждой поверхности.
