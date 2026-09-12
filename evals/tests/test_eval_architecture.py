from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

EVALS = Path(__file__).resolve().parents[1]
REPO = EVALS.parent
sys.path.insert(0, str(EVALS))

from contracts import MEMORY_KEYS, TOOL_CONTRACTS, validate_arguments
from fake_mcp import FakeSingularity, load_fixture
from ledger import replay_ledger
from release_policy import (
    product_version,
    runtime_tree_digest,
    skill_digest,
    validate_smoke_row,
)


def scored_row(
    case: dict[str, object], fake: FakeSingularity, timeline=None
) -> dict[str, object]:
    return {
        "phase": "green",
        "events": case["expected_events"],
        "tool_intents": list(dict.fromkeys(entry["tool"] for entry in fake.ledger)),
        "tool_ledger": fake.ledger,
        "approval_timeline": timeline or [],
        "fake_mode": "read-only" if fake.read_only else "read-write",
        "rubric_pass": True,
    }


class ContractTests(unittest.TestCase):
    def test_discovery_schema_and_runtime_validation_share_types(self) -> None:
        fake = FakeSingularity(load_fixture("R5"))
        discovered = {tool["name"]: tool["inputSchema"] for tool in fake.tools()}
        for name, contract in TOOL_CONTRACTS.items():
            self.assertEqual(discovered[name], contract.input_schema())
            self.assertFalse(discovered[name]["additionalProperties"])
            for property_schema in discovered[name]["properties"].values():
                self.assertIn(property_schema["type"], {"string", "boolean", "number"})
        for bad in (None, [], False, ""):
            with self.assertRaises(TypeError):
                validate_arguments("project_list", bad)
            with self.assertRaises(TypeError):
                fake.call("project_list", bad)  # type: ignore[arg-type]

    def test_memory_keys_have_one_definition(self) -> None:
        fake = FakeSingularity(load_fixture("R9"))
        self.assertEqual(set(fake.memory_show()), set(fake.memory) & set(MEMORY_KEYS))
        with self.assertRaises(ValueError):
            fake.memory_set("task_content", "forbidden")
        with self.assertRaises(ValueError):
            fake.memory_set("workdays", "Monday")


class ReplayTests(unittest.TestCase):
    def _row(self) -> dict[str, object]:
        fake = FakeSingularity(load_fixture("S1"))
        created = fake.call("task_create", {"title": "Позвонить стоматологу"})
        fake.call("task_get", {"id": created["id"]})
        return {"fake_mode": "read-write", "tool_ledger": fake.ledger}

    def test_replays_stateful_write_and_readback(self) -> None:
        report = replay_ledger("S1", self._row())
        self.assertEqual(report.tasks[-1]["id"], "t-fake-1")

    def test_rejects_wrong_id_readback_and_tampered_result(self) -> None:
        wrong_id = self._row()
        wrong_id["tool_ledger"][-1]["arguments"]["id"] = "t-wrong"  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "replay=task_get"):
            replay_ledger("S1", wrong_id)
        tampered = self._row()
        tampered["tool_ledger"][-1]["result"]["title"] = "forged"  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "replay_result=task_get"):
            replay_ledger("S1", tampered)

    def test_unrelated_valid_readback_does_not_verify_write(self) -> None:
        import behavior

        data = behavior.load_cases()
        case = next(item for item in data["cases"] if item["id"] == "M9")
        fake = FakeSingularity(load_fixture("M9"))
        fake.call("project_create", {"title": "Личный сайт опубликован"})
        fake.call("task_get", {"id": "t-project-raw"})
        row = {
            "phase": "green",
            "events": case["expected_events"],
            "tool_intents": [entry["tool"] for entry in fake.ledger],
            "tool_ledger": fake.ledger,
            "approval_timeline": [],
            "fake_mode": "read-write",
            "rubric_pass": True,
        }
        self.assertIn("missing:verify_write", behavior.validate_ledger(case, row))

    def test_rejects_tampered_mutation_error_and_memory(self) -> None:
        mutation = self._row()
        mutation["tool_ledger"][0]["result"]["id"] = "forged"  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "replay_result=task_create"):
            replay_ledger("S1", mutation)

        failure = FakeSingularity(load_fixture("S2"))
        failure.call("task_create", {"title": "A"})
        with self.assertRaises(RuntimeError):
            failure.call("task_create", {"title": "B"})
        row = {"fake_mode": "read-write", "tool_ledger": copy.deepcopy(failure.ledger)}
        row["tool_ledger"][-1]["result"]["error"] = "forged"
        with self.assertRaisesRegex(ValueError, "replay_result=task_create"):
            replay_ledger("S2", row)

        memory = FakeSingularity(load_fixture("R7"))
        memory.memory_set("last_weekly", "2026-08-09T12:00:00+03:00")
        row = {"fake_mode": "read-write", "tool_ledger": copy.deepcopy(memory.ledger)}
        row["tool_ledger"][0]["result"]["value"] = "stale"
        with self.assertRaisesRegex(ValueError, "replay_result=native_memory_set"):
            replay_ledger("R7", row)


class BehaviorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import behavior

        cls.behavior = behavior
        cls.data = behavior.load_cases()
        cls.cases = {case["id"]: case for case in cls.data["cases"]}

    def assert_case(self, case_id: str, fake: FakeSingularity, timeline=None) -> None:
        reasons = self.behavior.row_reasons(
            self.data,
            self.cases[case_id],
            scored_row(self.cases[case_id], fake, timeline),
        )
        self.assertEqual(reasons, [])

    def test_baseline_requires_a_real_exact_red_failure(self) -> None:
        case = self.cases["M1"]
        nondiscriminating = {
            "phase": "baseline",
            "events": case["expected_events"],
            "tool_intents": [],
            "tool_ledger": [],
            "approval_timeline": [],
            "fake_mode": "not-executed",
            "rubric_pass": False,
            "failure_reasons": [],
        }
        reasons = self.behavior.row_reasons(self.data, case, nondiscriminating)
        self.assertEqual(reasons, [])
        self.assertFalse(
            self.behavior.evidence_row_passes("baseline", nondiscriminating, reasons)
        )

        discriminating = copy.deepcopy(nondiscriminating)
        discriminating["events"] = []
        reasons = self.behavior.row_reasons(self.data, case, discriminating)
        discriminating["failure_reasons"] = reasons
        self.assertTrue(
            self.behavior.evidence_row_passes("baseline", discriminating, reasons)
        )
        discriminating["failure_reasons"] = reasons + ["invented failure"]
        self.assertFalse(
            self.behavior.evidence_row_passes("baseline", discriminating, reasons)
        )

    def test_project_reuse_abandon_and_setup_contracts(self) -> None:
        m9 = FakeSingularity(load_fixture("M9"))
        m9.record_tools_list(order=1)
        m9.call("task_get", {"id": "t-project-raw"}, order=2)
        project = m9.call(
            "project_create", {"title": "Личный сайт опубликован"}, order=5
        )
        m9.call(
            "task_update",
            {
                "id": "t-project-raw",
                "title": "Определить следующий шаг для проекта Личный сайт опубликован",
            },
            order=6,
        )
        m9.call(
            "task_move", {"id": "t-project-raw", "projectId": project["id"]}, order=7
        )
        m9.call("task_get", {"id": "t-project-raw"}, order=8)
        m9.call("project_get", {"id": project["id"]}, order=9)
        m9_timeline = [
            {"event": "preview", "order": 3},
            {"event": "confirmation", "order": 4, "accepted": True},
        ]
        m9_row = scored_row(self.cases["M9"], m9, m9_timeline)
        self.assertEqual(
            self.behavior.row_reasons(self.data, self.cases["M9"], m9_row), []
        )
        duplicate = copy.deepcopy(m9_row)
        duplicate["tool_intents"].append("task_create")
        self.assertIn(
            "invalid:M9_reuse_sequence",
            self.behavior.row_reasons(self.data, self.cases["M9"], duplicate),
        )

        m11 = FakeSingularity(load_fixture("M11"))
        m11.record_tools_list(order=1)
        m11.call("project_get", {"id": "p-abandon"}, order=2)
        m11.call("task_list", {"projectId": "p-abandon"}, order=3)
        m11.call(
            "project_update",
            {
                "id": "p-abandon",
                "note": "Результат больше не нужен\nПричина отказа: изменился рынок",
            },
            order=6,
        )
        m11.call("task_move", {"id": "t-move", "projectId": "p-other"}, order=7)
        m11.call("task_cancel", {"id": "t-cancel"}, order=8)
        m11.call("project_archive", {"id": "p-abandon"}, order=9)
        m11.call("project_get", {"id": "p-abandon"}, order=10)
        m11.call("task_get", {"id": "t-move"}, order=11)
        m11.call("task_get", {"id": "t-cancel"}, order=12)
        self.assert_case(
            "M11",
            m11,
            [
                {"event": "preview", "order": 4},
                {"event": "confirmation", "order": 5, "accepted": True},
            ],
        )

        m12 = FakeSingularity(load_fixture("M12"), read_only=True)
        m12.record_tools_list(order=1)
        m12.call("project_list", {}, order=2)
        m12.call("task_list", {}, order=3)
        self.assert_case("M12", m12)

    def test_manual_transfer_scheduled_privacy_and_capabilities(self) -> None:
        m10 = FakeSingularity(load_fixture("M10"), read_only=True)
        m10.record_tools_list(order=1)
        m10.call("task_list_inbox", {}, order=2)
        m10.call("task_get", {"id": "t-idea-raw"}, order=3)
        self.assert_case("M10", m10)

        s4 = FakeSingularity(load_fixture("S4"), read_only=True)
        s4.record_tools_list(order=1)
        s4.call(
            "task_list_today",
            {"timezone": "Europe/Moscow", "fields": "projectId"},
            order=2,
        )
        s4.call(
            "task_list_overdue",
            {"timezone": "Europe/Moscow", "fields": "projectId"},
            order=3,
        )
        s4_row = scored_row(self.cases["S4"], s4)
        self.assertEqual(
            self.behavior.row_reasons(self.data, self.cases["S4"], s4_row), []
        )
        leaked = copy.deepcopy(s4_row)
        leaked["tool_ledger"][1]["result"][0]["title"] = "leak"
        self.assertIn(
            "invalid:replay_result=task_list_today@2",
            self.behavior.row_reasons(self.data, self.cases["S4"], leaked),
        )
        invalid_result = copy.deepcopy(s4_row)
        invalid_result["tool_ledger"][1]["result"] = None
        self.assertIn(
            "invalid:result_schema=task_list_today",
            self.behavior.row_reasons(self.data, self.cases["S4"], invalid_result),
        )

        extra = FakeSingularity(load_fixture("S4"), read_only=True)
        extra.record_tools_list(order=1)
        extra.call(
            "task_list_today",
            {"timezone": "Europe/Moscow", "fields": "projectId"},
            order=2,
        )
        extra.call(
            "task_list_overdue",
            {"timezone": "Europe/Moscow", "fields": "projectId"},
            order=3,
        )
        extra.call("task_list", {}, order=4)
        extra_row = scored_row(self.cases["S4"], extra)
        self.assertIn(
            "forbidden:S4_extra_read",
            self.behavior.row_reasons(self.data, self.cases["S4"], extra_row),
        )

        s10 = FakeSingularity(load_fixture("S10"), read_only=True)
        s10.record_tools_list(order=1)
        s10.call("project_list", {}, order=2)
        self.assert_case("S10", s10)

    def test_memory_read_forget_and_reset_contracts(self) -> None:
        r9 = FakeSingularity(load_fixture("R9"))
        r9.memory_read(order=1)
        self.assert_case("R9", r9)

        r10 = FakeSingularity(load_fixture("R10"))
        r10.memory_delete("timezone", order=3)
        timeline = [
            {"event": "preview", "order": 1},
            {"event": "confirmation", "order": 2, "accepted": True},
        ]
        self.assert_case("R10", r10, timeline)

        r11 = FakeSingularity(load_fixture("R11"))
        for order, key in enumerate(sorted(r11.memory_show()), 3):
            r11.memory_delete(key, order=order)
        self.assert_case("R11", r11, timeline)

    def test_partial_failure_confirmation_and_weekly_timestamp_order(self) -> None:
        s2 = FakeSingularity(load_fixture("S2"))
        s2.call("task_create", {"title": "A"}, order=3)
        with self.assertRaises(RuntimeError):
            s2.call("task_create", {"title": "B"}, order=4)
        s2.call("task_get", {"id": "t-fake-1"}, order=5)
        timeline = [
            {"event": "preview", "order": 1},
            {"event": "confirmation", "order": 2, "accepted": True},
        ]
        s2_row = scored_row(self.cases["S2"], s2, timeline)
        self.assertEqual(
            self.behavior.row_reasons(self.data, self.cases["S2"], s2_row), []
        )
        early = copy.deepcopy(s2_row)
        early["approval_timeline"][1]["order"] = 5
        self.assertIn(
            "forbidden:write_before_confirmation",
            self.behavior.row_reasons(self.data, self.cases["S2"], early),
        )

        r7 = FakeSingularity(load_fixture("R7"))
        r7.memory_set("last_weekly", self.data["now"], order=2)
        confirmation = [{"event": "confirmation", "order": 1, "accepted": True}]
        r7_row = scored_row(self.cases["R7"], r7, confirmation)
        self.assertEqual(
            self.behavior.row_reasons(self.data, self.cases["R7"], r7_row), []
        )
        for field in ("arguments", "result"):
            tampered = copy.deepcopy(r7_row)
            tampered["tool_ledger"][0][field]["value"] = "stale"
            self.assertIn(
                "invalid:replay_result=native_memory_set@1",
                self.behavior.row_reasons(self.data, self.cases["R7"], tampered),
            )
        late = copy.deepcopy(r7_row)
        late["approval_timeline"][0]["order"] = 2
        self.assertIn(
            "missing:R7_timestamp_ledger",
            self.behavior.row_reasons(self.data, self.cases["R7"], late),
        )

    def test_touched_project_is_derived_from_runtime_reads(self) -> None:
        r4 = FakeSingularity(load_fixture("R4"))
        r4.record_tools_list(order=1)
        r4.call("task_list", {"modifiedSince": "2026-08-09T00:00:00+03:00"}, order=2)
        r4.call("task_list_today", {"timezone": "Europe/Moscow"}, order=3)
        r4.call("task_list_overdue", {"timezone": "Europe/Moscow"}, order=4)
        r4.call("project_get", {"id": "p-touched"}, order=5)
        r4.call("task_list", {"projectId": "p-touched"}, order=6)
        self.assert_case("R4", r4)


class SmokePolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.evidence = Path(self.temp.name)
        self.artifact = self.evidence / "session.json"
        self.artifact.write_text("{}\n")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def row(
        self, kind: str = "behavior", skill: str = "jedikit-tasks"
    ) -> dict[str, object]:
        row: dict[str, object] = {
            "schema_version": 1,
            "status": "passed",
            "kind": kind,
            "scenario": f"explicit {skill} {kind} smoke",
            "identity": {
                "host": "codex",
                "host_version": "codex 1.0",
                "model": "gpt-test",
                "product_version": product_version(REPO),
                "skill": skill,
            },
            "runtime_tree_sha256": runtime_tree_digest(),
            "skill_sha256": skill_digest(REPO, skill),
            "invocation": "codex exec explicit skill invocation",
            "artifact": {
                "path": self.artifact.name,
                "sha256": "",
            },
        }
        observed = {
            "behavior": {
                "response": "Reviewed response",
                "calls": [],
                "assertions": ["scenario invariant observed"],
                "review": {
                    "reviewer": "independent-reviewer-1",
                    "verdict": "passed",
                    "checks": ["response and execution checked"],
                },
            },
            "install": {
                "product_version": product_version(REPO),
                "discovered_skills": [skill],
                "loadable_skills": [skill],
            },
            "provider": {
                "provider": "singularity" if skill == "jedikit-tasks" else "habitify",
                "metadata_only": True,
                "initialize": "passed",
                "auth": "passed",
                "discovered_tools": [
                    "task_list" if skill == "jedikit-tasks" else "habit_list"
                ],
                "writes": 0,
            },
        }[kind]
        retained = {key: value for key, value in row.items() if key != "artifact"}
        retained["observed"] = observed
        self.write_artifact(row, retained)
        return row

    def write_artifact(self, row: dict[str, object], content: object) -> None:
        self.artifact.write_text(json.dumps(content) + "\n")
        row["artifact"]["sha256"] = hashlib.sha256(
            self.artifact.read_bytes()
        ).hexdigest()  # type: ignore[index]

    def test_strict_status_stale_runtime_and_artifact_tamper(self) -> None:
        self.assertEqual(
            validate_smoke_row(self.row(), 1, self.evidence, REPO),
            ("codex", "behavior/jedikit-tasks"),
        )
        row = self.row()
        row["status"] = "passed_but_not_really"
        with self.assertRaisesRegex(ValueError, "status must equal passed"):
            validate_smoke_row(row, 1, self.evidence, REPO)
        row = self.row()
        row["runtime_tree_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "stale runtime"):
            validate_smoke_row(row, 1, self.evidence, REPO)
        row = self.row()
        self.artifact.write_text("tampered")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            validate_smoke_row(row, 1, self.evidence, REPO)

    def test_valid_kind_specific_retained_artifacts(self) -> None:
        for kind in ("install", "behavior", "provider"):
            with self.subTest(kind=kind):
                row = self.row(kind)
                self.assertEqual(
                    validate_smoke_row(row, 1, self.evidence, REPO),
                    ("codex", f"{kind}/jedikit-tasks"),
                )

    def test_boolean_is_not_an_integer_schema_field(self) -> None:
        row = self.row()
        row["schema_version"] = True
        with self.assertRaisesRegex(ValueError, "schema_version"):
            validate_smoke_row(row, 1, self.evidence, REPO)

        row = self.row()
        retained = json.loads(self.artifact.read_text())
        retained["schema_version"] = True
        self.write_artifact(row, retained)
        with self.assertRaisesRegex(ValueError, "schema_version"):
            validate_smoke_row(row, 1, self.evidence, REPO)

        row = self.row("provider")
        retained = json.loads(self.artifact.read_text())
        retained["observed"]["writes"] = False
        self.write_artifact(row, retained)
        with self.assertRaisesRegex(ValueError, "connection/discovery"):
            validate_smoke_row(row, 1, self.evidence, REPO)

    def test_rejects_opaque_unbound_and_secret_retained_content(self) -> None:
        row = self.row()
        self.artifact.write_bytes(b"opaque bytes")
        row["artifact"]["sha256"] = hashlib.sha256(
            self.artifact.read_bytes()
        ).hexdigest()  # type: ignore[index]
        with self.assertRaisesRegex(ValueError, "versioned JSON"):
            validate_smoke_row(row, 1, self.evidence, REPO)

        row = self.row()
        self.write_artifact(row, {"retained": True})
        with self.assertRaisesRegex(ValueError, "schema fields mismatch"):
            validate_smoke_row(row, 1, self.evidence, REPO)

        for field, value in (
            ("identity", {"host": "other"}),
            ("runtime_tree_sha256", "0" * 64),
            ("kind", "install"),
        ):
            with self.subTest(field=field):
                row = self.row()
                retained = json.loads(self.artifact.read_text())
                retained[field] = value
                self.write_artifact(row, retained)
                with self.assertRaisesRegex(ValueError, "binding mismatch"):
                    validate_smoke_row(row, 1, self.evidence, REPO)

        row = self.row()
        retained = json.loads(self.artifact.read_text())
        retained["observed"]["response"] = "bearer abcdefghijklmnopqrstuvwxyz"
        self.write_artifact(row, retained)
        with self.assertRaisesRegex(ValueError, "secret-like"):
            validate_smoke_row(row, 1, self.evidence, REPO)

    def test_rejects_kind_specific_observation_mismatch(self) -> None:
        row = self.row("install")
        retained = json.loads(self.artifact.read_text())
        retained["observed"]["loadable_skills"] = ["jedikit-habits"]
        self.write_artifact(row, retained)
        with self.assertRaisesRegex(ValueError, "target skill"):
            validate_smoke_row(row, 1, self.evidence, REPO)

        row = self.row("provider", "jedikit-habits")
        retained = json.loads(self.artifact.read_text())
        retained["observed"]["provider"] = "singularity"
        self.write_artifact(row, retained)
        with self.assertRaisesRegex(ValueError, "provider does not match"):
            validate_smoke_row(row, 1, self.evidence, REPO)

        row = self.row("behavior")
        retained = json.loads(self.artifact.read_text())
        retained["observed"]["review"]["verdict"] = "passed-ish"
        self.write_artifact(row, retained)
        with self.assertRaisesRegex(ValueError, "behavior response/review"):
            validate_smoke_row(row, 1, self.evidence, REPO)


class PublicEntryTests(unittest.TestCase):
    def test_run_validate_public_entry(self) -> None:
        result = subprocess.run(
            [sys.executable, str(EVALS / "run.py"), "validate"],
            check=False,
            cwd=REPO,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("cases: 33 valid", result.stdout)

    def test_fake_stdio(self) -> None:
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "project_list", "arguments": {}},
            },
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "project_list", "arguments": None},
            },
        ]
        result = subprocess.run(
            [sys.executable, str(EVALS / "fake_mcp.py"), "--stdio", "--case", "S1"],
            check=False,
            cwd=REPO,
            input="".join(json.dumps(item) + "\n" for item in requests),
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        responses = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual([item["id"] for item in responses], [1, 2, 3, 4])
        self.assertTrue(responses[1]["result"]["tools"])
        payload = json.loads(responses[2]["result"]["content"][0]["text"])
        self.assertEqual(payload[0]["id"], "p-work")
        self.assertIn("arguments must be object", responses[3]["error"]["message"])


if __name__ == "__main__":
    unittest.main()
