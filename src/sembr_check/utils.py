"""
Module for checking semantic line breaks and related.
"""

import pysbd
import re

def is_single_sentence(line: str) -> bool:
    """
    Check if the given line contains only one sentence.

    Args:
        line (str): The line to check.

    Returns:
        bool: True if the line contains only one sentence, False otherwise.
    """

    if not line.strip():
        return True  # Consider empty lines as single sentences

    # Additional filtering for common reST and Markdown formatting
    if re.match(r'^[=\-~`#\*]+$', line):
        return True
    if re.match(r'^\.\.\s+\w+::', line):
        return True

    # Remove special characters that do not pertain to sentence structure
    line = re.sub(r'[^a-zA-Z0-9\s.,!?\'"()\-]', '', line)

    segmenter = pysbd.Segmenter(language="en", clean=False)
    sentences = segmenter.segment(line)
    return len(sentences) == 1

def check_file_for_semantic_line_breaks(file_path: str) -> bool:
    """
    Check if each line in the given file contains only one sentence.
    (i.e. a semantic line breaks).

    Args:
        file_path (str): The path to the file to check.

    Returns:
        bool: True if all lines contain only one sentence, False otherwise.
    """
    all_single_sentences = True
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if not is_single_sentence(line.strip()):
                print(f"Failed: line {line_number}: {line.strip()}")
                all_single_sentences = False
    return all_single_sentences
