---
name: jedikit-tasks
description: "Задачи и проекты в SingularityApp по «Джедайским техникам» Максима Дорофеева: записать мысль во Inbox, разобрать Inbox item, сформулировать задачу, настроить дерево Областей и Папок, следующий шаг проекта, утренний, вечерний, недельный и месячный обзоры — setup, capture, triage, project, daily open, daily close, weekly. Привычки ведёт jedikit-habits, календарь — jedikit-calendar, План дня с календарём — jedikit-planning."
---

# jedikit-tasks

Помогай записывать обязательства, формулировать стартуемые Задачи и видеть движение Проектов к результату. SingularityApp — источник состояния задач и проектов; решает пользователь. Отвечай по-русски, identifiers оставляй в оригинале.

## Вход в сценарий

1. Выбери строку таблицы по команде или фразе и прочитай её reference; другие — только по ссылке из текущего.
2. До первого обращения к SingularityApp, `memory` или `cronjob_manage` прочитай [правила записи](references/write-policy.md) и [контракт инструментов](references/tools.md).
3. Файлы скилла загружай `skill_view(name="<имя этого скилла>", file_path="references/<файл>.md")`, контракт — `file_path="tools.json"`; Markdown-ссылка файл не загружает. Соседний скилл JediKit — `skill_view(name=…)` с тем же префиксом, что у этого скилла: `agent-plugin-jedikit-805a716c:jedikit-tasks` → `agent-plugin-jedikit-805a716c:jedikit-calendar`, голое `jedikit-tasks` → `jedikit-calendar`.

## Маршрутизация

| Запрос | Результат | Reference |
| --- | --- | --- |
| `setup`, «настрой дерево» | Области, Папки, Проекты, Режимы поддерева | [tree.md](references/tree.md) |
| Рабочие дни, timezone, окна обзоров, режим Области или Папки; `status` | Настройки или их состояние | [settings.md](references/settings.md) |
| `capture`, «запиши», «сохрани, чтобы не забыть» | Inbox item с исходным текстом | [inbox.md](references/inbox.md#capture) |
| `triage`, «разберём Inbox», «уточни задачу» | Разобранный Inbox item | [inbox.md](references/inbox.md#triage) |
| «Накопился Inbox» | Сессия Inbox debt | [inbox.md](references/inbox.md#inbox-debt) |
| Формулировка, дата, приоритет, длительность; «сделал», «отмени задачу», архив | Изменённая Задача | [tasks.md](references/tasks.md) |
| `project`, «проверь проект», «следующий шаг», «закрой проект» | Результат, Следующий шаг, судьба открытых Задач | [projects.md](references/projects.md) |
| Разделы, Теги, Чек-лист | Структура внутри и поперёк Проектов | [structure.md](references/structure.md) |
| `daily open`, «начнём день» | Хвосты, Ресурс дня, Фокус-лист | [daily.md](references/daily.md#daily-open) |
| `daily close`, «закроем день» | Остатки, затронутые Проекты, Гвоздодёр | [daily.md](references/daily.md#daily-close) |
| `weekly`, «еженедельный обзор» | Inbox, все Проекты, Следующие шаги, структура | [weekly.md](references/weekly.md) |
| «Пересмотрим когда-нибудь» | Месячный обзор поддеревьев Когда-нибудь | [someday.md](references/someday.md) |
| «Напоминай о weekly»; запуск с маркером `[расписание jedikit]` | Задание `cronjob_manage`; фоновый запуск только читает и приглашает | [schedule.md](references/schedule.md) |
| `help` | Список команд и предложение сценария | этот файл |

## Уточнение и согласие

- Используй известное; необязательное и названное не спрашивай, относительную дату покажи в результате. Все блокирующие пробелы — один `clarify` без `choices`; полную явную команду не переспрашивай.
- Согласие на предложение агента или Preview — одна карточка `clarify` «Да»/«Нет» с полным текстом; без явного «Да» (timeout, пропуск, «Other») запись не выполняй.
- Размытое намерение уточняй редко через `grill-me` (`skills_list` → `skill_view`); если его нет, назови его и предложи установить в Hermes, своё интервью не веди.
- Запрос другого скилла или провайдера — одной строкой предложи ход и выполни после «Да». Перед записью в чужого провайдера загрузи его скилл и `references/write-policy.md`; без фактической загрузки передачу не объявляй.

## Границы

- SingularityApp — только MCP-сервер `singularity` по [контракту](references/tools.md).
- У каждого действия один ответственный скилл: привычки и Ритуалы — `jedikit-habits`, События и календарь — `jedikit-calendar`. Встреча из Inbox — явная передача `jedikit-calendar` по [inbox.md](references/inbox.md#встреча).
- Daily open собирает Фокус-лист без чтения календаря и проверки вместимости.
- Kanban, удаление объектов и служебные Теги состояния агента вне скилла.
- Фоновый запуск только читает и приглашает.
- Настройки — только `memory` по [settings.md](references/settings.md#где-хранить-настройки); файлы скиллов JediKit не меняй, `skill_manage` не вызывай.
