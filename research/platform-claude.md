# Claude / Claude Code: распространение и эксплуатация `singularity-jedi`

Снимок официальной документации на **2026-08-08**. Здесь разделены Claude Code (локальный CLI), Claude.ai/Cowork (продуктовые поверхности) и Claude API/Agent SDK: одно и то же имя Skill или plugin между ними автоматически не синхронизируется.

## Короткий вывод для v1

1. Поставлять `singularity-jedi` следует как обычный Claude Code plugin в Git-репозитории. В репозитории — plugin с `.claude-plugin/plugin.json`, `skills/<name>/SKILL.md` и (только при наличии реального сервера) `.mcp.json`; для каталога — отдельный `.claude-plugin/marketplace.json`. Такой layout поддерживается официальным plugin loader’ом ([plugins](https://code.claude.com/docs/en/plugins), [plugins reference](https://code.claude.com/docs/en/plugins-reference)).
2. До публикации достаточно локального `--plugin-dir` и проверки валидатором. Публичный marketplace не является автоматическим npm-подобным publish: Claude Code умеет подключить любой GitHub/Git/local каталог, а для каталога Anthropic/community действует отдельная заявка и проверка. Поэтому v1 можно начать с собственного репозитория/marketplace; подачу в community оставить отдельным релизным шагом ([plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces), [community repository](https://github.com/anthropics/claude-plugins-community)).
3. MCP — опциональный транспорт внешних инструментов/данных, а не обязательная часть Skill. Если сервер не нужен, `.mcp.json` не добавлять. Если нужен — предпочесть HTTP, для локального процесса использовать stdio; проектный `.mcp.json` коммитить только после проверки команд и секретов ([MCP](https://code.claude.com/docs/en/mcp)).
4. `/loop` и встроенный CronCreate — временные задания текущей сессии: нужен запущенный Claude Code, повторение истекает через 7 дней. Для автономного ежедневного прогона репозитория использовать Cloud Routine (`/schedule`), локальное Desktop scheduled task, GitHub Actions или системный cron/launchd — в зависимости от того, нужны ли локальные файлы ([scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks), [web scheduled tasks](https://code.claude.com/docs/en/web-scheduled-tasks)).
5. Безопасная база: режим `default`/`plan`, узкие `permissions.allow/ask/deny`, отсутствие `bypassPermissions`; Skill, который пишет/деплоит/создаёт расписания, пометить `disable-model-invocation: true` и запускать явно ([permissions](https://code.claude.com/docs/en/permissions), [skills](https://code.claude.com/docs/en/skills)).

## Поверхности и решение v1

| Возможность | Доказательство | Ограничение | Решение v1 |
|---|---|---|---|
| Agent Skills в Claude Code | Claude Code следует открытому Agent Skills формату: каталог Skill содержит `SKILL.md`; поддержаны `~/.claude/skills`, `.claude/skills` и `plugin/skills/<name>/SKILL.md` ([skills](https://code.claude.com/docs/en/skills)). | Skills из Claude.ai/API не появляются в файловой системе Claude Code автоматически; `disable-model-invocation: true` запрещает модельный и scheduled вызов. | Хранить Skill внутри plugin, сделать описание явным; изменяемые/опасные операции вызывать только пользователем. |
| Skills в Claude.ai и API | В API custom Skills загружаются через Skills API/Code Execution с beta-заголовками; в Claude.ai архив загружается в Settings → Features. Эти Skills workspace/user scoped соответственно ([Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), [Skills API guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide)). | Runtime API изолирован: нет сети и установки пакетов во время выполнения; custom Skills между claude.ai, API и Claude Code не синхронизируются. | Не считать API/Claude.ai каналом установки plugin. При необходимости сделать отдельный v2-архив/API wrapper и отдельную проверку. |
| Plugin и manifests | Минимум: `.claude-plugin/plugin.json` в plugin root; компоненты — `skills/`, `commands/`, `agents/`, `hooks/`, `.mcp.json`, `scripts/` на верхнем уровне ([plugins](https://code.claude.com/docs/en/plugins), [reference/layout](https://code.claude.com/docs/en/plugins-reference)). | В `.claude-plugin/` должен оставаться только `plugin.json` (для plugin); размещение `skills/` внутрь него — ошибка layout. | Рекомендуемый layout см. ниже; версию в `plugin.json` повышать на каждый релиз. |
| Локальное тестирование plugin | `claude --plugin-dir ./plugins/singularity-jedi` загружает plugin для сессии; `/reload-plugins` перечитывает компоненты ([plugins](https://code.claude.com/docs/en/plugins)). | Это не установка и не публикация; нужно открыть новую сессию для нового top-level Skill directory. | До Git-релиза прогнать `--plugin-dir`, вызвать namespaced Skill и проверить `/plugin` → Errors. |
| Marketplace как каталог | `.claude-plugin/marketplace.json` содержит `name`, `owner`, `plugins[]`; `source` может быть относительным путём, GitHub `{repo, ref/sha}`, Git URL, npm или archive. Подключение: `/plugin marketplace add owner/repo`; установка: `/plugin install plugin@marketplace` ([plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)). | Marketplace — лишь каталог; произвольный Git-репозиторий не получает автоматическую публикацию/доверие Anthropic. Источники лучше pin’ить на ref/SHA. | Сначала публиковать собственный Git-репозиторий и давать команду `marketplace add`; SHA-pin использовать для воспроизводимых инсталляций. |
| Публичные каталоги Anthropic/community | Официальный каталог `claude-plugins-official` добавляется автоматически при первом интерактивном старте; community-каталог — `anthropics/claude-plugins-community`. Community plugin подаётся через форму, проходит валидацию и автоматический security screening; зеркало синхронизируется ночью ([plugin creation](https://code.claude.com/docs/en/plugins), [community repo](https://github.com/anthropics/claude-plugins-community), [directory](https://claude.com/plugins)). | Нет гарантии принятия или срока публикации. Прямые PR в community repo закрываются; решение о включении принимает Anthropic. | Не блокировать v1 ожиданием directory review; подать после стабильного релиза, сохранив собственный marketplace как источник истины. |
| MCP-сервер | CLI поддерживает `claude mcp add`, `add-json`, `list`, `get`, `remove`; конфигурация — `mcpServers` в `.mcp.json` или plugin root. Поддержаны HTTP (рекомендуемый remote), stdio и websocket; SSE отмечен deprecated ([MCP](https://code.claude.com/docs/en/mcp)). | Project scope (`.mcp.json`) коммитится в Git и при интерактивном запуске просит approval; local/user scopes лежат в `~/.claude.json`. API/неинтерактивные сессии не могут показать prompt approval. | В v1 не включать MCP без конкретной интеграции. Для нужного сервера — read-only по умолчанию, `${VAR}` для секретов, project config только после ручной проверки. |
| Сессионный cron | `/loop 5m <prompt>` и CronCreate/CronList/CronDelete работают в текущем Claude Code session; `/loop` может запускать Skill, если тот разрешает model invocation ([scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)). | Требуется работающий процесс; recurring task истекает через 7 дней, пропущенные срабатывания не догоняются. `CLAUDE_CODE_DISABLE_CRON=1` отключает scheduler. | Использовать только для интерактивного наблюдения/короткого цикла, не как production scheduler. |
| Долговечное расписание | `/schedule` создаёт Cloud Routine; Cloud/Routines запускаются в новом облачном сеансе без открытого окна и имеют минимум 1 час между запусками. Desktop Local task работает на локальной машине и видит локальные файлы; Cowork отдельно документирует удалённые scheduled tasks ([web scheduled tasks](https://code.claude.com/docs/en/web-scheduled-tasks), [Cowork scheduled tasks](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork)). | Cloud Routine не имеет доступа к невыбранной локальной папке; local task требует включённого компьютера/Desktop. Облачные connector-инструменты выполняются без обычного prompt-permission, поэтому scope должен быть узким. | Для GitHub-отчётов/PR — GitHub Actions или Cloud Routine; для Obsidian/локальных файлов — Desktop Local task или launchd/cron. Документировать выбранный fallback, не обещать универсальный «cron Claude». |
| Agent SDK embedding | Agent SDK принимает `settingSources`/`setting_sources` (`user`, `project`), фильтр `skills`, локальные plugins и `mcpServers`; init сообщает загруженные skills/plugins ([SDK skills](https://code.claude.com/docs/en/agent-sdk/skills), [SDK plugins](https://code.claude.com/docs/en/agent-sdk/plugins), [SDK MCP](https://code.claude.com/docs/en/agent-sdk/mcp)). | Это программная интеграция, не marketplace-install; потребуется свой сервис, auth и lifecycle. | Оставить как v2-вариант, если `singularity-jedi` потребуется в приложении/боте, а не только в CLI. |
| Установка и вход | Рекомендуемый native install: `curl -fsSL https://claude.ai/install.sh | bash`; Homebrew: `brew install --cask claude-code`. Проверка: `claude --version`, `claude doctor`; вход — `claude auth login` или запуск `claude` с browser login ([getting started](https://code.claude.com/docs/en/getting-started), [CLI usage](https://code.claude.com/docs/en/cli-usage)). | Claude Code требует Pro/Max/Team/Enterprise или Console; бесплатный план его не включает. Native auto-updates, Homebrew требует ручного upgrade. | В onboarding явно указать требуемый план/auth; после установки сохранить вывод `--version` и `doctor` в отчёте проверки. |
| Permission model | `permissions.allow/ask/deny` применяются Claude Code; есть `default`, `acceptEdits`, `plan`, `dontAsk`, `bypassPermissions`. Sandbox и permissions — defense-in-depth; managed settings могут запретить override ([permissions](https://code.claude.com/docs/en/permissions)). | `bypassPermissions` пропускает большинство prompts и рекомендован только в изолированном контейнере/VM. Project settings действуют после trust dialog; connector/MCP explicit interaction может всё равно требовать подтверждение. | Для демо/пользователя — `default` или `plan`; запретить чтение секретов и destructive Bash; deploy/write tools — только `ask`/явная команда. |
| Проверяемость установки | `claude plugin validate <path> [--strict]`, `/plugin validate`; `claude plugin list --json`, `claude plugin details`; `claude mcp list`; `/mcp`; `claude --debug` и `/plugin` Errors помогают диагностике ([plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces), [plugins reference](https://code.claude.com/docs/en/plugins-reference), [MCP](https://code.claude.com/docs/en/mcp)). | `plugin list` подтверждает локальное состояние, а не доступность внешнего Git/marketplace или работоспособность MCP backend. | Делать smoke test в чистом каталоге: validate → install → namespaced Skill → MCP status (если есть) → повторная сессия. Сохранять JSON/логи проверки. |

## Layout для репозитория v1

Marketplace-файл должен быть в корне каталога marketplace; сам plugin — отдельным подпутём. Это позволяет тестировать plugin напрямую и устанавливать его через каталог:

```text
repo/
├── .claude-plugin/
│   └── marketplace.json
└── plugins/
    └── singularity-jedi/
        ├── .claude-plugin/
        │   └── plugin.json
        └── skills/
            └── singularity-jedi/
                └── SKILL.md
```

Минимальный `plugin.json` (значения `author` и `description` заменить реальными):

```json
{
  "name": "singularity-jedi",
  "description": "...",
  "version": "0.1.0",
  "author": { "name": "..." }
}
```

Минимальная запись в корневом `.claude-plugin/marketplace.json`:

```json
{
  "name": "singularity-jedi-marketplace",
  "owner": { "name": "..." },
  "plugins": [
    {
      "name": "singularity-jedi",
      "source": "./plugins/singularity-jedi",
      "description": "..."
    }
  ]
}
```

Не добавлять `.mcp.json`, пока нет конкретного MCP-сервера. Если он появится, конфиг должен содержать стандартный объект `mcpServers`; секреты передавать через `${ENV_VAR}`, а не хранить в Git ([MCP configuration](https://code.claude.com/docs/en/mcp)).

## Onboarding и smoke test (команды не запускались в рамках этого исследования)

```bash
# 1. На машине пользователя
claude --version
claude doctor
claude auth status              # exit 0 = logged in, exit 1 = not logged in

# 2. В checkout репозитория
claude plugin validate . --strict
claude --plugin-dir ./plugins/singularity-jedi

# 3. После публикации marketplace
claude plugin marketplace add owner/repo --scope user
claude plugin install singularity-jedi@singularity-jedi-marketplace --scope user
claude plugin list --json
claude plugin details singularity-jedi

# 4. Если plugin declares MCP
claude mcp list
claude mcp get <server-name>
```

В интерактивной сессии проверить namespaced вызов (`/singularity-jedi:<skill>`), `/plugin` → Installed/Errors и `/mcp` (только если MCP заявлен). Изменения plugin-компонентов применить `/reload-plugins`; новый каталог Skill проверить в новой сессии. Для community directory перед заявкой повторить `claude plugin validate ./plugins/singularity-jedi --strict`; прямой PR в зеркало не является поддержанным каналом ([community submission](https://github.com/anthropics/claude-plugins-community)).

### Источник решения по расписанию

| Нужны | Выбор |
|---|---|
| Короткий цикл при открытом Claude Code | `/loop`/CronCreate; срок и требования сессионные. |
| Репозиторий, PR или отчёт без локального диска | Cloud Routine через `/schedule` либо GitHub Actions. |
| Obsidian/vault и другие локальные файлы | Desktop Local scheduled task, либо macOS launchd/cron; Claude Code должен запускаться в нужном runtime. |
| API-сервис с собственным lifecycle | Agent SDK + внешний scheduler; не выдавать это за встроенную marketplace-функцию. |
