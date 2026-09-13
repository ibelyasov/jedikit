# Покрытие прежнего корпуса задач

**Проверено:** 2026-09-13 (Europe/Moscow)

Это публичная карта переноса двух прежних task-документов. Она помогает проверить полноту, но не заменяет provenance в [`author-method.md`](author-method.md) и [`community-practices.md`](community-practices.md). Общая история перестройки библиотеки находится в [`../coverage.md`](../coverage.md).

## `jedi-method-primary.md`

| Прежний раздел | Новое место | Решение |
|---|---|---|
| Статус источников и границы | author §§1, 11; [`README.md`](README.md) | сохранён; добавлены условия доступности и запрет реконструировать закрытые главы |
| Product overlay v1 | [`../product-decisions.md`](../product-decisions.md); ссылки из author §§1, 5–10 | исключён как дублирующая спецификация; каждое O указывает на canonical decision |
| Ограничение и полный рабочий цикл | author §2 | сохранены с границей «модель, не причинное доказательство» |
| Практики 1–18 | author §3, P01–P18 | каждая сохранена с источником, правилом, продуктовым выводом и ограничением |
| Приоритеты для Agent Skill | author §§4, 11 | сохранено как исследовательское ядро; readiness skill не утверждается |
| Что нельзя подтвердить | author §§4, 11 | сохранено и уточнено после повторной проверки |
| Минимальный контракт состояния | product decisions §§5–9; author §5 | исключён из research как нормативная schema; происхождение A/O сохранено |
| DT-1…DT-9 | author §5 | все девять сохранены как product interpretation, не алгоритм книги |
| OP-1…OP-18 | author §6 | все восемнадцать сопоставлены с практикой и O |
| 12 пар формулировок | author §7 | сохранены как редакторские примеры O, без ложной атрибуции |
| Entity/date tables | author §8 | сохранены; `start/deadline` помечены O |
| Daily/weekly/debt/closure | author §§3–5 | сохранены; ложная универсализация чисел удалена |
| Overload/refusal | author §§3, 5, 9 | авторская база отделена от permission model JediKit |
| Edge cases/anti-patterns | author §9 | сохранены в проверяемой таблице и перечне |
| MUST 10 / SHOULD 8 / MAY 6 | author §10 | все 24 ID сохранены; каждому присвоена A/O/узкая граница |
| Unknowns и итог | author §11 | сохранены; добавлены запреты causal/schema inference |

## `jedi-community-practices.md`

| Прежний раздел | Новое место | Решение |
|---|---|---|
| Evidence taxonomy | community §1; [`README.md`](README.md) | сохранена; авторское личное, community opinion и secondary разведены |
| S01–S36 | community §§2–6 | все 36 ID присутствуют; у каждого есть ситуация, источник, интерпретация/результат и ограничение |
| 16 bad→good examples | community §7 | все 16 учтены; прямые примеры отделены от O; ложные числа исправлены |
| Inbox triage | community §8.1 | сохранено с раздельными контекстами 30 секунд и 2 минуты |
| Decomposition/wording | community §8.2 | сохранено; 30 минут и waiting не объявлены defaults |
| Today overload | community §8.3 | сохранено без универсальных порогов `>20`, `3+` и cap 3–5 |
| Weekly review | community §8.4 | сохранено; interruption следует product §9, old inbox 15→10→5 — только TPL recovery |
| Recurring/no-clone | community §8.5 | сохранено как optional/alternative, не v1 default |
| External-system bridge | community §8.6 | сохранено с source-of-truth и confidentiality boundary |
| Recovery playbooks | community §9 | десять failure modes сохранены как O, не evidence |
| Candidates/instructions | community §10 | полезные кандидаты сохранены; финальное поведение оставлено product decisions |
| Optional defaults | community §10 | сохранены как исключённые или требующие отдельного решения; неподтверждённые числа не восстановлены |
| Do-not-default | community §10 | сохранено и усилено после source refresh |

## Материальные исправления

1. TPL §§3.8–3.9 поддерживает recovery старого inbox: 15 минут минимум два дня в неделю; при пропусках — 10 или даже 5 минут. Это не universal inbox, triage или weekly timebox.
2. B2 §6.2.2 описывает обратную прокрутку дня примерно на минуту. Десятиминутный вариант относится к редакционной статье SingularityApp.
3. Статья `singularity-app.ru/blog/dzhedajskie-tehniki/` подписана «Тайным Космонавтом» и считается secondary editorial.
4. Форумный URL S11 сейчас ведёт в Telegram; точный прежний сценарий не считается перепроверенным и не поддерживает continuation policy.
5. `30 секунд` R26 и вопрос о `2 минутах` CQ относятся к разным контекстам.
6. Личные workflow автора, функции SingularityApp, self-reports и корреляция не превращены в универсальные нормы или causal promises.

## Осознанно исключено

- Универсальные `today_soft_cap=5`, 1–2 deep-work, weekly 15/30/40 минут, пороги `>20`/`3+ переносов`, полный waiting workflow и обязательный no-clone.
- Точная state/API schema, permissions, scheduling и provider adapters: это продуктовый/runtime слой.
- Недоступный полный текст книг, реконструкция закрытых глав и длинные цитаты.
- Автокопирование Jira/CRM/чатов/календаря, публикация и внешние write-actions.
