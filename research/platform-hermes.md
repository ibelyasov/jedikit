# Hermes Agent для JediKit

Проверено **2026-09-13** по установленному публичному checkout и текущей
официальной документации. Локально установлен Hermes Agent **0.20.6
(2026.8.27)**, upstream commit
[`b4b7727e`](https://github.com/NousResearch/hermes-agent/commit/b4b7727ea07681b40402de411ddd000bb3c439fc).
На дату проверки последний официальный релиз —
[`v2026.9.11` / 0.21.2](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.9.11).
Поэтому факты из `main` и 0.21.2 ниже не выдаются за проверку локального
runtime 0.20.6.

## Вывод для JediKit

Hermes поддерживает JediKit как portable **Agent Plugins v1** package. Текущий
`packages/jedikit/plugin.json` проходит parser и `hermes plugins doctor`; оба
каталога `skills/jedikit-tasks` и `skills/jedikit-habits` обнаруживаются. В
установленном 0.20.6 habit skill зарегистрирован как
`agent-plugin-jedikit-805a716c:jedikit-habits`; запросы `jedikit-habits` и
`jedikit:jedikit-habits` через `skill_view` не разрешаются. Суффикс namespace
нельзя считать стабильным API: идентификатор надо каждый раз получать из
`skills_list`. Эти проверки доказывают layout, manifest parsing, регистрацию и
разрешение полного имени, но не provider, OAuth, MCP backend, расписание или
доставку.

JediKit не должен переносить host-level OAuth в portable `mcp.json`. Схема Agent
Plugins v1 допускает у remote MCP `type`, `url` и `headers`, но не поле
`auth: oauth`. Поэтому Hermes package остаётся skills-only, а SingularityApp и
Habitify подключаются и авторизуются средствами host. Это перевод
Claude-specific `.mcp.json`, а не утверждение, что OAuth исчезает.

## Проверенная матрица

| Область | Текущий контракт | Проверено здесь | Граница |
| --- | --- | --- | --- |
| Package | `plugin.json` в корне, schema `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`; skills в `skills/<name>/SKILL.md`; optional `mcp.json` | Локальный parser: `name=jedikit`, два skills, `mcp=`, diagnostics `0`; doctor exit 0 | Не проверялись install/update из сети и интерактивный вызов |
| Skill loading | Portable skills регистрируются plugin manager и получают внутренний namespace; доступные имена раскрываются через `skills_list`, content — через `skill_view` ([skills](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md)) | В 0.20.6 полный habit identifier — `agent-plugin-jedikit-805a716c:jedikit-habits`; только он прошёл `skill_view` | Hash namespace не является обещанным стабильным именем; всегда использовать identifier из текущего `skills_list` |
| MCP translation | Agent Plugins v1 описывает optional `mcp.json`; установленный валидатор допускает remote HTTP и local stdio shape ([spec](https://agent-plugins.org/)) | В package намеренно нет `mcp.json`; provider accounts/config не читались | Host-level OAuth connection необходимо проверить отдельно на пользовательском Hermes |
| Scheduling | Cron хранит jobs в `~/.hermes/cron/jobs.json`, attempts в `executions.db`, запускает fresh agent session; attached skills задаются `--skill`, а абсолютный `workdir` добавляет repository instructions ([cron](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/cron.md)) | Installed source подтверждает: missing skill логируется и пропускается, после чего job продолжает работу без его инструкций | До создания job нужно разрешить полный identifier через `skills_list` и подтвердить его content через `skill_view`; job/provider/channel здесь не создавались |
| Delivery | Cron поддерживает local, origin и конкретные configured channels; gateway проверяет due jobs примерно раз в минуту ([cron](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/cron.md), [gateway](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/messaging/index.md)) | Только чтение source/docs | Нужны реальные credentials, gateway и channel target; это пользовательская acceptance |
| Plugin CLI | Текущие команды включают `plugins install`, `list`, `doctor`, `update`, `uninstall`; каталог в актуальном `main` описан как curated in-repo catalog ([CLI](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/reference/cli-commands.md)) | `plugins doctor packages/jedikit --ci` на 0.20.6 прошёл | Current `main` CLI может отличаться от установленной версии; перед onboarding сверять `hermes plugins --help` |

## Runtime-порядок проверки

Это read-only acceptance checklist. В исследовании выполнены `--version`,
`plugins doctor` и skill discovery/view; provider/account, install, cron и
delivery не трогались.

```bash
hermes --version
hermes plugins doctor packages/jedikit --ci
hermes plugins list
hermes cron list
```

В интерактивной Hermes session сначала вызвать `skills_list`, скопировать
возвращённый полный identifier и проверить его через `skill_view`. Bare aliases
не использовать. Только после этой проверки и отдельного разрешения на мутацию
можно создать local-delivery smoke job, передав exact identifier в `--skill`.
Его prompt должен быть явно read-only, например: «Прочитай доступное состояние
выбранной привычки и сообщи краткий статус. Ничего не создавай, не изменяй, не
удаляй и не отправляй». После создания нужно проверить job record и результат:
skill действительно загружен, а не попал в список skipped.

Installed source подтверждает, что `hermes cron run` разрешает ссылку сначала
как exact job ID, затем как case-insensitive name; неоднозначное имя отклоняется
с требованием использовать ID. В этой работе `cron run` не вызывался.

## Исторический срез

Предыдущее исследование от **2026-08-08** было привязано к Hermes
[`v2026.8.3` / 0.20.0](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.8.3)
и временному имени `singularity-jedi`. Оно подтвердило общую модель skills,
MCP, gateway и cron, но его команды каталога и список каналов не являются
текущим контрактом. Product overlay от 2026-08-29 наблюдал 0.20.6 и portable
package. Настоящая перепроверка сохраняет эти версии как историю, заменяет
кодовое имя на JediKit и отделяет package validation от live runtime acceptance.

## Что остаётся неизвестным

- Полный habit identifier разрешён через `skill_view`, но выполнение инструкций
  skill в agent response пользователь ещё не проверил.
- Совместимость host-level OAuth connections с обоими provider tools не
  подтверждена в этой работе.
- Cron inference, timezone/DST, model drift guard и local/channel delivery не
  проверялись на локальном 0.20.6.
- Обновление с локального 0.20.6 до 0.21.2 не выполнялось. После обновления
  следует повторить doctor, `skills_list`/`skill_view`, skill invocation и
  отдельно разрешённый cron smoke test.
- Hermes выбран владельцем единственным обязательным хостом приёмки v1;
  Codex/Claude остаются без подтверждённой runtime-совместимости. Это решение
  уже перенесено в release gate; свежая Hermes acceptance всё ещё требуется,
  см. [решения](product-decisions.md).

## Фильтрация MCP и границы локального исполнения

Дополнительная проверка выполнена по установленному публичному checkout
`b4b7727e`, без чтения конфигурации аккаунтов. Это статические факты указанной
версии, а не тест защищённости реального окружения.

`tools.include` задаёт разрешающий список имён или glob-шаблонов,
`tools.exclude` — исключения. При наличии обоих приоритет у `include`;
пустой `include: []` не регистрирует ни одного инструмента, отсутствие обоих
регистрирует все. Поэтому denylist допускает новые инструменты сервера,
которые не совпали с исключением. Include также требует аккуратности: широкий
glob может охватить будущие имена. Это фильтр инструментов хоста, а не отзыв
OAuth-прав у сервера.
[Реализация фильтра](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/tools/mcp_tool.py#L7180),
[документация MCP](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/website/docs/user-guide/features/mcp.md#L111).

Локальный terminal исполняется от пользователя ОС и не образует изолированную
песочницу. Ограничения write_file/patch не следует переносить на произвольный
terminal process. Фильтрация environment у terminal, execute_code и MCP
различается; passthrough может возвращать переменные процессу. В частности,
реализация намеренно сохраняет общую AWS credential chain, поэтому утверждение
«все секреты хоста скрыты» неверно. Это свойство общего хоста, а не требование
давать JediKit доступ к terminal или credentials.
[Security boundary](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/website/docs/user-guide/security.md#L505),
[local environment](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/tools/environments/local.py#L301).

Иллюстрация риска: сервер добавляет write-tool, а конфигурация запрещала только
одно прежнее имя удаления. Новый tool может стать доступным при следующем
discovery. Это вывод из правил фильтрации, не воспроизведённая атака на аккаунт.

## Cron: preflight, дрейф модели и стоимость

Установленная реализация поддерживает per-job привязку provider/model и
снимки неприкреплённых параметров при создании. Перед inference проверяются
provider auth, явно требуемая настройка skill и delivery. Обнаруженная проблема
может блокировать запуск до создания агента, с записью результата и уведомлением.
Смена неприкреплённого provider/model относительно снимка также может остановить
inference. Это снижает риск неожиданного запуска на другой модели.
[Модель запуска](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/website/docs/user-guide/features/cron.md#L24).

Ограничения существенны: внутренние ошибки некоторых preflight проверок
обрабатываются с продолжением; отсутствующий или нечитаемый skill остаётся
в ветке skip-and-continue. При неудаче разрешения конфигурации снимок может
отсутствовать. Старые jobs без снимка и явно заданные cron defaults имеют
отдельные исключения из drift guard. Наличие fallback chain меняет проверку
primary-provider auth. Поэтому «preflight всегда гарантирует готовность» —
слишком сильный вывод.
[Preflight implementation](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/cron/scheduler.py#L5101),
[drift guard](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/cron/scheduler.py#L6216),
[снимки job](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/cron/jobs.py#L1899).

В проверенном коде не найден общий потолок расходов в деньгах или токенах.
Preflight/drift guard не следует описывать как бюджетный лимит.
`approvals.cron_mode: deny` относится к опасным командам в headless-запуске,
а не к стоимости inference.
[Cron approval mode](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/website/docs/user-guide/security.md#L30).

## Cron: время, результаты и восстановление

IANA timezone влияет на cron; ISO timestamp без offset интерпретируется в
настроенной зоне Hermes. Реализация сохраняет намерение расписания по местному
времени и пересчитывает его при изменении offset. При определённом переходе
DST возможен пропуск ожидающего срабатывания — это явно отражено в коде.
Текстовое «каждое утро» требует согласованной зоны и расписания; один успешный
запуск не проверяет поведение на переходе часов.
[Разбор времени](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/cron/jobs.py#L849),
[DST migration](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/cron/jobs.py#L3652).

Попытка сохраняется в `executions.db` до dispatch. У неё отдельный жизненный
цикл claimed → running → completed/failed/unknown; потерянное исполнение
может стать unknown без автоматического retry. Документирован `hermes cron runs`
для истории. Наличие job, факт попытки, результат модели и доставка — четыре
разных наблюдения. Их полезно записывать отдельно при будущей приёмке.
[История запусков](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/website/docs/user-guide/features/cron.md#L321).

## Gateway: кто получает доступ

Общая схема авторизации — отказ при отсутствии основания доступа; основания
включают pairing, platform/global allowlist, явный allow-all и документированные
исключения trusted adapters. Pairing и allowlists объединяются: наличие списка
не отменяет уже выданный pairing grant. При настроенном allowlist неизвестные
DM по умолчанию игнорируются; без списка обычно запускается pairing, у email
свой default ignore. Поэтому проверять нужно эффективные grants, а не один
видимый список.
[Авторизация](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/gateway/authz_mixin.py#L383),
[pairing](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/gateway/pairing.py#L92).

Разделение admin/user для slash-команд ограничивает именно slash-команды;
обычный чат само по себе не ограничивает. Доступ к боту, разрешение tool и
согласие на изменение задачи/привычки — разные границы.
[Slash access](https://github.com/NousResearch/hermes-agent/blob/b4b7727ea07681b40402de411ddd000bb3c439fc/gateway/slash_access.py#L1).

## Порядок будущей приёмки и оставшиеся ограничения

Это исследовательский вывод о порядке проверки, не список выполненных действий:

1. Зафиксировать source revision пакета и версию host; проверить manifest.
2. Получить точные skill identifiers, просмотреть content и проверить обычный
   интерактивный ответ с загрузкой нужных instructions.
3. Отдельно проверить официальные MCP connections, доступные schemas и
   read-only запросы. Фильтры хоста и scopes провайдера фиксируются раздельно.
4. Для выбранного расписания согласовать timezone, cadence, destination и
   разрешения. Убедиться, что нужный skill действительно загружается.
5. Проверить local delivery до внешнего канала; сопоставить job record,
   execution history, результат и реально полученную доставку.
6. Если нужен gateway, проверить effective identity/grants и разрешения
   конкретного канала. Проверка pairing не доказывает политику записей JediKit.

Все дополнительные факты выше подтверждены исходниками, а не живыми MCP,
cron, DST, recovery или gateway tests. В этой работе такие действия не запускались.
