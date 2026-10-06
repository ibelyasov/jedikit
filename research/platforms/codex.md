# Codex: актуальный контракт для JediKit

Дата проверки и доступа ко всем внешним источникам: **2026-10-05**.
Это исследование платформы, а не подтверждение runtime-совместимости JediKit.
Обязательная продуктовая приёмка остаётся на Hermes на Nix-сервере; Codex —
заявленная дополнительная платформа. В этой работе не выполнялись установка
плагина, OAuth, вызовы моделей или операции с данными провайдеров.

## Версии и границы доказательства

Локально наблюдался `codex-cli 0.160.0`, бинарник
`/opt/homebrew/Caskroom/codex/0.160.0/bin/codex`. Прочитаны версия и справки CLI.
Для проверки реализации скачан официальный tag `rust-v0.160.0`, разрешённый в
commit `a956835d020762cb2b570053af06f643a11c0ecc`; дата release tag —
2026-10-01. Справка не доказывает загрузку конкретного пакета.
[Официальный release](https://github.com/openai/codex/releases/tag/rust-v0.160.0) (доступ 2026-10-05),
[исходники версии](https://github.com/openai/codex/tree/a956835d020762cb2b570053af06f643a11c0ecc) (доступ 2026-10-05).

Текущая документация OpenAI не привязана к установленной версии. Дополнительно
прочитаны CLI command definitions и portable manifest parser текущего upstream
на commit `7c2ce90716335c889a5076ded9a630459f9c9899`: в этих ограниченных областях
не обнаружен отдельный CLI validator/eval, portable parser совпадает с 0.160.0.
Это не проверка всего upstream и не обещание для будущих релизов.
[CLI upstream](https://github.com/openai/codex/blob/7c2ce90716335c889a5076ded9a630459f9c9899/codex-rs/cli/src/main.rs) (доступ 2026-10-05),
[plugin commands](https://github.com/openai/codex/blob/7c2ce90716335c889a5076ded9a630459f9c9899/codex-rs/cli/src/plugin_cmd.rs) (доступ 2026-10-05),
[portable parser](https://github.com/openai/codex/blob/7c2ce90716335c889a5076ded9a630459f9c9899/codex-rs/core-plugins/src/agent_plugin_manifest.rs) (доступ 2026-10-05).

## Skills: единый источник и discovery

Документация требует отдельную папку skill с `SKILL.md`, YAML `name` и
`description`; scripts, references, assets и `agents/openai.yaml` опциональны.
Имя и description служат первоначальному выбору, полные инструкции читаются
после выбора. В CLI/IDE явный вызов — `$skill` или `/skills`; в ChatGPT — `@`.
Неявный выбор зависит от description, а не от гарантированного dispatch.
[Build skills](https://developers.openai.com/codex/skills) (доступ 2026-10-05).

Standalone repository discovery сканирует `.agents/skills` от cwd до repo root,
user discovery — `~/.agents/skills`, admin — `/etc/codex/skills`; имеются
встроенные system skills. Документирована поддержка symlinked skill folders.
Произвольная корневая `skills/` не становится standalone discovery автоматически.
В plugin она является компонентом пакета. Для JediKit достаточно одного
редактируемого дерева `skills/`; копировать его в каталоги каждого хоста или
генерировать варианты инструкций не требуется. Последнее — вывод для проекта,
основанный на контракте discovery и упаковки, не отдельная гарантия всех хостов.
[Local discovery](https://developers.openai.com/codex/skills#where-to-save-skills) (доступ 2026-10-05),
[plugin structure](https://developers.openai.com/plugins/build/plugins#plugin-structure) (доступ 2026-10-05).

Одинаковые имена skills не объединяются и могут появляться в selectors
несколько раз. Initial skills list ограничен 2% окна модели либо 8000 символами
при неизвестном окне; сначала сокращаются descriptions, затем возможны omission
и warning. Это ограничение списка, а не размера полного `SKILL.md`.
[Skills documentation](https://developers.openai.com/codex/skills) (доступ 2026-10-05).

## `agents/openai.yaml`

Файл находится **внутри каждой папки skill**:
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
[Optional metadata](https://developers.openai.com/codex/skills#optional-metadata) (доступ 2026-10-05),
[MCP dependency](https://developers.openai.com/plugins/build/skills#connect-skills-to-mcp-tools) (доступ 2026-10-05),
[portable MCP example](https://developers.openai.com/plugins/build/plugins#bundled-mcp-servers-and-lifecycle-hooks) (доступ 2026-10-05).

Исходники 0.160.0 также хранят dependency `command`, `oauth_callback_port` и
policy `products`; в `SkillPolicy` есть TODO о неполном enforcement product
gating. Поэтому undocumented поля и `products` не следует превращать в
обязательную защиту или portable контракт JediKit. Иконки standalone skill
разрешаются относительно skill под `assets/`; plugin skills могут ссылаться на
общие plugin assets с проверкой границы каталога.
[Metadata model](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/skills/src/model.rs) (доступ 2026-10-05),
[asset path resolver](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/skills/src/interface.rs) (доступ 2026-10-05).

## Portable manifest и Codex overlay

Текущий рекомендуемый формат — root `plugin.json` с
`$schema: https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`.
Portable identity (`name`, `version`, `description` и другие metadata) остаётся
в корне; OpenAI-specific presentation, registered app mappings и hooks —
в `extensions.com.openai`. `.codex-plugin/plugin.json` поддерживается как
compatibility manifest. Наличие старого scaffold в документации не делает его
единственным допустимым форматом.
[Package your plugin](https://developers.openai.com/plugins/build/plugins) (доступ 2026-10-05).

В проверенной реализации выбор portable root зависит от распознаваемого Agent
Plugins `$schema`. Нерелевантный root manifest позволяет legacy fallback;
schema из Agent Plugins namespace с неподдержанным номером выбирается и затем
отклоняется parser. Сам root manifest должен быть regular file, не symlink.
Legacy порядок — `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`,
`.cursor-plugin/plugin.json`. Это поведение Codex, не утверждение о parsers
Claude/Hermes.
[Manifest selection](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/utils/plugins/src/plugin_namespace.rs) (доступ 2026-10-05).

Если `extensions.com.openai` — объект, он **целиком заменяет** compatibility
overlay: значения из двух объектов не сливаются. Если inline object отсутствует,
overlay может предоставить OpenAI settings. Portable root identity и fixed
components при этом остаются canonical.
[Документированный приоритет](https://developers.openai.com/plugins/build/plugins#add-an-openai-and-codex-overlay) (доступ 2026-10-05),
[реализация](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/core-plugins/src/agent_plugin_manifest.rs) (доступ 2026-10-05).

Практически важная граница 0.160.0: portable parser задаёт фиксированные
`./skills` и `./mcp.json`; из OpenAI extension/overlay переносит только
apps, hooks, onboarding skill и interface. Поля `skills` и `mcpServers` в overlay
**не перенаправляют portable компоненты**. Отсутствующий `mcp.json` даёт пустую
MCP inventory; указание `mcpServers: "./.mcp.json"` в extension не заменяет его.
Legacy compatibility manifest имеет собственный механизм paths.
Следовательно, единую MCP декларацию для нескольких хостов нужно проверять
по всем их schema; нельзя обещать portable Codex redirect на `.mcp.json`.
[Portable parser](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/core-plugins/src/agent_plugin_manifest.rs) (доступ 2026-10-05),
[MCP loader](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/core-plugins/src/loader.rs) (доступ 2026-10-05).

## Локальный marketplace и разработка

Repo catalog — `.agents/plugins/marketplace.json`; `source.path` считается от
marketplace root, не от каталога `.agents/plugins/`. Путь начинается с `./` и
остаётся внутри root. Каталог может указывать непосредственно на один plugin
root с общим `skills/`; пример документации с копированием в `plugins/` не
является обязательным layout.
[Marketplace metadata](https://developers.openai.com/plugins/build/plugins#marketplace-metadata) (доступ 2026-10-05).

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
[CLI authoring](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli) (доступ 2026-10-05),
[CLI implementation](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/cli/src/plugin_cmd.rs) (доступ 2026-10-05),
[local marketplaces](https://developers.openai.com/plugins/build/plugins#how-local-marketplaces-work) (доступ 2026-10-05).

## MCP и ограничения проекта

Codex host поддерживает STDIO и Streamable HTTP, bearer/OAuth. Host configuration
лежит в `~/.codex/config.toml` либо `.codex/config.toml` trusted project;
hosted plugin tools могут иметь другой контракт. `agents/openai.yaml`, plugin
MCP descriptor и подключённый аккаунт — отдельные уровни, не взаимозаменяемые
доказательства доступа.
[Codex MCP](https://developers.openai.com/codex/mcp) (доступ 2026-10-05).

Для JediKit продуктовая граница — только официальные hosted MCP провайдеров,
без собственного server/proxy/runtime и без секретов в пакете. Portable MCP
документация показывает root `mcp.json`, Agent Plugins MCP schema и
`type: "streamable-http"`. Не достаточно переименовать `.mcp.json`: нужен
соответствующий schema/transport. В этом исследовании endpoints не подключались.
[Bundled MCP](https://developers.openai.com/plugins/build/plugins#bundled-mcp-servers-and-lifecycle-hooks) (доступ 2026-10-05).

## Официальные проверки и eval

В CLI 0.160.0 нет отдельной команды `codex plugin validate`, `codex skill validate`
или skill eval runner в прочитанном command tree. `codex features list`
показывает plugins stable; отдельный validator/eval feature не наблюдался.
`codex app-server generate-json-schema` — experimental генерация schema
**app-server protocol**, а не валидатор plugin package. Это ограниченный вывод
по установленной справке, CLI source и protocol definitions, не утверждение,
что OpenAI вообще не имеет других проверок.
[CLI command tree](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/cli/src/main.rs) (доступ 2026-10-05),
[plugin commands](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/cli/src/plugin_cmd.rs) (доступ 2026-10-05),
[app-server command definitions](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/cli/src/main.rs#L621) (доступ 2026-10-05).

Официальный bundled `skill-creator` содержит `scripts/quick_validate.py`:
минимальная проверка frontmatter, naming, unfinished placeholders. Он не
проверяет качество решений, `agents/openai.yaml`, marketplace и runtime.
Это реальный vendor helper, но Python; по ограничению проекта не запускался
и не предлагается как CI dependency. Native skill parser тоже отличается от
helper: например, может получить имя из каталога при отсутствующем `name`.
Следует сохранять документированный authoring contract, а не считать parser
leniency разрешением убрать обязательные metadata.
[Bundled validator](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/skills/src/assets/samples/skill-creator/scripts/quick_validate.py) (доступ 2026-10-05),
[skill parser](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/skills/src/parser.rs) (доступ 2026-10-05).

Официальная документация рекомендует тестировать прямые и косвенные triggers,
неполный ввод, non-triggers и edge cases, оценивая activation и output.
Bundled creator описывает независимую поведенческую проверку агентом при
достаточной сложности/риске; это инструкция workflow, не бесплатный
детерминированный CLI runner. В будущем отдельно нужны parser/load smoke и
поведенческие сценарии на pinned host/model, с preview/approval/read-back для
разрешённых действий. Ни schema validity, ни список skill names этого не доказывают.
[Test the skill](https://developers.openai.com/plugins/build/skills#test-the-skill) (доступ 2026-10-05),
[creator workflow](https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md) (доступ 2026-10-05).

## Evidence и открытые вопросы

Локальные read-only evidence находятся в `.work/research-platforms/codex/`:
CLI version/help, docs snapshots, annotated tag metadata, upstream commit
metadata и скачанные pinned sources. CodeGraph был вызван первым; команда
сообщила отсутствие доступного index в этом worktree, после чего использованы
прямые чтения. Это инструментальный результат, не доказательство качества кода.

Не проверены: загрузка текущего JediKit в новой сессии Codex, installed cache
identity, реальный implicit routing, OAuth и права официальных MCP, execution
и read-back, desktop/web availability в конкретном аккаунте. Совместимость общего
MCP descriptor с Claude/Hermes требует их независимой проверки. Внешние
community anecdotes не использованы; vendor documentation и source inspection
отделены от локальных наблюдений. Исторический отчёт `research/platform-codex.md`
прочитан как контекст, не использован вместо свежей проверки.

Предлагаемый минимальный общий layout и CI описаны в [исследовании Hermes](hermes.md)
как основной вывод для проекта. В отдельной статической проверке lead подтвердил,
что native validator Claude принимает explicit `mcpServers: "./mcp.json"` с
portable `$schema` и `streamable-http` без доступа к аккаунту. Это подтверждение
формата fixture; runtime загрузка и доступ к провайдерам остаются непроверенными.
