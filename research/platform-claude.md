# Claude / Claude Code: распространение и эксплуатация JediKit

Проверено **2026-09-13** по текущей официальной документации Claude. Локальный
Claude runtime, account, marketplace install, OAuth и provider calls в этой
работе не проверялись. Claude Code, Claude.ai/Desktop и Claude API имеют разные
installation и scheduling surfaces; skill или plugin между ними автоматически
не синхронизируется.

## Вывод для JediKit

Текущий repository layout уже соответствует обычному Claude Code plugin:

```text
repo/
├── .claude-plugin/plugin.json
├── .mcp.json
└── skills/
    ├── jedikit-tasks/SKILL.md
    └── jedikit-habits/SKILL.md
```

Manifest `.claude-plugin/plugin.json` в актуальном контракте необязателен, а
если присутствует, обязательным полем является только `name`. JediKit сохраняет
manifest для version и metadata. Компоненты располагаются в корне plugin, а не
в `.claude-plugin/`. Claude Code автоматически namespaces plugin skills
([plugins](https://code.claude.com/docs/en/plugins),
[reference](https://code.claude.com/docs/en/plugins-reference)).

Корневой `.mcp.json` уже объявляет два remote HTTP server: SingularityApp и
Habitify. Это часть Claude host package, а не переносимый Agent Plugins v1
manifest. URL не содержат секретов; OAuth consent и доступность backend всё ещё
нужно проверять в реальной Claude session.

## Проверенная матрица

| Область | Текущий контракт | Решение JediKit | Граница проверки |
| --- | --- | --- | --- |
| Skills | Claude Code читает project, user и plugin `skills/<name>/SKILL.md`; plugin skills namespaced ([skills](https://code.claude.com/docs/en/skills)) | Поставлять оба существующих skills в одном plugin | Фактический slash/model invocation не проверялся |
| Plugin manifest | `.claude-plugin/plugin.json` optional; при наличии `name` required; `skills/`, `.mcp.json`, hooks и agents находятся в plugin root ([reference](https://code.claude.com/docs/en/plugins-reference)) | Сохранить manifest и текущий root layout | Marketplace/install не выполнялись |
| Local validation | Документирован `claude plugin validate <path>`, `plugin list --json`, `plugin details`; `--strict` в текущем CLI contract не заявлен ([marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)) | Использовать validate без `--strict` | Команды не запускались без локально подтверждённой версии Claude |
| MCP | Project/plugin `.mcp.json` поддерживает remote HTTP; project server требует trust/approval при интерактивном использовании ([MCP](https://code.claude.com/docs/en/mcp)) | Сохранить два текущих HTTP server; секреты не коммитить | OAuth и provider tool calls не проверялись |
| Session scheduling | `/loop` и CronCreate работают пока запущена session; recurring task истекает через 7 дней ([scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)) | Только для коротких session-bound reminders | Не считать долговечным scheduler |
| Durable scheduling | Cloud scheduled tasks запускаются в fresh remote session; Desktop local tasks используют локальную среду, пока компьютер доступен ([scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)) | Выбирать native surface по требуемому доступу к repo/data | Создание task и delivery не проверялись |
| Claude.ai / API Skills | Claude.ai upload и Skills API — отдельные surfaces; API skills исполняются в Code Execution sandbox с ограничениями runtime/network ([overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), [API guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide)) | Не выдавать Claude Code plugin install за API/Claude.ai deployment | API wrapper/archive остаются отдельной будущей работой |

## Onboarding и acceptance checklist

Команды ниже не выполнялись в этом исследовании. Сначала нужно сверить локальную
версию с её `--help`, затем проверять package без provider mutation.

```bash
claude --version
claude doctor
claude plugin validate .
claude --plugin-dir .
```

В интерактивной session проверить оба namespaced skills, `/plugin` → Errors и
`/mcp`. Затем в новой session подтвердить, что оба MCP server видны, OAuth
consent понятен пользователю и read-only provider probes возвращают ожидаемый
shape. Публикация marketplace требует отдельного release решения; собственный
Git/GitHub marketplace и Anthropic community directory — разные trust и
distribution каналы ([plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces),
[community directory](https://github.com/anthropics/claude-plugins-community)).

## Scheduling boundary

| Нужен сценарий | Native surface |
| --- | --- |
| Короткий повтор при открытом Claude Code | `/loop` / session cron |
| Fresh remote run без локального диска | Cloud scheduled task |
| Доступ к разрешённым локальным файлам | Desktop local scheduled task |
| API service со своим lifecycle | Agent SDK и внешний scheduler |

Skill не должен автоматически выбирать scheduling surface, provider или
permission mode. Safety exceptions и approval policy остаются предметом
grilling; этот research refresh их не меняет. Ранее предложенное
`disable-model-invocation: true` удалено как продуктовое решение: оно также
запрещает автоматический и scheduled вызов skill и потому конфликтует с
согласованным направлением продукта. Конкретная policy должна быть принята
отдельно и проверена в runtime.

## Что остаётся неизвестным

- Локальная версия Claude Code и соответствие её parser текущим docs не
  проверены.
- Ни один JediKit skill не вызван в Claude runtime; MCP OAuth и tool result не
  проверены.
- Cloud/Desktop scheduling и delivery не проверялись.
- Для v1 владелец выбрал обязательную приёмку только в Hermes; Claude и Codex
  остаются без подтверждённой runtime-совместимости. См. [решения](product-decisions.md).

## Как выбирать поверхность и разбирать неполадки

Следующие различия важны при будущей проверке Claude. Они объясняют уже
приведённые официальные контракты, но не добавляют Claude к обязательной
приёмке v1.

- **Claude Code plugin:** проверяются layout, выбранный источник и version,
  затем namespace обоих skills и их доступность в новой сессии. Marketplace
  является способом доставки; появление listing не доказывает работу skill.
- **Project/user configuration:** важно, где задан MCP и кому доступен этот
  scope. Копирование проекта не переносит автоматически пользовательский OAuth.
  Доверие проекту, разрешение tools и осмысленное согласие на изменение данных
  следует различать.
- **Claude.ai/Desktop/API:** наличие одинакового Markdown-файла не делает
  одинаковыми окружение, подключённые серверы, доступ к диску и scheduling.
  Для каждой поверхности нужен собственный наблюдаемый тест.
- **Фоновый запуск:** заранее надо выяснить, как хост поступает с действием,
  требующим интерактивного согласия. Успех интерактивного запроса не доказывает
  возможность такого действия без человека. Снятие ограничений permissions
  не является способом подтвердить корректность политики JediKit.

Диагностика идёт от узкого слоя к широкому: прочитан ли нужный package source,
прошёл ли manifest validation, какие skills объявлены, что доступно текущей
session, какие MCP servers/tools доступны и только затем — правильность
ответа. В актуальной документации есть `plugin list --json` и `plugin details`;
точную поддержку локальной версии перед использованием нужно проверить по её
справке. Команды перезагрузки/cache и unattended flags не считаются проверенными
в этой записке.

Для scheduling отдельно записываются место исполнения, жизненный цикл,
доступный context, требуемые permissions и delivery target. Иллюстративный
сбой: session-bound повтор прекращается вместе с сессией, хотя пользователь
ожидал постоянное напоминание. Это пример несоответствия требований выбранной
поверхности, не наблюдавшийся сбой JediKit.
