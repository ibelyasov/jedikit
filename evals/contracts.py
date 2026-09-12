"""Typed contracts shared by fake discovery and ledger validation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True)
class Argument:
    json_type: str
    python_types: tuple[type, ...]


@dataclass(frozen=True)
class ToolContract:
    arguments: Mapping[str, Argument]
    required: frozenset[str] = frozenset()
    mutating: bool = False
    result_kind: str = "object"

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                name: {"type": argument.json_type}
                for name, argument in sorted(self.arguments.items())
            },
            "required": sorted(self.required),
            "additionalProperties": False,
        }

    def validate(self, tool: str, values: Any) -> None:
        if not isinstance(values, dict):
            raise TypeError(f"{tool}: arguments must be object")
        missing = self.required - values.keys()
        if missing:
            raise ValueError(f"{tool}: missing required {sorted(missing)}")
        extra = values.keys() - self.arguments.keys()
        if extra:
            raise ValueError(f"{tool}: unsupported arguments {sorted(extra)}")
        for name, value in values.items():
            if name in self.required and value in (None, ""):
                raise ValueError(f"{tool}: empty required argument {name}")
            expected = self.arguments[name].python_types
            if not isinstance(value, expected) or (
                isinstance(value, bool) and bool not in expected
            ):
                raise ValueError(f"{tool}: invalid type for {name}")


STRING = Argument("string", (str,))
BOOLEAN = Argument("boolean", (bool,))
NUMBER = Argument("number", (int, float))


def _args(*names: str, **overrides: Argument) -> Mapping[str, Argument]:
    values = {name: STRING for name in names}
    values.update(overrides)
    return MappingProxyType(values)


TOOL_CONTRACTS: Mapping[str, ToolContract] = MappingProxyType(
    {
        "project_list": ToolContract(
            _args(
                "parent",
                "journalDate",
                "deleteDate",
                "modifiedSince",
                includeRemoved=BOOLEAN,
                includeArchived=BOOLEAN,
                isNotebook=BOOLEAN,
                maxCount=NUMBER,
                offset=NUMBER,
                paginationData=BOOLEAN,
            ),
            result_kind="array",
        ),
        "project_get": ToolContract(_args("id"), frozenset({"id"})),
        "project_create": ToolContract(
            _args("title", "parent", "note"), frozenset({"title"}), True
        ),
        "project_update": ToolContract(
            _args("id", "title", "parent", "note"), frozenset({"id"}), True
        ),
        "project_archive": ToolContract(
            _args("id", "journalDate"), frozenset({"id"}), True
        ),
        "task_list": ToolContract(
            _args(
                "projectId",
                "parent",
                "group",
                "start",
                "deadline",
                "modifiedSince",
                includeRemoved=BOOLEAN,
                includeArchived=BOOLEAN,
                checked=NUMBER,
                priority=NUMBER,
                state=NUMBER,
                isNote=BOOLEAN,
                maxCount=NUMBER,
                offset=NUMBER,
                paginationData=BOOLEAN,
            ),
            result_kind="array",
        ),
        "task_get": ToolContract(_args("id"), frozenset({"id"})),
        "task_create": ToolContract(
            _args(
                "title",
                "projectId",
                "note",
                "start",
                "deadline",
                priority=NUMBER,
                timeLength=NUMBER,
            ),
            frozenset({"title"}),
            True,
        ),
        "task_update": ToolContract(
            _args(
                "id",
                "title",
                "projectId",
                "note",
                "start",
                "deadline",
                priority=NUMBER,
                timeLength=NUMBER,
            ),
            frozenset({"id"}),
            True,
        ),
        "task_move": ToolContract(
            _args("id", "projectId", "groupId"), frozenset({"id", "projectId"}), True
        ),
        "task_complete": ToolContract(_args("id"), frozenset({"id"}), True),
        "task_cancel": ToolContract(_args("id"), frozenset({"id"}), True),
        "task_archive": ToolContract(
            _args("id", "journalDate"), frozenset({"id"}), True
        ),
        "task_list_today": ToolContract(
            _args("timezone", "fields", maxCount=NUMBER),
            frozenset({"timezone"}),
            result_kind="array",
        ),
        "task_list_overdue": ToolContract(
            _args("timezone", "fields", maxCount=NUMBER),
            frozenset({"timezone"}),
            result_kind="array",
        ),
        "task_list_inbox": ToolContract(
            _args("fields", maxCount=NUMBER), result_kind="array"
        ),
    }
)

READ_TOOLS = frozenset(
    name for name, spec in TOOL_CONTRACTS.items() if not spec.mutating
)
WRITE_TOOLS = frozenset(name for name, spec in TOOL_CONTRACTS.items() if spec.mutating)
MEMORY_KEYS = frozenset(
    {
        "timezone",
        "workdays",
        "review_windows",
        "root_ids",
        "root_modes",
        "last_daily_close",
        "last_weekly",
    }
)
MEMORY_CONTRACTS: Mapping[str, tuple[type, ...]] = MappingProxyType(
    {
        "timezone": (str,),
        "workdays": (list,),
        "review_windows": (dict,),
        "root_ids": (list,),
        "root_modes": (dict,),
        "last_daily_close": (str,),
        "last_weekly": (str,),
    }
)


def validate_arguments(tool: str, arguments: Any) -> None:
    try:
        contract = TOOL_CONTRACTS[tool]
    except KeyError as exc:
        raise ValueError(f"unsupported tool: {tool}") from exc
    contract.validate(tool, arguments)


def validate_result(tool: str, result: Any) -> None:
    contract = TOOL_CONTRACTS[tool]
    if contract.result_kind == "array":
        if not isinstance(result, list) or any(
            not isinstance(item, dict) for item in result
        ):
            raise ValueError(f"{tool}: result must be object array")
    elif not isinstance(result, dict):
        raise ValueError(f"{tool}: result must be object")


def validate_memory_value(key: str, value: Any) -> None:
    try:
        expected = MEMORY_CONTRACTS[key]
    except KeyError as exc:
        raise ValueError(f"native memory key not allowed: {key}") from exc
    if not isinstance(value, expected):
        raise ValueError(f"native memory value has invalid type for {key}")  # noqa: TRY004 -- recorded data uses the ValueError rejection contract
