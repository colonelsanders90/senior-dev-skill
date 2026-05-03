"""Integrity tests for the senior-developer skill.

These tests programmatically verify the structural claims about the skill:
- paths advertised in SKILL.md actually exist
- the .skill bundle is in sync with the source files
- the TDD enforcement and runner-detection content is present
- the frontmatter is parseable and complete

If any of these regress, the skill is silently broken (which is exactly
what happened before this branch landed: SKILL.md pointed at references/
that didn't exist, so Claude couldn't load the TDD guidance).
"""
from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILL_MD = REPO / "SKILL.md"
REFERENCES = REPO / "references"
BUNDLE = REPO / "senior-developer.skill"
EXPECTED_REFS = {"design.md", "testing.md", "errors.md", "security.md", "patterns.md"}


def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise AssertionError("SKILL.md must start with a YAML frontmatter block")
    _, fm, body = text.split("---\n", 2)
    meta: dict[str, str] = {}
    for line in fm.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, body


@pytest.fixture(scope="module")
def skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def frontmatter(skill_text: str) -> dict[str, str]:
    meta, _ = _split_frontmatter(skill_text)
    return meta


class TestFrontmatter:
    def test_name_is_senior_developer(self, frontmatter):
        assert frontmatter.get("name") == "senior-developer"

    def test_description_is_present_and_concise(self, frontmatter):
        desc = frontmatter.get("description", "")
        assert desc, "description must not be empty"
        assert len(desc.split()) <= 60, (
            f"description should be tight for reliable triggering "
            f"(got {len(desc.split())} words)"
        )

    def test_description_mentions_core_triggers(self, frontmatter):
        desc = frontmatter.get("description", "").lower()
        for keyword in ("write", "code", "tdd"):
            assert keyword in desc, f"description should mention {keyword!r}"


class TestReferencePaths:
    """The original bug: SKILL.md referenced references/*.md but the files
    lived at the repo root. This class makes sure that can never silently
    happen again."""

    def test_all_expected_reference_files_exist(self):
        for name in EXPECTED_REFS:
            path = REFERENCES / name
            assert path.is_file(), f"{path} is missing"

    def test_no_legacy_root_level_reference_files(self):
        for name in EXPECTED_REFS:
            stray = REPO / name
            assert not stray.exists(), (
                f"{stray} exists at repo root — files moved to references/, "
                "having both copies invites drift"
            )

    def test_every_reference_path_in_skill_md_resolves(self, skill_text):
        cited = set(re.findall(r"references/([a-z]+\.md)", skill_text))
        assert cited, "SKILL.md should cite at least one reference file"
        for name in cited:
            path = REFERENCES / name
            assert path.is_file(), (
                f"SKILL.md cites references/{name} but {path} does not exist"
            )

    def test_referenced_files_are_non_empty(self):
        for name in EXPECTED_REFS:
            path = REFERENCES / name
            assert path.stat().st_size > 200, f"{path} is suspiciously short"


class TestTddEnforcement:
    """Headline feature: TDD enforcement. Make sure the operational
    instructions Claude needs are actually present, not just philosophy."""

    def test_skill_md_has_tdd_enforcement_section(self, skill_text):
        assert "TDD Enforcement" in skill_text, (
            "SKILL.md must contain a TDD Enforcement section so the rule "
            "is visible without a second file load"
        )

    def test_skill_md_demands_observed_failure(self, skill_text):
        lowered = skill_text.lower()
        assert "observed it fail" in lowered or "observe the failure" in lowered, (
            "SKILL.md must require observing the test fail, not just writing it"
        )

    def test_skill_md_has_revert_instruction(self, skill_text):
        lowered = skill_text.lower()
        assert "revert" in lowered, (
            "SKILL.md must instruct Claude to revert if it drifted into "
            "code-first mode (this is the specific failure the user reported)"
        )

    def test_testing_md_has_runner_detection(self):
        text = (REFERENCES / "testing.md").read_text(encoding="utf-8")
        for runner in ("pytest", "jest", "go test", "cargo test", "RSpec", "dotnet test"):
            assert runner in text, (
                f"references/testing.md must list {runner!r} so Claude can "
                "detect the right test command for the project"
            )

    def test_testing_md_has_no_runner_fallback(self):
        text = (REFERENCES / "testing.md").read_text(encoding="utf-8").lower()
        assert "no-test-runner fallback" in text, (
            "references/testing.md must tell Claude what to do when the "
            "project has no test harness, otherwise TDD silently degrades"
        )

    def test_testing_md_has_worked_example(self):
        text = (REFERENCES / "testing.md").read_text(encoding="utf-8")
        assert "Worked example" in text and "pytest" in text, (
            "references/testing.md must include a concrete RED→GREEN→REFACTOR "
            "transcript so the pattern is unmistakeable"
        )


class TestBundleFreshness:
    """The .skill bundle is what users install. If it drifts from the source,
    fixing the repo doesn't fix the user's machine — that was the install-side
    half of the original bug."""

    @pytest.fixture(scope="class")
    def bundle_files(self) -> dict[str, bytes]:
        with zipfile.ZipFile(BUNDLE) as zf:
            return {
                name: zf.read(name)
                for name in zf.namelist()
                if not name.endswith("/")
            }

    def test_bundle_contains_skill_md(self, bundle_files):
        assert "senior-developer/SKILL.md" in bundle_files

    def test_bundle_contains_all_references(self, bundle_files):
        for name in EXPECTED_REFS:
            key = f"senior-developer/references/{name}"
            assert key in bundle_files, f"{key} missing from bundle"

    def test_bundle_skill_md_matches_repo(self, bundle_files):
        bundled = bundle_files["senior-developer/SKILL.md"]
        on_disk = SKILL_MD.read_bytes()
        assert bundled == on_disk, (
            "The bundled SKILL.md is stale. Rebuild senior-developer.skill "
            "or installs from the bundle won't pick up source changes."
        )

    def test_bundle_references_match_repo(self, bundle_files):
        for name in EXPECTED_REFS:
            bundled = bundle_files[f"senior-developer/references/{name}"]
            on_disk = (REFERENCES / name).read_bytes()
            assert bundled == on_disk, (
                f"references/{name} in the bundle is stale relative to the repo"
            )

    def test_bundle_has_no_legacy_root_references(self, bundle_files):
        for name in EXPECTED_REFS:
            stray = f"senior-developer/{name}"
            assert stray not in bundle_files, (
                f"{stray} present in bundle — bundle still uses the broken "
                "flat layout that caused the original load failure"
            )
