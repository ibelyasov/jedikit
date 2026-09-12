"""Fail-closed policy for current, versioned release evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from behavior import (
    EXPECTED_IDS,
    evidence_row_passes,
    has_secret,
    load_cases,
    read_jsonl,
    row_reasons,
    validate_row,
)

SCHEMA_VERSION = 1
REQUIRED_HOSTS = ("codex", "hermes")
REQUIRED_KINDS = ("install", "behavior", "provider")
REQUIRED_SKILLS = ("jedikit-tasks", "jedikit-habits")
EXPECTED_PROVIDERS = {
    "jedikit-tasks": "singularity",
    "jedikit-habits": "habitify",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_tree_digest() -> str:
    root = Path(__file__).resolve().parent.parent
    runtime_roots = [
        root / "skills",
        root / ".codex-plugin" / "plugin.json",
        root / ".claude-plugin" / "plugin.json",
        root / ".mcp.json",
        root / "packages" / "jedikit",
    ]
    hasher = hashlib.sha256()
    paths: list[Path] = []
    for runtime_root in runtime_roots:
        paths.extend(
            item
            for item in (
                runtime_root.rglob("*") if runtime_root.is_dir() else [runtime_root]
            )
            if item.is_file() and "__pycache__" not in item.parts
        )
    for path in sorted(paths):
        hasher.update(path.relative_to(root).as_posix().encode())
        hasher.update(b"\0")
        hasher.update(path.read_bytes())
        hasher.update(b"\0")
    return hasher.hexdigest()


def skill_digest(root: Path, skill: str) -> str:
    skill_root = root / "skills" / skill
    hasher = hashlib.sha256()
    for path in sorted(item for item in skill_root.rglob("*") if item.is_file()):
        hasher.update(path.relative_to(root).as_posix().encode())
        hasher.update(b"\0")
        hasher.update(path.read_bytes())
        hasher.update(b"\0")
    return hasher.hexdigest()


def product_version(root: Path) -> str:
    manifest = json.loads((root / ".codex-plugin" / "plugin.json").read_text())
    version = manifest.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError("release manifest has no version")
    return version


def evaluator_digest(root: Path) -> str:
    hasher = hashlib.sha256()
    for name in (
        "behavior.py",
        "contracts.py",
        "fake_mcp.py",
        "ledger.py",
        "release_policy.py",
    ):
        path = root / "evals" / name
        hasher.update(name.encode())
        hasher.update(b"\0")
        hasher.update(path.read_bytes())
        hasher.update(b"\0")
    return hasher.hexdigest()


def current_evidence_status(path: Path, phase: str) -> tuple[set[str], list[str]]:
    data = load_cases()
    case_map = {case["id"]: case for case in data["cases"]}
    passed: set[str] = set()
    stale: list[str] = []
    for index, row in enumerate(read_jsonl(path), 1):
        if row.get("phase") != phase:
            continue
        case_id = row.get("case_id")
        if case_id not in case_map:
            stale.append(f"row {index}: unknown case {case_id}")
            continue
        try:
            validate_row(data, case_map[case_id], row, index)
            reasons = row_reasons(data, case_map[case_id], row)
        except (TypeError, ValueError) as exc:
            stale.append(f"{case_id}: {exc}")
            continue
        ok = evidence_row_passes(phase, row, reasons)
        if ok:
            passed.add(case_id)
        else:
            stale.append(
                f"{case_id}: " + ("|".join(reasons) or "recorded failure mismatch")
            )
    return passed, stale


def validate_current_behavior(evidence_dir: Path, root: Path) -> list[str]:
    blockers: list[str] = []
    runtime_sha = runtime_tree_digest()
    expected_skill_sha = skill_digest(root, "jedikit-tasks")
    pairings: dict[str, dict[str, set[tuple[str, str, str, str]]]] = {
        "baseline": {},
        "green": {},
    }
    for phase in ("baseline", "green"):
        path = evidence_dir / f"{phase}.jsonl"
        if not path.is_file():
            blockers.append(f"current {phase} evidence missing: {path}")
            continue
        rows = read_jsonl(path)
        for index, row in enumerate(rows, 1):
            prefix = f"{phase} row {index}"
            if (
                type(row.get("evidence_schema_version")) is not int
                or row.get("evidence_schema_version") != SCHEMA_VERSION
            ):
                blockers.append(f"{prefix}: schema version must be {SCHEMA_VERSION}")
            if row.get("runtime_tree_sha256") != runtime_sha:
                blockers.append(f"{prefix}: stale runtime digest")
            if row.get("skill_sha256") != expected_skill_sha:
                blockers.append(f"{prefix}: stale jedikit-tasks digest")
            if row.get("evaluator_sha256") != evaluator_digest(root):
                blockers.append(f"{prefix}: stale evaluator digest")
            invocation = row.get("invocation")
            if not isinstance(invocation, str) or not invocation.strip():
                blockers.append(f"{prefix}: invocation is required")
            for field in ("host", "host_version", "model"):
                if not isinstance(row.get(field), str) or not row[field].strip():
                    blockers.append(f"{prefix}: {field} is required")
            expected_mode = "absent" if phase == "baseline" else "present"
            if row.get("skill_mode") != expected_mode:
                blockers.append(f"{prefix}: skill_mode must be {expected_mode}")
            experiment_id = row.get("experiment_id")
            if not isinstance(experiment_id, str) or not experiment_id.strip():
                blockers.append(f"{prefix}: experiment_id is required")
            elif all(
                isinstance(row.get(field), str)
                for field in ("host", "host_version", "model")
            ):
                key = (row["host"], row["host_version"], row["model"], experiment_id)
                pairings[phase].setdefault(str(row.get("case_id")), set()).add(key)
        passed, stale = current_evidence_status(path, phase)
        missing = sorted(EXPECTED_IDS - passed)
        print(f"current {phase} behavior: {len(passed)}/{len(EXPECTED_IDS)}")
        if missing:
            blockers.append(f"current {phase} missing/failing: {', '.join(missing)}")
        blockers.extend(f"current {phase} stale: {reason}" for reason in stale)
    for case_id in sorted(EXPECTED_IDS):
        if pairings["baseline"].get(case_id, set()) != pairings["green"].get(
            case_id, set()
        ):
            blockers.append(
                f"current pair mismatch: {case_id} host/model/version/experiment"
            )
    return blockers


def validate_smoke_row(
    row: dict[str, Any], index: int, evidence_dir: Path, root: Path
) -> tuple[str, str]:
    label = f"smoke row {index}"
    required_fields = {
        "schema_version",
        "status",
        "kind",
        "scenario",
        "identity",
        "runtime_tree_sha256",
        "skill_sha256",
        "invocation",
        "artifact",
    }
    if set(row) != required_fields:
        missing = sorted(required_fields - row.keys())
        extra = sorted(row.keys() - required_fields)
        raise ValueError(
            f"{label}: schema fields mismatch missing={missing} extra={extra}"
        )
    if (
        type(row.get("schema_version")) is not int
        or row.get("schema_version") != SCHEMA_VERSION
    ):
        raise ValueError(f"{label}: schema_version must be {SCHEMA_VERSION}")
    if row.get("status") != "passed":
        raise ValueError(f"{label}: status must equal passed")
    kind = row.get("kind")
    if kind not in REQUIRED_KINDS:
        raise ValueError(f"{label}: invalid kind {kind!r}")
    scenario = row.get("scenario")
    if not isinstance(scenario, str) or not scenario.strip():
        raise ValueError(f"{label}: scenario is required")
    identity = row.get("identity")
    if not isinstance(identity, dict):
        raise ValueError(f"{label}: identity must be object")  # noqa: TRY004 -- recorded data uses the ValueError rejection contract
    required_identity = {"host", "host_version", "model", "product_version", "skill"}
    if set(identity) != required_identity or any(
        not isinstance(identity[field], str) or not identity[field].strip()
        for field in required_identity
    ):
        raise ValueError(f"{label}: identity fields must be exact non-empty strings")
    host = identity["host"]
    if host not in REQUIRED_HOSTS:
        raise ValueError(f"{label}: unsupported host {host!r}")
    if identity["product_version"] != product_version(root):
        raise ValueError(f"{label}: product version mismatch")
    if identity["skill"] not in REQUIRED_SKILLS:
        raise ValueError(f"{label}: unknown skill")
    if row.get("runtime_tree_sha256") != runtime_tree_digest():
        raise ValueError(f"{label}: stale runtime digest")
    if row.get("skill_sha256") != skill_digest(root, identity["skill"]):
        raise ValueError(f"{label}: stale skill digest")
    invocation = row.get("invocation")
    if not isinstance(invocation, str) or not invocation.strip():
        raise ValueError(f"{label}: invocation is required")
    artifact = row.get("artifact")
    if not isinstance(artifact, dict) or set(artifact) != {"path", "sha256"}:
        raise ValueError(f"{label}: artifact requires exact path and sha256")
    if not isinstance(artifact["path"], str) or not artifact["path"]:
        raise ValueError(f"{label}: artifact path must be non-empty string")
    if not isinstance(artifact["sha256"], str) or len(artifact["sha256"]) != 64:
        raise ValueError(f"{label}: artifact sha256 must be 64-char string")
    artifact_path = Path(artifact["path"])
    if not artifact_path.is_absolute():
        artifact_path = (evidence_dir / artifact_path).resolve()
        try:
            artifact_path.relative_to(evidence_dir.resolve())
        except ValueError as exc:
            raise ValueError(
                f"{label}: artifact path escapes evidence directory"
            ) from exc
    if not artifact_path.is_file():
        raise ValueError(f"{label}: retained artifact missing: {artifact_path}")
    if artifact.get("sha256") != _sha256(artifact_path):
        raise ValueError(f"{label}: retained artifact checksum mismatch")
    try:
        retained = json.loads(artifact_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label}: retained artifact must be versioned JSON") from exc
    if has_secret(retained):
        raise ValueError(f"{label}: secret-like value detected in retained artifact")
    validate_retained_artifact(retained, row, label)
    return host, f"{kind}/{identity['skill']}"


def _string_list(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def validate_retained_artifact(
    retained: Any, row: dict[str, Any], label: str = "smoke row"
) -> None:
    shared = {
        "schema_version",
        "status",
        "kind",
        "scenario",
        "identity",
        "runtime_tree_sha256",
        "skill_sha256",
        "invocation",
        "observed",
    }
    if not isinstance(retained, dict) or set(retained) != shared:
        raise ValueError(f"{label}: retained artifact schema fields mismatch")
    if type(retained["schema_version"]) is not int:
        raise ValueError(f"{label}: retained artifact schema_version must be integer")
    for field in shared - {"observed"}:
        if retained[field] != row[field]:
            raise ValueError(f"{label}: retained artifact binding mismatch: {field}")
    observed = retained["observed"]
    if not isinstance(observed, dict):
        raise ValueError(f"{label}: retained observed result must be object")  # noqa: TRY004 -- recorded data uses the ValueError rejection contract
    kind = row["kind"]
    skill = row["identity"]["skill"]
    if kind == "install":
        required = {"product_version", "discovered_skills", "loadable_skills"}
        if set(observed) != required:
            raise ValueError(f"{label}: install observation schema mismatch")
        if observed["product_version"] != row["identity"]["product_version"]:
            raise ValueError(f"{label}: install product version mismatch")
        if not _string_list(observed["discovered_skills"]) or not _string_list(
            observed["loadable_skills"]
        ):
            raise ValueError(f"{label}: install skill observations must be nonempty")
        if (
            skill not in observed["discovered_skills"]
            or skill not in observed["loadable_skills"]
        ):
            raise ValueError(f"{label}: target skill was not discovered and loadable")
    elif kind == "provider":
        required = {
            "provider",
            "metadata_only",
            "initialize",
            "auth",
            "discovered_tools",
            "writes",
        }
        if set(observed) != required:
            raise ValueError(f"{label}: provider observation schema mismatch")
        if observed["provider"] != EXPECTED_PROVIDERS[skill]:
            raise ValueError(f"{label}: provider does not match target skill")
        if (
            observed["metadata_only"] is not True
            or observed["initialize"] != "passed"
            or observed["auth"] != "passed"
            or type(observed["writes"]) is not int
            or observed["writes"] != 0
            or not _string_list(observed["discovered_tools"])
        ):
            raise ValueError(
                f"{label}: provider metadata connection/discovery did not pass"
            )
    elif kind == "behavior":
        required = {"response", "calls", "assertions", "review"}
        if set(observed) != required:
            raise ValueError(f"{label}: behavior observation schema mismatch")
        review = observed["review"]
        if (
            not isinstance(observed["response"], str)
            or not observed["response"].strip()
            or not _string_list(observed["calls"], allow_empty=True)
            or not _string_list(observed["assertions"])
            or not isinstance(review, dict)
            or set(review) != {"reviewer", "verdict", "checks"}
            or not isinstance(review["reviewer"], str)
            or not review["reviewer"].strip()
            or review["verdict"] != "passed"
            or not _string_list(review["checks"])
        ):
            raise ValueError(f"{label}: behavior response/review did not pass")


def validate_smokes(evidence_dir: Path, root: Path) -> list[str]:
    path = evidence_dir / "smoke.jsonl"
    if not path.is_file():
        return [f"current smoke evidence missing: {path}"]
    matrix: set[tuple[str, str]] = set()
    blockers: list[str] = []
    for index, row in enumerate(read_jsonl(path), 1):
        try:
            key = validate_smoke_row(row, index, evidence_dir, root)
        except (OSError, TypeError, ValueError) as exc:
            blockers.append(str(exc))
            continue
        if key in matrix:
            blockers.append(f"duplicate current smoke: {key[0]}/{key[1]}")
        matrix.add(key)
    print("current release matrix:")
    for host in REQUIRED_HOSTS:
        values = [
            f"{kind}/{skill}={'passed' if (host, f'{kind}/{skill}') in matrix else 'missing'}"
            for kind in REQUIRED_KINDS
            for skill in REQUIRED_SKILLS
        ]
        print(f"  {host}: " + ", ".join(values))
    expected = {
        (host, f"{kind}/{skill}")
        for host in REQUIRED_HOSTS
        for kind in REQUIRED_KINDS
        for skill in REQUIRED_SKILLS
    }
    for host, kind_skill in sorted(expected - matrix):
        blockers.append(f"current smoke missing: {host}/{kind_skill}")
    print(
        "scope: retained contracts bind install/loadability, metadata-only provider "
        "connection/discovery, and reviewed behavior; they do not authenticate provenance"
    )
    return blockers


def release_gate(evidence_dir: Path, root: Path) -> None:
    blockers = validate_current_behavior(evidence_dir, root)
    blockers.extend(validate_smokes(evidence_dir, root))
    if blockers:
        raise ValueError("release blocked — " + " || ".join(blockers))
    print("release gate: passed")
