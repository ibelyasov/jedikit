"""Offline package-drift checks used by the evaluator CLI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def check_package(root: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "build.py"), "--check"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ValueError(f"package check failed: {detail}")
    print(result.stdout.strip())
