# JediKit — Разгрузи голову. Действуй ясно.

**Статус:** `0.1.0-unreleased`. Реализация задач и привычек находится в репозитории; tag, публикация, реальные пользовательские данные и авторизованный Habitify smoke остаются отдельными решениями.

JediKit — русскоязычный plugin/package с двумя самостоятельными Agent Skills:

- `jedikit-tasks` управляет задачами и минимальным проектным контуром в SingularityApp;
- `jedikit-habits` проектирует и ведёт поведенческие эксперименты в Habitify на основе академических данных.

Оба skill используют только официальные hosted MCP. SingularityApp остаётся источником истины для задач, Habitify — для привычек.

## Как это вызывается

Обычно достаточно написать естественным языком: host выбирает skill по его описанию. Прямые `$jedikit-tasks` и `$jedikit-habits` нужны только как fallback.

В OpenAI `@jedikit` означает mention/scoping всего plugin. Это не третий skill и не router. Корневого `$jedikit` нет. В Claude и Hermes синтаксис explicit invocation отличается, поэтому portable-контракт опирается на независимые child skills, а не на межskill API.

Смешанный запрос про задачи и привычки делится на два последовательных workflow с отдельными подтверждениями. Общей транзакции или cross-provider rollback нет.

## Задачи

`jedikit-tasks` помогает:

- записать мысль во Inbox и разобрать её поштучно;
- сформулировать наблюдаемое следующее действие;
- минимально создать/проверить проект;
- провести daily open/close и weekly review;
- безопасно выполнить подтверждённые изменения с read-back.

Он не использует Singularity habits scopes и не подменяет привычку задачей. Календарь, ожидания, напоминания и отдельный процесс идей остаются вне текущего scope.

## Привычки

`jedikit-habits` — evidence-aware coach/operator для `setup`, `design`, `log`, `urge`, `review`, `adjust`, `pause`, `off`, `archive`, `status` и `help`.

Ключевые границы:

- снижение веса — outcome, а не привычка; skill работает с поздней едой, перееданием, сладким, покупками/планированием, движением и другими наблюдаемыми процессами;
- порно и мастурбация — два отдельных эксперимента; точные названия пользователя допустимы, abstinence не объявляется медицински полезной;
- существующая Habitify habit становится managed experiment только после явного adopt и согласованного человекочитаемого плана;
- один прямо запрошенный одиночный обратимый log может выполниться сразу только при обнаруженных native undo и read-back; остальные записи требуют preview, а permanent delete — отдельного подтверждения;
- clinical/safety risk останавливает coaching и записи; skill не диагностирует и не назначает лечение;
- Off Mode используется только как обнаруженная нативная account-wide capability Habitify. Если MCP её не показывает, skill даёт ручную UI-инструкцию и ничего не эмулирует.

Академические обзоры и provider-контракт находятся в [`skills/jedikit-habits/references`](skills/jedikit-habits/references). Runtime загружает только релевантный reference, поэтому `SKILL.md` остаётся рабочей инструкцией, а не энциклопедией.

## MCP и приватность

Plugin использует утверждённый вариант A и упаковку `bundle-both`: два независимых
child skills без root/router и два серверных подключения на plugin root:

- `singularity` — `https://mcp.singularity-app.com/mcp`;
- `habitify` — `https://mcp.habitify.me/mcp`.

На локальных plugin surfaces Codex/Claude root `.mcp.json` находится на уровне всего plugin: включённый bundle может сделать видимыми оба provider connection. Skills не вызывают чужой provider, но пользователь всё равно должен проверить OAuth consent и доступные tools. Habitify tool names и required fields не угадываются: после OAuth выполняются `initialize`/`tools/list`, а schema drift закрывает текущую операцию без REST или стороннего fallback.

Не сохраняются episodes, вес, sexual details, причины, заметки или токены. Допустимы только timezone, cadence, privacy preference, выбранные habit IDs и технические timestamps обзоров. Чувствительные названия не уходят во внешние уведомления без отдельного opt-in.

Root `.mcp.json` не является универсальной ChatGPT Connected App или Hermes-конфигурацией. ChatGPT/Work требует отдельно зарегистрированного connection/app, а Hermes — отдельного `hermes mcp add`; это не выполняется автоматически этим репозиторием.

## Локальная проверка candidate

Публичный marketplace ещё не заявлен. Для Claude Code plugin можно загрузить локально:

```bash
claude --plugin-dir /path/to/singularity-jedi-skill
```

Hermes устанавливает skills отдельно; после проверки source:

```bash
hermes skills inspect ibelyasov/singularity-jedi-skill/skills/jedikit-tasks
hermes skills install ibelyasov/singularity-jedi-skill/skills/jedikit-tasks
hermes skills inspect ibelyasov/singularity-jedi-skill/skills/jedikit-habits
hermes skills install ibelyasov/singularity-jedi-skill/skills/jedikit-habits
hermes mcp add singularity --url https://mcp.singularity-app.com/mcp --auth oauth
hermes mcp add habitify --url https://mcp.habitify.me/mcp --auth oauth
```

Не запускайте эти команды поверх уже настроенных одноимённых MCP без проверки текущего config. Для Codex one-plugin install нужен опубликованный или локально зарегистрированный marketplace; его создание/установка не входит в этот candidate turn.

## Разработка и проверка

```bash
python3 evals/fake_mcp.py --self-test
python3 evals/run.py release-gate
uv run --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/jedikit-tasks
uv run --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/jedikit-habits
uv run --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" .
```

Существующий task harness остаётся без второго параллельного Python-контура. `jedikit-habits` проверяется штатным skill-validator, plugin-validator и локальными ссылками; независимые forward-прогоны выполняются в изолированном временном workspace и не сохраняют сырые сессии в Git.

Старый task-only результат сохранён как исторический в
[`evals/evidence/candidate-gate-2026-08-29.md`](evals/evidence/candidate-gate-2026-08-29.md).
Claude runtime и реальный Habitify OAuth/account остаются `unverified`.

Исследовательская база и журнал решений: [`research/README.md`](research/README.md)
и [`research/habits-grill-decisions.md`](research/habits-grill-decisions.md).
Отложенные направления: [`BACKLOG.md`](BACKLOG.md).

## Лицензия и независимость

Оригинальные материалы проекта распространяются по MIT; ограничения по сторонним материалам перечислены в [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).

JediKit — независимый проект, не связанный и не одобренный Максимом Дорофеевым, SingularityApp или Habitify.
