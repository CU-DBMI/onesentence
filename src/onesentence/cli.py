"""
CLI for onesentence
"""

import sys
from typing import Optional

import fire

from onesentence.analyze import (
    check_file_for_one_sentence_per_line,
    correct_file_for_one_sentence_per_line,
)


class OneSentenceCheckCLI:
    def check(self, *file_paths: str) -> None:
        """
        Check that each line in the given file(s) contains only one sentence.

        Accepts one or more file paths (for example, the filenames pre-commit
        passes to a hook). Every file is checked independently.

        Args:
            *file_paths (str): One or more paths to files to check.

        Exits:
            0 if every file is compliant, 1 if any file has a violation,
            2 on usage errors (no files provided).
        """
        if not file_paths:
            print("error: no input files provided", file=sys.stderr)
            sys.exit(2)

        all_single_sentences = True
        for file_path in file_paths:
            if not check_file_for_one_sentence_per_line(file_path=file_path):
                all_single_sentences = False

        sys.exit(0 if all_single_sentences else 1)

    def fix(self, *file_paths: str, output: Optional[str] = None) -> None:
        """
        Fix lines that contain more than one sentence in the given file(s).

        Accepts one or more file paths. By default each file is corrected in
        place, so processing many files never lets one file overwrite another.
        Pass ``--output`` to write a single corrected file to a separate path;
        this is only valid with exactly one input file.

        Args:
            *file_paths (str): One or more paths to files to fix.
            output (str): Optional destination path for the corrected file.
                Only valid when exactly one input file is given.

        Exits:
            0 if every file was already compliant, 1 if any file required
            changes, 2 on usage errors (no files, or ``--output`` with more
            than one input file).
        """
        if not file_paths:
            print("error: no input files provided", file=sys.stderr)
            sys.exit(2)

        if output is not None and len(file_paths) != 1:
            print(
                "error: --output requires exactly one input file "
                f"(received {len(file_paths)})",
                file=sys.stderr,
            )
            sys.exit(2)

        all_single_sentences = True
        for file_path in file_paths:
            if not correct_file_for_one_sentence_per_line(
                file_path=file_path, dest_path=output
            ):
                all_single_sentences = False

        sys.exit(0 if all_single_sentences else 1)


def trigger():
    """
    Trigger the CLI to run.
    """
    fire.Fire(OneSentenceCheckCLI)
