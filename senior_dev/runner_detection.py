"""Detect a project's test runner from filesystem signals.

The signal table mirrors references/testing.md so the skill's documented
runner-detection step has a programmatic counterpart.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

Signal = tuple[str, Callable[[Path], bool]]


def _has_pytest_section(root: Path) -> bool:
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        return False
    return "[tool.pytest" in pyproject.read_text(encoding="utf-8")


def _exists(name: str) -> Callable[[Path], bool]:
    return lambda root: (root / name).is_file()


# Order matters: more specific signals come first so they win when multiple
# ecosystems coexist in one repo (a Python service with a JS frontend, etc.).
_SIGNALS: list[Signal] = [
    ("pytest", _exists("pytest.ini")),
    ("pytest", _has_pytest_section),
    ("jest", _exists("jest.config.js")),
    ("jest", _exists("jest.config.ts")),
    ("go test", _exists("go.mod")),
    ("cargo test", _exists("Cargo.toml")),
]


def detect_runner(project_root: Path) -> str | None:
    """Return the name of the test runner this project uses, or None.

    Returns the first runner whose signal matches, scanning in declaration
    order so more specific signals (pytest.ini) outrank generic ones
    (package.json).
    """
    for runner, matches in _SIGNALS:
        if matches(project_root):
            return runner
    return None
