## Как triage использует исходный Inbox item?

- reuse — task/project переиспользует item; при неизвестном шаге он становится «Определить следующий шаг…».
- duplicate — создаётся новая задача, исходный item закрывается отдельно.

## Как завершать triage идеи, справки или встречи?

- two-gates — дать инструкцию ручного переноса; после подтверждения переноса отдельно показать delete-preview и запросить подтверждение удаления.
- keep — только классифицировать и оставить item в Inbox.

## Что разрешено хранить в native memory?

- allowlist — timezone, workdays, review windows, IDs/modes и timestamps; без task/project content.
- content — также сохранять пользовательский task/project context.

## Что делает setup с существующими данными?

- audit-only — только читает кандидатов; migration имеет отдельные preview/confirmation, setup memo не создаётся.
- migrate — мигрирует в том же потоке и сохраняет memo.

## Как отказываться от активного проекта?

- resolve-first — записать причину, решить судьбу каждой открытой задачи, затем показать единый точный preview.
- bulk-close — массово отменить задачи и закрыть проект одним действием.

## Что делать без scopes для tags/checklists?

- degrade — продолжить tasks/projects, назвать gap и не расширять scopes автоматически.
- block — остановить core-flow до расширения scopes.

## Когда сценарий можно назвать supported?

- evidence — deterministic eval плюс отдельный runtime smoke провайдера; остальное помечать unverified.
- structural — достаточно описания и структурной валидации.

## Какой release-статус сохранять после зелёного gate?

- unreleased — без stable tag, production-ready claim и публикации до отдельного решения.
- release — автоматически поставить tag и опубликовать.

## Каков утверждённый scope этой итерации?

- implement — обновить research/runtime/evals/README/evidence и пройти gate; не tag/publish.
- plan-only — оставить только журнал решений и план.

## Публиковать ли первый устанавливаемый релиз сейчас?

- alpha — завершить gate, опубликовать `v0.1.0-alpha.1` и установить единый Hermes plugin.
- hold — оставить новый package локальным candidate без tag, публикации и установки.

## Что делать с неавторизованными MCP-дублями Hermes plugin?

- alpha2 — удалить `packages/jedikit/mcp.json`, сохранить host-level OAuth MCP, выпустить и установить `v0.1.0-alpha.2`.
- keep — оставить namespaced plugin MCP рядом с host-level connections и не выпускать исправление.
