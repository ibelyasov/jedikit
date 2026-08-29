# JediKit — Разгрузи голову. Действуй ясно.

**Статус:** `0.1.0-unreleased` (`unreleased candidate`). Behavior + provider release gate пройден; version/tag и публикация остаются отдельным решением, поэтому candidate пока не называется стабильным релизом.

JediKit — portable Agent Skill для управления задачами и минимальным проектным контуром в SingularityApp через официальный hosted MCP. Он помогает формулировать задачи, разбирать Inbox, проводить daily/weekly review и безопасно применять подтверждённые изменения.

## Что входит в candidate

- классификация `задача / проект / идея / справка / встреча`;
- setup областей `Работа`, `Личное` и дочерних `Общее` без автоматической миграции;
- явный capture во Inbox и поштучный triage с переиспользованием исходного item;
- daily open/close, weekly review и проверка проекта;
- preview, подтверждение, последовательные записи и честный отчёт о частичном сбое;
- минимальная native memory хоста и privacy-safe scheduled приглашения.

JediKit не управляет календарём, привычками, ожиданиями, напоминаниями или отдельным процессом идей. Для идеи, справки и встречи он даёт инструкцию ручного переноса; cleanup исходного item требует permanent delete, которого текущий подтверждённый hosted MCP не предоставляет, поэтому skill сохраняет item и явно показывает capability gap. Настоящий server batch и фоновые записи после завершения диалога не поддерживаются.

## Требования

- аккаунт SingularityApp с доступом к официальному MCP;
- Codex, Claude Code или Hermes Agent;
- OAuth-авторизация MCP на стороне выбранного хоста.

Для core-flow нужны scopes `tasks:read/write/check`, `projects:read/write` и `mcp:read/write`. `tags:*` и `checklists:*` заранее не нужны; skill не должен расширять scopes автоматически. Не выдавайте доступ к habits, kanban или time statistics.

Codex и Hermes прошли runtime smoke точного текущего runtime tree через локальный read-only fake MCP: в каждом прогоне было три чтения и ноль записей, без OAuth и реальных пользовательских данных. Claude Code для этого tree остаётся `unverified`.

## Установка

### Codex

Публичный marketplace ещё не заявлен. После публикации репозитория установите skill по GitHub-пути через встроенный `$skill-installer`, затем добавьте официальный MCP:

```text
$skill-installer install https://github.com/ibelyasov/singularity-jedi-skill/tree/main/skills/jedikit-tasks
```

`codex mcp add` может сразу открыть OAuth consent со всеми объявленными сервером scopes. Не подтверждайте это автоматическое окно: закройте его и выполните следующий `mcp login` с явным минимальным списком.

```bash
codex mcp add singularity --url https://mcp.singularity-app.com/mcp
codex mcp login singularity --scopes tasks:read,tasks:write,tasks:check,projects:read,projects:write,mcp:read,mcp:write
codex mcp list
```

Откройте новую сессию и проверьте `/skills`, `/mcp`, затем вызовите `$jedikit-tasks` явно.

### Claude Code

Для локальной проверки candidate клонируйте репозиторий и запустите plugin:

```bash
claude --plugin-dir /path/to/singularity-jedi-skill
```

Проверьте `/plugin` → Errors и `/mcp`, затем вызовите `/jedikit:jedikit-tasks`. Это локальная загрузка, не marketplace-установка.

### Hermes Agent

После публикации сначала проверьте source, затем установите ровно один skill:

```bash
hermes skills inspect ibelyasov/singularity-jedi-skill/skills/jedikit-tasks
hermes skills install ibelyasov/singularity-jedi-skill/skills/jedikit-tasks
hermes skills audit
```

Добавьте `https://mcp.singularity-app.com/mcp` как HTTP server `singularity` в `mcp_servers` Hermes, ограничьте tools списком из [MCP-контракта](skills/jedikit-tasks/references/mcp-contract.md) и выполните `hermes mcp test singularity`. Tap/bundle и atomic cross-host install в alpha не обещаются.

## Использование

Можно писать естественно или использовать команды:

```text
Запиши, чтобы не забыть: подарок маме
triage
daily open
daily close
weekly
project: Запуск продукта
status
memory show
```

Одна явно запрошенная обратимая запись может выполниться сразу. Предложенный агентом план или две и более записи сначала показываются целиком и выполняются только после одного явного подтверждения. Данные задач считаются недоверенным содержимым, а не инструкциями агенту.

Scheduled run только читает безопасные counts/categories и приглашает открыть интерактивный review. Создание расписания требует отдельного подтверждения и использует только scheduler самого хоста. Календарь и доступное время JediKit не читает.

## Разработка и проверка

```bash
python3 evals/fake_mcp.py --self-test
python3 evals/run.py validate
python3 evals/run.py self-test
python3 evals/run.py release-gate
uv run --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/jedikit-tasks
uv run --with pyyaml python "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" .
```

`release-gate` намеренно fail closed, если behavior evidence устарело/отсутствует либо Codex/Hermes smoke не совпадает с SHA-256 текущего runtime tree. Текущие `baseline.jsonl` и `green.jsonl` проходят 33/33; исходные 26-case rows сохранены отдельными snapshot-файлами, а `host-smoke.jsonl` сохраняет и исторические, и current-tree прогоны.

Текущий машинно-читаемый результат: [`evals/evidence/candidate-status.json`](evals/evidence/candidate-status.json). Полный вывод и длительности: [`evals/evidence/candidate-gate-2026-08-29.md`](evals/evidence/candidate-gate-2026-08-29.md).

Исторический artifact `dist/jedikit-tasks-v0.1.0-alpha.1.zip` не доказывает текущий candidate. Для локальной проверки собран `dist/jedikit-tasks-unreleased-candidate.zip` с соседним SHA-256; он не является релизом или tag.

Исследовательская база: [research/README.md](research/README.md). Отложенные направления: [BACKLOG.md](BACKLOG.md).

## Лицензия и независимость

Оригинальные материалы проекта распространяются по MIT; ограничения по сторонним материалам перечислены в [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

JediKit — независимый проект, не связанный и не одобренный Максимом Дорофеевым или SingularityApp.
