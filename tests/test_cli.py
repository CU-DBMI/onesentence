"""
Tests for onesentence.cli
"""

import pytest
from tests.utils import run_cli_command

def test_cli_util():
    """
    Test the run_cli_command for successful output
    """

    _, _, returncode = run_cli_command(["echo", "'hello world'"])

    assert returncode == 0

    assert returncode == 0

@pytest.mark.parametrize("file_content, expected_returncode", [
    ("This is a single sentence.\nAnother single sentence.\n", 0),
    ("This is the first sentence. This is the second sentence.\nAnother single sentence.\n", 1),
])
def test_cli_check_simulated_file(tmp_path, file_content, expected_returncode):
    """
    Test the onesentence CLI for different file contents.
    """
    file_path = tmp_path / "test_file.md"
    file_path.write_text(file_content)

    _, _, returncode = run_cli_command(["onesentence", "check", str(file_path)])

    assert returncode == expected_returncode

@pytest.mark.parametrize("file_path, expected_returncode", [
    ("tests/data/1_true_pos.md", 1),
    ("tests/data/2_true_neg.md", 0),
    ("tests/data/3_true_pos.rst", 1),
    ("tests/data/4_true_neg.rst", 0),
])
def test_cli_check_file(tmp_path, file_path, expected_returncode):
    """
    Test the onesentence CLI for checking different file contents.
    """

    _, _, returncode = run_cli_command(["onesentence", "check", str(file_path)])

    assert returncode == expected_returncode

@pytest.mark.parametrize("file_path, fixed_path, expected_returncode", [
    ("tests/data/1_true_pos.md", "tests/data/1_true_pos_fixed.md",  1),
    ("tests/data/2_true_neg.md", None, 0),
    ("tests/data/3_true_pos.rst", "tests/data/3_true_pos_fixed.rst", 1),
    ("tests/data/4_true_neg.rst", None, 0),
    ("tests/data/6_soft_wrapped.md", "tests/data/6_soft_wrapped_fixed.md", 1),
])
def test_cli_fix_file(tmp_path, file_path, fixed_path, expected_returncode):
    """
    Test the onesentence CLI for fixing different file contents.
    """

    dest_path = tmp_path / "test_file.md"
    _, _, returncode = run_cli_command(["onesentence", "fix", str(file_path), "--output", str(dest_path)])

    assert returncode == expected_returncode

    with open(dest_path, 'r') as file:
        dest_content = file.read()

    if fixed_path is not None:
        with open(fixed_path, 'r') as file:
            comparison_dest_content = file.read()
    else:
        with open(file_path, 'r') as file:
            comparison_dest_content = file.read()

    assert dest_content == comparison_dest_content


def test_cli_check_multiple_files(tmp_path):
    """
    check accepts multiple paths and fails if any single file has a violation.
    """
    good = tmp_path / "good.md"
    good.write_text("One good sentence.\nAnother good one.\n")
    bad = tmp_path / "bad.md"
    bad.write_text("One. Two.\n")

    # All compliant -> 0
    _, _, returncode = run_cli_command(["onesentence", "check", str(good)])
    assert returncode == 0

    # Any violation across the set -> 1
    _, _, returncode = run_cli_command(["onesentence", "check", str(good), str(bad)])
    assert returncode == 1


def test_cli_fix_multiple_files_independently(tmp_path):
    """
    fix corrects each file in place without letting one overwrite another.
    """
    a = tmp_path / "a.md"
    a.write_text("Alpha one. Alpha two.\n")
    b = tmp_path / "b.md"
    b.write_text("Beta one. Beta two.\n")

    _, _, returncode = run_cli_command(["onesentence", "fix", str(a), str(b)])
    assert returncode == 1  # both required changes

    assert a.read_text() == "Alpha one.\nAlpha two.\n"
    assert b.read_text() == "Beta one.\nBeta two.\n"


def test_cli_fix_output_rejects_multiple_files(tmp_path):
    """
    --output is only valid with a single input; using it with several inputs is
    a usage error and must not write or modify anything.
    """
    a = tmp_path / "a.md"
    a.write_text("Alpha one. Alpha two.\n")
    b = tmp_path / "b.md"
    b.write_text("Beta one. Beta two.\n")
    out = tmp_path / "out.md"

    _, _, returncode = run_cli_command(
        ["onesentence", "fix", str(a), str(b), "--output", str(out)]
    )
    assert returncode == 2
    assert not out.exists()
    # inputs are left untouched
    assert a.read_text() == "Alpha one. Alpha two.\n"
    assert b.read_text() == "Beta one. Beta two.\n"


def test_cli_fix_output_single_file_leaves_source_untouched(tmp_path):
    """
    fix --output writes the corrected content to the destination and leaves the
    source file unchanged.
    """
    src = tmp_path / "src.md"
    src.write_text("Alpha. Beta.\n")
    out = tmp_path / "out.md"

    _, _, returncode = run_cli_command(
        ["onesentence", "fix", str(src), "--output", str(out)]
    )
    assert returncode == 1
    assert src.read_text() == "Alpha. Beta.\n"
    assert out.read_text() == "Alpha.\nBeta.\n"


@pytest.mark.parametrize("subcommand", ["check", "fix"])
def test_cli_no_input_files_is_usage_error(subcommand):
    """
    Running check/fix with no file arguments is a usage error (exit code 2).
    """
    _, _, returncode = run_cli_command(["onesentence", subcommand])
    assert returncode == 2


def test_cli_fix_is_idempotent(tmp_path):
    """
    Fixing a file once makes subsequent checks pass and further fixes no-ops.
    """
    doc = tmp_path / "doc.md"
    doc.write_text("One. Two. Three.\n")

    _, _, returncode = run_cli_command(["onesentence", "fix", str(doc)])
    assert returncode == 1
    after_first_fix = doc.read_text()
    assert after_first_fix == "One.\nTwo.\nThree.\n"

    # A check now passes.
    _, _, returncode = run_cli_command(["onesentence", "check", str(doc)])
    assert returncode == 0

    # A second fix changes nothing and reports success.
    _, _, returncode = run_cli_command(["onesentence", "fix", str(doc)])
    assert returncode == 0
    assert doc.read_text() == after_first_fix


def test_cli_check_compliant_policy_document_returns_zero():
    """
    Checking a compliant document full of headings, tables, link definitions,
    URLs, and code returns a zero exit code.
    """
    _, _, returncode = run_cli_command(
        ["onesentence", "check", "tests/data/5_policy_compliant.md"]
    )
    assert returncode == 0
