# Codex: проверенный платформенный контракт JediKit

**Повторная проверка:** 2026-09-13. Локально установлен `codex-cli 0.154.0`:
версия и справка CLI прочитаны; установка, OAuth и runtime smoke не выполнялись.
Документ заменяет task-only рекомендации 2026-08-08. Исторический plugin smoke
2026-08-29 остаётся в `evals/evidence/` и не подтверждает текущие исходники.

## Skills и активация

Skill содержит `SKILL.md` с `name`/`description`, optional scripts/references/assets.
Codex сначала видит metadata, затем читает выбранный skill; короткое описание
должно содержать назначение и условия запуска. Standalone skills доступны в
CLI/IDE; plugin — отдельная единица распространения. В CLI/IDE явный вход —
`$` или `/skills`, в ChatGPT — `@`; не следует переносить один синтаксис на все
поверхности. Repo discovery сканирует `.agents/skills` от cwd до repo root.
Список metadata ограничен 2% context window либо 8000 символами при неизвестном
размере; описания могут сокращаться, а skills — не попасть в начальный список.
Это не ограничение размера загруженного SKILL.md.
[Официальный контракт skills](https://learn.chatgpt.com/docs/build-skills).

Для JediKit редактируемый источник — `skills/`, распространяемый через plugin;
это не утверждение, что произвольная корневая `skills/` автоматически является
standalone repo discovery path. Два самостоятельных entrypoint остаются
продуктовым решением, а не обязательным правилом OpenAI.

## Plugin и marketplace

Текущая документация рекомендует переносимый root `plugin.json` с Agent Plugins
schema, автоматическим discovery `skills/` и optional `mcp.json`. Специфичные
OpenAI настройки находятся в `extensions.com.openai`.
`.codex-plugin/plugin.json` сохраняется как compatibility fallback; объявлять
его единственным обязательным форматом теперь неверно. `.mcp.json` нельзя просто
переименовать: переносимый формат имеет собственную schema.
[Package plugins](https://developers.openai.com/plugins/build/plugins).

Текущий JediKit использует прежний поддержанный manifest и `.mcp.json`.
Новый формат — основание обсудить миграцию, но этот research refresh её не
выполняет. Plugin-идентичность, его skills и зарегистрированные серверы —
разные сущности; включение vendor URL не регистрирует опубликованный connector.

Локальный/repo marketplace и публичный Plugins Directory — разные способы
доставки. Документированные пути каталогов — `.agents/plugins/marketplace.json`
в repo и пользовательском каталоге; `source.path` относителен marketplace root.
Git/local sources поддерживает CLI `codex plugin marketplace`.
[Формат и команды marketplace](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli).

## MCP

Codex поддерживает STDIO и Streamable HTTP, включая OAuth. CLI configuration
может быть пользовательской либо project-local `.codex/config.toml` в trusted
project. Наличие сервера в конфигурации не доказывает доступ или корректность
его schema. Host-level конфигурация CLI не становится автоматически настройкой
hosted ChatGPT. OAuth и callbacks зависят от поддержки сервера и хоста;
не переносить токены вручную между namespace.
[Официальная MCP документация](https://learn.chatgpt.com/docs/extend/mcp).

JediKit уже требует официальные SingularityApp и Habitify MCP; прежняя фраза
«MCP понадобится позже» устарела. При исследовании endpoints не подключались,
данные аккаунтов не читались. Контракт операции определяется runtime discovery,
а согласие на действие — продуктовой политикой плюс ограничениями хоста.

## Scheduled tasks

Создание/обновление scheduled task из ChatGPT/Codex chat и из skill документировано.
CLI и IDE не предоставляют Scheduled management interface. Desktop local tasks
требуют включённой машины и запущенного приложения; web tasks не имеют доступа
к локальной папке. Event triggers на web/mobile не являются универсальным
scheduler API CLI/desktop. Доступ зависит от поверхности и workspace policy.
[Scheduled tasks](https://learn.chatgpt.com/docs/automations).

JediKit ограничивает фоновые обзоры чтением и приглашением к диалогу по своему
решению; это не встроенная гарантия всех scheduled tasks OpenAI. Сохранённый
prompt и runtime permissions нужно проверять отдельно.

## Публикация

Публичная submission поддерживает skills-only, MCP-only и смешанные plugins.
Нужны право Apps Management Write и проверенная identity организации;
документация перечисляет listing/support/privacy/terms, пять positive и три
negative cases. Submit, review и последующая публикация — разные этапы.
Для стороннего MCP требования подтверждения домена могут потребовать участия
владельца провайдера; root URL в manifest не даёт нам права подтвердить его домен.
[Submission](https://developers.openai.com/plugins/deploy/submission).

## Локально проверено и не проверено

Выполнены только read-only команды:

```text
codex --version
codex plugin marketplace --help
codex mcp --help
```

CLI 0.154.0 подтвердил `marketplace add/list/upgrade/remove` и
`mcp list/get/add/remove/login/logout`. Сами мутации не запускались.

Текущие официальные страницы подтверждают описанный формат, но не его принятие
каждой установленной версией или аккаунтом. Загрузка текущего JediKit, implicit
routing, writes/read-back и scheduler остаются отдельной runtime acceptance.
Решением владельца от 2026-09-13 Hermes стал единственным обязательным хостом
приёмки v1. Codex сохраняется как исследованная платформа с неподтверждённой
runtime-совместимостью. Исполняемый gate уже считает Codex optional и не
принимает его evidence вместо Hermes. Актуальный контракт —
[product-decisions §22](product-decisions.md#22-перепроверка-исследований-и-пересборка-2026-09-13).

## Как интерпретировать проверку совместимости

Исследовательский маршрут для будущей приёмки Codex состоит из разных уровней.
Это предлагаемый порядок проверки JediKit, а не результаты выполненного теста.

| Уровень | Что наблюдать | Почему этого ещё недостаточно |
| --- | --- | --- |
| Версия и интерфейс | Версия CLI и фактическая справка требуемой команды | Current docs могут описывать более новую реализацию |
| Источник распространения | Какой marketplace/repository и revision выбран | Наличие записи каталога не означает установку пакета |
| Пакет | Какие manifests, skills и MCP declarations приняты parser | Валидный JSON не доказывает загрузку инструкций моделью |
| Контекст новой сессии | Какие skills доступны и какое имя раскрывает host | UI-метка сама по себе не доказывает исполнение выбранного workflow |
| Discovery провайдера | Доступные официальные tools и их schemas | Соединение не подтверждает права на конкретную запись |
| Поведение | Позитивный запрос, отказ/уточнение, отсутствие лишних действий | Один удобный пример не покрывает safety и ошибки |
| Изменения | Preview, разрешённая операция и чтение результата обратно | Этот уровень нельзя заменить историческим trace или фиктивным отчётом |

До измерения поведения фиксируются исходник пакета, host/model и условия
запуска. После изменения инструкций прежний trace остаётся историческим.
Конкретные команды discovery/cache refresh следует брать из фактической
установленной версии; здесь не задаётся непроверенный путь удаления cache.

Полезный отрицательный пример: наличие `$jedikit-habits` в списке не является
свидетельством корректного отказа на опасный запрос. Полезный положительный
пример: наблюдаемая загрузка нужных instructions плюс корректный ответ на
заранее заданный сценарий подтверждает именно этот сценарий в этой среде.
Эти примеры — метод проверки, а не новые наблюдения.
