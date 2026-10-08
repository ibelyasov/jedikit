# Hermes Agent: текущий контракт и общий layout JediKit

Дата исходного исследования: **2026-10-05**, консолидация — **2026-10-06**. Плагин содержит только скиллы и контракт ожидаемых инструментов; подключения предоставляет хост ([ADR 0005](../../docs/adr/0005-one-source-host-connections.md)). Датированные snapshots не подтверждают runtime текущего пакета.

## Версия и типы доказательств

В проверке 2026-10-05 последний stable release официального GitHub API — **0.21.5 / `v2026.9.24`**, опубликован 2026-09-24, commit **`f97608f178d1ffeca59860195ab7da295f7c8e5f`**. Source facts ниже закреплены этим commit. Latest release повторно не аттестован 2026-10-06; текущие web docs могут описывать более новый `main`. [PL-H-1](../sources.md), [PL-H-2](../sources.md)

- **Независимо исследовано:** public release metadata и pinned source, включая parser, discovery, scanner, loader и validators. Это чтение реализации, а не runtime test.
- **Vendor claims:** текущие официальные docs о skills, memory, cron и plugins; их следует сверять с фактическим deployment. [PL-H-3](../sources.md), [PL-H-4](../sources.md), [PL-H-5](../sources.md), [PL-H-6](../sources.md)
- **Anecdote:** отзывы и старые пользовательские сессии не использованы как доказательство.

В исследовании 2026-10-05 Hermes локально не был установлен. Установка, validators Hermes, OAuth, MCP calls, memory writes, cron jobs при консолидации не выполнялись. Ни исходники, ни проверка package schema не подтверждают работающую авторизацию провайдеров.

## Root install и границы пакета

Portable package может находиться в repo root: `plugin.json`, `skills/<name>/SKILL.md`. Discovery пропускает foreign harness manifest directories `.claude-plugin/` и `.codex-plugin/`; parser выбирает portable root manifest. Это подтверждение реализации 0.21.5, не выполненная установка финального JediKit. По [ADR 0005](../../docs/adr/0005-one-source-host-connections.md) плагин не объявляет MCP и секреты ни для одного хоста. На Hermes владельца подключения предоставляет clanwright. [PL-H-8](../sources.md), [PL-H-9](../sources.md)

Installer принимает `owner/repo`, `owner/repo/path/to/plugin`, Git URLs и subdirectory fragment. `--ref` принимает полный 40-character commit SHA; branch, tag и abbreviated SHA не удовлетворяют проверенному exact-ref контракту. Subdirectory install использует sparse checkout. Пример будущей установки ниже; SHA должен принадлежать JediKit, не Hermes. [PL-H-10](../sources.md), [PL-H-3](../sources.md)

```sh
hermes plugins install ibelyasov/jedikit --ref <FULL_JEDIKIT_COMMIT_SHA> --enable
```

Skills Hub — другой механизм установки отдельного skill, например из `owner/repo/skills/name`. Он получает default-branch tree и revision для согласованного чтения bundle; его нельзя приравнивать к `plugins install --ref`. Plugin install предпочтительнее для общей package identity двух skills. Последнее — проектный вывод. [PL-H-11](../sources.md), [PL-H-4](../sources.md)

Symlink из plugin subdirectory наружу к корневому `skills/` нарушает containment: resolved path выходит за plugin root, parser его отклоняет, scanner выдаёт critical `symlink_escape`. Поэтому принят root install с настоящим `skills/`, без таких ссылок и копий. [PL-H-9](../sources.md), [PL-H-12](../sources.md)

## Discovery и scanner — разные проверки

Security scanner рекурсивно проверяет содержимое выбранного package, включая hidden directories; исключаются конкретные VCS/cache/environment names, например `.git`, `node_modules`, `.venv`. Foreign manifest directories пропускаются discovery, но их содержимое участвует в scanner. Само имя `.claude-plugin/`, `.codex-plugin/` или `.mcp.json` не блокируется; инструкции, scripts, documentation и symlinks могут дать findings. [PL-H-8](../sources.md), [PL-H-12](../sources.md), [PL-H-13](../sources.md)

Install вызывает scanner до swap: `safe` допускается, `caution` требует подтверждения либо `--force`, `dangerous` блокируется даже с `--force`. Следовательно, отсутствие parser incompatibility не гарантирует успешный root install всего repository. Final scanner verdict остаётся открытым; обход scanner не предлагается. [PL-H-10](../sources.md), [PL-H-12](../sources.md)

## mcp.json, .mcp.json и OAuth

Portable loader читает **только `mcp.json`** с точным Agent Plugins schema URI и top-level `$schema`/`mcpServers`. `.mcp.json` не является fallback и не конкурирует по precedence. Если рядом есть native YAML plugin manifest, он имеет приоритет над portable `plugin.json`. [PL-H-9](../sources.md), [PL-H-10](../sources.md)

Remote portable entry допускает `type: streamable-http`, `url`, `headers`; translation сохраняет URL/non-empty headers и добавляет `strict_redirect_headers: true`. **`auth: oauth` теперь нельзя описывать как просто потерянное поле:** unknown `auth` даёт diagnostic `unknown remote field`, и entry пропускается. В native host MCP configuration `auth: oauth` поддерживается отдельно. Portable specification тоже оставляет authentication клиенту и не определяет такое поле. [PL-H-9](../sources.md), [PL-H-14](../sources.md), [PL-H-15](../sources.md)

Plugin MCP server names не получают длинный skill namespace. Duplicate plugin server names пропускаются с warning; native configuration имеет приоритет по naming contract. Поэтому plugin inventory, effective native config и работающая OAuth connection — отдельные утверждения. Хост предоставляет SingularityApp MCP и операции Habitify с бизнес-контрактом REST/OpenAPI v2 по [ADR 0001](../../docs/adr/0001-habitify-via-rest.md). Подключения предоставляет хост; здесь connections не создавались. [PL-H-16](../sources.md), [PL-H-17](../sources.md), [PL-H-18](../sources.md)

## Naming, explicit invocation и native features

Portable namespace вычисляется как `agent-plugin-<slug>-<sha256(key)[:8]>`; полное имя skill следует получать из текущего discovery. Нельзя обещать стабильный identifier `jedikit:jedikit-habits`: изменение registry key может изменить namespace. [PL-H-16](../sources.md)

Plugin skills доступны в `skills_list` и разрешаются по qualified name в `skill_view`, не копируются в `~/.hermes/skills` и не включаются в system prompt `<available_skills>`. Slash-command scanner обходит physical project/local/external directories, а не plugin registry: нельзя обещать автоматический `/namespace:skill` для portable plugin. Проверенный explicit preload — `hermes chat --skills '<EXACT_QUALIFIED_SKILL_NAME>'`; parser передаёт identifier в `skill_view`. Эти source contracts не проверены выполнением с моделью. [PL-H-28](../sources.md), [PL-H-29](../sources.md), [PL-H-30](../sources.md)

Cron поддерживает attached skills через повторяемый `--skill`; проверенный identifier нужно получать из discovery, а не угадывать namespace. Source принимает `skills` list/string и legacy `skill`, загружает через `skill_view`, добавляет text в prompt перед injection scan. Missing skill логируется и пропускается: успешная job не доказывает загрузку нужного skill. Сам Markdown skill не предоставляет capabilities: native tools доступны по effective host configuration/toolsets. [PL-H-4](../sources.md), [PL-H-5](../sources.md), [PL-H-32](../sources.md)

Native memory хранится в Hermes profile и доступна через `memory`; она не становится общим хранилищем Claude/Codex. Source tool schema: target `memory|user`, actions `add|replace|remove`, `content` для add/replace, `old_text` для replace/remove; есть atomic `operations` array. Dynamic schema может сузить targets по host config. По [ADR 0006](../../docs/adr/0006-memory-holds-settings-only.md) JediKit сохраняет только настройки: timezone, рабочие дни, окна обзоров, режимы поддеревьев и ID выбранных привычек. Состояния обзоров и даты их завершения не сохраняются. Наличие native memory/cron не подтверждает inference, persistence, timezone или delivery на сервере владельца. [PL-H-5](../sources.md), [PL-H-6](../sources.md), [PL-H-31](../sources.md)

Описание инструмента `memory` в Hermes 0.21.5 направляет предпочтения пользователя «для этого вида работы» в скилл через `skill_manage`, а память оставляет для фактов, нужных в каждой сессии; лимиты store — 2 200 символов для `memory` и 1 375 для `user`. Запись при включённом `memory.write_approval` ставится в очередь (`staged`, `pending_id`, `/memory pending`). На хосте владельца setup `jedikit-calendar` по этой подсказке создал ожидающие изменения файлов скилла вместо записи в память, хотя скиллы подключены из `/nix/store` только для чтения. Поэтому скиллы JediKit явно называют инструмент `memory` и запрещают `skill_manage` для настроек ([ADR 0006](../../docs/adr/0006-memory-holds-settings-only.md)). [PL-H-31](../sources.md), [PL-H-MEMORY-0.21.5](../sources.md), [CLANWRIGHT-SETUP-2026-10-08](../sources.md)

Вне plugin install возможен `skills.external_dirs`, указывающий на canonical source без копирования. Docs предупреждают: агент может изменять external directories при наличии filesystem write permissions. Это отдельный deployment path, который не устанавливает portable MCP package автоматически. Для выбранного package root этот обход не нужен. [PL-H-4](../sources.md)

## Официальные validators и CI

В source 0.21.5 подтверждены commands:

```sh
hermes plugins doctor . --ci
hermes plugins validate . --json
```

Doctor копирует package во временный `HERMES_HOME`, выполняет discovery/load/registration и блокирует Python socket connects. Portable loader не импортирует Python entrypoint. Для декларативного package эта проверка не нуждается в provider accounts; установка самого Hermes/dependencies может требовать сети. Это source-derived вывод, команды здесь не запускались. Doctor не является OS sandbox для произвольного native plugin code. [PL-H-19](../sources.md), [PL-H-17](../sources.md)

`--ci` даёт exit `1` при `report.ok == false`, но doctor не вызывает install scanner. `plugins validate` включает scanner и portable validation. Его parser имеет `--json` и `--install-deps`, но не `--ci`, `--strict` или `--fail-on-warnings`; doctor имеет `--ci`, но не `--json`. **Оба инструмента имеют предел:** portable loader продолжает работу после component diagnostics, а validator превращает portable diagnostics в warnings. Поэтому exit `0` сам по себе не доказывает присутствие обоих skills и необходимых инструментов хоста. [PL-H-10](../sources.md), [PL-H-21](../sources.md), [PL-H-17](../sources.md), [PL-H-33](../sources.md)

Официальный GitHub Action имеет inputs только `path` и `hermes-ref`, устанавливает Hermes и запускает `plugins validate`; default `hermes-ref` — `main`, для release checks нужно явно pin revision. `fail-on-warnings` input отсутствует. Этот action не выполнялся. Отдельный строгий native flag «zero component diagnostics + exact expected inventory» в исследованных ветвях отсутствует. JSON report предоставляет `ok`, `checks`, `warnings`; warnings не меняют exit code. [PL-H-22](../sources.md), [PL-H-21](../sources.md), [PL-H-33](../sources.md), [PL-H-21](../sources.md)

## Принятый layout и область поддержки

По [ADR 0005](../../docs/adr/0005-one-source-host-connections.md) корневой `plugin.json` обслуживает Hermes/Codex, `.claude-plugin/plugin.json` — Claude Code, а настоящий корневой `skills/` содержит два независимых скилла. Router skill, generated copies, MCP declarations, agents metadata и собственный runtime не входят в пакет. Каждая operational reference остаётся внутри соответствующего skill.

Natural-language выбор по descriptions — целевой UX; explicit fallback Hermes использует identifier из discovery. Установка плагина не подключает провайдеры ни на одном хосте. `tools.json` задаёт базовые имена без host prefix, серверы `singularity`/`habitify`, доступ `read`/`write` и `required` у Habitify. При отсутствии tools агент называет недостающие операции и рекомендует подключить их на хосте; ничего не устанавливает. SingularityApp использует официальный hosted MCP; Habitify — REST/OpenAPI v2 как бизнес-контракт, с OpenAPI→MCP-адаптером хоста или эквивалентом с теми же именами. Ключ находится только у адаптера. Официальный Habitify MCP отвергнут из-за неполноты операций. Подробнее: [Claude Code](claude.md), [Codex](codex.md), [ADR 0001](../../docs/adr/0001-habitify-via-rest.md).

## Что CI может проверить без custom scripts

| Проверка | Native/official средство | Accounts и предел |
| --- | --- | --- |
| Hermes package admission/security findings | `hermes plugins validate . --json` или официальный action с pinned Hermes | Provider accounts не нужны для portable declarations; diagnostics могут остаться warnings [PL-H-21](../sources.md), [PL-H-22](../sources.md) |
| Hermes discovery/load/registration | `hermes plugins doctor . --ci` | Без provider accounts; socket-blocked test, не authentication и не exact inventory gate [PL-H-19](../sources.md), [PL-H-10](../sources.md) |
| Claude manifest/skill frontmatter | `claude plugin validate . --strict --json` | Проверено без аккаунта; не подключает сервисы и не оценивает поведение; [PL-C-6](../sources.md), детали в [claude.md](claude.md) |
| Codex package/skill deterministic validation | Отдельный native CLI validator в 0.160.0 не найден | См. [Codex](codex.md); runtime здесь не проверяется |
| Whitespace diff | `git diff --check` | Не schema/behavior validation |

По [ADR 0004](../../docs/adr/0004-no-custom-code.md) собственные автоматические gates, генераторы и authored assertion scripts не добавляются. Native reports читаются вместе с фактическим inventory: exit code не заменяет проверку обоих skills. Независимое агентное ревью дополняет validators и `git diff --check`; модельные прогоны не входят в проверку проекта.

## Непроверенные слои

Остаются непроверенными установка exact JediKit commit, actual qualified skill names и invocation, host tool discovery/OAuth, memory/cron, scheduler timezone/persistence/delivery. Исходники и статические проверки не подтверждают эти результаты. Accounts и provider data этой работой не затрагивались. [PL-H-4](../sources.md), [PL-H-5](../sources.md), [PL-H-6](../sources.md), [PL-H-14](../sources.md)

## Источники

Полные citations и объём доступа — в [реестре источников](../sources.md). Pinned source inspection 2026-10-05 и повторное чтение документации 2026-10-06 различаются в поле доступа.

## Датированные наблюдения прежней среды

Исследование **2026-09-13** наблюдало Hermes **0.20.6 (2026.8.27)**, public checkout `b4b7727ea07681b40402de411ddd000bb3c439fc`; тогда latest release был 0.21.2 / `v2026.9.11`. Parser и doctor прежнего skills-only пакета обнаружили оба skills. Habit identifier `agent-plugin-jedikit-805a716c:jedikit-habits` разрешался через `skill_view`; bare name и `jedikit:jedikit-habits` — нет. Это старое наблюдение, а не текущий identifier или runtime новых исходников. Срез 2026-08-08 относился к 0.20.0 / `v2026.8.3` и прежнему имени проекта; его catalog commands и channel list не являются нынешним контрактом. [PL-H-35](../sources.md)

YAML skill bundle — runtime alias уже доступных skills, tap — источник одиночных skills; это не эквивалент portable plugin install двух skills. Каждый skill остаётся самодостаточным: router не нужен для package identity, mixed request делится на два workflow с отдельными группами подтверждаемых операций. Это правило [jedikit-tasks](https://github.com/ibelyasov/jedikit/blob/43fc19e/skills/jedikit-tasks/SKILL.md) и [jedikit-habits](https://github.com/ibelyasov/jedikit/blob/43fc19e/skills/jedikit-habits/SKILL.md); vendor guarantee inter-skill dispatch из него не следует. [PL-H-4](../sources.md)

## Фильтры MCP и локальное исполнение

Следующие source facts прочитаны **2026-09-13** в public checkout `b4b7727e`; это не live security test. `tools.include` задаёт allowlist имён/globs, `tools.exclude` — исключения; при наличии обоих приоритет у include. Пустой `include: []` не регистрирует tools, отсутствие обоих разрешает все. Denylist может пропустить новый write-tool; широкий glob тоже может охватить будущие имена. Фильтр хоста не отзывает OAuth scope сервера. [PL-H-36](../sources.md)

Local terminal работает от пользователя ОС и не образует изолированную sandbox. Ограничения write_file/patch не ограничивают произвольный terminal process. Environment filtering terminal, execute_code и MCP различается; passthrough может вернуть переменные процессу. Проверенный код намеренно сохраняет общую AWS credential chain: нельзя утверждать, что все секреты хоста скрыты. JediKit не требует выдавать terminal дополнительные полномочия. [PL-H-37](../sources.md), [PL-H-39](../sources.md)

## Cron: preflight, время, стоимость и результаты

В срезе `b4b7727e` cron поддерживал per-job provider/model и snapshots неприкреплённых параметров. Preflight проверял provider auth, требуемую настройку skill и delivery; обнаруженная проблема могла блокировать inference. Drift guard мог остановить смену неприкреплённых provider/model. Однако некоторые ошибки preflight продолжали запуск, missing skill оставался skip-and-continue; snapshot мог отсутствовать при config error. Старые jobs и явные cron defaults имели исключения, fallback chain менял проверку primary auth. Preflight не гарантирует готовность. [PL-H-38](../sources.md), [PL-H-40](../sources.md)

В исследованном коде не был найден общий денежный/токенный budget cap. `approvals.cron_mode: deny` ограничивает опасные headless commands, а не расходы inference; drift guard тоже не бюджетный лимит. Это ограниченный source finding, не утверждение обо всех версиях. [PL-H-39](../sources.md)

IANA timezone влияет на cron; ISO timestamp без offset трактуется в configured zone. Код сохранял намерение местного времени и пересчитывал offset; определённый DST transition мог пропустить ожидающее срабатывание. «Каждое утро» требует явной зоны и cadence. Успешный разовый запуск не проверяет DST. [PL-H-40](../sources.md)

Попытка записывалась в `executions.db` до dispatch: claimed → running → completed/failed/unknown. Потерянное выполнение могло перейти в unknown без automatic retry; `hermes cron runs` предоставлял историю. Job record, факт попытки, ответ модели и delivery — отдельные наблюдения, которые нужно сопоставить при проверке runtime. `hermes cron run` в старой реализации разрешал exact job ID, затем case-insensitive name; неоднозначное имя требовало ID. Эти команды здесь не запускались. [PL-H-41](../sources.md)

По [ADR 0003](../../docs/adr/0003-no-unattended-writes.md) фоновые проверки JediKit только читают и предлагают изменения для weekly. Наличие host approvals или успешного cron не доказывает соблюдение этого контракта.

## Gateway: исторические границы доступа

Source `b4b7727e` отказывал в доступе без основания: pairing, platform/global allowlist, explicit allow-all или исключение trusted adapter. Pairing grants и allowlists объединялись; allowlist не отменял старый grant. Неизвестные DM с allowlist обычно игнорировались, без списка запускали pairing, email имел default ignore. Проверяется effective access, а не один список. Admin/user slash policy ограничивала slash commands, не обычный chat. Доступ к боту, разрешение tool и согласие изменить данные — разные границы. [PL-H-42](../sources.md), [PL-H-44](../sources.md), [PL-H-45](../sources.md)

## Организация коллекции skills: что переносимо

Исторический обзор **2026-09-13** сравнивал публичные коллекции: `openai/plugins` разделял marketplace и plugin, `anthropics/skills` группировал skills в Claude plugin, `anthropics/claude-plugins-official` представлял каталог отдельных sources/refs, `vercel-labs/agent-skills` использовал grouping metadata, `obra/superpowers` имел разные harness integration paths. Это примеры организации, не стандарты. Их полный текущий состав повторно не проверен; доступный repo не доказывает install/OAuth/runtime JediKit. [PL-X-1](../sources.md), [PL-X-2](../sources.md), [PL-X-3](../sources.md), [PL-X-4](../sources.md), [PL-X-5](../sources.md)

Package identity и router skill решают разные задачи. Router был бы полезен для явной классификации запроса или реально координирующего workflow с описанным отсутствием дочернего skill; широкий implicit description может конкурировать с domain skills, дублировать процедуры и создавать ложное впечатление dependency manager. В JediKit два самостоятельных скилла — [jedikit-tasks](https://github.com/ibelyasov/jedikit/blob/43fc19e/skills/jedikit-tasks/SKILL.md) и [jedikit-habits](https://github.com/ibelyasov/jedikit/blob/43fc19e/skills/jedikit-habits/SKILL.md) — обходятся без router. Skills стандарт задаёт каталог/frontmatter/relative resources, Agent Plugins — package manifest; ни один не гарантирует одинаковую host authentication или dispatch между skills. [PL-H-15](../sources.md)
