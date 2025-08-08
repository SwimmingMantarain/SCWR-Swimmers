# Testing library/framework: pytest
# These tests validate the structure and semantics of the requirements list
# introduced in the PR. They focus on ensuring each entry is parseable,
# correctly pinned where expected, and uses valid extras syntax.

import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
REQ_PATH = REPO_ROOT / "requirements" / "requirements.txt"

# Regex that captures: name, optional extras, optional pinned version
REQ_PATTERN = re.compile(
    r"^\s*"
    r"(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)"
    r"(?:\[(?P<extras>[A-Za-z0-9._,\-\s]+)\])?"
    r"(?:==(?P<version>[0-9][0-9A-Za-z._\-+!]*))?"
    r"\s*$",
    re.ASCII,
)

SEMVERISH_PATTERN = re.compile(r"^[0-9]+(?:\.[0-9]+){1,3}(?:[A-Za-z0-9._+\-!]*)?$")


def _load_requirement_lines():
    assert REQ_PATH.is_file(), f"Expected requirements file at {REQ_PATH}"
    lines = []
    with REQ_PATH.open("r", encoding="utf-8") as f:
        for raw in f:
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            lines.append(s)
    return lines


def parse_requirement(line: str):
    m = REQ_PATTERN.match(line)
    if not m:
        return None
    name = m.group("name")
    extras_raw = m.group("extras")
    version = m.group("version")
    extras = []
    if extras_raw:
        extras = [e.strip() for e in extras_raw.split(",") if e.strip()]
    return {
        "name": name,
        "name_lower": name.lower(),
        "extras": extras,
        "version": version,
        "raw": line,
    }


# -----------------------
# Parsing and structure
# -----------------------


@pytest.mark.parametrize(
    "line",
    _load_requirement_lines(),
    ids=lambda s: s
)
def test_each_requirement_line_is_parseable(line):
    parsed = parse_requirement(line)
    assert parsed is not None, f"Line failed to parse: {line!r}"
    assert parsed["name"], "Package name should not be empty"


def test_no_duplicate_packages_case_insensitive():
    lines = _load_requirement_lines()
    names = []
    for line in lines:
        parsed = parse_requirement(line)
        assert parsed is not None, f"Unparseable line: {line}"
        names.append(parsed["name_lower"])
    assert len(names) == len(set(names)), f"Duplicate packages found: {names}"


def test_no_vcs_urls_or_local_paths_in_requirements():
    lines = _load_requirement_lines()
    for line in lines:
        low = line.lower()
        assert "git+" not in low, f"VCS URLs not allowed: {line}"
        assert "://" not in low, f"URL specifications not allowed: {line}"
        assert not low.startswith("-e "), f"Editable installs not allowed: {line}"
        assert "file:" not in low, f"Local file refs not allowed: {line}"


# -----------------------
# Content expectations (from PR diff focus)
# -----------------------


def test_expected_packages_are_present():
    lines = _load_requirement_lines()
    parsed = [parse_requirement(line) for line in lines]
    names = {p["name_lower"] for p in parsed if p}
    # From the given diff, ensure these packages are present (case-insensitive)
    expected = {"beautifulsoup4", "python_bcrypt", "requests", "fastapi"}
    missing = expected - names
    assert not missing, f"Missing expected packages: {missing}"


def test_expected_versions_and_extras_for_known_entries():
    lines = _load_requirement_lines()
    reqs = {parse_requirement(line)["name_lower"]: parse_requirement(line) for line in lines}

    # Version pins expected for these entries
    expected_versions = {
        "beautifulsoup4": "4.13.4",
        "python_bcrypt": "0.3.2",
        "requests": "2.32.4",
    }
    for pkg, ver in expected_versions.items():
        assert pkg in reqs, f"{pkg} not found in requirements"
        actual = reqs[pkg]["version"]
        assert actual == ver, f"{pkg} expected version {ver}, got {actual}"

        # Version format sanity check
        assert SEMVERISH_PATTERN.match(actual), f"{pkg} version not semver-ish: {actual}"

    # fastapi entry: ensure 'standard' extra is present; version pin is optional per diff
    assert "fastapi" in reqs, "fastapi not found in requirements"
    fastapi = reqs["fastapi"]
    assert "standard" in fastapi["extras"], "fastapi should include [standard] extra"
    assert fastapi["version"] in (None, ""), "fastapi is expected unpinned in the provided diff"


def test_package_name_character_set_is_valid():
    lines = _load_requirement_lines()
    for line in lines:
        p = parse_requirement(line)
        assert p is not None
        # Basic PEP 508-ish name character validation already enforced by regex
        assert re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", p["name"]), f"Invalid package name: {p['name']}"


def test_all_pinned_versions_use_numeric_segments():
    lines = _load_requirement_lines()
    for line in lines:
        p = parse_requirement(line)
        assert p is not None
        if p["version"]:
            # Check at least two numeric segments (e.g., 1.2 or 1.2.3) to avoid single-digit pins
            assert re.match(r"^\d+\.\d+(\.\d+)?", p["version"]), f"Version should have at least major.minor: {p['version']}"