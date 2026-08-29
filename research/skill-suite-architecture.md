# Архитектура коллекции Agent Skills

**Проверено:** 2026-08-29 (Europe/Moscow).

**Статус:** platform research для набора JediKit. Context7 использован первым (`/openai/codex`, `/anthropics/claude-code`, `/nousresearch/hermes-agent`), затем выводы сверены с официальной документацией и публичными коллекциями.

## Краткий вывод

Нужно различать **umbrella package/source identity** и **router skill**.

- Единый бренд/репозиторий/plugin полезен: пользователь понимает, что task, habits и будущие skills принадлежат одному набору.
- Широкий implicit router не нужен: хосты уже маршрутизируют skills по `name` и `description`, а router добавит ложные срабатывания и дублирование инструкций.
- Даже после появления второй области выбран вариант A: два независимых implicit skills. Cross-domain workflow делится на отдельные вызовы; отдельный router можно пересмотреть только по новому подтверждённому контракту.
- «Одна установка» не является переносимым обещанием: Codex и Claude умеют plugin с несколькими skills; Hermes tap регистрирует источник, но документация показывает установку отдельных skills.

Решение: umbrella source/package/plugin `jedikit`, независимые skills `jedikit-tasks` и `jedikit-habits`, без root/router skill. Естественный язык — основной UX, explicit child invocation — fallback. `@jedikit` означает только OpenAI plugin mention/scoping; `$jedikit` не существует как portable tag.

## Подтверждённые факты платформ

### Codex

- Portable skill — каталог с `SKILL.md` и optional `scripts/`, `references/`, `assets`; discovery использует `name` и `description`, полное тело загружается при активации ([Build skills](https://learn.chatgpt.com/docs/build-skills)).
- Distributable plugin содержит `.codex-plugin/plugin.json` и может включать несколько каталогов в `skills/` ([Package plugins](https://developers.openai.com/plugins/build/plugins)).
- Один plugin install выставляет все bundled skills. Marketplace JSON — каталог plugins; добавление marketplace регистрирует источник, а не устанавливает весь каталог.
- Документированные Codex dependencies относятся к tools, а не образуют переносимый skill-to-skill dependency graph.
- Plugin mention `@jedikit` scopes plugin context, но не является отдельным router skill; implicit discovery по descriptions остаётся основным путём.

### Claude Code

- Plugin содержит `.claude-plugin/plugin.json` и `skills/<name>/SKILL.md`; skills вызываются в namespace plugin и могут активироваться по description ([Plugins](https://code.claude.com/docs/en/plugins)).
- Marketplace содержит `plugins[]`; пользователь добавляет источник и устанавливает конкретный plugin ([Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)).
- Один plugin может нести несколько skills и устанавливаться одной операцией.
- Claude имеет host-specific plugin dependencies и bundle-plugin; это нельзя переносить как общий контракт на Codex/Hermes ([Plugin dependencies](https://code.claude.com/docs/en/plugin-dependencies)).

### Hermes Agent

- Skills индексируются из `~/.hermes/skills`; supported sources включают bundled catalog, URL/GitHub и taps ([Skills](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md)).
- GitHub tap регистрирует коллекцию с `skills/<slug>/SKILL.md`, но официальные примеры показывают install отдельного skill; install-all для tap не подтверждён.
- YAML bundle перечисляет уже установленные skills и даёт `/bundle`; отсутствующий skill пропускается. Bundle — runtime alias, не dependency manager и не install package.

### Открытый формат Agent Skills

- Стандарт определяет каталог отдельного skill, frontmatter и относительные support files.
- Universal package manifest, межskill dependency graph и единый install protocol не определены ([Agent Skills specification](https://agentskills.io/specification)).

## Наблюдаемые публичные коллекции

| Коллекция                                                                                   | Наблюдаемый паттерн                                                        | Вывод                                                  |
| ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------ |
| [openai/plugins](https://github.com/openai/plugins)                                         | Один Codex marketplace catalog, plugins могут нести skills/MCP             | package/catalog выше отдельного skill                  |
| [anthropics/skills](https://github.com/anthropics/skills)                                   | Один Claude marketplace source; plugins группируют document/example skills | один plugin install может открыть набор skills         |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Большой каталог с pinned sources/refs                                      | marketplace — индекс, не atomic install каталога       |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)                     | Multi-skill repo и внешняя grouping metadata без обязательного router      | discovery может обходиться descriptions/grouping       |
| [obra/superpowers](https://github.com/obra/superpowers)                                     | Большая библиотека с отдельными harness integration paths                  | одинаковый repo не означает одинаковый install/runtime |

Observed repo patterns не являются стандартом и не доказывают поддержку теми хостами, где соответствующая механика не документирована.

## Router: когда нужен и когда вреден

Router полезен, когда:

- пользователь явно вызывает одну точку входа для классификации `task / project / idea / meeting`;
- один workflow действительно координирует несколько установленных domain skills;
- есть понятное поведение при отсутствии одного из skills.

Router вреден, когда:

- повторяет domain procedures;
- имеет широкое implicit description и конкурирует с дочерними skills;
- притворяется dependency manager;
- появляется до второй реализованной области.

Entity coaching остаётся внутри `jedikit-tasks`, а habit coaching — внутри `jedikit-habits`. Отдельный router не добавляется: mixed request должен явно разделяться на два workflow с независимыми approval boundaries.

## Naming, references и versioning

- Package/repo/plugin: `jedikit`; skills: `jedikit-tasks`, `jedikit-habits`, позднее `jedikit-reminders`, `jedikit-ideas`, `jedikit-projects`.
- Slugs — lowercase hyphenated, уникальные и короче лимита Agent Skills.
- Каждый skill должен быть runtime-самодостаточным. Нельзя полагаться на `../shared`: хосты по-разному копируют/cache plugin directories, а Hermes URL install переносит только явно referenced support files.
- Общий контракт можно поддерживать в canonical source и механически копировать при release, но в опубликованном skill каждая нужная reference лежит локально.
- Universal inter-skill dependencies отсутствуют; Claude dependencies не становятся общим форматом.
- Release фиксируется immutable tag/SHA. Версии manifests повышаются при изменении общего контракта; нельзя предполагать одинаковую semver resolution на трёх хостах.

## Минимальная архитектура v1

```text
jedikit/
├── skills/
│   ├── jedikit-tasks/
│   │   ├── SKILL.md
│   │   └── references/
│   └── jedikit-habits/
│       ├── SKILL.md
│       └── references/
├── adapters/
│   ├── codex/
│   ├── claude/
│   └── hermes/
├── evals/
└── research/
```

Точное release layout будет определено implementation plan и официальными validators. Это схема ответственности, не готовый scaffold.

## Риски трёх хостов

1. Разные manifests, scopes, caches и install semantics.
2. Разная implicit activation и namespacing.
3. Разные collision rules: namespace Claude, duplicate names Codex, local shadowing/bundle precedence Hermes.
4. Claude dependencies не работают как Codex/Hermes dependencies.
5. Разные update/version/hash механизмы.
6. Plugin/tap может включать scripts/hooks/MCP и имеет разную trust-поверхность.
7. Shared relative paths могут сломаться после materialization хостом.

## Подтверждённое решение продукта

- Umbrella identity — да.
- Root/router skill — нет; это вариант A.
- Два независимых skills (`jedikit-tasks`, `jedikit-habits`) — да.
- Implicit natural-language routing и explicit child fallback — да.
- `@jedikit` — только OpenAI plugin scope; `$jedikit` — отсутствующий tag.
- Atomic one-install на всех трёх хостах — не обещать.
- Ideas, waiting, reminders и расширенные projects — backlog до самостоятельной спецификации. Habits вышли из backlog и имеют отдельный академический reference/eval контур.
