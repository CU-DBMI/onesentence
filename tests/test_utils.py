"""
Tests for onesentence.utils
"""

import pytest
from onesentence.utils import is_single_sentence, check_file_for_one_sentence_per_line, correct_file_for_one_sentence_per_line

@pytest.mark.parametrize("line, expected", [
    ("This is a single sentence.", True),
    ("This is the first sentence. This is the second sentence.", False),
    ("Another single sentence", True),
    ("Sentence one. Sentence two. Sentence three.", False),
    ("Sentence one. Sentence two. Sentence three. <!-- noqa: onesentence -->", True),
    ("", True),  # Empty line should be considered as a single sentence
])
def test_is_single_sentence(line, expected):
    assert is_single_sentence(line, ignore_block=False) == expected

@pytest.mark.parametrize("file_content, expected", [
    ("This is a single sentence.\nAnother single sentence.\n", True),
    ("This is the first sentence. This is the second sentence.\nAnother single sentence.\n", False),
    ("Single sentence.\nSingle sentence.\nSingle sentence.\n", True),
    ("Sentence one. Sentence two.\nSentence three.\n", False),
    ("Sentence one. Sentence two. <!-- noqa: onesentence -->\nSentence three.\n", True),
    ("This is the first sentence. This is the second sentence.\nAnother single sentence.\n", False),
])
def test_check_file_for_single_sentences(tmp_path, file_content, expected):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text(file_content)
    assert check_file_for_one_sentence_per_line(file_path) == expected

@pytest.mark.parametrize("file_content, expected_content, expected_returncode", [
    (
        "This is a single sentence.\nAnother single sentence.\n",
        "This is a single sentence.\nAnother single sentence.\n",
        True
    ),
    (
        "This is the first sentence. This is the second sentence.\nAnother single sentence.\n",
        "This is the first sentence.\nThis is the second sentence.\nAnother single sentence.\n",
        False
    ),
    (
        "This is the first sentence. This is the second sentence. <!-- noqa: onesentence -->\nAnother single sentence.\n",
        "This is the first sentence. This is the second sentence. <!-- noqa: onesentence -->\nAnother single sentence.\n",
        True
    ),
    (
        "<!-- noqa: onesentence-start -->\nThis is the first sentence. This is the second sentence.\n<!-- noqa: onesentence-end -->\nAnother single sentence.\n",
        "<!-- noqa: onesentence-start -->\nThis is the first sentence. This is the second sentence.\n<!-- noqa: onesentence-end -->\nAnother single sentence.\n",
        True
    ),
])
def test_correct_file_for_one_sentence_per_line(tmp_path, file_content, expected_content, expected_returncode):
    """
    Test the correct_file_for_one_sentence_per_line function for different file contents.
    """
    file_path = tmp_path / "test_file.md"
    file_path.write_text(file_content)

    result = correct_file_for_one_sentence_per_line(file_path)

    corrected_content = file_path.read_text()
    print(corrected_content)
    print(expected_content)
    assert corrected_content == expected_content
    assert result == expected_returncode
