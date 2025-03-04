"""
Module for checking semantic line breaks and related.
"""

import pysbd
import re

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

    # Additional filtering for common reST and Markdown formatting
    if re.match(r'^[=\-~`#\*]+$', line):
        return True
    if re.match(r'^\.\.\s+\w+::', line):
        return True

    # Allow multiple sentences in list items (Markdown, reST, AsciiDoc)
    if re.match(r'^\s*[-*+]\s+', line):  # Unordered list item
        return True
    if re.match(r'^\s*\d+\.\s+', line):  # Ordered list item
        return True

    # Remove special characters that do not pertain to sentence structure
    line = re.sub(r'[^a-zA-Z0-9\s.,!?\'"()\-]', '', line)

    segmenter = pysbd.Segmenter(language="en", clean=False)
    sentences = segmenter.segment(line)
    return len(sentences) == 1

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
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if "noqa: onesentence-start" in line:
                ignore_block = True
                continue
            if "noqa: onesentence-end" in line:
                ignore_block = False
                continue
            if not is_single_sentence(line.strip(), ignore_block):
                print(f"Failed: line {line_number}: {line.strip()}")
                all_single_sentences = False
    return all_single_sentences

def correct_file_for_one_sentence_per_line(file_path: str) -> bool:
    """
    Check if each line in the given file contains only one sentence.
    If not, correct the file by replacing the contents with correctly segmented sentences.

    Args:
        file_path (str): The path to the file to check.

    Returns:
        bool: True if all lines contain only one sentence, False otherwise.
    """
    all_single_sentences = True
    ignore_block = False
    corrected_lines = []

    segmenter = pysbd.Segmenter(language="en", clean=False)

    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if "noqa: onesentence-start" in line:
                ignore_block = True
                corrected_lines.append(line.strip())
                continue
            if "noqa: onesentence-end" in line:
                ignore_block = False
                corrected_lines.append(line.strip())
                continue
            if not is_single_sentence(line.strip(), ignore_block):
                print(f"Failed: line {line_number}: {line.strip()}")
                all_single_sentences = False
                if not ignore_block:
                    sentences = segmenter.segment(line.strip())
                    corrected_lines.extend([sentence.strip() for sentence in sentences])
                else:
                    corrected_lines.append(line.strip())
            else:
                corrected_lines.append(line.strip())

    # Write the corrected content back to the file
    with open(file_path, 'w') as file:
        for corrected_line in corrected_lines:
            file.write(corrected_line + '\n')

    return all_single_sentences
