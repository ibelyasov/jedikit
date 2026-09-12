"""Deterministic replay of recorded provider and host-memory ledgers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from contracts import MEMORY_KEYS, TOOL_CONTRACTS, validate_result
from fake_mcp import FakeSingularity, load_fixture


@dataclass(frozen=True)
class ReplayReport:
    state_sha256: str
    projects: list[dict[str, Any]]
    tasks: list[dict[str, Any]]
    memory: dict[str, Any] | None


def replay_ledger(case_id: str, row: dict[str, Any]) -> ReplayReport:
    ledger = row.get("tool_ledger")
    if not isinstance(ledger, list):
        raise ValueError("invalid:tool_ledger")  # noqa: TRY004 -- recorded data uses the ValueError rejection contract
    fake = FakeSingularity(
        load_fixture(case_id), read_only=row.get("fake_mode") == "read-only"
    )
    required = {"seq", "order", "tool", "arguments", "result", "mutating"}
    previous_order = -1
    for index, observed in enumerate(ledger, 1):
        if not isinstance(observed, dict) or required - observed.keys():
            raise ValueError(f"invalid:tool_ledger_entry={index}")
        if observed["seq"] != index or not isinstance(observed["order"], int):
            raise ValueError(f"invalid:tool_ledger_order={index}")
        if observed["order"] <= previous_order:
            raise ValueError(f"invalid:tool_ledger_order={index}")
        previous_order = observed["order"]
        tool = observed["tool"]
        try:
            if tool == "tools_list":
                if observed["arguments"] != {}:
                    raise ValueError("tools_list arguments must be empty")
                fake.record_tools_list(order=observed["order"])
            elif tool == "native_memory_set":
                args = observed["arguments"]
                if not isinstance(args, dict) or set(args) != {"key", "value"}:
                    raise ValueError("native_memory_set arguments")
                if args["key"] not in MEMORY_KEYS:
                    raise ValueError("native_memory_set key")
                fake.memory_set(args["key"], args["value"], order=observed["order"])
            elif tool == "native_memory_delete":
                args = observed["arguments"]
                if not isinstance(args, dict) or set(args) != {"key"}:
                    raise ValueError("native_memory_delete arguments")
                if args["key"] not in MEMORY_KEYS:
                    raise ValueError("native_memory_delete key")
                fake.memory_delete(args["key"], order=observed["order"])
            elif tool == "native_memory_read":
                if observed["arguments"] != {}:
                    raise ValueError("native_memory_read arguments")
                fake.memory_read(order=observed["order"])
            elif tool in TOOL_CONTRACTS:
                fake.call(tool, observed["arguments"], order=observed["order"])
            else:
                raise ValueError(f"unknown tool {tool}")
        except RuntimeError:
            # Injected provider failures are part of the fixture and are recorded
            # before FakeSingularity raises. Other exceptions mean replay failed.
            if len(fake.ledger) != index:
                raise
        except (KeyError, PermissionError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid:replay={tool}:{exc}") from exc

        actual = fake.ledger[-1]
        if actual["result"] != observed["result"]:
            raise ValueError(f"invalid:replay_result={tool}@{index}")
        if actual["mutating"] != observed["mutating"]:
            raise ValueError(f"invalid:mutating_flag={tool}@{index}")
        if tool in TOOL_CONTRACTS and "error" not in actual["result"]:
            try:
                validate_result(tool, actual["result"])
            except ValueError as exc:
                raise ValueError(f"invalid:result_schema={exc}") from exc

    return ReplayReport(
        state_sha256=fake.snapshot_digest(),
        projects=fake.projects,
        tasks=fake.tasks,
        memory=fake.memory_show() if fake.memory_available else None,
    )
