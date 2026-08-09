# Codex platform fit for `singularity-jedi`

> **Product overlay 2026-08-09:** заголовок сохраняет временное кодовое имя исследования. Релизный пакет — `jedikit` с одним skill `jedikit-tasks`, без router. Если официальный Scheduled Tasks недоступен, skill только объясняет ограничение и не предлагает OS cron/launchd wrapper.

Дата проверки: **2026-08-08**. Источники ниже — только официальная документация OpenAI на `developers.openai.com`, `learn.chatgpt.com` и `platform.openai.com`. Установка, подключение и публикация в рамках этой проверки **не выполнялись**.

## Краткий вывод

- **Минимальный v1:** обычный Agent Skill в репозитории: `.agents/skills/<skill-name>/SKILL.md`. Codex сканирует такую директорию, умеет явный вызов через `$skill-name`/`/skills` и неявное срабатывание по `description`.
- **Распространение поддерживается:** skill можно упаковать в plugin с обязательным `.codex-plugin/plugin.json`. Для локального теста и команды есть repo/personal marketplace (`marketplace.json`); это отдельные источники и не публичный каталог.
- **Настоящий публичный релиз поддерживается:** submission portal → проверка OpenAI → ручная публикация → общий Plugins Directory ChatGPT и Codex. Для v1 это отложенный этап: нужны верифицированная личность/бизнес, права Apps Management и материалы ревью.
- **MCP не нужен для skill-only v1.** Если появится внешний сервис, Codex поддерживает STDIO и Streamable HTTP, `config.toml`, OAuth и политики approval.
- **Automation возможна:** официально сказано, что skill может создавать или обновлять scheduled task из Chat/Codex chat. Но CLI не управляет Scheduled; web-задачи не имеют локальной папки. В v1 skill только предлагает/drafts automation и создаёт её после явного запроса пользователя.

## Возможность / доказательство / ограничение / решение для v1

| Возможность | Доказательство (официальная документация) | Ограничение | Решение для v1 |
|---|---|---|---|
| Agent Skills: локальный и repo-scoped workflow | [Build skills](https://learn.chatgpt.com/docs/build-skills): skill — директория с обязательным `SKILL.md`, где есть `name` и `description`; Codex сканирует `.agents/skills` от `$CWD` до корня репозитория; явный вызов — `$skill-name` или `/skills`, неявный — по `description`. | Это локальное обнаружение, а не публикация. Список skills ограничен 2% контекста/8 000 символов; одинаковые имена не объединяются. | Держать ядро `singularity-jedi` обычным repo skill; дать короткое описание с чёткими trigger/boundary и проверять явным `$singularity-jedi`. |
| Plugin как устанавливаемый пакет | [Plugin architecture](https://developers.openai.com/plugins/concepts/plugins), [Package your plugin](https://developers.openai.com/plugins/build/plugins): каждый plugin требует `.codex-plugin/plugin.json`; в корне могут быть `skills/`, `.mcp.json`, `.app.json`, `hooks/`, `assets/`; пути в manifest — относительные `./`. | Plugins доступны на web Work, в desktop и Codex CLI, но не в IDE extension; после установки нужен новый chat/session. Hooks дают кодовые действия — их нужно отдельно доверять. | Если нужен install/share, сделать минимальный skills-only plugin: manifest + `skills/<name>/SKILL.md`; MCP/hooks/assets не добавлять без требования. |
| Локальный/repo/personal marketplace | [Build plugins](https://developers.openai.com/plugins/build/plugins): repo catalog — `$REPO_ROOT/.agents/plugins/marketplace.json`, personal — `~/.agents/plugins/marketplace.json`; `source.path` указывает на plugin с `./` относительно marketplace root. Codex CLI умеет `codex plugin marketplace add/list/upgrade/remove`; при локальной установке desktop docs указывают кэш `~/.codex/plugins/cache/...`. | Local/repo/personal catalog — отдельный источник authoring/testing/private distribution; доступность различается по surface. Это **не** универсальный публичный каталог. | Для командного репозитория — repo marketplace; для личной проверки — personal marketplace. Не называть локальную запись публичным релизом. |
| Публичный marketplace-релиз (universal Plugins Directory) | [Submit plugins](https://developers.openai.com/plugins/deploy/submission): принимаются skills-only, MCP-only и skills+MCP; после Submit идёт review, затем разработчик публикует одобренную версию; после публикации listing появляется в общем Plugins Directory ChatGPT/Codex. | Нужны Apps Management `Write`, верифицированная developer/business identity, публичные website/support/privacy/terms URL, 5 positive + 3 negative test cases. Для MCP добавляются production HTTPS URL, domain verification, demo credentials и tool annotations; сроки review могут меняться. | Возможность реальна, но публичный релиз не входит в v1. Сначала локальный plugin + representative evals; submission только после отдельного решения и подготовки identity/legal/MCP материалов. |
| MCP-подключение | [MCP for Codex](https://learn.chatgpt.com/docs/extend/mcp): общая конфигурация `~/.codex/config.toml` или trusted project `.codex/config.toml`; поддерживаются STDIO, Streamable HTTP, bearer/OAuth; официальные команды `codex mcp add`, `codex mcp list`, `codex mcp login`; TUI — `/mcp`. | ChatGPT web не читает локальный Codex config; plugin MCP может требовать отдельную auth/setup. При public plugin MCP нужен публичный production endpoint и ревью; approval modes (`auto`, `prompt`, `writes`, `approve`) применяются хостом. | В skill-only v1 MCP не добавлять. При реальной потребности — один минимальный сервер, least-privilege tools, OAuth/secret boundary и ручной read-only smoke test до публикации. |
| Scheduled tasks / automations | [Scheduled tasks](https://learn.chatgpt.com/docs/automations): task создаётся/обновляется из Chat или Codex chat; skills также могут создавать/обновлять scheduled tasks; task может использовать skills/plugins. | Codex CLI не имеет Scheduled management UI; создавать/управлять нужно web или desktop. Web-task не сохраняет локальную папку/worktree; desktop local project требует включённые компьютер и приложение. Запуск unattended использует sandbox; `approval_policy = "never"` действует только если разрешено org policy, иначе применяется выбранный permission mode. | Skill может **предложить и подготовить** automation; создание — только после явного запроса пользователя с подтверждёнными cadence, destination, tools и scope. Перед включением — протестировать prompt в обычном чате и посмотреть первые runs. |
| Первый запуск и onboarding | [Codex CLI quickstart](https://learn.chatgpt.com/docs/codex/cli), [Quickstart](https://learn.chatgpt.com/docs/quickstart): установить CLI, выполнить `codex` из project directory, на первом запуске выбрать Sign in with ChatGPT/доступный метод и затем описать первую задачу. | API-key sign-in не даёт часть plugin flows, если им нужен неподдерживаемый OAuth. Доступность отдельных surfaces/account features в документации не гарантируется для всех аккаунтов. | В документации проекта оставить только подтверждённую последовательность install → `codex` → sign-in → smoke prompt; ничего автоматически не устанавливать. |
| Проверка установки и работы | [Build skills](https://learn.chatgpt.com/docs/build-skills): изменения skill обнаруживаются автоматически, при необходимости перезапустить Codex; [Plugins](https://learn.chatgpt.com/docs/plugins): в CLI `/plugins`, после install новая session; [Build plugins](https://developers.openai.com/plugins/build/plugins): проверить manifest/skills, refresh, install из local source, затем representative requests; [MCP](https://learn.chatgpt.com/docs/extend/mcp): `codex mcp list` и `/mcp`. | Официальная страница не использована для утверждения о `codex --version`; эту команду в checklist не добавлять. Каталог, кэш и UI подтверждают разные слои — один факт не доказывает весь runtime. | Сделать ручной smoke-check: skill виден в `/skills`, явный `$singularity-jedi` даёт ожидаемый результат; plugin виден в `/plugins` и работает в новой session; при MCP сервер виден в `codex mcp list`/`/mcp`; сохранять вывод и first-run evidence. |

## Подтверждённые команды (только справка; в этой задаче не выполнялись)

CLI install/first run (официальный standalone installer для macOS/Linux):

```sh
curl -fsSL https://chatgpt.com/codex/install.sh | sh
codex
```

Marketplace sources (официальная plugin CLI reference):

```sh
codex plugin marketplace add ./local-marketplace-root
codex plugin marketplace list
codex plugin marketplace upgrade
codex plugin marketplace upgrade marketplace-name
codex plugin marketplace remove marketplace-name
```

MCP (официальная Codex MCP reference):

```sh
codex mcp add <server-name> --env VAR1=VALUE1 --env VAR2=VALUE2 -- <stdio-server-command>
codex mcp list
codex mcp login <server-name>
```

Codex TUI commands:

```text
/skills
/plugins
/mcp
```

## Рекомендуемый v1-поток

1. **Author:** `.agents/skills/singularity-jedi/SKILL.md`; проверить frontmatter `name`/`description`, границы и безопасный stop/ask.
2. **Local proof:** открыть `codex` из репозитория, вызвать `$singularity-jedi`, прогнать positive и negative prompts; при необходимости перезапустить Codex.
3. **Installable proof:** упаковать skills-only `.codex-plugin/plugin.json`, добавить repo/personal marketplace, установить через `/plugins`, открыть новую session и повторить representative requests.
4. **Automation (optional):** skill предлагает durable prompt + cadence; после явного подтверждения пользователь создаёт task в desktop/web, тестирует prompt и проверяет первые runs.
5. **Later:** MCP и public submission только при реальной external-tool потребности и после подготовки auth, identity, legal URLs, test cases и (для MCP) public endpoint/domain verification.

## Что официальная документация не подтверждает

- Не утверждается наличие отдельного публичного Git marketplace, который заменяет Plugins Directory: docs различают local/repo/personal JSON catalogs и universal public directory.
- Не утверждается обязательный отдельный confirmation dialog перед созданием scheduled task: docs описывают создание из чата и policy/sandbox boundaries, поэтому v1 должен требовать явное пользовательское решение как собственную безопасную политику.
- Не утверждается универсальная доступность всех plugins, OAuth flows, scheduled tasks или public submission для каждого account/workspace; это зависит от surface, org policy и текущей доступности.
