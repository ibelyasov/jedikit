# JediKit — Разгрузи голову. Действуй ясно.

**Версия:** `0.1.0-alpha.1`. Реализация задач и привычек находится в репозитории; это первый prerelease, а не заявление `production-ready`. Реальные пользовательские данные и Habitify writes не входят в release-проверку.

JediKit — русскоязычный plugin/package с двумя самостоятельными Agent Skills:

- `jedikit-tasks` управляет задачами и минимальным проектным контуром в SingularityApp;
- `jedikit-habits` проектирует и ведёт поведенческие эксперименты в Habitify на основе академических данных.

Оба skill используют только официальные hosted MCP. SingularityApp остаётся источником истины для задач, Habitify — для привычек.

## Как это вызывается

Обычно достаточно написать естественным языком: host выбирает skill по его описанию. Для standalone skill Codex использует `$jedikit-tasks` и `$jedikit-habits`; после plugin install их квалифицированные имена — `$jedikit:jedikit-tasks` и `$jedikit:jedikit-habits`.

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

На локальных plugin surfaces Codex/Claude используют root `.mcp.json`, а Hermes Portable Agent Plugin v1 — изолированный `packages/jedikit` с собственными `plugin.json`, `skills/` и `mcp.json`. Включённый package может сделать видимыми оба provider connection. Skills не вызывают чужой provider, но пользователь всё равно должен проверить OAuth consent и доступные tools. Habitify tool names и required fields не угадываются: после OAuth выполняются `initialize`/`tools/list`, а schema drift закрывает текущую операцию без REST или стороннего fallback.

Не сохраняются episodes, вес, sexual details, причины, заметки или токены. Допустимы только timezone, cadence, privacy preference, выбранные habit IDs и технические timestamps обзоров. Чувствительные названия не уходят во внешние уведомления без отдельного opt-in.

Root `.mcp.json` не является универсальной ChatGPT Connected App. ChatGPT/Work требует отдельно зарегистрированного connection/app. Hermes 0.20.6+ читает `packages/jedikit/plugin.json`, оба вложенных `skills/` и `packages/jedikit/mcp.json` как один Portable Agent Plugin v1; OAuth всё равно подтверждается пользователем на стороне каждого provider.

## Локальная проверка candidate

До публикации в отдельных marketplace package можно загрузить напрямую. Для Claude Code:

```bash
claude --plugin-dir /path/to/singularity-jedi-skill
```

Hermes 0.20.6+ устанавливает весь package одной командой после проверки source:

```bash
hermes plugins install ibelyasov/singularity-jedi-skill/packages/jedikit --enable
```

Для воспроизводимой установки релиза используйте указанный в GitHub release полный commit SHA через `--ref <full-commit-sha>`. Подкаталог отделяет публикуемый runtime от research/evidence репозитория, поэтому штатный Hermes security scan проверяет только устанавливаемые файлы. После появления записи с `subdir: packages/jedikit` в Hermes community plugin index идентификатор сократится до `jedikit`. Package регистрирует два namespaced child skills и два namespaced remote MCP, но не выдаёт OAuth-доступ без участия пользователя.

Hermes 0.20.6 регистрирует remote MCP из Portable Agent Plugin v1 под namespaced именами, но его portable-переводчик не передаёт `auth: oauth`, а `hermes mcp login` видит только host-level `mcp_servers`. Поэтому рабочие OAuth-подключения `singularity` и `habitify`, добавленные через `hermes mcp add`, пока нельзя удалять: plugin устанавливает оба skills одной командой, а provider consent остаётся host-level. Не копируйте токены между namespace и не отключайте security scan.

Для Codex one-plugin install нужен опубликованный или локально зарегистрированный marketplace. Smoke этого prerelease проверен через `codex plugin add`; публичная запись в universal Plugins Directory требует отдельной submission/review.

## Разработка и проверка

```bash
python3 evals/fake_mcp.py --self-test
python3 evals/run.py release-gate
uv run --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/jedikit-tasks
uv run --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/jedikit-habits
uv run --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" .
hermes plugins doctor packages/jedikit --ci
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
