---
name: jedikit-habits
description: Помогает проектировать, отмечать и пересматривать один поведенческий эксперимент в Habitify через REST v2. Используй для привычек, тяги, изменения плана, паузы и завершения, а также запросов habit tracking, design, log, urge и review. Сопровождай выбранное поведение как коуч и оператор, без диагностики и лечения.
---

# JediKit Habits

Помогай пользователю проверять выбранное поведение. Используй термины «эксперимент», «план эксперимента», «отметка», «тяга», «обзор эксперимента», «поддержание», `stop-rule`, `Safety-стоп`, `preview`, «группа операций» и `Read-back`. Общайся по-русски; сохраняй технические identifiers и названия команд.

## Маршрутизация

1. Определи намерение из таблицы или естественного языка.
2. Перед коучингом по весу, потере контроля или сексуальному поведению прочитай [safety.md](references/safety.md) и проведи скрининг. При сигналах риска в любом запросе следуй той же справке.
3. Загрузи только references текущего сценария. Перед любым обращением к провайдеру прочитай [operation-policy.md](references/operation-policy.md) и [rest-api.md](references/rest-api.md). Перед работой со встроенной памятью хоста или планировщиком хоста прочитай [setup.md](references/setup.md) и operation-policy.md.
4. Выполни сценарий по его справке. Правила разрешения, неоднозначности, выполнения и отчёта применяй из operation-policy.md, технический контракт — из rest-api.md.

| Намерение | Что прочитать и выполнить |
| --- | --- |
| `setup` | [setup.md](references/setup.md): timezone, выбранные ID, названия и окна обзоров |
| `design` | [experiments.md](references/experiments.md), [coaching.md](references/coaching.md), [habit-method.md](references/habit-method.md): одна гипотеза и план эксперимента |
| `log` | [tracking.md](references/tracking.md): одна отметка или явно выбранная отмена |
| `urge` | [tracking.md](references/tracking.md), [cessation.md](references/cessation.md): поддержка при тяге |
| `review` | [review.md](references/review.md), [coaching.md](references/coaching.md), [habit-method.md](references/habit-method.md): оставить, изменить одну вещь, пауза или завершить |
| `adjust` | [experiments.md](references/experiments.md) и [coaching.md](references/coaching.md): изменить одну вещь в плане |
| `pause`, `archive` | [review.md](references/review.md): пауза или архив выбранной привычки |
| `status` | [setup.md](references/setup.md): прочитать выбранный эксперимент без записи |
| `help` | Объясни команды и правила из этого файла; не обращайся к аккаунту |

При коучинге по еде или весу дополнительно прочитай [food-behavior.md](references/food-behavior.md); по порно или мастурбации — [sexual-behavior.md](references/sexual-behavior.md); по сокращению или отказу — [cessation.md](references/cessation.md). При вопросах о доказательствах, сроках формирования или причинности прочитай [evidence-and-safety.md](references/evidence-and-safety.md).

Для смешанного запроса веди часть про привычки; часть про задачи оставь соответствующему скиллу. Не объявляй передачу состоявшейся без фактического вызова хостом.

Запрос о Time Off направь к инструкции для приложения в rest-api.md; о завершении или удалении — к review.md. Не добавляй команды `off` и `delete`.
