# JediKit — Разгрузи голову. Действуй ясно.

Русскоязычный plugin с двумя самостоятельными Agent Skills:

- `jedikit-tasks` — задачи и минимальный проектный контур в SingularityApp;
- `jedikit-habits` — поведенческие эксперименты и обзоры привычек в Habitify.

SingularityApp и Habitify остаются источниками своих данных. Skills работают
через официальные hosted MCP. Собственного сервера, REST fallback и скрытой
синхронизации между провайдерами нет.

**Состояние:** локальный candidate после архитектурного ревью 2026-09-12.
Базовая версия manifests — `0.1.0-alpha.2`; она не означает, что изменённый tree
прошёл новую release acceptance. Исторические отчёты находятся в
[`evals/evidence/`](evals/evidence/). Готовность текущего tree определяет
`release-gate`, отдельно от offline проверки кода.

## Использование

Опишите задачу естественным языком: host выбирает skill по описанию.
Для прямого вызова в Codex standalone-имена — `$jedikit-tasks` и
`$jedikit-habits`; после plugin install — `$jedikit:jedikit-tasks` и
`$jedikit:jedikit-habits`. `@jedikit` обозначает plugin scope. Корневого
router-skill нет.

Tasks помогает записать мысль, разобрать Inbox, сформулировать следующий шаг,
проверить проект и провести daily/weekly review. Habits помогает спроектировать,
вести и пересматривать одну поведенческую гипотезу. Смешанный запрос разделяется
на два последовательных workflow с независимыми подтверждениями и отчётами.

Перед изменениями skill применяет свою матрицу подтверждений и проверяет
результат чтением обратно. Привычки не заменяют диагностику или лечение;
clinical/safety stop прекращает coaching и записи. Возможности провайдера,
включая undo и Habitify Off Mode, определяются runtime discovery.

## Установка и подключения

Проверенный платформенный срез — 2026-08-29. Подробности и ограничения:
[`research/skill-suite-architecture.md`](research/skill-suite-architecture.md).

Для локального candidate в Claude Code:

```bash
claude --plugin-dir /path/to/jedikit
```

Для Hermes 0.20.6+ — один skills-only package:

```bash
hermes plugins install ibelyasov/jedikit/packages/jedikit --ref <full-commit-sha> --enable
```

Выберите SHA проверенного релиза. Команда без `--ref` устанавливает состояние
удалённой ветки и не фиксирует воспроизводимую версию.

Hermes package использует host-level OAuth connections `singularity` и
`habitify`, предварительно настроенные через `hermes mcp add`. Проверка
подключений — `hermes mcp test singularity` и `hermes mcp test habitify`.
Package не переносит токены и не создаёт plugin-level MCP-дубли.

Root `.mcp.json` объявляет подключения для Codex/Claude. Для установки всего
plugin в Codex нужен локальный или опубликованный marketplace. Root manifest
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

Зелёный offline check не заменяет свежие behavior/host/provider evidence.
Старые ответы и smoke не получают новый source digest задним числом.
Формат evidence и порядок acceptance описаны в
[`research/testing-strategy.md`](research/testing-strategy.md).
Официальные host validators и реальные runtime smoke относятся к отдельной
проверке платформ, а не к воспроизводимой локальной сборке.

## Документация

- [Продуктовые решения](research/product-decisions.md) — согласованный scope и ограничения.
- [Архитектура](research/skill-suite-architecture.md) — ответственность модулей и платформ.
- [Исследования](research/README.md) — источники и датированные основания решений.
- [Backlog](BACKLOG.md) — отложенные направления.

## Лицензия и независимость

Оригинальные материалы распространяются по MIT; ограничения сторонних
материалов — в [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
JediKit не связан и не одобрен Максимом Дорофеевым, SingularityApp или Habitify.
