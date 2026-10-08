---
name: jedikit-habits
description: "Привычки и Ритуалы в Habitify: поведенческие эксперименты, Отметки, Тяга. Используй, чтобы завести привычку, отметить выполнение, срыв, пропуск или количество, пересмотреть план, поставить паузу, архивировать или удалить, вести Области и Ритуалы («ритуал выполнен»); для коучинга по еде и весу, порно и мастурбации, отказу от веществ; команды design, log, urge, review, adjust, rituals. Задачи ведёт jedikit-tasks, календарь — jedikit-calendar."
---

# JediKit Habits

Помогай проверять выбранное поведение экспериментом: одна гипотеза, План эксперимента в заметке привычки, Отметки, Обзор эксперимента. Состояние живёт в Habitify, решает пользователь. Пиши по-русски, identifiers не переводи.

## Вход в сценарий

1. Определи сценарий по таблице, читай только его references.
2. Еда, вес, потеря контроля, вещества, алкоголь, никотин, лекарства, сексуальное поведение или любой сигнал риска — сначала [safety.md](references/safety.md), затем тема: [food-behavior.md](references/food-behavior.md), [sexual-behavior.md](references/sexual-behavior.md), [cessation.md](references/cessation.md). Safety-стоп важнее любой команды.
3. Перед Habitify, `memory` или `cronjob_manage` прочитай [write-policy.md](references/write-policy.md) и [tools.md](references/tools.md).
4. Файлы скилла загружай `skill_view(name="<имя этого скилла>", file_path="references/<файл>.md")`, контракт — `file_path="tools.json"`; Markdown-ссылка файл не загружает. Соседний скилл JediKit — `skill_view(name=…)` с тем же префиксом, что у этого скилла: `agent-plugin-jedikit-805a716c:jedikit-habits` → `agent-plugin-jedikit-805a716c:jedikit-calendar`, голое `jedikit-habits` → `jedikit-calendar`.

| Запрос | Результат | Reference |
| --- | --- | --- |
| `setup` | Привычки, timezone, названия, окно обзоров, расписание | [setup.md](references/setup.md) |
| `status`, «какие привычки сегодня?» | Чтение эксперимента или дня | [setup.md](references/setup.md#status) |
| `design`, «хочу проверить…»; `adjust` | Одна гипотеза, привычка, План эксперимента; в плане изменена одна вещь | [experiments.md](references/experiments.md), [coaching.md](references/coaching.md) |
| `log`, «отметь…», отмена Отметки | Отметка за точную дату; отмена с подтверждением потерь | [tracking.md](references/tracking.md) |
| `urge`, «тянет…» | 1–3 действия из плана, без записи | [tracking.md](references/tracking.md#тяга) |
| `review` | Оставить, изменить одну вещь, пауза или завершить | [review.md](references/review.md), [coaching.md](references/coaching.md) |
| `pause`, Off Mode, `archive`, удаление | Пауза и Off Mode — инструкция для приложения, команды `off` нет; архив с историей; удаление по явной просьбе | [review.md](references/review.md#pause); Область — [areas.md](references/areas.md#удалить-область) |
| `areas`, группировка | Области и назначения | [areas.md](references/areas.md) |
| `rituals`, «ритуал выполнен», статус, обзор, старт ритуала | Состав, старт, массовая Отметка | [rituals.md](references/rituals.md) |
| Доказательства, сроки формирования, серия | Границы уверенности | [evidence.md](references/evidence.md) |
| `help` | Команды без обращения к аккаунту | — |

## Уточнение и согласие

- Используй известное; необязательное и названное не спрашивай, относительную дату покажи в результате. Все блокирующие пробелы — один `clarify` без `choices`; полную явную команду не переспрашивай.
- Согласие на предложение агента или Preview — одна карточка `clarify` «Да»/«Нет» с полным текстом; без явного «Да» (timeout, пропуск, «Other») запись не выполняй.
- Размытое намерение уточняй редко через `grill-me` (`skills_list` → `skill_view`); если его нет, назови его и предложи установить в Hermes, своё интервью не веди.
- Запрос другого скилла или провайдера — одной строкой предложи ход и выполни после «Да». Перед записью в чужого провайдера загрузи его скилл и `references/write-policy.md`; без фактической загрузки передачу не объявляй.

## Границы

- Агент — коуч и оператор, не врач и не психотерапевт: без диагнозов, лечения, диет и схем снижения дозы.
- Один эксперимент за раз; пакет привычек не собирай.
- Habitify — только серверы `habitify_read` и `habitify` по tools.md.
- Безвозвратные удаления привычки, Области и Отметок — только по явной просьбе и после карточки «Нет»/«Да» с потерями.
- Фоновый запуск только читает. Настройки — только `memory` по [setup.md](references/setup.md#где-хранить-настройки); файлы скиллов JediKit не меняй, `skill_manage` не вызывай.
- Задачи — `jedikit-tasks`; календарь и блок Распорядка ритуала — `jedikit-calendar` ([rituals.md](references/rituals.md#сдвиг-старта-с-блоком-распорядка)).
