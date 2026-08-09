# Hermes Agent для `singularity-jedi`

> **Product overlay 2026-08-09:** заголовок сохраняет временное кодовое имя исследования. Релизный source — `jedikit`, рабочий skill — `jedikit-tasks`, без router; Hermes tap не обещается как atomic install-all. Cron предлагается только как подтверждённый host-native scheduler и всегда read-only; при недоступности skill лишь объясняет ограничение.

Срез на **2026-08-08**. Под Hermes Agent здесь понимается open-source CLI/gateway из репозитория NousResearch, а не семейство моделей Nous Hermes. Context7 сначала разрешил библиотеку `/nousresearch/hermes-agent` (релевантность высокая, но каталог версий там отстаёт); источником истины для этого среза взят официальный релиз **Hermes Agent v0.20.0 / `v2026.8.3`**, опубликованный 2026-08-03: [release](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3). Документация ниже привязана к этому тегу, а не к плавающему `main`.

## Короткий вывод для v1

Hermes закрывает слой «секретарь/шлюз/расписание»: gateway, каналы, cron, skills и MCP. Для `singularity-jedi` разумно оставить его **опциональной внешней зависимостью**: обнаружить бинарник и конфиг, показать безопасные команды, но не устанавливать провайдеры, каналы, skills или MCP автоматически. Первый v1-профиль: один явно выбранный канал (Telegram, если он подтверждён пользователем), allowlist/DM-pairing, `approvals.mode: manual` и `cron_mode: deny`, MCP только с include-списком инструментов, cron-модель закреплена явно.

## Возможности, доказательства и решение

| Возможность | Доказательство (релизная документация) | Ограничение / риск | Решение v1 для `singularity-jedi` |
|---|---|---|---|
| Skills как on-demand `SKILL.md` | Skills живут в `~/.hermes/skills/`, bundled/Hub/agent-created используют один каталог; каждый skill становится slash-командой: [Skills System](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/features/skills.md). | Skill может быть изменён/удалён агентом; индекс всё равно добавляет prompt/tool overhead. | Поддержать локальный skill и явный путь; не считать наличие файла доказательством активной загрузки — проверять `hermes skills list` и `/skills`. |
| Установка и discovery skills | `hermes skills browse/search/inspect/install/list/check/update/audit/uninstall/reset`; пример `hermes skills install openai/skills/k8s`; прямой URL: `hermes skills install https://…/SKILL.md --name …` ([CLI](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/reference/cli-commands.md), [Skills Hub](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/features/skills.md)). | Все Hub-установки проходят сканер. `--force` обходит только caution/warn, но не `dangerous`; community-источники не равны official. | В v1 только `inspect → install → audit`; `--force` не использовать по умолчанию. |
| Публичный каталог / marketplace | Источники: `official` (`optional-skills/` в самом репо), `skills-sh`, `well-known`, GitHub/taps, ClawHub, LobeHub, browse.sh, URL ([список источников](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/features/skills.md)). `hermes skills tap add owner/repo` добавляет GitHub-каталог; layout — `skills/<slug>/SKILL.md`. | Нет доказательства единого first-party Hermes Marketplace с публикацией, модерацией и SLA. ClawHub прямо назван third-party; новый tap получает `community` trust. `hermes skills publish … --to github --repo owner/repo` означает публикацию в GitHub, а не выпуск в централизованный магазин. | Не зависеть от индекса Hub в v1: поставлять skill локально или через проверенный private/public GitHub tap; публикацию не выполнять без отдельного решения. |
| MCP: local stdio и remote HTTP | `mcp_servers` в `~/.hermes/config.yaml`; stdio через `command/args/env`, HTTP через `url/headers`; стандартная установка уже содержит MCP ([MCP](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/features/mcp.md)). | MCP запускает внешний код/процессы и не является sandbox. Каталожный manifest может делать `git clone`, `pip install`/`npm install`, затем запускать код; review Nous — не изоляция. | По умолчанию MCP выключен; подключать только после чтения manifest/source и отдельного allowlist. |
| Каталог Nous-approved MCP | `hermes mcp`, `hermes mcp catalog`, `hermes mcp install <name>`; entries в `optional-mcps/`, disabled by default, community submission tier нет ([MCP catalog](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/features/mcp.md)). | OAuth/API key могут записываться в `~/.hermes/.env`; probe сервера может не сработать, тогда install всё равно завершится с default tools. OAuth dynamic registration не подходит некоторым серверам (например, Google Drive/Atlassian — нужен pre-registered client). | Для v1 предпочесть ручной `mcp_servers` + `tools.include`; `hermes mcp test <name>` после настройки. |
| MCP tool permissions | `enabled: false`, `tools.include`, `tools.exclude`, fnmatch-globs; при обоих `include` имеет приоритет; зарегистрированные имена получают префикс `mcp_<server>_<tool>` ([filtering](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/features/mcp.md)). | `exclude` — denylist, поэтому новый инструмент может появиться после обновления сервера; include безопаснее. MCP получает только safe env (`PATH`, `HOME`, …) плюс явный `env`; обычный `terminal.env_passthrough` на MCP не действует ([security](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/security.md)). | Только `include`, минимальные `env`, отдельные credentials; после каждого обновления — `hermes mcp list/test` и повторный review. |
| Cron / scheduled tasks | In-chat `/cron add …`, CLI `hermes cron create …`, unified tool `cronjob(action="create|list|update|pause|resume|run|remove", …)`; gateway ticks every 60 s, jobs хранятся в `~/.hermes/cron/jobs.json`, попытки — в `executions.db` ([Scheduled Tasks](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/features/cron.md)). | Повторяющиеся jobs исполняются только пока живёт gateway/его trigger. Cron-run не может создавать новые cron jobs; по умолчанию новая изолированная agent session и не получает repo `AGENTS.md` без `workdir`. | Сначала проверить обычный chat/gateway, затем один тестовый job; `workdir` задавать абсолютным путём только явно. |
| Форматы расписания | One-shot: `30m`, `2h`, `1d`; interval: `every 30m`, `every 2h`, `every 1d`; cron: `0 9 * * *`; ISO timestamp: `2026-03-15T09:00:00`; `repeat=N` ограничивает повторы ([schedule formats](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/features/cron.md)). | В релизной документации не зафиксированы все timezone/DST правила для наивного ISO/cron выражения; это надо подтвердить в установленном runtime. | Для v1 использовать явно наблюдаемый `every …` или cron и проверять `next_run_at`/`hermes cron list`; не обещать timezone semantics без runtime-проверки. |
| Cron model / spend guard | При fire-time порядок: per-job pin → `cron.model`/`cron.model_provider` → global default. Без pin Hermes snapshots provider/model при создании и при смене global default fail-closed; `cron.model_drift_guard: false` отключает защиту ([cron model](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/features/cron.md)). | Непривязанный job может неожиданно остановиться (защита) или начать тратить деньги на новый provider (если guard отключён). | Всегда задавать cron-fleet модель: `hermes config set cron.model <model>` и при необходимости `cron.model_provider`; per-job pin — для критичных задач. Guard не отключать. |
| Что делает scheduled job | При tick: fresh `AIAgent`, optional attached skills, prompt до конца, auto-delivery final response, metadata/next run. Skills можно прикрепить повторяемым `--skill`; `workdir` включает context-файлы и serializes workdir jobs. | Session не видит delivered сообщение (fire-and-forget по умолчанию); `workdir`-jobs идут последовательно на tick. Ошибки preflight блокируют запуск без LLM-вызова. | Prompt должен быть самодостаточным; после создания выполнить `hermes cron run <id_or_name>` и проверить `hermes cron list`/`hermes cron status` (для истории использовать `hermes cron runs <id> --limit 20`, если подкоманда доступна в установленной версии). |
| No-agent cron | `hermes cron create "every 5m" --no-agent --script memory-watchdog.sh --deliver telegram`; stdout доставляется verbatim, пустой stdout — silent, non-zero/timeout — alert; script только внутри `$HERMES_HOME/scripts/`, env credentials санитизируется ([no-agent](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/features/cron.md)). | Это уже локальное выполнение скрипта с правами Hermes; нет модели/LLM/fallback. | Использовать для детерминированных watchdog/health-check; для содержательного решения — обычный agent cron с pin модели. |
| Каналы уведомлений | Gateway поддерживает Telegram, Discord, Slack, Google Chat, WhatsApp/Cloud API, Signal, SMS, Email, Home Assistant, Mattermost, Matrix, DingTalk, Feishu/Lark, WeCom, Weixin, BlueBubbles/Photon, QQ, Yuanbao, Teams, LINE, ntfy, Webhooks и др. ([Messaging Gateway](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/messaging/index.md)). | Возможности различаются по каналу (threads/media/streaming/scopes); credentials/scopes и home channel настраиваются отдельно. | В v1 выбрать один подтверждённый канал. `hermes gateway setup`, затем `hermes gateway install/start/status`; не включать остальные платформы. |
| Cron delivery targets | `origin`, `local`, `telegram`, `telegram:<chat_id>`, `telegram:<chat_id>:<thread_id>`, `discord:#channel`, `slack`, `whatsapp`, `signal`, `matrix`, `email`, `sms`, `all`, `telegram,discord`, `origin,all`; final response доставляется автоматически ([delivery table](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/features/cron.md)). | `all` разрешается в момент fire-time и при отсутствии home channels фиксируется как delivery failure; Telegram root DM в topic mode — system lobby, для reply нужен `TELEGRAM_CRON_THREAD_ID`. | Для первой проверки — `deliver: local` или один exact Telegram target; `all` не использовать до проверки каждого home channel. |
| Сценарий «только отправить текст» | `hermes send --to <target> "message"`, `--file`, `--list`; для bot-token платформ gateway не нужен, credentials берутся из `~/.hermes/.env` и `config.yaml` ([CLI](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/reference/cli-commands.md)). | `hermes send` не запускает LLM и не решает, что сказать; plugin-платформам всё ещё нужен живой gateway. | Для детерминированных уведомлений `hermes send`; не имитировать их через agent prompt. |
| Onboarding / provider | Install: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`; `hermes setup --portal` — OAuth Nous + Tool Gateway; `hermes setup` — Full/Blank Slate; `hermes model` — provider/model; затем `hermes gateway setup` ([Quickstart](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/getting-started/quickstart.md)). | Provider, модель, credentials и канал — пользовательский выбор; Blank Slate отключает skills/MCP/cron по умолчанию. | Skill не должен сам запускать onboarding или выбирать provider/channel; только показать следующий безопасный шаг и попросить подтверждение. |
| First-touch profile onboarding | `onboarding.profile_build: "ask"` (default) или `"off"`; offer consent-gated, at most once, connected accounts не читаются молча ([configuration](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/configuration.md)). | Это поведение первого gateway message, не полноценная identity/access policy; состояние `onboarding.seen` внутреннее. | В v1 рекомендовать `profile_build: off`, пока пользователь явно не выбрал profile-building. |
| Permissions и dangerous commands | Gateway по умолчанию deny для незнакомых пользователей; allowlists в `.env` (`TELEGRAM_ALLOWED_USERS=…`, `GATEWAY_ALLOWED_USERS=…`) или DM pairing (`hermes pairing approve …`). Slash admin/user split — `allow_admin_from`, `user_allowed_commands` в `~/.hermes/gateway-config.yaml` ([Security](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/user-guide/security.md), [Slash permissions](https://github.com/NousResearch/hermes-agent/blob/v2026.8.3/website/docs/reference/slash-commands.md)). | `approvals.mode: off`/`--yolo` отключает approval; `local` backend работает прямо на host, guards — defense-in-depth, не sandbox. Контейнерные backends дают изоляцию; hardline blocklist нельзя обойти. | В v1 `approvals.mode: manual`, `approvals.cron_mode: deny`, explicit allowlist/pairing, Docker/SSH для недоверенных runs; `--yolo` не использовать. |

## Точные команды и минимальный probe-порядок

Команды ниже только для будущей проверки (в этом исследовании ничего не устанавливалось и не запускалось):

```bash
# 0. Базовый факт: это Hermes Agent и какой release установлен
command -v hermes
hermes version
hermes doctor
hermes status --deep

# 1. Реальный provider/chat перед gateway/cron
hermes model
hermes chat -q "Ответь ровно: HERMES_PROBE_OK"
hermes --continue

# 2. Skills: каталог -> просмотр -> установка -> аудит
hermes skills browse --source official
hermes skills search <query>
hermes skills inspect <source>/<path>
hermes skills install <source>/<path>
hermes skills list --source all
hermes skills audit

# 3. MCP: список -> test -> inspect, а не blind install
hermes mcp catalog
hermes mcp list
hermes mcp test <name>
# custom stdio/HTTP: edit ~/.hermes/config.yaml, then:
hermes mcp add <name> --command <cmd> --args ...
hermes mcp configure <name>

# 4. Канал/gateway
hermes gateway setup
hermes gateway install
hermes gateway start
hermes gateway status

# 5. Cron: сначала local, затем exact channel
hermes config set cron.model <model>
hermes cron create "every 30m" "Return one-line health status" --deliver local --name health
hermes cron list
hermes cron run health
hermes cron runs health --limit 20
hermes cron status
```

Для краткого одноразового уведомления без LLM:

```bash
hermes send --to telegram:<chat_id> "probe"
```

## Явные неизвестные / что не следует обещать

1. Context7 каталог `/nousresearch/hermes-agent` на момент запроса перечислял версии лишь до `v2026.6.5`; это не доказательство версии установленного runtime. Проверять нужно `hermes version` и свежий release.
2. Без выбранного provider/model нельзя подтвердить, что cron реально вызовет inference; без credentials/scopes нельзя подтвердить конкретный канал. Документация не задаёт универсальное timezone/DST-правило для cron/наивного ISO timestamp — проверять `next_run_at` в runtime.
3. Skills Hub — агрегатор источников, а не доказанный единый marketplace с гарантированной публикацией/модерацией/индексацией. `hermes skills publish --to github` публикует в GitHub; ClawHub/LobeHub/skills.sh/well-known остаются внешними или community-источниками.
4. MCP catalog review не означает безопасность bootstrap-кода или server-side permissions. Нужно ограничивать `tools.include`, credentials и backend отдельно; `terminal` на local host не изолирован.
5. В рамках задачи установка, публикация, подключение канала и live probe намеренно не выполнялись; приведённые команды — проверочный runbook, а не отчёт о текущем локальном состоянии.
