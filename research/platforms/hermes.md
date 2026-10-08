# Hermes Agent: хост JediKit

Досье описывает, как Hermes Agent подключает и исполняет пять скиллов JediKit: `jedikit-tasks`, `jedikit-habits`, `jedikit-calendar`, `jedikit-planning` и навигатор `jedikit`. Принятые решения — [ADR 0005](../../docs/adr/0005-hermes-plugin-host-connections.md), [ADR 0003](../../docs/adr/0003-no-unattended-writes.md), [ADR 0006](../../docs/adr/0006-memory-holds-settings-only.md), [ADR 0013](../../docs/adr/0013-clarification.md) и [ADR 0014](../../docs/adr/0014-confirmations.md); здесь — их основания.

## Версия и типы доказательств

Последний stable release на 2026-10-08 — **0.21.5 / `v2026.9.24`**, опубликован 2026-09-24, commit **`f97608f178d1ffeca59860195ab7da295f7c8e5f`**. Source facts ниже закреплены этим commit; чтения 2026-10-05 и 2026-10-08 различаются в реестре. [PL-H-1](../sources.md), [PL-H-2](../sources.md)

- **Чтение source:** parser, discovery, loader, validators, skills, MCP, Tool Search, `clarify`, `memory`, cron на pin. Это чтение реализации, не runtime test.
- **Vendor docs:** текущие официальные страницы о skills, plugins, MCP, memory, cron и Nix; они могут описывать более новый `main`. [PL-H-3](../sources.md), [PL-H-4](../sources.md), [PL-H-5](../sources.md), [PL-H-6](../sources.md), [PL-H-7](../sources.md), [PL-H-18](../sources.md)
- **Конфигурация владельца:** чтение clanwright HEAD `6641f66`; декларативная конфигурация, не подтверждение deployment. [PL-H-66](../sources.md)
- **Live-наблюдение:** одно сообщение clanwright о setup `jedikit-calendar` ниже. [CLANWRIGHT-SETUP-2026-10-08](../sources.md)

Hermes на машине исследования не установлен. Установка, validators, OAuth, MCP calls, записи `memory`, задания cron и поведение модели здесь не выполнялись.

## Два способа установки

| | `skills.external_dirs` | `hermes plugins install` |
| --- | --- | --- |
| Что подключается | Каталог `skills/` закреплённой ревизии; ревизию задаёт источник каталога (checkout, Nix input) | Репозиторий с portable `plugin.json` в корне, `--ref <FULL_SHA> --enable` |
| Имена скиллов | Голые: `jedikit-tasks` | `agent-plugin-jedikit-805a716c:jedikit-tasks` |
| Индекс скиллов в system prompt | Да: имя и первые 57 символов `description` + `...` | Нет |
| Поиск и загрузка | Индекс, `skills_list`, `skill_view` | `skills_list`, `skill_view`, preload `hermes chat --skills '<имя>'` |
| Slash `/jedikit-tasks` | Да, scanner обходит физические каталоги | Не гарантирован: scanner не читает plugin registry |
| Защита от записи | Не даёт Hermes: обеспечивается файловой системой (у владельца — Nix store) | Plugin skills только для чтения |

Основания: external directories и их приоритет `project → local → skills.create_dir → external_dirs`, предупреждение, что внешний каталог не является границей защиты от записи, и подхват изменений в новой сессии — [PL-H-4](../sources.md) (vendor docs, 2026-10-08). Индекс и усечение description — [PL-H-50](../sources.md), [PL-H-51](../sources.md); `skills_list`/`skill_view` — [PL-H-49](../sources.md), [PL-H-48](../sources.md), [PL-H-28](../sources.md); slash scanner — [PL-H-29](../sources.md); preload — [PL-H-30](../sources.md).

**Plugin install.** Installer принимает `owner/repo`, subdirectory и Git URLs; `--ref` — только полный 40-символьный commit SHA, branch, tag и сокращённый SHA не подходят. Discovery выбирает portable root manifest. Перед установкой выполняется scanner: `safe` проходит, `caution` требует подтверждения или `--force`, `dangerous` блокируется и с `--force`. [PL-H-10](../sources.md), [PL-H-8](../sources.md), [PL-H-12](../sources.md)

Namespace вычисляется как `agent-plugin-<slug(key)>-<sha256(key)[:8]>`, key flat root install — `name` из manifest; для `jedikit` это `agent-plugin-jedikit-805a716c`. Hash не зависит от версии, commit и пути установки; смена key меняет его, поэтому точное имя лучше брать из текущего discovery. [PL-H-16](../sources.md). То же имя `agent-plugin-jedikit-805a716c:jedikit-habits` наблюдалось на Hermes 0.20.6 в 2026-09-13; голое имя тогда через `skill_view` не разрешалось. [PL-H-35](../sources.md)

Symlink из plugin root наружу нарушает containment: parser его отклоняет, scanner даёт critical `symlink_escape`. Поэтому `skills/` — настоящий каталог в корне, без ссылок и копий. [PL-H-9](../sources.md), [PL-H-12](../sources.md)

**Skills Hub** — отдельный механизм, не входящий в штатную установку JediKit. `hermes skills install ibelyasov/jedikit/skills/<скилл>` ставит один скилл за команду, `--ref` и выбора ревизии нет: берётся tree default branch, а при сбое API возможен fallback без ревизии. Пять установок независимы и могут получить разные ревизии; копия в `$HERMES_HOME/skills` изменяема, `hermes skills update` снова следует default branch. Перед копированием выполняются quarantine и security scan. [PL-H-63](../sources.md), [PL-H-64](../sources.md), [PL-H-11](../sources.md)

## Ресурсы скилла и соседние скиллы

`skill_view(name="<скилл>")` возвращает `SKILL.md`; файлы скилла читаются тем же инструментом: `skill_view(name="<скилл>", file_path="references/write-policy.md")`, `file_path="tools.json"`. JSON в корне скилла доступен по явному пути, хотя plugin `linked_files` перечисляет только `references/`, `templates/`, `assets/`, `scripts/`. Markdown-ссылка сама файл не загружает. `..` и выход за корень скилла запрещены, поэтому общий файл вне скилла недоступен: соседний скилл загружается по своему `name`. [PL-H-48](../sources.md), [PL-H-49](../sources.md)

Соседний скилл JediKit берётся с тем же префиксом, что у текущего: голое имя при `external_dirs`, тот же `agent-plugin-…:` при plugin install; plugin `skill_view` добавляет banner с именами соседей. При двух установках нельзя выбирать произвольный одноимённый скилл. У владельца файловые инструменты и terminal выключены, поэтому `skill_view` — единственный путь к ресурсам. [PL-H-48](../sources.md), [PL-H-66](../sources.md)

`skill_view` только загружает текст; выбор и исполнение сценария остаются за моделью. Markdown skill не даёт инструментов: доступны toolsets из конфигурации Hermes. [PL-H-49](../sources.md), [PL-H-4](../sources.md)

## Frontmatter

У JediKit только `name` и `description`. Portable validator требует `name`, совпадающий с каталогом (1–64 символа), и `description` 1–1024 символа. [PL-H-9](../sources.md)

Вложенный `metadata.hermes` portable plugin не принимает: `metadata` допускается только как отображение строка→строка. Ошибка становится diagnostic, скилл пропускается discovery, loader регистрирует только оставшиеся, а `plugins validate` выводит это как warning при exit `0`. Добавленный всем пяти скиллам `metadata.hermes` убрал бы их из plugin install. [PL-H-9](../sources.md), [PL-H-17](../sources.md), [PL-H-21](../sources.md)

При `external_dirs` Hermes читает `metadata.hermes.tags`, `related_skills`, `requires_*`, `fallback_for_*`, но это не нужно JediKit: tags и related skills не попадают в индекс, а `requires_toolsets`/`requires_tools` сравниваются с eager-набором инструментов. При включённом Tool Search отложенные MCP в этот набор не входят, и требование вроде `mcp-singularity` может скрыть исправный скилл из индекса (вывод из source, не воспроизведён). Имена MCP toolsets — `mcp-<server>`. [PL-H-51](../sources.md), [PL-H-50](../sources.md), [PL-H-52](../sources.md), [PL-H-53](../sources.md), [PL-H-54](../sources.md)

Индекс показывает `- имя: описание`, где описание усечено до первых 57 символов и `...`; полный `SKILL.md` не загружается. Поэтому начало `description` должно различать пять скиллов. `skills_list` читает metadata из первых 4000 символов файла. Качество выбора скилла моделью не измерялось. [PL-H-50](../sources.md), [PL-H-51](../sources.md), [PL-H-49](../sources.md)

## MCP-инструменты и Tool Search

Callable name — `mcp__<server>__<tool>`, где любой символ вне `[A-Za-z0-9_]`, включая `-`, заменён на `_`; длинное имя ограничивается 64 символами с hash suffix. Например, `get-event` на `google_calendar` — `mcp__google_calendar__get_event`. Базовые имена в `tools.json` менять не нужно. [PL-H-46](../sources.md)

У сервера с `trust=untrusted` Hermes сам запрашивает approval на вызов инструмента без `readOnlyHint=true`; это может затронуть и чтения без annotation. Host approval не заменяет согласие по правилам JediKit, и наоборот. [PL-H-47](../sources.md)

При включённом Tool Search schemas MCP отложены: отсутствие инструмента в видимом списке не означает его отсутствия. Путь — `tool_search(queries=[...])` → `tool_describe(names=[...])` → `tool_call(calls=[{name, arguments}])`; schemas можно получить группой, но для MCP в `calls` допускается один элемент. Текущая web-страница описывает несколько local calls иначе; pin однозначен. Tool Search сохраняет approvals исходного инструмента. [PL-H-54](../sources.md)

Пакет JediKit MCP не объявляет. Portable loader читает только `mcp.json` с точным schema URI; `.mcp.json` не fallback. Remote entry допускает `type`, `url`, `headers`; поле `auth` даёт diagnostic `unknown remote field`, и entry пропускается, тогда как native конфигурация Hermes поддерживает `auth: oauth`. Plugin inventory, effective native config и рабочая OAuth-сессия — разные утверждения. [PL-H-9](../sources.md), [PL-H-14](../sources.md), [PL-H-15](../sources.md), [PL-H-17](../sources.md), [PL-H-18](../sources.md)

Фильтр `tools.include`/`tools.exclude` (срез 0.20.6, 2026-09-13): include — allowlist имён и globs с приоритетом над exclude; пустой `include: []` не регистрирует инструменты. Denylist или широкий glob могут пропустить будущий write-tool; фильтр хоста не отзывает OAuth scope сервера. [PL-H-36](../sources.md)

## `clarify`

Схема: `questions:[{question, choices?, multi_select?}]`, 1–5 вопросов, до 4 вариантов; первый вариант помечается рекомендованным, UI добавляет «Other». Без `choices` ответ свободный. Ответ — `responses[]`; timeout, skip и недоставка не являются ответом. Timeout по умолчанию 3600 с. В Telegram пакет вопросов приходит отдельными последовательными карточками, полноценного multi-select нет. [PL-H-55](../sources.md)

Отсюда канал JediKit: все блокирующие пробелы — один вопрос без `choices` со всем списком, чтобы сохранить «одним сообщением» ADR 0013; одиночное предложение, общий Preview и подтверждение безвозвратной потери Habitify — одна карточка «Да»/«Нет» после полного текста. Порядок вариантов: «Да», «Нет»; для подтверждения потерь Habitify — «Нет», «Да», чтобы рекомендованным не стало удаление. Это продуктовая интерпретация, не security approval. В cron `clarify` недоступен. [PL-H-55](../sources.md), [PL-H-66](../sources.md)

## `memory`

Схема: `target: memory | user`, `action: add | replace | remove`, `content`, `old_text` для replace/remove; есть атомарный `operations` одного target. `replace` меняет всю запись, `old_text` лишь находит её. Отдельного чтения нет: записи видны в контексте памяти. Лимиты — 2200 символов на `memory` и 1375 на `user`, с разделителями. [PL-H-31](../sources.md), [PL-H-MEMORY-0.21.5](../sources.md)

При `memory.write_approval=true` foreground пытается получить approval сразу, без callback и в фоне запись ставится в очередь: `staged:true`, `pending_id`, `/memory pending`, `/memory approve <id>`. Применённая запись возвращает `done:true` с `usage` и `entry_count`, без содержимого. `done:true` — ответ инструмента о применении, не независимое чтение. [PL-H-56](../sources.md), [PL-H-31](../sources.md)

Описание `memory` в 0.21.5 советует хранить предпочтения «для вида работы» в скилле через `skill_manage`. На хосте владельца setup `jedikit-calendar` по этой подсказке создал ожидающие изменения файлов скилла вместо записи в память, хотя скиллы подключены из `/nix/store`. Поэтому JediKit явно называет `memory` и запрещает `skill_manage` для настроек. В Telegram `/skills` управляет ожидающими записями скиллов, а не каталогом. [PL-H-MEMORY-0.21.5](../sources.md), [CLANWRIGHT-SETUP-2026-10-08](../sources.md), [PL-H-65](../sources.md)

## Cron

Модельный инструмент — `cronjob_manage` (toolset `cronjob`): `action: create | list | update | pause | resume | remove | run`, адресация `job_id`. Create требует `schedule` и `prompt` либо хотя бы один `skills`; среди полей — `name`, `repeat`, `deliver`, `failure_deliver`, `skills`, `enabled_toolsets`. Schedule: `in 30m`, `every 2h`, cron expression, естественные день/время, ISO. Поля timezone нет: время берётся из `HERMES_TIMEZONE`, затем timezone профиля, затем локального времени сервера. [PL-H-57](../sources.md), [PL-H-58](../sources.md), [PL-H-5](../sources.md)

`skills` задания загружаются последовательно через `skill_view`; отсутствующий скилл пропускается с notice, поэтому успешное задание не доказывает загрузку скилла. Имена — голые при `external_dirs`, qualified при plugin install. Доставку выполняет scheduler, по умолчанию в исходный чат. [PL-H-32](../sources.md), [PL-H-58](../sources.md)

Per-job `enabled_toolsets` имеет приоритет над `platform_toolsets.cron`, а без явного выбора к заданию могут добавиться включённые MCP. Поэтому toolsets cron по умолчанию не доказывают read-only любого задания; JediKit не подставляет `enabled_toolsets` сам, а фоновое чтение без записи обеспечивает ADR 0003. [PL-H-58](../sources.md)

Срез 0.20.6 (2026-09-13): ISO без offset трактуется в настроенной зоне, отдельный DST-переход мог пропустить срабатывание; preflight проверял auth, настройку skill и доставку, но не гарантировал готовность; попытка проходила claimed → running → completed/failed/unknown в `executions.db` без автоматического retry. Задание, попытка, ответ модели и доставка — разные наблюдения. Общий денежный или токенный лимит не найден; `approvals.cron_mode: deny` ограничивает опасные команды, не расходы. [PL-H-38](../sources.md), [PL-H-39](../sources.md), [PL-H-40](../sources.md), [PL-H-41](../sources.md)

## Другие инструменты

- `todo_list`: список `{id, content, status}` до 256 элементов, вызов без аргументов читает. Подходит для шагов агента в длинном обзоре, не для задач пользователя. [PL-H-59](../sources.md)
- `session_search`: поиск и чтение прошлых сессий с ограниченным окном. Найденное — контекст разговора, а не актуальное состояние провайдера. [PL-H-62](../sources.md)
- `send_message` модели не зарегистрирован; фоновые уведомления — доставка cron. [PL-H-60](../sources.md)
- `delegate_task` у владельца выключен, а дочерним агентам недоступны `clarify`, `memory` и `cronjob`; соседний скилл JediKit загружается в той же сессии. [PL-H-61](../sources.md), [PL-H-66](../sources.md)

Local terminal (срез 0.20.6) работает от пользователя ОС и не является sandbox; фильтрация окружения terminal, `execute_code` и MCP различается. JediKit не требует terminal. [PL-H-37](../sources.md), [PL-H-39](../sources.md)

## Валидаторы и CI

```sh
hermes plugins validate . --json
hermes plugins doctor . --ci
```

`validate` включает scanner и portable validation; флаги `--json`, `--install-deps`, без `--ci`/`--strict`. `doctor` копирует пакет во временный `HERMES_HOME`, выполняет discovery/load/registration с блокировкой сокетов Python, имеет `--ci` (exit `1` при `report.ok == false`), но не вызывает install scanner. Provider accounts не нужны. [PL-H-10](../sources.md), [PL-H-19](../sources.md), [PL-H-21](../sources.md), [PL-H-33](../sources.md)

**Пределы.** Component diagnostics становятся warnings и не меняют exit, поэтому exit `0` не доказывает присутствие пяти скиллов: отчёт и warnings читаются вместе с ожидаемым inventory. Без `plugin.json`/`plugin.yaml` `validate` завершается ошибкой: штатного валидатора обычной коллекции для `external_dirs` нет. `hermes skills audit` перепроверяет только Hub inventory и при findings завершается `0`; scanner `skills_guard` — Python API, не CLI. Scanner не проверяет frontmatter целиком, ссылки и смысл инструкций. [PL-H-17](../sources.md), [PL-H-21](../sources.md), [PL-H-64](../sources.md), [PL-H-13](../sources.md)

Официальный GitHub Action `plugin-validate` имеет inputs `path` и `hermes-ref` (default `main`) и запускает только `validate`; `fail-on-warnings` нет. [PL-H-22](../sources.md) (Action на pin `f97608f`). CI JediKit закрепляет Action и `hermes-ref` на commit `781334eea4b9225a3e194faf0c241d9afe218634` с исправлением установки ([check.yml](../../.github/workflows/check.yml)); Action не экспортирует CLI, поэтому `doctor` выполняется локально. Шаг `git diff --check "$(git hash-object -t tree /dev/null)" HEAD` проверяет только пробелы, зато во всём дереве HEAD: обычный `git diff --check` в чистом checkout пуст. По [ADR 0004](../../docs/adr/0004-no-custom-code.md) собственные gates и assertion scripts не добавляются.

## Конфигурация владельца

Датированное наблюдение: clanwright HEAD `6641f66d74a1877f4c28f98bf9589af648a85d4c`, прочитан 2026-10-08; JediKit там закреплён на `v0.4.0` (`647b0d1`). Это декларация, не проверка deployment. [PL-H-66](../sources.md)

- JediKit подключён через `skills.external_dirs` из Nix store; plugin registry не используется. Hermes закреплён на том же `f97608f`. Nix-модули Hermes официально имеют уровень поддержки Tier 2 best effort. [PL-H-7](../sources.md)
- MCP: `singularity` — официальный hosted MCP с OAuth и `trust=untrusted`; `habitify_read`, `habitify`, `google_calendar` — локальные адаптеры с `trust=full`. Sampling, elicitation, resources и prompts выключены. Включены 35 инструментов Singularity, 7 чтений и 16 записей Habitify; allowlist Calendar берётся из `tools.json` JediKit.
- Toolsets Telegram: `clarify`, `todo`, `memory`, `session_search`, `web`, `search`, `skills`, `mcp-singularity`, `mcp-habitify`, `mcp-habitify_read`, `mcp-google_calendar`, с cron — `cronjob`. Tool Search включён.
- Фоновые toolsets: `web`, `skills`, `mcp-habitify_read`, `memory` — без Singularity и Calendar, поэтому фоновая утренняя сводка задач и календаря по ним невозможна. Задание сводки и его toolsets заводит владелец Hermes (clanwright); скиллы JediKit его не создают.
- Cron включён, timezone `Europe/Moscow`; `memory.write_approval=true`, `skills.write_approval=true`, `approvals.mode=manual`. Terminal, file, code execution, delegation, browser выключены.
- `grill-me` поставляется из официальных optional skills закреплённого Hermes; фактический discovery не проверен.

## Ограничения доступа gateway

Срез 0.20.6: доступ к боту требует pairing, allowlist, явного allow-all или trusted adapter; pairing grants и allowlists объединяются. Admin/user slash policy ограничивает slash-команды, не обычный чат. Доступ к боту, разрешение инструмента и согласие изменить данные — разные границы. [PL-H-42](../sources.md), [PL-H-44](../sources.md), [PL-H-45](../sources.md)

## Непроверенные слои

Не проверены: установка точного commit JediKit любым способом, фактические имена скиллов, индекс и slash, scanner verdict всего репозитория, MCP discovery и OAuth, вызовы Tool Search, карточки `clarify` в Telegram, записи и approval `memory`, задания cron, timezone, запуск и доставка, поведение модели и Read-back. Source и статические проверки эти результаты не подтверждают. Аккаунты и данные провайдеров этой работой не затрагивались.
