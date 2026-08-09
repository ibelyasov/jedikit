#!/usr/bin/env python3
"""Small in-memory SingularityApp MCP double for deterministic JediKit checks."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CASES_PATH = ROOT / "cases.json"

READ_TOOLS = {
    "project_list",
    "project_get",
    "task_list",
    "task_get",
    "task_list_today",
    "task_list_overdue",
    "task_list_inbox",
}
WRITE_TOOLS = {
    "project_create",
    "project_update",
    "project_archive",
    "task_create",
    "task_update",
    "task_move",
    "task_complete",
    "task_cancel",
    "task_archive",
}
TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "project_list": {"allowed": {"includeRemoved", "includeArchived", "parent", "journalDate", "deleteDate", "isNotebook", "maxCount", "offset", "modifiedSince", "paginationData"}, "required": set()},
    "project_get": {"allowed": {"id"}, "required": {"id"}},
    "project_create": {"allowed": {"title", "parent", "note"}, "required": {"title"}},
    "project_update": {"allowed": {"id", "title", "parent", "note"}, "required": {"id"}},
    "project_archive": {"allowed": {"id", "journalDate"}, "required": {"id"}},
    "task_list": {"allowed": {"includeRemoved", "includeArchived", "projectId", "parent", "group", "start", "deadline", "checked", "priority", "state", "isNote", "maxCount", "offset", "modifiedSince", "paginationData"}, "required": set()},
    "task_get": {"allowed": {"id"}, "required": {"id"}},
    "task_create": {"allowed": {"title", "projectId", "note", "start", "deadline", "priority", "timeLength"}, "required": {"title"}},
    "task_update": {"allowed": {"id", "title", "projectId", "note", "start", "deadline", "priority", "timeLength"}, "required": {"id"}},
    "task_move": {"allowed": {"id", "projectId", "groupId"}, "required": {"id", "projectId"}},
    "task_complete": {"allowed": {"id"}, "required": {"id"}},
    "task_cancel": {"allowed": {"id"}, "required": {"id"}},
    "task_archive": {"allowed": {"id", "journalDate"}, "required": {"id"}},
    "task_list_today": {"allowed": {"timezone", "maxCount", "fields"}, "required": {"timezone"}},
    "task_list_overdue": {"allowed": {"timezone", "maxCount", "fields"}, "required": {"timezone"}},
    "task_list_inbox": {"allowed": {"maxCount", "fields"}, "required": set()},
}
STRING_ARGUMENTS = {"id", "title", "parent", "note", "projectId", "group", "groupId", "journalDate", "deleteDate", "start", "deadline", "fields", "modifiedSince"}
BOOLEAN_ARGUMENTS = {"includeRemoved", "includeArchived", "isNotebook", "isNote", "paginationData"}
NUMBER_ARGUMENTS = {"maxCount", "offset", "priority", "state", "checked", "timeLength"}


def validate_arguments(tool: str, arguments: dict[str, Any]) -> None:
    if tool not in TOOL_SCHEMAS:
        raise ValueError(f"unsupported tool: {tool}")
    if not isinstance(arguments, dict):
        raise ValueError(f"{tool}: arguments must be object")
    schema = TOOL_SCHEMAS[tool]
    missing = schema["required"] - arguments.keys()
    if missing:
        raise ValueError(f"{tool}: missing required {sorted(missing)}")
    extra = arguments.keys() - schema["allowed"]
    if extra:
        raise ValueError(f"{tool}: unsupported arguments {sorted(extra)}")
    for key in schema["required"]:
        if arguments[key] in (None, ""):
            raise ValueError(f"{tool}: empty required argument {key}")
    for key, value in arguments.items():
        expected = str if key in STRING_ARGUMENTS else bool if key in BOOLEAN_ARGUMENTS else (int, float) if key in NUMBER_ARGUMENTS else None
        if key == "timezone":
            expected = (str, int)
        if expected and (not isinstance(value, expected) or isinstance(value, bool) and expected != bool):
            raise ValueError(f"{tool}: invalid type for {key}")


def load_fixture(case_id: str) -> dict[str, Any]:
    data = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    case = next((item for item in data["cases"] if item["id"] == case_id), None)
    if case is None:
        raise ValueError(f"unknown case: {case_id}")
    fixture = copy.deepcopy(data["fixtures"][case["fixture"]])
    fixture["_now"] = data["now"]
    return fixture


class FakeSingularity:
    def __init__(self, fixture: dict[str, Any], *, read_only: bool = False, ledger_path: Path | None = None):
        self.projects = copy.deepcopy(fixture.get("projects", []))
        self.tasks = copy.deepcopy(fixture.get("tasks", []))
        self.memory = copy.deepcopy(fixture.get("memory", {}))
        self.memory_available = fixture.get("memory_available", True)
        self.now = datetime.fromisoformat(fixture["_now"])
        self.sensitive_values = [value for key in ("fake_token", "diagnostic_task_title") if (value := fixture.get(key))]
        self.read_only = read_only
        self.fail_on_write_number = fixture.get("fail_on_write_number")
        self.write_count = 0
        self.ledger: list[dict[str, Any]] = []
        self.ledger_path = ledger_path

    def tools(self) -> list[dict[str, Any]]:
        names = sorted(READ_TOOLS | (set() if self.read_only else WRITE_TOOLS))
        tools = []
        for name in names:
            contract = TOOL_SCHEMAS[name]
            properties = {key: {} for key in sorted(contract["allowed"])}
            tools.append({
                "name": name,
                "description": f"Fake SingularityApp tool: {name}",
                "inputSchema": {"type": "object", "properties": properties, "required": sorted(contract["required"]), "additionalProperties": False},
            })
        return tools

    def record_tools_list(self, *, order: int = 1) -> list[dict[str, Any]]:
        result = self.tools()
        schema_raw = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        summary = {"tools": [tool["name"] for tool in result], "schema_sha256": hashlib.sha256(schema_raw.encode()).hexdigest()}
        self._record("tools_list", {}, summary, False, order)
        return result

    def memory_set(self, key: str, value: Any, *, order: int | None = None) -> dict[str, Any]:
        allowed = {"timezone", "workdays", "review_windows", "root_ids", "root_modes", "last_daily_close", "last_weekly"}
        if not self.memory_available:
            raise RuntimeError("native memory unavailable")
        if key not in allowed:
            raise ValueError(f"native memory key not allowed: {key}")
        self.memory[key] = copy.deepcopy(value)
        result = {"key": key, "value": copy.deepcopy(value)}
        self._record("native_memory_set", {"key": key, "value": value}, result, True, order)
        return result

    def memory_show(self) -> dict[str, Any]:
        if not self.memory_available:
            raise RuntimeError("native memory unavailable")
        allowed = {"timezone", "workdays", "review_windows", "root_ids", "root_modes", "last_daily_close", "last_weekly"}
        return copy.deepcopy({key: value for key, value in self.memory.items() if key in allowed})

    def safe_status(self) -> dict[str, Any]:
        return {
            "mcp_available": True,
            "read_tools": sorted(READ_TOOLS),
            "write_tools_available": not self.read_only,
            "memory_available": self.memory_available,
        }

    def snapshot_digest(self) -> str:
        state = {"projects": self.projects, "tasks": self.tasks, "memory": self.memory_show() if self.memory_available else None}
        raw = json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()

    def call(self, tool: str, arguments: dict[str, Any] | None = None, *, order: int | None = None) -> Any:
        arguments = arguments or {}
        validate_arguments(tool, arguments)
        mutating = tool in WRITE_TOOLS
        if mutating and self.read_only:
            raise PermissionError(f"read-only fake rejects {tool}")
        if mutating:
            self.write_count += 1
            if self.fail_on_write_number == self.write_count:
                error = {"error": f"injected failure on write {self.write_count}"}
                self._record(tool, arguments, error, True, order)
                raise RuntimeError(error["error"])

        result = self._dispatch(tool, arguments)
        self._record(tool, arguments, result, mutating, order)
        return result

    def _dispatch(self, tool: str, args: dict[str, Any]) -> Any:
        if tool == "project_list":
            return copy.deepcopy(self.projects)
        if tool == "project_get":
            return self._get(self.projects, self._required(args, "id"), "project")
        if tool == "task_list":
            tasks = self.tasks
            if "projectId" in args:
                tasks = [item for item in tasks if item.get("projectId") == args["projectId"]]
            for field in ("start", "deadline"):
                if field in args:
                    tasks = [item for item in tasks if item.get(field) == args[field]]
            return self._select_fields(tasks, args.get("fields"))
        if tool == "task_get":
            return self._get(self.tasks, self._required(args, "id"), "task")
        if tool == "task_list_today":
            self._required(args, "timezone")
            today = self.now.date().isoformat()
            tasks = [item for item in self.tasks if item.get("start") == today and item.get("status", "open") == "open"]
            return self._select_fields(tasks, args.get("fields"))
        if tool == "task_list_overdue":
            self._required(args, "timezone")
            today = self.now.date().isoformat()
            tasks = [
                item for item in self.tasks
                if item.get("status", "open") == "open"
                and any(item.get(field) and item[field][:10] < today for field in ("start", "deadline"))
            ]
            return self._select_fields(tasks, args.get("fields"))
        if tool == "task_list_inbox":
            tasks = [item for item in self.tasks if not item.get("projectId") and item.get("status", "open") == "open"]
            return self._select_fields(tasks, args.get("fields"))

        if tool == "project_create":
            item = {"id": self._new_id("p", self.projects), "title": self._required(args, "title")}
            item.update({key: args[key] for key in ("parent", "note") if key in args})
            self.projects.append(item)
            return copy.deepcopy(item)
        if tool == "project_update":
            item = self._get_ref(self.projects, self._required(args, "id"), "project")
            item.update({key: value for key, value in args.items() if key != "id"})
            return copy.deepcopy(item)
        if tool == "project_archive":
            item = self._get_ref(self.projects, self._required(args, "id"), "project")
            item["archived"] = True
            return copy.deepcopy(item)
        if tool == "task_create":
            item = {"id": self._new_id("t", self.tasks), "title": self._required(args, "title"), "status": "open"}
            item.update({key: args[key] for key in ("projectId", "note", "start", "deadline", "priority", "timeLength") if key in args})
            self.tasks.append(item)
            return copy.deepcopy(item)
        if tool == "task_update":
            item = self._get_ref(self.tasks, self._required(args, "id"), "task")
            item.update({key: value for key, value in args.items() if key != "id"})
            return copy.deepcopy(item)
        if tool == "task_move":
            item = self._get_ref(self.tasks, self._required(args, "id"), "task")
            item["projectId"] = self._required(args, "projectId")
            if "groupId" in args:
                item["groupId"] = args["groupId"]
            return copy.deepcopy(item)
        if tool in {"task_complete", "task_cancel", "task_archive"}:
            item = self._get_ref(self.tasks, self._required(args, "id"), "task")
            item["status"] = {"task_complete": "completed", "task_cancel": "cancelled", "task_archive": "archived"}[tool]
            return copy.deepcopy(item)
        raise AssertionError(tool)

    def _record(self, tool: str, arguments: dict[str, Any], result: Any, mutating: bool, order: int | None) -> None:
        seq = len(self.ledger) + 1
        entry = {"seq": seq, "order": order if order is not None else seq, "tool": tool, "arguments": copy.deepcopy(arguments), "result": copy.deepcopy(result), "mutating": mutating}
        self.ledger.append(entry)
        if self.ledger_path:
            with self.ledger_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    @staticmethod
    def _required(args: dict[str, Any], key: str) -> Any:
        if key not in args or args[key] in (None, ""):
            raise ValueError(f"missing required argument: {key}")
        return args[key]

    @staticmethod
    def _new_id(prefix: str, items: list[dict[str, Any]]) -> str:
        return f"{prefix}-fake-{len(items) + 1}"

    @staticmethod
    def _select_fields(items: list[dict[str, Any]], fields: str | None) -> list[dict[str, Any]]:
        if not fields:
            return copy.deepcopy(items)
        selected = {field.strip() for field in fields.split(",") if field.strip()}
        return [{key: copy.deepcopy(value) for key, value in item.items() if key in selected} for item in items]

    @classmethod
    def _get(cls, items: list[dict[str, Any]], item_id: str, kind: str) -> dict[str, Any]:
        return copy.deepcopy(cls._get_ref(items, item_id, kind))

    @staticmethod
    def _get_ref(items: list[dict[str, Any]], item_id: str, kind: str) -> dict[str, Any]:
        item = next((candidate for candidate in items if candidate.get("id") == item_id), None)
        if item is None:
            raise KeyError(f"unknown {kind}: {item_id}")
        return item


def response(request_id: Any, *, result: Any = None, error: Exception | None = None) -> dict[str, Any]:
    if error is not None:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": str(error)}}
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def serve(fake: FakeSingularity) -> None:
    for raw in sys.stdin:
        if not raw.strip():
            continue
        request = json.loads(raw)
        try:
            method = request.get("method")
            if method == "initialize":
                result = {"protocolVersion": "2025-11-25", "capabilities": {"tools": {}}, "serverInfo": {"name": "jedikit-fake", "version": "0.1.0"}}
            elif method == "tools/list":
                result = {"tools": fake.tools()}
            elif method == "tools/call":
                params = request.get("params", {})
                value = fake.call(params.get("name", ""), params.get("arguments", {}))
                result = {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}], "isError": False}
            elif method and method.startswith("notifications/"):
                continue
            else:
                raise ValueError(f"unsupported method: {method}")
            print(json.dumps(response(request.get("id"), result=result), ensure_ascii=False), flush=True)
        except Exception as exc:  # MCP must return errors, not terminate the fixture process.
            print(json.dumps(response(request.get("id"), error=exc), ensure_ascii=False), flush=True)


def self_test() -> None:
    fake = FakeSingularity(load_fixture("S2"))
    first = fake.call("task_create", {"title": "A"})
    assert first["title"] == "A"
    try:
        fake.call("task_create", {"title": "B"})
    except RuntimeError:
        pass
    else:
        raise AssertionError("injected failure did not fire")
    assert len(fake.tasks) == 1
    assert [entry["mutating"] for entry in fake.ledger] == [True, True]

    read_only = FakeSingularity(load_fixture("R5"), read_only=True)
    assert "task_create" not in {tool["name"] for tool in read_only.tools()}
    assert all(tool["inputSchema"]["additionalProperties"] is False for tool in read_only.tools())
    try:
        read_only.call("task_create", {"title": "blocked"})
    except PermissionError:
        pass
    else:
        raise AssertionError("read-only write was accepted")
    for tool, arguments in (("evil_tool", {}), ("task_get", {})):
        try:
            read_only.call(tool, arguments)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid schema accepted: {tool}")
    sparse = FakeSingularity(load_fixture("S4"), read_only=True)
    sparse_today = sparse.call("task_list_today", {"timezone": "Europe/Moscow", "fields": "projectId"})
    assert sparse_today and all(set(item) <= {"projectId"} for item in sparse_today)
    memory = FakeSingularity(load_fixture("R9"))
    shown = json.dumps(memory.memory_show(), ensure_ascii=False)
    assert "Позвонить врачу" not in shown and "Ремонт" not in shown
    memory.memory_set("last_weekly", "2026-08-09T12:00:00+03:00")
    assert memory.memory["last_weekly"] == "2026-08-09T12:00:00+03:00"
    secret = FakeSingularity(load_fixture("S7"))
    status = json.dumps(secret.safe_status(), ensure_ascii=False)
    assert all(value not in status for value in secret.sensitive_values)
    assert len(secret.snapshot_digest()) == 64
    print("fake_mcp: ok")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default="R5")
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--read-only", action="store_true")
    parser.add_argument("--stdio", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.stdio:
        parser.error("choose --stdio or --self-test")
    serve(FakeSingularity(load_fixture(args.case), read_only=args.read_only, ledger_path=args.ledger))


if __name__ == "__main__":
    main()
