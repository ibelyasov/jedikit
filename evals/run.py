#!/usr/bin/env python3
"""Offline evaluator and fail-closed release evidence gate."""

from __future__ import annotations

import argparse
import sys
import unittest
from collections import Counter
from pathlib import Path

import behavior
from fake_mcp import self_test as fake_self_test
from package_check import check_package
from release_policy import release_gate

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent


def run_regressions() -> None:
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        raise ValueError("evaluator regression tests failed")


def check() -> None:
    behavior.validate_cases()
    fake_self_test()
    behavior.self_test()
    run_regressions()
    check_package(REPO)
    print("eval check: passed")


def inspect_history(paths: list[Path]) -> None:
    for path in paths:
        rows = behavior.read_jsonl(path)
        phases = Counter(str(row.get("phase", "smoke")) for row in rows)
        hosts = sorted({str(row.get("host", "unknown")) for row in rows})
        print(f"{path}: rows={len(rows)} phases={dict(phases)} hosts={','.join(hosts)}")
    print("history: inspection only; rows are not current release evidence")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    subparsers.add_parser("self-test")
    subparsers.add_parser("check")
    gate = subparsers.add_parser("release-gate")
    gate.add_argument("--evidence-dir", type=Path, default=ROOT / "current")
    score = subparsers.add_parser("score")
    score.add_argument("path", type=Path)
    score.add_argument("--phase", choices=("baseline", "green"), required=True)
    score.add_argument("--cases")
    history = subparsers.add_parser("history")
    history.add_argument("paths", type=Path, nargs="*")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        if args.command == "validate":
            behavior.validate_cases()
        elif args.command == "self-test":
            behavior.self_test()
        elif args.command == "check":
            check()
        elif args.command == "release-gate":
            check()
            release_gate(args.evidence_dir.resolve(), REPO)
        elif args.command == "history":
            paths = args.paths or [
                ROOT / "evidence" / "baseline.jsonl",
                ROOT / "evidence" / "green.jsonl",
                ROOT / "evidence" / "host-smoke.jsonl",
            ]
            inspect_history(paths)
        else:
            behavior.score(args.path, args.phase, behavior.parse_selected(args.cases))
    except (OSError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
