# What a human decided

Written 2026-08-29 18:14 UTC. procoder reads this
file to avoid asking a question twice; edit an answer here to change what
it believes. Reword the question and it will be asked again.

## [decision] decisions.md

Key: 11776ded3d18
Question: Как завершать triage идеи, справки или встречи?

- two-gates — дать инструкцию ручного переноса; после подтверждения переноса отдельно показать delete-preview и запросить подтверждение удаления.
- keep — только классифицировать и оставить item в Inbox.

Answer: two-gates — дать инструкцию ручного переноса; после подтверждения переноса отдельно показать delete-preview и запросить подтверждение удаления.

## [decision] decisions.md

Key: 2d39940820db
Question: Что делать без scopes для tags/checklists?

- degrade — продолжить tasks/projects, назвать gap и не расширять scopes автоматически.
- block — остановить core-flow до расширения scopes.

Answer: degrade — продолжить tasks/projects, назвать gap и не расширять scopes автоматически.

## [decision] decisions.md

Key: 2f8ecdeffe38
Question: Что делает setup с существующими данными?

- audit-only — только читает кандидатов; migration имеет отдельные preview/confirmation, setup memo не создаётся.
- migrate — мигрирует в том же потоке и сохраняет memo.

Answer: audit-only — только читает кандидатов; migration имеет отдельные preview/confirmation, setup memo не создаётся.

## [decision] decisions.md

Key: 849e77392d38
Question: Что делать с неавторизованными MCP-дублями Hermes plugin?

- alpha2 — удалить `packages/jedikit/mcp.json`, сохранить host-level OAuth MCP, выпустить и установить `v0.1.0-alpha.2`.
- keep — оставить namespaced plugin MCP рядом с host-level connections и не выпускать исправление.

Answer: alpha2 — удалить `packages/jedikit/mcp.json`, сохранить host-level OAuth MCP, выпустить и установить `v0.1.0-alpha.2`.

## [decision] decisions.md

Key: a3cf0b45059c
Question: Какой release-статус сохранять после зелёного gate?

- unreleased — без stable tag, production-ready claim и публикации до отдельного решения.
- release — автоматически поставить tag и опубликовать.

Answer: unreleased — без stable tag, production-ready claim и публикации до отдельного решения.

## [decision] decisions.md

Key: aa5995e56f14
Question: Публиковать ли первый устанавливаемый релиз сейчас?

- alpha — завершить gate, опубликовать `v0.1.0-alpha.1` и установить единый Hermes plugin.
- hold — оставить новый package локальным candidate без tag, публикации и установки.

Answer: alpha — завершить gate, опубликовать `v0.1.0-alpha.1` и установить единый Hermes plugin.

## [decision] decisions.md

Key: b05a157ada9d
Question: Когда сценарий можно назвать supported?

- evidence — deterministic eval плюс отдельный runtime smoke провайдера; остальное помечать unverified.
- structural — достаточно описания и структурной валидации.

Answer: evidence — deterministic eval плюс отдельный runtime smoke провайдера; остальное помечать unverified.

## [decision] decisions.md

Key: bc98e190e749
Question: Как triage использует исходный Inbox item?

- reuse — task/project переиспользует item; при неизвестном шаге он становится «Определить следующий шаг…».
- duplicate — создаётся новая задача, исходный item закрывается отдельно.

Answer: reuse — task/project переиспользует item; при неизвестном шаге он становится «Определить следующий шаг…».

## [decision] decisions.md

Key: cae22f215106
Question: Как отказываться от активного проекта?

- resolve-first — записать причину, решить судьбу каждой открытой задачи, затем показать единый точный preview.
- bulk-close — массово отменить задачи и закрыть проект одним действием.

Answer: resolve-first — записать причину, решить судьбу каждой открытой задачи, затем показать единый точный preview.

## [decision] decisions.md

Key: f1e3e745ff01
Question: Каков утверждённый scope этой итерации?

- implement — обновить research/runtime/evals/README/evidence и пройти gate; не tag/publish.
- plan-only — оставить только журнал решений и план.

Answer: implement — обновить research/runtime/evals/README/evidence и пройти gate; не tag/publish.

## [decision] decisions.md

Key: f505652697e7
Question: Что разрешено хранить в native memory?

- allowlist — timezone, workdays, review windows, IDs/modes и timestamps; без task/project content.
- content — также сохранять пользовательский task/project context.

Answer: allowlist — timezone, workdays, review windows, IDs/modes и timestamps; без task/project content.
