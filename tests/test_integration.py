"""
Integration tests for onesentence.

These exercise onesentence together with the tools it is meant to be used
alongside: the ``mdformat`` formatter and the ``pre-commit`` / ``prek`` hook
runners. Each test is skipped when the relevant tool is not installed.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / ".pre-commit-hooks.yaml"


def _resolve_tool(name: str):
    """
    Resolve a CLI tool to an absolute path.

    Prefer the script that ships next to the active interpreter (the venv used
    to run the tests) so we bypass any shims on PATH; fall back to PATH.
    Returns None when the tool cannot be found.
    """
    candidate = os.path.join(os.path.dirname(sys.executable), name)
    if os.path.isfile(candidate):
        return candidate
    return shutil.which(name)


ONESENTENCE = _resolve_tool("onesentence")


def _run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


@pytest.mark.skipif(
    _resolve_tool("mdformat") is None or ONESENTENCE is None,
    reason="mdformat (or onesentence) is not installed",
)
def test_mdformat_and_onesentence_are_idempotent(tmp_path):
    """
    Repeated ``mdformat --wrap=keep`` + ``onesentence fix`` runs converge to a
    fixed point: once stable, further rounds change nothing and the document is
    one-sentence-per-line compliant.
    """
    mdformat = _resolve_tool("mdformat")
    doc = tmp_path / "doc.md"
    doc.write_text(
        "# Title\n"
        "\n"
        "## 1. Section\n"
        "\n"
        "First sentence. Second sentence. Third sentence.\n"
        "\n"
        "See https://example.com/x for details. Then continue onward.\n"
    )

    def round_trip():
        _run([mdformat, "--wrap=keep", str(doc)])
        return _run([ONESENTENCE, "fix", str(doc)])

    # Iterate until the content stops changing.
    previous = None
    for _ in range(6):
        round_trip()
        current = doc.read_text()
        if current == previous:
            break
        previous = current
    else:
        pytest.fail("mdformat + onesentence did not reach a fixed point")

    stable = doc.read_text()

    # Once stable, another round changes nothing and reports success (0).
    result = round_trip()
    assert doc.read_text() == stable
    assert result.returncode == 0

    # The stable document is one-sentence-per-line compliant.
    assert _run([ONESENTENCE, "check", str(doc)]).returncode == 0

    # And the multi-sentence prose really was split onto separate lines.
    assert "First sentence.\nSecond sentence.\nThird sentence." in stable


def _check_hook_from_manifest():
    """Load the ``check`` hook definition from the project's hook manifest."""
    hooks = yaml.safe_load(MANIFEST.read_text())
    return next(hook for hook in hooks if hook["id"] == "check")


def _write_consumer_repo(tmp_path):
    """
    Create a throwaway git repo configured to run onesentence as a local hook,
    deriving the file-selection rules (``types`` / ``files``) from the project's
    actual hook manifest so the test validates the manifest itself.
    """
    hook = _check_hook_from_manifest()
    _run(["git", "init", "-q", str(tmp_path)])
    _run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.com"])
    _run(["git", "-C", str(tmp_path), "config", "user.name", "test"])

    config = {
        "repos": [
            {
                "repo": "local",
                "hooks": [
                    {
                        "id": "onesentence-check",
                        "name": hook["name"],
                        # Use the resolved absolute entry so the hook does not
                        # depend on onesentence being on PATH.
                        "entry": f"{ONESENTENCE} check",
                        "language": "system",
                        "types": hook["types"],
                        "files": hook["files"],
                    }
                ],
            }
        ]
    }
    (tmp_path / ".pre-commit-config.yaml").write_text(yaml.safe_dump(config))

    # A genuine violation in a Markdown file...
    (tmp_path / "bad.md").write_text("# Title\n\nOne sentence. Two sentence.\n")
    # ...a compliant reStructuredText file...
    (tmp_path / "ok.rst").write_text("Title\n=====\n\nA single sentence.\n")
    # ...and a non-matching source file that must be ignored entirely.
    (tmp_path / "code.py").write_text("x = 1  # One. Two.\n")
    _run(["git", "-C", str(tmp_path), "add", "-A"])


@pytest.mark.skipif(ONESENTENCE is None, reason="onesentence is not installed")
@pytest.mark.parametrize("runner_name", ["pre-commit", "prek"])
def test_hook_runs_through_runner(runner_name, tmp_path):
    """
    The hook's file matching and exit codes behave correctly under both
    pre-commit and prek: matching files are checked, a violation fails, a
    compliant file passes, and non-matching files are skipped.
    """
    runner = _resolve_tool(runner_name)
    if runner is None:
        pytest.skip(f"{runner_name} is not installed")

    _write_consumer_repo(tmp_path)

    def run_on(*filenames):
        cmd = [runner, "run", "--files", *[str(tmp_path / f) for f in filenames]]
        return _run(cmd, cwd=tmp_path)

    # The Markdown file with two sentences on one line fails the hook. This
    # only happens if the file actually matched (the file-selection fix).
    bad = run_on("bad.md")
    assert bad.returncode != 0, bad.stdout + bad.stderr

    # The compliant reST file passes.
    ok = run_on("ok.rst")
    assert ok.returncode == 0, ok.stdout + ok.stderr

    # The Python file does not match and is skipped, so the run succeeds even
    # though its comment contains two sentences.
    code = run_on("code.py")
    assert code.returncode == 0, code.stdout + code.stderr
