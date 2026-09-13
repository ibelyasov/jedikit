# Архитектура коллекции Agent Skills

**Архитектура обновлена:** 2026-09-12 (Europe/Moscow).
**Повторная проверка платформенных источников:** 2026-09-13; локальные runtime smoke этим исследованием не выполнялись. Подробности версий и ограничений — в `platform-codex.md`, `platform-claude.md` и `platform-hermes.md`.

**Статус:** platform research для набора JediKit. Историческая проверка использовала Context7, затем официальные источники. Перепроверка 2026-09-13 опирается на доступные локальные версии/исходники и текущие официальные документы. Продуктовая архитектура и уже реализованные manifests не мигрируют автоматически вслед за изменением платформенных рекомендаций.

## Краткий вывод

Нужно различать **umbrella package/source identity** и **router skill**.

- Единый бренд/репозиторий/plugin полезен: пользователь понимает, что task, habits и будущие skills принадлежат одному набору.
- Широкий implicit router не нужен: хосты уже маршрутизируют skills по `name` и `description`, а router добавит ложные срабатывания и дублирование инструкций.
- Даже после появления второй области выбран вариант A: два независимых implicit skills. Cross-domain workflow делится на отдельные вызовы; отдельный router можно пересмотреть только по новому подтверждённому контракту.
- «Одна установка» реализуется платформенными plugin manifests: Codex и Claude устанавливают plugin с несколькими skills и root `.mcp.json`, а Hermes 0.20.6+ принимает skills-only package с root `plugin.json` и `skills/`.

Решение: umbrella source/package/plugin `jedikit`, независимые skills `jedikit-tasks` и `jedikit-habits`, без root/router skill. Естественный язык — основной UX, explicit child invocation — целевой fallback; для Hermes нужно брать фактическое qualified name из discovery, стабильность имени ещё не принята. `@jedikit` означает только OpenAI plugin mention/scoping; `$jedikit` не существует как portable tag.

## Подтверждённые факты платформ

### Codex

- Portable skill — каталог с `SKILL.md` и optional `scripts/`, `references/`, `assets`; discovery использует `name` и `description`, полное тело загружается при активации ([Build skills](https://learn.chatgpt.com/docs/build-skills)).
- Текущий переносимый plugin содержит root `plugin.json` и `skills/`; OpenAI-настройки вынесены в `extensions.com.openai`. `.codex-plugin/plugin.json` поддерживается как compatibility fallback и остаётся текущим форматом JediKit ([Package plugins](https://developers.openai.com/plugins/build/plugins)).
- Один plugin install выставляет все bundled skills. Marketplace JSON — каталог plugins; добавление marketplace регистрирует источник, а не устанавливает весь каталог.
- Документированные Codex dependencies относятся к tools, а не образуют переносимый skill-to-skill dependency graph.
- Plugin mention `@jedikit` scopes plugin context, но не является отдельным router skill; implicit discovery по descriptions остаётся основным путём.

### Claude Code

- JediKit содержит `.claude-plugin/plugin.json` и `skills/<name>/SKILL.md`; в текущем общем контракте Claude manifest необязателен, но при его наличии нужен `name`. Skills вызываются в namespace plugin и могут активироваться по description ([Plugins](https://code.claude.com/docs/en/plugins), [Plugin reference](https://code.claude.com/docs/en/plugins-reference)).
- Marketplace содержит `plugins[]`; пользователь добавляет источник и устанавливает конкретный plugin ([Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)).
- Один plugin может нести несколько skills и устанавливаться одной операцией.
- Claude имеет host-specific plugin dependencies и bundle-plugin; это нельзя переносить как общий контракт на Codex/Hermes ([Plugin dependencies](https://code.claude.com/docs/en/plugin-dependencies)).

### Hermes Agent

- Одиночные skills по-прежнему индексируются из `~/.hermes/skills` и устанавливаются через Skills Hub/taps ([Skills](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md)).
- Hermes 0.20.6+ отдельно поддерживает Portable Agent Plugins v1: `hermes plugins install <owner/repo/subdir> --enable` клонирует repository, но валидирует и сканирует только выбранный package subdirectory, затем регистрирует все валидные `skills/*/SKILL.md`. JediKit не кладёт туда `mcp.json`.
- Plugin-provided skills read-only и namespaced; они входят в progressive `skills_list`, но не копируются в плоский `~/.hermes/skills`. Root plugin не становится router skill. В установленной 0.20.6 обнаружено имя `agent-plugin-jedikit-805a716c:jedikit-habits`; bare name и `jedikit:jedikit-habits` не разрешаются. Это наблюдение, не стабильный portable identifier: точное имя берётся из `skills_list`. Cron может молча пропустить отсутствующий skill, поэтому успешного job недостаточно без проверки его загрузки.
- В повторно просмотренной локальной реализации Hermes 0.20.6 portable HTTP schema разрешает только `type`, `url`, `headers` и не переносит Claude-specific `auth: oauth`; поэтому текущий package использует host-level MCP connections. Это ограничение проверенной реализации/формата, не общее утверждение о невозможности OAuth у portable MCP. Последний документированный релиз 0.21.2 отдельно отмечен в [platform-hermes.md](platform-hermes.md); он не установлен этой работой.
- YAML skill bundle остаётся runtime alias уже доступных skills, а tap — источником одиночных skills; ни то ни другое не нужно для package install JediKit.

### Открытый формат Agent Skills

- Стандарт определяет каталог отдельного skill, frontmatter и относительные support files.
- Сам Agent Skills определяет отдельный skill, а отдельная спецификация [Agent Plugins 1.0.0](https://agent-plugins.org/specification) уже определяет переносимый root `plugin.json`, skills и MCP-компоненты. Прежний вывод «универсального manifest нет» был слишком широким. Наличие пакетного формата не доказывает одинаковую OAuth/install реализацию хостов или гарантированный вызов одного skill другим.

## Наблюдаемые публичные коллекции

| Коллекция                                                                                   | Наблюдаемый паттерн                                                        | Вывод                                                  |
| ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------ |
| [openai/plugins](https://github.com/openai/plugins)                                         | Один Codex marketplace catalog, plugins могут нести skills/MCP             | package/catalog выше отдельного skill                  |
| [anthropics/skills](https://github.com/anthropics/skills)                                   | Один Claude marketplace source; plugins группируют document/example skills | один plugin install может открыть набор skills         |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Большой каталог с pinned sources/refs                                      | marketplace — индекс, не atomic install каталога       |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)                     | Multi-skill repo и внешняя grouping metadata без обязательного router      | discovery может обходиться descriptions/grouping       |
| [obra/superpowers](https://github.com/obra/superpowers)                                     | Большая библиотека с отдельными harness integration paths                  | одинаковый repo не означает одинаковый install/runtime |

Эти репозитории приведены как примеры организации исходников из исходного исследования; их полный текущий состав этим refresh не аттестуется. Patterns не являются стандартом и не доказывают поддержку конкретного manifest, install или OAuth поведения теми хостами, где соответствующая механика не документирована. Наличие доступного репозитория не является runtime acceptance его plugins.

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
- Release фиксируется immutable tag/SHA. Для Hermes exact install используется `hermes plugins install <owner/repo/packages/jedikit> --ref <full-commit-sha> --enable`; версии manifests повышаются при изменении общего контракта.

## Текущая архитектура

| Module | Interface | Implementation |
| --- | --- | --- |
| Каждый domain skill | `SKILL.md`: intents, порядок работы, обязательные context pointers | Локальные references: метод, операции, provider-specific ограничения |
| Package builder | `python3 scripts/build.py` и `--check` | Общее metadata, platform manifests, Hermes-копии, детерминированный candidate archive |
| Offline checks | `python3 evals/run.py check` | Типизированные fake contracts, replay, проверка evidence и негативные regression tests |
| Release acceptance | `python3 evals/run.py release-gate` | Актуальность behavior evidence и раздельные smoke для hosts/providers |

`skills/` — редактируемый runtime-источник. `package-metadata.json` задаёт общие
метаданные и platform-specific дополнения. `.codex-plugin/plugin.json`,
`.claude-plugin/plugin.json` и `packages/jedikit/` генерируются и проверяются на
совпадение с исходником. `build/` содержит локальный candidate; `dist/` сохраняет
исторические release artifacts. Сборка не устанавливает и не публикует plugin.

Seam между workflow и провайдером находится в локальном provider reference:
workflow выбирает намерение, provider contract сопоставляет его с обнаруженными
MCP capabilities. Это текстовый interface для агента, а не собственный MCP
сервер или программный SDK. Различия tasks/habits не скрываются общим CRUD.

В habits обязательная safety-справка загружается до coaching и provider actions.
Матрица подтверждений имеет одно нормативное место; coaching и provider
references направляют к ней. Датированные REST facts не входят в runtime.
Mixed-request protocol доступен из каждого child skill, без дополнительного
router и зависимости на вызов другого skill.

Eval-модули разделяют tool contract, воспроизведение состояния, оценку
поведения и release policy. Проверка ledger использует тот же типизированный
контракт, что fake MCP. Установка пакета, выполнение skill и подключение
провайдера — разные утверждения: каждое требует evidence своего вида.
Offline gate проверяет implementation, но не превращает старые ответы в
новое доказательство поведения изменённых инструкций.

Research хранит основания решений и датированные наблюдения. Текущий продуктовый
scope определяется `product-decisions.md`; команды разработчика — корневым
README. Отдельный постоянный слой спецификаций не создаётся.

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
- Implicit natural-language routing и explicit child fallback — целевой UX; стабильный explicit identifier Hermes требует отдельной приёмки.
- `@jedikit` — только OpenAI plugin scope; `$jedikit` — отсутствующий tag.
- Atomic one-install на всех трёх хостах — не обещать.
- Ideas, waiting, reminders и расширенные projects — backlog до самостоятельной спецификации. Habits вышли из backlog и имеют отдельный академический reference/eval контур.

## Объём поддержки и отдельная исследовательская база

| Область | Принятое направление | Фактическая граница |
| --- | --- | --- |
| Hermes | Единственный обязательный хост приёмки v1 | Parser/discovery подтверждены; свежая полная behavior/provider acceptance ещё нужна |
| Codex/Claude | Сохраняются материалы о платформе и текущие package manifests | Runtime-совместимость текущего candidate не подтверждена |
| Release gate | Hermes-only обязательная матрица обоих skills | Реализована структурно; свежие реальные Hermes artifacts ещё отсутствуют |
| Research | Самостоятельная подробная библиотека в `research/` | Не исполняемая политика и не доказательство успешного runtime |
| Skills | Автономные инструкции с локальными оперативными references | Обязательные safety/operation правила остаются доступны внутри пакета |

Исследование привычек больше не требует читать runtime references как
единственный полный источник: подробные досье находятся в
[research/habits](habits/README.md), метод задач — в [research/tasks](tasks/README.md).
При изменении основания сначала фиксируется вывод и его влияние, затем
согласованный контракт переносится в skill и проверяется. Это сохраняет
самодостаточность пакета и позволяет библиотеке быть существенно подробнее
оперативных инструкций.
