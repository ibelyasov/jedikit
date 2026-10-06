# Hermes Agent: текущий контракт и общий layout JediKit

Дата исследования: **2026-10-05**. Решение владельца: обязательный acceptance host — Hermes на его Nix-сервере; Claude Code и Codex входят в заявленную поддержку. Старые snapshots используются только как контекст, без переноса их runtime evidence на новый пакет.

## Версия и типы доказательств

Последний stable release официального GitHub API на дату проверки — **0.21.5 / `v2026.9.24`**, опубликован 2026-09-24, commit **`f97608f178d1ffeca59860195ab7da295f7c8e5f`**. Все source links ниже закреплены этим commit. Текущие web docs могут описывать более новый `main`. [H1][H2]

- **Независимо исследовано:** public release metadata и pinned source, включая parser, discovery, scanner, loader и validators. Это чтение реализации, а не runtime test.
- **Vendor claims:** текущие официальные docs о skills, memory, cron, plugins и Nix; их следует сверять с фактическим deployment. [H3][H4][H5][H6][H7]
- **Anecdote:** отзывы и старые пользовательские сессии не использованы как доказательство.

Hermes локально не установлен. Установка, validators Hermes, OAuth, MCP calls, memory writes, cron jobs и изменения Nix-сервера здесь не выполнялись. Ни исходники, ни проверка package schema не подтверждают работающую авторизацию провайдеров.

## Root install: нужен ли packages/jedikit

**Hermes не требует `packages/jedikit`.** Portable package может находиться в repo root: `plugin.json`, `skills/<name>/SKILL.md`, optional `mcp.json`. Discovery явно пропускает foreign harness manifest directories `.claude-plugin/` и `.codex-plugin/`; parser выбирает portable root manifest. Наличие рядом `.mcp.json` тоже не является самостоятельным structural rejection. Это подтверждение реализации 0.21.5, не выполненный install финального JediKit. [H8][H9]

Installer принимает `owner/repo`, `owner/repo/path/to/plugin`, Git URLs и subdirectory fragment. `--ref` принимает полный 40-character commit SHA; branch, tag и abbreviated SHA не удовлетворяют проверенному exact-ref контракту. Subdirectory install использует sparse checkout. Пример будущей установки ниже; SHA должен принадлежать JediKit, не Hermes. [H10][H3]

```sh
hermes plugins install ibelyasov/jedikit --ref <FULL_JEDIKIT_COMMIT_SHA> --enable
```

Skills Hub — другой механизм установки отдельного skill, например из `owner/repo/skills/name`. Он получает default-branch tree и revision для согласованного чтения bundle; его нельзя приравнивать к `plugins install --ref`. Plugin install предпочтительнее для общей package identity двух skills. Последнее — проектный вывод. [H11][H4]

Symlink `packages/jedikit/skills -> ../../skills` нарушает containment: resolved path выходит за plugin root, parser его отклоняет, scanner выдаёт critical `symlink_escape`. Поэтому перенос root package в subdirectory со ссылкой наружу не решает задачу единственного источника. [H9][H12]

## Discovery и scanner — разные проверки

Security scanner рекурсивно проверяет содержимое выбранного package, включая hidden directories; исключаются конкретные VCS/cache/environment names, например `.git`, `node_modules`, `.venv`. Foreign manifest directories пропускаются discovery, но их содержимое участвует в scanner. Само имя `.claude-plugin/`, `.codex-plugin/` или `.mcp.json` не блокируется; инструкции, scripts, documentation и symlinks могут дать findings. [H8][H12][H13]

Install вызывает scanner до swap: `safe` допускается, `caution` требует подтверждения либо `--force`, `dangerous` блокируется даже с `--force`. Следовательно, отсутствие parser incompatibility не гарантирует успешный root install всего repository. Final scanner verdict остаётся открытым; обход scanner не предлагается. [H10][H12]

## mcp.json, .mcp.json и OAuth

Portable loader читает **только `mcp.json`** с точным Agent Plugins schema URI и top-level `$schema`/`mcpServers`. `.mcp.json` не является fallback и не конкурирует по precedence. Если рядом есть native YAML plugin manifest, он имеет приоритет над portable `plugin.json`. [H9][H10]

Remote portable entry допускает `type: streamable-http`, `url`, `headers`; translation сохраняет URL/non-empty headers и добавляет `strict_redirect_headers: true`. **`auth: oauth` теперь нельзя описывать как просто потерянное поле:** unknown `auth` даёт diagnostic `unknown remote field`, и entry пропускается. В native host MCP configuration `auth: oauth` поддерживается отдельно. Portable specification тоже оставляет authentication клиенту и не определяет такое поле. [H9][H14][H15]

Plugin MCP server names не получают длинный skill namespace. Duplicate plugin server names пропускаются с warning; native configuration имеет приоритет по naming contract. Поэтому plugin inventory, effective native config и работающая OAuth connection — отдельные утверждения. Будущую авторизацию официальных hosted MCP SingularityApp/Habitify нужно проверять на acceptance host; здесь никаких connections не создавалось. [H16][H17][H18]

## Naming, explicit invocation и native features

Portable namespace вычисляется как `agent-plugin-<slug>-<sha256(key)[:8]>`; полное имя skill следует получать из текущего discovery. Нельзя обещать стабильный identifier `jedikit:jedikit-habits`: изменение registry key может изменить namespace. [H16]

Plugin skills доступны в `skills_list` и разрешаются по qualified name в `skill_view`, не копируются в `~/.hermes/skills` и не включаются в system prompt `<available_skills>`. Slash-command scanner обходит physical project/local/external directories, а не plugin registry: нельзя обещать автоматический `/namespace:skill` для portable plugin. Проверенный explicit preload — `hermes chat --skills '<EXACT_QUALIFIED_SKILL_NAME>'`; parser передаёт identifier в `skill_view`. Эти source contracts не проверены выполнением с моделью. [H28][H29][H30]

Cron поддерживает attached skills через повторяемый `--skill`; проверенный identifier нужно получать из discovery, а не угадывать namespace. Source принимает `skills` list/string и legacy `skill`, загружает через `skill_view`, добавляет text в prompt перед injection scan. Missing skill логируется и пропускается: успешная job не доказывает загрузку нужного skill. Сам Markdown skill не предоставляет capabilities: native tools доступны по effective host configuration/toolsets. [H4][H5][H32]

Native memory хранится в Hermes profile и доступна через `memory`; она не становится общим хранилищем Claude/Codex. Source tool schema: target `memory|user`, actions `add|replace|remove`, `content` для add/replace, `old_text` для replace/remove; есть atomic `operations` array. Dynamic schema может сузить targets по host config. Skill может описывать этот native protocol без собственного memory runtime. Scheduler может запускать agent work со skills. Наличие этих host features не подтверждает inference, persistence, timezone или delivery на сервере владельца. [H5][H6][H31]

Вне plugin install возможен `skills.external_dirs`, указывающий на canonical source без копирования. Docs предупреждают: агент может изменять external directories при наличии filesystem write permissions. Это отдельный deployment path, который не устанавливает portable MCP package автоматически. Для выбранного package root этот обход не нужен. [H4]

## Официальные validators и CI

В source 0.21.5 подтверждены commands:

```sh
hermes plugins doctor . --ci
hermes plugins validate . --json
```

Doctor копирует package во временный `HERMES_HOME`, выполняет discovery/load/registration и блокирует Python socket connects. Portable loader не импортирует Python entrypoint. Для декларативного package эта проверка не нуждается в provider accounts; установка самого Hermes/dependencies может требовать сети. Это source-derived вывод, команды здесь не запускались. Doctor не является OS sandbox для произвольного native plugin code. [H19][H17]

`--ci` даёт exit `1` при `report.ok == false`, но doctor не вызывает install scanner. `plugins validate` включает scanner и portable validation. Его parser имеет `--json` и `--install-deps`, но не `--ci`, `--strict` или `--fail-on-warnings`; doctor имеет `--ci`, но не `--json`. **Оба инструмента имеют предел:** portable loader продолжает работу после component diagnostics, а validator превращает portable diagnostics в warnings. Поэтому exit `0` сам по себе не доказывает присутствие обоих skills и всех ожидаемых MCP entries. [H20][H21][H17][H33]

Официальный GitHub Action имеет inputs только `path` и `hermes-ref`, устанавливает Hermes и запускает `plugins validate`; default `hermes-ref` — `main`, для release checks нужно явно pin revision. `fail-on-warnings` input отсутствует. Этот action не выполнялся. Отдельный строгий native flag «zero component diagnostics + exact expected inventory» в исследованных ветвях отсутствует. JSON report предоставляет `ok`, `checks`, `warnings`; warnings не меняют exit code. [H22][H21][H33][H34]

## Минимальный single-source layout для трёх hosts

**Проектный вывод на основе parser contracts**, без миграции текущего репозитория в этой задаче:

```text
jedikit/
├── plugin.json                       # portable core для Hermes/Codex
├── .claude-plugin/
│   └── plugin.json                   # небольшой Claude adapter
├── skills/
│   ├── jedikit-tasks/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── agents/openai.yaml        # optional Codex metadata
│   └── jedikit-habits/
│       ├── SKILL.md
│       ├── references/
│       └── agents/openai.yaml        # optional
├── mcp.json                          # optional shared portable declarations
└── .agents/plugins/marketplace.json  # если нужен Codex local marketplace
```

Root portable `plugin.json` задаёт schema/name и обычные metadata; `skills/` и `mcp.json` фиксированы. Для Claude сохраняется `.claude-plugin/plugin.json` с name/metadata и, при bundled MCP, `"mcpServers": "./mcp.json"`; `skills` можно не указывать, поскольку стандартный путь уже общий. `.codex-plugin/plugin.json` не нужен в минимальном варианте: OpenAI presentation можно разместить в `extensions.com.openai`. Дополнительный Claude marketplace manifest нужен только при выборе marketplace distribution, для local development достаточно `--plugin-dir`. Это вывод из первичных контрактов [H9][H15][H23][H24][H25][H27]; детали — [claude.md](claude.md), [codex.md](codex.md).

**Один MCP descriptor возможен статически:** Codex/Hermes читают portable `mcp.json`, Claude adapter указывает тот же JSON. Native Claude 2.1.289 strict validator принял temporary fixture с portable `$schema` и `streamable-http`; negative fixture выявила неверный transport и отсутствие skill description. Runtime loading и authentication этого общего файла не проверены. Подробный независимый check и первичные ссылки — [claude.md](claude.md), доступ к его внешним источникам **2026-10-05**. [H9][H15]

Bundled `mcp.json` содержит только публичные официальные hosted endpoints/transport, без `auth`, tokens или credential references. Если Hermes требует native `auth: oauth`, это отдельная host configuration и acceptance, не дополнительный custom server. Skills-only package с заранее настроенными native official MCP остаётся допустимым минимальным вариантом; для native Claude plugin eval mocks plugin должен отдельно декларировать соответствующие server names. Не обещается одна установка с готовыми аккаунтами на трёх hosts. [H9][H14][H15][H18][H26]; Claude eval contract подробнее — [claude.md](claude.md).

`packages/jedikit`, build generator, runtime wrappers и generated skills copies не требуются этим layout. Единственные source instructions — root `skills/`; manifests являются небольшими отдельными декларациями. Final root scanner verdict и runtime loading каждого host ещё предстоит проверить. [H8][H9][H12]; Codex/Claude contracts — [codex.md](codex.md), [claude.md](claude.md).

## Что CI может проверить без custom scripts

| Проверка | Native/official средство | Accounts и предел |
| --- | --- | --- |
| Hermes package admission/security findings | `hermes plugins validate . --json` или официальный action с pinned Hermes | Provider accounts не нужны для portable declarations; diagnostics могут остаться warnings [H21][H22] |
| Hermes discovery/load/registration | `hermes plugins doctor . --ci` | Без provider accounts; socket-blocked test, не authentication и не exact inventory gate [H19][H20] |
| Claude manifest/skill frontmatter/MCP JSON | `claude plugin validate . --strict --json` | Проверено без аккаунта; не подключает сервисы и не оценивает поведение; [H27], детали в [claude.md](claude.md) |
| Поведение Claude с provider stubs | `claude plugin eval`, native Markdown mocks и graders | Требуется model account/budget; provider calls можно исключить; не Hermes acceptance; [H26], детали в [claude.md](claude.md) |
| Codex package/skill deterministic validation | Отдельный native CLI validator/eval в 0.160.0 не найден | Bundled `quick_validate.py` — официальный Python helper, исключён ограничением; [codex.md](codex.md), sources 2026-10-05 |
| Whitespace diff | `git diff --check` | Официальный Git command без аккаунта; не schema/behavior validation; [Git documentation](https://git-scm.com/docs/git-diff#Documentation/git-diff.txt---check), доступ 2026-10-05 |

**Что требует custom logic, если нужен автоматический gate:** exact Hermes inventory обоих skills/ожидаемых MCP и нулевые component diagnostics; синхронность metadata двух manifests; проверка всех reference links; произвольная stateful provider simulation; единая межплатформенная behavioral scoring/release policy. Исследованные official commands не предоставляют такой совокупный gate. Standard `jq -e` с authored expression мог бы проверить нулевые warnings без отдельного parser/script-файла, но это уже собственная assertion logic, а не native host validator; exact inventory оно само по себе тоже не подтверждает. Поэтому при строгом «no custom code» остаются доступные native checks плюс ручное чтение reports и отдельная runtime acceptance. Основание границ: [H17][H20][H21][H26][H34], [codex.md](codex.md), source access **2026-10-05**.

Claude fixture scaffolding через `context.scaffold_script` тоже требует авторского Bash и выходит за принятое «no custom code». Простые prompt/grader/mock cases этого не требуют. Python validators/builders, custom MCP/proxy и generated copies не нужны предложенному минимальному layout и не включены в допустимый CI. [H26]; Claude/Codex источники и проверки — в соответствующих platform files, дата доступа **2026-10-05**.

## Nix и открытая приёмка

Vendor документирует Nix/NixOS как **Tier 2, best effort**, предоставляет flake, NixOS/Home Manager modules. Нужно pin фактическую пару Hermes/nixpkgs и проводить acceptance на реальном сервере; его установленная версия этой работой не проверялась. [H7]

Остаются открыты: final root scanner verdict, установка exact JediKit commit, actual qualified skill names и invocation, effective MCP configuration/OAuth/read-only discovery, toolsets memory/cron, scheduler timezone/persistence/delivery, runtime loading общего MCP JSON в каждом host. Исходники и offline checks не заменяют эти результаты. Accounts и provider data не затрагивались. [H4][H5][H6][H12][H14][H17][H19]

## Первичные источники

Каждый source ниже проверен **2026-10-05**. Source inspection отделено от vendor docs и локальных запусков; ссылки на mutable docs не являются version pin.

- [H1] [Official latest release API](https://api.github.com/repos/NousResearch/hermes-agent/releases/latest), доступ 2026-10-05.
- [H2] [Release 0.21.5 / v2026.9.24](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.9.24), доступ 2026-10-05.
- [H3] [Plugins docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins/), доступ 2026-10-05.
- [H4] [Skills docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/), доступ 2026-10-05.
- [H5] [Cron docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron/), доступ 2026-10-05.
- [H6] [Memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory/), доступ 2026-10-05.
- [H7] [Nix setup docs](https://hermes-agent.nousresearch.com/docs/getting-started/nix-setup/), доступ 2026-10-05.
- [H8] [Plugin discovery](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/plugins_discovery.py#L30), доступ 2026-10-05.
- [H9] [Portable package parser, containment and MCP translation](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/agent_plugins.py), доступ 2026-10-05.
- [H10] [Plugin source parsing, clone, scanner and install](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/plugins_cmd.py#L225), доступ 2026-10-05.
- [H11] [GitHub Skills Hub source](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/tools/skills_hub_github.py#L264), доступ 2026-10-05.
- [H12] [Plugin security scanner](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/tools/plugin_guard.py), доступ 2026-10-05.
- [H13] [Skill content scanner](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/tools/skills_guard.py#L595), доступ 2026-10-05.
- [H14] [Native MCP OAuth configuration](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/mcp_config.py#L538), доступ 2026-10-05.
- [H15] [Agent Plugins 1.0.0 specification](https://agent-plugins.org/specification), доступ 2026-10-05.
- [H16] [Plugin/skill namespace and MCP naming](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/plugins_manifest.py#L60), доступ 2026-10-05.
- [H17] [Portable loader/registration](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/plugins_loader.py#L551), доступ 2026-10-05.
- [H18] [MCP docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp/), доступ 2026-10-05.
- [H19] [Doctor isolation and runtime checks](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/plugin_dev.py#L31), доступ 2026-10-05.
- [H20] [Doctor CLI and CI exit policy](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/plugins_cmd.py#L2405), доступ 2026-10-05.
- [H21] [Portable plugin validation](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/plugin_validate.py#L587), доступ 2026-10-05.
- [H22] [Official plugin validation action](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/.github/actions/plugin-validate/action.yml), доступ 2026-10-05.
- [H23] [Claude plugin manifest reference](https://code.claude.com/docs/en/plugins-reference), доступ 2026-10-05.
- [H24] [OpenAI portable plugin authoring](https://developers.openai.com/plugins/build/plugins), доступ 2026-10-05.
- [H25] [Codex 0.160.0 portable parser](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/core-plugins/src/agent_plugin_manifest.rs), доступ 2026-10-05.
- [H26] [Claude native eval cases, mocks and CI](https://code.claude.com/docs/en/plugin-evals), доступ 2026-10-05.
- [H27] [Claude native plugin CLI](https://code.claude.com/docs/en/plugins/cli-reference), доступ 2026-10-05.
- [H28] [Plugin skill registration contract](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/plugins.py#L993), доступ 2026-10-05.
- [H29] [Skill command scanning and preload](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/agent/skill_commands.py#L405), доступ 2026-10-05.
- [H30] [Chat skills CLI parser](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/_parser.py#L238), доступ 2026-10-05.
- [H31] [Native memory tool and schema](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/tools/memory_tool.py#L207), доступ 2026-10-05.
- [H32] [Cron skill prompt loading](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/cron/scheduler_prompt.py#L42), доступ 2026-10-05.
- [H33] [Validator/doctor subcommand flags](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/subcommands/plugins.py#L54), доступ 2026-10-05.
- [H34] [ValidationReport JSON and warnings](https://github.com/NousResearch/hermes-agent/blob/f97608f178d1ffeca59860195ab7da295f7c8e5f/hermes_cli/plugin_validate.py#L37), доступ 2026-10-05.
