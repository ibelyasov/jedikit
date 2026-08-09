# Live probe официального Singularity MCP

Проверено: **2026-08-09** (Europe/Moscow).

> Этот файл фиксирует первый least-privilege probe с одним `mcp:read`. Последующий full-scope metadata probe подтвердил 48 tools и вынесен в [singularity-mcp-tools.md](singularity-mcp-tools.md); встроенные prompts — в [singularity-mcp-prompts.md](singularity-mcp-prompts.md). Ни в одном из probes инструменты не вызывались.

## Граница проверки

Разрешён только контрактный probe: OAuth, MCP `initialize` и `tools/list`. Задачи, проекты, теги, ресурсы и другие данные аккаунта не читались. Ни один `tools/call` не выполнялся, записи и удаления не производились.

Клиент: Codex CLI `0.147.0`, direct app-server inventory без model turn. Сервер: `https://mcp.singularity-app.com/mcp`.

## OAuth-наблюдения

1. URL с `?toolsets=...` не прошёл OAuth в Codex: protected-resource metadata разрешает только точное resource `https://mcp.singularity-app.com/mcp`.
2. `codex mcp add` для базового URL автоматически начал OAuth и запросил все объявленные read/write scopes. Эта сессия была сразу отозвана до MCP-вызовов.
3. Повторный `codex mcp login --scopes mcp:read` запросил ровно `mcp:read` и завершился успешно.

Вывод: onboarding не должен предполагать, что ограничение `toolsets` в URL совместимо с OAuth-клиентом Codex. Он также не должен полагаться на scopes, автоматически выбранные `mcp add`: их нужно проверять и при необходимости проходить явный least-privilege login.

## Результат `tools/list`

С `mcp:read` сервер сообщил:

```json
{
  "serverInfo": {
    "name": "singularity-mcp",
    "version": "^2.0.1"
  },
  "authStatus": "oAuth",
  "toolCount": 1,
  "toolNames": ["get_my_context"]
}
```

Точная схема единственного доступного инструмента:

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
          "enum": [
            "projects",
            "tags",
            "glossary",
            "filter-syntax"
          ]
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

Инструмент не вызывался. Его описание подтверждает, что сервер также предлагает `singularity://` resources, но resources не входили в разрешённую проверку.

## Что доказано и что остаётся открытым

| Вопрос | Результат |
| --- | --- |
| Hosted MCP отвечает и проходит OAuth | Подтверждено |
| Server name/version | `singularity-mcp` / `^2.0.1` |
| Минимальный scope для inventory | `mcp:read` |
| `tools/list` зависит от OAuth scopes | Подтверждено: при `mcp:read` виден только `get_my_context` |
| Задачи или иные данные были прочитаны | Нет |
| Tool calls выполнялись | Нет |
| Полный контракт task/project/tag/checklist tools | В этом probe не подтверждён; позднее зафиксирован в [полном snapshot](singularity-mcp-tools.md) |
| Write/delete schemas | Create/update/lifecycle подтверждены позднее; явных permanent-delete/batch tools в 48 именах нет |

Исторический вывод этого шага — scopes нужно согласовывать отдельно — остаётся верным. Точные имена и JSON Schema последующего full-scope snapshot находятся в отдельном отчёте, чтобы не смешивать least-privilege observation с более широкой сессией.
