"""
Tests for sembr_check.utils
"""

import pytest
from sembr_check.utils import is_single_sentence, check_file_for_semantic_line_breaks

@pytest.mark.parametrize("line, expected", [
    ("This is a single sentence.", True),
    ("This is the first sentence. This is the second sentence.", False),
    ("Another single sentence", True),
    ("Sentence one. Sentence two. Sentence three.", False),
    ("", True),  # Empty line should be considered as a single sentence
])
def test_is_single_sentence(line, expected):
    assert is_single_sentence(line) == expected

@pytest.mark.parametrize("file_content, expected", [
    ("This is a single sentence.\nAnother single sentence.\n", True),
    ("This is the first sentence. This is the second sentence.\nAnother single sentence.\n", False),
    ("Single sentence.\nSingle sentence.\nSingle sentence.\n", True),
    ("Sentence one. Sentence two.\nSentence three.\n", False),
    ("This is the first sentence. This is the second sentence.\nAnother single sentence.\n", False),
])
def test_check_file_for_single_sentences(tmp_path, file_content, expected):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text(file_content)
    assert check_file_for_semantic_line_breaks(file_path) == expected

