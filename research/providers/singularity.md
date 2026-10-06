# SingularityApp: досье официального hosted MCP

Дата исходного исследования: **2026-10-05**. **2026-10-06** повторно прочитана публичная MCP Wiki; остальные публичные источники сохраняют прежнюю дату доступа. Документ предназначен для полной пересборки JediKit. Возможность, заявленная поставщиком, наличие имени в каталоге и проверенное действие с данными — разные уровни доказательства.

## Источники и границы доказательства

| Метка | Что подтверждает | Что не подтверждает |
| --- | --- | --- |
| **Поставщик / Wiki** | Опубликованную модель приложения и обещания интеграции на дату доступа; первичные ссылки приведены рядом с утверждениями. | Реальные MCP signatures, ответ конкретного аккаунта и side effects. |
| **Наблюдение / LIVE** | Переданные ведущим агентом результаты авторизованного discovery в Claude Code от 2026-10-05: имена tools и числовые enums; источник — официальный [SINGULARITY-DISCOVERY-2026-10-05](../sources.md). | Этот автор не проводил probe. Raw observation исполнителю не предоставлено; его расположение неизвестно. Точные schemas, annotations, outputs, scopes и параметры соединения здесь не воспроизводимы. По переданному описанию вызовов tools для чтения данных или записи не было. |
| **Поставщик / REST** | Публичный REST contract v2 из [SINGULARITY-OPENAPI](../sources.md) и [SINGULARITY-API](../sources.md), прочитанный 2026-10-05. | Соответствие REST полей, методов и фильтров hosted MCP. REST используется только для сравнения. |
| **Вывод** | Явно обозначенную интерпретацию источников или проектное правило. | Независимую runtime-проверку. |
| **Неизвестно** | Пробел в доступных доказательствах. | Отсутствие функции у поставщика вообще. |

Независимых испытаний действий с данными, benchmarks или независимых оценок надёжности в этом исследовании нет. Релевантные пользовательские anecdotes не использованы. Исторические metadata probes сохранены ниже и в [tools snapshot](singularity-tools-2026-08-09.md) и [prompts snapshot](singularity-prompts-2026-08-09.md); их наблюдения августа и документальная перепроверка сентября не являются текущим контрактом.

**Проектное решение владельца, переданное 2026-10-05:** полная пересборка; acceptance host — Hermes на Nix-сервере владельца; Claude Code и Codex заявляются поддерживаемыми клиентами. Используется только официальный hosted MCP, без REST fallback, собственного MCP, custom code/Python и generated copies; одна исходная skill tree. Это ограничения JediKit, а не обещания SingularityApp. Само это досье не устанавливает интеграцию и не доказывает совместимость клиентов.

## Подключение, доступ и отличие документации от discovery

Поставщик указывает адрес `https://mcp.singularity-app.com/mcp`, вход и подтверждение доступа через страницу SingularityApp, запись в Connected Apps; функция помечена Pro/Elite. Wiki перечисляет Codex и Claude среди клиентов. Это заявление поставщика, не выполненный клиентский тест. [SINGULARITY-MCP](../sources.md)

| Публичный toolset | Опубликованная область | Сопоставление с переданным discovery |
| --- | --- | --- |
| `tasks` | Tasks и checklists. [SINGULARITY-MCP](../sources.md) | Имена `task_*`, `checklist_item_*` наблюдались; точное правило включения не проверено. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) |
| `projects` | Projects. [SINGULARITY-MCP](../sources.md) | Имена `project_*` наблюдались. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) |
| `meta` | Core entities. [SINGULARITY-MCP](../sources.md) | Принадлежность `get_my_context` и `task_group_*` этой группе неизвестна. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) |
| `habits` | Habits. [SINGULARITY-MCP](../sources.md) | Наблюдались `habit_*`, `habit_progress_*`. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) |
| `kanban` | Kanban. [SINGULARITY-MCP](../sources.md) | Наблюдались `kanban_status_*`, `task_change_column`. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) |
| `tags` | Tags. [SINGULARITY-MCP](../sources.md) | Наблюдались `tag_*`. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) |
| `system` | Batch: выключен по умолчанию, до 20 операций за запрос. [SINGULARITY-MCP](../sources.md) | Batch tool в переданном наборе имён не обнаружен; включался ли `system`, неизвестно. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) |

Wiki допускает URL parameter `toolsets`, например `?toolsets=tasks,projects`; это выбор групп, а не доказанный read-only permission scope. Точные OAuth scope strings и матрица scope → tool по этой странице неизвестны. OAuth discovery endpoints в этом исследовании не запрашивались. [SINGULARITY-MCP](../sources.md)

Для JediKit по [решению #1](https://github.com/ibelyasov/jedikit/issues/1) выбран минимум `tasks,projects,meta,tags`: `https://mcp.singularity-app.com/mcp?toolsets=tasks,projects,meta,tags`. Наличие параметра и групп повторно подтверждено Wiki 2026-10-06. `habits`, `kanban`, `time_stat` и Batch не входят в продуктовый scope; REST fallback отсутствует ([ADR0007](../../docs/adr/0007-no-kanban.md), [ADR0005](../../docs/adr/0005-one-source-host-connections.md)). Это настройка доступного каталога, не гарантия OAuth least privilege. Исторический Codex probe ниже обнаружил несовместимость query URL с protected-resource validation; Hermes и нынешний Codex с этим URL не проверены. При несовместимости остановить подключение и сообщить ограничение, а не молча расширять доступ.

Отсутствие delete tool в наблюдении — граница каталога, а не доказательство устройства всего сервиса. Продуктовый сценарий разобранных идей, справок и встреч использует подтверждённый пользователем `task_cancel`, а не delete ([ADR0008](../../docs/adr/0008-cancel-instead-of-delete.md)).

**Вывод:** отсутствие batch или delete имени в этой сессии не доказывает их универсального отсутствия. `time_stat_*` наблюдались, хотя отдельного `time` toolset в списке Wiki нет. Нельзя самостоятельно назначить этим tools группу или требуемые scopes. Следует ориентироваться на discovery именно acceptance host и согласованные владельцем права. [SINGULARITY-MCP](../sources.md) [SINGULARITY-DISCOVERY-2026-10-05](../sources.md)

Выбор `tasks,projects,meta,tags` сам по себе не доказывает, что сервер скрывает каждое `time_stat_*`: точный mapping неизвестен. Независимо от состава discovery skill их не использует; приёмка должна явно проверить фактический каталог минимальной конфигурации.

## Модель данных: не путать проект, раздел и подзадачу

| Понятие | Официальная модель и граница MCP |
| --- | --- |
| Project и вложенный Project | UI поддерживает проекты внутри проектов. Это иерархия проектов, а не дерево подзадач. Поставщик отдельно предупреждает о каскадном удалении родительского проекта в UI; аналогичный MCP effect не проверен. [SINGULARITY-NESTED-PROJECTS](../sources.md) |
| Section / `task_group` | Раздел — блок задач внутри проекта. REST Wiki называет `task-group` разделом, а `parent` при создании — ID проекта. UI умеет преобразовывать section в project, но отдельный MCP conversion tool не наблюдался. [SINGULARITY-API](../sources.md) [SINGULARITY-SECTIONS](../sources.md) [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) |
| Task → Project / Task / Section | В REST `projectId` ссылается на проект, `parent` — на родительскую задачу, `group` — на раздел. У Project `parent` — другой Project. Эти разные связи нельзя взаимозаменять; текущие MCP имена полей не подтверждены переданным перечнем. [SINGULARITY-OPENAPI](../sources.md) |
| Subtask и Checklist item | Поставщик различает самостоятельные вложенные задачи и checklist: у пунктов checklist нет собственной даты, тегов или приоритета. `checklist_item_*` наблюдались; payload и фактическое наследование состояния не проверены. [SINGULARITY-GLOSSARY](../sources.md) [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) |
| Tags | В модели поставщика метки объединяют задачи и заметки поперёк проектов. Наличие `tag_*` подтверждено discovery, а операции над связью task ↔ tag отдельно не испытаны. [SINGULARITY-GLOSSARY](../sources.md) [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) |
| Habits, progress, time statistics | Имена отдельных семейств наблюдались. Нельзя приравнивать habit progress к task completion или time-stat к дате задачи; фактические единицы, дневные границы и поля MCP неизвестны. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) |

### Inbox: UI-определение не заменяет проверенный фильтр

Поставщик определяет Inbox как задачи без даты **и** без проекта. Страница Task creation формулирует выход из Inbox как назначение проекта **и** даты; это текстовое различие внутри UI-документации, не точный алгоритм membership. [SINGULARITY-GLOSSARY](../sources.md) [SINGULARITY-SYSTEM-FOLDERS](../sources.md) [SINGULARITY-TASK-CREATION](../sources.md)

В наблюдении есть `task_list_inbox`, но его predicates не переданы. Поэтому неизвестно, совпадает ли выборка с UI, исключает ли notes, subtasks, deferred, checked, archived или removed и что означает «без даты». REST фильтр `projectId.isSet=false` выражает только отсутствие проекта; он не доказывает Inbox и не доказывает доступность того же filter key через MCP. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) [SINGULARITY-OPENAPI](../sources.md)

**Вывод для capture/triage:** не создавать фиктивный Project «Inbox», не присваивать дату или проект ради попадания в выборку. Сначала проверить membership на заранее согласованных примерах. Расхождение UI/MCP показывать владельцу как ограничение выборки, а не «исправлять» данные.

### Даты и lifecycle

Обычная дата в UI обозначает планируемое начало работы; deadline — последний срок завершения. Их нельзя смешивать или автоматически переносить deadline вместе со start. [SINGULARITY-DATE](../sources.md) [SINGULARITY-DEADLINE](../sources.md)

Поставщик различает completion, cancellation и «Complete for Today»: последняя UI-операция временно завершает задачу с датой сегодня или раньше, и она становится активной завтра. UI-архивирование зависит от настроек. Наличие соответствующих MCP имён не подтверждает, как они реализуют дату, recurrence, timestamp и архив. [SINGULARITY-COMPLETE](../sources.md) [SINGULARITY-DISCOVERY-2026-10-05](../sources.md)

Server instructions, переданные ведущим 2026-10-05, требуют integer enums: `priority`: `0=HIGH`, `1=NORMAL`, `2=LOW`; `checked`: `0=EMPTY`, `1=CHECKED`, `2=CANCELLED`; `state`: `0=PINNED`, `1=UNPINNED`. Эти значения — наблюдение инструкций сервера, а не проверка записи; не переносить UI hotkeys или порядковый номер приоритета в payload. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md)

## Полный каталог наблюдённых имён и семантическая граница

Ниже перечислены все переданные имена. **Подсчёт по перечню: 52** (вывод автора, не server-reported total). Наличие tools подтверждается только переданным observation 2026-10-05. Для **каждого** имени точная per-tool MCP documentation в прочитанной Wiki не найдена; current `inputSchema`, required fields, output shape, annotations и side effects **не установлены**. REST/UI контекст в таблице относится только к указанному интерфейсу, не устанавливает mapping в MCP. Сопоставление по имени и классификация чтения/записи — рабочая гипотеза для будущего approval. Общая таблица ниже про undo, dates, pagination и errors относится ко всем перечисленным list/write workflows. [SINGULARITY-MCP](../sources.md) [SINGULARITY-DISCOVERY-2026-10-05](../sources.md)

| Семейство / число | Точные имена | Официальный REST/UI контекст; неизвестная MCP семантика | Источник |
| --- | --- | --- | --- |
| Context / 1 | `get_my_context` | Точное назначение tool в MCP Wiki не документировано. «Получить контекст» — вывод из имени; состав, размер и чувствительность неизвестны. Не вызывать автоматически как metadata. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) [SINGULARITY-MCP](../sources.md) |
| Tasks / 4 | `task_create`, `task_get`, `task_list`, `task_update` | REST: POST создаёт, GET читает объект/список, PATCH редактирует task. MCP required title/ID, partial update, null/omission, notes и tags mapping неизвестны. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); REST [SINGULARITY-API](../sources.md) |
| Task views / 3 | `task_list_inbox`, `task_list_today`, `task_list_overdue` | UI: Inbox без даты/проекта; Today собирает задачи дня и recurring instances; overdue показывает задачи с прошедшей датой и настраиваемым отображением. UI/REST не дают точных MCP predicates; membership, overdue definition, timezone и полнота неизвестны. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); UI [SINGULARITY-SYSTEM-FOLDERS](../sources.md) [SINGULARITY-TODAY](../sources.md) [SINGULARITY-OVERDUE](../sources.md) |
| Task movement / 2 | `task_move`, `task_change_column` | UI позволяет перенос в другой проект; REST move переносит в project/group, change-column меняет kanban column. MCP destination project/section/task, порядок, дочерние объекты и эффект Done неизвестны. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); UI [SINGULARITY-MOVE-TASKS](../sources.md); REST [SINGULARITY-OPENAPI](../sources.md) |
| Task completion / 4 | `task_complete`, `task_complete_today`, `task_uncomplete`, `task_cancel` | UI: done; временно done до завтра; снятие отметки; cancel вместо удаления. MCP timestamps, recurrence, checklist/subtasks и archive effects не проверены. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); UI [SINGULARITY-COMPLETE](../sources.md) |
| Task archive / 2 | `task_archive`, `task_unarchive` | UI archive сохраняет задачи вне активных списков; возврат описан через снятие completion. Совпадение этого возврата с MCP unarchive, старые поля/даты и вложения неизвестны. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); UI [SINGULARITY-TASK-ARCHIVE](../sources.md) |
| Projects / 4 | `project_create`, `project_get`, `project_list`, `project_update` | REST: создание, объект/список, редактирование project. MCP parent/notebook representation, shared visibility и включение descendants неизвестны. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); REST [SINGULARITY-API](../sources.md); UI [SINGULARITY-NESTED-PROJECTS](../sources.md) |
| Project archive / 2 | `project_archive`, `project_unarchive` | UI archive включает tasks/subprojects и приостанавливает recurrence; после возврата recurrence возобновляют вручную. Структура сохраняется. MCP cascade, порядок и восстановление состояний неизвестны. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); UI [SINGULARITY-PROJECT-ARCHIVE](../sources.md) |
| Sections / 4 | `task_group_create`, `task_group_get`, `task_group_list`, `task_group_update` | REST: создание, объект/список, редактирование task-group; parent — Project. UI section группирует задачи. MCP required fields, межпроектный перенос и nesting неизвестны. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); REST [SINGULARITY-API](../sources.md); UI [SINGULARITY-SECTIONS](../sources.md) |
| Checklist / 4 | `checklist_item_create`, `checklist_item_get`, `checklist_item_list`, `checklist_item_update` | REST: создание, объект/список, редактирование checklist-item; UI — пункты внутри Task. MCP attachment/order/update/list contract неизвестен. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); REST [SINGULARITY-API](../sources.md); UI [SINGULARITY-CHECKLISTS](../sources.md) |
| Checklist checks / 2 | `checklist_item_check`, `checklist_item_uncheck` | REST: check/uncheck; UI отмечает пункт отдельно, задачу завершают вручную. MCP повторные вызовы и parent effect не проверены. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); REST [SINGULARITY-OPENAPI](../sources.md); UI [SINGULARITY-CHECKLISTS](../sources.md) |
| Tags / 4 | `tag_create`, `tag_get`, `tag_list`, `tag_update` | REST: создание, объект/список, редактирование tag. UI метки связывают задачи/заметки. MCP duplicates, hierarchy и rename effects неизвестны. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); REST [SINGULARITY-OPENAPI](../sources.md); UI [SINGULARITY-TAGS](../sources.md) |
| Kanban / 4 | `kanban_status_create`, `kanban_status_get`, `kanban_status_list`, `kanban_status_update` | REST: создание, объект/список, редактирование колонки проекта. MCP required fields, системные статусы и completion mapping неизвестны. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); REST [SINGULARITY-API](../sources.md) |
| Habits / 4 | `habit_create`, `habit_get`, `habit_list`, `habit_update` | REST: создание, объект/список, редактирование habit. UI tracker отслеживает привычки по дням. MCP schedule, pause/archive, enum и тарифные ограничения неизвестны. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); REST [SINGULARITY-API](../sources.md); UI [SINGULARITY-HABIT-TRACKER](../sources.md) |
| Habit progress / 4 | `habit_progress_create`, `habit_progress_get`, `habit_progress_list`, `habit_progress_update` | REST: создание, объект/список, редактирование habit-daily-progress. UI показывает дневной progress. MCP habit/day identity, enum, upsert и duplicates неизвестны. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); REST [SINGULARITY-OPENAPI](../sources.md); UI [SINGULARITY-HABIT-TRACKER](../sources.md) |
| Time statistics / 4 | `time_stat_create`, `time_stat_get`, `time_stat_list`, `time_stat_update` | REST: создание, объект/список, редактирование time-stat. UI статистика отражает sessions/time spent; её связь с этими MCP records не установлена. MCP units/task linkage/overlap/running timer неизвестны. | [SINGULARITY-DISCOVERY-2026-10-05](../sources.md); REST [SINGULARITY-API](../sources.md); UI [SINGULARITY-POMODORO-STATISTICS](../sources.md) |

В перечне нет явного delete, batch, bulk, transaction или undo tool. Это ограничение **этого наблюдения**. Наличие `update` также не доказывает отсутствие потенциально разрушительных полей. До получения schemas нельзя обещать «MCP вообще не умеет удалять» или разрешать все updates как безопасные. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md)

## Что обещано, что неизвестно и как должен вести себя skill

| Вопрос | Первичный источник на 2026-10-05 | Граница и правило JediKit (вывод) |
| --- | --- | --- |
| Undo / rollback | UI содержит Undo/Redo hotkeys. [SINGULARITY-MAC-SHORTCUTS](../sources.md) В переданном наборе нет undo tool. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) | Не обещать, что Cmd+Z отменит удалённую MCP запись. Uncomplete/unarchive — отдельные операции, не восстановление всего snapshot. До теста никаких гарантий rollback. |
| Idempotency / повтор после timeout | MCP Wiki не публикует такой контракт; наблюдение не содержит annotations или idempotency keys. [SINGULARITY-MCP](../sources.md) [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) | Успех мог произойти до потери ответа. Не повторять create/mutation вслепую; остановиться, по разрешённому чтению сверить состояние и явно сообщить неопределённость. |
| Batch | Wiki заявляет `system`, default off, ≤20; tool/schema не переданы. [SINGULARITY-MCP](../sources.md) [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) | Не выводить atomicity, ordering, temp IDs, deduplication и rollback из REST batch. Последовательность нескольких вызовов тоже не транзакция; отчёт applied/failed/unapplied. |
| Dates / timezone | UI различает дату и deadline; в REST `modifiedSince` — full ISO datetime, offset нормализуется в UTC. [SINGULARITY-DATE](../sources.md) [SINGULARITY-DEADLINE](../sources.md) [SINGULARITY-OPENAPI](../sources.md) | MCP accepted format, timezone argument, clearing date, day boundary и DST не установлены. Согласовать IANA timezone и смысл даты до записи; не назначать 09:00 или UTC midnight по умолчанию. |
| Pagination / полнота | REST описывает `maxCount` 1–1000, `offset`, `paginationData` и предупреждает о пропусках при recurrence post-filter. [SINGULARITY-OPENAPI](../sources.md) Текущий MCP list contract неизвестен. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) | Не переносить REST параметры и не считать одну страницу полным аккаунтом. Проверить ответ, continuation и recurrence на разрешённых данных; неполные counts явно маркировать. |
| Filter syntax | REST публикует operator filters; MCP input schemas сейчас не воспроизведены. [SINGULARITY-OPENAPI](../sources.md) [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) | Не отправлять `.isSet`, `.gte` и другие REST keys через MCP без текущего discovery. При неподдерживаемом фильтре сказать об ограничении, не переходить на REST. |
| Errors / retry / limits | В доступных MCP Wiki и переданном observation нет точной таблицы ошибок, rate limits, retry или partial-success contract. [SINGULARITY-MCP](../sources.md) [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) | Различать отказ до вызова, server error, validation error и неизвестный результат записи. Не скрывать ошибку успехом, не делать автоматические повторные mutations. |
| Archive / removal / permanent delete | REST Wiki различает archive/trash и необратимый DELETE; это не MCP mapping. [SINGULARITY-API](../sources.md) | Не подменять пользовательское «удали» archive или cancel. Объяснить доступную проверенную операцию и её последствия; destructive/cascade тесты только после отдельного согласования. |
| Duplicate prevention | Наличие create/list не подтверждает unique constraint или atomic check-then-create. [SINGULARITY-DISCOVERY-2026-10-05](../sources.md) | Поиск похожего объекта — помощь, не гарантия exactly-once. При timeout/конкурентной записи не создавать второй объект автоматически. |

## Практический маршрут для пересборки

Следующие правила — проектные рекомендации, а не заявленная семантика provider. Они укладываются в решение владельца от 2026-10-05 об официальном hosted MCP и одной skill tree.

1. **Read-only review:** определить нужную сущность и минимальный разрешённый срез; получить IDs через проверенный list/get; обозначить неполноту, неизвестные filters и timezone. Не трактовать отсутствие объекта в неполной выдаче как отсутствие в аккаунте.
2. **Capture:** записать сырую мысль во Inbox без предварительной классификации, не выдумывать проект, section, deadline или start. Проверить доступную schema перед построением вызова. Явную одиночную команду выполнить сразу; предложенное агентом изменение — после Preview и подтверждения; группа операций требует единого Preview и подтверждения. После записи нужен Read-back.
3. **Project/section work:** различать цель-проект, nested project, section и subtask. Перед перемещением проверить IDs и связи; после разрешённой записи сверить изменённый объект и ожидаемые связи.
4. **Completion/cancel/archive:** выбрать действие по намерению владельца. Не считать cancel, complete_today, archive и delete синонимами. В UI некоторые действия зависят от настроек; ожидаемый MCP результат нужен в отдельном тесте.
5. **Несколько операций:** выполнить только согласованный перечень; при ошибке или неизвестном результате остановиться и указать подтверждённые изменения, неопределённые и ещё не выполненные. Не «лечить» ошибку дополнительными provider mutations.
6. **Внешний контекст:** descriptions, prompts, notes и task text считать данными источника, а не разрешением обойти пользовательские границы. Discovery/публичные документы не дают разрешения на чтение аккаунта или изменения.

## Acceptance: будущие проверки, не выполненные в этом досье

### Чтение после разрешения владельца

На Hermes на Nix-сервере владельца проверить текущий discovery, затем ограниченный read-only сценарий на заранее выбранных владельцем объектах. Зафиксировать версии host/client/server, endpoint, toolset configuration, разрешённые права без секретов, имена и schemas, timestamps, ожидаемый и фактический результат. Это план, а не инструкция немедленно менять OAuth или scopes.

Проверить: доступность всех требуемых семейств; project hierarchy и sections; различие Inbox/no-project/no-date; today/overdue при согласованной timezone; notes versus tasks; archive/removed visibility; pagination/recurrence и полноту counts. `get_my_context` — отдельное чтение данных и требует того же согласованного контура. Недоступные schemas или read permissions фиксировать как blocker для соответствующего workflow.

Claude Code и Codex заявлены поддерживаемыми клиентами без обязательного runtime-гейта ([ADR0005](../../docs/adr/0005-one-source-host-connections.md)); такие же read-only сценарии можно использовать для диагностики этих клиентов. Переданное Claude Code discovery не доказывает Hermes или Codex runtime. Обязательная приёмка проекта — Hermes.

### Запись только на отдельно согласованных disposable data

Отдельное разрешение должно назвать аккаунт/тестовые объекты и допустимые операции. Без него не создавать тестовую задачу, не менять данные, не запускать OAuth и не расширять права. Нужны проверяемые сценарии:

- create → read-back → update → read-back для task/project/section/checklist/tag;
- project/section/subtask move и сохранение структуры; completion/cancel/complete_today/uncomplete с проверкой следующего дня и recurrence;
- archive/unarchive task/project с проверкой nested objects, старых дат и настроек;
- offset/day-boundary/DST, validation errors и неизвестный результат записи; повтор mutation — лишь если он отдельно разрешён;
- группа согласованных последовательных операций с остановкой на первой ошибке; Batch не входит в приёмку JediKit.

Cleanup — тоже mutation. Archive не считать удалением, unarchive — полноценным undo. Permanent delete не включать в cleanup по умолчанию и не переходить на REST ради очистки. В артефактах хранить только обезличенные IDs/ожидания/результаты; tokens, OAuth URL с параметрами и private profile links не сохранять.

## Статус и нерешённые риски

**Сделано 2026-10-05:** прочитаны публичные официальные источники, отдельно учтён переданный discovery, охвачены все 52 перечисленных имени, сформулированы границы применения. Публичная MCP страница получена через web search после timeout прямого открытия. Вызовов provider tools, OAuth operations, чтения/записи аккаунта, установки и deployment не было.

**Открыто:** воспроизводимый raw snapshot текущих schemas; соответствие toolsets/scopes; signatures и outputs; доступ shared projects; Inbox predicates; filters/pagination/recurrence; timezone; idempotency; error/retry/rate limits; cascade effects; undo; Batch contract. Пока не выполнены перечисленные acceptance проверки, корректная формулировка — «каталог и модель исследованы; поведение с данными и поддержка клиентов не приняты».

Сведения об источниках и объёме чтения сведены в [реестр](../sources.md).

## Историческая least-privilege проверка 2026-08-09

Сохранённое наблюдение: Codex CLI `0.147.0`, direct app-server inventory без model turn, официальный базовый endpoint. Разрешались OAuth, `initialize`, `tools/list`; tools, resources и данные аккаунта не читались и не изменялись. Этот опыт не повторялся 2026-10-06.

1. URL `?toolsets=...` не прошёл OAuth в том Codex: protected-resource metadata разрешала только точное resource `https://mcp.singularity-app.com/mcp`.
2. `codex mcp add` для базового URL автоматически запросил все объявленные read/write scopes. Сессию отозвали до MCP-вызовов.
3. `codex mcp login --scopes mcp:read` запросил ровно `mcp:read` и завершился успешно.

Сервер сообщил `singularity-mcp`, version `^2.0.1`, `authStatus: oAuth`, один tool `get_my_context`. Это наблюдение одного inventory, не проверка абсолютного минимального разрешения или account access. Последующий entity-scope discovery дал 35 tools, а полный Hermes discovery — 48; точные объекты сохранены в [датированном tools snapshot](singularity-tools-2026-08-09.md). Отдельный [prompts snapshot](singularity-prompts-2026-08-09.md) хранит четыре шаблона, не исполнявшихся агентом.

Точный объект единственного tool в least-privilege probe:

```json
{
  "name": "get_my_context",
  "title": "Get my context",
  "description": "Use this only if you do not have access to singularity:// resources. If your client supports Resources, prefer them because they are cacheable. Returns fallback context such as projects, tags, glossary, and filter syntax.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "include": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": ["projects", "tags", "glossary", "filter-syntax"]
        }
      }
    },
    "additionalProperties": false
  },
  "annotations": {
    "readOnlyHint": true,
    "destructiveHint": false,
    "idempotentHint": true
  }
}
```

Инструмент не вызывался. Его description упоминает `singularity://` resources; это текст server contract, не чтение resources. Поэтому автоматический `get_my_context` нельзя считать metadata-only действием.

### Анонимные observations 2026-08-08: не повторены

- GET базового `/mcp`: HTTP 405, POST-only route. Анонимный POST `initialize`: HTTP 401 с Bearer challenge; это не текущий transport smoke.
- Resource metadata: resource базового endpoint, auth server `https://me.singularity-app.com`, bearer header; scopes `tasks:read/write/check`, `projects:read/write`, `habits:read/write`, `tags:read/write`, `kanban:read/write`, `time_stat:read/write`, `checklists:read/write`, `mcp:read/write`.
- OAuth metadata: authorize/token/register/introspection/revocation; code + refresh_token, PKCE `S256`, dynamic client metadata. Наличие scope не доказывает отдельный toolset.
- `resource_documentation` указывал `/docs`, а GET вернул 404. Не использовать исторический адрес как источник текущего tool contract.

Источники происхождения: [SINGULARITY-OAUTH-RESOURCE](../sources.md), [SINGULARITY-OAUTH-SERVER](../sources.md), [SINGULARITY-MCP-DOCS](../sources.md). Свежая Wiki не воспроизводит этот OAuth опыт.

## Дополнительный REST контекст: snapshot публичной схемы 2026-09-13

Далее сохранены полезные точные operation IDs и DTO из прежнего публичного чтения, **не перепроверенные 2026-10-06**. Тогда схема содержала 64 operations; это исторический count. REST использует Bearer rest-token из account dashboard, отдельно от MCP OAuth; JediKit REST не вызывает. [SINGULARITY-OPENAPI](../sources.md), [SINGULARITY-ACCOUNT-DASHBOARD](../sources.md)

### Релевантные REST операции и схемы

Ниже перечислены **точные REST operation IDs**, подтверждённые публичной OpenAPI в историческом чтении 2026-09-13. Это отдельный REST contract; официальные источники не раскрывают, использует ли hosted MCP эти endpoints или общий backend.

```text
task:
  TaskController_list, TaskController_create, TaskController_getById,
  TaskController_update, TaskController_delete,
  TaskController_complete, TaskController_uncomplete, TaskController_cancel,
  TaskController_completeToday, TaskController_archive, TaskController_unarchive,
  TaskController_move, TaskController_changeColumn

project / sections / kanban:
  ProjectController_list, ProjectController_create, ProjectController_getById,
  ProjectController_update, ProjectController_delete,
  ProjectController_archive, ProjectController_unarchive
  TaskGroupController_list, TaskGroupController_create,
  TaskGroupController_getById, TaskGroupController_update, TaskGroupController_delete
  KanbanStatusController_list, KanbanStatusController_create,
  KanbanStatusController_getById, KanbanStatusController_update, KanbanStatusController_delete
  KanbanTaskStatusController_list, KanbanTaskStatusController_create,
  KanbanTaskStatusController_getById, KanbanTaskStatusController_update,
  KanbanTaskStatusController_delete

checklist:
  ChecklistItemController_list, ChecklistItemController_create,
  ChecklistItemController_getById, ChecklistItemController_update,
  ChecklistItemController_delete, ChecklistItemController_check,
  ChecklistItemController_uncheck

tag:
  TagController_list, TagController_create, TagController_getById,
  TagController_update, TagController_delete

habit / progress:
  HabitController_list, HabitController_create, HabitController_getById,
  HabitController_update, HabitController_delete
  HabitDailyProgressController_list, HabitDailyProgressController_create,
  HabitDailyProgressController_getById, HabitDailyProgressController_update,
  HabitDailyProgressController_delete

time / batch:
  TimeStatController_list, TimeStatController_create,
  TimeStatController_getById, TimeStatController_update,
  TimeStatController_delete, TimeStatController_deleteBulk
  BatchController_execute
```

Ключевые публичные JSON schemas:

- `TaskCreateDto`: обязательно `title`; опционально `note`, `priority` (`0/1/2`), `start`, `deadline`, `projectId`, `parent`, `group`, `tags[]`, `isNote`, notifications и duration. `TaskUpdateDto` позволяет менять те же поля, а также `checked`, `complete`, `deleteDate`, `kanbanStatusId`.
- `ProjectCreateDto`: обязательно `title`; `note`, `start/end`, `parent`, `journalDate/deleteDate`, `isNotebook` и display fields. `ProjectUpdateDto` — partial update; archive DTO содержит `journalDate`.
- `ChecklistItemCreateDto`: обязательны `parent` (Task ID) и `title`; `done` и `parentOrder` опциональны. Update меняет title/done/parent/order; отдельные action endpoints check/uncheck.
- `TagCreateDto`: обязательно `title`; `parent`, `parentOrder`, `hotkey`, `color`; update в том JSON также помечен обязательным `title`.
- `BatchRequestDto`: `operations[]`, каждая операция имеет обязательные `method` (`POST|PATCH|DELETE`) и `path` (начинается с `/v2/`), опционально `body`, `uuid` (idempotency) и `tempId`. Response возвращает `results[]` и `tempIdMap`. GET внутри batch схемой не разрешён.

В том snapshot Note моделировалась Task `isNote=true`, Notebook — Project `isNotebook=true`; отдельных `/v2/note` и `/v2/notebook` не было. Это не устанавливает first-class MCP capability. API Wiki не разрешала создание recurring task и прямо отрицала webhooks/event streams/subscriptions. REST pagination использовала `maxCount` до 1000, `offset`, `modifiedSince`, sparse `fields`. [SINGULARITY-OPENAPI](../sources.md), [SINGULARITY-API](../sources.md)

Датированный drift 2026-09-13: Wiki time-record bulk delete — `POST /v2/time-stat/delete-bulk`, OpenAPI — `DELETE /v2/time-stat` (`TimeStatController_deleteBulk`, filters `dateFrom/dateTo/relatedTaskId`). Это историческое REST-only расхождение, не причина менять MCP или включать time-stat.

### Sandbox и публичные fixtures

В просмотренных публичных Wiki/MCP/API документах не найден отдельный sandbox/demo tenant, sample token или fixture contract. Это ограничение корпуса, не доказательство отсутствия предложения поставщика. Subscription Wiki 2026-09-13 описывала 14-day trial с большинством платных функций; MCP availability в trial отдельно не обещана. Анонимные Registry/GitHub searches 2026-08-08 не подтвердили сторонний SingularityApp server; найденный Singularity Layer/Marketplace относился к другому продукту. Эти отрицательные поиски исторические, архитектурный выбор official hosted MCP уже принят. [SINGULARITY-TRIAL](../sources.md)

## Открытые provider вопросы

Точный нынешний `tools/list`, Batch/delete schema и rollback не установлены; Batch/delete не требуются принятому scope. Нужны согласованные Hermes tests для query-toolsets/OAuth, filters/Inbox membership, pagination, enum payloads, timezone и side effects используемых task/project/checklist/tag операций. Публичное имя операции и annotation не доказывают atomicity, idempotency или успешное действие с данными. Restore/unarchive не считать универсальным undo. Новые результаты должны хранить дату, host/client/server, фактический read scope и очищенный evidence, сохраняя исторические snapshots отдельно.
