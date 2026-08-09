# Backlog

Отложенные области после завершённого grilling 2026-08-09. Это не roadmap и не обещание релиза: пункт получает scope только после отдельного исследования, grilling и acceptance cases.

## Future skills

### Ideas

- Отдельный ideas review/инкубатор.
- Cadence и правила пересмотра не считать автоматически weekly: авторская универсальная периодичность не подтверждена.
- Решения `оставить / дешёвый тест / task / project / убрать` требуют отдельного workflow и evals.
- v1 только распознаёт идею и предлагает пользовательское место; собственной структуры не создаёт.

### Waiting / delegation

- Определить семантику ожидания, follow-up и владельца результата.
- Не превращать чужую работу в личную задачу и не отправлять сообщения без подтверждения.
- Не создавать `Ожидание` как служебный контейнер до решения пользователя.

### Reminders

- Развести reminder, плановую дату `start`, внешний `deadline`, событие календаря и scheduled agent notification.
- Исследовать host-native reminder/scheduler capabilities и privacy delivery.
- Не имитировать reminder без подтверждённого канала и runtime.

### Habits

- Исследовать канон/другие методологии отдельно от task workflow.
- Спроектировать отдельные OAuth scopes и MCP tools (`habit_*`, `habit_progress_*`).
- Не включать habits scopes в task-skill.

### Projects

- Расширенное планирование, roadmap, milestones, зависимости, multi-project review и project health.
- Сохранить границу: текущий task-skill умеет только результат, полезный контекст, один следующий шаг, weekly check и archive.

## Integrations

- Calendar integration для реальной проверки вместимости daily и ближайших ограничений weekly.
- Event/webhook layer, только если vendor когда-либо предоставит подтверждённый контракт или появится обоснованный poller.
- Router/bundle после появления второй зрелой области.
- Marketplace submissions Codex/Claude и Hermes tap/Hub после стабильного GitHub release.

## Explicitly not planned without new evidence

- собственный production MCP;
- REST fallback;
- permanent delete через skill;
- транзакционный server batch, которого нет в hosted MCP;
- telemetry;
- self-update или scheduled installation;
- служебные проекты, теги, notebooks и metadata-блоки;
- public support SLA.
