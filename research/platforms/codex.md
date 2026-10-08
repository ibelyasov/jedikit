# Codex: актуальный контракт для JediKit

Дата исходного исследования: **2026-10-05**, консолидация — **2026-10-06**. Даты доступа отдельных источников указаны в [реестре](../sources.md).
Это исследование платформы, а не подтверждение runtime-совместимости JediKit.
Плагин не объявляет подключения или секреты; операции предоставляет хост ([ADR 0005](../../docs/adr/0005-one-source-host-connections.md)). В этой работе не выполнялись установка плагина, OAuth, вызовы моделей или операции с данными провайдеров.

## Версии и границы доказательства

Локально наблюдался `codex-cli 0.160.0`, бинарник
`/opt/homebrew/Caskroom/codex/0.160.0/bin/codex`. Прочитаны версия и справки CLI.
Для проверки реализации скачан официальный tag `rust-v0.160.0`, разрешённый в
commit `a956835d020762cb2b570053af06f643a11c0ecc`; дата release tag —
2026-10-01. Справка не доказывает загрузку конкретного пакета.
[PL-O-8](../sources.md),
[PL-O-9](../sources.md).

Текущая документация OpenAI не привязана к установленной версии. Дополнительно
прочитаны CLI command definitions и portable manifest parser текущего upstream
на commit `7c2ce90716335c889a5076ded9a630459f9c9899`: в этих ограниченных областях
не обнаружен отдельный CLI validator, portable parser совпадает с 0.160.0.
Это не проверка всего upstream и не обещание для будущих релизов.
[PL-O-18](../sources.md),
[PL-O-19](../sources.md),
[PL-O-20](../sources.md).

## Skills: единый источник и discovery

Документация требует отдельную папку skill с `SKILL.md`, YAML `name` и
`description`; scripts, references, assets и `agents/openai.yaml` опциональны.
Имя и description служат первоначальному выбору, полные инструкции читаются
после выбора. В CLI/IDE явный вызов — `$skill` или `/skills`; в ChatGPT — `@`.
Неявный выбор зависит от description, а не от гарантированного dispatch.
[PL-O-1](../sources.md).

Standalone repository discovery сканирует `.agents/skills` от cwd до repo root,
user discovery — `~/.agents/skills`, admin — `/etc/codex/skills`; имеются
встроенные system skills. Документирована поддержка symlinked skill folders.
Произвольная корневая `skills/` не становится standalone discovery автоматически.
В plugin она является компонентом пакета. Для JediKit достаточно одного
редактируемого дерева `skills/`; копировать его в каталоги каждого хоста или
генерировать варианты инструкций не требуется. Последнее — вывод для проекта,
основанный на контракте discovery и упаковки, не отдельная гарантия всех хостов.
[PL-O-1](../sources.md),
[PL-O-2](../sources.md).

Одинаковые имена skills не объединяются и могут появляться в selectors
несколько раз. Initial skills list ограничен 2% окна модели либо 8000 символами
при неизвестном окне; сначала сокращаются descriptions, затем возможны omission
и warning. Это ограничение списка, а не размера полного `SKILL.md`.
[PL-O-1](../sources.md).

## Optional metadata платформы

JediKit не поставляет agents metadata по [ADR 0005](../../docs/adr/0005-one-source-host-connections.md). Следующие сведения описывают возможности платформы, а не требования к пакету. Optional файл находится **внутри каждой папки skill**:
`skills/<name>/agents/openai.yaml`, рядом с уровнем `SKILL.md`, а не в
plugin-level `agents/`. Документированные optional fields:

| Раздел | Поля | Назначение |
| --- | --- | --- |
| `interface` | `display_name`, `short_description`, `icon_small`, `icon_large`, `brand_color`, `default_prompt` | Отображение и стартовый prompt |
| `policy` | `allow_implicit_invocation` | По умолчанию true; false оставляет explicit invocation |
| `dependencies.tools[]` | `type`, `value`, `description`, `transport`, `url` | Объявление требуемого MCP |

У dependency в примере документации транспорт называется `streamable_http`,
в portable `mcp.json` — `streamable-http`: это разные schema, нельзя механически
унифицировать написание. Dependency не является доказательством OAuth, прав
или успешного tool call. Эти свойства требуют отдельной runtime-проверки.
[PL-O-1](../sources.md),
[PL-O-4](../sources.md),
[PL-O-2](../sources.md).

Исходники 0.160.0 также хранят dependency `command`, `oauth_callback_port` и
policy `products`; в `SkillPolicy` есть TODO о неполном enforcement product
gating. Поэтому undocumented поля и `products` не следует превращать в
обязательную защиту или portable контракт JediKit. Иконки standalone skill
разрешаются относительно skill под `assets/`; plugin skills могут ссылаться на
общие plugin assets с проверкой границы каталога.
[PL-O-10](../sources.md),
[PL-O-11](../sources.md).

## Portable manifest и Codex overlay

Текущий рекомендуемый формат — root `plugin.json` с
`$schema: https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`.
Portable identity (`name`, `version`, `description` и другие metadata) остаётся
в корне; OpenAI-specific presentation, registered app mappings и hooks —
в `extensions.com.openai`. `.codex-plugin/plugin.json` поддерживается как
compatibility manifest. Наличие старого scaffold в документации не делает его
единственным допустимым форматом.
[PL-O-2](../sources.md).

В проверенной реализации выбор portable root зависит от распознаваемого Agent
Plugins `$schema`. Нерелевантный root manifest позволяет legacy fallback;
schema из Agent Plugins namespace с неподдержанным номером выбирается и затем
отклоняется parser. Сам root manifest должен быть regular file, не symlink.
Legacy порядок — `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`,
`.cursor-plugin/plugin.json`. Это поведение Codex, не утверждение о parsers
Claude/Hermes.
[PL-O-12](../sources.md).

Если `extensions.com.openai` — объект, он **целиком заменяет** compatibility
overlay: значения из двух объектов не сливаются. Если inline object отсутствует,
overlay может предоставить OpenAI settings. Portable root identity и fixed
components при этом остаются canonical.
[PL-O-2](../sources.md),
[PL-O-13](../sources.md).

Практически важная граница 0.160.0: portable parser задаёт фиксированные
`./skills` и `./mcp.json`; из OpenAI extension/overlay переносит только
apps, hooks, onboarding skill и interface. Поля `skills` и `mcpServers` в overlay
**не перенаправляют portable компоненты**. Отсутствующий `mcp.json` даёт пустую
MCP inventory; указание `mcpServers: "./.mcp.json"` в extension не заменяет его.
Legacy compatibility manifest имеет собственный механизм paths.
Следовательно, единую MCP декларацию для нескольких хостов нужно проверять
по всем их schema; нельзя обещать portable Codex redirect на `.mcp.json`.
[PL-O-13](../sources.md),
[PL-O-14](../sources.md).

## Локальный marketplace и разработка

Repo catalog — `.agents/plugins/marketplace.json`; `source.path` считается от
marketplace root, не от каталога `.agents/plugins/`. Путь начинается с `./` и
остаётся внутри root. Каталог может указывать непосредственно на один plugin
root с общим `skills/`; пример документации с копированием в `plugins/` не
является обязательным layout.
[PL-O-2](../sources.md).

Минимальная документированная форма каталога (пример, не установленная запись):

```json
{
  "name": "jedikit-local",
  "plugins": [{
    "name": "jedikit",
    "source": {"source": "local", "path": "./"},
    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
    "category": "Productivity"
  }]
}
```

Документированная команда разработки — `codex plugin marketplace add ./<root>`;
есть Git shorthand, HTTPS/SSH, `--ref`, `--sparse`, list/upgrade/remove.
Локальная справка 0.160.0 и source также подтверждают install command
`codex plugin add jedikit@jedikit-local`. Команды приведены для будущего
изолированного теста и здесь не выполнялись. Документация упаковки местами
направляет local install/test в desktop app, поэтому наличие CLI add проверено
отдельно. Local plugin install использует cache, а не обязательно живое дерево;
после правок нужно проверять фактический installed revision.
[PL-O-2](../sources.md),
[PL-O-17](../sources.md),
[PL-O-2](../sources.md).

## MCP и ограничения проекта

Codex host поддерживает STDIO и Streamable HTTP, bearer/OAuth. Host configuration
лежит в `~/.codex/config.toml` либо `.codex/config.toml` trusted project;
hosted plugin tools могут иметь другой контракт. `agents/openai.yaml`, plugin
MCP descriptor и подключённый аккаунт — отдельные уровни, не взаимозаменяемые
доказательства доступа.
[PL-O-3](../sources.md).

Для Codex SingularityApp MCP подключается на хосте. Habitify использует официальный REST/OpenAPI v2 как бизнес-контракт; транспорт — OpenAPI→MCP-адаптер хоста или эквивалент с теми же именами, ключ остаётся только у адаптера ([ADR 0001](../../docs/adr/0001-habitify-via-rest.md)). Официальный Habitify MCP отвергнут из-за неполноты операций. Плагин не объявляет MCP и секреты ни для одного хоста ([ADR 0005](../../docs/adr/0005-one-source-host-connections.md)). `tools.json` задаёт базовые имена без host prefix, серверы `singularity`/`habitify`, доступ `read`/`write` и `required` у Habitify. Если tools отсутствуют, агент называет недостающие операции и рекомендует подключить их на хосте; ничего не устанавливает и не запрашивает ключ.

## Официальные проверки

В CLI 0.160.0 нет отдельной команды `codex plugin validate` или `codex skill validate` в прочитанном command tree. `codex features list` показывает plugins stable; отдельный validator feature не наблюдался.
`codex app-server generate-json-schema` — experimental генерация schema
**app-server protocol**, а не валидатор plugin package. Это ограниченный вывод
по установленной справке, CLI source и protocol definitions, не утверждение,
что OpenAI вообще не имеет других проверок.
[PL-O-21](../sources.md),
[PL-O-17](../sources.md),
[PL-O-21](../sources.md).

Официальный bundled `skill-creator` содержит `scripts/quick_validate.py`:
минимальная проверка frontmatter, naming, unfinished placeholders. Он не
проверяет качество решений, `agents/openai.yaml`, marketplace и runtime.
Это реальный vendor helper, но Python; по ограничению проекта не запускался
и не предлагается как CI dependency. Native skill parser тоже отличается от
helper: например, может получить имя из каталога при отсутствующем `name`.
Следует сохранять документированный authoring contract, а не считать parser
leniency разрешением убрать обязательные metadata.
[PL-O-22](../sources.md),
[PL-O-23](../sources.md).

Официальная документация рекомендует тестировать прямые и косвенные triggers,
неполный ввод, non-triggers и edge cases, оценивая activation и output.
Bundled creator описывает независимую поведенческую проверку агентом при
достаточной сложности/риске; это инструкция workflow, не бесплатный
детерминированный CLI runner. Проверки проекта ограничены штатными Claude/Hermes validators, `git diff --check` и независимым агентным ревью; модельные прогоны не входят в текущую проверку. Ни schema validity, ни список skill names этого не доказывают.
[PL-O-4](../sources.md),
[PL-O-24](../sources.md).

## Evidence и открытые вопросы

Историческое исследование 2026-10-05 ссылалось на локальные CLI/docs/pinned source artifacts. В этом worktree они отсутствуют; их путь не является воспроизводимым evidence этой консолидации. На 2026-10-06 повторно прочитан `codex --version`: 0.160.0. Остальные source факты сохранены с датой исходной проверки; полного повторного source audit не выполнялось.

Не проверены: загрузка текущего JediKit в новой сессии Codex, installed cache
identity, реальный implicit routing, OAuth и права официальных MCP, execution
и read-back, desktop/web availability в конкретном аккаунте. Подключения и авторизация находятся на хосте ([ADR 0005](../../docs/adr/0005-one-source-host-connections.md)). Внешние
community anecdotes не использованы; vendor documentation и source inspection
отделены от локальных наблюдений. Исторические данные 2026-09-13 (`codex-cli 0.154.0`, чтение version/marketplace/MCP help без мутаций) сохранены как наблюдения прежней среды, не доказательство нынешней совместимости.

Принятый root layout и границы проверок — в [Hermes](hermes.md); детали Claude validator — в [Claude Code](claude.md). По [ADR 0006](../../docs/adr/0006-memory-holds-settings-only.md) native memory хранит только настройки, не состояние обзоров. Наличие host memory и plugin identity не обеспечивает перенос этих настроек между платформами.

## Scheduled tasks и публичная публикация

Официальная документация разделяет scheduled task management в ChatGPT/Codex chat и CLI/IDE, где Scheduled management interface отсутствует. Local Desktop tasks требуют работающей машины/app; web run не получает локальную папку. Event triggers web/mobile не образуют универсальный scheduler API CLI/Desktop. Availability зависит от поверхности и workspace policy. По [ADR 0003](../../docs/adr/0003-no-unattended-writes.md) JediKit фоновые обзоры только читают; это продуктовый контракт, не автоматическая гарантия хоста. Здесь task creation, permissions и delivery не проверялись. [PL-O-15](../sources.md)

Публичная submission принимает skills-only и MCP packages, требует Apps Management Write, verified organization identity, listing/support/privacy/terms и positive/negative cases. Submit, review и publish — разные стадии; URL стороннего provider не даёт права подтверждать его домен. JediKit не публикуется этой работой, listing не доказывает runtime. Requirements необходимо перепроверять перед реальной submission. [PL-O-16](../sources.md)

## Как оценивать совместимость

Версия/help, источник/revision, parser inventory, доступность skills в новой session, host connection/schema, наблюдаемое поведение и разрешённые writes/read-back — разные уровни. `$jedikit-habits` в selector не доказывает safety refusal; loaded instructions плюс корректный ответ подтверждают конкретный сценарий на конкретном host/model. После изменения instructions старый trace остаётся историческим. Installed cache нужно сопоставлять с исходниками, не удалять его непроверенными командами. `@jedikit` обозначает OpenAI plugin scoping, а не router skill; `$jedikit` не является portable тегом. Навигатор JediKit — скилл с тем же именем `jedikit`, что и плагин; как Codex различает `$jedikit` для скилла и `@jedikit` для плагина и какое qualified name получит скилл в Hermes, не проверено (в Claude Code — `/jedikit:jedikit`). [PL-O-1](../sources.md), [PL-O-2](../sources.md)
