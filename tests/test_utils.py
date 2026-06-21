"""
Tests for onesentence.utils
"""

import pytest
from onesentence.analyze import is_single_sentence, check_file_for_one_sentence_per_line, correct_file_for_one_sentence_per_line

@pytest.mark.parametrize("line, expected", [
    ("This is a single sentence.", True),
    ("This is the first sentence. This is the second sentence.", False),
    ("Another single sentence", True),
    ("Sentence one. Sentence two. Sentence three.", False),
    ("Sentence one. Sentence two. Sentence three. <!-- noqa: onesentence -->", True),
    ("", True),  # Empty line should be considered as a single sentence
    ("Use `file.txt` to store data.", True),
    ("Call `os.path.join()` to combine paths.", True),
    ("The value of `foo.bar.baz` is used here.", True),
    ("The pattern `Hello. World` matches two words.", True),
    ("Run `echo hello. world` in your shell.", True),
    ("The string `foo. Bar baz` is invalid.", True),
    ("> This is a blockquote. It has two sentences.", True),
    ("  continuation of a list item. With two sentences.", True),
    # Headings are structural and exempt, including numbered headings that pysbd
    # would otherwise split on (e.g. "### 1. Foo" -> ["### 1. ", "Foo"]).
    ("# Heading", True),
    ("## 1. Numbered Section", True),
    ("### 1.2 Subsection With Two. Looking Parts", True),
    # Horizontal rules / setext underlines.
    ("---", True),
    ("=====", True),
    # Table rows and separators are structural.
    ("| Severity | SLA |", True),
    ("| -------- | --- |", True),
    # Link reference definitions are structural.
    ("[docs]: https://example.com/docs", True),
    ('[docs]: https://example.com/docs "Documentation"', True),
    # URLs and Markdown links must not trigger false sentence breaks.
    ("Visit https://example.com/path for details.", True),
    ("See the [guide](https://example.com/guide) for more.", True),
    ("Contact us at <https://example.com>.", True),
    ("An image ![alt text](image.png) sits here.", True),
    # ...but a genuine sentence break after a URL/link is still detected.
    ("See https://example.com/a. Then continue here.", False),
    ("Read [the docs](https://example.com/y). Then proceed onward.", False),
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

def test_check_compliant_policy_document():
    """
    A realistic policy document made of headings (including numbered ones),
    a table, a link reference definition, URLs, and a code block must be
    reported as compliant.
    """
    assert check_file_for_one_sentence_per_line("tests/data/5_policy_compliant.md") is True


def test_headings_and_tables_are_not_flagged_but_prose_is(tmp_path):
    """
    Structural Markdown (headings, tables, link defs) is exempt, while genuine
    multi-sentence prose lines are still caught.
    """
    content = (
        "# Title\n\n"
        "## 1. Numbered Heading\n\n"
        "| Col A | Col B |\n"
        "| ----- | ----- |\n"
        "| 1     | 2     |\n\n"
        "This line is fine.\n"
        "This line has two sentences. That is a violation.\n"
    )
    file_path = tmp_path / "doc.md"
    file_path.write_text(content)
    # Only the genuine prose violation should fail the check.
    assert check_file_for_one_sentence_per_line(str(file_path)) is False


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
    (
        "Some text.\n```\nThis is the first sentence. This is the second sentence.\n```\nAnother single sentence.\n",
        "Some text.\n```\nThis is the first sentence. This is the second sentence.\n```\nAnother single sentence.\n",
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
