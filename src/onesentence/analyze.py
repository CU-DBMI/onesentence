"""
Module for checking for one sentence per line and related.
"""

import re
from typing import List, Optional

import pysbd

# A single segmenter is reused across calls; constructing one per line is
# needless overhead and the segmenter is stateless between ``segment`` calls.
_SEGMENTER = pysbd.Segmenter(language="en", clean=False)

# Non-prose Markdown / reStructuredText structures that are exempt from the
# "one sentence per line" rule.  These are matched against the stripped line.
_HEADING_RE = re.compile(r"^#{1,6}(\s|$)")  # ATX heading, incl. "### 1. Foo"
_RULE_OR_UNDERLINE_RE = re.compile(
    r"^[=\-~`#*_]+$"
)  # setext underline, thematic break, or emphasis-only line
_RST_DIRECTIVE_RE = re.compile(r"^\.\.\s+\w+::")  # ".. directive::"
_LINK_DEFINITION_RE = re.compile(
    r"^\[[^\]]+\]:\s+\S"
)  # link reference definition, e.g. "[id]: https://example.com"
_TABLE_ROW_RE = re.compile(r"^\|")  # "| cell | cell |"
_TABLE_SEPARATOR_RE = re.compile(
    r"^\|?[\s:|-]*\|[\s:|-]*$"
)  # "|---|:--:|" style separators

# Prose constructs whose internal punctuation must not be read as sentence
# boundaries; each is replaced with a single opaque token before segmentation.
_INLINE_CODE_RE = re.compile(r"``[^`]*``|`[^`]*`")  # `code` / ``code``
_INLINE_LINK_RE = re.compile(r"!?\[[^\]]*\]\([^)]*\)")  # [text](url) / ![alt](url)
_REFERENCE_LINK_RE = re.compile(r"\[[^\]]*\]\[[^\]]*\]")  # [text][ref]
_AUTOLINK_RE = re.compile(r"<[^>\s]+>")  # <https://example.com>
# Bare URLs, stopping before any trailing sentence punctuation so a period that
# actually ends the sentence is preserved.
_BARE_URL_RE = re.compile(
    r"\b(?:https?|ftp)://[^\s]+?(?=[.,!?;:'\")\]]*(?:\s|$))"
    r"|\bwww\.[^\s]+?(?=[.,!?;:'\")\]]*(?:\s|$))"
)
# Remaining markup (emphasis, heading markers, pipes, ...) that is not part of
# sentence structure.
_NON_SENTENCE_CHARS_RE = re.compile(r"[^a-zA-Z0-9\s.,!?\'\"()\-]")


def _is_structural_line(stripped: str) -> bool:
    """
    Return True for non-prose Markdown/reST lines exempt from the rule.

    Args:
        stripped (str): The line with surrounding whitespace removed.

    Returns:
        bool: True if the line is a heading, horizontal rule / underline,
        reST directive, link reference definition, or table row/separator.
    """
    return bool(
        _HEADING_RE.match(stripped)
        or _RULE_OR_UNDERLINE_RE.match(stripped)
        or _RST_DIRECTIVE_RE.match(stripped)
        or _LINK_DEFINITION_RE.match(stripped)
        or _TABLE_ROW_RE.match(stripped)
        or _TABLE_SEPARATOR_RE.match(stripped)
    )


def _mask_inline_constructs(text: str) -> str:
    """
    Replace inline code, links, and URLs with opaque tokens.

    This keeps their internal punctuation (dots in URLs, abbreviations inside
    code, ...) from being treated as sentence boundaries while leaving the
    surrounding prose intact for segmentation.

    Args:
        text (str): The stripped line to mask.

    Returns:
        str: The line with inline constructs and stray markup removed.
    """
    # Order matters: code first, then links (which may wrap URLs), then any
    # remaining autolinks / bare URLs.
    text = _INLINE_CODE_RE.sub("INLINECODE", text)
    text = _INLINE_LINK_RE.sub("LINK", text)
    text = _REFERENCE_LINK_RE.sub("LINK", text)
    text = _AUTOLINK_RE.sub("URL", text)
    text = _BARE_URL_RE.sub("URL", text)
    return _NON_SENTENCE_CHARS_RE.sub("", text)


def is_single_sentence(line: str, ignore_block: bool) -> bool:
    """
    Check if the given line contains only one sentence.

    Args:
        line (str): The line to check.
        ignore_block (bool): Whether the line is within an ignore block.

    Returns:
        bool: True if the line contains only one sentence, False otherwise.
    """

    if not line.strip():
        return True  # Consider empty lines as single sentences

    # Ignore lines with the "noqa: onesentence" comment
    if "noqa: onesentence" in line:
        return True

    # Ignore lines within an ignore block
    if ignore_block:
        return True

    stripped = line.strip()

    # Ignore non-prose structures (headings, rules, link definitions, tables,
    # reST directives). Numbered headings such as "### 1. Foo" are covered here.
    if _is_structural_line(stripped):
        return True

    # Allow multiple sentences in list items, their continuations, and blockquotes
    if re.match(r"^\s*[-*+]\s+", line):  # Unordered list item
        return True
    if re.match(r"^\s*\d+\.\s+", line):  # Ordered list item
        return True
    if re.match(r"^\s+\S", line):  # Indented continuation of a list item
        return True
    if re.match(r"^>\s*", line):  # Blockquote
        return True

    # Mask inline code, links, and URLs so their punctuation does not trigger
    # false sentence breaks, then count the remaining sentences.
    masked = _mask_inline_constructs(stripped)
    return len(_SEGMENTER.segment(masked)) == 1


def check_file_for_one_sentence_per_line(file_path: str) -> bool:
    """
    Check if each line in the given file contains only one sentence.

    Args:
        file_path (str): The path to the file to check.

    Returns:
        bool: True if all lines contain only one sentence, False otherwise.
    """
    all_single_sentences = True
    ignore_block = False
    in_code_block = False
    with open(file_path, "r") as file:
        for line_number, line in enumerate(file, start=1):
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
            if "noqa: onesentence-start" in line:
                ignore_block = True
                continue
            if "noqa: onesentence-end" in line:
                ignore_block = False
                continue
            if not is_single_sentence(line.rstrip("\n"), ignore_block or in_code_block):
                print(f"Failed: line {line_number}: {line.strip()}")
                all_single_sentences = False
    return all_single_sentences


def correct_file_for_one_sentence_per_line(
    file_path: str, dest_path: Optional[str] = None
) -> bool:
    """
    Check if each line in the given file contains only one sentence.
    If not, correct the file by replacing the contents with correctly segmented sentences.

    Args:
        file_path (str):
            The path to the file to check.
        dest_path (str):
            The path to write the file to.
            If not provided, the original file will be overwritten.

    Returns:
        bool: True if all lines contain only one sentence, False otherwise.
    """
    all_single_sentences = True
    ignore_block = False
    in_code_block = False
    corrected_lines: List[str] = []

    with open(file_path, "r") as file:
        for line_number, line in enumerate(file, start=1):
            original_indent = re.match(
                r"^\s*", line
            ).group()  # Capture the original indentation
            stripped_line = line.strip()

            if stripped_line.startswith("```"):
                in_code_block = not in_code_block
                corrected_lines.append(line.rstrip())
                continue
            if "noqa: onesentence-start" in stripped_line:
                ignore_block = True
                corrected_lines.append(line.rstrip())
                continue
            if "noqa: onesentence-end" in stripped_line:
                ignore_block = False
                corrected_lines.append(line.rstrip())
                continue
            if not is_single_sentence(line.rstrip("\n"), ignore_block or in_code_block):
                print(f"Failed: line {line_number}: {stripped_line}")
                all_single_sentences = False
                if not ignore_block:
                    sentences = _SEGMENTER.segment(stripped_line)
                    # Detect and move lines with only Markdown characters to the end of the second-to-last line
                    if sentences and re.match(r"^[=\-~`#\*]+$", sentences[-1]):
                        markdown_line = sentences.pop()
                        if sentences:
                            sentences[-1] += markdown_line
                    corrected_lines.extend(
                        [original_indent + sentence.strip() for sentence in sentences]
                    )
                else:
                    corrected_lines.append(line.rstrip())
            else:
                corrected_lines.append(line.rstrip())

    # If we have no dest path provided, we will overwrite the original file
    if dest_path is None:
        dest_path = file_path

    # Write the corrected content back to the file
    with open(dest_path, "w") as file:
        for corrected_line in corrected_lines:
            file.write(corrected_line + "\n")

    return all_single_sentences
