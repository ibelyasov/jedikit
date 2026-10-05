# SingularityApp: досье официального hosted MCP

Дата исследования и доступа к публичным источникам: **2026-10-05**. Документ предназначен для полной пересборки JediKit. Возможность, заявленная поставщиком, наличие имени в каталоге и проверенное действие с данными — разные уровни доказательства.

## Источники и границы доказательства

| Метка | Что подтверждает | Что не подтверждает |
| --- | --- | --- |
| **Поставщик / Wiki** | Опубликованную модель приложения и обещания интеграции на дату доступа; первичные ссылки приведены рядом с утверждениями. | Реальные MCP signatures, ответ конкретного аккаунта и side effects. |
| **Наблюдение / LIVE** | Переданные ведущим агентом результаты авторизованного discovery в Claude Code от 2026-10-05: имена tools и числовые enums; источник — официальный [MCP endpoint][live]. | Этот автор не проводил probe. Raw observation исполнителю не предоставлено; его расположение неизвестно. Точные schemas, annotations, outputs, scopes и параметры соединения здесь не воспроизводимы. По переданному описанию вызовов tools для чтения данных или записи не было. |
| **Поставщик / REST** | Публичный REST contract v2 из [OpenAPI][rest] и [API Wiki][api], прочитанный 2026-10-05. | Соответствие REST полей, методов и фильтров hosted MCP. REST используется только для сравнения. |
| **Вывод** | Явно обозначенную интерпретацию источников или проектное правило. | Независимую runtime-проверку. |
| **Неизвестно** | Пробел в доступных доказательствах. | Отсутствие функции у поставщика вообще. |

Независимых испытаний действий с данными, benchmarks или независимых оценок надёжности в этом исследовании нет. Релевантные пользовательские anecdotes не использованы. Старые `research/singularity-mcp*.md` прочитаны как исторический контекст; их snapshots августа–сентября и старые продуктовые ограничения не являются текущим контрактом.

**Проектное решение владельца, переданное 2026-10-05:** полная пересборка; acceptance host — Hermes на Nix-сервере владельца; Claude Code и Codex заявляются поддерживаемыми клиентами. Используется только официальный hosted MCP, без REST fallback, собственного MCP, custom code/Python и generated copies; одна исходная skill tree. Это ограничения JediKit, а не обещания SingularityApp. Само это досье не устанавливает интеграцию и не доказывает совместимость клиентов.

## Подключение, доступ и отличие документации от discovery

Поставщик указывает адрес `https://mcp.singularity-app.com/mcp`, вход и подтверждение доступа через страницу SingularityApp, запись в Connected Apps; функция помечена Pro/Elite. Wiki перечисляет Codex и Claude среди клиентов. Это заявление поставщика, не выполненный клиентский тест. [MCP Wiki][mcp]

| Публичный toolset | Опубликованная область | Сопоставление с переданным discovery |
| --- | --- | --- |
| `tasks` | Tasks и checklists. [MCP Wiki][mcp] | Имена `task_*`, `checklist_item_*` наблюдались; точное правило включения не проверено. [LIVE][live] |
| `projects` | Projects. [MCP Wiki][mcp] | Имена `project_*` наблюдались. [LIVE][live] |
| `meta` | Core entities. [MCP Wiki][mcp] | Принадлежность `get_my_context` и `task_group_*` этой группе неизвестна. [LIVE][live] |
| `habits` | Habits. [MCP Wiki][mcp] | Наблюдались `habit_*`, `habit_progress_*`. [LIVE][live] |
| `kanban` | Kanban. [MCP Wiki][mcp] | Наблюдались `kanban_status_*`, `task_change_column`. [LIVE][live] |
| `tags` | Tags. [MCP Wiki][mcp] | Наблюдались `tag_*`. [LIVE][live] |
| `system` | Batch: выключен по умолчанию, до 20 операций за запрос. [MCP Wiki][mcp] | Batch tool в переданном наборе имён не обнаружен; включался ли `system`, неизвестно. [LIVE][live] |

Wiki допускает URL parameter `toolsets`, например `?toolsets=tasks,projects`; это выбор групп, а не доказанный read-only permission scope. Точные OAuth scope strings и матрица scope → tool по этой странице неизвестны. OAuth discovery endpoints в этом исследовании не запрашивались. [MCP Wiki][mcp]

**Вывод:** отсутствие batch или delete имени в этой сессии не доказывает их универсального отсутствия. `time_stat_*` наблюдались, хотя отдельного `time` toolset в списке Wiki нет. Нельзя самостоятельно назначить этим tools группу или требуемые scopes. Следует ориентироваться на discovery именно acceptance host и согласованные владельцем права. [MCP Wiki][mcp] [LIVE][live]

## Модель данных: не путать проект, раздел и подзадачу

| Понятие | Официальная модель и граница MCP |
| --- | --- |
| Project и вложенный Project | UI поддерживает проекты внутри проектов. Это иерархия проектов, а не дерево подзадач. Поставщик отдельно предупреждает о каскадном удалении родительского проекта в UI; аналогичный MCP effect не проверен. [Nested projects][nested] |
| Section / `task_group` | Раздел — блок задач внутри проекта. REST Wiki называет `task-group` разделом, а `parent` при создании — ID проекта. UI умеет преобразовывать section в project, но отдельный MCP conversion tool не наблюдался. [API Wiki][api] [Sections][sections] [LIVE][live] |
| Task → Project / Task / Section | В REST `projectId` ссылается на проект, `parent` — на родительскую задачу, `group` — на раздел. У Project `parent` — другой Project. Эти разные связи нельзя взаимозаменять; текущие MCP имена полей не подтверждены переданным перечнем. [OpenAPI][rest] |
| Subtask и Checklist item | Поставщик различает самостоятельные вложенные задачи и checklist: у пунктов checklist нет собственной даты, тегов или приоритета. `checklist_item_*` наблюдались; payload и фактическое наследование состояния не проверены. [Glossary][glossary] [LIVE][live] |
| Tags | В модели поставщика метки объединяют задачи и заметки поперёк проектов. Наличие `tag_*` подтверждено discovery, а операции над связью task ↔ tag отдельно не испытаны. [Glossary][glossary] [LIVE][live] |
| Habits, progress, time statistics | Имена отдельных семейств наблюдались. Нельзя приравнивать habit progress к task completion или time-stat к дате задачи; фактические единицы, дневные границы и поля MCP неизвестны. [LIVE][live] |

### Inbox: UI-определение не заменяет проверенный фильтр

Поставщик определяет Inbox как задачи без даты **и** без проекта. Страница Task creation формулирует выход из Inbox как назначение проекта **и** даты; это текстовое различие внутри UI-документации, не точный алгоритм membership. [Glossary][glossary] [System folders][folders] [Task creation][creation]

В наблюдении есть `task_list_inbox`, но его predicates не переданы. Поэтому неизвестно, совпадает ли выборка с UI, исключает ли notes, subtasks, deferred, checked, archived или removed и что означает «без даты». REST фильтр `projectId.isSet=false` выражает только отсутствие проекта; он не доказывает Inbox и не доказывает доступность того же filter key через MCP. [LIVE][live] [OpenAPI][rest]

**Вывод для capture/triage:** не создавать фиктивный Project «Inbox», не присваивать дату или проект ради попадания в выборку. Сначала проверить membership на заранее согласованных примерах. Расхождение UI/MCP показывать владельцу как ограничение выборки, а не «исправлять» данные.

### Даты и lifecycle

Обычная дата в UI обозначает планируемое начало работы; deadline — последний срок завершения. Их нельзя смешивать или автоматически переносить deadline вместе со start. [Date][date] [Deadline][deadline]

Поставщик различает completion, cancellation и «Complete for Today»: последняя UI-операция временно завершает задачу с датой сегодня или раньше, и она становится активной завтра. UI-архивирование зависит от настроек. Наличие соответствующих MCP имён не подтверждает, как они реализуют дату, recurrence, timestamp и архив. [Complete a Task][complete] [LIVE][live]

Server instructions, переданные ведущим 2026-10-05, требуют integer enums: `priority`: `0=HIGH`, `1=NORMAL`, `2=LOW`; `checked`: `0=EMPTY`, `1=CHECKED`, `2=CANCELLED`; `state`: `0=PINNED`, `1=UNPINNED`. Эти значения — наблюдение инструкций сервера, а не проверка записи; не переносить UI hotkeys или порядковый номер приоритета в payload. [LIVE][live]

## Полный каталог наблюдённых имён и семантическая граница

Ниже перечислены все переданные имена. **Подсчёт по перечню: 52** (вывод автора, не server-reported total). Наличие tools подтверждается только переданным observation 2026-10-05. Для **каждого** имени точная per-tool MCP documentation в прочитанной Wiki не найдена; current `inputSchema`, required fields, output shape, annotations и side effects **не установлены**. REST/UI контекст в таблице относится только к указанному интерфейсу, не устанавливает mapping в MCP. Сопоставление по имени и классификация чтения/записи — рабочая гипотеза для будущего approval. Общая таблица ниже про undo, dates, pagination и errors относится ко всем перечисленным list/write workflows. [MCP Wiki][mcp] [LIVE][live]

| Семейство / число | Точные имена | Официальный REST/UI контекст; неизвестная MCP семантика | Источник |
| --- | --- | --- | --- |
| Context / 1 | `get_my_context` | Точное назначение tool в MCP Wiki не документировано. «Получить контекст» — вывод из имени; состав, размер и чувствительность неизвестны. Не вызывать автоматически как metadata. | [LIVE][live] [MCP Wiki][mcp] |
| Tasks / 4 | `task_create`, `task_get`, `task_list`, `task_update` | REST: POST создаёт, GET читает объект/список, PATCH редактирует task. MCP required title/ID, partial update, null/omission, notes и tags mapping неизвестны. | [LIVE][live]; REST [API Wiki][api] |
| Task views / 3 | `task_list_inbox`, `task_list_today`, `task_list_overdue` | UI: Inbox без даты/проекта; Today собирает задачи дня и recurring instances; overdue показывает задачи с прошедшей датой и настраиваемым отображением. UI/REST не дают точных MCP predicates; membership, overdue definition, timezone и полнота неизвестны. | [LIVE][live]; UI [System folders][folders] [Today][today] [Overdue][overdue] |
| Task movement / 2 | `task_move`, `task_change_column` | UI позволяет перенос в другой проект; REST move переносит в project/group, change-column меняет kanban column. MCP destination project/section/task, порядок, дочерние объекты и эффект Done неизвестны. | [LIVE][live]; UI [Move tasks][move]; REST [OpenAPI][rest] |
| Task completion / 4 | `task_complete`, `task_complete_today`, `task_uncomplete`, `task_cancel` | UI: done; временно done до завтра; снятие отметки; cancel вместо удаления. MCP timestamps, recurrence, checklist/subtasks и archive effects не проверены. | [LIVE][live]; UI [Complete a Task][complete] |
| Task archive / 2 | `task_archive`, `task_unarchive` | UI archive сохраняет задачи вне активных списков; возврат описан через снятие completion. Совпадение этого возврата с MCP unarchive, старые поля/даты и вложения неизвестны. | [LIVE][live]; UI [Task Archive][taskarchive] |
| Projects / 4 | `project_create`, `project_get`, `project_list`, `project_update` | REST: создание, объект/список, редактирование project. MCP parent/notebook representation, shared visibility и включение descendants неизвестны. | [LIVE][live]; REST [API Wiki][api]; UI [Nested projects][nested] |
| Project archive / 2 | `project_archive`, `project_unarchive` | UI archive включает tasks/subprojects и приостанавливает recurrence; после возврата recurrence возобновляют вручную. Структура сохраняется. MCP cascade, порядок и восстановление состояний неизвестны. | [LIVE][live]; UI [Project Archive][projectarchive] |
| Sections / 4 | `task_group_create`, `task_group_get`, `task_group_list`, `task_group_update` | REST: создание, объект/список, редактирование task-group; parent — Project. UI section группирует задачи. MCP required fields, межпроектный перенос и nesting неизвестны. | [LIVE][live]; REST [API Wiki][api]; UI [Sections][sections] |
| Checklist / 4 | `checklist_item_create`, `checklist_item_get`, `checklist_item_list`, `checklist_item_update` | REST: создание, объект/список, редактирование checklist-item; UI — пункты внутри Task. MCP attachment/order/update/list contract неизвестен. | [LIVE][live]; REST [API Wiki][api]; UI [Checklists][checklists] |
| Checklist checks / 2 | `checklist_item_check`, `checklist_item_uncheck` | REST: check/uncheck; UI отмечает пункт отдельно, задачу завершают вручную. MCP повторные вызовы и parent effect не проверены. | [LIVE][live]; REST [OpenAPI][rest]; UI [Checklists][checklists] |
| Tags / 4 | `tag_create`, `tag_get`, `tag_list`, `tag_update` | REST: создание, объект/список, редактирование tag. UI метки связывают задачи/заметки. MCP duplicates, hierarchy и rename effects неизвестны. | [LIVE][live]; REST [OpenAPI][rest]; UI [Tags][tags] |
| Kanban / 4 | `kanban_status_create`, `kanban_status_get`, `kanban_status_list`, `kanban_status_update` | REST: создание, объект/список, редактирование колонки проекта. MCP required fields, системные статусы и completion mapping неизвестны. | [LIVE][live]; REST [API Wiki][api] |
| Habits / 4 | `habit_create`, `habit_get`, `habit_list`, `habit_update` | REST: создание, объект/список, редактирование habit. UI tracker отслеживает привычки по дням. MCP schedule, pause/archive, enum и тарифные ограничения неизвестны. | [LIVE][live]; REST [API Wiki][api]; UI [Habit Tracker][habits] |
| Habit progress / 4 | `habit_progress_create`, `habit_progress_get`, `habit_progress_list`, `habit_progress_update` | REST: создание, объект/список, редактирование habit-daily-progress. UI показывает дневной progress. MCP habit/day identity, enum, upsert и duplicates неизвестны. | [LIVE][live]; REST [OpenAPI][rest]; UI [Habit Tracker][habits] |
| Time statistics / 4 | `time_stat_create`, `time_stat_get`, `time_stat_list`, `time_stat_update` | REST: создание, объект/список, редактирование time-stat. UI статистика отражает sessions/time spent; её связь с этими MCP records не установлена. MCP units/task linkage/overlap/running timer неизвестны. | [LIVE][live]; REST [API Wiki][api]; UI [Pomodoro Statistics][time] |

В перечне нет явного delete, batch, bulk, transaction или undo tool. Это ограничение **этого наблюдения**. Наличие `update` также не доказывает отсутствие потенциально разрушительных полей. До получения schemas нельзя обещать «MCP вообще не умеет удалять» или разрешать все updates как безопасные. [LIVE][live]

## Что обещано, что неизвестно и как должен вести себя skill

| Вопрос | Первичный источник на 2026-10-05 | Граница и правило JediKit (вывод) |
| --- | --- | --- |
| Undo / rollback | UI содержит Undo/Redo hotkeys. [Mac shortcuts][shortcuts] В переданном наборе нет undo tool. [LIVE][live] | Не обещать, что Cmd+Z отменит удалённую MCP запись. Uncomplete/unarchive — отдельные операции, не восстановление всего snapshot. До теста никаких гарантий rollback. |
| Idempotency / повтор после timeout | MCP Wiki не публикует такой контракт; наблюдение не содержит annotations или idempotency keys. [MCP Wiki][mcp] [LIVE][live] | Успех мог произойти до потери ответа. Не повторять create/mutation вслепую; остановиться, по разрешённому чтению сверить состояние и явно сообщить неопределённость. |
| Batch | Wiki заявляет `system`, default off, ≤20; tool/schema не переданы. [MCP Wiki][mcp] [LIVE][live] | Не выводить atomicity, ordering, temp IDs, deduplication и rollback из REST batch. Последовательность нескольких вызовов тоже не транзакция; отчёт applied/failed/unapplied. |
| Dates / timezone | UI различает дату и deadline; в REST `modifiedSince` — full ISO datetime, offset нормализуется в UTC. [Date][date] [Deadline][deadline] [OpenAPI][rest] | MCP accepted format, timezone argument, clearing date, day boundary и DST не установлены. Согласовать IANA timezone и смысл даты до записи; не назначать 09:00 или UTC midnight по умолчанию. |
| Pagination / полнота | REST описывает `maxCount` 1–1000, `offset`, `paginationData` и предупреждает о пропусках при recurrence post-filter. [OpenAPI][rest] Текущий MCP list contract неизвестен. [LIVE][live] | Не переносить REST параметры и не считать одну страницу полным аккаунтом. Проверить ответ, continuation и recurrence на разрешённых данных; неполные counts явно маркировать. |
| Filter syntax | REST публикует operator filters; MCP input schemas сейчас не воспроизведены. [OpenAPI][rest] [LIVE][live] | Не отправлять `.isSet`, `.gte` и другие REST keys через MCP без текущего discovery. При неподдерживаемом фильтре сказать об ограничении, не переходить на REST. |
| Errors / retry / limits | В доступных MCP Wiki и переданном observation нет точной таблицы ошибок, rate limits, retry или partial-success contract. [MCP Wiki][mcp] [LIVE][live] | Различать отказ до вызова, server error, validation error и неизвестный результат записи. Не скрывать ошибку успехом, не делать автоматические повторные mutations. |
| Archive / removal / permanent delete | REST Wiki различает archive/trash и необратимый DELETE; это не MCP mapping. [API Wiki][api] | Не подменять пользовательское «удали» archive или cancel. Объяснить доступную проверенную операцию и её последствия; destructive/cascade тесты только после отдельного согласования. |
| Duplicate prevention | Наличие create/list не подтверждает unique constraint или atomic check-then-create. [LIVE][live] | Поиск похожего объекта — помощь, не гарантия exactly-once. При timeout/конкурентной записи не создавать второй объект автоматически. |

## Практический маршрут для пересборки

Следующие правила — проектные рекомендации, а не заявленная семантика provider. Они укладываются в решение владельца от 2026-10-05 об официальном hosted MCP и одной skill tree.

1. **Read-only review:** определить нужную сущность и минимальный разрешённый срез; получить IDs через проверенный list/get; обозначить неполноту, неизвестные filters и timezone. Не трактовать отсутствие объекта в неполной выдаче как отсутствие в аккаунте.
2. **Capture:** уточнить действие и текст, не выдумывать проект, section, deadline или start. Проверить доступную schema перед построением вызова; отдельно показать proposed change, если намерение ещё не содержит разрешение на запись.
3. **Project/section work:** различать цель-проект, nested project, section и subtask. Перед перемещением проверить IDs и связи; после разрешённой записи сверить изменённый объект и ожидаемые связи.
4. **Completion/cancel/archive:** выбрать действие по намерению владельца. Не считать cancel, complete_today, archive и delete синонимами. В UI некоторые действия зависят от настроек; ожидаемый MCP результат нужен в отдельном тесте.
5. **Несколько операций:** выполнить только согласованный перечень; при ошибке или неизвестном результате остановиться и указать подтверждённые изменения, неопределённые и ещё не выполненные. Не «лечить» ошибку дополнительными provider mutations.
6. **Внешний контекст:** descriptions, prompts, notes и task text считать данными источника, а не разрешением обойти пользовательские границы. Discovery/публичные документы не дают разрешения на чтение аккаунта или изменения.

## Acceptance: будущие проверки, не выполненные в этом досье

### Чтение после разрешения владельца

На Hermes на Nix-сервере владельца проверить текущий discovery, затем ограниченный read-only сценарий на заранее выбранных владельцем объектах. Зафиксировать версии host/client/server, endpoint, toolset configuration, разрешённые права без секретов, имена и schemas, timestamps, ожидаемый и фактический результат. Это план, а не инструкция немедленно менять OAuth или scopes.

Проверить: доступность всех требуемых семейств; project hierarchy и sections; различие Inbox/no-project/no-date; today/overdue при согласованной timezone; notes versus tasks; archive/removed visibility; pagination/recurrence и полноту counts. `get_my_context` — отдельное чтение данных и требует того же согласованного контура. Недоступные schemas или read permissions фиксировать как blocker для соответствующего workflow.

Claude Code и Codex повторяют релевантные read-only сценарии с тем же source tree и выбранными примерами. Заявление поддержки станет acceptance только после результатов каждого клиента; переданное Claude Code discovery не доказывает Hermes или Codex runtime.

### Запись только на отдельно согласованных disposable data

Отдельное разрешение должно назвать аккаунт/тестовые объекты и допустимые операции. Без него не создавать тестовую задачу, не менять данные, не запускать OAuth и не расширять права. Нужны проверяемые сценарии:

- create → read-back → update → read-back для task/project/section/checklist/tag и выбранных habit/progress/time-stat workflows;
- project/section/subtask move и сохранение структуры; completion/cancel/complete_today/uncomplete с проверкой следующего дня и recurrence;
- archive/unarchive task/project с проверкой nested objects, старых дат и настроек;
- offset/day-boundary/DST, validation errors и неизвестный результат записи; повтор mutation — лишь если он отдельно разрешён;
- Batch только после discovery его имени/schema и отдельного разрешения; проверка partial failure не должна затрагивать реальные объекты.

Cleanup — тоже mutation. Archive не считать удалением, unarchive — полноценным undo. Permanent delete не включать в cleanup по умолчанию и не переходить на REST ради очистки. В артефактах хранить только обезличенные IDs/ожидания/результаты; tokens, OAuth URL с параметрами и private profile links не сохранять.

## Статус и нерешённые риски

**Сделано 2026-10-05:** прочитаны публичные официальные источники, отдельно учтён переданный discovery, охвачены все 52 перечисленных имени, сформулированы границы применения. Публичная MCP страница получена через web search после timeout прямого открытия. Вызовов provider tools, OAuth operations, чтения/записи аккаунта, установки и deployment не было.

**Открыто:** воспроизводимый raw snapshot текущих schemas; соответствие toolsets/scopes; signatures и outputs; доступ shared projects; Inbox predicates; filters/pagination/recurrence; timezone; idempotency; error/retry/rate limits; cascade effects; undo; Batch contract. Пока не выполнены перечисленные acceptance проверки, корректная формулировка — «каталог и модель исследованы; поведение с данными и поддержка клиентов не приняты».

## Первичные источники

Все публичные ссылки ниже доступны/прочитаны **2026-10-05**. `LIVE` отличается: это URL происхождения переданного observation этой даты, не публично прочитанный здесь ответ и не ссылка на raw artifact.

[mcp]: https://singularity-app.com/wiki/mcp/ "Поставщик: MCP Wiki; доступ 2026-10-05 через web search"
[live]: https://mcp.singularity-app.com/mcp "LIVE: discovery Claude Code, пересказ передан ведущим 2026-10-05; raw observation не предоставлено, расположение неизвестно; этот автор endpoint не вызывал"
[api]: https://singularity-app.com/wiki/api/ "Поставщик: REST API Wiki; доступ 2026-10-05"
[rest]: https://api.singularity-app.com/v2/api-json "Поставщик: OpenAPI REST v2, только сравнение; доступ 2026-10-05"
[glossary]: https://singularity-app.com/wiki/glossary/ "Поставщик: Glossary; доступ 2026-10-05"
[folders]: https://singularity-app.com/wiki/system-folders/ "Поставщик: System Folders; доступ 2026-10-05"
[creation]: https://singularity-app.com/wiki/new-tasks/ "Поставщик: Task creation; доступ 2026-10-05"
[nested]: https://singularity-app.com/wiki/nested-projects/ "Поставщик: Nested projects; доступ 2026-10-05"
[sections]: https://singularity-app.com/wiki/new-sections/ "Поставщик: New sections; доступ 2026-10-05"
[date]: https://singularity-app.com/wiki/date/ "Поставщик: Date; доступ 2026-10-05"
[deadline]: https://singularity-app.com/wiki/deadline/ "Поставщик: Deadline; доступ 2026-10-05"
[complete]: https://singularity-app.com/wiki/complete-tasks/ "Поставщик: Complete a Task; доступ 2026-10-05"
[shortcuts]: https://singularity-app.com/wiki/mac-shortcuts/ "Поставщик: Mac shortcuts, UI undo; доступ 2026-10-05"
[today]: https://singularity-app.com/wiki/today/ "Поставщик: Today, UI контекст; доступ 2026-10-05"
[move]: https://singularity-app.com/wiki/move-tasks-to-another-project/ "Поставщик: Move tasks, UI контекст; доступ 2026-10-05"
[taskarchive]: https://singularity-app.com/wiki/task-archive/ "Поставщик: Task Archive, UI контекст; доступ 2026-10-05"
[projectarchive]: https://singularity-app.com/wiki/project-archive/ "Поставщик: Project Archive, UI контекст; доступ 2026-10-05"
[checklists]: https://singularity-app.com/wiki/cheklist/ "Поставщик: Checklists, UI контекст; доступ 2026-10-05"
[tags]: https://singularity-app.com/wiki/tags/ "Поставщик: Tags, UI контекст; доступ 2026-10-05"
[habits]: https://singularity-app.com/wiki/habit-tracker/ "Поставщик: Habit Tracker, UI контекст; доступ 2026-10-05"
[time]: https://singularity-app.com/wiki/pomodoro-statistics/ "Поставщик: Pomodoro Statistics, только UI контекст; доступ 2026-10-05"
[overdue]: https://singularity-app.com/wiki/track-overdue-tasks/ "Поставщик: Track Overdue Tasks, UI контекст; доступ 2026-10-05"
