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
])
def test_cli_fix_file(tmp_path, file_path, fixed_path, expected_returncode):
    """
    Test the onesentence CLI for fixing different file contents.
    """

    dest_path = tmp_path / "test_file.md"
    _, _, returncode = run_cli_command(["onesentence", "fix", str(file_path), str(dest_path)])

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
