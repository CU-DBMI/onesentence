"""
CLI for onesentence
"""

import fire
import sys
from onesentence.utils import check_file_for_one_sentence_per_line

class OneSentenceCheckCLI:
    def check(self, file_path: str) -> bool:
        """
        Check if each line in the given file contains only one sentence.

        Args:
            file_path (str): The path to the file to check.

        Returns:
            bool: True if all lines contain only one sentence, False otherwise.
        """
        result = check_file_for_one_sentence_per_line(file_path)
        if result:
            sys.exit(0)
        else:
            sys.exit(1)

def trigger():
    """
    Trigger the CLI to run.
    """
    fire.Fire(OneSentenceCheckCLI)
