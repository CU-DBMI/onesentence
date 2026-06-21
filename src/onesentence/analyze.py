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

# Emphasis markers; neutralized (kept same length) before segmenting a paragraph
# so a period adjacent to one (e.g. "word.**") is still seen as a boundary.
_EMPHASIS_RE = re.compile(r"[*_~]")
# Trailing characters stripped when deciding whether a line ends a sentence.
_CLOSING_MARKERS = "*_`\"')]}>"


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


def _mask_for_segmentation(text: str) -> str:
    """
    Neutralize inline constructs while preserving length and offsets.

    Inline code, links, and URLs become equal-length runs of a word character
    so their internal punctuation is never read as a sentence boundary, and
    emphasis markers are replaced so a period adjacent to one (``word.**``) is
    still a boundary. Because every substitution keeps the original length, the
    masked text aligns character-for-character with ``text``.

    Args:
        text (str): The text to mask.

    Returns:
        str: The masked text, the same length as the input.
    """

    def _same_length(match: "re.Match") -> str:
        return "x" * (match.end() - match.start())

    for regex in (
        _INLINE_CODE_RE,
        _INLINE_LINK_RE,
        _REFERENCE_LINK_RE,
        _AUTOLINK_RE,
        _BARE_URL_RE,
    ):
        text = regex.sub(_same_length, text)
    return _EMPHASIS_RE.sub("x", text)


def _segment_markdown(text: str) -> List[str]:
    """
    Split a block of Markdown/reST prose into sentences, preserving markup.

    Segmentation runs on a length-preserving masked copy (see
    :func:`_mask_for_segmentation`) so links, code, and emphasis never cause a
    spurious split; the resulting spans are then sliced out of the original
    ``text`` so the raw markup is kept verbatim.

    Args:
        text (str): The (already joined) prose to segment.

    Returns:
        list[str]: The sentences, each stripped of surrounding whitespace.
    """
    masked = _mask_for_segmentation(text)
    sentences: List[str] = []
    position = 0
    for masked_sentence in _SEGMENTER.segment(masked):
        length = len(masked_sentence)
        raw = text[position : position + length].strip()
        position += length
        if raw:
            sentences.append(raw)
    # Guard against any character the segmenter did not account for.
    remainder = text[position:].strip()
    if remainder:
        sentences.append(remainder)
    return sentences or [text.strip()]


def _line_ends_sentence(line: str) -> bool:
    """Return True if a physical line ends at a sentence boundary."""
    trimmed = line.rstrip().rstrip(_CLOSING_MARKERS).rstrip()
    return trimmed.endswith((".", "!", "?"))


def _line_has_hard_break(line: str) -> bool:
    """Return True if a line carries an intentional Markdown hard line break."""
    if line.rstrip().endswith("\\"):
        return True
    return bool(line.strip()) and (len(line) - len(line.rstrip(" "))) >= 2


def _is_non_prose_line(line: str) -> bool:
    """
    Return True for lines that must be preserved rather than reflowed.

    This covers headings, horizontal rules, link reference definitions, tables,
    reST directives, list items and their indented continuations, blockquotes,
    and block-level HTML.
    """
    stripped = line.strip()
    if not stripped:
        return False
    return bool(
        _is_structural_line(stripped)
        or re.match(r"^\s*[-*+]\s+", line)  # unordered list item
        or re.match(r"^\s*\d+\.\s+", line)  # ordered list item
        or re.match(r"^\s+\S", line)  # indented continuation / indented code
        or re.match(r"^>\s*", line)  # blockquote
        or stripped.startswith("<")  # block-level HTML
    )


def _reflow_paragraph(lines: List[str]) -> List[str]:
    """
    Normalize one prose paragraph to a single complete sentence per line.

    Soft-wrapped lines (those that do not already end a sentence) are joined
    before segmenting, so a sentence split across several wrapped lines is
    rejoined and re-split cleanly. Paragraphs containing an intentional hard
    break are left untouched.

    Args:
        lines (list[str]): The raw lines making up the paragraph.

    Returns:
        list[str]: The reflowed lines.
    """
    if any(_line_has_hard_break(line) for line in lines):
        return list(lines)

    reflowed: List[str] = []
    buffer: List[str] = []
    for line in lines:
        buffer.append(line.strip())
        # A line that ends a sentence closes the current soft-wrapped run.
        if _line_ends_sentence(line):
            reflowed.extend(_segment_markdown(" ".join(buffer)))
            buffer = []
    if buffer:
        reflowed.extend(_segment_markdown(" ".join(buffer)))
    return reflowed


def correct_file_for_one_sentence_per_line(
    file_path: str, dest_path: Optional[str] = None
) -> bool:
    """
    Normalize a file so each prose sentence sits on its own line.

    Prose paragraphs are reflowed by joining Markdown soft-wrapped lines,
    segmenting the paragraph into sentences, and writing exactly one complete
    sentence per line. Intentional hard breaks, lists, blockquotes, headings,
    code blocks, tables, HTML, and ``noqa`` regions are preserved unchanged.

    Args:
        file_path (str):
            The path to the file to check.
        dest_path (str):
            The path to write the file to.
            If not provided, the original file will be overwritten.

    Returns:
        bool: True if the file was already compliant (no changes were needed),
        False otherwise.
    """
    with open(file_path, "r") as file:
        original = file.read()

    raw_lines = original.split("\n")
    # ``split`` leaves a trailing "" for a final newline; track and re-add it.
    trailing_newline = bool(raw_lines) and raw_lines[-1] == ""
    if trailing_newline:
        raw_lines.pop()

    output: List[str] = []
    paragraph: List[str] = []
    in_code_block = False
    ignore_block = False

    def flush_paragraph() -> None:
        if paragraph:
            output.extend(_reflow_paragraph(paragraph))
            paragraph.clear()

    for line in raw_lines:
        stripped = line.strip()
        is_fence = stripped.startswith("```") or stripped.startswith("~~~")

        if in_code_block:
            output.append(line.rstrip())
            if is_fence:
                in_code_block = False
            continue
        if is_fence:
            flush_paragraph()
            in_code_block = True
            output.append(line.rstrip())
            continue
        if ignore_block:
            output.append(line.rstrip())
            if "noqa: onesentence-end" in line:
                ignore_block = False
            continue
        if "noqa: onesentence-start" in line:
            flush_paragraph()
            ignore_block = True
            output.append(line.rstrip())
            continue
        if "noqa: onesentence-end" in line:
            flush_paragraph()
            output.append(line.rstrip())
            continue
        if stripped == "":
            flush_paragraph()
            output.append("")
            continue
        # Lines exempted inline, or that are not prose, are preserved as-is.
        if "noqa: onesentence" in line or _is_non_prose_line(line):
            flush_paragraph()
            output.append(line.rstrip())
            continue
        paragraph.append(line)
    flush_paragraph()

    corrected = "\n".join(output)
    if trailing_newline or corrected:
        corrected += "\n"

    if dest_path is None:
        dest_path = file_path
    with open(dest_path, "w") as file:
        file.write(corrected)

    return corrected == original
