---
name: jedikit-habits
description: Используй для экспериментов в Habitify, отметок поведения, поддержки при тяге, обзора или изменения плана, паузы, архива, удаления, областей и ритуалов; также для habit tracking, design, log, urge, review, setup, status, areas и rituals.
---

# JediKit Habits

Помогай проверять выбранное поведение через эксперимент и план эксперимента, отметки, поддержку при тяге и обзор. Общайся по-русски; сохраняй identifiers и названия команд.

Используй известные данные; все блокирующие пробелы собери одним сообщением, по пункту на пробел. Не спрашивай известное и необязательное; относительную дату покажи в результате.
Глубокое уточнение намерения проводи редко через внешний `grill-me`; если он недоступен, назови его и рекомендуй установить средствами хоста, без собственного интервью.
Если запрос относится к другому месту, одной строкой предложи правильный ход и выполни по «да» по правилам скилла-владельца.

## Маршрутизация

1. Определи намерение из таблицы или естественного языка.
2. Для еды, веса, потери контроля, веществ, алкоголя, никотина, лекарств и сексуального поведения прочитай [safety.md](references/safety.md): там определены краткий скрининг и Safety-стоп. При сигналах риска в любом запросе следуй той же справке. Перед созданием или изменением применяй также границы записи из operation-policy.md.
3. Загрузи только references текущего сценария. Перед любым обращением к провайдеру прочитай [operation-policy.md](references/operation-policy.md) и [habitify-tools.md](references/habitify-tools.md). Перед работой со встроенной памятью хоста или планировщиком хоста прочитай [setup.md](references/setup.md) и operation-policy.md.
4. Выполни сценарий по его справке; разрешения и отчёт — по operation-policy.md, вызовы — по habitify-tools.md.

| Намерение | Что прочитать и выполнить |
| --- | --- |
| `setup` | [setup.md](references/setup.md): существующие привычки, timezone, названия и окна обзоров |
| `design` | [experiments.md](references/experiments.md), [coaching.md](references/coaching.md), [habit-method.md](references/habit-method.md): одна гипотеза и план эксперимента |
| `log` | [tracking.md](references/tracking.md): одна отметка или явно выбранная отмена |
| `urge` | [tracking.md](references/tracking.md), [cessation.md](references/cessation.md): поддержка при тяге |
| `review` | [review.md](references/review.md), [coaching.md](references/coaching.md), [habit-method.md](references/habit-method.md): оставить, изменить одну вещь, пауза или завершить |
| `adjust` | [experiments.md](references/experiments.md) и [coaching.md](references/coaching.md): изменить одну вещь в плане |
| `pause`, `archive` | [review.md](references/review.md): пауза или архив выбранной привычки |
| Явное удаление | [operation-policy.md](references/operation-policy.md): одна строка подтверждения для привычки, области, удаления/`undo` отметок; заметку по полной команде удали сразу |
| `areas`, наблюдаемая потребность в группировке при setup/status/review | [areas.md](references/areas.md): существующая область прежде новой, одно небольшое предложение, назначения и Read-back |
| `rituals`, собрать или изменить ритуал, «ритуал выполнен», статус или обзор ритуала | [rituals.md](references/rituals.md): Область, состав, старт, отметки; сдвиг блока Распорядка — через `jedikit-calendar` |
| `status` | [setup.md](references/setup.md): выбранный эксперимент или запрошенный обзор привычек за день |
| `help` | Объясни команды и правила из этого файла; не обращайся к аккаунту |

При коучинге по еде или весу дополнительно прочитай [food-behavior.md](references/food-behavior.md); по порно или мастурбации — [sexual-behavior.md](references/sexual-behavior.md); по сокращению или отказу — [cessation.md](references/cessation.md). При вопросах о доказательствах, сроках формирования или причинности прочитай [evidence-and-safety.md](references/evidence-and-safety.md).

Для операций Habitify используй инструменты хоста по habitify-tools.md. Для смешанного запроса веди часть про привычки; задачи передавай `jedikit-tasks`, сдвиг блока Распорядка ритуала — `jedikit-calendar`. Перед чужой записью загрузи скилл-владелец и его правила записи по имени, не пересказывай их. Явную команду на два провайдера выполняй последовательно, стоп на первой ошибке; набор агента — после одного общего Preview. Не объявляй передачу состоявшейся без фактической загрузки скилла хостом.

Запрос о Time Off направь к инструкции для приложения в habitify-tools.md; о завершении — к review.md. Команды `off` нет.
