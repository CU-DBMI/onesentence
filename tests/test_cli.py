"""
Tests for sembr_check.cli
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
    Test the sembr_check CLI for different file contents.
    """
    file_path = tmp_path / "test_file.md"
    file_path.write_text(file_content)

    stdout, stderr, returncode = run_cli_command(["sembr_check", "check", str(file_path)])

    assert returncode == expected_returncode

@pytest.mark.parametrize("file_path, expected_returncode", [
    ("tests/data/1_true_pos.md", 1),
    ("tests/data/2_true_neg.md", 0),
])
def test_cli_check_file(tmp_path, file_path, expected_returncode):
    """
    Test the sembr_check CLI for different file contents.
    """

    stdout, stderr, returncode = run_cli_command(["sembr_check", "check", str(file_path)])

    print(stdout)
    print(stderr)
    assert returncode == expected_returncode