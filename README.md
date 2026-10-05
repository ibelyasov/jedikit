# JediKit — Разгрузи голову. Действуй ясно.

Русскоязычный plugin с двумя самостоятельными Agent Skills:

- `jedikit-tasks` — задачи и минимальный проектный контур в SingularityApp;
- `jedikit-habits` — поведенческие эксперименты и обзоры привычек в Habitify.

SingularityApp и Habitify остаются источниками своих данных. Skills работают
через официальные hosted MCP. Собственного сервера, REST fallback и скрытой
синхронизации между провайдерами нет.

**Состояние:** предварительная версия `0.1.0-alpha.3` для тестирования после пересборки обоих
скиллов по исследовательской библиотеке 2026-09-13. Следующий этап — тестирование
в Hermes, единственном обязательном хосте приёмки v1. Codex/Claude runtime
текущей версии не подтверждён. Исторические отчёты находятся в
[`evals/evidence/`](evals/evidence/) и не доказывают работу новых инструкций.

## Использование

Опишите задачу естественным языком: host выбирает skill по описанию.
Для явного вызова в Hermes найдите точное имя установленного skill через
`skills_list`, затем загрузите его через `skill_view`: plugin-имена могут быть
namespaced, короткий alias нельзя считать подтверждённым. Корневого
router-skill нет.

Tasks помогает записать мысль, разобрать Inbox, сформулировать следующий шаг,
проверить проект и провести daily/weekly review. Habits помогает спроектировать,
вести и пересматривать одну поведенческую гипотезу. Смешанный запрос разделяется
на два последовательных workflow с независимыми подтверждениями и отчётами.

Перед изменениями skill применяет свою матрицу подтверждений и проверяет
результат чтением обратно. Привычки не заменяют диагностику или лечение;
проверка безопасности при клиническом риске останавливает обычный coaching и
записи. Узкое исключение — подтверждённое отключение существующего напоминания
или поддержанная логическая пауза. Возможности провайдера,
включая undo и Habitify Off Mode, определяются runtime discovery.

## Установка и подключения

Платформенные основания и ограничения:
[`research/skill-suite-architecture.md`](research/skill-suite-architecture.md).
Локальный кандидат генерируется в `packages/jedikit/`, архив и SHA-256 — в
`build/`. Его можно проверить из корня репозитория без установки и подключения
к личным аккаунтам:

```bash
hermes plugins doctor ./packages/jedikit --ci
```

Эта проверка структуры не заменяет загрузку скиллов и пользовательские сценарии
в Hermes. Команда установки ниже читает GitHub и не устанавливает незакоммиченные
изменения из рабочего каталога.

Для Hermes 0.20.6+ — один skills-only package:

```bash
hermes plugins install ibelyasov/jedikit/packages/jedikit --ref <full-commit-sha> --enable
```

Для опубликованной версии выберите SHA проверенного релиза. Команда без `--ref` устанавливает состояние
удалённой ветки и не фиксирует воспроизводимую версию.

Hermes package использует host-level OAuth connections `singularity` и
`habitify`, предварительно настроенные через `hermes mcp add`. Проверка
подключений — `hermes mcp test singularity` и `hermes mcp test habitify`.
Package не переносит токены и не создаёт plugin-level MCP-дубли.

Codex/Claude plugin не объявляет MCP servers: подключения `singularity` и
`habitify` настраиваются на стороне host. Для установки всего plugin в Codex нужен локальный или опубликованный marketplace. Root manifest
не регистрирует ChatGPT Connected App; это отдельная platform integration.
Claude runtime, реальные Habitify writes и текущая provider acceptance не
подтверждаются локальной сборкой.

## Разработка и проверка

Требуется Python 3.11+; локальные инструменты используют стандартную библиотеку.

```bash
python3 scripts/build.py
python3 evals/run.py check
```

Сборка обновляет platform manifests и `packages/jedikit/skills/` из канонических
исходников, создаёт candidate ZIP и SHA-256 в `build/`. Исторические `dist/`
archives не меняются. Для проверки без генерации: `python3 scripts/build.py --check`.
Тесты сборки: `python3 -m unittest discover -s tests/build -v`.

Править нужно `skills/` и `package-metadata.json`. Сгенерированные manifests и
Hermes-копии коммитятся вместе с исходниками. CI проверяет совпадение, контракты,
негативные regression tests и воспроизводимость сборки. Он не обращается к
провайдерам и не требует домашнего каталога с Codex validator-скриптами.

Release acceptance запускается отдельно:

```bash
python3 evals/run.py release-gate
```

Gate требует свежие Hermes evidence для обоих skills: установку, поведение
и отдельную проверку официального провайдера. Для привычек обязательна полная
матрица сценариев; один ответ на `help` её не заменяет. Отсутствие Codex/Claude
runtime evidence не блокирует v1.

Зелёный offline check не заменяет свежие behavior/host/provider evidence.
Старые ответы и smoke не получают новый source digest задним числом.
Формат evidence и порядок acceptance описаны в
[`research/testing-strategy.md`](research/testing-strategy.md).
Официальные host validators и реальные runtime smoke относятся к отдельной
проверке платформ, а не к воспроизводимой локальной сборке.

## Документация

- [Продуктовые решения](research/product-decisions.md) — согласованный scope и ограничения.
- [Архитектура](research/skill-suite-architecture.md) — ответственность модулей и платформ.
- [Исследовательская библиотека](research/README.md) — подробные основания, источники, примеры и ограничения отдельно от скиллов.
- [Метод задач](research/tasks/README.md) и [исследования привычек](research/habits/README.md) — тематические маршруты чтения.
- [Backlog](BACKLOG.md) — отложенные направления.

## Лицензия и независимость

Оригинальные материалы распространяются по MIT; ограничения сторонних
материалов — в [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
JediKit не связан и не одобрен Максимом Дорофеевым, SingularityApp или Habitify.
