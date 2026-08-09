# JediKit — Разгрузи голову. Действуй ясно.

**Статус:** `v0.1.0-alpha.1`. Первый релиз русскоязычный.

JediKit — portable Agent Skill для управления задачами и минимальным проектным контуром в SingularityApp через официальный hosted MCP. Он помогает формулировать задачи, разбирать Inbox, проводить daily/weekly review и безопасно применять подтверждённые изменения.

## Что входит в alpha

- классификация `задача / проект / идея / справка / встреча`;
- setup областей `Работа`, `Личное` и дочерних `Общее` без автоматической миграции;
- явный capture во Inbox и поштучный triage;
- daily open/close, weekly review и проверка проекта;
- preview, подтверждение, последовательные записи и честный отчёт о частичном сбое;
- минимальная native memory хоста и privacy-safe scheduled приглашения.

JediKit не управляет календарём, привычками, ожиданиями, напоминаниями или отдельным процессом идей; не обещает permanent delete, настоящий batch, автоматический следующий шаг либо фоновые записи после завершения диалога.

## Требования

- аккаунт SingularityApp с доступом к официальному MCP;
- Codex, Claude Code или Hermes Agent;
- OAuth-авторизация MCP на стороне выбранного хоста.

Для минимального доступа нужны scopes `tasks:read/write/check`, `projects:read/write`, `tags:read/write`, `checklists:read/write` и `mcp:read/write`. Не выдавайте доступ к habits, kanban или time statistics для этого skill.

## Установка

### Codex

Публичный marketplace ещё не заявлен. После публикации репозитория установите skill по GitHub-пути через встроенный `$skill-installer`, затем добавьте официальный MCP:

```text
$skill-installer install https://github.com/ibelyasov/singularity-jedi-skill/tree/main/skills/jedikit-tasks
```

```bash
codex mcp add singularity --url https://mcp.singularity-app.com/mcp
codex mcp login singularity
codex mcp list
```

Откройте новую сессию и проверьте `/skills`, `/mcp`, затем вызовите `$jedikit-tasks` явно.

### Claude Code

Для alpha клонируйте репозиторий и запустите локальный plugin:

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
python3 evals/run.py score evals/evidence/baseline.jsonl --phase baseline
python3 evals/run.py score evals/evidence/green.jsonl --phase green
uv run --with pyyaml python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/jedikit-tasks
uv run --with pyyaml python ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

Runtime-only alpha artifact: `dist/jedikit-tasks-v0.1.0-alpha.1.zip`; контрольная сумма лежит рядом в `.zip.sha256`.

Исследовательская база: [research/README.md](research/README.md). Отложенные направления: [BACKLOG.md](BACKLOG.md).

## Лицензия и независимость

Оригинальные материалы проекта распространяются по MIT; ограничения по сторонним материалам перечислены в [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

JediKit — независимый проект, не связанный и не одобренный Максимом Дорофеевым или SingularityApp.
