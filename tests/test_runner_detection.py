"""TDD-driven test runner detection.

This module is built test-first as a live demonstration of the
senior-developer skill's RED → GREEN → REFACTOR protocol. The runner
table here matches the one in references/testing.md.
"""
from pathlib import Path

import pytest

from senior_dev.runner_detection import detect_runner


def test_empty_directory_has_no_runner(tmp_path: Path):
    assert detect_runner(tmp_path) is None


def test_pytest_ini_detected_as_pytest(tmp_path: Path):
    (tmp_path / "pytest.ini").write_text("[pytest]\n")
    assert detect_runner(tmp_path) == "pytest"


def test_jest_config_detected_as_jest(tmp_path: Path):
    (tmp_path / "jest.config.js").write_text("module.exports = {};")
    assert detect_runner(tmp_path) == "jest"


def test_go_mod_detected_as_go_test(tmp_path: Path):
    (tmp_path / "go.mod").write_text("module example.com/x\n")
    assert detect_runner(tmp_path) == "go test"


def test_cargo_toml_detected_as_cargo_test(tmp_path: Path):
    (tmp_path / "Cargo.toml").write_text("[package]\nname = 'x'\n")
    assert detect_runner(tmp_path) == "cargo test"


def test_pyproject_with_pytest_section_detected_as_pytest(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        "[tool.pytest.ini_options]\nminversion = '6.0'\n"
    )
    assert detect_runner(tmp_path) == "pytest"


def test_pyproject_without_pytest_section_is_not_pytest(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    assert detect_runner(tmp_path) is None


def test_pytest_ini_wins_over_package_json(tmp_path: Path):
    """If both Python and JS signals are present, the more specific signal
    (pytest.ini explicitly configures pytest) takes precedence."""
    (tmp_path / "pytest.ini").write_text("[pytest]\n")
    (tmp_path / "package.json").write_text('{"name": "x"}')
    assert detect_runner(tmp_path) == "pytest"
